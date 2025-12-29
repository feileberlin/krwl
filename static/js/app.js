// AUTO-GENERATED: This file is generated from src/modules/generator.py
// DO NOT EDIT: Manual changes will be overwritten on next build
// To modify: Edit templates in src/modules/generator.py, then run: python3 src/main.py generate

// KRWL HOF Community Events App
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
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
        
        // Display environment watermark if configured
        this.displayEnvironmentWatermark();
        
        // Initialize map (wrapped in try-catch to handle missing Leaflet)
        try {
            this.initMap();
        } catch (error) {
            console.warn('Map initialization failed:', error.message);
        }
        
        // Get user location
        this.getUserLocation();
        
        // Load events
        await this.loadEvents();
        
        // Setup event listeners (always run, even if map fails)
        this.setupEventListeners();
    }
    
    displayEnvironmentWatermark() {
        const watermark = document.getElementById('env-watermark');
        if (!watermark) return;
        
        // Check if watermark is enabled in config
        const watermarkConfig = this.config.watermark || {};
        const enabled = watermarkConfig.enabled !== undefined ? watermarkConfig.enabled : false;
        
        if (!enabled) {
            watermark.classList.add('hidden');
            return;
        }
        
        // Get environment info
        const environment = this.config.app?.environment || 'unknown';
        const envText = watermarkConfig.text || environment.toUpperCase();
        
        // Get build info (commit, PR)
        const buildInfo = this.config.build_info || {};
        let text = envText;
        
        // Add commit info if available
        if (buildInfo.commit_short) {
            text += ` • ${buildInfo.commit_short}`;
        }
        
        // Add PR number if available
        if (buildInfo.pr_number && buildInfo.pr_number !== '') {
            text += ` • PR#${buildInfo.pr_number}`;
        }
        
        // Set watermark text and style
        watermark.textContent = text;
        watermark.classList.remove('hidden', 'production', 'preview', 'testing', 'development');
        watermark.classList.add(environment.toLowerCase());
        
        // Make watermark clickable to show more details if available
        if (buildInfo.commit_sha) {
            watermark.style.cursor = 'pointer';
            watermark.title = `Click for build details\nCommit: ${buildInfo.commit_sha}\nDeployed: ${buildInfo.deployed_at || 'N/A'}\nDeployed by: ${buildInfo.deployed_by || 'N/A'}`;
            watermark.onclick = () => {
                const details = [
                    `Environment: ${environment}`,
                    `Commit: ${buildInfo.commit_sha}`,
                    buildInfo.pr_number ? `PR: #${buildInfo.pr_number}` : null,
                    `Deployed: ${buildInfo.deployed_at || 'N/A'}`,
                    `Deployed by: ${buildInfo.deployed_by || 'N/A'}`,
                    `Ref: ${buildInfo.ref || 'N/A'}`
                ].filter(Boolean).join('\n');
                alert(details);
            };
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
        const statusEl = document.getElementById('location-status');
        
        if ('geolocation' in navigator) {
            statusEl.textContent = 'Getting your location...';
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    // Center map on user location
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    
                    // Add user marker with custom geolocation icon
                    // Support customization from config or use default
                    const userMarkerConfig = this.config.map.user_location_marker || {};
                    const userIconUrl = userMarkerConfig.icon || 'markers/marker-geolocation.svg';
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
                    
                    statusEl.textContent = '📍 Location found';
                    
                    // Update events display
                    this.displayEvents();
                },
                (error) => {
                    console.error('Location error:', error);
                    statusEl.textContent = '⚠️ Location unavailable - using default location';
                    
                    // Use config default location as fallback
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    // Center map on default location
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    
                    // Still display events with fallback location
                    this.displayEvents();
                }
            );
        } else {
            statusEl.textContent = '⚠️ Geolocation not supported - using default location';
            
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
            
            this.events = allEvents;
            
            // Extract unique categories from events
            this.populateCategories();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
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
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
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
        const container = document.getElementById('events-container');
        const countEl = document.getElementById('event-count');
        
        // Update count with descriptive sentence
        this.updateFilterDescription(filteredEvents.length);
        
        // Clear existing content
        container.innerHTML = '';
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        if (filteredEvents.length === 0) {
            container.innerHTML = '<p>No events match the current filters.</p>';
            return;
        }
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Display events
        filteredEvents.forEach(event => {
            this.displayEventCard(event, container);
            this.addEventMarker(event);
        });
        
        // Fit map to show all markers
        this.fitMapToMarkers();
    }
    
    updateFilterDescription(count) {
        // Update individual parts of the filter sentence
        const eventCountText = document.getElementById('event-count-text');
        const categoryText = document.getElementById('category-text');
        const timeText = document.getElementById('time-text');
        const distanceText = document.getElementById('distance-text');
        const locationText = document.getElementById('location-text');
        
        // Event count
        if (eventCountText) {
            eventCountText.textContent = `${count} event${count !== 1 ? 's' : ''}`;
        }
        
        // Category description
        if (categoryText) {
            if (this.filters.category !== 'all') {
                categoryText.textContent = `in ${this.filters.category}`;
            } else {
                categoryText.textContent = 'in all categories';
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
            let locDescription = 'from your location';
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
        // Return SVG marker paths for different event categories
        const iconMap = {
            'on-stage': 'markers/marker-on-stage.svg',        // Diamond with microphone
            'pub-game': 'markers/marker-pub-games.svg',       // Hexagon with beer mug
            'festival': 'markers/marker-festivals.svg',       // Star with flag
            'workshop': 'markers/marker-workshops.svg',       // Workshop icon
            'market': 'markers/marker-shopping.svg',          // Shopping bag for markets
            'sports': 'markers/marker-sports.svg',            // Sports icon
            'community': 'markers/marker-community.svg',      // Community icon
            'other': 'markers/marker-default.svg'             // Default teardrop pin
        };
        
        return iconMap[category] || iconMap['other'];
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
        
        marker.bindPopup(`<strong>${event.title}</strong><br>${event.location.name}`);
        marker.on('click', () => this.showEventDetail(event));
        
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
        // Interactive filter sentence parts
        const categoryTextEl = document.getElementById('category-text');
        const timeTextEl = document.getElementById('time-text');
        const distanceTextEl = document.getElementById('distance-text');
        const locationTextEl = document.getElementById('location-text');
        
        const categoryDropdown = document.getElementById('category-dropdown');
        const timeDropdown = document.getElementById('time-dropdown');
        const distanceDropdown = document.getElementById('distance-dropdown');
        const locationDropdown = document.getElementById('location-dropdown');
        
        // Helper to hide all dropdowns
        const hideAllDropdowns = () => {
            categoryDropdown.classList.add('hidden');
            timeDropdown.classList.add('hidden');
            distanceDropdown.classList.add('hidden');
            locationDropdown.classList.add('hidden');
            
            categoryTextEl.classList.remove('active');
            timeTextEl.classList.remove('active');
            distanceTextEl.classList.remove('active');
            locationTextEl.classList.remove('active');
        };
        
        // Category filter click
        categoryTextEl.addEventListener('click', (e) => {
            e.stopPropagation();
            const wasHidden = categoryDropdown.classList.contains('hidden');
            hideAllDropdowns();
            if (wasHidden) {
                categoryDropdown.classList.remove('hidden');
                categoryTextEl.classList.add('active');
            }
        });
        
        // Time filter click
        timeTextEl.addEventListener('click', (e) => {
            e.stopPropagation();
            const wasHidden = timeDropdown.classList.contains('hidden');
            hideAllDropdowns();
            if (wasHidden) {
                timeDropdown.classList.remove('hidden');
                timeTextEl.classList.add('active');
            }
        });
        
        // Distance filter click
        distanceTextEl.addEventListener('click', (e) => {
            e.stopPropagation();
            const wasHidden = distanceDropdown.classList.contains('hidden');
            hideAllDropdowns();
            if (wasHidden) {
                distanceDropdown.classList.remove('hidden');
                distanceTextEl.classList.add('active');
            }
        });
        
        // Location filter click
        locationTextEl.addEventListener('click', (e) => {
            e.stopPropagation();
            const wasHidden = locationDropdown.classList.contains('hidden');
            hideAllDropdowns();
            if (wasHidden) {
                locationDropdown.classList.remove('hidden');
                locationTextEl.classList.add('active');
            }
        });
        
        // Click outside to close dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#filter-sentence') && !e.target.closest('.filter-dropdown')) {
                hideAllDropdowns();
            }
        });
        
        // Distance filter
        const distanceFilter = document.getElementById('distance-filter');
        const distanceValue = document.getElementById('distance-value');
        distanceFilter.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.filters.maxDistance = value;
            distanceValue.textContent = `${value} km`;
            this.displayEvents();
        });
        
        // Time filter
        const timeFilter = document.getElementById('time-filter');
        timeFilter.addEventListener('change', (e) => {
            this.filters.timeFilter = e.target.value;
            this.displayEvents();
            hideAllDropdowns();
        });
        
        // Category filter
        const categoryFilter = document.getElementById('category-filter');
        categoryFilter.addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.displayEvents();
            hideAllDropdowns();
        });
        
        // Custom location checkbox
        const useCustomLocation = document.getElementById('use-custom-location');
        const customLocationInputs = document.getElementById('custom-location-inputs');
        useCustomLocation.addEventListener('change', (e) => {
            if (e.target.checked) {
                customLocationInputs.classList.remove('hidden');
                // Pre-fill with current location if available
                if (this.userLocation) {
                    document.getElementById('custom-lat').value = this.userLocation.lat.toFixed(4);
                    document.getElementById('custom-lon').value = this.userLocation.lon.toFixed(4);
                }
            } else {
                customLocationInputs.classList.add('hidden');
                this.filters.useCustomLocation = false;
                this.filters.customLat = null;
                this.filters.customLon = null;
                this.displayEvents();
                hideAllDropdowns();
            }
        });
        
        // Apply custom location button
        const applyCustomLocation = document.getElementById('apply-custom-location');
        applyCustomLocation.addEventListener('click', () => {
            const lat = parseFloat(document.getElementById('custom-lat').value);
            const lon = parseFloat(document.getElementById('custom-lon').value);
            
            if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                this.filters.useCustomLocation = true;
                this.filters.customLat = lat;
                this.filters.customLon = lon;
                
                // Update map view to custom location
                this.map.setView([lat, lon], 13);
                
                this.displayEvents();
                hideAllDropdowns();
            } else {
                alert('Please enter valid latitude (-90 to 90) and longitude (-180 to 180) values.');
            }
        });
        
        // Reset filters button
        const resetFilters = document.getElementById('reset-filters-btn');
        resetFilters.addEventListener('click', (e) => {
            e.stopPropagation();
            // Reset all filters to defaults
            this.filters.maxDistance = 5;
            this.filters.timeFilter = 'sunrise';
            this.filters.category = 'all';
            this.filters.useCustomLocation = false;
            this.filters.customLat = null;
            this.filters.customLon = null;
            
            // Reset UI elements
            document.getElementById('distance-filter').value = 5;
            document.getElementById('distance-value').textContent = '5 km';
            document.getElementById('time-filter').value = 'sunrise';
            document.getElementById('category-filter').value = 'all';
            document.getElementById('use-custom-location').checked = false;
            document.getElementById('custom-location-inputs').classList.add('hidden');
            
            // Reset map view
            if (this.userLocation) {
                this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
            }
            
            this.displayEvents();
            hideAllDropdowns();
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
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
