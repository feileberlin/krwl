/**
 * EventStorage Module
 * 
 * Handles all localStorage/cookie operations for:
 * - Filter settings persistence
 * - Bookmark management
 * - Browser feature detection
 * 
 * KISS: Single responsibility - data persistence only
 */

class EventStorage {
    constructor(config) {
        this.config = config;
        this.MAX_BOOKMARKS = 15;
        this.MAX_CUSTOM_LOCATIONS = 10;
        this.bookmarks = this.loadBookmarks();  // Load bookmarks BEFORE custom locations
        this.customLocations = this.loadCustomLocations();
        this.browserFeatures = this.detectBrowserFeatures();
        
        // Initialize custom locations with predefined locations if empty
        this.initializeDefaultCustomLocations();
    }
    
    /**
     * Initialize custom locations with predefined locations from config
     * Only runs once when localStorage is empty
     */
    initializeDefaultCustomLocations() {
        // Only initialize if custom locations are empty
        if (this.customLocations.length > 0) {
            return;
        }
        
        // Get predefined locations from config
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        
        // Copy predefined locations to custom locations
        predefinedLocs.forEach((loc) => {
            this.customLocations.push({
                id: `custom_${loc.name}_${Date.now()}`,
                name: loc.display_name,
                lat: loc.lat,
                lon: loc.lon,
                created: new Date().toISOString(),
                fromPredefined: true
            });
        });
        
        // Save if we added any
        if (this.customLocations.length > 0) {
            this.saveCustomLocations();
            this.log('Initialized custom locations from predefined locations', this.customLocations);
        }
    }
    
    /**
     * Feature detection for browser capabilities
     * @returns {Object} Object with feature availability flags
     */
    detectBrowserFeatures() {
        const features = {
            localStorage: false,
            backdropFilter: false
        };
        
        // Test localStorage
        try {
            const testKey = '__krwl_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            features.localStorage = true;
        } catch (e) {
            features.localStorage = false;
        }
        
        // Test backdrop-filter support
        const testElement = document.createElement('div');
        const backdropFilterSupport = 
            testElement.style.backdropFilter !== undefined ||
            testElement.style.webkitBackdropFilter !== undefined;
        features.backdropFilter = backdropFilterSupport;
        
        return features;
    }
    
    /**
     * Check if bookmarking features should be enabled
     * Requires localStorage and backdrop-filter support
     * @returns {boolean} True if bookmarking is supported
     */
    isBookmarkingSupported() {
        return this.browserFeatures.localStorage && this.browserFeatures.backdropFilter;
    }
    
    /**
     * Save current filter settings to localStorage
     * Note: category and timeFilter are NOT saved (reset to defaults on reload)
     * @param {Object} filters - Filter settings object
     */
    saveFiltersToCookie(filters) {
        try {
            // Only save distance and location preferences
            // category and timeFilter are always reset to defaults on reload
            const filtersToSave = {
                maxDistance: filters.maxDistance,
                locationType: filters.locationType,
                selectedPredefinedLocation: filters.selectedPredefinedLocation,
                selectedCustomLocation: filters.selectedCustomLocation,
                useCustomLocation: filters.useCustomLocation,
                customLat: filters.customLat,
                customLon: filters.customLon
            };
            const filterData = JSON.stringify(filtersToSave);
            localStorage.setItem('krwl_filters', filterData);
            this.log('Filters saved to localStorage (excluding category and timeFilter)');
        } catch (error) {
            console.warn('Failed to save filters:', error);
        }
    }
    
    /**
     * Load filter settings from localStorage
     * Always returns default values for category ('all') and timeFilter ('sunrise')
     * @returns {Object|null} Saved filter settings or null
     */
    loadFiltersFromCookie() {
        try {
            const filterData = localStorage.getItem('krwl_filters');
            if (filterData) {
                const savedFilters = JSON.parse(filterData);
                // Always reset category and timeFilter to defaults
                const filters = {
                    ...savedFilters,
                    category: 'all',
                    timeFilter: 'sunrise'
                };
                this.log('Filters loaded from localStorage (category and timeFilter reset to defaults)', filters);
                return filters;
            }
        } catch (error) {
            console.warn('Failed to load filters:', error);
        }
        return null;
    }
    
