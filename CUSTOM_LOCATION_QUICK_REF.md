# Custom Location Region Fix - Quick Reference Card

## Problem in One Line
Custom locations show Antarctica data for all regions instead of region-specific locations.

## Root Cause
`storage.js` initializes from global `config.map.predefined_locations` instead of region-specific `activeRegionConfig.customFilters`.

## Files to Change (Only 2!)

### 1. assets/js/storage.js
- Line 13: Add `app` parameter to constructor
- Line 18: Load with `regionId` parameter
- Line 36: Use `activeRegionConfig.customFilters`
- Lines 238-250: Add `regionId` parameter to load method
- Lines 255-263: Save per-region to localStorage

### 2. assets/js/app.js
- Line ~25: Move `applyRegionFromUrl()` before storage creation
- Line ~30: Pass `this` to EventStorage constructor
- Line ~180: Reload custom locations when region changes

## Testing Commands
```bash
# Visit each region and check custom locations
open http://localhost:8000/hof        # Should show: Innenstadt, Altstadt, Theresienstein
open http://localhost:8000/nbg        # Should show: Altstadt, Gostenhof, Südstadt
open http://localhost:8000/antarctica # Should show: 🐧 Penguin HQ, 🧊 Ice Cube Bar
```

## Complexity
- **Files:** 2
- **Lines:** ~50
- **Risk:** Low
- **Time:** 1-2 hours
- **Value:** High

## Full Docs
- `CUSTOM_LOCATION_REGION_ANALYSIS.md` - Detailed analysis
- `CUSTOM_LOCATION_REGION_SUMMARY.md` - Executive summary
- `CODE_FLOW_VISUALIZATION.md` - Code flow diagrams
