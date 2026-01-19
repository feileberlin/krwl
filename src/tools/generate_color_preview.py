#!/usr/bin/env python3
"""
Generate Color Preview HTML for PR Comments

Extracts CSS variable colors and generates visual preview HTML
for displaying in GitHub PR comments.

KISS Approach:
- Parse design-tokens.css for color variables
- Generate HTML with inline styles (no external deps)
- Output self-contained HTML snippet
"""

import re
import sys
from pathlib import Path


def extract_css_color_variables(css_file_path):
    """
    Extract color CSS variables from design-tokens.css
    
    Returns:
        dict: {variable_name: color_value}
    """
    colors = {}
    
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match patterns like: --color-primary: #D689B8;
        # Only extract actual color variables (not comments/previews)
        pattern = r'--color-([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\));'
        
        matches = re.findall(pattern, content)
        
        for var_name, color_value in matches:
            # Skip comment/preview variables
            if not var_name.startswith('-'):
                colors[f'--color-{var_name}'] = color_value
        
        return colors
    
    except FileNotFoundError:
        print(f"Error: CSS file not found: {css_file_path}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error parsing CSS: {e}", file=sys.stderr)
        return {}


def generate_color_swatch_html(var_name, color_value):
    """
    Generate HTML for a single color swatch
    
    Args:
        var_name: CSS variable name (e.g., --color-primary)
        color_value: Color value (e.g., #D689B8)
    
    Returns:
        str: HTML snippet
    """
    # Clean variable name for display
    display_name = var_name.replace('--color-', '').replace('-', ' ').title()
    
    # Determine if color is light or dark (for text color)
    # Simple heuristic: check if hex value is > #888888
    is_light = False
    if color_value.startswith('#'):
        hex_val = color_value.lstrip('#')
        if len(hex_val) >= 6:
            avg = int(hex_val[:2], 16) + int(hex_val[2:4], 16) + int(hex_val[4:6], 16)
            is_light = avg > (128 * 3)
    
    text_color = '#000' if is_light else '#fff'
    
    html = f'''
    <div style="display: inline-block; margin: 8px; text-align: center; min-width: 150px;">
      <div style="
        background-color: {color_value};
        width: 150px;
        height: 60px;
        border: 1px solid #ddd;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {text_color};
        font-family: monospace;
        font-size: 11px;
        font-weight: bold;
      ">{color_value}</div>
      <div style="
        margin-top: 4px;
        font-size: 11px;
        color: #666;
        font-family: monospace;
      ">{var_name}</div>
      <div style="
        font-size: 10px;
        color: #999;
      ">{display_name}</div>
    </div>
    '''
    
    return html


