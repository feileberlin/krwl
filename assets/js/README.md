# JavaScript Directory

JavaScript modules for the KRWL HOF application.

## Architecture

The application follows a **modular architecture** with each module having a single responsibility (KISS principle). All modules are concatenated into a single inline script during site generation.

### Module Loading Order

Modules are loaded in dependency order (see `src/modules/site_generator.py`):

1. **storage.js** - Data persistence (no dependencies)
2. **filters.js** - Filtering logic (depends on: storage)
3. **map.js** - Map management (depends on: storage)
4. **speech-bubbles.js** - UI bubble components (depends on: storage)
5. **utils.js** - Utility functions (depends on: template-engine)
6. **template-engine.js** - Template processing
7. **dropdown.js** - UI dropdown component
8. **dashboard-ui.js** - Dashboard updates (depends on: utils)
9. **filter-description-ui.js** - Filter descriptions
10. **event-listeners.js** - Event listener setup (depends on: app, dropdown)
11. **app.js** - Application coordinator (depends on: all modules)

## Module Reference

### storage.js
**Purpose:** Data persistence layer  
**Responsibilities:**
- Filter settings persistence (localStorage/cookies)
- Bookmark management
- Browser feature detection

**Class:** `EventStorage`

### filters.js
**Purpose:** Event filtering logic  
**Responsibilities:**
- Time-based filters (sunrise, full moon, hours)
- Distance-based filters
- Category filters
- Location calculations

**Class:** `EventFilter`

### map.js
**Purpose:** Map management layer  
**Responsibilities:**
- Leaflet.js map initialization
- Marker management and spiderfying
- User location tracking
- Map bounds and zoom control

**Class:** `MapManager`

### speech-bubbles.js
**Purpose:** Speech bubble UI components  
**Responsibilities:**
- Speech bubble positioning (collision-aware)
- Organic spread around markers
- Bubble dragging and following
- Connector line rendering

**Class:** `SpeechBubbles`

### utils.js
**Purpose:** Utility functions  
**Responsibilities:**
- Template event processing (via TemplateEngine)
- Date formatting
- DOM caching

**Class:** `EventUtils`

### template-engine.js
**Purpose:** Dynamic event generation  
**Responsibilities:**
- Template event processing (recurring events)
- Relative time calculations
- Strategy pattern for different template types

**Class:** `TemplateEngine`

### dropdown.js
**Purpose:** Reusable dropdown component  
**Responsibilities:**
- Dropdown UI rendering
- Click handling and focus management
- Instance registry for global close handling

**Class:** `CustomDropdown`

### dashboard-ui.js
**Purpose:** Dashboard debug information  
**Responsibilities:**
- Git commit information display
- Deployment time and environment status
- Event counts and file sizes
- Cache statistics and duplicate warnings

**Class:** `DashboardUI`

### filter-description-ui.js
**Purpose:** Filter bar description updates  
**Responsibilities:**
- Semantic event count sentence generation
- Data-driven filter descriptions (lookup tables)
- Distance and time filter formatting

**Class:** `FilterDescriptionUI`

### event-listeners.js
**Purpose:** UI event listener management  
**Responsibilities:**
- Dashboard menu interactions
- Filter dropdowns and controls
- Keyboard shortcuts
- Focus management and orientation handling

**Class:** `EventListeners`

### app.js
**Purpose:** Application coordinator  
**Responsibilities:**
- Module initialization and coordination
- App state management
- Main application loop
- Event loading and rendering

**Class:** `EventsApp`

## Philosophy

**Vanilla JavaScript** - No frameworks, no build step complexity
- ES6+ features for modern browsers
- Progressive enhancement approach
- Works without JavaScript (noscript fallback)
- **KISS Principle**: Each module < 500 lines, single responsibility
- **Modular Design**: Clear dependencies, no circular references

## Usage

These files are inlined into the final HTML by the site generator:

```bash
# Generate static site (concatenates all modules)
python3 src/event_manager.py generate

# Fast event update (no full rebuild)
python3 src/event_manager.py update
```

The site generator automatically:
1. Loads all modules in dependency order
2. Removes CommonJS export statements (not needed in browser)
3. Concatenates them into single inline script
4. Wraps with debug comments showing module boundaries

## Code Style

- **ES6+ features** (arrow functions, async/await, classes)
- **KISS principle** - Keep functions small and focused
- **Single responsibility** - Each module does one thing well
- **Document complex logic** with JSDoc comments
- **Test on multiple browsers** (Chrome, Firefox, Safari)

## Module Size Guidelines

To maintain KISS compliance:
- ✅ Target: < 300 lines per module (ideal)
- ⚠️  Warning: 300-500 lines (acceptable)
- ❌ Error: > 500 lines (refactor into smaller modules)

Current sizes (approximate):
- storage.js: ~200 lines
- filters.js: ~350 lines
- map.js: ~450 lines
- speech-bubbles.js: ~800 lines (needs refactoring)
- utils.js: ~150 lines
- template-engine.js: ~200 lines
- dropdown.js: ~130 lines
- dashboard-ui.js: ~280 lines
- filter-description-ui.js: ~190 lines
- event-listeners.js: ~550 lines (acceptable, handles all UI events)
- app.js: ~700 lines (coordinator, acceptable for main orchestrator)

## Backup Files

The following files are **NOT** used in production (backup/reference only):
- `app-old.js` - Legacy monolithic app
- `app-original.js` - Original pre-refactor version
- `app-before-filter-ui.js` - Before FilterDescriptionUI extraction
- `app.js.backup` - Backup copy
- `event-listeners-old.js` - Legacy event listeners
- `event-listeners-refactored.js` - Intermediate refactor
- `speech-bubbles-complex.js` - Complex collision detection (unused)
- `utils-before-template.js` - Before TemplateEngine extraction

## Related

- **Styles**: [../css/style.css](../css/style.css)
- **HTML Templates**: [../html/](../html/)
- **Site Generator**: [../../src/modules/site_generator.py](../../src/modules/site_generator.py)
- **KISS Checker**: [../../src/modules/kiss_checker.py](../../src/modules/kiss_checker.py)
