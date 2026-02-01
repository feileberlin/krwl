# Custom Location Region Issue - Code Flow Visualization

## Current Broken Flow 🔴

```javascript
// 1. User visits /hof
window.location.pathname = '/hof'

// 2. app.js constructor (line ~30)
constructor(config) {
    // 3. Create storage BEFORE region detection
    this.storage = new EventStorage(config);  // ❌ activeRegion not set yet!
}

// 4. EventStorage constructor (storage.js line ~13)
constructor(config) {
    this.config = config;
    this.customLocations = this.loadCustomLocations();  // ❌ No regionId parameter
    this.initializeDefaultCustomLocations();            // ❌ Uses global config
}

// 5. initializeDefaultCustomLocations (storage.js line ~36)
initializeDefaultCustomLocations() {
    const predefinedLocs = this.config?.map?.predefined_locations || [];  
    // ❌ PROBLEM: Uses global predefined_locations (Antarctica data)
    // ✅ SHOULD USE: this.app.activeRegionConfig.customFilters (Hof data)
    
    predefinedLocs.forEach((loc) => {
        this.customLocations.push({
            name: loc.display_name,  // "🐧 Penguin HQ" ❌
            lat: loc.lat,            // -89.999 (Antarctica) ❌
            lon: loc.lon             // 45.0 (Antarctica) ❌
        });
    });
}

// 6. LATER: app.js applyRegionFromUrl (line ~105)
applyRegionFromUrl() {
    const regionId = 'hof';
    const region = this.config.regions[regionId];
    
    this.activeRegion = regionId;           // ✅ Set to 'hof'
    this.activeRegionConfig = region;       // ✅ Has customFilters for Hof
    
    // ❌ BUT: customLocations already initialized with Antarctica data!
    // ❌ No reload happens
}

// 7. User sees in dashboard dropdown:
//    🐧 Penguin HQ (-89.999, 45.0)  ❌ WRONG REGION!
//    🧊 Ice Cube Bar (-89.998, -90.0)  ❌ WRONG REGION!
```

---

## Fixed Flow ✅

```javascript
// 1. User visits /hof
window.location.pathname = '/hof'

// 2. app.js constructor (line ~30)
constructor(config) {
    // 3. Detect region FIRST
    this.applyRegionFromUrl();  // ✅ Set activeRegion early
    
    // 4. Create storage AFTER region detection
    this.storage = new EventStorage(config, this);  // ✅ Pass 'this' (app instance)
}

// 5. EventStorage constructor (storage.js line ~13) - MODIFIED
constructor(config, app) {
    this.config = config;
    this.app = app;  // ✅ Store reference to app
    
    // ✅ Load region-specific locations
    const regionId = this.app?.activeRegion || 'hof';
    this.customLocations = this.loadCustomLocations(regionId);  // ✅ Pass regionId
    this.initializeDefaultCustomLocations();  // ✅ Now uses activeRegionConfig
}

// 6. initializeDefaultCustomLocations (storage.js line ~36) - MODIFIED
initializeDefaultCustomLocations() {
    if (this.customLocations.length > 0) {
        return;  // Already initialized
    }
    
    // ✅ Use region-specific customFilters
    const regionConfig = this.app?.activeRegionConfig;
    const predefinedLocs = regionConfig?.customFilters || 
                           this.config?.map?.predefined_locations || [];
    
    predefinedLocs.forEach((loc) => {
        this.customLocations.push({
            id: `custom_${loc.id}_${Date.now()}`,
            name: loc.name?.de || loc.name?.en || loc.display_name,  // ✅ "Innenstadt"
            lat: loc.center?.lat || loc.lat,   // ✅ 50.3197 (Hof)
            lon: loc.center?.lng || loc.center?.lon || loc.lon,  // ✅ 11.9177 (Hof)
            created: new Date().toISOString(),
            fromPredefined: true
        });
    });
    
    if (this.customLocations.length > 0) {
        this.saveCustomLocations();  // ✅ Saves to localStorage[regionId]
    }
}

// 7. loadCustomLocations (storage.js line ~238) - MODIFIED
loadCustomLocations(regionId) {
    try {
        const allLocations = localStorage.getItem('krwl_custom_locations');
        if (allLocations) {
            const parsed = JSON.parse(allLocations);
            
            // ✅ Backward compatibility
            if (Array.isArray(parsed)) {
                return parsed;  // Old global format
            }
            
            // ✅ New per-region format
            return parsed[regionId] || [];
        }
    } catch (error) {
        console.warn('Failed to load custom locations:', error);
    }
    return [];
}

// 8. saveCustomLocations (storage.js line ~255) - MODIFIED
saveCustomLocations() {
    try {
        const regionId = this.app?.activeRegion || 'hof';
        
        // Load existing data
        let allLocations = {};
        const existing = localStorage.getItem('krwl_custom_locations');
        if (existing) {
            const parsed = JSON.parse(existing);
            if (!Array.isArray(parsed)) {
                allLocations = parsed;
            }
        }
        
        // ✅ Update this region's locations
        allLocations[regionId] = this.customLocations;
        
        // ✅ Save back to localStorage
        localStorage.setItem('krwl_custom_locations', JSON.stringify(allLocations));
    } catch (error) {
        console.warn('Failed to save custom locations:', error);
    }
}

// 9. User sees in dashboard dropdown (for /hof):
//    Innenstadt (50.3197, 11.9177)  ✅ CORRECT!
//    Altstadt (50.3220, 11.9150)  ✅ CORRECT!
//    Theresienstein (50.3289, 11.9089)  ✅ CORRECT!

// 10. User visits /nbg
window.location.pathname = '/nbg'

// 11. Region changes in app.js (line ~180) - ADD NEW CODE
applyRegionFromUrl() {
    const regionId = 'nbg';
    const region = this.config.regions[regionId];
    
    this.activeRegion = regionId;
    this.activeRegionConfig = region;
    
    // ✅ NEW: Reload custom locations for this region
    if (this.storage) {
        this.storage.customLocations = this.storage.loadCustomLocations(regionId);
        this.storage.initializeDefaultCustomLocations();
    }
}

// 12. User now sees in dashboard dropdown (for /nbg):
//     Altstadt (49.4541, 11.0767)  ✅ Nuremberg's Altstadt!
//     Gostenhof (49.4580, 11.0580)  ✅ Nuremberg location!
//     Südstadt (49.4350, 11.0800)  ✅ Nuremberg location!
```

