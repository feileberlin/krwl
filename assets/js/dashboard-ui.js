/**
 * DashboardUI Module - Reorganized Debug Cockpit
 * 
 * Handles dashboard debug information display with improved structure:
 * - Deployment info (git commit, environment, deployment time)
 * - Data & Performance (events, caching, file size, DOM cache)
 * - Warnings (duplicates, unpublished events)
 * 
 * KISS: Single responsibility - dashboard UI updates with clean structure
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
        
        // Deployment section
        this.updateGitInfo(debugInfo);
        this.updateDeploymentTime(debugInfo);
        this.updateEnvironmentInfo(debugInfo);
        
        // Data & Performance section
        this.updateEventCounts(debugInfo);
        this.updateFileSizeInfo(debugInfo);
        this.updateCachingInfo(debugInfo);
        this.updateDOMCacheInfo();
        this.updateSizeBreakdown(debugInfo);
        this.updateCacheStatistics();  // Cache & compression statistics
        this.updateDuplicateWarnings(duplicateStats);
        this.updateCustomLocations();
        
        // Lint Warnings section (WCAG AA compliance)
        this.updateLintWarnings(debugInfo);
        
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
        
        // Show/hide Add Location button based on max limit (2 locations)
        const addButton = document.getElementById('add-custom-location-btn');
        if (addButton) {
            if (customLocs.length >= 2) {
                addButton.style.display = 'none';
            } else {
                addButton.style.display = 'block';
            }
        }
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
            commitMessage.textContent = git.message || 'No commit message';
            commitMessage.title = git.message || 'No commit message';
        }
    }
    
    updateDeploymentTime(debugInfo) {
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
    
    updateEnvironmentInfo(debugInfo) {
        const debugEnvironment = document.getElementById('debug-environment');
        if (!debugEnvironment) return;
        
        const environment = debugInfo.environment || 
                          this.config?.watermark?.text || 
                          this.config?.app?.environment || 
                          'UNKNOWN';
        
        debugEnvironment.textContent = environment.toUpperCase();
        debugEnvironment.className = 'debug-value debug-env-badge';
        
        const envLower = environment.toLowerCase();
        if (envLower.includes('dev')) {
            debugEnvironment.classList.add('env-dev');
        } else if (envLower.includes('production')) {
            debugEnvironment.classList.add('env-production');
        } else if (envLower.includes('ci')) {
            debugEnvironment.classList.add('env-ci');
        }
    }
    
    updateEventCounts(debugInfo) {
        if (!debugInfo.event_counts) return;
        
        const counts = debugInfo.event_counts;
        this.setElementText('debug-event-counts-published', counts.published || 0);
        this.setElementText('debug-event-counts-pending', counts.pending || 0);
        this.setElementText('debug-event-counts-archived', counts.archived || 0);
    }
    
    updateFileSizeInfo(debugInfo) {
        const debugFileSize = document.getElementById('debug-file-size');
        if (!debugFileSize || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const totalKB = (sizes.total / 1024).toFixed(1);
        debugFileSize.textContent = `${totalKB} KB`;
        
        if (debugInfo.cache_enabled && debugInfo.cache_file_size) {
            const cacheKB = (debugInfo.cache_file_size / 1024).toFixed(1);
            debugFileSize.title = `HTML: ${totalKB} KB, Cache: ${cacheKB} KB`;
        }
    }
    
    updateCachingInfo(debugInfo) {
        const debugCaching = document.getElementById('debug-caching');
        if (!debugCaching) return;
        
        const cacheEnabled = debugInfo.cache_enabled;
        if (cacheEnabled !== undefined) {
            debugCaching.textContent = cacheEnabled ? 'Enabled' : 'Disabled';
            debugCaching.className = cacheEnabled ? 'debug-value cache-enabled' : 'debug-value cache-disabled';
        } else {
            debugCaching.textContent = 'Unknown';
            debugCaching.className = 'debug-value';
        }
    }
    
    updateDOMCacheInfo() {
        const debugDOMCache = document.getElementById('debug-dom-cache');
        if (debugDOMCache && this.utils) {
            const cacheSize = Object.keys(this.utils.domCache || {}).length;
            debugDOMCache.textContent = `${cacheSize} elements`;
            debugDOMCache.title = `DOM elements cached: ${Object.keys(this.utils.domCache || {}).join(', ') || 'none'}`;
        }
    }
    
    updateCacheStatistics() {
        /**
         * Update cache statistics for production mode
         * Shows:
         * - Cache hit/miss rates
         * - Compression ratios
         * - Cache file sizes
         */
        const debugInfo = window.DEBUG_INFO || {};
        
        // Check if we have cache statistics
        if (!debugInfo.cache_enabled) {
            return; // No cache statistics to show in development mode
        }
        
        // Update cache file size if available
        if (debugInfo.cache_file_size) {
            const debugFileSize = document.getElementById('debug-file-size');
            if (debugFileSize) {
                const cacheKB = (debugInfo.cache_file_size / 1024).toFixed(1);
                const htmlKB = debugInfo.html_sizes ? (debugInfo.html_sizes.total / 1024).toFixed(1) : '?';
                debugFileSize.title = `HTML: ${htmlKB} KB, Cache: ${cacheKB} KB`;
            }
        }
        
        // Update compression info if available
        if (debugInfo.compression) {
            const comp = debugInfo.compression;
            
            // Show compression ratio in title/tooltip
            const debugCaching = document.getElementById('debug-caching');
            if (debugCaching && comp.ratio) {
                const ratio = (comp.ratio * 100).toFixed(1);
                debugCaching.title = `Compression: ${ratio}% reduction (${comp.original_kb || '?'} KB → ${comp.compressed_kb || '?'} KB)`;
            }
        }
        
        // Log cache statistics for debugging (only in debug mode)
        if (this.config && this.config.debug) {
            console.log('[KRWL Debug] Cache Statistics:', {
                enabled: debugInfo.cache_enabled,
                file_size: debugInfo.cache_file_size,
                compression: debugInfo.compression
            });
        }
    }
    
    updateSizeBreakdown(debugInfo) {
        const debugSizeBreakdown = document.getElementById('debug-size-breakdown');
        if (!debugSizeBreakdown || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const components = [
            { name: 'Events Data', size: sizes.events_data },
            { name: 'Scripts', size: sizes.scripts },
            { name: 'Styles', size: sizes.stylesheets },
            { name: 'Translations', size: sizes.translations },
            { name: 'Markers', size: sizes.marker_icons },
            { name: 'Other', size: sizes.other }
        ];
        
        components.sort((a, b) => b.size - a.size);
        
        let breakdownHTML = '<ul class="debug-size-list">';
        components.forEach(comp => {
            const kb = (comp.size / 1024).toFixed(1);
            const percent = ((comp.size / sizes.total) * 100).toFixed(1);
            breakdownHTML += `<li>${comp.name}: ${kb} KB (${percent}%)</li>`;
        });
        breakdownHTML += '</ul>';
        
        debugSizeBreakdown.innerHTML = breakdownHTML;
    }
    
    updateWarnings(duplicateStats) {
        const warningsContainer = document.getElementById('debug-warnings-container');
        const duplicateWarnings = document.getElementById('debug-duplicate-warnings');
        const unpublishedWarnings = document.getElementById('debug-unpublished-warnings');
        
        let hasWarnings = false;
        
        // Update duplicate warnings
        if (duplicateStats && duplicateStats.total > 0) {
            hasWarnings = true;
            this.updateDuplicateWarnings(duplicateStats, duplicateWarnings);
        } else if (duplicateWarnings) {
            duplicateWarnings.style.display = 'none';
        }
        
        // Check if unpublished warnings exist (populated by app.js)
        if (unpublishedWarnings && unpublishedWarnings.style.display !== 'none') {
            hasWarnings = true;
        }
        
        // Show/hide warnings container
        if (warningsContainer) {
            warningsContainer.style.display = hasWarnings ? 'block' : 'none';
        }
    }
    
    updateDuplicateWarnings(duplicateStats, warningElement) {
        if (!warningElement) return;
        
        warningElement.style.display = 'block';
        
        const stats = duplicateStats;
        const warningMessage = `⚠️ ${stats.total} duplicate event${stats.total > 1 ? 's' : ''} found across ${stats.events} event${stats.events > 1 ? 's' : ''}`;
        
        let detailsHTML = '';
        const displayLimit = 5;
        stats.details.slice(0, displayLimit).forEach(d => {
            const shortTitle = d.title.length > 40 ? d.title.substring(0, 40) + '...' : d.title;
            detailsHTML += `<li><strong>${shortTitle}</strong>: ${d.count} duplicates</li>`;
        });
        
        const moreText = stats.details.length > displayLimit ? `<li>...and ${stats.details.length - displayLimit} more</li>` : '';
        
        warningElement.innerHTML = `
            <div class="debug-duplicate-warning-header">${warningMessage}</div>
            <ul class="debug-duplicate-list">
                ${detailsHTML}
                ${moreText}
            </ul>
        `;
    }
    
    showDebugSection() {
        const debugSection = document.getElementById('dashboard-debug-section');
        if (debugSection && debugSection.style.display === 'none') {
            debugSection.style.display = 'block';
        }
    }
    
    /**
     * Update lint warnings section with WCAG AA compliance results
     * Show summary with link to protocol file instead of detailed list
     * @param {Object} debugInfo - Debug info object containing lint_results
     */
    updateLintWarnings(debugInfo) {
        if (!debugInfo || !debugInfo.lint_results) return;
        
        const container = document.getElementById('debug-lint-warnings-container');
        const summary = document.getElementById('debug-lint-summary');
        const warningsList = document.getElementById('debug-lint-warnings-list');
        
        if (!container || !summary || !warningsList) return;
        
        const lintResults = debugInfo.lint_results;
        const warnings = lintResults.structured_warnings || [];
        
        // Show container if there are warnings
        if (warnings.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'block';
        
        // Show summary with link to protocol file (no detailed list)
        const errorCount = lintResults.error_count || 0;
        const warningCount = lintResults.warning_count || 0;
        
        summary.innerHTML = `
            <strong>${warningCount} accessibility ${warningCount === 1 ? 'warning' : 'warnings'}</strong>
            ${errorCount > 0 ? ` · ${errorCount} ${errorCount === 1 ? 'error' : 'errors'}` : ''}
            <br>
            <span style="font-size: 0.85em; color: var(--color-text-tertiary); margin-top: 0.5rem; display: block;">
                For details, see 
                <a href="wcag_protocol.txt" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   style="color: var(--color-primary); text-decoration: underline;">
                    wcag_protocol.txt
                </a>
            </span>
        `;
        
        // Hide the warnings list (no detailed display)
        warningsList.style.display = 'none';
    }
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} unsafe - Unsafe string
     * @returns {string} - Escaped string
     */
    escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        return unsafe
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
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
