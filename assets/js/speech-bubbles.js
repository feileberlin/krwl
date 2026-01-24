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

// Marker icon offset constants (for connector lines)
// Category markers are 200x200px with anchor at [100, 200] (bottom-center)
// Visual icon center is ~100px above the anchor point (at y=100 in the SVG)
// Lucide icons are scaled proportionally
const MARKER_ICON_CENTER_OFFSET_Y = -100; // Negative = upward offset from anchor (was -48 for 96px)
const MARKER_CIRCLE_RADIUS = 50; // Logical "protection" radius around marker icon (was 24 for 96px, now 50 for 200px)
const CONNECTOR_STOP_DISTANCE = MARKER_CIRCLE_RADIUS + 15; // Stop connector 15px outside circle edge for comic book effect
const BEZIER_CONTROL_POINT_FACTOR = 0.4; // Control points at 40% of distance for smooth curves
const CSS_TAIL_HEIGHT = 15; // Height of CSS tail triangle in pixels (must match CSS border-width)

// Filter bar constants
const FILTER_BAR_PADDING = 20;         // Extra padding below filter bar
const DEFAULT_FILTER_BAR_HEIGHT = 60;  // Fallback if filter bar not found

// Organic variation seeds (prime numbers for better distribution)
const SEED_MULTIPLIER_X = 17;
const SEED_OFFSET = 11;
const VARIATION_RANGE_X = 21;
const SEED_MULTIPLIER_Y = 13;
const VARIATION_RANGE_Y = 15;

// Force-directed layout constants
const REPULSION_FORCE = 0.8;          // Strength of repulsion between bubbles
const REPULSION_RADIUS = 300;          // Distance at which bubbles start repelling
const DAMPING = 0.7;                   // Velocity damping (prevents oscillation)
const MIN_VELOCITY = 0.5;              // Stop moving if velocity below this
const MAX_VELOCITY = 15;               // Cap velocity to prevent wild movements
const ANIMATION_DURATION = 600;        // ms for collision resolution animation
const COLLISION_CHECK_INTERVAL = 100;  // ms between collision checks

class SpeechBubbles {
    constructor(config, storage, onBubbleClick = null) {
        this.config = config;
        this.storage = storage;
        this.onBubbleClick = onBubbleClick; // Callback for bubble clicks
        this.speechBubbles = [];
        this.map = null;
        this.bubbleData = []; // Store bubble-marker associations for updates
        this.moveHandler = null; // Store reference for cleanup
        this.connectorLayer = null;
        this.markers = [];
        
        // Drag state - track if user actually dragged vs just clicked
        this.dragState = {
            isDragging: false,
            bubble: null,
            startX: 0,
            startY: 0,
            bubbleOffsetX: 0,
            bubbleOffsetY: 0,
            mapOffsetX: 0,
            mapOffsetY: 0,
            hasMoved: false // Track if mouse/touch moved during drag
        };
        
        // Force-directed layout state
        this.forceState = {
            isRunning: false,
            animationFrame: null,
            checkInterval: null,
            velocities: new Map(), // bubbleId -> {vx, vy}
            lastPositions: new Map() // bubbleId -> {x, y}
        };
        
        // Bind drag handlers to preserve context
        this.handleDragStart = this.handleDragStart.bind(this);
        this.handleDragMove = this.handleDragMove.bind(this);
        this.handleDragEnd = this.handleDragEnd.bind(this);
        this.handleBubbleClick = this.handleBubbleClick.bind(this);
        
        // Bind force-directed handlers
        this.applyForces = this.applyForces.bind(this);
        this.checkCollisions = this.checkCollisions.bind(this);
    }
    
