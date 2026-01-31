# IMMEDIATE FIX: Events Now Visible on Map

## Problem
**NO events were visible on map** due to overly restrictive default filter settings.

## Root Cause
Default filters were:
- `timeFilter: 'sunrise'` → Only shows events in next ~7 hours
- `maxDistance: 2` → Only shows events within 2km radius

With current event timestamps:
- 104 events in the PAST (filtered out)
- 46 events in FUTURE but most > 7 hours away
- **Result: 0 events passed the filter → empty map**

## The Fix
Changed default filter settings in `assets/js/app.js`:

```javascript
// BEFORE (too restrictive):
this.filters = {
    maxDistance: 2,        // Only 2km radius
    timeFilter: 'sunrise', // Only ~7 hours ahead
    ...
}

// AFTER (much better):
this.filters = {
    maxDistance: 50,       // 50km radius - shows more events
    timeFilter: '7d',      // 7 days ahead - shows WAY more events
    ...
}
```

## Result
**56 EVENTS NOW VISIBLE:**
- ✅ 46 events in next 7 days
- ✅ 10 demo events with `relative_time` (always current)
- ✅ User can still adjust filters via UI

## Files Changed
- `assets/js/app.js` → Changed default filter settings (lines 52-63)
- `public/index.html` → Regenerated with fix

## Testing
Run diagnostics:
```bash
python3 diagnose_events.py
python3 test_filter_logic.py
```

## Deploy
```bash
# Already done:
python3 src/event_manager.py generate

# Commit and push:
git add assets/js/app.js public/index.html
git commit -m "Fix: Change default filters to show events (50km, 7d)"
git push
```

## User Impact
- **BEFORE**: Empty map, 0 events visible ❌
- **AFTER**: 56 events visible immediately ✅
- Users can still filter down via UI controls
- Much better first-time experience

## Why This Wasn't Obvious
The data flow was PERFECT:
- ✅ Events in JSON
- ✅ Events embedded in HTML  
- ✅ JavaScript working
- ✅ Leaflet working

But the FILTER was too strict, silently removing all events before they reached the map.

## Prevention
Added diagnostic tools:
- `diagnose_events.py` - Full data flow check
- `test_filter_logic.py` - Filter testing
- Run these BEFORE assuming data issues
