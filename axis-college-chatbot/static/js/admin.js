// Axis Colleges Admin Panel JavaScript

class AdminPanel {
    constructor() {
        this.currentSection = 'dashboard';
        this.init();
    }

    init() {
        // Load dashboard data on page load
        this.loadDashboardData();
        
        // Update current time
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);
        
        // Initialize tooltips
        this.initTooltips();
        
        // Auto-refresh dashboard every 30 seconds
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000);
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    async loadDashboardData() {
        try {
            // Load statistics
            await this.loadStatistics();
            
            // Load recent activity
            await this.loadRecentActivity();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showAlert('Error loading dashboard data', 'danger');
        }
    }

    async loadStatistics() {
        try {
            const courses = await this.fetchData('/api/admin/courses');
            const faqs = await this.fetchData('/api/admin/faqs');
            const eventsStats = await this.fetchData('/api/admin/events/stats');
            
            document.getElementById('coursesCount').textContent = courses.length || 0;
            document.getElementById('faqsCount').textContent = faqs.length || 0;
            document.getElementById('eventsCount').textContent = eventsStats.upcoming_events || 0;
            document.getElementById('placementsCount').textContent = '15'; // Static for now
            
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    async loadRecentActivity() {
        try {
            // This would typically come from an API endpoint
            const activities = [
                { activity: 'New course added', section: 'Courses', time: '2 minutes ago' },
                { activity: 'FAQ updated', section: 'FAQs', time: '15 minutes ago' },
                { activity: 'Event created', section: 'Events', time: '1 hour ago' },
                { activity: 'Placement data updated', section: 'Placements', time: '2 hours ago' }
            ];
            
            const tbody = document.getElementById('recentActivity');
            if (tbody) {
                tbody.innerHTML = activities.map(activity => `
                    <tr>
                        <td>${activity.activity}</td>
                        <td><span class="badge bg-info">${activity.section}</span></td>
                        <td><small class="text-muted">${activity.time}</small></td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    async fetchData(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    async postData(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    async postFormData(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    async putData(url, data) {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    async deleteData(url) {
        const response = await fetch(url, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the content area
        const contentArea = document.querySelector('.content-area');
        contentArea.insertBefore(alertDiv, contentArea.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    showLoading(element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading...</p>
            </div>
        `;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

// Course Management
class CourseManager extends AdminPanel {
    async loadCourses() {
        const tbody = document.getElementById('coursesTable');
        this.showLoading(tbody);
        
        try {
            const response = await this.fetchData('/api/admin/courses');
            const courses = response.courses || [];
            
            if (courses.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            <i class="fas fa-inbox fa-2x mb-2"></i>
                            <p>No courses found. Click "Add Course" to create your first course.</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = courses.map(course => `
                <tr>
                    <td>${course.id}</td>
                    <td><strong>${course.name}</strong></td>
                    <td>${course.duration}</td>
                    <td>${this.formatCurrency(course.fees)}</td>
                    <td><small>${course.eligibility || 'N/A'}</small></td>
                    <td>
                        <button class="btn btn-sm btn-edit me-1" onclick="editCourse(${course.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-delete" onclick="deleteCourse(${course.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
        } catch (error) {
            console.error('Error loading courses:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <p>Error loading courses. Please try again.</p>
                    </td>
                </tr>
            `;
        }
    }

    async saveCourse() {
        const form = document.getElementById('courseForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const courseId = document.getElementById('courseId').value;
        const courseData = {
            name: document.getElementById('courseName').value,
            duration: document.getElementById('courseDuration').value,
            fees: parseFloat(document.getElementById('courseFees').value),
            eligibility: document.getElementById('courseEligibility').value,
            description: document.getElementById('courseDescription').value
        };
        
        try {
            let response;
            if (courseId) {
                // Update existing course
                response = await this.putData(`/api/admin/courses/${courseId}`, courseData);
                this.showAlert('Course updated successfully!', 'success');
            } else {
                // Add new course
                response = await this.postData('/api/admin/courses', courseData);
                this.showAlert('Course added successfully!', 'success');
            }
            
            // Close modal and reload courses
            const modal = bootstrap.Modal.getInstance(document.getElementById('courseModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            document.getElementById('courseId').value = '';
            
            // Reload courses if we're on the courses section
            if (this.currentSection === 'courses') {
                await this.loadCourses();
            }
            
            // Update dashboard stats
            if (this.currentSection === 'dashboard') {
                await this.loadStatistics();
            }
            
        } catch (error) {
            console.error('Error saving course:', error);
            this.showAlert('Error saving course. Please try again.', 'danger');
        }
    }

    async editCourse(courseId) {
        try {
            const response = await this.fetchData('/api/admin/courses');
            const courses = response.courses || [];
            const course = courses.find(c => c.id === courseId);
            
            if (!course) {
                this.showAlert('Course not found', 'danger');
                return;
            }
            
            // Populate form
            document.getElementById('courseId').value = course.id;
            document.getElementById('courseName').value = course.name;
            document.getElementById('courseDuration').value = course.duration;
            document.getElementById('courseFees').value = course.fees;
            document.getElementById('courseEligibility').value = course.eligibility || '';
            document.getElementById('courseDescription').value = course.description || '';
            
            // Update modal title
            document.getElementById('courseModalTitle').textContent = 'Edit Course';
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('courseModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error loading course:', error);
            this.showAlert('Error loading course details', 'danger');
        }
    }

    async deleteCourse(courseId) {
        if (!confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
            return;
        }
        
        try {
            await this.deleteData(`/api/admin/courses/${courseId}`);
            this.showAlert('Course deleted successfully!', 'success');
            await this.loadCourses();
            await this.loadStatistics();
        } catch (error) {
            console.error('Error deleting course:', error);
            this.showAlert('Error deleting course. Please try again.', 'danger');
        }
    }
}

// FAQ Management
class FAQManager extends AdminPanel {
    async loadFAQs() {
        const tbody = document.getElementById('faqsTable');
        this.showLoading(tbody);
        
        try {
            const response = await this.fetchData('/api/admin/faqs');
            const faqs = response.faqs || [];
            
            if (faqs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center text-muted">
                            <i class="fas fa-question-circle fa-2x mb-2"></i>
                            <p>No FAQs found. Click "Add FAQ" to create your first FAQ.</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = faqs.map(faq => `
                <tr>
                    <td>${faq.id}</td>
                    <td><strong>${faq.question}</strong></td>
                    <td><span class="badge bg-info">${faq.category}</span></td>
                    <td><small>${faq.answer.substring(0, 100)}${faq.answer.length > 100 ? '...' : ''}</small></td>
                    <td>
                        <button class="btn btn-sm btn-edit me-1" onclick="editFAQ(${faq.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-delete" onclick="deleteFAQ(${faq.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
        } catch (error) {
            console.error('Error loading FAQs:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <p>Error loading FAQs. Please try again.</p>
                    </td>
                </tr>
            `;
        }
    }

    async saveFAQ() {
        const form = document.getElementById('faqForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const faqId = document.getElementById('faqId').value;
        const faqData = {
            question: document.getElementById('faqQuestion').value,
            category: document.getElementById('faqCategory').value,
            answer: document.getElementById('faqAnswer').value
        };
        
        try {
            let response;
            if (faqId) {
                response = await this.putData(`/api/admin/faqs/${faqId}`, faqData);
                this.showAlert('FAQ updated successfully!', 'success');
            } else {
                response = await this.postData('/api/admin/faqs', faqData);
                this.showAlert('FAQ added successfully!', 'success');
            }
            
            // Close modal and reload FAQs
            const modal = bootstrap.Modal.getInstance(document.getElementById('faqModal'));
            modal.hide();
            
            // Reset form
            form.reset();
            document.getElementById('faqId').value = '';
            
            // Reload FAQs if we're on the FAQs section
            if (this.currentSection === 'faqs') {
                await this.loadFAQs();
            }
            
            // Update dashboard stats
            if (this.currentSection === 'dashboard') {
                await this.loadStatistics();
            }
            
        } catch (error) {
            console.error('Error saving FAQ:', error);
            this.showAlert('Error saving FAQ. Please try again.', 'danger');
        }
    }

    async editFAQ(faqId) {
        try {
            const response = await this.fetchData('/api/admin/faqs');
            const faqs = response.faqs || [];
            const faq = faqs.find(f => f.id === faqId);
            
            if (!faq) {
                this.showAlert('FAQ not found', 'danger');
                return;
            }
            
            // Populate form
            document.getElementById('faqId').value = faq.id;
            document.getElementById('faqQuestion').value = faq.question;
            document.getElementById('faqCategory').value = faq.category;
            document.getElementById('faqAnswer').value = faq.answer;
            
            // Update modal title
            document.getElementById('faqModalTitle').textContent = 'Edit FAQ';
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('faqModal'));
            modal.show();
            
        } catch (error) {
            console.error('Error loading FAQ:', error);
            this.showAlert('Error loading FAQ details', 'danger');
        }
    }

    async deleteFAQ(faqId) {
        if (!confirm('Are you sure you want to delete this FAQ? This action cannot be undone.')) {
            return;
        }
        
        try {
            await this.deleteData(`/api/admin/faqs/${faqId}`);
            this.showAlert('FAQ deleted successfully!', 'success');
            await this.loadFAQs();
            await this.loadStatistics();
        } catch (error) {
            console.error('Error deleting FAQ:', error);
            this.showAlert('Error deleting FAQ. Please try again.', 'danger');
        }
    }
}

class EventManager {
    constructor() {
        this.events = [];
    }

    async loadEvents() {
        try {
            console.log("Loading events from backend...");
            const response = await this.fetchData('/api/admin/events');
            console.log("Events response:", response);
            
            this.events = response.events || [];
            console.log(`Loaded ${this.events.length} events`);
            this.displayEvents();
        } catch (error) {
            console.error('Error loading events:', error);
            this.showEventsError(error.message || 'Unknown error occurred');
        }
    }

    displayEvents() {
        const tbody = document.getElementById('eventsTable');
        if (!tbody) return;

        if (this.events.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-calendar-times fa-2x mb-2"></i>
                        <p>No events found. Add your first event!</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.events.map(event => `
            <tr>
                <td>${event.id}</td>
                <td>
                    ${event.image_url ? 
                        `<img src="${event.image_url}" alt="${event.event_name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">` : 
                        '<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image text-muted"></i></div>'
                    }
                </td>
                <td>
                    <strong>${event.event_name}</strong>
                    <br>
                    <small class="text-muted">${event.description.substring(0, 50)}${event.description.length > 50 ? '...' : ''}</small>
                </td>
                <td>${this.formatDate(event.event_date)}</td>
                <td>${event.event_time}</td>
                <td>${event.venue}</td>
                <td>
                    <span class="badge bg-${this.getCategoryColor(event.category)}">${event.category}</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editEvent(${event.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEvent(${event.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getCategoryColor(category) {
        const colors = {
            'Cultural': 'success',
            'Technical': 'primary',
            'Sports': 'warning',
            'Academic': 'info'
        };
        return colors[category] || 'secondary';
    }

    formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }

    showEventsError(errorMessage = null) {
        const tbody = document.getElementById('eventsTable');
        if (tbody) {
            const displayMessage = errorMessage || 'Error loading events. Please try again.';
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <p>${displayMessage}</p>
                        <small class="text-muted">Check browser console for more details</small>
                    </td>
                </tr>
            `;
        }
    }

    async saveEvent() {
        console.log("=== saveEvent called ===");
        const form = document.getElementById('eventForm');
        console.log("Form:", form);
        
        // Enable form validation
        if (!form.checkValidity()) {
            console.log("Form validation failed");
            form.reportValidity();
            return;
        }
        
        console.log("Form validation passed");

        const eventId = document.getElementById('eventId').value;
        console.log("Event ID:", eventId);
        
        try {
            let response;
            if (eventId) {
                console.log("Editing existing event");
                // For editing, we'll still use JSON (file upload for edit can be added later)
                const eventData = {
                    event_name: document.getElementById('eventName').value,
                    description: document.getElementById('eventDescription').value,
                    event_date: document.getElementById('eventDate').value,
                    event_time: document.getElementById('eventTime').value,
                    venue: document.getElementById('eventVenue').value,
                    category: document.getElementById('eventCategory').value
                };
                console.log("Event data for edit:", eventData);
                response = await this.putData(`/api/admin/events/${eventId}`, eventData);
                
                // Check if edit was successful
                if (response && response.success) {
                    this.showAlert('Event updated successfully', 'success');
                } else {
                    const errorMessage = response?.error || 'Failed to update event. Please try again.';
                    this.showAlert(errorMessage, 'danger');
                    return; // Don't proceed if update failed
                }
            } else {
                console.log("Adding new event");
                
                // Get form values
                const eventName = document.getElementById('eventName').value;
                const description = document.getElementById('eventDescription').value;
                const eventDate = document.getElementById('eventDate').value;
                const eventTime = document.getElementById('eventTime').value;
                const venue = document.getElementById('eventVenue').value;
                const category = document.getElementById('eventCategory').value;
                
                console.log("Form values:", {eventName, description, eventDate, eventTime, venue, category});
                
                // Validate required fields
                if (!eventName || !description || !eventDate || !eventTime || !venue || !category) {
                    this.showAlert('Please fill in all required fields', 'danger');
                    return;
                }
                
                // For adding new event, use FormData for file upload
                const formData = new FormData();
                formData.append('event_name', eventName);
                formData.append('description', description);
                formData.append('event_date', eventDate);
                formData.append('event_time', eventTime);
                formData.append('venue', venue);
                formData.append('category', category);
                
                // Add image file if selected
                const imageFile = document.getElementById('eventImage').files[0];
                if (imageFile) {
                    console.log("Image file found:", imageFile.name);
                    formData.append('event_image', imageFile);
                } else {
                    console.log("No image file selected");
                }
                
                console.log("FormData prepared, sending to server...");
                response = await this.postFormData('/api/admin/events', formData);
                console.log("Server response:", response);
                
                // Check if save was successful
                if (response && response.success) {
                    this.showAlert('Event added successfully', 'success');
                } else {
                    const errorMessage = response?.error || 'Failed to save event. Please try again.';
                    this.showAlert(errorMessage, 'danger');
                    return; // Don't proceed if save failed
                }
            }

            // Close modal and reload events
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
            modal.hide();

            // Reset form
            form.reset();
            document.getElementById('eventId').value = '';
            
            // Reset image preview
            document.getElementById('imagePreview').style.display = 'none';

            // Reload events
            await this.loadEvents();

            // Update dashboard stats
            if (adminPanel.currentSection === 'dashboard') {
                await adminPanel.loadStatistics();
            }

        } catch (error) {
            console.error('Error saving event:', error);
            this.showAlert('Failed to save event. Please try again.', 'danger');
        }
    }

    async editEvent(eventId) {
        try {
            const response = await this.fetchData('/api/admin/events');
            const events = response.events || [];
            const event = events.find(e => e.id === eventId);

            if (!event) {
                this.showAlert('Event not found', 'danger');
                return;
            }

            // Populate form
            document.getElementById('eventId').value = event.id;
            document.getElementById('eventName').value = event.event_name;
            document.getElementById('eventDescription').value = event.description;
            document.getElementById('eventDate').value = event.event_date;
            document.getElementById('eventTime').value = event.event_time;
            document.getElementById('eventVenue').value = event.venue;
            document.getElementById('eventCategory').value = event.category;

            // Update modal title
            document.getElementById('eventModalTitle').textContent = 'Edit Event';

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('eventModal'));
            modal.show();
        } catch (error) {
            console.error('Error editing event:', error);
            this.showAlert('Error loading event data', 'danger');
        }
    }

    async deleteEvent(eventId) {
        if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await this.deleteData(`/api/admin/events/${eventId}`);
            console.log('Delete response:', response);
            
            // Check if the deletion was successful
            if (response && response.success) {
                this.showAlert('Event deleted successfully', 'success');
                await this.loadEvents();

                // Update dashboard stats
                if (adminPanel.currentSection === 'dashboard') {
                    await adminPanel.loadStatistics();
                }
            } else {
                // Handle backend error messages
                const errorMessage = response?.error || 'Failed to delete event. Please try again.';
                this.showAlert(errorMessage, 'danger');
            }

        } catch (error) {
            console.error('Error deleting event:', error);
            this.showAlert('Failed to delete event. Please try again.', 'danger');
        }
    }

    // API helper methods (reuse from other managers)
    async fetchData(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    async postData(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    async postFormData(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    async putData(url, data) {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    async deleteData(url) {
        const response = await fetch(url, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Initialize managers
const adminPanel = new AdminPanel();
const courseManager = new CourseManager();
const faqManager = new FAQManager();
const eventManager = new EventManager();

// Global functions for onclick handlers
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.sidebar-menu .nav-link').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show selected section
    const sectionElement = document.getElementById(`${section}-section`);
    if (sectionElement) {
        sectionElement.style.display = 'block';
    }
    
    // Add active class to clicked nav link
    event.target.classList.add('active');
    
    // Update current section
    adminPanel.currentSection = section;
    
    // Load section-specific data
    switch(section) {
        case 'dashboard':
            adminPanel.loadDashboardData();
            break;
        case 'courses':
            courseManager.loadCourses();
            break;
        case 'faqs':
            faqManager.loadFAQs();
            break;
        case 'events':
            eventManager.loadEvents();
            break;
        // Add other sections as needed
    }
    
    // Close mobile sidebar
    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('show');
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

// Event Management Global Functions
function openEventModal() {
    // Reset form
    document.getElementById('eventForm').reset();
    document.getElementById('eventId').value = '';
    
    // Reset image preview
    document.getElementById('imagePreview').style.display = 'none';
    
    // Update modal title
    document.getElementById('eventModalTitle').textContent = 'Add Event';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
}

function saveEvent() {
    eventManager.saveEvent();
}

function editEvent(eventId) {
    eventManager.editEvent(eventId);
}

function deleteEvent(eventId) {
    eventManager.deleteEvent(eventId);
}

function clearEventFilters() {
    document.getElementById('eventSearch').value = '';
    document.getElementById('eventCategoryFilter').value = '';
    document.getElementById('eventDateFilter').value = '';
    eventManager.displayEvents();
}

function openCourseModal() {
    document.getElementById('courseModalTitle').textContent = 'Add Course';
    document.getElementById('courseForm').reset();
    document.getElementById('courseId').value = '';
    const modal = new bootstrap.Modal(document.getElementById('courseModal'));
    modal.show();
}

function openFAQModal() {
    document.getElementById('faqModalTitle').textContent = 'Add FAQ';
    document.getElementById('faqForm').reset();
    document.getElementById('faqId').value = '';
    const modal = new bootstrap.Modal(document.getElementById('faqModal'));
    modal.show();
}

function saveCourse() {
    courseManager.saveCourse();
}

function saveFAQ() {
    faqManager.saveFAQ();
}

function editCourse(courseId) {
    courseManager.editCourse(courseId);
}

function editFAQ(faqId) {
    faqManager.editFAQ(faqId);
}

function deleteCourse(courseId) {
    courseManager.deleteCourse(courseId);
}

function deleteFAQ(faqId) {
    faqManager.deleteFAQ(faqId);
}

function exportData() {
    alert('Export functionality coming soon!');
}

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        document.getElementById('sidebar').classList.remove('show');
    }
});

// Handle form submissions
document.getElementById('courseForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    saveCourse();
});

document.getElementById('faqForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    saveFAQ();
});

// Close mobile sidebar when clicking outside
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.mobile-toggle');
    
    if (window.innerWidth <= 768 && 
        !sidebar.contains(e.target) && 
        !toggle.contains(e.target) && 
        sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
    }
});
