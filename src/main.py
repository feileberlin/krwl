#!/usr/bin/env python3
"""
KRWL HOF Community Events Manager
A modular Python TUI for managing community events
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.scraper import EventScraper
from modules.editor import EventEditor
from modules.generator import StaticSiteGenerator
from modules.utils import load_config, load_events, save_events, load_pending_events, save_pending_events


class EventManagerTUI:
    """Main TUI class for event management"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.config = load_config(self.base_path)
        self.running = True
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print application header"""
        print("=" * 60)
        print(f"  {self.config['app']['name']}")
        print("=" * 60)
        print()
    
    def print_footer(self, context="main"):
        """Print footer with contextual tooltips for admin/editorial users"""
        tooltips = {
            "main": "💡 Admin Tip: Use CLI mode for automation (python3 main.py --help) | View docs: option 6",
            "scrape": "💡 Editorial Tip: Configure sources in config.json | Scraped events go to pending queue for review",
            "review": "💡 Editorial Tip: (a)pprove publishes to site | (e)dit before approval | (r)eject removes permanently",
            "published": "💡 Admin Tip: Published events appear on the map | Filtered by geolocation (<5km) & time (till sunrise)",
            "generate": "💡 Admin Tip: Static files → static/ dir | Deploy to GitHub Pages | Include .nojekyll file",
            "settings": "💡 Admin Tip: Load examples for testing | Backups created with .backup extension | Config: config.json",
            "docs": "💡 Documentation Tip: Search with keywords | Navigate with n/p/q | Full docs in README.txt"
        }
        
        print()
        print("─" * 60)
        print(tooltips.get(context, tooltips["main"]))
        print("─" * 60)
        
    def show_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header()
        
        print("Main Menu:")
        print("-" * 60)
        print("1. Scrape New Events")
        print("2. Review Pending Events")
        print("3. View Published Events")
        print("4. Generate Static Site")
        print("5. Settings")
        print("6. View Documentation")
        print("7. Exit")
        print("-" * 60)
        self.print_footer("main")
        
    def scrape_events(self):
        """Scrape events from configured sources"""
        self.clear_screen()
        self.print_header()
        print("Scraping Events...")
        print("-" * 60)
        
        scraper = EventScraper(self.config, self.base_path)
        new_events = scraper.scrape_all_sources()
        
        print(f"\nScraped {len(new_events)} new events")
        self.print_footer("scrape")
        input("\nPress Enter to continue...")
        
    def review_pending_events(self):
        """Review and approve/reject pending events"""
        self.clear_screen()
        self.print_header()
        
        editor = EventEditor(self.base_path)
        editor.review_pending()
        
    def view_published_events(self):
        """View all published events"""
        self.clear_screen()
        self.print_header()
        print("Published Events:")
        print("-" * 60)
        
        events = load_events(self.base_path)
        
        if not events['events']:
            print("No published events found.")
        else:
            for i, event in enumerate(events['events'], 1):
                print(f"\n{i}. {event['title']}")
                print(f"   Location: {event['location']['name']}")
                print(f"   Date: {event['start_time']}")
                print(f"   Status: {event['status']}")
        
        self.print_footer("published")
        input("\nPress Enter to continue...")
        
    def generate_site(self):
        """Generate static site files"""
        self.clear_screen()
        self.print_header()
        print("Generating Static Site...")
        print("-" * 60)
        
        generator = StaticSiteGenerator(self.config, self.base_path)
        generator.generate_all()
        
        print("\nStatic site generated successfully!")
        print(f"Files saved to: {self.base_path / 'static'}")
        self.print_footer("generate")
        input("\nPress Enter to continue...")
        
    def settings(self):
        """Show settings and dev mode options"""
        self.clear_screen()
        self.print_header()
        print("Settings:")
        print("-" * 60)
        print("\n1. View Configuration")
        print("2. Load Example Data (Development Mode)")
        print("3. Clear All Data")
        print("4. Back to Main Menu")
        print("-" * 60)
        self.print_footer("settings")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\nCurrent Configuration:")
            print(json.dumps(self.config, indent=2))
            input("\nPress Enter to continue...")
        elif choice == '2':
            self.load_example_data()
        elif choice == '3':
            self.clear_all_data()
        elif choice == '4':
            return
        else:
            print("\nInvalid choice.")
            input("Press Enter to continue...")
    
    def load_example_data(self):
        """Load example data for development/debugging"""
        import shutil
        
        self.clear_screen()
        self.print_header()
        print("Load Example Data (Development Mode)")
        print("-" * 60)
        print("\nThis will load sample events and pending events.")
        print("Existing data will be backed up with .backup extension.")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        try:
            # Backup existing data
            events_file = self.base_path / 'data' / 'events.json'
            pending_file = self.base_path / 'data' / 'pending_events.json'
            
            if events_file.exists():
                shutil.copy(events_file, str(events_file) + '.backup')
                
            if pending_file.exists():
                shutil.copy(pending_file, str(pending_file) + '.backup')
            
            # Copy example data
            example_events = self.base_path / 'data' / 'events_example.json'
            example_pending = self.base_path / 'data' / 'pending_events_example.json'
            
            if example_events.exists():
                shutil.copy(example_events, events_file)
                print("✓ Loaded example events")
            else:
                print("⚠ Example events file not found")
                
            if example_pending.exists():
                shutil.copy(example_pending, pending_file)
                print("✓ Loaded example pending events")
            else:
                print("⚠ Example pending events file not found")
                
            print("\n✓ Example data loaded successfully!")
            print("Original data backed up with .backup extension")
            
        except Exception as e:
            print(f"\n✗ Error loading example data: {e}")
            
        input("\nPress Enter to continue...")
    
    def clear_all_data(self):
        """Clear all events data"""
        self.clear_screen()
        self.print_header()
        print("Clear All Data")
        print("-" * 60)
        print("\n⚠ WARNING: This will delete all events and pending events!")
        print("Data will be backed up with .backup extension.")
        
        confirm = input("\nType 'DELETE' to confirm: ").strip()
        
        if confirm != 'DELETE':
            print("Cancelled.")
            input("\nPress Enter to continue...")
            return
        
        try:
            import shutil
            
            events_file = self.base_path / 'data' / 'events.json'
            pending_file = self.base_path / 'data' / 'pending_events.json'
            
            # Backup before clearing
            if events_file.exists():
                shutil.copy(events_file, str(events_file) + '.backup')
                
            if pending_file.exists():
                shutil.copy(pending_file, str(pending_file) + '.backup')
            
            # Clear data
            save_events(self.base_path, {'events': []})
            save_pending_events(self.base_path, {'pending_events': []})
            
            print("\n✓ All data cleared successfully!")
            print("Backups saved with .backup extension")
            
        except Exception as e:
            print(f"\n✗ Error clearing data: {e}")
            
        input("\nPress Enter to continue...")
        
    def view_documentation(self):
        """View documentation"""
        readme_path = self.base_path / 'README.txt'
        
        if not readme_path.exists():
            print("Documentation file (README.txt) not found.")
            input("\nPress Enter to continue...")
            return
        
        while True:
            self.clear_screen()
            self.print_header()
            print("Documentation Viewer:")
            print("-" * 60)
            print("\n1. View Table of Contents")
            print("2. Search Documentation")
            print("3. View Full Documentation")
            print("4. Quick Start Guide")
            print("5. Back to Main Menu")
            print("-" * 60)
            self.print_footer("docs")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self._show_toc()
            elif choice == '2':
                self._search_docs()
            elif choice == '3':
                self._view_full_docs()
            elif choice == '4':
                self._show_quick_start()
            elif choice == '5':
                break
            else:
                print("\nInvalid choice.")
                input("Press Enter to continue...")
    
    def _show_toc(self):
        """Show table of contents"""
        self.clear_screen()
        self.print_header()
        print("Table of Contents:")
        print("-" * 60)
        
        readme_path = self.base_path / 'README.txt'
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Extract TOC section
        toc_start = content.find("TABLE OF CONTENTS")
        if toc_start != -1:
            toc_end = content.find("================================================================================", toc_start + 100)
            toc = content[toc_start:toc_end]
            print(toc)
        else:
            print("Table of Contents not found.")
        
        input("\nPress Enter to continue...")
    
    def _search_docs(self):
        """Search documentation"""
        self.clear_screen()
        self.print_header()
        print("Search Documentation:")
        print("-" * 60)
        
        search_term = input("\nEnter search term: ").strip()
        
        if not search_term:
            return
        
        readme_path = self.base_path / 'README.txt'
        with open(readme_path, 'r') as f:
            lines = f.readlines()
        
        matches = []
        for i, line in enumerate(lines, 1):
            if search_term.lower() in line.lower():
                matches.append((i, line.strip()))
        
        print(f"\nFound {len(matches)} matches for '{search_term}':\n")
        
        for line_num, line in matches[:20]:  # Show first 20 matches
            print(f"Line {line_num}: {line[:100]}")
        
        if len(matches) > 20:
            print(f"\n... and {len(matches) - 20} more matches.")
        
        input("\nPress Enter to continue...")
    
    def _view_full_docs(self):
        """View full documentation with pagination"""
        readme_path = self.base_path / 'README.txt'
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Simple pagination
        lines = content.split('\n')
        page_size = 40
        current_page = 0
        total_pages = (len(lines) + page_size - 1) // page_size
        
        while True:
            self.clear_screen()
            self.print_header()
            
            start = current_page * page_size
            end = min(start + page_size, len(lines))
            
            print(f"Documentation (Page {current_page + 1}/{total_pages}):")
            print("-" * 60)
            print('\n'.join(lines[start:end]))
            print("-" * 60)
            print("\nNavigation: [n]ext, [p]revious, [q]uit")
            
            nav = input("\nChoice: ").strip().lower()
            
            if nav == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif nav == 'p' and current_page > 0:
                current_page -= 1
            elif nav == 'q':
                break
    
    def _show_quick_start(self):
        """Show quick start guide"""
        self.clear_screen()
        self.print_header()
        print("Quick Start Guide:")
        print("-" * 60)
        
        readme_path = self.base_path / 'README.txt'
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Extract Quick Start section
        start = content.find("3. QUICK START GUIDE")
        if start != -1:
            end = content.find("================================================================================", start + 100)
            if end != -1:
                # Get next section end
                end = content.find("================================================================================", end + 100)
                quick_start = content[start:end]
                print(quick_start)
            else:
                print("Quick Start section not found.")
        else:
            print("Quick Start section not found.")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.show_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.scrape_events()
            elif choice == '2':
                self.review_pending_events()
            elif choice == '3':
                self.view_published_events()
            elif choice == '4':
                self.generate_site()
            elif choice == '5':
                self.settings()
            elif choice == '6':
                self.view_documentation()
            elif choice == '7':
                self.running = False
                print("\nGoodbye!")
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")


def print_help():
    """Print CLI help information"""
    help_text = """
