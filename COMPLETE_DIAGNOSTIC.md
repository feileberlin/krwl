# COMPLETE DIAGNOSTIC REPORT: Why No Flyers Show on Map

## Current Configuration (Reverted to Original)
- **defaultRegion**: `"hof"` (Germany, lat 50.3167, lon 11.9167)
- **Filter maxDistance**: `5 km` (from config.json)
- **Filter timeFilter**: `"sunrise"` (~7 hours from now)

## The Chain of Failures

### 1. TIME FILTER ISSUE
**Problem**: All 139 events near Hof are in the PAST (already happened)
- Current time: 2026-01-31 19:31
- Sunrise filter: Show events until 2026-02-01 02:31 (~7 hours)
- **Result**: 0 events from Hof pass the time filter

### 2. DISTANCE FILTER ISSUE  
**Problem**: The 10 events with `relative_time` (always current) are in ANTARCTICA
- Antarctica location: lat -90.0
- Hof location: lat 50.3167
- **Distance: 15,603 km**
- Filter maxDistance: 5 km
- **Result**: All Antarctica events filtered out by distance

### 3. COMBINED RESULT
**TIME filter removes Hof events (old) + DISTANCE filter removes Antarctica events (too far)**
**= ZERO events visible on map**

## What Needs to Happen

### Option A: Fresh Events (Best for Production)
```bash
# Re-scrape to get current events near Hof
python3 src/event_manager.py scrape

# Publish pending events
python3 src/event_manager.py bulk-publish '*'

# Regenerate
python3 src/event_manager.py generate
```

### Option B: Update Event Timestamps (Quick Fix for Demo)
Add `relative_time` to some Hof events to make them always current:
```json
{
  "id": "some_hof_event",
  "title": "Event in Hof",
  "location": {"lat": 50.3167, "lon": 11.9167, "name": "Hof"},
  "relative_time": {
    "type": "offset",
    "minutes": 30,
    "duration_hours": 2
  }
}
```

### Option C: Relax Filters Temporarily (Testing Only)
Change filters in `assets/js/app.js`:
```javascript
this.filters = {
    maxDistance: 100,  // Show events up to 100km
    timeFilter: '7d',  // Show events for next 7 days
    ...
}
```

## Why Your Original Settings Are Correct

- **defaultRegion: "hof"** ✅ Correct - This is for HOF users!
- **maxDistance: 5km** ✅ Correct - Reasonable city radius
- **timeFilter: "sunrise"** ✅ Correct - Shows imminent events

## The REAL Problem

**The events data is STALE.** All 139 Hof events are from mid-January 2026 and it's now end of January. They've all passed.

## Recommended Fix

1. Keep all settings as they are (hof, 5km, sunrise)
2. Run scraper to get fresh events
3. Or manually add test events with relative_time near Hof

## Status of Components

✅ Flyer template code - WORKING
✅ Leaflet integration - WORKING  
✅ JavaScript event loading - WORKING
✅ Filter logic - WORKING (correctly filtering out stale events)
✅ Distance calculation - WORKING
❌ Event data - STALE (need fresh scraping)
