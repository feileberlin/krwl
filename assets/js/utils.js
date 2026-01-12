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
        const now = new Date();
        
        return events.map(event => {
            if (!event.relative_time) {
                return event;
            }
            
            const processedEvent = { ...event };
            const spec = event.relative_time;
            const type = spec.type;
            
            let startTime, endTime;
            
            if (type === 'offset') {
                startTime = new Date(now);
                
                if (spec.hours) {
                    startTime.setHours(startTime.getHours() + spec.hours);
                }
                
                if (spec.minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.minutes);
                }
                
                const durationMs = (spec.duration_hours || 2) * 60 * 60 * 1000;
                endTime = new Date(startTime.getTime() + durationMs);
                
                const tzOffset = spec.timezone_offset || 0;
                if (tzOffset !== 0) {
                    const sign = tzOffset >= 0 ? '+' : '-';
                    const hours = Math.abs(Math.floor(tzOffset));
                    const minutes = Math.abs((tzOffset % 1) * 60);
                    const tzString = `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                    
                    processedEvent.start_time = this.formatDateTimeWithTZ(startTime, tzString);
                    processedEvent.end_time = this.formatDateTimeWithTZ(endTime, tzString);
                } else {
                    processedEvent.start_time = this.formatDateTime(startTime);
                    processedEvent.end_time = this.formatDateTime(endTime);
                }
                
            } else if (type === 'sunrise_relative') {
                const sunrise = filterModule.getNextSunrise();
                
                startTime = new Date(sunrise);
                if (spec.start_offset_hours) {
                    startTime.setHours(startTime.getHours() + spec.start_offset_hours);
                }
                if (spec.start_offset_minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.start_offset_minutes);
                }
                
                endTime = new Date(sunrise);
                if (spec.end_offset_hours) {
                    endTime.setHours(endTime.getHours() + spec.end_offset_hours);
                }
                if (spec.end_offset_minutes) {
                    endTime.setMinutes(endTime.getMinutes() + spec.end_offset_minutes);
                }
                
                processedEvent.start_time = this.formatDateTime(startTime);
                processedEvent.end_time = this.formatDateTime(endTime);
            }
            
            processedEvent.published_at = this.formatDateTime(now);
            
            return processedEvent;
        });
    }
    
    /**
     * Format date as ISO 8601 without timezone
     * @param {Date} date - Date to format
     * @returns {string} Formatted date string
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
        const message = bookmarked ? '❤️ Event bookmarked!' : '🤍 Bookmark removed';
        
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
