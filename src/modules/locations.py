"""
Location Management Module

Complete location management with backend CRUD, TUI, and CLI:
- LocationManager: Backend operations (add, update, delete, search, verify, merge)
- LocationTUI: Interactive text-based interface
- LocationCLI: Command-line interface

Usage:
    # Backend
    from modules.locations import LocationManager
    manager = LocationManager(base_path)
    location = manager.add_location(location_obj)
    
    # TUI
    from modules.locations import LocationTUI
    tui = LocationTUI(base_path)
    tui.run()
    
    # CLI
    python3 src/event_manager.py locations list
    python3 src/event_manager.py locations add --name "Theater Hof" --lat 50.32 --lon 11.92
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from .entity_models import Location, generate_location_id

logger = logging.getLogger(__name__)


class LocationManager:
    """Backend CRUD for locations.json library - NO UI CODE"""
    
    def __init__(self, base_path: Path):
        """
        Initialize location manager.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        self.locations_file = self.base_path / 'assets' / 'json' / 'locations.json'
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure locations.json exists"""
        if not self.locations_file.exists():
            self.locations_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                '_comment': 'Location library for unified entity management system',
                '_description': 'Central location repository with ID-based references.',
                '_version': '1.0',
                'locations': []
            }
            with open(self.locations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_data(self) -> dict:
        """Load locations.json"""
        with open(self.locations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: dict):
        """Save locations.json"""
        with open(self.locations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_location(self, location: Location) -> str:
        """
        Add new location to library.
        
        Args:
            location: Location object
            
        Returns:
            Location ID
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        # Check if ID already exists
        if any(loc['id'] == location.id for loc in locations):
            raise ValueError(f"Location ID already exists: {location.id}")
        
        # Set timestamps
        if not location.created_at:
            location.created_at = datetime.now(timezone.utc).isoformat()
        location.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Add to library
        locations.append(location.to_dict())
        data['locations'] = locations
        self._save_data(data)
        
        logger.info(f"Added location: {location.id} - {location.name}")
        return location.id
    
    def update_location(self, location_id: str, updates: Dict[str, Any]) -> Location:
        """
        Update existing location.
        
        Args:
            location_id: Location ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated Location object
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        # Find location
        for loc in locations:
            if loc['id'] == location_id:
                # Apply updates
                for key, value in updates.items():
                    if key not in ['id', 'created_at']:  # Protect immutable fields
                        loc[key] = value
                
                # Update timestamp
                loc['updated_at'] = datetime.now(timezone.utc).isoformat()
                
                # Save
                data['locations'] = locations
                self._save_data(data)
                
                logger.info(f"Updated location: {location_id}")
                return Location.from_dict(loc)
        
        raise ValueError(f"Location not found: {location_id}")
    
    def delete_location(self, location_id: str):
        """
        Delete location from library.
        
        Args:
            location_id: Location ID to delete
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        # Filter out location
        original_count = len(locations)
        locations = [loc for loc in locations if loc['id'] != location_id]
        
        if len(locations) == original_count:
            raise ValueError(f"Location not found: {location_id}")
        
        data['locations'] = locations
        self._save_data(data)
        
        logger.info(f"Deleted location: {location_id}")
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Get location by ID.
        
        Args:
            location_id: Location ID
            
        Returns:
            Location object or None
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        for loc in locations:
            if loc['id'] == location_id:
                return Location.from_dict(loc)
        
        return None
    
    def list_locations(self, verified_only: bool = False) -> List[Location]:
        """
        List all locations.
        
        Args:
            verified_only: If True, only return verified locations
            
        Returns:
            List of Location objects
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        if verified_only:
            locations = [loc for loc in locations if loc.get('verified', False)]
        
        return [Location.from_dict(loc) for loc in locations]
    
    def search_locations(self, query: str) -> List[Location]:
        """
        Search locations by name or address.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Location objects
        """
        query_lower = query.lower()
        data = self._load_data()
        locations = data.get('locations', [])
        
        results = []
        for loc in locations:
            name = loc.get('name', '').lower()
            address = loc.get('address', '').lower()
            
            if query_lower in name or query_lower in address:
                results.append(Location.from_dict(loc))
        
        return results
    
    def verify_location(self, location_id: str, verified_by: str = None):
        """
        Mark location as verified.
        
        Args:
            location_id: Location ID
            verified_by: User who verified (optional)
        """
        updates = {
            'verified': True,
            'verified_at': datetime.now(timezone.utc).isoformat(),
            'verified_by': verified_by
        }
        self.update_location(location_id, updates)
    
    def merge_locations(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Merge two locations (combine data, update event references).
        
        Args:
            source_id: Location to merge from (will be deleted)
            target_id: Location to merge into (will be kept)
            
        Returns:
            Dict with merge results
        """
        # Get both locations
        source = self.get_location(source_id)
        target = self.get_location(target_id)
        
        if not source:
            raise ValueError(f"Source location not found: {source_id}")
        if not target:
            raise ValueError(f"Target location not found: {target_id}")
        
        # Merge aliases
        source_aliases = set(source.aliases)
        source_aliases.add(source.name)  # Add source name as alias
        target_aliases = set(target.aliases)
        merged_aliases = list(source_aliases | target_aliases)
        
        # Update target with merged data
        updates = {
            'aliases': merged_aliases
        }
        
        # Merge metadata
        merged_metadata = {**source.metadata, **target.metadata}
        updates['metadata'] = merged_metadata
        
        self.update_location(target_id, updates)
        
        # Delete source
        self.delete_location(source_id)
        
        logger.info(f"Merged location {source_id} into {target_id}")
        
        return {
            'source_id': source_id,
            'target_id': target_id,
            'merged_aliases': merged_aliases
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get location library statistics.
        
        Returns:
            Dict with stats (total_locations, verified_count, etc.)
        """
        data = self._load_data()
        locations = data.get('locations', [])
        
        verified_count = sum(1 for loc in locations if loc.get('verified', False))
        with_address = sum(1 for loc in locations if loc.get('address'))
        with_phone = sum(1 for loc in locations if loc.get('phone'))
        with_website = sum(1 for loc in locations if loc.get('website'))
        
        return {
            'total_locations': len(locations),
            'verified_count': verified_count,
            'with_address': with_address,
            'with_phone': with_phone,
            'with_website': with_website
        }


class LocationTUI:
    """Interactive TUI - uses LocationManager"""
    
    def __init__(self, base_path: Path):
        """Initialize location TUI"""
        self.manager = LocationManager(base_path)
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Main TUI loop"""
        while self.running:
            self.show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.list_locations_interactive()
            elif choice == '2':
                self.add_location_interactive()
            elif choice == '3':
                self.edit_location_interactive()
            elif choice == '4':
                self.verify_location_interactive()
            elif choice == '5':
                self.search_locations_interactive()
            elif choice == '6':
                self.merge_locations_interactive()
            elif choice == '7':
                self.show_statistics()
            elif choice == '8':
                self.running = False
            else:
                print("\nInvalid choice. Try again.")
                input("Press Enter to continue...")
    
    def show_menu(self):
        """Display main menu"""
        self.clear_screen()
        print("=" * 70)
        print("  Location Management")
        print("=" * 70)
        print()
        print("1. List All Locations")
        print("2. Add New Location")
        print("3. Edit Location")
        print("4. Verify Location")
        print("5. Search Locations")
        print("6. Merge Locations")
        print("7. Show Statistics")
        print("8. Back to Main Menu")
        print()
        print("─" * 70)
    
    def list_locations_interactive(self):
        """List all locations interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  All Locations")
        print("=" * 70)
        print()
        
        locations = self.manager.list_locations()
        
        if not locations:
            print("No locations found.")
        else:
            for i, loc in enumerate(locations, 1):
                verified = "✅" if loc.verified else "⚪"
                print(f"{i}. {verified} {loc.name} ({loc.id})")
                print(f"   Coordinates: {loc.lat}, {loc.lon}")
                if loc.address:
                    print(f"   Address: {loc.address}")
                print()
        
        input("Press Enter to continue...")
    
    def add_location_interactive(self):
        """Add new location interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Add New Location")
        print("=" * 70)
        print()
        
        try:
            name = input("Location name: ").strip()
            if not name:
                print("❌ Name is required")
                input("Press Enter to continue...")
                return
            
            lat_str = input("Latitude: ").strip()
            lon_str = input("Longitude: ").strip()
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
            except ValueError:
                print("❌ Invalid coordinates")
                input("Press Enter to continue...")
                return
            
            address = input("Address (optional): ").strip() or None
            
            # Generate ID
            location_id = generate_location_id(name)
            
            # Create location
            location = Location(
                id=location_id,
                name=name,
                lat=lat,
                lon=lon,
                address=address
            )
            
            # Add to library
            self.manager.add_location(location)
            
            print(f"\n✅ Location added: {location_id}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def edit_location_interactive(self):
        """Edit location interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Edit Location")
        print("=" * 70)
        print()
        
        location_id = input("Location ID: ").strip()
        if not location_id:
            return
        
        location = self.manager.get_location(location_id)
        if not location:
            print(f"❌ Location not found: {location_id}")
            input("Press Enter to continue...")
            return
        
        print(f"\nCurrent: {location.name}")
        print(f"Coordinates: {location.lat}, {location.lon}")
        print(f"Address: {location.address or 'N/A'}")
        print()
        
        print("Enter new values (leave blank to keep current):")
        name = input(f"Name [{location.name}]: ").strip()
        lat_str = input(f"Latitude [{location.lat}]: ").strip()
        lon_str = input(f"Longitude [{location.lon}]: ").strip()
        address = input(f"Address [{location.address or 'N/A'}]: ").strip()
        
        updates = {}
        if name:
            updates['name'] = name
        if lat_str:
            try:
                updates['lat'] = float(lat_str)
            except ValueError:
                print("❌ Invalid latitude")
        if lon_str:
            try:
                updates['lon'] = float(lon_str)
            except ValueError:
                print("❌ Invalid longitude")
        if address:
            updates['address'] = address
        
        if updates:
            try:
                self.manager.update_location(location_id, updates)
                print(f"\n✅ Location updated: {location_id}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def verify_location_interactive(self):
        """Verify location interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Verify Location")
        print("=" * 70)
        print()
        
        location_id = input("Location ID: ").strip()
        if not location_id:
            return
        
        try:
            verified_by = input("Verified by (optional): ").strip() or None
            self.manager.verify_location(location_id, verified_by)
            print(f"\n✅ Location verified: {location_id}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def search_locations_interactive(self):
        """Search locations interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Search Locations")
        print("=" * 70)
        print()
        
        query = input("Search query: ").strip()
        if not query:
            return
        
        results = self.manager.search_locations(query)
        
        print()
        if not results:
            print("No results found.")
        else:
            print(f"Found {len(results)} locations:")
            print()
            for i, loc in enumerate(results, 1):
                verified = "✅" if loc.verified else "⚪"
                print(f"{i}. {verified} {loc.name} ({loc.id})")
                print(f"   Coordinates: {loc.lat}, {loc.lon}")
                if loc.address:
                    print(f"   Address: {loc.address}")
                print()
        
        input("Press Enter to continue...")
    
    def merge_locations_interactive(self):
        """Merge locations interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Merge Locations")
        print("=" * 70)
        print()
        print("⚠️  This will merge source into target and delete source")
        print()
        
        source_id = input("Source location ID (will be deleted): ").strip()
        target_id = input("Target location ID (will be kept): ").strip()
        
        if not source_id or not target_id:
            return
        
        confirm = input(f"\nMerge {source_id} → {target_id}? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        try:
            result = self.manager.merge_locations(source_id, target_id)
            print(f"\n✅ Merged successfully")
            print(f"   Aliases added: {', '.join(result['merged_aliases'])}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def show_statistics(self):
        """Show location statistics"""
        self.clear_screen()
        print("=" * 70)
        print("  Location Statistics")
        print("=" * 70)
        print()
        
        stats = self.manager.get_statistics()
        
        print(f"Total Locations:    {stats['total_locations']}")
        print(f"Verified:           {stats['verified_count']}")
        print(f"With Address:       {stats['with_address']}")
        print(f"With Phone:         {stats['with_phone']}")
        print(f"With Website:       {stats['with_website']}")
        print()
        
        input("Press Enter to continue...")


class LocationCLI:
    """CLI commands - uses LocationManager"""
    
    def __init__(self, base_path: Path):
        """Initialize CLI handler"""
        self.manager = LocationManager(base_path)
    
    def handle_command(self, args):
        """Route location subcommands"""
        subcommand = args.location_command
        
        if subcommand == 'list':
            return self.list_command(args)
        elif subcommand == 'add':
            return self.add_command(args)
        elif subcommand == 'edit':
            return self.edit_command(args)
        elif subcommand == 'verify':
            return self.verify_command(args)
        elif subcommand == 'search':
            return self.search_command(args)
        elif subcommand == 'merge':
            return self.merge_command(args)
        elif subcommand == 'stats':
            return self.stats_command(args)
        else:
            print(f"Unknown location command: {subcommand}")
            return 1
    
    def list_command(self, args):
        """List locations"""
        verified_only = getattr(args, 'verified_only', False)
        output_format = getattr(args, 'format', 'text')
        
        locations = self.manager.list_locations(verified_only=verified_only)
        
        if output_format == 'json':
            data = [loc.to_dict() for loc in locations]
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Total locations: {len(locations)}")
            print()
            for loc in locations:
                verified = "✅" if loc.verified else "⚪"
                print(f"{verified} {loc.name} ({loc.id})")
                print(f"   Coordinates: {loc.lat}, {loc.lon}")
                if loc.address:
                    print(f"   Address: {loc.address}")
                print()
        
        return 0
    
    def add_command(self, args):
        """Add location"""
        name = args.name
        lat = args.lat
        lon = args.lon
        address = getattr(args, 'address', None)
        
        location_id = generate_location_id(name)
        
        location = Location(
            id=location_id,
            name=name,
            lat=lat,
            lon=lon,
            address=address
        )
        
        try:
            self.manager.add_location(location)
            print(f"✅ Location added: {location_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def edit_command(self, args):
        """Edit location"""
        location_id = args.location_id
        
        updates = {}
        if hasattr(args, 'name') and args.name:
            updates['name'] = args.name
        if hasattr(args, 'lat') and args.lat:
            updates['lat'] = args.lat
        if hasattr(args, 'lon') and args.lon:
            updates['lon'] = args.lon
        if hasattr(args, 'address') and args.address:
            updates['address'] = args.address
        
        try:
            self.manager.update_location(location_id, updates)
            print(f"✅ Location updated: {location_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def verify_command(self, args):
        """Verify location"""
        location_id = args.location_id
        verified_by = getattr(args, 'verified_by', None)
        
        try:
            self.manager.verify_location(location_id, verified_by)
            print(f"✅ Location verified: {location_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def search_command(self, args):
        """Search locations"""
        query = args.query
        
        results = self.manager.search_locations(query)
        
        print(f"Found {len(results)} locations:")
        print()
        for loc in results:
            verified = "✅" if loc.verified else "⚪"
            print(f"{verified} {loc.name} ({loc.id})")
            print(f"   Coordinates: {loc.lat}, {loc.lon}")
            if loc.address:
                print(f"   Address: {loc.address}")
            print()
        
        return 0
    
    def merge_command(self, args):
        """Merge locations"""
        source_id = args.source_id
        target_id = args.target_id
        
        try:
            result = self.manager.merge_locations(source_id, target_id)
            print(f"✅ Merged {source_id} → {target_id}")
            print(f"   Aliases: {', '.join(result['merged_aliases'])}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def stats_command(self, args):
        """Show statistics"""
        stats = self.manager.get_statistics()
        
        print("Location Statistics:")
        print("=" * 50)
        print(f"Total Locations:    {stats['total_locations']}")
        print(f"Verified:           {stats['verified_count']}")
        print(f"With Address:       {stats['with_address']}")
        print(f"With Phone:         {stats['with_phone']}")
        print(f"With Website:       {stats['with_website']}")
        
        return 0


def setup_location_cli(subparsers):
    """
    Setup argparse subcommands for locations.
    
    Commands:
        locations list [--verified-only] [--format json]
        locations add --name NAME --lat LAT --lon LON [--address ADDR]
        locations verify LOCATION_ID
        locations search QUERY
        locations merge SOURCE_ID TARGET_ID
        locations stats
    """
    locations_parser = subparsers.add_parser('locations', help='Location management')
    locations_subparsers = locations_parser.add_subparsers(dest='location_command', help='Location subcommands')
    
    # list
    list_parser = locations_subparsers.add_parser('list', help='List all locations')
    list_parser.add_argument('--verified-only', action='store_true', help='Show only verified locations')
    list_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # add
    add_parser = locations_subparsers.add_parser('add', help='Add new location')
    add_parser.add_argument('--name', required=True, help='Location name')
    add_parser.add_argument('--lat', type=float, required=True, help='Latitude')
    add_parser.add_argument('--lon', type=float, required=True, help='Longitude')
    add_parser.add_argument('--address', help='Address (optional)')
    
    # edit
    edit_parser = locations_subparsers.add_parser('edit', help='Edit location')
    edit_parser.add_argument('location_id', help='Location ID')
    edit_parser.add_argument('--name', help='New name')
    edit_parser.add_argument('--lat', type=float, help='New latitude')
    edit_parser.add_argument('--lon', type=float, help='New longitude')
    edit_parser.add_argument('--address', help='New address')
    
    # verify
    verify_parser = locations_subparsers.add_parser('verify', help='Verify location')
    verify_parser.add_argument('location_id', help='Location ID')
    verify_parser.add_argument('--verified-by', help='User who verified')
    
    # search
    search_parser = locations_subparsers.add_parser('search', help='Search locations')
    search_parser.add_argument('query', help='Search query')
    
    # merge
    merge_parser = locations_subparsers.add_parser('merge', help='Merge locations')
    merge_parser.add_argument('source_id', help='Source location ID (will be deleted)')
    merge_parser.add_argument('target_id', help='Target location ID (will be kept)')
    
    # stats
    locations_subparsers.add_parser('stats', help='Show statistics')
