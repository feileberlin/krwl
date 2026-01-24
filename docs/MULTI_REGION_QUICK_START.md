# Multi-Region Quick Start Guide

## What Is This?

The KRWL HOF event map now supports **multiple Franconian cities** viewing the same event data from different perspectives. Think of it like Google Maps - same data, different starting locations.

**What it does:** URL path segment reads corresponding config variables (map center, zoom) to position the map.

**What it does NOT do:** No filter bar changes, no UI modifications. Custom filters are just data structure for future use.

## 5-Minute Overview

### The Concept

```
Single events.json → Multiple city views (Hof, Nürnberg, Bayreuth, etc.)
                     Different map centers, same events
```

### URL Structure (Future Flask App)

- `/` → Redirects to `/hof` (default region)
- `/hof` → Map centered on Hof (Saale)
- `/nbg` → Map centered on Nürnberg
- `/bayreuth` → Map centered on Bayreuth
- `/selb` → Map centered on Selb
- `/rehau` → Map centered on Rehau

**Each URL reads config to:**
- Center map at region's coordinates
- Apply region's default zoom
- **NO filter bar changes** - customFilters are just data structure
- **Same event data from events.json**

## Current Status

✅ **Infrastructure Complete** (v1.0)
- Config structure in place
- 5 regions defined (Hof, Nürnberg, Bayreuth, Selb, Rehau)
- Utility functions implemented
- Full test coverage
- Documentation complete
- Backward compatible with existing static site

❌ **Flask App Not Implemented Yet** (Future v2.0)
- No web server routes yet
- No dynamic URL routing yet
- No region-specific templates yet
- Static site works exactly as before

## Using Region Utils (Python)

### Basic Usage

```python
from pathlib import Path
from src.modules.region_utils import (
    get_all_regions,
    get_region_config,
    validate_region,
    haversine_distance
)

base_path = Path(__file__).parent

# Get all available regions
regions = get_all_regions(base_path)
print(regions.keys())  # ['hof', 'nbg', 'bayreuth', 'selb', 'rehau']

# Get config for specific region
hof = get_region_config('hof', base_path)
print(hof['displayName'])  # "Hof (Saale)"
print(hof['center'])       # {"lat": 50.3167, "lng": 11.9167}
print(hof['zoom'])         # 13

# Validate region exists
if validate_region('nbg', base_path):
    print("Nürnberg is valid!")

# Calculate distance between cities
distance = haversine_distance(
    11.9167, 50.3167,  # Hof
    11.0767, 49.4521   # Nuremberg
)
print(f"Distance: {distance:.1f} km")  # 113.4 km
```

### Custom Filters

```python
from src.modules.region_utils import get_custom_filters_for_region

# Get neighborhood filters for Hof
filters = get_custom_filters_for_region('hof', base_path)

for f in filters:
    print(f"- {f['name']['de']} ({f['radius']} km radius)")
# Output:
# - Innenstadt (1.5 km radius)
# - Altstadt (1.0 km radius)
# - Theresienstein (0.8 km radius)
```

### Optional Event Filtering

```python
from src.modules.region_utils import filter_events_by_region
import json

# Load all events
with open('assets/json/events.json') as f:
    data = json.load(f)
    all_events = data.get('events', [])

# Filter to only events within Hof's bounding box
hof_events = filter_events_by_region(all_events, 'hof', base_path)

print(f"Total: {len(all_events)} events")
print(f"In Hof region: {len(hof_events)} events")
```

## Testing

### Run All Multi-Region Tests

```bash
# Quick test all
python3 tests/test_multi_region_config.py
python3 tests/test_region_data_files.py
python3 tests/test_region_utils.py

# Verbose output
python3 tests/test_multi_region_config.py --verbose
```

### Test Static Site Generation

```bash
# Generate site (uses default region internally)
python3 src/event_manager.py generate

# Check output
ls -lh public/index.html
```

## Adding a New Region

1. Edit `config.json`, add to `regions` section:

