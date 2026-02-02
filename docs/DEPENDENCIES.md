# Module Dependency Map

**Purpose**: This document provides visual maps showing how modules depend on each other. Use this to understand what code might break when making changes.

## Quick Reference

### "If I change X, what breaks?"

| Module | Direct Impact | Indirect Impact |
|--------|---------------|-----------------|
| **config.json** | All modules | Entire application |
| **utils.py** | Most Python modules | Backend workflows |
| **event_schema.py** | scraper, editor, validator | Data integrity |
| **app.js** | All frontend modules | UI functionality |
| **site_generator.py** | HTML output | Deployment |
| **map.js** | Event markers | Visual display |
| **filters.js** | Event visibility | Search functionality |
| **storage.js** | Bookmarks, custom location | User data |

---

## Frontend Module Dependency Map

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    FRONTEND MODULE DEPENDENCY MAP                          ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: CORE UTILITIES (No dependencies on other modules)                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  utils.js        │  ← Core utilities (date formatting, etc.)
    │  EventUtils      │
    └────────┬─────────┘
             │ uses
             ↓
    ┌──────────────────┐
    │ template-engine  │  ← Template processing
    │ TemplateEngine   │
    └──────────────────┘

    ┌──────────────────┐
    │ dropdown.js      │  ← Custom dropdown widget
    │ CustomDropdown   │
    └──────────────────┘

    ┌──────────────────┐
    │ subjective-day   │  ← Time calculations (sunrise/sunset)
    │ SubjectiveDay    │
    └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: DOMAIN MODULES (Use Layer 1, no dependencies on Layer 3)         │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  storage.js      │  ← LocalStorage management (bookmarks, custom location)
    │  EventStorage    │
    └──────────────────┘

    ┌──────────────────┐
    │  filters.js      │  ← Event filtering logic
    │  EventFilter     │
    └──────────────────┘

    ┌──────────────────┐
    │  map.js          │  ← Leaflet.js map management
    │  MapManager      │
    └──────────────────┘

    ┌──────────────────┐
    │  forms.js        │  ← Form handling (submission to GitHub)
    │  FormsManager    │
    └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: UI MODULES (Use Layer 1 & 2)                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │  dashboard-ui.js     │  ← Dashboard menu, debug info, stats
    │  DashboardUI         │
    └──────────────────────┘
             │ uses
             ↓
    ┌──────────────────────┐
    │ event-listeners.js   │  ← Event handlers, keyboard shortcuts
    │ EventListeners       │  │ uses CustomDropdown
    └──────────┬───────────┘
               │
               ↓
    ┌──────────────────────┐
    │ filter-description   │  ← Filter UI descriptions
    │ FilterDescriptionUI  │
    └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: MAIN APPLICATION (Orchestrates all modules)                      │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │     app.js          │
                        │   EventsApp         │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ↓              ↓              ↓
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │ MapManager   │  │ EventFilter  │  │ EventStorage │
         └──────────────┘  └──────────────┘  └──────────────┘
                    ↓              ↓              ↓
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │EventListeners│  │ DashboardUI  │  │ FormsManager │
         └──────────────┘  └──────────────┘  └──────────────┘


═══════════════════════════════════════════════════════════════════════════════
 KEY RELATIONSHIPS:
═══════════════════════════════════════════════════════════════════════════════

 app.js (EventsApp)
   ├─→ uses MapManager (map.js)         - Map display & markers
   ├─→ uses EventFilter (filters.js)    - Filter events
   ├─→ uses EventStorage (storage.js)   - Save bookmarks & location
   ├─→ uses EventListeners (event-listeners.js) - UI interactions
   ├─→ uses DashboardUI (dashboard-ui.js) - Dashboard menu
   ├─→ uses FormsManager (forms.js)     - Event submission
   └─→ uses EventUtils (utils.js)       - Utilities

 event-listeners.js
   └─→ uses CustomDropdown (dropdown.js) - Filter dropdowns

 utils.js
   └─→ uses TemplateEngine (template-engine.js) - Template processing
