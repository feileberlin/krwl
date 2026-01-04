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
from modules.site_generator import SiteGenerator
from modules.archive_events import EventArchiver, print_config_info
from modules.batch_operations import expand_wildcards, process_in_batches, find_events_by_ids, determine_batch_size
from modules.utils import (
    load_config, load_events, save_events, 
    load_pending_events, save_pending_events, 
    backup_published_event, update_events_in_html,
    add_rejected_event
)

# Import new optimization modules
try:
    from modules.event_schema import EventSchema, validate_events_file, migrate_events_file
    from modules.cache_manager import CacheManager
    from modules.minifier import Minifier
    from modules.compressor import Compressor
    from modules.build_optimizer import BuildOptimizer
    from modules.template_processor import TemplateProcessor
    from modules.config_validator import ConfigValidator
    from modules.icon_mode_tui import IconModeTUI, switch_icon_mode_cli, compare_icon_modes
except ImportError as e:
    print(f"Warning: Failed to import optimization modules: {e}")
    # Graceful degradation - these are optional features
    EventSchema = None
    CacheManager = None
    Minifier = None
    Compressor = None
    BuildOptimizer = None
    TemplateProcessor = None
    ConfigValidator = None
    IconModeTUI = None


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
            "scrape": "💡 Editorial Tip: Configure sources in data/config.json | Scraped events go to pending queue for review",
            "review": "💡 Editorial Tip: (a)pprove publishes to site | (e)dit before approval | (r)eject removes permanently",
            "published": "💡 Admin Tip: Published events appear on the map | Filtered by geolocation (<5km) & time (till sunrise)",
            "generate": "💡 Admin Tip: Build output → public/ dir | Deploy to GitHub Pages | Include .nojekyll file",
            "settings": "💡 Admin Tip: Load examples for testing | Backups created with .backup extension | Config: data/config.json",
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
        print("7. 📘 Setup Guide (Create Your Own Site)")
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
        
        generator = SiteGenerator(self.base_path)
        success = generator.generate_site()
        
        if success:
            print("\nStatic site generated successfully!")
            print(f"Files saved to: {self.base_path / 'public'}")
        
        self.print_footer("generate")
        input("\nPress Enter to continue...")
    
    def show_setup_guide(self):
        """Show setup guide for creating your own site"""
        self.clear_screen()
        print_setup_guide()
        input("\nPress Enter to return to menu...")
    
    def run(self):
        """Main TUI loop"""
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
                # Settings - placeholder
                self.clear_screen()
                self.print_header()
                print("Settings (Coming soon)")
                input("\nPress Enter to continue...")
            elif choice == '6':
                # Documentation - placeholder
                self.clear_screen()
                self.print_header()
                print("Documentation")
                print("-" * 60)
                print("\nFor full documentation, see README.md")
                print("Or visit: https://github.com/feileberlin/krwl-hof")
                input("\nPress Enter to continue...")
            elif choice == '7':
                self.show_setup_guide()
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
    python3 event_manager.py [COMMAND] [OPTIONS]

COMMANDS:
    (no command)              Launch interactive TUI (default)
    setup                     Show detailed setup instructions for your own site
    scrape                    Scrape events from configured sources
    review                    Review pending events interactively
    publish EVENT_ID          Publish a specific pending event
    reject EVENT_ID           Reject a specific pending event
    bulk-publish IDS          Bulk publish pending events (comma-separated IDs/patterns)
    bulk-reject IDS           Bulk reject pending events (comma-separated IDs/patterns)
    list                      List all published events
    list-pending              List all pending events
    
    generate                  Generate static site with inlined HTML
                              - Ensures dependencies (Leaflet.js)
                              - Loads all resources (CSS, JS, events, translations)
                              - Builds HTML from templates with inlined assets
                              - Lints and validates content
                              - Outputs: public/index.html (self-contained)
    update                    Update events data in existing site (fast)
    dependencies fetch        Fetch third-party dependencies
    dependencies check        Check if dependencies are present
    
    schema validate           Validate events against schema
    schema migrate            Migrate events to new schema format
    schema categories         List all valid event categories
    
    cache stats               Show cache statistics
    cache clear               Clear asset cache
    cache inspect KEY         Inspect specific cache entry
    
    icons                     Show current icon mode
    icons mode [MODE]         Set or show icon mode (svg-paths | base64)
    icons switch              Interactive icon mode switcher
    icons compare             Compare icon modes
    
    config validate           Validate configuration file
    
    test                      Run all tests
    test --list               List available test categories and tests
    test core                 Run core functionality tests
    test features             Run feature tests
    test infrastructure       Run infrastructure tests
    test scraper              Run specific test (e.g., test_scraper)
    test --verbose            Run tests with verbose output
    
    utils                     List all utility commands
    utils --list              List all utility commands
    utils kiss-check          Check KISS compliance
    utils verify-features     Verify features are present
    utils config-edit         Launch config editor
    
    docs                      List all documentation tasks
    docs --list               List all documentation tasks
    docs readme               Generate README.md
    docs demos                Generate demo events
    docs lint-markdown        Lint markdown files
    docs generate             Run all generation tasks
    docs validate             Run all validation tasks
    
    archive-monthly           Archive old events based on retention window
    archive-monthly --dry-run Preview archiving without making changes
    archive-info              Show archiving configuration and existing archives
    archive                   Archive past events to archived_events.json (legacy)
    load-examples             Load example data for development
    clear-data                Clear all event data
    scraper-info              Show scraper capabilities (JSON output for workflows)
    
