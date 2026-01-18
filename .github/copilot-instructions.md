# Copilot Instructions for KRWL HOF Community Events

> **For GitHub Copilot Coding Agents**: This file provides comprehensive guidance for understanding and working with the KRWL HOF Community Events project. These instructions help you make context-aware suggestions, follow project conventions, and avoid common pitfalls.

## Project Overview

KRWL HOF is a **mobile-first Progressive Web App (PWA)** for discovering community events with interactive map visualization. The project uses a Python backend for event scraping/management and a vanilla JavaScript frontend with Leaflet.js for mapping.

### Architecture
- **Backend**: Python 3.x with modular TUI (Text User Interface)
- **Frontend**: Vanilla JavaScript (no frameworks), Leaflet.js for maps
- **Deployment**: Static site generation (configurable output path via `config.[prod,dev].json` → future `build` section, defaults to `public/index.html`) → Deployed to hosting platform (GitHub Pages, Netlify, Vercel, etc.)
- **Data Flow**: Scraping → Pending queue → Editorial review → Published events

## Technology Stack

### Backend (Python)
- **Core**: Python 3.x, modular design
- **Dependencies**: requests>=2.31.0, beautifulsoup4>=4.12.0, lxml>=4.9.0, feedparser>=6.0.10 (see `requirements.txt`)
- **Key Modules**:
  - `src/event_manager.py` - ⭐ CLI entry point, TUI, and event management (SINGLE SOURCE OF TRUTH)
  - `src/modules/scraper.py` - Event scraping (RSS, HTML, API)
  - `src/modules/editor.py` - Editorial workflow
  - `src/modules/site_generator.py` - HTML generation and build system
  - `src/modules/filter_tester.py` - Filter testing
  - `src/modules/feature_verifier.py` - Feature registry validation

### Frontend (JavaScript)
- **Framework**: None (vanilla JS)
- **Maps**: Leaflet.js
- **PWA**: Manifest.json for installability (service worker planned for future)
- **Files**: 
  - `public/index.html` - Main app
  - `assets/js/app.js` - App logic
  - `assets/css/style.css` - Styles

### Configuration

**IMPORTANT: Automatic Environment Detection**

This project uses a **single unified config file** (`config.json`) with automatic environment detection that works across **all major hosting platforms**:

- **config.json** - Unified configuration with smart defaults that automatically adapt based on environment
  - Local Development: `debug=true`, `data.source="both"` (real + demo events), `watermark="DEV"`
  - CI/Production: `debug=false`, `data.source="real"`, `watermark="PRODUCTION"`

**How It Works:**
- Environment is detected automatically using `os.environ` checks in Python
- **CI Detection**: Automatically detects GitHub Actions, GitLab CI, Travis CI, CircleCI, Jenkins, Bitbucket Pipelines, Azure Pipelines, AWS CodeBuild
- **Production Detection**: Automatically detects Vercel, Netlify, Heroku, Railway, Render, Fly.io, Google Cloud Run, AWS, or explicit `ENVIRONMENT=production` (legacy: `NODE_ENV=production`)
- **Development**: Default when NOT in CI and NOT in production (typical for local developers)

**Supported Hosting Platforms:**
- ✅ GitHub Pages (via GitHub Actions CI detection)
- ✅ Vercel (via VERCEL_ENV)
- ✅ Netlify (via NETLIFY + CONTEXT)
- ✅ Heroku (via DYNO)
- ✅ Railway (via RAILWAY_ENVIRONMENT)
- ✅ Render (via RENDER)
- ✅ Fly.io (via FLY_APP_NAME)
- ✅ Google Cloud Run (via K_SERVICE)
- ✅ AWS (via AWS_EXECUTION_ENV)
- ✅ Any platform with ENVIRONMENT=production or NODE_ENV=production (backward compatibility)

**NO MANUAL SWITCHING NEEDED** - Deploy to any platform and it automatically adapts!

See detailed documentation in the "Project Configuration" section below.

## ⚠️ CRITICAL: Single Entry Point

**There is ONLY ONE entry point: `src/event_manager.py`**

- ❌ **`src/main.py` does NOT exist** (and should never be created)
- ✅ **`src/event_manager.py`** contains:
  - CLI argument parsing (`main()` function)
  - TUI (Text User Interface) implementation (`EventManagerTUI` class)
  - All CLI commands (scrape, publish, reject, generate, etc.)

**If you see references to `src/main.py` anywhere:**
- They are **outdated** and should be replaced with `src/event_manager.py`
- Update documentation, scripts, and instructions accordingly

**Usage:**
```bash
# Launch TUI
python3 src/event_manager.py

# CLI commands
python3 src/event_manager.py scrape
python3 src/event_manager.py generate
python3 src/event_manager.py --help
```

## 📁 Project Structure

### Complete Directory Tree

```
krwl-hof/
│
├── .github/
│   ├── workflows/           # CI/CD automation
│   └── copilot-instructions.md  # This file
│
├── src/
│   ├── event_manager.py     # ⭐ SINGLE ENTRY POINT - CLI & TUI
│   └── modules/
│       ├── scraper.py       # Event scraping logic
│       ├── editor.py        # Editorial workflow
│       ├── site_generator.py # HTML generation & build system
│       ├── utils.py         # Common utilities
│       ├── config_editor.py # Config management TUI
│       ├── workflow_launcher.py # GitHub Actions launcher
│       ├── filter_tester.py # Filter testing
│       ├── feature_verifier.py # Feature registry validation
│       ├── kiss_checker.py  # KISS principle validator
│       └── scheduler.py     # Scheduling utilities
│
├── assets/
├── assets/
│   ├── css/
│   │   └── style.css       # ✅ Source styles
│   ├── js/
│   │   └── app.js          # ✅ Source app logic
│   ├── html/               # HTML template components
│   │   ├── html-head.html      # HTML head section with meta tags
│   │   ├── html-body-open.html # Opening body tag
│   │   ├── html-body-close.html # Closing body tag with scripts
│   │   ├── map-main.html       # Map container component
│   │   ├── dashboard-aside.html # Dashboard sidebar component
│   │   ├── filter-nav.html     # Filter navigation component
│   │   ├── noscript-content.html # Fallback content for JavaScript-disabled browsers
│   │   ├── design-tokens.css   # Generated CSS custom properties
│   │   ├── README.md           # Component system documentation
│   │   └── variables-reference.md # CSS design token reference
│   ├── svg/                # SVG icons (favicon, PWA icons, map markers)
│   │   ├── favicon.svg         # App icon
│   │   ├── icon-*.svg          # PWA icons
│   │   ├── marker-*.svg        # Map marker icons
│   │   └── README.md           # SVG marker documentation
│   └── json/               # JSON data files
│       ├── manifest.json       # PWA manifest
│       ├── events.json         # Published events data
│       ├── pending_events.json # Events awaiting approval
│       ├── rejected_events.json # Rejected events log
│       ├── archived_events.json # Archived past events
│       ├── events.demo.json    # Demo events for development
│       ├── old/                # Event backups
│       └── templates/          # JSON templates
│
├── lib/                    # Third-party libraries (gitignored, fetched at build)
│   ├── leaflet/            # Leaflet.js library
│   └── lucide/             # Lucide icons library
│
├── public/                 # Build output (gitignored)
│   └── index.html          # 🚫 AUTO-GENERATED (do not edit directly)
│
├── tests/
│   ├── test_scraper.py
│   ├── test_event_schema.py
│   ├── test_translations.py
│   └── ... (other test files)
│   # Note: test_filters functionality is in src/modules/filter_tester.py
│
├── config.json             # Unified configuration (auto-adapts to environment)
├── features.json           # Feature registry (MUST update when adding features)
└── requirements.txt        # Python dependencies
```

