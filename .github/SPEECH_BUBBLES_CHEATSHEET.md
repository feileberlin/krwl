# 💖 Speech Bubbles Cheat Sheet 💖

> **Quick reference for comic book speech bubble styling in KRWL>**  
> *EcoBarbie-powered design system* 🌸

---

## ✨ The Golden Rules: "ECO-BARBIE BORDERLESS UNIFIED" ✨

### 💕 1. ECO-Barbie Colors ONLY
- **Base**: `#D689B8` (EcoBarbie signature pink)
- **Always**: Use CSS variables (`var(--color-primary)`, `var(--color-shade-50)`)
- **Never**: Hardcode colors outside the spectrum!

### 🎨 2. BORDER-less Design
- **No borders** on bubbles or tails
- **Plain fills** only (white or EcoBarbie tints)
- Tail and bubble **merge seamlessly**

### 🔺 3. UNIFIED Tail Tip
- Both Bezier curves → **single tip point**
- **15px breathing room** from marker circle
- **Triangular tail** shape pointing toward marker

---

## 🌸 EcoBarbie Color Palette

## 🌸 EcoBarbie Color Palette

| Element | Color | Hex | CSS Variable |
|---------|-------|-----|--------------|
| 💖 **Headlines** | EcoBarbie Pink | `#D689B8` | `var(--color-primary)` |
| 📝 **Body Text** | Dark Shade | `#6b445c` | `var(--color-shade-50)` |
| 🎀 **Bookmarked BG** | Light Tint | `#eac0da` | `var(--color-tint-50)` |
| 🤍 **Regular BG** | Pure White | `#ffffff` | `var(--color-white)` |

> 💡 **Pro tip**: Tail fill always matches bubble background!

---

## ⚡ The 3-Second Check

**Before committing speech bubble changes, verify:**

1. 💖 **Colors**: Using EcoBarbie palette variables?
2. 🎨 **Borders**: None on bubble or tail?
3. 🔺 **Tail**: Single unified tip point?
4. ✨ **Shadow**: `filter: drop-shadow()` on parent only?

**All YES?** → 🎉 **You're perfect!**  
**Any NO?** → 📖 Review full guidelines in `copilot-instructions.md`

---

## 🚫 Common Mistakes (and how to fix them!)

### ❌ DON'T DO THIS:
```css
.speech-bubble {
  color: #1a1a2e;                    /* ❌ Not EcoBarbie spectrum! */
  border: 2px solid black;           /* ❌ No borders allowed! */
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* ❌ Creates ugly artifacts! */
}
```

### ✅ DO THIS INSTEAD:
```css
.speech-bubble {
  color: var(--color-shade-50);      /* 💖 EcoBarbie dark shade */
  background: var(--color-white);    /* 🤍 Plain fill, no border */
  filter: drop-shadow(0 2px 12px rgba(0, 0, 0, 0.1));  /* ✨ Unified shadow */
}
```

---

## 🔺 Tail Geometry - The Right Way

### ✅ CORRECT: Single Unified Tip
```javascript
// Both curves end at the SAME point (tipX, tipY)
const tipX = markerIconCenter.x - (dx / distance) * CONNECTOR_STOP_DISTANCE;
const tipY = markerIconCenter.y - (dy / distance) * CONNECTOR_STOP_DISTANCE;

const pathData = `
    M ${startPoint1.x},${startPoint1.y} C ... ${tipX},${tipY}
    M ${startPoint2.x},${startPoint2.y} C ... ${tipX},${tipY}
`;
```
> 🎯 **Result**: Clean triangular tail pointing toward marker!

### ❌ WRONG: Separate Endpoints
```javascript
// Each curve has its own endpoint - creates forked look
const circleEdge1X = markerIconCenter.x - (dx1 / dist1) * CONNECTOR_STOP_DISTANCE;
const circleEdge2X = markerIconCenter.x - (dx2 / dist2) * CONNECTOR_STOP_DISTANCE;
```
> 💥 **Problem**: Looks like a fork, not a comic bubble tail!

---

## 📏 Magic Numbers (Constants)

```javascript
const MARKER_CIRCLE_RADIUS = 50;           // 🎯 Protection circle (200x200px marker)
const CONNECTOR_STOP_DISTANCE = 65;        // ✨ MARKER_CIRCLE_RADIUS + 15 (breathing room)
```

> 💡 **Why 15px gap?** Creates authentic comic book spacing between tail tip and marker!

---

## 📁 Files You'll Edit

**When modifying speech bubbles:**

| File | Purpose | Action |
|------|---------|--------|
| `assets/js/speech-bubbles.js` | 🔺 Tail geometry | Edit source |
| `assets/css/bubbles.css` | 🎨 Styling & colors | Edit source |
| `public/index.html` | 📦 Generated output | Run `generate` command |

**After editing sources, rebuild:**
```bash
python3 src/event_manager.py generate
```

---

## 📚 Need More Details?

**Full documentation:**
- 📖 `.github/copilot-instructions.md` → "Speech Bubble Design Guidelines"
- Includes technical details, anti-patterns, and complete code examples

---

## 🎀 Remember the Mantra!

> **"ECO-BARBIE BORDERLESS UNIFIED"**

**Quick check (all must be YES):**
1. 💖 EcoBarbie colors?
2. 🎨 No borders?
3. 🔺 Unified tip?
4. ✨ Parent shadow?

**Happy EcoBarbie coding!** 🌸💕✨

