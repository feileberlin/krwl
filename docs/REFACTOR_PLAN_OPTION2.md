# Option 2: Full System Refactor + DDG AI + VGN Modularity

## Overview
Major system refactoring to unify data structures, add AI-powered enrichment, and make transit providers modular.

## New File Structure

```
assets/json/
├── pending.json              # Unified pending queue (all entity types)
├── events.json               # Verified events (existing, unchanged)
├── locations.json            # Verified locations/venues
├── organizers.json           # Verified organizers
└── trash.json                # Rejected/deleted items
```

## Phase 1: Data Structure Refactor (10-12 commits)

### 1.1 Create New Data Models
**File**: `src/modules/models.py` (extend existing)
- Add `PendingItem` dataclass with `type` field ("event", "location", "organizer")
- Add `Location` dataclass
- Add `Organizer` dataclass
- Add common fields: `id`, `verified`, `created_at`, `updated_at`, `source`

### 1.2 Create Migration Script
**File**: `scripts/migrate_to_unified_structure.py`
- Read `pending_events.json` → convert to `pending.json` with type="event"
- Read `unverified_locations.json` → convert to `pending.json` with type="location"
- Create empty `verified_locations.json` → `locations.json`
- Create empty `organizers.json`
- Create empty `trash.json`
- Backup old files to `assets/json/old/`

### 1.3 Update Utils Module
**File**: `src/modules/utils.py`
- Update `load_pending_events()` → `load_pending_items(item_type=None)`
- Update `save_pending_events()` → `save_pending_items(items, item_type=None)`
- Add `load_locations()`, `save_locations()`
- Add `load_organizers()`, `save_organizers()`
- Add `load_trash()`, `save_trash()`
- Keep backward compatibility where possible

### 1.4 Update Scraper Module
**File**: `src/modules/scraper.py`
- Update to write to unified `pending.json`
- Add `type` field to scraped items
- Handle locations and organizers separately
- Update OSM venue discoveries to use `pending.json`

### 1.5 Update Editor Module
**File**: `src/modules/editor.py`
- Support reviewing mixed entity types
- Add type-specific validation
- Update approve/reject to route to correct verified file
- Move rejected items to `trash.json`
- Side-by-side diff display for duplicates

### 1.6 Update Location Resolver
**File**: `src/modules/location_resolver.py`
- Read from unified `locations.json`
- Update location matching logic
- Handle pending locations

### 1.7 Update Event Context Aggregator
**File**: `src/modules/event_context_aggregator.py`
- Load locations from `locations.json`
- Load organizers from `organizers.json`
- Join event data with verified entities

### 1.8 Update Event Manager CLI
**File**: `src/event_manager.py`
- Update CLI commands to use new structure
- Add commands: `list-pending --type={event,location,organizer}`
- Add command: `review-pending --type={event,location,organizer}`
- Update `publish`, `reject` commands

### 1.9 Update VGN Module
**File**: `src/modules/vgn_transit.py`
- Write discovered venues to `pending.json` with type="location"
- Remove `cultural_venues.json` caching
- Integrate with unified workflow

### 1.10 Update Tests
**Files**: All test files
- Update test fixtures to use new structure
- Add tests for new data models
- Test migration script
- Update ~10 test files

## Phase 2: DuckDuckGo AI Enrichment (5-8 commits)

### 2.1 Create Data Enricher Module
**File**: `src/modules/data_enricher.py`

**Features**:
- Query DuckDuckGo AI Chat API for missing data
- Enrich events: missing addresses, descriptions, organizer info
- Enrich locations: missing addresses, phone numbers, URLs, categories
- Enrich organizers: missing contact info, descriptions, URLs
- Rate limiting (max 10 requests/minute)
- Error handling and retries
- Cache results to avoid duplicate queries

**Methods**:
- `enrich_event(event_dict) -> dict`
- `enrich_location(location_dict) -> dict`
- `enrich_organizer(organizer_dict) -> dict`
- `enrich_pending_items(item_type=None) -> stats`
- `_query_ddg_ai(query: str) -> str`

