# Face Recognition Attendance System

A modern web-based face recognition attendance system built with Python Flask, OpenCV, and face_recognition library.

## Features

- **Real-time Face Recognition**: Live camera feed with face detection and recognition
- **Web Interface**: Modern, responsive web UI built with Bootstrap
- **Employee Management**: Add, delete, and manage employees through web interface
- **Attendance Tracking**: Automatic attendance logging with timestamps
- **Employee Management**: Display registered employees from dataset
- **Attendance Reports**: View attendance history and today's count
- **RESTful API**: Backend API for frontend integration
- **Photo Upload**: Drag-and-drop photo upload for employee registration

## Prerequisites

- Python 3.7+
- Webcam
- Linux/Windows/macOS

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install opencv-python face-recognition numpy flask flask-cors
   ```

3. **Setup the dataset**:
   - Create a `dataset` folder in the project root
   - Add employee photos to the `dataset` folder
   - Use clear, front-facing photos with the employee's name as the filename
   - Supported formats: JPG, PNG, JPEG, GIF
   - Example: `john_doe.jpg`, `jane_smith.png`

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   - Open your browser and go to `http://localhost:5000`
   - The application will be available on all network interfaces

## Docker Usage

### Build the Docker image
```bash
docker build -t face-attendance-app .
```

### Run the Docker container
```bash
docker run -it --rm -p 5000:5000 \
  -v $(pwd)/dataset:/app/dataset \
  -v $(pwd)/logs:/app/logs \
  --device /dev/video0:/dev/video0 \
  face-attendance-app
```

- The `-v` flags mount your local `dataset` and `logs` folders for persistence.
- The `--device` flag passes your webcam to the container (may need adjustment for your system).
- Access the app at [http://localhost:5000](http://localhost:5000)

## Usage

### Managing Employees

1. **Access Employee Management**:
   - Click "Manage Employees" in the navigation bar
   - Or go directly to `http://localhost:5000/employees`

2. **Adding Employees**:
   - Fill in the employee name
   - Upload a clear, front-facing photo
   - Click "Add Employee"
   - The system will automatically process the photo and add the employee

3. **Deleting Employees**:
   - Find the employee in the employee list
   - Click the "Delete" button
   - Confirm the deletion in the modal dialog

### Taking Attendance

1. Click "Start Camera" to begin face recognition
2. Position employees in front of the camera
3. The system will automatically detect faces and mark attendance
4. Recognized employees will be highlighted in green with their names
5. Unknown faces will be highlighted in red

### Viewing Attendance

- **Today's Count**: Shows how many employees are present today
- **Attendance Log**: Complete history of all attendance records
- **Auto-refresh**: Attendance data updates automatically every 30 seconds

## File Structure

```
Face Recognition/
├── app.py                 # Main Flask application
├── templates/
│   ├── index.html        # Main dashboard
│   └── employees.html    # Employee management page
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       ├── app.js        # Main dashboard JavaScript
│       └── employees.js  # Employee management JavaScript
├── dataset/              # Employee photos folder
├── logs/
│   └── attendance.csv    # Attendance records
└── README.md
```

## API Endpoints

### Main Interface
- `GET /` - Main dashboard
- `GET /employees` - Employee management page

### Camera Control
- `GET /api/start-camera` - Start camera feed
- `GET /api/stop-camera` - Stop camera feed
- `GET /video_feed` - Live camera feed stream

### Employee Management
- `GET /api/employees` - Get registered employees
- `POST /api/employees/add` - Add new employee with photo
- `DELETE /api/employees/delete/<name>` - Delete employee
- `POST /api/employees/upload` - Upload employee photo

### Attendance
- `GET /api/attendance` - Get attendance records

### File Serving
- `GET /dataset/<filename>` - Serve employee photos

## Configuration

### Camera Settings
- Default camera index: 0 (first available camera)
- To use a different camera, modify the camera index in `app.py`

### File Upload Settings
- Maximum file size: 16MB
- Allowed formats: PNG, JPG, JPEG, GIF
- Upload folder: `dataset/`

### Attendance Log
- Location: `logs/attendance.csv`
- Format: `Name,DateTime`
- Automatically created on first run

## Troubleshooting

### Camera Issues
- Ensure your webcam is connected and working
- Check if another application is using the camera
- Try different camera indices (0, 1, 2, etc.)

### Face Recognition Issues
- Use high-quality, well-lit photos in the dataset
- Ensure photos show the full face clearly
- Avoid photos with glasses, hats, or extreme angles
- Photos must contain detectable faces

### Employee Management Issues
- Ensure photos are in supported formats (PNG, JPG, JPEG, GIF)
- Check file size (max 16MB)
- Use clear, front-facing photos for better recognition
- Employee names should be unique

### Import Errors
- Make sure all dependencies are installed correctly
- Use a virtual environment to avoid conflicts
- On Windows, you might need to install Visual C++ build tools for dlib

### Performance Issues
- Reduce camera resolution for better performance
- Close other applications using the camera
- Ensure adequate lighting for better face detection

## Security Considerations

- This is a basic implementation for demonstration purposes
- For production use, consider:
  - Adding authentication and authorization
  - Implementing HTTPS
  - Adding input validation and sanitization
  - Securing the API endpoints
  - Adding rate limiting
  - Validating uploaded file types and content

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 