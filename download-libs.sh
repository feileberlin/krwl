#!/bin/bash
# Download third-party libraries for local hosting
# This ensures the app works offline and improves performance

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/static/lib"

echo "📦 Downloading third-party libraries..."

# Create directories
mkdir -p "$LIB_DIR/leaflet/images"

# Download Leaflet 1.9.4
echo "📍 Downloading Leaflet 1.9.4..."
curl -sL https://unpkg.com/leaflet@1.9.4/dist/leaflet.css -o "$LIB_DIR/leaflet/leaflet.css"
curl -sL https://unpkg.com/leaflet@1.9.4/dist/leaflet.js -o "$LIB_DIR/leaflet/leaflet.js"

# Download Leaflet marker images
echo "🖼️  Downloading Leaflet marker images..."
curl -sL https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png -o "$LIB_DIR/leaflet/images/marker-icon.png"
curl -sL https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png -o "$LIB_DIR/leaflet/images/marker-icon-2x.png"
curl -sL https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png -o "$LIB_DIR/leaflet/images/marker-shadow.png"

echo "✅ All libraries downloaded successfully!"
echo ""
echo "Files downloaded:"
ls -lh "$LIB_DIR/leaflet/"
ls -lh "$LIB_DIR/leaflet/images/"
