#!/bin/bash
# Demonstration script for CDN Asset Version Tracking
# Shows the complete workflow for managing CDN assets

echo "=========================================="
echo "CDN Asset Version Tracking Demo"
echo "=========================================="
echo ""

echo "1. Check if dependencies are present locally"
echo "   Command: python3 src/event_manager.py dependencies check"
echo ""
python3 src/event_manager.py dependencies check
echo ""

echo "2. Show version information for tracked assets"
echo "   Command: python3 src/event_manager.py dependencies info"
echo ""
python3 src/event_manager.py dependencies info
echo ""

echo "3. Check for upstream updates"
echo "   Command: python3 src/event_manager.py dependencies update-check"
echo ""
python3 src/event_manager.py dependencies update-check
echo ""

echo "4. View versions.json file"
echo "   Location: lib/versions.json"
echo ""
if [ -f "lib/versions.json" ]; then
    echo "versions.json contents (first 30 lines):"
    head -30 lib/versions.json
else
    echo "versions.json not found (run 'dependencies fetch' first)"
fi
echo ""

echo "=========================================="
echo "Demo Complete!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  dependencies fetch        - Fetch dependencies from CDN"
echo "  dependencies check        - Check if dependencies present"
echo "  dependencies update-check - Check for upstream updates"
echo "  dependencies update       - Update to latest versions"
echo "  dependencies info         - Show version information"
echo ""
