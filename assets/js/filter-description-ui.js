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
        this.filterBar = document.getElementById('event-filter-bar');
        this.typingMode = this.config?.filter_sentence?.effect || 'terminal';
        this.typingSpeed = this.config?.filter_sentence?.typing_speed_ms || 34;
        if (this.filterBar) {
            this.filterBar.dataset.filterEffect = this.typingMode;
        }
        
        // Lookup tables for filter descriptions (KISS: replace switch statements)
        this.TIME_DESCRIPTIONS = {
            'sunrise': 'til sunrise',
            'sunday-primetime': "til Sunday's primetime",
            'full-moon': 'til full moon',
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

    typeText(element, text) {
        if (!element) return;
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            element.textContent = text;
            return;
        }
        clearTimeout(element._typingTimer);
        const minTypoLength = 6; // Minimum length before adding a typo (avoid short labels)
        const defaultTypoIndex = 3; // Early typo position for quick correction
        const typoIndex = text.length > minTypoLength ? Math.min(defaultTypoIndex, text.length - 2) : -1; // Keep typo off last char
        const typoChar = typoIndex > -1 ? 'x' : '';
        const frames = [];
        for (let i = 1; i <= text.length; i++) {
            if (i === typoIndex && typoChar) {
                frames.push(text.slice(0, i - 1) + typoChar);
                frames.push(text.slice(0, i - 1));
            }
            frames.push(text.slice(0, i));
        }
        const step = () => {
            if (!element.isConnected) {
                clearTimeout(element._typingTimer);
                return;
            }
            element.textContent = frames.shift() || text;
            if (frames.length) element._typingTimer = setTimeout(step, this.typingSpeed);
        };
        step();
    }
    
    /**
     * Update event count and category display
     * @param {number} count - Number of events
     * @param {string} category - Selected category (may be group key like "historical-monuments")
     */
    updateEventCount(count, category) {
        const element = document.getElementById('filter-bar-event-count');
        if (!element) return;
        
        const plural = count !== 1 ? 's' : '';
        
        // Convert category to display text
        let categoryText = '';
        if (category !== 'all') {
            // Check if this is a group key (kebab-case with dash)
            if (category.includes('-')) {
                // Convert group key to display label (e.g., "historical-monuments" -> "Historical & Monuments")
                categoryText = category
                    .split('-')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                
                // Special cases for better display
                if (category === 'historical-monuments') {
                    categoryText = 'Historical & Monuments';
                }
                
                categoryText += ' ';
            } else {
                // Simple category, just use as is
                categoryText = `${category} `;
            }
        }
        
        this.typeText(element, `${count} ${categoryText}event${plural}`);
    }
    
    /**
     * Update time range description
     * @param {string} timeFilter - Selected time filter
     */
    updateTimeDescription(timeFilter) {
        const element = document.getElementById('filter-bar-time-range');
        if (!element) return;
        
        // Simple descriptions for filter bar button (no extra info)
        const description = this.TIME_DESCRIPTIONS[timeFilter] || 'upcoming';
        
        // Note: Detailed info (dates/times) is shown in dropdown options only
        // See event-listeners.js setupTimeFilter() for dropdown labels
        
        this.typeText(element, `${description}`);
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
        this.typeText(element, `${description}`);
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
        this.typeText(element, `${description}`);
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
            return 'from here';
        }
        
        return 'from here';
    }
    
    /**
     * Get predefined location text
     * @param {number} locationIndex - Index of predefined location
     * @returns {string} Location text
     */
    getPredefinedLocationText(locationIndex) {
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        const selectedLoc = predefinedLocs[locationIndex];
        
        if (!selectedLoc) return 'from here';
        
        return `from ${selectedLoc.display_name}`;
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
