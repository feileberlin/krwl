# KRWL HOF Project Structure

> Clean, KISS-compliant organization for a static site generator

## 🎯 Philosophy

- **src/** - All source code (templates, styles, scripts, Python)
- **data/** - All data files (events, config, translations)
- **static/** - Build output and static assets (generated + libraries)
- **tests/** - Test files
- **scripts/** - Utility scripts
- **docs/** - Documentation

## 📦 Complete Structure

```
krwl-hof/
├── src/                          # SOURCE CODE
│   ├── components/               # HTML component templates (8 files)
│   │   ├── html-head.html
│   │   ├── html-body-open.html
│   │   ├── html-body-close.html
│   │   ├── map-main.html
│   │   ├── dashboard-aside.html
│   │   ├── filter-nav.html
│   │   ├── noscript-content.html
│   │   └── variables-reference.md
│   ├── css/                      # CSS source files (modular)
│   │   ├── base.css              # Global reset & body
│   │   ├── map.css               # Map container & Leaflet
│   │   ├── filters.css           # Filter bar & controls
│   │   ├── dashboard.css         # Dashboard modal
│   │   ├── mobile.css            # Mobile responsive
│   │   ├── leaflet-custom.css    # Leaflet customization
│   │   ├── scrollbar.css         # Scrollbar styling
│   │   ├── style.css             # Main CSS (legacy/fallback)
│   │   └── time-drawer.css       # Time drawer styles
│   ├── js/                       # JavaScript source files (modular)
│   │   ├── app.js                # Main application (1730 lines)
│   │   ├── i18n.js               # Internationalization (232 lines)
│   │   └── time-drawer.js        # Time-based markers (536 lines)
│   ├── templates/                # HTML templates
│   │   └── index.html            # Main template
│   ├── modules/                  # Python application modules
│   │   ├── scraper.py            # Event scraping
│   │   ├── editor.py             # Editorial workflow
│   │   ├── config_editor.py      # Config TUI
│   │   ├── feature_verifier.py   # Feature validation
│   │   ├── filter_tester.py      # Filter testing
│   │   ├── kiss_checker.py       # KISS compliance
│   │   ├── lucide_markers.py     # Marker generation
│   │   ├── scheduler.py          # Scheduling
│   │   ├── workflow_launcher.py  # GitHub Actions
│   │   └── smart_scraper/        # Smart scraping system
│   ├── tools/                    # Build tools
│   │   ├── generate_design_tokens.py  # CSS tokens generator
│   │   └── migrate_css_to_tokens.py   # CSS migration tool
│   ├── generator.py              # Site generator (main build system)
│   ├── linter.py                 # Code linting for build
│   ├── utils.py                  # Shared utilities
│   ├── event_manager.py          # Main CLI entry point
│   └── design-tokens.css         # Generated design tokens
│
├── data/                         # DATA FILES
│   ├── events.json               # Published events
│   ├── pending_events.json       # Awaiting approval
│   ├── rejected_events.json      # Rejected events
│   ├── events.demo.json          # Demo data
│   ├── content.json              # English translations
│   ├── content.de.json           # German translations
│   └── config.json               # Main configuration
│
├── static/                       # BUILD OUTPUT + STATIC ASSETS
│   ├── index.html                # Generated site (output)
│   ├── leaflet/                  # Leaflet.js library
│   │   ├── leaflet.js
│   │   ├── leaflet.css
│   │   └── images/
│   ├── lucide/                   # Lucide icons library
│   │   └── lucide.min.js
│   ├── markers/                  # SVG marker icons (78 files)
│   ├── favicon.svg               # App icon
│   ├── manifest.json             # PWA manifest
│   └── *.svg                     # Other icons
│
├── tests/                        # TEST FILES
│   ├── test_components.py
│   ├── test_scraper.py
│   ├── test_filters.py
│   ├── test_linter.py
│   └── ...
│
├── scripts/                      # UTILITY SCRIPTS
│   ├── validate_docs.py
│   ├── test_documentation.py
│   └── ...
│
├── docs/                         # DOCUMENTATION
│   ├── CHANGELOG.md
│   ├── QUICK_REFERENCE.md
│   ├── COLOR_SCHEME_BARBIE_PINK.md
│   └── ...
│
└── .github/                      # GITHUB CONFIG
    ├── workflows/
    └── DOCUMENTATION_STANDARD.md
```

## 🔧 Key Principles

### 1. Clear Separation of Concerns
- **src/** = Code you write
- **data/** = Data files
- **static/** = Generated output + third-party assets
- **tests/** = Tests
- **scripts/** = Tools
- **docs/** = Documentation

### 2. Minimal Nesting
- Maximum 2 levels deep in most cases
- Flat structures where possible
- Easy to navigate and understand

### 3. Modular Organization
- **src/css/** - 9 focused CSS modules (~85 lines each)
- **src/js/** - 3 focused JS modules (app, i18n, time-drawer)
- **src/components/** - 8 HTML component templates
- **src/modules/** - Python modules by function

### 4. Build System in src/
All build/generation related code in `src/`:
- `generator.py` - Main site generator
- `linter.py` - Build-time validation
- `utils.py` - Shared utilities
- `tools/` - Build tools and generators

## 🚀 Workflow

### Development
```bash
# Edit source files
vim src/css/map.css
vim src/js/app.js
vim src/components/filter-nav.html

# Generate design tokens
python3 src/tools/generate_design_tokens.py

# Build site
python3 src/event_manager.py generate

# Test locally
cd static && python3 -m http.server 8000
```

### Adding Features
1. Edit source in `src/`
2. Update `data/config.json` if needed
3. Regenerate site
4. Test with `tests/`

### Data Management
```bash
# Scrape events
python3 src/event_manager.py scrape

# Review pending
python3 src/event_manager.py  # Opens TUI

# Publish events
python3 src/event_manager.py publish EVENT_ID
```

## 📊 Statistics

- **Total Lines**: ~2,500 lines of custom code
- **Dependencies**: 2 (Leaflet.js, Lucide icons)
- **CSS Modules**: 9 files (~767 lines total)
- **JS Modules**: 3 files (~2,498 lines total)
- **HTML Components**: 8 templates
- **Python Modules**: 15+ modules
- **Directory Depth**: Maximum 2 levels
- **Top-level Dirs**: 6 (src, data, static, tests, scripts, docs)

## ✅ Benefits

1. **Intuitive**: Standard conventions (src/, data/, static/)
2. **Maintainable**: Clear separation, focused modules
3. **Scalable**: Easy to add new modules
4. **KISS**: Simple, flat, no over-engineering
5. **Professional**: Follows Django/Flask/Node.js patterns

## 🔄 Migration from Old Structure

### Old → New Mapping
- `assets/css/` → `src/css/`
- `assets/js/` → `src/js/`
- `src/templates/components/` → `layouts/components/`
- `src-modules/` → `src/modules/` + `src/`
- `event-data/` → `data/`
- `config.json` → `data/config.json`
- `assets/lib/` → `static/` (libraries)

---

**Last Updated**: January 2026  
**Status**: ✅ KISS-compliant, production-ready