---

## localStorage Structure Change

### Before (Global - BROKEN) 🔴
```javascript
localStorage.getItem('krwl_custom_locations')
// Returns:
[
  {
    id: "custom_location.no1_1738434000000",
    name: "🐧 Penguin HQ",
    lat: -89.999,
    lon: 45.0,
    fromPredefined: true
  },
  {
    id: "custom_location.no2_1738434000001", 
    name: "🧊 Ice Cube Bar",
    lat: -89.998,
    lon: -90.0,
    fromPredefined: true
  }
]
```

**Problem:** Same locations shown for ALL regions!

### After (Per-Region - FIXED) ✅
```javascript
localStorage.getItem('krwl_custom_locations')
// Returns:
{
  "hof": [
    {
      id: "custom_innenstadt_1738434000000",
      name: "Innenstadt",
      lat: 50.3197,
      lon: 11.9177,
      fromPredefined: true
    },
    {
      id: "custom_my_home_1738434000001",
      name: "My Home",
      lat: 50.3250,
      lon: 11.9200,
      fromPredefined: false  // User-added
    }
  ],
  "nbg": [
    {
      id: "custom_altstadt_1738434000002",
      name: "Altstadt",
      lat: 49.4541,
      lon: 11.0767,
      fromPredefined: true
    }
  ],
  "antarctica": [
    {
      id: "custom_penguin_hq_1738434000003",
      name: "🐧 Penguin HQ",
      lat: -89.999,
      lon: 45.0,
      fromPredefined: true
    }
  ]
}
```

**Solution:** Each region has its own custom locations array!

---

## Data Structure Mapping

### config.json - Global (DEPRECATED)
```javascript
{
  "map": {
    "predefined_locations": [
      {
        "name": "location.no1",           // ← Simple string key
        "display_name": "🐧 Penguin HQ",  // ← Display string
        "lat": -89.999,                   // ← Direct lat
        "lon": 45.0                       // ← Direct lon
      }
    ]
  }
}
```

### config.json - Per-Region (ACTIVE)
```javascript
{
  "regions": {
    "hof": {
      "customFilters": [
        {
          "id": "innenstadt",                    // ← Unique ID
          "name": {                              // ← i18n object
            "de": "Innenstadt",
            "en": "City Center"
          },
          "center": {                            // ← Nested center object
            "lat": 50.3197,
            "lng": 11.9177                       // ← Note: "lng" not "lon"!
          },
          "radius": 1.5,                         // ← Additional fields
          "zoom": 14
        }
      ]
    }
  }
}
```

