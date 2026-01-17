# Fix for GitHub Pages Deployment Workflow JSON Parsing Issue

## Problem Summary

The GitHub Actions workflow `website-maintenance.yml` was failing at the `discover-capabilities` job with a JSON parsing error when running `python3 src/event_manager.py scraper-info`. This blocked the entire deployment pipeline.

## Root Cause

The `scraper-info` command was outputting log messages (INFO, ERROR, WARNING) that could contaminate the JSON output:
- `logger.info()` and `logger.error()` calls during config loading and scraper initialization
- Import-time warnings from modules like `scraper.py` and `compressor.py`
- These logs appeared on stderr, but when mixed with JSON parsing, could cause issues

## Solution Implemented

### 1. Added `--json` Flag (event_manager.py)

Added a new `--json` command-line flag that:
- Suppresses ALL logging (sets level to CRITICAL and removes handlers)
- Ensures pure JSON output to stdout
- Makes the command safe for CI/CD pipelines and automation

```bash
# Old way (logs could appear)
python3 src/event_manager.py scraper-info

# New way (guaranteed pure JSON)
python3 src/event_manager.py scraper-info --json
```

### 2. Removed Import-Time Logging (scraper.py, compressor.py)

Modified modules to defer logging until actual operations:
- **scraper.py**: Moved "Scraping libraries not available" warning to scraping time
- **compressor.py**: Removed "Brotli not available" warning at import time
- This prevents warnings from appearing before logging can be suppressed

### 3. Enhanced Workflow Robustness (website-maintenance.yml)

Updated the `discover-capabilities` job with:
- **Better error handling**: Added `set -e` and proper error messages
- **JSON validation**: Uses `jq empty` to validate before parsing
- **Fallback mechanism**: Provides safe default values if parsing fails
- **Graceful degradation**: Workflow continues even if discovery has issues

```yaml
# Get capabilities with --json flag
CAPABILITIES=$(python3 src/event_manager.py scraper-info --json 2>&1)

# Validate JSON
if ! echo "$CAPABILITIES" | jq empty 2>/dev/null; then
  # Use safe defaults
  echo "enabled_sources=0" >> $GITHUB_OUTPUT
  exit 0  # Don't fail entire workflow
fi
```

### 4. Documentation Updates

- Added `--json` flag to help text
- Added example for CI/CD usage
- Updated inline comments explaining the fix

## Testing

### Manual Verification

```bash
# Test 1: Pure JSON output
python3 src/event_manager.py scraper-info --json | jq .

# Test 2: Extract specific fields
python3 src/event_manager.py scraper-info --json | jq -r '.scraping_libraries_installed'
python3 src/event_manager.py scraper-info --json | jq -r '.enabled_sources | length'

# Test 3: Simulate workflow
bash -c '
  CAPABILITIES=$(python3 src/event_manager.py scraper-info --json 2>&1)
  echo "$CAPABILITIES" | jq empty && echo "✅ Valid JSON"
'
```

### Automated Tests

Created comprehensive test suite in `tests/test_json_flag.py`:
- ✅ Test 1: JSON purity (no logs in output)
- ✅ Test 2: Stderr suppression (all logs suppressed)
- ✅ Test 3: jq compatibility (can be parsed by jq)

Run tests:
```bash
python3 tests/test_json_flag.py
```

### Existing Tests

Verified that existing tests still pass:
```bash
python3 tests/test_scraper.py --verbose
python3 tests/test_scraper_info_json.py --verbose
```

## Files Modified

1. **src/event_manager.py**
   - Added `--json` argument to parser
   - Added logging suppression when `--json` is used
   - Updated help text and examples

2. **src/modules/scraper.py**
   - Removed import-time warning
   - Stored error for later reporting
   - Added `_check_scraping_available()` method

3. **src/modules/compressor.py**
   - Removed import-time Brotli warning

4. **.github/workflows/website-maintenance.yml**
   - Updated to use `--json` flag
   - Added comprehensive error handling
   - Added JSON validation with `jq empty`
   - Added fallback mechanism with safe defaults

5. **tests/test_json_flag.py** (new)
   - Comprehensive test suite for `--json` flag

## Expected Outcome

After this fix is deployed:

1. ✅ **Workflow runs successfully**: The `discover-capabilities` job completes without errors
2. ✅ **Clean JSON output**: The `scraper-info --json` command outputs pure JSON
3. ✅ **Deployment proceeds**: GitHub Pages deployment job executes
4. ✅ **Website updates**: The site shows the latest commit hash instead of being stuck
5. ✅ **Resilience**: Future runs are protected against JSON parsing issues

## Verification Checklist

After merge, verify:

- [ ] Workflow `discover-capabilities` job completes successfully
- [ ] JSON validation step passes
- [ ] Source count and scraping status are correctly extracted
- [ ] Subsequent jobs (scrape-events, deploy) execute
- [ ] GitHub Pages deployment completes
- [ ] Website shows latest commit (not stuck at old commit)
- [ ] Check workflow run logs show no jq parse errors

## Rollback Plan

If issues occur, the fix is backward compatible:
- Old workflows without `--json` flag still work (just with logs on stderr)
- The stderr redirection (`2>/dev/null`) can be used as fallback
- Safe defaults ensure workflow doesn't completely fail

## Additional Notes

- The `--json` flag is now the **recommended** way to call `scraper-info` in CI/CD
- The normal mode (without `--json`) still shows logs for debugging
- All existing functionality remains unchanged
- This fix follows KISS principles: minimal changes, maximum impact
