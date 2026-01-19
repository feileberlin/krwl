#!/usr/bin/env python3
"""
Scientific Monochromatic Barbie Color Palette Generator

Generates a scientifically-accurate monochromatic palette from Barbie Pink base color.
Removes duplicates and ensures minimum visual distinction between colors.

Base Color: #D689B8 (ecoBarbie Pink)
HSV: 323.4° hue, 36.0% saturation, 83.9% value
"""

import colorsys
from typing import List, Tuple, Dict


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert RGB to HSV."""
    r, g, b = [x / 255.0 for x in rgb]
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_rgb(hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
    """Convert HSV to RGB."""
    r, g, b = colorsys.hsv_to_rgb(*hsv)
    return (int(r * 255), int(g * 255), int(b * 255))


def calculate_color_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate perceptual color distance using weighted Euclidean distance.
    Takes into account human perception (more sensitive to green).
    """
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    
    # Weighted Euclidean distance (perceptual)
    return ((2 * (r1 - r2) ** 2) + 
            (4 * (g1 - g2) ** 2) + 
            (3 * (b1 - b2) ** 2)) ** 0.5


def is_sufficiently_distinct(new_rgb: Tuple[int, int, int], 
                             existing_colors: List[Tuple[int, int, int]], 
                             min_distance: float = 30.0) -> bool:
    """Check if a color is sufficiently distinct from existing colors."""
    for existing_rgb in existing_colors:
        if calculate_color_distance(new_rgb, existing_rgb) < min_distance:
            return False
    return True


def generate_monochromatic_palette(base_hex: str = "#D689B8", 
                                   min_distance: float = 30.0) -> Dict:
    """
    Generate a scientifically-accurate monochromatic palette.
    
    Args:
        base_hex: Base color in hex format
        min_distance: Minimum perceptual distance between colors
    
    Returns:
        Dictionary with categorized colors
    """
    base_rgb = hex_to_rgb(base_hex)
    h, s, v = rgb_to_hsv(base_rgb)
    
    print(f"Base Color: {base_hex}")
    print(f"HSV: H={h*360:.1f}°, S={s*100:.1f}%, V={v*100:.1f}%")
    print(f"RGB: {base_rgb}")
    print(f"\nGenerating monochromatic palette with min distance: {min_distance}")
    print("=" * 70)
    
    palette = {
        'base': [],
        'tints': [],
        'shades': [],
        'tones': [],
        'special': []
    }
    
    unique_colors = []
    
    # Base color
    palette['base'].append({
        'name': 'Primary (Base)',
        'hex': base_hex,
        'rgb': base_rgb,
        'transform': 'Base 0%',
        'category': 'Core'
    })
    unique_colors.append(base_rgb)
    
    # Generate TINTS (add white - increase value, decrease saturation)
    print("\nGenerating TINTS (Base + White)...")
    tint_steps = [0.25, 0.5, 0.75, 1.0]  # 25%, 50%, 75%, 100%
    for i, step in enumerate(tint_steps):
        new_v = v + (1.0 - v) * step  # Increase value towards 1.0
        new_s = s * (1.0 - step * 0.8)  # Decrease saturation
        new_rgb = hsv_to_rgb((h, new_s, new_v))
        
        if is_sufficiently_distinct(new_rgb, unique_colors, min_distance):
            palette['tints'].append({
                'name': f'Tint {int(step * 100)}%',
                'hex': rgb_to_hex(new_rgb),
                'rgb': new_rgb,
                'transform': f'+{int(step * 100)}% white',
                'category': 'Tint'
            })
            unique_colors.append(new_rgb)
            print(f"  ✓ Tint {int(step * 100)}%: {rgb_to_hex(new_rgb)}")
        else:
            print(f"  ✗ Tint {int(step * 100)}%: Too similar, skipped")
    
    # Generate SHADES (add black - decrease value)
    print("\nGenerating SHADES (Base + Black)...")
    shade_steps = [0.25, 0.5, 0.75, 1.0]  # 25%, 50%, 75%, 100%
    for i, step in enumerate(shade_steps):
        new_v = v * (1.0 - step)  # Decrease value towards 0
        new_rgb = hsv_to_rgb((h, s, new_v))
        
        if is_sufficiently_distinct(new_rgb, unique_colors, min_distance):
            palette['shades'].append({
                'name': f'Shade {int(step * 100)}%',
                'hex': rgb_to_hex(new_rgb),
                'rgb': new_rgb,
                'transform': f'+{int(step * 100)}% black',
                'category': 'Shade'
            })
            unique_colors.append(new_rgb)
            print(f"  ✓ Shade {int(step * 100)}%: {rgb_to_hex(new_rgb)}")
        else:
            print(f"  ✗ Shade {int(step * 100)}%: Too similar, skipped")
    
    # Generate TONES (add grey - decrease saturation)
    print("\nGenerating TONES (Base + Grey)...")
    tone_steps = [0.25, 0.5, 0.75, 1.0]  # 25%, 50%, 75%, 100%
    for i, step in enumerate(tone_steps):
        new_s = s * (1.0 - step)  # Decrease saturation towards 0
        new_rgb = hsv_to_rgb((h, new_s, v))
        
        if is_sufficiently_distinct(new_rgb, unique_colors, min_distance):
            palette['tones'].append({
                'name': f'Tone {int(step * 100)}%',
                'hex': rgb_to_hex(new_rgb),
                'rgb': new_rgb,
                'transform': f'{int(step * 100)}% desaturated',
                'category': 'Tone'
            })
            unique_colors.append(new_rgb)
            print(f"  ✓ Tone {int(step * 100)}%: {rgb_to_hex(new_rgb)}")
        else:
            print(f"  ✗ Tone {int(step * 100)}%: Too similar, skipped")
    
    # Generate SPECIAL colors (saturation/value variations)
    print("\nGenerating SPECIAL variations...")
    special_variations = [
        (s + 0.1, v + 0.05, "Accent (+10% sat, +5% val)"),
        (s + 0.2, v + 0.1, "Warning (+20% sat, +10% val)"),
        (min(s + 0.3, 1.0), v - 0.2, "Error (+30% sat, -20% val)"),
    ]
    
    for new_s, new_v, desc in special_variations:
        new_s = min(max(new_s, 0), 1.0)  # Clamp 0-1
        new_v = min(max(new_v, 0), 1.0)  # Clamp 0-1
        new_rgb = hsv_to_rgb((h, new_s, new_v))
        
        if is_sufficiently_distinct(new_rgb, unique_colors, min_distance):
            palette['special'].append({
                'name': desc.split(' (')[0],
                'hex': rgb_to_hex(new_rgb),
                'rgb': new_rgb,
                'transform': desc.split('(')[1].rstrip(')'),
                'category': 'Special'
            })
            unique_colors.append(new_rgb)
            print(f"  ✓ {desc}: {rgb_to_hex(new_rgb)}")
        else:
            print(f"  ✗ {desc}: Too similar, skipped")
    
    return palette, unique_colors


