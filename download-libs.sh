#!/bin/bash
# Download third-party libraries for local hosting
# This ensures the app works offline and improves performance
# 
# This is a simple wrapper around the Python library manager
# For advanced features, use: python3 manage_libs.py --help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Downloading third-party libraries..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is required but not found"
    echo "   Please install Python 3.7 or later"
    exit 1
fi

# Use the Python library manager
cd "$SCRIPT_DIR"
python3 scripts/manage_libs.py download

echo ""
echo "✅ Library download complete!"
echo ""
echo "💡 Tip: Use 'python3 scripts/manage_libs.py list' to see installed libraries"
echo "💡 Tip: Use 'python3 scripts/manage_libs.py verify' to verify installations"
