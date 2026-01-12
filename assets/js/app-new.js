// KRWL HOF Community Events App - KISS Refactored
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
        
        this.showMainContent();
        
        // Initialize map via MapManager
        try {
            this.mapManager.initMap('map');
            this.mapManager.setupLeafletEventPrevention();
        } catch (error) {
            console.warn('Map initialization failed:', error.message);
            this.showMainContent();
        }
        
        // Get user location via MapManager
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
        
        // Check for pending events
        await this.checkPendingEvents();
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
            if (!this.config.weather?.display?.show_in_filter_bar) return;
            
            const cache = window.WEATHER_CACHE || {};
            const keys = Object.keys(cache);
            if (keys.length === 0) return;
            
            const key = keys.find(k => k.includes('Hof')) || keys[0];
            const entry = cache[key];
            
            if (entry?.data?.dresscode) {
                this.displayWeatherDresscode(entry.data.dresscode, entry.data.temperature);
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