### 2.2 Add Configuration
**File**: `config.json`
Add `data_enrichment` section:
```json
{
  "data_enrichment": {
    "enabled": true,
    "provider": "duckduckgo_ai",
    "rate_limit_rpm": 10,
    "auto_enrich_on_scrape": false,
    "cache_hours": 168
  }
}
```

### 2.3 Add CLI Commands
**File**: `src/event_manager.py`
- `python3 src/event_manager.py enrich-pending --type={event,location,organizer,all}`
- `python3 src/event_manager.py enrich-item <item_id>`

### 2.4 Integration with Scraper
**File**: `src/modules/scraper.py`
- Optional auto-enrichment after scraping
- Controlled by `config.data_enrichment.auto_enrich_on_scrape`

### 2.5 Add Tests
**File**: `tests/test_data_enricher.py`
- Test DDG AI querying (mocked)
- Test enrichment logic
- Test rate limiting
- Test error handling

### 2.6 Update Features Registry
**File**: `features.json`
- Add "Data Enrichment" feature entry
- Dependencies: requests, optional DDG API access

## Phase 3: VGN Modularity (3-5 commits)

### 3.1 Create Transit Provider Interface
**File**: `src/modules/transit/provider_interface.py`

**Abstract Base Class**: `TransitProvider`
```python
class TransitProvider(ABC):
    @abstractmethod
    def get_reachable_stations(self, origin, max_travel_time, max_transfers):
        pass
    
    @abstractmethod
    def discover_venues_near_stations(self, stations, radius_km):
        pass
    
    @abstractmethod
    def calculate_travel_time(self, origin, destination):
        pass
```

### 3.2 Refactor VGN as Plugin
**File**: `src/modules/transit/vgn_provider.py`
- Move logic from `vgn_transit.py` to new file
- Implement `TransitProvider` interface
- Keep existing functionality
- Make configuration-driven

### 3.3 Create Provider Registry
**File**: `src/modules/transit/registry.py`
- Register available providers
- Load provider based on config
- Default to VGN
- Allow future providers: Google Transit, MVV, etc.

### 3.4 Update Configuration
**File**: `config.json`
Change `vgn` → `transit`:
```json
{
  "transit": {
    "provider": "vgn",
    "enabled": true,
    "providers": {
      "vgn": {
        "reference_location": {...},
        "reachability": {...}
      }
    }
  }
}
```

### 3.5 Update CLI Commands
**File**: `src/event_manager.py`
- Rename `vgn` commands → `transit` commands
- Keep `vgn` as alias for backward compatibility
- Example: `python3 src/event_manager.py transit analyze 30`

### 3.6 Update Tests
**File**: `tests/test_transit_providers.py`
- Test abstract interface
- Test VGN provider implementation
- Test provider registry

## Implementation Order

1. ✅ Phase 1.1-1.2: Data models + migration script
2. ✅ Phase 1.3: Utils module update
3. ✅ Phase 1.4-1.5: Scraper + Editor updates
4. ✅ Phase 1.6-1.7: Location resolver + Event aggregator
5. ✅ Phase 1.8: Event manager CLI
6. ✅ Phase 1.9: VGN module integration
7. ✅ Phase 1.10: Update tests
8. ✅ Phase 2.1-2.6: DuckDuckGo AI enrichment
9. ✅ Phase 3.1-3.6: VGN modularity

## Estimated Timeline
- Phase 1: 2-3 hours (10-12 commits)
- Phase 2: 1-1.5 hours (5-8 commits)
- Phase 3: 0.5-1 hour (3-5 commits)
- **Total: 4-5.5 hours, 18-25 commits**

## Testing Strategy
- Run migration script on real data
- Test each phase independently
- Full integration test at end
- Backward compatibility checks

## Rollback Plan
- Backup all JSON files before migration
- Keep old structure in `assets/json/old/`
- Git allows reverting to pre-refactor state

## KISS Compliance
- Each module does one thing well
- Clear separation of concerns
- Minimal dependencies
- Configuration-driven
- Plugin architecture for extensibility
