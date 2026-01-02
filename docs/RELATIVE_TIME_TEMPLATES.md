# Relative Time Event Templates

## Overview

The KRWL HOF event system supports **dynamic event templates** with relative time specifications. This feature allows demo events to always display accurate relative times like "happening now" or "starting in 5 minutes" on every page reload, without requiring manual timestamp updates.

## How It Works

### Backend: Template Generation

Demo events are generated with a `relative_time` field that specifies how to calculate actual timestamps dynamically:

```json
{
  "id": "demo_happening_now",
  "title": "[DEMO] Event Happening Now",
  "relative_time": {
    "type": "offset",
    "minutes": -30,
    "duration_hours": 2
  }
}
```

### Frontend: Dynamic Processing

When the app loads, the `processTemplateEvents()` method in `app.js` detects events with `relative_time` specifications and calculates actual timestamps based on the current browser time:

```javascript
// Original template event
{
  "start_time": "2026-01-02T12:00:00",  // Static timestamp
  "relative_time": { "type": "offset", "minutes": 5 }
}

// Processed event (calculated at page load)
{
  "start_time": "2026-01-02T14:18:32",  // Current time + 5 minutes
  "relative_time": { "type": "offset", "minutes": 5 }
}
```

## Relative Time Specifications

### Type 1: Offset (Relative to Current Time)

Events that occur relative to the current moment:

```json
{
  "type": "offset",
  "hours": 1,           // Optional: hours offset from now
  "minutes": 5,         // Optional: minutes offset from now
  "duration_hours": 2,  // Event duration in hours
  "timezone_offset": 0  // Optional: timezone offset for testing
}
```

**Examples:**
- `{"type": "offset", "minutes": -30, "duration_hours": 2}` - Started 30 minutes ago
- `{"type": "offset", "minutes": 5, "duration_hours": 2}` - Starts in 5 minutes
- `{"type": "offset", "hours": 1, "duration_hours": 3}` - Starts in 1 hour, lasts 3 hours

### Type 2: Sunrise Relative (Relative to Next Sunrise)

Events that occur relative to the next sunrise (simplified as 6:00 AM):

```json
{
  "type": "sunrise_relative",
  "start_offset_hours": -2,    // Optional: hours offset for start time
  "start_offset_minutes": 0,   // Optional: minutes offset for start time
  "end_offset_hours": 0,       // Optional: hours offset for end time
  "end_offset_minutes": -5     // Optional: minutes offset for end time
}
```

**Examples:**
- `{"type": "sunrise_relative", "end_offset_minutes": -5, "start_offset_hours": -2}` - Ends 5 minutes before sunrise
- `{"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}` - Starts 2 hours before sunrise, ends 1 hour after

## Timezone Support

For international testing, events can specify timezone offsets:

```json
{
  "type": "offset",
  "hours": 1,
  "duration_hours": 2,
  "timezone_offset": 1  // UTC+1
}
```

This generates timestamps like `2026-01-02T14:07:41+01:00`.

## Usage

### Generating Demo Events

Run the demo event generator script:

```bash
python3 scripts/generate_demo_events.py > event-data/events.demo.json
```

This creates template events with relative_time specifications.

### Testing

Run the test suite to verify relative time processing:

```bash
# Python tests
python3 tests/test_relative_times.py

# Interactive HTML test
open tests/test_relative_times.html
```

### Regenerating the Site

After updating demo events, regenerate the static site:

```bash
# Copy demo events to static directory
cp event-data/events.demo.json static/events.demo.json

# Regenerate HTML
python3 src/event_manager.py generate
```

## Implementation Details

### Backend (`scripts/generate_demo_events.py`)

The script generates events with:
1. Static timestamps (for backward compatibility)
2. `relative_time` field (for dynamic processing)

### Frontend (`assets/js/app.js`)

The `processTemplateEvents()` method:
1. Detects events with `relative_time` field
2. Calculates actual timestamps based on current browser time
3. Returns a **new copy** of each event (no mutation)
4. Preserves events without `relative_time` unchanged

### Integration Flow

```
Demo Events (JSON)
    ↓
window.ALL_EVENTS (embedded in HTML)
    ↓
window.ACTIVE_EVENTS (filtered by config)
    ↓
fetch intercept (returns embedded data)
    ↓
loadEvents() in app.js
    ↓
processTemplateEvents() (calculates timestamps)
    ↓
Display events with fresh timestamps
```

## Benefits

1. **Always Fresh**: Demo events always show accurate relative times
2. **Filter Testing**: Test time-based filters (sunrise, 6h, 12h) with realistic data
3. **Timezone Testing**: Verify international time handling
4. **No Maintenance**: No need to manually update demo event timestamps
5. **Backward Compatible**: Real events without `relative_time` work unchanged

## Edge Cases

- **Events without `relative_time`**: Passed through unchanged
- **Invalid specifications**: Fallback to 2-hour duration
- **Timezone offsets**: Properly formatted in ISO 8601 format
- **Sunrise calculation**: Simplified to 6:00 AM (can be enhanced with actual calculations)

## Future Enhancements

Possible improvements:
- Real sunrise/sunset calculation based on geolocation
- Support for more relative time types (e.g., "next Monday", "end of week")
- Configurable sunrise time via settings
- Support for recurring events with relative times

## See Also

- [Event Schema Documentation](../tests/README.md)
- [Testing Guide](../tests/test_relative_times.py)
- [Demo Event Generator](../scripts/generate_demo_events.py)