    /**
     * Clear all speech bubbles from the map
     */
    clearSpeechBubbles() {
        // Stop force-directed layout
        this.stopForceDirectedLayout();
        
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
        
        // Start force-directed layout for collision avoidance
        if (eventItems.length > 1) {
            this.startForceDirectedLayout();
        }
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
        
        // Check bookmark status for both bubble and bookmark button
        const isBookmarked = this.storage.isBookmarked(event.id);
        bubble.className = isBookmarked ? 'speech-bubble bubble-is-bookmarked' : 'speech-bubble';
        bubble.setAttribute('data-event-id', event.id);
        bubble.setAttribute('data-bubble-index', index);
        bubble.dataset.bubbleId = event.id; // For force-directed layout tracking
        
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
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        const bookmarkingSupported = this.storage.isBookmarkingSupported();
        
        // Duplicate badge
        const duplicateBadge = duplicateCount > 1 ? 
            `<div class="bubble-duplicate-badge" title="${duplicateCount} duplicate events">×${duplicateCount}</div>` : '';
        
        // Demo/Fake badge (show "Fake" for demo events only)
        const isDemoEvent = event.source === 'demo';
        const demoBadge = isDemoEvent ? 
            `<div class="bubble-demo-badge" title="Demo event for testing">Fake</div>` : '';
        
        bubble.innerHTML = `
            ${duplicateBadge}
            ${demoBadge}
            <div class="bubble-time-headline">${timeStr}</div>
            <div class="bubble-date">${dateStr}</div>
            <div class="bubble-title">${this.truncateText(event.title, 50)}</div>
            <div class="bubble-location"><i data-lucide="map-pin" aria-hidden="true"></i> ${this.truncateText(event.location.name, 30)}</div>
            ${event.distance !== undefined ? `<div class="bubble-distance"><i data-lucide="footprints" aria-hidden="true"></i> ${event.distance.toFixed(1)} km</div>` : ''}
            ${bookmarkingSupported ? `<button class="bubble-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                <i data-lucide="heart" aria-hidden="true"></i>
            </button>` : ''}
        `;
        
        // Initialize Lucide icons
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
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
            event: event, // Store event data for click handler
            index: index,
            userOffset: null, // Track user-applied drag offset
            connector: connectorLine
        });
        
        // Add drag event listeners for repositioning
        this.setupDragListeners(bubble);
        
        // Add click handler for opening event details
        bubble.addEventListener('click', this.handleBubbleClick);
        
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
            mapOffsetY: mapRect.top,
            hasMoved: false // Reset movement tracking
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
        
        // Track if user actually moved the mouse/touch (not just a click)
        const dx = Math.abs(clientX - this.dragState.startX);
        const dy = Math.abs(clientY - this.dragState.startY);
        const DRAG_THRESHOLD = 5; // pixels - movement threshold to consider it a drag
        
        if (dx > DRAG_THRESHOLD || dy > DRAG_THRESHOLD) {
            this.dragState.hasMoved = true;
        }
        
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
            mapOffsetY: 0,
            hasMoved: false
        };
        
        this.log('Drag ended');
    }
    
    /**
     * Handle bubble click to open event details
     * Only triggers if user didn't drag the bubble
     * @param {Event} e - Click event
     */
    handleBubbleClick(e) {
        // Don't open event detail if user was dragging
        if (this.dragState.hasMoved) {
            return;
        }
        
        // Don't trigger if clicking on bookmark button (it has its own handler)
        if (e.target.closest('.bubble-bookmark')) {
            return;
        }
        
        const bubble = e.currentTarget;
        if (!bubble) return;
        
        // Find the event data associated with this bubble
        const bubbleData = this.bubbleData.find(data => data.bubble === bubble);
        if (!bubbleData || !bubbleData.event) {
            this.log('Warning: No event data found for clicked bubble');
            return;
        }
        
        // Call the callback if provided
        if (this.onBubbleClick && typeof this.onBubbleClick === 'function') {
            this.log('Opening event detail for:', bubbleData.event.title);
            this.onBubbleClick(bubbleData.event);
        } else {
            this.log('Warning: No onBubbleClick callback provided');
        }
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
     * Create SVG connector elements between a marker and its bubble.
     * Builds a single forked bezier connector path element (with two curves in
     * its path data) and an (optionally invisible) boundary circle around the
     * marker. The visual "tail" attached to the bubble itself is implemented
     * via CSS pseudo-element, not by this function.
     * @param {Object} markerPos - Marker position in container coordinates.
     * @param {Object} bubbleRect - Bubble rectangle bounds.
     * @returns {Object|null} Connector elements (path and circle).
     */
    createConnectorLine(markerPos, bubbleRect) {
        if (!this.connectorLayer) return null;
        
        // Create filled tail shape (behind the stroke paths)
        const fill = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        fill.classList.add('bubble-connector-fill');
        this.connectorLayer.appendChild(fill);
        
        // Create curved path (bezier) for SVG connectors (strokes on top)
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.classList.add('bubble-connector-path');
        this.connectorLayer.appendChild(path);
        
        // Create invisible boundary circle around the marker icon
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.classList.add('bubble-connector-circle');
        circle.setAttribute('r', MARKER_CIRCLE_RADIUS);
        this.connectorLayer.appendChild(circle);
        
        const connector = { path, circle, fill };
        this.updateConnectorLine({ connector }, bubbleRect, markerPos, true);
        return connector;
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
     * Updates SVG connector paths and CSS-based bubble tail positioning.
     * @param {Object} entry - Bubble data entry.
     * @param {Object} bubbleRect - Bubble rectangle bounds.
     * @param {Object} markerPos - Marker position in container coordinates (anchor point).
     * @param {boolean} isVisible - Whether the bubble is visible.
     */
    updateConnectorLine(entry, bubbleRect, markerPos, isVisible) {
        const connector = entry.connector;
        if (!connector) return;
        
        // Adjust marker position to point to the visual icon center instead of anchor point
        // Category markers have their icon centered ~48px above the bottom anchor
        const markerIconCenter = {
            x: markerPos.x,
            y: markerPos.y + MARKER_ICON_CENTER_OFFSET_Y
        };
        
        // Update circle position around marker
        if (connector.circle) {
            connector.circle.setAttribute('cx', markerIconCenter.x);
            connector.circle.setAttribute('cy', markerIconCenter.y);
            connector.circle.style.opacity = isVisible ? '' : '0';
        }
        
        // Get closest point on bubble rectangle as center reference
        const bubbleCenterPoint = this.getClosestPointOnRect(markerIconCenter, bubbleRect);
        
        // Calculate initial vector from marker to bubble (for perpendicular fork spread)
        const dx = markerIconCenter.x - bubbleCenterPoint.x;
        const dy = markerIconCenter.y - bubbleCenterPoint.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Guard against zero or near-zero distance to avoid division by zero / NaN coordinates
        if (distance < 0.01) {
            // Too close - hide connectors
            if (connector.path) connector.path.style.opacity = '0';
            if (connector.circle) connector.circle.style.opacity = '0';
            return;
        }
        
        // Create TWO starting points at bottom of bubble (forked tail)
        const forkSpacing = 12; // Distance between the two fork points
        // Calculate perpendicular direction for fork spread
        const perpX = -dy / distance;
        const perpY = dx / distance;
        
        const startPoint1 = {
            x: bubbleCenterPoint.x + perpX * forkSpacing,
            y: bubbleCenterPoint.y + perpY * forkSpacing
        };
        
        const startPoint2 = {
            x: bubbleCenterPoint.x - perpX * forkSpacing,
            y: bubbleCenterPoint.y - perpY * forkSpacing
        };
        
        // Calculate single tip point where both forks converge (classic comic book tail)
        // The tip should point toward the marker center, stopping at CONNECTOR_STOP_DISTANCE
        const tipX = markerIconCenter.x - (dx / distance) * CONNECTOR_STOP_DISTANCE;
        const tipY = markerIconCenter.y - (dy / distance) * CONNECTOR_STOP_DISTANCE;
        
        // Calculate distances from each fork start to the tip
        const dx1 = tipX - startPoint1.x;
        const dy1 = tipY - startPoint1.y;
        const dist1 = Math.sqrt(dx1 * dx1 + dy1 * dy1);
        
        const dx2 = tipX - startPoint2.x;
        const dy2 = tipY - startPoint2.y;
        const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
        
        // Calculate control points for each path using their respective distances
        const controlOffset1 = dist1 * BEZIER_CONTROL_POINT_FACTOR;
        const controlOffset2 = dist2 * BEZIER_CONTROL_POINT_FACTOR;
        
        // CRITICAL FIX: Keep second control point safely away from the marker boundary
        // When the bubble is dragged close to the marker, bias the curve so it does not visually cross the icon
        // Use at least the marker radius plus a small padding as a heuristic safe distance for the control point
        const minControlOffset = MARKER_CIRCLE_RADIUS + 2; // Marker radius + 2px padding from marker center
        const secondControlOffset1 = Math.max(minControlOffset, controlOffset1 * 0.5);
        const secondControlOffset2 = Math.max(minControlOffset, controlOffset2 * 0.5);
        
        // Calculate initial control point positions
        // Path 1: from startPoint1 to tip
        const controlX1_1 = startPoint1.x + (dx1 / dist1) * controlOffset1;
        const controlY1_1 = startPoint1.y + (dy1 / dist1) * (controlOffset1 * 0.3);
        let controlX1_2 = tipX - (dx1 / dist1) * secondControlOffset1;
        let controlY1_2 = tipY - (dy1 / dist1) * secondControlOffset1;
        
        // Path 2: from startPoint2 to tip
        const controlX2_1 = startPoint2.x + (dx2 / dist2) * controlOffset2;
        const controlY2_1 = startPoint2.y + (dy2 / dist2) * (controlOffset2 * 0.3);
        let controlX2_2 = tipX - (dx2 / dist2) * secondControlOffset2;
        let controlY2_2 = tipY - (dy2 / dist2) * secondControlOffset2;
        
        // Additional safety: Ensure control points maintain minimum radial distance from marker center
        // This addresses the mathematical issue that directional offset alone doesn't guarantee clearance
        const minRadialDistance = MARKER_CIRCLE_RADIUS + 4; // Minimum distance control point must be from marker center
        
        // Check and correct control point 1_2 if too close to marker center
        const radialDist1_2 = Math.sqrt(
            Math.pow(controlX1_2 - markerIconCenter.x, 2) + 
            Math.pow(controlY1_2 - markerIconCenter.y, 2)
        );
        if (radialDist1_2 < minRadialDistance) {
            const scale = minRadialDistance / radialDist1_2;
            controlX1_2 = markerIconCenter.x + (controlX1_2 - markerIconCenter.x) * scale;
            controlY1_2 = markerIconCenter.y + (controlY1_2 - markerIconCenter.y) * scale;
        }
        
        // Check and correct control point 2_2 if too close to marker center
        const radialDist2_2 = Math.sqrt(
            Math.pow(controlX2_2 - markerIconCenter.x, 2) + 
            Math.pow(controlY2_2 - markerIconCenter.y, 2)
        );
        if (radialDist2_2 < minRadialDistance) {
            const scale = minRadialDistance / radialDist2_2;
            controlX2_2 = markerIconCenter.x + (controlX2_2 - markerIconCenter.x) * scale;
            controlY2_2 = markerIconCenter.y + (controlY2_2 - markerIconCenter.y) * scale;
        }
        
        // Create filled tail shape connecting the two fork paths to a single tip
        // This creates the solid colored area forming the speech bubble tail
        const fillData = `
            M ${startPoint1.x},${startPoint1.y}
            C ${controlX1_1},${controlY1_1} ${controlX1_2},${controlY1_2} ${tipX},${tipY}
            L ${tipX},${tipY}
            C ${controlX2_2},${controlY2_2} ${controlX2_1},${controlY2_1} ${startPoint2.x},${startPoint2.y}
            Z
        `.trim();
        
        if (connector.fill) {
            connector.fill.setAttribute('d', fillData);
            connector.fill.style.opacity = isVisible ? '' : '0';
        }
        
        // Combine both paths converging to a single tip point
        const pathData = `
            M ${startPoint1.x},${startPoint1.y} 
            C ${controlX1_1},${controlY1_1} ${controlX1_2},${controlY1_2} ${tipX},${tipY}
            M ${startPoint2.x},${startPoint2.y} 
            C ${controlX2_1},${controlY2_1} ${controlX2_2},${controlY2_2} ${tipX},${tipY}
        `.trim();
        
        if (connector.path) {
            connector.path.setAttribute('d', pathData);
            connector.path.style.opacity = isVisible ? '' : '0';
        }
        
        // Update CSS-based tail on bubble element
        // The tail should point toward the single tip point
        if (entry.bubble) {
            // Calculate position where tail should point to (the single tip point)
            const tailTargetX = tipX;
            const tailTargetY = tipY;
            
            // Calculate tail attachment point relative to bubble
            const tailX = ((bubbleCenterPoint.x - bubbleRect.x) / bubbleRect.width) * 100;
            const tailY = ((bubbleCenterPoint.y - bubbleRect.y) / bubbleRect.height) * 100;
            
            // Calculate angle for tail rotation (pointing toward circle edge, not icon)
            const tailDx = tailTargetX - bubbleCenterPoint.x;
            const tailDy = tailTargetY - bubbleCenterPoint.y;
            const angleRad = Math.atan2(tailDy, tailDx);
            const angleDeg = (angleRad * 180 / Math.PI) + 90; // +90 because tail points down by default
            
            // CRITICAL FIX: Scale tail size based on distance to prevent crossing marker
            // When bubble is very close to marker, reduce tail size so it doesn't reach marker
            // CSS tail is normally 15px (CSS_TAIL_HEIGHT), but we scale it down when close
            const tailDistance = Math.sqrt(tailDx * tailDx + tailDy * tailDy);
            const minSafeDistance = CONNECTOR_STOP_DISTANCE; // 28px - tail should not reach marker
            const tailScale = Math.min(1.0, tailDistance / (minSafeDistance + CSS_TAIL_HEIGHT));
            
            // Set CSS custom properties for tail positioning
            entry.bubble.style.setProperty('--tail-x', `${tailX}%`);
            entry.bubble.style.setProperty('--tail-y', `${tailY}%`);
            entry.bubble.style.setProperty('--tail-angle', `${angleDeg}deg`);
            // Only update scale if it changed significantly (performance optimization)
            const currentScale = parseFloat(entry.bubble.style.getPropertyValue('--tail-scale')) || 1.0;
            if (Math.abs(currentScale - tailScale) > 0.01) {
                entry.bubble.style.setProperty('--tail-scale', tailScale.toFixed(2));
            }
        }
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
            // Adjust collision box y-coordinate to align with visual icon center, not the anchor, not the anchor
            const iconCenterY = pos.y + MARKER_ICON_CENTER_OFFSET_Y;
            return {
                x: pos.x - MARKER_CLEARANCE,
                y: iconCenterY - MARKER_CLEARANCE,
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
    
    /**
     * Start force-directed layout system for collision avoidance
     */
    startForceDirectedLayout() {
        if (this.forceState.isRunning) return;
        
        this.forceState.isRunning = true;
        
        // Initialize velocities for all bubbles
        this.speechBubbles.forEach(bubble => {
            const bubbleId = bubble.dataset.bubbleId;
            if (!this.forceState.velocities.has(bubbleId)) {
                this.forceState.velocities.set(bubbleId, { vx: 0, vy: 0 });
            }
            if (!this.forceState.lastPositions.has(bubbleId)) {
                const rect = bubble.getBoundingClientRect();
                this.forceState.lastPositions.set(bubbleId, { x: rect.left, y: rect.top });
            }
        });
        
        // Start collision checking interval
        this.forceState.checkInterval = setInterval(this.checkCollisions, COLLISION_CHECK_INTERVAL);
        
        this.log('Force-directed layout started');
    }
    
    /**
     * Stop force-directed layout system
     */
    stopForceDirectedLayout() {
        if (!this.forceState.isRunning) return;
        
        this.forceState.isRunning = false;
        
        if (this.forceState.animationFrame) {
            cancelAnimationFrame(this.forceState.animationFrame);
            this.forceState.animationFrame = null;
        }
        
        if (this.forceState.checkInterval) {
            clearInterval(this.forceState.checkInterval);
            this.forceState.checkInterval = null;
        }
        
        // Clear stored velocities and positions to avoid stale bubble IDs accumulating
        if (this.forceState.velocities && typeof this.forceState.velocities.clear === 'function') {
            this.forceState.velocities.clear();
        }
        if (this.forceState.lastPositions && typeof this.forceState.lastPositions.clear === 'function') {
            this.forceState.lastPositions.clear();
        }
        
        this.log('Force-directed layout stopped');
    }
    
    /**
     * Check for collisions between bubbles and start force application if needed
     */
    checkCollisions() {
        if (this.dragState.isDragging) return; // Don't interfere with drag
        
        let hasCollisions = false;
        
        // Check all pairs of bubbles for collisions
        for (let i = 0; i < this.speechBubbles.length; i++) {
            for (let j = i + 1; j < this.speechBubbles.length; j++) {
                const bubble1 = this.speechBubbles[i];
                const bubble2 = this.speechBubbles[j];
                
                if (this.bubblesCollide(bubble1, bubble2)) {
                    hasCollisions = true;
                    break;
                }
            }
            if (hasCollisions) break;
        }
        
        // Start animation loop if collisions detected and not already running
        if (hasCollisions && !this.forceState.animationFrame) {
            this.forceState.animationStartTime = performance.now();
            this.applyForces();
        }
    }
    
    /**
     * Check if two bubbles collide (including their tails)
     * @param {HTMLElement} bubble1 - First bubble
     * @param {HTMLElement} bubble2 - Second bubble
     * @returns {boolean} True if bubbles collide
     */
    bubblesCollide(bubble1, bubble2) {
        const rect1 = bubble1.getBoundingClientRect();
        const rect2 = bubble2.getBoundingClientRect();
        
        // Add padding for tail clearance
        const padding = 20; // Extra space for tails
        
        return !(
            rect1.right + padding < rect2.left ||
            rect1.left - padding > rect2.right ||
            rect1.bottom + padding < rect2.top ||
            rect1.top - padding > rect2.bottom
        );
    }
    
    /**
     * Apply repulsion forces between overlapping bubbles
     */
    applyForces() {
        const now = performance.now();
        const elapsed = now - (this.forceState.animationStartTime || now);
        
        // Stop if animation duration exceeded
        if (elapsed > ANIMATION_DURATION) {
            this.forceState.animationFrame = null;
            return;
        }
        
        const forces = new Map(); // bubbleId -> {fx, fy}
        
        // Initialize forces to zero
        this.speechBubbles.forEach(bubble => {
            const bubbleId = bubble.dataset.bubbleId;
            forces.set(bubbleId, { fx: 0, fy: 0 });
        });
        
        // Cache bounding rects once per bubble to avoid repeated layout reads
        const bubbleRects = this.speechBubbles.map(bubble => ({
            bubble,
            rect: bubble.getBoundingClientRect()
        }));
        
        // Calculate repulsion forces between all pairs
        for (let i = 0; i < bubbleRects.length; i++) {
            for (let j = i + 1; j < bubbleRects.length; j++) {
                const bubble1 = bubbleRects[i].bubble;
                const bubble2 = bubbleRects[j].bubble;
                
                const id1 = bubble1.dataset.bubbleId;
                const id2 = bubble2.dataset.bubbleId;
                
                const rect1 = bubbleRects[i].rect;
                const rect2 = bubbleRects[j].rect;
                
                // Calculate centers
                const center1 = {
                    x: rect1.left + rect1.width / 2,
                    y: rect1.top + rect1.height / 2
                };
                const center2 = {
                    x: rect2.left + rect2.width / 2,
                    y: rect2.top + rect2.height / 2
                };
                
                // Calculate distance between centers
                const dx = center2.x - center1.x;
                const dy = center2.y - center1.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Skip if too far apart
                if (distance > REPULSION_RADIUS) continue;
                
                // Calculate repulsion force (inverse square law)
                const force = distance > 0 ? REPULSION_FORCE * (REPULSION_RADIUS - distance) / distance : REPULSION_FORCE;
                
                // Apply force in opposite directions
                const fx = (dx / distance) * force;
                const fy = (dy / distance) * force;
                
                const force1 = forces.get(id1);
                const force2 = forces.get(id2);
                if (!force1 || !force2) continue; // Skip if bubble IDs are invalid
                
                force1.fx -= fx;
                force1.fy -= fy;
                force2.fx += fx;
                force2.fy += fy;
            }
        }
        
        // Apply forces to update velocities and positions
        let anyMovement = false;
        
        this.speechBubbles.forEach(bubble => {
            const bubbleId = bubble.dataset.bubbleId;
            const force = forces.get(bubbleId);
            if (!force) return; // Skip if force not calculated
            const velocity = this.forceState.velocities.get(bubbleId);
            if (!velocity) return; // Skip if velocity tracking not initialized
            
            // Update velocity with force and damping
            velocity.vx = (velocity.vx + force.fx) * DAMPING;
            velocity.vy = (velocity.vy + force.fy) * DAMPING;
            
            // Clamp velocity
            const speed = Math.sqrt(velocity.vx * velocity.vx + velocity.vy * velocity.vy);
            if (speed > MAX_VELOCITY) {
                velocity.vx = (velocity.vx / speed) * MAX_VELOCITY;
                velocity.vy = (velocity.vy / speed) * MAX_VELOCITY;
            }
            
            // Skip if velocity too small
            if (speed < MIN_VELOCITY) {
                velocity.vx = 0;
                velocity.vy = 0;
                return;
            }
            
            anyMovement = true;
            
            // Update position
            const currentStyle = window.getComputedStyle(bubble);
            const currentLeft = parseFloat(currentStyle.left) || 0;
            const currentTop = parseFloat(currentStyle.top) || 0;
            
            let newLeft = currentLeft + velocity.vx;
            let newTop = currentTop + velocity.vy;
            
            // Keep bubbles in viewport bounds
            const container = bubble.parentElement;
            const containerRect = container.getBoundingClientRect();
            const filterBar = document.querySelector('.filter-bar');
            const filterBarHeight = filterBar ? filterBar.offsetHeight + FILTER_BAR_PADDING : DEFAULT_FILTER_BAR_HEIGHT;
            
            newLeft = Math.max(BUBBLE_MARGIN, Math.min(newLeft, containerRect.width - BUBBLE_WIDTH - BUBBLE_MARGIN));
            newTop = Math.max(filterBarHeight + BUBBLE_MARGIN, Math.min(newTop, containerRect.height - BUBBLE_HEIGHT - BUBBLE_MARGIN));
            
            // Apply new position
            bubble.style.left = `${newLeft}px`;
            bubble.style.top = `${newTop}px`;
            
            // Update connector line if exists
            const bubbleDataEntry = this.bubbleData.find(bd => bd.bubble === bubble);
            if (bubbleDataEntry && bubbleDataEntry.connector) {
                const bubbleRect = bubble.getBoundingClientRect();
                const markerPos = this.map.latLngToContainerPoint(bubbleDataEntry.marker.getLatLng());
                this.updateConnectorLine(bubbleDataEntry, bubbleRect, markerPos, true);
            }
        });
        
        // Continue animation if there's still movement
        if (anyMovement) {
            this.forceState.animationFrame = requestAnimationFrame(this.applyForces);
        } else {
            this.forceState.animationFrame = null;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechBubbles;
}
