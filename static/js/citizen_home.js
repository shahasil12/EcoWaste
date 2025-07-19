// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
    
    // Photo upload preview
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');
    
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    photoPreview.innerHTML = `<img src="${e.target.result}" alt="Photo preview" style="max-width: 200px; max-height: 200px; border-radius: 5px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Get current location
    const getLocationBtn = document.getElementById('getLocation');
    const locationInput = document.getElementById('location');
    
    if (getLocationBtn && locationInput) {
        getLocationBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                this.textContent = 'Getting location...';
                this.disabled = true;
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        locationInput.value = `${lat}, ${lng}`;
                        getLocationBtn.textContent = 'Use Current Location';
                        getLocationBtn.disabled = false;
                        
                        // Optional: Reverse geocoding to get address
                        reverseGeocode(lat, lng);
                    },
                    function(error) {
                        alert('Error getting location: ' + error.message);
                        getLocationBtn.textContent = 'Use Current Location';
                        getLocationBtn.disabled = false;
                    }
                );
            } else {
                alert('Geolocation is not supported by this browser.');
            }
        });
    }
    
    // Search and filter functionality
    const searchInput = document.getElementById('searchReports');
    const statusFilter = document.getElementById('statusFilter');
    const reportCards = document.querySelectorAll('.report-card');
    
    function filterReports() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const statusValue = statusFilter ? statusFilter.value.toLowerCase() : '';
        
        reportCards.forEach(card => {
            const cardText = card.textContent.toLowerCase();
            const cardStatus = card.querySelector('.report-status');
            const cardStatusText = cardStatus ? cardStatus.textContent.toLowerCase() : '';
            
            const matchesSearch = cardText.includes(searchTerm);
            const matchesStatus = !statusValue || cardStatusText.includes(statusValue);
            
            if (matchesSearch && matchesStatus) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', filterReports);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterReports);
    }
    
    // Form submissions
    const reportForm = document.getElementById('reportForm');
    const paymentForm = document.getElementById('paymentForm');
    const profileForm = document.getElementById('profileForm');
    
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const wasteType = document.getElementById('wasteType').value;
            const description = document.getElementById('description').value;
            const photo = document.getElementById('photo').files[0];
            const location = document.getElementById('location').value;
            
            if (!wasteType || !description || !photo || !location) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
            
            // Simulate form submission (replace with actual AJAX call)
            setTimeout(() => {
                alert('Report submitted successfully!');
                this.reset();
                photoPreview.innerHTML = '';
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const reportId = document.getElementById('reportId').value;
            const amount = document.getElementById('amount').value;
            const paymentMethod = document.getElementById('paymentMethod').value;
            
            if (!reportId || !amount || !paymentMethod) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;
            
            // Simulate payment processing
            setTimeout(() => {
                alert('Payment processed successfully!');
                this.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 3000);
        });
    }
    
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Updating...';
            submitBtn.disabled = true;
            
            // Simulate profile update
            setTimeout(() => {
                alert('Profile updated successfully!');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
});

// Reverse geocoding function (optional - requires API key)
function reverseGeocode(lat, lng) {
    // This is a placeholder - you would need to implement actual reverse geocoding
    // using a service like Google Maps API, OpenStreetMap, etc.
    console.log(`Reverse geocoding for: ${lat}, ${lng}`);
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#27ae60';
            break;
        case 'error':
            notification.style.backgroundColor = '#e74c3c';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f39c12';
            break;
        default:
            notification.style.backgroundColor = '#3498db';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);