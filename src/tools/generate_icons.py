#!/usr/bin/env python3
"""
Icon Generation Tool - SVG Icon Resizer

Generates multiple icon sizes from a source SVG file for PWA and browser use.
Uses only Python standard library (no external dependencies like Pillow or Cairo).

This script reads the source SVG favicon and generates optimized versions
at different sizes with proportionally adjusted stroke-widths for optimal
rendering at small sizes.

Usage:
    python3 src/tools/generate_icons.py [--source PATH] [--output-dir PATH]
    
Examples:
    # Generate all icons with defaults
    python3 src/tools/generate_icons.py
    
    # Specify custom source SVG
    python3 src/tools/generate_icons.py --source assets/svg/custom-logo.svg
    
    # Specify custom output directory
    python3 src/tools/generate_icons.py --output-dir public/icons
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Tuple


class IconGenerator:
    """
    Generate multiple icon sizes from a source SVG file.
    
    This class handles reading a source SVG, adjusting its viewBox and dimensions,
    and adjusting stroke-width proportionally for smaller sizes to ensure
    the icon remains visible and crisp.
    """
    
    # Target icon sizes to generate
    ICON_SIZES = {
        'favicon-16x16.svg': {
            'size': 16,
            'description': 'Browser tab favicon (standard)',
            'stroke_scale': 0.6  # Thinner strokes for tiny size
        },
        'favicon-32x32.svg': {
            'size': 32,
            'description': 'Browser tab favicon (retina)',
            'stroke_scale': 1.0  # Original stroke width
        },
        'icon-192x192.svg': {
            'size': 192,
            'description': 'PWA icon for Android',
            'stroke_scale': 1.0  # Keep original
        },
        'icon-512x512.svg': {
            'size': 512,
            'description': 'PWA icon for iOS and splash screens',
            'stroke_scale': 1.0  # Keep original
        }
    }
    
    def __init__(self, source_path: Path, output_dir: Path):
        """
        Initialize icon generator.
        
        Args:
            source_path: Path to source SVG file
            output_dir: Directory where generated icons will be saved
        """
        self.source_path = source_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def read_source_svg(self) -> str:
        """
        Read source SVG file content.
        
        Returns:
            SVG content as string
            
        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source SVG not found: {self.source_path}")
        
        return self.source_path.read_text(encoding='utf-8')
    
    def extract_viewbox(self, svg_content: str) -> Tuple[float, float, float, float]:
        """
        Extract viewBox coordinates from SVG.
        
        Args:
            svg_content: SVG content as string
            
        Returns:
            Tuple of (min_x, min_y, width, height) from viewBox
            
        Raises:
            ValueError: If viewBox not found or invalid
        """
        viewbox_match = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', svg_content)
        if not viewbox_match:
            raise ValueError("No viewBox found in source SVG")
        
        viewbox_str = viewbox_match.group(1)
        try:
            coords = [float(x.strip()) for x in viewbox_str.split()]
            if len(coords) != 4:
                raise ValueError(f"Invalid viewBox format: expected 4 values, got {len(coords)}")
            return tuple(coords)  # type: ignore
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Failed to parse viewBox '{viewbox_str}': {e}")
    
    def adjust_stroke_width(self, svg_content: str, scale_factor: float) -> str:
        """
        Adjust all stroke-width values in SVG by a scale factor.
        
        For smaller icons, we reduce stroke width to maintain visual clarity.
        For larger icons, we keep the original stroke width.
        
        Args:
            svg_content: SVG content as string
            scale_factor: Multiplier for stroke-width (e.g., 0.6 for 60% of original)
            
        Returns:
            Modified SVG content with adjusted stroke widths
        """
        def replace_stroke_width(match):
            """Replace stroke-width value with scaled version"""
            original_width = float(match.group(1))
            new_width = original_width * scale_factor
            # Round to 1 decimal place for cleaner output
            return f'stroke-width:{new_width:.1f}'
        
        # Match stroke-width in style attributes or as standalone attributes
        # Pattern matches: stroke-width:1.8 or stroke-width="1.8"
        # Supports negative values and scientific notation
        pattern = r'stroke-width[:\s]*[=]?\s*["\']?(-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)["\']?'
        
        modified_svg = re.sub(pattern, replace_stroke_width, svg_content, flags=re.IGNORECASE)
        return modified_svg
    
    def generate_icon(self, svg_content: str, filename: str, config: Dict) -> str:
        """
        Generate a single icon at specified size.
        
        Args:
            svg_content: Source SVG content
            filename: Output filename
            config: Icon configuration with 'size', 'description', 'stroke_scale'
            
        Returns:
            Modified SVG content for the target size
        """
        size = config['size']
        stroke_scale = config['stroke_scale']
        
        # Adjust stroke width if needed
        modified_svg = self.adjust_stroke_width(svg_content, stroke_scale)
        
        # Update width and height attributes in <svg> tag
        # Match: <svg ... width="32" height="32" ...>
        modified_svg = re.sub(
            r'width\s*=\s*["\']?\d+["\']?',
            f'width="{size}"',
            modified_svg,
            count=1
        )
        modified_svg = re.sub(
            r'height\s*=\s*["\']?\d+["\']?',
            f'height="{size}"',
            modified_svg,
            count=1
        )
        
        # Update viewBox to match if the original viewBox matches the original size
        # This ensures the icon scales properly
        try:
            viewbox = self.extract_viewbox(svg_content)
            # If viewBox matches original dimensions (0 0 32 32), update it
            if viewbox[2] == viewbox[3]:  # Square viewBox
                original_size = viewbox[2]
                # Keep viewBox as is - it defines the coordinate system
                # The width/height attributes control the rendered size
                pass
        except ValueError:
            # If we can't parse viewBox, skip this step
            pass
        
        return modified_svg
    
    def generate_all_icons(self) -> Dict[str, bool]:
        """
        Generate all icon sizes from source SVG.
        
        Returns:
            Dictionary mapping filename to success status
        """
        print(f"Generating icons from {self.source_path}...")
        print()
        
        # Read source SVG
        try:
            source_svg = self.read_source_svg()
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return {}
        except Exception as e:
            print(f"❌ Failed to read source SVG: {e}")
            return {}
        
        results = {}
        
        # Generate each icon size
        for filename, config in self.ICON_SIZES.items():
            try:
                # Generate icon content
                icon_svg = self.generate_icon(source_svg, filename, config)
                
                # Write to file
                output_path = self.output_dir / filename
                output_path.write_text(icon_svg, encoding='utf-8')
                
                print(f"✓ Generated {output_path} ({config['description']})")
                results[filename] = True
                
            except Exception as e:
                print(f"❌ Failed to generate {filename}: {e}")
                results[filename] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """
        Print summary of generation results.
        
        Args:
            results: Dictionary mapping filename to success status
        """
        print()
        print("-" * 60)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"✓ All {total_count} icons generated successfully!")
        else:
            print(f"⚠ Generated {success_count}/{total_count} icons")
            print("  Some icons failed to generate - see errors above")
        
        print()
        print("Generated icons:")
        for filename, config in self.ICON_SIZES.items():
            status = "✓" if results.get(filename, False) else "✗"
            print(f"  {status} {filename} - {config['description']}")
        
        print()
        print("Next steps:")
        print("  1. Verify icons in assets/svg/ directory")
        print("  2. Test icons in browser and PWA")
        print("  3. Update manifest.json if needed")
        print("  4. Rebuild site: python3 src/event_manager.py generate")


def main():
    """Main entry point for icon generation script"""
    parser = argparse.ArgumentParser(
        description='Generate PWA and browser icons from source SVG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all icons with defaults
  python3 src/tools/generate_icons.py
  
  # Specify custom source SVG
  python3 src/tools/generate_icons.py --source assets/svg/custom-logo.svg
  
  # Specify custom output directory
  python3 src/tools/generate_icons.py --output-dir public/icons

Generated sizes:
  - favicon-16x16.svg    (Browser tab, standard)
  - favicon-32x32.svg    (Browser tab, retina)
  - icon-192x192.svg     (PWA icon, Android)
  - icon-512x512.svg     (PWA icon, iOS, splash screens)
        """
    )
    
    parser.add_argument(
        '--source',
        type=Path,
        default=Path('assets/svg/favicon.svg'),
        help='Path to source SVG file (default: assets/svg/favicon.svg)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('assets/svg'),
        help='Output directory for generated icons (default: assets/svg)'
    )
    
    args = parser.parse_args()
    
    # Create generator and run
    generator = IconGenerator(args.source, args.output_dir)
    results = generator.generate_all_icons()
    generator.print_summary(results)
    
    # Exit with error code if any icons failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == '__main__':
    main()
