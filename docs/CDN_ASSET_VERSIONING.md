# CDN Asset Version Tracking

Automatic version tracking and management system for CDN assets (Leaflet.js, fonts) with SHA256 checksums, update detection, and local-first serving.

## Overview

This feature automatically tracks versions of CDN assets stored locally in the `lib/` directory. It ensures that:

1. **Local files are always preferred** over CDN resources
2. **Version tracking** with SHA256 checksums for integrity verification
3. **Automatic update detection** to keep assets current
4. **Reproducible builds** through tracked versions.json

## Quick Start

```bash
# Fetch dependencies from CDN (if not already present)
python3 src/event_manager.py dependencies fetch

# Check if dependencies are present locally
python3 src/event_manager.py dependencies check

# Show version information for tracked assets
python3 src/event_manager.py dependencies info

# Check for upstream updates
python3 src/event_manager.py dependencies update-check

# Update dependencies to latest versions
python3 src/event_manager.py dependencies update

# Force re-fetch all dependencies
python3 src/event_manager.py dependencies update --force
```

## How It Works

### 1. Local-First Serving

When building the site, the generator:
1. Checks if assets exist in `lib/` directory
2. If present, uses local files (embedded inline in HTML)
3. If missing, injects CDN fallback loader code

This ensures **fast, reliable builds** that don't depend on CDN availability.

### 2. Version Tracking

Every asset download is tracked in `lib/versions.json`:

```json
{
  "metadata": {
    "created": "2026-02-01T11:59:07.067854",
    "last_updated": "2026-02-01T11:59:08.240557"
  },
  "assets": {
    "leaflet": {
      "version": "1.9.4",
      "files": {
        "leaflet/leaflet.js": {
          "checksum": "db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a",
          "size_bytes": 147552,
          "last_verified": "2026-02-01T11:59:07.687200"
        }
      }
    }
  }
}
```

**Key data tracked:**
- Package version
- SHA256 checksums for each file
- File sizes
- Last verification timestamps

### 3. Update Detection

The system can detect two types of updates:

1. **Version changes** - Configured version in `DEPENDENCIES` dict differs from local version
2. **Content changes** - File checksums differ even if version is the same

Run `dependencies update-check` to see what needs updating.

### 4. Integrity Verification

All fetched files are verified using SHA256 checksums:
- Checksums are calculated during download
- Can verify integrity of local files at any time
- Detects accidental file corruption or modification

## File Structure

```
lib/
├── versions.json           # Version tracking (git-tracked)
├── leaflet/
│   ├── leaflet.css
│   ├── leaflet.js
│   └── images/
│       ├── marker-icon.png
│       ├── marker-icon-2x.png
│       └── marker-shadow.png
└── roboto/
    ├── roboto-regular-latin.woff2
    ├── roboto-medium-latin.woff2
    ├── roboto-bold-latin.woff2
    └── roboto-mono-regular-latin.woff2
```

**Git Tracking:**
- `lib/versions.json` is tracked (for reproducible builds)
- All other files in `lib/` are gitignored (fetched at build time)

## Architecture

### Modules

- **`src/modules/asset_manager.py`** - Core version tracking logic
  - `record_asset_version()` - Save version metadata
  - `verify_asset_integrity()` - Check file checksums
  - `check_for_updates()` - Detect upstream changes
  
- **`src/modules/site_generator.py`** - Integration with build system
  - `fetch_file_from_url()` - Downloads and records versions
  - `check_for_updates()` - CLI wrapper for update checking
  - `update_dependencies()` - Update to latest versions

### Configuration

Dependencies are configured in `src/modules/site_generator.py`:

```python
DEPENDENCIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {"src": "/leaflet.css", "dest": "leaflet/leaflet.css"},
            {"src": "/leaflet.js", "dest": "leaflet/leaflet.js"},
            # ...
        ]
    }
}
```

To update a dependency version:
1. Change `version` in `DEPENDENCIES` dict
2. Run `python3 src/event_manager.py dependencies update`
3. Commit updated `lib/versions.json`

## Testing

Three test suites ensure reliability:

```bash
# Unit tests for AssetManager
python3 tests/test_asset_manager.py --verbose

# Integration tests for complete workflow
python3 tests/test_asset_versioning_integration.py --verbose

# Backward compatibility tests
python3 tests/test_cdn_fallback.py --verbose
```

**Test coverage:**
- Version recording and retrieval
- Checksum calculation and verification
- Update detection (version and content changes)
- Local-first serving behavior
- Backward compatibility with existing code

## Use Cases

### Daily Development

```bash
# Check if you have all dependencies
python3 src/event_manager.py dependencies check

# If missing, fetch them
python3 src/event_manager.py dependencies fetch
```

### Updating Dependencies

```bash
# Check what needs updating
python3 src/event_manager.py dependencies update-check

# Update if needed
python3 src/event_manager.py dependencies update
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Fetch dependencies
  run: python3 src/event_manager.py dependencies fetch
  
- name: Verify integrity
  run: |
    python3 src/event_manager.py dependencies check
    # Exit code 0 = all present, 1 = missing
```

### Troubleshooting

```bash
# Show detailed version info
python3 src/event_manager.py dependencies info

# Force re-fetch everything
python3 src/event_manager.py dependencies update --force

# Remove and re-fetch manually
rm -rf lib/leaflet lib/roboto lib/versions.json
python3 src/event_manager.py dependencies fetch
```

## Benefits

1. **Faster Builds** - No CDN latency, assets are local
2. **Offline Development** - Works without internet after initial fetch
3. **Reproducible Builds** - Tracked versions ensure consistency
4. **Automatic Updates** - Detect and install upstream changes easily
5. **Integrity Verification** - SHA256 checksums prevent corruption
6. **Zero Breaking Changes** - Backward compatible with existing workflows

## Security

- **SHA256 checksums** verify file integrity
- **HTTPS-only** CDN sources (unpkg.com, fonts.gstatic.com)
- **Subresource Integrity (SRI)** hashes in CDN fallback code
- **No secrets** in versions.json (only public CDN URLs and checksums)

## Future Enhancements

Potential improvements for future versions:

- [ ] Automatic periodic update checks (daily/weekly)
- [ ] Support for multiple CDN mirrors
- [ ] Differential updates (only fetch changed files)
- [ ] Version pinning per environment (dev/prod)
- [ ] Dependency vulnerability scanning

## Related Files

- Implementation: `src/modules/asset_manager.py`
- Integration: `src/modules/site_generator.py`
- CLI: `src/event_manager.py`
- Tests: `tests/test_asset_manager.py`, `tests/test_asset_versioning_integration.py`
- Config: `.gitignore` (excludes lib/* except versions.json)
- Docs: `.github/copilot-instructions.md`
- Feature Registry: `features.json` (cdn-asset-version-tracking)
