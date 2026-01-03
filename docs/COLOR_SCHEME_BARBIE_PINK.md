# Barbie Pink Color Scheme - Original Design Documentation

> Original color palette design for KRWL HOF Community Events

## 🎨 Overview

This document preserves the original Barbie Pink monochromatic color palette that was designed for the KRWL HOF project. These colors are now managed through design tokens in `config.json`, but this documentation serves as the authoritative color theory reference.

## 📦 Color Palette

### Base Color

**Barbie Red/Pink**: `#FF69B4` (RGB: 255, 105, 180)

![#FF69B4](https://via.placeholder.com/400x50/FF69B4/FFFFFF?text=Barbie+Red+%23FF69B4)

This is the signature color of the KRWL HOF brand - a vibrant pink that combines energy and approachability.

### Tints (Barbie Red + White)

Tints are created by mixing the base color with white, creating lighter, softer versions:

| Name | Hex Code | Color | Mix Ratio | Usage |
|------|----------|-------|-----------|-------|
| Lightest | `#FFE5F3` | ![#FFE5F3](https://via.placeholder.com/80x30/FFE5F3/000000?text=+) | 10% red, 90% white | Subtle backgrounds, hover states |
| Light | `#FFCCEB` | ![#FFCCEB](https://via.placeholder.com/80x30/FFCCEB/000000?text=+) | 30% red, 70% white | Light accents, borders |
| Medium | `#FFB3DF` | ![#FFB3DF](https://via.placeholder.com/80x30/FFB3DF/000000?text=+) | 50% red, 50% white | Secondary highlights |

### Pure

| Name | Hex Code | Color | Usage |
|------|----------|-------|-------|
| Barbie Red | `#FF69B4` | ![#FF69B4](https://via.placeholder.com/80x30/FF69B4/FFFFFF?text=+) | Primary brand color, CTAs, active states |

### Tones (Barbie Red + Grey)

Tones are created by mixing the base color with grey, creating muted versions:

| Name | Hex Code | Color | Mix Ratio | Usage |
|------|----------|-------|-----------|-------|
| Light Tone | `#D689B8` | ![#D689B8](https://via.placeholder.com/80x30/D689B8/000000?text=+) | Red + light grey | Muted accents |
| Medium Tone | `#B05F8E` | ![#B05F8E](https://via.placeholder.com/80x30/B05F8E/FFFFFF?text=+) | Red + medium grey | Subdued highlights |
| Dark Tone | `#8A4A70` | ![#8A4A70](https://via.placeholder.com/80x30/8A4A70/FFFFFF?text=+) | Red + dark grey | Deep accents |

### Shades (Barbie Red + Black)

Shades are created by mixing the base color with black, creating darker versions:

| Name | Hex Code | Color | Mix Ratio | Usage |
|------|----------|-------|-----------|-------|
| Light Shade | `#BF5087` | ![#BF5087](https://via.placeholder.com/80x30/BF5087/FFFFFF?text=+) | 75% red, 25% black | Dark accents |
| Medium Shade | `#80355A` | ![#80355A](https://via.placeholder.com/80x30/80355A/FFFFFF?text=+) | 50% red, 50% black | Deep backgrounds |
| Dark Shade | `#401B2D` | ![#401B2D](https://via.placeholder.com/80x30/401B2D/FFFFFF?text=+) | 25% red, 75% black | Very dark backgrounds |
| Darkest | `#200D16` | ![#200D16](https://via.placeholder.com/80x30/200D16/FFFFFF?text=+) | 10% red, 90% black | Nearly black with hint of warmth |

### Neutrals (Blacks & Greys)

Supporting neutral colors for backgrounds and text:

| Name | Hex Code | Color | Usage |
|------|----------|-------|-------|
| Pure Black | `#000000` | ![#000000](https://via.placeholder.com/80x30/000000/FFFFFF?text=+) | Maximum contrast |
| Near Black | `#0D0D0D` | ![#0D0D0D](https://via.placeholder.com/80x30/0D0D0D/FFFFFF?text=+) | Almost black |
| Dark Grey | `#1a1a1a` | ![#1a1a1a](https://via.placeholder.com/80x30/1a1a1a/FFFFFF?text=+) | Primary dark background |
| Medium Dark | `#2a2a2a` | ![#2a2a2a](https://via.placeholder.com/80x30/2a2a2a/FFFFFF?text=+) | Secondary dark background |
| Medium Grey | `#3a3a3a` | ![#3a3a3a](https://via.placeholder.com/80x30/3a3a3a/FFFFFF?text=+) | Tertiary background |
| Light Grey | `#555555` | ![#555555](https://via.placeholder.com/80x30/555555/FFFFFF?text=+) | Muted text, borders |
| Lighter Grey | `#888888` | ![#888888](https://via.placeholder.com/80x30/888888/FFFFFF?text=+) | Secondary text |
| White | `#ffffff` | ![#ffffff](https://via.placeholder.com/80x30/ffffff/000000?text=+) | Primary text on dark backgrounds |

## 🎨 Design Token Mapping

These original colors are now mapped to design tokens in `config.json`:

```json
{
  "design": {
    "colors": {
      "primary": "#FF69B4",           // Barbie Red
      "primary_hover": "#ff4da6",     // Slightly darker pink
      "bg_primary": "#0d1117",        // Near Black (GitHub-style)
      "bg_secondary": "#161b22",      // Dark background
      "bg_tertiary": "#21262d",       // Lighter dark background
      "text_primary": "#c9d1d9",      // Light text
      "text_secondary": "#8b949e",    // Muted text
      "text_tertiary": "#6e7681",     // Very muted text
      "border_primary": "#30363d",    // Subtle borders
      "border_secondary": "#21262d",  // Even more subtle borders
      "accent": "#58a6ff",            // Blue accent (complements pink)
      "success": "#3fb950",           // Green for success states
      "warning": "#d29922",           // Orange for warnings
      "error": "#f85149"              // Red for errors
    }
  }
}
```

## 💡 Usage Guidelines

### Primary Actions
Use **Barbie Red** (`#FF69B4`) for:
- Call-to-action buttons
- Active navigation items
- Primary links
- Focus indicators
- Brand elements

### Backgrounds
Use **Dark Shade** (`#401B2D`) or **Darkest** (`#200D16`) for:
- Card backgrounds
- Modal overlays
- Section dividers
- Subtle contrasts

### Text
Use **White** (`#ffffff`) for primary text on dark backgrounds.
Use **Lighter Grey** (`#888888`) for secondary text.

### Hover States
Use **Barbie Red Hover** (`#ff4da6`) or **Light Shade** (`#BF5087`) for interactive element hover states.

## 🔧 CSS Variables (Legacy)

Before migration to design tokens, these CSS variables were used:

```css
:root {
    /* Barbie Red Tints (lighter versions) */
    --barbie-tint-lightest: #FFE5F3;
    --barbie-tint-light: #FFCCEB;
    --barbie-tint-medium: #FFB3DF;
    
    /* Pure Barbie Red */
    --barbie-red: #FF69B4;
    --barbie-red-hover: #ff4da6;
    
    /* Barbie Red Tones (muted versions) */
    --barbie-tone-light: #D689B8;
    --barbie-tone-medium: #B05F8E;
    --barbie-tone-dark: #8A4A70;
    
    /* Barbie Red Shades (darker versions) */
    --barbie-shade-light: #BF5087;
    --barbie-shade-medium: #80355A;
    --barbie-shade-dark: #401B2D;
    --barbie-shade-darkest: #200D16;
    
    /* Blacks & Greys */
    --black: #000000;
    --near-black: #0D0D0D;
    --dark-grey: #1a1a1a;
    --medium-dark: #2a2a2a;
    --medium-grey: #3a3a3a;
    --light-grey: #555555;
    --lighter-grey: #888888;
    --white: #ffffff;
    
    /* Semantic color mappings */
    --bg-primary: var(--dark-grey);
    --bg-secondary: var(--medium-dark);
    --bg-tertiary: var(--medium-grey);
    --text-primary: var(--white);
    --text-secondary: #ccc;
    --text-tertiary: var(--lighter-grey);
    --accent-primary: var(--barbie-red);
    --accent-hover: var(--barbie-red-hover);
    --border-primary: var(--barbie-red);
}
```

## 🎨 Color Theory

### Why Monochromatic?

A monochromatic color scheme uses variations (tints, tones, shades) of a single hue. Benefits:

1. **Visual Cohesion** - Creates a unified, harmonious look
2. **Brand Recognition** - Strong association with the Barbie Pink color
3. **Simplicity** - Easy to maintain and extend
4. **Flexibility** - Provides enough variation for hierarchy
5. **Accessibility** - Clear contrast when used properly

### Contrast Ratios

For WCAG 2.1 Level AA compliance:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

**Safe Combinations:**
- ✅ White (`#ffffff`) on Dark Grey (`#1a1a1a`) = 15.8:1 ✨
- ✅ White on Barbie Red (`#FF69B4`) = 3.7:1 (large text only)
- ✅ Barbie Red on Dark Grey = 4.2:1 (borderline, use for large text)

## 🚀 Restoring Original Colors

If you want to restore the original color scheme exactly as designed:

```bash
# Edit config.json to match original colors
vim config.json

# Update design.colors section with original hex codes

# Regenerate CSS tokens
python3 src/templates/components/generate_design_tokens.py

# Rebuild site
python3 src/event_manager.py generate
```

## 📚 Related Documentation

- [Design Tokens](../templates/components/variables-reference.md) - Current design token system
- [Component System](../templates/components/README.md) - How tokens are used
- [Instant Rebranding](../KISS_IMPROVEMENTS.md) - How to rebrand the entire site

## 🎨 Design Philosophy

> "The Barbie Pink color scheme embodies the playful, community-focused spirit of KRWL HOF. It's bold without being aggressive, energetic without being overwhelming, and creates a unique visual identity that stands out in a sea of blue-and-white event platforms."

---

**Created**: Original design  
**Backed up**: January 3, 2026  
**Status**: Preserved for reference  
**Current System**: Design tokens in config.json  
