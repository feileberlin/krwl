/**
 * MapManager Module
 * 
 * Handles all Leaflet.js map operations:
 * - Map initialization
 * - Event markers with category icons (using Lucide icon font only)
 * - Auto-opening popups with event details
 * - User location tracking
 * - Map bounds and zoom
 * 
 * KISS: Single responsibility - map management only
 * 
 * UI PHILOSOPHY: Category markers with permanently open popups
 * - Traditional markers with category-based Lucide icons
 * - Popups open automatically showing event details
 * - Smart time display: Clock for "til sunrise", Calendar for other filters
 * - Heart bookmark button in each popup
 */

// Constants for marker positioning (offsetting markers at same location)
const MARKER_OFFSET_RADIUS = 0.0005;   // ~50 meters offset for overlapping markers
const MARKER_OFFSET_ANGLE = 45;        // Degrees between each offset marker
const LOCATION_PRECISION = 4;          // Decimal places for location grouping (~11m precision)

class MapManager {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.map = null;
        this.markers = [];          // Event markers with popups
        this.userLocation = null;
        this.locationCounts = {};   // Track markers at same location for offset
        this.referenceMarker = null; // Track the reference location marker (user/predefined/custom)
        this.isFallbackMode = false; // Track if we're showing fallback event list
    }
    
    /**
     * Backward compatibility: return markers as flyers
     */
    get flyers() {
        return this.markers;
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
     * Add event marker to map with category icon and permanently open popup
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler
     * @returns {Object} Leaflet marker with icon and popup
     */
    addEventMarker(event, onClick) {
        if (!this.map || !event.location) return null;
        
        // Detect category if not present
        const category = event.category || this.detectEventCategory(event);
        event.category = category; // Store detected category
        
        // Get category-based icon
        const iconUrl = this.getMarkerIconForCategory(category);
        
        // Create custom Leaflet icon with category styling
        const customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [40, 60],        // Classic marker size
            iconAnchor: [20, 60],      // Bottom center of marker
            popupAnchor: [0, -60],     // Above marker
            className: this.storage.isBookmarked(event.id) ? 'marker-bookmarked' : 'marker-unbookmarked'
        });
        
        // Calculate offset for markers at same location
        const locationKey = `${event.location.lat.toFixed(LOCATION_PRECISION)}_${event.location.lon.toFixed(LOCATION_PRECISION)}`;
        if (!this.locationCounts[locationKey]) {
            this.locationCounts[locationKey] = 0;
        }
        const offsetIndex = this.locationCounts[locationKey];
        this.locationCounts[locationKey]++;
        
        // Apply offset if there are multiple markers at same location
        let lat = event.location.lat;
        let lon = event.location.lon;
        if (offsetIndex > 0) {
            const angle = (offsetIndex * MARKER_OFFSET_ANGLE) * (Math.PI / 180);
            lat += MARKER_OFFSET_RADIUS * Math.cos(angle);
            lon += MARKER_OFFSET_RADIUS * Math.sin(angle);
        }
        
        // Create marker with icon
        const marker = L.marker([lat, lon], {
            icon: customIcon,
            customData: { id: event.id }
        }).addTo(this.map);
        
        // Store event data on marker
        marker.eventData = event;
        
        // Create popup content with time/date logic
        const popupContent = this.createPopupContent(event);
        
        // Bind popup and open it immediately (permanently open)
        marker.bindPopup(popupContent, {
            closeButton: false,       // No close button - permanently open
            autoClose: false,         // Don't close when clicking map
            closeOnClick: false,      // Don't close when clicking marker
            className: 'event-popup',
            maxWidth: 280,
            offset: [0, -5]           // Slight offset above marker
        }).openPopup();
        
        // Handle popup interactions after it's added to DOM
        setTimeout(() => {
            this.setupPopupInteractions(marker, event, onClick);
        }, 100);
        
        this.markers.push(marker);
        this.log('Marker added with popup for event', event.title);
        
        return marker;
    }
    
    /**
     * Detect event category from title and description (using Lucide icon names)
     * @param {Object} event - Event with title and description
     * @returns {string} Category name matching Lucide icon
     */
    detectEventCategory(event) {
        const text = `${event.title || ''} ${event.description || ''}`.toLowerCase();
        
        // Music & Performance
        if (/\b(concert|musik|music|band|sänger|singer|dj|live.*music)\b/i.test(text)) return 'music';
        if (/\b(theater|theatre|schauspiel|performance|show|comedy|stand.*up)\b/i.test(text)) return 'drama';
        
        // Arts & Culture
        if (/\b(art|kunst|gallery|galerie|exhibition|ausstellung|museum)\b/i.test(text)) return 'palette';
        if (/\b(film|kino|cinema|movie|screening)\b/i.test(text)) return 'film';
        if (/\b(photo|foto|photography)\b/i.test(text)) return 'camera';
        
        // Food & Dining
        if (/\b(food|essen|restaurant|dinner|lunch|culinary|küche|cooking)\b/i.test(text)) return 'utensils';
        if (/\b(coffee|café|cafe|kaffee|breakfast)\b/i.test(text)) return 'coffee';
        if (/\b(wine|beer|bier|wein|cocktail|bar|pub|drink)\b/i.test(text)) return 'wine';
        
        // Sports & Fitness
        if (/\b(sport|fitness|yoga|gym|workout|training|exercise)\b/i.test(text)) return 'dumbbell';
        if (/\b(football|soccer|fußball|basketball|tennis)\b/i.test(text)) return 'trophy';
        if (/\b(run|running|lauf|marathon|jogging)\b/i.test(text)) return 'footprints';
        
        // Education & Workshop
        if (/\b(workshop|seminar|kurs|course|class|lesson|training|schulung)\b/i.test(text)) return 'graduation-cap';
        if (/\b(talk|vortrag|lecture|presentation|conference)\b/i.test(text)) return 'presentation';
        if (/\b(book|buch|library|bibliothek|reading|lesung)\b/i.test(text)) return 'book-open';
        
        // Community & Social
        if (/\b(meetup|meeting|stammtisch|networking|community|social)\b/i.test(text)) return 'users';
        if (/\b(party|fest|festival|celebration|feier)\b/i.test(text)) return 'party-popper';
        if (/\b(market|markt|bazaar|fair|messe)\b/i.test(text)) return 'shopping-bag';
        
        // Nature & Outdoor
        if (/\b(park|garden|garten|nature|natur|outdoor|hike|wandern)\b/i.test(text)) return 'trees';
        if (/\b(bike|fahrrad|cycling|radtour)\b/i.test(text)) return 'bike';
        
        // Technology
        if (/\b(tech|technology|digital|coding|programming|hackathon)\b/i.test(text)) return 'laptop';
        if (/\b(game|gaming|esport|videogame)\b/i.test(text)) return 'gamepad-2';
        
        // Kids & Family
        if (/\b(kid|child|kinder|family|familie|baby)\b/i.test(text)) return 'baby';
        
        // Default fallback
        return 'calendar';
    }
    
    /**
     * Get marker icon HTML using individual Lucide icons
     * Each category shows its distinct icon directly without background shape
     * Uses only icons available in MAP_ICONS_MAP and DASHBOARD_ICONS_MAP
     * @param {string} category - Category name (maps to Lucide icon)
     * @returns {Object} Leaflet divIcon with category-specific Lucide icon
     */
    getMarkerIconForCategory(category) {
        // Map categories to available Lucide icon names
        // Only use icons that exist in the minimal Lucide build
        const iconMap = {
            'music': 'activity',        // musical activity (wave pattern)
            'drama': 'activity',
            'palette': 'book-open',     // arts/creativity
            'film': 'book-open',
            'camera': 'book-open',
            'utensils': 'map-pin',      // generic location marker
            'coffee': 'map-pin',
            'wine': 'map-pin',
            'dumbbell': 'activity',     // sports activity
            'trophy': 'activity',
            'footprints': 'footprints', // available!
            'graduation-cap': 'book-open', // education
            'presentation': 'book-open',
            'book-open': 'book-open',   // available!
            'users': 'map-pin',         // community
            'party-popper': 'activity',
            'shopping-bag': 'map-pin',
            'trees': 'map-pin',         // nature
            'bike': 'footprints',       // movement
            'laptop': 'book-text',      // available!
            'gamepad-2': 'activity',
            'baby': 'heart',            // available!
            'calendar': 'map-pin'       // default
        };
        
        const lucideIcon = iconMap[category] || 'map-pin';
        
        // Create div icon with just the Lucide icon (no background shape)
        // Each category icon is visually distinct
        const html = `
            <div class="category-icon-marker" data-category="${category}">
                <i data-lucide="${lucideIcon}" class="category-icon"></i>
            </div>
        `;
        
        return L.divIcon({
            className: 'category-icon-container',
            html: html,
            iconSize: [40, 40],
            iconAnchor: [20, 20],
            popupAnchor: [0, -20]
        });
    }
    
    /**
     * Create popup content HTML with smart time display
     * Shows clock for "til sunrise", calendar for other filters
     * @param {Object} event - Event data
     * @returns {string} HTML content for popup
     */
    createPopupContent(event) {
        if (!event || !event.start_time) {
            return '<div class="popup-error">Invalid event</div>';
        }
        
        const startTime = new Date(event.start_time);
        if (isNaN(startTime.getTime())) {
            return '<div class="popup-error">Invalid date</div>';
        }
        
        // Format time and date
        const hours = startTime.getHours();
        const minutes = startTime.getMinutes().toString().padStart(2, '0');
        const timeStr = `${hours}:${minutes}`;
        const dayStr = startTime.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
        
        // Get time filter from global app
        const app = window.app || window.eventsApp;
        const timeFilter = (app && app.filters && app.filters.timeFilter) || 'sunrise';
        const isSunriseFilter = (timeFilter === 'sunrise');
        
        // Check if bookmarked
        const isBookmarked = this.storage.isBookmarked(event.id);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        
        // Truncate title
        const title = event.title || 'Event';
        const displayTitle = title.length > 50 ? title.substring(0, 47) + '…' : title;
        
        // Distance display
        const distanceHtml = event.distance !== undefined 
            ? `<div class="popup-distance">
                 <i data-lucide="map-pin" class="popup-icon"></i>
                 <span>${event.distance.toFixed(1)} km</span>
               </div>`
            : '';
        
        // Build popup HTML based on time filter
        if (isSunriseFilter) {
            // Show TIME with map-pin icon for "til sunrise" filter (since clock isn't available)
            return `
                <div class="event-popup-content">
                    <div class="popup-time-display popup-time-mode">
                        <div class="time-badge" title="${timeStr}">
                            <span class="time-large">${this.escapeHtml(timeStr)}</span>
                        </div>
                    </div>
                    <h3 class="popup-title">${this.escapeHtml(displayTitle)}</h3>
                    <div class="popup-location">
                        <i data-lucide="map-pin" class="popup-icon"></i>
                        <span>${this.escapeHtml(event.location?.name || 'Unknown')}</span>
                    </div>
                    ${distanceHtml}
                    <button class="popup-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                        <i data-lucide="heart" class="bookmark-icon"></i>
                    </button>
                </div>
            `.trim();
        } else {
            // Show DATE for other filters
            return `
                <div class="event-popup-content">
                    <div class="popup-time-display popup-date-mode">
                        <div class="date-badge">
                            <span class="date-large">${this.escapeHtml(dayStr)}</span>
                        </div>
                    </div>
                    <h3 class="popup-title">${this.escapeHtml(displayTitle)}</h3>
                    <div class="popup-location">
                        <i data-lucide="map-pin" class="popup-icon"></i>
                        <span>${this.escapeHtml(event.location?.name || 'Unknown')}</span>
                    </div>
                    ${distanceHtml}
                    <button class="popup-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                        <i data-lucide="heart" class="bookmark-icon"></i>
                    </button>
                </div>
            `.trim();
        }
    }
    
    /**
     * Setup popup interactions (bookmark button, clicks)
     * @param {Object} marker - Leaflet marker
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler for event details
     */
    setupPopupInteractions(marker, event, onClick) {
        const popup = marker.getPopup();
        if (!popup) return;
        
        const popupElement = popup.getElement();
        if (!popupElement) return;
        
        // Initialize Lucide icons in popup
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons({ nameAttr: 'data-lucide' });
        }
        
        // Handle bookmark button click
        const bookmarkBtn = popupElement.querySelector('.popup-bookmark');
        if (bookmarkBtn) {
            bookmarkBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Toggle bookmark
                const isNowBookmarked = this.storage.toggleBookmark(event.id);
                
                // Update button appearance
                bookmarkBtn.classList.toggle('bookmarked', isNowBookmarked);
                
                // Re-render icon (heart should fill when bookmarked)
                if (window.lucide && typeof window.lucide.createIcons === 'function') {
                    window.lucide.createIcons({ nameAttr: 'data-lucide' });
                }
                
                this.log('Bookmark toggled', { eventId: event.id, bookmarked: isNowBookmarked });
            });
        }
        
        // Handle click on popup content to show full details
        if (onClick) {
            const content = popupElement.querySelector('.event-popup-content');
            if (content) {
                content.addEventListener('click', (e) => {
                    // Don't trigger if clicking bookmark button
                    if (!e.target.closest('.popup-bookmark')) {
                        onClick(event, marker);
                    }
                });
            }
        }
    }
    
    /**
     * Clear all markers from map
     */
    clearMarkers() {
        this.markers.forEach(marker => {
            if (marker && marker.remove) {
                marker.remove();
            }
        });
        this.markers = [];
        this.locationCounts = {}; // Reset offset tracking
        this.log('All markers cleared');
    }
    
    /**
     * Fit map bounds to show all markers
     */
    fitMapToMarkers() {
        if (!this.map || this.markers.length === 0) return;
        
        const group = L.featureGroup(this.markers);
        this.map.fitBounds(group.getBounds().pad(0.1)); // 10% padding
        
        this.log('Map fitted to markers', { count: this.markers.length });
    }
    
    /**
     * DEPRECATED: Old flyer methods for backward compatibility
     */
    createFlyerHtml(event) {
        // Legacy method - now creates popup content instead
        return this.createPopupContent(event);
    }
    
    clearFlyers() {
        // Legacy method - now clears markers
        return this.clearMarkers();
    }
    
    /**
     * Update marker bookmark state
     * @param {string} eventId - Event ID
     * @param {boolean} isBookmarked - New bookmark state
     */
    updateMarkerBookmarkState(eventId, isBookmarked) {
        const marker = this.markers.find(m => m.eventData && m.eventData.id === eventId);
        if (!marker) return;
        
        const popup = marker.getPopup();
        if (!popup) return;
        
        const popupElement = popup.getElement();
        if (!popupElement) return;
        
        const bookmarkBtn = popupElement.querySelector('.popup-bookmark');
        if (bookmarkBtn) {
            bookmarkBtn.classList.toggle('bookmarked', isBookmarked);
            
            // Re-render Lucide icon
            if (window.lucide && typeof window.lucide.createIcons === 'function') {
                window.lucide.createIcons({ nameAttr: 'data-lucide' });
            }
        }
        
        this.log('Marker bookmark state updated', { eventId, isBookmarked });
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
