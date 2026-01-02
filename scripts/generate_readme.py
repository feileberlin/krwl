#!/usr/bin/env python3
"""
Simplified README Generator for KRWL HOF Community Events

Philosophy: All documentation should be:
- Code comments (in the source files)
- CLI --help text (from argparse)
- Inline TUI hints (contextual tooltips)
- One consolidated README.md (this generates it)

No complex validation. No multiple documentation files.
Keep it simple, stupid (KISS).

Usage:
    python3 scripts/generate_readme.py
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_cli_help(script_path):
    """Extract CLI help from a Python script"""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"⚠️  Warning: Could not extract help from {script_path}: {e}")
        return None


def load_config():
    """Load configuration from config.json in root"""
    config_path = Path('config.json')
    if not config_path.exists():
        print("❌ Error: config.json not found")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_readme():
    """Generate comprehensive README.md from code and config"""
    
    config = load_config()
    
    # Extract app info from config
    app_name = config.get('app', {}).get('name', 'KRWL HOF Community Events')
    app_description = config.get('app', {}).get('description', 'Community events viewer')
    
    # Get CLI help from main scripts
    event_manager_help = get_cli_help('src/event_manager.py')
    
    # Build README content
    readme = f"""# {app_name}

> {app_description}

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web_apps/)
[![Accessibility](https://img.shields.io/badge/A11y-Compliant-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 🎯 What is This?

A **grassroots, mobile-first** Progressive Web App (PWA) for discovering local community events in Hof and surrounding region (Bavaria, Germany). Built by and for the local community - from punk concerts to farmers markets, from Off-Theater to VHS courses.

### ✨ Features

- 📱 **PWA**: Installable as native app on mobile and desktop
- 🗺️ **Interactive Map**: Leaflet.js with event markers and clustering
- 📍 **Geolocation Filtering**: Shows events within {config.get('filtering', {}).get('max_distance_km', 5.0)}km radius
- 🌅 **Time-based Filtering**: Shows events until {config.get('filtering', {}).get('show_until', 'next sunrise')}
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

"""

    # Add CLI help if available
    if event_manager_help:
        readme += f"""#### Full CLI Help

```
{event_manager_help}
```

"""

    # Add configuration section
    readme += f"""## ⚙️ Configuration

All configuration lives in `config.json`:

```json
{{
  "app": {{
    "name": "{config.get('app', {}).get('name', 'KRWL HOF')}",
    "description": "{config.get('app', {}).get('description', 'Community events')}"
  }},
  "map": {{
    "default_center": {json.dumps(config.get('map', {}).get('default_center', {}))},
    "default_zoom": {config.get('map', {}).get('default_zoom', 13)}
  }},
  "filtering": {{
    "max_distance_km": {config.get('filtering', {}).get('max_distance_km', 5.0)},
    "show_until": "{config.get('filtering', {}).get('show_until', 'next_sunrise')}"
  }},
  "scraping": {{
    "schedule": {json.dumps(config.get('scraping', {}).get('schedule', {}))},
    "sources": [...{len(config.get('scraping', {}).get('sources', []))} configured sources]
  }}
}}
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
├── config.json          # Central configuration file
├── config.dev.json      # Development environment config
├── config.prod.json     # Production environment config
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
│   └── backups/         # Individual event backups
│       └── events/      # Timestamped event backup files
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
{{
  "scraping": {{
    "sources": [
      {{
        "name": "Your Event Source",
        "url": "https://example.com/events",
        "type": "rss",  // or "html", "api"
        "enabled": true,
        "notes": "Description of the source"
      }}
    ]
  }}
}}
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
{{
  "section": {{
    "key": "Translation text"
  }}
}}
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

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Auto-generated by `scripts/generate_readme.py` • Documentation philosophy: Code comments + CLI help + TUI hints + README*
"""

    return readme


def main():
    """Main entry point"""
    print("📝 Generating README.md...")
    
    try:
        readme_content = generate_readme()
        
        # Write README
        readme_path = Path('README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ README.md generated successfully ({len(readme_content)} bytes)")
        print(f"📍 Location: {readme_path.absolute()}")
        
    except Exception as e:
        print(f"❌ Error generating README: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
