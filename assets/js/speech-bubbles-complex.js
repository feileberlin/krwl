/**
 * SpeechBubbles Module
 * 
 * Handles speech bubble UI elements that appear over map markers:
 * - Bubble creation and positioning
 * - Collision detection
 * - Deduplication logic
 * - Click handlers
 * 
 * KISS: Single responsibility - speech bubble management only
 */

class SpeechBubbles {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.speechBubbles = [];
        this.occupiedBubblePositions = [];
    }
    
    /**
     * Clear all speech bubbles from the map
     */
    clearSpeechBubbles() {
        this.speechBubbles.forEach(bubble => {
            if (bubble.parentElement) {
                bubble.remove();
            }
        });
        this.speechBubbles = [];
        this.occupiedBubblePositions = [];
    }
    
    /**
     * Show speech bubbles for all visible events
     * @param {Array} events - Filtered events to display
     * @param {Array} markers - Corresponding Leaflet markers
     * @param {Object} map - Leaflet map instance
     */
    showAllSpeechBubbles(events, markers, map) {
        this.clearSpeechBubbles();
        
        const maxBubbles = 30; // Limit to prevent performance issues
        const eventsToShow = events.slice(0, maxBubbles);
        
        // Build array of {event, marker, originalIndex} for deduplication
        const eventItems = eventsToShow.map((event, index) => ({
            event,
            marker: markers[index],
            originalIndex: index
        }));
        
        // Deduplicate events
        const uniqueItems = this.deduplicateEvents(eventItems);
        
        // Create speech bubbles for unique events
        uniqueItems.forEach((item, index) => {
            this.createSpeechBubble(
                item.event,
                item.marker,
                index,
                1, // groupSize (deprecated)
                0, // groupIndex (deprecated)
                item.duplicateCount,
                map
            );
        });
        
        this.log(`Showing ${uniqueItems.length} speech bubbles (${eventsToShow.length} total events)`);
    }
    
    /**
     * Deduplicate events based on title and start time
     * @param {Array} eventItems - Array of {event, marker, originalIndex}
     * @returns {Array} Array of unique items with duplicateCount property
     */
    deduplicateEvents(eventItems) {
        const uniqueMap = new Map();
        
        eventItems.forEach(item => {
            const title = item.event.title.toLowerCase().trim();
            const startTime = item.event.start_time;
            const key = `${title}|${startTime}`;
            
            if (uniqueMap.has(key)) {
                const existing = uniqueMap.get(key);
                existing.duplicateCount++;
                existing.duplicates.push(item.event);
            } else {
                uniqueMap.set(key, {
                    ...item,
                    duplicateCount: 1,
                    duplicates: [item.event]
                });
            }
        });
        
        return Array.from(uniqueMap.values());
    }
    
    /**
     * Create and position a speech bubble for an event
     * @param {Object} event - Event data
     * @param {Object} marker - Leaflet marker
     * @param {number} index - Display order index
     * @param {number} groupSize - Deprecated, kept for compatibility
     * @param {number} groupIndex - Deprecated, kept for compatibility
     * @param {number} duplicateCount - Number of duplicate events
     * @param {Object} map - Leaflet map instance
     */
    createSpeechBubble(event, marker, index, groupSize = 1, groupIndex = 0, duplicateCount = 1, map) {
        if (!marker || !map) return;
        
        // Get marker position in screen coordinates
        const markerPos = map.latLngToContainerPoint(marker.getLatLng());
        
        // Create bubble element
        const bubble = document.createElement('div');
        bubble.className = 'speech-bubble';
        bubble.setAttribute('data-event-id', event.id);
        
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
        
        // Position bubble
        const position = this.calculateBubblePosition(markerPos, index);
        bubble.style.left = position.x + 'px';
        bubble.style.top = position.y + 'px';
        
        // Add to map container
        document.getElementById('map').appendChild(bubble);
        this.speechBubbles.push(bubble);
        
        // Fade in animation
        setTimeout(() => bubble.classList.add('visible'), 10);
        
        return bubble;
    }
    
    /**
     * Calculate position for speech bubble with collision detection
     * Uses blended randomness + predictable patterns for organic variety
     * @param {Object} markerPos - {x, y} marker screen position
     * @param {number} index - Bubble index
     * @returns {Object} {x, y} position for bubble
     */
    calculateBubblePosition(markerPos, index) {
        const bubbleWidth = 220;
        const bubbleHeight = 140;
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        const margin = 10;
        const padding = 15; // Minimum spacing between bubbles
        
        // Helper: Check if two rectangles overlap
        const overlaps = (x1, y1, x2, y2) => {
            return !(x1 + bubbleWidth + padding < x2 || 
                     x2 + bubbleWidth + padding < x1 || 
                     y1 + bubbleHeight + padding < y2 || 
                     y2 + bubbleHeight + padding < y1);
        };
        
        // Try random positions with collision detection
        const maxAttempts = 100;
        let attempt = 0;
        
        while (attempt < maxAttempts) {
            // Semi-random offset with index-based bias
            const distance = 60 + Math.random() * 140;
            const randomAngle = Math.random() * 2 * Math.PI;
            const indexBias = (index * 0.5) % (2 * Math.PI);
            const angle = randomAngle + indexBias;
            
            let x = markerPos.x + Math.cos(angle) * distance;
            let y = markerPos.y + Math.sin(angle) * distance;
            
            // Clamp to viewport bounds
            x = Math.max(margin, Math.min(x, viewportWidth - bubbleWidth - margin));
            y = Math.max(margin, Math.min(y, viewportHeight - bubbleHeight - margin));
            
            // Check for overlaps
            let hasOverlap = false;
            for (const occupied of this.occupiedBubblePositions) {
                if (overlaps(x, y, occupied.x, occupied.y)) {
                    hasOverlap = true;
                    break;
                }
            }
            
            if (!hasOverlap) {
                this.occupiedBubblePositions.push({ x, y });
                return { x, y };
            }
            
            attempt++;
        }
        
        // Fallback: Spiral pattern with golden angle
        const spiralAttempts = 30;
        for (let i = 0; i < spiralAttempts; i++) {
            const spiralRadius = 80 + (i * 30);
            const goldenAngle = (index + i) * 0.618 * 2 * Math.PI;
            const randomOffset = (Math.random() - 0.5) * 0.5;
            const spiralAngle = goldenAngle + randomOffset;
            
            let x = markerPos.x + Math.cos(spiralAngle) * spiralRadius;
            let y = markerPos.y + Math.sin(spiralAngle) * spiralRadius;
            
            x = Math.max(margin, Math.min(x, viewportWidth - bubbleWidth - margin));
            y = Math.max(margin, Math.min(y, viewportHeight - bubbleHeight - margin));
            
            let hasOverlap = false;
            for (const occupied of this.occupiedBubblePositions) {
                if (overlaps(x, y, occupied.x, occupied.y)) {
                    hasOverlap = true;
                    break;
                }
            }
            
            if (!hasOverlap) {
                this.occupiedBubblePositions.push({ x, y });
                return { x, y };
            }
        }
        
        // Last resort: Grid layout
        const gridCellWidth = bubbleWidth + padding + 15;
        const gridCellHeight = bubbleHeight + padding + 5;
        const gridColumns = Math.floor(viewportWidth / gridCellWidth);
        
        const gridX = (index % gridColumns) * gridCellWidth + margin;
        const gridY = Math.floor(index / gridColumns) * gridCellHeight + margin;
        
        const forceX = Math.min(gridX, viewportWidth - bubbleWidth - margin);
        const forceY = Math.min(gridY, viewportHeight - bubbleHeight - margin);
        
        this.occupiedBubblePositions.push({ x: forceX, y: forceY });
        return { x: forceX, y: forceY };
    }
    
    /**
     * Truncate text to max length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
    
    /**
     * Debug logging helper
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
