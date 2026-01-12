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
