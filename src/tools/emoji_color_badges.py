#!/usr/bin/env python3
"""
Simple Color Emoji Badge Generator - KISS Approach

Converts hex colors to appropriate emoji indicators.
Super simple: 🟣 #D689B8

Usage:
    python3 src/tools/emoji_color_badges.py
"""

import re
from pathlib import Path


def get_color_emoji(hex_color):
    """
    Get appropriate square emoji for a hex color using KISS logic.
    Uses colored square emojis (🟥🟦🟩🟨🟪🟧🟫⬛⬜).
    
    Args:
        hex_color: Hex color code (e.g., '#D689B8')
    
    Returns:
        Square emoji character representing the color
    """
    color = hex_color.upper().lstrip('#')
    
    # Parse RGB
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Very light or very dark - use basic geometric squares
    if luminance > 0.95:
        return '⬜'  # White square
    elif luminance < 0.08:
        return '⬛'  # Black square
    
    # Pink/Purple detection (all ecoBarbie colors)
    if r > b and b > g:
        return '🟪'  # Purple square (closest to pink)
    
    if abs(r - b) < 30 and r > g and b > g:
        return '🟪'  # Purple square
    
    # For other color families
    if r > g and r > b:
        if r > 200:
            return '🟥' if g < 100 else '🟧'
        else:
            return '🟫'
    elif g > r and g > b:
        return '🟩'
    elif b > r and b > g:
        return '🟦'
    else:
        return '⬛' if luminance < 0.5 else '⬜'


def replace_with_emoji_badges(content: str) -> str:
    """
    Replace SVG data URI badges with simple emoji badges.
    
    Args:
        content: Markdown content
    
    Returns:
        Updated content with emoji badges
    """
    # Pattern: ![ALT](data:image/svg+xml,...fill%3D%22%23HEXCODE%22...)
    pattern = r'!\[[^\]]*\]\(data:image/svg[^)]*fill%3D%22%23([A-Fa-f0-9]{6})%22[^)]*\)'
    
    def replacer(match):
        hex_color = match.group(1)
        emoji = get_color_emoji(f"#{hex_color}")
        return f"{emoji} `#{hex_color}`"
    
    return re.sub(pattern, replacer, content)


def process_markdown_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a markdown file to replace SVG badges with emoji.
    
    Args:
        file_path: Path to markdown file
        dry_run: If True, only show changes without writing
    
    Returns:
        True if file was modified
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Replace badges
    new_content = replace_with_emoji_badges(original_content)
    
    # Check if modified
    if original_content == new_content:
        print("   ℹ️  No SVG badges found to replace")
        return False
    
    # Count replacements
    original_count = original_content.count('data:image/svg')
    new_count = new_content.count('data:image/svg')
    replaced = original_count - new_count
    
    print(f"   ✓ Replaced {replaced} SVG badge(s) with emoji")
    
    if dry_run:
        print("   🔍 DRY RUN - No changes written")
        # Show first few examples
        lines = new_content.split('\n')
        emoji_lines = [l for l in lines if '🟣' in l or '💗' in l or '🩷' in l or '💜' in l][:5]
        if emoji_lines:
            print("\n   Preview:")
            for line in emoji_lines:
                print(f"      {line.strip()}")
        return False
    
    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("   ✓ File updated")
    return True


def main():
    """Main function"""
    print("=" * 60)
    print("🎨 Simple Emoji Color Badges - KISS Approach")
    print("=" * 60)
    
    # Get base path (project root)
    base_path = Path(__file__).parent.parent.parent
    print(f"\nProject root: {base_path}")
    
    # Find markdown files
    markdown_files = [
        base_path / 'COLOR_PALETTE.md',
    ]
    
    # Filter to existing files
    existing_files = [f for f in markdown_files if f.exists()]
    
    if not existing_files:
        print("\n⚠️  No markdown files found")
        return 1
    
    print(f"\nFound {len(existing_files)} file(s) to process:")
    for f in existing_files:
        print(f"  • {f.relative_to(base_path)}")
    
    # Process files
    print("\n" + "=" * 60)
    print("Processing files...")
    print("=" * 60)
    
    modified_count = 0
    for file_path in existing_files:
        if process_markdown_file(file_path):
            modified_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Complete: {modified_count}/{len(existing_files)} file(s) modified")
    print("=" * 60)
    
    # Show examples
    print("\n💡 KISS Emoji Examples:")
    examples = [
        '#D689B8',  # Primary pink
        '#e07fba',  # Accent
        '#eb7dc0',  # Warning
        '#954476',  # Error (dark)
        '#eac0da',  # Tint (light)
        '#6b445c',  # Shade (dark)
        '#ffffff',  # White
        '#000000',  # Black
    ]
    
    for color in examples:
        emoji = get_color_emoji(color)
        print(f"   {emoji} {color}")
    
    print("\n   ✓ Super simple!")
    print("   ✓ No external dependencies")
    print("   ✓ Works everywhere")
    print("   ✓ Human-readable")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
