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
        this.map = L.map('map').setView([center.lat, center.lon], this.config.map.default_zoom);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
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
            const response = await fetch('events.json');
            const data = await response.json();
            this.events = data.events || [];
            
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
        const countEl = document.getElementById('event-count');
        
        // Build descriptive sentence
        const eventText = `${count} event${count !== 1 ? 's' : ''}`;
        
        // Time description
        let timeText = '';
        switch (this.filters.timeFilter) {
            case 'sunrise':
                timeText = 'till sunrise';
                break;
            case '6h':
                timeText = 'in the next 6 hours';
                break;
            case '12h':
                timeText = 'in the next 12 hours';
                break;
            case '24h':
                timeText = 'in the next 24 hours';
                break;
            case '48h':
                timeText = 'in the next 48 hours';
                break;
            case 'all':
                timeText = 'upcoming';
                break;
        }
        
        // Distance description (approximate travel time)
        const distance = this.filters.maxDistance;
        let distanceText = '';
        if (distance <= 1) {
            distanceText = 'within walking distance';
        } else if (distance <= 5) {
            const minutes = Math.round(distance * 3); // ~3 min per km walking
            distanceText = `within ${minutes} minutes walk`;
        } else if (distance <= 15) {
            const minutes = Math.round(distance * 4); // ~4 min per km by bike
            distanceText = `within ${minutes} minutes by bike`;
        } else {
            distanceText = `within ${distance} km`;
        }
        
        // Location description
        let locationText = 'from your location';
        if (this.filters.useCustomLocation && this.filters.customLat && this.filters.customLon) {
            locationText = 'from custom location';
        } else if (!this.userLocation) {
            locationText = 'from default location';
        }
        
        // Category description
        let categoryText = '';
        if (this.filters.category !== 'all') {
            categoryText = ` in ${this.filters.category}`;
        }
        
        // Construct the full sentence
        const description = `${eventText}${categoryText} ${timeText} ${distanceText} ${locationText}`;
        
        countEl.textContent = description;
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
        });
        
        // Category filter
        const categoryFilter = document.getElementById('category-filter');
        categoryFilter.addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.displayEvents();
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
            } else {
                alert('Please enter valid latitude (-90 to 90) and longitude (-180 to 180) values.');
            }
        });
        
        // Reset filters button
        const resetFilters = document.getElementById('reset-filters');
        resetFilters.addEventListener('click', () => {
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
