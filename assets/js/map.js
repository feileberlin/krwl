/**
 * MapManager Module
 * 
 * Handles all Leaflet.js map operations:
 * - Map initialization
 * - Event flyer management (no markers, just small flyer cards)
 * - User location tracking
 * - Map bounds and zoom
 * 
 * KISS: Single responsibility - map management only
 * 
 * UI PHILOSOPHY: Small "flyers" displayed next to event locations on the map
 * - No traditional markers (pins/icons)
 * - No popups that need to be clicked
 * - Events are immediately visible as compact cards
 */

// Constants for flyer positioning (offsetting flyers at same location)
const FLYER_OFFSET_RADIUS = 0.0005;   // ~50 meters offset for overlapping flyers
const FLYER_OFFSET_ANGLE = 45;        // Degrees between each offset flyer
const LOCATION_PRECISION = 4;         // Decimal places for location grouping (~11m precision)

class MapManager {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.map = null;
        this.flyers = [];           // Event flyer elements (was: markers)
        this.userLocation = null;
        this.locationCounts = {};   // Track flyers at same location for offset
        this.referenceMarker = null; // Track the reference location marker (user/predefined/custom)
        this.isFallbackMode = false; // Track if we're showing fallback event list
    }
    
    /**
     * Backward compatibility: return flyers as markers
     */
    get markers() {
        return this.flyers;
    }
    
    /**
     * Check if Leaflet is available
     * @returns {boolean} True if Leaflet is loaded
     */
    isLeafletAvailable() {
        return typeof L !== 'undefined' && typeof L.map === 'function';
    }
    
    /**
     * Initialize Leaflet map
     * @param {string} containerId - DOM element ID for map container
     * @returns {boolean} True if map initialized successfully
     */
    initMap(containerId = 'map') {
        // Check if Leaflet is available
        if (!this.isLeafletAvailable()) {
            console.warn('Leaflet library not available - map cannot be initialized');
            this.showMapFallback(containerId);
            return false;
        }
        
        // If retrying after fallback was shown, clear fallback content
        const container = document.getElementById(containerId);
        if (container && this.isFallbackMode) {
            container.innerHTML = ''; // Clear fallback HTML
            this.isFallbackMode = false; // Reset fallback flag
            this.log('Cleared fallback content, retrying map initialization');
        }
        
        const center = this.config.map.default_center;
        
        try {
            // Disable zoom controls - use keyboard shortcuts or pinch zoom
            this.map = L.map(containerId, {
                zoomControl: false,
                attributionControl: false
            }).setView([center.lat, center.lon], this.config.map.default_zoom);
            
            L.tileLayer(this.config.map.tile_provider, {
                attribution: this.config.map.attribution
            }).addTo(this.map);
            
            this.log('Map initialized', center);
            return true;
        } catch (error) {
            console.error('Map initialization error:', error);
            this.showMapFallback(containerId);
            return false;
        }
    }
    
    /**
     * Show fallback message when map cannot be initialized
     * @param {string} containerId - DOM element ID for map container
     */
    showMapFallback(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Create fallback with event list container (no prominent "unavailable" message)
        const fallback = document.createElement('div');
        fallback.className = 'map-fallback';
        fallback.innerHTML = `
            <div id="fallback-event-list" class="fallback-event-list" role="list" aria-label="Event list"></div>
        `;
        container.appendChild(fallback);
        
        // Mark that we're in fallback mode
        this.isFallbackMode = true;
        
        this.log('Map fallback displayed with event list container');
    }
    
    /**
     * Render events to fallback list when map is unavailable
     * @param {Array} events - Filtered events to display
     */
    renderFallbackEventList(events) {
        const listContainer = document.getElementById('fallback-event-list');
        if (!listContainer) return;
        
        // Clear existing content
        listContainer.innerHTML = '';
        
        if (events.length === 0) {
            listContainer.innerHTML = '<p class="fallback-no-events">No events match your current filters.</p>';
            return;
        }
        
        // Render each event as a card
        events.forEach(event => {
            const card = this.createFallbackEventCard(event);
            listContainer.appendChild(card);
        });
        
        this.log(`Rendered ${events.length} events to fallback list`);
    }
    
    /**
     * Create a fallback event card element
     * @param {Object} event - Event data
     * @returns {HTMLElement} Event card element
     */
    createFallbackEventCard(event) {
        const card = document.createElement('article');
        card.className = 'fallback-event-card';
        card.setAttribute('role', 'listitem');
        
        // Format date/time
        const startTime = new Date(event.start_time);
        const timeStr = startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = startTime.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
        
        // Distance info
        const distanceStr = event.distance !== undefined ? `${event.distance.toFixed(1)} km` : '';
        
        // Event URL link - the primary way users interact with fallback cards
        const urlHtml = event.url ? 
            `<a href="${this.escapeHtml(event.url)}" class="fallback-card-link" target="_blank" rel="noopener">More info →</a>` : '';
        
        // Build card HTML (escape content for XSS prevention)
        card.innerHTML = `
            <div class="fallback-card-time">${this.escapeHtml(timeStr)}</div>
            <div class="fallback-card-date">${this.escapeHtml(dateStr)}</div>
            <h3 class="fallback-card-title">${this.escapeHtml(event.title || 'Event')}</h3>
            <div class="fallback-card-location">${this.escapeHtml(event.location?.name || 'Unknown location')}</div>
            ${distanceStr ? `<div class="fallback-card-distance">${this.escapeHtml(distanceStr)}</div>` : ''}
            ${urlHtml}
        `;
        
        return card;
    }
    
    /**
     * Setup Leaflet event prevention on UI overlays
     * Prevents map interactions when clicking/scrolling on UI elements
     */
    setupLeafletEventPrevention() {
        if (typeof L === 'undefined' || !L.DomEvent) {
            this.log('Leaflet DomEvent not available, skipping event prevention');
            return;
        }
        
        // Prevent map interactions on filter bar
        const filterBar = document.getElementById('event-filter-bar');
        if (filterBar) {
            L.DomEvent.disableClickPropagation(filterBar);
            L.DomEvent.disableScrollPropagation(filterBar);
            this.log('Event prevention enabled for filter bar');
        }
        
        // Prevent map interactions on dashboard
        const dashboard = document.getElementById('dashboard-menu');
        if (dashboard) {
            L.DomEvent.disableClickPropagation(dashboard);
            L.DomEvent.disableScrollPropagation(dashboard);
            this.log('Event prevention enabled for dashboard');
        }
    }
    
    /**
     * Get user's geolocation
     * @param {Function} onSuccess - Callback with location {lat, lon}
     * @param {Function} onError - Callback with error
     * @param {boolean} centerMap - Whether to center map on user location (default: false)
     */
    getUserLocation(onSuccess, onError, centerMap = false) {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    this.log('User location obtained', this.userLocation);
                    
                    // Only center map if explicitly requested (e.g., user selected geolocation filter)
                    if (this.map && centerMap) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                        this.addUserMarker();
                    }
                    
                    if (onSuccess) onSuccess(this.userLocation);
                },
                (error) => {
                    console.error('Location error:', error);
                    
                    // Use default location as fallback for distance calculations
                    // But do NOT show a location card - user should select from predefined/custom locations
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    // Never center map on error fallback - keep region center
                    
                    if (onError) onError(error);
                }
            );
        } else {
            // Use default location as fallback for distance calculations
            // But do NOT show a location card - user should select from predefined/custom locations
            const defaultCenter = this.config.map.default_center;
            this.userLocation = {
                lat: defaultCenter.lat,
                lon: defaultCenter.lon
            };
            
            // Never center map when geolocation not supported - keep region center
            
            if (onError) onError(new Error('Geolocation not supported'));
        }
    }
    
    /**
     * Add user location marker to map
     * @deprecated Use updateReferenceMarker() instead for better control
     */
    addUserMarker() {
        if (!this.map || !this.userLocation) return;
        
        // Use the new unified method
        this.updateReferenceMarker(this.userLocation.lat, this.userLocation.lon, 'You are here');
    }
    
    /**
     * Update or create the reference location marker
     * This marker shows the reference point used for distance filtering
     * Now displayed as a card/flyer similar to event markers for better visibility
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {string} popupText - Popup text (optional, default: 'Reference location')
     */
    updateReferenceMarker(lat, lon, popupText = 'Reference location') {
        if (!this.map) return;
        
        // Remove old reference marker if it exists
        if (this.referenceMarker) {
            this.referenceMarker.remove();
            this.referenceMarker = null;
        }
        
        // Create location card HTML (similar to event flyers)
        const locationCardHtml = this.createLocationCardHtml(popupText);
        
        // Use divIcon to display as a card (matches event flyer pattern)
        const locationIcon = L.divIcon({
            className: 'location-flyer-container',
            html: locationCardHtml,
            iconSize: [140, 60],      // Compact card size
            iconAnchor: [70, 30],     // Center of card
            popupAnchor: [0, -30]     // Above card
        });
        
        // Create new reference marker with popup
        this.referenceMarker = L.marker([lat, lon], {
            icon: locationIcon,
            zIndexOffset: 1000 // Keep reference marker above event markers
        }).addTo(this.map).bindPopup(popupText);
        
        this.log('Reference marker updated as card', { lat, lon, popupText });
    }
    
    /**
     * Create HTML content for location card (similar to event flyer)
     * @param {string} label - Label text (e.g., 'You are here', 'Custom location')
     * @returns {string} HTML content for location card
     */
    createLocationCardHtml(label) {
        const displayLabel = label || 'My Location';
        const escapedLabel = this.escapeHtml(displayLabel);
        
        return `
            <div class="location-flyer" role="img" aria-label="${escapedLabel}">
                <div class="location-flyer-icon" aria-hidden="true">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="2" x2="5" y1="12" y2="12"></line>
                        <line x1="19" x2="22" y1="12" y2="12"></line>
                        <line x1="12" x2="12" y1="2" y2="5"></line>
                        <line x1="12" x2="12" y1="19" y2="22"></line>
                        <circle cx="12" cy="12" r="7"></circle>
                    </svg>
                </div>
                <div class="location-flyer-content">
                    <span class="location-flyer-label">${escapedLabel}</span>
                </div>
            </div>
        `.trim();
    }
    
    /**
     * Remove the reference location marker
     */
    removeReferenceMarker() {
        if (this.referenceMarker) {
            this.referenceMarker.remove();
            this.referenceMarker = null;
            this.log('Reference marker removed');
        }
    }
    
    /**
     * Add event flyer to map (replaces traditional markers)
     * Creates a small card-like flyer positioned next to the event location
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler
     * @returns {Object} Leaflet marker with flyer divIcon
     */
    addEventMarker(event, onClick) {
        if (!this.map || !event.location) return null;
        
        // Create flyer HTML content
        const flyerHtml = this.createFlyerHtml(event);
        
        // Use divIcon to create the flyer card
        const flyerIcon = L.divIcon({
            className: 'event-flyer-container',
            html: flyerHtml,
            iconSize: [140, 80],      // Compact flyer size
            iconAnchor: [70, 40],     // Center of flyer
            popupAnchor: [0, -40]     // Above flyer (not used, but keep for compatibility)
        });
        
        // Calculate offset for flyers at same location
        const locationKey = `${event.location.lat.toFixed(LOCATION_PRECISION)}_${event.location.lon.toFixed(LOCATION_PRECISION)}`;
        if (!this.locationCounts[locationKey]) {
            this.locationCounts[locationKey] = 0;
        }
        const offsetIndex = this.locationCounts[locationKey];
        this.locationCounts[locationKey]++;
        
        // Apply offset if there are multiple flyers at same location
        let lat = event.location.lat;
        let lon = event.location.lon;
        if (offsetIndex > 0) {
            const angle = (offsetIndex * FLYER_OFFSET_ANGLE) * (Math.PI / 180);
            lat += FLYER_OFFSET_RADIUS * Math.cos(angle);
            lon += FLYER_OFFSET_RADIUS * Math.sin(angle);
        }
        
        const flyer = L.marker([lat, lon], {
            icon: flyerIcon,
            customData: { id: event.id }
        }).addTo(this.map);
        
        // Add bookmark class if bookmarked
        if (this.storage.isBookmarked(event.id)) {
            flyer._icon.classList.add('event-flyer-bookmarked');
        }
        
        // Store event data on flyer (for backward compatibility)
        flyer.eventData = event;
        
        // NO popups - flyers show all info directly
        // Click opens detail panel only
        if (onClick) {
            flyer.on('click', () => onClick(event, flyer));
            
            // Add keyboard accessibility for Enter/Space key (WCAG 2.1.1)
            const flyerElement = flyer._icon?.querySelector('.event-flyer');
            if (flyerElement) {
                flyerElement.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onClick(event, flyer);
                    }
                });
            }
        }
        
        this.flyers.push(flyer);
        this.log('Flyer added for event', event.title);
        
        return flyer;
    }
    
    /**
     * Create HTML content for event flyer card
     * @param {Object} event - Event data
     * @returns {string} HTML content for flyer
     */
    createFlyerHtml(event) {
        // Defensive check: ensure we have a valid start_time before formatting
        if (!event || !event.start_time) {
            return `<div class="event-flyer event-flyer-error" role="alert">Invalid event</div>`;
        }

        const startTime = new Date(event.start_time);
        if (isNaN(startTime.getTime())) {
            return `<div class="event-flyer event-flyer-error" role="alert">Invalid date</div>`;
        }

        const hours = startTime.getHours().toString().padStart(2, '0');
        const minutes = startTime.getMinutes().toString().padStart(2, '0');
        const timeStr = `${hours}:${minutes}`;
        const dayStr = startTime.toLocaleDateString([], { weekday: 'short' });
        const dateNum = startTime.getDate();
        
        // Check time filter to decide display mode
        const timeFilter = this.storage.getFilters().timeFilter || 'sunrise';
        const isTimeMode = (timeFilter === 'sunrise');
        
        // Truncate title to fit in small flyer
        const title = event.title || 'Event';
        const shortTitle = title.length > 25 ? title.substring(0, 22) + '…' : title;
        
        // Category for styling
        const category = event.category || 'default';
        
        // Build compact flyer HTML (escape all dynamic content for XSS prevention)
        // When timeFilter is 'sunrise' (til sunrise), show quartz-style HH:MM
        // Otherwise, show calendar-style day + date
        if (isTimeMode) {
            // Quartz-style time display
            return `
                <div class="event-flyer event-flyer-time-mode" data-category="${this.escapeHtml(category)}" tabindex="0" role="button" aria-label="${this.escapeHtml(title)}">
                    <div class="event-flyer-date event-flyer-quartz">
                        <span class="flyer-quartz-time">${this.escapeHtml(timeStr)}</span>
                    </div>
                    <div class="event-flyer-content">
                        <div class="flyer-title">${this.escapeHtml(shortTitle)}</div>
                    </div>
                </div>
            `.trim();
        } else {
            // Calendar-style day + date display
            return `
                <div class="event-flyer" data-category="${this.escapeHtml(category)}" tabindex="0" role="button" aria-label="${this.escapeHtml(title)}">
                    <div class="event-flyer-date">
                        <span class="flyer-day">${this.escapeHtml(dayStr)}</span>
                        <span class="flyer-date-num">${this.escapeHtml(String(dateNum))}</span>
                    </div>
                    <div class="event-flyer-content">
                        <div class="flyer-title">${this.escapeHtml(shortTitle)}</div>
                        <div class="flyer-time">${this.escapeHtml(timeStr)}</div>
                    </div>
                </div>
            `.trim();
        }
    }
    
    /**
     * Escape HTML special characters to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Update flyer bookmark state
     * @param {string} eventId - Event ID
     * @param {boolean} isBookmarked - Whether event is bookmarked
     */
    updateMarkerBookmarkState(eventId, isBookmarked) {
        this.flyers.forEach(flyer => {
            if (flyer.eventData && flyer.eventData.id === eventId) {
                if (isBookmarked) {
                    flyer._icon.classList.add('event-flyer-bookmarked');
                } else {
                    flyer._icon.classList.remove('event-flyer-bookmarked');
                }
            }
        });
    }
    
    /**
     * Clear all event flyers from map
     */
    clearMarkers() {
        for (let i = 0; i < this.flyers.length; i++) {
            this.flyers[i].remove();
        }
        this.flyers = [];
        this.locationCounts = {}; // Reset location tracking for offset calculation
        this.log('All flyers cleared');
    }
    
    /**
     * Fit map bounds to show all flyers
     */
    fitMapToMarkers() {
        if (this.flyers.length === 0 || !this.map) {
            return;
        }
        
        const bounds = L.latLngBounds();
        
        // Add all flyer positions to bounds
        for (let i = 0; i < this.flyers.length; i++) {
            bounds.extend(this.flyers[i].getLatLng());
        }
        
        // Add user location to bounds if available
        if (this.userLocation) {
            bounds.extend([this.userLocation.lat, this.userLocation.lon]);
        }
        
        // Fit map to bounds with padding
        this.map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 15
        });
        
        this.log('Map fitted to markers');
    }
    
    /**
     * Calculate appropriate zoom level based on distance radius
     * @param {number} distanceKm - Distance in kilometers
     * @returns {number} Appropriate zoom level
     */
    calculateZoomFromDistance(distanceKm) {
        // Zoom level formula: Higher zoom = closer view
        // At equator, zoom level N shows approximately (40075 / (256 * 2^N)) km per pixel
        // We want to show the full radius, so calculate zoom to fit ~2x the distance
        // 
        // Approximate visible radius at different zoom levels (at mid-latitudes ~50°):
        // Zoom 10: ~40km radius
        // Zoom 11: ~20km radius
        // Zoom 12: ~10km radius
        // Zoom 13: ~5km radius (default)
        // Zoom 14: ~2.5km radius
        // Zoom 15: ~1.25km radius
        // Zoom 16: ~0.6km radius
        
        // Use logarithmic formula: each zoom level halves the visible area
        // Starting from zoom 13 (5km radius), calculate appropriate zoom
        const baseZoom = 13;
        const baseRadius = 5.0; // km at zoom 13
        
        // Calculate zoom adjustment: log2(baseRadius / desiredRadius)
        const zoomAdjustment = Math.log2(baseRadius / distanceKm);
        const calculatedZoom = baseZoom + zoomAdjustment;
        
        // Clamp zoom level to reasonable range (10-16)
        // Min zoom 10 for distances > 40km, max zoom 16 for very close distances
        const zoom = Math.max(10, Math.min(16, Math.round(calculatedZoom)));
        
        this.log('Calculated zoom from distance', { distanceKm, zoom });
        return zoom;
    }
    
    /**
     * Center map on specific location with optional distance-based zoom
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number|null} zoom - Zoom level (optional, defaults to 13)
     * @param {number|null} distanceKm - Distance in km to calculate zoom from (optional)
     */
    centerMap(lat, lon, zoom = null, distanceKm = null) {
        if (!this.map) return;
        
        // If distance provided, calculate zoom from it (overrides manual zoom)
        let finalZoom = zoom !== null ? zoom : 13;
        if (distanceKm !== null) {
            finalZoom = this.calculateZoomFromDistance(distanceKm);
        }
        
        this.map.setView([lat, lon], finalZoom);
        this.log('Map centered', {lat, lon, zoom: finalZoom, distanceKm});
    }
    
    /**
     * Invalidate map size (call after UI changes)
     */
    invalidateSize() {
        if (this.map) {
            this.map.invalidateSize();
        }
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Map]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MapManager;
}
