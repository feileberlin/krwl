/**
 * EventListeners Module
 * 
 * Handles all UI event listeners:
 * - Dashboard menu interactions
 * - Filter dropdowns and controls
 * - Keyboard shortcuts
 * - Focus management
 * 
 * KISS: Single responsibility - event listener setup only
 * Note: This is still large (812 lines) due to tight coupling in original code
 */

class EventListeners {
    constructor(app) {
        this.app = app;
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
         else {
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
                
                // Build category options with dynamic counts under current filter conditions
                const categoryCounts = this.countCategoriesUnderFilters();
                
                // Calculate total count for "All Categories"
                const totalCount = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
                
                // Build dropdown items HTML with current selection at top
                let dropdownHTML = '';
                
                // Current selection at top (highlighted)
                if (this.filters.category === 'all') {
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item current-selection" data-value="all">
                            <span class="item-label">${totalCount} event${totalCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                } else {
                    const currentCount = categoryCounts[this.filters.category] || 0;
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item current-selection" data-value="${this.filters.category}">
                            <span class="item-label">${currentCount} ${this.filters.category} event${currentCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                }
                
                // Other options with predictive counts
                // Add "All events" option if not currently selected
                if (this.filters.category !== 'all') {
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item" data-value="all">
                            <span class="item-label">${totalCount} event${totalCount !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                }
                
                // Sort categories alphabetically for consistent display
                const sortedCategories = Object.keys(categoryCounts).sort();
                
                sortedCategories.forEach(cat => {
                    // Skip current selection (already shown at top)
                    if (cat === this.filters.category) {
                        return;
                    }
                    
                    const count = categoryCounts[cat];
                    dropdownHTML += `
                        <div class="filter-bar-dropdown-item" data-value="${cat}">
                            <span class="item-label">${count} ${cat} event${count !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                });
                
                const dropdown = createDropdown(dropdownHTML, categoryTextEl);
                
                // Add click listeners to all dropdown items
                dropdown.querySelectorAll('.filter-bar-dropdown-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const value = item.getAttribute('data-value');
                        this.filters.category = value;
                        this.saveFiltersToCookie();
                        this.displayEvents();
                        hideAllDropdowns();
                    });
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
                
                // Note: "All upcoming events" temporarily disabled for performance reasons
                // Loading all events without time limit can cause browser slowdown with large datasets
                const content = `
                    <select id="time-filter">
                        <option value="sunrise">Next Sunrise (6 AM)</option>
                        <option value="sunday-primetime">Till Sunday's Primetime (20:15)</option>
                        <option value="full-moon">Till Next Full Moon</option>
                        <option value="6h">Next 6 hours</option>
                        <option value="12h">Next 12 hours</option>
                        <option value="24h">Next 24 hours</option>
                        <option value="48h">Next 48 hours</option>
                        <option value="all" disabled>All upcoming events (disabled for performance)</option>
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
                            // Keep custom lat/lon in memory so user can switch back
                            this.filters.locationType = 'geolocation';
                            this.filters.selectedPredefinedLocation = null;
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
                            // Keep custom lat/lon in memory so user can switch back
                            const index = parseInt(value.split('-')[1]);
                            this.filters.locationType = 'predefined';
                            this.filters.selectedPredefinedLocation = index;
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
                                // Pre-fill inputs with saved custom values if they exist
                                if (this.filters.customLat && this.filters.customLon) {
                                    dropdown.querySelector('#custom-lat').value = this.filters.customLat.toFixed(4);
                                    dropdown.querySelector('#custom-lon').value = this.filters.customLon.toFixed(4);
                                } else if (this.userLocation) {
                                    // Only fall back to current location if no custom values saved
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

}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventListeners;
}