KRWL HOF Community Events Manager
==================================

A modular Python TUI for managing community events with geolocation
and sunrise filtering.

USAGE:
    python3 main.py [COMMAND] [OPTIONS]

COMMANDS:
    (no command)              Launch interactive TUI (default)
    scrape                    Scrape events from configured sources
    review                    Review pending events interactively
    publish EVENT_ID          Publish a specific pending event
    reject EVENT_ID           Reject a specific pending event
    list                      List all published events
    list-pending              List all pending events
    generate                  Generate static site files
    load-examples             Load example data for development
    clear-data                Clear all event data
    
OPTIONS:
    -h, --help               Show this help message
    -v, --version            Show version information
    -c, --config PATH        Use custom config file
    
EXAMPLES:
    # Launch interactive TUI
    python3 main.py
    
    # Scrape events from sources
    python3 main.py scrape
    
    # List all published events
    python3 main.py list
    
    # Generate static site
    python3 main.py generate
    
    # Load example data for testing
    python3 main.py load-examples
    
    # Get help
    python3 main.py --help

DOCUMENTATION:
    Full documentation available in README.txt or via the TUI
    (Main Menu → View Documentation)

For more information, visit:
    https://github.com/feileberlin/krwl-hof
"""
    print(help_text)


def cli_scrape(base_path, config):
    """CLI: Scrape events"""
    print("Scraping events from configured sources...")
    scraper = EventScraper(config, base_path)
    new_events = scraper.scrape_all_sources()
    print(f"✓ Scraped {len(new_events)} new events")
    return 0


def cli_list_events(base_path):
    """CLI: List published events"""
    events_data = load_events(base_path)
    events = events_data.get('events', [])
    
    if not events:
        print("No published events found.")
        return 0
    
    print(f"\nPublished Events ({len(events)}):")
    print("-" * 80)
    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event.get('title', 'N/A')}")
        print(f"   Location: {event.get('location', {}).get('name', 'N/A')}")
        print(f"   Time: {event.get('start_time', 'N/A')}")
        print(f"   Status: {event.get('status', 'N/A')}")
    
    return 0


def cli_list_pending(base_path):
    """CLI: List pending events"""
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    if not events:
        print("No pending events found.")
        return 0
    
    print(f"\nPending Events ({len(events)}):")
    print("-" * 80)
    for i, event in enumerate(events, 1):
        print(f"\n{i}. ID: {event.get('id', 'N/A')}")
        print(f"   Title: {event.get('title', 'N/A')}")
        print(f"   Location: {event.get('location', {}).get('name', 'N/A')}")
        print(f"   Time: {event.get('start_time', 'N/A')}")
        print(f"   Source: {event.get('source', 'N/A')}")
    
    return 0


def cli_publish_event(base_path, event_id):
    """CLI: Publish a pending event"""
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Find event
    event = None
    event_index = None
    for i, e in enumerate(events):
        if e.get('id') == event_id:
            event = e
            event_index = i
            break
    
    if not event:
        print(f"Error: Event with ID '{event_id}' not found in pending queue.")
        return 1
    
    # Publish event
    event['status'] = 'published'
    event['published_at'] = datetime.now().isoformat()
    
    events_data = load_events(base_path)
    events_data['events'].append(event)
    save_events(base_path, events_data)
    
    # Remove from pending
    events.pop(event_index)
    save_pending_events(base_path, pending_data)
    
    print(f"✓ Published event: {event.get('title')}")
    return 0


def cli_reject_event(base_path, event_id):
    """CLI: Reject a pending event"""
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Find event
    event_index = None
    event_title = None
    for i, e in enumerate(events):
        if e.get('id') == event_id:
            event_index = i
            event_title = e.get('title')
            break
    
    if event_index is None:
        print(f"Error: Event with ID '{event_id}' not found in pending queue.")
        return 1
    
    # Remove from pending
    events.pop(event_index)
    save_pending_events(base_path, pending_data)
    
    print(f"✓ Rejected event: {event_title}")
    return 0


def cli_generate(base_path, config):
    """CLI: Generate static site"""
    print("Generating static site files...")
    generator = StaticSiteGenerator(config, base_path)
    generator.generate_all()
    print(f"✓ Static site generated successfully!")
    print(f"  Files saved to: {base_path / 'static'}")
    return 0


def cli_load_examples(base_path):
    """CLI: Load example data"""
    import shutil
    
    print("Loading example data...")
    
    # Backup existing data
    events_file = base_path / 'data' / 'events.json'
    pending_file = base_path / 'data' / 'pending_events.json'
    
    if events_file.exists():
        shutil.copy(events_file, str(events_file) + '.backup')
        
    if pending_file.exists():
        shutil.copy(pending_file, str(pending_file) + '.backup')
    
    # Copy example data
    example_events = base_path / 'data' / 'events_example.json'
    example_pending = base_path / 'data' / 'pending_events_example.json'
    
    if example_events.exists():
        shutil.copy(example_events, events_file)
        print("✓ Loaded example events")
    
    if example_pending.exists():
        shutil.copy(example_pending, pending_file)
        print("✓ Loaded example pending events")
    
    print("✓ Example data loaded successfully!")
    print("  Original data backed up with .backup extension")
    return 0


def cli_clear_data(base_path):
    """CLI: Clear all data"""
    import shutil
    
    print("⚠ WARNING: This will delete all events and pending events!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print("Cancelled.")
        return 0
    
    events_file = base_path / 'data' / 'events.json'
    pending_file = base_path / 'data' / 'pending_events.json'
    
    # Backup before clearing
    if events_file.exists():
        shutil.copy(events_file, str(events_file) + '.backup')
        
    if pending_file.exists():
        shutil.copy(pending_file, str(pending_file) + '.backup')
    
    # Clear data
    save_events(base_path, {'events': []})
    save_pending_events(base_path, {'pending_events': []})
    
    print("✓ All data cleared successfully!")
    print("  Backups saved with .backup extension")
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='KRWL HOF Community Events Manager',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default=None,
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show help message')
    parser.add_argument('-v', '--version', action='store_true',
                       help='Show version')
    parser.add_argument('-c', '--config', type=str,
                       help='Custom config file path')
    
    args = parser.parse_args()
    
    # Show help
    if args.help:
        print_help()
        return 0
    
    # Show version
    if args.version:
        print("KRWL HOF Community Events Manager v1.0.0")
        return 0
    
    # Get base path
    base_path = Path(__file__).parent.parent
    
    try:
        # Load config
        config = load_config(base_path)
        
        # Handle CLI commands
        if args.command == 'scrape':
            return cli_scrape(base_path, config)
        
        elif args.command == 'list':
            return cli_list_events(base_path)
        
        elif args.command == 'list-pending':
            return cli_list_pending(base_path)
        
        elif args.command == 'publish':
            if not args.args:
                print("Error: Missing event ID")
                print("Usage: python3 main.py publish EVENT_ID")
                return 1
            return cli_publish_event(base_path, args.args[0])
        
        elif args.command == 'reject':
            if not args.args:
                print("Error: Missing event ID")
                print("Usage: python3 main.py reject EVENT_ID")
                return 1
            return cli_reject_event(base_path, args.args[0])
        
        elif args.command == 'generate':
            return cli_generate(base_path, config)
        
        elif args.command == 'load-examples':
            return cli_load_examples(base_path)
        
        elif args.command == 'clear-data':
            return cli_clear_data(base_path)
        
        elif args.command == 'review':
            # Launch TUI in review mode
            app = EventManagerTUI()
            app.review_pending_events()
            return 0
        
        elif args.command is None:
            # No command - launch interactive TUI
            app = EventManagerTUI()
            app.run()
            return 0
        
        else:
            print(f"Error: Unknown command '{args.command}'")
            print("Use --help to see available commands")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
