#!/usr/bin/env python3
"""
Optimize Markers - Keep Only Markers Used by Current Events

This script analyzes the actual events in the deployment and keeps only
the marker files that correspond to categories actually in use.

KISS Approach:
1. Scan events.json and events.antarctica.json for categories
2. Look up which markers those categories use (from config.json)
3. Delete unused marker files
4. Keep essential markers (default, geolocation)

Usage:
    python3 scripts/optimize_markers.py [--dry-run]
    
Options:
    --dry-run    Show what would be deleted without actually deleting
"""

import json
import os
import sys
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
MARKER_DIR = BASE_DIR / 'assets' / 'svg'
CONFIG_FILE = BASE_DIR / 'config.json'
EVENT_FILES = [
    BASE_DIR / 'assets' / 'json' / 'events.json',
    BASE_DIR / 'assets' / 'json' / 'events.antarctica.json',
    BASE_DIR / 'assets' / 'json' / 'pending_events.json'
]

# Always keep these markers regardless of event categories
ESSENTIAL_MARKERS = {
    'marker-lucide-default',      # Fallback for unknown categories
    'marker-lucide-geolocation'   # Used for user location
}


def load_config():
    """Load configuration from config.json."""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_categories_from_events():
    """Scan all event files and extract unique categories."""
    categories = set()
    
    for filepath in EVENT_FILES:
        if not filepath.exists():
            continue
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Handle both list format and {"events": [...]} format
                events = data if isinstance(data, list) else data.get('events', [])
                
                for event in events:
                    if 'category' in event and event['category']:
                        categories.add(event['category'])
                        
        except Exception as e:
            print(f"⚠️  Warning: Could not read {filepath.name}: {e}")
    
    return categories


def get_markers_for_categories(config, categories):
    """Determine which markers are needed for the given categories."""
    needed_markers = set(ESSENTIAL_MARKERS)
    
    category_mapping = config.get('categories', {}).get('mapping', {})
    
    for category in categories:
        if category in category_mapping:
            marker = category_mapping[category].get('marker')
            if marker:
                needed_markers.add(marker)
        else:
            print(f"⚠️  Warning: Category '{category}' not in config.json, will use default marker")
    
    return needed_markers


def get_all_marker_files():
    """Get all marker SVG files currently in the directory."""
    markers = {}
    
    for filepath in MARKER_DIR.glob('marker-*.svg'):
        marker_name = filepath.stem  # e.g., 'marker-music'
        markers[marker_name] = filepath
    
    return markers


def optimize_markers(dry_run=False):
    """Main function to optimize marker files."""
    print("=" * 60)
    print("🎯 Marker Optimization Tool")
    print("=" * 60)
    print()
    
    # Step 1: Load config
    print("📋 Loading configuration...")
    config = load_config()
    
    # Step 2: Scan events for categories
    print("🔍 Scanning events for categories...")
    categories = get_categories_from_events()
    
    if not categories:
        print("⚠️  No categories found in events!")
        print("   Will keep only essential markers (default, geolocation)")
    else:
        print(f"✓ Found {len(categories)} unique categories:")
        for cat in sorted(categories):
            print(f"    - {cat}")
    
    print()
    
    # Step 3: Determine needed markers
    print("🎨 Determining required markers...")
    needed_markers = get_markers_for_categories(config, categories)
    print(f"✓ Need {len(needed_markers)} markers:")
    for marker in sorted(needed_markers):
        print(f"    - {marker}")
    
    print()
    
    # Step 4: Find all current marker files
    print("📂 Scanning marker directory...")
    all_markers = get_all_marker_files()
    print(f"✓ Found {len(all_markers)} marker files")
    
    print()
    
    # Step 5: Identify markers to delete
    markers_to_delete = []
    for marker_name in all_markers:
        if marker_name not in needed_markers:
            markers_to_delete.append(marker_name)
    
    if not markers_to_delete:
        print("✅ All markers are needed! Nothing to delete.")
        return
    
    print(f"🗑️  Markers to delete ({len(markers_to_delete)}):")
    for marker in sorted(markers_to_delete):
        print(f"    - {marker}")
    
    print()
    
    # Step 6: Delete or show dry-run
    if dry_run:
        print("🔍 DRY RUN - No files were deleted")
        print(f"   Would delete {len(markers_to_delete)} markers")
        print(f"   Would keep {len(needed_markers)} markers")
    else:
        print("🗑️  Deleting unused markers...")
        deleted_count = 0
        for marker_name in markers_to_delete:
            filepath = all_markers[marker_name]
            try:
                filepath.unlink()
                deleted_count += 1
                print(f"    ✓ Deleted {marker_name}.svg")
            except Exception as e:
                print(f"    ✗ Failed to delete {marker_name}.svg: {e}")
        
        print()
        print(f"✅ Deleted {deleted_count} unused markers")
        print(f"✅ Kept {len(needed_markers)} needed markers")
    
    print()
    print("=" * 60)
    print("✨ Optimization complete!")
    print("=" * 60)


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    optimize_markers(dry_run)
