#!/usr/bin/env python3
"""
KRWL HOF Community Events Manager
A modular Python TUI for managing community events
"""

import argparse
import fnmatch
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.scraper import EventScraper
from modules.editor import EventEditor
from modules.builder import Builder
from modules.workflow_launcher import WorkflowLauncher
from modules.utils import (
    load_config, load_events, save_events, 
    load_pending_events, save_pending_events, 
    backup_published_event, update_events_in_html,
    add_rejected_event
)


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
        print("5. Launch GitHub Workflows")
        print("6. Settings")
        print("7. View Documentation")
        print("8. Exit")
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
        
        builder = Builder(self.base_path)
        success = builder.build_html('production')
        
        if success:
            print("\nStatic site generated successfully!")
            print(f"Files saved to: {self.base_path / 'static'}")
        
        self.print_footer("generate")
        input("\nPress Enter to continue...")
        
    def launch_workflows(self):
        """Launch GitHub Actions workflows"""
        launcher = WorkflowLauncher(self.base_path)
        
        while True:
            self.clear_screen()
            self.print_header()
            print("GitHub Actions Workflows:")
            print("-" * 60)
            
            # Check if GitHub CLI is available
            if not launcher.gh_available:
                print("\n⚠️  GitHub CLI (gh) is not installed or not in PATH.")
                print("\nTo use this feature, install GitHub CLI:")
                print("  https://cli.github.com/")
                print("\nThen authenticate with: gh auth login")
                input("\nPress Enter to return to main menu...")
                return
            
            # Check authentication
            auth_ok, auth_msg = launcher.check_gh_auth()
            if not auth_ok:
                print(f"\n⚠️  {auth_msg}")
                print("\nTo authenticate, run: gh auth login")
                input("\nPress Enter to return to main menu...")
                return
            
            # List workflows
            workflows = launcher.list_workflows()
            
            print("\nAvailable Workflows:\n")
            for i, workflow in enumerate(workflows, 1):
                print(f"{i}. {workflow['name']}")
                print(f"   {workflow['description']}")
                if workflow['has_inputs']:
                    print(f"   ⚙️  Configurable inputs available")
                print()
            
            print(f"{len(workflows) + 1}. Back to Main Menu")
            print("-" * 60)
            print("\n💡 Tip: Workflows will be triggered on the 'preview' branch by default")
            
            choice = input("\nSelect workflow to launch (1-{}): ".format(len(workflows) + 1)).strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(workflows) + 1:
                    return
                elif 1 <= choice_num <= len(workflows):
                    selected_workflow = workflows[choice_num - 1]
                    self._launch_specific_workflow(launcher, selected_workflow)
                else:
                    print("\nInvalid choice.")
                    input("Press Enter to continue...")
            except ValueError:
                print("\nInvalid input. Please enter a number.")
                input("Press Enter to continue...")
    
    def _launch_specific_workflow(self, launcher, workflow_info):
        """Launch a specific workflow with input configuration"""
        self.clear_screen()
        self.print_header()
        
        workflow_id = workflow_info['id']
        workflow_data = launcher.get_workflow_info(workflow_id)
        
        print(f"Launch Workflow: {workflow_info['name']}")
        print("-" * 60)
        print(f"\nDescription: {workflow_info['description']}")
        print(f"Workflow file: .github/workflows/{workflow_info['file']}")
        
        # Get branch
        print("\nSelect branch:")
        print("1. preview (default)")
        print("2. main")
        print("3. Custom branch")
        
        branch_choice = input("\nBranch (1-3, default: 1): ").strip() or "1"
        
        if branch_choice == "1":
            branch = "preview"
        elif branch_choice == "2":
            branch = "main"
        elif branch_choice == "3":
            branch = input("Enter branch name: ").strip()
        else:
            branch = "preview"
        
        # Collect inputs if workflow has any
        inputs = {}
        if workflow_data['inputs']:
            print("\n" + "=" * 60)
            print("Configure Workflow Inputs:")
            print("=" * 60)
            
            for input_key, input_config in workflow_data['inputs'].items():
                print(f"\n{input_config['description']}")
                
                if input_config.get('options'):
                    print(f"Options: {', '.join(input_config['options'])}")
                
                default = input_config.get('default', '')
                user_input = input(f"Value (default: {default}): ").strip()
                
                inputs[input_key] = user_input if user_input else default
        
        # Confirm launch
        print("\n" + "=" * 60)
        print("Confirm Launch:")
        print("=" * 60)
        print(f"Workflow: {workflow_info['name']}")
        print(f"Branch: {branch}")
        if inputs:
            print(f"Inputs:")
            for key, value in inputs.items():
                print(f"  - {key}: {value}")
        
        confirm = input("\nLaunch workflow? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            print("\nTriggering workflow...")
            success, message = launcher.trigger_workflow(workflow_id, branch, inputs)
            print(f"\n{message}")
            
            if success:
                print("\nℹ️  You can monitor the workflow run at:")
                print(f"   https://github.com/feileberlin/krwl-hof/actions/workflows/{workflow_info['file']}")
        else:
            print("\nWorkflow launch cancelled.")
        
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
            events_file = self.base_path / 'static' / 'events.json'
            pending_file = self.base_path / 'static' / 'pending_events.json'
            
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
            
            events_file = self.base_path / 'static' / 'events.json'
            pending_file = self.base_path / 'static' / 'pending_events.json'
            
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
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.scrape_events()
            elif choice == '2':
                self.review_pending_events()
            elif choice == '3':
                self.view_published_events()
            elif choice == '4':
                self.generate_site()
            elif choice == '5':
                self.launch_workflows()
            elif choice == '6':
                self.settings()
            elif choice == '7':
                self.view_documentation()
            elif choice == '8':
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
    bulk-publish IDS          Bulk publish pending events (comma-separated IDs/patterns)
    bulk-reject IDS           Bulk reject pending events (comma-separated IDs/patterns)
    list                      List all published events
    list-pending              List all pending events
    
    build [MODE]              Generate HTML (production or development mode)
    events                    Update events in HTML (fast, no regeneration)
    libs [--verify]           Download or verify CDN libraries
    generate                  Generate static site files (legacy, use 'build')
    archive                   Archive past events (automatic on generate)
    load-examples             Load example data for development
    clear-data                Clear all event data
    
    workflow list             List available GitHub Actions workflows
    workflow run WORKFLOW_ID  Trigger a workflow (requires gh CLI)
    workflow status WORKFLOW  Show recent runs of a workflow
    
OPTIONS:
    -h, --help               Show this help message
    -v, --version            Show version information
    -c, --config PATH        Use custom config file
    
EXAMPLES:
    # Launch interactive TUI
    python3 main.py
    
    # Build HTML (production mode)
    python3 main.py build production
    
    # Build HTML (development mode with demo events and DEV badge)
    python3 main.py build development
    
    # Fast event update (after scraping or publishing)
    python3 main.py events
    
    # Download CDN libraries
    python3 main.py libs
    
    # Verify libraries are present
    python3 main.py libs --verify
    
    # Scrape events from sources
    python3 main.py scrape
    
    # List all published events
    python3 main.py list
    
    # Publish a single event
    python3 main.py publish pending_1
    
    # Bulk publish multiple events (exact IDs)
    python3 main.py bulk-publish pending_1,pending_2,pending_3
    
    # Bulk publish using wildcards
    python3 main.py bulk-publish "pending_*"
    python3 main.py bulk-publish "html_frankenpost_*"
    
    # Bulk reject with wildcards and exact IDs
    python3 main.py bulk-reject "html_frankenpost_*,pending_5"
    
    # Reject all events with specific pattern in title/ID
    python3 main.py bulk-reject "*AUCHEVENTMELDERWERDEN*"
    
    # List available workflows
    python3 main.py workflow list
    
    # Load example data for testing
    python3 main.py load-examples
    
    # Get help
    python3 main.py --help

WILDCARD PATTERNS:
    Bulk operations support Unix-style wildcards:
    *       Matches any characters (including none)
    ?       Matches exactly one character
    [seq]   Matches any character in seq
    [!seq]  Matches any character not in seq
    
    Examples:
    pending_*              Match all events with IDs starting with 'pending_'
    html_frankenpost_*     Match all events from the Frankenpost source
    *AUCHEVENT*            Match any event with 'AUCHEVENT' in the ID
    pending_[1-3]          Match pending_1, pending_2, pending_3
    
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
    
    # Backup the published event
    backup_path = backup_published_event(base_path, event)
    print(f"✓ Event backed up to: {backup_path.relative_to(base_path)}")
    
    events_data = load_events(base_path)
    events_data['events'].append(event)
    save_events(base_path, events_data)
    
    # Remove from pending
    events.pop(event_index)
    save_pending_events(base_path, pending_data)
    
    print(f"✓ Published event: {event.get('title')}")
    
    # Update events in HTML
    print("Updating events in HTML...")
    update_events_in_html(base_path)
    
    return 0


def expand_wildcard_patterns(patterns, pending_events):
    """
    Expand wildcard patterns to match event IDs.
    
    Args:
        patterns: List of patterns (can include wildcards like * and ?)
        pending_events: List of pending events with 'id' field
        
    Returns:
        List of expanded event IDs (duplicates removed, order preserved)
    """
    expanded_ids = []
    seen_ids = set()
    
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
            
        # Check if pattern contains wildcards
        if '*' in pattern or '?' in pattern or '[' in pattern:
            # Match against all pending event IDs
            matches_found = False
            for event in pending_events:
                event_id = event.get('id', '')
                if fnmatch.fnmatch(event_id, pattern):
                    matches_found = True
                    if event_id not in seen_ids:
                        expanded_ids.append(event_id)
                        seen_ids.add(event_id)
            
            if not matches_found:
                print(f"⚠ Warning: Pattern '{pattern}' matched no events")
        else:
            # Exact ID - add if not already seen
            if pattern not in seen_ids:
                expanded_ids.append(pattern)
                seen_ids.add(pattern)
    
    return expanded_ids


def cli_reject_event(base_path, event_id):
    """CLI: Reject a pending event"""
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Find event
    event_index = None
    event_title = None
    event_source = None
    for i, e in enumerate(events):
        if e.get('id') == event_id:
            event_index = i
            event_title = e.get('title')
            event_source = e.get('source', 'unknown')
            break
    
    if event_index is None:
        print(f"Error: Event with ID '{event_id}' not found in pending queue.")
        return 1
    
    # Add to rejected events list
    add_rejected_event(base_path, event_title, event_source)
    
    # Remove from pending
    events.pop(event_index)
    save_pending_events(base_path, pending_data)
    
    print(f"✓ Rejected event: {event_title}")
    print(f"✓ Added to rejected_events.json")
    return 0


def cli_bulk_publish_events(base_path, event_ids_str):
    """CLI: Bulk publish pending events (supports wildcards)"""
    # Parse comma-separated event IDs/patterns
    patterns = [p.strip() for p in event_ids_str.split(',')]
    
    if not patterns:
        print("Error: No event IDs or patterns provided")
        return 1
    
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Expand wildcards
    event_ids = expand_wildcard_patterns(patterns, events)
    
    if not event_ids:
        print("Error: No events matched the provided patterns")
        return 1
    
    events_data = load_events(base_path)
    
    published_count = 0
    failed_count = 0
    failed_ids = []
    
    print(f"Bulk publishing {len(event_ids)} event(s)...")
    print("-" * 80)
    
    # Collect events and indices first
    events_to_publish = []
    for event_id in event_ids:
        # Find event
        event = None
        event_index = None
        for i, e in enumerate(events):
            if e.get('id') == event_id:
                event = e
                event_index = i
                break
        
        if not event:
            print(f"✗ Event '{event_id}' not found in pending queue")
            failed_count += 1
            failed_ids.append(event_id)
        else:
            events_to_publish.append((event_index, event_id, event))
    
    # Sort by index in reverse order to safely remove from pending list
    events_to_publish.sort(key=lambda x: x[0], reverse=True)
    
    for event_index, event_id, event in events_to_publish:
        try:
            # Publish event
            event['status'] = 'published'
            event['published_at'] = datetime.now().isoformat()
            
            # Backup the published event
            backup_path = backup_published_event(base_path, event)
            
            # Add to published events
            events_data['events'].append(event)
            
            # Remove from pending (safe because we're removing in reverse order)
            events.pop(event_index)
            
            print(f"✓ Published: {event.get('title')} (ID: {event_id})")
            published_count += 1
        except Exception as e:
            print(f"✗ Failed to publish '{event_id}': {e}")
            failed_count += 1
            failed_ids.append(event_id)
    
    # Save changes
    if published_count > 0:
        save_events(base_path, events_data)
        save_pending_events(base_path, pending_data)
        
        # Update events in HTML
        print("\nUpdating events in HTML...")
        update_events_in_html(base_path)
    
    # Summary
    print("-" * 80)
    print(f"✓ Successfully published: {published_count} event(s)")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count} event(s)")
        print(f"  Failed IDs: {', '.join(failed_ids)}")
        return 1
    
    return 0