OPTIONS:
    -h, --help               Show this help message
    -v, --version            Show version information
    -c, --config PATH        Use custom config file
    
EXAMPLES:
    # Launch interactive TUI
    python3 event_manager.py
    
    # Generate static site (runtime-configurable)
    python3 event_manager.py generate
    
    # Fast content update
    python3 event_manager.py update
    
    # Fetch dependencies
    python3 event_manager.py dependencies fetch
    
    # Check dependencies
    python3 event_manager.py dependencies check
    
    # Scrape events from sources
    python3 event_manager.py scrape
    
    # Show scraper capabilities (for workflow introspection)
    python3 event_manager.py scraper-info
    
    # List all published events
    python3 event_manager.py list
    
    # Publish a single event
    python3 event_manager.py publish pending_1
    
    # Bulk publish using wildcards
    python3 event_manager.py bulk-publish "pending_*"
    
    # Load example data for testing
    python3 event_manager.py load-examples
    
    # Run all tests
    python3 event_manager.py test
    
    # Run specific test category
    python3 event_manager.py test core
    python3 event_manager.py test features
    
    # Run individual test
    python3 event_manager.py test scraper
    python3 event_manager.py test translations
    
    # List available tests
    python3 event_manager.py test --list
    
    # Run tests with verbose output
    python3 event_manager.py test --verbose
    python3 event_manager.py test core --verbose
    
    # Run utilities
    python3 event_manager.py utils --list
    python3 event_manager.py utils kiss-check
    python3 event_manager.py utils verify-features --verbose
    
    # Documentation tasks
    python3 event_manager.py docs --list
    python3 event_manager.py docs readme
    python3 event_manager.py docs lint-markdown --all
    python3 event_manager.py docs lint-markdown README.md
    python3 event_manager.py docs lint-markdown --fix --all
    python3 event_manager.py docs generate
    python3 event_manager.py docs validate
    
    # Get help
    python3 event_manager.py --help

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


def print_setup_guide():
    """Print detailed setup instructions for creating your own KRWL site"""
    setup_guide = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KRWL SETUP GUIDE - Create Your Own Site                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

This guide helps you set up "krwl-xyz" - your own community events website.

📋 TABLE OF CONTENTS
────────────────────────────────────────────────────────────────────────────────
1. Prerequisites
2. Initial Setup
3. Configuration
4. Customization
5. Deployment
6. Maintenance

═══════════════════════════════════════════════════════════════════════════════
1. PREREQUISITES
═══════════════════════════════════════════════════════════════════════════════

✓ Python 3.7 or higher
✓ Git
✓ A git hosting account (GitHub, GitLab, Gitea, etc.)
✓ Optional: Domain name for your site

Check your setup:
  $ python3 --version
  $ git --version

═══════════════════════════════════════════════════════════════════════════════
2. INITIAL SETUP
═══════════════════════════════════════════════════════════════════════════════

Step 1: Clone or Fork the Repository
────────────────────────────────────────────────────────────────────────────────
  # Option A: Fork on your git hosting platform
  1. Go to the repository page
  2. Click "Fork" button
  3. Clone your fork:
     $ git clone https://your-host.com/your-username/krwl-xyz.git
     $ cd krwl-xyz

  # Option B: Clone and re-initialize
     $ git clone https://github.com/feileberlin/krwl-hof.git krwl-xyz
     $ cd krwl-xyz
     $ rm -rf .git
     $ git init
     $ git add .
     $ git commit -m "Initial commit for krwl-xyz"

Step 2: Install Dependencies
────────────────────────────────────────────────────────────────────────────────
  $ pip install -r requirements.txt

Step 3: Fetch Third-Party Dependencies (Leaflet)
────────────────────────────────────────────────────────────────────────────────
  $ python3 src/event_manager.py dependencies fetch

  This downloads:
  - Leaflet.js (map library)
  - Required CSS and images

═══════════════════════════════════════════════════════════════════════════════
3. CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

