/**
 * SpeechBubbles Module (Simplified)
 * 
 * Handles speech bubble UI components for events on the map.
 * Simplified positioning using CSS Grid instead of complex collision detection.
 * Bubbles follow their markers when map is panned/zoomed.
 * 
 * KISS: Replaced 100-line calculateBubblePosition() with simple grid layout
 */

// Bubble dimension constants
const BUBBLE_WIDTH = 220;
const BUBBLE_HEIGHT = 140;
const BUBBLE_MARGIN = 15;

// Positioning constants
const MARKER_VERTICAL_OFFSET = 50;     // Pixels above marker
const BASE_SPREAD_OFFSET = 60;         // Minimum distance from marker
const SPREAD_FACTOR = 40;              // Additional spread per bubble
const HORIZONTAL_SPREAD_MULTIPLIER = 1.2; // Wider horizontal spread

// Filter bar constants
const FILTER_BAR_PADDING = 20;         // Extra padding below filter bar
const DEFAULT_FILTER_BAR_HEIGHT = 60;  // Fallback if filter bar not found

// Organic variation seeds (prime numbers for better distribution)
const SEED_MULTIPLIER_X = 17;
const SEED_OFFSET = 11;
const VARIATION_RANGE_X = 21;
const SEED_MULTIPLIER_Y = 13;
const VARIATION_RANGE_Y = 15;

