# Fix: Demo Events on Production Map

## Problem Statement

Demo events were appearing on the production map at https://feileberlin.github.io/krwl-hof/, which should only show real community events.

## Root Cause

The `config.json` file had `environment: "development"` hardcoded, which forced the system to:
1. Load both real events AND demo events (`data.source: "both"`)
2. Use development mode settings even in production/CI
3. Bypass the automatic environment detection system

## Solution

### 1. Fixed config.json

**Before:**
```json
{
  "environment": "development",
  ...
}
```

**After:**
```json
{
  "environment": "auto",
  ...
}
```

This enables automatic environment detection based on where the code runs:
- **Local Development**: `debug=true`, `data.source="both"` (real + demo events)
- **CI/Production**: `debug=false`, `data.source="real"` (real events only)

### 2. Added Config Validation

Created `scripts/validate_config.py` that:
- ✅ Checks that `environment` is set to `"auto"`
- ✅ Prevents `"development"` or `"production"` hardcoding
- ✅ Provides clear error messages when validation fails

**Usage:**
```bash
python3 scripts/validate_config.py
```

### 3. Added CI Integration

Created `.github/workflows/config-validation.yml` that:
- ✅ Runs automatically on every PR touching config.json
- ✅ Blocks PRs if validation fails
- ✅ Prevents demo events from reaching production

### 4. Added Tests

Created `tests/test_config_validation.py` that verifies:
- ✅ Validation passes with `environment: "auto"`
- ✅ Validation rejects `environment: "development"`
- ✅ Validation rejects `environment: "production"`

### 5. Updated Documentation

- ✅ Updated `.github/copilot-instructions.md` with config validation section
- ✅ Updated `scripts/README.md` with validation usage
- ✅ Added config validation to checklists

## Verification

### Before Fix
```json
// In public/index.html
{
  "data": {
    "source": "both",  // ❌ Wrong: loads demo events
    ...
  },
  "debug": true  // ❌ Wrong: development mode in production
}
```

### After Fix
```json
// In public/index.html
{
  "data": {
    "source": "real",  // ✅ Correct: only real events
    ...
  },
  "debug": false  // ✅ Correct: production mode
}
```

### Test Results
```
✅ Config validation passes
✅ All config validation tests pass
✅ Data source is 'real' (not 'both')
✅ No [DEMO] events in HTML (0 found)
✅ Environment auto-detected as 'ci' (not forced to 'development')
```

## Prevention Mechanism

This issue is now prevented by multiple layers:

1. **Config Validation Script**: Catches environment issues before commit
2. **CI Workflow**: Automatically validates config.json on every PR
3. **Tests**: Ensures validation logic works correctly
4. **Documentation**: Clear guidelines in copilot instructions and READMEs
5. **Error Messages**: Helpful feedback when validation fails

## How This Could Happen

The issue occurred because:
1. Someone manually set `environment: "development"` in config.json for testing
2. The change was committed and pushed without running validation
3. The CI system built the site with development settings
4. Demo events were included in the production build

## Prevention for Future

To prevent similar issues:

### For Developers
```bash
# ALWAYS run before committing config.json changes
python3 scripts/validate_config.py
```

### For Reviewers
- Check that config.json has `environment: "auto"`
- Verify CI validation passed
- Look for `[DEMO]` in PR diffs

### For CI/CD
- GitHub Actions automatically blocks PRs with invalid config
- No manual intervention needed

## Related Files

- `config.json` - Fixed environment setting
- `scripts/validate_config.py` - Validation script
- `.github/workflows/config-validation.yml` - CI workflow
- `tests/test_config_validation.py` - Test suite
- `.github/copilot-instructions.md` - Updated documentation
- `scripts/README.md` - Updated documentation
- `public/index.html` - Regenerated without demo events

## Impact

- ✅ Production map now shows only real events
- ✅ Development environment still has demo events for testing
- ✅ Future changes are protected by automated validation
- ✅ Clear error messages guide developers to fix issues
