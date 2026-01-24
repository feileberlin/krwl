# Multi-Region Infrastructure

## Overview

KRWL HOF now supports **multiple regions** (cities) viewing the same event data from different map perspectives. The URL path determines which city's map view to show:

- `/hof` - Hof (Saale) view
- `/nbg` - Nürnberg view  
- `/bayreuth` - Bayreuth view
- `/selb` - Selb view
- `/rehau` - Rehau view

**Key principle:** All regions share the same `events.json` data file. **The URL path segment just reads config variables (map center and zoom) to center the map** - no filter bar changes or UI modifications.

**What this infrastructure provides:**
- ✅ Configuration structure for 5 Franconian cities
- ✅ URL path determines map center and zoom
- ✅ Utility functions to read region config
- ❌ **NO filter bar changes** - customFilters are just data structure for future
- ❌ **NO UI modifications** - existing interface unchanged

## Architecture

### Single Shared Data Model

```
┌─────────────────────────────────────────────────────────┐
│                    events.json                          │
│              (Single shared data file)                  │
│                                                         │
│  All events from all locations in Franconia            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Used by all regions
                          ▼
    ┌──────────┬──────────┬──────────┬──────────┬─────────┐
    │   Hof    │ Nürnberg │ Bayreuth │   Selb   │  Rehau  │
    │  View    │   View   │   View   │   View   │   View  │
    └──────────┴──────────┴──────────┴──────────┴─────────┘
     Different map centers, same data
```

### What Regions Define

Each region in `config.json` specifies:

1. **Map Center** - Where to center the map (lat/lng) - **ACTIVE: Used to center map based on URL**
2. **Default Zoom** - Initial zoom level - **ACTIVE: Applied when map loads**
3. **Bounding Box** - Suggested area boundaries (optional filtering)
4. **Custom Filters** - Neighborhood/district data structure - **NOT USED YET: Just configuration for future**
5. **Display Name** - Human-readable name (e.g., "Hof (Saale)")
6. **Default Language** - Preferred language for the region

**Important:** Only map center and zoom are actively used. The URL path segment reads these config variables to center the map. Custom filters are just data structure for future implementation - **no filter bar changes in this PR**.

## Configuration Structure

### Location in config.json

The regions configuration is located in `config.json` after the design section:

```json
{
  "design": { ... },
  
  "regions": {
    "hof": { ... },
    "nbg": { ... },
    "bayreuth": { ... },
    "selb": { ... },
    "rehau": { ... }
  },
  
  "defaultRegion": "hof",
  "supportedLanguages": ["de", "en", "cs"],
  
  "app": { ... }
}
```

### Region Schema

Each region has the following structure:

```json
{
  "name": "hof",                          // Internal identifier
  "displayName": "Hof (Saale)",           // Display name
  "center": {                             // Map center coordinates
    "lat": 50.3167,
    "lng": 11.9167
  },
  "zoom": 13,                             // Default zoom level
  "boundingBox": {                        // Optional bounding box
    "north": 50.4,
    "south": 50.2,
    "east": 12.0,
    "west": 11.8
  },
  "dataSource": "events.json",            // Same for all regions
  "defaultLanguage": "de",                // Default language
  "customFilters": [                      // Neighborhood/district filters
    {
      "id": "innenstadt",
      "name": {
        "de": "Innenstadt",
        "en": "City Center"
      },
      "center": {
        "lat": 50.3197,
        "lng": 11.9177
      },
      "radius": 1.5,                      // Radius in km
      "zoom": 14                          // Zoom when filter active
    }
  ]
}
```

## Current Regions

### 1. Hof (Saale) - Default Region

**Center:** 50.3167°N, 11.9167°E  
**Zoom:** 13  
**Custom Filters:**
- **Innenstadt** (City Center) - 1.5 km radius
- **Altstadt** (Old Town) - 1.0 km radius
- **Theresienstein** (Park) - 0.8 km radius

### 2. Nürnberg (nbg)

**Center:** 49.4521°N, 11.0767°E  
**Zoom:** 12  
**Custom Filters:**
- **Altstadt** (Old Town) - 1.2 km radius
- **Gostenhof** - 1.0 km radius
- **Südstadt** (South District) - 1.5 km radius

