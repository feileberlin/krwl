#!/usr/bin/env python3
"""
KRWL HOF Configuration Editor Module

This module provides interactive and CLI-based editing of configuration files.
Supports both config.dev.json and config.prod.json editing.

Supports three execution modes:
- CLI Mode: Direct config value updates via command line
- TUI Mode: Interactive menu-driven configuration editor
- Daemon Mode: N/A (config editing is interactive)
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


class ConfigEditor:
    """Configuration editor with validation and backup support"""
    
    def __init__(self, config_path=None, verbose=False):
        """
        Initialize config editor
        
        Args:
            config_path: Path to config file (default: config.dev.json)
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.repo_root = Path.cwd()
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config.dev.json
            self.config_path = self.repo_root / "config.dev.json"
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        self.config = self.load_config()
        self.original_config = json.loads(json.dumps(self.config))  # Deep copy
    
    def log(self, message, level="INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def load_config(self):
        """Load configuration from file"""
        self.log(f"Loading config from {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self, backup=True):
        """
        Save configuration to file
        
        Args:
            backup: Create backup before saving
        """
        if backup:
            self.create_backup()
        
        self.log(f"Saving config to {self.config_path}")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✅ Configuration saved to {self.config_path}")
    
    def create_backup(self):
        """Create timestamped backup of current config"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_path.parent / f"{self.config_path.stem}.backup.{timestamp}.json"
        shutil.copy2(self.config_path, backup_path)
        self.log(f"Created backup: {backup_path}")
        return backup_path
    
    def restore_from_backup(self, backup_path):
        """Restore configuration from backup"""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        shutil.copy2(backup_file, self.config_path)
        self.config = self.load_config()
        print(f"✅ Configuration restored from {backup_path}")
    
    def get_value(self, key_path):
        """
        Get configuration value by dot-notation key path
        
        Args:
            key_path: Dot-separated path (e.g., "map.default_zoom")
        
        Returns:
            Value at key path or None if not found
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    def set_value(self, key_path, value):
        """
        Set configuration value by dot-notation key path
        
        Args:
            key_path: Dot-separated path (e.g., "map.default_zoom")
            value: New value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the value
        final_key = keys[-1]
        
        # Auto-convert value types
        old_value = config_ref.get(final_key)
        if old_value is not None:
            if isinstance(old_value, bool):
                value = value.lower() in ('true', 'yes', '1', 'on') if isinstance(value, str) else bool(value)
            elif isinstance(old_value, int):
                value = int(value)
            elif isinstance(old_value, float):
                value = float(value)
        
        config_ref[final_key] = value
        self.log(f"Set {key_path} = {value}")
    
    def list_all_settings(self, prefix="", obj=None, results=None):
        """
        List all configuration settings as flat key paths
        
        Args:
            prefix: Current key path prefix
            obj: Current object to traverse
            results: Accumulator for results
        
        Returns:
            List of (key_path, value) tuples
        """
        if results is None:
            results = []
        if obj is None:
            obj = self.config
        
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self.list_all_settings(full_key, value, results)
            elif isinstance(value, list):
                results.append((full_key, f"[list with {len(value)} items]"))
            else:
                results.append((full_key, value))
        
        return results
    
    def validate_config(self):
        """
        Validate configuration structure and required fields
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required top-level keys
        required_keys = ['app', 'map', 'filtering', 'scraping', 'data']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required key: {key}")
        
        # Validate app section
        if 'app' in self.config:
            if 'name' not in self.config['app']:
                errors.append("Missing app.name")
        
        # Validate map section
        if 'map' in self.config:
            if 'default_center' not in self.config['map']:
                errors.append("Missing map.default_center")
            else:
                center = self.config['map']['default_center']
                if 'lat' not in center or 'lon' not in center:
                    errors.append("Missing lat/lon in map.default_center")
        
        # Validate scraping sources
        if 'scraping' in self.config:
            if 'sources' not in self.config['scraping']:
                errors.append("Missing scraping.sources")
            elif not isinstance(self.config['scraping']['sources'], list):
                errors.append("scraping.sources must be a list")
        
        return errors
    
    def add_scraping_source(self, name, url, source_type, enabled=True, notes=""):
        """Add a new scraping source"""
        if 'scraping' not in self.config:
            self.config['scraping'] = {'sources': []}
        
        if 'sources' not in self.config['scraping']:
            self.config['scraping']['sources'] = []
        
        new_source = {
            'name': name,
            'url': url,
            'type': source_type,
            'enabled': enabled,
            'notes': notes
        }
        
        self.config['scraping']['sources'].append(new_source)
        self.log(f"Added scraping source: {name}")
    
    def remove_scraping_source(self, name):
        """Remove a scraping source by name"""
        if 'scraping' not in self.config or 'sources' not in self.config['scraping']:
            return False
        
        sources = self.config['scraping']['sources']
        original_count = len(sources)
        self.config['scraping']['sources'] = [s for s in sources if s.get('name') != name]
        
        removed = len(sources) - len(self.config['scraping']['sources'])
        if removed > 0:
            self.log(f"Removed scraping source: {name}")
            return True
        return False
    
    def add_predefined_location(self, name, lat, lon):
        """Add a predefined location"""
        if 'map' not in self.config:
            self.config['map'] = {}
        
        if 'predefined_locations' not in self.config['map']:
            self.config['map']['predefined_locations'] = []
        
        new_location = {
            'name': name,
            'lat': lat,
            'lon': lon
        }
        
        self.config['map']['predefined_locations'].append(new_location)
        self.log(f"Added predefined location: {name}")
    
    def remove_predefined_location(self, name):
        """Remove a predefined location by name"""
        if 'map' not in self.config or 'predefined_locations' not in self.config['map']:
            return False
        
        locations = self.config['map']['predefined_locations']
        original_count = len(locations)
        self.config['map']['predefined_locations'] = [loc for loc in locations if loc.get('name') != name]
        
        removed = len(locations) - len(self.config['map']['predefined_locations'])
        if removed > 0:
            self.log(f"Removed predefined location: {name}")
            return True
        return False


def run_tui(editor):
    """Run interactive TUI mode for configuration editing"""
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header():
        print("=" * 70)
        print(f"  KRWL HOF Configuration Editor - {editor.config_path.name}")
        print("=" * 70)
        print()
    
    def print_footer(context="main"):
        """Print contextual help tooltips"""
        tooltips = {
            "main": "💡 Tip: Changes are not saved until you select 'Save Changes' | Use CLI for automation",
            "edit": "💡 Tip: Use dot notation for nested keys (e.g., map.default_zoom) | Values auto-convert to correct type",
            "sources": "💡 Tip: Disabled sources are skipped during scraping | Type: html, facebook, or api",
            "locations": "💡 Tip: Predefined locations appear in the map's location dropdown | Use decimal degrees",
            "validate": "💡 Tip: Always validate before saving | Missing required keys will prevent saving",
            "backup": "💡 Tip: Backups are timestamped | Restore to undo changes | Max 10 shown",
        }
        print()
        print("─" * 70)
        print(tooltips.get(context, tooltips["main"]))
        print("─" * 70)
    
    while True:
        clear_screen()
        print_header()
        print("Options:")
        print("-" * 70)
        print("1. View All Settings")
        print("2. Edit Setting")
        print("3. Manage Scraping Sources")
        print("4. Manage Predefined Locations")
        print("5. Validate Configuration")
        print("6. Save Changes")
        print("7. Restore from Backup")
        print("8. Reset to Original")
        print("9. Exit")
        print("-" * 70)
        print_footer("main")
        print()
        
        choice = input("Select an option (1-9): ").strip()
        
        if choice == '1':
            clear_screen()
            print_header()
            print("Current Configuration Settings:")
            print("-" * 70)
            settings = editor.list_all_settings()
            for key, value in settings:
                print(f"{key}: {value}")
            print_footer("main")
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            clear_screen()
            print_header()
            print("Edit Setting")
            print("-" * 70)
            print_footer("edit")
            print()
            key_path = input("Enter setting key path (e.g., map.default_zoom): ").strip()
            
            current_value = editor.get_value(key_path)
            if current_value is None:
                print(f"❌ Key not found: {key_path}")
            else:
                print(f"Current value: {current_value}")
                new_value = input("Enter new value: ").strip()
                
                try:
                    editor.set_value(key_path, new_value)
                    print(f"✅ Updated {key_path} = {new_value}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            # Manage scraping sources
            while True:
                clear_screen()
                print_header()
                print("Manage Scraping Sources")
                print("-" * 70)
                
                sources = editor.config.get('scraping', {}).get('sources', [])
                if sources:
                    for i, src in enumerate(sources, 1):
                        status = "✓" if src.get('enabled') else "✗"
                        print(f"{i}. [{status}] {src.get('name')} - {src.get('type')}")
                else:
                    print("No scraping sources configured.")
                
                print("-" * 70)
                print("a. Add new source")
                print("r. Remove source")
                print("b. Back to main menu")
                print_footer("sources")
                print()
                
                sub_choice = input("Select option: ").strip().lower()
                
                if sub_choice == 'a':
                    print("\nAdd New Scraping Source:")
                    name = input("Name: ").strip()
                    url = input("URL: ").strip()
                    source_type = input("Type (html/facebook/api): ").strip()
                    enabled = input("Enabled? (y/n): ").strip().lower() == 'y'
                    notes = input("Notes (optional): ").strip()
                    
                    editor.add_scraping_source(name, url, source_type, enabled, notes)
                    print(f"✅ Added source: {name}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == 'r':
                    name = input("\nEnter source name to remove: ").strip()
                    if editor.remove_scraping_source(name):
                        print(f"✅ Removed source: {name}")
                    else:
                        print(f"❌ Source not found: {name}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == 'b':
                    break
        
        elif choice == '4':
            # Manage predefined locations
            while True:
                clear_screen()
                print_header()
                print("Manage Predefined Locations")
                print("-" * 70)
                
                locations = editor.config.get('map', {}).get('predefined_locations', [])
                if locations:
                    for i, loc in enumerate(locations, 1):
                        print(f"{i}. {loc.get('name')} ({loc.get('lat')}, {loc.get('lon')})")
                else:
                    print("No predefined locations configured.")
                
                print("-" * 70)
                print("a. Add new location")
                print("r. Remove location")
                print("b. Back to main menu")
                print_footer("locations")
                print()
                
                sub_choice = input("Select option: ").strip().lower()
                
                if sub_choice == 'a':
                    print("\nAdd New Predefined Location:")
                    name = input("Name: ").strip()
                    lat = float(input("Latitude: ").strip())
                    lon = float(input("Longitude: ").strip())
                    
                    editor.add_predefined_location(name, lat, lon)
                    print(f"✅ Added location: {name}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == 'r':
                    name = input("\nEnter location name to remove: ").strip()
                    if editor.remove_predefined_location(name):
                        print(f"✅ Removed location: {name}")
                    else:
                        print(f"❌ Location not found: {name}")
                    input("\nPress Enter to continue...")
                
                elif sub_choice == 'b':
                    break
        
        elif choice == '5':
            clear_screen()
            print_header()
            print("Validating Configuration...")
            print("-" * 70)
            errors = editor.validate_config()
            
            if errors:
                print(f"❌ Found {len(errors)} validation error(s):\n")
                for error in errors:
                    print(f"  • {error}")
            else:
                print("✅ Configuration is valid!")
            
            print_footer("validate")
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            clear_screen()
            print_header()
            print("Validating before save...")
            errors = editor.validate_config()
            
            if errors:
                print(f"❌ Cannot save - {len(errors)} validation error(s):")
                for error in errors:
                    print(f"  • {error}")
                input("\nFix errors before saving. Press Enter to continue...")
            else:
                confirm = input("Save changes to configuration? (y/n): ").strip().lower()
                if confirm == 'y':
                    editor.save_config(backup=True)
                    input("\nPress Enter to continue...")
        
        elif choice == '7':
            clear_screen()
            print_header()
            print("Restore from Backup")
            print("-" * 70)
            
            # List available backups
            backup_pattern = f"{editor.config_path.stem}.backup.*.json"
            backups = sorted(editor.config_path.parent.glob(backup_pattern), reverse=True)
            
            if backups:
                print("Available backups:")
                for i, backup in enumerate(backups[:10], 1):  # Show last 10
                    print(f"{i}. {backup.name}")
                print_footer("backup")
                print()
                
                try:
                    idx = int(input(f"Select backup (1-{min(len(backups), 10)}): ").strip())
                    if 1 <= idx <= len(backups):
                        editor.restore_from_backup(backups[idx - 1])
                    else:
                        print("Invalid selection")
                except (ValueError, IndexError):
                    print("Invalid input")
            else:
                print("No backups found.")
            
            input("\nPress Enter to continue...")
        
        elif choice == '8':
            clear_screen()
            print_header()
            confirm = input("Reset all changes to original configuration? (y/n): ").strip().lower()
            if confirm == 'y':
                editor.config = json.loads(json.dumps(editor.original_config))
                print("✅ Reset to original configuration (not saved yet)")
            input("\nPress Enter to continue...")
        
        elif choice == '9':
            # Check for unsaved changes
            if editor.config != editor.original_config:
                clear_screen()
                print_header()
                print("⚠️  You have unsaved changes!")
                confirm = input("Exit without saving? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            print("\nExiting...")
            break
        
        else:
            print("Invalid option")
            input("Press Enter to continue...")


def main():
    """Main entry point supporting CLI and TUI modes"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="KRWL HOF Configuration Editor"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Path to config file (default: config.dev.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch interactive TUI mode"
    )
    parser.add_argument(
        "--get",
        type=str,
        help="Get configuration value by key path (e.g., map.default_zoom)"
    )
    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Set configuration value (e.g., --set map.default_zoom 14)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all configuration settings"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of current configuration"
    )
    parser.add_argument(
        "--add-source",
        nargs='+',
        metavar="ARGS",
        help="Add scraping source: NAME URL TYPE [--add-source 'My Source' 'https://...' html]"
    )
    parser.add_argument(
        "--remove-source",
        type=str,
        metavar="NAME",
        help="Remove scraping source by name"
    )
    parser.add_argument(
        "--add-location",
        nargs=3,
        metavar=("NAME", "LAT", "LON"),
        help="Add predefined location: NAME LAT LON [--add-location 'Park' 50.123 11.456]"
    )
    parser.add_argument(
        "--remove-location",
        type=str,
        metavar="NAME",
        help="Remove predefined location by name"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize editor
        editor = ConfigEditor(
            config_path=args.config,
            verbose=args.verbose
        )
        
        # TUI mode
        if args.tui:
            run_tui(editor)
            sys.exit(0)
        
        # CLI operations
        modified = False
        
        if args.get:
            value = editor.get_value(args.get)
            if value is None:
                print(f"❌ Key not found: {args.get}")
                sys.exit(1)
            else:
                print(value)
                sys.exit(0)
        
        if args.set:
            key, value = args.set
            editor.set_value(key, value)
            print(f"✅ Set {key} = {value}")
            modified = True
        
        if args.list:
            settings = editor.list_all_settings()
            for key, value in settings:
                print(f"{key}: {value}")
            sys.exit(0)
        
        if args.validate:
            errors = editor.validate_config()
            if errors:
                print(f"❌ Found {len(errors)} validation error(s):")
                for error in errors:
                    print(f"  • {error}")
                sys.exit(1)
            else:
                print("✅ Configuration is valid")
                sys.exit(0)
        
        if args.backup:
            backup_path = editor.create_backup()
            print(f"✅ Backup created: {backup_path}")
            sys.exit(0)
        
        if args.add_source:
            if len(args.add_source) < 3:
                print("❌ Error: --add-source requires NAME URL TYPE")
                sys.exit(1)
            name, url, source_type = args.add_source[0], args.add_source[1], args.add_source[2]
            editor.add_scraping_source(name, url, source_type)
            print(f"✅ Added scraping source: {name}")
            modified = True
        
        if args.remove_source:
            if editor.remove_scraping_source(args.remove_source):
                print(f"✅ Removed scraping source: {args.remove_source}")
                modified = True
            else:
                print(f"❌ Source not found: {args.remove_source}")
                sys.exit(1)
        
        if args.add_location:
            name, lat, lon = args.add_location[0], float(args.add_location[1]), float(args.add_location[2])
            editor.add_predefined_location(name, lat, lon)
            print(f"✅ Added predefined location: {name}")
            modified = True
        
        if args.remove_location:
            if editor.remove_predefined_location(args.remove_location):
                print(f"✅ Removed predefined location: {args.remove_location}")
                modified = True
            else:
                print(f"❌ Location not found: {args.remove_location}")
                sys.exit(1)
        
        # Save if modified
        if modified:
            editor.save_config(backup=True)
        
        # If no operations specified, show help
        if not any([args.get, args.set, args.list, args.validate, args.backup,
                   args.add_source, args.remove_source, args.add_location, args.remove_location]):
            parser.print_help()
            print("\nTip: Use --tui for interactive mode")
            sys.exit(0)
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
