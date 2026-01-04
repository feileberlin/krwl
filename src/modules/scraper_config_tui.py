"""Interactive TUI for scraper configuration and setup.

Provides interactive interface for:
- Adding new scraping sources
- Editing existing sources
- Testing scrapers
- Fixing broken scrapers
- Configuring source options
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


class ScraperConfigTUI:
    """Interactive TUI for managing scraper configuration."""
    
    def __init__(self, config_path: str = None, base_path: str = None):
        """Initialize scraper config TUI.
        
        Args:
            config_path: Path to config file
            base_path: Base path for data files
        """
        self.config_path = config_path or 'config.json'
        self.base_path = Path(base_path or '.')
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return {'scraping': {'sources': []}}
        except json.JSONDecodeError as e:
            print(f"Error parsing config: {e}")
            return {'scraping': {'sources': []}}
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"✗ Error saving config: {e}")
    
    def show_main_menu(self):
        """Display main menu."""
        while True:
            print("\n" + "=" * 60)
            print("SCRAPER CONFIGURATION & SETUP")
            print("=" * 60)
            print("\n1. List all sources")
            print("2. Add new source")
            print("3. Edit existing source")
            print("4. Test source")
            print("5. Enable/Disable source")
            print("6. Delete source")
            print("7. Configure source options (filters, AI, etc.)")
            print("8. Fix broken scrapers")
            print("9. Save and exit")
            print("0. Exit without saving")
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '1':
                self.list_sources()
            elif choice == '2':
                self.add_source()
            elif choice == '3':
                self.edit_source()
            elif choice == '4':
                self.test_source()
            elif choice == '5':
                self.toggle_source()
            elif choice == '6':
                self.delete_source()
            elif choice == '7':
                self.configure_options()
            elif choice == '8':
                self.fix_broken_scrapers()
            elif choice == '9':
                self._save_config()
                print("Goodbye!")
                break
            elif choice == '0':
                print("Exiting without saving changes.")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def list_sources(self):
        """List all configured sources."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources configured.")
            return
        
        print("\n" + "=" * 60)
        print("CONFIGURED SOURCES")
        print("=" * 60)
        
        for i, source in enumerate(sources, 1):
            status = "✓ ENABLED" if source.get('enabled', False) else "⊘ DISABLED"
            print(f"\n{i}. {source.get('name', 'Unnamed')} [{status}]")
            print(f"   Type: {source.get('type', 'unknown')}")
            print(f"   URL: {source.get('url', 'N/A')}")
            if source.get('notes'):
                print(f"   Notes: {source.get('notes')}")
    
    def add_source(self):
        """Add a new scraping source interactively."""
        print("\n" + "=" * 60)
        print("ADD NEW SOURCE")
        print("=" * 60)
        
        # Get source name
        name = input("\nSource name (e.g., 'City Events Page'): ").strip()
        if not name:
            print("✗ Name is required.")
            return
        
        # Get source type
        print("\nAvailable types:")
        print("1. RSS feed")
        print("2. HTML page")
        print("3. JSON API")
        print("4. Atom feed")
        print("5. Facebook")
        print("6. Instagram")
        print("7. TikTok")
        print("8. X (Twitter)")
        print("9. Telegram")
        
        type_choice = input("\nSelect type (1-9): ").strip()
        
        type_map = {
            '1': 'rss',
            '2': 'html',
            '3': 'api',
            '4': 'atom',
            '5': 'facebook',
            '6': 'instagram',
            '7': 'tiktok',
            '8': 'x',
            '9': 'telegram'
        }
        
        source_type = type_map.get(type_choice)
        if not source_type:
            print("✗ Invalid type selection.")
            return
        
        # Get URL
        url = input(f"\n{source_type.upper()} URL: ").strip()
        if not url:
            print("✗ URL is required.")
            return
        
        # Optional notes
        notes = input("\nNotes (optional): ").strip()
        
        # Enable by default
        enabled_input = input("\nEnable this source? (Y/n): ").strip().lower()
        enabled = enabled_input != 'n'
        
        # Create source
        source = {
            'name': name,
            'type': source_type,
            'url': url,
            'enabled': enabled
        }
        
        if notes:
            source['notes'] = notes
        
        # Add to config
        if 'scraping' not in self.config:
            self.config['scraping'] = {}
        if 'sources' not in self.config['scraping']:
            self.config['scraping']['sources'] = []
        
        self.config['scraping']['sources'].append(source)
        
        print(f"\n✓ Source '{name}' added successfully!")
        
        # Ask if user wants to configure options
        configure = input("\nConfigure advanced options now? (y/N): ").strip().lower()
        if configure == 'y':
            self._configure_source_options(source)
    
    def edit_source(self):
        """Edit an existing source."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources to edit.")
            return
        
        print("\n" + "=" * 60)
        print("EDIT SOURCE")
        print("=" * 60)
        
        self.list_sources()
        
        try:
            choice = int(input("\nSelect source to edit (number): ").strip())
            if choice < 1 or choice > len(sources):
                print("✗ Invalid selection.")
                return
            
            source = sources[choice - 1]
            
            print(f"\nEditing: {source.get('name')}")
            print("Leave blank to keep current value")
            
            # Edit name
            new_name = input(f"\nName [{source.get('name')}]: ").strip()
            if new_name:
                source['name'] = new_name
            
            # Edit URL
            new_url = input(f"URL [{source.get('url')}]: ").strip()
            if new_url:
                source['url'] = new_url
            
            # Edit notes
            new_notes = input(f"Notes [{source.get('notes', '')}]: ").strip()
            if new_notes:
                source['notes'] = new_notes
            
            print(f"\n✓ Source '{source.get('name')}' updated!")
            
        except (ValueError, IndexError):
            print("✗ Invalid selection.")
    
    def test_source(self):
        """Test a scraping source."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources to test.")
            return
        
        print("\n" + "=" * 60)
        print("TEST SOURCE")
        print("=" * 60)
        
        self.list_sources()
        
        try:
            choice = int(input("\nSelect source to test (number): ").strip())
            if choice < 1 or choice > len(sources):
                print("✗ Invalid selection.")
                return
            
            source = sources[choice - 1]
            
            print(f"\n🔍 Testing: {source.get('name')}")
            print(f"Type: {source.get('type')}")
            print(f"URL: {source.get('url')}")
            
            # Try to scrape
            try:
                from .scraper import EventScraper
                scraper = EventScraper(self.config, self.base_path)
                events = scraper.scrape_source(source)
                
                if events:
                    print(f"\n✓ Success! Found {len(events)} event(s)")
                    print("\nFirst event:")
                    if events:
                        print(f"  Title: {events[0].get('title', 'N/A')}")
                        print(f"  Date: {events[0].get('start_time', 'N/A')}")
                        print(f"  Location: {events[0].get('location', {}).get('name', 'N/A')}")
                else:
                    print("\n⚠ No events found. Source may be working but no events available.")
                    
            except Exception as e:
                print(f"\n✗ Test failed: {str(e)}")
                print("\nThis source may need fixing. Use option 8 to fix broken scrapers.")
                
        except (ValueError, IndexError):
            print("✗ Invalid selection.")
    
    def toggle_source(self):
        """Enable or disable a source."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources to toggle.")
            return
        
        print("\n" + "=" * 60)
        print("ENABLE/DISABLE SOURCE")
        print("=" * 60)
        
        self.list_sources()
        
        try:
            choice = int(input("\nSelect source to toggle (number): ").strip())
            if choice < 1 or choice > len(sources):
                print("✗ Invalid selection.")
                return
            
            source = sources[choice - 1]
            source['enabled'] = not source.get('enabled', False)
            
            status = "enabled" if source['enabled'] else "disabled"
            print(f"\n✓ Source '{source.get('name')}' {status}!")
            
        except (ValueError, IndexError):
            print("✗ Invalid selection.")
    
    def delete_source(self):
        """Delete a source."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources to delete.")
            return
        
        print("\n" + "=" * 60)
        print("DELETE SOURCE")
        print("=" * 60)
        
        self.list_sources()
        
        try:
            choice = int(input("\nSelect source to delete (number): ").strip())
            if choice < 1 or choice > len(sources):
                print("✗ Invalid selection.")
                return
            
            source = sources[choice - 1]
            name = source.get('name')
            
            confirm = input(f"\n⚠ Delete '{name}'? This cannot be undone! (yes/no): ").strip().lower()
            if confirm == 'yes':
                sources.pop(choice - 1)
                print(f"\n✓ Source '{name}' deleted!")
            else:
                print("Deletion cancelled.")
                
        except (ValueError, IndexError):
            print("✗ Invalid selection.")
    
    def configure_options(self):
        """Configure advanced options for a source."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources to configure.")
            return
        
        print("\n" + "=" * 60)
        print("CONFIGURE SOURCE OPTIONS")
        print("=" * 60)
        
        self.list_sources()
        
        try:
            choice = int(input("\nSelect source to configure (number): ").strip())
            if choice < 1 or choice > len(sources):
                print("✗ Invalid selection.")
                return
            
            source = sources[choice - 1]
            self._configure_source_options(source)
            
        except (ValueError, IndexError):
            print("✗ Invalid selection.")
    
    def _configure_source_options(self, source: Dict[str, Any]):
        """Configure options for a specific source."""
        print(f"\nConfiguring options for: {source.get('name')}")
        
        if 'options' not in source:
            source['options'] = {}
        
        options = source['options']
        
        # Filter ads
        filter_ads = input(f"\nFilter ads/spam? (y/N) [{options.get('filter_ads', False)}]: ").strip().lower()
        if filter_ads == 'y':
            options['filter_ads'] = True
        elif filter_ads == 'n':
            options['filter_ads'] = False
        
        # Exclude keywords
        exclude = input(f"\nExclude keywords (comma-separated) [{','.join(options.get('exclude_keywords', []))}]: ").strip()
        if exclude:
            options['exclude_keywords'] = [k.strip() for k in exclude.split(',')]
        
        # Include keywords
        include = input(f"\nInclude keywords (comma-separated, optional) [{','.join(options.get('include_keywords', []))}]: ").strip()
        if include:
            options['include_keywords'] = [k.strip() for k in include.split(',')]
        
        # Max days ahead
        max_days = input(f"\nMax days ahead (e.g., 60) [{options.get('max_days_ahead', 60)}]: ").strip()
        if max_days:
            try:
                options['max_days_ahead'] = int(max_days)
            except ValueError:
                print("⚠ Invalid number, keeping previous value")
        
        # Category
        category = input(f"\nCategory (e.g., culture, music) [{options.get('category', '')}]: ").strip()
        if category:
            options['category'] = category
        
        # AI provider
        ai_provider = input(f"\nAI provider (duckduckgo, bing, google, ollama) [{options.get('ai_provider', '')}]: ").strip()
        if ai_provider:
            options['ai_provider'] = ai_provider
        
        print("\n✓ Options configured!")
    
    def fix_broken_scrapers(self):
        """Interactive tool to fix broken scrapers."""
        sources = self.config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("\n⚠ No sources configured.")
            return
        
        print("\n" + "=" * 60)
        print("FIX BROKEN SCRAPERS")
        print("=" * 60)
        print("\nTesting all sources to find broken ones...")
        
        broken = []
        working = []
        
        try:
            from .scraper import EventScraper
            scraper = EventScraper(self.config, self.base_path)
            
            for i, source in enumerate(sources, 1):
                if not source.get('enabled', False):
                    continue
                
                print(f"\n{i}. Testing {source.get('name')}...", end=' ')
                
                try:
                    events = scraper.scrape_source(source)
                    if events is None or (isinstance(events, list) and len(events) == 0):
                        print("⚠ No events")
                        broken.append((i-1, source, "No events found"))
                    else:
                        print(f"✓ OK ({len(events)} events)")
                        working.append(source)
                except Exception as e:
                    print(f"✗ FAILED")
                    broken.append((i-1, source, str(e)))
            
            if not broken:
                print("\n✓ All sources are working!")
                return
            
            print(f"\n\n⚠ Found {len(broken)} broken source(s):")
            for idx, source, error in broken:
                print(f"\n{idx + 1}. {source.get('name')}")
                print(f"   Error: {error}")
            
            fix_choice = input("\nFix broken sources? (y/N): ").strip().lower()
            if fix_choice != 'y':
                return
            
            for idx, source, error in broken:
                print(f"\n{'='*60}")
                print(f"Fixing: {source.get('name')}")
                print(f"Error: {error}")
                print(f"{'='*60}")
                
                print("\nCommon fixes:")
                print("1. Update URL")
                print("2. Change scraper type")
                print("3. Disable source")
                print("4. Delete source")
                print("5. Skip")
                
                fix_type = input("\nSelect fix (1-5): ").strip()
                
                if fix_type == '1':
                    new_url = input(f"New URL [{source.get('url')}]: ").strip()
                    if new_url:
                        source['url'] = new_url
                        print("✓ URL updated")
                elif fix_type == '2':
                    print("\n1. RSS  2. HTML  3. API  4. Atom")
                    new_type_choice = input("New type (1-4): ").strip()
                    type_map = {'1': 'rss', '2': 'html', '3': 'api', '4': 'atom'}
                    new_type = type_map.get(new_type_choice)
                    if new_type:
                        source['type'] = new_type
                        print(f"✓ Type changed to {new_type}")
                elif fix_type == '3':
                    source['enabled'] = False
                    print("✓ Source disabled")
                elif fix_type == '4':
                    sources.pop(idx)
                    print("✓ Source deleted")
                else:
                    print("Skipped")
            
            print("\n✓ Finished fixing broken scrapers!")
            
        except Exception as e:
            print(f"\n✗ Error during testing: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive scraper configuration')
    parser.add_argument('--config', default='config.json', 
                       help='Path to config file')
    parser.add_argument('--base-path', default='.',
                       help='Base path for data files')
    
    args = parser.parse_args()
    
    tui = ScraperConfigTUI(args.config, args.base_path)
    tui.show_main_menu()


if __name__ == '__main__':
    main()
