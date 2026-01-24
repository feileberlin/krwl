#!/bin/bash
# Regenerate public/index.html locally
# This file is gitignored and generated fresh on each CI run

set -e  # Exit on error

echo "🔨 Regenerating public/index.html..."
echo ""

# Check if we're in the project root
if [ ! -f "src/event_manager.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Install dependencies if needed (skip in CI environments with no network)
echo "📦 Checking Python dependencies..."
if ! python3 -c "import requests, bs4, lxml" 2>/dev/null; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt || {
        echo "⚠️  Warning: Failed to install some dependencies"
        echo "   Continuing anyway (CI environment may have network restrictions)"
    }
fi

# Fetch frontend libraries (Leaflet.js, etc.) - may fail in CI
echo "📥 Fetching frontend libraries..."
python3 src/event_manager.py dependencies fetch || {
    echo "⚠️  Warning: Failed to fetch some dependencies from CDN"
    echo "   HTML will use CDN fallbacks at runtime"
}

# Generate the HTML
echo "🏗️  Generating HTML..."
python3 src/event_manager.py generate || {
    echo "❌ Error: Failed to generate HTML"
    exit 1
}

# Verify it was created
if [ -f "public/index.html" ]; then
    SIZE=$(du -h public/index.html | cut -f1)
    echo ""
    echo "✅ Success! public/index.html generated ($SIZE)"
    echo ""
    echo "💡 This file is gitignored and will NOT be committed to git."
    echo "💡 CI will regenerate it automatically on each run."
    echo ""
    echo "🚀 To view locally, run:"
    echo "   cd public && python3 -m http.server 8000"
else
    echo ""
    echo "❌ Error: public/index.html was not generated"
    exit 1
fi
