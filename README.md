# KRWL HOF Community Events

> Community events scraper and viewer with geolocation filtering

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web-apps/)
[![Accessibility](https://img.shields.io/badge/A11y-Compliant-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 🎯 Overview

A **fullscreen, mobile-first** interactive map application for discovering community events near you. All events are displayed as markers directly on the map with no separate navigation—just filters and markers.

### ✨ Key Features

#### 🗺️ Map Features
- ✅ Event time tooltips
- ✅ Rich event popups
- ✅ Geolocation filtering

#### 🎨 UI/UX Features
- ✅ Responsive design
- ✅ Mobile viewport support

#### 📱 PWA Features
- ✅ PWA manifest
- ✅ Installable as app
- ✅ Offline support

#### ♿ Accessibility Features
- ✅ ARIA navigation landmarks
- ✅ Skip to content link
- ✅ ARIA labels

## 🏗️ Architecture


```
┌─────────────────────────────────────────────────────────────┐
│                    KRWL HOF Architecture                     │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │  index.html  │  ← Entry Point
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
    │   app.js     │ │ style.css│ │ Leaflet.js │
    │  (Business   │ │  (UI/UX) │ │  (Maps)    │
    │   Logic)     │ └──────────┘ └────────────┘
    └───────┬──────┘
            │
    ┌───────┼──────────────┐
    │       │              │
┌───▼──┐ ┌──▼───────┐ ┌───▼──────────┐
│config│ │events.json│ │manifest.json │
│.json │ │  (Data)   │ │    (PWA)     │
└──────┘ └───────────┘ └──────────────┘

Data Flow:
1. config.json → Configures app behavior, UI, map
2. events.json → Fetched and filtered by location/time
3. app.js → Renders markers with tooltips on Leaflet map
4. User interaction → Updates filters → Refreshes map
```


## 🎨 User Interface Design

### Design Philosophy
- **Fullscreen Map**: No traditional headers/footers—everything overlays the map
- **Filter Sentence**: Natural language filters integrated at the top
- **Map-First**: Events shown as markers with tooltips, no separate list
- **Mobile-First**: Responsive design optimized for mobile devices first
- **Pure Leaflet.js**: Uses standard Leaflet conventions (markers, tooltips, popups)


```
User Journey:
                                
    ┌─────────────┐
    │   Landing   │
    │   (Map)     │
    └──────┬──────┘
           │
           │ sees filter sentence at top
           │ sees events as markers with time labels
           │
    ┌──────▼──────────────────────────┐
    │ Filter Controls (Top of Map)    │
    │ • Event count & category        │
    │ • Time range                    │
    │ • Distance                      │
    │ • Location                      │
    └──────┬──────────────────────────┘
           │
           │ click filter → map updates
           │
    ┌──────▼──────────────────────────┐
    │ Map Interaction                 │
    │ • Hover marker → see time       │
    │ • Click marker → see popup      │
    │   - Event title                 │
    │   - Time, location, distance    │
    │   - Description                 │
    │   - Link to more info           │
    └─────────────────────────────────┘
```


## 📱 Progressive Web App (PWA)

The application is installable as a native app on any platform:

### Installation
1. **Desktop (Chrome/Edge)**: Click the install icon in the address bar
2. **Mobile (Android)**: Tap "Add to Home Screen" in browser menu
3. **Mobile (iOS)**: Tap Share → "Add to Home Screen"

### PWA Assets
- ✅ `manifest.json` - PWA configuration
- ✅ Multiple icon sizes (192x192, 512x512)
- ✅ Maskable icons for Android adaptive icons
- ✅ Favicon and Apple Touch Icons
- ✅ Theme colors and splash screen

See [PWA_README.md](static/PWA_README.md) for detailed PWA documentation.

## ⚙️ Configuration

All fork-specific customizations are in `static/config.json`:

```json
{
  "app": {
    "name": "Your App Name",
    "description": "Your description"
  },
  "ui": {
    "logo": "logo.svg",
    "imprint_url": "imprint.html",
    "imprint_text": "Imprint",
    "theme_color": "#4CAF50",
    "background_color": "#1a1a1a"
  },
  "map": {
    "default_center": { "lat": 50.3167, "lon": 11.9167 },
    "default_zoom": 13,
    "tile_provider": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    "predefined_locations": [
      { "name": "Location Name", "lat": 50.0, "lon": 11.0 }
    ]
  }
}
```

### Customizable Elements
- **App name and description**: `config.app.*`
- **Logo and branding**: `config.ui.logo`, `config.ui.theme_color`
- **Map tiles**: `config.map.tile_provider` (OpenStreetMap, CartoDB, etc.)
- **Default location**: `config.map.default_center`
- **Predefined locations**: `config.map.predefined_locations[]`

## 🎯 Event Data Format

Events are loaded from `static/events.json`:

```json
{
  "events": [
    {
      "id": "event_1",
      "title": "Event Name",
      "description": "Event description",
      "location": {
        "name": "Venue Name",
        "lat": 50.3175,
        "lon": 11.9165
      },
      "start_time": "2025-12-09T19:00:00",
      "end_time": "2025-12-09T23:00:00",
      "url": "https://example.com/event",
      "category": "on-stage",
      "source": "manual",
      "status": "published"
    }
  ]
}
```

## 🚀 Quick Start

### Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/feileberlin/krwl-hof.git
   cd krwl-hof
   ```

2. **Download dependencies** (Leaflet map library)
   ```bash
   ./download-libs.sh
   ```
   
   This downloads Leaflet.js locally for better performance and offline PWA support.

3. **Serve the static files**
   ```bash
   cd static
   python3 -m http.server 8000
   ```

4. **Open in browser**
   ```
   http://localhost:8000
   ```

### Production Deployment

The `static/` directory contains all files needed for deployment:

- **GitHub Pages**: Already configured (see `.nojekyll`)
- **Netlify/Vercel**: Point to `static/` directory
- **Any static host**: Upload `static/` contents

## ♿ Accessibility

This application follows WCAG 2.1 Level AA guidelines:

- ✅ Semantic HTML5 (main, nav, footer, etc.)
- ✅ ARIA landmarks and labels
- ✅ Skip to content link for keyboard navigation
- ✅ Focus indicators for all interactive elements
- ✅ Screen reader announcements for dynamic updates
- ✅ Keyboard navigation support
- ✅ Sufficient color contrast
- ✅ Descriptive alt text for images

### Screen Reader Support
The application provides context to screen reader users:
- Explains the fullscreen map interface on page load
- Announces filter changes and event counts
- Provides ARIA labels for all controls
- Uses semantic HTML for proper navigation

## 🧪 Testing

### Running Tests

**Documentation validation:**
```bash
python3 docs/build_docs.py --validate
```

This validates:
- All required files exist
- Config has all required sections
- Documentation matches code features
- All links in docs are valid

**Scraper tests:**
```bash
python3 test_scraper.py --verbose
```

This tests:
- Manual event creation
- Event deduplication logic
- Source type handling (RSS, API, HTML)
- Data validation
- Error handling

**Filter tests:**
```bash
python3 test_filters.py --verbose
```

This tests:
- Time filtering (sunrise, sunday, full moon, hours)
- Distance filtering (15 min foot, 10 min bike, 1 hr transport)
- Event type filtering
- Location filtering

**Feature verification:**
```bash
python3 verify_features.py --verbose
```

This verifies:
- All declared features are implemented
- Feature registry matches codebase
- No undeclared features exist

### Manual Testing Checklist
- [ ] Map loads and displays correctly
- [ ] Filters update event markers
- [ ] Markers show time tooltips on hover
- [ ] Popups show full event details on click
- [ ] Responsive design works on mobile
- [ ] PWA installs correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces updates

## 📝 Project Structure

```
krwl-hof/
├── .github/
│   └── workflows/          # CI/CD workflows
├── static/                 # All static files for deployment
│   ├── index.html         # Main HTML entry point
│   ├── manifest.json      # PWA manifest
│   ├── config.json        # App configuration
│   ├── events.json        # Event data
│   ├── css/
│   │   └── style.css      # All styles
│   ├── js/
│   │   └── app.js         # Application logic
│   ├── favicon.svg        # Browser favicon
│   ├── logo.svg           # App logo
│   ├── icon-*.svg         # PWA icons
│   └── PWA_README.md      # PWA documentation
├── src/                    # Python backend (scraping/editing)
│   └── modules/
├── data/                   # Event data storage
├── docs/                   # Documentation
│   └── build_docs.py      # Documentation builder
└── README.md              # This file
```

## 🔧 Development

### Adding New Features

1. **Update code** in `static/` directory
2. **Update config** if adding configurable options
3. **Test locally** with a simple HTTP server
4. **Run docs builder** to update README
5. **Commit changes** including updated docs

### Code Style
- **HTML**: Semantic HTML5, ARIA labels
- **CSS**: Mobile-first, BEM-like naming
- **JavaScript**: ES6+, pure vanilla JS, JSDoc comments
- **Config**: JSON with comments in docs

## 📊 Browser Support

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome  | ✅ Full | ✅ Full |
| Firefox | ✅ Full | ✅ Full |
| Safari  | ✅ Full | ⚠️ Limited PWA |
| Edge    | ✅ Full | ✅ Full |
| Samsung | - | ✅ Full |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run documentation builder
5. Submit a pull request

### Documentation Requirements
- All code changes must be documented
- Run `python3 docs/build_docs.py` before committing
- Update config.json for new configurable features
- Add JSDoc comments for new functions

### Managing Dependencies
The project uses a custom library manager for CDN replacements:

```bash
# Download/update libraries
python3 manage_libs.py download

# Verify installations
python3 manage_libs.py verify

# List managed libraries
python3 manage_libs.py list

# Update a specific library
python3 manage_libs.py update leaflet 1.9.5
```

See `static/lib/README.md` for more details.

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- **Leaflet.js** - Open-source map library
- **CartoDB** - Dark map tiles
- **OpenStreetMap** - Map data contributors

## 📞 Support

For issues and questions:
- GitHub Issues: [github.com/feileberlin/krwl-hof/issues](https://github.com/feileberlin/krwl-hof/issues)
- See imprint link in app for contact info

---

**Built with ❤️ for the KRWL HOF community**

*Last updated: 2025-12-09 02:52:24*
*Auto-generated by docs/build_docs.py*
