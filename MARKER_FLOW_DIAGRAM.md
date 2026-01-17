# Marker Movement Feature - Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   USER INTERACTION FLOW                          │
└─────────────────────────────────────────────────────────────────┘

1. USER SELECTS LOCATION
   ┌──────────────────┐
   │  Location Filter │
   │  Dropdown        │
   └─────┬────────────┘
         │
         ├─→ "📍 From here" (Geolocation)
         │
         ├─→ "🚂 Hauptbahnhof Hof" (Predefined #1)
         │
         └─→ "☀️ Sonnenplatz Hof" (Predefined #2)


2. EVENT LISTENER TRIGGERED
   ┌─────────────────────────────────────────┐
   │  EventListeners.setupLocationDropdown() │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ if (value === 'geolocation')            │
   │   → updateReferenceMarker(              │
   │       userLocation.lat,                 │
   │       userLocation.lon,                 │
   │       'You are here'                    │
   │     )                                   │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ if (value.startsWith('predefined-'))    │
   │   → updateReferenceMarker(              │
   │       selectedLoc.lat,                  │
   │       selectedLoc.lon,                  │
   │       selectedLoc.display_name          │
   │     )                                   │
   └───────────────┬─────────────────────────┘


3. MAP MANAGER UPDATES MARKER
   ┌─────────────────────────────────────────┐
   │  MapManager.updateReferenceMarker()     │
   └───────────────┬─────────────────────────┘
                   │
                   ├─→ [1] Check if old marker exists
                   │      if (this.referenceMarker) {
                   │        referenceMarker.remove()
                   │        referenceMarker = null
                   │      }
                   │
                   ├─→ [2] Create new marker
                   │      referenceMarker = L.marker(
                   │        [lat, lon], 
                   │        { icon: userIcon, zIndexOffset: 1000 }
                   │      )
                   │
                   └─→ [3] Add to map with popup
                          .addTo(map)
                          .bindPopup(popupText)


4. VISUAL RESULT ON MAP
   ┌─────────────────────────────────────────┐
   │           MAP VIEW                      │
   │  ╔═══════════════════════════════════╗ │
   │  ║                                   ║ │
   │  ║     🎯 ← Reference Marker        ║ │
   │  ║     (Green circle with popup)     ║ │
   │  ║                                   ║ │
   │  ║  📍 Event markers (colored pins)  ║ │
   │  ║  📍 Event markers                ║ │
   │  ║     📍 Event markers             ║ │
   │  ║                                   ║ │
   │  ╚═══════════════════════════════════╝ │
   └─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   MARKER STATE DIAGRAM                           │
└─────────────────────────────────────────────────────────────────┘

Initial State:
┌───────────────────┐
│ referenceMarker   │
│ = null            │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ User gets         │
│ geolocation       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ referenceMarker   │
│ = Marker at       │
│   user location   │
│ Popup: "You are   │
│   here"           │
└─────────┬─────────┘
          │
          │ User selects predefined location
          ▼
┌───────────────────┐
│ OLD marker        │
│ removed           │ ←─── Old marker.remove()
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ referenceMarker   │
│ = Marker at       │
│   predefined loc  │ ←─── New marker created
│ Popup:            │
│   "Hauptbahnhof"  │
└───────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   KEY FEATURES                                   │
└─────────────────────────────────────────────────────────────────┘

✅ Single marker that moves (no duplicates)
✅ Old marker always removed before creating new one
✅ Marker positioned at exact coordinates of selected location
✅ Custom popup text for each location type
✅ Marker stays on top of event markers (zIndexOffset: 1000)
✅ Works with geolocation, predefined, and custom locations
✅ Map centers on new location automatically


┌─────────────────────────────────────────────────────────────────┐
│                   EXAMPLE SCENARIOS                              │
└─────────────────────────────────────────────────────────────────┘

Scenario 1: Switch from Geolocation to Predefined
  ┌──────────────────┐
  │ User at 50.3167, │  Step 1: Geolocation marker shown
  │ 11.9167          │  "You are here"
  └────────┬─────────┘
           │
           │ User clicks "Hauptbahnhof Hof"
           ▼
  ┌──────────────────┐
  │ Marker moves to  │  Step 2: Old marker removed,
  │ 50.308053,       │  new marker at Hauptbahnhof
  │ 11.9233          │  "Hauptbahnhof Hof"
  └──────────────────┘

Scenario 2: Switch between Predefined Locations
  ┌──────────────────┐
  │ At Hauptbahnhof  │  Step 1: Marker at train station
  │ 50.308053,       │  "Hauptbahnhof Hof"
  │ 11.9233          │
  └────────┬─────────┘
           │
           │ User clicks "Sonnenplatz Hof"
           ▼
  ┌──────────────────┐
  │ Marker moves to  │  Step 2: Old marker removed,
  │ 50.3164799,      │  new marker at Sonnenplatz
  │ 11.9146205       │  "Sonnenplatz Hof"
  └──────────────────┘
```

## Technical Implementation Details

### MapManager Class
```javascript
class MapManager {
    constructor() {
        this.referenceMarker = null;  // Track single reference marker
    }
    
    updateReferenceMarker(lat, lon, popupText) {
        // 1. Remove old marker
        if (this.referenceMarker) {
            this.referenceMarker.remove();
            this.referenceMarker = null;
        }
        
        // 2. Create new marker
        this.referenceMarker = L.marker([lat, lon], {
            icon: userIcon,
            zIndexOffset: 1000
        }).addTo(this.map).bindPopup(popupText);
    }
}
```

### Event Handler Integration
```javascript
// Geolocation
if (value === 'geolocation') {
    this.app.mapManager.updateReferenceMarker(
        userLocation.lat, 
        userLocation.lon, 
        'You are here'
    );
}

// Predefined
if (value.startsWith('predefined-')) {
    this.app.mapManager.updateReferenceMarker(
        selectedLoc.lat, 
        selectedLoc.lon, 
        selectedLoc.display_name
    );
}
```
