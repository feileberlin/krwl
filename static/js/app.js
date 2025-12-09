/**
 * KRWL HOF Community Events Application
 * 
 * A fullscreen, mobile-first interactive map application for discovering community events.
 * Uses vanilla JavaScript with Leaflet.js for mapping.
 * 
 * Key Features:
 * - Fullscreen map with no separate event list
 * - Pure Leaflet.js conventions (standard markers, tooltips, popups)
 * - Natural language filter sentence overlay
 * - Full keyboard navigation and accessibility
 * - PWA support with offline capability
 * - All configuration from JSON files
 * 
 * @author KRWL HOF Community
 * @version 1.0.0
 */

class EventsApp {
    /**
     * Initialize the EventsApp
     * Sets up default configuration and starts the application
     */
    constructor() {
        // Leaflet map instance
        this.map = null;
        
        // User's current geolocation {lat, lon}
        this.userLocation = null;
        
        // Array of all event objects loaded from events.json
        this.events = [];
        
        // Array of Leaflet marker objects currently displayed on map
        this.markers = [];
        
        // Special marker for imprint/project location
        this.imprintMarker = null;
        
        // Configuration object loaded from config.json
        this.config = null;
        
        // Debug mode flag (enables console logging)
        this.debug = false;
        
        // Current filter settings
        this.filters = {
            maxDistance: 1.25,        // Distance in km (15 min walk)
            timeFilter: 'sunrise',     // Time range filter
            category: 'all',           // Event category filter
            useCustomLocation: false,  // Use predefined location instead of geolocation
            customLat: null,           // Custom location latitude
            customLon: null            // Custom location longitude
        };
        
        // Current marker index for keyboard navigation
        this.currentMarkerIndex = -1;
        
        // Start the application
        this.init();
    }
    
    /**
     * Debug logging function
     * Only logs when debug mode is enabled
     * @param {...any} args - Arguments to log
     */
    log(...args) {
        if (this.debug) {
            console.log('[KRWL Debug]', ...args);
        }
    }
    
    /**
     * Initialize the application
     * Loads config, sets up UI, initializes map, gets location, loads events
     * @async
     */
    async init() {
        // Load configuration from config.json
        await this.loadConfig();
        
        // Initialize i18n system with config
        if (window.i18n) {
            await window.i18n.init(this.config);
            this.log('i18n initialized with locale:', window.i18n.getLocale());
        }
        
        // Initialize UI elements from config (logo, title, etc.)
        this.initUI();
        
        // Initialize Leaflet map with configured tile provider
        this.initMap();
        
        // Get user's geolocation or use default location
        this.getUserLocation();
        
        // Load event data from events.json
        await this.loadEvents();
        
        // Initialize UI translations for filters
        this.updateUITranslations();
        
        // Setup all event listeners (filters, keyboard nav, etc.)
        this.setupEventListeners();
    }
    
    /**
     * Initialize UI elements from configuration
     * Sets page title, logo, imprint link based on config.json
     */
    initUI() {
        // Set page title from config (append [DEBUG MODE] if debug enabled)
        if (this.config.app && this.config.app.name) {
            document.title = this.config.app.name + (this.debug ? ' [DEBUG MODE]' : '');
        }
        
        // Set logo and imprint link from config
        const ui = this.config.ui || {};
        const imprintLink = document.getElementById('imprint-link');
        const siteLogo = document.getElementById('site-logo');
        const imprintText = document.getElementById('imprint-text');
        
        // Update imprint URL if configured
        if (imprintLink && ui.imprint_url) {
            imprintLink.href = ui.imprint_url;
        }
        
        // Update imprint text if configured
        if (imprintText && ui.imprint_text) {
            imprintText.textContent = ui.imprint_text;
        }
        
        // Load logo if configured
        if (siteLogo && ui.logo) {
            siteLogo.src = ui.logo;
            siteLogo.style.display = 'block';
            if (imprintText) {
                imprintText.style.display = 'none';
            }
            // Handle logo load error - fallback to text
            siteLogo.onerror = () => {
                siteLogo.style.display = 'none';
                if (imprintText) {
                    imprintText.style.display = 'inline';
                }
            };
        }
    }
    
    /**
     * Load application configuration from config.json
     * Config contains functional settings only, not translated content
     * @async
     */
    async loadConfig() {
        try {
            // Fetch configuration file (language-independent)
            const response = await fetch('config.json');
            this.config = await response.json();
            
            // Enable debug mode if configured
            this.debug = this.config.debug || false;
            this.log('Config loaded:', this.config);
            
            // Fetch next full moon date for "till next full moon" filter
            await this.fetchNextFullMoon();
        } catch (error) {
            // If config fails to load, use safe defaults
            console.error('Error loading config:', error);
            this.config = {
                debug: false,
                app: {
                    name: 'KRWL HOF Community Events',
                    language: 'auto'
                },
                ui: {
                    logo: '',
                    imprint_url: '#'
                },
                imprint: {
                    enabled: true,
                    location: {
                        lat: 50.3167,
                        lon: 11.9167,
                        marker: 'marker-city-center.svg'
                    },
                    contact: {},
                    responsible: {},
                    technical: {}
                },
                map: {
                    default_center: { lat: 50.3167, lon: 11.9167 },
                    default_zoom: 13,
                    tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'
                },
                filtering: {
                    max_distance_km: 5.0,
                    show_until: "next_sunrise"
                }
            };
        }
    }
    
