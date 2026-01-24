"""
Region Management Module

Provides TUI and CLI interfaces for managing multi-region configuration.
Allows adding, editing, listing, and removing regions without manual JSON editing.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List

from .utils import load_config
from .region_utils import (
    get_all_regions, 
    get_default_region,
    validate_region,
    get_region_config
)


class RegionTUI:
    """Interactive TUI for managing regions"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.config_path = base_path / 'config.json'
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print header"""
        print("=" * 70)
        print("  Region Management - Multi-Region Configuration")
        print("=" * 70)
        print()
    
    def show_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header()
        
        print("Region Management Menu:")
        print("-" * 70)
        print("1. List All Regions")
        print("2. Add New Region")
        print("3. Edit Region")
        print("4. Remove Region")
        print("5. Set Default Region")
        print("6. View Region Details")
        print("7. Manage Custom Filters")
        print("8. Back to Main Menu")
        print("-" * 70)
        print()
    
    def list_regions(self):
        """List all configured regions"""
        self.clear_screen()
        self.print_header()
        print("Configured Regions:")
        print("-" * 70)
        
        regions = get_all_regions(self.base_path)
        default_region = get_default_region(self.base_path)
        
        if not regions:
            print("No regions configured.")
        else:
            for region_id, region_config in regions.items():
                default_marker = " ⭐ (default)" if region_id == default_region else ""
                print(f"\n• {region_id}{default_marker}")
                print(f"  Name: {region_config.get('displayName', 'N/A')}")
                print(f"  Center: {region_config.get('center', {}).get('lat', 'N/A')}, "
                      f"{region_config.get('center', {}).get('lng', 'N/A')}")
                print(f"  Zoom: {region_config.get('zoom', 'N/A')}")
                filters_count = len(region_config.get('customFilters', []))
                print(f"  Custom Filters: {filters_count}")
        
        print()
        input("Press Enter to continue...")
    
    def add_region(self):
        """Add a new region interactively"""
        self.clear_screen()
        self.print_header()
        print("Add New Region:")
        print("-" * 70)
        
        # Get region details
        region_id = input("\nRegion ID (short key, e.g., 'hof', 'nbg'): ").strip().lower()
        
        if not region_id:
            print("❌ Region ID cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Check if region already exists
        regions = get_all_regions(self.base_path)
        if region_id in regions:
            print(f"❌ Region '{region_id}' already exists")
            input("\nPress Enter to continue...")
            return
        
        display_name = input("Display Name (e.g., 'Hof (Saale)'): ").strip()
        
        # Get coordinates
        try:
            lat = input("Latitude (4 decimals, e.g., 50.3167): ").strip()
            lng = input("Longitude (4 decimals, e.g., 11.9167): ").strip()
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            print("❌ Invalid coordinates")
            input("\nPress Enter to continue...")
            return
        
        # Get zoom level
        try:
            zoom = int(input("Default Zoom (10-18, recommend 13): ").strip() or "13")
        except ValueError:
            zoom = 13
        
        # Create region config
        new_region = {
            "name": region_id,
            "displayName": display_name,
            "center": {
                "lat": round(lat, 4),
                "lng": round(lng, 4)
            },
            "zoom": zoom,
            "boundingBox": {
                "north": round(lat + 0.1, 4),
                "south": round(lat - 0.1, 4),
                "east": round(lng + 0.1, 4),
                "west": round(lng - 0.1, 4)
            },
            "dataSource": "events.json",
            "defaultLanguage": "de",
            "customFilters": []
        }
        
        # Confirm
        print("\nNew Region Configuration:")
        print(json.dumps(new_region, indent=2))
        confirm = input("\nSave this region? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Load config, add region, save
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'regions' not in config:
                config['regions'] = {}
            
            config['regions'][region_id] = new_region
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Region '{region_id}' added successfully")
        else:
            print("\n❌ Cancelled")
        
        input("\nPress Enter to continue...")
    
    def view_region_details(self):
        """View detailed information about a region"""
        self.clear_screen()
        self.print_header()
        print("View Region Details:")
        print("-" * 70)
        
        regions = get_all_regions(self.base_path)
        if not regions:
            print("No regions configured.")
            input("\nPress Enter to continue...")
            return
        
        region_id = input("\nEnter region ID: ").strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            input("\nPress Enter to continue...")
            return
        
        region_config = get_region_config(region_id, self.base_path)
        
        print(f"\n📍 Region: {region_id}")
        print("-" * 70)
        print(json.dumps(region_config, indent=2, ensure_ascii=False))
        
        input("\nPress Enter to continue...")
    
    def remove_region(self):
        """Remove a region"""
        self.clear_screen()
        self.print_header()
        print("Remove Region:")
        print("-" * 70)
        
        regions = get_all_regions(self.base_path)
        if not regions:
            print("No regions configured.")
            input("\nPress Enter to continue...")
            return
        
        region_id = input("\nEnter region ID to remove: ").strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            input("\nPress Enter to continue...")
            return
        
        # Confirm
        confirm = input(f"\n⚠️  Remove region '{region_id}'? This cannot be undone. (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Load config, remove region, save
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            del config['regions'][region_id]
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Region '{region_id}' removed successfully")
        else:
            print("\n❌ Cancelled")
        
        input("\nPress Enter to continue...")
    
    def set_default_region(self):
        """Set the default region"""
        self.clear_screen()
        self.print_header()
        print("Set Default Region:")
        print("-" * 70)
        
        regions = get_all_regions(self.base_path)
        if not regions:
            print("No regions configured.")
            input("\nPress Enter to continue...")
            return
        
        current_default = get_default_region(self.base_path)
        print(f"\nCurrent default: {current_default}")
        print("\nAvailable regions:")
        for region_id in regions.keys():
            print(f"  • {region_id}")
        
        region_id = input("\nEnter new default region ID: ").strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            input("\nPress Enter to continue...")
            return
        
        # Load config, set default, save
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['defaultRegion'] = region_id
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Default region set to '{region_id}'")
        input("\nPress Enter to continue...")
    
    def manage_custom_filters(self):
        """Manage custom filters for a region"""
        self.clear_screen()
        self.print_header()
        print("Manage Custom Filters:")
        print("-" * 70)
        
        regions = get_all_regions(self.base_path)
        if not regions:
            print("No regions configured.")
            input("\nPress Enter to continue...")
            return
        
        # Select region
        print("\nAvailable regions:")
        for region_id in regions.keys():
            print(f"  • {region_id}")
        
        region_id = input("\nEnter region ID: ").strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            input("\nPress Enter to continue...")
            return
        
        # Show filter submenu
        while True:
            self.clear_screen()
            self.print_header()
            print(f"Custom Filters for '{region_id}':")
            print("-" * 70)
            
            region_config = get_region_config(region_id, self.base_path)
            filters = region_config.get('customFilters', [])
            
            print("\nCurrent Custom Filters:")
            if not filters:
                print("  No custom filters configured")
            else:
                for i, f in enumerate(filters, 1):
                    name_de = f.get('name', {}).get('de', 'N/A')
                    print(f"  {i}. {f.get('id')} - {name_de}")
                    print(f"     Center: {f.get('center', {}).get('lat')}, {f.get('center', {}).get('lng')}")
                    print(f"     Radius: {f.get('radius')} km, Zoom: {f.get('zoom')}")
            
            print("\nOptions:")
            print("1. Add Custom Filter")
            print("2. Remove Custom Filter")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                self.add_custom_filter(region_id)
            elif choice == '2':
                self.remove_custom_filter(region_id)
            elif choice == '3':
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def add_custom_filter(self, region_id: str):
        """Add a custom filter to a region"""
        print("\n" + "=" * 70)
        print("Add Custom Filter")
        print("=" * 70)
        
        filter_id = input("\nFilter ID (e.g., 'innenstadt', 'altstadt'): ").strip().lower()
        if not filter_id:
            print("❌ Filter ID cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        name_de = input("Name (German): ").strip()
        name_en = input("Name (English): ").strip()
        
        try:
            lat = float(input("Center Latitude (4 decimals, e.g., 50.3167): ").strip())
            lng = float(input("Center Longitude (4 decimals, e.g., 11.9167): ").strip())
            radius = float(input("Radius in km (e.g., 1.5): ").strip())
            zoom = int(input("Zoom level (e.g., 14): ").strip())
        except ValueError:
            print("❌ Invalid numeric input")
            input("\nPress Enter to continue...")
            return
        
        # Format to 4 decimal places
        lat = round(lat, 4)
        lng = round(lng, 4)
        
        # Create filter object
        new_filter = {
            "id": filter_id,
            "name": {
                "de": name_de,
                "en": name_en
            },
            "center": {
                "lat": lat,
                "lng": lng
            },
            "radius": radius,
            "zoom": zoom
        }
        
        # Load config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Add filter
        if 'customFilters' not in config['regions'][region_id]:
            config['regions'][region_id]['customFilters'] = []
        
        config['regions'][region_id]['customFilters'].append(new_filter)
        
        # Save config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Custom filter '{filter_id}' added to region '{region_id}'")
        input("\nPress Enter to continue...")
    
    def remove_custom_filter(self, region_id: str):
        """Remove a custom filter from a region"""
        print("\n" + "=" * 70)
        print("Remove Custom Filter")
        print("=" * 70)
        
        region_config = get_region_config(region_id, self.base_path)
        filters = region_config.get('customFilters', [])
        
        if not filters:
            print("\nNo custom filters to remove")
            input("\nPress Enter to continue...")
            return
        
        print("\nCurrent filters:")
        for i, f in enumerate(filters, 1):
            name_de = f.get('name', {}).get('de', 'N/A')
            print(f"  {i}. {f.get('id')} - {name_de}")
        
        filter_id = input("\nEnter filter ID to remove: ").strip().lower()
        
        # Load config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Find and remove filter
        filters_list = config['regions'][region_id].get('customFilters', [])
        original_count = len(filters_list)
        filters_list = [f for f in filters_list if f.get('id') != filter_id]
        
        if len(filters_list) == original_count:
            print(f"❌ Filter '{filter_id}' not found")
        else:
            config['regions'][region_id]['customFilters'] = filters_list
            
            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Custom filter '{filter_id}' removed from region '{region_id}'")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main TUI loop"""
        while self.running:
            self.show_menu()
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                self.list_regions()
            elif choice == '2':
                self.add_region()
            elif choice == '3':
                print("\n⚠️  Edit functionality: Please manually edit config.json")
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.remove_region()
            elif choice == '5':
                self.set_default_region()
            elif choice == '6':
                self.view_region_details()
            elif choice == '7':
                self.manage_custom_filters()
            elif choice == '8':
                self.running = False
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")


