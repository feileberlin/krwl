/**
 * MapManager Module
 * 
 * Handles all Leaflet.js map operations:
 * - Map initialization
 * - Marker management
 * - User location tracking
 * - Map bounds and zoom
 * 
 * KISS: Single responsibility - map management only
 */

class MapManager {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.map = null;
        this.markers = [];
        this.userLocation = null;
        this.locationCounts = {}; // Track markers at same location for offset
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
        
        // Create fallback message
        const fallback = document.createElement('div');
        fallback.className = 'map-fallback';
        fallback.innerHTML = `
            <div class="map-fallback-content">
                <div class="map-fallback-icon">🗺️</div>
                <h2>Map Loading...</h2>
                <p>The interactive map is loading. If this message persists, the map library may be blocked by your browser or network.</p>
                <p class="map-fallback-note">Events are still available in the filter bar above.</p>
            </div>
        `;
        container.appendChild(fallback);
        this.log('Map fallback displayed');
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
     */
    getUserLocation(onSuccess, onError) {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    this.log('User location obtained', this.userLocation);
                    
                    // Center map on user location
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                        this.addUserMarker();
                    }
                    
                    if (onSuccess) onSuccess(this.userLocation);
                },
                (error) => {
                    console.error('Location error:', error);
                    
                    // Use default location as fallback
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    }
                    
                    if (onError) onError(error);
                }
            );
        } else {
            // Use default location as fallback
            const defaultCenter = this.config.map.default_center;
            this.userLocation = {
                lat: defaultCenter.lat,
                lon: defaultCenter.lon
            };
            
            if (onError) onError(new Error('Geolocation not supported'));
        }
    }
    
    /**
     * Add user location marker to map
     */
    addUserMarker() {
        if (!this.map || !this.userLocation) return;
        
        // Get user marker config
        const userMarkerConfig = this.config.map.user_location_marker || {};
        const userIconUrl = userMarkerConfig.icon || 
            (window.MARKER_ICONS && window.MARKER_ICONS['marker-geolocation']) ||
            'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI4IiBmaWxsPSIjNENBRjUwIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiIGZpbGw9IiNmZmYiLz48L3N2Zz4=';
        const userIconSize = userMarkerConfig.size || [32, 48];
        const userIconAnchor = userMarkerConfig.anchor || [userIconSize[0] / 2, userIconSize[1]];
        const userPopupAnchor = userMarkerConfig.popup_anchor || [0, -userIconSize[1]];
        
        const userIcon = L.icon({
            iconUrl: userIconUrl,
            iconSize: userIconSize,
            iconAnchor: userIconAnchor,
            popupAnchor: userPopupAnchor
        });
        
        L.marker([this.userLocation.lat, this.userLocation.lon], {
            icon: userIcon
        }).addTo(this.map).bindPopup('You are here');
        
        this.log('User marker added');
    }
    
    /**
     * Add event marker to map
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler
     * @returns {Object} Leaflet marker
     */
    addEventMarker(event, onClick) {
        if (!this.map || !event.location) return null;
        
        // Get marker icon based on category (uses SVG filename pattern: marker-{category})
        const category = event.category || 'default';
        const iconUrl = window.MARKER_ICONS && window.MARKER_ICONS[`marker-${category}`] || 
            window.MARKER_ICONS && window.MARKER_ICONS['marker-default'] ||
            'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjRkY2OUI0IiBkPSJNMTIgMkM4LjEzIDIgNSA1LjEzIDUgOWMwIDUuMjUgNyAxMyA3IDEzczctNy43NSA3LTEzYzAtMy44Ny0zLjEzLTctNy03em0wIDkuNWMtMS4zOCAwLTIuNS0xLjEyLTIuNS0yLjVzMS4xMi0yLjUgMi41LTIuNSAyLjUgMS4xMiAyLjUgMi41LTEuMTIgMi41LTIuNSAyLjV6Ii8+PC9zdmc+';
        
        const markerIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [32, 48],
            iconAnchor: [16, 48],
            popupAnchor: [0, -48]
        });
        
        // Calculate offset for markers at same location (spiderfying)
        const locationKey = `${event.location.lat.toFixed(4)}_${event.location.lon.toFixed(4)}`;
        if (!this.locationCounts[locationKey]) {
            this.locationCounts[locationKey] = 0;
        }
        const offsetIndex = this.locationCounts[locationKey];
        this.locationCounts[locationKey]++;
        
        // Apply circular offset if there are multiple markers at same location
        let lat = event.location.lat;
        let lon = event.location.lon;
        if (offsetIndex > 0) {
            const offsetRadius = 0.0003; // ~30 meters offset
            const angle = (offsetIndex * 60) * (Math.PI / 180); // 60 degree increments
            lat += offsetRadius * Math.cos(angle);
            lon += offsetRadius * Math.sin(angle);
        }
        
        const marker = L.marker([lat, lon], {
            icon: markerIcon,
            customData: { id: event.id }
        }).addTo(this.map);
        
        // Add bookmark class if bookmarked
        if (this.storage.isBookmarked(event.id)) {
            marker._icon.classList.add('bookmarked-marker');
        }
        
        // Store event data on marker (for backward compatibility)
        marker.eventData = event;
        
        // Add click handler
        if (onClick) {
            marker.on('click', () => onClick(event, marker));
        }
        
        this.markers.push(marker);
        this.log('Marker added for event', event.title);
        
        return marker;
    }
    
    /**
     * Update marker bookmark state
     * @param {string} eventId - Event ID
     * @param {boolean} isBookmarked - Whether event is bookmarked
     */
    updateMarkerBookmarkState(eventId, isBookmarked) {
        this.markers.forEach(marker => {
            if (marker.eventData && marker.eventData.id === eventId) {
                if (isBookmarked) {
                    marker._icon.classList.add('bookmarked-marker');
                } else {
                    marker._icon.classList.remove('bookmarked-marker');
                }
            }
        });
    }
    
    /**
     * Clear all event markers from map
     */
    clearMarkers() {
        for (let i = 0; i < this.markers.length; i++) {
            this.markers[i].remove();
        }
        this.markers = [];
        this.locationCounts = {}; // Reset location tracking for offset calculation
        this.log('All markers cleared');
    }
    
    /**
     * Fit map bounds to show all markers
     */
    fitMapToMarkers() {
        if (this.markers.length === 0 || !this.map) {
            return;
        }
        
        const bounds = L.latLngBounds();
        
        // Add all marker positions to bounds
        for (let i = 0; i < this.markers.length; i++) {
            bounds.extend(this.markers[i].getLatLng());
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
     * Center map on specific location
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} zoom - Zoom level (optional)
     */
    centerMap(lat, lon, zoom = 13) {
        if (this.map) {
            this.map.setView([lat, lon], zoom);
            this.log('Map centered', {lat, lon, zoom});
        }
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
