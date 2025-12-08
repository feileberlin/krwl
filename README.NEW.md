# KRWL HOF Community Events

A modular Python application for managing and displaying community events with geolocation filtering, automated quality assurance, and KISS compliance monitoring.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Running the TUI](#running-the-tui)
  - [Using CLI Commands](#using-cli-commands)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
  - [Event Scraping](#event-scraping)
  - [Editor Workflow](#editor-workflow)
  - [Interactive Map UI](#interactive-map-ui)
  - [Filter System](#filter-system)
  - [Static Site Generation](#static-site-generation)
- [Quality Assurance System](#quality-assurance-system)
  - [Feature Registry](#feature-registry)
  - [KISS Compliance Monitoring](#kiss-compliance-monitoring)
  - [Automated Linting](#automated-linting)
  - [Testing](#testing)
- [Development](#development)
  - [Configuration](#configuration)
  - [Adding New Features](#adding-new-features)
  - [Running Tests](#running-tests)
  - [Code Style](#code-style)
- [Deployment](#deployment)
  - [Preview Deployment](#preview-deployment)
  - [Production Deployment](#production-deployment)
  - [Custom Domains](#custom-domains)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

KRWL HOF is a community events management system that scrapes events from various sources, allows editorial review, and displays them on an interactive map. The system includes comprehensive quality assurance tools to maintain code quality and prevent feature loss during development.

**Key Characteristics:**
- 🐍 **Python-based**: Modular Python architecture with TUI and CLI interfaces
- 🗺️ **Interactive UI**: Inline filter controls with real-time updates
- 📍 **Smart Filtering**: Geolocation, time, distance, and event type filters
- 🌅 **Time-aware**: Filter by sunrise, sunset, full moon, or custom time ranges
- ✅ **Quality Assured**: Automated feature verification and KISS compliance
- 🚀 **Static Output**: Generates deployable static site files
- 📦 **KISS Principle**: Keep It Simple, Stupid - clean, maintainable code

---

## Features

### Core Features (27 Total)

#### Event Management
- 🔍 **Event Scraping**: RSS feeds, APIs, and HTML page scraping
- ✅ **Editor Workflow**: Review, edit, approve, or reject events
- 📝 **JSON Storage**: Plain JSON for configuration and data
- 💾 **Backup System**: Automatic backups before destructive operations
- 🗄️ **Archiving**: Archive old events automatically

#### User Interface
- 🗺️ **Interactive Map**: Fullscreen Leaflet.js map with inline filters
- 🎯 **Inline Filters**: Single-line interactive filter sentence on map overlay
  - Format: `[COUNT TYPE] [TIME] [DISTANCE] [LOCATION]`
  - Example: "21 on stage events till sunrise within 15 min by foot from your location"
- 🐍 **Python TUI**: Text User Interface for command-line management
- ⌨️ **CLI Commands**: Scriptable command-line interface
- 📱 **Responsive**: Mobile-friendly design

#### Filtering System
- 📍 **Geolocation**: GPS-based location with fallback to predefined locations
- 🌅 **Time Filtering**:
  - Till sunrise (default)
  - Till sunday night
  - Till next full moon (real API data)
  - Custom hours (6h, 12h, 24h, 48h)
  - All upcoming events
- 🚶 **Distance Filtering**:
  - 15 minutes by foot (1.25 km, default)
  - 10 minutes by bike (3.33 km)
  - 1 hour by public transport (15 km)
- 🎭 **Event Type Filtering**:
  - All events (default)
  - On stage (concerts, performances)
  - Pub games
  - Festivals

#### Deployment
- 🌐 **Static Site Generation**: GitHub Pages compatible
- 🚀 **Automated Deployment**: CI/CD workflows for preview and production
- 🔗 **Custom Domain Support**: Auto-detects CNAME configuration
- 🐛 **Debug Mode**: Development config with detailed logging
- ⚡ **Production Mode**: Optimized for performance

### Quality Assurance Features

#### Feature Registry & Verification
- 📋 **Feature Registry**: `features.json` documents all 27 features
- ✅ **Automated Testing**: Verifies features on every commit
- 🔍 **Pattern Matching**: Checks code patterns, files, and config keys
- 📊 **Detailed Reports**: Clear failure messages with fix suggestions

#### KISS Compliance Monitoring
- 📏 **Complexity Analysis**: Monitors file size, function length, nesting depth
- 🎯 **Thresholds**: Configurable limits for maintainability
  - Max file size: 500 lines
  - Max function length: 50 lines
  - Max nesting depth: 4 levels
  - Max imports: 15 per file
- 📝 **Tracking Issues**: Automatically creates GitHub issues for violations
- 💡 **Fix Suggestions**: Specific refactoring guidance per violation type

#### Automated Linting
- 🐍 **Python**: flake8 with configurable rules
- 📜 **JavaScript**: jshint for frontend code
- 📄 **JSON**: jsonlint for configuration files
- ⚙️ **Configurable**: Separate critical errors from style warnings
- 🚫 **Smart Blocking**: Only blocks on critical errors (syntax, undefined vars)

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/feileberlin/krwl-hof.git
cd krwl-hof

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# No external dependencies required - uses Python stdlib only!
```

### Running the TUI

```bash
# Start the Text User Interface
python3 src/main.py
```

**TUI Menu Options:**
1. **Scrape New Events** - Fetch events from configured sources
2. **Review Pending Events** - Approve/reject/edit scraped events
3. **View Published Events** - See all approved events
4. **Generate Static Site** - Create deployment files
5. **Settings** - View and manage configuration
6. **View Documentation** - Built-in help system
7. **Exit** - Close application

### Using CLI Commands

```bash
# Feature verification
python3 verify_features.py --verbose

# KISS compliance check
python3 check_kiss.py --json

# Filter logic testing
python3 test_filters.py

# Generate demo events
python3 generate_demo_events.py

# All tools also available as subcommands (future)
python3 src/main.py verify-features --verbose
python3 src/main.py check-kiss --json
```

---

## Project Structure

```
krwl-hof/
├── .github/
│   ├── workflows/
│   │   ├── deploy-preview.yml        # Preview deployment workflow
│   │   ├── deploy-production.yml     # Production deployment
│   │   ├── verify-features.yml       # Feature verification
│   │   ├── kiss-compliance.yml       # KISS monitoring
│   │   └── lint.yml                  # Code linting
│   ├── FEATURE_REGISTRY.md           # Feature documentation
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── PROMOTE_WORKFLOW.md           # Promotion workflow
│
├── src/
│   ├── main.py                       # Main TUI application (792 lines)
│   └── modules/
│       ├── __init__.py               # Module initialization
│       ├── scraper.py                # Event scraping (108 lines)
│       ├── editor.py                 # Event editing (150 lines)
│       ├── generator.py              # Static site generator (1165 lines)
│       ├── utils.py                  # Utility functions (190 lines)
│       ├── feature_verifier.py       # Feature verification (306 lines)
│       ├── filter_tester.py          # Filter testing (349 lines)
│       └── kiss_checker.py           # KISS compliance (455 lines)
│
├── static/                           # Generated static site
│   ├── index.html                    # Main HTML file
│   ├── events.json                   # Published events data
│   ├── css/
│   │   └── style.css                 # Styles
│   └── js/
│       └── app.js                    # Frontend application (661 lines)
│
├── data/
│   ├── events.json                   # Published events (backend)
│   ├── pending_events.json           # Events awaiting review
│   ├── events_example.json           # Example data
│   └── pending_events_example.json   # Example pending data
│
├── config.dev.json                   # Development configuration
├── config.prod.json                  # Production configuration
├── features.json                     # Feature registry
│
├── verify_features.py                # Feature verifier wrapper (19 lines)
├── check_kiss.py                     # KISS checker wrapper (19 lines)
├── test_filters.py                   # Filter tester wrapper (19 lines)
├── generate_demo_events.py           # Demo event generator (366 lines)
│
└── README.md                         # This file
```

**Total Python LOC:** ~4,400 lines
**Total JavaScript LOC:** ~660 lines

---

## Core Features

### Event Scraping

The event scraping system supports multiple source types:

**Supported Sources:**
- RSS Feeds (XML parsing)
- REST APIs (JSON)
- HTML Pages (web scraping)

**Configuration:**
```json
{
  "scraping": {
    "sources": [
      {
        "name": "Example RSS Feed",
        "type": "rss",
        "url": "https://example.com/events.rss",
        "enabled": true
      },
      {
        "name": "Example API",
        "type": "api",
        "url": "https://api.example.com/events",
        "enabled": true
      }
    ],
    "interval_minutes": 60
  }
}
```

**Usage:**
```bash
# Via TUI
python3 src/main.py
# Select option 1: Scrape New Events

# Via Python API
from modules.scraper import EventScraper
scraper = EventScraper(config, base_path)
events = scraper.scrape_all_sources()
```

### Editor Workflow

Editorial review process with approval workflow:

**Features:**
- Review scraped events before publishing
- Edit event details (title, description, location, time)
- Approve events for publication
- Reject events permanently
- Bulk operations support

**Workflow:**
1. Events scraped → `pending_events.json`
2. Editor reviews → Approve/Edit/Reject
3. Approved events → `events.json`
4. Static site generation → `static/events.json`

### Interactive Map UI

Modern, KISS-compliant map interface with inline filters:

**Map Overlay - Interactive Filter Sentence:**
```
[21 on stage events] [till sunrise] [within 15 min by foot] [from your current location]
     ↓ dropdown         ↓ dropdown       ↓ dropdown              ↓ dropdown
```

Each component is clickable and updates the map in real-time.

**Features:**
- Click any underlined text to change filter
- Real-time event count updates
- Dynamic filter descriptions
- No separate filter panel needed
- Maximum KISS compliance

**Example Sentences:**
- "21 events till sunrise within 15 min by foot from your current location"
- "5 on stage events till sunday night within 10 min by bike from Main Station"
- "3 festivals till next full moon within 1 hr public transport from Mayor's Office"

### Filter System

Comprehensive filtering with human-readable options:

**Time Filters:**
- `till sunrise` - Events until next sunrise (default)
- `till sunday night` - Events until end of week
- `till next full moon` - Uses real moon phase API
- `6h`, `12h`, `24h`, `48h` - Hour-based filters
- `all` - No time limit

**Distance Filters:**
- `within 15 min by foot` - 1.25 km radius (5 km/h walking, default)
- `within 10 min by bike` - 3.33 km radius (20 km/h cycling)
- `within 1 hr public transport` - 15 km radius (15 km/h transit)

**Event Type Filters:**
- `events` - All event types (default)
- `on stage` - Concerts, performances, theater
- `pub games` - Pub quizzes, board game nights
- `festivals` - Multi-day festivals and celebrations

**Location Filters:**
- `from your current location` - GPS geolocation (default)
- `from Main Station` - Predefined location 1
- `from Mayor's Office` - Predefined location 2
- `from City Center` - Predefined location 3
- (Configurable in `config.dev.json` / `config.prod.json`)

**Full Moon Integration:**
- Fetches real moon phase data from wttr.in API
- Based on map center coordinates
- Accurate lunar calculations
- Fallback to approximation if API unavailable
- No API key required (free service)

**Testing:**
```bash
# Run comprehensive filter tests
python3 test_filters.py --verbose

# Test suite includes:
# - Distance calculation (Haversine formula)
# - Filter thresholds validation
# - Event type filtering
# - Time filtering logic
# - Combined filter scenarios
# - Predefined location handling
```

### Static Site Generation

Generates deployable static files:

**Generated Files:**
- `static/index.html` - Main HTML
- `static/events.json` - Event data
- `static/config.json` - Configuration
- `static/css/style.css` - Styles
- `static/js/app.js` - Application logic
- `static/.nojekyll` - GitHub Pages config

**Features:**
- No build process required
- Direct GitHub Pages deployment
- CDN-friendly static files
- Optimized for performance

---

## Quality Assurance System

### Feature Registry

The feature registry prevents accidental feature loss during refactoring.

**File:** `features.json`

**Structure:**
```json
{
  "features": [
    {
      "id": "event-scraping",
      "name": "Event Scraping",
      "description": "Scrape events from RSS, APIs, and HTML",
      "category": "backend",
      "implemented": true,
      "files": ["src/modules/scraper.py"],
      "code_patterns": [
        {
          "file": "src/modules/scraper.py",
          "pattern": "class EventScraper",
          "description": "EventScraper class exists"
        }
      ],
      "config_keys": ["scraping.sources"],
      "test_method": "check_code_patterns"
    }
  ]
}
```

**Verification Methods:**
1. **File Existence**: Checks if required files exist
2. **Code Patterns**: Regex search for specific code patterns
3. **Config Keys**: Validates JSON config structure

**Usage:**
```bash
# Run verification
python3 verify_features.py --verbose

# JSON output for CI
python3 verify_features.py --json

# Via module
from modules.feature_verifier import FeatureVerifier
verifier = FeatureVerifier(verbose=True)
results = verifier.verify_all()
```

**CI Integration:**
- Runs automatically on push/PR
- Posts detailed comments on failures
- Never blocks merges
- Creates tracking issues for regressions

### KISS Compliance Monitoring

Monitors code complexity to maintain simplicity:

**Thresholds:**
- **File Size**: Max 500 lines (warn at 350)
- **Function Length**: Max 50 lines (warn at 30)
- **Nesting Depth**: Max 4 levels (warn at 3)
- **Imports**: Max 15 per file (warn at 10)
- **Workflow Steps**: Max 20 steps (warn at 15)

**Scoring:**
- **Excellent**: 0 violations, 0-3 warnings
- **Good**: 0 violations, 4+ warnings
- **Fair**: 1-2 violations
- **Poor**: 3+ violations

**Usage:**
```bash
# Check compliance
python3 check_kiss.py

# Verbose output
python3 check_kiss.py --verbose

# JSON output
python3 check_kiss.py --json

# Via module
from modules.kiss_checker import KISSChecker
checker = KISSChecker(verbose=True)
results = checker.check_all()
exit_code = checker.print_report()
```

**CI Integration:**
- Runs after merges to preview branch
- Creates GitHub issues for major violations
- Provides specific refactoring guidance
- Configurable enforcement levels

**Refactoring Guidance:**
```
Violation: File too large (792 lines)
Suggestion: Split into smaller modules:
  - Extract handler functions
  - Move utilities to separate file
  - Create focused submodules

Violation: Deep nesting (9 levels)
Suggestion: Flatten using techniques:
  - Use early returns (guard clauses)
  - Extract nested logic to functions
  - Replace nested if/else with strategy pattern
```

### Automated Linting

Multi-language linting with configurable enforcement:

**Python (flake8):**
- Syntax errors (blocking)
- Undefined variables (blocking)
- PEP8 style (warning)
- Max line length: 100 characters

**JavaScript (jshint):**
- Syntax errors (configurable)
- Undefined variables (configurable)
- ES6 support
- Browser globals allowed

**JSON (jsonlint):**
- Syntax validation
- Schema compliance
- Formatting checks

**Configuration:**
```yaml
env:
  FAIL_ON_PYTHON_CRITICAL: 'true'   # Block on syntax errors
  FAIL_ON_PYTHON_STYLE: 'false'     # Warn on PEP8 violations
  FAIL_ON_JS_ERRORS: 'false'        # Warn on JS issues
  MAX_PYTHON_ERRORS: 0              # Threshold before blocking
```

**Usage:**
```bash
# Manual linting
flake8 src/ --max-line-length=100
jshint static/js/app.js
jsonlint features.json

# CI runs automatically on push/PR
```

### Testing

Comprehensive test suite for all features:

**Filter Tests** (`test_filters.py`):
```bash
# Run all filter tests
python3 test_filters.py --verbose

# Tests cover:
# - Distance calculation (Haversine formula)
# - Distance filter thresholds
# - Event type filtering
# - Time-based filtering
# - Combined filter scenarios
# - Predefined location validation
```

**Feature Tests** (`verify_features.py`):
```bash
# Verify all 27 features
python3 verify_features.py --verbose

# Checks:
# - File existence
# - Code pattern presence
# - Config key validation
```

**KISS Tests** (`check_kiss.py`):
```bash
# Check code complexity
python3 check_kiss.py --verbose

# Analyzes:
# - File sizes
# - Function lengths
# - Nesting depths
# - Import counts
# - Workflow complexity
```

---

## Development

### Configuration

Two configuration files for different environments:

**`config.dev.json`** - Development Mode
```json
{
  "app": {
    "name": "KRWL HOF Community Events",
    "debug": true
  },
  "map": {
    "center": {"lat": 50.3167, "lon": 11.9167},
    "zoom": 13
  },
  "filters": {
    "default_distance_km": 1.25,
    "default_time_filter": "till_sunrise"
  },
  "predefined_locations": [
    {"name": "Main Station", "lat": 50.3125, "lon": 11.9189},
    {"name": "Mayor's Office", "lat": 50.3177, "lon": 11.9156},
    {"name": "City Center", "lat": 50.3167, "lon": 11.9167}
  ],
  "scraping": {
    "sources": [],
    "interval_minutes": 60
  },
  "editor": {
    "require_approval": true,
    "auto_publish": false
  }
}
```

**`config.prod.json`** - Production Mode
```json
{
  "app": {
    "name": "KRWL HOF Community Events",
    "debug": false
  },
  // ... same structure, optimized values
}
```

### Adding New Features

When adding a new feature, update the feature registry:

1. **Add to `features.json`:**
```json
{
  "id": "my-new-feature",
  "name": "My New Feature",
  "description": "Description of the feature",
  "category": "frontend|backend|deployment",
  "implemented": true,
  "files": ["path/to/file.py"],
  "code_patterns": [
    {
      "file": "path/to/file.py",
      "pattern": "class MyFeature|def my_function",
      "description": "Feature implementation exists"
    }
  ],
  "config_keys": ["config.key.path"],
  "test_method": "check_code_patterns"
}
```

2. **Verify the feature:**
```bash
python3 verify_features.py --verbose
```

3. **Check KISS compliance:**
```bash
python3 check_kiss.py
```

4. **Run tests:**
```bash
python3 test_filters.py  # If filter-related
```

### Running Tests

```bash
# Run all quality checks
python3 verify_features.py --verbose
python3 check_kiss.py --verbose
python3 test_filters.py --verbose

# Run linters
flake8 src/ --max-line-length=100
jshint static/js/app.js
jsonlint features.json config.dev.json config.prod.json

# Check everything
python3 verify_features.py && \
python3 check_kiss.py && \
python3 test_filters.py && \
echo "✓ All checks passed!"
```

### Code Style

**Python:**
- PEP8 compliant
- Max line length: 100 characters
- Use docstrings for all functions/classes
- Type hints where appropriate
- Follow KISS principles

**JavaScript:**
- ES6+ syntax
- Semicolons required
- Use const/let (not var)
- camelCase for variables
- Clear function names

**General:**
- Keep files under 500 lines
- Keep functions under 50 lines
- Max nesting depth: 4 levels
- Meaningful variable names
- Comments for complex logic

---

## Deployment

### Preview Deployment

Automatic deployment to preview branch on every push:

**URL:**
- With custom domain: `https://yourdomain.com/preview`
- GitHub Pages: `https://feileberlin.github.io/krwl-hof/preview`

**Workflow:** `.github/workflows/deploy-preview.yml`

**Features:**
- Auto-detects custom domain from CNAME
- Generates correct base URLs
- Deploys to `gh-pages` branch under `/preview` path
- No hardcoded paths

**Manual Preview:**
```bash
# Generate static files
python3 src/main.py
# Select option 4: Generate Static Site

# Files created in static/
# Deploy manually or wait for CI
```

### Production Deployment

Controlled deployment to production:

**URL:**
- With custom domain: `https://yourdomain.com`
- GitHub Pages: `https://feileberlin.github.io/krwl-hof`

**Workflow:** `.github/workflows/deploy-production.yml`

**Promotion Process:**
1. Test changes in preview environment
2. Create promotion PR from preview to main
3. Automated checks run (features, KISS, linting)
4. Review and approve PR
5. Merge triggers production deployment

### Custom Domains

To use a custom domain:

1. **Create CNAME file:**
```bash
echo "yourdomain.com" > static/CNAME
```

2. **Configure DNS:**
```
Type: CNAME
Name: @ (or subdomain)
Value: feileberlin.github.io
```

3. **Deploy:**
```bash
# Push changes
git add static/CNAME
git commit -m "Add custom domain"
git push

# Workflows auto-detect CNAME
# Preview: yourdomain.com/preview
# Production: yourdomain.com
```

---

## Documentation

All documentation consolidated in this README:

**Sections:**
- [Overview](#overview) - Project introduction
- [Features](#features) - Complete feature list
- [Quick Start](#quick-start) - Getting started guide
- [Project Structure](#project-structure) - File organization
- [Core Features](#core-features) - Detailed feature docs
- [Quality Assurance](#quality-assurance-system) - QA tools
- [Development](#development) - Developer guide
- [Deployment](#deployment) - Deployment instructions

**Additional Documentation:**
- `.github/FEATURE_REGISTRY.md` - Feature registry guide
- `.github/DEPLOYMENT.md` - Deployment details
- `.github/PROMOTE_WORKFLOW.md` - Promotion workflow
- Inline code comments - All modules well-commented

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Before Starting:**
   - Check existing issues
   - Read the feature registry
   - Review KISS principles

2. **Development:**
   - Create feature branch
   - Write tests for new features
   - Keep code simple (KISS)
   - Add feature to registry
   - Update documentation

3. **Quality Checks:**
   ```bash
   # Run all checks before committing
   python3 verify_features.py
   python3 check_kiss.py
   python3 test_filters.py
   flake8 src/
   ```

4. **Pull Requests:**
   - Clear description
   - Link related issues
   - Include tests
   - Pass all CI checks
   - Update feature registry
   - Update this README if needed

5. **Code Review:**
   - Address reviewer feedback
   - Keep changes focused
   - Maintain backward compatibility
   - Document breaking changes

---

## License

This project is open source. Please check the LICENSE file for details.

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/feileberlin/krwl-hof/issues)
- **Discussions**: [GitHub Discussions](https://github.com/feileberlin/krwl-hof/discussions)
- **Email**: See GitHub profile

---

## Changelog

### Recent Changes

**v2.0.0 - KISS Refactoring & QA System** (Current)
- ✅ Complete Python modularization
- ✅ Feature registry system (27 features)
- ✅ KISS compliance monitoring
- ✅ Automated linting (Python, JS, JSON)
- ✅ Inline interactive filter UI
- ✅ Full moon API integration
- ✅ Comprehensive test suite
- ✅ Thin wrapper scripts for backward compatibility
- ✅ Consolidated documentation

**v1.0.0 - Initial Release**
- Event scraping and management
- Editor workflow with approval
- Interactive map with geolocation
- Static site generation
- GitHub Pages deployment

---

**Made with ❤️ for the community**

*This README consolidates all project documentation. For specific details, see inline code comments and workflow files.*
