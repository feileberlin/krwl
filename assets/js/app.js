// ============================================================================
// PROGRESSIVE ENHANCEMENT: Enable JavaScript-dependent content
// ============================================================================
// This runs immediately (before DOMContentLoaded) to show the app container
// and hide the noscript fallback. Without JavaScript, users see event listings.
(function enableJavaScriptContent() {
    document.documentElement.classList.add('js-enabled');
    var appEl = document.getElementById('app');
    if (appEl) appEl.style.display = 'block';
})();

// ============================================================================
// KRWL HOF Community Events App - KISS Refactored
// ============================================================================
// 
// This file coordinates modules and handles UI interactions.
// Core logic delegated to focused modules (each < 500 lines):
// - EventStorage: Data persistence (localStorage, bookmarks)
// - EventFilter: Filtering logic (time, distance, category)  
// - MapManager: Leaflet map operations
// - SpeechBubbles: UI bubble components
// - EventUtils: Utility functions
//

class EventsApp {
    constructor() {
        // Get default config (will be replaced by utils module)
        this.config = window.APP_CONFIG || this.getDefaultConfig();
        
        // Detect and apply region from URL path (e.g., /hof, /nbg, /bth)
        this.applyRegionFromUrl();
        
        // Initialize modules
        this.storage = new EventStorage(this.config);
        this.eventFilter = new EventFilter(this.config, this.storage);
        this.mapManager = new MapManager(this.config, this.storage);
        // Speech bubbles disabled - using Leaflet default popups instead
        // this.speechBubbles = new SpeechBubbles(this.config, this.storage, (event) => this.showEventDetail(event));
        this.utils = new EventUtils(this.config);
        this.dashboardUI = new DashboardUI(this.config, this.utils);
        this.filterDescriptionUI = new FilterDescriptionUI(this.config);
        this.eventListeners = new EventListeners(this);
        this.formsManager = new FormsManager(this.config);
        
        // App state
        this.events = [];
        this.currentEventIndex = null;
        this.currentEdgeDetail = null;
        this.duplicateStats = null;
        
        // Filter settings (load from storage module)
        this.filters = this.storage.loadFiltersFromCookie() || {
            maxDistance: 50,  // INCREASED: 50km radius (was 2km) - shows more events
            timeFilter: '7d',  // CHANGED: 7 days (was 'sunrise' ~7 hours) - shows way more events
            category: 'all',
            locationType: 'geolocation',
            selectedPredefinedLocation: null,
            selectedCustomLocation: null,
            selectedCustomLocationName: null,  // Store display name
            useCustomLocation: false,
            customLat: null,
            customLon: null
        };
        
        // Debounce timer
        this.filterDebounceTimer = null;
        this.SLIDER_DEBOUNCE_DELAY = 100;
        
        // Animation durations
        this.ORIENTATION_CHANGE_DELAY = 100;
        this.DASHBOARD_EXPANSION_DURATION = 500;
        this.DASHBOARD_FADE_DURATION = 300;
        
        // Weather popup state
        this.weatherPopupInitialized = false; // Prevent duplicate event listeners
        this.weatherIframeLoaded = false;     // Prevent loading iframe multiple times
        this.weatherPopupFocusTrap = null;    // Focus trap for accessibility
        this.weatherPreloadTimer = null;      // Timer ID for preload cleanup
        
        // Dashboard state
        this.dashboardLastFocusedElement = null;
        this.dashboardTrapFocus = null;
        
        // Filter dropdown state
        this.activeDropdown = null;
        this.activeFilterEl = null;
        
        this.init();
    }
    
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[KRWL]', message, ...args);
        }
    }
    
    /**
     * Detect region from URL path and apply region-specific settings.
     * Supports paths like /hof, /nbg, /bth, /selb, /rehau
     * Also checks sessionStorage for redirected paths from 404.html
     * Handles both root (krwl.in/hof) and subdirectory (user.github.io/repo/hof) deployments
     * Unknown regions redirect to South Pole with setup instructions
     */
    applyRegionFromUrl() {
        // Check for redirected path from 404.html
        let path = sessionStorage.getItem('spa_redirect_path');
        let wasRedirected = false;
        if (path) {
            sessionStorage.removeItem('spa_redirect_path');
            wasRedirected = true;
        } else {
            path = window.location.pathname;
        }
        
        // Extract region ID from the last segment of the path
        // This handles both /hof and /repo/hof correctly
        const segments = path.split('/').filter(Boolean);
        const regionId = segments.length > 0 ? segments[segments.length - 1].toLowerCase() : '';
        
        if (!regionId || regionId === 'index.html') {
            return; // No region specified, use defaults
        }
        
        // Restore the original URL in the address bar if we were redirected via 404.html
        // This ensures krwl.in/hof stays as krwl.in/hof (not krwl.in)
        if (wasRedirected && path !== window.location.pathname) {
            history.replaceState(null, '', path);
            console.log(`[KRWL] Restored URL path: ${path}`);
        }
        
        // Check if this region exists in config
        const regions = this.config.regions || {};
        const region = regions[regionId];
        
        if (!region) {
            // Unknown region - redirect to South Pole with colony setup instructions
            console.log(`[KRWL] Unknown region: ${regionId} - showing colony setup at South Pole`);
            this.applyUnknownRegion(regionId);
            return;
        }
        
        console.log(`[KRWL] Applying region: ${regionId} (${region.displayName || region.name})`);
        
        // Apply region settings to config
        if (region.center) {
            this.config.map.default_center = {
                lat: region.center.lat,
                lon: region.center.lng || region.center.lon
            };
        }
        if (region.zoom) {
            this.config.map.default_zoom = region.zoom;
        }
        
        // Store active region for reference
        this.activeRegion = regionId;
        this.activeRegionConfig = region;
    }
    
    /**
     * Handle unknown/unconfigured regions by showing South Pole with setup instructions
     * @param {string} regionId - The unknown region ID from the URL
     */
    applyUnknownRegion(regionId) {
        // South Pole coordinates for unknown regions
        const SOUTH_POLE = { lat: -90, lon: 0 };
        const ONE_YEAR_MS = 365 * 24 * 60 * 60 * 1000;
        
        // Set map center to South Pole
        this.config.map.default_center = SOUTH_POLE;
        this.config.map.default_zoom = 3;
        
        // Store unknown region info - used by injectColonySetupEvent()
        this.activeRegion = regionId;
        this.isUnknownRegion = true;
        
        // Add a special "colony setup" event that will be injected into the events list
        // This replaces all normal events to focus attention on the setup instructions
        this.colonySetupEvent = {
            id: 'colony_setup_' + regionId,
            title: `🏴 Start a new colony: "${regionId}"`,
            description: `This region "${regionId}" is not yet configured. Want to bring KRWL to your area?\n\n` +
                `🚀 Option 1: Clone the repository\n` +
                `Fork https://github.com/feileberlin/krwl-hof and add your region to config.json\n\n` +
                `📧 Option 2: Contact the editors\n` +
                `Reach out to request "${regionId}" be added as a new region.\n\n` +
                `🌍 Join the community and help map events in your area!`,
            location: {
                name: 'South Pole - Unclaimed Territory',
                lat: SOUTH_POLE.lat,
                lon: SOUTH_POLE.lon
            },
            start_time: new Date(Date.now() + ONE_YEAR_MS).toISOString(),
            end_time: null,
            url: 'https://github.com/feileberlin/krwl-hof',
            source: 'system',
            status: 'published',
            category: 'community'
        };
    }
    
    getDefaultConfig() {
        return this.utils ? this.utils.getDefaultConfig() : {
            debug: false,
            app: { environment: 'unknown' },
            map: {
                default_center: { lat: 50.3167, lon: 11.9167 },  // Fallback only
                default_zoom: 13,  // Fallback only
                tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            },
            data: { source: 'real', sources: {} },
            _comment: 'Fallback config only - actual config loaded from window.APP_CONFIG'
        };
    }
    
    displayEventsDebounced(delay = this.SLIDER_DEBOUNCE_DELAY) {
        if (this.filterDebounceTimer) {
            clearTimeout(this.filterDebounceTimer);
        }
        this.filterDebounceTimer = setTimeout(() => {
            this.displayEvents();
            this.filterDebounceTimer = null;
        }, delay);
    }
    
    async init() {
        this.config = window.APP_CONFIG || this.getDefaultConfig();
        this.log('App initialized', 'Config:', this.config);
        
        // Make app instance globally available for dashboard
        window.app = this;
        window.eventsApp = this;
        
        this.showMainContent();
        
        // Initialize map via MapManager
        let mapInitialized = false;
        try {
            mapInitialized = this.mapManager.initMap('map');
            if (mapInitialized) {
                this.mapManager.setupLeafletEventPrevention();
            }
        } catch (error) {
            console.warn('Map initialization failed:', error.message);
        }
        
        // Load events FIRST (before geolocation) to avoid race condition
        // This ensures this.events is populated before displayEvents() is called
        try {
            await this.loadEvents();
        } catch (error) {
            console.error('Failed to load events:', error);
            this.showMainContent();
        }
        
        // Get user location via MapManager (still works without map for filtering)
        // Events are now loaded, so displayEvents() will have data to work with
        this.mapManager.getUserLocation(
            (location) => {
                this.displayEvents();
            },
            (error) => {
                this.displayEvents();
            }
        );
        
        // Load weather
        await this.loadWeather();
        
        // Setup event listeners
        this.setupEventListeners();
        this.initializeIcons();
        
        // Check for pending events
        await this.checkPendingEvents();
        this.updateDebugUnpublishedWarnings();
        this.startPendingEventsPolling();
        
        // Mark app as ready
        this.markAppAsReady();
        
        // Preload weather iframe after a short delay for better UX
        this.scheduleWeatherPreload();
    }
    
    markAppAsReady() {
        document.body.setAttribute('data-app-ready', 'true');
        window.dispatchEvent(new CustomEvent('app-ready', {
            detail: {
                timestamp: Date.now(),
                eventsLoaded: this.events.length,
                mapInitialized: !!this.mapManager.map
            }
        }));
        this.log('App ready signal sent');
    }
    
    /**
     * Schedule weather iframe preload after page is fully loaded
     * Preloads the iframe content in the background for instant popup display
     */
    scheduleWeatherPreload() {
        // Only preload if weather is enabled
        if (!this.config?.weather?.enabled) return;
        
        // Match UI gating: only preload when weather is shown in the filter bar
        if (!this.config?.weather?.display?.show_in_filter_bar) return;
        
        // Also require the weather chip element to exist and be visible
        const weatherChip = document.getElementById('filter-bar-weather');
        if (!weatherChip || weatherChip.offsetParent === null) return;
        
        // Delay preload to prioritize main content loading (3 seconds after app ready)
        const PRELOAD_DELAY = 3000;
        
        this.weatherPreloadTimer = setTimeout(() => {
            this.weatherPreloadTimer = null;
            this.log('Preloading weather iframe...');
            this.loadWeatherIframe();
        }, PRELOAD_DELAY);
    }
    
    showMainContent() {
        try {
            const mainContent = document.getElementById('main-content');
            if (mainContent && mainContent.style.display === 'none') {
                mainContent.style.display = 'block';
                this.log('Main content displayed');
            }
        } catch (error) {
            console.error('Failed to show main content:', error);
        }
    }

    initializeIcons() {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }
    
    async loadEvents() {
        try {
            this.log('Loading events...');
            
            if (window.__INLINE_EVENTS_DATA__) {
                this.log('Using inline events data');
                const data = window.__INLINE_EVENTS_DATA__;
                this.events = data.events || [];
                window.__EVENTS_DATA__ = data;
                this.log(`Loaded ${this.events.length} events from inline data`);
                this.events = this.utils.processTemplateEvents(this.events, this.eventFilter);
                
                // Inject colony setup event for unknown regions
                this.injectColonySetupEvent();
                return;
            }
            
            // Fallback to fetching
            const dataSource = this.config.data?.source || 'real';
            const dataSources = this.config.data?.sources || {};
            let allEvents = [];
            let eventsData = null;
            
            if (dataSource === 'both' && dataSources.both?.urls) {
                for (const url of dataSources.both.urls) {
                    try {
                        const response = await fetch(url);
                        const data = await response.json();
                        allEvents = allEvents.concat(data.events || []);
                        if (!eventsData && data.pending_count !== undefined) {
                            eventsData = data;
                        }
                    } catch (err) {
                        console.warn(`Failed to load from ${url}:`, err);
                    }
                }
            } else {
                const sourceConfig = dataSources[dataSource];
                const url = sourceConfig?.url || 'events.json';
                const response = await fetch(url);
                eventsData = await response.json();
                allEvents = eventsData.events || [];
            }
            
            if (eventsData) {
                window.__EVENTS_DATA__ = eventsData;
            }
            
            this.events = this.utils.processTemplateEvents(allEvents, this.eventFilter);
            
            // Inject colony setup event for unknown regions
            this.injectColonySetupEvent();
            
            this.updateDashboard();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
    }
    
    /**
     * Inject colony setup event for unknown regions
     * Clears normal events and shows only the setup instruction
     */
    injectColonySetupEvent() {
        if (this.isUnknownRegion && this.colonySetupEvent) {
            // For unknown regions, replace all events with just the colony setup event
            this.events = [this.colonySetupEvent];
            console.log(`[KRWL] Showing colony setup event for unknown region: ${this.activeRegion}`);
        }
    }
    
    async loadWeather() {
        try {
            // Check if weather is enabled and should be displayed
            const weather = this.config.weather;
            if (!weather?.enabled || !weather?.display?.show_in_filter_bar) return;
            
            // Get weather data from config (embedded by backend)
            const weatherData = weather.data;
            if (!weatherData) return;
            
            // Display dresscode if available
            if (weatherData.dresscode) {
                this.displayWeatherDresscode(weatherData.dresscode, weatherData.temperature);
            }
        } catch (error) {
            console.warn('Weather load failed:', error);
        }
    }
    
    displayWeatherDresscode(dresscode, temperature) {
        const weatherChip = this.utils.getCachedElement('#filter-bar-weather');
        if (!weatherChip) return;
        
        const formatted = `with ${dresscode}.`;
        weatherChip.textContent = formatted;
        
        if (temperature) {
            weatherChip.setAttribute('data-temperature', temperature);
            weatherChip.setAttribute('title', `${temperature} • ${formatted} • Click for full forecast`);
        }
        
        weatherChip.style.display = '';
        
        // Setup weather popup click handler (event listeners only)
        this.setupWeatherPopup(weatherChip);
        
        this.log('Weather displayed:', formatted);
    }
    
    /**
     * Setup weather popup click handlers
     * @param {HTMLElement} weatherChip - The weather chip button element
     */
    setupWeatherPopup(weatherChip) {
        // Prevent duplicate initialization (guard against multiple calls)
        if (this.weatherPopupInitialized) return;
        
        const popup = document.getElementById('weather-popup');
        const closeBtn = document.getElementById('weather-popup-close');
        const backdrop = popup?.querySelector('.weather-popup-backdrop');
        
        if (!popup || !weatherChip) return;
        
        // Mark as initialized to prevent duplicate event listeners
        this.weatherPopupInitialized = true;
        
        // Click weather chip to open popup
        weatherChip.addEventListener('click', (e) => {
            e.stopPropagation();
            this.openWeatherPopup();
        });
        
        // Close button
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeWeatherPopup());
        }
        
        // Click backdrop to close
        if (backdrop) {
            backdrop.addEventListener('click', () => this.closeWeatherPopup());
        }
        
        // Escape key to close (added only once due to guard above)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !popup.classList.contains('hidden')) {
                this.closeWeatherPopup();
            }
        });
    }
    
    /**
     * Load the wttr.in iframe content
     * Called either via preload (3s after app ready) or when popup is opened
     * Only loads once per session for efficiency
     * 
     * Security: allow-same-origin is required for wttr.in to function properly.
     * URL is pinned to https://wttr.in/* to prevent navigation to other origins.
     */
    loadWeatherIframe() {
        // Guard: Only load iframe once
        if (this.weatherIframeLoaded) return;
        
        const iframe = document.getElementById('weather-iframe');
        if (!iframe) return;
        
        // Mark as loaded to prevent duplicate requests
        this.weatherIframeLoaded = true;
        
        // Get location from weather config, fallback to map default center
        const locations = this.config?.weather?.locations;
        const location = locations?.[0];
        const defaultCenter = this.config?.map?.default_center;
        
        // Build wttr.in URL - use location name or coordinates
        // Format: ?2nTF (2=today+tomorrow, n=narrow, T=transparent, F=no Follow line)
        const lat = location?.lat || defaultCenter?.lat || 50.3167;
        const lon = location?.lon || defaultCenter?.lon || 11.9167;
        const locationStr = location?.name || `${lat},${lon}`;
        const wttrUrl = `https://wttr.in/${encodeURIComponent(locationStr)}?2nTF`;
        
        // Security: Validate URL hostname is pinned to wttr.in
        // Uses URL parsing to prevent path traversal attacks
        try {
            const parsedUrl = new URL(wttrUrl);
            if (parsedUrl.hostname !== 'wttr.in' || parsedUrl.protocol !== 'https:') {
                console.error('Weather iframe URL validation failed:', wttrUrl);
                return;
            }
        } catch (e) {
            console.error('Weather iframe URL parsing failed:', e);
            return;
        }
        
        // Set iframe src (preloaded in background for instant popup display)
        iframe.src = wttrUrl;
        
        this.log('Weather iframe loaded:', wttrUrl);
    }
    
    /**
     * Open the weather popup with focus trap
     */
    openWeatherPopup() {
        const popup = document.getElementById('weather-popup');
        const weatherChip = document.getElementById('filter-bar-weather');
        
        if (!popup) return;
        
        // Load iframe if not already preloaded
        this.loadWeatherIframe();
        
        popup.classList.remove('hidden');
        weatherChip?.setAttribute('aria-expanded', 'true');
        
        // Setup focus trap for accessibility (WCAG 2.1 compliance)
        this.setupWeatherPopupFocusTrap(popup);
        
        // Focus close button for accessibility
        const closeBtn = document.getElementById('weather-popup-close');
        if (closeBtn) {
            closeBtn.focus();
        }
        
        this.log('Weather popup opened');
    }
    
    /**
     * Setup focus trap to prevent focus from leaving the modal
     * @param {HTMLElement} popup - The popup element
     */
    setupWeatherPopupFocusTrap(popup) {
        const focusableElements = popup.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), iframe'
        );
        
        // Guard: Need at least one focusable element
        if (focusableElements.length === 0) return;
        
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        // Remove any existing trap
        if (this.weatherPopupFocusTrap) {
            document.removeEventListener('keydown', this.weatherPopupFocusTrap);
        }
        
        // Create focus trap handler
        this.weatherPopupFocusTrap = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                // Shift+Tab: if on first element, wrap to last
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                // Tab: if on last element, wrap to first
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        };
        
        document.addEventListener('keydown', this.weatherPopupFocusTrap);
    }
    
    /**
     * Close the weather popup and remove focus trap
     */
    closeWeatherPopup() {
        const popup = document.getElementById('weather-popup');
        const weatherChip = document.getElementById('filter-bar-weather');
        
        if (!popup) return;
        
        popup.classList.add('hidden');
        weatherChip?.setAttribute('aria-expanded', 'false');
        
        // Remove focus trap
        if (this.weatherPopupFocusTrap) {
            document.removeEventListener('keydown', this.weatherPopupFocusTrap);
            this.weatherPopupFocusTrap = null;
        }
        
        // Return focus to weather chip
        if (weatherChip) {
            weatherChip.focus();
        }
        
        this.log('Weather popup closed');
    }
    
    displayEvents() {
        // Use EventFilter module for filtering
        const location = this.getReferenceLocation();
        const filteredEvents = this.eventFilter.filterEvents(this.events, this.filters, location);
        
        this.updateFilterDescription(filteredEvents.length);
        this.updateDashboard();
        this.showMainContent();
        
        // Use MapManager to clear and add markers
        this.mapManager.clearMarkers();
        // Speech bubbles disabled - using Leaflet default popups
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Check if map is available or if we're in fallback mode
        if (this.mapManager.isFallbackMode) {
            // Render events to fallback list when map is unavailable
            // Cards have direct "More info" links, no click handler needed
            this.mapManager.renderFallbackEventList(filteredEvents);
            return;
        }
        
        if (filteredEvents.length === 0) return;
        
        // Add markers via MapManager
        const markers = [];
        filteredEvents.forEach(event => {
            const marker = this.mapManager.addEventMarker(event, (evt, mkr) => {
                this.showEventDetail(evt);
            });
            markers.push(marker);
        });
        
        // Fit map
        this.mapManager.fitMapToMarkers();
        
        // Speech bubbles disabled - using Leaflet default popups instead
        // Popups are automatically bound to markers in mapManager.addEventMarker()
    }
    
    getReferenceLocation() {
        if (this.filters.locationType === 'predefined' && this.filters.selectedPredefinedLocation !== null) {
            const locs = this.config?.map?.predefined_locations || [];
            const loc = locs[this.filters.selectedPredefinedLocation];
            return loc ? { lat: loc.lat, lon: loc.lon } : this.mapManager.userLocation;
        } else if (this.filters.locationType === 'custom' && this.filters.customLat && this.filters.customLon) {
            return { lat: this.filters.customLat, lon: this.filters.customLon };
        }
        return this.mapManager.userLocation;
    }

    updateDashboard() {
        // Delegate to DashboardUI module
        this.dashboardUI.update(this.duplicateStats);
    }

    updateDuplicateWarnings() {
        // Calculate duplicate statistics
        if (!this.events || this.events.length === 0) {
            this.duplicateStats = null;
            return;
        }

        const titleMap = new Map();
        this.events.forEach(event => {
            const key = event.title.toLowerCase().trim();
            if (!titleMap.has(key)) {
                titleMap.set(key, []);
            }
            titleMap.get(key).push(event);
        });

        const duplicates = [];
        titleMap.forEach((events, title) => {
            if (events.length > 1) {
                duplicates.push({ title: events[0].title, count: events.length });
            }
        });

        if (duplicates.length > 0) {
            this.duplicateStats = {
                total: duplicates.reduce((sum, d) => sum + d.count, 0),
                events: duplicates.length,
                details: duplicates.sort((a, b) => b.count - a.count).slice(0, 5)
            };
        } else {
            this.duplicateStats = null;
        }
    }


    async checkPendingEvents() {
        /**
         * Check for pending events and update UI notifications
         * 
         * Reads pending_count from the events data that's already loaded.
         * Updates:
         * 1. Dashboard notification box (if count > 0)
         * 2. Browser tab title (adds ❗ emoji if count > 0)
         * 
         * This is lightweight and uses existing data - no extra HTTP request needed!
         */
        try {
            // Check if we have events data loaded with pending_count field
            const eventsData = window.__EVENTS_DATA__ || null;
            
            if (!eventsData || typeof eventsData.pending_count === 'undefined') {
                // No pending count data available (backward compatibility)
                this.log('No pending count data available');
                return;
            }
            
            const count = eventsData.pending_count || 0;
            
            this.log('Pending events count:', count);
            
            // Update browser title
            const baseTitle = 'KRWL HOF - Community Events';
            if (count > 0) {
                document.title = '❗ ' + baseTitle;
            } else {
                document.title = baseTitle;
            }
            
            // Update dashboard notification
            const notificationBox = document.getElementById('pending-notification');
            const notificationText = document.getElementById('pending-notification-text');
            
            if (notificationBox && notificationText) {
                if (count > 0) {
                    notificationText.textContent = `${count} pending event${count > 1 ? 's' : ''} awaiting review`;
                    notificationBox.style.display = 'flex';
                    notificationBox.setAttribute('aria-hidden', 'false');
                } else {
                    notificationBox.style.display = 'none';
                    notificationBox.setAttribute('aria-hidden', 'true');
                }
            }
        } catch (error) {
            this.log('Could not check pending events:', error.message);
            // Fail silently - this is a non-critical feature
        }
    }

    updateDebugUnpublishedWarnings() {
        /**
         * Update debug section with unpublished events and unverified locations warnings
         * 
         * Shows warnings in the debug area (bottom of dashboard) when:
         * - There are pending events awaiting review
         * - There are unverified locations needing verification
         * - Debug mode is enabled (config.debug === true)
         */
        try {
            // Only show in debug mode
            if (!this.config || !this.config.debug) {
                return;
            }
            
            const eventsData = window.__EVENTS_DATA__ || null;
            
            if (!eventsData) {
                return;
            }
            
            const pendingCount = eventsData.pending_count || 0;
            const unverifiedCount = eventsData.unverified_locations_count || 0;
            const warningBox = document.getElementById('debug-unpublished-warnings');
            const warningContent = document.getElementById('debug-unpublished-content');
            
            if (!warningBox || !warningContent) {
                return;
            }
            
            // Show warnings if either count > 0
            if (pendingCount > 0 || unverifiedCount > 0) {
                let messages = [];
                
                // Get repository URL from config (fallback to hardcoded for backward compatibility)
                const repoUrl = this.config?.app?.repository?.url || 'https://github.com/feileberlin/krwl-hof';
                
                // Pending events warning
                if (pendingCount > 0) {
                    messages.push(`
                        <div class="debug-warning-message">
                            <strong>${pendingCount} unpublished event${pendingCount > 1 ? 's' : ''}</strong> 
                            ${pendingCount > 1 ? 'are' : 'is'} awaiting editorial review.
                        </div>
                        <div class="debug-warning-hint">
                            Events must be reviewed and approved before appearing on the map.
                            <a href="${repoUrl}/actions/workflows/scrape-events.yml" 
                               target="_blank" 
                               rel="noopener noreferrer"
                               class="debug-warning-link">→ Review Events in GitHub Actions</a>
                        </div>
                    `);
                }
                
                // Unverified locations warning
                if (unverifiedCount > 0) {
                    const unverifiedMessageClass = `debug-warning-message${pendingCount > 0 ? ' with-spacing' : ''}`;
                    messages.push(`
                        <div class="${unverifiedMessageClass}">
                            <strong>${unverifiedCount} unverified location${unverifiedCount > 1 ? 's' : ''}</strong> 
                            ${unverifiedCount > 1 ? 'need' : 'needs'} verification.
                        </div>
                        <div class="debug-warning-hint">
                            Locations should be added to <code>verified_locations.json</code> to prevent duplicates.
                            <a href="${repoUrl}/blob/main/assets/json/unverified_locations.json" 
                               target="_blank" 
                               rel="noopener noreferrer"
                               class="debug-warning-link">→ View Unverified Locations</a>
                        </div>
                    `);
                }
                
                warningContent.innerHTML = messages.join('');
                warningBox.style.display = 'block';
            } else {
                warningBox.style.display = 'none';
            }
        } catch (error) {
            this.log('Could not update debug unpublished warnings:', error.message);
        }
    }

    startPendingEventsPolling() {
        /**
         * Set up periodic checking for pending events
         * Checks every 5 minutes
         * 
         * Note: In practice, this will only update if the page is refreshed
         * since events data is embedded at build time. But we keep it for
         * potential future enhancements (e.g., dynamic loading).
         */
        setInterval(() => {
            this.checkPendingEvents();
        }, 5 * 60 * 1000); // 5 minutes
    }


    updateFilterDescription(count) {
        // Delegate to FilterDescriptionUI module
        this.filterDescriptionUI.update(count, this.filters, this.userLocation);
    }

    setupEventListeners() {
        // Delegate to EventListeners module
        this.eventListeners.setupEventListeners();
    }

    navigateEvents(direction) {
        if (this.currentEventIndex === null || this.currentEventIndex === undefined) {
            this.currentEventIndex = 0;
        }
        
        // Get filtered events sorted by start time
        const location = this.getReferenceLocation();
        const filteredEvents = this.eventFilter.filterEvents(this.events, this.filters, location);
        filteredEvents.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
        
        if (filteredEvents.length === 0) return;
        
        // Calculate next index with wrapping
        this.currentEventIndex = (this.currentEventIndex + direction + filteredEvents.length) % filteredEvents.length;
        
        const nextEvent = filteredEvents[this.currentEventIndex];
        this.showEventDetail(nextEvent);
        
        // Center map on the event
        if (this.mapManager.map && nextEvent.location) {
            this.mapManager.map.setView([nextEvent.location.lat, nextEvent.location.lon], 15);
        }
    }
    

    showEventDetail(event) {
        // Track current event index for keyboard navigation
        const location = this.getReferenceLocation();
        const filteredEvents = this.eventFilter.filterEvents(this.events, this.filters, location);
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

}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