### 3. Bayreuth

**Center:** 49.9481°N, 11.5783°E  
**Zoom:** 13  
**Custom Filters:**
- **Innenstadt** (City Center) - 1.0 km radius
- **Festspielhaus** (Festival Theatre) - 0.5 km radius
- **Universität** (University) - 1.2 km radius

### 4. Selb

**Center:** 50.1705°N, 12.1328°E  
**Zoom:** 13  
**Custom Filters:**
- **Innenstadt** (City Center) - 1.0 km radius

### 5. Rehau

**Center:** 50.2489°N, 12.0364°E  
**Zoom:** 13  
**Custom Filters:**
- **Marktplatz** (Market Square) - 0.8 km radius

## Utility Functions

The `src/modules/region_utils.py` module provides helper functions:

### Getting Region Information

```python
from src.modules.region_utils import (
    get_all_regions,
    get_default_region,
    validate_region,
    get_region_config
)
from pathlib import Path

base_path = Path(__file__).parent.parent

# Get all regions
regions = get_all_regions(base_path)
# Returns: {'hof': {...}, 'nbg': {...}, ...}

# Get default region
default = get_default_region(base_path)
# Returns: 'hof'

# Validate region exists
is_valid = validate_region('hof', base_path)
# Returns: True

is_valid = validate_region('invalid', base_path)
# Returns: False

# Get specific region config
hof_config = get_region_config('hof', base_path)
# Returns: {'name': 'hof', 'displayName': 'Hof (Saale)', ...}
```

### Distance Calculations

```python
from src.modules.region_utils import haversine_distance

# Calculate distance between Hof and Nuremberg
distance = haversine_distance(
    lon1=11.9167, lat1=50.3167,  # Hof
    lon2=11.0767, lat2=49.4521   # Nuremberg
)
# Returns: 113.4 (km)
```

### Bounding Box Checks

```python
from src.modules.region_utils import is_point_in_bounding_box

bbox = {
    'north': 50.4,
    'south': 50.2,
    'east': 12.0,
    'west': 11.8
}

# Check if point is inside
inside = is_point_in_bounding_box(50.3, 11.9, bbox)
# Returns: True

outside = is_point_in_bounding_box(51.0, 11.9, bbox)
# Returns: False
```

### Filtering Events by Region

```python
from src.modules.region_utils import filter_events_by_region

# Load events from events.json
events = load_events_from_file()

# Filter to only events within Hof's bounding box
hof_events = filter_events_by_region(events, 'hof', base_path)
# Returns: List of events within Hof's bounding box

# Note: This is OPTIONAL - you can show all events regardless of region
```

### Custom Filters

```python
from src.modules.region_utils import get_custom_filters_for_region

# Get custom filters for Hof
filters = get_custom_filters_for_region('hof', base_path)
# Returns: [
#   {'id': 'innenstadt', 'name': {'de': 'Innenstadt', ...}, ...},
#   {'id': 'altstadt', 'name': {'de': 'Altstadt', ...}, ...},
#   ...
# ]
```

## Adding a New Region

To add a new region (e.g., Münchberg):

1. **Add to config.json** in the `regions` section:

```json
"muenchberg": {
  "name": "muenchberg",
  "displayName": "Münchberg",
  "center": {
    "lat": 50.1928,
    "lng": 11.7878
  },
  "zoom": 13,
  "boundingBox": {
    "north": 50.25,
    "south": 50.15,
    "east": 11.85,
    "west": 11.70
  },
  "dataSource": "events.json",
  "defaultLanguage": "de",
  "customFilters": [
    {
      "id": "innenstadt",
      "name": {
        "de": "Innenstadt",
        "en": "City Center"
      },
      "center": {
        "lat": 50.1928,
        "lng": 11.7878
      },
      "radius": 1.0,
      "zoom": 14
    }
  ]
}
```

2. **Test configuration**:

```bash
python3 tests/test_multi_region_config.py --verbose
```

3. **That's it!** The new region is now available.

## Future Flask Integration (Not Implemented Yet)

When implementing a Flask web application:

### Route Structure

