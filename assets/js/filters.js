/**
 * EventFilter Module
 * 
 * Handles event filtering logic:
 * - Time-based filters (sunrise, full moon, hours)
 * - Distance-based filters
 * - Category filters
 * - Location calculations
 * 
 * KISS: Single responsibility - filtering logic only
 */

class EventFilter {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
    }
    
    /**
     * Calculate distance between two lat/lon coordinates (Haversine formula)
     * @param {number} lat1 - Latitude of first point
     * @param {number} lon1 - Longitude of first point
     * @param {number} lat2 - Latitude of second point
     * @param {number} lon2 - Longitude of second point
     * @returns {number} Distance in kilometers
     */
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    /**
     * Get maximum event time based on filter
     * @param {string} timeFilter - Time filter value (sunrise, 6h, 12h, etc.)
     * @returns {Date} Maximum event time
     */
    getMaxEventTime(timeFilter) {
        const now = new Date();
        
        switch (timeFilter) {
            case 'sunrise':
                return this.getNextSunrise();
                
            case 'sunday-primetime':
                return this.getNextSundayPrimetime();
                
            case 'full-moon':
                return this.getNextFullMoonMorning();
                
            case '6h':
                return new Date(now.getTime() + 6 * 60 * 60 * 1000);
                
            case '12h':
                return new Date(now.getTime() + 12 * 60 * 60 * 1000);
                
            case '24h':
                return new Date(now.getTime() + 24 * 60 * 60 * 1000);
                
            case '48h':
                return new Date(now.getTime() + 48 * 60 * 60 * 1000);
                
            case 'all':
                return new Date(now.getFullYear() + 10, 11, 31);
                
            default:
                return this.getNextSunrise();
        }
    }
    
    /**
     * Get next sunrise time (simplified: 6 AM)
     * @returns {Date} Next sunrise
     */
    getNextSunrise() {
        const now = new Date();
        const sunrise = new Date(now);
        sunrise.setHours(6, 0, 0, 0);
        
        if (now.getHours() >= 6) {
            sunrise.setDate(sunrise.getDate() + 1);
        }
        
        return sunrise;
    }
    
    /**
     * Get next Sunday at primetime (20:15)
     * @returns {Date} Next Sunday at 20:15
     */
    getNextSundayPrimetime() {
        const now = new Date();
        const result = new Date(now);
        
        // Get current day of week (0 = Sunday, 1 = Monday, etc.)
        const currentDay = now.getDay();
        
        // Calculate days until next Sunday
        let daysUntilSunday;
        if (currentDay === 0) {
            // It's Sunday - check if we're past 20:15
            const currentTime = now.getHours() * 60 + now.getMinutes();
            const primetimeMinutes = 20 * 60 + 15;
            
            if (currentTime >= primetimeMinutes) {
                daysUntilSunday = 7;
            } else {
                daysUntilSunday = 0;
            }
        } else {
            daysUntilSunday = 7 - currentDay;
        }
        
        result.setDate(result.getDate() + daysUntilSunday);
        result.setHours(20, 15, 0, 0);
        
        return result;
    }
    
    /**
     * Get morning after next full moon following next Sunday
     * @returns {Date} 6am on day after next full moon
     */
    getNextFullMoonMorning() {
        const nextSunday = new Date(this.getNextSundayPrimetime().getTime());
        nextSunday.setHours(0, 0, 0, 0);
        
        // Known full moon: January 6, 2000, 18:14 UTC
        const knownFullMoon = new Date(Date.UTC(2000, 0, 6, 18, 14, 0));
        
        // Lunar cycle length in milliseconds
        const lunarCycle = 29.53058770576 * 24 * 60 * 60 * 1000;
        
        // Calculate cycles since known full moon
        const now = new Date();
        const timeSinceKnownFullMoon = now.getTime() - knownFullMoon.getTime();
        const cyclesSinceKnown = Math.floor(timeSinceKnownFullMoon / lunarCycle);
        
        // Find first full moon after next Sunday
        let fullMoon = new Date(knownFullMoon.getTime() + cyclesSinceKnown * lunarCycle);
        
        while (fullMoon <= nextSunday) {
            fullMoon = new Date(fullMoon.getTime() + lunarCycle);
        }
        
        // Set to 6am of day after full moon
        const dayAfterFullMoon = new Date(fullMoon);
        dayAfterFullMoon.setDate(dayAfterFullMoon.getDate() + 1);
        dayAfterFullMoon.setHours(6, 0, 0, 0);
        
        return dayAfterFullMoon;
    }
    
    /**
     * Filter events based on current filter settings
     * @param {Array} events - All events
     * @param {Object} filters - Filter settings
     * @param {Object} referenceLocation - Location to calculate distance from
     * @returns {Array} Filtered events
     */
    filterEvents(events, filters, referenceLocation) {
        const maxEventTime = this.getMaxEventTime(filters.timeFilter);
        const maxDistance = filters.maxDistance;
        const category = filters.category;
        
        const filtered = events.filter(event => {
            // Always include bookmarked events
            if (this.storage.isBookmarked(event.id)) {
                // Calculate distance even for bookmarked events
                if (referenceLocation && event.location) {
                    const distance = this.calculateDistance(
                        referenceLocation.lat,
                        referenceLocation.lon,
                        event.location.lat,
                        event.location.lon
                    );
                    event.distance = distance;
                }
                return true;
            }
            
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                return false;
            }
            
            // Filter by category
            if (category !== 'all' && event.category !== category) {
                return false;
            }
            
            // Filter by distance if location is available
            if (referenceLocation && event.location) {
                const distance = this.calculateDistance(
                    referenceLocation.lat,
                    referenceLocation.lon,
                    event.location.lat,
                    event.location.lon
                );
                event.distance = distance;
                
                if (distance > maxDistance) {
                    return false;
                }
            }
            
            return true;
        });
        
        return filtered;
    }
    
    /**
     * Count category occurrences under current filter conditions (excluding category filter)
     * @param {Array} events - All events
     * @param {Object} filters - Filter settings (category ignored)
     * @param {Object} referenceLocation - Location to calculate distance from
     * @returns {Object} Map of category names to their occurrence counts
     */
    countCategoriesUnderFilters(events, filters, referenceLocation) {
        const maxEventTime = this.getMaxEventTime(filters.timeFilter);
        const maxDistance = filters.maxDistance;
        
        const categoryCounts = {};
        
        events.forEach(event => {
            // Count bookmarked events regardless of other filters
            if (this.storage.isBookmarked(event.id)) {
                const cat = event.category || 'uncategorized';
                categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
                return;
            }
            
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                return;
            }
            
            // Filter by distance if location is available
            if (referenceLocation && event.location) {
                const distance = this.calculateDistance(
                    referenceLocation.lat,
                    referenceLocation.lon,
                    event.location.lat,
                    event.location.lon
                );
                
                if (distance > maxDistance) {
                    return;
                }
            }
            
            // Count this event's category
            const cat = event.category || 'uncategorized';
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
        
        return categoryCounts;
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Filter]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventFilter;
}
