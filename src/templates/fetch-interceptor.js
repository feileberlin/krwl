/**
 * KRWL HOF - Fetch API Interceptor
 * 
 * Purpose: Return embedded data instead of making network requests
 * Used by: Embedded in static/index.html during generation
 * 
 * Why: The generated HTML is self-contained with all data inlined.
 * The app still uses fetch() calls, but we intercept them to return
 * embedded data instead of making actual HTTP requests.
 * 
 * Intercepted URLs:
 * - config.json → window.ACTIVE_CONFIG
 * - events.json → window.ACTIVE_EVENTS
 * - content.json / content.de.json → window.EMBEDDED_CONTENT_*
 * 
 * Benefits:
 * - ✅ Works offline (PWA)
 * - ✅ No CORS issues
 * - ✅ Faster (no network delay)
 * - ✅ Code unchanged (still uses fetch)
 */
// Intercept fetch calls to return embedded data
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (url.includes('config.json')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(window.ACTIVE_CONFIG)
            });
        }
        if (url.includes('events.json')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({events: window.ACTIVE_EVENTS})
            });
        }
        if (url.includes('content.json')) {
            const content = url.includes('.de.') ? window.EMBEDDED_CONTENT_DE : window.EMBEDDED_CONTENT_EN;
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(content)
            });
        }
        return originalFetch.apply(this, arguments);
    };
})();
