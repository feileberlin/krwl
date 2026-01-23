#!/usr/bin/env python3
"""
Extract icons from marker SVGs and create icon-only versions (no gyro shape).

SIMPLE APPROACH (KISS):
1. Read all marker-*.svg files
2. Remove the standard gyro-shaped pin outline
3. Scale up the remaining content by 6.25x (200x200px)
4. Save back to assets/svg/ directory

Usage: python3 scripts/extract_icon_only_markers.py
"""

import os
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
MARKER_DIR = BASE_DIR / 'assets' / 'svg'
SCALE_FACTOR = 6.25  # 6.25x larger (200/32)
ORIGINAL_SIZE = (32, 48)  # Original marker size
NEW_SIZE = (200, 200)  # Square icon, 6.25x scale of 32px width
COLOR = "#D689B8"  # ecoBarbie color

def remove_gyro_outline(svg_content):
    """Remove the gyro-shaped pin outline from marker SVG."""
    # Remove the standard gyro shape path
    # Pattern: <path d="M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z".../>
    svg_content = re.sub(
        r'<path d="M16 2\s+C9 2 3 8 3 15\s+C3 24 16 46 16 46\s+C16 46 29 24 29 15\s+C29 8 23 2 16 2\s+Z"[^>]*/>',
        '',
        svg_content,
        flags=re.DOTALL
    )
    
    # Also remove any "STANDARD GYRO SHAPE" comment
    svg_content = re.sub(r'<!--\s*STANDARD GYRO SHAPE.*?-->', '', svg_content, flags=re.DOTALL)
    
    return svg_content

def scale_svg_3x(svg_content):
    """Scale SVG from 32x48 to 200x200 (6.25x) and center the icon."""
    
    # Remove gyro outline first
    svg_content = remove_gyro_outline(svg_content)
    
    # Update viewBox and dimensions
    # Match both original 32x48 and current 96x96 formats
    svg_content = re.sub(
        r'viewBox="0 0 (?:32 48|96 96)"',
        f'viewBox="0 0 {NEW_SIZE[0]} {NEW_SIZE[1]}"',
        svg_content
    )
    
    svg_content = re.sub(
        r'width="(?:32|96)"',
        f'width="{NEW_SIZE[0]}"',
        svg_content
    )
    
    svg_content = re.sub(
        r'height="(?:48|96)"',
        f'height="{NEW_SIZE[1]}"',
        svg_content
    )
    
    # Scale and center the icon content
    # Original content was centered around (16, ~15-20) in 32x48 viewBox
    # Current viewBox may be 96x96 (center at 48, 48) or 32x48
    # New viewBox is 200x200, so center is at (100, 100)
    # Scale factor is 6.25x, so we need to scale and translate
    
    # Find the content after drop shadow and before </svg>
    # Extract the innermost Lucide icon content, ignoring previous scaling wrappers
    # Pattern matches: <!-- Lucide icon --> ... up to the last </g> before </svg>
    match = re.search(r'<!-- Lucide icon.*?-->(.*?)(?:</g>\s*){1,}</svg>', svg_content, re.DOTALL)
    
    if match:
        icon_content = match.group(1).strip()
        
        # No drop shadow - per user requirement
        
        # Wrap icon content in a scaled and centered group
        # Offset to center: original (16, 15) -> new (100, 100)
        # We scale by 6.25, so translate by (100 - 16*6.25, 100 - 15*6.25) = (0, 6.25)
        centered_content = f'''
  <!-- Icon content scaled 6.25x and centered -->
  <g transform="translate({NEW_SIZE[0]/2 - 16*SCALE_FACTOR}, {NEW_SIZE[1]/2 - 15*SCALE_FACTOR}) scale({SCALE_FACTOR})">
<!-- Lucide icon (scaled and positioned) -->{icon_content}
  </g>'''
        
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {NEW_SIZE[0]} {NEW_SIZE[1]}" width="{NEW_SIZE[0]}" height="{NEW_SIZE[1]}">
  <!-- Icon-only marker (no gyro outline) - 6.25x larger -->
{centered_content}
</svg>'''
    
    return svg_content

def process_markers():
    """Process all marker SVG files."""
    
    marker_files = sorted(MARKER_DIR.glob('marker-*.svg'))
    
    if not marker_files:
        print(f"❌ No marker-*.svg files found in {MARKER_DIR}")
        return
    
    print(f"🔍 Found {len(marker_files)} marker files")
    print(f"📂 Input directory: {MARKER_DIR}")
    print(f"📏 Output size: {NEW_SIZE[0]}x{NEW_SIZE[1]}px (6.25x scale)")
    print()
    
    processed = 0
    
    for marker_file in marker_files:
        try:
            # Read original marker SVG
            with open(marker_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Scale to 3x and remove gyro outline
            scaled_svg = scale_svg_3x(svg_content)
            
            # Save back to same location (overwrite)
            with open(marker_file, 'w', encoding='utf-8') as f:
                f.write(scaled_svg)
            
            processed += 1
            print(f"✅ {marker_file.name}")
        
        except Exception as e:
            print(f"❌ Error processing {marker_file.name}: {e}")
    
    print()
    print(f"✨ Processed {processed} markers")
    print()
    print("🎯 Next steps:")
    print("   1. Verify marker size (200x200px)")
    print("   2. Regenerate site: python3 src/event_manager.py generate")

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Icon-Only Marker Generator")
    print("=" * 60)
    print()
    
    process_markers()
