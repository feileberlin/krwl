# Custom Location Region-Specific Feature - Analysis Complete ✅

## Your Questions Answered

### 1. Which modules/files handle custom locations?

**Primary Module: `assets/js/storage.js` (EventStorage class)**
- `loadCustomLocations()` - Lines 238-250
- `saveCustomLocations()` - Lines 255-263  
- `initializeDefaultCustomLocations()` - Lines 29-55
- `addCustomLocation()`, `deleteCustomLocation()`, etc.

**Secondary Modules:**
- `assets/js/app.js` - Uses storage.customLocations
- `assets/html/filter-nav.html` - Displays custom location dropdown UI
- `assets/js/filter-description-ui.js` - Uses predefined_locations for display

### 2. Which modules/files handle regions and map centering?

**Primary Module: `assets/js/app.js` (EventApp class)**
- `applyRegionFromUrl()` - Lines 105-181
  - Detects region from URL path (e.g., `/hof`, `/nbg`)
  - Sets `this.activeRegion` (e.g., 'hof')
  - Sets `this.activeRegionConfig` (full region object from config.json)
  - Applies region-specific map center and zoom

**Secondary Module: `assets/js/map.js` (MapManager class)**
- `initMap()` - Lines 58-90
  - Initializes Leaflet map with region-specific center
- `centerMap(lat, lon)` - Centers map on specific coordinates

**Configuration: `config.json`**
- `regions.{hof,nbg,bth,selb,rawetz,antarctica}` - All region configs

### 3. Dependencies between these features?

```
config.json (regions + customFilters)
    ↓
app.js (detects region, sets activeRegion/activeRegionConfig)
    ↓
storage.js (❌ should use activeRegionConfig but doesn't)
    ↓
UI (displays custom locations)
```

**Feature Dependencies (from features.json):**
```
interactive-map (base)
  ↑ used_by
  ├── geolocation-filtering
  │     ↑ used_by
  │     └── custom-location ← YOUR FEATURE
  │
  └── custom-location ← YOUR FEATURE
```

### 4. What files need to be modified?

**ONLY 2 FILES need changes:**

#### File 1: `assets/js/storage.js` (HIGH PRIORITY)

**Change 1 - Line 36 (initializeDefaultCustomLocations):**
```javascript
// BEFORE
const predefinedLocs = this.config?.map?.predefined_locations || [];

// AFTER  
const regionConfig = this.app?.activeRegionConfig;
const predefinedLocs = regionConfig?.customFilters || 
                       this.config?.map?.predefined_locations || [];

// ALSO: Handle data structure difference
predefinedLocs.forEach((loc) => {
    this.customLocations.push({
        id: `custom_${loc.id}_${Date.now()}`,
        name: loc.name?.de || loc.name?.en || loc.display_name,  // i18n support
        lat: loc.center?.lat || loc.lat,   // customFilters use 'center'
        lon: loc.center?.lng || loc.center?.lon || loc.lon,
        created: new Date().toISOString(),
        fromPredefined: true
    });
});
```

**Change 2 - Line 238 (loadCustomLocations):**
```javascript
// BEFORE
loadCustomLocations() {
    const locationsData = localStorage.getItem('krwl_custom_locations');
    if (locationsData) {
        return JSON.parse(locationsData);
    }
    return [];
}

// AFTER
loadCustomLocations(regionId) {
    const allLocations = localStorage.getItem('krwl_custom_locations');
    if (allLocations) {
        const parsed = JSON.parse(allLocations);
        
        // Backward compatibility: support old array format
        if (Array.isArray(parsed)) {
            return parsed;  // Old global format
        }
        
        // New format: per-region object
        return parsed[regionId] || [];
    }
    return [];
}
```

**Change 3 - Line 255 (saveCustomLocations):**
```javascript
// BEFORE
saveCustomLocations() {
    const locationsData = JSON.stringify(this.customLocations);
    localStorage.setItem('krwl_custom_locations', locationsData);
}

// AFTER
saveCustomLocations() {
    const regionId = this.app?.activeRegion || 'hof';
    
    // Load all regions' locations
    let allLocations = {};
    try {
        const existing = localStorage.getItem('krwl_custom_locations');
        if (existing) {
            const parsed = JSON.parse(existing);
            if (!Array.isArray(parsed)) {
                allLocations = parsed;
            }
        }
    } catch (e) {
        console.warn('Failed to parse existing custom locations:', e);
    }
    
    // Update this region's locations
    allLocations[regionId] = this.customLocations;
    
    // Save back
    localStorage.setItem('krwl_custom_locations', JSON.stringify(allLocations));
}
```

**Change 4 - Line 18 (constructor):**
```javascript
// BEFORE
this.customLocations = this.loadCustomLocations();

// AFTER
this.customLocations = this.loadCustomLocations(this.app?.activeRegion);
```

#### File 2: `assets/js/app.js` (MEDIUM PRIORITY)

