# ADR-001: Fallback List When Map Fails

**Status**: Accepted  
**Date**: 2026-02-01  
**Deciders**: @feileberlin, Development Team  
**Tags**: frontend, progressive-enhancement, accessibility

## Context

The KRWL> application relies on Leaflet.js for interactive map visualization of community events. However, map loading can fail due to several reasons:

- **Network Issues**: CDN unavailable, slow/blocked connections
- **Script Blocking**: Ad blockers, privacy extensions, corporate firewalls
- **Browser Compatibility**: Old browsers, JavaScript disabled
- **CDN Failures**: unpkg.com or other CDNs experiencing downtime

When the map fails to load, users see either a blank page or a cryptic error. This creates a poor user experience and makes the application unusable in many real-world scenarios.

## Decision

We implemented a **fallback list view** that displays events in a scrollable list format when Leaflet.js fails to load or initialize.

**Implementation Details:**
- JavaScript checks for Leaflet object (`typeof L === 'undefined'`)
- If map fails, renders events as HTML cards in a list container
- List includes all event information (name, date, location, description)
- Users can still filter, search, and interact with events
- Fallback is automatic—no user intervention required

**Files Affected:**
- `assets/js/app.js` - Map initialization and fallback logic
- `assets/js/map.js` - MapManager class with error handling
- `assets/css/style.css` - Fallback list styles

## Consequences

### Positive

- **Resilience**: Application remains functional even when map breaks
- **Progressive Enhancement**: Core functionality works regardless of environment
- **Accessibility**: Users without JavaScript or in restricted networks can still access content
- **Better UX**: Graceful degradation instead of complete failure
- **Mobile-Friendly**: List view works well on small screens

### Negative

- **Maintenance Burden**: Must maintain two display modes (map + list)
- **Code Complexity**: Additional branching logic for fallback detection
- **Testing Overhead**: Need to test both map and fallback modes
- **Feature Parity**: Some map-specific features (clustering, panning) unavailable in list mode

### Neutral

- **Performance**: List view is actually faster to render than map with many markers
- **Design Consistency**: Both modes use same event card components
- **State Management**: Filters and search work identically in both modes

## Alternatives Considered

### 1. Server-Side Rendering of Static Map
**Rejected**: Requires external API (Google Maps Static, etc.), increases cost and complexity

### 2. Inline Leaflet.js Instead of CDN
**Partially Adopted**: We inline Leaflet when building, but still need CDN fallback for development and edge cases

### 3. Require Map to Function
**Rejected**: Violates progressive enhancement principles, excludes users with restricted networks

### 4. Show Error Message Only
**Rejected**: Doesn't help users access event data, poor UX

## Related Decisions

- **features.json**: `interactive-map` (id: interactive-map)
- **features.json**: `event-cards` (id: event-cards) - Used in fallback list
- **DEPENDENCIES.md**: Frontend Module Dependency Map showing map.js relationships
- **ADR-002**: Vanilla JS Over Frameworks - Enables lightweight fallback without framework overhead

## Verification

Test the fallback by blocking Leaflet.js from loading:

**Method 1: Block CDN in DevTools**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Right-click on any request → "Block request domain"
4. Add `unpkg.com` to blocked domains
5. Reload page → should see fallback list view

**Method 2: Simulate build without Leaflet**
1. Edit `src/modules/site_generator.py` to skip Leaflet inlining temporarily
2. Run `python3 src/event_manager.py generate`
3. Open `public/index.html` → should fallback to list view

## References

- [Progressive Enhancement - MDN](https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement)
- [Resilient Web Design](https://resilientwebdesign.com/)
- Issue: *(Original issue that prompted this decision)*
