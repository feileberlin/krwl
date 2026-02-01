#!/usr/bin/env python3
"""
Lucide Icons Generator for KRWL>
====================================

Automatically generates src/modules/lucide_markers.py by scanning the codebase
for icon usage in JavaScript and HTML files.

This ensures the DASHBOARD_ICONS_MAP stays in sync with actual usage,
preventing missing icon warnings in the browser console.

Usage:
    python3 scripts/generate_lucide_icons.py
    
The script will:
1. Scan assets/js/*.js and assets/html/*.html for data-lucide attributes
2. Resolve SVG paths for each unique icon using the embedded LUCIDE_SVG_MAP (offline, no CDN fetch)
3. Generate src/modules/lucide_markers.py with the icon map
4. Report statistics on icons found and generated

Run this script:
- Before deployment to ensure all icons are available
- When adding new UI features that use Lucide icons
- As part of CI/CD pipeline (automated in GitHub Actions)
"""

import re
import sys
from pathlib import Path
from typing import Set

# ============================================================================
# EMBEDDED LUCIDE ICON SVG PATHS
# ============================================================================
# Sourced from Lucide v0.263.1 (https://lucide.dev)
# MIT Licensed - https://github.com/lucide-icons/lucide/blob/main/LICENSE

LUCIDE_SVG_MAP = {
    'heart': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
    'map-pin': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    'footprints': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z"/><path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z"/></svg>',
    'map': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/></svg>',
    'check': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    'edit-2': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>',
    'edit-3': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
    'trash-2': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>',
    'rotate-ccw': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>',
    'activity': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'alert-triangle': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
    'book-open': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    'book-text': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M8 7h6"/><path d="M8 11h8"/></svg>',
    'bug': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m8 2 1.88 1.88"/><path d="M14.12 3.88 16 2"/><path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1"/><path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6"/><path d="M12 20v-9"/><path d="M6.53 9C4.6 8.8 3 7.1 3 5"/><path d="M6 13H2"/><path d="M3 21c0-2.1 1.7-3.9 3.8-4"/><path d="M20.97 5c0 2.1-1.6 3.8-3.5 4"/><path d="M22 13h-4"/><path d="M17.2 17c2.1.1 3.8 1.9 3.8 4"/></svg>',
    'git-commit': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><line x1="3" x2="9" y1="12" y2="12"/><line x1="15" x2="21" y1="12" y2="12"/></svg>',
    'megaphone': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>',
    'message-circle': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>',
    'package': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    'send': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
    'shield-alert': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>',
    'upload': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
    'upload-cloud': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>',
    'user': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
}


def find_icon_usage(base_path: Path) -> Set[str]:
    """
    Scan JavaScript and HTML files for data-lucide attribute usage.
    
    Returns:
        Set of unique icon names found in the codebase
    """
    icons = set()
    
    # Patterns to match data-lucide attributes
    patterns = [
        r'data-lucide=["\']([^"\']+)["\']',  # Standard usage
        r'setAttribute\(["\']data-lucide["\']\s*,\s*["\']([^"\']+)["\']',  # setAttribute
        r'<i\s+data-lucide=["\']([^"\']+)["\']',  # Template strings with <i> tags
    ]
    
    # Scan JavaScript files
    js_path = base_path / 'assets' / 'js'
    if js_path.exists():
        for js_file in js_path.glob('*.js'):
            content = js_file.read_text(encoding='utf-8')
            for pattern in patterns:
                matches = re.findall(pattern, content)
                icons.update(matches)
            ternary_matches = re.findall(r"[?:]\s*['\"]([a-z][a-z0-9-]{2,})['\"]", content)
            for match in ternary_matches:
                # Only add if it looks like a Lucide icon name (hyphenated)
                if '-' in match and len(match) > 3:
                    icons.add(match)
    
    # Scan HTML template files
    html_path = base_path / 'assets' / 'html'
    if html_path.exists():
        for html_file in html_path.glob('*.html'):
            content = html_file.read_text(encoding='utf-8')
            for pattern in patterns:
                matches = re.findall(pattern, content)
                icons.update(matches)
    
    # Remove dynamic placeholders (e.g., ${iconType})
    icons = {icon for icon in icons if not icon.startswith('$') and not '{' in icon}
    
    return icons


