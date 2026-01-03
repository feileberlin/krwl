# Custom SVG Map Markers

Terminal/hacker style map markers with green (#00ff00) outlines matching the application theme.

## Design Philosophy

All markers follow the terminal aesthetic:
- **No fill colors** - Transparent backgrounds
- **Green outlines only** - #00ff00 (bright green)
- **Distinct shapes** - Different geometric shapes for easy identification
- **Minimalist icons** - Simple, readable symbols
- **Consistent size** - All 32x48px for uniform appearance
- **Drop shadows** - For depth on dark backgrounds

## Location Markers

### Geolocation (`marker-geolocation.svg`)
- **Shape**: Square pin
- **Icon**: Person silhouette
- **Use**: "You are here" - user's current location
- **Size**: 32x48px

### Main Station (`marker-main-station.svg`)
- **Shape**: Rectangle with railroad crossing X
- **Icon**: Train/rails
- **Use**: Main train/bus station location
- **Size**: 32x48px

### City Center (`marker-city-center.svg`)
- **Shape**: Octagon (8-sided)
- **Icon**: Crosshair/target center point
- **Use**: City center reference point
- **Size**: 32x48px

### Mayor's Office (`marker-mayors-office.svg`)
- **Shape**: Building with pillars
- **Icon**: Classical building facade with female symbol (♀)
- **Use**: Government building, mayor's office
- **Size**: 32x48px

## Event Category Markers

### Default Event (`marker-default.svg`)
- **Shape**: Classic teardrop pin
- **Icon**: Circle with center dot
- **Use**: Default event marker, all events
- **Size**: 32x48px

### Active/Selected (`marker-active.svg`)
- **Shape**: Teardrop pin with glow
- **Icon**: Larger glowing center dot
- **Use**: Currently selected or hovered event
- **Size**: 32x48px
- **Features**: Thicker strokes, outer glow effect

### On Stage (`marker-on-stage.svg`)
- **Shape**: Diamond pin
- **Icon**: Microphone
- **Use**: Music, theater, performances
- **Size**: 32x48px

### Pub Games (`marker-pub-games.svg`)
- **Shape**: Hexagon pin
- **Icon**: Beer mug
- **Use**: Pub quizzes, game nights, social events
- **Size**: 32x48px

### Festivals (`marker-festivals.svg`)
- **Shape**: Star pin
- **Icon**: Festival flag
- **Use**: Festivals, celebrations, large events
- **Size**: 32x48px

## Community Place Markers

### Church (`marker-church.svg`)
- **Shape**: Cross-shaped pin
- **Icon**: Christian cross
- **Use**: Churches, chapels, religious buildings
- **Size**: 32x48px

### Swimming Pool (`marker-swimming.svg`)
- **Shape**: Wave-topped pin
- **Icon**: Waves and swimmer
- **Use**: Swimming pools, aquatic centers, beaches
- **Size**: 32x48px

### Sports Field (`marker-sports-field.svg`)
- **Shape**: Rectangular stadium pin
- **Icon**: Playing field with goals
- **Use**: Sports fields, stadiums, athletic facilities
- **Size**: 32x48px

### Cemetery (`marker-cemetery.svg`)
- **Shape**: Rounded tombstone pin
- **Icon**: Cross on tombstone
- **Use**: Cemeteries, memorial gardens
- **Size**: 32x48px

### Library (`marker-library.svg`)
- **Shape**: Book spine pin
- **Icon**: Book with pages
- **Use**: Libraries, reading rooms, archives
- **Size**: 32x48px

### Hospital (`marker-hospital.svg`)
- **Shape**: Pentagon pin
- **Icon**: Medical cross (equal arms)
- **Use**: Hospitals, clinics, medical centers
- **Size**: 32x48px

### Park/Garden (`marker-park.svg`)
- **Shape**: Tree crown pin
- **Icon**: Tree with multiple circular crowns
- **Use**: Parks, gardens, green spaces
- **Size**: 32x48px

### School (`marker-school.svg`)
- **Shape**: Trapezoid (graduation cap) pin
- **Icon**: Graduation cap with tassel
- **Use**: Schools, universities, educational institutions
- **Size**: 32x48px

### Shopping (`marker-shopping.svg`)
- **Shape**: Shopping bag pin
- **Icon**: Bag with handles and items
- **Use**: Shopping centers, markets, retail areas
- **Size**: 32x48px

### Museum (`marker-museum.svg`)
- **Shape**: Classical temple pin
- **Icon**: Temple with columns and pediment
- **Use**: Museums, galleries, cultural centers
- **Size**: 32x48px

## Terminal Color Palette

- **Primary**: #00ff00 (bright green)
- **Glow/Active**: #00ff00 with opacity variations
- **Shadow**: #000 with 50% opacity
- **Background**: Transparent (shows map underneath)

## Usage in Leaflet

### Basic Usage

```javascript
// Create custom terminal-style icon
const terminalIcon = L.icon({
    iconUrl: 'markers/marker-default.svg',
    iconSize: [32, 48],
    iconAnchor: [16, 48],
    popupAnchor: [0, -48]
});

const marker = L.marker([lat, lon], { icon: terminalIcon }).addTo(map);
```

### Location-Based Markers

```javascript
// Get marker for predefined locations
function getLocationMarker(locationType) {
    const iconMap = {
        'geolocation': 'markers/marker-geolocation.svg',
        'main-station': 'markers/marker-main-station.svg',
        'city-center': 'markers/marker-city-center.svg',
        'mayors-office': 'markers/marker-mayors-office.svg'
    };
    
    return L.icon({
        iconUrl: iconMap[locationType],
        iconSize: [32, 48],
        iconAnchor: [16, 48],
        popupAnchor: [0, -48]
    });
}

// Use for user location
L.marker([userLat, userLon], { 
    icon: getLocationMarker('geolocation') 
}).addTo(map);
```

### Category-Based Event Markers

```javascript
// Get marker based on event category
function getEventMarker(category) {
    const iconMap = {
        'on-stage': 'markers/marker-on-stage.svg',
        'pub-games': 'markers/marker-pub-games.svg',
        'festivals': 'markers/marker-festivals.svg',
        'default': 'markers/marker-default.svg'
    };
    
    const iconUrl = iconMap[category] || iconMap.default;
    
    return L.icon({
        iconUrl: iconUrl,
        iconSize: [32, 48],
        iconAnchor: [16, 48],
        popupAnchor: [0, -48]
    });
}

// Use in marker creation
const marker = L.marker([event.lat, event.lon], { 
    icon: getEventMarker(event.category) 
}).addTo(map);
```

### Active/Hover State

```javascript
// Change marker on hover to show selection
marker.on('mouseover', function() {
    this.setIcon(L.icon({
        iconUrl: 'markers/marker-active.svg',
        iconSize: [32, 48],
        iconAnchor: [16, 48],
        popupAnchor: [0, -48]
    }));
});

marker.on('mouseout', function() {
    // Reset to original category marker
    this.setIcon(getEventMarker(event.category));
});
```

## Shape Distinctions

Each marker has a unique shape for quick visual identification:

| Marker | Shape | Visual Characteristic |
|--------|-------|----------------------|
| Default | Teardrop | Classic location pin |
| Active | Teardrop + Glow | Thicker strokes, glowing |
| Geolocation | Square | User location |
| Main Station | Rectangle + X | Railroad crossing |
| City Center | Octagon | 8-sided symmetry |
| Mayor's Office | Building | Classical facade |
| On Stage | Diamond | 4-pointed shape |
| Pub Games | Hexagon | 6-sided shape |
| Festivals | Star | Multiple points |

## Accessibility Features

- **High contrast**: Green on black background
- **Shape variety**: Distinguishable without color
- **Clear outlines**: 2px stroke width for visibility
- **Icons**: Additional visual cues beyond shape
- **Drop shadow**: Improves depth perception
- **Size consistency**: All same size for fairness

## Technical Specifications

### Common Elements
- **Stroke Color**: #00ff00 (bright green)
- **Stroke Width**: 2px (main outline), 1-1.5px (details)
- **Fill**: none (transparent)
- **Drop Shadow**: ellipse, black with 50% opacity
- **Icon Size**: 32×48 pixels
- **Anchor Point**: [16, 48] (bottom center)
- **Popup Anchor**: [0, -48] (above marker)

### File Format
- Format: SVG (Scalable Vector Graphics)
- Encoding: UTF-8
- Namespace: http://www.w3.org/2000/svg
- ViewBox: 0 0 32 48
- Optimization: Minimal, hand-coded paths

## Customization

### Changing the Terminal Color

To change from green to another terminal color (e.g., cyan, amber):

```svg
<!-- Change all stroke="#00ff00" to: -->
stroke="#00ffff"  <!-- Cyan -->
stroke="#ffaa00"  <!-- Amber -->
stroke="#ff0000"  <!-- Red -->
```

### Adding New Location Markers

1. Copy an existing marker SVG
2. Create a unique shape (triangle, pentagon, etc.)
3. Add an appropriate icon
4. Keep the same terminal style (green outline only)
5. Name it `marker-{location-name}.svg`
6. Add to `getLocationMarker()` function

### Adding New Category Markers

1. Copy an existing category marker
2. Design a new shape (avoid duplicates)
3. Add a category-appropriate icon
4. Keep terminal aesthetics
5. Name it `marker-{category-name}.svg`
6. Add to `getEventMarker()` function

### Design Guidelines

- Use only outlines (no fills except shadow and accents)
- Keep stroke width consistent (2px main, 1-1.5px details)
- Center anchor at bottom point (16, 48)
- Test at actual size for readability
- Ensure shape is distinctive at small sizes
- Icons should be 6-10px in the marker head

## CRT/Terminal Effect (Optional)

For enhanced CRT monitor effect, add glow in CSS:

```css
.leaflet-marker-icon {
    filter: drop-shadow(0 0 2px #00ff00);
}

.leaflet-marker-icon:hover {
    filter: drop-shadow(0 0 4px #00ff00) 
            drop-shadow(0 0 8px #00ff00);
}
```

## Browser Support

SVG markers work in all modern browsers:
- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Mobile browsers: ✅

## References

- [Leaflet Icon Documentation](https://leafletjs.com/reference.html#icon)
- [SVG Path Specification](https://www.w3.org/TR/SVG2/paths.html)
- Terminal color palettes: Green (#00ff00), Amber (#ffaa00), Cyan (#00ffff)