class RegionCLI:
    """Command-line interface for region management"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.config_path = base_path / 'config.json'
    
    def handle_command(self, args):
        """Handle region CLI commands"""
        command = args.region_command
        
        if command == 'list':
            return self.list_regions(args)
        elif command == 'add':
            return self.add_region(args)
        elif command == 'remove':
            return self.remove_region(args)
        elif command == 'view':
            return self.view_region(args)
        elif command == 'set-default':
            return self.set_default_region(args)
        elif command == 'add-filter':
            return self.add_custom_filter(args)
        elif command == 'remove-filter':
            return self.remove_custom_filter(args)
        elif command == 'list-filters':
            return self.list_custom_filters(args)
        else:
            print(f"❌ Unknown region command: {command}")
            print("Usage: python3 src/event_manager.py regions [list|add|remove|view|set-default|add-filter|remove-filter|list-filters]")
            return 1
    
    def list_regions(self, args):
        """List all regions"""
        regions = get_all_regions(self.base_path)
        default_region = get_default_region(self.base_path)
        
        if getattr(args, 'format', 'text') == 'json':
            # JSON output
            output = {
                "defaultRegion": default_region,
                "regions": regions
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Text output
            print(f"Default Region: {default_region}\n")
            print("Configured Regions:")
            print("-" * 70)
            
            if not regions:
                print("No regions configured.")
            else:
                for region_id, region_config in regions.items():
                    default_marker = " ⭐" if region_id == default_region else ""
                    print(f"\n{region_id}{default_marker}")
                    print(f"  Display Name: {region_config.get('displayName', 'N/A')}")
                    print(f"  Center: {region_config.get('center', {}).get('lat', 'N/A')}, "
                          f"{region_config.get('center', {}).get('lng', 'N/A')}")
                    print(f"  Zoom: {region_config.get('zoom', 'N/A')}")
                    filters_count = len(region_config.get('customFilters', []))
                    print(f"  Custom Filters: {filters_count}")
        
        return 0
    
    def add_region(self, args):
        """Add a new region"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: --id required")
            print("Usage: python3 src/event_manager.py regions add --id REGION_ID --name 'Display Name' --lat LAT --lng LNG [--zoom ZOOM]")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        # Check if region already exists
        regions = get_all_regions(self.base_path)
        if region_id in regions:
            print(f"❌ Region '{region_id}' already exists")
            return 1
        
        # Validate required fields
        if not hasattr(args, 'display_name') or not args.display_name:
            print("❌ Error: --name required")
            return 1
        
        if not hasattr(args, 'lat') or args.lat is None:
            print("❌ Error: --lat required")
            return 1
        
        if not hasattr(args, 'lng') or args.lng is None:
            print("❌ Error: --lng required")
            return 1
        
        # Create region config
        zoom = getattr(args, 'zoom', 13)
        lat = round(float(args.lat), 4)
        lng = round(float(args.lng), 4)
        
        new_region = {
            "name": region_id,
            "displayName": args.display_name,
            "center": {
                "lat": lat,
                "lng": lng
            },
            "zoom": zoom,
            "boundingBox": {
                "north": round(lat + 0.1, 4),
                "south": round(lat - 0.1, 4),
                "east": round(lng + 0.1, 4),
                "west": round(lng - 0.1, 4)
            },
            "dataSource": "events.json",
            "defaultLanguage": "de",
            "customFilters": []
        }
        
        # Load config, add region, save
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'regions' not in config:
            config['regions'] = {}
        
        config['regions'][region_id] = new_region
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Region '{region_id}' added successfully")
        return 0
    
    def remove_region(self, args):
        """Remove a region"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions remove REGION_ID")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        # Load config, remove region, save
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        del config['regions'][region_id]
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Region '{region_id}' removed successfully")
        return 0
    
    def view_region(self, args):
        """View region details"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions view REGION_ID")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        region_config = get_region_config(region_id, self.base_path)
        print(json.dumps(region_config, indent=2, ensure_ascii=False))
        return 0
    
    def set_default_region(self, args):
        """Set default region"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions set-default REGION_ID")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        # Load config, set default, save
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['defaultRegion'] = region_id
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Default region set to '{region_id}'")
        return 0
    
    def list_custom_filters(self, args):
        """List custom filters for a region"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions list-filters REGION_ID")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        region_config = get_region_config(region_id, self.base_path)
        filters = region_config.get('customFilters', [])
        
        if getattr(args, 'format', 'text') == 'json':
            print(json.dumps(filters, indent=2, ensure_ascii=False))
        else:
            print(f"Custom Filters for '{region_id}':")
            print("-" * 70)
            if not filters:
                print("No custom filters configured")
            else:
                for f in filters:
                    name_de = f.get('name', {}).get('de', 'N/A')
                    print(f"\n{f.get('id')} - {name_de}")
                    print(f"  Center: {f.get('center', {}).get('lat')}, {f.get('center', {}).get('lng')}")
                    print(f"  Radius: {f.get('radius')} km, Zoom: {f.get('zoom')}")
        
        return 0
    
    def add_custom_filter(self, args):
        """Add custom filter via CLI"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions add-filter REGION_ID --filter-id ID --name-de NAME --name-en NAME --lat LAT --lng LNG --radius RADIUS --zoom ZOOM")
            return 1
        
        region_id = args.region_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        # Validate required arguments
        required = ['filter_id', 'name_de', 'name_en', 'lat', 'lng', 'radius', 'zoom']
        for req in required:
            if not hasattr(args, req) or getattr(args, req) is None:
                print(f"❌ Error: --{req.replace('_', '-')} is required")
                return 1
        
        # Format coordinates to 4 decimal places
        lat = round(float(args.lat), 4)
        lng = round(float(args.lng), 4)
        
        # Create filter object
        new_filter = {
            "id": args.filter_id.strip().lower(),
            "name": {
                "de": args.name_de.strip(),
                "en": args.name_en.strip()
            },
            "center": {
                "lat": lat,
                "lng": lng
            },
            "radius": float(args.radius),
            "zoom": int(args.zoom)
        }
        
        # Load config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Add filter
        if 'customFilters' not in config['regions'][region_id]:
            config['regions'][region_id]['customFilters'] = []
        
        config['regions'][region_id]['customFilters'].append(new_filter)
        
        # Save config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Custom filter '{args.filter_id}' added to region '{region_id}'")
        return 0
    
    def remove_custom_filter(self, args):
        """Remove custom filter via CLI"""
        if not hasattr(args, 'region_id') or not args.region_id:
            print("❌ Error: region ID required")
            print("Usage: python3 src/event_manager.py regions remove-filter REGION_ID FILTER_ID")
            return 1
        
        if not hasattr(args, 'filter_id') or not args.filter_id:
            print("❌ Error: filter ID required")
            print("Usage: python3 src/event_manager.py regions remove-filter REGION_ID FILTER_ID")
            return 1
        
        region_id = args.region_id.strip().lower()
        filter_id = args.filter_id.strip().lower()
        
        if not validate_region(region_id, self.base_path):
            print(f"❌ Region '{region_id}' not found")
            return 1
        
        # Load config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Find and remove filter
        filters_list = config['regions'][region_id].get('customFilters', [])
        original_count = len(filters_list)
        filters_list = [f for f in filters_list if f.get('id') != filter_id]
        
        if len(filters_list) == original_count:
            print(f"❌ Filter '{filter_id}' not found in region '{region_id}'")
            return 1
        
        config['regions'][region_id]['customFilters'] = filters_list
        
        # Save config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Custom filter '{filter_id}' removed from region '{region_id}'")
        return 0