def generate_lucide_markers_module(icons: Set[str], output_path: Path, 
                                   regenerate_maps: str = 'all') -> None:
    """
    Generate src/modules/lucide_markers.py with icon maps.
    
    Args:
        icons: Set of icon names to include
        output_path: Path to output lucide_markers.py file
        regenerate_maps: Which maps to regenerate ('all', 'marker', 'map', 'dashboard', or 'map,dashboard')
    """
    # Parse which maps to regenerate
    maps_to_regenerate = set(regenerate_maps.split(',')) if regenerate_maps != 'all' else {'marker', 'map', 'dashboard'}
    
    # Load existing file if doing partial regeneration
    existing_marker_icons = {}
    existing_map_icons = {}
    existing_dashboard_icons = {}
    
    if regenerate_maps != 'all' and output_path.exists():
        # Load existing icon maps from the file
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract MAP_ICONS_MAP
            map_match = re.search(r'MAP_ICONS_MAP = \{([^}]+)\}', content, re.DOTALL)
            if map_match:
                # Parse the dict entries
                for match in re.finditer(r"'([^']+)':\s*'([^']+)'", map_match.group(1)):
                    existing_map_icons[match.group(1)] = match.group(2).replace('\\"', '"')
            
            # Extract DASHBOARD_ICONS_MAP
            dashboard_match = re.search(r'DASHBOARD_ICONS_MAP = \{([^}]+)\}', content, re.DOTALL)
            if dashboard_match:
                for match in re.finditer(r"'([^']+)':\s*'([^']+)'", dashboard_match.group(1)):
                    existing_dashboard_icons[match.group(1)] = match.group(2).replace('\\"', '"')
            
            # Extract LUCIDE_MARKER_BASE64_MAP (if it has entries in the future)
            marker_match = re.search(r'LUCIDE_MARKER_BASE64_MAP = \{([^}]+)\}', content, re.DOTALL)
            if marker_match:
                for match in re.finditer(r"'([^']+)':\s*'([^']+)'", marker_match.group(1)):
                    existing_marker_icons[match.group(1)] = match.group(2).replace('\\"', '"')
                    
            print(f"📂 Loaded existing icon maps:")
            print(f"   Map icons: {len(existing_map_icons)}")
            print(f"   Dashboard icons: {len(existing_dashboard_icons)}")
            print(f"   Marker icons: {len(existing_marker_icons)}")
        except Exception as e:
            print(f"⚠️  Could not load existing maps: {e}")
            print("   Will regenerate all maps")
            maps_to_regenerate = {'marker', 'map', 'dashboard'}
    
    # Categorize icons into 3 groups
    marker_icons = existing_marker_icons.copy() if 'marker' not in maps_to_regenerate else {}
    map_icons = existing_map_icons.copy() if 'map' not in maps_to_regenerate else {}
    dashboard_icons = existing_dashboard_icons.copy() if 'dashboard' not in maps_to_regenerate else {}
    missing_icons = []
    
    # Icons used on the map/in speech bubbles
    MAP_ICON_NAMES = {
        'heart', 'map-pin', 'footprints', 'map',
        'check', 'edit-2', 'edit-3', 'trash-2', 'rotate-ccw'
    }
    
    # Process icons based on what we're regenerating
    for icon in sorted(icons):
        if icon.startswith('marker-'):
            # Category marker icons
            if 'marker' in maps_to_regenerate:
                if icon in LUCIDE_SVG_MAP:
                    marker_icons[icon] = LUCIDE_SVG_MAP[icon]
                else:
                    missing_icons.append(icon)
        elif icon in MAP_ICON_NAMES:
            # Map UI icons
            if 'map' in maps_to_regenerate:
                if icon in LUCIDE_SVG_MAP:
                    map_icons[icon] = LUCIDE_SVG_MAP[icon]
                else:
                    missing_icons.append(icon)
        else:
            # Dashboard/debug icons
            if 'dashboard' in maps_to_regenerate:
                if icon in LUCIDE_SVG_MAP:
                    dashboard_icons[icon] = LUCIDE_SVG_MAP[icon]
                else:
                    missing_icons.append(icon)
    
    if missing_icons:
        for icon in missing_icons:
            print(f"⚠️  Warning: Icon '{icon}' not found in embedded map")
    
    # Generate Python module content
    regenerated_info = ', '.join(sorted(maps_to_regenerate))
    module_content = f'''"""
Lucide Icons for KRWL>
=========================

This module provides three icon maps organized by usage:

1. LUCIDE_MARKER_BASE64_MAP - Category marker icons (e.g., marker-music, marker-sports)
   Currently empty - category markers use custom SVG designs, not Lucide icons.

2. MAP_ICONS_MAP - Map UI icons used in speech bubbles and map interactions
   Icons: heart (bookmarks), map-pin (location), footprints (distance), edit/trash controls

3. DASHBOARD_ICONS_MAP - Dashboard and debug UI icons
   Icons: activity, alert-triangle, bug, package, etc.

Icons are sourced from Lucide (https://lucide.dev) and are MIT licensed.
This minimal subset includes only the icons actually used in the application
to keep bundle size small (~3KB instead of ~531KB for the full library).

AUTO-GENERATED by src/modules/lucide_generator.py
Regenerated maps: {regenerated_info}
DO NOT EDIT MANUALLY - Run: python3 src/event_manager.py generate-icons [--map MAP_TYPE]
"""

# ============================================================================
# MAP ICONS MAP - Map UI Icons (speech bubbles, map controls)
# ============================================================================

MAP_ICONS_MAP = {{
'''
    
    # Add map icon entries
    for icon_name, svg_content in sorted(map_icons.items()):
        svg_escaped = svg_content.replace('"', '\\"')
        module_content += f'    \'{icon_name}\': \'{svg_escaped}\',\n'
    
    module_content += '''}

# ============================================================================
# DASHBOARD ICONS MAP - Dashboard & Debug UI Icons
# ============================================================================

DASHBOARD_ICONS_MAP = {
'''
    
    # Add dashboard icon entries
    for icon_name, svg_content in sorted(dashboard_icons.items()):
        svg_escaped = svg_content.replace('"', '\\"')
        module_content += f'    \'{icon_name}\': \'{svg_escaped}\',\n'
    
    module_content += '''}

# ============================================================================
# LUCIDE MARKER BASE64 MAP - Category Marker Icons (Base64 encoded)
# ============================================================================
# This map would contain Base64-encoded SVG strings for category markers
# (e.g., music, sports, food categories). Currently empty - category markers
# use custom SVG designs in assets/svg/marker-*.svg, not Lucide icons.
# To add Lucide category markers, run: 
#   python3 src/event_manager.py generate-icons --map marker

LUCIDE_MARKER_BASE64_MAP = {
'''
    
    # Add marker icon entries (if any)
    for icon_name, svg_content in sorted(marker_icons.items()):
        svg_escaped = svg_content.replace('"', '\\"')
        module_content += f'    \'{icon_name}\': \'{svg_escaped}\',\n'
    
    module_content += '''}
'''
    
    # Write to file
    output_path.write_text(module_content, encoding='utf-8')
    
    print(f"\n✅ Generated {output_path}")
    print(f"   Regenerated: {regenerated_info}")
    print(f"   Map icons: {len(map_icons)} (speech bubbles, map UI)")
    print(f"   Dashboard icons: {len(dashboard_icons)} (debug, settings)")
    print(f"   Marker icons: {len(marker_icons)} (category markers)")
    if missing_icons:
        unique_missing = sorted(set(missing_icons))
        print(f"   ⚠️  Missing icons: {len(unique_missing)} - {', '.join(unique_missing)}")
    print(f"   Estimated size: ~{len(module_content) / 1024:.1f} KB")