def cli_bulk_reject_events(base_path, event_ids_str):
    """CLI: Bulk reject pending events (supports wildcards)"""
    # Parse comma-separated event IDs/patterns
    patterns = [p.strip() for p in event_ids_str.split(',')]
    
    if not patterns:
        print("Error: No event IDs or patterns provided")
        return 1
    
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Expand wildcards
    event_ids = expand_wildcard_patterns(patterns, events)
    
    if not event_ids:
        print("Error: No events matched the provided patterns")
        return 1
    
    rejected_count = 0
    failed_count = 0
    failed_ids = []
    
    print(f"Bulk rejecting {len(event_ids)} event(s)...")
    print("-" * 80)
    
    # Collect indices first to avoid shifting issues during removal
    indices_to_remove = []
    for event_id in event_ids:
        # Find event
        event_index = None
        event_title = None
        event_source = None
        for i, e in enumerate(events):
            if e.get('id') == event_id:
                event_index = i
                event_title = e.get('title')
                event_source = e.get('source', 'unknown')
                break
        
        if event_index is None:
            print(f"✗ Event '{event_id}' not found in pending queue")
            failed_count += 1
            failed_ids.append(event_id)
        else:
            indices_to_remove.append((event_index, event_id, event_title, event_source))
    
    # Sort by index in reverse order and remove
    indices_to_remove.sort(key=lambda x: x[0], reverse=True)
    
    for event_index, event_id, event_title, event_source in indices_to_remove:
        try:
            # Add to rejected events list
            add_rejected_event(base_path, event_title, event_source)
            
            # Remove from pending (safe because we're removing in reverse order)
            events.pop(event_index)
            print(f"✓ Rejected: {event_title} (ID: {event_id})")
            rejected_count += 1
        except Exception as e:
            print(f"✗ Failed to reject '{event_id}': {e}")
            failed_count += 1
            failed_ids.append(event_id)
    
    # Save changes
    if rejected_count > 0:
        save_pending_events(base_path, pending_data)
        print(f"\n✓ Added {rejected_count} event(s) to rejected_events.json")
    
    # Summary
    print("-" * 80)
    print(f"✓ Successfully rejected: {rejected_count} event(s)")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count} event(s)")
        print(f"  Failed IDs: {', '.join(failed_ids)}")
        return 1
    
    return 0


