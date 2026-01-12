/**
 * TemplateEngine Module
 * 
 * Handles event template processing for dynamic/recurring events.
 * Extracted from utils.js to reduce complexity.
 * 
 * KISS: Strategy pattern for different template types
 */

class TemplateEngine {
    constructor(config) {
        this.config = config;
    }
    
    /**
     * Process template events (dynamic event generation)
     * @param {Array} events - Events to process
     * @param {Object} filterModule - EventFilter instance for time calculations
     * @returns {Array} Processed events
     */
    processTemplateEvents(events, filterModule) {
        if (!events || events.length === 0) return [];
        
        const processedEvents = [];
        
        events.forEach(event => {
            if (event.template && event.template.enabled) {
                // Generate dynamic events from template
                const generated = this.generateFromTemplate(event, filterModule);
                processedEvents.push(...generated);
            } else {
                // Regular event, no processing needed
                processedEvents.push(event);
            }
        });
        
        this.log(`Processed ${events.length} events → ${processedEvents.length} events (with templates)`);
        return processedEvents;
    }
    
    /**
     * Generate events from template specification
     * @param {Object} event - Template event
     * @param {Object} filterModule - EventFilter instance
     * @returns {Array} Generated events
     */
    generateFromTemplate(event, filterModule) {
        const template = event.template;
        const type = template.type;
        
        // Strategy pattern: route to appropriate processor
        if (type === 'offset') {
            return this.processOffsetTemplate(event, template);
        } else if (type === 'sunrise_relative') {
            return this.processSunriseTemplate(event, template, filterModule);
        }
        
        // Unknown template type - return original event
        this.log(`Unknown template type: ${type}`);
        return [event];
    }
    
    /**
     * Process offset-based template (relative to current time)
     * @param {Object} event - Template event
     * @param {Object} template - Template specification
     * @returns {Array} Generated events
     */
    processOffsetTemplate(event, template) {
        const spec = template.spec;
        const count = spec.count || 1;
        const events = [];
        
        const now = new Date();
        
        for (let i = 0; i < count; i++) {
            const offsetMinutes = this.parseTimeOffset(spec.offset);
            const incrementMinutes = spec.increment ? this.parseTimeOffset(spec.increment) : 0;
            
            const totalOffset = offsetMinutes + (i * incrementMinutes);
            const eventTime = new Date(now.getTime() + totalOffset * 60000);
            
            // Create event instance
            const instance = this.createEventInstance(event, eventTime, i);
            events.push(instance);
        }
        
        return events;
    }
    
    /**
     * Process sunrise-relative template
     * @param {Object} event - Template event
     * @param {Object} template - Template specification
     * @param {Object} filterModule - EventFilter instance
     * @returns {Array} Generated events
     */
    processSunriseTemplate(event, template, filterModule) {
        const spec = template.spec;
        const count = spec.count || 1;
        const events = [];
        
        const now = new Date();
        
        for (let i = 0; i < count; i++) {
            // Get next sunrise (uses EventFilter's sunrise calculation)
            const sunriseTime = filterModule ? filterModule.getNextSunrise() : new Date(now.getTime() + 12 * 3600000);
            
            // Apply offset from sunrise
            const offsetMinutes = this.parseTimeOffset(spec.offset_from_sunrise);
            const eventTime = new Date(sunriseTime.getTime() + offsetMinutes * 60000);
            
            // Apply increment for subsequent events
            const incrementMinutes = spec.increment ? this.parseTimeOffset(spec.increment) : 0;
            eventTime.setTime(eventTime.getTime() + (i * incrementMinutes * 60000));
            
            // Create event instance
            const instance = this.createEventInstance(event, eventTime, i);
            events.push(instance);
        }
        
        return events;
    }
    
    /**
     * Parse time offset string to minutes
     * Supports formats: "30m", "2h", "1h30m"
     * @param {string} offset - Time offset string
     * @returns {number} Offset in minutes
     */
    parseTimeOffset(offset) {
        if (!offset) return 0;
        
        let totalMinutes = 0;
        
        // Parse hours
        const hoursMatch = offset.match(/(\d+)h/);
        if (hoursMatch) {
            totalMinutes += parseInt(hoursMatch[1]) * 60;
        }
        
        // Parse minutes
        const minutesMatch = offset.match(/(\d+)m/);
        if (minutesMatch) {
            totalMinutes += parseInt(minutesMatch[1]);
        }
        
        // Handle negative offsets
        if (offset.startsWith('-')) {
            totalMinutes = -totalMinutes;
        }
        
        return totalMinutes;
    }
    
    /**
     * Create event instance from template
     * @param {Object} event - Template event
     * @param {Date} eventTime - Generated event time
     * @param {number} index - Instance index
     * @returns {Object} Event instance
     */
    createEventInstance(event, eventTime, index) {
        const instance = { ...event };
        
        // Generate unique ID
        instance.id = `${event.id}_t${index}`;
        
        // Set start time
        instance.start_time = eventTime.toISOString();
        
        // Set end time (if duration specified)
        if (event.template.spec.duration) {
            const durationMinutes = this.parseTimeOffset(event.template.spec.duration);
            const endTime = new Date(eventTime.getTime() + durationMinutes * 60000);
            instance.end_time = endTime.toISOString();
        }
        
        // Remove template specification from instance
        delete instance.template;
        
        return instance;
    }
    
    /**
     * Log helper
     * @param {string} message - Message to log
     * @param  {...any} args - Additional arguments
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[TemplateEngine]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TemplateEngine;
}
