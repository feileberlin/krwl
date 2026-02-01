# KRWL HOF Community Events

> Community events scraper and viewer with geolocation filtering

**🌐 Live Site: [https://krwl.in](https://krwl.in)**

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web_apps/)
[![Accessibility](https://img.shields.io/badge/A11y-Compliant-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 🎯 What is This?

A **grassroots, mobile-first** Progressive Web App (PWA) for discovering community events around. Built by and for the local community - from punk concerts to farmers markets, from Off-Theater to VHS courses.

**Visit the live app at [krwl.in](https://krwl.in)** to see events on an interactive map!

### ✨ Features

- 📱 **PWA**: Installable as native app on mobile and desktop
- 🗺️ **Interactive Map**: Leaflet.js with event markers and clustering
- 🏙️ **Multi-Region Support**: View events from different Franconian cities (Hof, Nürnberg, Bayreuth, Selb, Rehau)
- 📍 **Geolocation Filtering**: Shows events within 5.0km radius
- 🌅 **Time-based Filtering**: Shows events until next_sunrise
- 📡 **RSS Feeds**: Per-region "Until Sunrise" RSS feeds for stay updated
- 🤖 **Telegram Bot**: Community event submissions via Telegram messenger
- 🌐 **Bilingual**: English and German (i18n support)
- ♿ **Accessible**: WCAG 2.1 Level AA compliant
- 📱 **Responsive**: Mobile-first design, works on all screen sizes
- 🔄 **Auto-scraping**: Configurable event sources with automatic updates

### 🔍 Functionality Overview

Here's how the main features work from a user's perspective:

#### 🗺️ Interactive Map with Speech Bubbles

When you open the app, you'll see an interactive map displaying local events as markers. Each event appears with a **comic book-style speech bubble** showing the event name, time, and location. The bubbles are designed with:
- **Collision-aware positioning**: Bubbles automatically spread out to avoid overlapping
- **Draggable bubbles**: You can drag bubbles to reposition them if needed
- **Connector lines**: Visual lines connect each bubble to its marker on the map
- **Smooth animations**: Bubbles follow their markers when you pan or zoom the map

Click on any bubble to see full event details including description, category, and a link to the original source.

#### 🔖 Bookmark Events

Found an interesting event? Save it for later with the **bookmark feature**:
- **One-tap bookmarking**: Click the bookmark icon on any event to save it
- **Highlighted bubbles**: Bookmarked events appear with a distinct pink background color
- **Persistent storage**: Your bookmarks are saved locally and persist across sessions
- **Maximum 15 bookmarks**: When you add a 16th bookmark, the oldest one is automatically removed (FIFO)

This works entirely offline using your browser's localStorage - no account needed!

#### 📍 Smart Filtering

The filter bar at the top lets you customize which events appear:

| Filter | What It Does |
|--------|-------------|
| **Distance** | Slider to show events within 1-10km of your location |
| **Time** | Show events happening "until sunrise" (perfect for evening outings), "next 24 hours", or "all upcoming" |
| **Category** | Filter by event type (music, sports, arts, food, etc.) |
| **Location** | Use GPS location, pick a saved location, or set a custom point on the map |

Filters are combined intelligently - for example, you can see all music events within 3km happening before sunrise.

#### 📱 Progressive Web App (PWA)

The app works like a native mobile app:
- **Install to home screen**: On mobile, you can add the app to your home screen for quick access
- **Works offline**: Core functionality works without internet (using cached data)
- **Fast loading**: Optimized for mobile networks
- **Responsive design**: Works on phones, tablets, and desktops

#### 📡 RSS Feeds - "Until Sunrise"

Stay updated with per-region RSS feeds showing upcoming events until next sunrise:
- **Per-Region Feeds**: Each region (Hof, Nürnberg, Bayreuth, Selb, Rehau) has its own RSS feed
- **Sunrise Filtering**: Feeds show only events happening between now and next sunrise - perfect for evening planning
- **RSS 2.0 Standard**: Compatible with all RSS readers (Feedly, NewsBlur, etc.)
- **Auto-Discovery**: Browsers and RSS readers automatically detect feeds via `<link>` tags

**Feed URLs:**
- Hof: `https://krwl.in/assets/feeds/hof-til-sunrise.xml`
- Nürnberg: `https://krwl.in/assets/feeds/nbg-til-sunrise.xml`
- Bayreuth: `https://krwl.in/assets/feeds/bth-til-sunrise.xml`
- Selb: `https://krwl.in/assets/feeds/selb-til-sunrise.xml`
- Rehau: `https://krwl.in/assets/feeds/rehau-til-sunrise.xml`

**How to Subscribe:**
1. Copy your region's feed URL
2. Open your RSS reader (e.g., Feedly, NewsBlur, NetNewsWire)
3. Add the feed URL
4. Get notified when new events are added!

**For Developers:**
- Feeds regenerate automatically during site builds (`python3 src/event_manager.py generate`)
- Generate feeds manually: `python3 src/event_manager.py generate-feeds`
- Sunrise calculation adapts to each region's coordinates

#### 🌐 Language Support (i18n)

Switch between English and German with a single click:
- **Dynamic translation**: All UI text updates instantly when you change language
- **Localized dates/times**: Times display in local format (e.g., "Heute 20:00" vs "Today 8:00 PM")
- **Event content**: Event descriptions remain in their original language

### 🏙️ Multi-Region Support

KRWL HOF now supports viewing events from different Franconian cities! **URL path segment reads config variables (map center, zoom) to position the map** - all regions share the same event data.

**Supported Regions:**
- 🏛️ **Hof (Saale)** - Default region (50.3167°N, 11.9167°E)
- 🏰 **Nürnberg** - Franconia's metropolis (49.4521°N, 11.0767°E)  
- 🎭 **Bayreuth** - Festival city (49.9481°N, 11.5783°E)
- 🏺 **Selb** - Porcelain city (50.1705°N, 12.1328°E)
- 🏔️ **Rehau** - Mountain town (50.2489°N, 12.0364°E)

**What this provides:**
- ✅ Configuration structure for multiple cities
- ✅ URL path determines map center and zoom
- ✅ Utility functions for region config access
- ❌ **NO filter bar changes** - existing UI unchanged
- ❌ **NO data splitting** - single shared events.json

**For Developers:**
- See [`docs/MULTI_REGION_QUICK_START.md`](docs/MULTI_REGION_QUICK_START.md) for usage guide
- See [`docs/MULTI_REGION_INFRASTRUCTURE.md`](docs/MULTI_REGION_INFRASTRUCTURE.md) for full documentation
- Use `src/modules/region_utils.py` for programmatic access

```python
from src.modules.region_utils import get_region_config, haversine_distance

# Get Nürnberg's configuration
nbg_config = get_region_config('nbg', base_path)
print(nbg_config['displayName'])  # "Nürnberg"

# Calculate distance between cities
distance = haversine_distance(11.9167, 50.3167, 11.0767, 49.4521)
print(f"{distance:.1f} km")  # 113.4 km (Hof to Nürnberg)
```

### 🌍 Single-Page App with Three Content Types

KRWL is a **Single-Page Application (SPA)** that serves three content types from one HTML page using URL-based routing:

#### 1. 🐧 **Showcase** - Antarctica (`/` or `/antarctica`)
**Purpose:** Project information and setup guide  
**Location:** South Pole (90°S)  
**Events:** Showcase events explaining how to fork and set up your own region

When you visit the root URL (`/`), you'll see Antarctica - our project showcase page featuring fun demo events that explain:
- How to fork the repository for your own community
- How to configure your first region
- Example events with various features (sunrise filtering, distance filtering, bookmarks, etc.)

Perfect for developers exploring the project or wanting to set up KRWL for their own community!

#### 2. 🌊 **Error-handling** - Atlantis (`/atlantis` or any unknown region)
**Purpose:** Humorous 404 handler  
**Location:** Mid-Atlantic Ridge (31°N 24°W)  
**Events:** Playful sunken city-themed events with hints to visit `/` or fork the repo

Try visiting an unconfigured region like `/berlin` or `/tokyo` - you'll be taken to Atlantis! This humorous 404 page features:
- 🌊 Events about Poseidon's Palace tours and underwater archaeology
- 🐠 Clever hints about visiting Antarctica (/) or forking the repo
- 🏛️ A lighthearted way to explain the app structure to curious visitors

#### 3. 🗺️ **Production** - Multiple Regional Entry Points
**Purpose:** Live event calendars for actual communities  
**Entry Points:** Each region has its own URL path  
**Events:** Real scraped events from configured sources

The SPA serves **multiple independent production regions**, each accessible via its own URL:
- `/hof` - Hof (Saale) events
- `/bth` - Bayreuth events  
- `/nbg` - Nürnberg events
- `/selb` - Selb events
- `/rawetz` - Rehau/Schwarzenbach/Wunsiedel events

Each production region:
- Has its own geographic center and zoom level
- Shows only real scraped events (excludes Antarctica/Atlantis)
- Uses the same SPA with different URL routing
- Can be added by configuring new regions in `config.json`

**How It Works (Single-Page App Architecture):**

One HTML page (`public/index.html`) serves all content, with client-side routing filtering events:

1. **Backend** (`src/modules/site_generator.py`):
   - Generates ONE static HTML file (570 KB)
   - Embeds ALL 167 events from three sources: `events.json`, `events.antarctica.json`, `events.atlantis.json`

2. **Frontend** (`assets/js/app.js`):
   - Detects URL path without page reload (e.g., `/hof`, `/bth`, `/nbg`, `/`, `/unknown-region`)
   - Filters events by `source` field client-side:
     - **Showcase** (`/` or `/antarctica`): Shows `source: "antarctica"` or `source: "demo"`
     - **Error-handling** (unknown regions): Shows `source: "atlantis"`
     - **Production** (`/hof`, `/bth`, `/nbg`, `/selb`, `/rawetz`): Shows all events EXCEPT antarctica/atlantis

3. **Multiple entry points** - Each production region (`/hof`, `/bth`, etc.) is a separate entry point to the same SPA

**Adding Your Own Region:**

1. Fork the repository: `https://github.com/feileberlin/krwl-hof`
2. Add your region to `config.json`:
   ```json
   "regions": {
     "your-city": {
       "name": "Your City",
       "displayName": "Your City Name",
       "center": {"lat": 48.1351, "lng": 11.5820},
       "zoom": 13
     }
   }
   ```
3. Configure scrapers for your region's event sources
4. Deploy and share with your community!

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

## 🔍 PR Preview (KISS Approach)

Want to test changes before merging? We use a **simple artifact-based preview** system!

When you open a PR, GitHub Actions automatically:
1. **Builds** the site in development mode
2. **Uploads** as downloadable artifact (90-day retention)
3. **Comments** on PR with download link

**How to test:**
```bash
# Download artifact from PR comment link
# Extract ZIP and either:
cd public && python3 -m http.server 8000  # Local server
# OR just open public/index.html in browser
```

**Why artifacts, not live URLs?**
- ✅ KISS: No external services (Netlify, Vercel)
- ✅ Simple: Just download and test
- ✅ Private: Test locally, no external deployments
- ✅ Free: Pure GitHub, no extra accounts

👉 [Full PR Preview Documentation](docs/PR_PREVIEW.md)

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
    telegram-bot              Start Telegram bot for event submissions and contact form
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
python3 src/modules/kiss_checker.py --verbose
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

## 🤖 Telegram Bot Integration

The project includes a **Telegram bot** that allows community members to submit events directly via Telegram messenger. This provides an easy, accessible way for people without GitHub accounts to contribute events.

### Features

- **📝 Manual Event Submission**: Users can submit events by answering a few questions in a conversation
- **📸 Flyer Upload with OCR**: Upload event flyer images and automatically extract event details using OCR
- **💬 Contact Form**: Send messages directly to the event maintainers
- **🔒 Admin Notifications**: All submissions notify admins in their Telegram chat
- **✅ Editorial Review**: Submissions go to `pending_events.json` for approval before publishing

### Phase 1: Local Bot (Manual Operation)

Run the bot locally on your development machine:

```bash
# 1. Get a bot token from @BotFather on Telegram
# 2. Enable the bot in config.json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "_comment_bot_token": "Or use TELEGRAM_BOT_TOKEN env var",
    "admin_chat_ids": [123456789],
    "_comment_admin_chat_ids": "Your Telegram user ID",
    "features": {
      "event_submission": true,
      "flyer_upload": true,
      "contact_form": true
    }
  }
}

# 3. Start the bot
python3 src/event_manager.py telegram-bot

# 4. Open Telegram and send /start to your bot
```

**Bot Commands:**
- `/start` - Get welcome message with your Telegram ID
- `/submit` - Submit a new event (guided conversation)
- `/upload` - Upload event flyer image for OCR processing
- `/contact` - Send a message to maintainers
- `/status` - Check bot status and pending events count
- `/help` - Show available commands
- `/cancel` - Cancel current operation

### Phase 2: GitHub Actions Integration (Automated Operation)

For production deployments, the bot runs automatically in **GitHub Actions** as a scheduled workflow:

#### Setup

1. **Add Bot Token to GitHub Secrets:**
   - Go to: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from @BotFather
   - Click "Add secret"

2. **Configure Admin Chat IDs** in `config.json`:
   ```json
   {
     "telegram": {
       "enabled": true,
       "admin_chat_ids": [123456789, 987654321],
       "_comment_admin_chat_ids": "Your Telegram user IDs"
     }
   }
   ```

3. **Enable the Workflow:**
   - The workflow is located at `.github/workflows/telegram-bot.yml`
   - It runs automatically every 15 minutes during active hours (6 AM - 10 PM CET)
   - You can also trigger it manually

#### How It Works

1. **Scheduled Execution**: GitHub Actions runs the bot every 15 minutes
2. **Polling Mode**: Bot checks for new messages from users
3. **Save Submissions**: New events are added to `assets/json/pending_events.json`
4. **Auto-Commit**: Changes are automatically committed back to the repository
5. **Admin Notifications**: Admins receive Telegram notifications for new submissions

#### Manual Workflow Trigger

Go to: **Actions** → **Telegram Bot** → **Run workflow**

**Options:**
- **Duration**: How long to run the bot (1-60 minutes, default: 10 min)
- **Mode**: 
  - `polling` - Run bot with long polling (default)
  - `webhook` - Set up webhook (future implementation)
  - `stop` - Stop bot gracefully

#### Monitoring

Check workflow status:
```bash
# View workflow logs in GitHub Actions UI
# Or check the workflow file:
cat .github/workflows/telegram-bot.yml
```

The workflow reports:
- ✅ Bot run status
- 📊 Number of pending events
- 📝 New submissions detected
- 💾 Commit information

#### Security & Rate Limiting

- **Token Security**: Bot token is stored in GitHub Secrets (never in code)
- **Rate Limiting**: Max 10 submissions per user per hour (configurable in `config.json`)
- **File Size Limits**: Max 10 MB per flyer upload (configurable)
- **Description Length**: Max 1000 characters (configurable)

### Getting Your Telegram User ID

To receive admin notifications, you need your Telegram user ID:

1. Start your bot: `/start`
2. The bot will reply with: "Your Telegram ID: `123456789`"
3. Add this ID to `config.json` → `telegram.admin_chat_ids`

### Testing the Integration

```bash
# 1. Test bot locally
python3 tests/test_telegram_bot.py --verbose

# 2. Test bot instantiation (requires python-telegram-bot library)
pip install python-telegram-bot>=20.0
python3 -c "from src.modules.telegram_bot import TelegramBot, TELEGRAM_AVAILABLE; print(f'Available: {TELEGRAM_AVAILABLE}')"

# 3. Test feature verification
python3 src/modules/feature_verifier.py --verbose | grep telegram
```

### Configuration Reference

Full configuration options in `config.json`:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "",
    "_comment_bot_token": "Token from @BotFather (or use env var)",
    "admin_chat_ids": [],
    "_comment_admin_chat_ids": "List of admin Telegram user IDs",
    "features": {
      "event_submission": true,
      "_comment_event_submission": "Allow manual event submission",
      "flyer_upload": true,
      "_comment_flyer_upload": "Allow flyer image uploads",
      "contact_form": true,
      "_comment_contact_form": "Allow contact messages"
    },
    "limits": {
      "max_flyer_size_mb": 10,
      "_comment_max_flyer_size_mb": "Max flyer file size",
      "max_description_length": 1000,
      "_comment_max_description_length": "Max event description length",
      "rate_limit_per_user": 10,
      "_comment_rate_limit_per_user": "Max submissions per user per hour"
    },
    "messages": {
      "welcome": "🎉 Welcome to KRWL HOF Events Bot!...",
      "help": "📋 Available Commands:\n\n/submit - ..."
    }
  }
}
```

### Troubleshooting

**Bot not responding:**
- Check that `telegram.enabled: true` in config.json
- Verify TELEGRAM_BOT_TOKEN is set (env var or config)
- Check bot token is valid (test with @BotFather)

**No admin notifications:**
- Verify your Telegram user ID is in `telegram.admin_chat_ids`
- Start the bot with `/start` to get your user ID
- Check admin IDs are integers, not strings

**GitHub Actions workflow not running:**
- Verify TELEGRAM_BOT_TOKEN is added to GitHub Secrets
- Check workflow file syntax: `.github/workflows/telegram-bot.yml`
- Review Actions logs for error messages

**OCR not working:**
- OCR requires system package: `tesseract-ocr`
- Install: `sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu`
- Verify: `python3 -c "from src.modules.smart_scraper.image_analyzer.ocr import is_ocr_available; print(is_ocr_available())"`

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

---

*Last updated: 2026-01-04 19:31:58*  
*Auto-generated by `scripts/generate_readme.py` • Documentation philosophy: Code comments + CLI help + TUI hints + README*
