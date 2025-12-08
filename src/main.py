#!/usr/bin/env python3
"""
KRWL HOF Community Events Manager
A modular Python TUI for managing community events
"""

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
from modules.utils import load_config, load_events, save_events


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
        print("6. Exit")
        print("-" * 60)
        
    def scrape_events(self):
        """Scrape events from configured sources"""
        self.clear_screen()
        self.print_header()
        print("Scraping Events...")
        print("-" * 60)
        
        scraper = EventScraper(self.config, self.base_path)
        new_events = scraper.scrape_all_sources()
        
        print(f"\nScraped {len(new_events)} new events")
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
        
    def run(self):
        """Main application loop"""
        while self.running:
            self.show_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
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
                self.running = False
                print("\nGoodbye!")
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")


def main():
    """Main entry point"""
    try:
        app = EventManagerTUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