    /**
     * Load bookmarks from localStorage
     * @returns {Array} Array of bookmarked event IDs
     */
    loadBookmarks() {
        try {
            const bookmarksData = localStorage.getItem('krwl_bookmarks');
            if (bookmarksData) {
                const bookmarks = JSON.parse(bookmarksData);
                this.log('Bookmarks loaded from localStorage', bookmarks);
                return Array.isArray(bookmarks) ? bookmarks : [];
            }
        } catch (error) {
            console.warn('Failed to load bookmarks:', error);
        }
        return [];
    }
    
    /**
     * Save bookmarks to localStorage
     */
    saveBookmarks() {
        try {
            const bookmarksData = JSON.stringify(this.bookmarks);
            localStorage.setItem('krwl_bookmarks', bookmarksData);
            this.log('Bookmarks saved to localStorage', this.bookmarks);
        } catch (error) {
            console.warn('Failed to save bookmarks:', error);
        }
    }
    
    /**
     * Toggle bookmark for an event
     * @param {string} eventId - Event ID to bookmark/unbookmark
     * @returns {boolean} True if bookmarked, false if unbookmarked
     */
    toggleBookmark(eventId) {
        const index = this.bookmarks.indexOf(eventId);
        
        if (index !== -1) {
            // Remove bookmark
            this.bookmarks.splice(index, 1);
            this.saveBookmarks();
            this.log('Bookmark removed:', eventId);
            return false;
        } else {
            // Add bookmark (enforce 15-item limit)
            if (this.bookmarks.length >= this.MAX_BOOKMARKS) {
                // Remove oldest bookmark (first in array)
                const removed = this.bookmarks.shift();
                this.log('Max bookmarks reached, removed oldest:', removed);
            }
            this.bookmarks.push(eventId);
            this.saveBookmarks();
            this.log('Bookmark added:', eventId);
            return true;
        }
    }
    
    /**
     * Check if an event is bookmarked
     * @param {string} eventId - Event ID to check
     * @returns {boolean} True if bookmarked
     */
    isBookmarked(eventId) {
        return this.bookmarks.includes(eventId);
    }
    
    /**
     * Get all bookmarked event IDs
     * @returns {Array} Array of bookmarked event IDs
     */
    getBookmarks() {
        return [...this.bookmarks];
    }
    
    /**
     * Load custom locations from localStorage
     * @returns {Array} Array of custom location objects
     */
    loadCustomLocations() {
        try {
            const locationsData = localStorage.getItem('krwl_custom_locations');
            if (locationsData) {
                const locations = JSON.parse(locationsData);
                this.log('Custom locations loaded from localStorage', locations);
                return Array.isArray(locations) ? locations : [];
            }
        } catch (error) {
            console.warn('Failed to load custom locations:', error);
        }
        return [];
    }
    
    /**
     * Save custom locations to localStorage
     */
    saveCustomLocations() {
        try {
            const locationsData = JSON.stringify(this.customLocations);
            localStorage.setItem('krwl_custom_locations', locationsData);
            this.log('Custom locations saved to localStorage', this.customLocations);
        } catch (error) {
            console.warn('Failed to save custom locations:', error);
        }
    }
    
    /**
     * Add a new custom location
     * @param {Object} location - Location object {name, lat, lon}
     * @returns {boolean} True if added successfully
     */
    addCustomLocation(location) {
        if (!location || !location.name || location.lat === undefined || location.lon === undefined) {
            console.warn('Invalid location object');
            return false;
        }
        
        // Check if we've reached the limit
        if (this.customLocations.length >= this.MAX_CUSTOM_LOCATIONS) {
            console.warn('Maximum custom locations reached');
            return false;
        }
        
        // Add unique ID based on timestamp
        const newLocation = {
            id: `custom_${Date.now()}`,
            name: location.name,
            lat: location.lat,
            lon: location.lon,
            created: new Date().toISOString()
        };
        
        this.customLocations.push(newLocation);
        this.saveCustomLocations();
        this.log('Custom location added:', newLocation);
        return true;
    }
    
