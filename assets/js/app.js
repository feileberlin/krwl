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
        
        // Initialize modules
        this.storage = new EventStorage(this.config);
        this.eventFilter = new EventFilter(this.config, this.storage);
        this.mapManager = new MapManager(this.config, this.storage);
        this.speechBubbles = new SpeechBubbles(this.config, this.storage);
        this.utils = new EventUtils(this.config);
        this.dashboardUI = new DashboardUI(this.config, this.utils);
        this.filterDescriptionUI = new FilterDescriptionUI(this.config);
        this.eventListeners = new EventListeners(this);
        
        // App state
        this.events = [];
        this.currentEventIndex = null;
        this.currentEdgeDetail = null;
        this.duplicateStats = null;
        
        // Filter settings (load from storage module)
        this.filters = this.storage.loadFiltersFromCookie() || {
            maxDistance: 2,
            timeFilter: 'sunrise',
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
    
    getDefaultConfig() {
        return this.utils ? this.utils.getDefaultConfig() : {
            debug: false,
            app: { environment: 'unknown' },
            map: {
                default_center: { lat: 50.3167, lon: 11.9167 },
                default_zoom: 13,
                tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            },
            data: { source: 'real', sources: {} }
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
        
        // Get user location via MapManager (still works without map for filtering)
        this.mapManager.getUserLocation(
            (location) => {
                this.displayEvents();
            },
            (error) => {
                this.displayEvents();
            }
        );
        
        // Load events
        try {
            await this.loadEvents();
        } catch (error) {
            console.error('Failed to load events:', error);
            this.showMainContent();
        }
        
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
            this.updateDashboard();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
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
            weatherChip.setAttribute('title', `${temperature} • ${formatted}`);
        }
        
        weatherChip.style.display = '';
        this.log('Weather displayed:', formatted);
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
        this.speechBubbles.clearSpeechBubbles();
        
        if (filteredEvents.length === 0) return;
        
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
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
        
        // Show speech bubbles via SpeechBubbles module
        setTimeout(() => {
            this.speechBubbles.showAllSpeechBubbles(filteredEvents, markers, this.mapManager.map);
            
            // Add bookmark handlers to bubbles
            const bubbles = document.querySelectorAll('.bubble-bookmark');
            bubbles.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const eventId = btn.getAttribute('data-event-id');
                    const isBookmarked = this.storage.toggleBookmark(eventId);
                    btn.classList.toggle('bookmarked', isBookmarked);
                    
                    // Also toggle class on parent speech bubble for border styling
                    const speechBubble = btn.closest('.speech-bubble');
                    if (speechBubble) {
                        speechBubble.classList.toggle('bubble-is-bookmarked', isBookmarked);
                    }
                    
                    this.mapManager.updateMarkerBookmarkState(eventId, isBookmarked);
                    this.utils.showBookmarkFeedback(isBookmarked);
                });
            });
        }, 500);
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

}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