Edit data/config.json (Unified Configuration - Auto-Adapts to Environment)
────────────────────────────────────────────────────────────────────────────────
  Open data/config.json and customize:

  {
    "app": {
      "name": "Your City Events",           ← Change this
      "description": "Community events"
    },
    "map": {
      "default_center": {
        "lat": 50.3167,                     ← Your city coordinates
        "lon": 11.9167
      },
      "default_zoom": 13
    },
    "scraping": {
      "sources": [                          ← Add your event sources
        {
          "name": "Local Events Site",
          "url": "https://example.com/events",
          "type": "html",
          "enabled": true
        }
      ]
    }
  }

  ✨ AUTOMATIC ENVIRONMENT DETECTION:
  - Local development: Automatically enables debug mode and demo events
  - Production/CI: Automatically optimizes for performance and real data only
  - Works with all hosting platforms: GitHub Pages, Vercel, Netlify, Heroku, 
    Railway, Render, Fly.io, Google Cloud Run, AWS, and more!
  - No manual switching needed - just deploy and it adapts!

  See DEPLOYMENT.md for hosting platform setup guides.

Update Translations
────────────────────────────────────────────────────────────────────────────────
  Edit these files for your language:
  - assets/json/i18n/content.json (English)
  - assets/json/i18n/content.de.json (German)
  
  Or create new language files:
  - assets/json/i18n/content.fr.json (French)
  - assets/json/i18n/content.es.json (Spanish)

═══════════════════════════════════════════════════════════════════════════════
4. CUSTOMIZATION
═══════════════════════════════════════════════════════════════════════════════

Customize Branding
────────────────────────────────────────────────────────────────────────────────
  1. Replace favicon:
     - assets/favicon.svg
     
  2. Update colors in assets/css/style.css:
     :root {
       --primary-color: #FF69B4;    ← Change to your brand color
       --bg-color: #1a1a1a;
       --text-color: #ffffff;
     }
  
  3. Update PWA manifest (assets/json/manifest.json):
     {
       "name": "Your City Events",
       "short_name": "YourCity",
       "theme_color": "#FF69B4"
     }

Add Event Sources
────────────────────────────────────────────────────────────────────────────────
  In data/config.json → scraping.sources[], add:
  
  {
    "name": "Your Event Source",
    "url": "https://example.com/events",
    "type": "html",          # or "rss", "api"
    "enabled": true,
    "options": {
      "category": "culture",
      "default_location": {
        "name": "City Center",
        "lat": 50.000,
        "lon": 11.000
      }
    }
  }

═══════════════════════════════════════════════════════════════════════════════
5. DEPLOYMENT
═══════════════════════════════════════════════════════════════════════════════

Generate Your Site
────────────────────────────────────────────────────────────────────────────────
  $ python3 src/event_manager.py generate

  This creates:
  - public/index.html (your complete site in one file!)
  - Embeds all configs (runtime environment detection)
  - Includes all events

Test Locally
────────────────────────────────────────────────────────────────────────────────
  $ cd public
  $ python3 -m http.server 8000
  
  Open: http://localhost:8000
  
  The site will automatically detect it's running locally and use dev config.

Deploy to Git Hosting
────────────────────────────────────────────────────────────────────────────────
  Most git hosts support static site hosting:

  GitHub Pages:
    1. Push to main branch
    2. Go to Settings → Pages
    3. Source: Deploy from branch "main", folder "/public"
    4. Save

  GitLab Pages:
    1. Add .gitlab-ci.yml:
       pages:
         script:
           - cp -r public .
         artifacts:
           paths:
             - public
    2. Push to main branch

  Gitea Pages:
    1. Enable Pages in repository settings
    2. Configure to serve from /public directory
    3. Push to main branch

Custom Domain (Optional)
────────────────────────────────────────────────────────────────────────────────
  1. Add CNAME file in public/ with your domain
  2. Configure DNS:
     - CNAME record pointing to your git host
  3. Enable HTTPS in your git host settings

═══════════════════════════════════════════════════════════════════════════════
6. MAINTENANCE
═══════════════════════════════════════════════════════════════════════════════

Daily Operations
────────────────────────────────────────────────────────────────────────────────
  # Scrape new events
  $ python3 src/event_manager.py scrape

  # Review pending events
  $ python3 src/event_manager.py review

  # Update site with new events (fast!)
  $ python3 src/event_manager.py update

  # Commit and push
  $ git add public/
  $ git commit -m "Update events"
  $ git push

Automated Updates
────────────────────────────────────────────────────────────────────────────────
  Set up automation in your git host:

  GitHub Actions (.github/workflows/scrape.yml):
    on:
      schedule:
        - cron: '0 4 * * *'  # Daily at 4 AM
    jobs:
      scrape:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: pip install -r requirements.txt
          - run: python3 src/event_manager.py scrape
          - run: python3 src/event_manager.py update
          - run: |
              git config user.name "bot"
              git config user.email "bot@example.com"
              git add public/
              git commit -m "Auto-update events"
              git push

  GitLab CI (.gitlab-ci.yml):
    Similar structure with scheduled pipelines

  Gitea Actions:
    Similar to GitHub Actions