### Mapping Code (storage.js)
```javascript
// OLD CODE (global predefined_locations)
predefinedLocs.forEach((loc) => {
    this.customLocations.push({
        id: `custom_${loc.name}_${Date.now()}`,
        name: loc.display_name,  // Simple string
        lat: loc.lat,            // Direct property
        lon: loc.lon             // Direct property
    });
});

// NEW CODE (region customFilters)
predefinedLocs.forEach((loc) => {
    this.customLocations.push({
        id: `custom_${loc.id}_${Date.now()}`,
        name: loc.name?.de || loc.name?.en || loc.display_name,  // i18n or fallback
        lat: loc.center?.lat || loc.lat,                         // Nested or direct
        lon: loc.center?.lng || loc.center?.lon || loc.lon,     // Handle both lng/lon
        created: new Date().toISOString(),
        fromPredefined: true
    });
});
```

---

## Constructor Order Issue

### Current Order (BROKEN) 🔴
```javascript
// app.js
class EventApp {
    constructor(config) {
        this.config = config;
        
        // 1. Storage created FIRST
        this.storage = new EventStorage(config);  // ❌ activeRegion = undefined
        
        // 2. Region detected LATER
        this.applyRegionFromUrl();  // ✅ activeRegion = 'hof'
        
        // 3. Map initialized LATER
        this.mapManager = new MapManager(config, this.eventFilter);
    }
}
```

**Problem:** Storage doesn't know which region to load!

### Fixed Order ✅
```javascript
// app.js
class EventApp {
    constructor(config) {
        this.config = config;
        
        // 1. Region detected FIRST
        this.applyRegionFromUrl();  // ✅ activeRegion = 'hof'
        
        // 2. Storage created with region context
        this.storage = new EventStorage(config, this);  // ✅ Pass app instance
        
        // 3. Map initialized with correct region
        this.mapManager = new MapManager(config, this.eventFilter);
    }
}

// storage.js
class EventStorage {
    constructor(config, app) {  // ✅ Accept app parameter
        this.config = config;
        this.app = app;  // ✅ Store reference
        
        // ✅ Now has access to app.activeRegion and app.activeRegionConfig
        const regionId = this.app?.activeRegion || 'hof';
        this.customLocations = this.loadCustomLocations(regionId);
        this.initializeDefaultCustomLocations();
    }
}
```

---

## Testing Scenarios

### Scenario 1: Fresh Installation (No localStorage)
```javascript
// User visits /hof for first time
// Expected: Loads Hof's customFilters

localStorage.getItem('krwl_custom_locations')  // null

// After initialization:
localStorage.getItem('krwl_custom_locations')
// {
//   "hof": [
//     { name: "Innenstadt", lat: 50.3197, lon: 11.9177 },
//     { name: "Altstadt", lat: 50.3220, lon: 11.9150 },
//     { name: "Theresienstein", lat: 50.3289, lon: 11.9089 }
//   ]
// }
```

### Scenario 2: Migration from Old Format
```javascript
// User has old global format
localStorage.getItem('krwl_custom_locations')
// [{ name: "🐧 Penguin HQ", lat: -89.999, lon: 45.0 }]

// After first save in /hof:
localStorage.getItem('krwl_custom_locations')
// {
//   "hof": [
//     { name: "Innenstadt", ... },
//     { name: "My Home", ... }  // User-added
//   ]
// }

// Old global data is replaced (migrated)
```

### Scenario 3: Region Switching
```javascript
// User in /hof, adds custom location
this.storage.addCustomLocation({ name: "My Home", lat: 50.3250, lon: 11.9200 });

localStorage.getItem('krwl_custom_locations')
// { "hof": [..., { name: "My Home" }] }

// User navigates to /nbg
window.location.pathname = '/nbg'
// Triggers: app.applyRegionFromUrl()
// Calls: storage.loadCustomLocations('nbg')

localStorage.getItem('krwl_custom_locations')
// {
//   "hof": [..., { name: "My Home" }],  // ✅ Still there!
//   "nbg": [{ name: "Altstadt", ... }]
// }

// User navigates back to /hof
window.location.pathname = '/hof'
// "My Home" reappears! ✅
```

---

## Summary

**Root Cause:** Constructor order + missing region context in EventStorage

**Solution:** 
1. Detect region before creating storage
2. Pass app reference to storage
3. Load/save custom locations per region
4. Reload when region changes

**Impact:** Low risk, high value - fixes UX issue for all multi-region deployments

**Files Changed:** 2 files, ~50 lines of code

**Backward Compatible:** Yes - supports old localStorage format

**Testing Required:** Manual testing across all 6 regions
