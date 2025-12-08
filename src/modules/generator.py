"""Static site generator module"""

import json
from pathlib import Path
from .utils import load_events


class StaticSiteGenerator:
    """Generator for static site files"""
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.static_path = base_path / 'static'
        
    def generate_all(self):
        """Generate all static files"""
        print("Generating HTML...")
        self._generate_html()
        
        print("Generating CSS...")
        self._generate_css()
        
        print("Generating JavaScript...")
        self._generate_js()
        
        print("Copying data files...")
        self._copy_data_files()
        
    def _generate_html(self):
        """Generate index.html"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KRWL HOF - Community Events</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body>
    <div id="app">
        <header>
            <h1>KRWL HOF Community Events</h1>
            <div id="status">
                <span id="location-status">Getting location...</span>
                <span id="event-count">0 events nearby</span>
            </div>
        </header>
        
        <div id="map"></div>
        
        <div id="event-list">
            <h2>Upcoming Events (Until Sunrise)</h2>
            <div id="events-container">
                <p>Loading events...</p>
            </div>
        </div>
        
        <div id="event-detail" class="hidden">
            <div class="detail-content">
                <button id="close-detail">&times;</button>
                <h2 id="detail-title"></h2>
                <p id="detail-description"></p>
                <div id="detail-info">
                    <p><strong>Location:</strong> <span id="detail-location"></span></p>
                    <p><strong>Time:</strong> <span id="detail-time"></span></p>
                    <p><strong>Distance:</strong> <span id="detail-distance"></span></p>
                </div>
                <a id="detail-link" href="#" target="_blank">More Info</a>
            </div>
        </div>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
'''
        
        html_path = self.static_path / 'index.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
            
    def _generate_css(self):
        """Generate style.css"""
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: #1a1a1a;
    color: #ffffff;
    overflow: hidden;
}

#app {
    height: 100vh;
    display: flex;
    flex-direction: column;
}

header {
    background: #2d2d2d;
    padding: 1rem 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    z-index: 1000;
}

header h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

#status {
    display: flex;
    gap: 2rem;
    font-size: 0.9rem;
    color: #aaa;
}

#status span {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

#map {
    flex: 1;
    position: relative;
    z-index: 1;
}

#event-list {
    position: fixed;
    right: 0;
    top: 100px;
    bottom: 0;
    width: 350px;
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    overflow-y: auto;
    box-shadow: -5px 0 20px rgba(0, 0, 0, 0.3);
    z-index: 999;
}

#event-list h2 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #fff;
}

.event-card {
    background: rgba(45, 45, 45, 0.9);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    border-left: 3px solid #4CAF50;
}

.event-card:hover {
    transform: translateX(-5px);
    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.event-card h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: #4CAF50;
}

.event-card p {
    font-size: 0.85rem;
    color: #ccc;
    margin-bottom: 0.3rem;
}

.event-card .distance {
    color: #888;
    font-size: 0.8rem;
}

#event-detail {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

#event-detail.hidden {
    display: none;
}

.detail-content {
    background: #2d2d2d;
    border-radius: 12px;
    padding: 2rem;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
}

#close-detail {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    color: #fff;
    font-size: 2rem;
    cursor: pointer;
    line-height: 1;
}

#close-detail:hover {
    color: #4CAF50;
}

.detail-content h2 {
    margin-bottom: 1rem;
    color: #4CAF50;
}

.detail-content p {
    line-height: 1.6;
    margin-bottom: 1rem;
}

#detail-info {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

#detail-link {
    display: inline-block;
    background: #4CAF50;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    text-decoration: none;
    transition: background 0.2s;
}

#detail-link:hover {
    background: #45a049;
}

/* Leaflet customization */
.leaflet-popup-content-wrapper {
    background: #2d2d2d;
    color: white;
}

.leaflet-popup-tip {
    background: #2d2d2d;
}

/* Custom marker */
.event-marker {
    background: #4CAF50;
    border: 3px solid white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}

::-webkit-scrollbar-thumb {
    background: #4CAF50;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #45a049;
}

@media (max-width: 768px) {
    #event-list {
        width: 100%;
        top: auto;
        bottom: 0;
        height: 40vh;
    }
    
    #map {
        height: 60vh;
    }
}
'''
        
        css_path = self.static_path / 'css' / 'style.css'
        with open(css_path, 'w') as f:
            f.write(css_content)
            
    def _generate_js(self):
        """Generate app.js"""
        js_content = '''// KRWL HOF Community Events App
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
        
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
                    statusEl.textContent = '⚠️ Location unavailable';
                    
                    // Still display events, but without distance filtering
                    this.displayEvents();
                }
            );
        } else {
            statusEl.textContent = '⚠️ Geolocation not supported';
            this.displayEvents();
        }
    }
    
    async loadEvents() {
        try {
            const response = await fetch('events.json');
            const data = await response.json();
            this.events = data.events || [];
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
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
        const nextSunrise = this.getNextSunrise();
        const maxDistance = this.config.filtering.max_distance_km;
        
        return this.events.filter(event => {
            // Filter by time (until next sunrise)
            const eventTime = new Date(event.start_time);
            if (eventTime > nextSunrise) {
                return false;
            }
            
            // Filter by distance if user location is available
            if (this.userLocation && event.location) {
                const distance = this.calculateDistance(
                    this.userLocation.lat,
                    this.userLocation.lon,
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
    }
    
    displayEvents() {
        const filteredEvents = this.filterEvents();
        const container = document.getElementById('events-container');
        const countEl = document.getElementById('event-count');
        
        // Update count
        countEl.textContent = `${filteredEvents.length} events nearby`;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        if (filteredEvents.length === 0) {
            container.innerHTML = '<p>No upcoming events found nearby.</p>';
            return;
        }
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Display events
        filteredEvents.forEach(event => {
            this.displayEventCard(event, container);
            this.addEventMarker(event);
        });
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
'''
        
        js_path = self.static_path / 'js' / 'app.js'
        with open(js_path, 'w') as f:
            f.write(js_content)
            
    def _copy_data_files(self):
        """Copy data and config files to static directory"""
        import shutil
        
        # Copy events.json
        events_src = self.base_path / 'data' / 'events.json'
        events_dst = self.static_path / 'events.json'
        shutil.copy(events_src, events_dst)
        
        # Copy config.json
        config_src = self.base_path / 'config' / 'config.json'
        config_dst = self.static_path / 'config.json'
        shutil.copy(config_src, config_dst)
