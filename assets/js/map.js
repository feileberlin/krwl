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

// Smart clustering thresholds
const CLUSTER_THRESHOLD = 10;          // Only cluster if more than 10 events visible
const MAX_CLUSTER_RADIUS = 80;         // Max pixels for cluster radius
const MIN_CLUSTER_RADIUS = 40;         // Min pixels for cluster radius

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
        this.markerClusterGroup = null; // MarkerClusterGroup instance (deprecated - use categoryClusterGroups)
        this.categoryClusterGroups = {}; // Category-specific cluster groups
        this.useClusteringForCurrentView = false; // Dynamic clustering decision
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
        
        // Detect location type from label for better marker identification
        // NOTE: This is a heuristic-based approach. For future improvement, consider
        // passing location type as an explicit parameter from the calling code.
        let locationType = 'custom';
        let locationTypeLabel = 'Custom Location';
        
        // Geolocation: User's current position
        if (label && (label.includes('You are here') || label.includes('My Location') || label.includes('Current location'))) {
            locationType = 'geolocation';
            locationTypeLabel = 'Your Location';
        } 
        // Predefined: Known landmarks (detect by presence of common landmark indicators)
        // This works for most predefined locations regardless of specific names
        else if (label && !label.includes('🐧') && !label.includes('Custom')) {
            // If label doesn't contain custom indicators and isn't geolocation,
            // it's likely a predefined landmark from the config
            const hasLandmarkPattern = /\b(station|platz|bahnhof|zentrum|center|hauptbahnhof|markt|rathaus|kirche|church)\b/i.test(label);
            if (hasLandmarkPattern) {
                locationType = 'predefined';
                locationTypeLabel = 'Reference Point';
            }
        }
        
        return `
            <div class="location-flyer" role="img" aria-label="${escapedLabel}" data-location-type="${locationType}">
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
                    <span class="location-flyer-type">${locationTypeLabel}</span>
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
     * Add event marker to map with category icon and popup
     * Supports both clustered and non-clustered modes
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler
     * @param {boolean} addToCluster - Whether to add to cluster group (default: auto-detect)
     * @returns {Object} Leaflet marker with icon and popup
     */
    addEventMarker(event, onClick, addToCluster = null) {
        if (!this.map || !event.location) return null;
        
        // Auto-detect clustering if not specified
        if (addToCluster === null) {
            addToCluster = this.useClusteringForCurrentView && this.markerClusterGroup;
        }
        
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
        
        // Use original coordinates when clustering (cluster plugin handles spacing)
        // Use layout distribution when not clustering (smart visual arrangement)
        let lat = event.location.lat;
        let lon = event.location.lon;
        
        if (!addToCluster) {
            // Track location for layout calculation
            const locationKey = `${lat.toFixed(LOCATION_PRECISION)}_${lon.toFixed(LOCATION_PRECISION)}`;
            if (!this.locationCounts[locationKey]) {
                this.locationCounts[locationKey] = 0;
            }
            const offsetIndex = this.locationCounts[locationKey];
            this.locationCounts[locationKey]++;
            
            // Get total markers that will be at this location (for better layout)
            // This is approximate since we're adding markers incrementally
            const totalAtLocation = this.locationCounts[locationKey];
            
            // Use layout distribution algorithm
            const layoutPos = this.calculateLayoutPosition(
                { lat, lon },
                offsetIndex,
                totalAtLocation
            );
            lat = layoutPos.lat;
            lon = layoutPos.lon;
        }
        
        // Create marker with icon
        const marker = L.marker([lat, lon], {
            icon: customIcon,
            customData: { id: event.id }
        });
        
        // Store event data on marker
        marker.eventData = event;
        
        // Create popup content with time/date logic
        const popupContent = this.createPopupContent(event);
        
        // Bind popup (behavior depends on clustering)
        if (addToCluster) {
            // Clustered mode: popups open on click only
            marker.bindPopup(popupContent, {
                closeButton: true,        // Show close button in clustered mode
                autoClose: true,          // Allow closing when clicking elsewhere
                closeOnClick: false,      // Don't close when clicking marker
                className: 'event-popup',
                maxWidth: 280,
                offset: [0, -5]
            });
        } else {
            // Non-clustered mode: popups permanently open
            marker.bindPopup(popupContent, {
                closeButton: false,       // No close button - permanently open
                autoClose: false,         // Don't close when clicking map
                closeOnClick: false,      // Don't close when clicking marker
                className: 'event-popup',
                maxWidth: 280,
                offset: [0, -5]
            }).openPopup();
        }
        
        // Add marker to map or cluster group
        if (addToCluster && this.useClusteringForCurrentView) {
            // Category-based clustering: add to category-specific cluster group
            const category = event.category || 'other';
            const categoryClusterGroup = this.categoryClusterGroups?.[category];
            
            if (categoryClusterGroup) {
                categoryClusterGroup.addLayer(marker);
                this.log('Marker added to category cluster for event', event.title, 'category:', category);
            } else {
                // Fallback: add to legacy cluster group if available
                if (this.markerClusterGroup) {
                    this.markerClusterGroup.addLayer(marker);
                    this.log('Marker added to legacy cluster for event', event.title);
                } else {
                    marker.addTo(this.map);
                    this.log('Marker added to map (no cluster group) for event', event.title);
                }
            }
        } else {
            marker.addTo(this.map);
            this.log('Marker added to map for event', event.title);
        }
        
        // Handle popup interactions after it's added to DOM
        setTimeout(() => {
            this.setupPopupInteractions(marker, event, onClick);
        }, 100);
        
        this.markers.push(marker);
        
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
        
        // Human-readable category labels for accessibility
        const categoryLabels = {
            'music': 'Music Event',
            'drama': 'Theater',
            'palette': 'Arts',
            'film': 'Cinema',
            'camera': 'Photography',
            'utensils': 'Food',
            'coffee': 'Café',
            'wine': 'Bar',
            'dumbbell': 'Sports',
            'trophy': 'Competition',
            'footprints': 'Walking',
            'graduation-cap': 'Workshop',
            'presentation': 'Talk',
            'book-open': 'Reading',
            'users': 'Meetup',
            'party-popper': 'Party',
            'shopping-bag': 'Market',
            'trees': 'Outdoor',
            'bike': 'Cycling',
            'laptop': 'Tech',
            'gamepad-2': 'Gaming',
            'baby': 'Family',
            'calendar': 'Event'
        };
        
        const lucideIcon = iconMap[category] || 'map-pin';
        const categoryLabel = categoryLabels[category] || 'Event';
        
        // Create div icon with just the Lucide icon (no background shape)
        // Each category icon is visually distinct with accessible label
        const html = `
            <div class="category-icon-marker" data-category="${category}" aria-label="${categoryLabel}">
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
     * NOW WITH: AI translation transparency indicators
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
        
        // Get translated title with transparency indicator
        const i18n = app && app.i18n;
        let displayTitle = event.title || 'Event';
        let titleIndicator = '';
        
        if (i18n) {
            const titleData = i18n.getTranslatedField(event, 'title');
            displayTitle = titleData.text;
            titleIndicator = i18n.createTranslationIndicator(titleData.metadata);
        }
        
        // Truncate title
        displayTitle = displayTitle.length > 50 ? displayTitle.substring(0, 47) + '…' : displayTitle;
        
        // Get translated location with transparency indicator
        let locationName = event.location?.name || 'Unknown';
        let locationIndicator = '';
        
        if (i18n) {
            const locationData = i18n.getTranslatedField(event, 'location_name');
            locationName = locationData.text;
            locationIndicator = i18n.createTranslationIndicator(locationData.metadata);
        }
        
        // Distance display
        const distanceHtml = event.distance !== undefined 
            ? `<div class="popup-distance">
                 <i data-lucide="map-pin" class="popup-icon"></i>
                 <span>${event.distance.toFixed(1)} km</span>
               </div>`
            : '';
        
        // Translation footer (if translated content)
        const translationFooter = i18n ? i18n.createTranslationFooter(event) : '';
        
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
                    <h3 class="popup-title">${this.escapeHtml(displayTitle)}${titleIndicator}</h3>
                    <div class="popup-location">
                        <i data-lucide="map-pin" class="popup-icon"></i>
                        <span>${this.escapeHtml(locationName)}${locationIndicator}</span>
                    </div>
                    ${distanceHtml}
                    <button class="popup-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                        <i data-lucide="heart" class="bookmark-icon"></i>
                    </button>
                    ${translationFooter}
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
                    <h3 class="popup-title">${this.escapeHtml(displayTitle)}${titleIndicator}</h3>
                    <div class="popup-location">
                        <i data-lucide="map-pin" class="popup-icon"></i>
                        <span>${this.escapeHtml(locationName)}${locationIndicator}</span>
                    </div>
                    ${distanceHtml}
                    <button class="popup-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                        <i data-lucide="heart" class="bookmark-icon"></i>
                    </button>
                    ${translationFooter}
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
        
        // Remove and reset all category cluster groups if they exist
        if (this.categoryClusterGroups) {
            Object.values(this.categoryClusterGroups).forEach(clusterGroup => {
                if (clusterGroup) {
                    // Explicitly clear all layers to ensure event listeners and references are released
                    if (typeof clusterGroup.clearLayers === 'function') {
                        clusterGroup.clearLayers();
                    }
                    if (this.map && this.map.hasLayer(clusterGroup)) {
                        this.map.removeLayer(clusterGroup);
                    }
                }
            });
            this.categoryClusterGroups = {};
        }
        
        // Remove and reset legacy marker cluster group if it exists (backward compatibility)
        if (this.markerClusterGroup) {
            // Explicitly clear all layers to ensure event listeners and references are released
            if (typeof this.markerClusterGroup.clearLayers === 'function') {
                this.markerClusterGroup.clearLayers();
            }
            this.map.removeLayer(this.markerClusterGroup);
            this.markerClusterGroup = null;
        }
        
        this.locationCounts = {}; // Reset offset tracking
        this.useClusteringForCurrentView = false; // Reset clustering decision
        this.log('All markers cleared');
    }
    
    /**
     * Determine if clustering should be used based on filtered events and config
     * Smart logic: Only cluster when it makes sense to humans
     * 
     * @param {Array} events - Filtered events to display
     * @returns {boolean} True if clustering should be enabled
     */
    shouldUseClustering(events) {
        if (!events || events.length === 0) return false;
        
        // Check config for clustering settings
        const clusterConfig = this.config?.map?.clustering || {};
        const mode = clusterConfig.mode || 'smart';
        const enabled = clusterConfig.enabled !== false;
        
        // If clustering is disabled or mode is 'never', never cluster
        if (!enabled || mode === 'never') {
            this.log('Clustering disabled by configuration');
            return false;
        }
        
        // If mode is 'always', always cluster (if enough events)
        if (mode === 'always') {
            return events.length >= 2;
        }
        
        // Smart mode (default): analyze event distribution
        const threshold = clusterConfig.threshold || CLUSTER_THRESHOLD;
        
        // Don't cluster if very few events (< threshold)
        if (events.length < threshold) {
            return false;
        }
        
        // Count unique locations
        const locationCounts = {};
        events.forEach(event => {
            if (event.location) {
                const key = `${event.location.lat.toFixed(LOCATION_PRECISION)}_${event.location.lon.toFixed(LOCATION_PRECISION)}`;
                locationCounts[key] = (locationCounts[key] || 0) + 1;
            }
        });
        
        const uniqueLocations = Object.keys(locationCounts).length;
        const maxAtOneLocation = Math.max(...Object.values(locationCounts));
        
        // Cluster if:
        // 1. Many events at same location (5+ at one spot)
        // 2. Many total events but relatively few locations (high density)
        if (maxAtOneLocation >= 5) {
            this.log(`Clustering enabled: ${maxAtOneLocation} events at same location`);
            return true;
        }
        
        // Use configured density ratio (default: 0.33 = one third)
        const densityRatio = clusterConfig.density_ratio || 0.33;
        const densityThreshold = events.length * densityRatio;
        
        if (events.length >= 20 && uniqueLocations <= densityThreshold) {
            this.log(`Clustering enabled: High density (${events.length} events, ${uniqueLocations} locations, threshold: ${densityThreshold.toFixed(1)})`);
            return true;
        }
        
        this.log(`Clustering disabled: Low density (${events.length} events, ${uniqueLocations} locations)`);
        return false;
    }
    
    /**
     * Calculate layout position for marker using configured distribution pattern
     * This creates visually pleasing arrangement without requiring geographic accuracy
     * 
     * @param {Object} baseLocation - Original location {lat, lon}
     * @param {number} index - Marker index at this location
     * @param {number} totalAtLocation - Total markers at this location
     * @returns {Object} Adjusted location {lat, lon}
     */
    calculateLayoutPosition(baseLocation, index, totalAtLocation) {
        const layoutConfig = this.config?.map?.clustering?.layout_distribution || {};
        const pattern = layoutConfig.pattern || 'spiral';
        const spacing = layoutConfig.spacing || 0.001;
        const maxSpread = layoutConfig.max_spread || 0.01;
        
        let lat = baseLocation.lat;
        let lon = baseLocation.lon;
        
        // First marker stays at original location
        if (index === 0) {
            return { lat, lon };
        }
        
        switch (pattern) {
            case 'spiral':
                // Archimedean spiral: r = a + b*θ
                const angle = index * 137.508; // Golden angle (360° × (1 - 1/φ)) for optimal packing
                const radius = Math.min(spacing * Math.sqrt(index), maxSpread);
                const rad = (angle * Math.PI) / 180;
                lat += radius * Math.cos(rad);
                lon += radius * Math.sin(rad);
                break;
                
            case 'circle':
                // Circular arrangement in rings
                const ring = Math.floor(Math.sqrt(index));
                const posInRing = index - (ring * ring);
                const itemsInRing = 2 * ring + 1;
                const circleAngle = (posInRing / itemsInRing) * 2 * Math.PI;
                const circleRadius = spacing * (ring + 1);
                lat += circleRadius * Math.cos(circleAngle);
                lon += circleRadius * Math.sin(circleAngle);
                break;
                
            case 'grid':
                // Grid pattern
                const gridSize = Math.ceil(Math.sqrt(totalAtLocation));
                const row = Math.floor(index / gridSize);
                const col = index % gridSize;
                const offsetX = (col - gridSize / 2) * spacing;
                const offsetY = (row - gridSize / 2) * spacing;
                lat += offsetY;
                lon += offsetX;
                break;
                
            default:
                // Fallback to simple radial offset
                const radialAngle = (index * MARKER_OFFSET_ANGLE) * (Math.PI / 180);
                lat += MARKER_OFFSET_RADIUS * Math.cos(radialAngle);
                lon += MARKER_OFFSET_RADIUS * Math.sin(radialAngle);
        }
        
        return { lat, lon };
    }
    
    /**
     * Initialize or reinitialize marker cluster group with filter-aware configuration
     * 
     * @param {Object} filters - Current filter settings (for cluster customization)
     * @returns {Object} MarkerClusterGroup instance
     */
    initializeClusterGroup(filters = {}) {
        // Check if MarkerCluster plugin is available
        if (typeof L === 'undefined' || typeof L.markerClusterGroup === 'undefined') {
            this.log('MarkerCluster plugin not available');
            return null;
        }
        
        // Calculate cluster radius based on zoom level and filter settings
        // Tighter clustering for distance filters (users want compact view)
        // Looser clustering for category/time filters (users exploring)
        const configMaxRadius = clusterConfig.max_radius || MAX_CLUSTER_RADIUS;
        const configMinRadius = clusterConfig.min_radius || MIN_CLUSTER_RADIUS;
        const distanceThreshold = clusterConfig.distance_filter_threshold_km || 5;
        
        let clusterRadius = configMaxRadius;
        
        if (filters.maxDistance && filters.maxDistance <= distanceThreshold) {
            // Tight distance filter = smaller clusters (more detail)
            clusterRadius = configMinRadius;
        } else if (filters.category && filters.category !== 'all') {
            // Category filter = medium clusters (focused view)
            clusterRadius = (configMinRadius + configMaxRadius) / 2;
        }
        
        // Create cluster group with custom icon and category-based clustering
        this.markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: clusterRadius,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            
            // Category-aware clustering: only cluster markers with same category
            iconCreateFunction: (cluster) => {
                const count = cluster.getChildCount();
                const markers = cluster.getAllChildMarkers();
                
                // Analyze categories in cluster
                const categories = {};
                markers.forEach(marker => {
                    const category = marker.eventData?.category || 'other';
                    categories[category] = (categories[category] || 0) + 1;
                });
                
                // Determine dominant category (most events)
                const categoryKeys = Object.keys(categories);
                const dominantCategory = categoryKeys.length > 0
                    ? categoryKeys.reduce((a, b) => (categories[a] > categories[b] ? a : b))
                    : 'other';
                
                // Size based on count
                let size = 'small';
                if (count >= 100) size = 'large';
                else if (count >= 10) size = 'medium';
                
                // Show category in cluster icon
                const isSingleCategory = categoryKeys.length === 1;
                const categoryHint = isSingleCategory 
                    ? `category-${dominantCategory}` 
                    : 'category-mixed';
                
                return L.divIcon({
                    html: `<div class="marker-cluster-count">${count}</div>`,
                    className: `marker-cluster marker-cluster-${size} ${categoryHint}`,
                    iconSize: L.point(40, 40)
                });
            },
            
            // Disable default clustering behavior - we'll group by category manually
            disableClusteringAtZoom: null,
            
            // Custom function to determine if two markers should be clustered together
            // Only cluster markers with the same category
            chunkedLoading: false,
            
            // Use maxClusterRadius but apply category filtering
            maxClusterRadius: function(zoom) {
                return clusterRadius;
            }
        });
        
        this.log(`Initialized marker cluster group (radius: ${clusterRadius}px)`);
        return this.markerClusterGroup;
    }
    
    /**
     * Initialize category-specific cluster group with filter-aware configuration
     * This creates separate cluster groups for each event category
     * 
     * @param {Object} filters - Current filter settings (for cluster customization)
     * @param {string} category - Event category for this cluster group
     * @param {number} categoryEventCount - Number of events in this category
     * @returns {Object} MarkerClusterGroup instance for this category
     */
    initializeCategoryClusterGroup(filters = {}, category = 'other', categoryEventCount = 0) {
        // Check if MarkerCluster plugin is available
        if (typeof L === 'undefined' || typeof L.markerClusterGroup === 'undefined') {
            this.log('MarkerCluster plugin not available');
            return null;
        }
        
        // Get cluster configuration
        const clusterConfig = this.config?.map?.clustering || {};
        const configMaxRadius = clusterConfig.max_radius || MAX_CLUSTER_RADIUS;
        const configMinRadius = clusterConfig.min_radius || MIN_CLUSTER_RADIUS;
        const distanceThreshold = clusterConfig.distance_filter_threshold_km || 5;
        
        let clusterRadius = configMaxRadius;
        
        if (filters.maxDistance && filters.maxDistance <= distanceThreshold) {
            // Tight distance filter = smaller clusters (more detail)
            clusterRadius = configMinRadius;
        } else if (filters.category && filters.category !== 'all') {
            // Category filter = medium clusters (focused view)
            clusterRadius = (configMinRadius + configMaxRadius) / 2;
        }
        
        // Create cluster group with category-specific styling
        const categoryClusterGroup = L.markerClusterGroup({
            maxClusterRadius: clusterRadius,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            
            // Custom cluster icon showing category icon + event count
            iconCreateFunction: (cluster) => {
                const count = cluster.getChildCount();
                
                // Size based on count
                let size = 'small';
                if (count >= 100) size = 'large';
                else if (count >= 10) size = 'medium';
                
                // Get category icon mapping (same as getMarkerIconForCategory)
                const iconMap = {
                    'music': 'activity',
                    'drama': 'activity',
                    'palette': 'book-open',
                    'film': 'book-open',
                    'camera': 'book-open',
                    'utensils': 'map-pin',
                    'coffee': 'map-pin',
                    'wine': 'map-pin',
                    'dumbbell': 'activity',
                    'trophy': 'activity',
                    'footprints': 'footprints',
                    'graduation-cap': 'book-open',
                    'presentation': 'book-open',
                    'book-open': 'book-open',
                    'users': 'map-pin',
                    'party-popper': 'activity',
                    'shopping-bag': 'map-pin',
                    'trees': 'map-pin',
                    'bike': 'footprints',
                    'laptop': 'book-text',
                    'gamepad-2': 'activity',
                    'baby': 'heart',
                    'calendar': 'map-pin'
                };
                
                const lucideIcon = iconMap[category] || 'map-pin';
                
                // Single category cluster - show category icon + count
                const categoryClass = `category-${category}`;
                
                // Create HTML with category icon and count badge
                const iconHtml = `
                    <div class="marker-cluster-icon">
                        <i data-lucide="${lucideIcon}" class="cluster-category-icon"></i>
                    </div>
                    <div class="marker-cluster-count-badge">${count}</div>
                `;
                
                return L.divIcon({
                    html: iconHtml,
                    className: `marker-cluster marker-cluster-${size} ${categoryClass}`,
                    iconSize: L.point(40, 40)
                });
            }
        });
        
        this.log(`Initialized category cluster group for '${category}' (${categoryEventCount} events, radius: ${clusterRadius}px)`);
        return categoryClusterGroup;
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
