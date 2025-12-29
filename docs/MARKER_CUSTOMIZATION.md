# Map Marker Customization Guide

This guide explains how to customize map markers for events and user location in the KRWL HOF Community Events app.

## Overview

The app supports three levels of marker customization:
1. **Category-based markers** (default) - Automatic based on event category
2. **Per-event custom markers** - Override marker for individual events
3. **User location marker** - Configure the "You are here" marker

## Category-Based Markers (Default)

By default, events use category-based SVG markers:

| Category | Marker File | Shape | Icon |
|----------|------------|-------|------|
| `on-stage` | `marker-on-stage.svg` | Diamond | Microphone |
| `pub-game` | `marker-pub-games.svg` | Hexagon | Beer mug |
| `festival` | `marker-festivals.svg` | Star | Festival flag |
| `workshop` | `marker-workshops.svg` | Workshop shape | Tools |
| `market` | `marker-shopping.svg` | Shopping bag | Bag with items |
| `sports` | `marker-sports.svg` | Sports shape | Ball |
| `community` | `marker-community.svg` | Community shape | People |
| `other` | `marker-default.svg` | Teardrop | Center dot |

These markers are automatically selected based on the event's `category` field.

## Per-Event Custom Markers

You can override the marker for any individual event by adding optional fields to the event data.

### Basic Custom Marker

To use a custom marker icon for a single event:

```json
{
  "id": "special-event-1",
  "title": "Special Concert",
  "category": "on-stage",
  "marker_icon": "markers/marker-opera-house.svg",
  "location": {
    "name": "Opera House",
    "lat": 50.3167,
    "lon": 11.9167
  },
  "start_time": "2025-01-15T19:00:00",
  "source": "manual",
  "status": "published"
}
```

The event will use `marker-opera-house.svg` instead of the default `marker-on-stage.svg`.

### Custom Marker with Size

To use a different sized marker:

```json
{
  "id": "large-event-1",
  "title": "Major Festival",
  "category": "festival",
  "marker_icon": "markers/marker-festivals.svg",
  "marker_size": [48, 72],
  "location": { ... },
  "start_time": "2025-01-20T10:00:00",
  "source": "manual",
  "status": "published"
}
```

### Full Custom Marker Configuration

For complete control over marker positioning:

```json
{
  "id": "custom-event-1",
  "title": "Custom Event",
  "category": "other",
  "marker_icon": "markers/custom-marker.svg",
  "marker_size": [40, 60],
  "marker_anchor": [20, 60],
  "marker_popup_anchor": [0, -60],
  "location": { ... },
  "start_time": "2025-01-25T14:00:00",
  "source": "manual",
  "status": "published"
}
```

### Marker Fields Reference

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `marker_icon` | string | Path to SVG file relative to static root | Category-based marker |
| `marker_size` | [width, height] | Marker size in pixels | `[32, 48]` |
| `marker_anchor` | [x, y] | Point on marker that corresponds to marker's location | `[width/2, height]` (bottom center) |
| `marker_popup_anchor` | [x, y] | Point from which the popup should open relative to marker | `[0, -height]` (above marker) |

**All marker fields are optional.** If not specified, defaults are used.

## User Location Marker Customization

You can customize the "You are here" marker via the configuration file.

### Default User Location Marker

By default, the app uses `marker-geolocation.svg` (square pin with person icon).

### Custom User Location Marker

Add a `user_location_marker` section to your config file (`config.prod.json`, `config.dev.json`, etc.):

```json
{
  "map": {
    "default_center": { ... },
    "default_zoom": 13,
    "tile_provider": "...",
    "attribution": "...",
    "user_location_marker": {
      "icon": "markers/marker-geolocation.svg",
      "size": [32, 48],
      "anchor": [16, 48],
      "popup_anchor": [0, -48]
    }
  }
}
```

### Configuration Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `icon` | string | Path to SVG file | `"markers/marker-geolocation.svg"` |
| `size` | [width, height] | Marker size in pixels | `[32, 48]` |
| `anchor` | [x, y] | Anchor point on marker | `[16, 48]` (bottom center) |
| `popup_anchor` | [x, y] | Popup anchor relative to marker | `[0, -48]` (above marker) |

## Creating Custom Markers

### Design Guidelines

All markers should follow the terminal aesthetic:

1. **Size**: 32×48 pixels (or proportional)
2. **ViewBox**: `0 0 32 48` (or proportional)
3. **Style**: Barbie red outlines (`#FF69B4`), no fills
4. **Stroke Width**: 2px for main outline, 1-1.5px for details
5. **Shadow**: Black ellipse with 50% opacity at bottom
6. **Anchor**: Bottom center point

