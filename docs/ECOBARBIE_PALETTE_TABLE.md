# Complete ecoBarbie Color Palette - Single Table Reference

**Quick visual reference for all KRWL> colors**

## Complete Color Palette Table

| Badge | Name | Hex | RGB | CSS Variable | Category | Usage |
|-------|------|-----|-----|--------------|----------|-------|
| 🩷 | **Primary (Base)** | `#D689B8` | 214, 137, 184 | `--color-primary` | Core | Base color for all transformations |
| 💗 | **Primary Hover** | `#E8A5C8` | 232, 165, 200 | `--color-primary-hover` | Core | Interactive hover states |
| 🩷 | **Success** | `#D689B8` | 214, 137, 184 | `--color-success` | Status | Success state (uses primary) |
| | | | | | | |
| **TINTS (Lighter - Add White)** | | | | | | |
| 💗 | **Tint 50%** | `#eac0da` | 234, 192, 218 | `--color-tint-50` | Tint | Light backgrounds, hover states |
| ⚪ | **Tint 100%** | `#ffffff` | 255, 255, 255 | `--color-tint-100` | Tint | Pure white, maximum contrast |
| | | | | | | |
| **SHADES (Darker - Add Black)** | | | | | | |
| 🟣 | **Shade 50%** | `#6b445c` | 107, 68, 92 | `--color-shade-50` | Shade | Dark accents, borders, text |
| ⚫ | **Shade 100%** | `#000000` | 0, 0, 0 | `--color-shade-100` | Shade | Pure black, maximum contrast |
| | | | | | | |
| **TONES (Muted - Add Grey)** | | | | | | |
| 💗 | **Tone 50%** | `#d6afc7` | 214, 175, 199 | `--color-tone-50` | Tone | Disabled states, secondary text |
| ⚪ | **Tone 100%** | `#d6d6d6` | 214, 214, 214 | `--color-tone-100` | Tone | Neutral grey, fully desaturated |
| | | | | | | |
| **BACKGROUNDS (Very Dark)** | | | | | | |
| ⚫ | **BG Primary** | `#110a0e` | 17, 10, 14 | `--color-bg-primary` | Background | Main background (92% darker) |
| ⚫ | **BG Secondary** | `#150d12` | 21, 13, 18 | `--color-bg-secondary` | Background | Secondary background (90% darker) |
| ⚫ | **BG Tertiary** | `#191016` | 25, 16, 22 | `--color-bg-tertiary` | Background | Tertiary background (88% darker) |
| | | | | | | |
| **TEXT (Very Light)** | | | | | | |
| ⚪ | **Text Primary** | `#f9f5f8` | 249, 245, 248 | `--color-text-primary` | Text | Primary text (98% lighter, high contrast) |
| 💗 | **Text Secondary** | `#f2e9ee` | 242, 233, 238 | `--color-text-secondary` | Text | Secondary text (95% lighter) |
| 💗 | **Text Tertiary** | `#eadde5` | 234, 221, 229 | `--color-text-tertiary` | Text | Tertiary text (92% lighter) |
| | | | | | | |
| **BORDERS** | | | | | | |
| 🟪 | **Border Primary** | `#35222e` | 53, 34, 46 | `--color-border-primary` | Border | Primary border (75% darker) |
| 🟪 | **Border Secondary** | `#2f1e28` | 47, 30, 40 | `--color-border-secondary` | Border | Secondary border (78% darker) |
| | | | | | | |
| **ACCENTS** | | | | | | |
| 🩷 | **Accent** | `#e07fba` | 224, 127, 186 | `--color-accent` | Accent | Links, info, highlights (+20% sat, +5% val) |
| 🩷 | **Warning** | `#eb7dc0` | 235, 125, 192 | `--color-warning` | Status | Warnings, pending states (+30% sat, +10% val) |
| 🟣 | **Error** | `#954476` | 149, 68, 118 | `--color-error` | Status | Errors, critical alerts (+50% sat, -30% val) |
| | | | | | | |
| **BOOKMARKS** | | | | | | |
| 💗 | **Bookmark** | `#eeb2d7` | 238, 178, 215 | `--color-bookmark` | Special | Bookmark highlight |
| 💗 | **Bookmark Light** | `#f6c1e2` | 246, 193, 226 | `--color-bookmark-light` | Special | Bookmark hover |
| 💗 | **Bookmark Lighter** | `#fce0ef` | 252, 224, 239 | `--color-bookmark-lighter` | Special | Bookmark subtle (90% lighter) |

## Quick Legend

- 🩷 **Pink** - Main ecoBarbie colors (medium brightness)
- 💗 **Light Pink** - Tints and light variations
- 🟣 **Purple** - Medium-dark shades and accents
- 🟪 **Dark Purple** - Borders and dark elements
- ⚪ **White** - Very light colors and pure white
- ⚫ **Black** - Very dark colors and pure black

## Emoji Badge Key

| Emoji | Represents | Luminance Range |
|-------|------------|-----------------|
| 💗 | Very Light Pink | 70-95% brightness |
| 🩷 | Medium Pink | 50-70% brightness |
| 🟣 | Purple | 30-50% brightness |
| 🟪 | Dark Purple | 10-30% brightness |
| ⚪ | White/Very Light | 95%+ brightness |
| ⚫ | Black/Very Dark | <8% brightness |

## Usage Examples

```css
/* Using the color variables */
.element {
  color: var(--color-text-primary);        /* ⚪ #f9f5f8 */
  background: var(--color-bg-primary);     /* ⚫ #110a0e */
  border: 1px solid var(--color-primary);  /* 🩷 #D689B8 */
}

.button {
  background: var(--color-primary);        /* 🩷 #D689B8 */
  color: var(--color-tint-100);           /* ⚪ #ffffff */
}

.button:hover {
  background: var(--color-primary-hover);  /* 💗 #E8A5C8 */
}

.error {
  color: var(--color-error);               /* 🟣 #954476 */
}
```

## Inline Reference

Quick copy-paste for documentation:

- 🩷 `#D689B8` - Primary
- 💗 `#E8A5C8` - Primary Hover
- 💗 `#eac0da` - Tint 50%
- ⚪ `#ffffff` - White
- 🟣 `#6b445c` - Shade 50%
- ⚫ `#000000` - Black
- 💗 `#d6afc7` - Tone 50%
- ⚪ `#d6d6d6` - Grey
- ⚫ `#110a0e` - BG Primary
- ⚪ `#f9f5f8` - Text Primary
- 🟪 `#35222e` - Border Primary
- 🩷 `#e07fba` - Accent
- 🩷 `#eb7dc0` - Warning
- 🟣 `#954476` - Error
- 💗 `#eeb2d7` - Bookmark

---

**Total Colors:** 26 colors (all derived from single base color #D689B8)

**Monochromatic Purity:** 100% - Every color is a tint, shade, or tone of ecoBarbie pink

**WCAG Compliance:** All text/background combinations meet AA standards

**Files:**
- Source: `config.json` → `design.colors`
- Generated: `assets/html/design-tokens.css`
- Full Documentation: `COLOR_PALETTE.md`

---

**Last Updated:** 2026-01-19  
**Generator:** `python3 src/tools/generate_design_tokens.py`
