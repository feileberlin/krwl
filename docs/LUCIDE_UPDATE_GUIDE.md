# Lucide Update Guide

**Purpose**: Ensure Lucide icon library updates don't break our icon system.

## 🎯 Our Approach

We use Lucide's UMD build with standard initialization:
- **Library**: `lib/lucide/lucide.min.js` - Official Lucide UMD build
- **Usage**: `assets/js/app.js` - Initialize icons with `lucide.createIcons()`
- **Pattern**: HTML attributes `data-lucide="icon-name"` for declarative icons

This approach means:
✅ **Safe to update Lucide** - We use stable public API
✅ **No build dependencies** - Pure runtime initialization
✅ **Icons load dynamically** - No hardcoded SVG paths

## 📦 How to Update Lucide

### Before Updating

1. **Run compatibility test**:
   ```bash
   python3 tests/test_lucide_compatibility.py
   ```
   This checks:
   - ✅ Only official Lucide API methods used
   - ✅ All icons available in Lucide
   - ✅ No deprecated methods
   - ✅ Proper initialization pattern

2. **Check current version**:
   ```bash
   grep -A 5 '"lucide"' src/modules/site_generator.py
   ```
   Current: `latest` (auto-updates to newest stable)

3. **Review Lucide changelog**:
   - Visit: https://github.com/lucide-icons/lucide/releases
   - Look for API changes, icon renames, or deprecations

### Updating Process

1. **Update version in code** (optional - we use "latest"):
   ```bash
   vim src/modules/site_generator.py
   ```
   Change line 66:
   ```python
   "version": "latest",  # Or pin to specific version like "0.400.0"
   ```

2. **Download new Lucide library**:
   ```bash
   python3 src/event_manager.py libs
   ```
   This fetches:
   - `lucide.min.js` (minified UMD build)
   - `lucide.js` (development UMD build)

3. **Test compatibility**:
   ```bash
   python3 tests/test_lucide_compatibility.py
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
   - ✅ All icons render correctly
   - ✅ Icons have correct colors (CSS theming)
   - ✅ Icon hover effects work
   - ✅ No console errors
   - ✅ Mobile icons visible

### After Updating

1. **Verify all icons render**:
   - Check dashboard menu icons
   - Check filter bar icons
   - Check event detail icons
   - Check navigation icons

2. **Run full test suite**:
   ```bash
   python3 tests/test_components.py
   ```

3. **Update icon list** (if you added new icons):
   ```bash
   vim tests/test_lucide_compatibility.py
   ```
   Add new icon names to `USED_ICONS` set

4. **Commit changes**:
   ```bash
   git add src/modules/site_generator.py lib/lucide/
   git commit -m "chore: Update Lucide to vX.X.X"
   ```

## 🎨 Icons We Use

Current icons in use (update `tests/test_lucide_compatibility.py` when adding):

| Icon Name | Usage | Location |
|-----------|-------|----------|
| `calendar` | Event dates | Event cards |
| `clock` | Time filters | Filter bar |
| `map-pin` | Location | Event details |
| `navigation` | Geolocation | Map controls |
| `filter` | Filter toggle | Filter bar |
| `x` | Close buttons | Modals, popups |
| `menu` | Dashboard toggle | Top bar |
| `info` | Information | Dashboard |
| `settings` | Settings | Dashboard |
| `github` | GitHub link | Footer |
| `external-link` | External URLs | Event links |
| `chevron-down` | Expand | Dropdowns |
| `chevron-up` | Collapse | Dropdowns |
| `search` | Search | Future feature |
| `home` | Home link | Navigation |
| `star` | Favorites | Future feature |
| `heart` | Likes | Future feature |
| `trash` | Delete | Admin actions |
| `edit` | Edit | Admin actions |
| `check` | Confirm | Forms |
| `alert-circle` | Alerts | Notifications |
| `help-circle` | Help | Documentation |

## 🔧 How We Use Lucide

### Method 1: Declarative (Recommended)

```html
<!-- HTML with data-lucide attribute -->
<i data-lucide="calendar"></i>
<i data-lucide="map-pin"></i>

<!-- Icons are automatically replaced on page load -->
<script>
  lucide.createIcons();
