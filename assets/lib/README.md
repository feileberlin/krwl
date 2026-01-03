# Third-Party Libraries

This directory contains local copies of third-party JavaScript libraries used by the application.

## Quick Start

### Download All Libraries

```bash
# Simple method (from repository root)
./scripts/download-libs.sh

# Or use the Python manager directly
python3 manage_libs.py download
```

## Library Manager

The `manage_libs.py` module provides comprehensive library management:

### Commands

**Download all libraries:**
```bash
python3 manage_libs.py download
```

**Verify all files are present:**
```bash
python3 manage_libs.py verify
```

**List library inventory:**
```bash
python3 manage_libs.py list
```

**Update a library to a new version:**
```bash
python3 manage_libs.py update leaflet 1.9.5
```

**Clean backup files:**
```bash
python3 manage_libs.py clean
```

## Managed Libraries

### Leaflet 1.9.4
Interactive mapping library for web applications.

**Files:**
- `leaflet/leaflet.css` - Leaflet styles
- `leaflet/leaflet.js` - Leaflet JavaScript
- `leaflet/images/marker-icon.png` - Default marker icon
- `leaflet/images/marker-icon-2x.png` - High-DPI marker icon
- `leaflet/images/marker-shadow.png` - Marker shadow

**Source:** https://unpkg.com/leaflet@1.9.4/dist/

### Lucide Icons (latest)
Beautiful, consistent open-source icon library.

**Files:**
- `lucide/lucide.js` - Lucide development version (unminified UMD)
- `lucide/lucide.min.js` - Lucide production version (minified)

**CDN URLs:**
- Development: `https://unpkg.com/lucide@latest/dist/umd/lucide.js`
- Production: `https://unpkg.com/lucide@latest`

**License:** ISC  
**Website:** https://lucide.dev/

## Why Local Hosting?

1. **Better Performance**: No external CDN delays
2. **Offline Support**: Required for PWA functionality
3. **Reliability**: No dependency on external services
4. **Privacy**: No third-party requests
5. **Security**: Control over exact library versions
6. **No Blocking**: Avoid CDN blocking by corporate firewalls or ad blockers

## Adding New Libraries

To add a new library to the management system:

1. Edit `manage_libs.py`
2. Add library configuration to the `LIBRARIES` dictionary:

```python
LIBRARIES = {
    "your-library": {
        "version": "1.0.0",
        "base_url": "https://cdn.example.com/{version}",
        "files": [
            {
                "src": "library.css",
                "dest": "your-library/library.css",
                "type": "css"
            },
            {
                "src": "library.js",
                "dest": "your-library/library.js",
                "type": "js"
            }
        ]
    }
}
```

3. Run `python3 manage_libs.py download` to fetch the library

## Troubleshooting

**Downloads fail:**
- Check internet connection
- Verify CDN URLs are accessible
- Check firewall/proxy settings

**Files missing after download:**
```bash
python3 manage_libs.py verify
python3 manage_libs.py download
```

**Want to update a library:**
```bash
# Check current version
python3 manage_libs.py list

# Update to new version
python3 manage_libs.py update leaflet 1.9.5
```

**Clean up old backups:**
```bash
python3 manage_libs.py clean
```