def cli_generate(base_path, config):
    """CLI: Generate static site (legacy command - uses builder)"""
    print("Generating static site files...")
    builder = Builder(base_path)
    success = builder.build_html('production')
    if success:
        print(f"✓ Static site generated successfully!")
        return 0
    return 1


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


def cli_archive_old_events(base_path):
    """CLI: Archive past events"""
    from modules.utils import archive_old_events
    
    print("Archiving past events...")
    archived_count = archive_old_events(base_path)
    
    if archived_count > 0:
        print(f"✓ Archived {archived_count} past event(s)")
        print(f"  Archived events saved to: {base_path / 'data' / 'archived_events.json'}")
    else:
        print("✓ No past events to archive")
    
    return 0


def cli_workflow(base_path, subcommand, args):
    """CLI: Manage GitHub Actions workflows"""
    launcher = WorkflowLauncher(base_path)
    
    if subcommand == 'list':
        # List available workflows
        workflows = launcher.list_workflows()
        
        print("\nAvailable GitHub Actions Workflows:")
        print("-" * 80)
        
        for i, workflow in enumerate(workflows, 1):
            print(f"\n{i}. {workflow['name']} (ID: {workflow['id']})")
            print(f"   {workflow['description']}")
            print(f"   File: .github/workflows/{workflow['file']}")
            if workflow['has_inputs']:
                print(f"   ⚙️  Configurable inputs available")
        
        print("-" * 80)
        print("\nUsage: python3 main.py workflow run WORKFLOW_ID [--branch BRANCH] [--input key=value]")
        return 0
    
    elif subcommand == 'run':
        # Trigger a workflow
        if not args:
            print("Error: Missing workflow ID")
            print("Usage: python3 main.py workflow run WORKFLOW_ID [--branch BRANCH] [--input key=value]")
            print("\nRun 'python3 main.py workflow list' to see available workflows")
            return 1
        
        workflow_id = args[0]
        branch = 'preview'
        inputs = {}
        
        # Parse additional arguments
        i = 1
        while i < len(args):
            if args[i] == '--branch' and i + 1 < len(args):
                branch = args[i + 1]
                i += 2
            elif args[i] == '--input' and i + 1 < len(args):
                inp = args[i + 1]
                if '=' in inp:
                    key, value = inp.split('=', 1)
                    inputs[key] = value
                i += 2
            else:
                i += 1
        
        print(f"Triggering workflow '{workflow_id}' on branch '{branch}'...")
        if inputs:
            print(f"Inputs: {inputs}")
        
        success, message = launcher.trigger_workflow(workflow_id, branch, inputs)
        print(message)
        
        if success:
            workflow_info = launcher.get_workflow_info(workflow_id)
            if workflow_info:
                print(f"\n💡 Monitor workflow at:")
                print(f"   https://github.com/feileberlin/krwl-hof/actions/workflows/{workflow_info['file']}")
        
        return 0 if success else 1
    
    elif subcommand == 'status':
        # Show workflow status
        if not args:
            print("Error: Missing workflow ID")
            print("Usage: python3 main.py workflow status WORKFLOW_ID")
            return 1
        
        workflow_id = args[0]
        limit = 5
        
        # Check for --limit argument
        if '--limit' in args:
            idx = args.index('--limit')
            if idx + 1 < len(args):
                try:
                    limit = int(args[idx + 1])
                except ValueError:
                    pass
        
        print(f"Recent runs of workflow '{workflow_id}':")
        success, runs = launcher.get_workflow_runs(workflow_id, limit)
        
        if success and runs:
            print("-" * 80)
            for run in runs:
                status = run.get('status', 'unknown')
                conclusion = run.get('conclusion', '-')
                branch = run.get('headBranch', '-')
                created = run.get('createdAt', '-')
                run_id = run.get('databaseId', '-')
                
                status_icon = '✓' if conclusion == 'success' else '✗' if conclusion == 'failure' else '⋯'
                print(f"{status_icon} Run #{run_id}: {status} / {conclusion}")
                print(f"   Branch: {branch} | Created: {created}")
            print("-" * 80)
        elif success:
            print("No recent runs found.")
        else:
            print("Failed to fetch workflow runs.")
        
        return 0
    
    else:
        print(f"Error: Unknown workflow subcommand '{subcommand}'")
        print("Available subcommands: list, run, status")
        return 1


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
        
        elif args.command == 'bulk-publish':
            if not args.args:
                print("Error: Missing event IDs")
                print("Usage: python3 main.py bulk-publish EVENT_ID1,EVENT_ID2,...")
                print("Example: python3 main.py bulk-publish pending_1,pending_2,pending_3")
                return 1
            return cli_bulk_publish_events(base_path, args.args[0])
        
        elif args.command == 'bulk-reject':
            if not args.args:
                print("Error: Missing event IDs")
                print("Usage: python3 main.py bulk-reject EVENT_ID1,EVENT_ID2,...")
                print("Example: python3 main.py bulk-reject pending_1,pending_2,pending_3")
                return 1
            return cli_bulk_reject_events(base_path, args.args[0])
        
        elif args.command == 'generate':
            return cli_generate(base_path, config)
        
        elif args.command == 'build':
            mode = args.args[0] if args.args else 'production'
            if mode not in ['production', 'development']:
                print(f"Error: Invalid mode '{mode}'")
                print("Usage: python3 main.py build [production|development]")
                return 1
            from modules.builder import Builder
            builder = Builder(base_path)
            return 0 if builder.build_html(mode) else 1
        
        elif args.command == 'events':
            from modules.builder import Builder
            builder = Builder(base_path)
            return 0 if builder.update_events() else 1
        
        elif args.command == 'libs':
            from modules.builder import Builder
            builder = Builder(base_path)
            if 'verify' in args.args or '--verify' in args.args:
                return 0 if builder.verify_libs() else 1
            return 0 if builder.download_libs() else 1
        
        elif args.command == 'archive':
            return cli_archive_old_events(base_path)
        
        elif args.command == 'load-examples':
            return cli_load_examples(base_path)
        
        elif args.command == 'clear-data':
            return cli_clear_data(base_path)
        
        elif args.command == 'workflow':
            # Workflow management commands
            if not args.args:
                print("Error: Missing workflow subcommand")
                print("Usage: python3 main.py workflow [list|run|status] [OPTIONS]")
                print("\nAvailable subcommands:")
                print("  list          List available workflows")
                print("  run WORKFLOW  Trigger a workflow")
                print("  status WORKFLOW Show workflow run status")
                return 1
            return cli_workflow(base_path, args.args[0], args.args[1:])
        
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
