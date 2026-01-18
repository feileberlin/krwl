/**
 * Forms Module - Contact Form & Flyer Upload
 * 
 * Handles form submissions for:
 * - Contact form (sends message via Telegram Bot API)
 * - Flyer upload form (creates pending event via Telegram Bot API)
 * 
 * KISS: Simple client-side form handling with direct Telegram Bot API calls
 * 
 * Note: This uses a serverless function or GitHub Actions workflow as a proxy
 * to keep the TELEGRAM_BOT_TOKEN secret.
 */

class FormsManager {
    constructor(config) {
        this.config = config;
        this.isSubmitting = false;
        
        // Telegram configuration from config
        this.telegramConfig = config.telegram || {};
        this.adminChatIds = this.telegramConfig.admin_chat_ids || [];
        
        // API endpoint (GitHub Actions workflow or serverless function)
        // This will be a GitHub Actions workflow that proxies to Telegram Bot API
        this.apiEndpoint = 'https://api.github.com/repos/feileberlin/krwl-hof/dispatches';
        
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
        this.showStatus(statusEl, 'loading', 'Sending message...');
        this.disableForm(form, true);
        
        try {
            // For now, show a message with alternative contact methods
            // TODO: Implement GitHub Actions workflow to proxy to Telegram
            const altContactMessage = 
                '✅ Thank you for your interest!\n\n' +
                'Direct form submission is coming soon. For now, please reach out via:\n' +
                '• GitHub: https://github.com/feileberlin/krwl-hof/issues\n' +
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
        
        // Check file type
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showStatus(statusEl, 'error', 'Invalid file type. Please upload JPG, PNG, or PDF.');
            return;
        }
        
        this.isSubmitting = true;
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
                '→ https://github.com/feileberlin/krwl-hof/issues/new';
            
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
        }
    }
    
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    showStatus(element, type, message) {
        if (!element) return;
        
        element.style.display = 'block';
        element.className = 'form-status form-status--' + type;
        
        // Support multiline messages
        element.innerHTML = message.replace(/\n/g, '<br>');
        
        // Auto-hide success messages after 10 seconds
        if (type === 'success') {
            setTimeout(() => {
                element.style.display = 'none';
            }, 10000);
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
