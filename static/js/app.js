// KRWL HOF Community Events App
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
        this.debug = false;
        this.filters = {
            maxDistance: 1.25,  // Default: 15 minutes by foot
            timeFilter: 'sunrise',
            category: 'all',
            useCustomLocation: false,
            customLat: null,
            customLon: null
        };
        
        this.init();
    }
    
    log(...args) {
        if (this.debug) {
            console.log('[KRWL Debug]', ...args);
        }
    }
    
    async init() {
        // Load configuration
        await this.loadConfig();
        
        // Initialize map
        this.initMap();
        
        // Get user location
        this.getUserLocation();
        
        // Load events
        await this.loadEvents();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    async loadConfig() {
        try {
            const response = await fetch('config.json');
            this.config = await response.json();
            this.debug = this.config.debug || false;
            this.log('Config loaded:', this.config);
            if (this.debug) {
                document.title += ' [DEBUG MODE]';
            }
            
            // Fetch next full moon date based on map center location
            await this.fetchNextFullMoon();
        } catch (error) {
            console.error('Error loading config:', error);
            // Use defaults
            this.config = {
                debug: false,
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
    
    async fetchNextFullMoon() {
        try {
            const lat = this.config.map?.default_center?.lat || 50.3167;
            const lon = this.config.map?.default_center?.lon || 11.9167;
            
            // Use astronomy API to get lunar phase data
            // Using wttr.in which is free and doesn't require API key
            const url = `https://wttr.in/${lat},${lon}?format=j1`;
            
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                if (data.weather && data.weather[0]?.astronomy) {
                    const astronomy = data.weather[0].astronomy[0];
                    const moonPhase = astronomy.moon_phase || '';
                    const moonIllumination = parseInt(astronomy.moon_illumination) || 50;
                    
                    // Calculate next full moon
                    this.nextFullMoonDate = this.calculateNextFullMoonFromData(moonPhase, moonIllumination);
                    this.log('Next full moon date:', this.nextFullMoonDate, 'Moon phase:', moonPhase, 'Illumination:', moonIllumination + '%');
                }
            } else {
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
    
    initMap() {
        const center = this.config.map.default_center;
        
        // Initialize map with minimal UI - no zoom controls, no attribution box
        this.map = L.map('map', {
            zoomControl: false,        // Remove zoom +/- buttons
            attributionControl: false  // Remove attribution box
        }).setView([center.lat, center.lon], this.config.map.default_zoom);
        
        // Use dark/night mode tile layer with minimal details
        // CartoDB Dark Matter: Clean, minimal, night mode style
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
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
                    
                    // Add user marker
                    L.marker([this.userLocation.lat, this.userLocation.lon], {
                        icon: L.divIcon({
                            className: 'user-marker',
                            html: '<div style="background: #2196F3; border: 3px solid white; border-radius: 50%; width: 20px; height: 20px;"></div>'
                        })
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
                    this.log('Using fallback location:', this.userLocation);
                    
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
                
            case 'sunday':
                // Next Sunday at 23:59
                const sunday = new Date(now);
                const daysUntilSunday = (7 - now.getDay()) % 7 || 7;
                sunday.setDate(sunday.getDate() + daysUntilSunday);
                sunday.setHours(23, 59, 59, 999);
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
        const container = document.getElementById('events-container');
        
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
        // Update the count filter display
        const countFilterEl = document.getElementById('event-count-filter');
        
        // Build count text based on selected category
        let countText = '';
        if (this.filters.category === 'all') {
            countText = `${count} events`;
        } else {
            // Get the text from the selected category option
            const categoryFilter = document.getElementById('category-filter');
            const selectedOption = categoryFilter.options[categoryFilter.selectedIndex];
            const categoryText = selectedOption.textContent;
            
            // For specific categories, show count with type
            if (categoryText === 'events') {
                countText = `${count} events`;
            } else if (categoryText === 'festivals') {
                countText = `${count} festivals`;
            } else {
                countText = `${count} ${categoryText} events`;
            }
        }
        
        // Update the count display
        countFilterEl.options[0].text = countText;
        countFilterEl.value = 'count';
        
        this.log('Filter count updated:', countText);
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
    
    addEventMarker(event) {
        if (!event.location) return;
        
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: L.divIcon({
                className: 'event-marker',
                html: '<div style="background: #4CAF50; border: 3px solid white; border-radius: 50%; width: 20px; height: 20px;"></div>'
            })
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
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
