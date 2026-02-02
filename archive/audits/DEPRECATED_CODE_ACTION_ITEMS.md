# Deprecated Code - Action Items

**Date:** 2026-01-29  
**Based On:** DEPRECATED_CODE_AUDIT.md

This document provides actionable steps to address deprecated code findings.

---

## Priority 1: Documentation Corrections (No Code Changes)

### 1.1 Update Telegram Bot References

**File:** `docs/TELEGRAM_INTEGRATION.md` (line 257)

**Current:** References `src/modules/telegram_bot.py` (doesn't exist)  
**Should Be:** `src/modules/telegram_bot_simple.py` (actual file)

**Action:**
```bash
# Edit docs/TELEGRAM_INTEGRATION.md line 257
# Change: "src/modules/telegram_bot.py"
# To: "src/modules/telegram_bot_simple.py"
```

---

## Priority 2: Remove Dead Comments (Safe Cleanup)

### 2.1 Remove WEATHER_CACHE Comment

**File:** `src/modules/site_generator.py` (line 1832)  
**Impact:** None - This is just a comment

**Current:**
```python
# Note: WEATHER_CACHE is now deprecated, weather data is in APP_CONFIG.weather.data
```

**Action:** 
```bash
# Remove the comment after verifying no code references WEATHER_CACHE variable
grep -r "WEATHER_CACHE" src/ assets/ --exclude="*.pyc"
# If no references, remove the comment
```

**Verification Required:** Confirm no JavaScript code reads `window.WEATHER_CACHE`

---

### 2.2 Remove Config Loader Placeholder Comment

**File:** `src/modules/site_generator.py` (line 1893)  
**Impact:** None - Just a comment

**Current:**
```python
# Config loader and fetch interceptor (legacy placeholders - not currently used)
config_loader = ''
fetch_interceptor = ''
```

**Action:**
```bash
# If config_loader and fetch_interceptor are truly unused:
# 1. Remove the comment
# 2. Remove the empty variable assignments
# 3. Check if they're referenced elsewhere in the file
```

---

### 2.3 Remove Deprecated CSS Comment

**File:** `assets/css/style.css` (line 1722)  
**Impact:** None - Just a comment

**Current:**
```css
/* Details/Summary for Size Breakdown (deprecated - now using table) */
```

**Action:**
```bash
# Check if there are associated styles below this comment
# If not, remove the comment entirely
```

---

## Priority 3: CSS Cleanup (After Verification)

### 3.1 Remove Legacy Filter Class Support

**File:** `assets/css/filters.css` (lines 74-85)  
**Impact:** Low - Only if class is truly unused

**Finding:** `.filter-bar-item` class is NOT used in any JS or HTML files

**Current:**
```css
/* Legacy support for .filter-bar-item class (deprecated) */
#event-filter-bar .filter-bar-item {
    cursor: pointer;
    text-decoration: underline;
    /* ... more styles ... */
}
```

**Action:**
```bash
# Verification shows 0 uses of .filter-bar-item
# Safe to remove entire block (lines 74-85)
```

**Risk:** Low - Grep confirms class is not used

---

## Priority 4: Future Major Version (v2.0)

These changes should wait for a major version bump as they break backward compatibility.

### 4.1 Remove Deprecated Archive Command

**File:** `src/event_manager.py` (line 435)  
**Impact:** Medium - Command still works, users may rely on it

**Current:**
```python
archive                   Archive past events to archived_events.json (legacy)
```

**Action for v2.0:**
1. Remove `archive` command from CLI
2. Keep only `archive-monthly`
3. Update all documentation
4. Add deprecation warning in v1.x releases first

**Migration Path:**
```python
# v1.x: Add warning
if command == "archive":
    print("⚠️  WARNING: 'archive' is deprecated. Use 'archive-monthly' instead.")
    # Still execute old behavior

# v2.0: Remove entirely
```

---

### 4.2 Remove Deprecated JavaScript Method

**File:** `assets/js/map.js` (line 267)  
**Impact:** Low - Method is called internally but redirects to new method

**Finding:** `addUserMarker()` is called once at line 223 in same file

**Current:**
```javascript
/**
 * @deprecated Use updateReferenceMarker() instead for better control
 */
addUserMarker() {
    // Redirects to updateReferenceMarker()
}
```

**Action for v2.0:**
1. Update call site at line 223:
   ```javascript
   // Old:
   this.addUserMarker();
   
   // New:
   this.updateReferenceMarker(
       this.userLocation.lat, 
       this.userLocation.lon, 
       'You are here'
   );
   ```

2. Remove `addUserMarker()` method entirely

**Risk:** Low - Only internal usage found

---

### 4.3 Remove Deprecated Config Keys

**Files:** `config.json`, validation schemas  
**Impact:** Medium - May break old configs

**Keys to Remove:**
- `watermark.text` - No longer displayed in UI (replaced by dashboard)
- Backward compatibility for `NODE_ENV` - Keep only `ENVIRONMENT`

**Action for v2.0:**
1. Add migration guide
2. Remove from config schema
3. Remove from validation
4. Update documentation

**Migration Path:**
```markdown
# Config Migration Guide v1.x → v2.0

## Removed Keys
- `watermark.text` → Use dashboard menu instead (no config needed)
- `NODE_ENV` → Use `ENVIRONMENT` instead
```

---

## Priority 5: No Action Needed

These items are **working as intended** and should be kept:

### 5.1 SmartScraper Legacy Fallback ✅

**Files:** 
- `src/modules/scraper.py` (lines 288-289)
- `src/modules/smart_scraper/core.py` (lines 236, 337, 347-351)

**Reason:** Intentional safety mechanism for backward compatibility  
**Action:** KEEP

---

### 5.2 Archive Directory ✅

**Location:** `/archive/`  
**Contents:** Legacy JS, docs, images, JSON backups

**Reason:** Excellent historical reference, properly isolated  
**Action:** KEEP

---

### 5.3 Cleanup Tools ✅

**Files:**
- `src/tools/cleanup_obsolete.py`
- `src/tools/cleanup_old_docs.py`

**Reason:** Active utilities for maintenance  
**Action:** KEEP and use periodically

---

### 5.4 Deprecation Tests ✅

**File:** `tests/test_lucide_compatibility.py`

**Reason:** Prevents future deprecated code introduction  
**Action:** KEEP

---

## Implementation Plan

### Phase 1: Safe Cleanup (This PR)

1. ✅ Create audit report (DEPRECATED_CODE_AUDIT.md)
2. ✅ Create action items (this document)
3. Update telegram bot documentation reference
4. Remove dead comments (after verification)
5. Remove unused CSS class support (verified unused)

**Timeline:** Immediate  
**Risk:** None - Documentation and comment cleanup only

---

### Phase 2: v1.x Releases (Add Warnings)

Add deprecation warnings for features planned for removal:

```python
# In CLI commands
if command == "archive":
    print("⚠️  DEPRECATION WARNING: 'archive' command will be removed in v2.0")
    print("    Use 'archive-monthly' instead")
```

**Timeline:** Next minor release  
**Risk:** None - Warnings only

---

### Phase 3: v2.0 (Breaking Changes)

1. Remove deprecated commands
2. Remove deprecated JavaScript methods
3. Remove deprecated config keys
4. Update all documentation
5. Provide migration guide

**Timeline:** Next major version  
**Risk:** Medium - Breaking changes require user migration

---

## Testing Requirements

### For Phase 1 (Safe Cleanup)

```bash
# 1. Verify no references to removed items
grep -r "filter-bar-item" src/ assets/ tests/
grep -r "WEATHER_CACHE" src/ assets/ --exclude="*.pyc"

# 2. Run existing tests
python3 tests/test_lucide_compatibility.py --verbose
python3 tests/test_event_schema.py --verbose

# 3. Build and verify
python3 src/event_manager.py generate
# Check that public/index.html builds successfully

# 4. Manual verification
# - Open public/index.html in browser
# - Check console for errors
# - Verify filters work correctly
# - Verify map displays correctly
```

---

## Summary

**Safe to Do Now (Phase 1):**
- ✅ Update documentation references
- ✅ Remove dead comments (3 files)
- ✅ Remove unused CSS class support (1 file)

**Do in Next Minor Release (Phase 2):**
- Add deprecation warnings for v2.0 removals

**Do in Next Major Release (Phase 3):**
- Remove deprecated commands
- Remove deprecated methods
- Remove deprecated config keys
- Provide migration guide

**Keep Forever:**
- Archive directory (historical reference)
- Legacy fallback mechanisms (backward compatibility)
- Cleanup tools (active utilities)
- Deprecation tests (quality assurance)

---

## Conclusion

The codebase is in **excellent shape** regarding deprecated code:
- Only minor documentation and comment cleanup needed now
- Clear path for future major version cleanup
- All "legacy" code is either intentional or archived
- No urgent technical debt

**Recommendation:** Proceed with Phase 1 safe cleanup in this PR.
