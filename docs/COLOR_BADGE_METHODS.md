# Color Badge Comparison - Self-Contained Methods

This document demonstrates multiple self-contained methods for displaying color badges in markdown **without external dependencies**.

## Quick Comparison Table

| Method | GitHub Support | Readability | Visual Quality | Best For |
|--------|----------------|-------------|----------------|----------|
| SVG Data URI | ✅ Excellent | ⚠️ Long URLs | ✅ Perfect | Tables, formal docs |
| HTML `<kbd>` | ⚠️ May be sanitized | ✅ Clean | ✅ Good | Inline text |
| HTML `<pre>` | ⚠️ May be sanitized | ✅ Clean | ✅ Good | Large blocks |
| Unicode `█` | ✅ Works | ✅ Excellent | ❌ No color | Plain text |
| Emoji 🟣 | ✅ Works | ✅ Excellent | ⚠️ Approximate | Informal docs |

---

## Method 1: SVG Data URI (✅ IMPLEMENTED)

**Status:** ✅ Currently used in COLOR_PALETTE.md

### Example Table with SVG Badges

| Color Name | Badge | Hex Code | Usage |
|------------|-------|----------|-------|
| Primary | ![#D689B8](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%23D689B8%22/%3E%3C/svg%3E) | `#D689B8` | Base ecoBarbie color |
| Accent | ![#e07fba](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%23e07fba%22/%3E%3C/svg%3E) | `#e07fba` | Links, info |
| Warning | ![#eb7dc0](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%23eb7dc0%22/%3E%3C/svg%3E) | `#eb7dc0` | Warnings |
| Error | ![#954476](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%23954476%22/%3E%3C/svg%3E) | `#954476` | Errors |
| Tint 50% | ![#eac0da](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%23eac0da%22/%3E%3C/svg%3E) | `#eac0da` | Light backgrounds |
| Shade 50% | ![#6b445c](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2280%22%20height%3D%2220%22%3E%3Crect%20width%3D%2280%22%20height%3D%2220%22%20fill%3D%22%236b445c%22/%3E%3C/svg%3E) | `#6b445c` | Dark accents |

**Pros:**
- ✅ Works reliably in GitHub markdown
- ✅ Self-contained (no external URLs)
- ✅ Displays exact color swatch
- ✅ Can customize size easily

**Cons:**
- ⚠️ Very long URLs in raw markdown
- ⚠️ Not human-readable in source

---

## Method 2: HTML kbd Element with Inline Styles

**Status:** 🧪 Experimental - Testing GitHub sanitization

### Inline Color Swatches

The primary color is <kbd style="background-color: #D689B8; color: black; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#D689B8</kbd> and the accent is <kbd style="background-color: #e07fba; color: black; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#e07fba</kbd>.

### Table with kbd Badges

<table>
<tr><th>Color</th><th>Badge</th><th>Hex</th></tr>
<tr><td>Primary</td><td><kbd style="background-color: #D689B8; color: black; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#D689B8</kbd></td><td><code>#D689B8</code></td></tr>
<tr><td>Accent</td><td><kbd style="background-color: #e07fba; color: black; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#e07fba</kbd></td><td><code>#e07fba</code></td></tr>
<tr><td>Warning</td><td><kbd style="background-color: #eb7dc0; color: black; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#eb7dc0</kbd></td><td><code>#eb7dc0</code></td></tr>
<tr><td>Error</td><td><kbd style="background-color: #954476; color: white; padding: 3px 8px; border-radius: 3px; border: 1px solid #999;">#954476</kbd></td><td><code>#954476</code></td></tr>
</table>

**Pros:**
- ✅ Compact source code
- ✅ Can include text inside badge
- ✅ Auto-adjusts text color (white/black)

**Cons:**
- ⚠️ GitHub may sanitize inline styles
- ⚠️ May not work in all viewers

---

## Method 3: HTML pre Block with Background

**Status:** 🧪 Experimental - Testing GitHub sanitization

### Color Block Examples

<pre style="background-color: #D689B8; color: black; padding: 10px; border-radius: 5px; border: 2px solid #999;"><b>#D689B8</b> - Primary (ecoBarbie)</pre>

<pre style="background-color: #e07fba; color: black; padding: 10px; border-radius: 5px; border: 2px solid #999;"><b>#e07fba</b> - Accent</pre>

<pre style="background-color: #eb7dc0; color: black; padding: 10px; border-radius: 5px; border: 2px solid #999;"><b>#eb7dc0</b> - Warning</pre>

<pre style="background-color: #954476; color: white; padding: 10px; border-radius: 5px; border: 2px solid #999;"><b>#954476</b> - Error</pre>

**Pros:**
- ✅ Large, prominent display
- ✅ Can include description text
- ✅ Clear visual hierarchy

**Cons:**
- ⚠️ Takes more vertical space
- ⚠️ GitHub may strip styles

---

## Method 4: Plain Unicode Blocks

**Status:** ✅ Always works (fallback option)

### Simple Text Format

- `█` #D689B8 - Primary (ecoBarbie)
- `█` #e07fba - Accent
- `█` #eb7dc0 - Warning
- `█` #954476 - Error
- `█` #eac0da - Tint 50%
- `█` #6b445c - Shade 50%

### In a Table

| Symbol | Hex Code | Name |
|--------|----------|------|
| `█` | `#D689B8` | Primary |
| `█` | `#e07fba` | Accent |
| `█` | `#eb7dc0` | Warning |
| `█` | `#954476` | Error |

**Pros:**
- ✅ Works everywhere
- ✅ Extremely clean source
- ✅ Human-readable

**Cons:**
- ❌ No actual color shown
- ⚠️ Relies on terminal/editor for color display

---

## Method 5: Color-Coded Emoji

**Status:** ✅ Always works (informal option)

### Emoji Color Indicators

- 🟣 `#D689B8` - Primary (purple-ish pink)
- 💗 `#e07fba` - Accent (light pink)
- 🎀 `#eb7dc0` - Warning (bright pink)
- 🍷 `#954476` - Error (dark magenta)
- ⬜ `#ffffff` - White (tint 100%)
- ⬛ `#000000` - Black (shade 100%)
- 🟪 `#d6afc7` - Tone 50% (muted purple)

**Pros:**
- ✅ Universal support
- ✅ Fun and approachable
- ✅ No HTML needed

**Cons:**
- ⚠️ Colors are approximate
- ⚠️ Limited emoji color options
- ⚠️ Less professional

---

## Recommendation by Use Case

### For COLOR_PALETTE.md (Current):
✅ **Use Method 1 (SVG Data URI)**
- Most reliable in GitHub
- Professional appearance
- Exact color representation

### For Inline Documentation:
✅ **Use Method 4 (Unicode Blocks)**
- Simple: `█ #D689B8`
- Clean source code
- Works everywhere

### For Quick Reference:
✅ **Use Method 5 (Emoji)**
- Fast to type
- Friendly appearance
- Good for informal docs

### If GitHub Supports Inline Styles:
⚠️ **Use Method 2 (HTML kbd)**
- Best visual quality
- Most compact
- Professional appearance

---

## Testing Instructions

To test which methods GitHub renders correctly:

1. View this file on GitHub.com
2. Compare rendered output with raw markdown
3. Check if inline styles are preserved or sanitized
4. Note which method looks best in your browser

---

## Implementation Status

- [x] Method 1 - SVG Data URI - **IMPLEMENTED** in COLOR_PALETTE.md
- [x] Method 2 - HTML kbd - **DOCUMENTED** (experimental)
- [x] Method 3 - HTML pre - **DOCUMENTED** (experimental)
- [x] Method 4 - Unicode - **DOCUMENTED** (always works)
- [x] Method 5 - Emoji - **DOCUMENTED** (informal)

---

## Related Files

- `COLOR_PALETTE.md` - Main color reference (uses Method 1)
- `config.json` - Design tokens with `_preview_*` keys
- `assets/html/design-tokens.css` - Generated CSS variables
- `src/tools/generate_color_badges.py` - Badge generator script

---

**Last Updated:** 2026-01-19  
**Maintainer:** KRWL> Project