def generate_icon_map(base_path: Path = None, regenerate_maps: str = 'all') -> bool:
    """
    Generate Lucide icons map from codebase usage.
    
    Args:
        base_path: Optional base path to repository root. If None, auto-detects.
        regenerate_maps: Which maps to regenerate ('all', 'marker', 'map', 'dashboard', or 'map,dashboard')
        
    Returns:
        True if successful, False otherwise
    """
    if base_path is None:
        # Auto-detect repository root
        script_dir = Path(__file__).parent.parent.parent  # Go up from src/modules/
        base_path = script_dir
    
    print(f"🔍 Scanning for Lucide icon usage...")
    print(f"   Base path: {base_path}")
    if regenerate_maps != 'all':
        print(f"   Regenerating: {regenerate_maps} map(s) only")
    
    # Find all icon usage
    icons = find_icon_usage(base_path)
    
    print(f"\n📊 Found {len(icons)} unique icons:")
    for icon in sorted(icons):
        status = "✓" if icon in LUCIDE_SVG_MAP else "✗"
        print(f"   {status} {icon}")
    
    # Generate module
    output_path = base_path / 'src' / 'modules' / 'lucide_markers.py'
    generate_lucide_markers_module(icons, output_path, regenerate_maps=regenerate_maps)
    
    print("\n✨ Done! Icon map generated successfully.")
    return True


def main():
    """Main entry point for CLI usage"""
    try:
        # Get repository root
        script_dir = Path(__file__).parent.parent.parent  # Go up from src/modules/
        base_path = script_dir
        
        success = generate_icon_map(base_path)
        
        if success:
            print("\nNext steps:")
            print("  1. Review the generated file")
            print("  2. Run: python3 src/event_manager.py generate")
            print("  3. Test that all icons appear correctly in the browser")
            return 0
        else:
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