</script>
```

**Benefits:**
- ✅ Simple, declarative
- ✅ Automatic replacement
- ✅ No manual SVG handling

### Method 2: Programmatic

```javascript
// Create icon dynamically
const icon = lucide.createElement('calendar');
container.appendChild(icon);
```

**Benefits:**
- ✅ Dynamic icon creation
- ✅ Full control over attributes

### Our Initialization Pattern

```javascript
// In assets/js/app.js
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  } else {
    console.warn('Lucide library not loaded');
  }
});
```

**Safety features:**
- ✅ Checks if Lucide loaded
- ✅ Waits for DOM ready
- ✅ Warns if library missing

## 🎨 Styling Lucide Icons

We style icons with CSS custom properties:

```css
/* Icon theming */
[data-lucide] {
  color: var(--color-text-primary);
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

[data-lucide]:hover {
  color: var(--color-primary);
}
```

**Design tokens used:**
- `--color-text-primary` - Default icon color
- `--color-primary` - Accent/hover color
- `--color-text-secondary` - Muted icons

This means:
- ✅ Instant rebranding (edit config.json)
- ✅ Consistent theming across all icons
- ✅ No hardcoded colors

## 📋 Pre-Update Checklist

Before updating Lucide, verify:

- [ ] Compatibility test passes (`test_lucide_compatibility.py`)
- [ ] Lucide changelog reviewed for breaking changes
- [ ] Current site icons render correctly (baseline)
- [ ] Backup created (`git commit` before updating)

## 📋 Post-Update Checklist

After updating Lucide, verify:

- [ ] Compatibility test still passes
- [ ] All icons render without errors
- [ ] Icons have correct colors and sizes
- [ ] Hover effects work correctly
- [ ] Mobile icons visible
- [ ] No console errors
- [ ] All component tests pass

## 🔧 Troubleshooting

### Issue: Icons don't render after update

**Cause**: Lucide API changed or library didn't load

**Fix 1**: Check console for errors
```javascript
// In browser console
console.log(window.lucide);  // Should show object
```

**Fix 2**: Verify library loaded
```bash
# Check if file exists and has content
ls -lh lib/lucide/lucide.min.js
```

**Fix 3**: Re-download library
```bash
rm -rf lib/lucide/
python3 src/event_manager.py libs
```

### Issue: Some icons missing after update

**Cause**: Lucide renamed or removed icons

**Fix**: Check Lucide changelog for icon renames
```bash
# Find renamed icons in changelog
curl -s https://api.github.com/repos/lucide-icons/lucide/releases/latest \
  | grep -i "renamed\|removed"
```

Update icon names in code:
```html
<!-- Old -->
<i data-lucide="old-name"></i>

<!-- New -->
<i data-lucide="new-name"></i>
```

### Issue: Icons render but styling is wrong

**Cause**: Lucide changed SVG structure or default styles

**Fix**: Update CSS selectors
```css
/* Check new SVG structure */
[data-lucide] svg {
  /* Adjust styles */
}
```

### Issue: Icons too large/small after update

**Cause**: Lucide changed default size or stroke-width

**Fix**: Explicitly set size in CSS
```css
[data-lucide] {
  width: 20px !important;
  height: 20px !important;
  stroke-width: 2;
}
```

## 🚫 Deprecated Patterns

### ❌ Old: lucide.replace()

```javascript
// Deprecated in v0.263.0+
lucide.replace();
```

### ✅ New: lucide.createIcons()

```javascript
// Current method
lucide.createIcons();
```

### ❌ Old: new lucide.Icon()

```javascript
// Deprecated
const icon = new lucide.Icon('calendar');
```

### ✅ New: lucide.createElement()

```javascript
// Current method
const icon = lucide.createElement('calendar');
```

## 📚 Resources

- **Lucide Website**: https://lucide.dev
- **Lucide GitHub**: https://github.com/lucide-icons/lucide
- **Lucide Releases**: https://github.com/lucide-icons/lucide/releases
- **Icon Directory**: https://lucide.dev/icons/
- **API Docs**: https://lucide.dev/guide/packages/lucide
- **Our Usage**: `assets/js/app.js`
- **Design Tokens**: `config.json` (design section)

## 🎯 Version Pinning Strategy

### Current: "latest" (Auto-update)

```python
"version": "latest",
```

**Pros:**
- ✅ Always newest features
- ✅ Automatic bug fixes
- ✅ No manual version bumps

**Cons:**
- ⚠️ Potential breaking changes
- ⚠️ Less predictable

### Alternative: Pin specific version

```python
"version": "0.400.0",
```

**Pros:**
- ✅ Predictable behavior
- ✅ No surprise breaks
- ✅ Controlled updates

**Cons:**
- ⚠️ Manual version management
- ⚠️ Miss bug fixes

**Recommendation**: Use "latest" + run compatibility test frequently

## 🚀 Best Practices

1. **Always test before production** - Update in dev branch first
2. **Use compatibility test** - Catches API changes automatically
3. **Document icon usage** - Update USED_ICONS list when adding icons
4. **Use declarative syntax** - Prefer `data-lucide` over programmatic
5. **Style with tokens** - Use CSS variables, never hardcode colors
6. **Check for renames** - Review changelog for icon name changes
7. **Keep initialization simple** - Don't overcomplicate icon loading

## 📝 Version History

| Lucide Version | Date | Status | Notes |
|----------------|------|--------|-------|
| latest | 2024 | ✅ Current | Using auto-update strategy |

## 🎯 Summary

**Our approach is safe because:**
1. We use **stable public API** (`createIcons()`, `createElement()`)
2. We use **declarative syntax** (data-lucide attributes)
3. We have **safety checks** (library availability)
4. We use **design tokens** for theming
5. We have **automated tests** to catch breaking changes

**Updating Lucide is low-risk when you:**
1. Run compatibility test first
2. Review changelog for breaking changes
3. Test all icons after update
4. Keep icon usage documented
5. Use version pinning if stability critical

This guide ensures Lucide updates are **smooth, safe, and predictable**. 🎉
