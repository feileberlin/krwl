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
 * Refactored to use smaller, focused methods
 */

class EventListeners {
    constructor(app) {
        this.app = app;
        this.dashboardLastFocusedElement = null;
        this.dashboardTrapFocus = null;
    }
    
    setupEventListeners() {
        this.setupDashboardListeners();
        this.setupFilterListeners();
        this.setupDistanceSliderListener();
        this.setupLocationFilterListener();
        this.setupKeyboardShortcuts();
        this.setupOrientationHandler();
    }
    
    setupDashboardListeners() {
        const dashboardLogo = document.getElementById('filter-bar-logo');
        const dashboardMenu = document.getElementById('dashboard-menu');
        const closeDashboard = document.getElementById('close-dashboard');
        
        if (!dashboardLogo || !dashboardMenu) return;
        
        // Create focus trap function
        this.dashboardTrapFocus = this.createFocusTrap(dashboardMenu);
        
        // Open dashboard on click
        dashboardLogo.addEventListener('click', () => this.openDashboard(dashboardMenu, closeDashboard));
        
        // Open dashboard on Enter/Space
        dashboardLogo.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.openDashboard(dashboardMenu, closeDashboard);
            }
        });
        
        // Close dashboard on close button
        if (closeDashboard) {
            closeDashboard.addEventListener('click', () => this.closeDashboard(dashboardMenu, dashboardLogo));
        }
        
        // Close dashboard on background click
        dashboardMenu.addEventListener('click', (e) => {
            if (e.target === dashboardMenu) {
                this.closeDashboard(dashboardMenu, dashboardLogo);
            }
        });
    }
    
    createFocusTrap(container) {
        return (e) => {
            if (e.key !== 'Tab' || container.classList.contains('hidden')) return;
            
            const focusableElements = container.querySelectorAll(
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
    }
    
    async openDashboard(dashboardMenu, closeDashboard) {
        this.dashboardLastFocusedElement = document.activeElement;
        
        // Step 1: Expand filter bar
        const filterBar = document.getElementById('event-filter-bar');
        if (filterBar) {
            filterBar.classList.add('dashboard-opening');
            await this.waitForTransition(filterBar, this.app.DASHBOARD_EXPANSION_DURATION + 100);
        }
        
        // Step 2: Show dashboard
        dashboardMenu.classList.remove('hidden');
        dashboardMenu.classList.add('visible');
        document.getElementById('filter-bar-logo')?.setAttribute('aria-expanded', 'true');
        this.app.updateDashboard();
        
        // Step 3: Focus close button after fade-in
        await this.waitForTransition(dashboardMenu, this.app.DASHBOARD_FADE_DURATION + 100);
        closeDashboard?.focus();
        this.app.mapManager?.invalidateSize();
        
        // Add focus trap
        document.addEventListener('keydown', this.dashboardTrapFocus);
    }
    
    async closeDashboard(dashboardMenu, dashboardLogo) {
        // Step 1: Collapse filter bar
        const filterBar = document.getElementById('event-filter-bar');
        if (filterBar) {
            filterBar.classList.remove('dashboard-opening');
        }
        
        // Step 2: Hide dashboard
        dashboardMenu.classList.add('hidden');
        dashboardMenu.classList.remove('visible');
        dashboardLogo.setAttribute('aria-expanded', 'false');
        
        // Remove focus trap
        document.removeEventListener('keydown', this.dashboardTrapFocus);
        
        // Step 3: Return focus after animation
        await this.waitForTransition(filterBar, this.app.DASHBOARD_EXPANSION_DURATION + 100);
        this.dashboardLastFocusedElement?.focus();
        this.app.mapManager?.invalidateSize();
    }
    
    waitForTransition(element, timeout) {
        return new Promise(resolve => {
            if (!element) {
                resolve();
                return;
            }
            
            const handleTransitionEnd = (e) => {
                if (e.target === element) {
                    element.removeEventListener('transitionend', handleTransitionEnd);
                    resolve();
                }
            };
            element.addEventListener('transitionend', handleTransitionEnd);
            setTimeout(resolve, timeout);
        });
    }
    
    setupFilterListeners() {
        // Category filter
        const categoryTextEl = document.getElementById('filter-bar-event-count');
        if (categoryTextEl) {
            this.setupCategoryFilter(categoryTextEl);
        }
        
        // Time filter
        const timeTextEl = document.getElementById('filter-bar-time-range');
        if (timeTextEl) {
            this.setupTimeFilter(timeTextEl);
        }
        
        // Distance filter
        const distanceTextEl = document.getElementById('filter-bar-distance');
        if (distanceTextEl) {
            this.setupDistanceFilter(distanceTextEl);
        }
    }
    
    setupCategoryFilter(categoryTextEl) {
        const getCategoryItems = () => {
            const location = this.app.getReferenceLocation();
            const categoryCounts = this.app.eventFilter.countCategoriesUnderFilters(
                this.app.events || [],
                this.app.filters,
                location
            );
            const totalCount = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
            
            // Use the same category groups from EventFilter
            const categoryGroups = this.app.eventFilter.categoryGroups;
            
            // Build grouped category counts
            const groupedCounts = {};
            const ungroupedCategories = new Set();
            
            Object.keys(categoryCounts).forEach((categoryValue) => {
                let grouped = false;
                for (const [groupKey, subcategories] of Object.entries(categoryGroups)) {
                    if (subcategories.includes(categoryValue)) {
                        groupedCounts[groupKey] = (groupedCounts[groupKey] || 0) + categoryCounts[categoryValue];
                        grouped = true;
                        break;
                    }
                }
                if (!grouped && categoryCounts[categoryValue] > 0) {
                    ungroupedCategories.add(categoryValue);
                }
            });
            
            // Build category list dynamically
            const categories = [{ label: 'events', value: 'all' }];
            
            // Add grouped categories (sorted)
            Object.keys(groupedCounts).sort().forEach((groupKey) => {
                if (groupedCounts[groupKey] > 0) {
                    // Convert group key to display label (e.g., "historical-monuments" -> "Historical & Monuments")
                    let displayLabel = groupKey
                        .split('-')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(' ');
                    
                    // Special case for "Historical Monuments" -> "Historical & Monuments"
                    if (groupKey === 'historical-monuments') {
                        displayLabel = 'Historical & Monuments';
                    }
                    
                    categories.push({
                        label: displayLabel,
                        value: groupKey,
                        count: groupedCounts[groupKey]
                    });
                }
            });
            
            // Add ungrouped categories (sorted), excluding "uncategorized"
            Array.from(ungroupedCategories).sort().forEach((categoryValue) => {
                // Skip "uncategorized" - these events only appear in "all events"
                if (categoryValue === 'uncategorized') {
                    return;
                }
                categories.push({
                    label: `${categoryValue} events`,
                    value: categoryValue,
                    count: categoryCounts[categoryValue]
                });
            });
            
            // Map to items with counts at the beginning
            return categories.map((item) => {
                const count = item.value === 'all' ? totalCount : item.count;
                // For "all", show "20 events total". For others, show count + label
                const displayLabel = item.value === 'all' ? 'events total' : item.label;
                return {
                    ...item,
                    label: `${count} ${displayLabel}`
                };
            });
        };
        
        new CustomDropdown(
            categoryTextEl,
            getCategoryItems,
            () => this.app.filters.category,
            (value) => {
                this.app.filters.category = value;
                this.app.storage.saveFiltersToCookie(this.app.filters);
                this.app.displayEvents();
            }
        );
    }
    
    setupTimeFilter(timeTextEl) {
        // Function to generate time range options with calculated dates/times
        const getTimeRanges = () => {
            const now = new Date();
            
            // Helper function to format time remaining
            const formatTimeRemaining = (targetDate) => {
                const msRemaining = targetDate - now;
                const hoursRemaining = msRemaining / (1000 * 60 * 60);
                
                if (hoursRemaining < 1) {
                    const minutesRemaining = Math.round(msRemaining / (1000 * 60));
                    return `${minutesRemaining} minute${minutesRemaining !== 1 ? 's' : ''}`;
                } else if (hoursRemaining < 24) {
                    const hours = Math.round(hoursRemaining);
                    return `${hours} hour${hours !== 1 ? 's' : ''}`;
                } else {
                    const days = Math.round(hoursRemaining / 24);
                    return `${days} day${days !== 1 ? 's' : ''}`;
                }
            };
            
            // Calculate actual dates/times for each filter
            const ranges = [];
            
            // Sunrise
            const sunrise = this.app.eventFilter.getNextSunrise();
            ranges.push({
                value: 'sunrise',
                label: `til sunrise (${formatTimeRemaining(sunrise)})`,
                timestamp: sunrise.getTime()
            });
            
            // Sunday primetime
            const sundayPrimetime = this.app.eventFilter.getNextSundayPrimetime();
            ranges.push({
                value: 'sunday-primetime',
                label: `til Sunday's primetime (${formatTimeRemaining(sundayPrimetime)})`,
                timestamp: sundayPrimetime.getTime()
            });
            
            // Full moon
            const fullMoon = this.app.eventFilter.getNextFullMoon();
            ranges.push({
                value: 'full-moon',
                label: `til full moon (${formatTimeRemaining(fullMoon)})`,
                timestamp: fullMoon.getTime()
            });
            
            // Sort by timestamp (earliest first)
            ranges.sort((a, b) => a.timestamp - b.timestamp);
            
            // Note: "upcoming (all events)" temporarily disabled for performance reasons
            // Loading all events without time limit can cause browser slowdown with large datasets
            // Commented out - uncomment when performance optimizations are implemented
            /* ranges.push({
                value: 'all',
                label: 'upcoming (all events)',
                timestamp: Infinity
            }); */
            
            // Add disabled placeholder to show option exists but is unavailable
            ranges.push({
                value: 'all',
                label: '~~upcoming (all events)~~ (disabled for performance)',
                timestamp: Infinity,
                disabled: true
            });
            
            return ranges;
        };
        
        new CustomDropdown(
            timeTextEl,
            getTimeRanges,
            () => this.app.filters.timeFilter,
            (value) => {
                this.app.filters.timeFilter = value;
                this.app.storage.saveFiltersToCookie(this.app.filters);
                this.app.displayEvents();
            }
        );
    }
    
    setupDistanceFilter(distanceTextEl) {
        const distances = [
            { label: 'within 30 min walk (2 km)', value: '2' },
            { label: 'within 30 min bicycle ride (3.75 km)', value: '3.75' },
            { label: 'within 30 min public transport (12.5 km)', value: '12.5' },
            { label: 'within 60 min car sharing (60 km)', value: '60' }
        ];
        
        new CustomDropdown(
            distanceTextEl,
            distances,
            String(this.app.filters.maxDistance),
            (value) => {
                this.app.filters.maxDistance = parseFloat(value);
                this.app.storage.saveFiltersToCookie(this.app.filters);
                this.app.displayEvents();
            }
        );
    }
    
    setupDistanceSliderListener() {
        const distanceSlider = document.getElementById('filter-distance-slider');
        if (!distanceSlider) return;
        
        distanceSlider.addEventListener('input', (e) => {
            this.app.filters.maxDistance = parseFloat(e.target.value);
            this.app.displayEventsDebounced();
        });
        
        distanceSlider.addEventListener('change', () => {
            this.app.storage.saveFiltersToCookie(this.app.filters);
        });
    }
    
    setupLocationFilterListener() {
        const locationTextEl = document.getElementById('filter-bar-location');
        if (!locationTextEl) return;
        
        const getLocationItems = () => {
            const geolocationLabel = 'from here';
            const prefix = 'from';
            const customLocs = this.app.storage.getCustomLocations();
            
            const items = [{ label: geolocationLabel, value: 'geolocation' }];
            
            // Add custom locations (only config.json predefined locations)
            customLocs.forEach((loc) => {
                items.push({ 
                    label: `${prefix} ${loc.name}`, 
                    value: `custom-${loc.id}`,
                    customLocation: true
                });
            });
            
            // Note: Custom location creation removed from dropdown - use dashboard instead
            
            return items;
        };
        
        const getCurrentValue = () => {
            if (this.app.filters.locationType === 'custom' && this.app.filters.selectedCustomLocation) {
                return `custom-${this.app.filters.selectedCustomLocation}`;
            }
            return 'geolocation';
        };
        
        new CustomDropdown(
            locationTextEl,
            getLocationItems,
            getCurrentValue,
            (value) => {
                if (value === 'geolocation') {
                    this.app.filters.locationType = 'geolocation';
                    this.app.filters.selectedPredefinedLocation = null;
                    this.app.filters.selectedCustomLocation = null;
                    this.app.storage.saveFiltersToCookie(this.app.filters);
                    
                    const userLocation = this.app.mapManager?.userLocation;
                    if (userLocation) {
                        // Center map with zoom based on current distance filter
                        const distanceKm = this.app.filters.maxDistance;
                        this.app.mapManager.centerMap(userLocation.lat, userLocation.lon, null, distanceKm);
                        
                        // Update reference marker to show geolocation
                        this.app.mapManager.updateReferenceMarker(
                            userLocation.lat, 
                            userLocation.lon, 
                            'You are here'
                        );
                    }
                    
                    this.app.displayEvents();
                    return;
                }
                
                if (value.startsWith('custom-')) {
                    const locationId = value.replace('custom-', '');
                    const selectedLoc = this.app.storage.getCustomLocationById(locationId);
                    if (!selectedLoc) return;
                    
                    this.app.filters.locationType = 'custom';
                    this.app.filters.selectedPredefinedLocation = null;
                    this.app.filters.selectedCustomLocation = locationId;
                    this.app.filters.selectedCustomLocationName = selectedLoc.name; // Store name for display
                    this.app.filters.customLat = selectedLoc.lat;
                    this.app.filters.customLon = selectedLoc.lon;
                    this.app.storage.saveFiltersToCookie(this.app.filters);
                    
                    // Center map with zoom based on current distance filter
                    const distanceKm = this.app.filters.maxDistance;
                    this.app.mapManager?.centerMap(selectedLoc.lat, selectedLoc.lon, null, distanceKm);
                    
                    // Update reference marker to show custom location
                    this.app.mapManager.updateReferenceMarker(
                        selectedLoc.lat, 
                        selectedLoc.lon, 
                        selectedLoc.name || 'Custom location'
                    );
                    
                    this.app.displayEvents();
                    return;
                }
            }
        );
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // ESC to close dashboard
            if (e.key === 'Escape') {
                const dashboardMenu = document.getElementById('dashboard-menu');
                if (dashboardMenu && !dashboardMenu.classList.contains('hidden')) {
                    this.closeDashboard(dashboardMenu, document.getElementById('filter-bar-logo'));
                }
            }
            
            // Arrow keys for event navigation
            if (e.key === 'ArrowLeft') {
                this.app.navigateEvents?.(-1);
            } else if (e.key === 'ArrowRight') {
                this.app.navigateEvents?.(1);
            }
        });
    }
    
    setupOrientationHandler() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.app.utils?.updateViewportDimensions();
                this.app.mapManager?.invalidateSize();
            }, this.app.ORIENTATION_CHANGE_DELAY);
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventListeners;
}