class SpeechBubbles {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.speechBubbles = [];
        this.map = null;
        this.bubbleData = []; // Store bubble-marker associations for updates
        this.moveHandler = null; // Store reference for cleanup
    }
    
    /**
     * Clear all speech bubbles from the map
     */
    clearSpeechBubbles() {
        // Remove map move listener if exists
        if (this.map && this.moveHandler) {
            this.map.off('move', this.moveHandler);
            this.map.off('zoom', this.moveHandler);
            this.moveHandler = null;
        }
        
        // Remove all bubble elements
        const bubbles = document.querySelectorAll('.speech-bubble');
        bubbles.forEach(bubble => bubble.remove());
        
        // Clear arrays
        this.speechBubbles = [];
        this.bubbleData = [];
        
        this.log('Speech bubbles cleared');
    }
    
    /**
     * Show speech bubbles for all filtered events
     * @param {Array} events - Filtered events to display
     * @param {Array} markers - Corresponding Leaflet markers
     * @param {Object} map - Leaflet map instance
     */
    showAllSpeechBubbles(events, markers, map) {
        if (!events || events.length === 0) return;
        if (!markers || markers.length === 0 || !map) {
            this.log('Cannot show speech bubbles: markers or map not available');
            return;
        }
        
        this.clearSpeechBubbles();
        this.map = map;
        
        // Group events by location (deduplication)
        const eventItems = this.deduplicateEvents(events);
        
        this.log(`Showing ${eventItems.length} speech bubbles (${events.length} events after deduplication)`);
        
        // Create bubbles with simple grid positioning
        eventItems.forEach((item, index) => {
            const marker = markers.find(m => 
                m && m.options && m.options.customData && m.options.customData.id === item.event.id
            );
            
            if (marker) {
                this.createSpeechBubble(
                    item.event,
                    marker,
                    index,
                    item.groupSize,
                    0,
                    item.duplicateCount,
                    map
                );
            }
        });
        
        // Setup map move/zoom listener to update bubble positions
        this.moveHandler = () => this.updateBubblePositions();
        map.on('move', this.moveHandler);
        map.on('zoom', this.moveHandler);
    }
    
    /**
     * Deduplicate events by title similarity
     * @param {Array} events - Events to deduplicate
     * @returns {Array} Deduplicated event items with metadata
     */
    deduplicateEvents(events) {
        const titleMap = new Map();
        
        events.forEach(event => {
            const key = event.title.toLowerCase().trim();
            if (!titleMap.has(key)) {
                titleMap.set(key, []);
            }
            titleMap.get(key).push(event);
        });
        
        const eventItems = [];
        titleMap.forEach((group, title) => {
            eventItems.push({
                event: group[0],
                groupSize: group.length,
                duplicateCount: group.length
            });
        });
        
        return eventItems;
    }
    
    /**
     * Create a single speech bubble for an event
     * Bubbles follow their markers when map is moved
     * @param {Object} event - Event data
     * @param {Object} marker - Leaflet marker
     * @param {number} index - Bubble index for positioning
     * @param {number} groupSize - Number of events in group
     * @param {number} groupIndex - Index within group
     * @param {number} duplicateCount - Number of duplicate events
     * @param {Object} map - Leaflet map instance
     * @returns {HTMLElement} Created bubble element
     */
    createSpeechBubble(event, marker, index, groupSize = 1, groupIndex = 0, duplicateCount = 1, map) {
        if (!marker || !map) return;
        
        // Get marker position in screen coordinates
        const markerPos = map.latLngToContainerPoint(marker.getLatLng());
        
        // Create bubble element
        const bubble = document.createElement('div');
        bubble.className = 'speech-bubble';
        bubble.setAttribute('data-event-id', event.id);
        bubble.setAttribute('data-bubble-index', index);
        
        // Format start time
        const startTime = new Date(event.start_time);
        const timeStr = startTime.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        const dateStr = startTime.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
        
        // Bookmark button
        const isBookmarked = this.storage.isBookmarked(event.id);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        const bookmarkingSupported = this.storage.isBookmarkingSupported();
        
        // Duplicate badge
        const duplicateBadge = duplicateCount > 1 ? 
            `<div class="bubble-duplicate-badge" title="${duplicateCount} duplicate events">×${duplicateCount}</div>` : '';
        
        bubble.innerHTML = `
            ${duplicateBadge}
            <div class="bubble-time-headline">${timeStr}</div>
            <div class="bubble-date">${dateStr}</div>
            <div class="bubble-title">${this.truncateText(event.title, 50)}</div>
            <div class="bubble-location">📍 ${this.truncateText(event.location.name, 30)}</div>
            ${event.distance !== undefined ? `<div class="bubble-distance">🚶 ${event.distance.toFixed(1)} km</div>` : ''}
            ${bookmarkingSupported ? `<button class="bubble-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                <i data-lucide="heart" aria-hidden="true"></i>
            </button>` : ''}
        `;
        
        // Initialize Lucide icons
        if (bookmarkingSupported && typeof lucide !== 'undefined') {
            setTimeout(() => lucide.createIcons(), 10);
        }
        
        // Calculate position relative to marker (bubble appears above/around marker)
        const position = this.calculateMarkerRelativePosition(markerPos, index);
        bubble.style.left = position.x + 'px';
        bubble.style.top = position.y + 'px';
        
        // Add to map container
        document.getElementById('map').appendChild(bubble);
        this.speechBubbles.push(bubble);
        
        // Store bubble-marker association for updates on map move
        this.bubbleData.push({
            bubble: bubble,
            marker: marker,
            index: index
        });
        
        // Fade in animation
        setTimeout(() => bubble.classList.add('visible'), 10);
        
        return bubble;
    }
    
    /**
     * Update all bubble positions when map is moved/zoomed
     * Called on map 'move' and 'zoom' events
     */
    updateBubblePositions() {
        if (!this.map || this.bubbleData.length === 0) return;
        
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        
        this.bubbleData.forEach(({ bubble, marker, index }) => {
            // Get updated marker position in screen coordinates
            const markerPos = this.map.latLngToContainerPoint(marker.getLatLng());
            
            // Calculate new position relative to marker
            const position = this.calculateMarkerRelativePosition(markerPos, index);
            
            // Update bubble position
            bubble.style.left = position.x + 'px';
            bubble.style.top = position.y + 'px';
            
            // Hide bubble if marker is outside viewport (with some margin)
            const isVisible = markerPos.x > -BUBBLE_WIDTH && 
                              markerPos.x < viewportWidth + BUBBLE_WIDTH &&
                              markerPos.y > -BUBBLE_HEIGHT && 
                              markerPos.y < viewportHeight + BUBBLE_HEIGHT;
            
            bubble.style.opacity = isVisible ? '' : '0';
            bubble.style.pointerEvents = isVisible ? '' : 'none';
        });
    }
    
    /**
     * Calculate position for speech bubble relative to its marker
     * Bubbles spread like leaves around the marker, growing upward
     * @param {Object} markerPos - {x, y} marker screen position
     * @param {number} index - Bubble index for spread variation
     * @returns {Object} {x, y} position for bubble
     */
    calculateMarkerRelativePosition(markerPos, index) {
        // Get filter bar height dynamically to avoid overlap
        const filterBar = document.getElementById('event-filter-bar');
        const filterBarHeight = filterBar ? filterBar.offsetHeight + FILTER_BAR_PADDING : DEFAULT_FILTER_BAR_HEIGHT;
        
        // Get map dimensions
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        
        // Use golden angle for natural leaf-like spread around marker
        const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // ~137.5 degrees
        const angle = index * goldenAngle;
        
        // Distance from marker increases with index (like tree branches)
        const offset = BASE_SPREAD_OFFSET + Math.sqrt(index) * SPREAD_FACTOR;
        
        // Calculate offset from marker position
        // Spread mostly upward and sideways (like leaves on a tree)
        const offsetX = Math.cos(angle) * offset * HORIZONTAL_SPREAD_MULTIPLIER;
        const offsetY = -Math.abs(Math.sin(angle) * offset) - MARKER_VERTICAL_OFFSET;
        
        // Position bubble relative to marker
        let x = markerPos.x + offsetX - BUBBLE_WIDTH / 2;
        let y = markerPos.y + offsetY - BUBBLE_HEIGHT;
        
        // Add small organic variation for natural feel
        const seed = (index * SEED_MULTIPLIER_X + SEED_OFFSET) % 100;
        const organicX = ((seed % VARIATION_RANGE_X) - Math.floor(VARIATION_RANGE_X / 2));
        const organicY = (((seed * SEED_MULTIPLIER_Y) % VARIATION_RANGE_Y) - Math.floor(VARIATION_RANGE_Y / 2));
        
        x += organicX;
        y += organicY;
        
        // Clamp to viewport bounds - ensure bubbles stay below filter bar
        x = Math.max(BUBBLE_MARGIN, Math.min(x, viewportWidth - BUBBLE_WIDTH - BUBBLE_MARGIN));
        y = Math.max(filterBarHeight + BUBBLE_MARGIN, Math.min(y, viewportHeight - BUBBLE_HEIGHT - BUBBLE_MARGIN));
        
        return { x, y };
    }
    
    /**
     * Truncate text to max length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
    
    /**
     * Log helper
     * @param {string} message - Message to log
     * @param  {...any} args - Additional arguments
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[SpeechBubbles]', message, ...args);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechBubbles;
}
