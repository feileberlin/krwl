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
        const categories = [
            { label: 'all events', value: 'all' },
            { label: 'music events', value: 'music' },
            { label: 'sports events', value: 'sports' },
            { label: 'cultural events', value: 'culture' }
        ];
        
        const getCategoryItems = () => {
            const location = this.app.getReferenceLocation();
            const categoryCounts = this.app.eventFilter.countCategoriesUnderFilters(
                this.app.events || [],
                this.app.filters,
                location
            );
            const totalCount = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
            
            return categories.map((item) => {
                const count = item.value === 'all' ? totalCount : (categoryCounts[item.value] || 0);
                return {
                    ...item,
                    label: `${item.label} (${count})`
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
        const timeRanges = [
            { label: 'Next Sunrise (6 AM)', value: 'sunrise' },
            { label: "Till Sunday's Primetime (20:15)", value: 'sunday-primetime' },
            { label: 'Till Next Full Moon', value: 'full-moon' },
            { label: 'All upcoming events', value: 'all' }
        ];
        
        new CustomDropdown(
            timeTextEl,
            timeRanges,
            this.app.filters.timeFilter,
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
        // Location filter logic would go here
        // This is a placeholder for the complex location handling
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
