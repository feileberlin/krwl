# Entity Management System - Migration Guide

## Overview

The unified entity management system provides a centralized way to manage locations and organizers with flexible override support.

## Features

- **Centralized Libraries**: Single source of truth for locations and organizers
- **Three-Tier Override System**: Support for reference-only, partial overrides, and full overrides
- **Backward Compatible**: Existing embedded data continues to work
- **TUI & CLI**: Interactive and command-line interfaces
- **Validation**: Automatic validation of entity references

## Quick Start

### One-Time Migration

```bash
# Preview migration (dry-run)
python3 scripts/migrate_once.py --dry-run

# Execute migration
python3 scripts/migrate_once.py

# Delete migration script after success
rm scripts/migrate_once.py
```

### Manual Migration (Advanced)

```bash
# Step 1: Add entity references
python3 src/event_manager.py entities add-references

# Step 2: Validate references
python3 src/event_manager.py entities validate

# Step 3: Extract entities to libraries
python3 src/event_manager.py entities migrate

# Step 4: Track override patterns
python3 src/event_manager.py entities track-overrides
```

## Three-Tier Override System

### Tier 1: Reference Only (Recommended - 85% of events)

```json
{
  "id": "event_1",
  "title": "Regular Concert",
  "location_id": "loc_theater_hof"
}
```

**Benefits**: 
- DRY principle - update location once, affects all events
- Smaller JSON files (40-60% size reduction)
- Consistent coordinates across events

### Tier 2: Partial Override (Event-specific changes - 10% of events)

```json
{
  "id": "event_2",
  "title": "VIP Concert",
  "location_id": "loc_theater_hof",
  "location_override": {
    "name": "Theater Hof - VIP Lounge",
    "address": "Side entrance"
  }
}
```

**Use cases**:
- VIP sections with different entrance
- Temporary modifications (construction, seasonal changes)
- Event-specific access information

### Tier 3: Full Override (One-off events - 5% of events)

```json
{
  "id": "event_3",
  "title": "Pop-Up Festival",
  "location": {
    "name": "Temporary Stage",
    "lat": 50.3250,
    "lon": 11.9200
  }
}
```

**Use cases**:
- One-time pop-up events
- Unknown venues
- Testing new locations

## CLI Commands

### Entity Operations

```bash
# Add location_id and organizer_id to all events
python3 src/event_manager.py entities add-references

# Preview changes without applying
python3 src/event_manager.py entities add-references --dry-run

# Track override patterns
python3 src/event_manager.py entities track-overrides

# Validate entity references
python3 src/event_manager.py entities validate

# Extract entities to libraries (one-time)
python3 src/event_manager.py entities migrate
```

### Location Management

```bash
# Launch interactive TUI
python3 src/event_manager.py locations

# List all locations
python3 src/event_manager.py locations list

# Add new location
python3 src/event_manager.py locations add --name "Theater Hof" --lat 50.32 --lon 11.92 --address "Kulmbacher Str., 95030 Hof"

# Verify location
python3 src/event_manager.py locations verify loc_theater_hof

# Search locations
python3 src/event_manager.py locations search "Theater"

# Merge duplicate locations
python3 src/event_manager.py locations merge loc_old_id loc_new_id

# Show statistics
python3 src/event_manager.py locations stats
```

### Organizer Management

```bash
# Launch interactive TUI
python3 src/event_manager.py organizers

# List all organizers
python3 src/event_manager.py organizers list

# Add new organizer
python3 src/event_manager.py organizers add --name "Kulturverein Hof" --website "https://kulturverein-hof.de" --email "info@kulturverein-hof.de"

# Verify organizer
python3 src/event_manager.py organizers verify org_kulturverein_hof

# Search organizers
python3 src/event_manager.py organizers search "Kultur"

# Merge duplicate organizers
python3 src/event_manager.py organizers merge org_old_id org_new_id

# Show statistics
python3 src/event_manager.py organizers stats
```

