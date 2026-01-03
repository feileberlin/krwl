# Leaflet Update Guide

**Purpose**: Ensure Leaflet library updates don't break our custom theming.

## 🎯 Our Approach

We follow Leaflet's official customization pattern:
- **Core CSS**: `lib/leaflet/leaflet.css` - Handles functionality (position, layout, mechanics)
- **Custom CSS**: `assets/css/leaflet-custom.css` - Handles theming (colors, shadows, borders)

This separation means:
✅ **Safe to update Leaflet core** - Functional CSS won't conflict with our theme
✅ **Safe to rebrand** - Our custom CSS only touches visual properties
✅ **No breakage** - We don't override positioning, sizing, or z-index

## 📦 How to Update Leaflet

### Before Updating

1. **Run compatibility test**:
   ```bash
   python3 tests/test_leaflet_compatibility.py
   ```
   This checks:
   - ✅ Only official Leaflet classes used
   - ✅ No dangerous property overrides
   - ✅ No `!important` conflicts
   - ✅ CSS variables used properly

2. **Check current version**:
   ```bash
   grep -A 5 '"leaflet"' src/modules/site_generator.py
   ```
   Current: `1.9.4`

3. **Review Leaflet changelog**:
   - Visit: https://github.com/Leaflet/Leaflet/blob/main/CHANGELOG.md
   - Look for CSS class changes or deprecations

### Updating Process

1. **Update version in code**:
   ```bash
   vim src/modules/site_generator.py
   ```
   Change line 55:
   ```python
   "version": "1.9.4",  # Update this number
   ```

2. **Download new Leaflet files**:
   ```bash
   python3 src/event_manager.py libs
   ```
   This fetches:
   - `leaflet.css` (core styles)
   - `leaflet.js` (library)
   - Marker images (icon-*.png)

3. **Test compatibility**:
   ```bash
   python3 tests/test_leaflet_compatibility.py
   ```
   Must pass with no errors!

4. **Rebuild site**:
   ```bash
   python3 src/event_manager.py generate
   ```

5. **Manual testing**:
   ```bash
   cd public && python3 -m http.server 8000
   ```
   Test:
   - ✅ Map loads correctly
   - ✅ Markers display with pink glow
   - ✅ Popups have dark theme
   - ✅ Zoom controls visible
   - ✅ No console errors

### After Updating

1. **Verify visual appearance**:
   - Screenshot before/after
   - Check marker hover effects
   - Check popup styling
   - Check mobile responsiveness

2. **Run full test suite**:
   ```bash
   python3 tests/test_components.py
   ```

3. **Update documentation**:
   ```bash
   # Update this file with new version number
   vim docs/LEAFLET_UPDATE_GUIDE.md
   ```

4. **Commit changes**:
   ```bash
   git add src/modules/site_generator.py lib/leaflet/
   git commit -m "chore: Update Leaflet to vX.X.X"
   ```

## 🛡️ What We Customize (Safe)

### Visual Properties Only

```css
/* ✅ SAFE: Visual customization */
.leaflet-popup-content-wrapper {
    background: var(--color-bg-secondary);      /* Color */
    color: var(--color-text-primary);           /* Color */
    border: 2px solid var(--color-border-primary);  /* Border */
}

.leaflet-marker-icon {
    filter: drop-shadow(0 0 2px var(--color-primary));  /* Effect */
}
```

These properties are **purely visual** and don't affect Leaflet's functionality.

## 🚫 What We DON'T Override (Dangerous)

### Functional Properties

```css
/* ❌ DANGEROUS: Never override these */
.leaflet-container {
    /* position: absolute;  ← DON'T TOUCH */
    /* width: 100%;         ← DON'T TOUCH */
    /* height: 100%;        ← DON'T TOUCH */
    /* z-index: 0;          ← DON'T TOUCH */
    /* overflow: hidden;    ← DON'T TOUCH */
}

.leaflet-marker-icon {
    /* position: absolute;  ← DON'T TOUCH */
    /* transform: translate3d(...);  ← DON'T TOUCH */
    /* pointer-events: auto;  ← DON'T TOUCH */
}
```

