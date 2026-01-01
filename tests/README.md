# Tests Directory

This directory contains test scripts for the KRWL HOF project.

## Test Scripts

### Core Functionality Tests
- **test_scraper.py** - Event scraper functionality (manual events, deduplication, source handling)
- **test_filters.py** - Event filtering logic (distance, time, category filters)
- **test_event_schema.py** - Event schema validation and filter stringency testing

### Feature Tests
- **test_translations.py** - Translation completeness and consistency
- **test_bulk_operations.py** - Bulk approve/reject operations with wildcards
- **test_rejected_events.py** - Auto-reject functionality for recurring events
- **test_scheduler.py** - Scheduler module tests
- **test_smart_scraper.py** - Smart scraper system tests

### Infrastructure Tests
- **test_cdn_fallback.py** - CDN fallback functionality
- **test_dev_environment.py** - Development environment verification

## Running Tests

All tests can be run from the project root directory:

```bash
# Run individual tests
python3 tests/test_scraper.py --verbose
python3 tests/test_filters.py --verbose
python3 tests/test_event_schema.py --verbose
python3 tests/test_translations.py --verbose

# Run all tests (if available)
./run-dev-tests.sh
```

## Test Coverage

These tests cover:
- ✅ Event scraping and parsing
- ✅ Event filtering and validation
- ✅ Schema compliance
- ✅ Translation completeness
- ✅ Bulk operations
- ✅ CDN fallback behavior
- ✅ Development environment setup

## See Also
- Scripts: [`../scripts/`](../scripts/)
- Main application: [`../src/main.py`](../src/main.py)
- Testing documentation: [`../docs/TESTING.md`](../docs/TESTING.md)