def generate_color_preview_html(css_file_path, output_file=None):
    """
    Generate complete color preview HTML
    
    Args:
        css_file_path: Path to design-tokens.css
        output_file: Optional output file path (defaults to stdout)
    
    Returns:
        str: Complete HTML
    """
    colors = extract_css_color_variables(css_file_path)
    
    if not colors:
        return "<p>No CSS color variables found.</p>"
    
    # Group colors by category
    categories = {
        'Primary': [],
        'Tints': [],
        'Shades': [],
        'Tones': [],
        'Backgrounds': [],
        'Text': [],
        'Borders': [],
        'Accents': []
    }
    
    for var_name, color_value in sorted(colors.items()):
        var_lower = var_name.lower()
        
        if 'primary' in var_lower and 'bg' not in var_lower and 'text' not in var_lower and 'border' not in var_lower:
            categories['Primary'].append((var_name, color_value))
        elif 'tint' in var_lower:
            categories['Tints'].append((var_name, color_value))
        elif 'shade' in var_lower:
            categories['Shades'].append((var_name, color_value))
        elif 'tone' in var_lower:
            categories['Tones'].append((var_name, color_value))
        elif 'bg' in var_lower or 'background' in var_lower:
            categories['Backgrounds'].append((var_name, color_value))
        elif 'text' in var_lower:
            categories['Text'].append((var_name, color_value))
        elif 'border' in var_lower:
            categories['Borders'].append((var_name, color_value))
        else:
            categories['Accents'].append((var_name, color_value))
    
    html_header = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>CSS Color Variables Preview</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      padding: 20px;
      background: #f5f5f5;
    }}
    .category {{
      background: white;
      padding: 16px;
      margin-bottom: 16px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .category h3 {{
      margin: 0 0 12px 0;
      color: #333;
      font-size: 16px;
      border-bottom: 2px solid #D689B8;
      padding-bottom: 8px;
    }}
    .swatches {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
  </style>
</head>
<body>
  <h2 style="color: #333; margin-top: 0;">🎨 CSS Color Variables Preview</h2>
  <p style="color: #666;">Total colors: <strong>{total}</strong></p>
'''.format(total=len(colors))
    
    html_parts = [html_header]
    
    # Generate swatches by category
    for category, color_list in categories.items():
        if color_list:
            html_parts.append(f'  <div class="category">\n')
            html_parts.append(f'    <h3>{category} ({len(color_list)} colors)</h3>\n')
            html_parts.append(f'    <div class="swatches">\n')
            
            for var_name, color_value in color_list:
                html_parts.append(generate_color_swatch_html(var_name, color_value))
            
            html_parts.append('    </div>\n')
            html_parts.append('  </div>\n')
    
    html_parts.append('''
</body>
</html>
''')
    
    html = ''.join(html_parts)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ Color preview saved to: {output_file}")
        except Exception as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
    
    return html


def generate_markdown_color_preview(css_file_path):
    """
    Generate markdown-formatted color preview for PR comments
    
    Args:
        css_file_path: Path to design-tokens.css
    
    Returns:
        str: Markdown with HTML table
    """
    colors = extract_css_color_variables(css_file_path)
    
    if not colors:
        return "No CSS color variables found."
    
    # Group by category
    categories = {}
    for var_name, color_value in sorted(colors.items()):
        var_lower = var_name.lower()
        
        if 'primary' in var_lower and 'bg' not in var_lower and 'text' not in var_lower and 'border' not in var_lower:
            cat = 'Primary'
        elif 'tint' in var_lower:
            cat = 'Tints'
        elif 'shade' in var_lower:
            cat = 'Shades'
        elif 'tone' in var_lower:
            cat = 'Tones'
        elif 'bg' in var_lower or 'background' in var_lower:
            cat = 'Backgrounds'
        elif 'text' in var_lower:
            cat = 'Text'
        elif 'border' in var_lower:
            cat = 'Borders'
        else:
            cat = 'Accents'
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((var_name, color_value))
    
    md_parts = [f"## 🎨 CSS Color Variables ({len(colors)} colors)\n\n"]
    
    for category, color_list in categories.items():
        if color_list:
            md_parts.append(f"### {category}\n\n")
            md_parts.append("| Variable | Color | Preview |\n")
            md_parts.append("|----------|-------|----------|\n")
            
            for var_name, color_value in color_list:
                # Create inline color swatch using Unicode block character
                swatch = f'<span style="display:inline-block;width:20px;height:20px;background:{color_value};border:1px solid #ccc;vertical-align:middle;"></span>'
                md_parts.append(f"| `{var_name}` | `{color_value}` | {swatch} |\n")
            
            md_parts.append("\n")
    
    return ''.join(md_parts)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CSS color variable preview')
    parser.add_argument('css_file', nargs='?', 
                       default='assets/html/design-tokens.css',
                       help='Path to design-tokens.css (default: assets/html/design-tokens.css)')
    parser.add_argument('-o', '--output', 
                       help='Output HTML file path')
    parser.add_argument('-m', '--markdown', action='store_true',
                       help='Output markdown format for PR comments')
    
    args = parser.parse_args()
    
    # Resolve path
    css_path = Path(args.css_file)
    if not css_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent.parent.parent
        css_path = script_dir / args.css_file
    
    if not css_path.exists():
        print(f"Error: CSS file not found: {args.css_file}", file=sys.stderr)
        sys.exit(1)
    
    if args.markdown:
        md = generate_markdown_color_preview(str(css_path))
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"✓ Markdown preview saved to: {args.output}")
        else:
            print(md)
    else:
        html = generate_color_preview_html(str(css_path), args.output)
        if not args.output:
            print(html)


if __name__ == '__main__':
    main()
