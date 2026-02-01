# Debugging Guide - HTML Generation Debug Comments

## Overview

The KRWL> event manager automatically adds debug comments to generated HTML files to help developers understand where embedded resources come from. This feature is **automatically controlled by the environment** with **optional force override** for troubleshooting!

## How It Works

### Automatic Environment Detection with Force Override (KISS)

Debug comments are controlled by a simple 4-level priority system:

1. **🎯 Environment Variable** (highest priority - for GitHub Actions)
   - Set `DEBUG_COMMENTS=true` to force enable
   - Set `DEBUG_COMMENTS=false` to force disable
   
2. **⚙️ Config File Setting** (second priority - explicit debug override)
   - Edit `config.json`: set `"debug_comments": {"force_enabled": true}`
   
3. **🔧 Config Environment Override** (third priority - respects forced environment)
   - Edit `config.json`: set `"environment": "development"`
   - Enables debug comments **even in CI/production environments**
   
4. **🤖 Auto-Detection** (default behavior - fallback)
   - ✅ **Development** (local machine) → Debug comments **ENABLED**
   - ❌ **Production/CI** (deployed/CI) → Debug comments **DISABLED**

**No configuration needed for normal use** - it just works! Use override only when troubleshooting production issues.

### What Gets Debug Comments?

When debug comments are enabled, you'll see detailed metadata for:

1. **CSS Resources**
   - Roboto fonts (base64-encoded WOFF2 files)
   - Leaflet CSS (map library styles)
   - Application CSS (`assets/css/style.css`)

2. **JavaScript Resources**
   - Leaflet JS (map library)
   - Modular app JS (concatenated from `assets/js/*.js`)
   - Lucide Icons library

3. **JSON Data**
   - Runtime configuration (APP_CONFIG)
   - Events data (published + demo events)
   - Translations (English + German)
   - Marker icons (base64 data URLs)
   - Dashboard icons
   - Debug information

4. **HTML Components**
   - Component boundary markers showing source files
   - `html-head.html`, `html-body-open.html`, `html-body-close.html`
   - `map-main.html`, `dashboard-aside.html`, `filter-nav.html`

## Debug Comment Format

### CSS/JS Resources

```css
/*
 * ==============================================================================
 * EMBEDDED RESOURCE DEBUG INFO
 * ==============================================================================
 * generated_at: 2026-01-12T13:25:00.123456
 * source_file: assets/css/style.css
 * size_bytes: 45678
 * size_kb: 44.61
 * type: css
 * description: Main application styles
 * ==============================================================================
 */
/* ... actual CSS content ... */
/* END OF CSS: assets/css/style.css */
```

### JSON Data

```javascript
/*
 * ==============================================================================
 * EMBEDDED RESOURCE DEBUG INFO
 * ==============================================================================
 * generated_at: 2026-01-12T13:25:00.123456
 * source_file: assets/json/events.json + events.demo.json
 * size_bytes: 123456
 * size_kb: 120.56
 * type: json
 * description: Published events data
 * count: 27
 * ==============================================================================
 */
window.__INLINE_EVENTS_DATA__ = { "events": [ /* ... */ ] };
```

### HTML Component Boundaries

```html
<!-- ▼ START COMPONENT: assets/html/map-main.html ▼ -->
<div id="map"></div>
<!-- ▲ END COMPONENT: assets/html/map-main.html ▲ -->
```

## How to Enable/Disable Debug Comments

### Default Behavior (No Configuration)

Simply run the generation locally or in CI:

```bash
# On your local machine (NOT in CI)
python3 src/event_manager.py generate
# → Debug comments AUTO-ENABLED

# In CI/production
python3 src/event_manager.py generate
# → Debug comments AUTO-DISABLED
```

### Force Enable Debug Comments (Override)

**Method 1: Environment Variable (GitHub Actions)**

Set the `DEBUG_COMMENTS` environment variable:

```bash
# Local testing with forced debug
export DEBUG_COMMENTS=true
python3 src/event_manager.py generate

# Or inline
DEBUG_COMMENTS=true python3 src/event_manager.py generate
```

**In GitHub Actions workflow:**

```yaml
- name: Generate HTML with debug comments
  env:
    DEBUG_COMMENTS: true  # Force enable debug comments
  run: |
    python3 src/event_manager.py generate
```

**Or use workflow dispatch input:**

1. Go to Actions → "Auto-Generate HTML on Merge"
2. Click "Run workflow"
3. Select `force_debug_comments: true`
4. HTML will be generated with debug comments in CI!

