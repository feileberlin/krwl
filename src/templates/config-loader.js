/**
 * KRWL HOF - Runtime Configuration Loader
 * 
 * Purpose: Detects environment and selects appropriate config
 * Used by: Embedded in static/index.html during generation
 * 
 * How it works:
 * 1. Checks hostname and pathname for dev indicators
 * 2. Selects config from window.ALL_CONFIGS array
 * 3. Filters events based on config.data.source
 * 
 * Environment detection:
 * - localhost/127.0.0.1 → development (index 1)
 * - /dev/ or /test/ in path → development (index 1)
 * - Everything else → production (index 0)
 * 
 * Result:
 * - window.ACTIVE_CONFIG - Selected configuration
 * - window.ACTIVE_EVENTS - Filtered events (real only in prod)
 */
// Runtime configuration loader - detects environment
(function() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Determine which config to use based on environment
    let configIndex = 0; // Default to production (first config)
    
    // Development indicators
    if (hostname === 'localhost' || 
        hostname === '127.0.0.1' ||
        pathname.includes('/dev/') ||
        pathname.includes('/test/')) {
        configIndex = 1; // Use development config if available
    }
    
    // Select config (fallback to first if index out of bounds)
    window.ACTIVE_CONFIG = window.ALL_CONFIGS[configIndex] || window.ALL_CONFIGS[0];
    
    // Filter events based on active config
    if (window.ACTIVE_CONFIG.data && window.ACTIVE_CONFIG.data.source === 'real') {
        // Production: only real events (filter out demo events)
        window.ACTIVE_EVENTS = window.ALL_EVENTS.filter(e => !e.id.includes('demo_'));
    } else {
        // Development: all events
        window.ACTIVE_EVENTS = window.ALL_EVENTS;
    }
})();
