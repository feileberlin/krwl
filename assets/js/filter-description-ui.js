/**
 * FilterDescriptionUI Module
 * 
 * Handles filter bar description updates (semantic event count sentence).
 * Extracted from app.js to reduce complexity.
 * 
 * KISS: Data-driven approach using lookup tables instead of switch statements
 */

class FilterDescriptionUI {
    constructor(config) {
        this.config = config;
        
        // Lookup tables for filter descriptions (KISS: replace switch statements)
        this.TIME_DESCRIPTIONS = {
            'sunrise': 'till sunrise',
            'sunday-primetime': "till Sunday's primetime",
            'full-moon': 'till next full moon',
            '6h': 'in the next 6 hours',
            '12h': 'in the next 12 hours',
            '24h': 'in the next 24 hours',
            '48h': 'in the next 48 hours',
            'all': 'upcoming'
        };
        
        this.DISTANCE_DESCRIPTIONS = {
            2: 'within 30 min walk',
            3.75: 'within 30 min bicycle ride',
            12.5: 'within 30 min public transport',
            60: 'within 60 min car sharing'
        };
    }
    
    /**
     * Update all filter description elements
     * @param {number} count - Number of filtered events
     * @param {Object} filters - Current filter settings
     * @param {Object} userLocation - User's current location (for "from here")
     */
    update(count, filters, userLocation = null) {
        this.updateEventCount(count, filters.category);
        this.updateTimeDescription(filters.timeFilter);
        this.updateDistanceDescription(filters.maxDistance);
        this.updateLocationDescription(filters, userLocation);
    }
    
    /**
     * Update event count and category display
     * @param {number} count - Number of events
     * @param {string} category - Selected category
     */
    updateEventCount(count, category) {
        const element = document.getElementById('filter-bar-event-count');
        if (!element) return;
        
        const plural = count !== 1 ? 's' : '';
        const categoryText = category === 'all' ? '' : `${category} `;
        
        element.textContent = `[${count} ${categoryText}event${plural}]`;
    }
    
    /**
     * Update time range description
     * @param {string} timeFilter - Selected time filter
     */
    updateTimeDescription(timeFilter) {
        const element = document.getElementById('filter-bar-time-range');
        if (!element) return;
        
        const description = this.TIME_DESCRIPTIONS[timeFilter] || 'upcoming';
        element.textContent = `[${description}]`;
    }
    
    /**
     * Update distance description (travel time estimate)
     * @param {number} distance - Distance in km
     */
    updateDistanceDescription(distance) {
        const element = document.getElementById('filter-bar-distance');
        if (!element) return;
        
        // Use lookup table or fallback to km
        const description = this.DISTANCE_DESCRIPTIONS[distance] || `within ${distance} km`;
        element.textContent = `[${description}]`;
    }
    
    /**
     * Update location description
     * @param {Object} filters - Filter settings
     * @param {Object} userLocation - User's current location
     */
    updateLocationDescription(filters, userLocation) {
        const element = document.getElementById('filter-bar-location');
        if (!element) return;
        
        let description = this.getLocationText(filters, userLocation);
        element.textContent = `[${description}]`;
    }
    
    /**
     * Get location description text
     * @param {Object} filters - Filter settings
     * @param {Object} userLocation - User's current location
     * @returns {string} Location description
     */
    getLocationText(filters, userLocation) {
        // Predefined location
        if (filters.locationType === 'predefined' && filters.selectedPredefinedLocation !== null) {
            return this.getPredefinedLocationText(filters.selectedPredefinedLocation);
        }
        
        // Custom location
        if (filters.locationType === 'custom' && filters.customLat && filters.customLon) {
            return 'from custom location';
        }
        
        // Geolocation - always show "from here" when geolocation is active
        if (filters.locationType === 'geolocation') {
            return window.i18n ? window.i18n.t('filters.locations.geolocation') : 'from here';
        }
        
        return 'from here';
    }
    
    /**
     * Get predefined location text with i18n support
     * @param {number} locationIndex - Index of predefined location
     * @returns {string} Location text
     */
    getPredefinedLocationText(locationIndex) {
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        const selectedLoc = predefinedLocs[locationIndex];
        
        if (!selectedLoc) return 'from here';
        
        // Try to get translated name, fallback to display_name
        const translatedName = window.i18n ? 
            window.i18n.t(`filters.predefined_locations.${selectedLoc.name}`) : 
            selectedLoc.display_name;
        
        const prefix = window.i18n ? window.i18n.t('filters.locations.prefix') : 'from';
        
        return `${prefix} ${translatedName}`;
    }
    
    /**
     * Log helper
     * @param {string} message - Message to log
     * @param  {...any} args - Additional arguments
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[FilterDescriptionUI]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FilterDescriptionUI;
}