### Module Purposes & When to Edit

| Module | Purpose | Edit When... |
|--------|---------|--------------|
| `src/event_manager.py` | CLI entry point & TUI | Adding CLI commands, TUI menus, or main workflow |
| `src/modules/scraper.py` | Event scraping | Adding/modifying scraping logic or sources |
| `src/modules/editor.py` | Editorial workflow | Changing approval/rejection flow |
| `src/modules/site_generator.py` | HTML generation | Modifying build process or HTML templates |
| `src/modules/utils.py` | Common utilities | Adding shared helper functions |
| `src/modules/config_editor.py` | Config management | Changing config TUI or validation |
| `src/modules/workflow_launcher.py` | GitHub Actions | Modifying CI/CD integration |
| `assets/js/app.js` | Frontend logic | Adding map features, filters, or UI behavior |
| `assets/css/style.css` | Styles | Changing appearance, layout, or themes |
| `config.json` | Configuration | Adding settings, sources, or options |
| `features.json` | Feature registry | **ALWAYS** when adding new features |

## File System Structure - HTML Template Components

### Directory: `/assets/html/`
Location for reusable HTML template snippets and components that are included/assembled into the final HTML.

**Purpose**: Store modular HTML template fragments as part of the assets directory, colocated with CSS and JavaScript

**Contents**:
- `html-head.html` - HTML head section with meta tags
- `html-body-open.html` - Opening body tag
- `html-body-close.html` - Closing body tag with scripts
- `map-main.html` - Map container component
- `dashboard-aside.html` - Dashboard sidebar component
- `filter-nav.html` - Filter navigation component
- `noscript-content.html` - Fallback content for JavaScript-disabled browsers
- `design-tokens.css` - Generated CSS custom properties
- `README.md` - Component system documentation
- `variables-reference.md` - CSS design token reference

**Usage in Python**:
```python
from src.modules.site_generator import SiteGenerator
generator = SiteGenerator(base_path)
html_head = generator.load_component('html-head.html')  # Loads from /assets/html/
```

**Why "assets/html/"?**:
- Colocates HTML templates with other assets (CSS, JS)
- Clear organization of all frontend resources
- Follows KISS principles (flat, simple structure within assets)
- Aligns with modern web development practices

### Frontend File Edit Policy

✅ **DO edit these source files:**
- `assets/css/style.css` - Source styles
- `assets/js/app.js` - Source app logic  

📝 **Note:** The `site_generator.py` reads source files directly from `assets/css/` and `assets/js/` directories. Build output goes to `public/index.html`.

🚫 **DO NOT edit generated files:**
- `public/index.html` (regenerated by `site_generator.py`)

After editing source files, regenerate with:
```bash
python3 src/event_manager.py generate
```

## 🗺️ Decision Tree: Where to Place New Code

```
┌─ Is this a new feature? ─────────────────────┐
│                                               │
│  ┌─ YES → Update features.json FIRST         │
│  │         (otherwise tests will fail!)      │
│  │                                            │
│  └─ What type of feature?                    │
│       │                                       │
│       ├─ Data/Events related?                │
│       │   ├─ Scraping → src/modules/scraper.py
│       │   ├─ Editorial → src/modules/editor.py
│       │   └─ Management → src/event_manager.py
│       │                                       │
│       ├─ UI/Frontend related?                │
│       │   ├─ Styling → assets/css/style.css │
│       │   └─ Logic → assets/js/app.js       │
│       │                                       │
│       ├─ Build/Generation related?           │
│       │   └─ src/modules/site_generator.py   │
│       │                                       │
│       ├─ Configuration related?              │
│       │   ├─ Settings → config.json
│       │   └─ Config UI → src/modules/config_editor.py
│       │                                       │
│       ├─ Workflow/CI related?                │
│       │   ├─ GitHub Actions → .github/workflows/
│       │   └─ Launcher → src/modules/workflow_launcher.py
│       │                                       │
│       └─ Utility/Helper related?             │
│           └─ src/modules/utils.py            │
│                                               │
└───────────────────────────────────────────────┘
```

### Rules for New Code Placement

1. **Never create top-level Python files** - All Python code belongs in `src/` or `src/modules/`
2. **Never create `src/main.py`** - Use `src/event_manager.py` only
3. **Backend changes go in `src/modules/`** - Keep event_manager.py focused on CLI/TUI
4. **Frontend changes go in `assets/`** - Edit CSS/JS source files, never `public/index.html`
5. **Always update `features.json`** - Required for all new features

## 🚫 Anti-Patterns: What NOT to Do

### ❌ DON'T: Create duplicate entry points
```python
# ❌ BAD: Creating src/main.py
# src/main.py
if __name__ == "__main__":
    # This duplicates event_manager.py functionality
```

### ✅ DO: Use the single entry point
```python
# ✅ GOOD: Use src/event_manager.py
python3 src/event_manager.py scrape
```

---

### ❌ DON'T: Edit auto-generated files
```html
<!-- ❌ BAD: Editing public/index.html directly -->
<style>
  .new-style { color: red; }
</style>
```

