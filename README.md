# KRWL HOF Community Events

> Mobile-first Progressive Web App for discovering local community events with interactive geolocation filtering

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web-apps/)
[![Accessibility](https://img.shields.io/badge/A11y-WCAG_2.1_AA-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

🌐 **Live Site**: [https://krwl.in](https://krwl.in)

## 🎯 Overview

KRWL HOF is a grassroots, mobile-first Progressive Web App (PWA) for discovering local community events in Hof and the surrounding region (Bavaria, Germany). Built by and for the local community, it aggregates events from multiple sources—from punk concerts to farmers markets, from Off-Theater performances to VHS courses.

The app features an interactive map with geolocation filtering, showing events within walking distance that are happening soon. It's installable as a native app on mobile and desktop, works offline, and is fully accessible.

## 📦 Features

### 🗺️ Interactive Map
- Leaflet.js-based interactive map
- Custom Lucide icon markers for 29 event categories
- Click markers to see event details
- Responsive design works on all screen sizes

### 📍 Smart Filtering
- **Geolocation**: Shows events within 5km radius
- **Time-based**: Shows events until next sunrise
- **Distance**: Configurable radius filter
- **Categories**: Filter by event type (29 categories supported)

### 📱 Progressive Web App
- Installable on mobile and desktop
- Works offline (manifest.json)
- Mobile-first responsive design
- WCAG 2.1 Level AA accessible

### 🌐 Internationalization
- English and German translations
- Runtime language switching
- Extensible i18n system

### 🔄 Auto-Scraping
- Configurable event sources
- Automated scraping via GitHub Actions
- Editorial workflow for quality control
- Support for RSS, HTML, and API sources

## 🚀 Quick Start

### For End Users

Visit [https://krwl.in](https://krwl.in) to use the app!

**Install as PWA:**
1. Open krwl.in in your mobile browser
2. Tap "Add to Home Screen" (iOS) or "Install" (Android)
3. Launch from your home screen like a native app

### For Developers

```bash
# Clone repository
git clone https://github.com/feileberlin/krwl-hof.git
cd krwl-hof

# Install Python dependencies
pip install -r requirements.txt

# Download frontend libraries
python3 src/event_manager.py libs

# Generate static site
python3 src/event_manager.py generate

# Run local server
cd static
python3 -m http.server 8000

# Open http://localhost:8000
```

## 📚 Documentation

### Core Documentation
- [Features Registry](features.json) - Complete feature list with implementation details
- [Quick Reference](docs/QUICK_REFERENCE.md) - Common commands and workflows
- [KISS Improvements](docs/KISS_IMPROVEMENTS.md) - Simplifications and KISS principles
- [Changelog](docs/CHANGELOG.md) - Version history and updates

### Developer Guides
- [Component System](src/templates/components/README.md) - Component-based templating
- [CSS Variables](src/templates/components/variables-reference.md) - Design token reference
- [Testing Guide](tests/README.md) - Running and writing tests
- [Scripts Guide](scripts/README.md) - Available utility scripts
- [Documentation Standard](.github/DOCUMENTATION_STANDARD.md) - How to write docs

### Setup Guides
- [Dev Container](.devcontainer/README.md) - VSCode dev container setup

## 🔧 Configuration

### Environment Auto-Detection

The app automatically detects its environment:
- **Development**: Debug mode, demo events, DEV watermark
- **CI/Production**: Optimized mode, real events only
- **Supported Platforms**: GitHub Pages, Vercel, Netlify, Heroku, Railway, Render, Fly.io, Google Cloud Run, AWS

No manual configuration needed—just deploy!

### Design Tokens

Instant rebranding via `config.json`:

```bash
# Edit design section in config.json
vim config.json

# Generate CSS custom properties
python3 src/templates/components/generate_design_tokens.py

# Rebuild site
python3 src/event_manager.py generate

# Deploy
git commit -am "🎨 Rebrand" && git push
```

See [Component System](src/templates/components/README.md) for details.

## 🛠️ CLI Usage

### Interactive TUI

```bash
# Launch text-based UI
python3 src/event_manager.py
```

### Event Management

```bash
# Scrape events from configured sources
python3 src/event_manager.py scrape

# List all published events
python3 src/event_manager.py list

# List pending events (awaiting approval)
python3 src/event_manager.py list-pending

# Approve a pending event
python3 src/event_manager.py publish EVENT_ID

# Reject a pending event
python3 src/event_manager.py reject EVENT_ID

# Bulk operations (supports wildcards)
python3 src/event_manager.py bulk-publish "pending_*"
python3 src/event_manager.py bulk-reject "pending_*"
```

### Site Generation

```bash
# Full site generation (with linting)
python3 src/event_manager.py generate

# Fast event update (no full rebuild)
python3 src/event_manager.py update

# Download/update dependencies
python3 src/event_manager.py libs

# Verify dependencies
python3 src/event_manager.py libs verify
```

### Data Management

```bash
# Archive past events
python3 src/event_manager.py archive

# Load example data (development)
python3 src/event_manager.py load-examples

# Clear all event data
python3 src/event_manager.py clear-data
```

## 🧪 Testing

### Run Tests

```bash
# All tests
python3 -m pytest tests/ -v

# Specific test suites
python3 tests/test_components.py          # Component system
python3 tests/test_scraper.py             # Event scraping
python3 tests/test_filters.py             # Event filtering
python3 tests/test_event_schema.py        # Event validation
python3 tests/test_translations.py        # i18n
python3 tests/test_linter.py              # Code linting

# Validate documentation
python3 scripts/validate_docs.py --verbose
```

### Code Quality

```bash
# Lint all code
python3 src-modules/linter.py

# Check KISS compliance
python3 src-modules/kiss_checker.py

# Verify features registry
python3 src-modules/feature_verifier.py --verbose
```

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.x (standard library preferred)
- Modular CLI and TUI
- BeautifulSoup4 for HTML scraping
- Feedparser for RSS feeds

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Leaflet.js for maps
- Lucide icons
- CSS custom properties for theming

**Build:**
- Static site generation (single HTML file)
- All assets inlined
- Component-based templating
- Design token system

### Project Structure

```text
krwl-hof/
├── src/
│   ├── event_manager.py              # Main CLI entry point
│   └── templates/
│       ├── index.html                # Main template
│       └── components/               # Modular components
├── src-modules/                      # Core modules (flat)
│   ├── scraper.py                    # Event scraping
│   ├── editor.py                     # Editorial workflow
│   ├── site_generator.py             # HTML generation
│   ├── linter.py                     # Code validation
│   └── utils.py                      # Utilities
├── assets/
│   ├── css/                          # Source stylesheets (modular)
│   ├── js/                           # Source scripts
│   ├── markers/                      # SVG marker icons
│   ├── leaflet/                      # Leaflet.js library
│   └── lucide/                       # Lucide icons library
├── target/                           # Generated site (output)
├── event-data/                       # Event JSON files
├── tests/                            # Test suites
├── scripts/                          # Utility scripts
├── docs/                             # Additional documentation
└── config.json                       # Main configuration
```

## 🤝 Contributing

### Before Contributing

1. Read [Documentation Standard](.github/DOCUMENTATION_STANDARD.md)
2. Check [Features Registry](features.json) for existing features
3. Run tests before submitting PR
4. Follow KISS principles (see [KISS Improvements](docs/KISS_IMPROVEMENTS.md))

### Adding Features

```bash
# Implement feature (add code and tests)

# Update features.json

# Validate
python3 src-modules/feature_verifier.py --verbose

# Run tests
python3 -m pytest tests/ -v

# Submit PR
```

### Code Style

- **Python**: PEP 8, standard library preferred
- **JavaScript**: ES6+, vanilla only (no frameworks)
- **CSS**: Mobile-first, use CSS custom properties
- **Documentation**: Follow the standard, use emojis for headers

## ❓ Troubleshooting

### Site won't generate

```bash
# Check dependencies
python3 src/event_manager.py libs verify

# Download if missing
python3 src/event_manager.py libs

# Try generating again
python3 src/event_manager.py generate
```

### Tests failing

```bash
# Check if you're in the right directory
pwd  # Should be project root

# Install dependencies
pip install -r requirements.txt

# Run specific test with verbose output
python3 tests/test_*.py --verbose
```

### Map not loading

1. Check browser console for errors
2. Verify `target/index.html` exists
3. Ensure Leaflet.js is downloaded (`libs` command)
4. Try clearing browser cache

### Events not showing

1. Check `event-data/events.json` has events
2. Verify events are not in the past
3. Check filter settings (distance, time)
4. Try the "Load Examples" command for test data

## 📖 Resources

### External Documentation
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)
- [Lucide Icons](https://lucide.dev/)
- [Progressive Web Apps](https://web.dev/progressive-web-apps/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Related Projects
- [Event Scraping Tools](https://github.com/topics/event-scraping)
- [Geolocation APIs](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- **Leaflet.js** - Interactive maps library
- **Lucide** - Beautiful open-source icons
- **OpenStreetMap** - Map data contributors
- **CartoDB** - Dark map tile provider
- **GitHub** - Hosting and CI/CD platform

---

**Built with 💖 in Hof, Bavaria**

For questions or issues, please [open an issue](https://github.com/feileberlin/krwl-hof/issues) on GitHub.
