import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import base64
import threading
import time
import shutil
from werkzeug.utils import secure_filename
import bcrypt
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

path = 'dataset'
images = []
classNames = []

# Admin credentials (hashed password for 'ADMIN')
ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD_HASH = bcrypt.hashpw(b'ADMIN', bcrypt.gensalt())
app.secret_key = 'supersecretkey'  # Change this in production

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_employees():
    """Load all employee faces from dataset"""
    global images, classNames
    images = []
    classNames = []
    
    if not os.path.exists(path):
        os.makedirs(path)
        return
    
    myList = os.listdir(path)
    for cl in myList:
        if cl.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
            curImg = cv2.imread(f'{path}/{cl}')
            if curImg is not None:
                images.append(curImg)
                classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img)
        if face_encodings:
            encode = face_encodings[0]
            encodeList.append(encode)
        else:
            print(f"Warning: No face detected in image")
    return encodeList

def markAttendance(name):
    with open('logs/attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

def save_live_face(img, faceLoc, employee_id):
    y1, x2, y2, x1 = faceLoc
    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
    face_img = img[y1:y2, x1:x2]
    filename = f"{employee_id}_{uuid.uuid4().hex[:8]}.jpg"
    save_dir = os.path.join('static', 'live_captures')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, face_img)
    return f"/static/live_captures/{filename}"

# Global variables for camera feed
camera = None
is_camera_active = False
current_frame = None
encodeListKnown = []

# For attendance confirmation popup
last_attendance_event = {
    'timestamp': None,
    'name': None,
    'employee_id': None,
    'uploaded_photo_url': None,
    'live_photo_url': None
}

# Load initial employees
load_employees()
encodeListKnown = findEncodings(images) if images else []

# Remove or restrict public attendance API
def is_admin_logged_in():
    return session.get('admin_logged_in', False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employees():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    return render_template('employees.html')

@app.route('/api/start-camera')
def start_camera():
    global camera, is_camera_active
    if not is_camera_active:
        camera = cv2.VideoCapture(0)
        is_camera_active = True
        threading.Thread(target=camera_loop, daemon=True).start()
    return jsonify({"status": "success", "message": "Camera started"})

@app.route('/api/stop-camera')
def stop_camera():
    global camera, is_camera_active
    if is_camera_active and camera is not None:
        camera.release()
        is_camera_active = False
    return jsonify({"status": "success", "message": "Camera stopped"})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '').encode('utf-8')
        if username == ADMIN_USERNAME and bcrypt.checkpw(password, ADMIN_PASSWORD_HASH):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    try:
        with open('logs/attendance.csv', 'r') as f:
            lines = f.readlines()
            attendance_data = []
            for line in lines[1:]:  # Skip header
                if line.strip():
                    name, datetime_str = line.strip().split(',', 1)
                    attendance_data.append({
                        'name': name,
                        'datetime': datetime_str
                    })
        return render_template('admin_dashboard.html', attendance_data=attendance_data, employees=classNames)
    except FileNotFoundError:
        return render_template('admin_dashboard.html', attendance_data=[], employees=classNames)

@app.route('/api/employees')
def get_employees():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "Not authorized"}), 403
    return jsonify({"status": "success", "data": classNames})

@app.route('/api/employees/add', methods=['POST'])
def add_employee():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "Not authorized"}), 403
    try:
        if 'photo' not in request.files:
            return jsonify({"status": "error", "message": "No photo uploaded"}), 400
        file = request.files['photo']
        employee_name = request.form.get('name', '').strip()
        if file.filename == '' or file.filename is None:
            return jsonify({"status": "error", "message": "No file selected"}), 400
        if not employee_name:
            return jsonify({"status": "error", "message": "Employee name is required"}), 400
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400
        filename = secure_filename(employee_name)
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        final_filename = f"{filename}.{file_extension}"
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], final_filename)):
            return jsonify({"status": "error", "message": "Employee already exists"}), 400
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        load_employees()
        global encodeListKnown
        encodeListKnown = findEncodings(images) if images else []
        return jsonify({
            "status": "success", 
            "message": f"Employee {employee_name} added successfully",
            "employee": employee_name
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/employees/delete/<employee_name>', methods=['DELETE'])
def delete_employee(employee_name):
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "Not authorized"}), 403
    try:
        employee_files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().startswith(employee_name.lower()) and allowed_file(filename):
                employee_files.append(filename)
        if not employee_files:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        deleted_files = []
        for filename in employee_files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)
            deleted_files.append(filename)
        load_employees()
        global encodeListKnown
        encodeListKnown = findEncodings(images) if images else []
        return jsonify({
            "status": "success", 
            "message": f"Employee {employee_name} deleted successfully",
            "deleted_files": deleted_files
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/employees/upload', methods=['POST'])
def upload_employee_photo():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "Not authorized"}), 403
    try:
        if 'photo' not in request.files:
            return jsonify({"status": "error", "message": "No photo uploaded"}), 400
        file = request.files['photo']
        employee_name = request.form.get('name', '').strip()
        if file.filename == '' or file.filename is None:
            return jsonify({"status": "error", "message": "No file selected"}), 400
        if not employee_name:
            return jsonify({"status": "error", "message": "Employee name is required"}), 400
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400
        filename = secure_filename(employee_name)
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        final_filename = f"{filename}.{file_extension}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        return jsonify({
            "status": "success", 
            "message": f"Photo uploaded for {employee_name}",
            "filename": final_filename
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def camera_loop():
    global current_frame, camera, is_camera_active, encodeListKnown, last_attendance_event
    while is_camera_active and camera is not None:
        success, img = camera.read()
        if success:
            imgS = cv2.resize(img, (0,0), fx=0.25, fy=0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    markAttendance(name)

                    # Save live face image
                    employee_id = classNames[matchIndex]
                    uploaded_photo_url = f"/dataset/{employee_id}.jpeg" if os.path.exists(f"dataset/{employee_id}.jpeg") else f"/dataset/{employee_id}.jpg"
                    live_photo_url = save_live_face(img, faceLoc, employee_id)
                    last_attendance_event = {
                        'timestamp': time.time(),
                        'name': name,
                        'employee_id': employee_id,
                        'uploaded_photo_url': uploaded_photo_url,
                        'live_photo_url': live_photo_url
                    }

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(img, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                else:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 2)
                    cv2.putText(img, "Unknown", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            current_frame = img
        time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', current_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # Send a blank frame if no camera feed
                blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', blank_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dataset/<filename>')
def serve_employee_photo(filename):
    """Serve employee photos from the dataset folder"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/last-attendance')
def api_last_attendance():
    if last_attendance_event['timestamp']:
        return jsonify({"status": "success", "data": last_attendance_event})
    else:
        return jsonify({"status": "none"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
