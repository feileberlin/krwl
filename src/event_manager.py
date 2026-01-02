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
            print(f"Files saved to: {self.base_path / 'static'}")
        
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
                              - Outputs: static/index.html (self-contained)
    update                    Update events data in existing site (fast)
    dependencies fetch        Fetch third-party dependencies
    dependencies check        Check if dependencies are present
    
    archive                   Archive past events (automatic on generate)
    load-examples             Load example data for development
    clear-data                Clear all event data
    
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
    
    # List all published events
    python3 event_manager.py list
    
    # Publish a single event
    python3 event_manager.py publish pending_1
    
    # Bulk publish using wildcards
    python3 event_manager.py bulk-publish "pending_*"
    
    # Load example data for testing
    python3 event_manager.py load-examples
    
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

Edit config.json (Unified Configuration - Auto-Adapts to Environment)
────────────────────────────────────────────────────────────────────────────────
  Open config.json and customize:

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
  - data/content.json (English)
  - data/content.de.json (German)
  
  Or create new language files:
  - data/content.fr.json (French)
  - data/content.es.json (Spanish)

═══════════════════════════════════════════════════════════════════════════════
4. CUSTOMIZATION
═══════════════════════════════════════════════════════════════════════════════

Customize Branding
────────────────────────────────────────────────────────────────────────────────
  1. Replace favicon:
     - static/favicon.svg
     
  2. Update colors in static/css/style.css:
     :root {
       --primary-color: #FF69B4;    ← Change to your brand color
       --bg-color: #1a1a1a;
       --text-color: #ffffff;
     }
  
  3. Update PWA manifest (static/manifest.json):
     {
       "name": "Your City Events",
       "short_name": "YourCity",
       "theme_color": "#FF69B4"
     }

Add Event Sources
────────────────────────────────────────────────────────────────────────────────
  In config.json → scraping.sources[], add:
  
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
  - static/index.html (your complete site in one file!)
  - Embeds all configs (runtime environment detection)
  - Includes all events

Test Locally
────────────────────────────────────────────────────────────────────────────────
  $ cd static
  $ python3 -m http.server 8000
  
  Open: http://localhost:8000
  
  The site will automatically detect it's running locally and use dev config.

Deploy to Git Hosting
────────────────────────────────────────────────────────────────────────────────
  Most git hosts support static site hosting:

  GitHub Pages:
    1. Push to main branch
    2. Go to Settings → Pages
    3. Source: Deploy from branch "main", folder "/static"
    4. Save

  GitLab Pages:
    1. Add .gitlab-ci.yml:
       pages:
         script:
           - cp -r static public
         artifacts:
           paths:
             - public
    2. Push to main branch

  Gitea Pages:
    1. Enable Pages in repository settings
    2. Configure to serve from /static directory
    3. Push to main branch

Custom Domain (Optional)
────────────────────────────────────────────────────────────────────────────────
  1. Add CNAME file in static/ with your domain
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
  $ git add static/
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
              git add static/
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
  □ Edit config.json (app name, location, event sources)
  □ Customize colors in static/css/style.css
  □ Replace favicon: static/favicon.svg
  □ Generate site: python3 src/event_manager.py generate
  □ Test locally: cd static && python3 -m http.server 8000
  □ Deploy to hosting platform (see DEPLOYMENT.md)
  □ (Optional) Configure custom domain

═══════════════════════════════════════════════════════════════════════════════
🎯 NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

  1. Run interactive TUI to explore features:
     $ python3 src/event_manager.py

  2. Read full documentation:
     - README.md
     - docs/ directory

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
    
    print(f"Bulk publishing {len(event_ids)} event(s)...")
    print("-" * 80)
    
    # Find events to publish
    events_to_publish, initial_failed_ids = _find_events_to_process(event_ids, events)
    failed_count = len(initial_failed_ids)
    
    # Publish events
    published_count, pub_failed_count, pub_failed_ids = _publish_events_batch(
        base_path, events_to_publish, events, events_data
    )
    failed_count += pub_failed_count
    failed_ids = initial_failed_ids + pub_failed_ids
    
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
    embedded. Uses KISS templating (Python .format()) from src/templates/.
    
    Output: static/index.html (~313KB single-file HTML)
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
    events_file = base_path / 'event-data' / 'events.json'
    pending_file = base_path / 'event-data' / 'pending_events.json'
    
    if events_file.exists():
        shutil.copy(events_file, str(events_file) + '.backup')
        
    if pending_file.exists():
        shutil.copy(pending_file, str(pending_file) + '.backup')
    
    # Copy example data
    example_events = base_path / 'event-data' / 'events_example.json'
    example_pending = base_path / 'event-data' / 'pending_events_example.json'
    
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
    
    events_file = base_path / 'event-data' / 'events.json'
    pending_file = base_path / 'event-data' / 'pending_events.json'
    
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
        print(f"  Archived events saved to: {base_path / 'event-data' / 'archived_events.json'}")
    else:
        print("✓ No past events to archive")
    
    return 0


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
    
    if command == 'review':
        app = EventManagerTUI()
        app.review_pending_events()
        return 0
    
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
