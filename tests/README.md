# Tests Directory

This directory contains test scripts for the KRWL HOF project.

## Running Tests (Unified CLI)

The test suite is integrated into the main application CLI for easy access:

### Run All Tests
```bash
python3 src/event_manager.py test
```

### Run Specific Category
```bash
# Core functionality tests
python3 src/event_manager.py test core

# Feature tests
python3 src/event_manager.py test features

# Infrastructure tests
python3 src/event_manager.py test infrastructure
```

### Run Individual Test
```bash
# Run a specific test by name
python3 src/event_manager.py test scraper
python3 src/event_manager.py test translations
python3 src/event_manager.py test linter

# Works with or without 'test_' prefix
python3 src/event_manager.py test test_scraper
```

### List Available Tests
```bash
python3 src/event_manager.py test --list
```

### Verbose Output
```bash
# Verbose mode shows detailed test output
python3 src/event_manager.py test --verbose

# Works with categories and individual tests
python3 src/event_manager.py test core --verbose
python3 src/event_manager.py test translations --verbose
```

## Test Organization

Tests are organized into three categories:

### Core Functionality Tests (5 tests)
- **test_scraper** - Event scraper functionality (manual events, deduplication, source handling)
- **test_scrape_status** - Scraper status file generation and workflow compatibility
- **test_timestamp_update** - Timestamp update behavior for event files
- **test_filters** - Event filtering logic (distance, time, category filters)
- **test_event_schema** - Event schema validation and filter stringency testing

### Feature Tests (5 tests)
- **test_translations** - Translation completeness and consistency
- **test_bulk_operations** - Bulk approve/reject operations with wildcards
- **test_rejected_events** - Auto-reject functionality for recurring events
- **test_scheduler** - Scheduler module tests
- **test_smart_scraper** - Smart scraper system tests

### Infrastructure Tests (14 tests)
- **test_cdn_fallback** - CDN fallback functionality
- **test_dev_environment** - Development environment verification
- **test_linter** - Linter functionality
- **test_validation** - Validation models
- **test_dependency_resilience** - Dependency fetching resilience
- **test_dependency_url_construction** - Dependency URL construction
- **test_leaflet_compatibility** - Leaflet library compatibility
- **test_lucide_compatibility** - Lucide icon library compatibility
- **test_lucide_cdn** - Lucide CDN functionality
- **test_components** - HTML component system
- **test_pending_count** - Pending event counter
- **test_environment_override** - Environment override functionality
- **test_relative_times** - Relative time display
- **test_watermark_simplification** - Watermark simplification

## Legacy Method (Still Supported)

Individual test files can still be run directly for backward compatibility:

```bash
# Run tests directly (legacy method)
python3 tests/test_scraper.py --verbose
python3 tests/test_event_schema.py --verbose
python3 tests/test_translations.py --verbose

# Filter tests are now integrated in src/modules/
python3 src/modules/filter_tester.py --verbose
```

This method is still supported and useful for:
- Running tests without installing the application
- Integration with external test runners
- Debugging specific test files

## Test Coverage

These tests cover:
- ✅ Event scraping and parsing
- ✅ Event filtering and validation
- ✅ Schema compliance
- ✅ Translation completeness
- ✅ Bulk operations
- ✅ CDN fallback behavior
- ✅ Development environment setup
- ✅ Component system
- ✅ Dependency management
- ✅ Library compatibility

## CI/CD Integration

The unified test runner is designed for easy CI/CD integration:

```yaml
# GitHub Actions example
- name: Run all tests
  run: python3 src/event_manager.py test

# GitLab CI example
test:
  script:
    - python3 src/event_manager.py test
```

## See Also
- Test Runner Module: [`../src/modules/test_runner.py`](../src/modules/test_runner.py)
- Main Application: [`../src/event_manager.py`](../src/event_manager.py)
- Scripts: [`../scripts/`](../scripts/)