These properties control **functionality** and would break map mechanics.

## 📋 Pre-Update Checklist

Before updating Leaflet, verify:

- [ ] Compatibility test passes (`test_leaflet_compatibility.py`)
- [ ] Leaflet changelog reviewed for breaking changes
- [ ] Current site works correctly (baseline)
- [ ] Backup created (`git commit` before updating)

## 📋 Post-Update Checklist

After updating Leaflet, verify:

- [ ] Compatibility test still passes
- [ ] Map loads without console errors
- [ ] Markers display correctly with pink glow
- [ ] Popups styled with dark theme
- [ ] Zoom controls visible and functional
- [ ] Mobile view works correctly
- [ ] No visual regressions (compare screenshots)
- [ ] All component tests pass

## 🔧 Troubleshooting

### Issue: Popups look wrong after update

**Cause**: Leaflet changed popup HTML structure

**Fix**: Update selectors in `assets/css/leaflet-custom.css`
```bash
# Check Leaflet's new structure
vim lib/leaflet/leaflet.css
# Search for .leaflet-popup

# Update our custom CSS accordingly
vim assets/css/leaflet-custom.css
```

### Issue: Markers don't have glow effect

**Cause**: Leaflet changed marker class structure

**Fix**: Update marker styling
```css
/* Old */
.leaflet-marker-icon {
    filter: drop-shadow(...);
}

/* New - check Leaflet CSS for current class name */
.leaflet-marker-icon-new-class {
    filter: drop-shadow(...);
}
```

### Issue: Z-index conflicts

**Cause**: Leaflet changed internal z-index values

**Fix**: Update z-index tokens in `config.json`
```json
{
  "design": {
    "z_index": {
      "layer_2_leaflet_popup": 700,  // Update based on Leaflet's new values
      "layer_2_leaflet_tooltip": 650,
      ...
    }
  }
}
```

## 📚 Resources

- **Leaflet Documentation**: https://leafletjs.com/reference.html
- **Leaflet GitHub**: https://github.com/Leaflet/Leaflet
- **Leaflet Changelog**: https://github.com/Leaflet/Leaflet/blob/main/CHANGELOG.md
- **Our Customizations**: `assets/css/leaflet-custom.css`
- **Design Tokens**: `config.json` (design section)

## 🎨 Design Token Integration

All Leaflet customizations use CSS variables from `config.json`:

```json
{
  "design": {
    "colors": {
      "primary": "#FF69B4",           // Marker glow color
      "bg_secondary": "#161b22",      // Popup background
      "border_primary": "#30363d",    // Popup border
      ...
    }
  }
}
```

This means:
- ✅ Instant rebranding (just edit config.json)
- ✅ Consistent theming across all Leaflet elements
- ✅ No hardcoded colors in CSS

## 🚀 Best Practices

1. **Always test before production** - Update in dev branch first
2. **Use compatibility test** - Catches 90% of issues automatically
3. **Document version** - Keep version number in site_generator.py up-to-date
4. **Keep customizations minimal** - Less custom CSS = fewer conflicts
5. **Use design tokens** - Never hardcode colors or values
6. **Separate concerns** - Core functionality (Leaflet) vs theme (our CSS)

## 📝 Version History

| Leaflet Version | Date | Status | Notes |
|-----------------|------|--------|-------|
| 1.9.4 | 2024 | ✅ Current | Initial component system version |

## 🎯 Summary

**Our approach is safe because:**
1. We only customize **visual properties** (colors, borders, shadows)
2. We never touch **functional properties** (position, size, z-index)
3. We use **official Leaflet classes** only
4. We use **CSS variables** for easy updates
5. We have **automated tests** to catch conflicts

**Updating Leaflet is low-risk when you:**
1. Run compatibility test first
2. Review changelog for breaking changes
3. Test thoroughly after update
4. Keep customizations minimal

This guide ensures Leaflet updates are **smooth, safe, and predictable**. 🎉
