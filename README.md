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

# Install Python dependencies
pip install -r requirements.txt

# Download frontend libraries (Leaflet.js)
python3 src/event_manager.py dependencies fetch

# Run locally
cd static
python3 -m http.server 8000
```

Open http://localhost:8000 in your browser

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
    
    generate                  Generate static site (runtime-configurable)
    update                    Update events data in existing site (fast)
    dependencies fetch        Fetch third-party dependencies
    dependencies check        Check if dependencies are present
    
    archive                   Archive past events (automatic on generate)
    load-examples             Load example data for development
    clear-data                Clear all event data
    
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
    
    # List all published events
    python3 event_manager.py list
    
    # Publish a single event
    python3 event_manager.py publish pending_1
    
    # Bulk publish using wildcards
    python3 event_manager.py bulk-publish "pending_*"
    
    # Load example data for testing
    python3 event_manager.py load-examples
    
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

# Filter tests
python3 tests/test_filters.py --verbose

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
├── event-data/                # Event and translation data
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

Approved events move to `data/events.json` and appear on the map.

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

The app supports English and German:

- `data/content.json` - English translations
- `static/content.de.json` - German translations

Add translations using the key path format:
```json
{
  "section": {
    "key": "Translation text"
  }
}
```

In code: `i18n.t('section.key')`

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

---

*Last updated: 2026-01-02 17:46:12*  
*Auto-generated by `scripts/generate_readme.py` • Documentation philosophy: Code comments + CLI help + TUI hints + README*