### Example Custom Marker SVG

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 48" width="32" height="48">
  <!-- Drop shadow -->
  <ellipse cx="16" cy="46" rx="6" ry="2" fill="#000" opacity="0.5"/>
  
  <!-- Custom shape -->
  <path d="M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z" 
        fill="none" stroke="#FF69B4" stroke-width="2"/>
  
  <!-- Custom icon -->
  <circle cx="16" cy="15" r="4" fill="none" stroke="#FF69B4" stroke-width="1.5"/>
</svg>
```

Save your custom marker to `static/markers/marker-custom-name.svg`.

## Examples

### Example 1: VIP Event with Larger Marker

```json
{
  "id": "vip-event-1",
  "title": "VIP Gala",
  "category": "on-stage",
  "marker_icon": "markers/marker-opera-house.svg",
  "marker_size": [48, 72],
  "marker_anchor": [24, 72],
  "marker_popup_anchor": [0, -72],
  "location": {
    "name": "Grand Theater",
    "lat": 50.3200,
    "lon": 11.9200
  },
  "start_time": "2025-02-01T20:00:00",
  "source": "manual",
  "status": "published"
}
```

### Example 2: Outdoor Market with Custom Icon

```json
{
  "id": "farmers-market-1",
  "title": "Farmers Market",
  "category": "market",
  "marker_icon": "markers/marker-shopping.svg",
  "location": {
    "name": "Town Square",
    "lat": 50.3150,
    "lon": 11.9180
  },
  "start_time": "2025-02-05T08:00:00",
  "source": "manual",
  "status": "published"
}
```

### Example 3: Config with Custom User Location

```json
{
  "app": { ... },
  "map": {
    "default_center": {
      "lat": 50.3167,
      "lon": 11.9167
    },
    "default_zoom": 13,
    "tile_provider": "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    "attribution": "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    "user_location_marker": {
      "icon": "markers/marker-geolocation.svg",
      "size": [40, 60],
      "anchor": [20, 60],
      "popup_anchor": [0, -60]
    }
  }
}
```

## Available Markers

The app comes with many pre-made markers in `static/markers/`:

**Event Categories:**
- `marker-on-stage.svg` - Performances
- `marker-pub-games.svg` - Pub events
- `marker-festivals.svg` - Festivals
- `marker-workshops.svg` - Workshops
- `marker-sports.svg` - Sports events
- `marker-community.svg` - Community events
- `marker-music.svg` - Music events
- `marker-arts.svg` - Art events
- `marker-food.svg` - Food events
- `marker-default.svg` - Default/other

**Locations:**
- `marker-geolocation.svg` - User location
- `marker-main-station.svg` - Train/bus station
- `marker-city-center.svg` - City center
- `marker-park.svg` - Parks
- `marker-museum.svg` - Museums
- `marker-library.svg` - Libraries
- `marker-shopping.svg` - Shopping areas

**Special:**
- `marker-active.svg` - Highlighted/selected event

See `static/markers/README.md` for the complete list.

## Terminal Glow Effect

All markers automatically get a barbie red glow effect via CSS:

```css
.leaflet-marker-icon {
    filter: drop-shadow(0 0 2px #FF69B4);
}

.leaflet-marker-icon:hover {
    filter: drop-shadow(0 0 4px #FF69B4) 
            drop-shadow(0 0 8px #FF69B4);
}
```

The glow intensifies on hover for better user experience.

## Testing Custom Markers

1. Add your custom SVG to `static/markers/`
2. Add the marker fields to an event in `data/events.json`
3. Start the local server: `cd static && python3 -m http.server 8000`
4. Open `http://localhost:8000` and check the map

## Troubleshooting

### Marker Not Showing

- Check that the SVG file exists in `static/markers/`
- Verify the path is correct (relative to static root)
- Check browser console for 404 errors

### Marker Position Wrong

- Adjust `marker_anchor` - should point to the "tip" of the marker
- Default is `[width/2, height]` for bottom-center

### Popup Position Wrong

- Adjust `marker_popup_anchor`
- Default is `[0, -height]` to appear above marker
- Use positive Y values to move popup down

### Marker Too Large/Small

- Adjust `marker_size`
- Maintain aspect ratio: if width increases by 2x, height should too
- Update anchors proportionally

## Related Documentation

- [Marker Design System](../static/markers/DESIGN_SYSTEM.md) - Visual design guide
- [Marker README](../static/markers/README.md) - Complete marker catalog
- [Event Schema](../test_event_schema.py) - Event data structure
- [Configuration Guide](./SETUP.md) - App configuration

## Future Enhancements

Planned features for marker customization:

- [ ] Marker animations
- [ ] Cluster markers for multiple events at same location
- [ ] Dynamic marker coloring based on time/distance
- [ ] Custom marker shapes via CSS classes
- [ ] Marker legends/key