```python
from flask import Flask, render_template, jsonify
from src.modules.region_utils import (
    get_region_config,
    validate_region,
    get_default_region
)

app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to default region"""
    default_region = get_default_region(base_path)
    return redirect(f'/{default_region}')

@app.route('/<region>')
def region_map(region):
    """Show map for specific region"""
    if not validate_region(region, base_path):
        region = get_default_region(base_path)
    
    region_config = get_region_config(region, base_path)
    return render_template('map.html', region=region_config)

@app.route('/<region>/api/events')
def region_events(region):
    """Get events (optionally filtered by region)"""
    events = load_all_events()
    
    # Optional: filter by bounding box
    # events = filter_events_by_region(events, region, base_path)
    
    return jsonify(events)

@app.route('/<region>/config.json')
def region_config(region):
    """Get region-specific configuration"""
    config = get_region_config(region, base_path)
    return jsonify(config)
```

### Frontend JavaScript

```javascript
// Extract region from URL path
const pathSegments = window.location.pathname.split('/').filter(s => s);
const currentRegion = pathSegments[0] || 'hof';

// Fetch region-specific config
fetch(`/${currentRegion}/config.json`)
  .then(res => res.json())
  .then(regionConfig => {
    // Initialize map with region center and zoom from config
    // This is the main purpose: URL path determines map view
    const map = L.map('map').setView(
      [regionConfig.center.lat, regionConfig.center.lng],
      regionConfig.zoom
    );
    
    // Note: customFilters are available in regionConfig but NOT used yet
    // No filter bar changes in this implementation - filters are just data structure
    // Example for future use (not implemented):
    // regionConfig.customFilters.forEach(filter => { ... });
    
    // Load events (same for all regions)
    fetch(`/${currentRegion}/api/events`)
      .then(res => res.json())
      .then(events => {
        // Display events on map
        displayEvents(events, map);
      });
  });
```

## Testing

### Run All Tests

```bash
# Configuration tests
python3 tests/test_multi_region_config.py --verbose

# Data file tests
python3 tests/test_region_data_files.py --verbose

# Utility function tests
python3 tests/test_region_utils.py --verbose

# Backward compatibility
python3 tests/test_config_validation.py
python3 scripts/validate_config.py
```

### Test Static Generation

```bash
# Generate static site (backward compatible)
python3 src/event_manager.py generate

# Check output
ls -lh public/index.html
```

## Design Principles

### KISS (Keep It Simple, Stupid)

1. **Single data source** - All regions use `events.json`
2. **No data splitting** - No separate files per region
3. **URL-based routing** - Path determines map view
4. **Optional filtering** - Show all events or filter by bounding box
5. **Backward compatible** - Existing static site works unchanged

### Benefits

✅ **Simple maintenance** - One event data file to manage  
✅ **Consistent data** - All regions see same events  
✅ **Easy addition** - Add regions without data migration  
✅ **Flexible filtering** - Client-side or server-side filtering  
✅ **Backward compatible** - No breaking changes  

### Trade-offs

⚠️ **Large datasets** - All events loaded regardless of region (consider pagination if > 10,000 events)  
⚠️ **Client-side filtering** - Filter by distance/category on client  
⚠️ **Optional region filtering** - Can filter by bounding box if needed  

## Troubleshooting

### Region Not Found

If a region isn't recognized:

1. Check spelling in URL (case-sensitive)
2. Verify region exists in `config.json`
3. Run: `python3 tests/test_multi_region_config.py`

### Custom Filters Not Working

If custom filters don't appear:

1. Check `customFilters` array in region config
2. Verify multilingual `name` has required language
3. Check coordinates and radius are valid numbers

### Events Not Showing

If events don't appear for a region:

1. Verify `events.json` exists and is valid JSON
2. Check event has `location` with `lat`/`lon` fields
3. Optionally filter by bounding box if events too far

## References

- **Config File**: `config.json` (regions section)
- **Utilities**: `src/modules/region_utils.py`
- **Tests**: `tests/test_multi_region_*.py`
- **Main App**: `src/event_manager.py`

## Support

For questions or issues:
- Review this documentation
- Check test files for usage examples
- See `region_utils.py` docstrings for API details
