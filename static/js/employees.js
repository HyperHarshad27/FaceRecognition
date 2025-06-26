// Employee Management JavaScript

class EmployeeManager {
    constructor() {
        this.deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
        this.toast = new bootstrap.Toast(document.getElementById('status-toast'));
        this.employeeToDelete = null;
        
        this.initializeEventListeners();
        this.loadEmployees();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('add-employee-form').addEventListener('submit', (e) => this.handleAddEmployee(e));
        
        // Photo preview
        document.getElementById('employee-photo').addEventListener('change', (e) => this.handlePhotoPreview(e));
        
        // Refresh button
        document.getElementById('refresh-employees').addEventListener('click', () => this.loadEmployees());
        
        // Delete confirmation
        document.getElementById('confirm-delete').addEventListener('click', () => this.confirmDelete());
    }

    async handleAddEmployee(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const name = formData.get('name').trim();
        const photo = formData.get('photo');
        
        if (!name || !photo) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }
        
        try {
            this.showLoading(document.querySelector('#add-employee-form button[type="submit"]'));
            
            const response = await fetch('/api/employees/add', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showToast(data.message, 'success');
                e.target.reset();
                document.getElementById('photo-preview').classList.add('d-none');
                this.loadEmployees();
            } else {
                this.showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Error adding employee:', error);
            this.showToast('Error adding employee', 'error');
        } finally {
            this.hideLoading(document.querySelector('#add-employee-form button[type="submit"]'));
        }
    }

    handlePhotoPreview(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('photo-preview');
        const previewImage = document.getElementById('preview-image');
        
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                preview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        } else {
            preview.classList.add('d-none');
        }
    }

    async loadEmployees() {
        try {
            const response = await fetch('/api/employees');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayEmployees(data.data);
                this.displayEmployeesTable(data.data);
            } else {
                this.showToast('Failed to load employees', 'error');
            }
        } catch (error) {
            console.error('Error loading employees:', error);
            this.showToast('Error loading employees', 'error');
        }
    }

    displayEmployees(employees) {
        const employeesList = document.getElementById('employees-list');
        
        if (employees.length === 0) {
            employeesList.innerHTML = `
                <p class="text-muted">No employees registered</p>
                <small class="text-muted">Add employees using the form on the left</small>
            `;
            return;
        }

        const employeeBadges = employees.map(employee => 
            `<span class="employee-badge">${employee}</span>`
        ).join('');
        
        employeesList.innerHTML = employeeBadges;
    }

    displayEmployeesTable(employees) {
        const tableBody = document.getElementById('employees-table');
        
        if (employees.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No employees found</td></tr>';
            return;
        }

        const rows = employees.map(employee => `
            <tr class="fade-in">
                <td><strong>${employee}</strong></td>
                <td>
                    <img src="/dataset/${employee}.jpg" alt="${employee}" 
                         class="img-thumbnail" style="width: 50px; height: 50px; object-fit: cover;"
                         onerror="this.style.display='none'">
                </td>
                <td>
                    <span class="badge bg-success">Active</span>
                </td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="employeeManager.deleteEmployee('${employee}')">
                        <i class="fas fa-trash me-1"></i>
                        Delete
                    </button>
                </td>
            </tr>
        `).join('');

        tableBody.innerHTML = rows;
    }

    async deleteEmployee(employeeName) {
        this.employeeToDelete = employeeName;
        document.getElementById('delete-employee-name').textContent = employeeName;
        this.deleteModal.show();
    }

    async confirmDelete() {
        if (!this.employeeToDelete) return;
        
        try {
            this.showLoading(document.getElementById('confirm-delete'));
            
            const response = await fetch(`/api/employees/delete/${this.employeeToDelete}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showToast(data.message, 'success');
                this.loadEmployees();
            } else {
                this.showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Error deleting employee:', error);
            this.showToast('Error deleting employee', 'error');
        } finally {
            this.hideLoading(document.getElementById('confirm-delete'));
            this.deleteModal.hide();
            this.employeeToDelete = null;
        }
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
}

// Initialize the employee manager when DOM is loaded
let employeeManager;
document.addEventListener('DOMContentLoaded', () => {
    employeeManager = new EmployeeManager();
});

// Global function for delete button onclick
window.deleteEmployee = function(employeeName) {
    if (employeeManager) {
        employeeManager.deleteEmployee(employeeName);
    }
}; 