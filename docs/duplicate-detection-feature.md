# Duplicate Event Detection Feature - Visual Guide

## 🎯 Feature Overview

The duplicate detection feature automatically scans all loaded events and displays warnings in the dashboard debug section when duplicates are found.

## 📊 Visual Examples

### Example 1: No Duplicates (Success State)
```
┌─────────────────────────────────────────────┐
│ Debug Info                                  │
│ ┌─────────────────────────────────────────┐ │
│ │ Last commit: 2b96235                    │ │
│ │ Events: 15/0/3  Env: DEV                │ │
│ │ Cache: Disabled  Size: 222.4 KB        │ │
│ │ DOM: 3 elements  Hist: Backend (Python)│ │
│ │                                          │ │
│ │ ┌─────────────────────────────────────┐ │ │
│ │ │ ✓ No duplicates                     │ │ │
│ │ └─────────────────────────────────────┘ │ │
│ │                                          │ │
│ │ index.html size breakdown:              │ │
│ │ Scripts: 85.3 KB (38.3%)                │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Example 2: Duplicates Detected (Warning State)
```
┌─────────────────────────────────────────────┐
│ Debug Info                                  │
│ ┌─────────────────────────────────────────┐ │
│ │ Last commit: 2b96235                    │ │
│ │ Events: 15/0/3  Env: DEV                │ │
│ │ Cache: Disabled  Size: 222.4 KB        │ │
│ │ DOM: 3 elements  Hist: Backend (Python)│ │
│ │                                          │ │
│ │ ┌─────────────────────────────────────┐ │ │
│ │ │ ⚠️ 3 duplicates detected            │ │ │
│ │ │                                      │ │ │
│ │ │ Summer Festival (3x)                │ │ │
│ │ │ Jul 15, 6:00 PM at City Park        │ │ │
│ │ │                                      │ │ │
│ │ │ Market Day (2x)                     │ │ │
│ │ │ Jul 20, 10:00 AM at Town Square    │ │ │
│ │ └─────────────────────────────────────┘ │ │
│ │                                          │ │
│ │ index.html size breakdown:              │ │
│ │ Scripts: 85.3 KB (38.3%)                │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## 🎨 Color Coding

**Success State (No Duplicates):**
- Background: EcoBarbie Light Tone tint (rgba(214, 137, 184, 0.15))
- Border: EcoBarbie Light Tone (rgba(214, 137, 184, 0.3))
- Text: EcoBarbie Light Tone (#D689B8)
- Icon: ✓ (checkmark)

**Warning State (Duplicates Found):**
- Background: Orange tint (rgba(217, 119, 6, 0.15))
- Border: Orange (rgba(217, 119, 6, 0.3))
- Text: Orange (#f59e0b)
- Icon: ⚠️ (warning triangle)

## 🔍 Detection Logic

### Duplicate Identification
Events are considered duplicates if they have:

**Option 1: Same Event ID**
```javascript
event1.id === event2.id
// e.g., both have id: "event-123"
```

**Option 2: Same Title + Start Time + Location**
```javascript
event1.title === event2.title &&
event1.start_time === event2.start_time &&
event1.location.lat === event2.location.lat &&
event1.location.lon === event2.location.lon
```

### Example Duplicate Scenarios

**Scenario 1: Same Event ID**
```json
[
  { "id": "event-1", "title": "Concert", "start_time": "2026-07-15T18:00:00" },
  { "id": "event-1", "title": "Concert", "start_time": "2026-07-15T18:00:00" }
]
// ✗ Duplicate detected (same ID)
```

**Scenario 2: Same Title/Time/Location (no ID)**
```json
[
  { 
    "title": "Market Day", 
    "start_time": "2026-07-20T10:00:00",
    "location": { "name": "Town Square", "lat": 50.3150, "lon": 11.9180 }
  },
  { 
    "title": "Market Day", 
    "start_time": "2026-07-20T10:00:00",
    "location": { "name": "Town Square", "lat": 50.3150, "lon": 11.9180 }
  }
]
// ✗ Duplicate detected (same title + time + location)
```

**Scenario 3: Similar but NOT Duplicates**
```json
[
  { 
    "title": "Market Day", 
    "start_time": "2026-07-20T10:00:00",
    "location": { "name": "Town Square", "lat": 50.3150, "lon": 11.9180 }
  },
  { 
    "title": "Market Day", 
    "start_time": "2026-07-27T10:00:00",  // Different date
    "location": { "name": "Town Square", "lat": 50.3150, "lon": 11.9180 }
  }
]
// ✓ Not duplicates (different start times)
```

## 📍 Where to Find It

1. Open the KRWL HOF app
2. Click the project logo (top-left) to open dashboard
3. Scroll down to "Debug Info" section
4. Look for the duplicate detection box (below cache stats, above size breakdown)

## 🔧 Technical Details

### Functions Added

**`detectDuplicateEvents()`**
- Scans `this.events` array
- Creates unique keys for each event
- Counts occurrences
- Returns array of duplicates with counts

**`updateDuplicateWarnings()`**
- Called from `updateDashboard()`
- Gets duplicate info from `detectDuplicateEvents()`
- Updates DOM element `#debug-duplicates`
- Shows warning or success message

### Files Modified

1. **assets/js/app.js** - Added duplicate detection functions
2. **assets/css/style.css** - Added duplicate warning styles
3. **assets/html/dashboard-aside.html** - Added duplicate warnings HTML element
4. **public/index.html** - Applied all changes to generated file

### CSS Classes

- `.debug-duplicates` - Container for duplicate info
- `.debug-duplicates.warning` - Warning state (orange)
- `.debug-duplicates.ok` - Success state (green)
- `.duplicate-warning` - Warning text style
- `.duplicate-ok` - Success text style
- `.duplicate-details` - Container for duplicate list
- `.duplicate-item` - Individual duplicate entry
- `.duplicate-hint` - Subtitle with time/location info

## 🧪 Testing

**Test File:** `tests/test_duplicate_detection_demo.html`

**Scenarios:**
1. No duplicates (3 unique events) → Shows ✓ success
2. One duplicate (2 identical events) → Shows ⚠️ warning
3. Multiple duplicates (5 events with 2 duplicate groups) → Shows ⚠️ warning with details

## 🎉 Benefits

- ✅ **Automatic Detection**: No manual checking needed
- ✅ **Visual Feedback**: Clear warnings when duplicates exist
- ✅ **Detailed Info**: Shows which events are duplicated and how many times
- ✅ **Performance**: Efficient scanning using Map data structure
- ✅ **Developer Tool**: Helps identify data quality issues

---

**Last Updated**: 2026-01-05
**Feature Version**: 1.0
**Status**: ✅ Implemented and Working
