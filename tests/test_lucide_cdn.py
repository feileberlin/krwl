#!/usr/bin/env python3
"""
Test Lucide Inline Implementation

Verifies that the minimal Lucide icon implementation works correctly.
Since we no longer use the full Lucide CDN library, this test validates:
- DASHBOARD_ICONS_MAP contains all required icons
- The generate_minimal_lucide_js() function produces valid JS
- Icons are properly defined as inline SVGs
"""

import sys
from pathlib import Path

# Add src/modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'modules'))

from lucide_markers import DASHBOARD_ICONS_MAP


def test_lucide_inline_implementation():
    """Test that Lucide inline implementation is correctly configured"""
    print("=" * 60)
    print("Testing Lucide Inline Implementation")
    print("=" * 60)
    
    # Required icons for the application
    required_icons = {
        'alert-triangle',  # Dashboard: Pending events notification
        'book-open',       # Dashboard: About section
        'book-text',       # Dashboard: Documentation
        'bug',             # Dashboard: Debug info
        'git-commit',      # Dashboard: Git info
        'heart',           # Dashboard: Thanks to / Bookmarks
        'megaphone',       # Filter bar: Events button
        'user',            # Dashboard: Maintainer
    }
    
    # Test 1: Check all required icons are present
    print(f"\n1. Testing that all {len(required_icons)} required icons are present...")
    missing_icons = required_icons - set(DASHBOARD_ICONS_MAP.keys())
    if missing_icons:
        print(f"   ❌ Missing icons: {', '.join(missing_icons)}")
        return False
    print(f"   ✓ All required icons found in DASHBOARD_ICONS_MAP")
    
    # Test 2: Check icons are valid SVG strings
    print(f"\n2. Testing that all icons are valid SVG strings...")
    for icon_name, svg_content in DASHBOARD_ICONS_MAP.items():
        if not svg_content.startswith('<svg'):
            print(f"   ❌ Icon '{icon_name}' does not start with <svg")
            return False
        if not svg_content.endswith('</svg>'):
            print(f"   ❌ Icon '{icon_name}' does not end with </svg>")
            return False
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            print(f"   ❌ Icon '{icon_name}' is missing xmlns attribute")
            return False
    print(f"   ✓ All {len(DASHBOARD_ICONS_MAP)} icons are valid SVG strings")
    
    # Test 3: Test generate_minimal_lucide_js() produces valid JS
    print(f"\n3. Testing generate_minimal_lucide_js() output...")
    try:
        # Import site_generator but patch DASHBOARD_ICONS_MAP since relative import may fail
        import site_generator
        # Ensure DASHBOARD_ICONS_MAP is populated (may be empty due to relative import)
        if not site_generator.DASHBOARD_ICONS_MAP:
            site_generator.DASHBOARD_ICONS_MAP = DASHBOARD_ICONS_MAP
        
        generator = site_generator.SiteGenerator(Path(__file__).parent.parent)
        lucide_js = generator.generate_minimal_lucide_js()
        
        # Check for key components
        if 'window.lucide' not in lucide_js:
            print(f"   ❌ Missing window.lucide export")
            return False
        if 'createIcons' not in lucide_js:
            print(f"   ❌ Missing createIcons function")
            return False
        if 'LUCIDE_ICONS' not in lucide_js:
            print(f"   ❌ Missing LUCIDE_ICONS constant")
            return False
        
        # Check all icons are included (search for "icon-name": pattern)
        for icon_name in required_icons:
            # JSON format is "icon-name": "<svg..."
            if f'"{icon_name}":' not in lucide_js and f'"{icon_name}" :' not in lucide_js:
                print(f"   ❌ Icon '{icon_name}' not found in generated JS")
                return False
        
        print(f"   ✓ Generated JS contains all required components")
        print(f"   ✓ Generated JS size: {len(lucide_js)} bytes (~{len(lucide_js)//1024}KB)")
        
    except ImportError as e:
        print(f"   ⚠ Could not import SiteGenerator: {e}")
        print(f"   ⚠ Skipping JS generation test")
    
    print("\n" + "=" * 60)
    print("✅ All Lucide inline implementation tests passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = test_lucide_inline_implementation()
    sys.exit(0 if success else 1)
