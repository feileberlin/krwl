/**
 * Forms Module - Contact Form & Flyer Upload
 * 
 * Handles client-side behavior for:
 * - Contact form (validates input and shows user-friendly guidance)
 * - Flyer upload form (validates input and explains how to submit events)
 * 
 * KISS: Simple client-side form handling that displays status messages
 * and alternative contact methods (e.g. GitHub issues) without making
 * any direct API calls.
 * 
 * Backend integration (e.g. Telegram Bot API via serverless function
 * or GitHub Actions workflow) is planned for Phase 2.
 */

class FormsManager {
    constructor(config) {
        this.config = config;
        this.isSubmitting = false;
        
        this.init();
    }
    
    init() {
        // Initialize contact form
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => this.handleContactSubmit(e));
        }
        
        // Initialize flyer upload form
        const flyerForm = document.getElementById('flyer-form');
        if (flyerForm) {
            flyerForm.addEventListener('submit', (e) => this.handleFlyerSubmit(e));
        }
    }
    
    async handleContactSubmit(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        
        const form = event.target;
        const name = document.getElementById('contact-name').value.trim();
        const email = document.getElementById('contact-email').value.trim();
        const message = document.getElementById('contact-message').value.trim();
        const statusEl = document.getElementById('contact-form-status');
        
        // Validation
        if (!name || !email || !message) {
            this.showStatus(statusEl, 'error', 'Please fill in all fields.');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showStatus(statusEl, 'error', 'Please enter a valid email address.');
            return;
        }
        
        this.isSubmitting = true;
        
        // Disable submit button to prevent double-submission
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        
        this.showStatus(statusEl, 'loading', 'Sending message...');
        this.disableForm(form, true);
        
        try {
            // For now, show a message with alternative contact methods
            // TODO: Implement GitHub Actions workflow to proxy to Telegram
            const altContactMessage = 
                '✅ Thank you for your interest!\n\n' +
                'Direct form submission is coming soon. For now, please reach out via:\n' +
                '• GitHub: https://github.com/feileberlin/krwl.in/issues\n' +
                '• Email: See repository README';
            
            this.showStatus(statusEl, 'success', altContactMessage);
            
            // Log to console for debugging
            if (this.config.debug) {
                console.log('Contact form submission:', { name, email, message });
            }
            
            form.reset();
        } catch (error) {
            console.error('Contact form error:', error);
            this.showStatus(statusEl, 'error', '❌ Failed to send message. Please contact us via GitHub.');
        } finally {
            this.isSubmitting = false;
            this.disableForm(form, false);
            
            // Re-enable submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = false;
        }
    }
    
    async handleFlyerSubmit(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        
        const form = event.target;
        const name = document.getElementById('flyer-name').value.trim();
        const email = document.getElementById('flyer-email').value.trim();
        const file = document.getElementById('flyer-file').files[0];
        const notes = document.getElementById('flyer-notes').value.trim();
        const statusEl = document.getElementById('flyer-form-status');
        
        // Validation
        if (!name || !email || !file) {
            this.showStatus(statusEl, 'error', 'Please fill in all required fields.');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showStatus(statusEl, 'error', 'Please enter a valid email address.');
            return;
        }
        
        // Check file size (10MB max)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showStatus(statusEl, 'error', 'File too large. Maximum size is 10MB.');
            return;
        }
        
        // Check file type (include both image/jpeg and image/jpg for broader compatibility)
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showStatus(statusEl, 'error', 'Invalid file type. Please upload JPG, PNG, or PDF.');
            return;
        }
        
        this.isSubmitting = true;
        
        // Disable submit button to prevent double-submission
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        
        this.showStatus(statusEl, 'loading', 'Uploading flyer...');
        this.disableForm(form, true);
        
        try {
            // For now, show a message with alternative submission methods
            // TODO: Implement GitHub Actions workflow to handle file uploads
            const altUploadMessage = 
                '✅ Thank you for your submission!\n\n' +
                'Direct flyer upload is coming soon. For now, please:\n' +
                '1. Create a GitHub issue\n' +
                '2. Attach your flyer image\n' +
                '3. We\'ll review and add it to the map\n\n' +
                '→ https://github.com/feileberlin/krwl.in/issues/new';
            
            this.showStatus(statusEl, 'success', altUploadMessage);
            
            // Log to console for debugging
            if (this.config.debug) {
                console.log('Flyer upload:', { name, email, fileName: file.name, fileSize: file.size, notes });
            }
            
            form.reset();
        } catch (error) {
            console.error('Flyer upload error:', error);
            this.showStatus(statusEl, 'error', '❌ Failed to upload flyer. Please create a GitHub issue instead.');
        } finally {
            this.isSubmitting = false;
            this.disableForm(form, false);
            
            // Re-enable submit button
            const submitBtn2 = form.querySelector('button[type="submit"]');
            if (submitBtn2) submitBtn2.disabled = false;
        }
    }
    
    isValidEmail(email) {
        // More robust email validation pattern
        const re = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return re.test(email);
    }
    
    showStatus(element, type, message) {
        if (!element) return;
        
        // Clear any previous timeout and click handler to avoid leaks/duplication
        if (element._statusTimeout) {
            clearTimeout(element._statusTimeout);
            element._statusTimeout = null;
        }
        if (element._statusClickHandler) {
            element.removeEventListener('click', element._statusClickHandler);
            element._statusClickHandler = null;
        }
        
        element.style.display = 'block';
        element.className = 'form-status form-status--' + type;
        
        // Support multiline messages safely without using innerHTML
        // Treat message as plain text and insert <br> elements between lines
        const text = String(message == null ? '' : message);
        
        // Clear any existing content
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
        
        const lines = text.split('\n');
        lines.forEach((line, index) => {
            element.appendChild(document.createTextNode(line));
            if (index < lines.length - 1) {
                element.appendChild(document.createElement('br'));
            }
        });
        
        // Add a close button for manual dismissal
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'form-status__close';
        closeButton.setAttribute('aria-label', 'Close message');
        closeButton.textContent = '×';
        element.appendChild(closeButton);
        
        const hideStatus = () => {
            element.style.display = 'none';
            if (element._statusTimeout) {
                clearTimeout(element._statusTimeout);
                element._statusTimeout = null;
            }
            if (element._statusClickHandler) {
                element.removeEventListener('click', element._statusClickHandler);
                element._statusClickHandler = null;
            }
        };
        
        // Allow dismissal by clicking anywhere on the status element
        const clickHandler = (event) => {
            // Prevent default button behavior
            event.preventDefault();
            hideStatus();
        };
        
        element._statusClickHandler = clickHandler;
        element.addEventListener('click', clickHandler);
        
        // Auto-hide messages:
        // - success after 10 seconds
        // - error after 20 seconds (longer visibility)
        let timeoutDuration = null;
        if (type === 'success') {
            timeoutDuration = 10000;
        } else if (type === 'error') {
            timeoutDuration = 20000;
        }
        
        if (timeoutDuration !== null) {
            element._statusTimeout = setTimeout(() => {
                hideStatus();
            }, timeoutDuration);
        }
    }
    
    disableForm(form, disabled) {
        const inputs = form.querySelectorAll('input, textarea, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormsManager;
}
