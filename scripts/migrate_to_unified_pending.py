#!/usr/bin/env python3
"""
Migration Script: Old Structure → Unified Pending Structure

Migrates:
- pending_events.json → pending.json (type: event)
- unverified_locations.json → pending.json (type: location)
- verified_locations.json → locations.json (verified locations)

Creates:
- assets/json/pending.json
- assets/json/locations.json
- assets/json/organizers.json (empty initially)
- assets/json/trash.json (empty initially)

Backs up old files to .backup
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import uuid


def generate_id(entity_type: str, name: str) -> str:
    """
    Generate unique ID for entity using UUID4 for collision resistance.
    
    Uses UUID4 to minimize collision risk as the dataset grows.
    Prefix is kept for backward compatibility with existing ID schemes.
    
    Args:
        entity_type: Type of entity (location, organizer, event)
        name: Name of the entity (not used in UUID but kept for API compatibility)
        
    Returns:
        Unique ID with format: {prefix}_{uuid}
    """
    prefix = {"location": "loc", "organizer": "org", "event": "evt"}[entity_type]
    unique_part = uuid.uuid4().hex[:16]  # Use first 16 hex chars for readability
    return f"{prefix}_{unique_part}"


def migrate_pending_events(base_path: Path) -> list:
    """Migrate pending_events.json to new structure."""
    old_file = base_path / 'assets' / 'json' / 'pending_events.json'
    
    if not old_file.exists():
        print(f"⚠️  {old_file} not found, skipping pending events migration")
        return []
    
    print(f"📖 Reading {old_file}")
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    events = old_data.get('pending_events', [])
    migrated_events = []
    
    for event in events:
        # Generate ID if not present
        event_id = event.get('id', generate_id('event', event.get('title', 'unknown')))
        
        # Convert to new structure
        new_event = {
            "id": event_id,
            "type": "event",
            "title": event.get('title'),
            "description": event.get('description'),
            "location": event.get('location'),  # Keep embedded for now, will link later
            "start_time": event.get('start_time'),
            "end_time": event.get('end_time'),
            "url": event.get('url'),
            "source": event.get('source'),
            "category": event.get('category', 'community'),
            "status": "pending",
            "scraped_at": event.get('scraped_at', datetime.now().isoformat()),
            "verified": False
        }
        migrated_events.append(new_event)
    
    print(f"✅ Migrated {len(migrated_events)} pending events")
    return migrated_events


def migrate_unverified_locations(base_path: Path) -> list:
    """Migrate unverified_locations.json to pending.json structure."""
    old_file = base_path / 'assets' / 'json' / 'unverified_locations.json'
    
    if not old_file.exists():
        print(f"⚠️  {old_file} not found, skipping unverified locations migration")
        return []
    
    print(f"📖 Reading {old_file}")
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    locations = old_data.get('locations', {})
    migrated_locations = []
    
    for name, data in locations.items():
        location_id = generate_id('location', name)
        
        new_location = {
            "id": location_id,
            "type": "location",
            "name": name,
            "lat": data.get('lat'),
            "lon": data.get('lon'),
            "address": data.get('address'),
            "category": "venue",
            "url": None,
            "phone": None,
            "occurrence_count": data.get('occurrence_count', 1),
            "sources": data.get('sources', []),
            "source": "scraper",
            "first_seen": data.get('first_seen'),
            "last_seen": data.get('last_seen'),
            "verified": False,
            "scraping_enabled": False,
            "notes": "",
            "created_at": data.get('first_seen', datetime.now().isoformat())
        }
        migrated_locations.append(new_location)
    
    print(f"✅ Migrated {len(migrated_locations)} unverified locations")
    return migrated_locations


def migrate_verified_locations(base_path: Path) -> dict:
    """Migrate verified_locations.json to new locations.json structure."""
    old_file = base_path / 'assets' / 'json' / 'verified_locations.json'
    
    if not old_file.exists():
        print(f"⚠️  {old_file} not found, creating empty locations.json")
        return {}
    
    print(f"📖 Reading {old_file}")
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    old_locations = old_data.get('locations', {})
    new_locations = {}
    
    for name, data in old_locations.items():
        location_id = generate_id('location', name)
        
        new_locations[location_id] = {
            "id": location_id,
            "name": name,
            "lat": data.get('lat'),
            "lon": data.get('lon'),
            "address": data.get('address'),
            "category": "venue",
            "url": None,
            "phone": None,
            "scraping_enabled": False,
            "scraping_urls": [],
            "verified": True,
            "verified_at": datetime.now().isoformat(),
            "verified_by": "migration_script"
        }
    
    print(f"✅ Migrated {len(new_locations)} verified locations")
    return new_locations


def create_empty_collections(base_path: Path):
    """Create empty organizers.json and trash.json."""
    json_path = base_path / 'assets' / 'json'
    
    organizers_file = json_path / 'organizers.json'
    print(f"📝 Creating empty {organizers_file}")
    organizers_data = {
        "_schema_version": "2.0",
        "_description": "Verified organizers database",
        "organizers": {}
    }
    with open(organizers_file, 'w', encoding='utf-8') as f:
        json.dump(organizers_data, f, indent=2, ensure_ascii=False)
    
    trash_file = json_path / 'trash.json'
    print(f"📝 Creating empty {trash_file}")
    trash_data = {
        "_schema_version": "2.0",
        "_description": "Rejected items archive",
        "items": []
    }
    with open(trash_file, 'w', encoding='utf-8') as f:
        json.dump(trash_data, f, indent=2, ensure_ascii=False)


def backup_old_files(base_path: Path):
    """Backup old files before migration."""
    json_path = base_path / 'assets' / 'json'
    old_files = [
        'pending_events.json',
        'unverified_locations.json',
        'verified_locations.json'
    ]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for filename in old_files:
        old_file = json_path / filename
        if old_file.exists():
            backup_file = json_path / f"{filename}.backup_{timestamp}"
            print(f"💾 Backing up {filename} → {backup_file.name}")
            shutil.copy2(old_file, backup_file)


def main():
    """Run migration."""
    print("=" * 60)
    print("🔄 Data Structure Migration: Old → Unified Pending")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    json_path = base_path / 'assets' / 'json'
    
    # Step 1: Backup old files
    print("\n📦 Step 1: Backing up old files...")
    backup_old_files(base_path)
    
    # Step 2: Migrate pending events
    print("\n📦 Step 2: Migrating pending events...")
    migrated_events = migrate_pending_events(base_path)
    
    # Step 3: Migrate unverified locations
    print("\n📦 Step 3: Migrating unverified locations...")
    migrated_locations = migrate_unverified_locations(base_path)
    
    # Step 4: Migrate verified locations
    print("\n📦 Step 4: Migrating verified locations...")
    new_locations = migrate_verified_locations(base_path)
    
    # Step 5: Create unified pending.json
    print("\n📦 Step 5: Creating unified pending.json...")
    pending_items = migrated_events + migrated_locations
    pending_data = {
        "_schema_version": "2.0",
        "_description": "Unified pending queue for events, locations, and organizers",
        "items": pending_items,
        "last_updated": datetime.now().isoformat()
    }
    
    pending_file = json_path / 'pending.json'
    print(f"💾 Writing {pending_file}")
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(pending_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created pending.json with {len(pending_items)} items")
    
    # Step 6: Create new locations.json
    print("\n📦 Step 6: Creating new locations.json...")
    locations_data = {
        "_schema_version": "2.0",
        "_description": "Verified locations database",
        "_coordinate_precision": "4 decimal places (≈10m accuracy)",
        "locations": new_locations
    }
    
    locations_file = json_path / 'locations.json'
    print(f"💾 Writing {locations_file}")
    with open(locations_file, 'w', encoding='utf-8') as f:
        json.dump(locations_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created locations.json with {len(new_locations)} locations")
    
    # Step 7: Create empty collections
    print("\n📦 Step 7: Creating empty organizers.json and trash.json...")
    create_empty_collections(base_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"  - Pending items: {len(pending_items)}")
    print(f"    - Events: {len(migrated_events)}")
    print(f"    - Locations: {len(migrated_locations)}")
    print(f"  - Verified locations: {len(new_locations)}")
    print(f"  - New files created:")
    print(f"    ✓ pending.json")
    print(f"    ✓ locations.json")
    print(f"    ✓ organizers.json")
    print(f"    ✓ trash.json")
    print(f"\n⚠️  Old files backed up with timestamp suffix")
    print(f"⚠️  Review new files before deleting old ones")
    print("=" * 60)


if __name__ == '__main__':
    main()
