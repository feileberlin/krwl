// KRWL HOF Community Events App
// 
// PERFORMANCE OPTIMIZATIONS:
// - Debounced filter updates to reduce re-renders during slider drag
// - DOM element caching to minimize querySelectorAll calls
// - For-loop instead of forEach for marker operations (reduced overhead)
// - Batched marker removal and bounds calculation
//
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
        this.currentEdgeDetail = null;
        this.currentEventIndex = null; // Track which event is currently displayed
        
        // BOOKMARKS: Array of bookmarked event IDs (max 15)
        this.bookmarks = this.loadBookmarks();
        this.MAX_BOOKMARKS = 15;
        
        // Speech bubbles: Array of active speech bubble elements
        this.speechBubbles = [];
        
        // Load saved filter settings from cookie or use defaults
        this.filters = this.loadFiltersFromCookie() || {
            maxDistance: 2, // Default to 30 min walk (2 km)
            timeFilter: 'sunrise',
            category: 'all',
            locationType: 'geolocation', // 'geolocation', 'predefined', or 'custom'
            selectedPredefinedLocation: null, // Index or name of predefined location
            useCustomLocation: false,
            customLat: null,
            customLon: null
        };
        
        // OPTIMIZATION: Cache frequently accessed DOM elements
        this.domCache = {};
        
        // OPTIMIZATION: Debounce timer for filter updates
        this.filterDebounceTimer = null;
        
        // OPTIMIZATION: Debounce delay constant for slider interactions (milliseconds)
        this.SLIDER_DEBOUNCE_DELAY = 100;
        
        // VIEWPORT: Delay for orientation change to complete before updating dimensions (milliseconds)
        this.ORIENTATION_CHANGE_DELAY = 100;
        
        // ANIMATION: Dashboard expansion animation duration (milliseconds)
        // Must match CSS transition duration in filters.css
        this.DASHBOARD_EXPANSION_DURATION = 500;
        
        // ANIMATION: Dashboard fade-in duration (milliseconds)
        // Must match CSS transition duration in dashboard.css
        this.DASHBOARD_FADE_DURATION = 300;
        
        this.init();
    }
    
    // Debug logging helper
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[KRWL Debug]', message, ...args);
        }
    }
    
    /**
     * OPTIMIZATION: Debounced version of displayEvents
     * Prevents excessive re-renders when filters change rapidly (e.g., slider drag)
     * 
     * @param {number} delay - Milliseconds to wait before executing (default: SLIDER_DEBOUNCE_DELAY)
     */
    displayEventsDebounced(delay = this.SLIDER_DEBOUNCE_DELAY) {
        if (this.filterDebounceTimer) {
            clearTimeout(this.filterDebounceTimer);
        }
        
        this.filterDebounceTimer = setTimeout(() => {
            this.displayEvents();
            this.filterDebounceTimer = null;
        }, delay);
    }
    
    /**
     * OPTIMIZATION: Get cached DOM element or query and cache it
     * Reduces repeated querySelectorAll/querySelector calls
     * 
     * @param {string} selector - CSS selector
     * @param {boolean} multiple - If true, use querySelectorAll (default: false)
     * @returns {Element|NodeList|null} Cached or newly queried element(s)
     */
    getCachedElement(selector, multiple = false) {
        const cacheKey = `${multiple ? 'all:' : ''}${selector}`;
        
        if (!this.domCache[cacheKey]) {
            this.domCache[cacheKey] = multiple 
                ? document.querySelectorAll(selector)
                : document.querySelector(selector);
        }
        
        return this.domCache[cacheKey];
    }
    
    /**
     * Clear DOM cache (call when DOM structure changes significantly)
     */
    clearDOMCache() {
        this.domCache = {};
    }
    
    /**
     * Feature detection for browser capabilities
     * @returns {Object} Object with feature availability flags
     */
    detectBrowserFeatures() {
        const features = {
            localStorage: false,
            backdropFilter: false
        };
        
        // Test localStorage
        try {
            const testKey = '__krwl_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            features.localStorage = true;
        } catch (e) {
            features.localStorage = false;
        }
        
        // Test backdrop-filter support
        const testElement = document.createElement('div');
        const backdropFilterSupport = 
            testElement.style.backdropFilter !== undefined ||
            testElement.style.webkitBackdropFilter !== undefined;
        features.backdropFilter = backdropFilterSupport;
        
        return features;
    }
    
    /**
     * Check if bookmarking features should be enabled
     * Requires localStorage and backdrop-filter support
     * @returns {boolean} True if bookmarking is supported
     */
    isBookmarkingSupported() {
        if (this.browserFeatures === undefined) {
            this.browserFeatures = this.detectBrowserFeatures();
        }
        return this.browserFeatures.localStorage && this.browserFeatures.backdropFilter;
    }
    
    /**
     * COOKIE/LOCALSTORAGE UTILITIES
     * Save and load filter settings and bookmarks
     */
    
    /**
     * Save current filter settings to cookie
     */
    saveFiltersToCookie() {
        try {
            const filterData = JSON.stringify(this.filters);
            // Save to localStorage (more reliable than cookies for complex data)
            localStorage.setItem('krwl_filters', filterData);
            this.log('Filters saved to localStorage');
        } catch (error) {
            console.warn('Failed to save filters:', error);
        }
    }
    
    /**
     * Load filter settings from cookie
     * @returns {Object|null} Saved filter settings or null
     */
    loadFiltersFromCookie() {
        try {
            const filterData = localStorage.getItem('krwl_filters');
            if (filterData) {
                const filters = JSON.parse(filterData);
                this.log('Filters loaded from localStorage', filters);
                return filters;
            }
        } catch (error) {
            console.warn('Failed to load filters:', error);
        }
        return null;
    }
    
    /**
     * Load bookmarks from localStorage
     * @returns {Array} Array of bookmarked event IDs
     */
    loadBookmarks() {
        try {
            const bookmarksData = localStorage.getItem('krwl_bookmarks');
            if (bookmarksData) {
                const bookmarks = JSON.parse(bookmarksData);
                this.log('Bookmarks loaded from localStorage', bookmarks);
                return Array.isArray(bookmarks) ? bookmarks : [];
            }
        } catch (error) {
            console.warn('Failed to load bookmarks:', error);
        }
        return [];
    }
    
    /**
     * Save bookmarks to localStorage
     */
    saveBookmarks() {
        try {
            const bookmarksData = JSON.stringify(this.bookmarks);
            localStorage.setItem('krwl_bookmarks', bookmarksData);
            this.log('Bookmarks saved to localStorage', this.bookmarks);
        } catch (error) {
            console.warn('Failed to save bookmarks:', error);
        }
    }
    
    /**
     * Toggle bookmark for an event
     * @param {string} eventId - Event ID to bookmark/unbookmark
     * @returns {boolean} True if bookmarked, false if unbookmarked
     */
    toggleBookmark(eventId) {
        const index = this.bookmarks.indexOf(eventId);
        
        if (index !== -1) {
            // Remove bookmark
            this.bookmarks.splice(index, 1);
            this.saveBookmarks();
            this.log('Bookmark removed:', eventId);
            return false;
        } else {
            // Add bookmark (enforce 15-item limit)
            if (this.bookmarks.length >= this.MAX_BOOKMARKS) {
                // Remove oldest bookmark (first in array)
                const removed = this.bookmarks.shift();
                this.log('Max bookmarks reached, removed oldest:', removed);
            }
            this.bookmarks.push(eventId);
            this.saveBookmarks();
            this.log('Bookmark added:', eventId);
            return true;
        }
    }
    
    /**
     * Check if an event is bookmarked
     * @param {string} eventId - Event ID to check
     * @returns {boolean} True if bookmarked
     */
    isBookmarked(eventId) {
        return this.bookmarks.includes(eventId);
    }
    
    async init() {
        // Load configuration from embedded window.APP_CONFIG (set by backend during site generation)
        // Note: config.json is backend-only and NOT fetched by frontend
        this.config = window.APP_CONFIG || this.getDefaultConfig();
        
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
        
        // Check for pending events and update notifications
        await this.checkPendingEvents();
        
        // Start periodic polling for pending events
        this.startPendingEventsPolling();
        
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
            const cacheSize = Object.keys(this.domCache).length;
            const cacheStatus = cacheSize > 0 ? `${cacheSize} elements cached` : 'No elements cached';
            debugDOMCache.textContent = cacheStatus;
            debugDOMCache.title = `DOM elements cached: ${Object.keys(this.domCache).join(', ') || 'none'}`;
        }
        
        const debugHistoricalCache = document.getElementById('debug-historical-cache');
        if (debugHistoricalCache) {
            // Note: Frontend doesn't have access to backend Python cache
            // This shows if we implement a frontend cache in the future
            debugHistoricalCache.textContent = 'Backend (Python)';
            debugHistoricalCache.title = 'Historical events are cached in the backend during scraping to improve performance';
        }
        
        // Show debug section after data is loaded
        if (debugSection && debugSection.style.display === 'none') {
            debugSection.style.display = 'block';
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

    
    getDefaultConfig() {
        // Fallback config if window.APP_CONFIG is not available
        // This should never happen in production (set by site_generator.py)
        console.warn('window.APP_CONFIG not found, using fallback defaults');
        return {
            debug: false,
            app: {
                environment: 'unknown'
            },
            map: {
                default_center: { lat: 50.3167, lon: 11.9167 },
                default_zoom: 13,
                tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            },
            data: {
                source: 'real',
                sources: {}
            }
        };
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
        
        // Leaflet Best Practice: Disable map interactions on UI overlays
        // This prevents clicks on filter bar and dashboard from affecting the map
        this.setupLeafletEventPrevention();
    }
    
    /**
     * Setup Leaflet-specific event prevention on UI overlays
     * 
     * Follows Leaflet best practices for preventing map interactions
     * when clicking/scrolling on UI elements that overlay the map.
     * 
     * See: https://leafletjs.com/reference.html#domevent
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
            this.log('Leaflet event prevention enabled for filter bar');
        }
        
        // Prevent map interactions on dashboard
        const dashboard = document.getElementById('dashboard-menu');
        if (dashboard) {
            L.DomEvent.disableClickPropagation(dashboard);
            L.DomEvent.disableScrollPropagation(dashboard);
            this.log('Leaflet event prevention enabled for dashboard');
        }
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
                
                // Store globally for pending count access (backward compatible)
                window.__EVENTS_DATA__ = data;
                
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
            let eventsData = null;
            
            if (dataSource === 'both' && dataSources.both?.urls) {
                // Load from multiple sources and combine
                this.log('Loading from multiple sources:', dataSources.both.urls);
                for (const url of dataSources.both.urls) {
                    try {
                        const response = await fetch(url);
                        const data = await response.json();
                        const events = data.events || [];
                        allEvents = allEvents.concat(events);
                        // Store the first data object for pending_count
                        if (!eventsData && data.pending_count !== undefined) {
                            eventsData = data;
                        }
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
                eventsData = await response.json();
                allEvents = eventsData.events || [];
                this.log(`Loaded ${allEvents.length} events from ${url}`);
            }
            
            // Store globally for pending count access
            if (eventsData) {
                window.__EVENTS_DATA__ = eventsData;
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
                
            case 'sunday-primetime':
                // Next Sunday at 20:15 (prime time)
                return this.getNextSundayPrimetime();
                
            case 'full-moon':
                // Until 6am of the day following the next full moon after next Sunday
                return this.getNextFullMoonMorning();
                
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
    
    getNextSundayPrimetime() {
        // Calculate next Sunday at 20:15 (prime time)
        const now = new Date();
        const result = new Date(now);
        
        // Get current day of week (0 = Sunday, 1 = Monday, etc.)
        const currentDay = now.getDay();
        
        // Calculate days until next Sunday
        let daysUntilSunday;
        if (currentDay === 0) {
            // It's Sunday - check if we're past 20:15
            const currentTime = now.getHours() * 60 + now.getMinutes();
            const primetimeMinutes = 20 * 60 + 15;
            
            if (currentTime >= primetimeMinutes) {
                // Past 20:15 on Sunday, go to next Sunday
                daysUntilSunday = 7;
            } else {
                // Before 20:15 on Sunday, use today
                daysUntilSunday = 0;
            }
        } else {
            // Calculate days to next Sunday (1-6 days ahead)
            daysUntilSunday = 7 - currentDay;
        }
        
        result.setDate(result.getDate() + daysUntilSunday);
        result.setHours(20, 15, 0, 0);
        
        return result;
    }
    
    getNextFullMoonMorning() {
        // Calculate the morning (6am) after the next full moon following next Sunday
        // Create a new Date to avoid modifying the return value of getNextSundayPrimetime()
        const nextSunday = new Date(this.getNextSundayPrimetime().getTime());
        // Set to start of Sunday for comparison
        nextSunday.setHours(0, 0, 0, 0);
        
        // Known full moon reference: January 6, 2000, 18:14 UTC
        // Source: US Naval Observatory astronomical data
        // Accuracy: ±12 hours (sufficient for event filtering, not astronomical precision)
        const knownFullMoon = new Date(Date.UTC(2000, 0, 6, 18, 14, 0));
        
        // Lunar cycle length in milliseconds (29.53058770576 days)
        const lunarCycle = 29.53058770576 * 24 * 60 * 60 * 1000;
        
        // Calculate number of cycles since the known full moon
        const now = new Date();
        const timeSinceKnownFullMoon = now.getTime() - knownFullMoon.getTime();
        const cyclesSinceKnown = Math.floor(timeSinceKnownFullMoon / lunarCycle);
        
        // Calculate approximate next full moons
        let fullMoon = new Date(knownFullMoon.getTime() + cyclesSinceKnown * lunarCycle);
        
        // Find the first full moon after next Sunday
        while (fullMoon <= nextSunday) {
            fullMoon = new Date(fullMoon.getTime() + lunarCycle);
        }
        
        // Set to 6am of the day after the full moon
        const dayAfterFullMoon = new Date(fullMoon);
        dayAfterFullMoon.setDate(dayAfterFullMoon.getDate() + 1);
        dayAfterFullMoon.setHours(6, 0, 0, 0);
        
        return dayAfterFullMoon;
    }
    
    filterEvents() {
        const maxEventTime = this.getMaxEventTime();
        const maxDistance = this.filters.maxDistance;
        const category = this.filters.category;
        
        // Determine which location to use for distance calculation
        let referenceLocation = this.userLocation;
        
        if (this.filters.locationType === 'predefined' && this.filters.selectedPredefinedLocation !== null) {
            // Use predefined location from config
            const predefinedLocs = this.config?.map?.predefined_locations || [];
            const selectedLoc = predefinedLocs[this.filters.selectedPredefinedLocation];
            if (selectedLoc) {
                referenceLocation = {
                    lat: selectedLoc.lat,
                    lon: selectedLoc.lon
                };
            }
        } else if (this.filters.locationType === 'custom' && this.filters.customLat && this.filters.customLon) {
            // Use custom location
            referenceLocation = {
                lat: this.filters.customLat,
                lon: this.filters.customLon
            };
        }
        // Otherwise use geolocation (this.userLocation)
        
        const filtered = this.events.filter(event => {
            // BOOKMARKS: Always include bookmarked events regardless of filters
            if (this.isBookmarked(event.id)) {
                // Calculate distance even for bookmarked events
                if (referenceLocation && event.location) {
                    const distance = this.calculateDistance(
                        referenceLocation.lat,
                        referenceLocation.lon,
                        event.location.lat,
                        event.location.lon
                    );
                    event.distance = distance;
                }
                return true;
            }
            
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
        
        // OPTIMIZATION: Create bounds more efficiently using a single pass
        const bounds = L.latLngBounds();
        
        // Batch extend bounds (single loop, avoid forEach overhead)
        const markerCount = this.markers.length;
        for (let i = 0; i < markerCount; i++) {
            bounds.extend(this.markers[i].getLatLng());
        }
        
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
        
        // OPTIMIZATION: Clear existing markers efficiently
        // Remove all at once instead of iterating
        if (this.markers.length > 0) {
            for (let i = 0; i < this.markers.length; i++) {
                this.markers[i].remove();
            }
            this.markers = [];
        }
        
        // Clear existing speech bubbles
        this.clearSpeechBubbles();
        
        if (filteredEvents.length === 0) {
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
        
        // Show speech bubbles for all visible events after a short delay
        // (allows map to settle and markers to be positioned)
        setTimeout(() => {
            this.showAllSpeechBubbles(filteredEvents);
        }, 500);
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
            timeText.textContent = timeDescription;
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
            distanceText.textContent = distanceDescription;
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
        
        // Add custom class name based on bookmark state
        const isBookmarked = this.isBookmarked(event.id);
        const bookmarkClass = isBookmarked ? 'marker-bookmarked' : 'marker-unbookmarked';
        
        // Create custom SVG icon using Leaflet's L.icon
        const customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: iconSize,
            iconAnchor: iconAnchor,
            popupAnchor: popupAnchor,
            className: bookmarkClass
        });
        
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: customIcon
        }).addTo(this.map);
        
        // Store event data on marker for speech bubble access
        marker.eventData = event;
        
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
    }
    
    /**
     * Update marker appearance based on bookmark state
     * @param {string} eventId - Event ID
     * @param {boolean} isBookmarked - Whether event is bookmarked
     */
    updateMarkerBookmarkState(eventId, isBookmarked) {
        // Find marker for this event
        const marker = this.markers.find(m => 
            m.eventData && m.eventData.id === eventId
        );
        
        if (!marker) return;
        
        // Get the marker icon element
        const markerElement = marker.getElement();
        if (!markerElement) return;
        
        // Update CSS classes
        if (isBookmarked) {
            markerElement.classList.remove('marker-unbookmarked');
            markerElement.classList.add('marker-bookmarked');
        } else {
            markerElement.classList.remove('marker-bookmarked');
            markerElement.classList.add('marker-unbookmarked');
        }
    }
    
    /**
     * SPEECH BUBBLES: Show event details automatically on load
     */
    
    /**
     * Clear all speech bubbles from the map
     */
    clearSpeechBubbles() {
        this.speechBubbles.forEach(bubble => {
            if (bubble.parentNode) {
                bubble.parentNode.removeChild(bubble);
            }
        });
        this.speechBubbles = [];
    }
    
    /**
     * Show speech bubbles for all visible events
     * @param {Array} events - Filtered events to display
     */
    showAllSpeechBubbles(events) {
        // Limit number of bubbles to avoid clutter (show top 20 by distance)
        const maxBubbles = 20;
        const eventsToShow = events.slice(0, maxBubbles);
        
        // Group events by their coordinates to detect co-location
        const locationGroups = new Map();
        
        eventsToShow.forEach((event, index) => {
            // Find the marker for this event
            const marker = this.markers.find(m => 
                m.eventData && (
                    (m.eventData.id && m.eventData.id === event.id) || 
                    (m.eventData.title === event.title && m.eventData.start_time === event.start_time)
                )
            );
            
            if (marker) {
                // Create location key with 4 decimal places (about 11m precision)
                const latLng = marker.getLatLng();
                const locationKey = `${latLng.lat.toFixed(4)},${latLng.lng.toFixed(4)}`;
                
                if (!locationGroups.has(locationKey)) {
                    locationGroups.set(locationKey, []);
                }
                
                locationGroups.get(locationKey).push({
                    event,
                    marker,
                    originalIndex: index
                });
            }
        });
        
        // Now create speech bubbles with intelligent positioning
        // For each location group, detect and remove duplicates
        let bubbleIndex = 0;
        locationGroups.forEach((group, locationKey) => {
            // Detect duplicates within this location group
            const uniqueEvents = this.deduplicateEvents(group);
            
            uniqueEvents.forEach((item, groupIndex) => {
                // Delay each bubble slightly for a nice cascading effect
                setTimeout(() => {
                    // Pass both the group size and position within group for intelligent spacing
                    // Also pass duplicate count if > 1
                    this.createSpeechBubble(
                        item.event, 
                        item.marker, 
                        bubbleIndex,
                        uniqueEvents.length,
                        groupIndex,
                        item.duplicateCount
                    );
                }, bubbleIndex * 50);
                bubbleIndex++;
            });
        });
    }
    
    /**
     * Deduplicate events based on title and start time
     * Returns array of unique events with duplicate count
     * @param {Array} eventItems - Array of {event, marker, originalIndex}
     * @returns {Array} Array of unique items with duplicateCount property
     */
    deduplicateEvents(eventItems) {
        const uniqueMap = new Map();
        
        eventItems.forEach(item => {
            // Create a key based on title and start time (case-insensitive)
            const title = item.event.title.toLowerCase().trim();
            const startTime = item.event.start_time;
            const key = `${title}|${startTime}`;
            
            if (uniqueMap.has(key)) {
                // Increment duplicate count
                const existing = uniqueMap.get(key);
                existing.duplicateCount++;
                // Keep the array of all duplicate events for potential future use
                existing.duplicates.push(item.event);
            } else {
                // First occurrence - add to map
                uniqueMap.set(key, {
                    ...item,
                    duplicateCount: 1,
                    duplicates: [item.event]
                });
            }
        });
        
        return Array.from(uniqueMap.values());
    }
    
    /**
     * Create and position a speech bubble for an event
     * @param {Object} event - Event data
     * @param {Object} marker - Leaflet marker
     * @param {number} index - Display order index (global across all bubbles)
     * @param {number} groupSize - Number of events at this location (default: 1)
     * @param {number} groupIndex - Index within the co-located group (default: 0)
     * @param {number} duplicateCount - Number of duplicate events (default: 1)
     */
    createSpeechBubble(event, marker, index, groupSize = 1, groupIndex = 0, duplicateCount = 1) {
        // Get marker position in screen coordinates
        const markerPos = this.map.latLngToContainerPoint(marker.getLatLng());
        
        // Create bubble element
        const bubble = document.createElement('div');
        bubble.className = 'speech-bubble';
        bubble.setAttribute('data-event-id', event.id);
        
        // Format start time nicely
        const startTime = new Date(event.start_time);
        const timeStr = startTime.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        const dateStr = startTime.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
        
        // Create bookmark button only if bookmarking is supported
        const isBookmarked = this.isBookmarked(event.id);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        const bookmarkingSupported = this.isBookmarkingSupported();
        
        // Build bubble HTML with start time as headline
        // Add duplicate count badge if there are duplicates
        const duplicateBadge = duplicateCount > 1 ? 
            `<div class="bubble-duplicate-badge" title="${duplicateCount} duplicate events">×${duplicateCount}</div>` : '';
        
        bubble.innerHTML = `
            ${duplicateBadge}
            <div class="bubble-time-headline">${timeStr}</div>
            <div class="bubble-date">${dateStr}</div>
            <div class="bubble-title">${this.truncateText(event.title, 50)}</div>
            <div class="bubble-location">📍 ${this.truncateText(event.location.name, 30)}</div>
            ${event.distance !== undefined ? `<div class="bubble-distance">🚶 ${event.distance.toFixed(1)} km</div>` : ''}
            ${bookmarkingSupported ? `<button class="bubble-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                <i data-lucide="heart" aria-hidden="true"></i>
            </button>` : ''}
        `;
        
        // Initialize Lucide icons in the bubble
        if (bookmarkingSupported && typeof lucide !== 'undefined') {
            // Need to call createIcons after adding to DOM
            setTimeout(() => {
                lucide.createIcons();
            }, 10);
        }
        
        // Position bubble intelligently around marker
        const position = this.calculateBubblePosition(markerPos, index, groupSize, groupIndex);
        bubble.style.left = position.x + 'px';
        bubble.style.top = position.y + 'px';
        
        // Add click handler to show full details
        bubble.addEventListener('click', (e) => {
            // Don't trigger if clicking bookmark button
            if (!e.target.classList.contains('bubble-bookmark') && !e.target.closest('.bubble-bookmark')) {
                this.showEventDetail(event);
            }
        });
        
        // Add bookmark button handler only if bookmarking is supported
        if (bookmarkingSupported) {
            const bookmarkBtn = bubble.querySelector('.bubble-bookmark');
            if (bookmarkBtn) {
                bookmarkBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const nowBookmarked = this.toggleBookmark(event.id);
                    
                    // Update button appearance (CSS handles color via .bookmarked class)
                    bookmarkBtn.classList.toggle('bookmarked', nowBookmarked);
                    
                    // Update marker appearance
                    this.updateMarkerBookmarkState(event.id, nowBookmarked);
                    
                    // Show feedback
                    this.showBookmarkFeedback(nowBookmarked);
                });
            }
        }
        
        // Add to map container
        document.getElementById('map').appendChild(bubble);
        this.speechBubbles.push(bubble);
        
        // Fade in animation
        setTimeout(() => {
            bubble.classList.add('visible');
        }, 10);
    }
    
    /**
     * Calculate intelligent position for speech bubble around marker
     * @param {Object} markerPos - {x, y} marker screen position
     * @param {number} index - Bubble index for variation (global)
     * @param {number} groupSize - Number of events at this location (default: 1)
     * @param {number} groupIndex - Index within the co-located group (default: 0)
     * @returns {Object} {x, y} position for bubble
     */
    calculateBubblePosition(markerPos, index, groupSize = 1, groupIndex = 0) {
        const bubbleWidth = 220;
        const bubbleHeight = 140;
        
        // Base offset distance from marker
        let baseOffset = 60;
        
        // For co-located events (multiple events at same location),
        // use wider spacing to distribute them more effectively
        if (groupSize > 1) {
            // Increase spacing based on how many events share this location
            // More events = wider spread to avoid overlap
            baseOffset = 80 + (Math.min(groupSize - 1, 5) * 20);
            
            // Use a circular distribution pattern for co-located events
            const angle = (groupIndex / groupSize) * 2 * Math.PI;
            
            // Add variation based on group size to create layered circles
            const radiusMultiplier = 1 + Math.floor(groupIndex / 8) * 0.5;
            const radius = baseOffset * radiusMultiplier;
            
            // Calculate position on circle
            const relPos = {
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius
            };
            
            let x = markerPos.x + relPos.x;
            let y = markerPos.y + relPos.y;
            
            // Keep bubble within viewport bounds
            const mapContainer = document.getElementById('map');
            const viewportWidth = mapContainer.clientWidth;
            const viewportHeight = mapContainer.clientHeight;
            
            // Adjust if too far right
            if (x + bubbleWidth > viewportWidth - 10) {
                x = viewportWidth - bubbleWidth - 10;
            }
            
            // Adjust if too far left
            if (x < 10) {
                x = 10;
            }
            
            // Adjust if too far down
            if (y + bubbleHeight > viewportHeight - 10) {
                y = viewportHeight - bubbleHeight - 10;
            }
            
            // Adjust if too far up
            if (y < 10) {
                y = 10;
            }
            
            return { x, y };
        }
        
        // For single events (not co-located), use the original spiral pattern
        const offset = baseOffset;
        
        // Use a spiral pattern to position bubbles
        // Vary position based on index to create natural spread
        const positions = [
            { x: offset, y: -offset },      // Top right
            { x: -offset, y: -offset },     // Top left
            { x: offset, y: offset },       // Bottom right
            { x: -offset, y: offset },      // Bottom left
            { x: offset * 1.5, y: 0 },      // Right
            { x: -offset * 1.5, y: 0 },     // Left
            { x: 0, y: -offset * 1.5 },     // Top
            { x: 0, y: offset * 1.5 }       // Bottom
        ];
        
        const posIndex = index % positions.length;
        const relPos = positions[posIndex];
        
        let x = markerPos.x + relPos.x;
        let y = markerPos.y + relPos.y;
        
        // Keep bubble within viewport bounds
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        
        // Adjust if too far right
        if (x + bubbleWidth > viewportWidth - 10) {
            x = viewportWidth - bubbleWidth - 10;
        }
        
        // Adjust if too far left
        if (x < 10) {
            x = 10;
        }
        
        // Adjust if too far down
        if (y + bubbleHeight > viewportHeight - 10) {
            y = viewportHeight - bubbleHeight - 10;
        }
        
        // Adjust if too far up
        if (y < 10) {
            y = 10;
        }
        
        return { x, y };
    }
    
    /**
     * Truncate text to max length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
    
    /**
     * Show visual feedback when bookmarking
     * @param {boolean} bookmarked - True if bookmarked, false if unbookmarked
     */
    showBookmarkFeedback(bookmarked) {
        const message = bookmarked ? '❤️ Event bookmarked!' : '🤍 Bookmark removed';
        
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.className = 'bookmark-feedback';
        feedback.textContent = message;
        document.body.appendChild(feedback);
        
        // Remove after animation
        setTimeout(() => {
            feedback.classList.add('fade-out');
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.parentNode.removeChild(feedback);
                }
            }, 300);
        }, 2000);
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
                    this.saveFiltersToCookie();
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
                            this.filters.locationType = 'geolocation';
                            this.filters.selectedPredefinedLocation = null;
                            this.filters.customLat = null;
                            this.filters.customLon = null;
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
                            const index = parseInt(value.split('-')[1]);
                            this.filters.locationType = 'predefined';
                            this.filters.selectedPredefinedLocation = index;
                            this.filters.customLat = null;
                            this.filters.customLon = null;
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
                                // Pre-fill with current location if available and no custom values set
                                if (this.userLocation && !this.filters.customLat && !this.filters.customLon) {
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
    
    /**
     * Update viewport dimensions in CSS custom properties
     * This ensures all fixed-position layers scale consistently with layer 1 (map)
     * 
     * PROGRESSIVE ENHANCEMENT:
     * - Without this function: Falls back to dvh/dvw (modern) or vh/vw (legacy)
     * - With this function: Uses exact pixel dimensions for perfect accuracy
     * 
     * Handles:
     * - Window resize
     * - Mobile browser address bar show/hide
     * - Orientation changes
     * - Keyboard appearance on mobile
     */
    updateViewportDimensions() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Update CSS custom properties
        document.documentElement.style.setProperty('--app-width', `${width}px`);
        document.documentElement.style.setProperty('--app-height', `${height}px`);
        
        this.log(`Viewport updated: ${width}x${height}`);
        
        // Invalidate map size if it exists (Leaflet needs to recalculate)
        if (this.map) {
            this.map.invalidateSize();
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
