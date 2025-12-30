/* Leaflet JS placeholder for local testing */
/* In production, this file is downloaded by the deployment workflow using manage_libs.py */
/* This is a minimal mock to prevent errors during development without network access */

// Minimal Leaflet mock for development
(function() {
    'use strict';
    
    // Create minimal Leaflet object to prevent errors
    window.L = {
        version: '1.9.4-mock',
        
        map: function(id, options) {
            console.log('[Leaflet Mock] Map created for element:', id);
            return {
                setView: function(latlng, zoom) {
                    console.log('[Leaflet Mock] setView:', latlng, zoom);
                    return this;
                },
                fitBounds: function(bounds, options) {
                    console.log('[Leaflet Mock] fitBounds:', bounds, options);
                    return this;
                }
            };
        },
        
        tileLayer: function(url, options) {
            console.log('[Leaflet Mock] Tile layer created:', url);
            return {
                addTo: function(map) {
                    console.log('[Leaflet Mock] Tile layer added to map');
                    return this;
                }
            };
        },
        
        marker: function(latlng, options) {
            console.log('[Leaflet Mock] Marker created at:', latlng);
            return {
                addTo: function(map) {
                    console.log('[Leaflet Mock] Marker added to map');
                    return this;
                },
                bindPopup: function(content) {
                    console.log('[Leaflet Mock] Popup bound:', content);
                    return this;
                },
                getLatLng: function() {
                    return latlng;
                },
                remove: function() {
                    console.log('[Leaflet Mock] Marker removed');
                }
            };
        },
        
        icon: function(options) {
            console.log('[Leaflet Mock] Icon created:', options);
            return options;
        },
        
        latLngBounds: function() {
            const bounds = [];
            return {
                extend: function(latlng) {
                    bounds.push(latlng);
                    console.log('[Leaflet Mock] Bounds extended:', latlng);
                }
            };
        }
    };
    
    console.log('[Leaflet Mock] Loaded - This is a placeholder for development');
    console.log('[Leaflet Mock] In production, the real Leaflet library is downloaded by the deployment workflow');
})();