```json
"newcity": {
  "name": "newcity",
  "displayName": "New City",
  "center": {"lat": 50.0, "lng": 11.0},
  "zoom": 13,
  "boundingBox": {
    "north": 50.1, "south": 49.9,
    "east": 11.1, "west": 10.9
  },
  "dataSource": "events.json",
  "defaultLanguage": "de",
  "customFilters": [
    {
      "id": "downtown",
      "name": {"de": "Innenstadt", "en": "Downtown"},
      "center": {"lat": 50.0, "lng": 11.0},
      "radius": 1.0,
      "zoom": 14
    }
  ]
}
```

2. Test it:

```bash
python3 tests/test_multi_region_config.py
```

3. Done! Region is now available via utilities.

## Future Flask Implementation (v2.0)

When implementing the Flask web app, use these utilities:

### Example Flask Route

```python
from flask import Flask, jsonify
from src.modules.region_utils import get_region_config, validate_region

app = Flask(__name__)

@app.route('/<region>')
def map_view(region):
    # Validate and get region config
    if not validate_region(region, base_path):
        return "Region not found", 404
    
    config = get_region_config(region, base_path)
    
    # Pass to template
    return render_template('map.html', 
        center=config['center'],
        zoom=config['zoom'],
        filters=config['customFilters']
    )
```

### Example JavaScript

```javascript
// Get current region from URL
const region = window.location.pathname.split('/')[1] || 'hof';

// Fetch region config
const response = await fetch(`/api/regions/${region}`);
const config = await response.json();

// Initialize map with region settings
const map = L.map('map').setView(
    [config.center.lat, config.center.lng],
    config.zoom
);

// Populate custom filters dropdown
config.customFilters.forEach(filter => {
    const option = document.createElement('option');
    option.value = filter.id;
    option.textContent = filter.name.de;
    filterSelect.appendChild(option);
});
```

## Common Patterns

### Check If Region Exists

```python
from src.modules.region_utils import validate_region

region = request.args.get('region', 'hof')
if not validate_region(region, base_path):
    # Fall back to default
    region = 'hof'
```

### Get Region Center for Map Init

```python
from src.modules.region_utils import get_region_center, get_region_zoom

center = get_region_center('nbg', base_path)  # {"lat": ..., "lng": ...}
zoom = get_region_zoom('nbg', base_path)      # 12
```

### Filter Events by Distance from Region Center

```python
from src.modules.region_utils import get_region_center, haversine_distance

center = get_region_center('hof', base_path)
max_distance = 10  # km

nearby_events = [
    event for event in all_events
    if 'location' in event and
       haversine_distance(
           event['location']['lon'], event['location']['lat'],
           center['lng'], center['lat']
       ) <= max_distance
]
```

## FAQ

**Q: Do I need separate event files for each region?**  
A: No! All regions share `events.json`. The URL path just changes the map view.

**Q: How do I filter events by region?**  
A: Use `filter_events_by_region()` to filter by bounding box, or use distance-based filtering with `haversine_distance()`.

**Q: Can I have region-specific events?**  
A: Yes, but they all go in the same `events.json`. You can add a `region` field to events and filter client-side or server-side.

**Q: Does this break the existing static site?**  
A: No! The static site works exactly as before. Multi-region is just infrastructure for future enhancement.

**Q: How do I change the default region?**  
A: Edit `defaultRegion` in `config.json`.

**Q: Can regions overlap?**  
A: Yes! Bounding boxes can overlap. An event can appear in multiple region views.

## Next Steps

1. **Read full docs**: `docs/MULTI_REGION_INFRASTRUCTURE.md`
2. **Explore utilities**: `src/modules/region_utils.py`
3. **Run tests**: `tests/test_multi_region_*.py`
4. **Plan Flask app**: When ready for dynamic routing

## Support

- Full documentation: `docs/MULTI_REGION_INFRASTRUCTURE.md`
- API reference: See docstrings in `src/modules/region_utils.py`
- Test examples: `tests/test_region_utils.py`
