# Architecture Overview

This document provides a high-level overview of the KRWL HOF architecture, including module dependencies, data flow, and system design.

## Table of Contents

1. [System Overview](#system-overview)
2. [Module Dependency Diagram](#module-dependency-diagram)
3. [Data Flow](#data-flow)
4. [Key Architectural Decisions](#key-architectural-decisions)

## System Overview

KRWL HOF is a **mobile-first Progressive Web App (PWA)** for discovering community events with interactive map visualization.

**Technology Stack:**
- **Backend**: Python 3.x with modular design
- **Frontend**: Vanilla JavaScript + Leaflet.js
- **Build**: Static site generation
- **Deployment**: GitHub Pages / Netlify / Vercel

**Architecture Philosophy:**
- **KISS Principle**: Keep it simple, avoid over-engineering
- **Progressive Enhancement**: Works without JavaScript, better with it
- **Mobile First**: Optimized for mobile devices
- **Modular Design**: Clear separation of concerns

## Module Dependency Diagram

### Complete System Architecture

```mermaid
graph TB
    subgraph "External Sources"
        RSS[RSS Feeds]
        HTML[HTML Pages]
        API[External APIs]
        FB[Facebook Pages]
        IG[Instagram]
        TG[Telegram Bot]
    end

    subgraph "Backend - Data Ingestion"
        SCRAPER[scraper.py<br/>Event Scraping]
        OCR[OCR Module<br/>Image Analysis]
        AI_CAT[AI Categorization<br/>Event Classification]
        AI_EXT[AI Extraction<br/>Text Processing]
        LOC_RES[Location Resolver<br/>Geocoding]
    end

    subgraph "Backend - Data Management"
        EDITOR[editor.py<br/>Editorial Workflow]
        ARCHIVE[Event Archiving<br/>Old Events]
        BACKUP[Backup System<br/>Event History]
        WEATHER[Weather Scraper<br/>Dresscode Data]
    end

    subgraph "Backend - Core Logic"
        EVENT_MGR[event_manager.py<br/>CLI/TUI Entry Point]
        UTILS[utils.py<br/>Common Utilities]
        CONFIG[config.json<br/>Configuration]
        SCHEMA[Event Schema<br/>Data Validation]
    end

    subgraph "Backend - Build System"
        SITE_GEN[site_generator.py<br/>HTML Generation]
        ASSET_MGR[Asset Manager<br/>CDN Version Tracking]
        LINTER[WCAG Linter<br/>Accessibility Check]
    end

    subgraph "Frontend - Core"
        APP[app.js<br/>Main Orchestrator]
        CONFIG_JS[APP_CONFIG & EventUtils<br/>Env Detection & Defaults]
        UTILS_JS[utils.js<br/>Helper Functions]
    end

    subgraph "Frontend - Map & Events"
        MAP[map.js<br/>MapManager]
        MARKERS[Marker System<br/>Event Icons]
        BUBBLES[Speech Bubbles<br/>Event Details]
        CARDS[Event Cards<br/>Fallback List]
    end

    subgraph "Frontend - UI Components"
        FILTERS[filters.js<br/>Event Filtering]
        SEARCH[Search Logic<br/>Text Search]
        DASHBOARD[Dashboard Menu<br/>Settings UI]
        TIME_DRAWER[Time Drawer<br/>Time Filters]
    end

    subgraph "Frontend - User Data"
        STORAGE[storage.js<br/>LocalStorage]
        BOOKMARKS[Bookmarks<br/>Saved Events]
        CUSTOM_LOC[Custom Location<br/>User Override]
    end

    subgraph "Data Files"
        EVENTS[events.json<br/>Published Events]
        PENDING[pending_events.json<br/>Awaiting Approval]
        REJECTED[rejected_events.json<br/>Rejected Events]
        DEMO[events.demo.json<br/>Demo Data]
        WEATHER_CACHE[weather_cache.json<br/>Weather Data]
    end

    subgraph "Output"
        HTML_OUT[public/index.html<br/>Generated Site]
        ASSETS_OUT[public/assets/<br/>Inlined CSS/JS]
    end

    %% External to Scraper
    RSS --> SCRAPER
    HTML --> SCRAPER
    API --> SCRAPER
    FB --> OCR
    IG --> SCRAPER
    TG --> SCRAPER

    %% Scraper to Data Management
    SCRAPER --> PENDING
    OCR --> SCRAPER
    AI_CAT --> SCRAPER
    AI_EXT --> SCRAPER
    LOC_RES --> SCRAPER

    %% Data Management Flow
    PENDING --> EDITOR
    EDITOR --> EVENTS
    EDITOR --> REJECTED
    EVENTS --> ARCHIVE
    EVENTS --> BACKUP
    WEATHER --> WEATHER_CACHE

    %% Core Logic Dependencies
    EVENT_MGR --> SCRAPER
    EVENT_MGR --> EDITOR
    EVENT_MGR --> SITE_GEN
    UTILS --> SCRAPER
    UTILS --> EDITOR
    UTILS --> SITE_GEN
    CONFIG --> UTILS
    SCHEMA --> SCRAPER
    SCHEMA --> EDITOR

    %% Build System
    SITE_GEN --> HTML_OUT
    SITE_GEN --> ASSETS_OUT
    ASSET_MGR --> SITE_GEN
    LINTER --> SITE_GEN
    EVENTS --> SITE_GEN
    DEMO --> SITE_GEN
    WEATHER_CACHE --> SITE_GEN
    CONFIG --> SITE_GEN

    %% Frontend Dependencies
    APP --> CONFIG_JS
    APP --> UTILS_JS
    APP --> MAP
    APP --> FILTERS
    APP --> STORAGE
    APP --> DASHBOARD
    
    MAP --> MARKERS
    MAP --> BUBBLES
    MARKERS --> BUBBLES
    
    FILTERS --> SEARCH
    FILTERS --> TIME_DRAWER
    
    STORAGE --> BOOKMARKS
    STORAGE --> CUSTOM_LOC
    
    MAP -.Fallback.-> CARDS

    %% Data to Frontend
    HTML_OUT --> APP
    EVENTS -.Embedded.-> HTML_OUT

    %% Styling
    classDef backend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef frontend fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef external fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    
    class SCRAPER,OCR,AI_CAT,AI_EXT,LOC_RES,EDITOR,ARCHIVE,BACKUP,WEATHER,EVENT_MGR,UTILS,CONFIG,SCHEMA,SITE_GEN,ASSET_MGR,LINTER backend
    class APP,CONFIG_JS,UTILS_JS,MAP,MARKERS,BUBBLES,CARDS,FILTERS,SEARCH,DASHBOARD,TIME_DRAWER,STORAGE,BOOKMARKS,CUSTOM_LOC frontend
    class EVENTS,PENDING,REJECTED,DEMO,WEATHER_CACHE,HTML_OUT,ASSETS_OUT data
    class RSS,HTML,API,FB,IG,TG external
```

### Backend Module Dependency Detail

```mermaid
graph LR
    subgraph "Layer 1: Configuration"
        CONFIG[config.json]
    end

    subgraph "Layer 2: Core Utilities"
        UTILS[utils.py]
        SCHEMA[Event Schema]
    end

    subgraph "Layer 3: Business Logic"
        SCRAPER[scraper.py]
        EDITOR[editor.py]
        ARCHIVE[archive_events.py]
        WEATHER[weather_scraper.py]
    end

    subgraph "Layer 4: Generation"
        SITE_GEN[site_generator.py]
        ASSET_MGR[asset_manager.py]
    end

    subgraph "Layer 5: Entry Point"
        EVENT_MGR[event_manager.py<br/>CLI & TUI]
    end

    CONFIG --> UTILS
    UTILS --> SCRAPER
    UTILS --> EDITOR
    UTILS --> SITE_GEN
    SCHEMA --> SCRAPER
    SCHEMA --> EDITOR
    
    SCRAPER --> EVENT_MGR
    EDITOR --> EVENT_MGR
    ARCHIVE --> EVENT_MGR
    WEATHER --> EVENT_MGR
    SITE_GEN --> EVENT_MGR
    ASSET_MGR --> SITE_GEN

    classDef layer1 fill:#ffebee,stroke:#c62828
    classDef layer2 fill:#fff3e0,stroke:#e65100
    classDef layer3 fill:#e8f5e9,stroke:#2e7d32
    classDef layer4 fill:#e3f2fd,stroke:#1565c0
    classDef layer5 fill:#f3e5f5,stroke:#6a1b9a
    
    class CONFIG layer1
    class UTILS,SCHEMA layer2
    class SCRAPER,EDITOR,ARCHIVE,WEATHER layer3
    class SITE_GEN,ASSET_MGR layer4
    class EVENT_MGR layer5
```

### Frontend Module Dependency Detail

```mermaid
graph LR
    subgraph "Layer 1: Core Utilities"
        UTILS_JS[utils.js<br/>EventUtils]
        TEMPLATE[template-engine.js]
        DROPDOWN[dropdown.js]
        SUBJ_DAY[subjective-day.js]
    end

    subgraph "Layer 2: Domain Logic"
        STORAGE[storage.js<br/>LocalStorage]
        FILTERS[filters.js<br/>EventFilter]
        MAP[map.js<br/>MapManager]
    end

    subgraph "Layer 3: UI Components"
        MARKERS[Marker rendering<br/>in map.js]
        BUBBLES[Event popups<br/>Leaflet native]
        CARDS[Event display<br/>in app.js]
        TIME_DRAWER[filter-description-ui.js]
        DASHBOARD[dashboard-ui.js]
    end

    subgraph "Layer 4: Application"
        APP[app.js<br/>EventApp]
    end

    UTILS_JS --> FILTERS
    UTILS_JS --> MAP
    UTILS_JS --> MARKERS
    TEMPLATE --> BUBBLES
    SUBJ_DAY --> TIME_DRAWER
    
    STORAGE --> APP
    FILTERS --> APP
    MAP --> APP
    
    MAP --> MARKERS
    MAP --> BUBBLES
    MARKERS --> BUBBLES
    FILTERS --> TIME_DRAWER
    
    BUBBLES --> APP
    CARDS --> APP
    TIME_DRAWER --> APP
    DASHBOARD --> APP

    classDef layer1 fill:#ffebee,stroke:#c62828
    classDef layer2 fill:#fff3e0,stroke:#e65100
    classDef layer3 fill:#e8f5e9,stroke:#2e7d32
    classDef layer4 fill:#f3e5f5,stroke:#6a1b9a
    
    class UTILS_JS,TEMPLATE,DROPDOWN,SUBJ_DAY layer1
    class STORAGE,FILTERS,MAP layer2
    class MARKERS,BUBBLES,CARDS,TIME_DRAWER,DASHBOARD layer3
    class APP layer4
```

## Data Flow

### Event Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Scraper
    participant Pending
    participant Editor
    participant Events
    participant Generator
    participant Frontend

    User->>Scraper: Run scrape command
    Scraper->>External: Fetch event data
    External-->>Scraper: Raw data
    Scraper->>Pending: Save pending events
    
    User->>Editor: Review pending events
    Editor->>Pending: Load pending
    Editor->>User: Show events for review
    User->>Editor: Approve/Reject
    Editor->>Events: Save approved events
    Editor->>Rejected: Save rejected events
    
    User->>Generator: Run generate command
    Generator->>Events: Load published events
    Generator->>Config: Load configuration
    Generator->>Frontend: Generate HTML/JS/CSS
    Frontend-->>User: Serve interactive map
```

### Build Process

```mermaid
flowchart TD
    START[Start Build] --> LOAD_CONFIG[Load config.json]
    LOAD_CONFIG --> DETECT_ENV[Detect Environment<br/>Dev vs Production]
    DETECT_ENV --> LOAD_EVENTS[Load events.json]
    LOAD_EVENTS --> LOAD_DEMO{Demo Events?}
    LOAD_DEMO -->|Yes - Dev| MERGE_DEMO[Merge demo events]
    LOAD_DEMO -->|No - Prod| SKIP_DEMO[Skip demo events]
    MERGE_DEMO --> LOAD_WEATHER[Load weather cache]
    SKIP_DEMO --> LOAD_WEATHER
    LOAD_WEATHER --> LOAD_TEMPLATES[Load HTML templates]
    LOAD_TEMPLATES --> LOAD_ASSETS[Load CSS/JS assets]
    LOAD_ASSETS --> INLINE_ASSETS[Inline assets into HTML]
    INLINE_ASSETS --> INJECT_CONFIG[Inject APP_CONFIG]
    INJECT_CONFIG --> INJECT_EVENTS[Inject event data]
    INJECT_EVENTS --> RUN_LINTER[Run WCAG linter]
    RUN_LINTER --> WRITE_OUTPUT[Write public/index.html]
    WRITE_OUTPUT --> END[Build Complete]

    style START fill:#e8f5e9,stroke:#2e7d32
    style END fill:#e8f5e9,stroke:#2e7d32
    style DETECT_ENV fill:#fff3e0,stroke:#e65100
    style LOAD_DEMO fill:#fff3e0,stroke:#e65100
```

## Key Architectural Decisions

See [Architectural Decision Records (ADRs)](./adr/README.md) for detailed rationale:

1. **[ADR-001: Fallback List When Map Fails](./adr/001-fallback-list-when-map-fails.md)**
   - Progressive enhancement strategy
   - Resilience against CDN failures
   - Accessibility considerations

2. **[ADR-002: Vanilla JS Over Frameworks](./adr/002-vanilla-js-over-frameworks.md)**
   - KISS principle for frontend
   - No React/Vue/Angular dependency
   - Small bundle size, fast loading

3. **[ADR-003: Single Entry Point](./adr/003-single-entry-point.md)**
   - Unified CLI/TUI in event_manager.py
   - No src/main.py confusion
   - Consistent initialization

## Critical Dependencies

### Backend Critical Path

```
config.json → utils.py → (scraper.py, editor.py) → event_manager.py
```

**If you change:**
- `config.json` → Test ALL modules (entire app affected)
- `utils.py` → Test scraper, editor, site_generator (most backend affected)
- `event_manager.py` → Test CLI commands and TUI (entry point)

### Frontend Critical Path

```
utils.js → (map.js, filters.js) → app.js
```

**If you change:**
- `app.js` → Test entire frontend (main orchestrator)
- `map.js` → Test marker display, speech bubbles (map visualization)
- `filters.js` → Test event filtering, search (event visibility)

## Performance Considerations

### Bundle Size Targets

- **Total JS**: < 50KB (currently ~40KB)
- **Total CSS**: < 30KB (currently ~25KB)
- **Leaflet.js**: ~40KB (external, cacheable)
- **Total Page Weight**: < 150KB (excluding images)

### Loading Performance

- **First Contentful Paint**: < 1.5s target
- **Time to Interactive**: < 5s target
- **Page Load**: < 3s target

### Optimization Strategies

- Inline all CSS/JS (no external requests except CDN)
- Minify CSS/JS in production builds
- Compress images (SVG preferred)
- Lazy load event data (load on scroll for large lists)
- Cache events in localStorage
- Prefetch weather data

## Security Considerations

### Backend

- ✅ Input validation on all scraped data
- ✅ Schema validation (Pydantic models)
- ✅ No secrets in config files (use environment variables)
- ✅ Editorial workflow prevents malicious event injection

### Frontend

- ✅ XSS protection via proper escaping
- ✅ Content Security Policy headers
- ✅ HTTPS only (enforced by hosting)
- ✅ LocalStorage data sanitization

## Testing Strategy

### Backend Tests

- **Unit Tests**: Individual module functions
- **Integration Tests**: End-to-end workflows (scrape → approve → generate)
- **Schema Tests**: Event data validation
- **KISS Tests**: Architecture compliance

### Frontend Tests

- **Manual Testing**: Browser DevTools, mobile emulation
- **Accessibility Testing**: WCAG AA compliance, screen readers
- **Cross-Browser Testing**: Chrome, Firefox, Safari
- **Performance Testing**: Lighthouse scores

### Test Commands

```bash
# Backend tests
python3 tests/test_scraper.py --verbose
python3 tests/test_event_schema.py --verbose
python3 src/modules/kiss_checker.py --verbose

# Feature verification
python3 src/modules/feature_verifier.py --verbose

# Filter tests
python3 src/modules/filter_tester.py --verbose

# Config validation (CRITICAL before commits)
python3 scripts/validate_config.py
```

## Deployment Architecture

```mermaid
flowchart LR
    DEV[Local Development] -->|git push| GITHUB[GitHub Repo]
    GITHUB -->|PR Created| CI[GitHub Actions CI]
    CI -->|Tests Pass| PREVIEW[PR Preview Deploy]
    PREVIEW -->|Review Approved| MERGE[Merge to main]
    MERGE -->|Auto Deploy| PROD[Production Site]
    
    CI -->|Run Tests| TESTS[pytest, linting, KISS check]
    CI -->|Build Site| BUILD[python3 src/event_manager.py generate]
    BUILD -->|Deploy| GH_PAGES[GitHub Pages]
    
    style DEV fill:#e8f5e9,stroke:#2e7d32
    style PROD fill:#ffebee,stroke:#c62828
    style CI fill:#e3f2fd,stroke:#1565c0
```

## References

- **Feature Registry**: [features.json](../features.json) - Complete feature list with dependencies
- **Dependency Maps**: [DEPENDENCIES.md](../DEPENDENCIES.md) - Detailed module relationships
- **Project Guidelines**: [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Coding standards
- **ADRs**: [docs/adr/](./adr/) - Architectural decisions with rationale

## Contributing

When making architectural changes:

1. **Check dependencies first**: Use `python3 src/modules/dependency_checker.py --check-feature FEATURE_ID`
2. **Document decisions**: Create ADR if making significant architectural choice
3. **Update diagrams**: Keep this document in sync with code
4. **Run tests**: Verify no breaking changes
5. **Update features.json**: Add/update feature entries with dependencies