    /**
     * Update an existing custom location
     * @param {string} id - Location ID
     * @param {Object} updates - Updates object {name?, lat?, lon?}
     * @returns {boolean} True if updated successfully
     */
    updateCustomLocation(id, updates) {
        const index = this.customLocations.findIndex(loc => loc.id === id);
        if (index === -1) {
            console.warn('Custom location not found:', id);
            return false;
        }
        
        // Apply updates
        if (updates.name !== undefined) this.customLocations[index].name = updates.name;
        if (updates.lat !== undefined) this.customLocations[index].lat = updates.lat;
        if (updates.lon !== undefined) this.customLocations[index].lon = updates.lon;
        
        this.saveCustomLocations();
        this.log('Custom location updated:', this.customLocations[index]);
        return true;
    }
    
    /**
     * Reset a predefined custom location to its original config.json values
     * @param {string} id - Location ID
     * @returns {boolean} True if reset successfully
     */
    resetCustomLocation(id) {
        const location = this.getCustomLocationById(id);
        if (!location) {
            console.warn('Custom location not found:', id);
            return false;
        }
        
        if (!location.fromPredefined) {
            console.warn('Cannot reset non-predefined location:', id);
            return false;
        }
        
        // Find the original predefined location from config
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        const originalLoc = predefinedLocs.find(loc => 
            loc.display_name === location.name || 
            location.id.includes(loc.name)
        );
        
        if (!originalLoc) {
            console.warn('Original predefined location not found in config:', location.name);
            return false;
        }
        
        // Reset to original values
        const index = this.customLocations.findIndex(loc => loc.id === id);
        if (index !== -1) {
            this.customLocations[index].name = originalLoc.display_name;
            this.customLocations[index].lat = originalLoc.lat;
            this.customLocations[index].lon = originalLoc.lon;
            this.saveCustomLocations();
            this.log('Custom location reset to original:', this.customLocations[index]);
            return true;
        }
        
        return false;
    }
    
    /**
     * Delete a custom location
     * @param {string} id - Location ID
     * @returns {boolean} True if deleted successfully
     */
    deleteCustomLocation(id) {
        const index = this.customLocations.findIndex(loc => loc.id === id);
        if (index === -1) {
            console.warn('Custom location not found:', id);
            return false;
        }
        
        const deleted = this.customLocations.splice(index, 1);
        this.saveCustomLocations();
        this.log('Custom location deleted:', deleted[0]);
        return true;
    }
    
    /**
     * Get all custom locations
     * @returns {Array} Array of custom location objects
     */
    getCustomLocations() {
        return [...this.customLocations];
    }
    
    /**
     * Get a custom location by ID
     * @param {string} id - Location ID
     * @returns {Object|null} Location object or null if not found
     */
    getCustomLocationById(id) {
        return this.customLocations.find(loc => loc.id === id) || null;
    }
    
    /**
     * Check if a predefined location has been modified from its original config.json values
     * @param {string} id - Location ID
     * @returns {boolean} True if location has been modified, false if unchanged or not predefined
     */
    isPredefinedLocationModified(id) {
        const location = this.getCustomLocationById(id);
        if (!location || !location.fromPredefined) {
            return false;
        }
        
        // Find the original predefined location from config
        const predefinedLocs = this.config?.map?.predefined_locations || [];
        const originalLoc = predefinedLocs.find(loc => 
            loc.display_name === location.name || 
            location.id.includes(loc.name)
        );
        
        if (!originalLoc) {
            // If we can't find the original, assume it's modified
            return true;
        }
        
        // Check if any values differ from original
        const nameMatches = location.name === originalLoc.display_name;
        const latMatches = Math.abs(location.lat - originalLoc.lat) < 0.0001; // Allow tiny floating point differences
        const lonMatches = Math.abs(location.lon - originalLoc.lon) < 0.0001;
        
        return !(nameMatches && latMatches && lonMatches);
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Storage]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventStorage;
}