```

---

## Backend Module Dependency Map

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    BACKEND MODULE DEPENDENCY MAP                           ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: CORE UTILITIES & CONFIGURATION                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
    │  utils.py        │      │  config.json     │      │  exceptions.py   │
    │  (load_config,   │      │  (project config)│      │  (custom errors) │
    │   path helpers)  │      └──────────────────┘      └──────────────────┘
    └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: DATA MODELS & VALIDATION                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐      ┌──────────────────┐
    │ event_schema.py  │      │ event_validator  │
    │ (event structure)│──┬──→│ (validation)     │
    └──────────────────┘  │   └──────────────────┘
                          │
                          │   ┌──────────────────┐
                          └──→│ entity_models.py │
                              │ (data models)    │
                              └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: CORE BUSINESS LOGIC                                              │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
    │  scraper.py      │      │  editor.py       │      │ archive_events   │
    │  (event scraping)│      │  (review/approve)│      │ (old events)     │
    └────────┬─────────┘      └──────────────────┘      └──────────────────┘
             │ uses
             ↓
    ┌──────────────────┐      ┌──────────────────┐
    │ weather_scraper  │      │ location_resolver│
    │ (weather data)   │      │ (geocoding)      │
    └──────────────────┘      └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: SITE GENERATION & BUILD                                          │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │ site_generator.py   │
                        │ (HTML generation)   │
                        └──────────┬──────────┘
                                   │ uses
                    ┌──────────────┼──────────────┐
                    ↓              ↓              ↓
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │ linter.py    │  │ minifier.py  │  │ compressor   │
         │ (WCAG check) │  │ (CSS/JS min) │  │ (gzip)       │
         └──────────────┘  └──────────────┘  └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: CLI & ORCHESTRATION                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │ event_manager.py    │ ⭐ SINGLE ENTRY POINT
                        │ (CLI + TUI)         │
                        └──────────┬──────────┘
                                   │ orchestrates
                    ┌──────────────┼──────────────────────────┐
                    ↓              ↓              ↓           ↓
         ┌──────────────┐  ┌──────────────┐  ┌────────┐  ┌─────────┐
         │ scraper.py   │  │ editor.py    │  │ site   │  │ feature │
         │              │  │              │  │ gen    │  │ verify  │
         └──────────────┘  └──────────────┘  └────────┘  └─────────┘


═══════════════════════════════════════════════════════════════════════════════
 KEY WORKFLOWS:
═══════════════════════════════════════════════════════════════════════════════

 1. SCRAPING WORKFLOW:
    event_manager.py → scraper.py → weather_scraper.py
                                 ↓
                          pending_events.json

 2. EDITORIAL WORKFLOW:
    event_manager.py → editor.py → events.json (published)
                                 ↓
                          rejected_events.json (rejected)

 3. BUILD WORKFLOW:
    event_manager.py → site_generator.py → linter.py
                                        ↓
                                   public/index.html

 4. FEATURE VALIDATION:
    event_manager.py → feature_verifier.py → features.json
                                           ↓
                                      validation report


═══════════════════════════════════════════════════════════════════════════════
 CRITICAL DEPENDENCIES (If you change X, these are affected):
═══════════════════════════════════════════════════════════════════════════════

 utils.py
   ↓ affects EVERYTHING (config loading, path resolution)

 event_schema.py
   ↓ affects: event_validator.py, scraper.py, editor.py, site_generator.py

 scraper.py
   ↓ affects: pending_events.json, event_manager.py CLI

 site_generator.py
   ↓ affects: public/index.html, deployment workflow

 config.json
   ↓ affects: ALL modules (configuration source)
```

---

## Detailed Module Dependencies

### Frontend Modules

#### app.js (EventsApp)
- **Depends on:**
  - `map.js` (MapManager) - Map rendering and marker placement
  - `filters.js` (EventFilter) - Event filtering logic
  - `storage.js` (EventStorage) - LocalStorage operations
  - `event-listeners.js` (EventListeners) - UI event handling
  - `dashboard-ui.js` (DashboardUI) - Dashboard menu
  - `forms.js` (FormsManager) - Form submissions
  - `utils.js` (EventUtils) - Utility functions
