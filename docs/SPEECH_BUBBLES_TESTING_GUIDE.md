# Speech Bubble Feature Testing Guide

## Overview
This guide explains how to manually test the speech bubble (comic bubble) feature to verify it's working correctly.

## Prerequisites
- Local development environment with Python 3
- Generated `public/index.html` file
- Events data (real or demo)

## Setup
```bash
# Generate the site with events
python3 src/event_manager.py generate

# Start local server
cd public
python3 -m http.server 8000

# Open in browser
# Navigate to: http://localhost:8000
```

## What Speech Bubbles Are
Speech bubbles are **the complete event details**, displayed as comic-style info cards floating around event markers on the map. They are NOT preview cards that open separate panels.

## Complete Feature Checklist

### Visual Appearance ✓
- [ ] Bubbles appear automatically when page loads
- [ ] Bubbles have dark backdrop with pink border glow
- [ ] Each bubble shows triangular "tail" pointing toward its marker
- [ ] Curved connector line (SVG path) connects bubble to marker
- [ ] Fade-in animation when bubbles appear
- [ ] Hover effect: bubble scales up slightly with stronger glow

### Content Display ✓
- [ ] **Time** (headline, prominent, pink color) - e.g., "3:30 PM"
- [ ] **Date** - e.g., "Sat, Jan 4"
- [ ] **Title** - Event name (truncated to 50 chars if needed)
- [ ] **Location** 📍 - With map pin icon (truncated to 30 chars)
- [ ] **Distance** 👣 - Walking distance in km (e.g., "2.5 km")
- [ ] **Bookmark button** ❤️ - Heart icon (outlined when not bookmarked, filled when bookmarked)
- [ ] **Duplicate badge** (if multiple events with same title) - Yellow badge showing "×N"
- [ ] **Demo badge** (for test events) - Red "Fake" badge

### Interactivity ✓
- [ ] **Dragging**: Click and drag bubble to reposition it
  - Cursor changes to "grab" on hover
  - Cursor changes to "grabbing" while dragging
  - Bubble scales up and shows elevated shadow while dragging
  - Map panning is disabled while dragging
  - Bubble stays at new position after release
  
- [ ] **Bookmark**: Click heart button inside bubble
  - Heart fills with red color when bookmarked
  - Toast notification appears: "Event bookmarked!"
  - Bookmarked events bypass filters (always visible)
  - Clicking heart again unbookmarks

- [ ] **Map Movement**: Pan or zoom the map
  - Bubbles follow their markers
  - User-repositioned bubbles maintain relative offset
  - Connector lines update smoothly
  - Bubbles hide when marker goes off-screen

### Positioning ✓
- [ ] Maximum 20 bubbles shown (closest events by distance)
- [ ] Bubbles don't overlap with each other
- [ ] Bubbles don't overlap with filter bar at top
- [ ] Bubbles don't overlap with markers
- [ ] Bubbles stay within viewport bounds
- [ ] Golden angle spiral distribution around markers

### Responsive Design ✓
- [ ] **Desktop** (> 768px):
  - Bubbles: 220px wide
  - Font size: 0.85rem
  - Full positioning flexibility

- [ ] **Mobile** (≤ 768px):
  - Bubbles: 180px wide (smaller)
  - Font size: 0.75rem (smaller)
  - Still draggable via touch
  - Stay within mobile viewport

### Bookmark Feature ✓
- [ ] Bookmark up to 15 events
- [ ] 16th bookmark removes oldest
- [ ] Bookmarks persist on page reload (localStorage)
- [ ] Bookmarked bubbles show red border instead of pink
- [ ] Bookmarked bubble text changes to red shades
- [ ] Bookmarked events always visible (bypass filters)

### Performance ✓
- [ ] Only 20 bubbles maximum (performance optimization)
- [ ] Smooth animations (no lag)
- [ ] Efficient updates on map move
- [ ] No memory leaks (check browser DevTools)

## Common Issues & Solutions

### Issue: Bubbles Don't Appear
**Possible Causes:**
1. No events in filtered results
2. Map not initialized (Leaflet library not loaded)
3. Events outside configured distance filter

**Solution:**
- Check browser console for errors
- Verify events data exists in `assets/json/events.json`
- Try expanding distance filter to "within 10 km" or more

### Issue: Connector Lines Missing
**Possible Causes:**
1. SVG layer not created
2. JavaScript error preventing connector creation

**Solution:**
- Inspect DOM: look for `<svg class="bubble-connectors">` element
- Check browser console for JavaScript errors

### Issue: Bubbles Overlap
**Possible Causes:**
1. Force-directed layout not running
2. Too many events in small area

**Solution:**
- Manually drag overlapping bubbles to separate them
- Wait a few seconds for collision resolution to complete
- Check console for "[SpeechBubbles] Force-directed layout started"

### Issue: Drag Not Working
**Possible Causes:**
1. JavaScript error
2. Browser doesn't support pointer events

**Solution:**
- Check browser console for errors
- Try different browser (Chrome, Firefox, Safari all supported)
- On mobile, ensure touch events are enabled

## Testing on Production
The speech bubble feature works on any deployment where:
- Leaflet.js loads successfully (from CDN or local)
- Events data is present
- Map initializes correctly

Test on actual deployment URL to verify CDN dependencies load correctly.

## Automated Testing
Currently, speech bubbles require visual/manual testing because:
- They depend on Leaflet map library
- They involve complex DOM positioning
- They use CSS transforms and animations

Automated tests exist for:
- Event data structure validation
- Configuration validation
- Dependency resilience

## Feature Complete ✅
All speech bubble features are fully implemented as of January 2026:
- Visual design (comic-style with tails)
- Content display (time, date, title, location, distance)
- Interactivity (dragging, bookmarking)
- Positioning (collision-aware, responsive)
- Performance (limited to 20 bubbles)

**No additional features needed** unless new requirements are defined.
