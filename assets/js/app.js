// KRWL HOF Community Events App
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
        this.currentEdgeDetail = null;
        this.timeDrawer = null; // Time drawer for dynamic marker sizing
        this.currentEventIndex = null; // Track which event is currently displayed
        this.filters = {
            maxDistance: 5,
            timeFilter: 'sunrise',
            category: 'all',
            useCustomLocation: false,
            customLat: null,
            customLon: null
        };
        
        this.init();
    }
    
    // Debug logging helper
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[KRWL Debug]', message, ...args);
        }
    }
    
    async init() {
        // Load configuration
        await this.loadConfig();
        
        this.log('App initialized', 'Config:', this.config);
        
        // Show main content early with error handling
        this.showMainContent();
        
        // Initialize map (wrapped in try-catch to handle missing Leaflet)
        try {
            this.initMap();
        } catch (error) {
            console.warn('Map initialization failed:', error.message);
            // Ensure content is visible even if map fails
            this.showMainContent();
        }
        
        // Initialize TimeDrawer if map is available
        if (this.map && typeof TimeDrawer !== 'undefined') {
            this.timeDrawer = new TimeDrawer(
                this.map,
                this.events,
                () => this.getNextSunrise()
            );
            this.log('TimeDrawer initialized');
        }
        
        // Get user location
        this.getUserLocation();
        
        // Load events
        try {
            await this.loadEvents();
        } catch (error) {
            console.error('Failed to load events:', error);
            // Ensure content is visible even if event loading fails
            this.showMainContent();
        }
        
        // Setup event listeners (always run, even if map fails)
        this.setupEventListeners();
        
        // Signal that app is ready (for screenshot tools, etc.)
        this.markAppAsReady();
    }
    
    markAppAsReady() {
        /**
         * App Ready Signal for Screenshot Generation
         * 
         * Emits a ready signal when the app is fully initialized and ready for screenshot capture.
         * This solves the problem of screenshots being taken before the map and event data 
         * have finished loading.
         * 
         * FEATURE: App ready signal
         * PURPOSE: Enable reliable screenshot generation by tools like Playwright, Puppeteer, or Selenium
         * 
         * SIGNAL METHODS:
         * 1. Body attribute: <body data-app-ready="true">
         *    - Can be detected with CSS selector: body[data-app-ready="true"]
         * 
         * 2. Custom event: window 'app-ready' event
         *    - Includes metadata: timestamp, eventsLoaded count, mapInitialized status
         *    - Can be listened to: window.addEventListener('app-ready', handler)
         * 
         * TIMING: Signal is emitted after all async operations complete:
         * 1. ✅ Config loaded
         * 2. ✅ Map initialized
         * 3. ✅ Geolocation requested (or skipped)
         * 4. ✅ Events loaded and processed
         * 5. ✅ Event listeners set up
         * 
         * NOTE: Map tiles may still be loading after the ready signal. Add a small delay 
         *       (1-2s) for visual completeness in screenshots.
         * 
         * USAGE EXAMPLE (Playwright):
         *   page.goto('http://localhost:8000')
         *   page.wait_for_selector('body[data-app-ready="true"]', timeout=30000)
         *   page.wait_for_timeout(2000)  // Optional: wait for map tiles
         *   page.screenshot(path='screenshot.png')
         * 
         * For complete usage examples, see:
         * - scripts/generate_screenshots.py - Full implementation with mobile/desktop screenshots
         * - README.md section "Advanced Features > Screenshot Generation"
         */
        // Set data attribute on body to signal app is ready
        document.body.setAttribute('data-app-ready', 'true');
        
        // Dispatch custom event for programmatic detection
        window.dispatchEvent(new CustomEvent('app-ready', {
            detail: {
                timestamp: Date.now(),
                eventsLoaded: this.events.length,
                mapInitialized: !!this.map
            }
        }));
        
        this.log('App ready signal sent', {
            events: this.events.length,
            map: !!this.map
        });
    }
    
    showMainContent() {
        // Safely show main content with error handling
        // This prevents flash of unstyled content while ensuring content is visible
        try {
            const mainContent = document.getElementById('main-content');
            if (mainContent && mainContent.style.display === 'none') {
                mainContent.style.display = 'block';
                this.log('Main content displayed');
            }
        } catch (error) {
            console.error('Failed to show main content:', error);
            // Try one more time with a fallback approach
            try {
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.removeAttribute('style');
                }
            } catch (fallbackError) {
                console.error('Fallback to show main content also failed:', fallbackError);
            }
        }
    }
    
    updateDashboard() {
        // Update dashboard debug info with current state
        const debugEnvironment = document.getElementById('debug-environment');
        const debugEventCount = document.getElementById('debug-event-count');
        const debugDataSource = document.getElementById('debug-data-source');
        const debugMode = document.getElementById('debug-mode');
        
        if (debugEnvironment) {
            const environment = this.config?.watermark?.text || this.config?.app?.environment || 'UNKNOWN';
            debugEnvironment.textContent = environment.toUpperCase();
            // Add color coding based on environment
            if (environment.toLowerCase().includes('dev')) {
                debugEnvironment.style.color = '#FFB3DF'; // Lighter pink for dev
            } else if (environment.toLowerCase().includes('production')) {
                debugEnvironment.style.color = '#4CAF50'; // Green for production
            }
        }
        
        if (debugEventCount) {
            const totalEvents = this.events.length;
            const visibleEvents = this.filterEvents().length;
            debugEventCount.textContent = `${visibleEvents}/${totalEvents}`;
        }
        
        if (debugDataSource) {
            const dataSource = this.config?.data?.source || 'unknown';
            debugDataSource.textContent = dataSource;
        }
        
        if (debugMode) {
            const debugEnabled = this.config?.debug || false;
            debugMode.textContent = debugEnabled ? 'Enabled' : 'Disabled';
            debugMode.style.color = debugEnabled ? '#FFB3DF' : '#888';
        }
    }
    
    async loadConfig() {
        try {
            const response = await fetch('config.json');
            this.config = await response.json();
        } catch (error) {
            console.error('Error loading config:', error);
            // Use defaults
            this.config = {
                map: {
                    default_center: { lat: 52.52, lon: 13.405 },
                    default_zoom: 13
                },
                filtering: {
                    max_distance_km: 5.0,
                    show_until: "next_sunrise"
                }
            };
        }
    }
    
    initMap() {
        const center = this.config.map.default_center;
        // Disable zoom controls - use keyboard shortcuts (+ / -) or pinch zoom on mobile
        this.map = L.map('map', {
            zoomControl: false,
            attributionControl: false
        }).setView([center.lat, center.lon], this.config.map.default_zoom);
        
        L.tileLayer(this.config.map.tile_provider, {
            attribution: this.config.map.attribution
        }).addTo(this.map);
    }
    
    getUserLocation() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    // Center map on user location (if map is initialized)
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                        
                        // Add user marker with custom geolocation icon
                        // Support customization from config or use default
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
                    }
                    
                    // Update events display
                    this.displayEvents();
                },
                (error) => {
                    console.error('Location error:', error);
                    
                    // Use config default location as fallback
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    // Center map on default location (if map is initialized)
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    }
                    
                    // Still display events with fallback location
                    this.displayEvents();
                }
            );
        } else {
            // Use config default location as fallback
            const defaultCenter = this.config.map.default_center;
            this.userLocation = {
                lat: defaultCenter.lat,
                lon: defaultCenter.lon
            };
            
            this.displayEvents();
        }
    }
    
    async loadEvents() {
        try {
            this.log('Loading events...', 'Data source:', this.config.data?.source);
            
            // Check for inline events data first
            if (window.__INLINE_EVENTS_DATA__) {
                this.log('Using inline events data');
                const data = window.__INLINE_EVENTS_DATA__;
                this.events = data.events || [];
                this.log(`Loaded ${this.events.length} events from inline data`);
                // Process template events with relative times
                this.events = this.processTemplateEvents(this.events);
                return;
            }
            
            // Fallback to fetching events if no inline data
            // Determine which data source(s) to load
            const dataSource = this.config.data?.source || 'real';
            const dataSources = this.config.data?.sources || {};
            
            let allEvents = [];
            
            if (dataSource === 'both' && dataSources.both?.urls) {
                // Load from multiple sources and combine
                this.log('Loading from multiple sources:', dataSources.both.urls);
                for (const url of dataSources.both.urls) {
                    try {
                        const response = await fetch(url);
                        const data = await response.json();
                        const events = data.events || [];
                        allEvents = allEvents.concat(events);
                        this.log(`Loaded ${events.length} events from ${url}`);
                    } catch (err) {
                        console.warn(`Failed to load events from ${url}:`, err);
                    }
                }
            } else {
                // Load from single source
                const sourceConfig = dataSources[dataSource];
                const url = sourceConfig?.url || 'events.json';
                this.log('Loading from single source:', url);
                
                const response = await fetch(url);
                const data = await response.json();
                allEvents = data.events || [];
                this.log(`Loaded ${allEvents.length} events from ${url}`);
            }
            
            // Process template events with relative times
            this.events = this.processTemplateEvents(allEvents);
            
            // Update dashboard with event count
            this.updateDashboard();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
    }
    
    processTemplateEvents(events) {
        /**
         * Dynamic Event Templates with Relative Times
         * 
         * Process events with relative_time specifications to calculate actual timestamps.
         * This allows demo events to always have fresh timestamps on every page load.
         * Creates copies of events to avoid mutation.
         * 
         * FEATURE: Dynamic event templates
         * PURPOSE: Demo events always display accurate relative times like "happening now" 
         *          or "starting in 5 minutes" without manual timestamp updates
         * 
         * USAGE: Events generated by scripts/generate_demo_events.py include a relative_time
         *        field that specifies how to calculate timestamps dynamically at page load.
         * 
         * SUPPORTED TYPES:
         * 1. "offset" - Relative to current time
         *    Example: {"type": "offset", "minutes": 5, "duration_hours": 2}
         *    Creates an event starting 5 minutes from now, lasting 2 hours
         * 
         * 2. "sunrise_relative" - Relative to next sunrise (simplified as 6:00 AM)
         *    Example: {"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}
         *    Creates an event starting 2 hours before sunrise, ending 1 hour after
         * 
         * INTEGRATION FLOW:
         * Demo Events (JSON) → window.ALL_EVENTS → window.ACTIVE_EVENTS → 
         * fetch intercept → loadEvents() → processTemplateEvents() → Display
         * 
         * For usage documentation, see README.md section "Advanced Features > Dynamic Event Templates"
         */
        const now = new Date();
        
        return events.map(event => {
            // If no relative_time spec, return event as-is
            if (!event.relative_time) {
                return event;
            }
            
            // Create a copy of the event to avoid mutation
            const processedEvent = { ...event };
            const spec = event.relative_time;
            const type = spec.type;
            
            let startTime, endTime;
            
            if (type === 'offset') {
                // Calculate start time from current time plus offset
                startTime = new Date(now);
                
                // Add hours offset
                if (spec.hours) {
                    startTime.setHours(startTime.getHours() + spec.hours);
                }
                
                // Add minutes offset
                if (spec.minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.minutes);
                }
                
                // Calculate end time using duration
                const durationMs = (spec.duration_hours || 2) * 60 * 60 * 1000;
                endTime = new Date(startTime.getTime() + durationMs);
                
                // Apply timezone offset if specified
                const tzOffset = spec.timezone_offset || 0;
                if (tzOffset !== 0) {
                    // Format with timezone
                    const sign = tzOffset >= 0 ? '+' : '-';
                    const hours = Math.abs(Math.floor(tzOffset));
                    const minutes = Math.abs((tzOffset % 1) * 60);
                    const tzString = `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                    
                    processedEvent.start_time = this.formatDateTimeWithTZ(startTime, tzString);
                    processedEvent.end_time = this.formatDateTimeWithTZ(endTime, tzString);
                } else {
                    processedEvent.start_time = this.formatDateTime(startTime);
                    processedEvent.end_time = this.formatDateTime(endTime);
                }
                
            } else if (type === 'sunrise_relative') {
                // Calculate next sunrise (simplified: 6 AM)
                const sunrise = this.getNextSunrise();
                
                // Calculate start time
                startTime = new Date(sunrise);
                if (spec.start_offset_hours) {
                    startTime.setHours(startTime.getHours() + spec.start_offset_hours);
                }
                if (spec.start_offset_minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.start_offset_minutes);
                }
                
                // Calculate end time
                endTime = new Date(sunrise);
                if (spec.end_offset_hours) {
                    endTime.setHours(endTime.getHours() + spec.end_offset_hours);
                }
                if (spec.end_offset_minutes) {
                    endTime.setMinutes(endTime.getMinutes() + spec.end_offset_minutes);
                }
                
                processedEvent.start_time = this.formatDateTime(startTime);
                processedEvent.end_time = this.formatDateTime(endTime);
            }
            
            // Update published_at to current time
            processedEvent.published_at = this.formatDateTime(now);
            
            return processedEvent;
        });
    }
    
    formatDateTime(date) {
        // Format as ISO 8601 without timezone: YYYY-MM-DDTHH:mm:ss
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    }
    
    formatDateTimeWithTZ(date, tzString) {
        // Format as ISO 8601 with timezone: YYYY-MM-DDTHH:mm:ss+HH:mm
        return this.formatDateTime(date) + tzString;
    }
    
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
    
    getMaxEventTime() {
        const now = new Date();
        const timeFilter = this.filters.timeFilter;
        
        switch (timeFilter) {
            case 'sunrise':
                // Simplified: next sunrise at 6 AM
                const sunrise = new Date(now);
                sunrise.setHours(6, 0, 0, 0);
                if (now.getHours() >= 6) {
                    sunrise.setDate(sunrise.getDate() + 1);
                }
                return sunrise;
                
            case '6h':
                return new Date(now.getTime() + 6 * 60 * 60 * 1000);
                
            case '12h':
                return new Date(now.getTime() + 12 * 60 * 60 * 1000);
                
            case '24h':
                return new Date(now.getTime() + 24 * 60 * 60 * 1000);
                
            case '48h':
                return new Date(now.getTime() + 48 * 60 * 60 * 1000);
                
            case 'all':
                // Return a date far in the future
                return new Date(now.getFullYear() + 10, 11, 31);
                
            default:
                return this.getNextSunrise();
        }
    }
    
    getNextSunrise() {
        // Simplified: next sunrise at 6 AM
        const now = new Date();
        const sunrise = new Date(now);
        sunrise.setHours(6, 0, 0, 0);
        
        if (now.getHours() >= 6) {
            sunrise.setDate(sunrise.getDate() + 1);
        }
        
        return sunrise;
    }
    
    filterEvents() {
        const maxEventTime = this.getMaxEventTime();
        const maxDistance = this.filters.maxDistance;
        const category = this.filters.category;
        
        // Determine which location to use for distance calculation
        let referenceLocation = this.userLocation;
        if (this.filters.useCustomLocation && this.filters.customLat && this.filters.customLon) {
            referenceLocation = {
                lat: this.filters.customLat,
                lon: this.filters.customLon
            };
        }
        
        const filtered = this.events.filter(event => {
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
    
    fitMapToMarkers() {
        if (this.markers.length === 0) {
            return;
        }
        
        // Create bounds from all marker positions
        const bounds = L.latLngBounds();
        
        this.markers.forEach(marker => {
            bounds.extend(marker.getLatLng());
        });
        
        // Add user location to bounds if available
        if (this.userLocation) {
            bounds.extend([this.userLocation.lat, this.userLocation.lon]);
        }
        
        // Fit the map to show all markers with some padding
        this.map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 15
        });
    }
    
    displayEvents() {
        const filteredEvents = this.filterEvents();
        
        // Update count with descriptive sentence
        this.updateFilterDescription(filteredEvents.length);
        
        // Update dashboard with event stats
        this.updateDashboard();
        
        // Ensure main content is visible (with error handling)
        this.showMainContent();
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        // Clear TimeDrawer markers if available
        if (this.timeDrawer) {
            this.timeDrawer.clearMarkers();
        }
        
        if (filteredEvents.length === 0) {
            // No events to display on map
            // Disable TimeDrawer when no events
            if (this.timeDrawer) {
                this.timeDrawer.disable();
            }
            return;
        }
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Display events as markers on the map
        filteredEvents.forEach(event => {
            this.addEventMarker(event);
        });
        
        // Fit map to show all markers
        this.fitMapToMarkers();
        
        // Enable/disable TimeDrawer based on filter and event count
        if (this.timeDrawer) {
            this.timeDrawer.enable(this.filters.timeFilter, filteredEvents.length);
        }
    }
    
    updateFilterDescription(count) {
        // Filter Bar Structure:
        // #event-filter-bar - Main container for all filter controls
        //   .filter-bar-logo - Logo/icon for visual identity
        //   #filter-bar-event-count - Shows "X events" with category
        //   #filter-bar-time-range - Time filter (sunrise, 6h, 12h, etc.)
        //   #filter-bar-distance - Distance filter (km radius)
        //   #filter-bar-location - Location source (here/custom)
        
        // Update individual parts of the filter sentence
        const eventCountCategoryText = document.getElementById('filter-bar-event-count');
        const timeText = document.getElementById('filter-bar-time-range');
        const distanceText = document.getElementById('filter-bar-distance');
        const locationText = document.getElementById('filter-bar-location');
        
        // Combined event count and category (KISS principle)
        if (eventCountCategoryText) {
            let categoryName = this.filters.category;
            
            if (this.filters.category === 'all') {
                // "0 events" or "5 events"
                eventCountCategoryText.textContent = `${count} event${count !== 1 ? 's' : ''}`;
            } else {
                // "0 music events" or "5 music events"
                eventCountCategoryText.textContent = `${count} ${categoryName} event${count !== 1 ? 's' : ''}`;
            }
        }
        
        // Time description
        if (timeText) {
            let timeDescription = '';
            switch (this.filters.timeFilter) {
                case 'sunrise':
                    timeDescription = 'till sunrise';
                    break;
                case '6h':
                    timeDescription = 'in the next 6 hours';
                    break;
                case '12h':
                    timeDescription = 'in the next 12 hours';
                    break;
                case '24h':
                    timeDescription = 'in the next 24 hours';
                    break;
                case '48h':
                    timeDescription = 'in the next 48 hours';
                    break;
                case 'all':
                    timeDescription = 'upcoming';
                    break;
            }
            timeText.textContent = timeDescription;
        }
        
        // Distance description (approximate travel time)
        if (distanceText) {
            const distance = this.filters.maxDistance;
            let distanceDescription = '';
            if (distance <= 1) {
                distanceDescription = 'within walking distance';
            } else if (distance <= 5) {
                const minutes = Math.round(distance * 3); // ~3 min per km walking
                distanceDescription = `within ${minutes} minutes walk`;
            } else if (distance <= 15) {
                const minutes = Math.round(distance * 4); // ~4 min per km by bike
                distanceDescription = `within ${minutes} minutes by bike`;
            } else {
                distanceDescription = `within ${distance} km`;
            }
            distanceText.textContent = distanceDescription;
        }
        
        // Location description
        if (locationText) {
            let locDescription = 'from here';
            if (this.filters.useCustomLocation && this.filters.customLat && this.filters.customLon) {
                locDescription = 'from custom location';
            } else if (!this.userLocation) {
                locDescription = 'from default location';
            }
            locationText.textContent = locDescription;
        }
    }
    
    displayEventCard(event, container) {
        const card = document.createElement('div');
        card.className = 'event-card';
        
        const title = document.createElement('h3');
        title.textContent = event.title;
        
        const location = document.createElement('p');
        location.textContent = `📍 ${event.location.name}`;
        
        const time = document.createElement('p');
        const eventDate = new Date(event.start_time);
        time.textContent = `🕐 ${eventDate.toLocaleString()}`;
        
        card.appendChild(title);
        card.appendChild(location);
        card.appendChild(time);
        
        if (event.distance !== undefined) {
            const distance = document.createElement('p');
            distance.className = 'distance';
            distance.textContent = `📏 ${event.distance.toFixed(1)} km away`;
            card.appendChild(distance);
        }
        
        card.addEventListener('click', () => this.showEventDetail(event));
        
        container.appendChild(card);
    }
    
    getMarkerIconForCategory(category) {
        // Return base64 data URL for marker icons from embedded MARKER_ICONS
        // Comprehensive mapping of event categories to marker icons
        const iconNameMap = {
            // Performance & Entertainment
            'on-stage': 'marker-on-stage',
            'performance': 'marker-on-stage',
            'concert': 'marker-music',
            'music': 'marker-music',
            'opera': 'marker-opera-house',
            'theater': 'marker-on-stage',
            'theatre': 'marker-on-stage',
            
            // Social & Games
            'pub-game': 'marker-pub-games',
            'pub': 'marker-pub-games',
            'bar': 'marker-pub-games',
            'games': 'marker-pub-games',
            
            // Festivals & Celebrations
            'festival': 'marker-festivals',
            'celebration': 'marker-festivals',
            'party': 'marker-festivals',
            
            // Educational & Skills
            'workshop': 'marker-workshops',
            'class': 'marker-workshops',
            'training': 'marker-workshops',
            'seminar': 'marker-workshops',
            'course': 'marker-workshops',
            'lecture': 'marker-school',
            'education': 'marker-school',
            
            // Shopping & Markets
            'market': 'marker-shopping',
            'shopping': 'marker-shopping',
            'farmers-market': 'marker-shopping',
            'bazaar': 'marker-shopping',
            
            // Sports & Fitness
            'sports': 'marker-sports',
            'sport': 'marker-sports',
            'fitness': 'marker-sports',
            'athletics': 'marker-sports-field',
            'swimming': 'marker-swimming',
            'pool': 'marker-swimming',
            
            // Community & Social Services
            'community': 'marker-community',
            'social': 'marker-community',
            'meetup': 'marker-community',
            'gathering': 'marker-community',
            'meeting': 'marker-community',
            
            // Arts & Culture
            'arts': 'marker-arts',
            'art': 'marker-arts',
            'exhibition': 'marker-museum',
            'gallery': 'marker-museum',
            'museum': 'marker-museum',
            
            // Food & Dining
            'food': 'marker-food',
            'dining': 'marker-food',
            'restaurant': 'marker-food',
            'culinary': 'marker-food',
            
            // Cultural & Religious
            'religious': 'marker-church',
            'worship': 'marker-church',
            'ceremony': 'marker-festivals',
            'traditional': 'marker-traditional-oceanic',
            'cultural': 'marker-traditional-oceanic',
            
            // Historical & Tourism
            'historical': 'marker-castle',
            'heritage': 'marker-monument',
            'monument': 'marker-monument',
            'landmark': 'marker-tower',
            'ruins': 'marker-ruins',
            'castle': 'marker-castle',
            'palace': 'marker-palace',
            
            // Parks & Nature
            'park': 'marker-park',
            'nature': 'marker-park',
            'outdoor': 'marker-park',
            'garden': 'marker-park',
            
            // Government & Civic
            'civic': 'marker-city-center',
            'government': 'marker-parliament',
            'political': 'marker-parliament',
            'city-hall': 'marker-mayors-office',
            
            // Libraries & Archives
            'library': 'marker-library',
            'archive': 'marker-national-archive',
            'books': 'marker-library',
            
            // Default fallback
            'other': 'marker-default',
            'general': 'marker-default',
            'event': 'marker-default'
        };
        
        const markerName = iconNameMap[category] || iconNameMap['other'];
        
        // Return base64 data URL from embedded MARKER_ICONS
        if (window.MARKER_ICONS && window.MARKER_ICONS[markerName]) {
            return window.MARKER_ICONS[markerName];
        }
        
        // Fallback: try alternative marker names
        const fallbackNames = ['marker-default', 'marker-community', 'marker-festivals'];
        for (const name of fallbackNames) {
            if (window.MARKER_ICONS && window.MARKER_ICONS[name]) {
                return window.MARKER_ICONS[name];
            }
        }
        
        // Ultimate fallback: return a data URL for a simple SVG circle
        return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDMyIDQ4Ij48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIxMiIgZmlsbD0iI0ZGNjlCNCIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48cGF0aCBkPSJNMTYgMjhMMTYgNDQiIHN0cm9rZT0iI0ZGNjlCNCIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+PC9zdmc+';
    }
    
    addEventMarker(event) {
        if (!event.location) return;
        
        // Check if event has custom marker icon, otherwise use category-based icon
        const iconUrl = event.marker_icon || this.getMarkerIconForCategory(event.category);
        
        // Support custom marker size if specified in event data
        const iconSize = event.marker_size || [32, 48];
        const iconAnchor = event.marker_anchor || [iconSize[0] / 2, iconSize[1]];
        const popupAnchor = event.marker_popup_anchor || [0, -iconSize[1]];
        
        // Create custom SVG icon using Leaflet's L.icon
        const customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: iconSize,
            iconAnchor: iconAnchor,
            popupAnchor: popupAnchor
        });
        
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: customIcon
        }).addTo(this.map);
        
        // Show edge detail on hover
        marker.on('mouseover', () => {
            this.showEventDetailAtEdge(event, marker);
        });
        
        // Hide edge detail when mouse leaves (with slight delay)
        marker.on('mouseout', () => {
            setTimeout(() => {
                // Only hide if not hovering over the detail box
                const edgeDetail = document.getElementById('current-edge-detail');
                if (edgeDetail && !edgeDetail.matches(':hover')) {
                    this.hideEventDetailAtEdge();
                }
            }, 200);
        });
        
        // Click shows full modal
        marker.on('click', () => this.showEventDetail(event));
        
        this.markers.push(marker);
        
        // Register marker with TimeDrawer if available
        if (this.timeDrawer) {
            // Generate a unique ID if event doesn't have one
            const eventId = event.id || `event_${event.title}_${event.start_time}`;
            this.timeDrawer.registerMarker(eventId, marker, event);
        }
    }
    
    navigateEvents(direction) {
        if (this.currentEventIndex === null || this.currentEventIndex === undefined) {
            this.currentEventIndex = 0;
        }
        
        // Get filtered events sorted by start time
        const filteredEvents = this.filterEvents();
        filteredEvents.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
        
        if (filteredEvents.length === 0) return;
        
        // Calculate next index with wrapping
        this.currentEventIndex = (this.currentEventIndex + direction + filteredEvents.length) % filteredEvents.length;
        
        const nextEvent = filteredEvents[this.currentEventIndex];
        this.showEventDetail(nextEvent);
        
        // Center map on the event
        if (this.map && nextEvent.location) {
            this.map.setView([nextEvent.location.lat, nextEvent.location.lon], 15);
        }
    }
    
    showEventDetail(event) {
        // Track current event index for keyboard navigation
        const filteredEvents = this.filterEvents();
        filteredEvents.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
        this.currentEventIndex = filteredEvents.findIndex(e => 
            (e.id && e.id === event.id) || 
            (e.title === event.title && e.start_time === event.start_time)
        );
        
        const detail = document.getElementById('event-detail');
        
        document.getElementById('detail-title').textContent = event.title;
        document.getElementById('detail-description').textContent = event.description || 'No description available.';
        document.getElementById('detail-location').textContent = event.location.name;
        
        const eventDate = new Date(event.start_time);
        document.getElementById('detail-time').textContent = eventDate.toLocaleString();
        
        if (event.distance !== undefined) {
            document.getElementById('detail-distance').textContent = `${event.distance.toFixed(1)} km away`;
        } else {
            document.getElementById('detail-distance').textContent = 'Unknown';
        }
        
        const link = document.getElementById('detail-link');
        if (event.url) {
            link.href = event.url;
            link.style.display = 'inline-block';
        } else {
            link.style.display = 'none';
        }
        
        detail.classList.remove('hidden');
    }
    
    // Edge-positioned event details with SVG arrows
    showEventDetailAtEdge(event, markerElement) {
        // Remove any existing edge details
        this.hideEventDetailAtEdge();
        
        if (!this.map || !markerElement) return;
        
        // Get marker position on screen
        const markerLatLng = markerElement.getLatLng();
        const markerPoint = this.map.latLngToContainerPoint(markerLatLng);
        
        // Create detail box
        const detailBox = document.createElement('div');
        detailBox.className = 'event-detail-edge';
        detailBox.id = 'current-edge-detail';
        
        // Format event data
        const eventDate = new Date(event.start_time);
        const timeStr = eventDate.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const distanceStr = event.distance !== undefined 
            ? `${event.distance.toFixed(1)} km away` 
            : '';
        
        detailBox.innerHTML = `
            <h3>${event.title}</h3>
            <p class="detail-time">🕐 ${timeStr}</p>
            <p>📍 ${event.location.name}</p>
            ${distanceStr ? `<p class="detail-distance">📏 ${distanceStr}</p>` : ''}
        `;
        
        // Add to overlay
        const mapOverlay = document.getElementById('map-overlay');
        mapOverlay.appendChild(detailBox);
        
        // Determine best edge position
        const position = this.calculateEdgePosition(markerPoint, detailBox);
        
        // Position the detail box
        detailBox.style.top = position.top + 'px';
        detailBox.style.left = position.left + 'px';
        
        // Draw SVG arrow
        this.drawArrowToDetailBox(markerPoint, position, detailBox);
        
        // Store reference
        this.currentEdgeDetail = {
            box: detailBox,
            event: event,
            marker: markerElement
        };
        
        // Click to show full detail modal
        detailBox.addEventListener('click', () => this.showEventDetail(event));
        
        // Keep detail visible when hovering over it
        detailBox.addEventListener('mouseenter', () => {
            // Cancel any pending hide timeout
            if (this.hideEdgeDetailTimeout) {
                clearTimeout(this.hideEdgeDetailTimeout);
                this.hideEdgeDetailTimeout = null;
            }
        });
        
        // Hide when mouse leaves the detail box
        detailBox.addEventListener('mouseleave', () => {
            this.hideEdgeDetailTimeout = setTimeout(() => {
                this.hideEventDetailAtEdge();
            }, 300);
        });
    }
    
    calculateEdgePosition(markerPoint, detailBox) {
        const mapContainer = document.getElementById('map');
        const mapRect = mapContainer.getBoundingClientRect();
        const boxRect = detailBox.getBoundingClientRect();
        
        const margin = 20;
        const boxWidth = 280;
        const boxHeight = boxRect.height || 120;
        
        let top, left, edge;
        
        // Determine which edge is closest
        const distToLeft = markerPoint.x;
        const distToRight = mapRect.width - markerPoint.x;
        const distToTop = markerPoint.y;
        const distToBottom = mapRect.height - markerPoint.y;
        
        const minDist = Math.min(distToLeft, distToRight, distToTop, distToBottom);
        
        if (minDist === distToRight) {
            // Position on right edge
            left = mapRect.width - boxWidth - margin;
            top = Math.max(margin, Math.min(markerPoint.y - boxHeight / 2, mapRect.height - boxHeight - margin));
            edge = 'right';
        } else if (minDist === distToLeft) {
            // Position on left edge
            left = margin;
            top = Math.max(margin, Math.min(markerPoint.y - boxHeight / 2, mapRect.height - boxHeight - margin));
            edge = 'left';
        } else if (minDist === distToBottom) {
            // Position on bottom edge
            top = mapRect.height - boxHeight - margin;
            left = Math.max(margin, Math.min(markerPoint.x - boxWidth / 2, mapRect.width - boxWidth - margin));
            edge = 'bottom';
        } else {
            // Position on top edge
            top = margin + 80; // Account for filter sentence at top
            left = Math.max(margin, Math.min(markerPoint.x - boxWidth / 2, mapRect.width - boxWidth - margin));
            edge = 'top';
        }
        
        return { top, left, edge, markerPoint };
    }
    
    drawArrowToDetailBox(markerPoint, position, detailBox) {
        const arrowContainer = document.getElementById('event-arrows-container');
        if (!arrowContainer) return;
        
        // Clear existing arrows
        arrowContainer.innerHTML = '';
        
        // Create SVG
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.pointerEvents = 'none';
        
        // Calculate detail box center
        const boxRect = detailBox.getBoundingClientRect();
        const boxCenterX = boxRect.left + boxRect.width / 2;
        const boxCenterY = boxRect.top + boxRect.height / 2;
        
        // Calculate connection points for smoother arrows
        let boxX, boxY;
        const dx = boxCenterX - markerPoint.x;
        const dy = boxCenterY - markerPoint.y;
        const angle = Math.atan2(dy, dx);
        
        // Find edge point on box
        if (Math.abs(dx) > Math.abs(dy)) {
            // Connect to left or right edge
            boxX = dx > 0 ? boxRect.left : boxRect.right;
            boxY = boxCenterY;
        } else {
            // Connect to top or bottom edge
            boxX = boxCenterX;
            boxY = dy > 0 ? boxRect.top : boxRect.bottom;
        }
        
        // Create curved path
        const midX = (markerPoint.x + boxX) / 2;
        const midY = (markerPoint.y + boxY) / 2;
        
        // Create path with quadratic curve
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const pathData = `M ${markerPoint.x} ${markerPoint.y} Q ${midX} ${midY} ${boxX} ${boxY}`;
        path.setAttribute('d', pathData);
        path.setAttribute('stroke', '#FF69B4');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-dasharray', '5,5');
        path.style.filter = 'drop-shadow(0 0 3px rgba(255, 105, 180, 0.5))';
        
        svg.appendChild(path);
        
        // Add arrowhead at box end
        const arrowhead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        const arrowSize = 8;
        const arrowAngle = Math.atan2(boxY - midY, boxX - midX);
        
        const p1x = boxX + arrowSize * Math.cos(arrowAngle + Math.PI * 0.8);
        const p1y = boxY + arrowSize * Math.sin(arrowAngle + Math.PI * 0.8);
        const p2x = boxX;
        const p2y = boxY;
        const p3x = boxX + arrowSize * Math.cos(arrowAngle - Math.PI * 0.8);
        const p3y = boxY + arrowSize * Math.sin(arrowAngle - Math.PI * 0.8);
        
        arrowhead.setAttribute('points', `${p1x},${p1y} ${p2x},${p2y} ${p3x},${p3y}`);
        arrowhead.setAttribute('fill', '#FF69B4');
        arrowhead.style.filter = 'drop-shadow(0 0 3px rgba(255, 105, 180, 0.5))';
        
        svg.appendChild(arrowhead);
        arrowContainer.appendChild(svg);
    }
    
    hideEventDetailAtEdge() {
        if (this.currentEdgeDetail) {
            if (this.currentEdgeDetail.box && this.currentEdgeDetail.box.parentElement) {
                this.currentEdgeDetail.box.remove();
            }
            this.currentEdgeDetail = null;
        }
        
        // Clear arrows
        const arrowContainer = document.getElementById('event-arrows-container');
        if (arrowContainer) {
            arrowContainer.innerHTML = '';
        }
    }
    
    setupEventListeners() {
        // Dashboard menu
        const dashboardLogo = document.getElementById('filter-bar-logo');
        const dashboardMenu = document.getElementById('dashboard-menu');
        const closeDashboard = document.getElementById('close-dashboard');
        
        if (dashboardLogo && dashboardMenu) {
            // Open dashboard on logo click
            dashboardLogo.addEventListener('click', () => {
                dashboardMenu.classList.remove('hidden');
                this.updateDashboard(); // Refresh data when opening
            });
            
            // Open dashboard on Enter/Space key
            dashboardLogo.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    dashboardMenu.classList.remove('hidden');
                    this.updateDashboard();
                }
            });
        }
        
        if (closeDashboard && dashboardMenu) {
            // Close dashboard on close button
            closeDashboard.addEventListener('click', () => {
                dashboardMenu.classList.add('hidden');
            });
        }
        
        if (dashboardMenu) {
            // Close dashboard on background click
            dashboardMenu.addEventListener('click', (e) => {
                if (e.target.id === 'dashboard-menu') {
                    dashboardMenu.classList.add('hidden');
                }
            });
        }
        
        // Custom dropdown helper class
        class CustomDropdown {
            constructor(triggerEl, items, currentValue, onSelect, app) {
                this.triggerEl = triggerEl;
                this.items = items;
                this.currentValue = currentValue;
                this.onSelect = onSelect;
                this.app = app;
                this.dropdownEl = null;
                this.isOpen = false;
                
                this.triggerEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (this.isOpen) {
                        this.close();
                    } else {
                        // Close other dropdowns first
                        document.querySelectorAll('.filter-bar-dropdown').forEach(d => d.remove());
                        document.querySelectorAll('.filter-bar-item').forEach(el => el.classList.remove('editing'));
                        this.open();
                    }
                });
            }
            
            open() {
                this.isOpen = true;
                this.triggerEl.classList.add('editing');
                
                // Create dropdown element
                this.dropdownEl = document.createElement('div');
                this.dropdownEl.className = 'filter-bar-dropdown';
                
                // Add items
                this.items.forEach(item => {
                    const itemEl = document.createElement('div');
                    itemEl.className = 'filter-bar-dropdown-item';
                    if (item.value === this.currentValue) {
                        itemEl.classList.add('selected');
                    }
                    itemEl.textContent = item.label;
                    itemEl.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.onSelect(item.value);
                        this.close();
                    });
                    this.dropdownEl.appendChild(itemEl);
                });
                
                // Position dropdown near trigger
                document.body.appendChild(this.dropdownEl);
                const rect = this.triggerEl.getBoundingClientRect();
                this.dropdownEl.style.left = `${rect.left}px`;
                this.dropdownEl.style.top = `${rect.bottom + 5}px`;
                
                // Adjust if off-screen
                setTimeout(() => {
                    const dropRect = this.dropdownEl.getBoundingClientRect();
                    if (dropRect.right > window.innerWidth) {
                        this.dropdownEl.style.left = `${window.innerWidth - dropRect.width - 10}px`;
                    }
                    if (dropRect.bottom > window.innerHeight) {
                        this.dropdownEl.style.top = `${rect.top - dropRect.height - 5}px`;
                    }
                }, 0);
            }
            
            close() {
                this.isOpen = false;
                this.triggerEl.classList.remove('editing');
                if (this.dropdownEl) {
                    this.dropdownEl.remove();
                    this.dropdownEl = null;
                }
            }
        }
        
        // Interactive filter sentence parts
        const categoryTextEl = document.getElementById('filter-bar-event-count');
        const timeTextEl = document.getElementById('filter-bar-time-range');
        const distanceTextEl = document.getElementById('filter-bar-distance');
        const locationTextEl = document.getElementById('filter-bar-location');
        
        // Store references to active dropdowns
        this.activeDropdown = null;
        this.activeFilterEl = null;
        
        // Helper to hide all dropdowns
        const hideAllDropdowns = () => {
            if (this.activeDropdown && this.activeDropdown.parentElement) {
                this.activeDropdown.remove();
                this.activeDropdown = null;
            }
            
            if (categoryTextEl) categoryTextEl.classList.remove('active');
            if (timeTextEl) timeTextEl.classList.remove('active');
            if (distanceTextEl) distanceTextEl.classList.remove('active');
            if (locationTextEl) locationTextEl.classList.remove('active');
            
            this.activeFilterEl = null;
        };
        
        // Helper to create and position dropdown
        const createDropdown = (content, targetEl) => {
            hideAllDropdowns();
            
            const dropdown = document.createElement('div');
            dropdown.className = 'filter-bar-dropdown';
            dropdown.innerHTML = content;
            
            // Add to body for proper positioning
            document.body.appendChild(dropdown);
            
            // Position below the target element
            const rect = targetEl.getBoundingClientRect();
            dropdown.style.position = 'fixed';
            dropdown.style.top = (rect.bottom + 5) + 'px';
            dropdown.style.left = rect.left + 'px';
            
            // Adjust if dropdown goes off screen
            const dropdownRect = dropdown.getBoundingClientRect();
            if (dropdownRect.right > window.innerWidth) {
                dropdown.style.left = (window.innerWidth - dropdownRect.width - 10) + 'px';
            }
            if (dropdownRect.bottom > window.innerHeight) {
                dropdown.style.top = (rect.top - dropdownRect.height - 5) + 'px';
            }
            
            this.activeDropdown = dropdown;
            this.activeFilterEl = targetEl;
            targetEl.classList.add('active');
            
            return dropdown;
        };
        
        // Category filter click
        if (categoryTextEl) {
            categoryTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === categoryTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                // Build category options from events
                let optionsHTML = '<option value="all">All Categories</option>';
                const categories = new Set();
                this.events.forEach(event => {
                    if (event.category) categories.add(event.category);
                });
                categories.forEach(cat => {
                    const selected = cat === this.filters.category ? ' selected' : '';
                    optionsHTML += `<option value="${cat}"${selected}>${cat}</option>`;
                });
                
                const content = `<select id="category-filter">${optionsHTML}</select>`;
                const dropdown = createDropdown(content, categoryTextEl);
                
                // Add event listener to select
                const select = dropdown.querySelector('#category-filter');
                select.value = this.filters.category;
                select.addEventListener('change', (e) => {
                    this.filters.category = e.target.value;
                    this.displayEvents();
                    hideAllDropdowns();
                });
            });
        }
        
        // Time filter click
        if (timeTextEl) {
            timeTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === timeTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const content = `
                    <select id="time-filter">
                        <option value="sunrise">Next Sunrise (6 AM)</option>
                        <option value="6h">Next 6 hours</option>
                        <option value="12h">Next 12 hours</option>
                        <option value="24h">Next 24 hours</option>
                        <option value="48h">Next 48 hours</option>
                        <option value="all">All upcoming events</option>
                    </select>
                `;
                const dropdown = createDropdown(content, timeTextEl);
                
                const select = dropdown.querySelector('#time-filter');
                select.value = this.filters.timeFilter;
                select.addEventListener('change', (e) => {
                    this.filters.timeFilter = e.target.value;
                    this.displayEvents();
                    hideAllDropdowns();
                });
            });
        }
        
        // Distance filter click
        if (distanceTextEl) {
            distanceTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === distanceTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const content = `
                    <input type="range" id="distance-filter" min="1" max="50" value="${this.filters.maxDistance}" step="0.5">
                    <span id="distance-value">${this.filters.maxDistance} km</span>
                `;
                const dropdown = createDropdown(content, distanceTextEl);
                
                const slider = dropdown.querySelector('#distance-filter');
                const valueDisplay = dropdown.querySelector('#distance-value');
                slider.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    this.filters.maxDistance = value;
                    valueDisplay.textContent = `${value} km`;
                    this.displayEvents();
                });
            });
        }
        
        // Location filter click
        if (locationTextEl) {
            locationTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === locationTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const latValue = this.filters.customLat || (this.userLocation ? this.userLocation.lat.toFixed(4) : '');
                const lonValue = this.filters.customLon || (this.userLocation ? this.userLocation.lon.toFixed(4) : '');
                const checked = this.filters.useCustomLocation ? ' checked' : '';
                const inputsHidden = !this.filters.useCustomLocation ? ' hidden' : '';
                
                const content = `
                    <label>
                        <input type="checkbox" id="use-custom-location"${checked}>
                        Use custom location
                    </label>
                    <div id="custom-location-inputs" class="${inputsHidden}">
                        <input type="number" id="custom-lat" placeholder="Latitude" step="0.0001" value="${latValue}">
                        <input type="number" id="custom-lon" placeholder="Longitude" step="0.0001" value="${lonValue}">
                        <button id="apply-custom-location">Apply</button>
                    </div>
                `;
                const dropdown = createDropdown(content, locationTextEl);
                
                const checkbox = dropdown.querySelector('#use-custom-location');
                const inputs = dropdown.querySelector('#custom-location-inputs');
                const applyBtn = dropdown.querySelector('#apply-custom-location');
                
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        inputs.classList.remove('hidden');
                        // Pre-fill with current location if available
                        if (this.userLocation) {
                            dropdown.querySelector('#custom-lat').value = this.userLocation.lat.toFixed(4);
                            dropdown.querySelector('#custom-lon').value = this.userLocation.lon.toFixed(4);
                        }
                    } else {
                        inputs.classList.add('hidden');
                        this.filters.useCustomLocation = false;
                        this.filters.customLat = null;
                        this.filters.customLon = null;
                        this.displayEvents();
                        hideAllDropdowns();
                    }
                });
                
                applyBtn.addEventListener('click', () => {
                    const lat = parseFloat(dropdown.querySelector('#custom-lat').value);
                    const lon = parseFloat(dropdown.querySelector('#custom-lon').value);
                    
                    if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                        this.filters.useCustomLocation = true;
                        this.filters.customLat = lat;
                        this.filters.customLon = lon;
                        
                        // Update map view to custom location
                        if (this.map) {
                            this.map.setView([lat, lon], 13);
                        }
                        
                        this.displayEvents();
                        hideAllDropdowns();
                    } else {
                        alert('Please enter valid latitude (-90 to 90) and longitude (-180 to 180) values.');
                    }
                });
            });
        }
        
        // Click outside to close dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#event-filter-bar') && !e.target.closest('.filter-bar-dropdown')) {
                hideAllDropdowns();
            }
        });
        
        // Event detail close listeners
        const closeDetail = document.getElementById('close-detail');
        const eventDetail = document.getElementById('event-detail');
        
        if (closeDetail) {
            closeDetail.addEventListener('click', () => {
                if (eventDetail) eventDetail.classList.add('hidden');
            });
        }
        
        if (eventDetail) {
            eventDetail.addEventListener('click', (e) => {
                if (e.target.id === 'event-detail') {
                    eventDetail.classList.add('hidden');
                }
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            const eventDetail = document.getElementById('event-detail');
            const dashboardMenu = document.getElementById('dashboard-menu');
            
            // ESC: Close event detail popup, dashboard, and dropdowns
            if (e.key === 'Escape') {
                if (eventDetail && !eventDetail.classList.contains('hidden')) {
                    eventDetail.classList.add('hidden');
                    e.preventDefault();
                } else if (dashboardMenu && !dashboardMenu.classList.contains('hidden')) {
                    dashboardMenu.classList.add('hidden');
                    e.preventDefault();
                }
                hideAllDropdowns();
            }
            
            // SPACE: Center map on user's geolocation
            if (e.key === ' ' || e.code === 'Space') {
                if (this.map && this.userLocation) {
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    e.preventDefault();
                }
            }
            
            // SHIFT + Arrow keys: Pan the map
            if (e.shiftKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
                if (this.map) {
                    const panAmount = 100; // pixels to pan
                    
                    switch(e.key) {
                        case 'ArrowUp':
                            this.map.panBy([0, -panAmount]);
                            break;
                        case 'ArrowDown':
                            this.map.panBy([0, panAmount]);
                            break;
                        case 'ArrowLeft':
                            this.map.panBy([-panAmount, 0]);
                            break;
                        case 'ArrowRight':
                            this.map.panBy([panAmount, 0]);
                            break;
                    }
                    e.preventDefault();
                }
            }
            // Arrow LEFT/RIGHT: Navigate through listed events (always)
            else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                this.navigateEvents(e.key === 'ArrowRight' ? 1 : -1);
                e.preventDefault();
            }
            
            // Map zoom shortcuts
            if (e.key === '+' || e.key === '=') {
                if (this.map) this.map.zoomIn();
                e.preventDefault();
            }
            if (e.key === '-' || e.key === '_') {
                if (this.map) this.map.zoomOut();
                e.preventDefault();
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