═══════════════════════════════════════════════════════════════════════════════
💡 QUICK START CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

  □ Install dependencies: pip install -r requirements.txt
  □ Fetch libraries: python3 src/event_manager.py dependencies fetch
  □ Edit data/config.json (app name, location, event sources)
  □ Customize colors in assets/css/style.css
  □ Replace favicon: assets/favicon.svg
  □ Generate site: python3 src/event_manager.py generate
  □ Test locally: cd public && python3 -m http.server 8000
  □ Deploy to hosting platform (see DEPLOYMENT.md)
  □ (Optional) Configure custom domain

═══════════════════════════════════════════════════════════════════════════════
🎯 NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

  1. Run interactive TUI to explore features:
     $ python3 src/event_manager.py

  2. Read full documentation:
     - README.md (consolidated guide)
     - Inline code comments for technical details

  3. Join the community:
     - GitHub: https://github.com/feileberlin/krwl-hof
     - Issues: Report bugs or request features

═══════════════════════════════════════════════════════════════════════════════

Need help? Run: python3 src/event_manager.py --help

"""
    print(setup_guide)


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


def _find_events_to_process(event_ids, events):
    """Find events and their indices from the pending list.
    
    Args:
        event_ids: List of event IDs to find
        events: List of pending events
        
    Returns:
        Tuple of (events_to_process, failed_ids)
    """
    events_to_process = []
    failed_ids = []
    
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
            failed_ids.append(event_id)
        else:
            events_to_process.append((event_index, event_id, event))
    
    # Sort by index in reverse order to safely remove from pending list
    events_to_process.sort(key=lambda x: x[0], reverse=True)
    
    return events_to_process, failed_ids


def _publish_events_batch(base_path, events_to_publish, events, events_data):
    """Publish a batch of events.
    
    Args:
        base_path: Repository root path
        events_to_publish: List of (index, id, event) tuples
        events: Pending events list (modified in place)
        events_data: Published events data (modified in place)
        
    Returns:
        Tuple of (published_count, failed_count, failed_ids)
    """
    published_count = 0
    failed_count = 0
    failed_ids = []
    
    for event_index, event_id, event in events_to_publish:
        try:
            # Publish event
            event['status'] = 'published'
            event['published_at'] = datetime.now().isoformat()
            
            # Backup the published event
            backup_published_event(base_path, event)
            
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
    
    return published_count, failed_count, failed_ids


def cli_bulk_publish_events(base_path, event_ids_str):
    """CLI: Bulk publish pending events (supports wildcards and batching)"""
    # Parse comma-separated event IDs/patterns
    patterns = [p.strip() for p in event_ids_str.split(',')]
    
    if not patterns:
        print("Error: No event IDs or patterns provided")
        return 1
    
    pending_data = load_pending_events(base_path)
    events = pending_data.get('pending_events', [])
    
    # Expand wildcards using modular function
    event_ids = expand_wildcards(patterns, events)
    
    if not event_ids:
        print("Error: No events matched the provided patterns")
        return 1
    
    events_data = load_events(base_path)
    
    print(f"📝 Bulk publishing {len(event_ids)} event(s)...")
    print("=" * 80)
    
    # Determine optimal batch size
    batch_size = determine_batch_size(len(event_ids))
    
    # Process in batches using modular function
    def publish_batch(batch_ids, batch_num, total_batches):
        """Process a batch of events for publishing"""
        batch_result = {'success': [], 'failed': []}
        
        # Find events in this batch
        events_to_publish, failed_ids = find_events_by_ids(batch_ids, events)
        batch_result['failed'].extend(failed_ids)
        
        # Publish the batch
        published_count, pub_failed_count, pub_failed_ids = _publish_events_batch(
            base_path, events_to_publish, events, events_data
        )
        
        # Track successes
        for event_id in batch_ids:
            if event_id not in failed_ids and event_id not in pub_failed_ids:
                batch_result['success'].append(event_id)
        
        batch_result['failed'].extend(pub_failed_ids)
        
        print(f"   ✓ Batch {batch_num}: {len(batch_result['success'])} published, {len(batch_result['failed'])} failed")
        
        return batch_result
    
    # Process all batches
    results = process_in_batches(event_ids, batch_size=batch_size, callback=publish_batch)
    
    # Save changes if any events were published
    if results['processed'] > 0:
        print("\n💾 Saving changes...")
        save_events(base_path, events_data)
        save_pending_events(base_path, pending_data)
        
        print("🔄 Updating events in HTML...")
        update_events_in_html(base_path)
    
    # Summary
    print("=" * 80)
    print(f"✅ Successfully published: {results['processed']} event(s)")
    if results['failed'] > 0:
        print(f"❌ Failed: {results['failed']} event(s)")
        return 1
    
    return 0


def _reject_events_batch(base_path, events_to_reject, events):
    """Reject a batch of events.
    
    Args:
        base_path: Repository root path
        events_to_reject: List of (index, id, title, source) tuples
        events: Pending events list (modified in place)
        
    Returns:
        Tuple of (rejected_count, failed_count, failed_ids)
    """
    rejected_count = 0
    failed_count = 0
    failed_ids = []
    
    for event_index, event_id, event_title, event_source in events_to_reject:
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
    
    return rejected_count, failed_count, failed_ids


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
    
    print(f"Bulk rejecting {len(event_ids)} event(s)...")
    print("-" * 80)
    
    # Find events to reject
    events_to_reject = []
    failed_ids = []
    
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
            failed_ids.append(event_id)
        else:
            events_to_reject.append((event_index, event_id, event_title, event_source))
    
    # Sort by index in reverse order
    events_to_reject.sort(key=lambda x: x[0], reverse=True)
    
    # Reject events
    rejected_count, rej_failed_count, rej_failed_ids = _reject_events_batch(
        base_path, events_to_reject, events
    )
    failed_count = len(failed_ids) + rej_failed_count
    failed_ids.extend(rej_failed_ids)
    
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
    """
    CLI: Generate static site with inlined HTML.
    
    Creates a self-contained HTML file with all CSS, JS, events, and translations
    embedded. Uses KISS templating (Python .format()) from assets/html/.
    
    Output: public/index.html (~313KB single-file HTML)
    """
    print("Generating static site...")
    generator = SiteGenerator(base_path)
    success = generator.generate_site()
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


def cli_archive_monthly(base_path, config, dry_run=False):
    """
    Archive old events based on configurable retention window.
    
    This command moves events older than the configured retention window
    (default: 60 days) to monthly archive files. This keeps the active
    events list manageable and improves site performance.
    
    Configuration: config.json → archiving section
    - retention.active_window_days: How many days to keep active
    - organization.path: Where to save archives
    - organization.format: Archive filename format (YYYYMM or YYYY-MM)
    
    Usage:
        python3 src/event_manager.py archive-monthly           # Run archiving
        python3 src/event_manager.py archive-monthly --dry-run # Preview changes
    
    Archives are organized by month (e.g., 202601.json for January 2026)
    and stored in assets/json/events/archived/
    
    Args:
        base_path: Repository root path
        config: Loaded configuration
        dry_run: If True, show what would be archived without making changes
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        archiver = EventArchiver(config, base_path)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print("-" * 60)
        
        results = archiver.archive_events(dry_run=dry_run)
        
        if not results.get('enabled'):
            print("ℹ️  Archiving is disabled in config.json")
            print("   To enable: Set archiving.enabled = true")
            return 0
        
        # Print results
        print(f"\n{'DRY RUN ' if dry_run else ''}ARCHIVING RESULTS")
        print("=" * 60)
        print(f"Total events: {results['total_events']}")
        print(f"{'Would archive' if dry_run else 'Archived'}: {results['archived_count']}")
        print(f"Remaining active: {results['active_count']}")
        print(f"Retention window: {results['retention_days']} days")
        print(f"Cutoff date: {results['cutoff_date'][:10]}")
        
        if results['archived_count'] > 0:
            if not dry_run:
                print(f"\n✓ Successfully archived {results['archived_count']} event(s)")
                print(f"  Archives saved to: {archiver.archive_path}")
                
                # List archives
                archives = archiver.list_archives()
                if archives:
                    print(f"\n  Archive files:")
                    for arch in archives[-5:]:  # Show last 5 archives
                        print(f"    • {arch['filename']}: {arch['event_count']} events")
            else:
                print(f"\n💡 Run without --dry-run to archive these events")
        else:
            print("\n✓ No events to archive (all within retention window)")
        
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"✗ Error during archiving: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cli_archive_info(base_path, config):
    """
    Display current event archiving configuration.
    
    Shows the archiving settings from config.json including:
    - Whether archiving is enabled
    - Retention window (how many days of events stay active)
    - Schedule (when archiving runs automatically)
    - Archive organization (path, format, grouping)
    
    Usage:
        python3 src/event_manager.py archive-info
    
    This is useful for understanding how archiving works and
    verifying your configuration before running archiving.
    
    Args:
        base_path: Repository root path
        config: Loaded configuration
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        archiver = EventArchiver(config, base_path)
        
        # Use the shared print function from archive_events module
        print_config_info(archiver)
        
        # List existing archives
        archives = archiver.list_archives()
        if archives:
            print("EXISTING ARCHIVES")
            print("=" * 60)
            print(f"Total archive files: {len(archives)}")
            print("\nRecent archives:")
            for arch in archives[-10:]:  # Show last 10
                print(f"  • {arch['filename']}: {arch['event_count']} events "
                      f"(updated: {arch['last_updated'][:10]})")
            print("=" * 60)
        else:
            print("No archive files yet.")
            print("Run 'archive-monthly' to create archives.")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error reading archive configuration: {e}")
        return 1


def cli_test(base_path, test_name=None, verbose=False, list_tests=False):
    """CLI: Run tests
    
    Args:
        base_path: Repository root path
        test_name: Test category name (core, features, infrastructure) or specific test name to run
        verbose: Enable verbose output
        list_tests: List available tests
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    from modules.test_runner import TestRunner
    
    runner = TestRunner(base_path, verbose=verbose)
    
    if list_tests:
        runner.list_tests()
        return 0
    
    # If a specific name is provided, check if it's a category or individual test
    if test_name:
        # Check if it's a category
        if test_name in runner.TEST_CATEGORIES:
            result = runner.run_category(test_name)
            return 0 if result['success'] else 1
        # Otherwise treat as individual test
        return 0 if runner.run_single(test_name) else 1
    
    # No specific test name provided: run all tests
    return 0 if runner.run_all() else 1


