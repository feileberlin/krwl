/**
 * SpeechBubbles Module
 * 
 * Handles speech bubble UI components for events on the map.
 * Collision-aware positioning with organic spread around markers.
 * Bubbles follow their markers when map is panned/zoomed.
 * Users can drag bubbles to resolve positioning conflicts manually.
 */

// Bubble dimension constants
const BUBBLE_WIDTH = 220;
const BUBBLE_HEIGHT = 140;
const BUBBLE_MARGIN = 15;
const BUBBLE_GUTTER = 12;

// Positioning constants
const MARKER_VERTICAL_OFFSET = 50;     // Pixels above marker
const BASE_SPREAD_OFFSET = 60;         // Minimum distance from marker
const SPREAD_FACTOR = 40;              // Additional spread per bubble
const HORIZONTAL_SPREAD_MULTIPLIER = 1.2; // Wider horizontal spread
const MARKER_CLEARANCE = 18;
const MAX_POSITION_ATTEMPTS = 30;
const GOLDEN_ANGLE = 2.399963229728653; // Golden ratio angle (≈137.5°) in radians
const SPREAD_BASE = 1;                 // Avoid sqrt(0) spacing

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
        this.connectorLayer = null;
        this.markers = [];
        
        // Drag state
        this.dragState = {
            isDragging: false,
            bubble: null,
            startX: 0,
            startY: 0,
            bubbleOffsetX: 0,
            bubbleOffsetY: 0,
            mapOffsetX: 0,
            mapOffsetY: 0
        };
        
        // Bind drag handlers to preserve context
        this.handleDragStart = this.handleDragStart.bind(this);
        this.handleDragMove = this.handleDragMove.bind(this);
        this.handleDragEnd = this.handleDragEnd.bind(this);
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

        if (this.connectorLayer) {
            this.connectorLayer.remove();
            this.connectorLayer = null;
        }
        
        // Clear arrays
        this.speechBubbles = [];
        this.bubbleData = [];
        this.markers = [];
        
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
        this.markers = markers;
        this.setupConnectorLayer();
        
        // Group events by location (deduplication)
        const eventItems = this.deduplicateEvents(events);
        
        this.log(`Showing ${eventItems.length} speech bubbles (${events.length} events after deduplication)`);
        
        const occupiedRects = [];
        const markerBounds = this.getMarkerBounds(markers, map);

        // Create bubbles with collision-aware positioning
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
                    map,
                    occupiedRects,
                    markerBounds
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
     * @param {Array} occupiedRects - Existing bubble rectangles
     * @param {Array} markerBounds - Marker rectangles
     * @returns {HTMLElement} Created bubble element
     */
    createSpeechBubble(event, marker, index, groupSize = 1, groupIndex = 0, duplicateCount = 1, map, occupiedRects = [], markerBounds = []) {
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
        if (bookmarkingSupported && window.lucide && typeof window.lucide.createIcons === 'function') {
            setTimeout(() => window.lucide.createIcons(), 10);
        }
        
        // Calculate position relative to marker (bubble appears above/around marker)
        const position = this.calculateMarkerRelativePosition(markerPos, index, occupiedRects, markerBounds);
        bubble.style.left = position.x + 'px';
        bubble.style.top = position.y + 'px';
        
        // Add to map container
        document.getElementById('map').appendChild(bubble);
        this.speechBubbles.push(bubble);

        const bubbleRect = this.getBubbleRect(position.x, position.y);
        occupiedRects.push(bubbleRect);
        const connectorLine = this.createConnectorLine(markerPos, bubbleRect);
        
        // Store bubble-marker association for updates on map move
        this.bubbleData.push({
            bubble: bubble,
            marker: marker,
            index: index,
            userOffset: null, // Track user-applied drag offset
            connector: connectorLine
        });
        
        // Add drag event listeners for repositioning
        this.setupDragListeners(bubble);
        
        // Fade in animation
        setTimeout(() => bubble.classList.add('visible'), 10);
        
        return bubble;
    }
    
    /**
     * Setup drag event listeners for a bubble
     * Supports both mouse and touch events for mobile
     * @param {HTMLElement} bubble - Bubble element
     */
    setupDragListeners(bubble) {
        // Mouse events
        bubble.addEventListener('mousedown', this.handleDragStart);
        
        // Touch events for mobile
        bubble.addEventListener('touchstart', this.handleDragStart, { passive: false });
    }
    
    /**
     * Handle drag start (mousedown/touchstart)
     * @param {Event} e - Mouse or touch event
     */
    handleDragStart(e) {
        // Don't drag if clicking on bookmark button
        if (e.target.closest('.bubble-bookmark')) return;
        
        const bubble = e.target.closest('.speech-bubble');
        if (!bubble) return;
        
        // Prevent map panning while dragging bubble
        if (this.map) {
            this.map.dragging.disable();
        }
        
        // Get starting position
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
        
        const rect = bubble.getBoundingClientRect();
        const mapContainer = document.getElementById('map');
        const mapRect = mapContainer.getBoundingClientRect();
        
        // Store the mouse offset within the bubble (relative to bubble's top-left)
        // and the map container offset for coordinate conversion
        this.dragState = {
            isDragging: true,
            bubble: bubble,
            startX: clientX,
            startY: clientY,
            // Offset of click point within the bubble
            bubbleOffsetX: clientX - rect.left,
            bubbleOffsetY: clientY - rect.top,
            // Map container's position for coordinate conversion
            mapOffsetX: mapRect.left,
            mapOffsetY: mapRect.top
        };
        
        bubble.classList.add('dragging');
        
        // Add move/end listeners to document
        document.addEventListener('mousemove', this.handleDragMove);
        document.addEventListener('mouseup', this.handleDragEnd);
        document.addEventListener('touchmove', this.handleDragMove, { passive: false });
        document.addEventListener('touchend', this.handleDragEnd);
        
        // Prevent text selection and default touch behavior
        e.preventDefault();
        
        this.log('Drag started for bubble');
    }
    
    /**
     * Handle drag move (mousemove/touchmove)
     * @param {Event} e - Mouse or touch event
     */
    handleDragMove(e) {
        if (!this.dragState.isDragging || !this.dragState.bubble) return;
        
        const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
        
        const mapContainer = document.getElementById('map');
        const mapRect = mapContainer.getBoundingClientRect();
        
        // Calculate new position relative to map container
        // clientX/Y is in viewport coords, subtract map offset to get map-relative position
        // then subtract bubble offset to position the bubble where user grabbed it
        let newX = clientX - mapRect.left - this.dragState.bubbleOffsetX;
        let newY = clientY - mapRect.top - this.dragState.bubbleOffsetY;
        
        // Get filter bar height to avoid overlap
        const filterBar = document.getElementById('event-filter-bar');
        const filterBarHeight = filterBar ? filterBar.offsetHeight + FILTER_BAR_PADDING : DEFAULT_FILTER_BAR_HEIGHT;
        
        // Clamp to viewport bounds
        newX = Math.max(BUBBLE_MARGIN, Math.min(newX, mapContainer.clientWidth - BUBBLE_WIDTH - BUBBLE_MARGIN));
        newY = Math.max(filterBarHeight + BUBBLE_MARGIN, Math.min(newY, mapContainer.clientHeight - BUBBLE_HEIGHT - BUBBLE_MARGIN));
        
        // Apply position
        this.dragState.bubble.style.left = newX + 'px';
        this.dragState.bubble.style.top = newY + 'px';
        this.updateConnectorLineForBubble(this.dragState.bubble);
        
        e.preventDefault();
    }
    
    /**
     * Handle drag end (mouseup/touchend)
     * @param {Event} e - Mouse or touch event
     */
    handleDragEnd(e) {
        if (!this.dragState.isDragging) return;
        
        const bubble = this.dragState.bubble;
        
        // Re-enable map panning
        if (this.map) {
            this.map.dragging.enable();
        }
        
        if (bubble) {
            bubble.classList.remove('dragging');
            
            // Store user offset so position persists during map move
            const bubbleDataEntry = this.bubbleData.find(d => d.bubble === bubble);
            if (bubbleDataEntry && bubbleDataEntry.marker && this.map) {
                const markerPos = this.map.latLngToContainerPoint(bubbleDataEntry.marker.getLatLng());
                const bubbleX = parseFloat(bubble.style.left);
                const bubbleY = parseFloat(bubble.style.top);
                
                // Store offset from marker position
                bubbleDataEntry.userOffset = {
                    x: bubbleX - markerPos.x,
                    y: bubbleY - markerPos.y
                };
                
                this.log('User repositioned bubble, offset stored:', bubbleDataEntry.userOffset);
            }
        }
        
        // Remove move/end listeners
        document.removeEventListener('mousemove', this.handleDragMove);
        document.removeEventListener('mouseup', this.handleDragEnd);
        document.removeEventListener('touchmove', this.handleDragMove);
        document.removeEventListener('touchend', this.handleDragEnd);
        
        // Reset drag state
        this.dragState = {
            isDragging: false,
            bubble: null,
            startX: 0,
            startY: 0,
            bubbleOffsetX: 0,
            bubbleOffsetY: 0,
            mapOffsetX: 0,
            mapOffsetY: 0
        };
        
        this.log('Drag ended');
    }
    
    /**
     * Update all bubble positions when map is moved/zoomed
     * Called on map 'move' and 'zoom' events
     * Respects user-adjusted positions (userOffset) when available
     */
    updateBubblePositions() {
        if (!this.map || this.bubbleData.length === 0) return;
        
        // Don't update positions while user is dragging
        if (this.dragState.isDragging) return;
        
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        this.updateConnectorViewport(viewportWidth, viewportHeight);
        
        const { height: filterBarHeight } = this.getFilterBarMetrics(mapContainer);
        const markerBounds = this.getMarkerBounds(this.markers.length ? this.markers : this.bubbleData.map(entry => entry.marker), this.map);
        const occupiedRects = [];
        
        this.bubbleData.forEach(({ bubble, marker, index, userOffset, connector }) => {
            if (!this.isValidMarker(marker)) {
                return;
            }
            // Get updated marker position in screen coordinates
            const markerPos = this.map.latLngToContainerPoint(marker.getLatLng());
            
            let x, y;
            let bubbleRect;
            
            // If user has manually repositioned this bubble, use their offset
            if (userOffset) {
                x = markerPos.x + userOffset.x;
                y = markerPos.y + userOffset.y;
                
                // Clamp to viewport bounds
                x = Math.max(BUBBLE_MARGIN, Math.min(x, viewportWidth - BUBBLE_WIDTH - BUBBLE_MARGIN));
                y = Math.max(filterBarHeight + BUBBLE_MARGIN, Math.min(y, viewportHeight - BUBBLE_HEIGHT - BUBBLE_MARGIN));
                bubbleRect = this.getBubbleRect(x, y);
            } else {
                // Use automatic positioning
                const position = this.calculateMarkerRelativePosition(markerPos, index, occupiedRects, markerBounds);
                x = position.x;
                y = position.y;
                bubbleRect = this.getBubbleRect(x, y);
            }
            
            // Update bubble position
            bubble.style.left = x + 'px';
            bubble.style.top = y + 'px';

            occupiedRects.push(bubbleRect);
            
            // Hide bubble if marker is outside viewport (with some margin)
            const isVisible = markerPos.x > -BUBBLE_WIDTH && 
                              markerPos.x < viewportWidth + BUBBLE_WIDTH &&
                              markerPos.y > -BUBBLE_HEIGHT && 
                              markerPos.y < viewportHeight + BUBBLE_HEIGHT;
            
            bubble.style.opacity = isVisible ? '' : '0';
            bubble.style.pointerEvents = isVisible ? '' : 'none';
            if (connector) {
                this.updateConnectorLine({ bubble, marker, connector }, bubbleRect, markerPos, isVisible);
            }
        });
    }

    /**
     * Create or reset the SVG layer for bubble connectors.
     */
    setupConnectorLayer() {
        if (!this.map) return;
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        if (this.connectorLayer) {
            this.connectorLayer.remove();
        }

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.classList.add('bubble-connectors');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', `0 0 ${mapContainer.clientWidth} ${mapContainer.clientHeight}`);
        mapContainer.appendChild(svg);
        this.connectorLayer = svg;
    }

    /**
     * Update SVG connector viewbox to match the current viewport.
     * @param {number} width - Map container width.
     * @param {number} height - Map container height.
     */
    updateConnectorViewport(width, height) {
        if (!this.connectorLayer) return;
        this.connectorLayer.setAttribute('viewBox', `0 0 ${width} ${height}`);
    }

    /**
     * Create a connector line element between a marker and bubble.
     * @param {Object} markerPos - Marker position in container coordinates.
     * @param {Object} bubbleRect - Bubble rectangle bounds.
     * @returns {SVGLineElement|null} Connector line element.
     */
    createConnectorLine(markerPos, bubbleRect) {
        if (!this.connectorLayer) return null;
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.classList.add('bubble-connector-line');
        this.connectorLayer.appendChild(line);
        this.updateConnectorLine({ connector: line }, bubbleRect, markerPos, true);
        return line;
    }

    /**
     * Update connector line for a single bubble (used during drag).
     * @param {HTMLElement} bubble - Bubble element being moved.
     */
    updateConnectorLineForBubble(bubble) {
        if (!bubble || !this.map) return;
        const entry = this.bubbleData.find(data => data.bubble === bubble);
        if (!entry || !entry.marker || !entry.connector) return;
        const markerPos = this.map.latLngToContainerPoint(entry.marker.getLatLng());
        const bubbleRect = this.getBubbleRectFromElement(bubble);
        this.updateConnectorLine(entry, bubbleRect, markerPos, true);
    }

    /**
     * Update connector coordinates between a marker and bubble.
     * @param {Object} entry - Bubble data entry.
     * @param {Object} bubbleRect - Bubble rectangle bounds.
     * @param {Object} markerPos - Marker position in container coordinates.
     * @param {boolean} isVisible - Whether the bubble is visible.
     */
    updateConnectorLine(entry, bubbleRect, markerPos, isVisible) {
        const connector = entry.connector;
        if (!connector) return;
        const endPoint = this.getClosestPointOnRect(markerPos, bubbleRect);
        connector.setAttribute('x1', markerPos.x);
        connector.setAttribute('y1', markerPos.y);
        connector.setAttribute('x2', endPoint.x);
        connector.setAttribute('y2', endPoint.y);
        connector.style.opacity = isVisible ? '' : '0';
    }

    /**
     * Build a rectangle object for collision checks.
     * @param {number} x - Left position.
     * @param {number} y - Top position.
     * @returns {Object} Rectangle bounds.
     */
    getBubbleRect(x, y) {
        return {
            x,
            y,
            width: BUBBLE_WIDTH,
            height: BUBBLE_HEIGHT
        };
    }

    /**
     * Extract bubble rectangle bounds from a DOM element.
     * @param {HTMLElement} bubble - Bubble element.
     * @returns {Object} Rectangle bounds.
     */
    getBubbleRectFromElement(bubble) {
        const x = parseFloat(bubble.style.left) || 0;
        const y = parseFloat(bubble.style.top) || 0;
        return this.getBubbleRect(x, y);
    }

    /**
     * Get the closest point on a rectangle to a target point.
     * @param {Object} point - Target point.
     * @param {Object} rect - Rectangle bounds.
     * @returns {Object} Closest point.
     */
    getClosestPointOnRect(point, rect) {
        const x = Math.max(rect.x, Math.min(point.x, rect.x + rect.width));
        const y = Math.max(rect.y, Math.min(point.y, rect.y + rect.height));
        return { x, y };
    }

    /**
     * Check if two rectangles overlap with optional padding.
     * @param {Object} rectA - First rectangle.
     * @param {Object} rectB - Second rectangle.
     * @param {number} padding - Extra gutter between rectangles.
     * @returns {boolean} True if rectangles overlap.
     */
    rectanglesOverlap(rectA, rectB, padding = 0) {
        return !(rectA.x + rectA.width + padding < rectB.x ||
                 rectB.x + rectB.width + padding < rectA.x ||
                 rectA.y + rectA.height + padding < rectB.y ||
                 rectB.y + rectB.height + padding < rectA.y);
    }

    /**
     * Get filter bar bounds and safe height within the map container.
     * @param {HTMLElement} mapContainer - Map container element.
     * @returns {Object} Metrics including height and rect.
     */
    getFilterBarMetrics(mapContainer) {
        const filterBar = document.getElementById('event-filter-bar');
        if (!filterBar || !mapContainer) {
            return { height: DEFAULT_FILTER_BAR_HEIGHT, rect: null };
        }

        const mapRect = mapContainer.getBoundingClientRect();
        const barRect = filterBar.getBoundingClientRect();
        const rect = {
            x: barRect.left - mapRect.left,
            y: barRect.top - mapRect.top,
            width: barRect.width,
            height: barRect.height
        };
        return {
            height: rect.y + rect.height + FILTER_BAR_PADDING,
            rect
        };
    }

    /**
     * Validate marker instance before accessing its position.
     * @param {Object} marker - Leaflet marker.
     * @returns {boolean} True if marker can be used.
     */
    isValidMarker(marker) {
        return !!(marker && typeof marker.getLatLng === 'function' && marker._map);
    }

    /**
     * Build bounding boxes around markers for collision avoidance.
     * @param {Array} markers - Leaflet markers.
     * @param {Object} map - Leaflet map instance.
     * @returns {Array} Marker rectangles.
     */
    getMarkerBounds(markers, map) {
        if (!markers || !map) return [];
        return markers.map(marker => {
            if (!this.isValidMarker(marker)) return null;
            const pos = map.latLngToContainerPoint(marker.getLatLng());
            return {
                x: pos.x - MARKER_CLEARANCE,
                y: pos.y - MARKER_CLEARANCE,
                width: MARKER_CLEARANCE * 2,
                height: MARKER_CLEARANCE * 2
            };
        }).filter(Boolean);
    }
    
    /**
     * Calculate position for speech bubble relative to its marker
     * Bubbles spread like leaves around the marker, growing upward
     * @param {Object} markerPos - {x, y} marker screen position
     * @param {number} index - Bubble index for spread variation
     * @param {Array} occupiedRects - Existing bubble rectangles
     * @param {Array} markerBounds - Marker rectangles
     * @returns {Object} {x, y} position for bubble
     */
    calculateMarkerRelativePosition(markerPos, index, occupiedRects = [], markerBounds = []) {
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        const { height: filterBarHeight, rect: filterBarRect } = this.getFilterBarMetrics(mapContainer);
        const startAngle = index * GOLDEN_ANGLE;
        const seedBase = index * SEED_MULTIPLIER_X + SEED_OFFSET;

        for (let attempt = 0; attempt < MAX_POSITION_ATTEMPTS; attempt++) {
            const angle = startAngle + attempt * GOLDEN_ANGLE;
            const offset = BASE_SPREAD_OFFSET + Math.sqrt(attempt + index + SPREAD_BASE) * SPREAD_FACTOR;
            const offsetX = Math.cos(angle) * offset * HORIZONTAL_SPREAD_MULTIPLIER;
            const offsetY = -Math.abs(Math.sin(angle) * offset) - MARKER_VERTICAL_OFFSET;

            let x = markerPos.x + offsetX - BUBBLE_WIDTH / 2;
            let y = markerPos.y + offsetY - BUBBLE_HEIGHT;

            const seed = (seedBase + attempt) % 100;
            const organicX = ((seed % VARIATION_RANGE_X) - Math.floor(VARIATION_RANGE_X / 2));
            const organicY = (((seed * SEED_MULTIPLIER_Y) % VARIATION_RANGE_Y) - Math.floor(VARIATION_RANGE_Y / 2));

            x += organicX;
            y += organicY;

            x = Math.max(BUBBLE_MARGIN, Math.min(x, viewportWidth - BUBBLE_WIDTH - BUBBLE_MARGIN));
            y = Math.max(filterBarHeight + BUBBLE_MARGIN, Math.min(y, viewportHeight - BUBBLE_HEIGHT - BUBBLE_MARGIN));

            const bubbleRect = this.getBubbleRect(x, y);

            if (filterBarRect && this.rectanglesOverlap(bubbleRect, filterBarRect, BUBBLE_GUTTER)) {
                continue;
            }

            if (markerBounds && markerBounds.some(rect => this.rectanglesOverlap(bubbleRect, rect, BUBBLE_GUTTER))) {
                continue;
            }

            if (occupiedRects && occupiedRects.some(rect => this.rectanglesOverlap(bubbleRect, rect, BUBBLE_GUTTER))) {
                continue;
            }

            return { x, y };
        }

        let x = markerPos.x - BUBBLE_WIDTH / 2;
        let y = markerPos.y - MARKER_VERTICAL_OFFSET - BUBBLE_HEIGHT;
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