### ✅ DO: Edit source files and regenerate
```css
/* ✅ GOOD: Edit assets/css/style.css */
.new-style { color: red; }
```
```bash
python3 src/event_manager.py generate
```

---

### ❌ DON'T: Create top-level Python files
```
krwl-hof/
├── my_new_script.py  # ❌ BAD: Top-level script
```

### ✅ DO: Add to appropriate module
```
krwl-hof/
├── src/
│   └── modules/
│       └── my_new_module.py  # ✅ GOOD: In modules/
```

---

### ❌ DON'T: Skip feature registry updates
```python
# ❌ BAD: Adding feature without updating features.json
# Feature verification tests will fail!
```

### ✅ DO: Always update features.json
```json
// ✅ GOOD: Add entry to features.json
{
  "id": "my-new-feature",
  "name": "My New Feature",
  "description": "What it does",
  "category": "backend",
  "implementation_files": ["src/modules/my_new_module.py"]
}
```

---

### ❌ DON'T: Mix backend and frontend code
```python
# ❌ BAD: HTML generation in scraper.py
def scrape_events():
    events = get_events()
    return f"<html>{events}</html>"  # Wrong layer!
```

### ✅ DO: Keep layers separated
```python
# ✅ GOOD: Scraper returns data only
def scrape_events():
    return get_events()  # Data layer

# site_generator.py handles HTML generation
```

---

### ❌ DON'T: Hardcode configuration
```python
# ❌ BAD: Hardcoded values
MAX_DISTANCE = 5.0
DEFAULT_LAT = 50.3167
```

### ✅ DO: Use config files
```python
# ✅ GOOD: Load from config
config = load_config()
MAX_DISTANCE = config['filtering']['max_distance_km']
DEFAULT_LAT = config['map']['default_center']['lat']
```

---

### ❌ DON'T: Hardcode colors in CSS
```css
/* ❌ BAD: Hardcoded color values */
.bubble-bookmark {
    border: 2px solid #ffb3b3;
    color: #D689B8;
}
```

### ✅ DO: Use CSS variables from design system
```css
/* ✅ GOOD: Use design tokens */
.bubble-bookmark {
    border: 2px solid var(--color-bookmark);
    color: var(--color-primary);
}
```

**If you need a new color:**
1. Add to `config.json` → `design.colors`
2. Run: `python3 src/tools/generate_design_tokens.py`
3. Use: `var(--color-your-new-color)`

## ✅ Quick Reference Checklists

### Pre-Implementation Checklist

Before writing code:
- [ ] Read through the Critical Single Entry Point section
- [ ] Identify which module(s) need changes using the Decision Tree
- [ ] Check if similar functionality already exists (avoid duplication)
- [ ] Plan where to add tests (in `tests/` directory)
- [ ] Review KISS principles in `src/modules/kiss_checker.py`

### Implementation Checklist

While coding:
- [ ] Edit source files only (never auto-generated files)
- [ ] Add/update tests in `tests/` directory
- [ ] Follow existing code style and patterns
- [ ] Keep changes minimal and focused
- [ ] Add docstrings for complex functions
- [ ] Use `src/event_manager.py` for all CLI commands

### Post-Implementation Checklist

After coding:
- [ ] Update `features.json` if adding new features
- [ ] Run relevant tests: `python3 tests/test_*.py --verbose`
- [ ] Verify KISS compliance: `python3 src/modules/kiss_checker.py`
- [ ] Run feature verification: `python3 src/modules/feature_verifier.py --verbose`
- [ ] **Validate config.json**: `python3 scripts/validate_config.py` (prevents demo events on production)
- [ ] If frontend changes: `python3 src/event_manager.py generate`
- [ ] Test manually (run TUI, check generated HTML, etc.)
- [ ] Update documentation if needed

### Pull Request Requirements

Before submitting PR:
- [ ] All tests pass
- [ ] Config validation passes (`python3 scripts/validate_config.py`)
- [ ] No references to `src/main.py` exist
- [ ] `features.json` is up to date
- [ ] Auto-generated files are committed if changed
- [ ] KISS principles followed
- [ ] Code review requested if significant changes


## Critical: Auto-Generated Files 🚫

**DO NOT manually edit these files** - they are generated by `src/modules/site_generator.py`:
- `public/index.html` - Single-file HTML with everything inlined
- `public/lint_protocol.txt` - WCAG AA compliance lint report (generated during build)

### To modify the HTML:
1. Edit component templates in `layouts/components/` directory
2. Edit source CSS/JS files: `assets/css/style.css`, `assets/js/app.js`
3. For advanced changes, edit `src/modules/site_generator.py` build logic
4. Run: `python3 src/event_manager.py generate`
5. Commit both source changes AND generated `public/index.html`

## Build and Test Instructions

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download frontend libraries (Leaflet.js)
python3 src/event_manager.py libs

# Verify library integrity
python3 src/event_manager.py libs verify
```

### Running Locally
```bash
# Start local server
cd public
python3 -m http.server 8000
# Open http://localhost:8000
```

### Testing (ALWAYS run before finalizing changes)

#### Quick Development Tests
```bash
# Feature verification (validates features.json registry)
python3 verify_features.py --verbose

# Scraper tests
python3 test_scraper.py --verbose

# Filter tests (integrated module)
python3 src/modules/filter_tester.py --verbose
# Or via test runner:
python3 src/event_manager.py test filters --verbose

# Event schema validation
python3 test_event_schema.py --verbose

# KISS principle compliance
python3 check_kiss.py --verbose

# Scheduler tests
python3 test_scheduler.py --verbose

