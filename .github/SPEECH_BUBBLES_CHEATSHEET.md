# Speech Bubbles Cheat Sheet 🎯

**Quick reference for comic book speech bubble styling in KRWL HOF**

## The Golden Rules: "ECO-BARBIE BORDERLESS UNIFIED"

### 1. ECO-Barbie Colors ONLY ✨
- Base: `#D689B8` (EcoBarbie pink)
- Use CSS variables: `var(--color-primary)`, `var(--color-shade-50)`, etc.
- **Never hardcode colors!**

### 2. BORDER-less Design 🚫
- No borders on bubbles or tails
- Plain color fills only
- Tail and bubble merge seamlessly

### 3. UNIFIED Tail Tip 📍
- Both Bezier curves → single tip point
- 15px breathing room from marker
- Triangular tail shape

---

## Quick Color Guide

| Element | Color | CSS Variable |
|---------|-------|--------------|
| Regular bubble background | White | `var(--color-white)` |
| Bookmarked bubble background | Light pink | `var(--color-tint-50)` |
| Body text | Dark gray-pink | `var(--color-shade-50)` |
| Headlines | EcoBarbie pink | `var(--color-primary)` |
| Tail fill | Matches bubble | Same as bubble bg |

---

## The 3-Second Check ✅

Before committing speech bubble changes, ask:

1. ✅ **Colors**: Using EcoBarbie palette variables?
2. ✅ **Borders**: None on bubble or tail?
3. ✅ **Tail**: Single unified tip point?
4. ✅ **Shadow**: `filter: drop-shadow()` on parent only?

**All YES?** → You're good to go! 🎉  
**Any NO?** → Review full guidelines in `copilot-instructions.md`

---

## Common Mistakes ❌

### ❌ DON'T:
```css
.speech-bubble {
  color: #1a1a2e;                    /* ❌ Not EcoBarbie spectrum */
  border: 2px solid black;           /* ❌ No borders allowed */
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);  /* ❌ Creates artifacts */
}
```

### ✅ DO:
```css
.speech-bubble {
  color: var(--color-shade-50);      /* ✅ EcoBarbie dark shade */
  background: var(--color-white);    /* ✅ Plain fill, no border */
  filter: drop-shadow(0 2px 12px rgba(0, 0, 0, 0.1));  /* ✅ Unified shadow */
}
```

---

## Tail Geometry Quick Reference

```javascript
// ✅ CORRECT: Single unified tip
const tipX = markerIconCenter.x - (dx / distance) * CONNECTOR_STOP_DISTANCE;
const tipY = markerIconCenter.y - (dy / distance) * CONNECTOR_STOP_DISTANCE;

// Both curves end at (tipX, tipY)
const pathData = `
    M ${startPoint1.x},${startPoint1.y} C ... ${tipX},${tipY}
    M ${startPoint2.x},${startPoint2.y} C ... ${tipX},${tipY}
`;
```

```javascript
// ❌ WRONG: Separate endpoints
const circleEdge1X = markerIconCenter.x - (dx1 / dist1) * CONNECTOR_STOP_DISTANCE;
const circleEdge2X = markerIconCenter.x - (dx2 / dist2) * CONNECTOR_STOP_DISTANCE;
// Creates forked look instead of pointed tail
```

---

## Constants

```javascript
const MARKER_CIRCLE_RADIUS = 50;           // Protection circle around 200x200px marker
const CONNECTOR_STOP_DISTANCE = 65;        // MARKER_CIRCLE_RADIUS + 15 (breathing room)
```

---

## Files to Edit

When modifying speech bubbles:
- **Source**: `assets/js/speech-bubbles.js` (tail geometry)
- **Source**: `assets/css/bubbles.css` (styling)
- **Generated**: `public/index.html` (run `python3 src/event_manager.py generate` to rebuild)

---

## Need More Details?

See full documentation in:
- `.github/copilot-instructions.md` → "Speech Bubble Design Guidelines"
- Includes technical details, anti-patterns, and complete examples

---

**Remember**: When in doubt, check these 4 things:
1. EcoBarbie colors? ✅
2. No borders? ✅
3. Unified tip? ✅
4. Parent shadow? ✅

Happy coding! 🚀
