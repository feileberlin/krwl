# Preview Deployment Solution Summary

## Problem
The original question: "why does the Deploy Preview Environment workflow do artifacts?"

The evolved requirements:
1. Preview deployment was using GitHub Pages artifacts (complex)
2. Production showed 404 when preview was enabled (conflict)
3. Need everything in one file - no deployment at all
4. Get rid of "deployment" terminology - it's just generation

## Solution: Self-Contained Single HTML File (NO DEPLOYMENT)

Instead of deploying anywhere, we generate a **single, self-contained HTML file** (`preview/index.html`) that:

- **Inlines everything**: All CSS, JavaScript, configuration, and event data
- **No external dependencies**: Works completely offline
- **~260KB file size**: Reasonable for a complete app with 27+ events
- **KISS compliant**: Generation script is only 101 lines
- **No deployment needed**: Just download and open the file

### How It Works

```
┌─────────────────────────────────────────────────────┐
│ 1. Push to preview branch                          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 2. GitHub Action (generate-preview.yml) runs:      │
│    - Download Leaflet library                      │
│    - Generate fresh demo events                    │
│    - Run scripts/generate_preview.py               │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 3. Script generates preview/index.html by:         │
│    - Loading config.preview.json                   │
│    - Merging events.json + events.demo.json        │
│    - Loading translations (content.json/de)        │
│    - Inlining Leaflet CSS/JS                       │
│    - Inlining app CSS/JS (style.css + app.js)     │
│    - Embedding all data as window.EMBEDDED_*       │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 4. Commit preview/index.html back to preview       │
│    branch (with [skip ci] to avoid infinite loop)  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 5. NO DEPLOYMENT! Just download and open the file  │
│    Or optionally merge to main for /preview/ path  │
└─────────────────────────────────────────────────────┘
```

### Production Unaffected

```
main branch (production)              preview branch
    │                                      │
    ├── static/                            ├── static/
    │   ├── index.html (production)        │   └── ... (same)
    │   ├── css/                           │
    │   ├── js/                            ├── preview/
    │   └── ...                            │   ├── index.html ← self-contained
    │                                      │   └── README.md
    └── CNAME (krwl.in)                    │
                                           └── ... (same)

GitHub Pages deploys from: main branch
  → Root: static/ directory (production)
  → /preview/: preview/index.html (when merged to main)
```

### Viewing the Preview

**Option 1: Download and test locally**
```bash
# Download preview/index.html from preview branch
# Open in browser - works completely offline!
```

**Option 2: Merge to main**
```bash
# Merge preview → main
# Now accessible at: https://krwl.in/preview/
# Production at https://krwl.in/ continues working
```

**Option 3: Raw GitHub**
```
https://raw.githubusercontent.com/feileberlin/krwl-hof/preview/preview/index.html
```

## Benefits

### ✅ Simplicity (KISS)
- No GitHub Pages artifacts
- No complex deployment workflows
- Just one HTML file to commit
- 101-line generation script

### ✅ No Production Impact
- Preview is just a file in a branch
- Production deployment unchanged
- Both can coexist on main branch
- No 404 errors

### ✅ Self-Contained
- Works offline
- No network requests after load
- Easy to test locally
- Easy to share

### ✅ Efficient
- Single 260KB file vs multiple files + requests
- All resources inlined
- No CDN dependencies at runtime
- Fast initial load

## Files Changed

1. **scripts/generate_preview.py** - New 101-line script (KISS compliant)
2. **.github/workflows/deploy-preview.yml** - Simplified to just generate + commit
3. **preview/index.html** - Generated self-contained HTML (260KB)
4. **preview/README.md** - Documentation for preview usage
5. **.github/DEPLOYMENT.md** - Updated deployment guide

## Technical Details

### Embedded Data Structure
```javascript
window.EMBEDDED_CONFIG = {...};      // config.preview.json
window.EMBEDDED_EVENTS = [...];       // events.json + events.demo.json
window.EMBEDDED_CONTENT_EN = {...};   // content.json
window.EMBEDDED_CONTENT_DE = {...};   // content.de.json
```

### Fetch Interception
```javascript
// Override fetch to use embedded data
window.fetch = function(url, options) {
  if (url.includes('config.json'))
    return Promise.resolve({ok: true, json: () => Promise.resolve(window.EMBEDDED_CONFIG)});
  if (url.includes('events.json'))
    return Promise.resolve({ok: true, json: () => Promise.resolve({events: window.EMBEDDED_EVENTS})});
  // ... similar for translations
  return originalFetch.apply(this, arguments);
};
```

## Why This Is Better Than Artifacts

| Aspect | Old (Artifacts) | New (Single File) |
|--------|----------------|-------------------|
| Deployment | GitHub Pages action | Git commit |
| Files | Multiple (static/*) | One (preview/index.html) |
| Size | ~70KB HTML + assets | ~260KB total |
| Requests | Many | One |
| Offline | No | Yes |
| Conflicts | Can break production | Never affects production |
| Complexity | High (artifacts, deployment) | Low (just generate + commit) |
| Testing | Need deployment | Download and open |

## Conclusion

By switching from GitHub Pages artifacts to a self-contained HTML file, we:
- **Eliminated deployment complexity** (no more artifacts)
- **Protected production** (no more 404 errors)
- **Followed KISS principles** (101-line script, simple workflow)
- **Made testing easier** (download and open locally)
- **Reduced network overhead** (one file vs many requests)

The preview is now just a file that lives in the preview branch and can be optionally merged to main when needed.
