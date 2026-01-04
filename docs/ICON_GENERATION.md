# Icon Generation Guide

## Overview

The KRWL HOF project includes a Python-based icon generation tool that creates multiple sizes of icons from a single source SVG file. This ensures consistency across browser tabs, PWA installations, and mobile devices.

## Tool Location

```
src/tools/generate_icons.py
```

## Generated Icon Sizes

The tool generates 4 icon sizes optimized for different use cases:

| File | Size | Description | Stroke Scale |
|------|------|-------------|--------------|
| `favicon-16x16.svg` | 16×16px | Browser tab favicon (standard) | 0.6× (thinner) |
| `favicon-32x32.svg` | 32×32px | Browser tab favicon (retina) | 1.0× (original) |
| `icon-192x192.svg` | 192×192px | PWA icon for Android | 1.0× (original) |
| `icon-512x512.svg` | 512×512px | PWA icon for iOS, splash screens | 1.0× (original) |

### Why Different Stroke Widths?

At very small sizes (16×16px), the standard stroke width can appear too bold and blur details. The tool automatically scales stroke widths proportionally:

- **16×16px**: 60% of original stroke width for crisper rendering
- **32×32px and larger**: 100% original stroke width

## Usage

### Basic Usage

```bash
# Generate all icons from default source
python3 src/tools/generate_icons.py
```

This reads `assets/svg/favicon.svg` and outputs icons to `assets/svg/`.

### Custom Source SVG

```bash
# Use a custom source SVG file
python3 src/tools/generate_icons.py --source assets/svg/custom-logo.svg
```

### Custom Output Directory

```bash
# Specify a custom output directory
python3 src/tools/generate_icons.py --output-dir public/icons
```

### Help

```bash
# View all options
python3 src/tools/generate_icons.py --help
```

## Source SVG Requirements

The source SVG should:

1. **Be square** - Equal width and height for best results
2. **Have a viewBox** - Defines the coordinate system
3. **Use stroke-based graphics** - Fills are preserved, but strokes are optimized
4. **Be self-contained** - No external references or scripts

### Example Source SVG

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <!-- Background -->
  <rect width="32" height="32" fill="#4CAF50" rx="6"/>
  
  <!-- Icon content with stroke -->
  <path style="fill:none;stroke:#FF69B4;stroke-width:1.8;..." d="..." />
</svg>
```

## Output

The tool generates SVG files with:

- **Adjusted dimensions** - Width and height attributes updated for target size
- **Scaled stroke widths** - Proportionally adjusted for optimal rendering
- **Preserved viewBox** - Maintains the coordinate system from the source
- **Clean formatting** - Well-formatted, readable SVG output

### Example Output (16×16)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="16" height="16">
  <!-- Background -->
  <rect width="32" height="32" fill="#4CAF50" rx="6"/>
  
  <!-- Icon content with adjusted stroke -->
  <path style="fill:none;stroke:#FF69B4;stroke-width:1.1;..." d="..." />
</svg>
```

Notice:
- `width="16" height="16"` - Updated dimensions
- `stroke-width:1.1` - Reduced from 1.8 (1.8 × 0.6 = 1.08, rounded to 1.1)
- `viewBox="0 0 32 32"` - Preserved from source

## Integration with Build Process

The icon generation is **separate** from the main site build process. You should regenerate icons when:

1. **Changing the logo design** - Any visual updates to the source SVG
2. **Adjusting colors** - Color scheme changes (e.g., stroke color updates)
3. **Adding new sizes** - If you need additional icon sizes

After generating icons:

```bash
# Rebuild the site to include updated icons
python3 src/event_manager.py generate
```

## Design Considerations

### Color Consistency

The filter bar logo uses the same stroke color as the filter bar text for visual consistency:

- **Color**: `#FF69B4` (Barbie Pink)
- **CSS Variable**: `var(--color-primary)`
- **Defined in**: `assets/css/style.css`

When updating the source SVG, ensure the stroke color matches:

```xml
<path style="stroke:#FF69B4;..." />
```

### Stroke Width Guidelines

| Icon Size | Recommended Stroke Width | Notes |
|-----------|-------------------------|-------|
| 16×16px | 1.0-1.2 | Very thin for clarity |
| 32×32px | 1.8-2.0 | Standard width |
| 192×192px+ | 1.8-2.0 | Can be slightly bolder |

The tool automatically scales these proportionally.

## Technical Details

### Dependencies

- **Python Standard Library Only** - No external dependencies (PIL, Cairo, etc.)
- Uses `re` for SVG parsing and manipulation
- Uses `pathlib` for cross-platform file handling

### SVG Manipulation

The tool:

1. **Reads** the source SVG file
2. **Parses** viewBox, width, height attributes using regex
3. **Adjusts** stroke-width values proportionally
4. **Updates** width and height attributes for target size
5. **Preserves** all other SVG content (paths, shapes, fills, etc.)
6. **Writes** the modified SVG to the output directory

### Error Handling

The tool provides clear error messages for:

- Missing source SVG file
- Invalid viewBox format
- Missing or malformed SVG attributes
- File write permissions

## Examples

### Regenerate After Logo Update

```bash
# 1. Edit the source SVG
vim assets/svg/favicon.svg

# 2. Regenerate all icons
python3 src/tools/generate_icons.py

# 3. Verify the output
ls -lh assets/svg/favicon*.svg assets/svg/icon-*.svg

# 4. Rebuild the site
python3 src/event_manager.py generate
```

### Test Icon Appearance

```bash
# Start a local server
cd public && python3 -m http.server 8000

# Open in browser: http://localhost:8000
# Check:
# - Browser tab favicon (16×16, 32×32)
# - PWA install icon (192×192, 512×512)
```

## Troubleshooting

### Icons Not Appearing in Browser

1. **Clear browser cache** - Browsers aggressively cache favicons
2. **Hard refresh** - Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. **Check generated files** - Verify SVG files exist in `assets/svg/`
4. **Rebuild site** - Ensure site was regenerated after icon changes

### Stroke Width Too Bold/Thin

Adjust the stroke scale factors in the tool:

```python
ICON_SIZES = {
    'favicon-16x16.svg': {
        'size': 16,
        'stroke_scale': 0.6  # Adjust this value (0.5-0.8)
    },
    ...
}
```

Then regenerate icons.

### Colors Not Matching

Ensure the source SVG uses the correct color:

```bash
# Check current color
grep "stroke:" assets/svg/favicon.svg

# Should show: stroke:#FF69B4
```

## Future Enhancements

Possible future improvements:

- [ ] PNG/ICO generation using headless browser (if needed)
- [ ] Maskable icon generation for Android adaptive icons
- [ ] Automatic manifest.json updates
- [ ] SVG optimization (SVGO integration)
- [ ] Batch processing of multiple source files
- [ ] Custom stroke width overrides per size

## References

- **PWA Icons**: [Web.dev - Icons & Splash Screens](https://web.dev/add-manifest/)
- **Favicon Best Practices**: [MDN - Favicon](https://developer.mozilla.org/en-US/docs/Glossary/Favicon)
- **SVG Optimization**: [SVGO](https://github.com/svg/svgo)

---

**Last Updated**: January 2025  
**Tool Version**: 1.0  
**Status**: ✅ Production Ready
