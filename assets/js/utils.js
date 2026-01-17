/**
 * EventUtils Module
 * 
 * Utility functions for event processing:
 * - Template event processing (dynamic relative times)
 * - Date formatting
 * - DOM caching
 * 
 * KISS: Single responsibility - utility functions only
 */

class EventUtils {
    constructor(config) {
        this.config = config;
        this.domCache = {};
    }
    
    /**
     * Process template events with relative_time specifications
     * @param {Array} events - Array of events
     * @param {Object} filterModule - Filter module for getNextSunrise
     * @returns {Array} Processed events with computed timestamps
     */
    processTemplateEvents(events, filterModule) {
        // Delegate to TemplateEngine module
        const templateEngine = new TemplateEngine(this.config);
        return templateEngine.processTemplateEvents(events, filterModule);
    }
    
    /**
     * Format date as ISO 8601 string
     * @param {Date} date - Date to format
     * @returns {string} Formatted date string (YYYY-MM-DDTHH:MM:SS)
     */
    formatDateTime(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    }
    
    /**
     * Format date as ISO 8601 with timezone
     * @param {Date} date - Date to format
     * @param {string} tzString - Timezone string (e.g., "+02:00")
     * @returns {string} Formatted date string with timezone
     */
    formatDateTimeWithTZ(date, tzString) {
        return this.formatDateTime(date) + tzString;
    }
    
    /**
     * Get cached DOM element or query and cache it
     * Reduces repeated querySelectorAll/querySelector calls
     * @param {string} selector - CSS selector
     * @param {boolean} multiple - If true, use querySelectorAll
     * @returns {Element|NodeList|null} Cached or newly queried element(s)
     */
    getCachedElement(selector, multiple = false) {
        const cacheKey = `${multiple ? 'all:' : ''}${selector}`;
        
        if (!this.domCache[cacheKey]) {
            this.domCache[cacheKey] = multiple 
                ? document.querySelectorAll(selector)
                : document.querySelector(selector);
        }
        
        return this.domCache[cacheKey];
    }
    
    /**
     * Clear DOM cache (call when DOM structure changes)
     */
    clearDOMCache() {
        this.domCache = {};
    }
    
    /**
     * Update viewport dimensions in CSS custom properties
     * Ensures all layers scale consistently
     */
    updateViewportDimensions() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        document.documentElement.style.setProperty('--app-width', `${width}px`);
        document.documentElement.style.setProperty('--app-height', `${height}px`);
        
        this.log(`Viewport updated: ${width}x${height}`);
    }
    
    /**
     * Show visual feedback when bookmarking
     * @param {boolean} bookmarked - True if bookmarked, false if unbookmarked
     */
    showBookmarkFeedback(bookmarked) {
        const message = bookmarked ? 'Event bookmarked!' : 'Bookmark removed';
        
        const feedback = document.createElement('div');
        feedback.className = 'bookmark-feedback';
        feedback.textContent = message;
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.classList.add('fade-out');
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.parentNode.removeChild(feedback);
                }
            }, 300);
        }, 2000);
    }
    
    /**
     * Get default config fallback
     * @returns {Object} Default configuration
     */
    getDefaultConfig() {
        console.warn('window.APP_CONFIG not found, using fallback defaults');
        return {
            debug: false,
            app: {
                environment: 'unknown'
            },
            map: {
                default_center: { lat: 50.3167, lon: 11.9167 },
                default_zoom: 13,
                tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            },
            data: {
                source: 'real',
                sources: {}
            }
        };
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Utils]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventUtils;
}