# ==================== Production Optimization CLI Commands ====================

def cli_schema_validate(base_path):
    """Validate events against schema"""
    if not EventSchema:
        print("❌ Event schema module not available")
        return 1
    
    events_file = base_path / 'assets' / 'json' / 'events.json'
    
    if not events_file.exists():
        print(f"❌ Events file not found: {events_file}")
        return 1
    
    is_valid, errors, invalid = validate_events_file(events_file)
    
    if is_valid:
        print(f"✅ All events in {events_file.name} are valid!")
        return 0
    else:
        print(f"❌ Found {len(errors)} validation error(s):")
        for error in errors:
            print(f"  • {error}")
        return 1


def cli_schema_migrate(base_path):
    """Migrate events to new schema"""
    if not EventSchema:
        print("❌ Event schema module not available")
        return 1
    
    events_file = base_path / 'assets' / 'json' / 'events.json'
    
    if not events_file.exists():
        print(f"❌ Events file not found: {events_file}")
        return 1
    
    count = migrate_events_file(events_file)
    
    if count > 0:
        print(f"✅ Migrated {count} events to new schema")
        print(f"   Backup created: {events_file}.backup")
        return 0
    else:
        print("❌ Migration failed")
        return 1


def cli_schema_categories(base_path):
    """List valid event categories"""
    if not EventSchema:
        print("❌ Event schema module not available")
        return 1
    
    schema = EventSchema()
    
    print(f"\n📋 Valid Event Categories ({len(schema.categories)} total)")
    print("=" * 60)
    
    for i, category in enumerate(schema.categories, 1):
        icon = schema.get_icon_for_category(category)
        print(f"  {i:2d}. {category:30s} → {icon}")
    
    print("=" * 60)
    return 0


