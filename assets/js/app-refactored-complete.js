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

    updateDashboard() {
        // Update dashboard debug info with current state
        const debugSection = document.getElementById('dashboard-debug-section');
        
        // Use DEBUG_INFO from backend if available
        const debugInfo = window.DEBUG_INFO || {};
        
        // Git commit stamp (prominent display)
        const commitHash = document.getElementById('debug-commit-hash');
        const commitAuthor = document.getElementById('debug-commit-author');
        const commitDate = document.getElementById('debug-commit-date');
        const commitMessage = document.getElementById('debug-commit-message');
        
        if (debugInfo.git_commit) {
            const git = debugInfo.git_commit;
            if (commitHash) commitHash.textContent = git.hash || 'unknown';
            if (commitAuthor) commitAuthor.textContent = git.author || 'unknown';
            if (commitDate) commitDate.textContent = git.date || 'unknown';
            if (commitMessage) {
                commitMessage.textContent = git.message || 'unknown';
                commitMessage.title = git.message || 'No commit message';
            }
        }
        
        // Deployment time
        const deploymentTime = document.getElementById('debug-deployment-time');
        if (deploymentTime && debugInfo.deployment_time) {
            try {
                const date = new Date(debugInfo.deployment_time);
                deploymentTime.textContent = date.toLocaleString();
                deploymentTime.title = `Deployment timestamp: ${debugInfo.deployment_time}`;
            } catch (e) {
                deploymentTime.textContent = debugInfo.deployment_time;
            }
        }
        
        // Event counts (individual fields)
        const eventCountsPublished = document.getElementById('debug-event-counts-published');
        const eventCountsPending = document.getElementById('debug-event-counts-pending');
        const eventCountsArchived = document.getElementById('debug-event-counts-archived');
        const eventCountsTotal = document.getElementById('debug-event-counts-total');
        
        if (debugInfo.event_counts) {
            const counts = debugInfo.event_counts;
            if (eventCountsPublished) eventCountsPublished.textContent = counts.published || 0;
            if (eventCountsPending) eventCountsPending.textContent = counts.pending || 0;
            if (eventCountsArchived) eventCountsArchived.textContent = counts.archived || 0;
            if (eventCountsTotal) eventCountsTotal.textContent = counts.total || 0;
        }
        
        // Environment
        const debugEnvironment = document.getElementById('debug-environment');
        if (debugEnvironment) {
            const environment = debugInfo.environment || this.config?.watermark?.text || this.config?.app?.environment || 'UNKNOWN';
            debugEnvironment.textContent = environment.toUpperCase();
            // Add color coding based on environment using CSS classes
            debugEnvironment.className = 'debug-env-badge';
            if (environment.toLowerCase().includes('dev')) {
                debugEnvironment.classList.add('env-dev');
            } else if (environment.toLowerCase().includes('production')) {
                debugEnvironment.classList.add('env-production');
            } else if (environment.toLowerCase().includes('ci')) {
                debugEnvironment.classList.add('env-ci');
            }
        }
        
        // Caching status
        const debugCaching = document.getElementById('debug-caching');
        if (debugCaching) {
            const cacheEnabled = debugInfo.cache_enabled;
            if (cacheEnabled !== undefined) {
                debugCaching.textContent = cacheEnabled ? 'Enabled' : 'Disabled';
                debugCaching.className = cacheEnabled ? 'cache-enabled' : 'cache-disabled';
            } else {
                debugCaching.textContent = 'Unknown';
            }
        }
        
        // File size information
        const debugFileSize = document.getElementById('debug-file-size');
        if (debugFileSize && debugInfo.html_sizes) {
            const sizes = debugInfo.html_sizes;
            const totalKB = (sizes.total / 1024).toFixed(1);
            
            if (debugInfo.cache_enabled && debugInfo.cache_file_size) {
                // Show cache file size if caching is enabled
                const cacheKB = (debugInfo.cache_file_size / 1024).toFixed(1);
                debugFileSize.textContent = `${totalKB} KB (HTML) | ${cacheKB} KB (Cache)`;
                debugFileSize.title = `Cache file: ${debugInfo.cache_file_path || 'unknown'}`;
            } else {
                // Show HTML size only
                debugFileSize.textContent = `${totalKB} KB (HTML only)`;
                if (!debugInfo.cache_enabled) {
                    debugFileSize.title = 'Caching disabled - showing HTML size only';
                }
            }
        }
        
        // Size breakdown
        const debugSizeBreakdown = document.getElementById('debug-size-breakdown');
        if (debugSizeBreakdown && debugInfo.html_sizes) {
            const sizes = debugInfo.html_sizes;
            
            // Show top 3 largest components
            const components = [
                { name: 'Events', size: sizes.events_data },
                { name: 'Scripts', size: sizes.scripts },
                { name: 'Styles', size: sizes.stylesheets },
                { name: 'Translations', size: sizes.translations },
                { name: 'Markers', size: sizes.marker_icons },
                { name: 'Other', size: sizes.other }
            ];
            
            components.sort((a, b) => b.size - a.size);
            
            // Build breakdown as list items
            let breakdownHTML = '<ul class="debug-size-list">';
            for (let i = 0; i < 3 && i < components.length; i++) {
                const comp = components[i];
                const kb = (comp.size / 1024).toFixed(1);
                const percent = ((comp.size / sizes.total) * 100).toFixed(1);
                breakdownHTML += `<li>${comp.name}: ${kb} KB (${percent}%)</li>`;
            }
            breakdownHTML += '</ul>';
            
            debugSizeBreakdown.innerHTML = breakdownHTML;
            
            // Full breakdown in title
            const fullBreakdown = components.map(c => 
                `${c.name}: ${(c.size / 1024).toFixed(1)} KB (${((c.size / sizes.total) * 100).toFixed(1)}%)`
            ).join('\n');
            debugSizeBreakdown.title = `Full breakdown:\n${fullBreakdown}`;
        }
        
        // OPTIMIZATION INFO: Display cache statistics
        const debugDOMCache = document.getElementById('debug-dom-cache');
        if (debugDOMCache) {
            const cacheSize = Object.keys(this.utils.domCache).length;
            const cacheStatus = cacheSize > 0 ? `${cacheSize} elements cached` : 'No elements cached';
            debugDOMCache.textContent = cacheStatus;
            debugDOMCache.title = `DOM elements cached: ${Object.keys(this.utils.domCache).join(', ') || 'none'}`;
        }
        
        const debugHistoricalCache = document.getElementById('debug-historical-cache');
        if (debugHistoricalCache) {
            // Note: Frontend doesn't have access to backend Python cache
            // This shows if we implement a frontend cache in the future
            debugHistoricalCache.textContent = 'Backend (Python)';
            debugHistoricalCache.title = 'Historical events are cached in the backend during scraping to improve performance';
        }
        
        // Detect and display event duplicates
        this.updateDuplicateWarnings();
        
        // Show debug section after data is loaded
        if (debugSection && debugSection.style.display === 'none') {
            debugSection.style.display = 'block';
        }
    }

    updateDuplicateWarnings() {
        const warningElement = document.getElementById('debug-duplicate-warnings');
        
        if (!warningElement) {
            this.log('Debug duplicate warnings element not found');
            return;
        }
        
        if (!this.duplicateStats || this.duplicateStats.total === 0) {
            // No duplicates - hide warning
            warningElement.style.display = 'none';
            return;
        }
        
        // Show duplicate warning
        const stats = this.duplicateStats;
        const warningIcon = '⚠️';
        const warningMessage = `${warningIcon} ${stats.total} duplicate event${stats.total > 1 ? 's' : ''} detected (${stats.eventsWithDuplicates} unique event${stats.eventsWithDuplicates > 1 ? 's' : ''} with duplicates)`;
        
        // Build detail list (limit to top 5)
        const detailsHTML = stats.details.slice(0, 5).map(d => 
            `<li>${d.title.substring(0, 40)}${d.title.length > 40 ? '...' : ''} (×${d.count})</li>`
        ).join('');
        
        const moreText = stats.details.length > 5 ? `<li>...and ${stats.details.length - 5} more</li>` : '';
        
        warningElement.innerHTML = `
            <div class="debug-duplicate-warning-header">${warningMessage}</div>
            <ul class="debug-duplicate-list">
                ${detailsHTML}
                ${moreText}
            </ul>
        `;
        warningElement.style.display = 'block';
        
        this.log('Duplicate warnings updated:', stats);
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
        // Filter Bar Structure (Semantic Header):
        // <header id="event-filter-bar"> - Page header/banner with filters
        //   <button .filter-bar-logo> - Project menu button
        //   <div role="status"> - Live region for event count updates
        //     #filter-bar-event-count - Shows "X events" with category
        //   #filter-bar-time-range - Time filter button (sunrise, 6h, 12h, etc.)
        //   #filter-bar-distance - Distance filter button (km radius)
        //   #filter-bar-location - Location filter button (here/custom)
        
        // Update individual parts of the filter sentence
        const eventCountCategoryText = document.getElementById('filter-bar-event-count');
        const timeText = document.getElementById('filter-bar-time-range');
        const distanceText = document.getElementById('filter-bar-distance');
        const locationText = document.getElementById('filter-bar-location');
        
        // Combined event count and category (KISS principle)
        if (eventCountCategoryText) {
            let categoryName = this.filters.category;
            
            if (this.filters.category === 'all') {
                // "[0 events]" or "[5 events]"
                eventCountCategoryText.textContent = `[${count} event${count !== 1 ? 's' : ''}]`;
            } else {
                // "[0 music events]" or "[5 music events]"
                eventCountCategoryText.textContent = `[${count} ${categoryName} event${count !== 1 ? 's' : ''}]`;
            }
        }
        
        // Time description
        if (timeText) {
            let timeDescription = '';
            switch (this.filters.timeFilter) {
                case 'sunrise':
                    timeDescription = 'till sunrise';
                    break;
                case 'sunday-primetime':
                    timeDescription = "till Sunday's primetime";
                    break;
                case 'full-moon':
                    timeDescription = 'till next full moon';
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
            timeText.textContent = `[${timeDescription}]`;
        }
        
        // Distance description (approximate travel time)
        if (distanceText) {
            const distance = this.filters.maxDistance;
            let distanceDescription = '';
            
            // Match predefined distance filter options
            if (distance === 2) {
                distanceDescription = 'within 30 min walk';
            } else if (distance === 3.75) {
                distanceDescription = 'within 30 min bicycle ride';
            } else if (distance === 12.5) {
                distanceDescription = 'within 30 min public transport';
            } else if (distance === 60) {
                distanceDescription = 'within 60 min car sharing';
            } else {
                // Fallback for any other distance values (backward compatibility)
                distanceDescription = `within ${distance} km`;
            }
            distanceText.textContent = `[${distanceDescription}]`;
        }
        
        // Location description
        if (locationText) {
            let locDescription = window.i18n ? window.i18n.t('filters.locations.geolocation') : 'from here';
            
            if (this.filters.locationType === 'predefined' && this.filters.selectedPredefinedLocation !== null) {
                // Get predefined location name from config
                const predefinedLocs = this.config?.map?.predefined_locations || [];
                const selectedLoc = predefinedLocs[this.filters.selectedPredefinedLocation];
                if (selectedLoc) {
                    // Try to get translated name, fallback to display_name
                    const translatedName = window.i18n ? window.i18n.t(`filters.predefined_locations.${selectedLoc.name}`) : selectedLoc.display_name;
                    const prefix = window.i18n ? window.i18n.t('filters.locations.prefix') : 'from';
                    locDescription = `${prefix} ${translatedName}`;
                }
            } else if (this.filters.locationType === 'custom' && this.filters.customLat && this.filters.customLon) {
                locDescription = 'from custom location';
            } else if (!this.userLocation && this.filters.locationType === 'geolocation') {
                locDescription = 'from default location';
            }
            
            locationText.textContent = `[${locDescription}]`;
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

    setupEventListeners() {
        // Dashboard menu with focus management
        const dashboardLogo = document.getElementById('filter-bar-logo');
        const dashboardMenu = document.getElementById('dashboard-menu');
        const closeDashboard = document.getElementById('close-dashboard');
        
        // Store last focused element and focus trap function in class properties for ESC handler access
        this.dashboardLastFocusedElement = null;
        
        // Focus trap helper
        this.dashboardTrapFocus = (e) => {
            if (e.key !== 'Tab') return;
            if (dashboardMenu.classList.contains('hidden')) return;
            
            const focusableElements = dashboardMenu.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        };
        
        if (dashboardLogo && dashboardMenu) {
            // Open dashboard on logo click with animation
            dashboardLogo.addEventListener('click', async () => {
                this.dashboardLastFocusedElement = document.activeElement;
                
                // Get filter bar element for animation
                const filterBar = document.getElementById('event-filter-bar');
                
                // Step 1: Expand filter bar (triggers CSS transition)
                if (filterBar) {
                    filterBar.classList.add('dashboard-opening');
                    
                    // Step 2: Wait for expansion to complete using transitionend event
                    await new Promise(resolve => {
                        const handleTransitionEnd = (e) => {
                            // Only resolve when the filter bar's transition ends (not child elements)
                            if (e.target === filterBar) {
                                filterBar.removeEventListener('transitionend', handleTransitionEnd);
                                resolve();
                            }
                        };
                        filterBar.addEventListener('transitionend', handleTransitionEnd);
                        
                        // Fallback timeout in case transitionend doesn't fire
                        setTimeout(resolve, this.DASHBOARD_EXPANSION_DURATION + 100);
                    });
                }
                
                // Step 3: Show dashboard and remove hidden class
                dashboardMenu.classList.remove('hidden');
                dashboardMenu.classList.add('visible');
                dashboardLogo.setAttribute('aria-expanded', 'true');
                this.updateDashboard(); // Refresh data when opening
                
                // Move focus to close button after fade-in using transitionend
                const handleDashboardTransitionEnd = (e) => {
                    if (e.target === dashboardMenu || e.target.classList.contains('dashboard-content')) {
                        dashboardMenu.removeEventListener('transitionend', handleDashboardTransitionEnd);
                        if (closeDashboard) {
                            closeDashboard.focus();
                        }
                        // Leaflet Best Practice: Invalidate map size after UI changes
                        if (this.map) {
                            this.map.invalidateSize({ animate: false });
                        }
                    }
                };
                dashboardMenu.addEventListener('transitionend', handleDashboardTransitionEnd);
                
                // Fallback timeout
                setTimeout(() => {
                    dashboardMenu.removeEventListener('transitionend', handleDashboardTransitionEnd);
                    if (closeDashboard && document.activeElement !== closeDashboard) {
                        closeDashboard.focus();
                    }
                    if (this.map) {
                        this.map.invalidateSize({ animate: false });
                    }
                }, this.DASHBOARD_FADE_DURATION + 100);
                
                // Add focus trap
                document.addEventListener('keydown', this.dashboardTrapFocus);
            });
            
            // Open dashboard on Enter/Space key
            dashboardLogo.addEventListener('keydown', async (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.dashboardLastFocusedElement = document.activeElement;
                    
                    // Get filter bar element for animation
                    const filterBar = document.getElementById('event-filter-bar');
                    
                    // Step 1: Expand filter bar
                    if (filterBar) {
                        filterBar.classList.add('dashboard-opening');
                        
                        // Step 2: Wait for expansion using transitionend event
                        await new Promise(resolve => {
                            const handleTransitionEnd = (e) => {
                                if (e.target === filterBar) {
                                    filterBar.removeEventListener('transitionend', handleTransitionEnd);
                                    resolve();
                                }
                            };
                            filterBar.addEventListener('transitionend', handleTransitionEnd);
                            
                            // Fallback timeout
                            setTimeout(resolve, this.DASHBOARD_EXPANSION_DURATION + 100);
                        });
                    }
                    
                    // Step 3: Show dashboard
                    dashboardMenu.classList.remove('hidden');
                    dashboardMenu.classList.add('visible');
                    dashboardLogo.setAttribute('aria-expanded', 'true');
                    this.updateDashboard();
                    
                    // Move focus after fade-in using transitionend
                    const handleDashboardTransitionEnd = (e) => {
                        if (e.target === dashboardMenu || e.target.classList.contains('dashboard-content')) {
                            dashboardMenu.removeEventListener('transitionend', handleDashboardTransitionEnd);
                            if (closeDashboard) {
                                closeDashboard.focus();
                            }
                        }
                    };
                    dashboardMenu.addEventListener('transitionend', handleDashboardTransitionEnd);
                    
                    // Fallback timeout
                    setTimeout(() => {
                        dashboardMenu.removeEventListener('transitionend', handleDashboardTransitionEnd);
                        if (closeDashboard && document.activeElement !== closeDashboard) {
                            closeDashboard.focus();
                        }
                        // Leaflet Best Practice: Invalidate map size after UI changes
                        if (this.map) {
                            this.map.invalidateSize({ animate: false });
                        }
                    }, this.DASHBOARD_FADE_DURATION + 100);
                    
                    // Add focus trap
                    document.addEventListener('keydown', this.dashboardTrapFocus);
                }
            });
        }
        
        if (closeDashboard && dashboardMenu) {
            // Close dashboard on close button
            closeDashboard.addEventListener('click', () => {
                dashboardMenu.classList.remove('visible');
                dashboardMenu.classList.add('hidden');
                
                // Step 4: Collapse filter bar
                if (filterBar) {
                    filterBar.classList.remove('dashboard-opening');
                }
                
                if (dashboardLogo) {
                    dashboardLogo.setAttribute('aria-expanded', 'false');
                }
                
                // Remove focus trap
                document.removeEventListener('keydown', this.dashboardTrapFocus);
                
                // Return focus to logo after collapse animation using transitionend
                if (filterBar) {
                    const handleCollapseEnd = (e) => {
                        if (e.target === filterBar) {
                            filterBar.removeEventListener('transitionend', handleCollapseEnd);
                            if (this.dashboardLastFocusedElement) {
                                this.dashboardLastFocusedElement.focus();
                            }
                            // Leaflet Best Practice: Invalidate map size after UI changes
                            if (this.map) {
                                this.map.invalidateSize({ animate: false });
                            }
                        }
                    };
                    filterBar.addEventListener('transitionend', handleCollapseEnd);
                    
                    // Fallback timeout
                    setTimeout(() => {
                        filterBar.removeEventListener('transitionend', handleCollapseEnd);
                        if (this.dashboardLastFocusedElement && document.activeElement !== this.dashboardLastFocusedElement) {
                            this.dashboardLastFocusedElement.focus();
                        }
                        if (this.map) {
                            this.map.invalidateSize({ animate: false });
                        }
                    }, this.DASHBOARD_EXPANSION_DURATION + 100);
                }
            });
        }
        
        if (dashboardMenu) {
            // Close dashboard on background click (backdrop)
            dashboardMenu.addEventListener('click', (e) => {
                // Check if click is on the backdrop (::before pseudo-element area)
                // This works by checking if the click is outside the dashboard-content
                const dashboardContent = dashboardMenu.querySelector('.dashboard-content');
                if (dashboardContent && !dashboardContent.contains(e.target)) {
                    dashboardMenu.classList.remove('visible');
                    dashboardMenu.classList.add('hidden');
                    
                    // Collapse filter bar
                    if (filterBar) {
                        filterBar.classList.remove('dashboard-opening');
                    }
                    
                    if (dashboardLogo) {
                        dashboardLogo.setAttribute('aria-expanded', 'false');
                    }
                    
                    // Remove focus trap
                    document.removeEventListener('keydown', this.dashboardTrapFocus);
                    
                    // Return focus after collapse using transitionend
                    if (filterBar) {
                        const handleCollapseEnd = (e) => {
                            if (e.target === filterBar) {
                                filterBar.removeEventListener('transitionend', handleCollapseEnd);
                                if (this.dashboardLastFocusedElement) {
                                    this.dashboardLastFocusedElement.focus();
                                }
                            }
                        };
                        filterBar.addEventListener('transitionend', handleCollapseEnd);
                        
                        setTimeout(() => {
                            filterBar.removeEventListener('transitionend', handleCollapseEnd);
                            if (this.dashboardLastFocusedElement && document.activeElement !== this.dashboardLastFocusedElement) {
                                this.dashboardLastFocusedElement.focus();
                            }
                            // Leaflet Best Practice: Invalidate map size after UI changes
                            if (this.map) {
                                this.map.invalidateSize({ animate: false });
                            }
                        }, this.DASHBOARD_EXPANSION_DURATION + 100);
                    }
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
                
                // Build category options with dynamic counts under current filter conditions
                const categoryCounts = this.countCategoriesUnderFilters();
                
                // Calculate total count for "All Categories"
                const totalCount = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
                
                // Build dropdown items HTML with current selection at top
                let dropdownHTML = '';
                
                // Current selection at top (highlighted)
                if (this.filters.category === 'all') {
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item current-selection" data-value="all">
                            <span class="item-label">${totalCount} event${totalCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                } else {
                    const currentCount = categoryCounts[this.filters.category] || 0;
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item current-selection" data-value="${this.filters.category}">
                            <span class="item-label">${currentCount} ${this.filters.category} event${currentCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                }
                
                // Other options with predictive counts
                // Add "All events" option if not currently selected
                if (this.filters.category !== 'all') {
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item" data-value="all">
                            <span class="item-label">${totalCount} event${totalCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                }
                
                // Sort categories alphabetically for consistent display
                const sortedCategories = Object.keys(categoryCounts).sort();
                
                sortedCategories.forEach(cat => {
                    // Skip current selection (already shown at top)
                    if (cat === this.filters.category) {
                        return;
                    }
                    
                    const count = categoryCounts[cat];
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item" data-value="${cat}">
                            <span class="item-label">${count} ${cat} event${count !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                });
                
                const dropdown = createDropdown(dropdownHTML, categoryTextEl);
                
                // Add click listeners to all dropdown items
                dropdown.querySelectorAll('.filter-bar-dropdown-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const value = item.getAttribute('data-value');
                        this.filters.category = value;
                        this.saveFiltersToCookie();
                        this.displayEvents();
                        hideAllDropdowns();
                    });
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
                
                // TODO: Internationalize dropdown options
                // Currently using hardcoded English text to match existing pattern
                // Translation keys exist in content.json: time_ranges.sunday-primetime, time_ranges.full-moon
                // Future: Use i18n.t('time_ranges.sunday-primetime') when i18n is fully integrated
                const content = `
                    <select id="time-filter">
                        <option value="sunrise">Next Sunrise (6 AM)</option>
                        <option value="sunday-primetime">Till Sunday's Primetime (20:15)</option>
                        <option value="full-moon">Till Next Full Moon</option>
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
                    this.saveFiltersToCookie();
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
                    <select id="distance-filter">
                        <option value="2">within 30 min walk (2 km)</option>
                        <option value="3.75">within 30 min bicycle ride (3.75 km)</option>
                        <option value="12.5">within 30 min public transport (12.5 km)</option>
                        <option value="60">within 60 min car sharing (60 km)</option>
                    </select>
                `;
                const dropdown = createDropdown(content, distanceTextEl);
                
                const select = dropdown.querySelector('#distance-filter');
                select.value = this.filters.maxDistance;
                select.addEventListener('change', (e) => {
                    this.filters.maxDistance = parseFloat(e.target.value);
                    this.saveFiltersToCookie();
                    this.displayEvents();
                    hideAllDropdowns();
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
                
                // Build location options HTML
                let locationOptionsHtml = '';
                
                // 1. Geolocation option (from here)
                const geolocationChecked = this.filters.locationType === 'geolocation' ? ' checked' : '';
                const geolocationLabel = window.i18n ? window.i18n.t('filters.locations.geolocation') : 'from here';
                locationOptionsHtml += `
                    <label class="location-option">
                        <input type="radio" name="location-type" value="geolocation"${geolocationChecked}>
                        ${geolocationLabel}
                    </label>
                `;
                
                // 2. Predefined locations from config
                const predefinedLocs = this.config?.map?.predefined_locations || [];
                predefinedLocs.forEach((loc, index) => {
                    const checked = (this.filters.locationType === 'predefined' && this.filters.selectedPredefinedLocation === index) ? ' checked' : '';
                    // Try to get translated name, fallback to display_name
                    const translatedName = window.i18n ? window.i18n.t(`filters.predefined_locations.${loc.name}`) : loc.display_name;
                    const prefix = window.i18n ? window.i18n.t('filters.locations.prefix') : 'from';
                    locationOptionsHtml += `
                        <label class="location-option">
                            <input type="radio" name="location-type" value="predefined-${index}"${checked}>
                            ${prefix} ${translatedName}
                        </label>
                    `;
                });
                
                // 3. Custom location option
                const customChecked = this.filters.locationType === 'custom' ? ' checked' : '';
                const latValue = this.filters.customLat || '';
                const lonValue = this.filters.customLon || '';
                const inputsHidden = this.filters.locationType !== 'custom' ? ' hidden' : '';
                
                locationOptionsHtml += `
                    <label class="location-option">
                        <input type="radio" name="location-type" value="custom"${customChecked}>
                        Custom location
                    </label>
                    <div id="custom-location-inputs" class="${inputsHidden}">
                        <input type="number" id="custom-lat" placeholder="Latitude" step="0.0001" value="${latValue}">
                        <input type="number" id="custom-lon" placeholder="Longitude" step="0.0001" value="${lonValue}">
                        <button id="apply-custom-location">Apply</button>
                    </div>
                `;
                
                const content = locationOptionsHtml;
                const dropdown = createDropdown(content, locationTextEl);
                
                // Add event listeners for radio buttons
                const radioButtons = dropdown.querySelectorAll('input[type="radio"]');
                radioButtons.forEach(radio => {
                    radio.addEventListener('change', (e) => {
                        const value = e.target.value;
                        const inputs = dropdown.querySelector('#custom-location-inputs');
                        
                        if (value === 'geolocation') {
                            // Switch to geolocation
                            // Keep custom lat/lon in memory so user can switch back
                            this.filters.locationType = 'geolocation';
                            this.filters.selectedPredefinedLocation = null;
                            this.saveFiltersToCookie();
                            if (inputs) inputs.classList.add('hidden');
                            
                            // Center map on user location if available
                            if (this.userLocation && this.map) {
                                this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                            }
                            
                            this.displayEvents();
                            hideAllDropdowns();
                            
                        } else if (value.startsWith('predefined-')) {
                            // Switch to predefined location
                            // Keep custom lat/lon in memory so user can switch back
                            const index = parseInt(value.split('-')[1]);
                            this.filters.locationType = 'predefined';
                            this.filters.selectedPredefinedLocation = index;
                            this.saveFiltersToCookie();
                            if (inputs) inputs.classList.add('hidden');
                            
                            // Center map on predefined location
                            const selectedLoc = predefinedLocs[index];
                            if (selectedLoc && this.map) {
                                this.map.setView([selectedLoc.lat, selectedLoc.lon], 13);
                            }
                            
                            this.displayEvents();
                            hideAllDropdowns();
                            
                        } else if (value === 'custom') {
                            // Show custom location inputs
                            this.filters.locationType = 'custom';
                            this.filters.selectedPredefinedLocation = null;
                            if (inputs) {
                                inputs.classList.remove('hidden');
                                // Pre-fill inputs with saved custom values if they exist
                                if (this.filters.customLat && this.filters.customLon) {
                                    dropdown.querySelector('#custom-lat').value = this.filters.customLat.toFixed(4);
                                    dropdown.querySelector('#custom-lon').value = this.filters.customLon.toFixed(4);
                                } else if (this.userLocation) {
                                    // Only fall back to current location if no custom values saved
                                    dropdown.querySelector('#custom-lat').value = this.userLocation.lat.toFixed(4);
                                    dropdown.querySelector('#custom-lon').value = this.userLocation.lon.toFixed(4);
                                }
                            }
                        }
                    });
                });
                
                // Apply button for custom location
                const applyBtn = dropdown.querySelector('#apply-custom-location');
                if (applyBtn) {
                    applyBtn.addEventListener('click', () => {
                        const lat = parseFloat(dropdown.querySelector('#custom-lat').value);
                        const lon = parseFloat(dropdown.querySelector('#custom-lon').value);
                        
                        if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                            this.filters.customLat = lat;
                            this.filters.customLon = lon;
                            this.saveFiltersToCookie();
                            
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
                }
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
            const dashboardLogo = document.getElementById('filter-bar-logo');
            
            // ESC: Close event detail popup, dashboard, and dropdowns
            if (e.key === 'Escape') {
                if (eventDetail && !eventDetail.classList.contains('hidden')) {
                    eventDetail.classList.add('hidden');
                    e.preventDefault();
                } else if (dashboardMenu && dashboardMenu.classList.contains('visible')) {
                    dashboardMenu.classList.remove('visible');
                    dashboardMenu.classList.add('hidden');
                    if (dashboardLogo) {
                        dashboardLogo.setAttribute('aria-expanded', 'false');
                    }
                    
                    // Remove focus trap
                    if (this.dashboardTrapFocus) {
                        document.removeEventListener('keydown', this.dashboardTrapFocus);
                    }
                    
                    // Return focus after collapse using transitionend
                    if (filterBar) {
                        const handleCollapse = (event) => {
                            if (event.target === filterBar) {
                                filterBar.removeEventListener('transitionend', handleCollapse);
                                if (this.dashboardLastFocusedElement) {
                                    this.dashboardLastFocusedElement.focus();
                                }
                            }
                        };
                        filterBar.addEventListener('transitionend', handleCollapse);
                        
                        setTimeout(() => {
                            filterBar.removeEventListener('transitionend', handleCollapse);
                            if (this.dashboardLastFocusedElement && document.activeElement !== this.dashboardLastFocusedElement) {
                                this.dashboardLastFocusedElement.focus();
                            }
                        }, this.DASHBOARD_FADE_DURATION + this.DASHBOARD_EXPANSION_DURATION + 100);
                    }
                    
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
        
        // Viewport resize handler for responsive layer scaling
        // Updates CSS custom properties so all layers follow layer 1 (map) behavior
        this.updateViewportDimensions();
        
        // Listen for resize and orientation changes
        window.addEventListener('resize', () => this.updateViewportDimensions());
        window.addEventListener('orientationchange', () => {
            // Delay update to allow orientation to complete
            setTimeout(() => this.updateViewportDimensions(), this.ORIENTATION_CHANGE_DELAY);
        });
    }

}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
