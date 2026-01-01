# Scripts Directory

This directory contains utility scripts and thin wrapper scripts for the KRWL HOF project.

## Contents

### Wrapper Scripts (Delegate to `src/modules/`)
- **check_kiss.py** - KISS compliance checker (delegates to `src/modules/kiss_checker.py`)
- **verify_features.py** - Feature registry verification (delegates to `src/modules/feature_verifier.py`)
- **test_filters.py** - Filter testing (delegates to `src/modules/filter_tester.py`)
- **config_editor.py** - Configuration editor (delegates to `src/modules/config_editor.py`)

### Utility Scripts
- **manage_libs.py** - CDN library manager (download, verify, update third-party libraries)
- **generate_demo_events.py** - Generate demo events with dynamic timestamps
- **cleanup_obsolete.py** - Remove obsolete files from the project

## Usage

All scripts can be run from the project root directory:

```bash
# Wrapper scripts
python3 scripts/check_kiss.py --verbose
python3 scripts/verify_features.py --verbose
python3 scripts/test_filters.py --verbose
python3 scripts/config_editor.py

# Utility scripts
python3 scripts/manage_libs.py download
python3 scripts/generate_demo_events.py > events.demo.json
python3 scripts/cleanup_obsolete.py
```

## See Also
- Test scripts: [`../tests/`](../tests/)
- Main application: [`../src/main.py`](../src/main.py)
- Documentation: [`../docs/`](../docs/)