def cli_cache_stats(base_path):
    """Show cache statistics"""
    if not CacheManager:
        print("❌ Cache manager module not available")
        return 1
    
    cache = CacheManager(base_path)
    cache.print_stats()
    return 0


def cli_cache_clear(base_path):
    """Clear cache"""
    if not CacheManager:
        print("❌ Cache manager module not available")
        return 1
    
    cache = CacheManager(base_path)
    count = cache.clear()
    
    print(f"✅ Cleared {count} cache entries")
    return 0


def cli_cache_inspect(base_path, key):
    """Inspect cache entry"""
    if not CacheManager:
        print("❌ Cache manager module not available")
        return 1
    
    cache = CacheManager(base_path)
    entry = cache.inspect(key)
    
    if entry:
        print(f"\n📦 Cache Entry: {key}")
        print("=" * 60)
        for k, v in entry.items():
            print(f"  {k:20s}: {v}")
        print("=" * 60)
        return 0
    else:
        print(f"❌ Key not found: {key}")
        return 1


def cli_icons_mode(base_path, mode=None):
    """Set or show icon mode"""
    if not IconModeTUI:
        print("❌ Icon mode TUI module not available")
        return 1
    
    config_path = base_path / 'config.json'
    
    if mode:
        # Set mode
        success = switch_icon_mode_cli(base_path, mode, config_path)
        return 0 if success else 1
    else:
        # Show current mode
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_mode = config.get('icons', {}).get('mode', 'svg-paths')
            
            print(f"\n🎨 Current Icon Mode: {current_mode}")
            print("=" * 60)
            
            mode_info = IconModeTUI.MODE_INFO.get(current_mode, {})
            for key, value in mode_info.items():
                print(f"  {key:20s}: {value}")
            
            print("=" * 60)
            print()
            print("💡 To change mode:")
            print("   python3 src/event_manager.py icons mode <svg-paths|base64>")
            print("   python3 src/event_manager.py icons switch (interactive)")
            
            return 0
        except Exception as e:
            print(f"❌ Failed to read config: {e}")
            return 1


