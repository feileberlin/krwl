/**
 * DashboardUI Module
 * 
 * Handles dashboard debug information display:
 * - Git commit information
 * - Deployment time
 * - Event counts
 * - Environment status
 * - File sizes and breakdown
 * - Cache statistics
 * - Duplicate warnings
 * 
 * KISS: Single responsibility - dashboard UI updates
 */

class DashboardUI {
    constructor(config, utils) {
        this.config = config;
        this.utils = utils;
    }
    
    /**
     * Update all dashboard debug information
     * @param {Object} duplicateStats - Statistics about duplicate events
     */
    update(duplicateStats = null) {
        const debugInfo = window.DEBUG_INFO || {};
        
        this.updateGitInfo(debugInfo);
        this.updateDeploymentInfo(debugInfo);
        this.updateEventCounts(debugInfo);
        this.updateEnvironmentInfo(debugInfo);
        this.updateCachingInfo(debugInfo);
        this.updateFileSizeInfo(debugInfo);
        this.updateSizeBreakdown(debugInfo);
        this.updateCacheStatistics();
        this.updateDuplicateWarnings(duplicateStats);
        this.updateCustomLocations();
        this.showDebugSection();
    }
    
    /**
     * Update custom locations display in dashboard
     */
    updateCustomLocations() {
        const container = document.getElementById('custom-locations-list');
        if (!container) return;
        
        // Get storage from global app instance if available
        const app = window.app || window.eventsApp;
        if (!app || !app.storage) {
            container.innerHTML = '<div class="custom-locations-empty">Storage not available</div>';
            return;
        }
        
        const customLocs = app.storage.getCustomLocations();
        
        if (customLocs.length === 0) {
            container.innerHTML = '<div class="custom-locations-empty">No locations saved yet</div>';
            return;
        }
        
        let html = '';
        
        // Show all custom locations (includes initialized predefined locations)
        customLocs.forEach((loc) => {
            const locationLabel = loc.fromPredefined ? 
                `<i data-lucide="map-pin" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;"></i> ${loc.name}` : 
                `<i data-lucide="edit-3" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;"></i> ${loc.name}`;
            
            html += `
                <div class="custom-location-item">
                    <div class="custom-location-header">
                        <div class="custom-location-name">${locationLabel}</div>
                    </div>
                    <div class="custom-location-coords">${loc.lat.toFixed(4)}°, ${loc.lon.toFixed(4)}°</div>
                    <div class="custom-location-actions">
                        <button class="custom-location-btn" data-action="edit" data-id="${loc.id}">Edit</button>
                        <button class="custom-location-btn delete" data-action="delete" data-id="${loc.id}">Delete</button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Initialize Lucide icons for the newly added HTML
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
        
        // Attach event listeners to action buttons
        container.querySelectorAll('.custom-location-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.getAttribute('data-action');
                const id = btn.getAttribute('data-id');
                
                if (action === 'edit') {
                    this.editCustomLocation(id, app);
                } else if (action === 'delete') {
                    this.deleteCustomLocation(id, app);
                }
            });
        });
    }
    
    /**
     * Edit a custom location
     * @param {string} id - Location ID
     * @param {Object} app - App instance
     */
    editCustomLocation(id, app) {
        const loc = app.storage.getCustomLocationById(id);
        if (!loc) return;
        
        const newName = prompt('Enter new name:', loc.name);
        if (!newName || !newName.trim()) return;
        
        const newLatStr = prompt('Enter new latitude:', loc.lat.toString());
        const newLonStr = prompt('Enter new longitude:', loc.lon.toString());
        
        const newLat = parseFloat(newLatStr);
        const newLon = parseFloat(newLonStr);
        
        if (isNaN(newLat) || isNaN(newLon)) {
            alert('Invalid coordinates!');
            return;
        }
        
        const success = app.storage.updateCustomLocation(id, {
            name: newName.trim(),
            lat: newLat,
            lon: newLon
        });
        
        if (success) {
            alert('✅ Location updated!');
            this.updateCustomLocations();
            // Refresh the location dropdown
            if (app.eventListeners) {
                app.eventListeners.setupFilterListeners();
            }
        }
    }
    
    /**
     * Delete a custom location
     * @param {string} id - Location ID
     * @param {Object} app - App instance
     */
    deleteCustomLocation(id, app) {
        const loc = app.storage.getCustomLocationById(id);
        if (!loc) return;
        
        if (!confirm(`Delete "${loc.name}"?`)) {
            return;
        }
        
        const success = app.storage.deleteCustomLocation(id);
        if (success) {
            alert('✅ Location deleted!');
            this.updateCustomLocations();
            // Refresh the location dropdown
            if (app.eventListeners) {
                app.eventListeners.setupFilterListeners();
            }
        }
    }
    
    updateGitInfo(debugInfo) {
        if (!debugInfo.git_commit) return;
        
        const git = debugInfo.git_commit;
        this.setElementText('debug-commit-hash', git.hash || 'unknown');
        this.setElementText('debug-commit-author', git.author || 'unknown');
        this.setElementText('debug-commit-date', git.date || 'unknown');
        
        const commitMessage = document.getElementById('debug-commit-message');
        if (commitMessage) {
            commitMessage.textContent = git.message || 'unknown';
            commitMessage.title = git.message || 'No commit message';
        }
    }
    
    updateDeploymentInfo(debugInfo) {
        const deploymentTime = document.getElementById('debug-deployment-time');
        if (!deploymentTime || !debugInfo.deployment_time) return;
        
        try {
            const date = new Date(debugInfo.deployment_time);
            deploymentTime.textContent = date.toLocaleString();
            deploymentTime.title = `Deployment timestamp: ${debugInfo.deployment_time}`;
        } catch (e) {
            deploymentTime.textContent = debugInfo.deployment_time;
        }
    }
    
    updateEventCounts(debugInfo) {
        if (!debugInfo.event_counts) return;
        
        const counts = debugInfo.event_counts;
        this.setElementText('debug-event-counts-published', counts.published || 0);
        this.setElementText('debug-event-counts-pending', counts.pending || 0);
        this.setElementText('debug-event-counts-archived', counts.archived || 0);
        this.setElementText('debug-event-counts-total', counts.total || 0);
    }
    
    updateEnvironmentInfo(debugInfo) {
        const debugEnvironment = document.getElementById('debug-environment');
        if (!debugEnvironment) return;
        
        const environment = debugInfo.environment || 
                          this.config?.watermark?.text || 
                          this.config?.app?.environment || 
                          'UNKNOWN';
        
        debugEnvironment.textContent = environment.toUpperCase();
        debugEnvironment.className = 'debug-env-badge';
        
        const envLower = environment.toLowerCase();
        if (envLower.includes('dev')) {
            debugEnvironment.classList.add('env-dev');
        } else if (envLower.includes('production')) {
            debugEnvironment.classList.add('env-production');
        } else if (envLower.includes('ci')) {
            debugEnvironment.classList.add('env-ci');
        }
    }
    
    updateCachingInfo(debugInfo) {
        const debugCaching = document.getElementById('debug-caching');
        if (!debugCaching) return;
        
        const cacheEnabled = debugInfo.cache_enabled;
        if (cacheEnabled !== undefined) {
            debugCaching.textContent = cacheEnabled ? 'Enabled' : 'Disabled';
            debugCaching.className = cacheEnabled ? 'cache-enabled' : 'cache-disabled';
        } else {
            debugCaching.textContent = 'Unknown';
        }
    }
    
    updateFileSizeInfo(debugInfo) {
        const debugFileSize = document.getElementById('debug-file-size');
        if (!debugFileSize || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const totalKB = (sizes.total / 1024).toFixed(1);
        
        if (debugInfo.cache_enabled && debugInfo.cache_file_size) {
            const cacheKB = (debugInfo.cache_file_size / 1024).toFixed(1);
            debugFileSize.textContent = `${totalKB} KB (HTML) | ${cacheKB} KB (Cache)`;
            debugFileSize.title = `Cache file: ${debugInfo.cache_file_path || 'unknown'}`;
        } else {
            debugFileSize.textContent = `${totalKB} KB (HTML only)`;
            if (!debugInfo.cache_enabled) {
                debugFileSize.title = 'Caching disabled - showing HTML size only';
            }
        }
    }
    
    updateSizeBreakdown(debugInfo) {
        const debugSizeBreakdown = document.getElementById('debug-size-breakdown');
        if (!debugSizeBreakdown || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const components = [
            { name: 'Events', size: sizes.events_data },
            { name: 'Scripts', size: sizes.scripts },
            { name: 'Styles', size: sizes.stylesheets },
            { name: 'Translations', size: sizes.translations },
            { name: 'Markers', size: sizes.marker_icons },
            { name: 'Other', size: sizes.other }
        ];
        
        components.sort((a, b) => b.size - a.size);
        
        // Show top 3
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
    
    updateCacheStatistics() {
        const debugDOMCache = document.getElementById('debug-dom-cache');
        if (debugDOMCache && this.utils) {
            const cacheSize = Object.keys(this.utils.domCache || {}).length;
            const cacheStatus = cacheSize > 0 ? `${cacheSize} elements cached` : 'No elements cached';
            debugDOMCache.textContent = cacheStatus;
            debugDOMCache.title = `DOM elements cached: ${Object.keys(this.utils.domCache || {}).join(', ') || 'none'}`;
        }
        
        const debugHistoricalCache = document.getElementById('debug-historical-cache');
        if (debugHistoricalCache) {
            debugHistoricalCache.textContent = 'Backend (Python)';
            debugHistoricalCache.title = 'Historical events are cached in the backend during scraping to improve performance';
        }
    }
    
    updateDuplicateWarnings(duplicateStats) {
        const duplicatesContainer = document.getElementById('debug-duplicates-container');
        if (!duplicatesContainer) return;
        
        if (!duplicateStats || duplicateStats.total === 0) {
            duplicatesContainer.style.display = 'none';
            return;
        }
        
        duplicatesContainer.style.display = 'block';
        
        this.setElementText('debug-duplicates-count', duplicateStats.total);
        this.setElementText('debug-duplicates-events', duplicateStats.events);
        
        const detailsList = document.getElementById('debug-duplicates-details');
        if (detailsList && duplicateStats.details) {
            let html = '<ul>';
            duplicateStats.details.forEach(d => {
                html += `<li><strong>${d.title.substring(0, 40)}...</strong>: ${d.count} duplicates</li>`;
            });
            html += '</ul>';
            detailsList.innerHTML = html;
        }
    }
    
    showDebugSection() {
        const debugSection = document.getElementById('dashboard-debug-section');
        if (debugSection && debugSection.style.display === 'none') {
            debugSection.style.display = 'block';
        }
    }
    
    /**
     * Helper to set element text content safely
     * @param {string} id - Element ID
     * @param {string|number} text - Text content to set
     */
    setElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardUI;
}