# Config validation (prevents demo events on production)
python3 scripts/validate_config.py
```

#### Config Validation (CRITICAL)

**ALWAYS run config validation before committing to prevent demo events on production:**

```bash
python3 scripts/validate_config.py
```

#### **⚠️ CRITICAL: Pre-Existing Test Failures**

**ALWAYS fix pre-existing test failures, even if unrelated to your current changes.**

When you run tests, if you discover any failing tests:
1. **Investigate the failure** - Understand why the test is failing
2. **Fix the underlying issue** - Don't skip or ignore the failure
3. **Verify the fix** - Re-run the test to ensure it passes
4. **Include in your PR** - Pre-existing fixes are part of maintaining code quality

**Why this matters:**
- Broken tests accumulate technical debt
- Future developers lose confidence in the test suite
- Bugs may be masked by ignored test failures
- Test-driven development requires a reliable test suite

**Exception:** If a test failure is due to missing infrastructure (external services, API keys, etc.) that you cannot fix, document it clearly in your PR description.
**What it checks:**
- ✅ `environment` field must be set to `"auto"` (not `"development"` or `"production"`)
- ✅ Prevents demo events from appearing on production map
- ✅ Ensures proper environment auto-detection across all hosting platforms

**Why this matters:**
- Setting `environment: "development"` forces demo events to load in production/CI
- Setting `environment: "production"` forces real events to load in local development
- Using `environment: "auto"` (required) enables automatic environment detection

**CI Integration:**
- GitHub Actions automatically runs this check on every PR
- PRs will be blocked if config validation fails
- This is a **hard requirement** before merging to main branch

See `.github/workflows/config-validation.yml` for the CI workflow.

#### Documentation
```bash
# Regenerate README.md (auto-generated)
python3 scripts/generate_readme.py
```

#### Linting
- **Python**: Linting is advisory (warnings don't block PRs)
- **JavaScript**: ESLint for syntax checking
- **JSON**: Strict validation (blocks PRs on errors)

See `.github/workflows/lint.yml` for full linting configuration.

### Building the Application
```bash
# Generate static site (production-ready HTML)
python3 src/event_manager.py generate

# Fast event update (after scraping or publishing, no full rebuild)
python3 src/event_manager.py update

# Fast weather update (no full rebuild)
python3 src/event_manager.py update-weather
```

**Note:** The `generate` command uses automatic environment detection (development vs production)
based on where the code runs. See "Project Configuration" section for details.

## Code Guidelines

### KISS Principle (Keep It Simple, Stupid)
This project follows **strict KISS principles**. Always:
- Minimize complexity
- Avoid over-engineering
- Use vanilla solutions over frameworks when possible
- Keep files small and focused
- Avoid unnecessary abstractions

**Enforcement**: `check_kiss.py` validates KISS compliance. Review `src/modules/kiss_checker.py` for rules.

### Python Style
- **Python 3.x** standard library preferred
- **Type hints**: Not required but appreciated
- **Docstrings**: **REQUIRED** - Single source of truth for all documentation
- **Error handling**: Comprehensive try/except blocks
- **Module structure**: Keep modules under 1000 lines

### Documentation Philosophy: Docstrings as Single Source of Truth

**This project uses Python docstrings as the primary documentation method to avoid duplication.**

#### Why Docstrings?
- ✅ **No duplication** - Write documentation once, use everywhere
- ✅ **Always up-to-date** - Documentation lives with the code
- ✅ **Programmatic access** - Extract with `__doc__` for help text, CLI, and docs generation
- ✅ **IDE integration** - Hover hints, autocomplete work automatically
- ✅ **Standard Python** - No custom documentation system needed

#### Docstring Best Practices

**Module-level docstrings** (top of file):
```python
"""
Event Archiving Module - KISS Implementation

Simple monthly event archiving based on config.json settings.
Archives old events to keep active list manageable.
"""
```

**Function/method docstrings** (detailed for public APIs):
```python
def archive_events(self, dry_run=False):
    """
    Archive old events based on configurable retention window.
    
    This command moves events older than the configured retention window
    (default: 60 days) to monthly archive files. This keeps the active
    events list manageable and improves site performance.
    
    Configuration: config.json → archiving section
    - retention.active_window_days: How many days to keep active
    - organization.path: Where to save archives
    
    Usage:
        python3 src/event_manager.py archive-monthly           # Run archiving
        python3 src/event_manager.py archive-monthly --dry-run # Preview
    
    Args:
        dry_run: If True, show what would be archived without making changes
        
    Returns:
        Dict with results: total_events, archived_count, active_count, etc.
    """
```

**Short docstrings** (for internal/simple functions):
```python
def _parse_event_date(self, start_str):
    """Parse event start date string to datetime, return None if invalid."""
    # Implementation...
```

#### Using Docstrings for Help Text

Extract docstrings programmatically instead of duplicating text:

```python
# ❌ BAD: Duplicated help text
HELP_TEXT = "Archive events based on retention window..."
def cli_archive():
    """Archive events based on retention window..."""  # Duplicate!

# ✅ GOOD: Single source of truth
def cli_archive():
    """Archive events based on retention window..."""
    
# Extract for help:
print(cli_archive.__doc__)
```

#### When to Write Detailed Docstrings

1. **Always** - Public functions, CLI commands, API endpoints
2. **Always** - Modules (top of file)
3. **Always** - Classes (what they do, how to use them)
4. **Sometimes** - Complex internal functions (if non-obvious)
5. **Rarely** - Simple getters/setters, obvious helpers

#### Docstring Format

Use **Google Style** (readable, concise):

```python
def function(arg1, arg2):
    """
    Short one-line summary.
    
    Longer explanation if needed. Can span multiple paragraphs.
    Explain what the function does, why it exists, and how to use it.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When and why this is raised
    """
```

#### Documentation Generation

The project can auto-generate documentation from docstrings:

```bash
# Generate README from docstrings
python3 scripts/generate_readme.py

# View function help
python3 -c "from src.modules.archive_events import EventArchiver; help(EventArchiver.archive_events)"
```

#### Inline Comments vs Docstrings

- **Docstrings** - WHAT the code does, HOW to use it (external interface)
- **Comments** - WHY the code does it this way (internal reasoning)

```python
def archive_events(self, dry_run=False):
    """Archive old events based on retention window."""  # WHAT it does
    
    # KISS: Use simple month-based grouping instead of complex date math
    # This avoids timezone issues and keeps the code maintainable
    filename = f"{event_date.strftime('%Y%m')}.json"  # WHY we chose this format
```

### JavaScript Style
- **ES6+** features are okay (async/await, arrow functions, etc.)
- **No frameworks**: Vanilla JS only (Leaflet.js is the only external library)
- **Progressive Enhancement**: App must work without JavaScript for basic content
- **Mobile First**: Always test on mobile viewport sizes

### CSS Style
- **Mobile First**: Write for mobile, enhance for desktop
- **CSS Variables**: Use for theming (see `assets/css/style.css`)
- **Responsive**: Use media queries, flexbox, grid
- **Accessibility**: Ensure sufficient contrast, focus indicators

### Design System & CSS Variables (CRITICAL)

**This project uses a centralized design system with CSS custom properties (variables).**

#### Rules for Colors and Styling

1. **NEVER hardcode color values in CSS** (e.g., `color: #ffb3b3`)
2. **ALWAYS use CSS variables from design-tokens.css** (e.g., `color: var(--color-bookmark)`)
3. **To add new colors:**
   - Add to `config.json` → `design.colors` section
   - Run: `python3 src/tools/generate_design_tokens.py`
   - Use the generated `--color-*` variable in your CSS