def cli_icons_switch(base_path):
    """Interactive icon mode switcher"""
    if not IconModeTUI:
        print("❌ Icon mode TUI module not available")
        return 1
    
    tui = IconModeTUI(base_path)
    result = tui.run()
    
    return 0 if result else 1


def cli_icons_compare(base_path):
    """Compare icon modes"""
    if not IconModeTUI:
        print("❌ Icon mode TUI module not available")
        return 1
    
    compare_icon_modes()
    return 0


def cli_config_validate(base_path):
    """Validate configuration"""
    if not ConfigValidator:
        print("❌ Config validator module not available")
        return 1
    
    config_path = base_path / 'config.json'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return 1
    
    validator = ConfigValidator()
    is_valid = validator.print_validation_results(config)
    
    return 0 if is_valid else 1


def _execute_command(args, base_path, config):
    """Execute the specified CLI command.
    
    Args:
        args: Parsed command line arguments
        base_path: Repository root path
        config: Loaded configuration
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    command = args.command
    
    if command == 'setup':
        print_setup_guide()
        return 0
    
    if command == 'scrape':
        return cli_scrape(base_path, config)
    
    if command == 'list':
        return cli_list_events(base_path)
    
    if command == 'list-pending':
        return cli_list_pending(base_path)
    
    if command == 'publish':
        if not args.args:
            print("Error: Missing event ID")
            print("Usage: python3 event_manager.py publish EVENT_ID")
            return 1
        return cli_publish_event(base_path, args.args[0])
    
    if command == 'reject':
        if not args.args:
            print("Error: Missing event ID")
            print("Usage: python3 event_manager.py reject EVENT_ID")
            return 1
        return cli_reject_event(base_path, args.args[0])
    
    if command == 'bulk-publish':
        if not args.args:
            print("Error: Missing event IDs")
            print("Usage: python3 event_manager.py bulk-publish EVENT_ID1,EVENT_ID2,...")
            return 1
        return cli_bulk_publish_events(base_path, args.args[0])
    
    if command == 'bulk-reject':
        if not args.args:
            print("Error: Missing event IDs")
            print("Usage: python3 event_manager.py bulk-reject EVENT_ID1,EVENT_ID2,...")
            return 1
        return cli_bulk_reject_events(base_path, args.args[0])
    
    if command == 'generate':
        return cli_generate(base_path, config)
    
    if command == 'update':
        generator = SiteGenerator(base_path)
        return 0 if generator.update_events_data() else 1
    
    if command == 'dependencies':
        return _execute_dependencies_command(args, base_path)
    
    if command == 'archive':
        return cli_archive_old_events(base_path)
    
    if command == 'load-examples':
        return cli_load_examples(base_path)
    
    if command == 'clear-data':
        return cli_clear_data(base_path)
    
    if command == 'test':
        # Parse test arguments
        verbose = '--verbose' in args.args if args.args else False
        list_tests = '--list' in args.args if args.args else False
        
        # Filter out flags to get the actual test/category name
        test_args = [arg for arg in (args.args or []) if not arg.startswith('--')]
        test_name = test_args[0] if test_args else None
        
        return cli_test(base_path, test_name=test_name, verbose=verbose, list_tests=list_tests)
    
    if command == 'utils':
        # Delegate to utility runner module (KISS: keep main CLI simple)
        from modules.utility_runner import UtilityRunner
        
        runner = UtilityRunner(base_path)
        
        # Check for --list flag
        if not args.args or '--list' in args.args:
            runner.list_utilities()
            return 0
        
        # Run specific utility with remaining args
        utility_name = args.args[0]
        utility_args = args.args[1:]
        return 0 if runner.run_utility(utility_name, utility_args) else 1
    
    if command == 'docs':
        # Delegate to documentation runner module (KISS: keep main CLI simple)
        from modules.docs_runner import DocsRunner
        
        runner = DocsRunner(base_path)
        
        # Check for --list flag
        if not args.args or '--list' in args.args:
            runner.list_tasks()
            return 0
        
        # Run specific task or category with remaining args
        task_name = args.args[0]
        task_args = args.args[1:]
        
        # Check if it's a category
        if task_name in runner.DOCS_TASKS:
            return 0 if runner.run_category(task_name) else 1
        
        # Otherwise run as individual task
        return 0 if runner.run_task(task_name, task_args) else 1
    
    if command == 'archive-monthly':
        # Archive old events based on config retention window
        return cli_archive_monthly(base_path, config, dry_run='--dry-run' in (args.args or []))
    
    if command == 'archive-info':
        # Show archiving configuration
        return cli_archive_info(base_path, config)
    
    if command == 'review':
        app = EventManagerTUI()
        app.review_pending_events()
        return 0
    
    if command == 'scraper-info':
        # Output scraper capabilities as JSON for workflow consumption
        scraper = EventScraper(config, base_path)
        capabilities = scraper.get_scraper_capabilities()
        print(json.dumps(capabilities, indent=2))
        return 0
    
    # Production Optimization Commands
    if command == 'schema':
        # Schema subcommands
        if not args.args:
            print("Error: Missing schema subcommand")
            print("Usage: python3 event_manager.py schema [validate|migrate|categories]")
            return 1
        
        subcommand = args.args[0]
        
        if subcommand == 'validate':
            return cli_schema_validate(base_path)
        elif subcommand == 'migrate':
            return cli_schema_migrate(base_path)
        elif subcommand == 'categories':
            return cli_schema_categories(base_path)
        else:
            print(f"Error: Unknown schema subcommand '{subcommand}'")
            return 1
    
    if command == 'cache':
        # Cache subcommands
        if not args.args:
            print("Error: Missing cache subcommand")
            print("Usage: python3 event_manager.py cache [stats|clear|inspect KEY]")
            return 1
        
        subcommand = args.args[0]
        
        if subcommand == 'stats':
            return cli_cache_stats(base_path)
        elif subcommand == 'clear':
            return cli_cache_clear(base_path)
        elif subcommand == 'inspect' and len(args.args) > 1:
            return cli_cache_inspect(base_path, args.args[1])
        else:
            print(f"Error: Unknown or incomplete cache subcommand")
            print("Usage: python3 event_manager.py cache [stats|clear|inspect KEY]")
            return 1
    
    if command == 'icons':
        # Icons subcommands
        if not args.args:
            # No subcommand - show current mode
            return cli_icons_mode(base_path)
        
        subcommand = args.args[0]
        
        if subcommand == 'mode':
            if len(args.args) > 1:
                # Set mode
                return cli_icons_mode(base_path, args.args[1])
            else:
                # Show mode
                return cli_icons_mode(base_path)
        elif subcommand == 'switch':
            return cli_icons_switch(base_path)
        elif subcommand == 'compare':
            return cli_icons_compare(base_path)
        else:
            print(f"Error: Unknown icons subcommand '{subcommand}'")
            print("Usage: python3 event_manager.py icons [mode|switch|compare]")
            return 1
    
    if command == 'config':
        # Config subcommands
        if not args.args:
            print("Error: Missing config subcommand")
            print("Usage: python3 event_manager.py config [validate]")
            return 1
        
        subcommand = args.args[0]
        
        if subcommand == 'validate':
            return cli_config_validate(base_path)
        else:
            print(f"Error: Unknown config subcommand '{subcommand}'")
            return 1
    
    if command is None:
        # No command - launch interactive TUI
        app = EventManagerTUI()
        app.run()
        return 0
    
    print(f"Error: Unknown command '{command}'")
    print("Use --help to see available commands")
    return 1


def _execute_dependencies_command(args, base_path):
    """Execute dependencies subcommand.
    
    Args:
        args: Parsed command line arguments
        base_path: Repository root path
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not args.args:
        print("Error: Missing dependencies subcommand")
        print("Usage: python3 event_manager.py dependencies [fetch|check]")
        return 1
    
    generator = SiteGenerator(base_path)
    subcommand = args.args[0]
    
    if subcommand == 'fetch':
        return 0 if generator.fetch_all_dependencies() else 1
    
    if subcommand == 'check':
        return 0 if generator.check_all_dependencies() else 1
    
    print(f"Error: Unknown dependencies subcommand '{subcommand}'")
    print("Usage: python3 event_manager.py dependencies [fetch|check]")
    return 1


def main():
    """Main entry point"""
    # Use parse_known_args to allow command-specific flags
    parser = argparse.ArgumentParser(
        description='KRWL HOF Community Events Manager',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default=None,
                       help='Command to execute')
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show help message')
    parser.add_argument('-v', '--version', action='store_true',
                       help='Show version')
    parser.add_argument('-c', '--config', type=str,
                       help='Custom config file path')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    # Parse known args first, then capture remaining args
    args, remaining = parser.parse_known_args()
    args.args = remaining  # Store remaining args for command processing
    
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
    
    # Configure logging based on mode
    from modules.logging_config import configure_for_cli, configure_for_tui
    if args.command is None:
        # TUI mode - log to file only
        configure_for_tui()
    else:
        # CLI mode - log to console
        configure_for_cli(debug=args.debug)
    
    try:
        # Load config
        config = load_config(base_path)
        
        # Execute command
        return _execute_command(args, base_path, config)
            
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
