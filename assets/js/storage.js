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
        this.bookmarks = this.loadBookmarks();
        this.browserFeatures = this.detectBrowserFeatures();
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
