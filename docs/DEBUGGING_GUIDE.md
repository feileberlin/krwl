# Debugging Guide - HTML Generation Debug Comments

## Overview

The KRWL HOF event manager automatically adds debug comments to generated HTML files to help developers understand where embedded resources come from. This feature is **automatically controlled by the environment** - no manual configuration needed!

## How It Works

### Automatic Environment Detection

Debug comments are automatically:
- ✅ **ENABLED** in **development mode** (local development)
- ❌ **DISABLED** in **production/CI mode** (deployed sites)

The system uses the same environment detection as the rest of the application (see `src/modules/utils.py`):
- **Development**: Running locally on developer's machine
- **Production**: Vercel, Netlify, Heroku, Railway, Render, Fly.io, Google Cloud Run, AWS, or explicit `ENVIRONMENT=production`
- **CI**: GitHub Actions, GitLab CI, Travis CI, CircleCI, Jenkins, etc.

### What Gets Debug Comments?

When debug comments are enabled, you'll see detailed metadata for:

1. **CSS Resources**
   - Roboto fonts (base64-encoded WOFF2 files)
   - Leaflet CSS (map library styles)
   - Application CSS (`assets/css/style.css`)

2. **JavaScript Resources**
   - Leaflet JS (map library)
   - i18n JS (internationalization system)
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

### Enable Debug Comments (Development Mode)

Simply run the generation locally on your development machine:

```bash
# On your local machine (NOT in CI)
python3 src/event_manager.py generate
```

The system will auto-detect development environment and enable debug comments.

### Disable Debug Comments (Production Mode)

Debug comments are automatically disabled when:

1. **Deploying to hosting platforms** (Vercel, Netlify, etc.)
   - Just deploy normally - comments disabled automatically

2. **Running in CI/CD pipelines**
   - GitHub Actions, GitLab CI, etc. auto-disable comments

3. **Forcing production mode locally**
   ```bash
   # Set environment variable to force production mode
   export ENVIRONMENT=production
   python3 src/event_manager.py generate
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
