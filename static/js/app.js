// Face Recognition Attendance System - Frontend JavaScript

class AttendanceSystem {
    constructor() {
        this.isCameraActive = false;
        this.cameraFeed = document.getElementById('camera-feed');
        this.cameraPlaceholder = document.getElementById('camera-placeholder');
        this.startButton = document.getElementById('start-camera');
        this.stopButton = document.getElementById('stop-camera');
        this.attendanceModal = new bootstrap.Modal(document.getElementById('attendanceModal'));
        this.employeeFullName = document.getElementById('employee-fullname');
        this.employeeId = document.getElementById('employee-id');
        this.employeeUploadedPhoto = document.getElementById('employee-uploaded-photo');
        this.employeeLivePhoto = document.getElementById('employee-live-photo');
        this.toast = new bootstrap.Toast(document.getElementById('status-toast'));
        this.lastAttendanceTimestamp = localStorage.getItem('lastAttendanceTimestamp') || null;
        
        this.initializeEventListeners();
        this.startAttendancePolling();
    }

    initializeEventListeners() {
        this.startButton.addEventListener('click', () => this.startCamera());
        this.stopButton.addEventListener('click', () => this.stopCamera());
    }

    async startCamera() {
        try {
            this.showLoading(this.startButton);
            const response = await fetch('/api/start-camera');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isCameraActive = true;
                this.cameraFeed.src = '/video_feed';
                this.cameraFeed.onload = () => {
                    this.cameraPlaceholder.parentElement.classList.add('camera-active');
                };
                this.updateCameraButtons();
                this.showToast('Camera started successfully', 'success');
            } else {
                this.showToast('Failed to start camera', 'error');
            }
        } catch (error) {
            console.error('Error starting camera:', error);
            this.showToast('Error starting camera', 'error');
        } finally {
            this.hideLoading(this.startButton);
        }
    }

    async stopCamera() {
        try {
            this.showLoading(this.stopButton);
            const response = await fetch('/api/stop-camera');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isCameraActive = false;
                this.cameraFeed.src = '';
                this.cameraPlaceholder.parentElement.classList.remove('camera-active');
                this.updateCameraButtons();
                this.showToast('Camera stopped', 'info');
            } else {
                this.showToast('Failed to stop camera', 'error');
            }
        } catch (error) {
            console.error('Error stopping camera:', error);
            this.showToast('Error stopping camera', 'error');
        } finally {
            this.hideLoading(this.stopButton);
        }
    }

    updateCameraButtons() {
        this.startButton.disabled = this.isCameraActive;
        this.stopButton.disabled = !this.isCameraActive;
    }

    // Simulate attendance confirmation popup (replace with real event in production)
    showAttendanceConfirmation({ fullName, employeeId, uploadedPhotoUrl, livePhotoUrl }) {
        this.employeeFullName.textContent = fullName;
        this.employeeId.textContent = employeeId;
        this.employeeUploadedPhoto.src = uploadedPhotoUrl;
        this.employeeLivePhoto.src = livePhotoUrl;
        this.attendanceModal.show();
        // Auto-close after 4 seconds
        setTimeout(() => {
            this.attendanceModal.hide();
        }, 4000);
    }

    showLoading(button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Loading...';
        button.dataset.originalText = originalText;
    }

    hideLoading(button) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }

    showToast(message, type = 'info') {
        const toastMessage = document.getElementById('toast-message');
        const toastHeader = document.querySelector('#status-toast .toast-header i');
        
        toastMessage.textContent = message;
        
        // Update icon based on message type
        toastHeader.className = 'fas me-2';
        switch (type) {
            case 'success':
                toastHeader.classList.add('fa-check-circle', 'text-success');
                break;
            case 'error':
                toastHeader.classList.add('fa-exclamation-circle', 'text-danger');
                break;
            case 'warning':
                toastHeader.classList.add('fa-exclamation-triangle', 'text-warning');
                break;
            default:
                toastHeader.classList.add('fa-info-circle', 'text-info');
        }
        
        this.toast.show();
    }

    startAttendancePolling() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/last-attendance');
                const result = await response.json();
                if (result.status === 'success' && result.data.timestamp) {
                    if (this.lastAttendanceTimestamp !== String(result.data.timestamp)) {
                        this.lastAttendanceTimestamp = String(result.data.timestamp);
                        localStorage.setItem('lastAttendanceTimestamp', this.lastAttendanceTimestamp);
                        this.showAttendanceConfirmation({
                            fullName: result.data.name,
                            employeeId: result.data.employee_id,
                            uploadedPhotoUrl: result.data.uploaded_photo_url,
                            livePhotoUrl: result.data.live_photo_url
                        });
                    }
                }
            } catch (err) {
                // Optionally handle polling errors
            }
        }, 1000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new AttendanceSystem();
    // For demonstration, you can trigger the popup manually:
    // app.showAttendanceConfirmation({
    //     fullName: 'John Doe',
    //     employeeId: 'EMP001',
    //     uploadedPhotoUrl: '/dataset/Harshad.jpeg',
    //     livePhotoUrl: '/static/img/sample_live.jpg'
    // });
});

// Handle page visibility changes to pause/resume camera
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, could stop camera to save resources
        console.log('Page hidden');
    } else {
        // Page is visible again
        console.log('Page visible');
    }
});

// Handle window resize for responsive design
window.addEventListener('resize', () => {
    // Add any responsive adjustments here if needed
});

// Error handling for network issues
window.addEventListener('online', () => {
    console.log('Network connection restored');
});

window.addEventListener('offline', () => {
    console.log('Network connection lost');
}); 