def print_palette_table(palette: Dict):
    """Print the palette as a markdown table."""
    print("\n" + "=" * 70)
    print("SCIENTIFIC MONOCHROMATIC BARBIE COLOR PALETTE")
    print("=" * 70)
    print("\n## Complete Palette - No Duplicates, Visually Distinct\n")
    print("| Badge | Name | Hex | RGB | Transform | Category |")
    print("|-------|------|-----|-----|-----------|----------|")
    
    for category_name, colors in palette.items():
        if not colors:
            continue
        
        if category_name == 'base':
            section_name = "PRIMARY (BASE)"
        else:
            section_name = category_name.upper()
        
        print(f"| **{section_name}** | | | | | |")
        
        for color in colors:
            rgb_str = f"{color['rgb'][0]}, {color['rgb'][1]}, {color['rgb'][2]}"
            badge = '🟪'
            
            # Determine badge based on luminance
            r, g, b = color['rgb']
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            if luminance > 0.95:
                badge = '⬜'
            elif luminance < 0.08:
                badge = '⬛'
            
            print(f"| {badge} | **{color['name']}** | `{color['hex']}` | {rgb_str} | {color['transform']} | {color['category']} |")


def main():
    """Main execution."""
    # Generate palette with minimum distance of 30
    palette, unique_colors = generate_monochromatic_palette("#D689B8", min_distance=30.0)
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = sum(len(colors) for colors in palette.values())
    print(f"Total unique colors: {total}")
    print(f"Base colors: {len(palette['base'])}")
    print(f"Tints: {len(palette['tints'])}")
    print(f"Shades: {len(palette['shades'])}")
    print(f"Tones: {len(palette['tones'])}")
    print(f"Special: {len(palette['special'])}")
    
    # Print markdown table
    print_palette_table(palette)
    
    print("\n" + "=" * 70)
    print("✓ Palette generated successfully!")
    print("✓ All colors are visually distinct (min distance: 30)")
    print("✓ 100% monochromatic (all from base #D689B8)")
    print("=" * 70)


if __name__ == '__main__':
    main()
