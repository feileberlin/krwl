"""
Entity Operations Module - ALL operations in one place

Provides all entity-related operations:
- Add references to events (location_id, organizer_id)
- Track override patterns
- Validate entity references
- Migrate existing events to entity system

Can be used via:
1. CLI: python3 src/event_manager.py entities <command>
2. Import: from modules.entity_operations import EntityOperations
3. TUI: Interactive menus
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
from collections import defaultdict

from .entity_models import generate_location_id, generate_organizer_id, Location, Organizer

logger = logging.getLogger(__name__)


class EntityOperations:
    """
    ALL entity-related operations in one place.
    
    Backend operations for entity system management without UI dependencies.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize entity operations.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        self.events_file = self.base_path / 'assets' / 'json' / 'events.json'
        self.pending_file = self.base_path / 'assets' / 'json' / 'pending_events.json'
        self.locations_file = self.base_path / 'assets' / 'json' / 'locations.json'
        self.organizers_file = self.base_path / 'assets' / 'json' / 'organizers.json'
        self.report_file = self.base_path / 'assets' / 'json' / 'entity_override_report.json'
    
    def add_references(self, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Add location_id and organizer_id to all events.
        
        Scans all events (published and pending) and adds entity references
        based on embedded location/organizer data.
        
        Args:
            dry_run: If True, show what would be changed without making changes
            force: If True, overwrite existing references
            
        Returns:
            Statistics: events_modified, location_ids_added, organizer_ids_added
        """
        stats = {
            'events_modified': 0,
            'location_ids_added': 0,
            'organizer_ids_added': 0,
            'events_analyzed': 0,
            'events_with_locations': 0,
            'events_with_organizers': 0
        }
        
        # Process both published and pending events
        for file_path in [self.events_file, self.pending_file]:
            if not file_path.exists():
                continue
            
            # Load events
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get events list (handle different formats)
            if file_path == self.events_file:
                events = data.get('events', [])
            else:
                events = data.get('pending_events', [])
            
            modified = False
            
            for event in events:
                stats['events_analyzed'] += 1
                event_modified = False
                
                # Add location_id if location exists
                if 'location' in event and isinstance(event['location'], dict):
                    stats['events_with_locations'] += 1
                    location_name = event['location'].get('name', '')
                    
                    if location_name and (force or 'location_id' not in event):
                        location_id = generate_location_id(location_name)
                        if not dry_run:
                            event['location_id'] = location_id
                        stats['location_ids_added'] += 1
                        event_modified = True
                        logger.info(f"Added location_id '{location_id}' to event {event.get('id')}")
                
                # Add organizer_id if organizer exists
                if 'organizer' in event and isinstance(event['organizer'], dict):
                    stats['events_with_organizers'] += 1
                    organizer_name = event['organizer'].get('name', '')
                    
                    if organizer_name and (force or 'organizer_id' not in event):
                        organizer_id = generate_organizer_id(organizer_name)
                        if not dry_run:
                            event['organizer_id'] = organizer_id
                        stats['organizer_ids_added'] += 1
                        event_modified = True
                        logger.info(f"Added organizer_id '{organizer_id}' to event {event.get('id')}")
                
                if event_modified:
                    stats['events_modified'] += 1
                    modified = True
            
            # Save changes
            if modified and not dry_run:
                # Backup original
                backup_path = file_path.with_suffix('.json.backup')
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backup created: {backup_path}")
                
                # Save updated data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Updated: {file_path}")
        
        return stats
    
    def track_overrides(self, output_format: str = 'text') -> Dict[str, Any]:
        """
        Track override patterns across all events.
        
        Analyzes events to detect:
        - Reference only (clean)
        - Partial override (event-specific changes)
        - Full override (fully embedded)
        - Needs migration (no reference or embedded data)
        
        Args:
            output_format: 'text' or 'json'
            
        Returns:
            Statistics and override details
        """
        results = {
            'total_events': 0,
            'location_patterns': {
                'reference_only': 0,
                'partial_override': 0,
                'full_override': 0,
                'needs_migration': 0
            },
            'organizer_patterns': {
                'reference_only': 0,
                'partial_override': 0,
                'full_override': 0,
                'needs_migration': 0
            },
            'partial_overrides': [],
            'full_overrides': [],
            'needs_migration': []
        }
        
        # Analyze all events
        for file_path in [self.events_file, self.pending_file]:
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if file_path == self.events_file:
                events = data.get('events', [])
            else:
                events = data.get('pending_events', [])
            
            for event in events:
                results['total_events'] += 1
                event_id = event.get('id', 'unknown')
                
                # Analyze location pattern
                location_pattern = self._classify_location_pattern(event)
                results['location_patterns'][location_pattern] += 1
                
                if location_pattern == 'partial_override':
                    results['partial_overrides'].append({
                        'event_id': event_id,
                        'title': event.get('title', ''),
                        'entity_type': 'location',
                        'base_id': event.get('location_id'),
                        'overridden_fields': list(event.get('location_override', {}).keys())
                    })
                elif location_pattern == 'full_override':
                    results['full_overrides'].append({
                        'event_id': event_id,
                        'title': event.get('title', ''),
                        'entity_type': 'location',
                        'embedded': event.get('location', {}).get('name', '')
                    })
                elif location_pattern == 'needs_migration':
                    results['needs_migration'].append({
                        'event_id': event_id,
                        'title': event.get('title', ''),
                        'entity_type': 'location',
                        'reason': 'No location_id or embedded location'
                    })
                
                # Analyze organizer pattern
                organizer_pattern = self._classify_organizer_pattern(event)
                results['organizer_patterns'][organizer_pattern] += 1
                
                if organizer_pattern == 'partial_override':
                    results['partial_overrides'].append({
                        'event_id': event_id,
                        'title': event.get('title', ''),
                        'entity_type': 'organizer',
                        'base_id': event.get('organizer_id'),
                        'overridden_fields': list(event.get('organizer_override', {}).keys())
                    })
        
        # Save report to JSON
        with open(self.report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def _classify_location_pattern(self, event: dict) -> str:
        """Classify location reference pattern"""
        has_location_id = 'location_id' in event
        has_location_override = 'location_override' in event
        has_embedded_location = 'location' in event and isinstance(event['location'], dict)
        
        if has_location_id and has_location_override:
            return 'partial_override'
        elif has_location_id and not has_location_override:
            return 'reference_only'
        elif has_embedded_location and not has_location_id:
            return 'full_override'
        else:
            return 'needs_migration'
    
    def _classify_organizer_pattern(self, event: dict) -> str:
        """Classify organizer reference pattern"""
        has_organizer_id = 'organizer_id' in event
        has_organizer_override = 'organizer_override' in event
        has_embedded_organizer = 'organizer' in event and isinstance(event['organizer'], dict)
        
        if has_organizer_id and has_organizer_override:
            return 'partial_override'
        elif has_organizer_id and not has_organizer_override:
            return 'reference_only'
        elif has_embedded_organizer and not has_organizer_id:
            return 'full_override'
        else:
            return 'reference_only'  # No organizer is valid
    
    def validate_references(self) -> Dict[str, Any]:
        """
        Validate all entity references.
        
        Checks:
        - Every event has location_id OR location
        - ID format is correct (loc_*, org_*)
        - No ambiguous cases
        
        Returns:
            Validation results with errors and warnings
        """
        results = {
            'valid_events': 0,
            'errors': [],
            'warnings': [],
            'total_events': 0
        }
        
        # Load location and organizer libraries
        locations = self._load_entity_library(self.locations_file)
        organizers = self._load_entity_library(self.organizers_file)
        
        location_ids = {loc['id'] for loc in locations}
        organizer_ids = {org['id'] for org in organizers}
        
        # Validate all events
        for file_path in [self.events_file, self.pending_file]:
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if file_path == self.events_file:
                events = data.get('events', [])
            else:
                events = data.get('pending_events', [])
            
            for event in events:
                results['total_events'] += 1
                event_id = event.get('id', 'unknown')
                is_valid = True
                
                # Check location
                location_id = event.get('location_id')
                has_embedded_location = 'location' in event
                
                if not location_id and not has_embedded_location:
                    results['errors'].append({
                        'event_id': event_id,
                        'error': 'No location_id or embedded location'
                    })
                    is_valid = False
                
                if location_id:
                    # Validate ID format
                    if not location_id.startswith('loc_'):
                        results['errors'].append({
                            'event_id': event_id,
                            'error': f'Invalid location_id format: {location_id} (should start with "loc_")'
                        })
                        is_valid = False
                    
                    # Check if referenced location exists
                    if location_id not in location_ids:
                        results['warnings'].append({
                            'event_id': event_id,
                            'warning': f'Location ID not found in library: {location_id}'
                        })
                
                # Check organizer (optional)
                organizer_id = event.get('organizer_id')
                if organizer_id:
                    # Validate ID format
                    if not organizer_id.startswith('org_'):
                        results['errors'].append({
                            'event_id': event_id,
                            'error': f'Invalid organizer_id format: {organizer_id} (should start with "org_")'
                        })
                        is_valid = False
                    
                    # Check if referenced organizer exists
                    if organizer_id not in organizer_ids:
                        results['warnings'].append({
                            'event_id': event_id,
                            'warning': f'Organizer ID not found in library: {organizer_id}'
                        })
                
                if is_valid:
                    results['valid_events'] += 1
        
        return results
    
    def _load_entity_library(self, file_path: Path) -> List[dict]:
        """Load entity library from JSON file"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both 'locations'/'organizers' keys
                for key in ['locations', 'organizers']:
                    if key in data:
                        return data[key]
                return []
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []
    
    def migrate_to_system(self, force: bool = False) -> Dict[str, Any]:
        """
        Extract unique locations and organizers to libraries.
        
        Creates:
        - assets/json/locations.json
        - assets/json/organizers.json
        
        Args:
            force: If True, overwrite existing libraries
            
        Returns:
            Migration statistics
        """
        stats = {
            'locations_extracted': 0,
            'organizers_extracted': 0,
            'events_processed': 0,
            'duplicates_merged': 0
        }
        
        # Check if libraries exist
        if self.locations_file.exists() and not force:
            logger.warning(f"Locations library already exists: {self.locations_file}")
            logger.warning("Use --force to overwrite")
            return stats
        
        # Collect unique entities
        locations_map = {}  # key: location_id, value: location dict
        organizers_map = {}  # key: organizer_id, value: organizer dict
        
        # Process all events
        for file_path in [self.events_file, self.pending_file]:
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if file_path == self.events_file:
                events = data.get('events', [])
            else:
                events = data.get('pending_events', [])
            
            for event in events:
                stats['events_processed'] += 1
                
                # Extract location
                if 'location' in event and isinstance(event['location'], dict):
                    location = event['location']
                    location_name = location.get('name', '')
                    
                    if location_name:
                        location_id = event.get('location_id') or generate_location_id(location_name)
                        
                        if location_id not in locations_map:
                            # Create Location object
                            location_entry = Location(
                                id=location_id,
                                name=location_name,
                                lat=location.get('lat', 0.0),
                                lon=location.get('lon', 0.0),
                                address=location.get('address'),
                                address_hidden=location.get('address_hidden', False),
                                created_at=datetime.now(timezone.utc).isoformat()
                            )
                            locations_map[location_id] = location_entry.to_dict()
                            stats['locations_extracted'] += 1
                        else:
                            stats['duplicates_merged'] += 1
                
                # Extract organizer
                if 'organizer' in event and isinstance(event['organizer'], dict):
                    organizer = event['organizer']
                    organizer_name = organizer.get('name', '')
                    
                    if organizer_name:
                        organizer_id = event.get('organizer_id') or generate_organizer_id(organizer_name)
                        
                        if organizer_id not in organizers_map:
                            # Create Organizer object
                            organizer_entry = Organizer(
                                id=organizer_id,
                                name=organizer_name,
                                website=organizer.get('website'),
                                email=organizer.get('email'),
                                phone=organizer.get('phone'),
                                created_at=datetime.now(timezone.utc).isoformat()
                            )
                            organizers_map[organizer_id] = organizer_entry.to_dict()
                            stats['organizers_extracted'] += 1
                        else:
                            stats['duplicates_merged'] += 1
        
        # Save locations library
        locations_data = {
            '_comment': 'Location library for unified entity management system',
            '_description': 'Central location repository with ID-based references. Events reference locations via location_id.',
            '_version': '1.0',
            'locations': list(locations_map.values())
        }
        
        with open(self.locations_file, 'w', encoding='utf-8') as f:
            json.dump(locations_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Created locations library: {self.locations_file}")
        
        # Save organizers library
        organizers_data = {
            '_comment': 'Organizer library for unified entity management system',
            '_description': 'Central organizer repository with ID-based references. Events reference organizers via organizer_id.',
            '_version': '1.0',
            'organizers': list(organizers_map.values())
        }
        
        with open(self.organizers_file, 'w', encoding='utf-8') as f:
            json.dump(organizers_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Created organizers library: {self.organizers_file}")
        
        return stats


class EntityOperationsCLI:
    """CLI commands for entity operations"""
    
    def __init__(self, base_path: Path):
        """Initialize CLI handler"""
        self.operations = EntityOperations(base_path)
    
    def handle_command(self, args):
        """Route entity subcommands"""
        subcommand = args.entity_command
        
        if subcommand == 'add-references':
            return self.add_references_command(args)
        elif subcommand == 'track-overrides':
            return self.track_overrides_command(args)
        elif subcommand == 'validate':
            return self.validate_command(args)
        elif subcommand == 'migrate':
            return self.migrate_command(args)
        else:
            print(f"Unknown entity command: {subcommand}")
            return 1
    
    def add_references_command(self, args):
        """Add entity references to events"""
        dry_run = getattr(args, 'dry_run', False)
        force = getattr(args, 'force', False)
        
        print("=" * 70)
        print("  Add Entity References")
        print("=" * 70)
        print()
        
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print()
        
        stats = self.operations.add_references(dry_run=dry_run, force=force)
        
        print(f"✅ Events analyzed:        {stats['events_analyzed']}")
        print(f"✅ Events with locations:  {stats['events_with_locations']}")
        print(f"✅ Events with organizers: {stats['events_with_organizers']}")
        print(f"✅ Events modified:        {stats['events_modified']}")
        print(f"✅ Location IDs added:     {stats['location_ids_added']}")
        print(f"✅ Organizer IDs added:    {stats['organizer_ids_added']}")
        print()
        
        if dry_run:
            print("💡 Run without --dry-run to apply changes")
        
        return 0
    
    def track_overrides_command(self, args):
        """Track override patterns"""
        output_format = getattr(args, 'format', 'text')
        
        print("=" * 70)
        print("  Track Entity Override Patterns")
        print("=" * 70)
        print()
        
        results = self.operations.track_overrides(output_format=output_format)
        
        if output_format == 'json':
            print(json.dumps(results, indent=2))
        else:
            self._print_override_report(results)
        
        return 0
    
    def _print_override_report(self, results: dict):
        """Print human-readable override report"""
        total = results['total_events']
        loc = results['location_patterns']
        
        print("📊 Entity Override Report")
        print("=" * 70)
        print()
        print("📍 Location Override Analysis:")
        print("━" * 70)
        print(f"Total Events:          {total}")
        print(f"Reference Only:        {loc['reference_only']}  ({loc['reference_only']*100//total if total else 0}%)  ✅ Clean references")
        print(f"Partial Override:      {loc['partial_override']}  ({loc['partial_override']*100//total if total else 0}%)  ⚠️  Event-specific changes")
        print(f"Full Override:         {loc['full_override']}  ({loc['full_override']*100//total if total else 0}%)  📦 Fully embedded")
        print(f"Needs Migration:       {loc['needs_migration']}  ({loc['needs_migration']*100//total if total else 0}%)  ❌ Legacy events")
        print("━" * 70)
        print()
        
        if results['partial_overrides']:
            print("🔍 Partial Overrides Detected:")
            print("━" * 70)
            for i, override in enumerate(results['partial_overrides'][:10], 1):
                if override['entity_type'] == 'location':
                    print(f"{i}. {override['event_id']} - {override['title']}")
                    print(f"   Base Location: {override['base_id']}")
                    print(f"   Overridden Fields: {', '.join(override['overridden_fields'])}")
                    print()
            print("━" * 70)
            print()
        
        print(f"📄 Full report saved to: assets/json/entity_override_report.json")
        print()
    
    def validate_command(self, args):
        """Validate entity references"""
        print("=" * 70)
        print("  Validate Entity References")
        print("=" * 70)
        print()
        
        results = self.operations.validate_references()
        
        print(f"✅ Valid events:     {results['valid_events']}")
        print(f"⚠️  Warnings:        {len(results['warnings'])}")
        print(f"❌ Errors:          {len(results['errors'])}")
        print()
        
        if results['errors']:
            print("❌ Errors Found:")
            print("━" * 70)
            for error in results['errors']:
                print(f"Event: {error['event_id']}")
                print(f"  Error: {error['error']}")
            print()
        
        if results['warnings']:
            print("⚠️  Warnings:")
            print("━" * 70)
            for warning in results['warnings'][:10]:
                print(f"Event: {warning['event_id']}")
                print(f"  Warning: {warning['warning']}")
            if len(results['warnings']) > 10:
                print(f"  ... and {len(results['warnings']) - 10} more")
            print()
        
        return 0 if not results['errors'] else 1
    
    def migrate_command(self, args):
        """Migrate to entity system"""
        force = getattr(args, 'force', False)
        
        print("=" * 70)
        print("  Migrate to Entity System")
        print("=" * 70)
        print()
        
        stats = self.operations.migrate_to_system(force=force)
        
        print(f"✅ Events processed:        {stats['events_processed']}")
        print(f"✅ Locations extracted:     {stats['locations_extracted']}")
        print(f"✅ Organizers extracted:    {stats['organizers_extracted']}")
        print(f"✅ Duplicates merged:       {stats['duplicates_merged']}")
        print()
        print("📄 Created:")
        print("  - assets/json/locations.json")
        print("  - assets/json/organizers.json")
        print()
        
        return 0


def setup_entity_operations_cli(subparsers):
    """
    Setup argparse subcommands for entity operations.
    
    Commands:
        entities add-references [--dry-run] [--force]
        entities track-overrides [--format json]
        entities validate
        entities migrate [--force]
    """
    entities_parser = subparsers.add_parser('entities', help='Entity management operations')
    entities_subparsers = entities_parser.add_subparsers(dest='entity_command', help='Entity subcommands')
    
    # add-references
    add_refs = entities_subparsers.add_parser('add-references', help='Add location_id and organizer_id to events')
    add_refs.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    add_refs.add_argument('--force', action='store_true', help='Overwrite existing references')
    
    # track-overrides
    track = entities_subparsers.add_parser('track-overrides', help='Track override patterns')
    track.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # validate
    entities_subparsers.add_parser('validate', help='Validate entity references')
    
    # migrate
    migrate = entities_subparsers.add_parser('migrate', help='Extract entities to libraries')
    migrate.add_argument('--force', action='store_true', help='Overwrite existing libraries')
