# KRWL HOF Community Events

> Community events scraper and viewer with geolocation filtering

**🌐 Live Site: [https://krwl.in](https://krwl.in)**

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web_apps/)
[![Accessibility](https://img.shields.io/badge/A11y-Compliant-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 🎯 What is This?

A **grassroots, mobile-first** Progressive Web App (PWA) for discovering local community events in Hof and surrounding region (Bavaria, Germany). Built by and for the local community - from punk concerts to farmers markets, from Off-Theater to VHS courses.

**Visit the live app at [krwl.in](https://krwl.in)** to see events on an interactive map!

### ✨ Features

- 📱 **PWA**: Installable as native app on mobile and desktop
- 🗺️ **Interactive Map**: Leaflet.js with event markers and clustering
- 📍 **Geolocation Filtering**: Shows events within 5.0km radius
- 🌅 **Time-based Filtering**: Shows events until next_sunrise
- 🌐 **Bilingual**: English and German (i18n support)
- ♿ **Accessible**: WCAG 2.1 Level AA compliant
- 📱 **Responsive**: Mobile-first design, works on all screen sizes
- 🔄 **Auto-scraping**: Configurable event sources with automatic updates

## 🆕 Want to Build Your Own Event Discovery App?

**See [INITIATE.md](INITIATE.md)** for a comprehensive bootstrap guide on how to implement a project like this from scratch without common pitfalls. Get a working MVP in ~1 day with our step-by-step roadmap!

## 🚀 Quick Start for Developers

Want to run it locally or contribute?

### Prerequisites
- Python 3.x
- Modern web browser
- Internet connection (for Leaflet.js CDN)

### Setup

```bash
# Clone the repository
git clone https://github.com/feileberlin/krwl-hof.git
cd krwl-hof

# Install system dependencies (for Facebook flyer OCR)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
# macOS:
brew install tesseract tesseract-lang

# Install Python dependencies
pip install -r requirements.txt

# Download frontend libraries (Leaflet.js)
python3 src/event_manager.py dependencies fetch

# Run locally
cd static
python3 -m http.server 8000
```

Open http://localhost:8000 in your browser

### 📸 Facebook Flyer Scraping with OCR

This project includes **automatic event extraction from Facebook page flyer images** using Optical Character Recognition (OCR). When you scrape Facebook pages like "Punk in Hof", the system:

1. **Scans posts** - Downloads images from Facebook posts
2. **OCR Analysis** - Extracts text from flyer images (dates, times, event names)
3. **Smart Detection** - Identifies event-related keywords and patterns
4. **Auto-Creation** - Creates pending events from flyer data

**Requirements:**
- Tesseract OCR system library (see installation above)
- Python packages: `Pillow`, `pytesseract`, `exifread` (included in requirements.txt)

**How to enable:**
Facebook sources in `config.json` should have `scan_posts: true`:

```json
{
  "name": "Punkrock in Hof",
  "url": "https://www.facebook.com/people/Punk-in-Hof/100090512583516/",
  "type": "facebook",
  "enabled": true,
  "options": {
    "scan_posts": true,
    "ocr_enabled": true,  // Optional - defaults to true when scan_posts is enabled
    "category": "music"
  }
}
```

**Note:** `ocr_enabled` defaults to `true` if not specified, so it's optional. Facebook scraping works without API credentials but may be limited by Facebook's page structure changes.

## 📚 Documentation Philosophy

**Keep It Simple, Stupid (KISS)**

All documentation lives in:
1. **Code comments** - In the source files where the logic lives
2. **CLI --help** - Every script has comprehensive help text
3. **TUI hints** - Contextual tooltips in the interactive interface
4. **This README** - One consolidated guide (you're reading it!)

No complex documentation systems. No wiki syncing. No auto-generated multi-file docs. Just code comments, CLI help, and this README.

## 🛠️ CLI Usage

### Event Manager (Main Interface)

The primary tool for managing events:

```bash
python3 src/event_manager.py              # Launch interactive TUI
python3 src/event_manager.py --help       # Show all commands
```

#### Full CLI Help

```

KRWL HOF Community Events Manager
==================================

A modular Python TUI for managing community events with geolocation
and sunrise filtering.

USAGE:
    python3 event_manager.py [COMMAND] [OPTIONS]

COMMANDS:
    (no command)              Launch interactive TUI (default)
    setup                     Show detailed setup instructions for your own site
    scrape                    Scrape events from configured sources
    review                    Review pending events interactively
    publish EVENT_ID          Publish a specific pending event
    reject EVENT_ID           Reject a specific pending event
    bulk-publish IDS          Bulk publish pending events (comma-separated IDs/patterns)
    bulk-reject IDS           Bulk reject pending events (comma-separated IDs/patterns)
    list                      List all published events
    list-pending              List all pending events
    
    generate                  Generate static site with inlined HTML
                              - Ensures dependencies (Leaflet.js)
                              - Loads all resources (CSS, JS, events, translations)
                              - Builds HTML from templates with inlined assets
                              - Lints and validates content
                              - Outputs: public/index.html (self-contained)
    update                    Update events data in existing site (fast)
    dependencies fetch        Fetch third-party dependencies
    dependencies check        Check if dependencies are present
    
    schema validate           Validate events against schema
    schema migrate            Migrate events to new schema format
    schema categories         List all valid event categories
    
    cache stats               Show cache statistics
    cache clear               Clear asset cache
    cache inspect KEY         Inspect specific cache entry
    
    icons                     Show current icon mode
    icons mode [MODE]         Set or show icon mode (svg-paths | base64)
    icons switch              Interactive icon mode switcher
    icons compare             Compare icon modes
    
    config validate           Validate configuration file
    
    test                      Run all tests
    test --list               List available test categories and tests
    test core                 Run core functionality tests
    test features             Run feature tests
    test infrastructure       Run infrastructure tests
    test scraper              Run specific test (e.g., test_scraper)
    test --verbose            Run tests with verbose output
    
    utils                     List all utility commands
    utils --list              List all utility commands
    utils kiss-check          Check KISS compliance
    utils verify-features     Verify features are present
    utils config-edit         Launch config editor
    
    docs                      List all documentation tasks
    docs --list               List all documentation tasks
    docs readme               Generate README.md
    docs demos                Generate demo events
    docs lint-markdown        Lint markdown files
    docs generate             Run all generation tasks
    docs validate             Run all validation tasks
    
    archive-monthly           Archive old events based on retention window
    archive-monthly --dry-run Preview archiving without making changes
    archive-info              Show archiving configuration and existing archives
    archive                   Archive past events to archived_events.json (legacy)
    load-examples             Load example data for development
    clear-data                Clear all event data
    scraper-info              Show scraper capabilities (JSON output for workflows)
    
OPTIONS:
    -h, --help               Show this help message
    -v, --version            Show version information
    -c, --config PATH        Use custom config file
    
EXAMPLES:
    # Launch interactive TUI
    python3 event_manager.py
    
    # Generate static site (runtime-configurable)
    python3 event_manager.py generate
    
    # Fast content update
    python3 event_manager.py update
    
    # Fetch dependencies
    python3 event_manager.py dependencies fetch
    
    # Check dependencies
    python3 event_manager.py dependencies check
    
    # Scrape events from sources
    python3 event_manager.py scrape
    
    # Show scraper capabilities (for workflow introspection)
    python3 event_manager.py scraper-info
    
    # List all published events
    python3 event_manager.py list
    
    # Publish a single event
    python3 event_manager.py publish pending_1
    
    # Bulk publish using wildcards
    python3 event_manager.py bulk-publish "pending_*"
    
    # Load example data for testing
    python3 event_manager.py load-examples
    
    # Run all tests
    python3 event_manager.py test
    
    # Run specific test category
    python3 event_manager.py test core
    python3 event_manager.py test features
    
    # Run individual test
    python3 event_manager.py test scraper
    python3 event_manager.py test translations
    
    # List available tests
    python3 event_manager.py test --list
    
    # Run tests with verbose output
    python3 event_manager.py test --verbose
    python3 event_manager.py test core --verbose
    
    # Run utilities
    python3 event_manager.py utils --list
    python3 event_manager.py utils kiss-check
    python3 event_manager.py utils verify-features --verbose
    
    # Documentation tasks
    python3 event_manager.py docs --list
    python3 event_manager.py docs readme
    python3 event_manager.py docs lint-markdown --all
    python3 event_manager.py docs lint-markdown README.md
    python3 event_manager.py docs lint-markdown --fix --all
    python3 event_manager.py docs generate
    python3 event_manager.py docs validate
    
    # Get help
    python3 event_manager.py --help

WILDCARD PATTERNS:
    Bulk operations support Unix-style wildcards:
    *       Matches any characters (including none)
    ?       Matches exactly one character
    [seq]   Matches any character in seq
    [!seq]  Matches any character not in seq
    
    Examples:
    pending_*              Match all events with IDs starting with 'pending_'
    html_frankenpost_*     Match all events from the Frankenpost source
    *AUCHEVENT*            Match any event with 'AUCHEVENT' in the ID
    pending_[1-3]          Match pending_1, pending_2, pending_3
    
DOCUMENTATION:
    Full documentation available in README.txt or via the TUI
    (Main Menu → View Documentation)

For more information, visit:
    https://github.com/feileberlin/krwl-hof


```

## ⚙️ Configuration

All configuration lives in `config.json`:

```json
{
  "app": {
    "name": "KRWL HOF Community Events",
    "description": "Community events scraper and viewer with geolocation filtering"
  },
  "map": {
    "default_center": {"lat": 50.3167, "lon": 11.9167},
    "default_zoom": 13
  },
  "filtering": {
    "max_distance_km": 5.0,
    "show_until": "next_sunrise"
  },
  "scraping": {
    "schedule": {"timezone": "Europe/Berlin", "times": ["04:00", "16:00"], "_comment_schedule_usage": "Only active in CI/production environments for automated scraping"},
    "sources": [...12 configured sources]
  }
}
```

### What You Can Customize

- **App name/description**: `config.app.*`
- **Map center and zoom**: `config.map.*`
- **Distance filter**: `config.filtering.max_distance_km`
- **Time filter**: `config.filtering.show_until`
- **Scraping schedule**: `config.scraping.schedule`
- **Event sources**: `config.scraping.sources[]` (RSS, HTML, API)
- **Editor settings**: `config.editor.*`

## 🧪 Testing

Run tests before committing:

```bash
# Feature verification
python3 scripts/verify_features.py --verbose

# Event schema validation
python3 tests/test_event_schema.py --verbose

# Scraper tests
python3 tests/test_scraper.py --verbose

# Filter tests (integrated module)
python3 src/event_manager.py test filters --verbose

# Translation tests
python3 tests/test_translations.py --verbose

# KISS principle compliance
python3 scripts/check_kiss.py --verbose
```

## 📝 Project Structure

```
krwl-hof/
├── config.json          # Unified configuration (auto-detects environment)
├── static/              # Only index.html
│   └── index.html       # Main app (auto-generated, DO NOT EDIT)
├── assets/              # Frontend assets (CSS, JS, libraries, icons)
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript modules
│   ├── lib/             # Third-party libraries (Leaflet.js)
│   ├── markers/         # Event marker SVG icons
│   ├── manifest.json    # PWA manifest
│   └── *.svg            # App icons (favicon, PWA icons, logo)
├── data/                # Event and translation data
│   ├── events.json      # Published events
│   ├── pending_events.json  # Events awaiting approval
│   ├── rejected_events.json # Rejected events
│   ├── archived_events.json # Past events
│   ├── events.demo.json # Demo events for testing
│   ├── content.json     # English translations
│   ├── content.de.json  # German translations
│   └── old/             # Historical event archives
├── src/                 # Python backend
│   ├── event_manager.py # Main CLI/TUI entry point
│   └── modules/         # Modular components
├── scripts/             # Utility scripts
├── tests/               # Test suite
└── README.md            # This file (auto-generated)
```

## 🔄 Workflow

### 1. Scraping Events

```bash
# Scrape from configured sources
python3 src/event_manager.py scrape

# Or interactively
python3 src/event_manager.py  # Option 1: Scrape New Events
```

Scraped events go to `static/pending_events.json` for editorial review.

### 2. Editorial Review

```bash
# Review pending events interactively
python3 src/event_manager.py review

# Or approve/reject specific events
python3 src/event_manager.py publish EVENT_ID
python3 src/event_manager.py reject EVENT_ID

# Bulk operations (supports wildcards)
python3 src/event_manager.py bulk-publish "pending_*"
python3 src/event_manager.py bulk-reject "pending_*"
```

Approved events move to `assets/json/events.json` and appear on the map.

### 3. Static Site Generation

```bash
# Generate complete static site
python3 src/event_manager.py generate

# Fast event update (no full rebuild)
python3 src/event_manager.py update
```

Output: `static/index.html` (single-file HTML with everything inlined)

## 🕷️ Adding Event Sources

Edit `config.json`:

```json
{
  "scraping": {
    "sources": [
      {
        "name": "Your Event Source",
        "url": "https://example.com/events",
        "type": "rss",  // or "html", "api"
        "enabled": true,
        "notes": "Description of the source"
      }
    ]
  }
}
```

Test the scraper:
```bash
python3 src/event_manager.py scrape
python3 tests/test_scraper.py --verbose
```

## 🌐 Internationalization (i18n)

The app supports English and German with **URL-based language routing**:

### Language URLs

- **German (Default)**: `krwl.in/` - German is the default language at the root
- **English**: `krwl.in/en/` - English is available at the `/en/` path

**No language menu is provided** - language selection is purely URL-based. Users can switch languages by navigating to the appropriate URL.

### Language Detection Priority

The i18n system detects language in this order:

1. **URL Path** (highest priority): `/en/` → English, `/` → German
2. **Config Setting**: If URL doesn't specify, check `config.json`
3. **Browser Language**: Auto-detect from browser settings
4. **Default Fallback**: German (de)

### Translation Files

- `assets/json/i18n/content.json` - English translations
- `assets/json/i18n/content.de.json` - German translations

### Adding Translations

Add translations using the key path format:
```json
{
  "section": {
    "key": "Translation text"
  }
}
```

In code: `i18n.t('section.key')`

### Technical Details

- The site generator (`site_generator.py`) creates two HTML files:
  - `public/index.html` - German version (root)
  - `public/en/index.html` - English version
- Translation JSON files are copied to both directories
- The `i18n.js` module handles URL detection and content loading
- Relative paths are adjusted automatically for subdirectories

## 🧪 Advanced Features

### Dynamic Event Templates with Relative Times

The app supports **dynamic event templates** with relative time specifications. This feature allows demo events to always display accurate relative times like "happening now" or "starting in 5 minutes" on every page reload, without requiring manual timestamp updates.

#### How It Works

Demo events can include a `relative_time` field that specifies how to calculate actual timestamps dynamically:

```json
{
  "id": "demo_happening_now",
  "title": "[DEMO] Event Happening Now",
  "relative_time": {
    "type": "offset",
    "minutes": -30,
    "duration_hours": 2
  }
}
```

When the app loads, the `processTemplateEvents()` method in `assets/js/app.js` detects events with `relative_time` specifications and calculates actual timestamps based on the current browser time.

#### Relative Time Specifications

**Type 1: Offset (Relative to Current Time)**

Events that occur relative to the current moment:

```json
{
  "type": "offset",
  "hours": 1,           // Optional: hours offset from now
  "minutes": 5,         // Optional: minutes offset from now
  "duration_hours": 2,  // Event duration in hours
  "timezone_offset": 0  // Optional: timezone offset for testing
}
```

Examples:
- `{"type": "offset", "minutes": -30, "duration_hours": 2}` - Started 30 minutes ago
- `{"type": "offset", "minutes": 5, "duration_hours": 2}` - Starts in 5 minutes
- `{"type": "offset", "hours": 1, "duration_hours": 3}` - Starts in 1 hour, lasts 3 hours

**Type 2: Sunrise Relative (Relative to Next Sunrise)**

Events that occur relative to the next sunrise (simplified as 6:00 AM):

```json
{
  "type": "sunrise_relative",
  "start_offset_hours": -2,    // Optional: hours offset for start time
  "start_offset_minutes": 0,   // Optional: minutes offset for start time
  "end_offset_hours": 0,       // Optional: hours offset for end time
  "end_offset_minutes": -5     // Optional: minutes offset for end time
}
```

Examples:
- `{"type": "sunrise_relative", "end_offset_minutes": -5, "start_offset_hours": -2}` - Ends 5 minutes before sunrise
- `{"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}` - Starts 2 hours before sunrise, ends 1 hour after

#### Generating Demo Events

Run the demo event generator script:

```bash
python3 scripts/generate_demo_events.py > data/events.demo.json
```

This creates template events with `relative_time` specifications. See inline comments in `scripts/generate_demo_events.py` for implementation details.

#### Benefits

- **Always Fresh**: Demo events always show accurate relative times
- **Filter Testing**: Test time-based filters (sunrise, 6h, 12h) with realistic data
- **Timezone Testing**: Verify international time handling
- **No Maintenance**: No need to manually update demo event timestamps
- **Backward Compatible**: Real events without `relative_time` work unchanged

For technical implementation details, see inline comments in:
- `scripts/generate_demo_events.py` - Template generation logic
- `assets/js/app.js` - `processTemplateEvents()` method

### Screenshot Generation

The app includes a **ready signal** that indicates when the page is fully loaded and ready for screenshot capture. This solves the problem of screenshots being taken before the map and event data have finished loading.

#### The Ready Signal

When ready, the app:
1. Sets a body attribute: `<body data-app-ready="true">`
2. Dispatches a custom event on the `window` object with metadata

#### Quick Usage Example (Playwright)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Set viewport for desired screenshot size
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # Navigate to the page
    page.goto('http://localhost:8000')
    
    # Wait for app to be ready (max 30 seconds)
    page.wait_for_selector('body[data-app-ready="true"]', timeout=30000)
    
    # Optional: Wait a bit more for map tiles to fully render
    page.wait_for_timeout(2000)
    
    # Take screenshot
    page.screenshot(path='screenshot.png', full_page=True)
    
    browser.close()
```

#### Complete Screenshot Script

For a full example that generates both mobile and desktop screenshots, see `scripts/generate_screenshots.py`:

```bash
# Generate PWA screenshots
python3 scripts/generate_screenshots.py
```

This generates:
- `assets/screenshot-mobile.png` (640×1136)
- `assets/screenshot-desktop.png` (1280×800)

#### Recommended Screenshot Sizes

For PWA manifest compliance:
- **Mobile**: 640×1136 (narrow form factor)
- **Desktop**: 1280×800 (wide form factor)

For technical implementation details and other automation tools (Puppeteer, Selenium), see inline comments in:
- `assets/js/app.js` - `markAppAsReady()` method
- `scripts/generate_screenshots.py` - Complete implementation

## 🤝 Contributing

We welcome contributions! Found a bug? Know a venue that should be included? Want to improve the UI?

### Guidelines

1. **KISS Principle**: Keep it simple. Avoid over-engineering.
2. **Mobile First**: Always test on mobile viewport sizes.
3. **Accessibility**: Maintain WCAG 2.1 Level AA compliance.
4. **Test Before Commit**: Run the test suite.
5. **No Frameworks**: Vanilla JavaScript only (Leaflet.js is the only external library).

### Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python3 tests/test_scraper.py --verbose`
5. Submit a pull request

Questions? Open an issue!

## 🔐 Security

- **No secrets in code**: Use environment variables or config files (gitignored)
- **Input validation**: Always sanitize user input and scraped data
- **XSS protection**: Escape HTML when displaying user-generated content
- **HTTPS**: Production uses HTTPS (GitHub Pages enforces this)

Found a security issue? Please report it privately via GitHub Security Advisories.

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

Built with love for the Hof community. Special thanks to all the local venues and organizations sharing their event information.

## 🔗 Links

- **Live App**: [krwl.in](https://krwl.in)
- **GitHub Repository**: [github.com/feileberlin/krwl-hof](https://github.com/feileberlin/krwl-hof)
- **Report Issues**: [GitHub Issues](https://github.com/feileberlin/krwl-hof/issues)
- **Bootstrap Guide**: [INITIATE.md](INITIATE.md) - Build your own from scratch

---

*Last updated: 2026-01-04 19:31:58*  
*Auto-generated by `scripts/generate_readme.py` • Documentation philosophy: Code comments + CLI help + TUI hints + README*