**Method 2: Config File (Local Override)**

Edit `config.json`:

```json
{
  "debug_comments": {
    "force_enabled": true  // Set to true to force enable
  }
}
```

Then regenerate:

```bash
python3 src/event_manager.py generate
```

### Force Disable Debug Comments

**Method 1: Environment Variable**

```bash
# Force disable even in development
export DEBUG_COMMENTS=false
python3 src/event_manager.py generate
```

**Method 2: Config File**

Leave `force_enabled: false` (default) in `config.json` - auto-detection will disable in production/CI.

### Priority Order (KISS)

The system checks in this order:

1. **Environment variable `DEBUG_COMMENTS`** (if set, overrides everything)
2. **Config file `debug_comments.force_enabled`** (if true, overrides auto-detection)
3. **Auto-detection** (development=on, production/ci=off)

**Example scenarios:**

```bash
# Scenario 1: Force enable in CI (for troubleshooting)
DEBUG_COMMENTS=true python3 src/event_manager.py generate
# → Debug comments ON (even though CI normally disables)

# Scenario 2: Force disable in development (testing production output)
DEBUG_COMMENTS=false python3 src/event_manager.py generate
# → Debug comments OFF (even though development normally enables)

# Scenario 3: Config override
# config.json: "force_enabled": true
python3 src/event_manager.py generate
# → Debug comments ON (regardless of environment)

# Scenario 4: Normal auto-detection (no overrides)
python3 src/event_manager.py generate
# → Development: ON, Production/CI: OFF
```

## Configuration

### In `config.json`

The environment mode is controlled by the top-level `environment` field:

```json
{
  "environment": "auto",   // Options: "auto", "development", "production"
  ...
}
```

**Recommended**: Leave as `"auto"` for automatic detection!

- `"auto"` - Automatically detects environment (default, recommended)
- `"development"` - Forces development mode (debug comments enabled)
- `"production"` - Forces production mode (debug comments disabled)

### In Code (`src/modules/site_generator.py`)

The `SiteGenerator` class automatically detects the environment:

```python
class SiteGenerator:
    def __init__(self, base_path):
        # ... 
        # Auto-detect debug comments based on environment
        from .utils import is_production, is_ci
        self.enable_debug_comments = not is_production() and not is_ci()
```

No manual configuration needed - it just works!

## Benefits of Debug Comments

### For Developers
- **Understand resource origins** - See exactly where each embedded asset comes from
- **Track file sizes** - Monitor size of CSS, JS, and JSON resources
- **Debug template issues** - Know which HTML component contains specific markup
- **Verify generation** - Timestamp shows when HTML was generated

### For Production
- **Smaller file sizes** - No debug overhead in production builds
- **Cleaner code** - Production HTML is streamlined
- **Better performance** - Less data to transfer and parse

## File Size Impact

Debug comments add approximately:
- **~50-100 bytes per resource** (header + footer)
- **~500 bytes for large JSON** (with pretty-printing)
- **~20-30 HTML comments** (component boundaries)

Total overhead in development mode: **~5-10 KB** (negligible for debugging, significant for production)

## Troubleshooting

### Debug comments not appearing locally?

Check your environment detection:

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from modules.utils import is_production, is_ci
print(f'Production: {is_production()}')
print(f'CI: {is_ci()}')
print(f'Debug comments should be: {not is_production() and not is_ci()}')
"
```

### Force development mode

```bash
# Unset any production environment variables
unset ENVIRONMENT
unset NODE_ENV
unset CI
unset VERCEL_ENV
unset NETLIFY

# Generate with debug comments
python3 src/event_manager.py generate
```

### Verify debug comments in generated HTML

```bash
# Check for debug comments
grep -c "EMBEDDED RESOURCE DEBUG INFO" public/index.html

# Should return > 0 in development, 0 in production/CI
```

## Related Documentation

- [Environment Configuration](../config.json) - Main configuration file
- [Component System](../assets/html/README.md) - HTML component documentation
- [KISS Compliance](../KISS_COMPLIANCE_ACHIEVED.md) - Simplicity principles

## Summary

**TL;DR**: Debug comments automatically appear in development mode and disappear in production/CI. No configuration needed - it just works based on where you run the code!

- 🏠 **Local dev** → Debug comments enabled
- 🚀 **Production/CI** → Debug comments disabled
- 🎯 **Simple** → No manual switching required
