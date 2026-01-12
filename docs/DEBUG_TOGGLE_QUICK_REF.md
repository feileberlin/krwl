# Debug Comments Toggle - Quick Reference

## TL;DR - 3 Ways to Control Debug Comments (KISS)

### 1. 🎯 Environment Variable (GitHub Actions)
```bash
# Force enable
DEBUG_COMMENTS=true python3 src/event_manager.py generate

# Force disable  
DEBUG_COMMENTS=false python3 src/event_manager.py generate
```

### 2. ⚙️ Config File (Local Override)
Edit `config.json`:
```json
{
  "debug_comments": {
    "force_enabled": true
  }
}
```

### 3. 🤖 Auto-Detection (Default)
```bash
# Just run normally - auto-detects environment
python3 src/event_manager.py generate
# Development: debug ON
# Production/CI: debug OFF
```

---

## Priority Order

1. **Environment Variable** (`DEBUG_COMMENTS`) - overrides everything
2. **Config File** (`debug_comments.force_enabled`) - overrides auto-detection
3. **Auto-Detection** - development=on, production/ci=off

---

## GitHub Actions Usage

### Manual Trigger with Debug
1. Go to Actions → "Auto-Generate HTML on Merge"
2. Click "Run workflow"
3. Select **force_debug_comments: true**
4. HTML generated with debug comments!

### In Workflow YAML
```yaml
- name: Generate HTML with debug
  env:
    DEBUG_COMMENTS: true
  run: python3 src/event_manager.py generate
```

---

## Common Scenarios

### Troubleshoot Production Issues
```bash
# Force debug in production-like environment
DEBUG_COMMENTS=true python3 src/event_manager.py generate
```

### Test Production Output Locally
```bash
# Force disable debug in development
DEBUG_COMMENTS=false python3 src/event_manager.py generate
```

### Permanent Local Override
```json
// config.json
{
  "debug_comments": {
    "force_enabled": true  // Always enable locally
  }
}
```

### CI Troubleshooting
```yaml
# .github/workflows/troubleshoot.yml
- name: Generate HTML with debug for troubleshooting
  env:
    DEBUG_COMMENTS: true  # Override CI default
  run: python3 src/event_manager.py generate
```

---

## Verification

### Check if Debug Enabled
```bash
# Count debug comments in HTML
grep -c "EMBEDDED RESOURCE DEBUG INFO" public/index.html

# Show sample debug comment
grep -A 5 "EMBEDDED RESOURCE DEBUG INFO" public/index.html | head -20

# Show HTML component markers
grep "START COMPONENT\|END COMPONENT" public/index.html
```

### Test Detection
```python
import sys
from pathlib import Path
sys.path.insert(0, 'src')
from modules.site_generator import SiteGenerator

gen = SiteGenerator(Path('.'))
print(f'Debug comments enabled: {gen.enable_debug_comments}')
```

---

## What Gets Debug Comments?

When enabled, debug metadata is added to:
- ✅ CSS (Roboto fonts, Leaflet CSS, app styles)
- ✅ JavaScript (Leaflet, i18n, app modules, Lucide icons)
- ✅ JSON (events, translations, config, markers)
- ✅ HTML components (boundary markers with file paths)

**File size impact:** ~5-10 KB overhead (only when enabled)

---

## Related Documentation

- **Full guide:** [docs/DEBUGGING_GUIDE.md](./DEBUGGING_GUIDE.md)
- **Examples:** [docs/DEBUG_COMMENTS_EXAMPLES.md](./DEBUG_COMMENTS_EXAMPLES.md)
- **Config:** [config.json](../config.json) → `debug_comments` section

---

## Summary

**Default:** Auto-detects environment (no config needed)
**Override:** Set `DEBUG_COMMENTS=true` environment variable
**GitHub Actions:** Use workflow dispatch input or set env var
**KISS:** One toggle, three ways to set it, works everywhere!
