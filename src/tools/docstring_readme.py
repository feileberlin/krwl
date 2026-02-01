#!/usr/bin/env python3
"""
Docstring-Based README Generator for KRWL> Events from here til sunrise

Generates README.md by extracting documentation from Python docstrings.
This ensures a single source of truth: docstrings serve as code documentation,
CLI help text, and README content.

Philosophy: All documentation should be:
- Python docstrings (single source of truth)
- CLI --help text (extracted from docstrings)
- Inline TUI hints (contextual tooltips)
- One consolidated README.md (generated from docstrings)

No complex validation. No multiple documentation files.
Keep it simple, stupid (KISS).

Usage:
    python3 scripts/docstring_readme.py [--update-github-about]
    
Options:
    --update-github-about    Also update GitHub repository About section
                             (requires GITHUB_TOKEN env var)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
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
    app_name = config.get('app', {}).get('name', 'KRWL> Events from here til sunrise')
    app_description = config.get('app', {}).get('description', 'Community events viewer')
    
    # Get CLI help from main scripts
    event_manager_help = get_cli_help('src/event_manager.py')
    
    # Build README content
    readme = f"""# {app_name}

> {app_description}

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
git clone https://github.com/feileberlin/krwl.in.git
cd krwl.in

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
    "name": "{config.get('app', {}).get('name', 'KRWL>')}",
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
python3 src/modules/feature_verifier.py --verbose

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
krwl.in/
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

## 🧪 Advanced Features

### Dynamic Event Templates with Relative Times

The app supports **dynamic event templates** with relative time specifications. This feature allows demo events to always display accurate relative times like "happening now" or "starting in 5 minutes" on every page reload, without requiring manual timestamp updates.

#### How It Works

Demo events can include a `relative_time` field that specifies how to calculate actual timestamps dynamically:

```json
{{
  "id": "demo_happening_now",
  "title": "[DEMO] Event Happening Now",
  "relative_time": {{
    "type": "offset",
    "minutes": -30,
    "duration_hours": 2
  }}
}}
```

When the app loads, the `processTemplateEvents()` method in `assets/js/app.js` detects events with `relative_time` specifications and calculates actual timestamps based on the current browser time.

#### Relative Time Specifications

**Type 1: Offset (Relative to Current Time)**

Events that occur relative to the current moment:

```json
{{
  "type": "offset",
  "hours": 1,           // Optional: hours offset from now
  "minutes": 5,         // Optional: minutes offset from now
  "duration_hours": 2,  // Event duration in hours
  "timezone_offset": 0  // Optional: timezone offset for testing
}}
```

Examples:
- `{{"type": "offset", "minutes": -30, "duration_hours": 2}}` - Started 30 minutes ago
- `{{"type": "offset", "minutes": 5, "duration_hours": 2}}` - Starts in 5 minutes
- `{{"type": "offset", "hours": 1, "duration_hours": 3}}` - Starts in 1 hour, lasts 3 hours

**Type 2: Sunrise Relative (Relative to Next Sunrise)**

Events that occur relative to the next sunrise (simplified as 6:00 AM):

```json
{{
  "type": "sunrise_relative",
  "start_offset_hours": -2,    // Optional: hours offset for start time
  "start_offset_minutes": 0,   // Optional: minutes offset for start time
  "end_offset_hours": 0,       // Optional: hours offset for end time
  "end_offset_minutes": -5     // Optional: minutes offset for end time
}}
```

Examples:
- `{{"type": "sunrise_relative", "end_offset_minutes": -5, "start_offset_hours": -2}}` - Ends 5 minutes before sunrise
- `{{"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}}` - Starts 2 hours before sunrise, ends 1 hour after

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
    page.set_viewport_size({{"width": 1280, "height": 800}})
    
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
- **GitHub Repository**: [github.com/feileberlin/krwl.in](https://github.com/feileberlin/krwl.in)
- **Report Issues**: [GitHub Issues](https://github.com/feileberlin/krwl.in/issues)

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Auto-generated by `scripts/generate_readme.py` • Documentation philosophy: Code comments + CLI help + TUI hints + README*
"""

    return readme


def update_github_about(config):
    """Update GitHub repository About section using GitHub API.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("\n⚠️  GITHUB_TOKEN not set. Skipping GitHub About update.")
        print("   To update GitHub About section, set GITHUB_TOKEN and run again.")
        print("   Get token at: https://github.com/settings/tokens")
        return False
    
    owner = 'feileberlin'
    repo = 'krwl.in'
    
    # Prepare description
    description = f"{config.get('app', {}).get('description', 'Community events viewer')}. Mobile-first PWA for discovering local events in Hof, Bavaria. Live at krwl.in"
    homepage = "https://krwl.in"
    
    topics = [
        "pwa", "progressive-web-app", "events", "community",
        "geolocation", "leaflet", "python", "javascript",
        "mobile-first", "accessibility", "i18n"
    ]
    
    print(f"\n🔧 Updating GitHub About section for {owner}/{repo}...")
    
    # Update repository details
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = {
            'description': description,
            'homepage': homepage
        }
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                print("✅ Repository description and homepage updated")
            else:
                print(f"⚠️  Failed to update repository: HTTP {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"⚠️  HTTP Error: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"⚠️  Error updating repository: {e}")
        return False
    
    # Update topics
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/topics"
        data = {'names': topics}
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.mercy-preview+json',
            'Content-Type': 'application/json',
        }
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='PUT'
        )
        
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                print("✅ Repository topics updated")
                print(f"   Topics: {', '.join(topics)}")
            else:
                print(f"⚠️  Failed to update topics: HTTP {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"⚠️  HTTP Error: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"⚠️  Error updating topics: {e}")
        return False
    
    print(f"🎉 GitHub About section updated successfully!")
    print(f"🌐 View at: https://github.com/{owner}/{repo}")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate README.md and optionally update GitHub About section'
    )
    parser.add_argument(
        '--update-github-about',
        action='store_true',
        help='Update GitHub repository About section (requires GITHUB_TOKEN)'
    )
    
    args = parser.parse_args()
    
    print("📝 Generating README.md...")
    
    try:
        config = load_config()
        readme_content = generate_readme()
        
        # Write README
        readme_path = Path('README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ README.md generated successfully ({len(readme_content)} bytes)")
        print(f"📍 Location: {readme_path.absolute()}")
        
        # Optionally update GitHub About section
        if args.update_github_about:
            update_github_about(config)
        
    except Exception as e:
        print(f"❌ Error generating README: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
