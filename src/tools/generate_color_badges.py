#!/usr/bin/env python3
"""
Color Badge Generator for Markdown

Generates self-contained color badges for markdown documentation
without external dependencies (no shields.io URLs).

Uses inline SVG with data URIs for maximum compatibility.

Usage:
    python3 src/tools/generate_color_badges.py
"""

import json
import re
from pathlib import Path
from typing import Dict
from urllib.parse import quote


def create_inline_svg_badge(hex_color: str, width: int = 80, height: int = 20) -> str:
    """
    Create an inline SVG badge as a data URI.
    
    Args:
        hex_color: Hex color code (e.g., '#D689B8' or 'D689B8')
        width: Badge width in pixels
        height: Badge height in pixels
    
    Returns:
        Data URI for inline SVG badge
    """
    # Remove '#' if present
    color = hex_color.lstrip('#')
    
    # Create SVG
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="{width}" height="{height}" fill="#{color}"/></svg>'
    
    # URL encode for data URI
    encoded_svg = quote(svg)
    
    return f"data:image/svg+xml,{encoded_svg}"


def create_html_kbd_badge(hex_color: str) -> str:
    """
    Create HTML kbd element with background color.
    
    Args:
        hex_color: Hex color code
    
    Returns:
        HTML kbd element
    """
    # Determine text color (white or black) based on background lightness
    color_without_hash = hex_color.lstrip('#')
    r = int(color_without_hash[0:2], 16)
    g = int(color_without_hash[2:4], 16)
    b = int(color_without_hash[4:6], 16)
    
    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    text_color = 'black' if luminance > 0.5 else 'white'
    
    return f'<kbd style="background-color: {hex_color}; color: {text_color}; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">{hex_color}</kbd>'


def create_html_pre_badge(hex_color: str, description: str = None) -> str:
    """
    Create HTML pre block with background color.
    
    Args:
        hex_color: Hex color code
        description: Optional description text
    
    Returns:
        HTML pre element
    """
    color_without_hash = hex_color.lstrip('#')
    r = int(color_without_hash[0:2], 16)
    g = int(color_without_hash[2:4], 16)
    b = int(color_without_hash[4:6], 16)
    
    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    text_color = 'black' if luminance > 0.5 else 'white'
    
    text = f"<b>{hex_color}</b>"
    if description:
        text += f" - {description}"
    
    return f'<pre style="background-color: {hex_color}; color: {text_color}; padding: 10px; border-radius: 5px; border: 2px solid #999;">{text}</pre>'


def create_markdown_badge(hex_color: str, alt_text: str = None, style: str = 'svg') -> str:
    """
    Create markdown badge for color preview.
    
    Args:
        hex_color: Hex color code
        alt_text: Alt text for image (defaults to hex color)
        style: Badge style - 'svg', 'kbd', or 'pre'
    
    Returns:
        Markdown/HTML badge
    """
    if alt_text is None:
        alt_text = hex_color
    
    if style == 'kbd':
        return create_html_kbd_badge(hex_color)
    elif style == 'pre':
        return create_html_pre_badge(hex_color, alt_text)
    else:  # default to 'svg'
        data_uri = create_inline_svg_badge(hex_color)
        return f"![{alt_text}]({data_uri})"


def replace_shields_badges(content: str) -> str:
    """
    Replace shields.io badge URLs with inline SVG data URIs.
    
    Args:
        content: Markdown content
    
    Returns:
        Updated content with inline badges
    """
    # Pattern: ![#HEXCODE](https://img.shields.io/badge/%20-%20-HEXCODE?style=flat-square)
    pattern = r'!\[([^\]]+)\]\(https://img\.shields\.io/badge/%20-%20-([A-Fa-f0-9]{6})\?[^\)]*\)'
    
    def replacer(match):
        alt_text = match.group(1)
        hex_color = match.group(2)
        return create_markdown_badge(f"#{hex_color}", alt_text)
    
    return re.sub(pattern, replacer, content)


def process_markdown_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a markdown file to replace external badges.
    
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
    new_content = replace_shields_badges(original_content)
    
    # Check if modified
    if original_content == new_content:
        print("   ℹ️  No changes needed")
        return False
    
    # Count replacements
    original_count = original_content.count('img.shields.io')
    new_count = new_content.count('img.shields.io')
    replaced = original_count - new_count
    
    print(f"   ✓ Replaced {replaced} external badge(s) with inline SVG")
    
    if dry_run:
        print("   🔍 DRY RUN - No changes written")
        return False
    
    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("   ✓ File updated")
    return True


def main():
    """Main function"""
    print("=" * 60)
    print("🎨 Color Badge Generator - Self-Contained Badges")
    print("=" * 60)
    
    # Get base path (project root)
    base_path = Path(__file__).parent.parent.parent
    print(f"\nProject root: {base_path}")
    
    # Find markdown files with color references
    markdown_files = [
        base_path / 'COLOR_PALETTE.md',
        base_path / 'docs' / 'ECOLOGICAL_BARBIE_COLORS.md',
    ]
    
    # Filter to existing files
    existing_files = [f for f in markdown_files if f.exists()]
    
    if not existing_files:
        print("\n⚠️  No markdown files found with color badges")
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
    
    # Show example
    print("\n💡 Example inline badge:")
    example_color = "#D689B8"
    example_badge = create_markdown_badge(example_color)
    print(f"   {example_badge}")
    print(f"\n   Renders as: A self-contained {example_color} color swatch")
    print("   ✓ No external dependencies")
    print("   ✓ Works in all markdown renderers")
    print("   ✓ Embeds directly in documentation")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