#### Design Token Workflow

```json
// config.json
{
  "design": {
    "colors": {
      "primary": "#D689B8",
      "bookmark": "#ffb3b3",
      "bookmark_light": "#ffcccc"
      // ... add your colors here
    }
  }
}
```

```bash
# Regenerate design tokens
python3 src/tools/generate_design_tokens.py
```

```css
/* CSS - Use the generated variables */
.my-element {
  color: var(--color-primary);        /* ✅ CORRECT */
  border: 2px solid var(--color-bookmark); /* ✅ CORRECT */
  
  color: #D689B8;                     /* ❌ WRONG - hardcoded */
  border: 2px solid #ffb3b3;          /* ❌ WRONG - hardcoded */
}
```

#### Available Design Token Categories

- **Colors**: `--color-primary`, `--color-bookmark`, `--color-text-primary`, etc.
- **Typography**: `--font-family-base`, `--font-size-base`, `--line-height-base`, etc.
- **Spacing**: `--spacing-xs`, `--spacing-sm`, `--spacing-md`, etc.
- **Z-Index**: `--z-layer-1-map`, `--z-layer-2-event-popups`, etc.
- **Borders**: `--border-width-thin`, `--border-radius-sm`, etc.
- **Effects**: `--shadow-sm`, `--shadow-md`, `--transition-fast`, etc.

#### Why This Matters

- **Instant Rebranding**: Change one value in `config.json`, regenerate, done!
- **Consistency**: All colors come from a single source of truth
- **Maintainability**: No hunting for hardcoded values across 20+ CSS files
- **Design System**: Professional approach to styling
- **Theme Support**: Easy to add dark/light themes in the future

#### When Suggesting CSS Changes

**Before:**
```css
.bubble-bookmark svg {
  fill: #ffb3b3;  /* ❌ Bad - hardcoded */
}
```

**After:**
```css
.bubble-bookmark svg {
  fill: var(--color-bookmark);  /* ✅ Good - uses design token */
}
```

**If the color doesn't exist yet:**
1. Add it to `config.json` → `design.colors`
2. Run `python3 src/tools/generate_design_tokens.py`
3. Use `var(--color-your-new-color)` in CSS

#### Files Involved

- **Source of Truth**: `config.json` → `design` section
- **Generator Script**: `src/tools/generate_design_tokens.py`
- **Generated Output**: `assets/html/design-tokens.css` (auto-generated, do not edit)
- **Usage**: All CSS files in `assets/css/*.css`

## Project Configuration

### Environment Detection (IMPORTANT)

This project uses **automatic environment detection** with smart defaults. Configuration is stored in a single unified file (`config.json`) that intelligently adapts based on where the code runs.

#### Environment Modes