**Change 1 - Line ~180 (after activeRegion is set):**
```javascript
// After these lines:
this.activeRegion = regionId;
this.activeRegionConfig = region;

// ADD THIS:
// Reload custom locations for this region
if (this.storage) {
    this.storage.customLocations = this.storage.loadCustomLocations(regionId);
    this.storage.initializeDefaultCustomLocations();
}
```

---

## The Root Cause

**Problem:** `storage.js` initializes custom locations from global `config.map.predefined_locations` (Antarctica demo data) instead of region-specific `activeRegionConfig.customFilters`.

**Why it happens:** 
1. `storage.js` is instantiated before region detection completes
2. `initializeDefaultCustomLocations()` runs in constructor, before `activeRegion` is set
3. No mechanism to reload custom locations when region changes

**Evidence:**
```javascript
// config.json - Global predefined locations (WRONG)
"map": {
  "predefined_locations": [
    { "name": "location.no1", "lat": -89.999, "display_name": "🐧 Penguin HQ" },
    { "name": "location.no2", "lat": -89.998, "display_name": "🧊 Ice Cube Bar" }
  ]
}

// config.json - Region-specific customFilters (CORRECT)
"regions": {
  "hof": {
    "customFilters": [
      { "id": "innenstadt", "name": {"de": "Innenstadt"}, "center": {lat: 50.3197, lng: 11.9177} },
      { "id": "altstadt", "name": {"de": "Altstadt"}, "center": {lat: 50.3220, lng: 11.9150} },
      { "id": "theresienstein", "name": {"de": "Theresienstein"}, "center": {lat: 50.3289, lng: 11.9089} }
    ]
  }
}
```

---

## Verification - All Regions Have customFilters ✅

| Region      | customFilters Count | Example Locations |
|-------------|---------------------|-------------------|
| hof         | 3                   | Innenstadt, Altstadt, Theresienstein |
| nbg         | 3                   | Altstadt, Gostenhof, Südstadt |
| bth         | 3                   | Innenstadt, Festspielhaus, Universität |
| selb        | 1                   | Innenstadt |
| rawetz      | 1                   | Marktplatz |
| antarctica  | 2                   | 🐧 Penguin HQ, 🧊 Ice Cube Bar |

**All regions already have the data!** We just need to use it.

---

## Impact Analysis

### What Breaks If Not Fixed?

1. **User sees wrong locations** - Antarctica locations shown in Hof
2. **Distance filtering broken** - Filters calculate distance from Antarctica instead of Hof
3. **Confusing UX** - Map centers on Hof but dropdown shows Penguin HQ
4. **No region-specific customization** - Can't have different custom locations per region

### What Depends On This Feature?

From `features.json`:
- **custom-location** (this feature) depends on:
  - `interactive-map` ✅
  - `geolocation-filtering` ✅
  
- **geolocation-filtering** depends on:
  - `interactive-map` ✅
  - `custom-location` (uses custom location for distance calculations)

**Risk if broken:** High - Core UX feature for multi-region deployments

---

## Testing Plan

```bash
# Test 1: Hof region
# Open: http://localhost:8000/hof
# Expected custom locations: Innenstadt, Altstadt, Theresienstein

# Test 2: Nuremberg region  
# Open: http://localhost:8000/nbg
# Expected custom locations: Altstadt, Gostenhof, Südstadt

# Test 3: Antarctica region
# Open: http://localhost:8000/antarctica
# Expected custom locations: 🐧 Penguin HQ, 🧊 Ice Cube Bar

# Test 4: Persistence across region switches
# 1. Add custom location in /hof ("My Home")
# 2. Navigate to /nbg
# 3. Navigate back to /hof
# Expected: "My Home" location still exists in Hof

# Test 5: Backward compatibility
# 1. Set old localStorage format: ['custom_1', 'custom_2']
# 2. Reload page
# Expected: Works without errors, migrates to new format on save
```

---

## Complexity Estimate

- **Files to change:** 2 files
- **Lines of code:** ~50 lines total
- **Risk level:** Low (additive changes, backward compatible)
- **Testing effort:** 30 minutes (manual testing across regions)
- **Implementation time:** 1-2 hours

**Why low risk?**
- Changes are localized to storage.js and app.js
- Backward compatibility built in (supports old localStorage format)
- No breaking changes to existing APIs
- All regions already have customFilters data

---

## Next Steps

1. ✅ **Analysis complete** - You now understand the architecture
2. 📝 **Create implementation plan** - Detail step-by-step changes
3. 🔨 **Implement changes** - Modify storage.js and app.js
4. 🧪 **Test across all regions** - Verify Hof, Nuremberg, Antarctica
5. 📚 **Update documentation** - Update features.json, add ADR if needed

---

## Key Files for Reference

- **CUSTOM_LOCATION_REGION_ANALYSIS.md** - Full detailed analysis (17KB)
- **features.json** - Feature registry (custom-location entry)
- **config.json** - Region configuration (regions.*.customFilters)
- **docs/architecture.md** - System architecture overview
- **docs/MULTI_REGION_INFRASTRUCTURE.md** - Multi-region setup guide
- **.github/copilot-instructions.md** - Project conventions

---

**Questions? Ask the complexity-manager agent!**
