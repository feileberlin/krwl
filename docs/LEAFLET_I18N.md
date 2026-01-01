# Leaflet.js and Internationalization

## Our Approach vs Leaflet i18n Plugins

### What We Use
We use a **custom i18n solution** (`static/js/i18n.js`) because:

1. **No Leaflet UI controls** - We disabled built-in controls:
   ```javascript
   L.map('map', {
       zoomControl: false,        // No zoom buttons
       attributionControl: false  // No attribution text
   })
   ```

2. **Custom overlay UI** - All UI is custom HTML/CSS overlays on the map
3. **Application-specific strings** - Our content is unique to our app (filter labels, event details, etc.)

### When to Use Leaflet i18n Plugins

Use **Leaflet.i18n** or similar plugins if you:

1. **Use Leaflet's built-in controls**:
   - Zoom buttons (+/-)
   - Attribution control
   - Scale control
   - Layer control

2. **Need to translate Leaflet's standard messages**:
   - "Zoom in" / "Zoom out" tooltips
   - "Leaflet | © OpenStreetMap contributors"
   - Geolocation messages ("Locating...")

### Available Leaflet i18n Plugins

#### 1. Leaflet.i18n (npm: leaflet-i18n)
**Best for:** Translating Leaflet's built-in controls

```html
<script src="https://unpkg.com/leaflet-i18n@0.3.1/Leaflet.i18n.min.js"></script>
```

Usage:
```javascript
// Set language for Leaflet controls
L.i18n.setLanguage('de');

// Leaflet controls will use German text
L.control.zoom().addTo(map);  // Shows "Vergrößern" / "Verkleinern"
```

#### 2. leaflet-plugins (includes L.I18n)
**Best for:** Custom translations in map interactions

```javascript
L.I18n.setLanguage('de', {
    'Zoom in': 'Vergrößern',
    'Zoom out': 'Verkleinern'
});
```

#### 3. Custom Solution (What We Use)
**Best for:** Full application i18n including non-Leaflet content

Our implementation:
- Single HTML file
- JSON content files per language
- Dynamic loading based on config/browser
- Supports all UI elements, not just map

## Our Implementation Details

### What Gets Translated

✅ **Custom overlay content**:
- Filter labels and options
- Event detail popups (handled by custom HTML)
- Burger menu actions
- User messages and errors
- Accessibility labels

✅ **Leaflet-rendered content**:
- Marker tooltips (time display)
- User location popup ("You are here")
- Custom popup content

❌ **Not translated** (because disabled):
- Zoom control buttons (we use zoomControl: false)
- Attribution text (we use attributionControl: false)
- Scale control (not used)

### How Marker Content is Translated

```javascript
// In app.js - example of translated marker popup
const popup = `
    <h3>${event.title}</h3>
    <p>${i18n.t('event_detail.location_label')} ${event.location.name}</p>
    <p>${i18n.t('event_detail.time_label')} ${eventTime}</p>
`;

marker.bindPopup(popup);
```

### Integration with Leaflet

Our i18n system works alongside Leaflet:

```javascript
// Initialize i18n before creating map
await i18n.init(config);

// Create map
this.map = L.map('map', {
    zoomControl: false,
    attributionControl: false
});

// Use translations in marker content
marker.bindPopup(i18n.t('map.user_location_popup'));
```

## If You Enable Leaflet Controls

If you want to enable Leaflet's built-in controls AND translate them:

### 1. Add Leaflet.i18n to scripts/manage_libs.py

```python
LIBRARIES = {
    "leaflet": { /* existing config */ },
    "leaflet-i18n": {
        "version": "0.3.5",
        "base_url": "https://unpkg.com/leaflet-i18n@{version}",
        "files": [
            {
                "src": "Leaflet.i18n.min.js",
                "dest": "leaflet-i18n/Leaflet.i18n.min.js",
                "type": "js"
            }
        ]
    }
}
```

### 2. Load in index.html

```html
<script src="lib/leaflet/leaflet.js"></script>
<script src="lib/leaflet-i18n/Leaflet.i18n.min.js"></script>
```

### 3. Configure in app.js

```javascript
// After loading i18n
await i18n.init(config);

// Set Leaflet's language
if (window.L && L.i18n) {
    L.i18n.setLanguage(i18n.getLocale());
}

// Enable controls with translations
this.map = L.map('map', {
    zoomControl: true,  // Will show translated zoom buttons
    attributionControl: true
});
```

## Comparison Table

| Feature | Our Custom i18n | Leaflet.i18n Plugin |
|---------|-----------------|---------------------|
| Leaflet controls | ❌ (disabled) | ✅ |
| Custom UI overlays | ✅ | ❌ |
| Event content | ✅ | ❌ |
| Filter labels | ✅ | ❌ |
| Messages/errors | ✅ | ❌ |
| Marker popups | ✅ | ❌ |
| Accessibility labels | ✅ | ❌ |
| Config-based switching | ✅ | ❌ |
| Browser auto-detect | ✅ | ❌ |
| Format dates/numbers | ✅ | ❌ |
| Multiple simultaneous languages | ✅ | ❌ |

## Recommendation

**Stick with our custom solution** because:

1. ✅ We don't use Leaflet's built-in controls
2. ✅ We have extensive custom UI that needs translation
3. ✅ Our solution is more flexible and complete
4. ✅ No additional dependencies needed
5. ✅ Better integration with application state

**Consider adding Leaflet.i18n** only if:
- You enable Leaflet's built-in controls
- You want standard zoom/attribution UI
- You need minimal setup for basic maps

## Testing Leaflet Integration

Our tests verify:
```bash
# Check all translations are complete
python3 tests/test_translations.py --verbose

# Verify Leaflet content renders with translations
# (Would need browser/e2e tests for this)
```

## References

- [Leaflet.i18n on npm](https://www.npmjs.com/package/leaflet-i18n)
- [Leaflet Control Translation](https://github.com/yohanboniface/Leaflet.i18n)
- [Leaflet Documentation](https://leafletjs.com/reference.html)
- Our custom i18n: `static/js/i18n.js`