- **Used by:** None (top-level orchestrator)
- **Impact if changed:** 🔴 CRITICAL - Affects entire frontend

#### map.js (MapManager)
- **Depends on:** Leaflet.js (external library)
- **Used by:** `app.js`
- **Impact if changed:** 🟠 HIGH - Affects map display, markers, popups

#### filters.js (EventFilter)
- **Depends on:** None (standalone)
- **Used by:** `app.js`
- **Impact if changed:** 🟠 HIGH - Affects event visibility and search

#### storage.js (EventStorage)
- **Depends on:** LocalStorage API (browser)
- **Used by:** `app.js`
- **Impact if changed:** 🟡 MEDIUM - Affects bookmarks and custom location

#### event-listeners.js (EventListeners)
- **Depends on:**
  - `dropdown.js` (CustomDropdown) - Dropdown widgets
- **Used by:** `app.js`
- **Impact if changed:** 🟡 MEDIUM - Affects UI interactions

#### dashboard-ui.js (DashboardUI)
- **Depends on:** None (standalone)
- **Used by:** `app.js`
- **Impact if changed:** 🟢 LOW - Only affects dashboard menu

#### utils.js (EventUtils)
- **Depends on:**
  - `template-engine.js` (TemplateEngine) - Template processing
- **Used by:** `app.js`
- **Impact if changed:** 🟠 HIGH - Utility functions used throughout

### Backend Modules

#### event_manager.py (CLI/TUI)
- **Depends on:**
  - `scraper.py` - Event scraping
  - `editor.py` - Editorial workflow
  - `site_generator.py` - HTML generation
  - `feature_verifier.py` - Feature validation
  - `utils.py` - Config and path utilities
- **Used by:** None (entry point)
- **Impact if changed:** 🔴 CRITICAL - Affects all CLI commands

#### scraper.py
- **Depends on:**
  - `utils.py` - Config loading
  - `event_schema.py` - Event validation
  - `weather_scraper.py` - Weather data
- **Used by:** `event_manager.py`
- **Impact if changed:** 🟠 HIGH - Affects event data collection

#### editor.py
- **Depends on:**
  - `utils.py` - Config and file operations
  - `event_validator.py` - Event validation
- **Used by:** `event_manager.py`
- **Impact if changed:** 🟡 MEDIUM - Affects editorial workflow

#### site_generator.py
- **Depends on:**
  - `utils.py` - Config and paths
  - `linter.py` - WCAG validation
  - `minifier.py` - CSS/JS minification
- **Used by:** `event_manager.py`
- **Impact if changed:** 🔴 CRITICAL - Affects HTML output and deployment

#### utils.py
- **Depends on:** `config.json`
- **Used by:** Nearly all backend modules
- **Impact if changed:** 🔴 CRITICAL - Affects entire backend

---

## Testing Guidelines

### Before Making Changes

1. **Identify affected modules** using this dependency map
2. **Run relevant tests:**
   ```bash
   # For frontend changes
   python3 src/event_manager.py generate  # Regenerate HTML
   
   # For backend changes
   python3 src/modules/feature_verifier.py --verbose
   python3 tests/test_scraper.py --verbose
   python3 tests/test_event_schema.py --verbose
   ```

3. **Test downstream impacts:**
   - If you change `utils.py` → test ALL modules
   - If you change `app.js` → test ALL frontend features
   - If you change `scraper.py` → test event data integrity

### After Making Changes

1. **Validate features:** `python3 src/modules/feature_verifier.py`
2. **Run affected tests**
3. **Check generated output** (HTML, JSON files)
4. **Review dependencies** in this document

---

## For GitHub Copilot Agents

**Use this document to:**
1. Understand blast radius of changes
2. Identify which tests to run
3. Determine what to verify after changes
4. Avoid breaking unrelated features

**When making changes:**
1. Check this map BEFORE editing code
2. Identify all dependent modules
3. Plan minimal surgical changes
4. Test all affected modules
5. Update features.json if adding new dependencies

---

## Maintenance

This document should be updated when:
- [ ] New modules are added
- [ ] Module dependencies change
- [ ] Major refactoring occurs
- [ ] Features are added/removed

Last updated: 2026-01-27
