/**
 * FilterDescriptionUI Module
 * 
 * Handles filter bar description updates (semantic event count sentence).
 * Extracted from app.js to reduce complexity.
 * 
 * KISS: Data-driven approach using lookup tables instead of switch statements
 * Now with i18n support for multilanguage UI
 */

class FilterDescriptionUI {
    constructor(config, i18n = null) {
        this.config = config;
        this.i18n = i18n;
        
        // Lookup tables for filter descriptions (KISS: replace switch statements)
        // Now using translation keys instead of hardcoded strings
        this.TIME_FILTER_KEYS = {
            'sunrise': 'filter_bar.time_filters.sunrise',
            'sunday-primetime': 'filter_bar.time_filters.sunday_primetime',
            'full-moon': 'filter_bar.time_filters.full_moon',
            '6h': 'filter_bar.time_filters.6h',
            '12h': 'filter_bar.time_filters.12h',
            '24h': 'filter_bar.time_filters.24h',
            '48h': 'filter_bar.time_filters.48h',
            'all': 'filter_bar.time_filters.all'
        };
        
        // Distance values map to translation keys
        // Note: Using underscore instead of dot to avoid conflicts with dot-notation parsing
        this.DISTANCE_FILTER_KEYS = {
            2: 'filter_bar.distance_filters.2',
            3.75: 'filter_bar.distance_filters.3_75',
            12.5: 'filter_bar.distance_filters.12_5',
            60: 'filter_bar.distance_filters.60'
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
        this.updateWeatherDescription();
    }
    
    /**
     * Update event count and category display
     * @param {number} count - Number of events
     * @param {string} category - Selected category (may be group key like "historical-monuments")
     */
    updateEventCount(count, category) {
        const element = document.getElementById('filter-bar-event-count');
        if (!element) return;
        
        // Get singular/plural form from translations
        const eventWord = this.i18n 
            ? (count !== 1 
                ? this.i18n.t('filter_bar.event_count.plural')
                : this.i18n.t('filter_bar.event_count.singular'))
            : (count !== 1 ? 'events' : 'event');  // Fallback
        
        // Convert category to display text
        let categoryText = '';
        if (category !== 'all') {
            // Check if this is a group key (kebab-case with dash)
            if (category.includes('-')) {
                // Try to get translation first
                const categoryKey = `categories.${category.replace(/-/g, '_')}`;
                categoryText = this.i18n 
                    ? this.i18n.t(categoryKey)
                    : category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                
                // Special cases for better display (if translation not found)
                if (categoryText === categoryKey && category === 'historical-monuments') {
                    categoryText = this.i18n 
                        ? this.i18n.t('categories.historical_monuments')
                        : 'Historical & Monuments';
                }
                
                categoryText += ' ';
            } else {
                // Simple category, just use as is
                categoryText = `${category} `;
            }
        }
        
        element.textContent = `${count} ${categoryText}${eventWord}`;
    }
    
    /**
     * Update time range description
     * @param {string} timeFilter - Selected time filter
     */
    updateTimeDescription(timeFilter) {
        const element = document.getElementById('filter-bar-time-range');
        if (!element) return;
        
        // Get translated description
        const translationKey = this.TIME_FILTER_KEYS[timeFilter];
        const description = this.i18n && translationKey
            ? this.i18n.t(translationKey)
            : (translationKey ? timeFilter : 'upcoming');  // Fallback
        
        // Note: Detailed info (dates/times) is shown in dropdown options only
        // See event-listeners.js setupTimeFilter() for dropdown labels
        
        element.textContent = `${description}`;
    }
    
    /**
     * Update distance description (travel time estimate)
     * @param {number} distance - Distance in km
     */
    updateDistanceDescription(distance) {
        const element = document.getElementById('filter-bar-distance');
        if (!element) return;
        
        // Get translated description or fallback to km
        const translationKey = this.DISTANCE_FILTER_KEYS[distance];
        const description = this.i18n && translationKey
            ? this.i18n.t(translationKey)
            : (translationKey 
                ? `within ${distance} km` 
                : this.i18n 
                    ? this.i18n.t('filter_bar.distance_filters.within_km', { distance })
                    : `within ${distance} km`);  // Final fallback
        
        element.textContent = `${description}`;
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
        element.textContent = `${description}`;
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
        
        // Custom location - use stored name (KISS: no lookup needed)
        if (filters.locationType === 'custom' && filters.selectedCustomLocationName) {
            return this.i18n
                ? this.i18n.t('filter_bar.location_filters.from_location', { 
                    location: filters.selectedCustomLocationName 
                  })
                : `from ${filters.selectedCustomLocationName}`;  // Fallback
        }
        
        // Geolocation - always show "from here" when geolocation is active
        if (filters.locationType === 'geolocation') {
            return this.i18n 
                ? this.i18n.t('filter_bar.location_filters.from_here')
                : 'from here';  // Fallback
        }
        
        return this.i18n 
            ? this.i18n.t('filter_bar.location_filters.from_here')
            : 'from here';  // Fallback
    }
    
    /**
     * Get predefined location text
     * @param {number} locationIndex - Index of predefined location
     * @returns {string} Location text
     */
    getPredefinedLocationText(locationIndex) {
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        const selectedLoc = predefinedLocs[locationIndex];
        
        if (!selectedLoc) {
            return this.i18n 
                ? this.i18n.t('filter_bar.location_filters.from_here')
                : 'from here';  // Fallback
        }
        
        return this.i18n
            ? this.i18n.t('filter_bar.location_filters.from_location', { 
                location: selectedLoc.display_name 
              })
            : `from ${selectedLoc.display_name}`;  // Fallback
    }
    
    /**
     * Update weather description (dresscode display)
     */
    updateWeatherDescription() {
        const element = document.getElementById('filter-bar-weather');
        if (!element) return;
        
        // Check if weather is enabled and should be displayed
        if (!this.config?.weather?.enabled || !this.config?.weather?.display?.show_in_filter_bar) {
            element.style.display = 'none';
            return;
        }
        
        // Get weather data from APP_CONFIG (embedded by backend)
        const weatherData = window.APP_CONFIG?.weather?.data;
        if (!weatherData || !weatherData.dresscode) {
            element.style.display = 'none';
            return;
        }
        
        // Display dresscode with format: "not without a {dresscode}" (lowercase)
        const dresscodeRaw = weatherData.dresscode.toLowerCase();
        
        // Translate dresscode value using i18n.t('dresscodes.KEY')
        const dresscode = this.i18n
            ? (this.i18n.t(`dresscodes.${dresscodeRaw}`) || dresscodeRaw)
            : dresscodeRaw;
        
        const text = this.i18n
            ? this.i18n.t('filter_bar.weather.not_without', { dresscode })
            : `not without a ${dresscode}`;  // Fallback
        
        element.textContent = text;
        element.style.display = '';  // Show the element
        
        this.log('Weather description updated:', weatherData.dresscode);
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