## Interactive TUI

The Text User Interface provides an easy way to manage entities:

```bash
# Location management TUI
python3 src/event_manager.py locations

# Organizer management TUI
python3 src/event_manager.py organizers
```

Features:
- Browse all locations/organizers
- Add new entries
- Edit existing entries
- Mark as verified
- Search by name
- Merge duplicates
- View statistics

## Python API

### Backend Usage

```python
from pathlib import Path
from modules.locations import LocationManager
from modules.organizers import OrganizerManager
from modules.entity_resolver import EntityResolver
from modules.entity_models import Location, Organizer

base_path = Path(__file__).parent

# Location management
location_mgr = LocationManager(base_path)

# Add location
location = Location(
    id="loc_theater_hof",
    name="Theater Hof",
    lat=50.3200,
    lon=11.9180,
    address="Kulmbacher Str., 95030 Hof"
)
location_mgr.add_location(location)

# Get location
location = location_mgr.get_location("loc_theater_hof")

# Update location
location_mgr.update_location("loc_theater_hof", {
    "verified": True,
    "phone": "+49 9281 1234"
})

# Entity resolution
resolver = EntityResolver(base_path)

# Resolve single event
event = {
    "id": "event_1",
    "location_id": "loc_theater_hof"
}
resolved_event = resolver.resolve_event(event)

# Resolve multiple events
resolved_events = resolver.resolve_events(events)
```

## File Structure

```
assets/json/
├── locations.json              # Location library
├── organizers.json             # Organizer library
├── entity_override_report.json # Override analysis
├── events.json                 # Events (with references)
└── pending_events.json         # Pending events (with references)
```

## Benefits

### For Developers
- ✅ **DRY principle** - Update location once, affects all events
- ✅ **KISS structure** - Flat, simple, 8 modules total
- ✅ **Flexible** - Three-tier overrides handle all cases
- ✅ **Testable** - Backend isolated from UI
- ✅ **Reusable** - Import entity_operations anywhere

### For Editors
- ✅ **Efficiency** - Select from location library (no retyping)
- ✅ **Consistency** - Same venue = same coordinates
- ✅ **Insights** - See location usage statistics
- ✅ **Quality** - Verified, enriched data

### For End Users
- ✅ **Performance** - 40-60% smaller JSON files
- ✅ **Quality** - Better, verified data
- ✅ **Compatibility** - No breaking changes

## Testing

```bash
# Run entity model tests
python3 tests/test_entity_models.py

# Run entity resolver tests
python3 tests/test_entity_resolver.py
```

## Troubleshooting

### Migration Issues

**Problem**: Events modified count is 0
**Solution**: References may already exist. Use `--force` to overwrite:
```bash
python3 src/event_manager.py entities add-references --force
```

**Problem**: Library already exists
**Solution**: Use `--force` to overwrite existing libraries:
```bash
python3 src/event_manager.py entities migrate --force
```

### Validation Errors

**Problem**: "Location ID not found in library"
**Solution**: Run migration to extract entities:
```bash
python3 src/event_manager.py entities migrate
```

**Problem**: "Invalid location_id format"
**Solution**: IDs must start with `loc_` or `org_`. Regenerate IDs:
```bash
python3 src/event_manager.py entities add-references --force
```

## Rollback

If anything goes wrong:

1. **Restore from backups**:
   ```bash
   cp assets/json/*.json.backup assets/json/
   ```

2. **Git revert**:
   ```bash
   git checkout assets/json/events.json
   git checkout assets/json/pending_events.json
   ```

3. **Delete libraries** (embedded data still works):
   ```bash
   rm assets/json/locations.json
   rm assets/json/organizers.json
   ```

## Next Steps

1. Review generated libraries (`locations.json`, `organizers.json`)
2. Verify locations manually
3. Add missing contact information (phone, website)
4. Monitor override report for optimization opportunities
5. Update scraping to use location references

For questions or issues, see the main README.md or open a GitHub issue.
