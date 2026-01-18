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
        
        // Show all custom locations with appropriate buttons
        customLocs.forEach((loc) => {
            const iconType = loc.fromPredefined ? 'map-pin' : 'edit-3';
            
            // Show different buttons based on whether it's predefined or user-created
            let actionButtons;
            if (loc.fromPredefined) {
                // For predefined locations: always show Edit, only show Reset if modified
                const isModified = app.storage.isPredefinedLocationModified(loc.id);
                actionButtons = isModified ? `
                    <button class="custom-location-btn custom-location-btn--edit" data-action="edit" data-id="${loc.id}" title="Edit location">
                        <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
                        <span>Edit</span>
                    </button>
                    <button class="custom-location-btn custom-location-btn--reset" data-action="reset" data-id="${loc.id}" title="Reset to config.json values">
                        <i data-lucide="rotate-ccw" style="width: 14px; height: 14px;"></i>
                        <span>Reset</span>
                    </button>
                ` : `
                    <button class="custom-location-btn custom-location-btn--edit" data-action="edit" data-id="${loc.id}" title="Edit location">
                        <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
                        <span>Edit</span>
                    </button>
                `;
            } else {
                // For user-created locations: show Edit and Delete
                actionButtons = `
                    <button class="custom-location-btn custom-location-btn--edit" data-action="edit" data-id="${loc.id}" title="Edit location">
                        <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
                        <span>Edit</span>
                    </button>
                    <button class="custom-location-btn custom-location-btn--delete" data-action="delete" data-id="${loc.id}" title="Delete location">
                        <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                        <span>Delete</span>
                    </button>
                `;
            }
            
            html += `
                <div class="custom-location-item" data-location-id="${loc.id}">
                    <!-- View State -->
                    <div class="custom-location-view">
                        <div class="custom-location-header">
                            <div class="custom-location-actions">
                                ${actionButtons}
                            </div>
                            <div class="custom-location-name">
                                <i data-lucide="${iconType}" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;"></i>
                                <span class="location-name-text">${loc.name}</span>
                            </div>
                        </div>
                        <div class="custom-location-coords custom-location-coords--clickable" data-location-id="${loc.id}" tabindex="0" role="button" aria-label="Click to edit coordinates">${loc.lat.toFixed(4)}°, ${loc.lon.toFixed(4)}°</div>
                    </div>
                    
                    <!-- Edit State (hidden by default) - Same structure as view state -->
                    <div class="custom-location-edit" style="display: none;">
                        <div class="custom-location-header">
                            <div class="custom-location-actions">
                                <!-- Empty - maintains same structure as view -->
                            </div>
                            <div class="custom-location-name">
                                <i data-lucide="${iconType}" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;"></i>
                                <span class="location-name-text">${loc.name}</span>
                            </div>
                        </div>
                        <div class="custom-location-coords-edit">
                            <input type="text" 
                                   id="edit-lat-${loc.id}" 
                                   class="custom-location-input custom-location-input--coordinate custom-location-input--inline" 
                                   value="${loc.lat.toFixed(4)}" 
                                   placeholder="Latitude"
                                   pattern="^-?\\d+\\.\\d{4}$"
                                   data-type="latitude"
                                   aria-label="Latitude">°, 
                            <input type="text" 
                                   id="edit-lon-${loc.id}" 
                                   class="custom-location-input custom-location-input--coordinate custom-location-input--inline" 
                                   value="${loc.lon.toFixed(4)}" 
                                   placeholder="Longitude"
                                   pattern="^-?\\d+\\.\\d{4}$"
                                   data-type="longitude"
                                   aria-label="Longitude">°
                            <button class="custom-location-btn custom-location-btn--save custom-location-btn--inline" data-action="save" data-id="${loc.id}" title="Save changes">
                                <i data-lucide="check" style="width: 14px; height: 14px;"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Initialize Lucide icons for the newly added HTML
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
        
        // Attach click/focus handlers to coordinates for inline editing
        container.querySelectorAll('.custom-location-coords--clickable').forEach(coordElement => {
            const id = coordElement.getAttribute('data-location-id');
            
            // Click handler
            coordElement.addEventListener('click', () => {
                this.toggleEditMode(id, true);
            });
            
            // Keyboard handler (Enter/Space)
            coordElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleEditMode(id, true);
                }
            });
        });
        
        // Attach input validation to coordinate inputs
        container.querySelectorAll('.custom-location-input--coordinate').forEach(input => {
            // Format value on blur to ensure exactly 4 decimal places
            input.addEventListener('blur', (e) => {
                const value = e.target.value.trim();
                const type = e.target.getAttribute('data-type');
                
                // Try to parse as number
                const num = parseFloat(value);
                if (!isNaN(num)) {
                    // Validate range
                    if (type === 'latitude' && (num < -90 || num > 90)) {
                        this.showValidationError(e.target, 'Latitude must be between -90 and 90');
                        return;
                    }
                    if (type === 'longitude' && (num < -180 || num > 180)) {
                        this.showValidationError(e.target, 'Longitude must be between -180 and 180');
                        return;
                    }
                    
                    // Format to exactly 4 decimal places
                    e.target.value = num.toFixed(4);
                }
            });
            
            // Validate input in real-time
            input.addEventListener('input', (e) => {
                let value = e.target.value;
                
                // Allow: digits, minus sign (at start), and one decimal point
                // Remove any characters that aren't digits, minus, or decimal
                value = value.replace(/[^\d.-]/g, '');
                
                // Ensure minus is only at the start
                if (value.indexOf('-') > 0) {
                    value = value.replace(/-/g, '');
                }
                
                // Ensure only one decimal point
                const parts = value.split('.');
                if (parts.length > 2) {
                    value = parts[0] + '.' + parts.slice(1).join('');
                }
                
                // Limit to 4 decimal places
                if (parts.length === 2 && parts[1].length > 4) {
                    value = parts[0] + '.' + parts[1].substring(0, 4);
                }
                
                e.target.value = value;
            });
        });
        
        // Attach event listeners to all action buttons
        container.querySelectorAll('.custom-location-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.getAttribute('data-action');
                const id = btn.getAttribute('data-id');
                
                if (action === 'edit') {
                    this.toggleEditMode(id, true);
                } else if (action === 'save') {
                    this.saveCustomLocation(id, app);
                } else if (action === 'cancel') {
                    this.toggleEditMode(id, false);
                } else if (action === 'reset') {
                    this.resetCustomLocation(id, app);
                } else if (action === 'delete') {
                    this.deleteCustomLocation(id, app);
                }
            });
        });
    }
    
    /**
     * Toggle edit mode for a custom location
     * @param {string} id - Location ID
     * @param {boolean} enabled - Whether to enable edit mode
     */
    toggleEditMode(id, enabled) {
        const item = document.querySelector(`.custom-location-item[data-location-id="${id}"]`);
        if (!item) return;
        
        const viewState = item.querySelector('.custom-location-view');
        const editState = item.querySelector('.custom-location-edit');
        
        if (enabled) {
            // Enter edit mode
            viewState.style.display = 'none';
            editState.style.display = 'block';
            
            // Focus on the latitude input (first coordinate input)
            const latInput = editState.querySelector(`#edit-lat-${id}`);
            if (latInput) {
                setTimeout(() => latInput.focus(), 50);
            }
            
            // Add ESC key listener to exit edit mode (use capture phase to intercept before dashboard handler)
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    e.stopPropagation(); // Prevent dashboard from closing
                    e.preventDefault(); // Prevent default behavior
                    this.toggleEditMode(id, false);
                    document.removeEventListener('keydown', escHandler, true);
                }
            };
            // Use capture phase (true) to intercept before other handlers
            document.addEventListener('keydown', escHandler, true);
            // Store handler for cleanup
            editState.dataset.escHandler = 'attached';
        } else {
            // Exit edit mode (restore original values)
            viewState.style.display = 'block';
            editState.style.display = 'none';
            
            // Reset form values to original
            const app = window.app || window.eventsApp;
            if (app && app.storage) {
                const loc = app.storage.getCustomLocationById(id);
                if (loc) {
                    const latInput = editState.querySelector(`#edit-lat-${id}`);
                    const lonInput = editState.querySelector(`#edit-lon-${id}`);
                    
                    if (latInput) latInput.value = loc.lat.toFixed(4);
                    if (lonInput) lonInput.value = loc.lon.toFixed(4);
                }
            }
        }
    }
    
    /**
     * Save changes to a custom location
     * @param {string} id - Location ID
     * @param {Object} app - App instance
     */
    saveCustomLocation(id, app) {
        const item = document.querySelector(`.custom-location-item[data-location-id="${id}"]`);
        if (!item) return;
        
        const editState = item.querySelector('.custom-location-edit');
        const latInput = editState.querySelector(`#edit-lat-${id}`);
        const lonInput = editState.querySelector(`#edit-lon-${id}`);
        
        if (!latInput || !lonInput) return;
        
        // Get current location to check if it's predefined
        const currentLoc = app.storage.getCustomLocationById(id);
        if (!currentLoc) return;
        
        // Get values - name stays the same, only coordinates change
        let newName = currentLoc.name;
        let latValue = latInput.value.trim();
        let lonValue = lonInput.value.trim();
        
        // Validate decimal format (exactly 4 decimal places)
        const decimalRegex = /^-?\d+\.\d{4}$/;
        if (!decimalRegex.test(latValue)) {
            this.showValidationError(latInput, 'Latitude must have exactly 4 decimal places (e.g., 50.3081)');
            return;
        }
        if (!decimalRegex.test(lonValue)) {
            this.showValidationError(lonInput, 'Longitude must have exactly 4 decimal places (e.g., 11.9233)');
            return;
        }
        
        let newLat = parseFloat(latValue);
        let newLon = parseFloat(lonValue);
        
        // Handle empty fields for predefined locations - revert to config.json values
        if (currentLoc.fromPredefined) {
            const originalLoc = app.storage.getOriginalPredefinedLocation(id);
            
            if (originalLoc) {
                // If lat is empty or invalid, use original predefined lat
                if (isNaN(newLat) || latInput.value.trim() === '') {
                    newLat = originalLoc.lat;
                }
                
                // If lon is empty or invalid, use original predefined lon
                if (isNaN(newLon) || lonInput.value.trim() === '') {
                    newLon = originalLoc.lon;
                }
            }
        }
        
        // Validate (after applying defaults for predefined locations)
        
        if (isNaN(newLat) || newLat < -90 || newLat > 90) {
            this.showValidationError(latInput, 'Invalid latitude (must be between -90 and 90)');
            return;
        }
        
        if (isNaN(newLon) || newLon < -180 || newLon > 180) {
            this.showValidationError(lonInput, 'Invalid longitude (must be between -180 and 180)');
            return;
        }
        
        // Update storage
        const success = app.storage.updateCustomLocation(id, {
            name: newName,
            lat: newLat,
            lon: newLon
        });
        
        if (success) {
            // Exit edit mode and refresh display
            this.updateCustomLocations();
            
            // Refresh the location dropdown
            if (app.eventListeners) {
                app.eventListeners.setupFilterListeners();
            }
            
            // Show success feedback
            this.showSaveSuccess(item);
        } else {
            this.showValidationError(nameInput, 'Failed to save location');
        }
    }
    
    /**
     * Show validation error on an input field
     * @param {HTMLElement} input - Input element
     * @param {string} message - Error message
     */
    showValidationError(input, message) {
        // Add error class
        input.classList.add('input-error');
        
        // Create or update error message
        let errorEl = input.parentElement.querySelector('.error-message');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'error-message';
            input.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
        
        // Focus the input
        input.focus();
        
        // Remove error after 3 seconds
        setTimeout(() => {
            input.classList.remove('input-error');
            if (errorEl) errorEl.remove();
        }, 3000);
    }
    
    /**
     * Show save success feedback
     * @param {HTMLElement} item - Location item element
     */
    showSaveSuccess(item) {
        // Add success class temporarily
        item.classList.add('save-success');
        
        // Remove after animation
        setTimeout(() => {
            item.classList.remove('save-success');
        }, 1000);
    }
    
    /**
     * Reset a predefined custom location to its original config.json values
     * @param {string} id - Location ID
     * @param {Object} app - App instance
     */
    resetCustomLocation(id, app) {
        const loc = app.storage.getCustomLocationById(id);
        if (!loc) return;
        
        if (!confirm(`Reset "${loc.name}" to its original config.json values?`)) {
            return;
        }
        
        const success = app.storage.resetCustomLocation(id);
        
        if (success) {
            alert('✅ Location reset to original values!');
            this.updateCustomLocations();
            // Refresh the location dropdown
            if (app.eventListeners) {
                app.eventListeners.setupFilterListeners();
            }
        } else {
            alert('❌ Failed to reset location. It may not be a predefined location.');
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
        
        if (!confirm(`Delete custom location "${loc.name}"?`)) {
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
        } else {
            alert('❌ Failed to delete location.');
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
            <span class="debug-lint-details">
                For details, see 
                <a href="wcag_protocol.txt" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   class="debug-lint-details-link">
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