    /**
     * Fetch next full moon date from astronomy API
     * Uses wttr.in free API to get moon phase and illumination
     * Calculates next full moon date based on current moon phase
     * @async
     */
    async fetchNextFullMoon() {
        try {
            // Get coordinates from config for accurate moon phase
            const lat = this.config.map?.default_center?.lat || 50.3167;
            const lon = this.config.map?.default_center?.lon || 11.9167;
            
            // Using wttr.in weather API (includes astronomy data)
            // format=j1 returns JSON with detailed astronomy information
            const url = `https://wttr.in/${lat},${lon}?format=j1`;
            
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                
                // Extract moon phase and illumination from astronomy data
                if (data.weather && data.weather[0]?.astronomy) {
                    const astronomy = data.weather[0].astronomy[0];
                    const moonPhase = astronomy.moon_phase || '';           // e.g., "Waxing Gibbous"
                    const moonIllumination = parseInt(astronomy.moon_illumination) || 50;  // 0-100%
                    
                    // Calculate next full moon based on current phase
                    this.nextFullMoonDate = this.calculateNextFullMoonFromData(moonPhase, moonIllumination);
                    this.log('Next full moon date:', this.nextFullMoonDate, 'Moon phase:', moonPhase, 'Illumination:', moonIllumination + '%');
                }
            } else {
                // API unavailable, will use approximation in filter
                this.log('Weather API unavailable, using approximation');
                this.nextFullMoonDate = null;
            }
        } catch (error) {
            this.log('Error fetching moon data:', error);
            this.nextFullMoonDate = null;
        }
    }
    
    calculateNextFullMoonFromData(phase, illumination) {
        // Lunar cycle is ~29.53 days
        const lunarCycle = 29.53;
        const now = new Date();
        let daysToFullMoon;
        
        // Determine days to full moon based on phase and illumination
        if (phase.includes('Full Moon') || illumination >= 95) {
            // Already at or very close to full moon
            daysToFullMoon = lunarCycle; // Next one is a full cycle away
        } else if (phase.includes('Waxing')) {
            // Moon is growing towards full
            daysToFullMoon = ((100 - illumination) / 100) * (lunarCycle / 2);
        } else if (phase.includes('Waning') || phase.includes('Last Quarter')) {
            // Moon is shrinking, next full moon is ~3/4 cycle away
            daysToFullMoon = (illumination / 100) * (lunarCycle / 2) + (lunarCycle / 2);
        } else if (phase.includes('New Moon') || illumination < 5) {
            // New moon, full moon is ~2 weeks away
            daysToFullMoon = lunarCycle / 2;
        } else {
            // Default approximation
            daysToFullMoon = 15;
        }
        
        const fullMoonDate = new Date(now);
        fullMoonDate.setDate(fullMoonDate.getDate() + Math.ceil(daysToFullMoon));
        fullMoonDate.setHours(23, 59, 59, 999);
        
        return fullMoonDate;
    }
    
    /**
     * Initialize Leaflet Map
     * Creates a minimal, clean map interface with no UI controls
     * - NO zoom controls (+/- buttons) for cleaner look
     * - NO attribution box (moved to config if needed)
     * - Uses tile provider from config.json
     * - Centers on configured default location
     * 
     * Map Philosophy:
     * - Fullscreen, immersive experience
     * - No distractions from traditional map UI
     * - All controls overlay on map (filter sentence, logo)
     * - Events are the primary focus
     */
    initMap() {
        const center = this.config.map.default_center;
        
        // Initialize Leaflet map with MINIMAL UI
        // zoomControl: false    → No +/- zoom buttons (cleaner interface)
        // attributionControl: false → No "Leaflet | © OpenStreetMap" box
        this.map = L.map('map', {
            zoomControl: false,        // Remove zoom +/- buttons
            attributionControl: false  // Remove attribution box at bottom-right
        }).setView([center.lat, center.lon], this.config.map.default_zoom);
        
        // Load map tiles from configured provider
        // Default: CartoDB Dark No Labels (minimal - only major roads, no POIs/labels)
        // This keeps the focus on our event markers from JSON
        // Alternative options in config:
        //   - dark_nolabels: Minimal, no labels or POIs
        //   - dark_all: More detail with labels
        //   - light_nolabels: Light theme, minimal
        const tileProvider = this.config.map.tile_provider || 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png';
        const attribution = this.config.map.attribution || '';
        
        // Add tile layer to map
        L.tileLayer(tileProvider, {
            maxZoom: 19,           // Maximum zoom level
            attribution: attribution,  // Attribution text (if any)
            subdomains: 'abcd'     // Load balance across tile servers
        }).addTo(this.map);
        
        this.log('Map initialized:', {
            center: center,
            zoom: this.config.map.default_zoom,
            tileProvider: tileProvider,
            style: 'minimal (no labels/POIs - focus on event markers)'
        });
    }
    
    /**
     * Get User's Geolocation
     * Attempts to get user's current position using browser geolocation API
     * Falls back to configured default location if:
     * - User denies permission
     * - Geolocation not available
     * - Geolocation fails/times out
     * 
     * Once location is obtained:
     * - Centers map on user location
     * - Adds blue marker showing "You are here"
     * - Triggers event display (filters by distance from this location)
     */
    getUserLocation() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    // Center map on user location
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    
                    // Create custom icon for user location
                    const userIcon = L.icon({
                        iconUrl: 'markers/marker-geolocation.svg',
                        iconSize: [32, 48],
                        iconAnchor: [16, 48],
                        popupAnchor: [0, -48]
                    });
                    
                    // Add user marker with custom icon
                    const popupText = window.i18n ? window.i18n.t('map.user_location_popup') : 'You are here';
                    L.marker([this.userLocation.lat, this.userLocation.lon], {
                        icon: userIcon,
                        zIndexOffset: 1000  // Keep on top of event markers
                    })
                        .addTo(this.map)
                        .bindPopup(popupText);
                    
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
                    this.log('Using fallback location:', this.userLocation);
                    
                    // Center map on default location
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    
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
            this.log('Geolocation not supported, using fallback location:', this.userLocation);
            
            this.displayEvents();
        }
    }
    
    async loadEvents() {
        try {
            this.log('Loading events from config data source');
            const dataConfig = this.config.data || { source: 'real' };
            const source = dataConfig.source || 'real';
            
            this.log(`Data source mode: ${source}`);
            
            let allEvents = [];
            
            if (source === 'real') {
                // Load only real events
                const response = await fetch('events.json');
                const data = await response.json();
                allEvents = data.events || [];
                this.log(`Loaded ${allEvents.length} real events`);
            } else if (source === 'demo') {
                // Load only demo events
                const response = await fetch('events.demo.json');
                const data = await response.json();
                allEvents = data.events || [];
                this.log(`Loaded ${allEvents.length} demo events`);
            } else if (source === 'both') {
                // Load and combine both real and demo events
                try {
                    const realResponse = await fetch('events.json');
                    const realData = await realResponse.json();
                    const realEvents = realData.events || [];
                    this.log(`Loaded ${realEvents.length} real events`);
                    allEvents = allEvents.concat(realEvents);
                } catch (e) {
                    this.log('Could not load real events:', e);
                }
                
                try {
                    const demoResponse = await fetch('events.demo.json');
                    const demoData = await demoResponse.json();
                    const demoEvents = demoData.events || [];
                    this.log(`Loaded ${demoEvents.length} demo events`);
                    allEvents = allEvents.concat(demoEvents);
                } catch (e) {
                    this.log('Could not load demo events:', e);
                }
                
                this.log(`Combined total: ${allEvents.length} events`);
            }
            
            this.events = allEvents;
            this.log(`Total events loaded: ${this.events.length}`);
            
            // Extract unique categories from events
            this.populateCategories();
            
            // Populate location selector with predefined locations
            this.populateLocationSelector();
            
            // Sort time filter options by minutes from now
            this.sortTimeFilters();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
    }
    
    populateLocationSelector() {
        const locationSelector = document.getElementById('location-selector');
        if (this.config.map?.predefined_locations) {
            this.config.map.predefined_locations.forEach(loc => {
                const option = document.createElement('option');
                option.value = JSON.stringify({ lat: loc.lat, lon: loc.lon });
                option.textContent = `from ${loc.name}`;
                locationSelector.appendChild(option);
            });
        }
    }
    
    /**
     * Sort time filter options by minutes from now
     * Orders the three time filter choices from shortest to longest time
     */
    sortTimeFilters() {
        const timeFilter = document.getElementById('time-filter');
        if (!timeFilter) return;
        
        const now = new Date();
        
        // Calculate minutes from now for each filter option
        const optionsWithTime = Array.from(timeFilter.options).map(option => {
            const value = option.value;
            let targetTime;
            
            switch (value) {
                case 'sunrise':
                    targetTime = new Date(now);
                    targetTime.setHours(6, 0, 0, 0);
                    if (now.getHours() >= 6) {
                        targetTime.setDate(targetTime.getDate() + 1);
                    }
                    break;
                    
                case 'sunday':
                    targetTime = new Date(now);
                    const daysUntilSunday = (7 - now.getDay()) % 7 || 7;
                    targetTime.setDate(targetTime.getDate() + daysUntilSunday);
                    targetTime.setHours(20, 15, 0, 0);
                    break;
                    
                case 'full-moon':
                    if (this.nextFullMoonDate) {
                        targetTime = this.nextFullMoonDate;
                    } else {
                        // Fallback: approximate ~29.5 days lunar cycle
                        targetTime = new Date(now);
                        targetTime.setDate(targetTime.getDate() + 15);
                        targetTime.setHours(23, 59, 59, 999);
                    }
                    break;
                    
                default:
                    targetTime = now;
            }
            
            const minutesFromNow = Math.floor((targetTime - now) / (1000 * 60));
            
            return {
                option: option,
                value: value,
                text: option.textContent,
                minutesFromNow: minutesFromNow,
                selected: option.selected
            };
        });
        
        // Sort by minutes from now (ascending)
        optionsWithTime.sort((a, b) => a.minutesFromNow - b.minutesFromNow);
        
        // Remove all options
        while (timeFilter.options.length > 0) {
            timeFilter.remove(0);
        }
        
        // Add options back in sorted order
        optionsWithTime.forEach(item => {
            const option = document.createElement('option');
            option.value = item.value;
            option.textContent = item.text;
            option.selected = item.selected;
            timeFilter.appendChild(option);
        });
        
        this.log('Time filters sorted by minutes from now:', optionsWithTime.map(o => `${o.value}: ${o.minutesFromNow} min`));
    }
    
    populateCategories() {
        const categories = new Set();
        this.events.forEach(event => {
            if (event.category) {
                categories.add(event.category);
            }
        });
        
        // Populate category filter dropdown
        const categoryFilter = document.getElementById('category-filter');
        
        // Clear existing dynamically-added options, keeping only the "all" option
        // Verify first option is the "all" option before clearing
        if (categoryFilter.options.length > 0 && categoryFilter.options[0].value === 'all') {
            while (categoryFilter.options.length > 1) {
                categoryFilter.remove(1);
            }
        } else {
            // If first option isn't "all", clear everything and recreate
            categoryFilter.innerHTML = '';
            const allOption = document.createElement('option');
            allOption.value = 'all';
            allOption.textContent = window.i18n ? window.i18n.t('filters.categories.all') : 'events';
            categoryFilter.appendChild(allOption);
        }
        
        // Update the "all" option text with translation
        if (window.i18n && categoryFilter.options.length > 0) {
            categoryFilter.options[0].textContent = window.i18n.t('filters.categories.all');
        }
        
        // Add category options with translations
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            // Use i18n translation if available, fallback to category name
            option.textContent = window.i18n ? window.i18n.t(`filters.categories.${category}`) : category;
            categoryFilter.appendChild(option);
        });
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
                
            case 'sunday':
                // Next Sunday at 20:15 (prime time)
                const sunday = new Date(now);
                const daysUntilSunday = (7 - now.getDay()) % 7 || 7;
                sunday.setDate(sunday.getDate() + daysUntilSunday);
                sunday.setHours(20, 15, 0, 0);
                return sunday;
                
            case 'full-moon':
                // Use fetched full moon date or fallback to approximation
                if (this.nextFullMoonDate) {
                    return this.nextFullMoonDate;
                } else {
                    // Fallback: approximate ~29.5 days lunar cycle
                    const nextFullMoon = new Date(now);
                    nextFullMoon.setDate(nextFullMoon.getDate() + 15);
                    nextFullMoon.setHours(23, 59, 59, 999);
                    return nextFullMoon;
                }
                
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
        
        this.log('Filtering events:', {
            totalEvents: this.events.length,
            maxEventTime: maxEventTime,
            maxDistance: maxDistance,
            category: category,
            referenceLocation: referenceLocation
        });
        
        const filtered = this.events.filter(event => {
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                this.log(`Event "${event.title}" filtered out: after time limit`);
                return false;
            }
            
            // Filter by category
            if (category !== 'all' && event.category !== category) {
                this.log(`Event "${event.title}" filtered out: category mismatch`);
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
                    this.log(`Event "${event.title}" filtered out: ${distance.toFixed(1)}km > ${maxDistance}km`);
                    return false;
                }
            }
            
            return true;
        });
        
        this.log(`Filtered to ${filtered.length} events`);
        return filtered;
    }
    
    fitMapToMarkers() {
        if (this.markers.length === 0) {
            this.log('No markers to fit');
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
        
        this.log('Map fitted to bounds:', bounds);
    }
    
    displayEvents() {
        const filteredEvents = this.filterEvents();
        
        // Update count with descriptive sentence
        this.updateFilterDescription(filteredEvents.length);
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        // Reset marker navigation index when markers change
        this.currentMarkerIndex = -1;
        
        if (filteredEvents.length === 0) {
            this.log('No events to display');
            this.announceToScreenReader('No events match the current filters');
            return;
        }
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Display events as map markers only
        filteredEvents.forEach(event => {
            this.addEventMarker(event);
        });
        
        // Fit map to show all markers
        this.fitMapToMarkers();
        
        // Announce to screen readers
        this.announceToScreenReader(`${filteredEvents.length} events displayed on map. Use arrow keys to navigate between events.`);
    }
    
    announceToScreenReader(message) {
        // Create or update ARIA live region for screen reader announcements
        let liveRegion = document.getElementById('aria-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'aria-live-region';
            liveRegion.className = 'sr-only';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            document.body.appendChild(liveRegion);
        }
        liveRegion.textContent = message;
    }
    
    updateFilterDescription(count) {
        // Get the category filter element
        const categoryFilter = document.getElementById('category-filter');
        
        // First, restore all options to their original text
        for (let i = 0; i < categoryFilter.options.length; i++) {
            const option = categoryFilter.options[i];
            // Store original text on first run
            if (!option.dataset.originalText) {
                option.dataset.originalText = option.textContent;
            }
            // Restore to original text
            option.textContent = option.dataset.originalText;
        }
        
        // Now update the selected option with the count
        const selectedOption = categoryFilter.options[categoryFilter.selectedIndex];
        const categoryValue = selectedOption.value;
        const categoryText = selectedOption.dataset.originalText;
        
        // Helper function to get singular or plural form
        const getCountText = (count) => {
            if (!window.i18n) {
                // Fallback without i18n
                if (count === 0) return 'No events';
                return count === 1 ? `${count} event` : `${count} events`;
            }
            
            // Use translation system with proper singular/plural
            if (count === 0) {
                return window.i18n.t('filters.event_count.none');
            } else if (count === 1) {
                return window.i18n.t('filters.event_count.singular', { count: count });
            } else {
                return window.i18n.t('filters.event_count.plural', { count: count });
            }
        };
        
        // Helper to get event word (singular/plural)
        const getEventWord = (count) => {
            if (!window.i18n) {
                return count === 1 ? 'event' : 'events';
            }
            return count === 1 ? 
                window.i18n.t('filters.event_word.singular') : 
                window.i18n.t('filters.event_word.plural');
        };
        
        // Build count text based on selected category
        let countText = '';
        if (categoryValue === 'all') {
            // For "all" category, just show count
            countText = getCountText(count);
        } else {
            // Get the base category text for comparison
            const baseCategory = window.i18n ? window.i18n.t(`filters.categories.${categoryValue}`) : categoryText;
            
            // Check if this is the main "events" category by comparing with translated value
            const allCategoryText = window.i18n ? window.i18n.t('filters.categories.all') : 'events';
            
            if (categoryText === allCategoryText) {
                // Don't double-show "events" - just use the count text
                countText = getCountText(count);
            } else if (categoryValue === 'festivals') {
                // Festivals has special singular form
                const singularForm = window.i18n ? window.i18n.t('filters.categories_singular.festivals') : 'festival';
                countText = count === 1 ? `${count} ${singularForm}` : `${count} ${categoryText}`;
            } else {
                // For other categories: "X category events" or "1 category event"
                const eventWord = getEventWord(count);
                countText = `${count} ${categoryText} ${eventWord}`;
            }
        }
        
        // Update the category filter to show the count
        selectedOption.textContent = countText;
        
        this.log('Filter count updated:', countText);
    }
    
    /**
     * Update all UI text with current language translations
     * Called when language is changed
     */
    updateUITranslations() {
        if (!window.i18n) return;
        
        const t = (key) => window.i18n.t(key);
        
        // Update time filter options
        const timeFilter = document.getElementById('time-filter');
        if (timeFilter) {
            const timeOptions = timeFilter.options;
            for (let i = 0; i < timeOptions.length; i++) {
                const value = timeOptions[i].value;
                timeOptions[i].textContent = t(`filters.time_ranges.${value}`);
            }
        }
        
        // Update distance filter options
        const distanceFilter = document.getElementById('distance-filter');
        if (distanceFilter) {
            const distOptions = distanceFilter.options;
            for (let i = 0; i < distOptions.length; i++) {
                const value = distOptions[i].value;
                distOptions[i].textContent = t(`filters.distances.${value}`);
            }
        }
        
        // Update category filter options
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            const catOptions = categoryFilter.options;
            for (let i = 0; i < catOptions.length; i++) {
                const value = catOptions[i].value;
                const translatedText = t(`filters.categories.${value}`);
                catOptions[i].textContent = translatedText;
                // Update the stored original text for the new language
                catOptions[i].dataset.originalText = translatedText;
            }
        }
        
        // Update location selector options
        const locationSelector = document.getElementById('location-selector');
        if (locationSelector) {
            // Update the geolocation option
            if (locationSelector.options[0]) {
                locationSelector.options[0].textContent = t('filters.locations.geolocation');
            }
        }
        
        this.log('UI translations updated');
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        // Get locale for formatting - use proper BCP 47 locale tags
        const locale = window.i18n ? window.i18n.getLocale() : 'en';
        const localeMap = {
            'en': 'en-US',
            'de': 'de-DE',
            'fr': 'fr-FR',
            'es': 'es-ES',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'nl': 'nl-NL'
        };
        const localeString = localeMap[locale] || locale;
        
        const timeStr = date.toLocaleTimeString(localeString, { hour: '2-digit', minute: '2-digit' });
        
        // Check if today - use i18n translation
        if (date.toDateString() === now.toDateString()) {
            const todayText = window.i18n ? window.i18n.t('time.today') : 'Today';
            return `${todayText} ${timeStr}`;
        }
        // Check if tomorrow - use i18n translation
        else if (date.toDateString() === tomorrow.toDateString()) {
            const tomorrowText = window.i18n ? window.i18n.t('time.tomorrow') : 'Tomorrow';
            return `${tomorrowText} ${timeStr}`;
        }
        // Otherwise show date with locale-aware formatting
        else {
            return date.toLocaleString(localeString, { 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    }
    
    /**
     * Get marker icon based on event category
     * Returns a Leaflet icon object with the appropriate SVG marker
     * @param {string} category - Event category (music, sports, arts, food, festivals, workshops, community, etc.)
     * @returns {L.Icon} Leaflet icon object
     */
    getCategoryIcon(category) {
        // Map categories to marker files
        const markerMap = {
            'music': 'markers/marker-music.svg',
            'sports': 'markers/marker-sports.svg',
            'arts': 'markers/marker-arts.svg',
            'food': 'markers/marker-food.svg',
            'festivals': 'markers/marker-festivals.svg',
            'workshops': 'markers/marker-workshops.svg',
            'community': 'markers/marker-community.svg',
            // Legacy categories (backward compatibility)
            'on-stage': 'markers/marker-on-stage.svg',
            'pub-games': 'markers/marker-pub-games.svg'
        };
        
        // Get marker URL for this category, or use default
        const iconUrl = markerMap[category] || 'markers/marker-default.svg';
        
        return L.icon({
            iconUrl: iconUrl,
            iconSize: [32, 48],
            iconAnchor: [16, 48],
            popupAnchor: [0, -48]
        });
    }
    
    addEventMarker(event) {
        if (!event.location) return;
        
        const eventDate = new Date(event.start_time);
        const previewTime = this.formatTime(event.start_time);
        
        // Get category-specific icon
        const icon = this.getCategoryIcon(event.category);
        
        // Standard Leaflet marker with custom icon (pure Leaflet convention)
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: icon
        })
            .addTo(this.map);
        
        // Make marker keyboard accessible after element is created
        // Use setTimeout to ensure DOM element is available
        setTimeout(() => {
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.setAttribute('tabindex', '0');
                markerElement.setAttribute('role', 'button');
                markerElement.setAttribute('aria-label', `${event.title} at ${event.location.name}, ${previewTime}. Press Enter to view details.`);
                
                // Add keyboard event listeners
                markerElement.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        marker.openPopup();
                    }
                });
                
                this.log(`Keyboard accessibility added to marker: ${event.title}`);
            } else {
                console.warn(`Marker element not available for: ${event.title}`);
            }
        }, 0);
        
        // Use Leaflet's bindTooltip for time preview (permanent tooltip above marker)
        marker.bindTooltip(previewTime, {
            permanent: true,
            direction: 'top',
            offset: [0, -10],
            className: 'event-time-tooltip'
        });
        
        // Create rich popup with all event details (pure Leaflet convention)
        // Add line index for staggered typewriter animation
        let lineIndex = 0;
        const eventId = `event-${event.id || Math.random().toString(36).substr(2, 9)}`;
        
        // Get translations for popup content
        const t = (key) => window.i18n ? window.i18n.t(key) : key;
        const distanceText = event.distance !== undefined ? 
            t('event_detail.distance_format').replace('{distance}', event.distance.toFixed(1)) : 
            '';
        
        const popupContent = `
            <div class="event-popup" data-event-id="${eventId}">
                <!-- Burger Menu Button (Terminal Style) -->
                <button class="burger-menu" aria-label="Event actions menu" aria-expanded="false" aria-controls="${eventId}-menu" title="Actions">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                
                <!-- Dropdown Menu with Terminal-Style Actions -->
                <div class="burger-menu-dropdown" id="${eventId}-menu" role="menu">
                    <!-- Bookmark/Highlight -->
                    <button class="menu-item bookmark-event" role="menuitem" data-event-id="${eventId}" title="${t('burger_menu.actions.bookmark.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.bookmark.icon')}</span> <span class="menu-text">${t('burger_menu.actions.bookmark.label')}</span>
                    </button>
                    
                    <!-- Copy Event Details (Terminal Style) -->
                    <button class="menu-item copy-details" role="menuitem" title="${t('burger_menu.actions.copy.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.copy.icon')}</span> <span class="menu-text">${t('burger_menu.actions.copy.label')}</span>
                    </button>
                    
                    <!-- Share Event -->
                    <button class="menu-item share-event" role="menuitem" data-title="${event.title.replace(/"/g, '&quot;')}" data-location="${event.location.name.replace(/"/g, '&quot;')}" title="${t('burger_menu.actions.share.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.share.icon')}</span> <span class="menu-text">${t('burger_menu.actions.share.label')}</span>
                    </button>
                    
                    ${event.url ? `<a href="${event.url}" target="_blank" rel="noopener noreferrer" class="menu-item" role="menuitem" title="${t('burger_menu.actions.url.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.url.icon')}</span> <span class="menu-text">${t('burger_menu.actions.url.label')}</span>
                    </a>` : ''}
                    
                    <!-- Navigation to Event -->
                    <button class="menu-item navigate-event" role="menuitem" data-lat="${event.location.lat}" data-lon="${event.location.lon}" title="${t('burger_menu.actions.navigate.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.navigate.icon')}</span> <span class="menu-text">${t('burger_menu.actions.navigate.label')}</span>
                    </button>
                    
                    <!-- Add to Calendar -->
                    <button class="menu-item add-calendar" role="menuitem" title="${t('burger_menu.actions.calendar.aria_label')}" data-event='${JSON.stringify({title: event.title, start: event.start_time, location: event.location.name, description: event.description || ''}).replace(/'/g, "&apos;")}'>
                        <span class="menu-icon">${t('burger_menu.actions.calendar.icon')}</span> <span class="menu-text">${t('burger_menu.actions.calendar.label')}</span>
                    </button>
                    
                    <!-- Visit Counter (Placeholder for future) -->
                    <div class="menu-item menu-info" role="menuitem" title="${t('burger_menu.actions.views.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.views.icon')}</span> <span class="menu-text">${t('burger_menu.actions.views.label')}<span class="visit-count">--</span></span>
                    </div>
                    
                    <!-- Close Popup -->
                    <button class="menu-item close-popup" role="menuitem" title="${t('burger_menu.actions.exit.aria_label')}">
                        <span class="menu-icon">${t('burger_menu.actions.exit.icon')}</span> <span class="menu-text">${t('burger_menu.actions.exit.label')}</span>
                    </button>
                </div>
                
                <h3>${event.title}</h3>
                <div class="event-popup-info">
                    <p style="--line-index: ${lineIndex++};"><span class="icon">🕐</span> ${eventDate.toLocaleString([], { 
                        weekday: 'short',
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit', 
                        minute: '2-digit' 
                    })}</p>
                    <p style="--line-index: ${lineIndex++};"><span class="icon">📍</span> ${event.location.name}</p>
                    ${event.distance !== undefined ? 
                        `<p style="--line-index: ${lineIndex++};"><span class="icon">📏</span> ${distanceText}</p>` : 
                        ''}
                </div>
                ${event.description ? 
                    `<div class="event-popup-description">${event.description}</div>` : 
                    ''}
            </div>
        `;
        
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            minWidth: 200,
            className: 'event-popup-container',
            closeButton: false  // Hide default close button, use our burger menu
        });
        
        // Store event data for menu actions
        marker.eventFullData = event;
        
        // Add typewriter animation and burger menu functionality when popup opens
        marker.on('popupopen', (e) => {
            const popupWrapper = e.popup.getElement().querySelector('.leaflet-popup-content-wrapper');
            if (popupWrapper) {
                // Add typing class to trigger animation
                setTimeout(() => {
                    popupWrapper.classList.add('typing');
                }, 10);
                
                // Remove typing class after animation completes
                setTimeout(() => {
                    popupWrapper.classList.remove('typing');
                }, 2000);
                
                // Setup burger menu functionality
                const burgerBtn = popupWrapper.querySelector('.burger-menu');
                const dropdown = popupWrapper.querySelector('.burger-menu-dropdown');
                const closeBtn = popupWrapper.querySelector('.close-popup');
                const shareBtn = popupWrapper.querySelector('.share-event');
                const bookmarkBtn = popupWrapper.querySelector('.bookmark-event');
                const copyBtn = popupWrapper.querySelector('.copy-details');
                const navigateBtn = popupWrapper.querySelector('.navigate-event');
                const calendarBtn = popupWrapper.querySelector('.add-calendar');
                
                if (burgerBtn && dropdown) {
                    // Toggle burger menu
                    burgerBtn.addEventListener('click', (event) => {
                        event.stopPropagation();
                        const isExpanded = burgerBtn.getAttribute('aria-expanded') === 'true';
                        burgerBtn.setAttribute('aria-expanded', !isExpanded);
                        burgerBtn.classList.toggle('active');
                        dropdown.classList.toggle('show');
                    });
                    
                    // Close popup button
                    if (closeBtn) {
                        closeBtn.addEventListener('click', () => {
                            e.target.closePopup();
                        });
                    }
                    
                    // Bookmark/Highlight event
                    if (bookmarkBtn) {
                        // Check if already bookmarked
                        const bookmarkedEvents = JSON.parse(localStorage.getItem('bookmarkedEvents') || '[]');
                        const eventId = bookmarkBtn.dataset.eventId;
                        
                        if (bookmarkedEvents.includes(eventId)) {
                            bookmarkBtn.classList.add('bookmarked');
                            const unbookmarkText = window.i18n ? window.i18n.t('burger_menu.actions.bookmark.label_active') : 'unbookmark';
                            bookmarkBtn.querySelector('.menu-text').textContent = unbookmarkText;
                        }
                        
                        bookmarkBtn.addEventListener('click', () => {
                            this.toggleBookmark(eventId, bookmarkBtn, marker);
                        });
                    }
                    
                    // Copy event details to clipboard
                    if (copyBtn) {
                        copyBtn.addEventListener('click', () => {
                            const eventData = marker.eventFullData;
                            const text = `EVENT: ${eventData.title}\nTIME: ${new Date(eventData.start_time).toLocaleString()}\nLOCATION: ${eventData.location.name}\nDESCRIPTION: ${eventData.description || 'N/A'}\n${eventData.url ? 'URL: ' + eventData.url : ''}`;
                            
                            navigator.clipboard.writeText(text).then(() => {
                                copyBtn.querySelector('.menu-text').textContent = 'copied!';
                                setTimeout(() => {
                                    copyBtn.querySelector('.menu-text').textContent = 'copy_data';
                                }, 2000);
                            }).catch(err => {
                                console.error('Copy failed:', err);
                            });
                        });
                    }
                    
                    // Share button
                    if (shareBtn) {
                        shareBtn.addEventListener('click', () => {
                            const title = shareBtn.dataset.title;
                            const location = shareBtn.dataset.location;
                            const text = `Check out: ${title} at ${location}`;
                            
                            if (navigator.share) {
                                navigator.share({
                                    title: title,
                                    text: text,
                                    url: window.location.href
                                }).catch(err => console.log('Share cancelled'));
                            } else {
                                navigator.clipboard.writeText(text).then(() => {
                                    shareBtn.querySelector('.menu-text').textContent = 'shared!';
                                    setTimeout(() => {
                                        shareBtn.querySelector('.menu-text').textContent = 'share';
                                    }, 2000);
                                }).catch(err => console.error('Share failed:', err));
                            }
                        });
                    }
                    
                    // Navigate to event location
                    if (navigateBtn) {
                        navigateBtn.addEventListener('click', () => {
                            const lat = navigateBtn.dataset.lat;
                            const lon = navigateBtn.dataset.lon;
                            // Open in Google Maps
                            window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`, '_blank');
                        });
                    }
                    
                    // Add to calendar
                    if (calendarBtn) {
                        calendarBtn.addEventListener('click', () => {
                            const eventData = JSON.parse(calendarBtn.dataset.event.replace(/&apos;/g, "'"));
                            this.addToCalendar(eventData);
                        });
                    }
                    
                    // Close dropdown when clicking outside
                    document.addEventListener('click', (event) => {
                        if (!burgerBtn.contains(event.target) && !dropdown.contains(event.target)) {
                            dropdown.classList.remove('show');
                            burgerBtn.classList.remove('active');
                            burgerBtn.setAttribute('aria-expanded', 'false');
                        }
                    });
                }
            }
        });
        
        // Store event data with marker for keyboard navigation
        marker.eventData = event;
        
        this.markers.push(marker);
    }
    
    showEventDetail(event) {
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
        // Distance filter (now a select)
        const distanceFilter = document.getElementById('distance-filter');
        distanceFilter.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            this.filters.maxDistance = value;
            this.displayEvents();
        });
        
        // Time filter
        const timeFilter = document.getElementById('time-filter');
        timeFilter.addEventListener('change', (e) => {
            this.filters.timeFilter = e.target.value;
            this.displayEvents();
        });
        
        // Category filter
        const categoryFilter = document.getElementById('category-filter');
        categoryFilter.addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.displayEvents();
        });
        
        // Location selector
        const locationSelector = document.getElementById('location-selector');
        locationSelector.addEventListener('change', (e) => {
            if (e.target.value === 'geolocation') {
                // Use geolocation
                this.filters.useCustomLocation = false;
                this.filters.customLat = null;
                this.filters.customLon = null;
                if (this.userLocation) {
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                }
            } else {
                // Use predefined location
                const location = JSON.parse(e.target.value);
                this.filters.useCustomLocation = true;
                this.filters.customLat = location.lat;
                this.filters.customLon = location.lon;
                this.map.setView([location.lat, location.lon], 13);
            }
            this.displayEvents();
        });
        
        // Event detail close listeners
        document.getElementById('close-detail').addEventListener('click', () => {
            document.getElementById('event-detail').classList.add('hidden');
        });
        
        document.getElementById('event-detail').addEventListener('click', (e) => {
            if (e.target.id === 'event-detail') {
                document.getElementById('event-detail').classList.add('hidden');
            }
        });
        
        // Keyboard navigation for cycling through event markers
        this.currentMarkerIndex = -1;
        document.addEventListener('keydown', (e) => {
            // Only handle arrow keys when not focused on an input/select
            if (document.activeElement.tagName === 'SELECT' || 
                document.activeElement.tagName === 'INPUT' ||
                document.activeElement.tagName === 'TEXTAREA') {
                return;
            }
            
            if (this.markers.length === 0) return;
            
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateToNextMarker();
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateToPreviousMarker();
            } else if (e.key === 'Escape') {
                // Close any open popups
                this.map.closePopup();
                document.getElementById('event-detail').classList.add('hidden');
            }
        });
        
        // Imprint link handler - show project location on map if configured
        const imprintLink = document.getElementById('imprint-link');
        if (imprintLink && this.config.ui && this.config.ui.imprint_location) {
            imprintLink.addEventListener('click', (e) => {
                // Only handle if URL is '#' (indicating map marker mode)
                if (this.config.ui.imprint_url === '#') {
                    e.preventDefault();
                    this.showImprintLocation();
                }
            });
        }
        
        // Language selector - switch language and re-render content
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            // Set initial value based on current i18n locale
            if (window.i18n) {
                languageSelect.value = window.i18n.getLocale();
            }
            
            languageSelect.addEventListener('change', async (e) => {
                const newLocale = e.target.value;
                this.log('Language changed to:', newLocale);
                
                if (window.i18n) {
                    await window.i18n.switchLanguage(newLocale);
                    // Update all UI text with new translations
                    this.updateUITranslations();
                    // Re-display events to update time formatting (Today/Tomorrow) and popups
                    this.displayEvents();
                }
            });
        }
    }
    
    /**
     * Show the project/imprint location on the map with a marker
     * Uses config for functional data (coordinates, URLs) and content for translated text
     */
    showImprintLocation() {
        const imprintConfig = this.config.imprint;
        if (!imprintConfig || !imprintConfig.enabled || !imprintConfig.location) return;
        
        const loc = imprintConfig.location;
        const content = window.i18n.content.imprint;  // Get translated content
        
        // Pan to imprint location
        this.map.setView([loc.lat, loc.lon], 16);
        
        // Create custom icon for imprint location
        const iconUrl = loc.marker || 'markers/marker-city-center.svg';
        const imprintIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [32, 48],
            iconAnchor: [16, 48],
            popupAnchor: [0, -48]
        });
        
        // Remove any existing imprint marker
        if (this.imprintMarker) {
            this.map.removeLayer(this.imprintMarker);
        }
        
        // Create marker
        this.imprintMarker = L.marker([loc.lat, loc.lon], {
            icon: imprintIcon,
            zIndexOffset: 1000  // Keep on top
        }).addTo(this.map);
        
        // Build imprint popup content using translated content + functional config
        let popupContent = `<div class="imprint-popup">`;
        
        // Header (translated)
        popupContent += `<h3>${content.title}</h3>`;
        
        // Operator information (translated labels + data)
        popupContent += `<div class="imprint-section">`;
        popupContent += `<p><strong>${content.operator.name}</strong></p>`;
        popupContent += `<p><em>${content.operator.type}</em></p>`;
        
        // Address (from content - allows translation of state/country names)
        const addr = content.address;
        popupContent += `<p>${addr.postal_code} ${addr.city}</p>`;
        popupContent += `<p>${addr.state}, ${addr.country}</p>`;
        popupContent += `</div>`;
        
        // Contact information (functional URLs from config, labels from content)
        const contact = imprintConfig.contact;
        popupContent += `<div class="imprint-section">`;
        if (contact.email) {
            popupContent += `<p>📧 <a href="mailto:${contact.email}">${contact.email}</a></p>`;
        }
        if (contact.website) {
            popupContent += `<p>🌐 <a href="${contact.website}" target="_blank" rel="noopener">${content.contact.website}</a></p>`;
        }
        if (contact.github) {
            popupContent += `<p>💻 <a href="${contact.github}" target="_blank" rel="noopener">${content.contact.github}</a></p>`;
        }
        popupContent += `</div>`;
        
        // Responsible person (functional data from config, labels from content)
        const resp = imprintConfig.responsible;
        if (resp.name) {
            popupContent += `<div class="imprint-section">`;
            popupContent += `<p><strong>${content.responsible.label}:</strong></p>`;
            popupContent += `<p>${resp.name} - ${content.responsible.role}</p>`;
            if (resp.email) {
                popupContent += `<p>📧 <a href="mailto:${resp.email}">${resp.email}</a></p>`;
            }
            popupContent += `</div>`;
        }
        
        // Technical information (functional data from config, labels from content)
        const tech = imprintConfig.technical;
        popupContent += `<div class="imprint-section">`;
        popupContent += `<p><strong>${content.technical.label}:</strong></p>`;
        if (tech.hosting) popupContent += `<p>${content.technical.hosting}: ${tech.hosting}</p>`;
        if (tech.domain) popupContent += `<p>${content.technical.domain}: ${tech.domain}</p>`;
        if (tech.open_source && tech.repository) {
            popupContent += `<p><a href="${tech.repository}" target="_blank" rel="noopener">${content.technical.open_source}</a></p>`;
        }
        popupContent += `</div>`;
        
        // Legal information (all from translated content)
        popupContent += `<div class="imprint-section imprint-legal">`;
        if (content.legal.disclaimer) {
            popupContent += `<p><small>${content.legal.disclaimer}</small></p>`;
        }
        if (content.legal.copyright) {
            popupContent += `<p><small>${content.legal.copyright}</small></p>`;
        }
        popupContent += `</div>`;
        
        // Coordinates
        popupContent += `<div class="imprint-section">`;
        popupContent += `<p><small>📍 ${loc.lat.toFixed(4)}, ${loc.lon.toFixed(4)}</small></p>`;
        popupContent += `</div>`;
        
        popupContent += `</div>`;
        
        // Bind and open popup with larger size for imprint data
        this.imprintMarker.bindPopup(popupContent, {
            maxWidth: 400,
            maxHeight: 500,
            className: 'imprint-popup-container'
        }).openPopup();
        
        // Announce to screen reader
        this.announceToScreenReader(`Showing imprint and legal information for: ${content.title}`);
    }
    
    navigateToNextMarker() {
        if (this.markers.length === 0) return;
        
        this.currentMarkerIndex = (this.currentMarkerIndex + 1) % this.markers.length;
        this.focusMarker(this.currentMarkerIndex);
    }
    
    navigateToPreviousMarker() {
        if (this.markers.length === 0) return;
        
        this.currentMarkerIndex = this.currentMarkerIndex <= 0 
            ? this.markers.length - 1 
            : this.currentMarkerIndex - 1;
        this.focusMarker(this.currentMarkerIndex);
    }
    
    focusMarker(index) {
        const marker = this.markers[index];
        if (!marker) return;
        
        // Pan to marker
        this.map.panTo(marker.getLatLng());
        
        // Focus the marker element
        const markerElement = marker.getElement();
        if (markerElement) {
            markerElement.focus();
        }
        
        // Open popup
        marker.openPopup();
        
        // Announce to screen reader
        if (marker.eventData) {
            this.announceToScreenReader(
                `Event ${index + 1} of ${this.markers.length}: ${marker.eventData.title} at ${marker.eventData.location.name}`
            );
        }
    }
    
    /**
     * Toggle bookmark for an event
     * Saves bookmarked events to localStorage
     * Highlights bookmarked events on map with different style
     * @param {string} eventId - Unique event identifier
     * @param {HTMLElement} button - Bookmark button element
     * @param {L.Marker} marker - Leaflet marker to highlight
     */
    toggleBookmark(eventId, button, marker) {
        const bookmarkedEvents = JSON.parse(localStorage.getItem('bookmarkedEvents') || '[]');
        const index = bookmarkedEvents.indexOf(eventId);
        
        if (index > -1) {
            // Remove bookmark
            bookmarkedEvents.splice(index, 1);
            button.classList.remove('bookmarked');
            const bookmarkText = window.i18n ? window.i18n.t('burger_menu.actions.bookmark.label') : 'bookmark';
            button.querySelector('.menu-text').textContent = bookmarkText;
            
            // Remove highlight from marker
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.classList.remove('bookmarked-marker');
            }
            
            this.announceToScreenReader('Bookmark removed');
        } else {
            // Add bookmark
            bookmarkedEvents.push(eventId);
            button.classList.add('bookmarked');
            const unbookmarkText = window.i18n ? window.i18n.t('burger_menu.actions.bookmark.label_active') : 'unbookmark';
            button.querySelector('.menu-text').textContent = unbookmarkText;
            
            // Highlight marker
            const markerElement = marker.getElement();
            if (markerElement) {
                markerElement.classList.add('bookmarked-marker');
            }
            
            this.announceToScreenReader('Event bookmarked');
        }
        
        // Save to localStorage
        localStorage.setItem('bookmarkedEvents', JSON.stringify(bookmarkedEvents));
        this.log('Bookmarked events:', bookmarkedEvents);
    }
    
    /**
     * Add event to calendar
     * Generates iCalendar (.ics) file for download
     * @param {Object} eventData - Event information
     */
    addToCalendar(eventData) {
        // Create iCalendar format
        const startDate = new Date(eventData.start);
        const endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000); // Default 2 hours
        
        // Format dates for iCal (YYYYMMDDTHHmmss)
        const formatDate = (date) => {
            return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        };
        
        const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//KRWL HOF//Community Events//EN
BEGIN:VEVENT
UID:${Date.now()}@krwl-hof.events
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(startDate)}
DTEND:${formatDate(endDate)}
SUMMARY:${eventData.title}
LOCATION:${eventData.location}
DESCRIPTION:${eventData.description.replace(/\n/g, '\\n')}
END:VEVENT
END:VCALENDAR`;
        
        // Create download link
        const blob = new Blob([icsContent], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `event-${eventData.title.replace(/[^a-z0-9]/gi, '-')}.ics`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.announceToScreenReader('Event added to calendar');
        this.log('Calendar file generated for:', eventData.title);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
