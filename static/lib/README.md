# Third-Party Libraries

This directory contains local copies of third-party JavaScript libraries used by the application.

## Leaflet

The map functionality uses Leaflet.js. To install it locally:

```bash
# From the static/lib directory
mkdir -p leaflet/images
cd leaflet

# Download Leaflet 1.9.4 files
curl -O https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
curl -O https://unpkg.com/leaflet@1.9.4/dist/leaflet.js

# Download marker images
cd images
curl -O https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png
curl -O https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png
curl -O https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png
```

Alternatively, use the provided download script:

```bash
# From the repository root
./download-libs.sh
```

## Why Local Hosting?

1. **Better Performance**: No external CDN delays
2. **Offline Support**: Required for PWA functionality
3. **Reliability**: No dependency on external services
4. **Privacy**: No third-party requests
5. **Security**: Control over exact library versions
