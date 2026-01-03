# Third-Party Dependency Update Guide

**Purpose**: Master guide for updating all third-party libraries safely.

## 📚 Dependencies We Use

| Library | Version | Purpose | Update Guide |
|---------|---------|---------|--------------|
| **Leaflet** | 1.9.4 | Interactive maps | [LEAFLET_UPDATE_GUIDE.md](LEAFLET_UPDATE_GUIDE.md) |
| **Lucide** | latest | Icon library | [LUCIDE_UPDATE_GUIDE.md](LUCIDE_UPDATE_GUIDE.md) |

## 🎯 Update Philosophy

### Our Approach

We follow **runtime dependency** pattern:
- ✅ **No build step** - Libraries loaded at runtime
- ✅ **CDN fallback** - Download from unpkg.com
- ✅ **Version pinning** - Control when to update
- ✅ **Automated testing** - Catch breaking changes early

### Why This Matters

Third-party updates can break:
- 🔴 **API changes** - Methods renamed or removed
- 🔴 **CSS conflicts** - Style changes break our theming
- 🔴 **Breaking changes** - Major version bumps
- 🔴 **File structure** - Moved or renamed files

Our system prevents these issues!

## 🔧 Universal Update Process

### 1. Pre-Update Checks

```bash
# Check current versions
grep -A 10 'DEPENDENCIES' src/modules/site_generator.py

# Run all compatibility tests
python3 tests/test_leaflet_compatibility.py
python3 tests/test_lucide_compatibility.py

# Create backup
git add . && git commit -m "backup: Before dependency update"
```

### 2. Review Changelogs

**Leaflet:**
- https://github.com/Leaflet/Leaflet/blob/main/CHANGELOG.md

**Lucide:**
- https://github.com/lucide-icons/lucide/releases

Look for:
- ⚠️ BREAKING CHANGES
- ⚠️ Deprecated methods
- ⚠️ Renamed classes/methods
- ✅ Bug fixes
- ✅ New features

### 3. Update Version Number

```bash
vim src/modules/site_generator.py
```

Edit the `DEPENDENCIES` dict:
```python
DEPENDENCIES = {
    "leaflet": {
        "version": "1.9.4",  # Update this
        ...
    },
    "lucide": {
        "version": "latest",  # Or pin to "0.400.0"
        ...
    }
}
```

### 4. Download New Version

```bash
# Clean old files
rm -rf lib/leaflet/ lib/lucide/

# Download new versions
python3 src/event_manager.py libs

# Verify download
ls -lh lib/leaflet/
ls -lh lib/lucide/
```

### 5. Run Tests

```bash
# Compatibility tests (library-specific)
python3 tests/test_leaflet_compatibility.py
python3 tests/test_lucide_compatibility.py

# Component tests (integration)
python3 tests/test_components.py

# Full site generation
python3 src/event_manager.py generate
```

### 6. Manual Testing

```bash
# Start local server
cd public && python3 -m http.server 8000
```

**Test checklist:**
- [ ] Map loads correctly
- [ ] Markers display with effects
- [ ] Popups styled correctly
- [ ] Icons render (all of them)
- [ ] Mobile view works
- [ ] No console errors
- [ ] Filters work
- [ ] Dashboard opens
- [ ] Time drawer functions

### 7. Commit Changes

```bash
git add src/modules/site_generator.py static/
git commit -m "chore: Update Leaflet to vX.X.X and Lucide to vX.X.X"
git push
```

## 🧪 Testing Matrix

| Test | Leaflet | Lucide | Purpose |
|------|---------|--------|---------|
| **Compatibility** | ✅ | ✅ | API usage validation |
| **Components** | ✅ | ✅ | Integration testing |
| **Manual** | ✅ | ✅ | Visual verification |
| **Console** | ✅ | ✅ | Error detection |

## 🎨 Customization Safety

### What We Can Safely Override

**Leaflet:**
```css
/* ✅ SAFE: Visual properties only */
.leaflet-popup-content-wrapper {
  background: var(--color-bg-secondary);  /* Theme color */
  border: 2px solid var(--color-primary); /* Theme border */
}
```

**Lucide:**
```css
/* ✅ SAFE: Icon styling */
[data-lucide] {
  color: var(--color-text-primary);  /* Theme color */
  width: 20px;                       /* Size */
}
```

### What We MUST NOT Override

**Leaflet:**
```css
/* ❌ DANGEROUS: Functional properties */
.leaflet-container {
  position: absolute;  /* DON'T TOUCH - breaks map */
  z-index: 0;         /* DON'T TOUCH - breaks layering */
}
```

**Lucide:**
```javascript
// ❌ DANGEROUS: Monkey-patching
window.lucide.createIcons = function() { ... };  // DON'T DO THIS
```

## 📋 Complete Pre-Update Checklist

Run through this before ANY dependency update:

- [ ] **Backup**: Commit current working state
- [ ] **Changelog**: Read for breaking changes
- [ ] **Tests**: Run all compatibility tests (baseline)
- [ ] **Document**: Note current versions
- [ ] **Branch**: Create update branch (`git checkout -b update/leaflet-2.0`)

## 📋 Complete Post-Update Checklist

After updating ANY dependency:

- [ ] **Compatibility**: All tests pass
- [ ] **Components**: Integration tests pass
- [ ] **Generation**: Site builds successfully
- [ ] **Manual**: Visual testing complete
- [ ] **Console**: No errors in browser
- [ ] **Mobile**: Responsive layout works
- [ ] **Commit**: Changes committed with clear message
- [ ] **Document**: Update version history in guides

## 🚨 Rollback Procedure

If update breaks something:

```bash
# Option 1: Git revert (recommended)
git revert HEAD
git push

# Option 2: Git reset (if not pushed yet)
git reset --hard HEAD~1

# Option 3: Restore specific files
git checkout HEAD~1 -- src/modules/site_generator.py
git checkout HEAD~1 -- lib/leaflet/
git checkout HEAD~1 -- lib/lucide/

# Rebuild
python3 src/event_manager.py generate
```

## 🔧 Troubleshooting

### Issue: Tests pass but site breaks

**Cause**: Tests don't cover edge case

**Fix**: Enhance test coverage
```bash
# Add test case
vim tests/test_leaflet_compatibility.py
# or
vim tests/test_lucide_compatibility.py
```

### Issue: CDN download fails

**Cause**: unpkg.com down or URL changed

**Fix**: Use alternative CDN
```python
# Edit site_generator.py
"base_url": "https://cdn.jsdelivr.net/npm/leaflet@{version}/dist",
```

### Issue: Version incompatibility

**Cause**: New version has breaking changes

**Fix**: Pin to older version
```python
"version": "1.9.4",  # Stay on known-good version
```

## 📚 Dependency Documentation

### Leaflet

- **Website**: https://leafletjs.com
- **GitHub**: https://github.com/Leaflet/Leaflet
- **Docs**: https://leafletjs.com/reference.html
- **CDN**: https://unpkg.com/leaflet@{version}/dist/
- **Our Guide**: [LEAFLET_UPDATE_GUIDE.md](LEAFLET_UPDATE_GUIDE.md)

### Lucide

- **Website**: https://lucide.dev
- **GitHub**: https://github.com/lucide-icons/lucide
- **Docs**: https://lucide.dev/guide/packages/lucide
- **CDN**: https://unpkg.com/lucide@{version}/
- **Our Guide**: [LUCIDE_UPDATE_GUIDE.md](LUCIDE_UPDATE_GUIDE.md)

## 🎯 Version Strategy

### Semantic Versioning Primer

```
vMAJOR.MINOR.PATCH
 1.9.4
 │ │ │
 │ │ └─ Patch: Bug fixes (safe to update)
 │ └─── Minor: New features (usually safe)
 └───── Major: Breaking changes (REVIEW REQUIRED)
```

### Our Strategy

| Bump Type | Action | Risk Level |
|-----------|--------|------------|
| **Patch** (1.9.4 → 1.9.5) | Auto-update | 🟢 Low |
| **Minor** (1.9.4 → 1.10.0) | Review + Test | 🟡 Medium |
| **Major** (1.9.4 → 2.0.0) | Full audit | 🔴 High |

## 🚀 Best Practices

1. **Test locally first** - Never update directly in production
2. **Read changelogs** - Know what's changing before update
3. **Run tests** - Automated tests catch 90% of issues
4. **Version pinning** - Control when updates happen
5. **Document versions** - Keep version history updated
6. **Rollback plan** - Know how to revert if needed
7. **Gradual updates** - Update one dependency at a time

## 📝 Update Log Template

When updating dependencies, document it:

```markdown
## [Date] - Dependency Update

**Updated:**
- Leaflet: 1.9.4 → 1.9.5
- Lucide: 0.395.0 → 0.400.0

**Reason:**
- Security patch in Leaflet
- New icons in Lucide

**Testing:**
- ✅ Compatibility tests pass
- ✅ Component tests pass
- ✅ Manual testing complete
- ✅ No console errors

**Breaking Changes:**
None

**Migration Steps:**
N/A

**Rollback:**
`git revert abc123` if issues found
```

## 🎯 Summary

**Safe dependency updates require:**
1. ✅ **Automated testing** - Catch issues early
2. ✅ **Version control** - Know exactly what changed
3. ✅ **Documentation** - Understand our usage patterns
4. ✅ **Gradual approach** - One update at a time
5. ✅ **Rollback plan** - Quick recovery if needed

**This system ensures:**
- 🎉 **Zero downtime** - Issues caught before deployment
- 🎉 **Confidence** - Know updates won't break production
- 🎉 **Speed** - Automated tests run in seconds
- 🎉 **Control** - Update on your schedule, not forced

With proper testing and documentation, **dependency updates are low-risk, high-value activities**! 🚀
