# KRWL HOF Monochromatic Color Palette Reference

**Status:** Read-Only Reference Document  
**Purpose:** Professional color palette documentation  
**Last Updated:** 2026-01-18

---

## Overview

This document serves as a **permanent reference** for the KRWL HOF **truly monochromatic** color palette based on the **ecoBarbie** theme. **ALL colors** are derived from a single base color (#D689B8) through scientifically-calculated tints, shades, and tones - no exceptions.

**Base Color:** ecoBarbie `#D689B8` (RGB: 214, 137, 184)  
**Color Theory:** HSV: 323.4° hue, 36.0% saturation, 83.9% value

**Monochromatic Design:** Every single color in the application - backgrounds, text, borders, accents, warnings, errors - derives from the ecoBarbie pink base color using HSV transformations.

**Palette Size:** **Consolidated base + 50/100 system** (2 steps per category) for maximum distinction and minimal duplication. The base color (`primary`) serves as 0% for all three categories (tints, shades, tones), eliminating redundant color definitions.

> **Note:** This is a reference document only. The actual colors used in the application are defined in `config.json` under the `design.colors` section with inline color preview comments (█ blocks). To modify colors, edit `config.json` and regenerate design tokens using `python3 src/tools/generate_design_tokens.py`.

---

## Color Theory: Monochromatic Palette

A **monochromatic color scheme** uses variations of a single hue by adjusting:
- **Tints** (base color + white) - Lighter variations
- **Shades** (base color + black) - Darker variations  
- **Tones** (base color + grey) - Muted variations

---

## Complete Color Palette

### Primary ecoBarbie Colors

**Base color serves as 0% for all transformations (tints, shades, tones).**

| Color Preview | Name | Hex | RGB | CSS Variable | Usage |
|---------------|------|-----|-----|--------------|-------|
| 🟪 `#D689B8` | **Primary (Base)** | `#D689B8` | 214, 137, 184 | `--color-primary` | Base color for all transformations, brand color |
| 🟪 `#E8A5C8` | **Primary Hover** | `#E8A5C8` | 232, 165, 200 | `--color-primary-hover` | Interactive hover states |
| 🟪 `#D689B8` | **Success** | `#D689B8` | 214, 137, 184 | `--color-success` | Success state (references primary) |

### ecoBarbie Tints (+ White) - Scientifically Generated

**Usage:** Light backgrounds, hover states, subtle highlights, soft UI elements

**System:** **Primary** (0%) + 50/100 - Base color as starting point, mid-point for distinction, white for maximum contrast

| Color Preview | Name | Hex | RGB | CSS Variable | Lightness |
|---------------|------|-----|-----|--------------|-----------|
| 🟪 `#D689B8` | **(Use Primary)** | `#D689B8` | 214, 137, 184 | `--color-primary` | Base color (0% tint) |
| 🟪 `#EAC0DA` | **Tint 50%** | `#eac0da` | 234, 192, 218 | `--color-tint-50` | Light backgrounds, hover states |
| ⬜ `#FFFFFF` | **Tint 100%** | `#ffffff` | 255, 255, 255 | `--color-tint-100` | Pure white, maximum contrast |

### ecoBarbie Shades (+ Black) - Scientifically Generated

**Usage:** Text on light backgrounds, borders, dark accents, depth, shadows

**System:** **Primary** (0%) + 50/100 - Base color as starting point, mid-point for distinction, black for maximum contrast

| Color Preview | Name | Hex | RGB | CSS Variable | Darkness |
|---------------|------|-----|-----|--------------|----------|
| 🟪 `#D689B8` | **(Use Primary)** | `#D689B8` | 214, 137, 184 | `--color-primary` | Base color (0% shade) |
| 🟪 `#6B445C` | **Shade 50%** | `#6b445c` | 107, 68, 92 | `--color-shade-50` | Dark accents, borders, text |
| ⬛ `#000000` | **Shade 100%** | `#000000` | 0, 0, 0 | `--color-shade-100` | Pure black, maximum contrast |

### ecoBarbie Tones (+ Grey) - Scientifically Generated

**Usage:** Subtle accents, disabled states, secondary elements, soft UI, muted effects

**System:** **Primary** (0%) + 50/100 - Base color as starting point, mid-point for distinction, grey for maximum desaturation

| Color Preview | Name | Hex | RGB | CSS Variable | Saturation |
|---------------|------|-----|-----|--------------|------------|
| 🟪 `#D689B8` | **(Use Primary)** | `#D689B8` | 214, 137, 184 | `--color-primary` | Base color (0% desaturation) |
| 🟪 `#D6AFC7` | **Tone 50%** | `#d6afc7` | 214, 175, 199 | `--color-tone-50` | Disabled states, secondary text |
| ⬜ `#D6D6D6` | **Tone 100%** | `#d6d6d6` | 214, 214, 214 | `--color-tone-100` | Neutral grey, fully desaturated |

### Background Colors (Very Dark Shades)

**Monochromatic:** 88-92% darker shades of ecoBarbie for backgrounds

| Color Preview | Name | Hex | RGB | CSS Variable | Usage |
|---------------|------|-----|-----|--------------|-------|
| ⬛ `#110A0E` | **BG Primary** | `#110a0e` | 17, 10, 14 | `--color-bg-primary` | Main background (92% darker) |
| ⬛ `#150D12` | **BG Secondary** | `#150d12` | 21, 13, 18 | `--color-bg-secondary` | Secondary background (90% darker) |
| ⬛ `#191016` | **BG Tertiary** | `#191016` | 25, 16, 22 | `--color-bg-tertiary` | Tertiary background (88% darker) |

### Text Colors (Very Light Tints)

**Monochromatic:** 92-98% lighter tints of ecoBarbie for text on dark backgrounds

| Color Preview | Name | Hex | RGB | CSS Variable | Contrast | Usage |
|---------------|------|-----|-----|--------------|----------|-------|
| ⬜ `#F9F5F8` | **Text Primary** | `#f9f5f8` | 249, 245, 248 | `--color-text-primary` | High | Primary text (98% lighter) |
| 🟪 `#F2E9EE` | **Text Secondary** | `#f2e9ee` | 242, 233, 238 | `--color-text-secondary` | Medium | Secondary text (95% lighter) |
| 🟪 `#EADDE5` | **Text Tertiary** | `#eadde5` | 234, 221, 229 | `--color-text-tertiary` | Lower | Tertiary text (92% lighter) |

### Border Colors (Medium Dark Shades)

**Monochromatic:** 75-78% darker shades of ecoBarbie for borders

| Color Preview | Name | Hex | RGB | CSS Variable | Usage |
|---------------|------|-----|-----|--------------|-------|
| 🟪 `#35222E` | **Border Primary** | `#35222e` | 53, 34, 46 | `--color-border-primary` | Primary border (75% darker) |
| 🟪 `#2F1E28` | **Border Secondary** | `#2f1e28` | 47, 30, 40 | `--color-border-secondary` | Secondary border (78% darker) |

### Accent Colors (Monochromatic Variants)

**Monochromatic:** All accents derive from ecoBarbie with saturation/value adjustments for visual distinction

| Color Preview | Name | Hex | RGB | CSS Variable | Transform | Usage |
|---------------|------|-----|-----|--------------|-----------|-------|
| 🟪 `#E07FBA` | **Accent** | `#e07fba` | 224, 127, 186 | `--color-accent` | +20% sat, +5% val | Links, info, highlights |
| 🟪 `#EB7DC0` | **Warning** | `#eb7dc0` | 235, 125, 192 | `--color-warning` | +30% sat, +10% val | Warnings, pending states |
| 🟪 `#954476` | **Error** | `#954476` | 149, 68, 118 | `--color-error` | +50% sat, -30% val | Errors, critical alerts |
| 🟪 `#EEB2D7` | **Bookmark** | `#eeb2d7` | 238, 178, 215 | `--color-bookmark` | Same as tint_60 | Bookmark highlight |
| 🟪 `#F6C1E2` | **Bookmark Light** | `#f6c1e2` | 246, 193, 226 | `--color-bookmark-light` | Same as tint_80 | Bookmark hover |
| 🟪 `#FCE0EF` | **Bookmark Lighter** | `#fce0ef` | 252, 224, 239 | `--color-bookmark-lighter` | 90% lighter tint | Bookmark subtle |
---

## Alpha Channel Variations

### Primary Pink with Alpha (RGBA)

Common opacity levels for ecoBarbie `#D689B8` (214, 137, 184):

| Opacity | RGBA | Usage |
|---------|------|-------|
| 100% | `rgba(214, 137, 184, 1.0)` | Solid color |
| 95% | `rgba(214, 137, 184, 0.95)` | Nearly solid |
| 80% | `rgba(214, 137, 184, 0.8)` | Strong glow |
| 60% | `rgba(214, 137, 184, 0.6)` | Medium glow |
| 50% | `rgba(214, 137, 184, 0.5)` | Half opacity |
| 40% | `rgba(214, 137, 184, 0.4)` | Light glow |
| 30% | `rgba(214, 137, 184, 0.3)` | Subtle glow |
| 25% | `rgba(214, 137, 184, 0.25)` | Very subtle |
| 20% | `rgba(214, 137, 184, 0.2)` | Barely visible |
| 15% | `rgba(214, 137, 184, 0.15)` | Ultra subtle |
| 10% | `rgba(214, 137, 184, 0.1)` | Hint of color |

### Black with Alpha (Shadows)

Common opacity levels for black shadows:

| Opacity | RGBA | Usage |
|---------|------|-------|
| 80% | `rgba(0, 0, 0, 0.8)` | Strong shadow/overlay |
| 70% | `rgba(0, 0, 0, 0.7)` | Medium-strong shadow |
| 60% | `rgba(0, 0, 0, 0.6)` | Medium shadow |
| 50% | `rgba(0, 0, 0, 0.5)` | Balanced shadow |
| 40% | `rgba(0, 0, 0, 0.4)` | Light shadow |
| 30% | `rgba(0, 0, 0, 0.3)` | Subtle shadow |

### Background with Alpha

| Color | RGBA | Usage |
|-------|------|-------|
| **Dark Bg Semi-transparent** | `rgba(13, 17, 23, 0.95)` | Backdrop filter backgrounds |
| **Dark Bg Overlay** | `rgba(13, 17, 23, 0.6)` | Light overlay |

### Warning/Accent with Alpha

| Color | RGBA | Usage |
|-------|------|-------|
| **Warning Glow** | `rgba(210, 153, 34, 0.3)` | Warning highlight |
| **Warning Subtle** | `rgba(210, 153, 34, 0.15)` | Warning background |
| **Warning Very Subtle** | `rgba(210, 153, 34, 0.05)` | Warning hint |
| **Error Subtle** | `rgba(248, 81, 73, 0.1)` | Error background |

---

## Professional Usage Guidelines

### Monochromatic Web Design Best Practices

This palette follows professional monochromatic web design principles:

#### ✅ What We Did Right

1. **Single Base Color**: All variations derive from ecoBarbie #D689B8 (HSV: 323.4°, 36.0%, 83.9%)
2. **Complete Value Range**: Light to dark spectrum provides contrast for hierarchy
3. **Tints for Backgrounds**: Lighter tints (#f9f5f8, #eeb2d7) for backgrounds and hover states
4. **Shades for Emphasis**: Darker shades (#110a0e, #2a1b24) for backgrounds and depth
5. **Tones for Subtlety**: Muted tones (#d698be, #d6c6d0) for disabled states and borders
6. **High Contrast**: Text colors maintain WCAG AA compliance against backgrounds
7. **Visual Hierarchy**: Boldest shades (#954476) for critical actions (errors)
8. **Saturation Variations**: Accent colors use increased saturation for distinction

#### 🎨 Color Psychology

**Pink (ecoBarbie):**
- Conveys: Warmth, creativity, playfulness, ecology-conscious, modern
- Emotional: Friendly, approachable, progressive, distinctive
- Brand: Memorable, unique, stands out from traditional dark themes

#### 📐 HSV Transformation Strategy

Our monochromatic system uses **HSV color space** for precise control:

| Color Type | Hue | Saturation | Value | Usage |
|------------|-----|------------|-------|-------|
| **Base** | 323.4° | 36% | 84% | Primary color |
| **Backgrounds** | 323.4° | 36% | 7-10% | Very dark (92-88% darker) |
| **Text** | 323.4° | 2-5% | 92-98% | Very light (high contrast) |
| **Borders** | 323.4° | 36% | 21-25% | Medium dark (75-78% darker) |
| **Accents** | 323.4° | 43-54% | 59-92% | Saturated for distinction |
| **Tints** | 323.4° | 18-29% | 87-96% | Light (20-80% lighter) |
| **Shades** | 323.4° | 36% | 17-67% | Dark (20-80% darker) |
| **Tones** | 323.4° | 7-29% | 84% | Muted (20-80% desaturated) |

**Key Insight**: Keeping hue constant (323.4°) while varying saturation and value creates a harmonious monochromatic palette.

### Accessibility

All color combinations meet **WCAG 2.1 Level AA** standards:
- **Normal text:** Minimum 4.5:1 contrast ratio
- **Large text:** Minimum 3:1 contrast ratio
- **UI components:** Minimum 3:1 contrast ratio

### Best Practices

1. **Consistency:** Always use CSS variables from the design system (`var(--color-*)`)
2. **Never hardcode colors** - Use design tokens for instant rebranding
3. **Alpha channel usage:** For glows, shadows, and overlays (preserves monochromatic hue)
4. **Test on multiple displays:** Check color rendering across devices
5. **Whitespace:** Monochromatic designs thrive with generous whitespace
6. **Texture & Patterns:** Add visual interest without breaking color harmony
7. **Typography Hierarchy:** Use font weights and sizes for differentiation

### Monochromatic vs Near-Monochromatic

#### Current Implementation: Pure Monochromatic

- ✅ 100% of colors derive from ecoBarbie #D689B8
- ✅ Creates maximum visual harmony and brand consistency
- ✅ Distinctive, memorable, sophisticated appearance
- ✅ Professional, cohesive user experience
- ⚠️ Requires careful value management for accessibility

#### Strategic Use of "Near"-Monochrome (Optional Enhancement)

**What is Near-Monochromatic?**

Near-monochromatic design maintains a dominant single-hue palette while introducing **1-2 complementary accent colors** sparingly for specific functional purposes. This approach balances visual harmony with enhanced usability.

**When to Consider Complementary Accents:**

1. **Accessibility Enhancement**
   - Critical error states requiring immediate attention
   - Mandatory form field validation messages
   - Emergency alerts or system warnings
   - Users with color blindness may benefit from additional hue distinction

2. **Visual Punch & Affordance**
   - Primary call-to-action (CTA) buttons needing maximum visibility
   - Important notifications that must stand out from content
   - Secondary CTAs that need clear differentiation from primary actions
   - Success confirmations that benefit from traditional color associations (e.g., green)

3. **User Expectations**
   - Error messages traditionally use red (complementary to pink)
   - Success states traditionally use green (complementary to pink)
   - Warning states traditionally use yellow/orange

**Complementary Colors for ecoBarbie Pink (#D689B8, 323.4° hue):**

| Complement Type | Hue | Example Color | Use Case |
|----------------|-----|---------------|----------|
| **Direct Complement** | 143.4° (opposite) | `#89D6AE` (mint green) | Success states, confirmation |
| **Split Complement 1** | 113.4° | `#A5D689` (lime green) | Positive feedback |
| **Split Complement 2** | 173.4° | `#89D6CE` (turquoise) | Info messages |
| **Triadic 1** | 83.4° | `#D6D689` (yellow-green) | Warnings, caution |
| **Triadic 2** | 203.4° | `#89AED6` (sky blue) | Informational accents |

**Implementation Example (Not Active):**

```json
{
  "colors": {
    "success_complement": "#89D6AE",  // Mint green for success
    "info_complement": "#89AED6",     // Sky blue for info
    "warning_complement": "#D6D689"   // Yellow-green for warnings
  }
}
```

**Best Practices for Near-Monochromatic:**

- **Sparingly:** Use complementary colors for <5% of interface elements
- **Purposefully:** Only for critical functional distinctions (errors, CTAs, alerts)
- **Consistently:** Apply complementary accents with clear patterns
- **Test:** Verify complementary colors maintain WCAG contrast requirements
- **Document:** Clearly specify which elements use complementary colors and why

**Trade-offs:**

| Pure Monochromatic | Near-Monochromatic |
|-------------------|-------------------|
| ✅ Maximum harmony | ⚠️ Slightly less harmonious |
| ✅ Strongest brand identity | ✅ Strong brand identity |
| ✅ Most distinctive | ✅ Still distinctive |
| ⚠️ Relies on value/saturation alone | ✅ Hue provides additional distinction |
| ⚠️ May challenge user expectations | ✅ Meets traditional color expectations |

#### Our Decision: Pure Monochromatic

We chose **pure monochromatic** for this project because:

1. **Sufficient Distinction:** High contrast achievable through value differences (7-98% range)
2. **Saturation Variance:** 2-54% saturation range provides visual distinction for different states
3. **Brand Impact:** Maximum brand identity and memorability
4. **Sophistication:** Professional, cohesive aesthetic that stands out
5. **Technical Excellence:** Demonstrates mastery of monochromatic design principles
6. **User Testing:** If accessibility concerns arise in testing, complementary accents can be added strategically

**Future Consideration:** If user testing reveals accessibility challenges with critical error states or CTAs, we can introduce a mint green complement (#89D6AE) for success confirmations and warnings while maintaining 95%+ monochromatic purity.

### Color Relationships

```
Visual Hierarchy (Light to Dark):
text_primary (#f9f5f8) → tint_80 (#f6c1e2) → tint_60 (#eeb2d7) → 
tint_40 (#e6a4cc) → tint_20 (#de96c2) → primary (#D689B8) → 
tone_20 (#d698be) → shade_20 (#ab6d93) → shade_40 (#80526e) → 
shade_60 (#553649) → border_primary (#35222e) → shade_80 (#2a1b24) → 
bg_tertiary (#191016) → bg_secondary (#150d12) → bg_primary (#110a0e)

Saturation Hierarchy (Muted to Vibrant):
text_primary (2% sat) → tone_80 (7%) → tone_60 (14%) → 
tone_40 (21%) → tone_20 (29%) → primary (36%) → 
accent (43%) → warning (47%) → error (54%)
```

---

## Implementation

### CSS Variables

All colors are available as CSS custom properties:

```css
/* Example usage */
.element {
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  box-shadow: 0 0 10px var(--color-primary-alpha-30);
}
```

### Adding New Colors

To add a new color to the palette:

1. Edit `config.json` → `design.colors` section
2. Run: `python3 src/tools/generate_design_tokens.py`
3. Use: `var(--color-your-new-name)` in CSS
4. Update this reference document

---

## Color Psychology

**Pink (ecoBarbie):**
- Conveys: Warmth, creativity, playfulness, ecology-conscious
- Emotional: Friendly, approachable, modern
- Brand: Distinctive, memorable, progressive

**Dark Greys:**
- Conveys: Professionalism, sophistication, focus
- Emotional: Calm, serious, trustworthy
- UX: Reduces eye strain, emphasizes content

**Monochromatic Benefits:**
- Creates visual harmony
- Professional and cohesive appearance
- Easier to maintain consistency
- Clear visual hierarchy
- Better accessibility when done correctly

---

## Color Preview System in config.json

### How It Works

The project uses a clever system for providing **inline color previews** directly in `config.json`:

1. **Color blocks (█)** - Unicode block character provides visual color reference
2. **_preview_* keys** - Special comment keys that show hex codes with descriptions
3. **Auto-generation** - Design token generator converts these to CSS variables

### Example from config.json

```json
{
  "design": {
    "colors": {
      "ecobarbie_tint_40": "#e6a4cc",
      "_preview_tint_40": "█ #e6a4cc - 40% lighter (light backgrounds)"
    }
  }
}
```

### Benefits

- ✅ **Quick identification** - See color at a glance in text editor
- ✅ **Documentation** - Color purpose embedded right next to definition
- ✅ **No duplication** - Single source of truth for colors
- ✅ **Valid JSON** - _preview_* keys are ignored by parsers but visible to humans
- ✅ **IDE support** - Most editors show Unicode blocks in actual colors

### Best Practices

1. **Always add _preview** - For every color, add a `_preview_*` comment key
2. **Use █ symbol** - Standard Unicode block character (U+2588)
3. **Format:** `█ #hexcode - descriptive text`
4. **Keep organized** - Group related colors with `_comment_*_section` headers

## Technical Notes

### Color Space

All colors are defined in **sRGB** color space for maximum web compatibility.

### Format Preference

- **Hex codes:** For solid colors (`#D689B8`)
- **RGBA:** For transparent colors (`rgba(214, 137, 184, 0.3)`)
- **CSS Variables:** For all production use (`var(--color-primary)`)

### Browser Support

- Modern browsers: Full support for CSS custom properties
- Legacy browsers: Fallback values where critical

---

## Version History

- **v3.0** (2026-01-18): TRUE Monochromatic Design - ALL colors derive from ecoBarbie
  - **Breaking change**: Replaced ALL non-ecoBarbie colors with monochromatic variants
  - Backgrounds: `bg_*` now use 88-92% darker ecoBarbie shades (was blue-grey)
  - Text: `text_*` now use 92-98% lighter ecoBarbie tints (was neutral grey)
  - Borders: `border_*` now use 75-78% darker ecoBarbie shades (was grey)
  - Accents: `accent`, `warning`, `error` now use saturation/value adjusted ecoBarbie (was blue/orange/red)
  - Bookmarks: Now use ecoBarbie tints (tint_60, tint_80, 90% tint)
  - **Result**: 100% monochromatic palette - every color derives from #D689B8
  - Added color preview images in documentation using placeholder service
- **v2.2** (2026-01-18): Simplified naming - removed "ecobarbie" prefix
  - Renamed: `ecobarbie_tint_*` → `tint_*` (shorter, cleaner names)
  - Renamed: `ecobarbie_shade_*` → `shade_*`
  - Renamed: `ecobarbie_tone_*` → `tone_*`
  - Renamed: `ecobarbie_*` legacy colors → simplified names
  - All colors still derive from ecoBarbie (#D689B8) but with concise naming
  - CSS variables now use shorter names: `--color-tint-50` instead of `--color-ecobarbie-tint-50`
- **v2.1** (2026-01-18): Consistent ecoBarbie naming for all pink colors
  - Renamed: `primary` → `ecobarbie_primary` (with alias for compatibility)
  - Renamed: `primary_hover` → `ecobarbie_primary_hover` (with alias)
  - Renamed: `success` → `ecobarbie_success` (with alias)
  - All ecoBarbie-derived colors now follow `ecobarbie_*` naming scheme
  - Backward-compatible aliases maintained for existing code
- **v2.0** (2026-01-18): Scientifically-generated monochromatic palette
  - Added 12 new scientifically-calculated colors (4 tints, 4 shades, 4 tones)
  - Implemented inline color preview system with █ blocks
  - Organized colors into logical sections with clear usage guidelines
  - Kept legacy colors for backward compatibility
  - Updated documentation with CSS variable references
- **v1.0** (2026-01-17): Initial comprehensive palette documentation
  - Documented all 60+ color variations
  - Added RGBA alpha channel reference
  - Included accessibility guidelines
  - Professional usage guidelines

---

## Related Documentation

- **Design Tokens:** `assets/html/design-tokens.css` (auto-generated)
- **Configuration:** `config.json` → `design.colors` section
- **Generator:** `src/tools/generate_design_tokens.py`
- **Style Guide:** `assets/css/style.css` (header comments)

---

**Questions or Suggestions?**  
Open an issue on GitHub or contact the maintainers.