- **Local Development** (developer's machine):
  - `debug = true` - Verbose logging and debug features enabled
  - `data.source = "both"` - Load both real events AND demo events for testing
  - `watermark.text = "DEV"` - Show DEV watermark in UI
  - `app.name` includes `[DEV]` suffix
  - `performance.cache_enabled = false` - Fresh data on each load
  - `performance.prefetch_events = false` - On-demand loading
  - **Detection**: Automatically detected when NOT in CI and NOT in production

- **CI/Production** (All major CI systems and hosting platforms):
  - `debug = false` - Production mode, minimal logging
  - `data.source = "real"` - Only real scraped events (no demo data)
  - `watermark.text = "PRODUCTION"` - Show PRODUCTION watermark
  - `app.name` without `[DEV]` suffix
  - `performance.cache_enabled = true` - Enable caching for speed
  - `performance.prefetch_events = true` - Preload events for performance
  - **Detection**: Automatic via platform-specific environment variables (see list below)

#### How Environment Detection Works

The configuration system uses Python's `os.environ` to automatically detect the environment across all major platforms:

**CI Detection** - Checks for these environment variables:
- `CI` - Generic CI flag (most CI systems)
- `GITHUB_ACTIONS` - GitHub Actions
- `GITLAB_CI` - GitLab CI
- `TRAVIS` - Travis CI
- `CIRCLECI` - CircleCI
- `JENKINS_HOME` / `JENKINS_URL` - Jenkins
- `BITBUCKET_BUILD_NUMBER` - Bitbucket Pipelines
- `TF_BUILD` - Azure Pipelines
- `CODEBUILD_BUILD_ID` - AWS CodeBuild

**Production Detection** - Checks for these environment variables:
- `ENVIRONMENT=production` - Explicit production setting (preferred for Python apps)
- `NODE_ENV=production` - Legacy explicit production setting (backward compatibility)
- `VERCEL_ENV=production` - Vercel
- `NETLIFY=true` + `CONTEXT=production` - Netlify
- `DYNO` - Heroku
- `RAILWAY_ENVIRONMENT=production` - Railway
- `RENDER=true` - Render
- `FLY_APP_NAME` - Fly.io
- `K_SERVICE` - Google Cloud Run
- `AWS_EXECUTION_ENV` - AWS (non-Lambda)

**Development Detection** - Default when neither CI nor production

See `src/modules/utils.py` for the complete implementation:

```python
import os

def is_ci():
    """Detect if running in CI environment"""
    ci_indicators = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'TRAVIS', 
                     'CIRCLECI', 'JENKINS_HOME', 'BITBUCKET_BUILD_NUMBER',
                     'TF_BUILD', 'CODEBUILD_BUILD_ID']
    return any(os.environ.get(var) for var in ci_indicators)

def is_production():
    """Detect if running in production"""
    # Checks for ENVIRONMENT=production (preferred) or NODE_ENV=production (legacy),
    # Vercel, Netlify, Heroku, Railway, Render, Fly.io, Google Cloud Run, AWS
    # See full implementation in src/modules/utils.py
    ...

def is_development():
    """Detect if running in local development"""
    return not is_production() and not is_ci()
```

#### Configuration Loading

The `load_config()` function in `src/modules/utils.py` handles automatic environment detection:

```python
from src.modules.utils import load_config

# Automatically detects environment and applies appropriate overrides
config = load_config(base_path)

# Logs which mode is active: "🚀 Running in development mode (debug: True, data source: both)"
# Or: "🚀 Running in ci mode (debug: False, data source: real)"
# Or: "🚀 Running in production mode (debug: False, data source: real)"
```

#### NO MANUAL SWITCHING NEEDED

The beauty of this system is that **you never need to manually switch configurations**:
- Developers working locally get debug mode automatically
- CI systems get production mode automatically
- **All hosting platforms get production mode automatically** - Just deploy and it works!
- Deployed production sites get production mode automatically

Just write your code and let the environment detection handle the rest!

#### Configuration File Structure

The unified `config.json` contains:
- Inline comments (using `_comment_*` keys) explaining auto-detection behavior
- Base configuration values (defaults used for production/CI)
- All sections: `app`, `debug`, `watermark`, `performance`, `data`, `scraping`, `filtering`, `map`, `editor`

**Important**: The values in `config.json` represent the **base/production defaults**. Development-specific overrides are applied automatically by `load_config()` when running locally.

#### Configuration Override (KISS Approach)

**Simple Override**: To force a specific environment, edit the `environment` field at the top of `config.json`:

```json
{
  "environment": "development",  // Options: "development", "production", or "auto"
  ...
}
```

**Options:**
- `"development"` - Force dev mode (debug, demo events, DEV watermark) - bypasses auto-detection
- `"production"` - Force prod mode (no debug, real events only, PRODUCTION watermark) - bypasses auto-detection  
- `"auto"` - Use automatic detection (default) - detects from hosting platform

**This is the ONLY setting you need to change** - everything else (debug mode, demo events, watermark, caching) automatically follows!

#### Automatic Detection (when environment="auto")

When `environment` is set to `"auto"` (default), the system automatically detects where code is running based on environment variables. Auto-detection still works as described above for CI systems and hosting platforms.

### When Suggesting Code Changes

**ALWAYS follow these guidelines:**

1. **Never hardcode environment checks scattered throughout code**
   - ❌ Bad: `if os.environ.get('CI') == 'true': ...` in multiple files
   - ✅ Good: Use `config['debug']`, `config['data']['source']` from centralized config

2. **Always use the centralized config loader with automatic detection**
   - Import: `from src.modules.utils import load_config`
   - Load: `config = load_config(base_path)`
   - Use: `if config['debug']: print("Debug info...")`

3. **Never suggest placing config in static folders** 
   - Security risk: Config files should stay in repository root
   - Never put `config.json` in `public/` directory

4. **Use environment flags from config object**
   - Debug mode: `if config['debug']:`
   - Data source: `source = config['data']['source']`
   - Watermark: `text = config['watermark']['text']`

5. **When adding new environment-specific behavior**
   - Add the setting to `config.json` with inline comments
   - Add override logic to `load_config()` in `src/modules/utils.py`
   - Document in this copilot instructions file

## Weather Feature

**Weather functionality is simplified and optional:**

### Overview
- Displays current weather dresscode for the map center location
- Embedded directly in `APP_CONFIG.weather.data` (not a separate cache file)
- Controlled by `weather.enabled` config flag (true/false)

### Configuration (`config.json`)
```json
{
  "weather": {
    "enabled": true,           // Master switch (true/false)
    "cache_hours": 1,          // How long to cache scraped weather
    "timeout": 10,             // Scraping timeout in seconds
    "locations": [{            // Location(s) to fetch weather for
      "name": "Hof",
      "lat": 50.3167,
      "lon": 11.9167
    }],
    "display": {
      "show_in_filter_bar": true  // Show in UI filter bar
    }
  }
}
```

### How It Works
1. **Backend**: `python3 src/event_manager.py scrape-weather`
   - Scrapes MSN Weather for configured map center location
   - Validates dresscode against whitelist (`assets/json/weather_dresscodes.json`)
   - Saves to `assets/json/weather_cache.json` (1-hour cache)

2. **Fast Update (Recommended)**: `python3 src/event_manager.py update-weather`
   - Updates weather data directly in existing `public/index.html` without full rebuild
   - Parses `window.APP_CONFIG` and updates `weather.data` field
   - **Performance**: ~0.005 seconds (vs ~30 seconds for full rebuild)
   - **Use case**: Hourly weather scraping in CI/CD without triggering expensive rebuilds

3. **Build Process**: `python3 src/event_manager.py generate`
   - Loads weather cache if available
   - Embeds weather data in `APP_CONFIG.weather.data` (not separate WEATHER_CACHE)
   - Structure: `{dresscode: "Light jacket", temperature: "15°C", timestamp: "..."}`
   - Only needed for full site rebuild (config changes, CSS/JS changes, etc.)

4. **Frontend**: `assets/js/app.js`
   - Reads from `window.APP_CONFIG.weather.data` (not WEATHER_CACHE)
   - Displays in filter bar if `weather.enabled` and `weather.display.show_in_filter_bar`

### Disabling Weather
Set `weather.enabled: false` in `config.json` - that's it! Weather scraping and display will be skipped.

### Key Files
- **Scraper**: `src/modules/weather_scraper.py`
- **Fast Updater**: `src/modules/site_generator.py` → `update_weather_data()` method
- **Config**: `config.json` → `weather` section
- **Dresscodes**: `assets/json/weather_dresscodes.json` (whitelist of valid values)
- **Cache**: `assets/json/weather_cache.json` (generated by scraper, optional)
- **Frontend**: `assets/js/app.js` → `loadWeather()` method

### CI/CD Integration
The GitHub Actions workflow (`website-maintenance.yml`) automatically uses the fast update method:
1. Scrapes weather hourly
2. Calls `update-weather` to inject into HTML (no full rebuild)
3. Commits both `weather_cache.json` and updated `public/index.html` with `[skip ci]` flag
4. Uploads artifact and deploys to GitHub Pages

This avoids triggering expensive full rebuilds every hour for weather updates.

### Migration Note (January 2025)
- **Deprecated**: `window.WEATHER_CACHE` object (complex multi-location cache)
- **New**: `APP_CONFIG.weather.data` (single location, embedded in config)
- Old code reading `window.WEATHER_CACHE` should be updated to use `APP_CONFIG.weather`

## Dependencies and CDN Fallbacks

**Leaflet.js and other dependencies have automatic CDN fallbacks:**

### Overview
The site generator can build HTML even when dependencies (Leaflet, fonts, etc.) are not locally available. This is critical for CI environments without internet access.

### How It Works
1. **Primary**: Site generator tries to inline local dependencies from `lib/` directory
2. **Fallback**: If files missing, injects CDN loader code into generated HTML
3. **Runtime**: Browser loads dependencies from CDN if not inlined

### CDN Fallback Example
When Leaflet is missing locally:
```javascript
/* Leaflet JS: Load from CDN at runtime */
(function() {
    if (typeof L === 'undefined') {
        console.warn('Leaflet not available - loading from CDN...');
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
        script.crossOrigin = '';
        document.head.appendChild(script);
        // ... plus CSS link
    }
})();
```

### Production Best Practice
1. Run `python3 src/event_manager.py dependencies fetch` to download dependencies locally
2. Dependencies are cached in `lib/` directory (gitignored)
3. Inlined dependencies = faster page load, no external requests

### CI/Testing
- Generation continues even if dependencies can't be fetched
- Warns but doesn't fail: `⚠️ Failed to fetch dependencies - will use CDN fallbacks`
- This allows testing/previewing without internet access

### Key Files
- **Generator**: `src/modules/site_generator.py`
  - `load_stylesheet_resources()` - CSS fallbacks
  - `load_script_resources()` - JS fallbacks
  - `ensure_dependencies_present()` - Warns but doesn't fail
- **Config**: Dependencies defined in `DEPENDENCIES` dict in `site_generator.py`

## Feature Registry System

All features must be documented in `features.json` with:
- Unique ID
- Name and description
- Category: `backend`, `frontend`, or `infrastructure`
- Implementation files
- Config keys (if applicable)
- Test method

**Validation**: Run `python3 verify_features.py` to ensure registry matches codebase.

When adding features:
1. Implement the feature
2. Add entry to `features.json`
3. Run `python3 verify_features.py --verbose` to validate

## Testing Requirements

### For Backend Changes
- Add/update tests in `test_*.py` files
- Run relevant test suite before committing
- Ensure tests pass in CI/CD

### For Frontend Changes
- Test in Chrome, Firefox, Safari
- Test on mobile devices (or Chrome DevTools mobile emulation)
- Verify PWA functionality (installability, offline mode)
- Check accessibility (keyboard navigation, screen readers)

### For UI Screenshots
When taking screenshots of the application for PR documentation:
- **ALWAYS wait for the map to fully load** before taking screenshots
- The map uses Leaflet.js which loads asynchronously from CDN
- Wait for markers to appear on the map (not just the "Map Loading..." fallback)
- If using Playwright or similar tools, wait for the map container to be ready:
  - Wait for Leaflet tiles to load
  - Wait for event markers to render
  - Ensure speech bubbles/popups are visible if demonstrating those features
- Screenshots showing "Map Loading..." or fallback content are not acceptable for PR documentation

**CI Environment Limitation**: In CI environments, external CDN resources (Leaflet.js, fonts) may be blocked. If the map cannot load due to network restrictions, document this limitation in the PR and skip the screenshot rather than including a "Map Loading..." screenshot.

### For Configuration Changes
- Test with unified `config.json` (automatic environment detection)
- Verify environment detection works correctly for your changes
- Validate JSON syntax
- Run full test suite

## Deployment Workflow

Simplified workflow with two modes:

1. **Feature branch** → PR to `main` branch
2. **Main branch** → Auto-deploys to production (environment auto-detected)

GitHub Pages serves the `public/` directory directly.

### Build Modes:
- **Production**: Real events only, optimized
- **Development**: Real + demo events, DEV badge shown

## Documentation Standards

### README.md
**AUTO-GENERATED** by `scripts/generate_readme.py`. Do not edit directly.
- Run `python3 scripts/generate_readme.py` to regenerate

### Code Documentation
- Python modules: Docstring at top of file
- Complex functions: Docstring explaining purpose, args, returns
- Configuration: Comments in JSON files (where parser allows)

### Markdown Files
- Use ATX-style headers (`#`, `##`, etc.)
- Include code blocks with language specifiers
- Add examples where helpful
- Keep lines under 120 characters when possible

## Workflow-Specific Guidelines

### Event Scraping
1. Configure source in `config.json` under `scraping.sources[]`
2. Implement scraper logic in `src/modules/scraper.py` if needed
3. Test with: `python3 test_scraper.py --verbose`
4. Scraped events go to `data/pending_events.json` for editorial review

### Editorial Workflow
1. Pending events require approval (unless `editor.auto_publish: true`)
2. Use TUI: `python3 src/event_manager.py` → "Review Pending Events"
3. Or use GitHub UI: Actions → "Review Events (GitHub UI)" → Run workflow
4. Actions: approve (a), edit (e), reject (r)
5. Approved events → `data/events.json` → appear on map
6. Approved events backed up to `backups/events/`

### Static Generation
1. HTML is generated by `src/modules/site_generator.py`
2. Generate: `python3 src/event_manager.py generate`
3. Fast event update: `python3 src/event_manager.py update` (no full rebuild)
4. Output: `public/index.html` (single-file HTML with everything inlined)
5. Data files live directly in `public/` (events.json, config files, etc.)

**Environment Detection:** The `generate` command automatically adapts based on where it runs 
(development vs CI/production). No need for separate production/development flags.

## Documenting Legacy and Deprecated Commands

When commands become obsolete or are replaced, follow these guidelines for documentation:

### In-Code Documentation (Primary Method)

Use **docstrings** to mark deprecated commands directly in `src/event_manager.py`:

```python
def cli_old_command(base_path, config):
    """
    [DEPRECATED] Old command description.
    
    **Status:** Deprecated as of v2.0.0 (January 2025)
    **Replacement:** Use `python3 src/event_manager.py new-command` instead
    **Reason:** The new command provides the same functionality with automatic environment detection
    
    This command is maintained for backward compatibility but may be removed in future versions.
    """
    print("⚠️  WARNING: This command is deprecated. Use 'new-command' instead.")
    # Implementation...
```

### CLI Help Text

Mark deprecated commands in the help output with clear warnings:

```python
def print_help():
    help_text = """
    COMMANDS:
        new-command              The current, recommended command
        old-command              [DEPRECATED] Use new-command instead
    """
```

### Documentation Files

In copilot-instructions.md and README files:
- ✅ **DO**: Remove references to truly phantom commands (commands that never existed in code)
- ✅ **DO**: Document deprecated commands with clear replacement instructions
- ✅ **DO**: Use consistent markers: `[DEPRECATED]`, `[LEGACY]`, `[REMOVED]`
- ❌ **DON'T**: Label current, working commands as "legacy"
- ❌ **DON'T**: Keep documentation for non-existent commands

### Example: Documenting a Real Deprecation

```markdown
### Generate Commands
- `python3 src/event_manager.py generate` - Generate static site (current)
- ~~`python3 src/event_manager.py build`~~ - [REMOVED in v2.0.0] Use `generate` instead

**Migration Note:** The `build production` and `build development` commands were referenced 
in older documentation but never implemented. Use `generate` with automatic environment detection.
```

### KISS Principle for Deprecations

- **Document once** in the command's docstring (single source of truth)
- **Extract to help** programmatically from docstrings
- **Remove completely** when no longer needed (don't accumulate dead references)
- **Communicate clearly** why the change was made and what to use instead

## Security Considerations

- **No secrets in code**: Use environment variables or config files (gitignored)
- **Input validation**: Always sanitize user input and scraped data
- **XSS protection**: Escape HTML when displaying user-generated content
- **HTTPS**: Production must use HTTPS (enforced by GitHub Pages)

## Common Tasks

### Add a new event source
1. Edit `config.json` in root directory
2. Add to `scraping.sources[]` array
3. Specify `type` (rss, html, api) and `url`
4. Test: `python3 src/event_manager.py scrape`

### Generate the application
1. Generate static site: `python3 src/event_manager.py generate`
2. Fast event update: `python3 src/event_manager.py update`
3. Fast weather update: `python3 src/event_manager.py update-weather`

### Add a new filter
1. Edit `assets/js/app.js` (filter logic)
2. Edit `assets/css/style.css` (filter UI styles)
3. Rebuild: `python3 src/event_manager.py generate`
4. Test: `python3 src/event_manager.py test filters --verbose`

### Update documentation
1. Run: `python3 scripts/generate_readme.py` to regenerate README.md
2. Commit generated `README.md`

## Accessibility (A11y)

- **WCAG 2.1 Level AA** compliance required
- **Keyboard navigation**: All interactive elements must be keyboard accessible
- **ARIA labels**: Use for dynamic content and complex widgets
- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus indicators**: Visible focus styles required
- **Screen readers**: Test with NVDA (Windows) or VoiceOver (Mac/iOS)

### WCAG AA Compliance Linter

The project includes automated WCAG 2.1 Level AA compliance checking during the build process:

**How it works:**
1. Linter runs automatically during `python3 src/event_manager.py generate`
2. Warnings are displayed in the debug section of the dashboard menu (when debug mode is enabled)
3. Warnings are **non-blocking** - build continues even with warnings
4. Full lint protocol is saved to `public/lint_protocol.txt` for detailed review
5. Warnings are clickable in the UI to show full context and remediation guidance

**What is checked:**
- Missing `lang` attribute on `<html>` tag (WCAG 3.1.1)
- Images without `alt` attributes (WCAG 1.1.1)
- Links without text content (WCAG 2.4.4)
- Form inputs without proper labels (WCAG 3.3.2)
- Heading hierarchy issues (WCAG 1.3.1)
- Missing ARIA attributes
- Missing skip navigation links (WCAG 2.4.1)

**Viewing lint warnings:**
1. Enable debug mode (automatic in local development)
2. Open the dashboard menu (click logo)
3. Scroll to "WCAG AA Compliance" section
4. Click on individual warnings to expand full protocol details
5. For full report: view `public/lint_protocol.txt`

**Files involved:**
- `src/modules/linter.py` - Linting logic and WCAG checks
- `src/modules/site_generator.py` - Runs linter during build
- `assets/js/dashboard-ui.js` - Displays warnings in UI
- `assets/css/style.css` - Styles for clickable warning items
- `public/lint_protocol.txt` - Full lint report (auto-generated)

## Performance

- **Page load**: Target < 3 seconds
- **Time to Interactive**: Target < 5 seconds
- **First Contentful Paint**: Target < 1.5 seconds
- **JavaScript bundle**: Keep minimal (vanilla JS helps)
- **Images**: Optimize, use SVG where possible
- **Caching**: Production uses aggressive caching via `config.prod.json`

## Git Workflow

### Commit Messages
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, etc.
- Keep first line under 72 characters
- Add body for complex changes

### Branch Naming
- Feature: `feature/description`
- Fix: `fix/description`
- Copilot: `copilot/description` (auto-generated by Copilot)

### Pull Requests
- Target `main` branch
- Provide clear description
- Link related issues
- Ensure CI passes

## Questions or Issues?

- Check `README.md` for comprehensive guide
- Check `features.json` for feature registry documentation
- Run CLI commands with `--help` for detailed usage information

## Remember

1. **Test before committing** - Run relevant test suite
2. **Don't edit auto-generated files** - Edit source CSS/JS files instead
3. **Follow KISS principles** - Keep it simple
4. **Document features** - Update `features.json`
5. **Validate schemas** - Run `python3 test_event_schema.py`
6. **Check accessibility** - Test keyboard navigation and screen readers

## CLI Commands Reference

All commands are run through `src/event_manager.py`:

### Site Generation Commands
- `python3 src/event_manager.py generate` - Generate static site HTML (auto-detects environment)
- `python3 src/event_manager.py update` - Fast event update (no full rebuild)
- `python3 src/event_manager.py update-weather` - Fast weather update (no full rebuild)
- `python3 src/event_manager.py dependencies fetch` - Download CDN libraries (Leaflet.js, fonts)
- `python3 src/event_manager.py dependencies check` - Verify libraries are installed

**Environment Auto-Detection:** All commands automatically adapt to development vs production 
based on environment variables. No manual mode switching needed.

### Event Management
- `python3 src/event_manager.py scrape` - Scrape events from sources
- `python3 src/event_manager.py scrape-weather` - Scrape weather data
- `python3 src/event_manager.py list` - List published events
- `python3 src/event_manager.py list-pending` - List pending events
- `python3 src/event_manager.py publish EVENT_ID` - Approve a pending event
- `python3 src/event_manager.py reject EVENT_ID` - Reject a pending event
- `python3 src/event_manager.py bulk-publish "pending_*"` - Bulk approve (supports wildcards)
- `python3 src/event_manager.py bulk-reject "pending_*"` - Bulk reject (supports wildcards)

### Utility
- `python3 src/event_manager.py` - Interactive TUI
- `python3 src/event_manager.py --help` - Show all commands
- `python3 src/event_manager.py generate` - Generate static site
