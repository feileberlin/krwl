================================================================================
                    KRWL HOF COMMUNITY EVENTS SYSTEM
                    Complete Documentation and Guide
================================================================================

TABLE OF CONTENTS
================================================================================

1. INTRODUCTION
   1.1 Overview
   1.2 Key Features
   1.3 System Requirements

2. PROJECT STRUCTURE
   2.1 Directory Layout
   2.2 File Descriptions

3. QUICK START GUIDE
   3.1 Installation
   3.2 Running the Python TUI
   3.3 Using CLI Mode
   3.4 Development Mode with Example Data
   3.5 Basic Workflow

4. PYTHON TUI REFERENCE
   4.1 Main Menu Options
   4.2 Scraping Events
   4.3 Reviewing Pending Events
   4.4 Viewing Published Events
   4.5 Generating Static Site
   4.6 Settings and Development Mode
   4.7 Documentation Viewer

5. CLI REFERENCE
   5.1 CLI Commands
   5.2 Command Examples
   5.3 Help and Version

5. CONFIGURATION
   5.1 config.json Structure
   5.2 Configuration Options
   5.3 Scraping Sources
   5.4 Filtering Options
   5.5 Map Configuration

6. DATA FORMATS
   6.1 Event Data Structure
   6.2 Published Events (events.json)
   6.3 Pending Events (pending_events.json)
   6.4 Example Data Files

7. WEB INTERFACE
   7.1 Features Overview
   7.2 Geolocation Filtering
   7.3 Sunrise Filtering
   7.4 Map Interface
   7.5 Event Display and Details

8. STATIC SITE GENERATION
   8.1 Generated Files
   8.2 HTML Structure
   8.3 CSS Styling
   8.4 JavaScript Application

9. DEPLOYMENT
   9.1 GitHub Pages Setup
   9.2 Deployment Options
   9.3 Custom Domain Setup

10. EXTENDING THE SYSTEM
    10.1 Adding New Scraping Sources
    10.2 Customizing the Interface
    10.3 Adding TUI Features
    10.4 Module Development

11. DEVELOPMENT AND DEBUGGING
    11.1 Code Structure
    11.2 Development Mode
    11.3 Example Data Usage
    11.4 Testing Workflow

12. TROUBLESHOOTING
    12.1 Common Issues
    12.2 Location Problems
    12.3 Data Issues
    12.4 Build Problems

13. TECHNICAL REFERENCE
    13.1 Python Modules
    13.2 JavaScript API
    13.3 Distance Calculation
    13.4 Time Filtering

14. ROADMAP AND FUTURE FEATURES

15. LICENSE AND CREDITS


================================================================================
1. INTRODUCTION
================================================================================

1.1 OVERVIEW
------------
KRWL HOF Community Events is a complete system for scraping, curating, and
displaying community events on an interactive map. It features:

- A Python-based Terminal User Interface (TUI) for event management
- Automatic filtering by geolocation (shows nearby events only)
- Time-based filtering (shows events until next sunrise only)
- Static site generation for GitHub Pages deployment
- JSON-based configuration and data storage
- Vanilla JavaScript frontend with no framework dependencies


1.2 KEY FEATURES
----------------
    ┌─────────────────────────────────────────────────────────────┐
    │                    SYSTEM OVERVIEW                          │
    └─────────────────────────────────────────────────────────────┘

    Web Sources        Python TUI         Static Site
    ┌─────────┐       ┌──────────┐       ┌──────────┐
    │  RSS    │──────►│          │       │          │
    │  API    │──────►│  Scrape  │──────►│  Review  │
    │  HTML   │──────►│          │       │  & Edit  │
    └─────────┘       └──────────┘       └────┬─────┘
                                              │
                                              ▼
                                         ┌─────────┐
                                         │ Publish │
                                         └────┬────┘
                                              │
                                              ▼
                                      ┌───────────────┐
                                      │   Generate    │
                                      │  Static Site  │
                                      └───────┬───────┘
                                              │
                                              ▼
    User's Browser    ◄───────────────  GitHub Pages
    ┌────────────┐                     ┌─────────────┐
    │  🗺️ Map    │                     │ index.html  │
    │  📍 Filter │                     │ app.js      │
    │  🌅 Time   │                     │ events.json │
    └────────────┘                     └─────────────┘

Features:
🔍 Event Scraping: Scrape events from RSS feeds, APIs, and HTML pages
✅ Editor Workflow: Review, edit, approve, or reject events before publishing
🗺️ Interactive Map: Fullscreen map interface with Leaflet.js
📍 Geolocation Filtering: Shows only events near the user's location
🌅 Sunrise Filtering: Displays events only until the next sunrise
📝 JSON-based: Plain JSON for configuration and data storage
🐍 Python TUI: Single modular Python terminal interface
🌐 Static Site: Generates static files for GitHub Pages deployment
🚀 No Jekyll: Includes .nojekyll for direct GitHub Pages hosting
🛠️ Development Mode: Includes example data for testing and debugging


1.3 SYSTEM REQUIREMENTS
-----------------------
- Python 3.7 or higher
- Modern web browser with JavaScript enabled
- Internet connection for map tiles
- Geolocation support (HTTPS or localhost for web interface)

Optional dependencies (for enhanced scraping):
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)
- feedparser (RSS feed parsing)
- astral (accurate sunrise/sunset calculations)


================================================================================
2. PROJECT STRUCTURE
================================================================================

2.1 DIRECTORY LAYOUT
--------------------
                     krwl-hof/
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    [Config]         [Source]         [Output]
        │                │                │
        ▼                ▼                ▼
    
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ config/ │     │  src/   │     │ static/ │
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         │               ├─ main.py      ├─ index.html
         │               │               ├─ events.json
         │               └─ modules/     ├─ config.json
         │                    │          ├─ css/
         │                    ├─ scraper.py     │
         │                    ├─ editor.py      └─ style.css
         │                    ├─ generator.py   
         │                    └─ utils.py  └─ js/
         │                                      │
         └─ config.json                         └─ app.js

    ┌─────────┐
    │  data/  │  ← Storage
    └────┬────┘
         │
         ├─ events.json              (Published)
         ├─ pending_events.json      (Under Review)
         ├─ events_example.json      (Sample Data)
         └─ pending_events_example.json

    ┌──────────────┐
    │ Root Files   │
    └──────────────┘
         │
         ├─ .nojekyll          (GitHub Pages config)
         ├─ .gitignore         (Git ignore rules)
         ├─ README.txt         (This file)
         └─ requirements.txt   (Python deps)

Data Flow:
    Web Sources → [Scraper] → pending_events.json
    pending_events.json → [Editor] → events.json
    events.json → [Generator] → static/


2.2 FILE DESCRIPTIONS
---------------------
.nojekyll
    Empty file that tells GitHub Pages not to process files with Jekyll.
    This allows direct serving of static files.

config/config.json
    Main configuration file containing app settings, scraping sources,
    filtering options, and map configuration.

data/events.json
    Published events that are approved and displayed on the website.

data/pending_events.json
    Events that have been scraped but await editor review and approval.

data/events_example.json
    Sample published events for development and testing.

data/pending_events_example.json
    Sample pending events for development and testing.

src/main.py
    Main entry point for the Python TUI application. Provides menu system
    and orchestrates all modules.

src/modules/scraper.py
    Handles event scraping from various sources (RSS, API, HTML).

src/modules/editor.py
    Provides event review and approval workflow.

src/modules/generator.py
    Generates static HTML, CSS, and JavaScript files.

src/modules/utils.py
    Shared utility functions for file I/O, distance calculation, etc.

static/
    Directory containing generated static website files ready for deployment.


================================================================================
3. QUICK START GUIDE
================================================================================

3.1 INSTALLATION
----------------
1. Clone the repository:
   $ git clone https://github.com/feileberlin/krwl-hof.git
   $ cd krwl-hof

2. (Optional) Create a virtual environment:
   $ python3 -m venv venv
   $ source venv/bin/activate    # On Windows: venv\Scripts\activate

3. (Optional) Install dependencies for enhanced scraping:
   $ pip install -r requirements.txt


3.2 RUNNING THE PYTHON TUI
---------------------------
$ cd src
$ python3 main.py

The TUI will display a menu with the following options:
1. Scrape New Events
2. Review Pending Events
3. View Published Events
4. Generate Static Site
5. Settings
6. View Documentation
7. Exit


3.3 USING CLI MODE
------------------
The script can also be used as a command-line tool for scripting and automation:

# Display help
$ python3 main.py --help

# List all published events
$ python3 main.py list

# List pending events
$ python3 main.py list-pending

# Scrape new events
$ python3 main.py scrape

# Generate static site
$ python3 main.py generate

# Load example data
$ python3 main.py load-examples

# Publish a specific event by ID
$ python3 main.py publish pending_1

# Reject a specific event by ID
$ python3 main.py reject pending_2

# Show version
$ python3 main.py --version

See section 5 (CLI REFERENCE) for complete documentation.


3.4 DEVELOPMENT MODE WITH EXAMPLE DATA
--------------------------------------
For testing and development, you can load pre-made example data:

1. Run the Python TUI:
   $ cd src
   $ python3 main.py

2. Select option 5 (Settings)

3. Select option 2 (Load Example Data)

4. Confirm by typing "yes"

This will:
- Back up your existing data with .backup extension
- Load 5 example published events
- Load 2 example pending events
- Allow you to test the full system immediately

Example events include:
- Community Garden Meetup (evening event)
- Open Mic Night at Berlin Cafe (evening event)
- Neighborhood Book Club (evening event)
- Morning Yoga in the Park (morning event)
- Tech Skills Workshop (afternoon event)

Example pending events include:
- Street Food Market
- Bike Repair Workshop


3.5 BASIC WORKFLOW
------------------
                                    
    ┌─────────────────┐
    │  Load Example   │  Step 1: Load sample data
    │      Data       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ View Published  │  Step 2: Check what's live
    │     Events      │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Review Pending  │  Step 3: Curate new events
    │     Events      │
    └────────┬────────┘
             │
        ┌────┴────┐
        ▼         ▼
    [Approve] [Reject]  Step 4: Editorial decision
        │
        ▼
    ┌─────────────────┐
    │ Generate Static │  Step 5: Build website
    │      Site       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  View Website   │  Step 6: Test result
    │  in Browser     │
    └─────────────────┘


================================================================================
4. PYTHON TUI REFERENCE
================================================================================

4.1 MAIN MENU OPTIONS
---------------------
The TUI provides six main options:

1. Scrape New Events
   Fetch events from configured scraping sources and add them to the
   pending queue for review.

2. Review Pending Events
   Review each pending event individually with options to approve,
   edit, reject, or skip.

3. View Published Events
   Display all approved and published events.

4. Generate Static Site
   Create static HTML, CSS, and JavaScript files in the static/ directory
   ready for deployment to GitHub Pages.

5. Settings
   View configuration and access development mode features.

6. Exit
   Close the application.


4.2 SCRAPING EVENTS
-------------------
This option scrapes events from all enabled sources defined in config.json.

The scraper supports three types of sources:
- RSS feeds (type: "rss")
- JSON APIs (type: "api")
- HTML pages (type: "html")

Scraped events are added to pending_events.json and await review.

Note: The base implementation includes placeholder scraping logic.
For production use, implement the actual scraping logic in
src/modules/scraper.py based on your event sources.


4.3 REVIEWING PENDING EVENTS
----------------------------
The review interface shows each pending event one at a time with details:
- Title
- Description
- Location name and coordinates
- Start and end times
- Source URL
- Source type

Editorial Workflow:

    ┌──────────────┐
    │   Scraped    │
    │    Event     │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Pending    │
    │    Queue     │
    └──────┬───────┘
           │
    ┌──────┴──────┬──────────┬─────────┐
    │             │          │         │
    ▼             ▼          ▼         ▼
 [Approve]     [Edit]    [Reject]  [Skip]
    │             │          │         │
    ▼             ▼          ▼         │
┌────────┐   ┌────────┐  ┌──────┐     │
│Published│   │Modified│  │Trash │     │
│ Events │◄──┤  Event │  └──────┘     │
└────────┘   └────────┘                │
                                       │
                ┌──────────────────────┘
                │
                ▼
           [Next Event]

All changes are saved immediately.


4.4 VIEWING PUBLISHED EVENTS
----------------------------
Displays a list of all published events with:
- Title
- Location name
- Date and time
- Status

This is a read-only view for verification purposes.


4.5 GENERATING STATIC SITE
---------------------------
This option generates all files needed for the website:

1. static/index.html - Main page with map and event list
2. static/css/style.css - Styling and layout
3. static/js/app.js - JavaScript application logic
4. static/events.json - Copy of published events
5. static/config.json - Copy of configuration

The generated site is a complete single-page application that works
with no server-side processing.


4.6 SETTINGS AND DEVELOPMENT MODE
---------------------------------
The Settings menu provides:

1. View Configuration
   Display current config.json settings.

2. Load Example Data (Development Mode)
   Load pre-made example events for testing.
   - Backs up existing data automatically
   - Loads events_example.json → events.json
   - Loads pending_events_example.json → pending_events.json

3. Clear All Data
   Delete all events and pending events.
   - Requires typing "DELETE" to confirm
   - Backs up data before clearing

4. Back to Main Menu
   Return to main menu.


4.7 DOCUMENTATION VIEWER
------------------------
Access comprehensive documentation from within the TUI:

Main Menu → View Documentation (option 6)

The documentation viewer provides:

1. View Table of Contents
   Browse all documentation sections

2. Search Documentation
   Search for specific terms across the entire README
   - Shows line numbers and context
   - Displays up to 20 matches

3. View Full Documentation
   Read the complete documentation with pagination
   - Use 'n' for next page
   - Use 'p' for previous page
   - Use 'q' to quit viewer

4. Quick Start Guide
   View just the Quick Start section for rapid onboarding

5. Back to Main Menu
   Return to the main TUI menu

The documentation viewer allows editors to access help without leaving the
TUI, making it easy to reference configuration options, workflows, and
troubleshooting guides during event management tasks.


================================================================================
5. CLI REFERENCE
================================================================================

5.1 CLI COMMANDS
----------------
The main.py script supports both interactive TUI mode and command-line mode:

Interactive Mode (Default):
    $ python3 main.py
    Launches the full interactive TUI

Command-Line Mode:
    $ python3 main.py COMMAND [ARGS] [OPTIONS]
    Execute specific commands without entering the TUI

Available Commands:

scrape
    Scrape events from all configured sources
    Example: $ python3 main.py scrape

list
    List all published events
    Example: $ python3 main.py list

list-pending
    List all pending events awaiting review
    Example: $ python3 main.py list-pending

publish EVENT_ID
    Approve and publish a specific pending event
    Example: $ python3 main.py publish pending_1

reject EVENT_ID
    Reject and delete a specific pending event
    Example: $ python3 main.py reject pending_2

review
    Launch interactive review mode for pending events
    Example: $ python3 main.py review

generate
    Generate static site files for deployment
    Example: $ python3 main.py generate

load-examples
    Load example data for testing/development
    Example: $ python3 main.py load-examples

clear-data
    Clear all event data (requires confirmation)
    Example: $ python3 main.py clear-data


5.2 COMMAND EXAMPLES
--------------------
Basic Workflow via CLI:

    # 1. Load example data
    $ python3 main.py load-examples
    
    # 2. List events
    $ python3 main.py list
    
    # 3. Check pending events
    $ python3 main.py list-pending
    
    # 4. Publish a pending event
    $ python3 main.py publish pending_1
    
    # 5. Generate the static site
    $ python3 main.py generate

Automation Scripts:

    # Daily scraping cron job
    0 8 * * * cd /path/to/krwl-hof/src && python3 main.py scrape
    
    # Auto-generate site after changes
    $ python3 main.py scrape && python3 main.py generate
    
    # Batch processing
    for event_id in pending_1 pending_2 pending_3; do
        python3 main.py publish $event_id
    done


5.3 HELP AND VERSION
--------------------
Get Help:
    $ python3 main.py --help
    $ python3 main.py -h
    
    Displays complete usage information, all commands, options,
    and examples.

Check Version:
    $ python3 main.py --version
    $ python3 main.py -v
    
    Shows the application version number.

Invalid Commands:
    $ python3 main.py invalid-command
    
    Error: Unknown command 'invalid-command'
    Use --help to see available commands
    
    The script provides helpful error messages and suggests using
    --help for correct syntax.


================================================================================
6. CONFIGURATION
================================================================================

5.1 config.json STRUCTURE
-------------------------
The configuration file is located at config/config.json and contains
four main sections:
- app: Application metadata
- scraping: Event scraping configuration
- filtering: Event filtering rules
- map: Map display settings
- editor: Editorial workflow settings


5.2 CONFIGURATION OPTIONS
--------------------------
{
  "app": {
    "name": "KRWL HOF Community Events",
    "description": "Community events scraper and viewer"
  },

  "scraping": {
    "sources": [...],
    "interval_minutes": 60
  },

  "filtering": {
    "max_distance_km": 5.0,
    "show_until": "next_sunrise"
  },

  "map": {
    "default_center": {
      "lat": 52.52,
      "lon": 13.405
    },
    "default_zoom": 13,
    "tile_provider": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "attribution": "..."
  },

  "editor": {
    "require_approval": true,
    "auto_publish": false
  }
}


5.3 SCRAPING SOURCES
--------------------
Each source in the scraping.sources array can have:

{
  "name": "source_name",          # Identifier for the source
  "url": "https://...",           # URL to scrape
  "type": "rss"|"api"|"html",    # Source type
  "enabled": true|false           # Whether to scrape this source
}

Example RSS source:
{
  "name": "community_rss",
  "url": "https://example.com/events.rss",
  "type": "rss",
  "enabled": true
}


5.4 FILTERING OPTIONS
---------------------
max_distance_km (float)
    Maximum distance in kilometers from user location.
    Events beyond this distance are filtered out.
    Default: 5.0

show_until (string)
    Time filtering mode. Currently only "next_sunrise" is supported.
    Shows events that occur before the next sunrise (approximately 6 AM).


5.5 MAP CONFIGURATION
---------------------
default_center (object)
    Initial map center coordinates.
    lat: Latitude (e.g., 52.52 for Berlin)
    lon: Longitude (e.g., 13.405 for Berlin)

default_zoom (integer)
    Initial zoom level (1-20, higher = more zoomed in)
    Default: 13

tile_provider (string)
    URL template for map tiles. Default uses OpenStreetMap.

attribution (string)
    Attribution text for map tiles (required by most tile providers).


================================================================================
6. DATA FORMATS
================================================================================

6.1 EVENT DATA STRUCTURE
-------------------------
Each event is a JSON object with the following fields:

{
  "id": "unique_identifier",        # Required: Unique event ID
  "title": "Event Title",           # Required: Event name
  "description": "Description...",  # Optional: Event details
  "location": {                     # Required: Event location
    "name": "Venue Name",           # Location display name
    "lat": 52.52,                   # Latitude
    "lon": 13.405                   # Longitude
  },
  "start_time": "2025-12-08T18:00:00",  # Required: ISO 8601 format
  "end_time": "2025-12-08T20:00:00",    # Optional: ISO 8601 format
  "url": "https://...",             # Optional: More info URL
  "source": "manual",               # Required: Source identifier
  "status": "published",            # Required: "pending" or "published"
  "scraped_at": "2025-12-08T10:00:00",  # Optional: Scrape timestamp
  "published_at": "2025-12-08T12:00:00" # Optional: Publish timestamp
}


6.2 PUBLISHED EVENTS (events.json)
----------------------------------
Structure:
{
  "events": [
    {...},  # Array of event objects
    {...}
  ],
  "last_updated": "2025-12-08T12:00:00"  # ISO 8601 timestamp
}

All events in this file have status: "published" and are displayed
on the website.


6.3 PENDING EVENTS (pending_events.json)
----------------------------------------
Structure:
{
  "pending_events": [
    {...},  # Array of event objects
    {...}
  ],
  "last_scraped": "2025-12-08T10:30:00"  # ISO 8601 timestamp
}

All events in this file have status: "pending" and await review
in the TUI.


6.4 EXAMPLE DATA FILES
----------------------
events_example.json
    Contains 5 sample published events demonstrating various event types:
    - Evening community events
    - Morning activities
    - Afternoon workshops
    - Different locations around Berlin

pending_events_example.json
    Contains 2 sample pending events demonstrating:
    - Different source types (RSS, API)
    - Events awaiting review

These files can be loaded via Settings → Load Example Data in the TUI.


================================================================================
7. WEB INTERFACE
================================================================================

7.1 FEATURES OVERVIEW
---------------------
The web interface is a single-page application that provides:
- Full-screen interactive Leaflet.js map
- Automatic geolocation detection
- Real-time distance calculation
- Event list sidebar
- Event detail modal
- Responsive design for mobile devices
- Dark theme interface


7.2 GEOLOCATION FILTERING
--------------------------
Geolocation Flow:

    ┌──────────────┐
    │  User Visits │
    │     Page     │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────┐
    │ Request Geolocation  │
    └──────┬───────────────┘
           │
      ┌────┴────┐
      │         │
    [OK]     [Denied]
      │         │
      ▼         ▼
   ┌──────┐  ┌────────────────┐
   │ Got  │  │ Show All Events│
   │ Lat/ │  │ (No Distance)  │
   │ Lon  │  └────────────────┘
   └──┬───┘
      │
      ▼
   ┌─────────────────────┐
   │ Calculate Distance  │
   │  to All Events      │
   │ (Haversine Formula) │
   └──────┬──────────────┘
          │
          ▼
   ┌─────────────────────┐    ┌─────────────┐
   │  Event Distance?    ├───►│   > 5 km    │──► [Filter Out]
   └──────┬──────────────┘    └─────────────┘
          │
          ▼
   ┌─────────────┐
   │   < 5 km    │──► [Show Event]
   └─────────────┘
          │
          ▼
   ┌─────────────────┐
   │  Sort by        │
   │  Distance       │
   │  (Nearest First)│
   └─────────────────┘


7.3 SUNRISE FILTERING
---------------------
Events are filtered to show only those occurring before the next sunrise:

Timeline Visualization:

    Current Time: 3 AM              Current Time: 10 AM
    ─────────────────────           ─────────────────────
    
    12 AM ├────────                 12 AM ├────────
     1 AM │                          1 AM │
     2 AM │  ← You are here          2 AM │
     3 AM ●                          3 AM │
     4 AM │                          4 AM │
     5 AM │ Show events             5 AM │
     6 AM ├─ ☀ Next Sunrise         6 AM ├─ ☀ Already passed
     7 AM │                          7 AM │
     8 AM │ (Hide events)            8 AM │
     9 AM │                          9 AM │
    10 AM │                         10 AM ●  ← You are here
    11 AM │                         11 AM │
    12 PM ├────────                 12 PM │ Show events
     ...                             ...  │
                                     6 AM ├─ ☀ Next Sunrise (tomorrow)

    Shows: Midnight to 6 AM         Shows: 10 AM to 6 AM (next day)
    
Logic:
    IF current_time < 6:00 AM
        SHOW events WHERE start_time < 6:00 AM TODAY
    ELSE
        SHOW events WHERE start_time < 6:00 AM TOMORROW

Note: Current implementation uses simplified 6 AM sunrise time.
For production, integrate the astral library for accurate sunrise
times based on user location.


7.4 MAP INTERFACE
-----------------
Map Layout:

    ┌─────────────────────────────────────────────────────┐
    │  KRWL HOF Community Events        📍 5 events nearby│
    ├─────────────────────────────────────────────────────┤
    │                                    ╔════════════════╗│
    │         ┌─┐ [+]                    ║ Upcoming Events║│
    │         └─┘ [-]                    ╠════════════════╣│
    │                                    ║ ┌────────────┐ ║│
    │    ●  ← Event #1 (green)          ║ │🎭 Concert  │ ║│
    │         (2.3 km away)              ║ │📍 Theater  │ ║│
    │                                    ║ │📏 2.3 km   │ ║│
    │             ●  ← You (blue)        ║ └────────────┘ ║│
    │                                    ║                ║│
    │  ●  ← Event #2                     ║ ┌────────────┐ ║│
    │       (3.1 km)                     ║ │🍔 Food Mkt │ ║│
    │                                    ║ │📍 Square   │ ║│
    │        ● ← Event #3                ║ │📏 3.1 km   │ ║│
    │           (4.5 km)                 ║ └────────────┘ ║│
    │                                    ║                ║│
    │  [OpenStreetMap tiles]             ║ ┌────────────┐ ║│
    │                                    ║ │🚴 Workshop │ ║│
    │                                    ║ │📍 Hub      │ ║│
    │                                    ║ │📏 4.5 km   │ ║│
    │                                    ║ └────────────┘ ║│
    └────────────────────────────────────╚════════════════╝│

Map controls:
- Zoom in/out buttons [+] [-]
- Pan by dragging
- Double-click to zoom
- Scroll wheel zoom (on desktop)
- Click marker/card for details


7.5 EVENT DISPLAY AND DETAILS
-----------------------------
Event List Sidebar:
- Shows filtered events sorted by distance
- Each card displays:
  * Event title
  * Location name
  * Date and time
  * Distance (if geolocation available)
- Click any card to view full details

Event Detail Modal:
- Full event information
- Location details
- Distance information
- Link to event URL (if available)
- Close button to return to list


================================================================================
8. STATIC SITE GENERATION
================================================================================

8.1 GENERATED FILES
-------------------
Static Site Generation Process:

    ┌──────────────┐
    │  Python TUI  │
    │ "Generate    │
    │  Static"     │
    └──────┬───────┘
           │
           ├────────────────────────────────────┐
           │                                    │
           ▼                                    ▼
    ┌─────────────┐                    ┌──────────────┐
    │ Templates   │                    │  Data Files  │
    │  (Python)   │                    │   (JSON)     │
    └──────┬──────┘                    └──────┬───────┘
           │                                   │
           ├─► index.html                      ├─► events.json
           ├─► style.css                       └─► config.json
           └─► app.js                          
           │
           ▼
    ┌─────────────────────────────────────────┐
    │          static/ Directory              │
    ├─────────────────────────────────────────┤
    │  index.html       ← Main page           │
    │  events.json      ← Event data          │
    │  config.json      ← Configuration       │
    │  css/                                   │
    │    └─ style.css   ← Styling             │
    │  js/                                    │
    │    └─ app.js      ← Application logic   │
    └─────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────┐
    │  GitHub Pages   │
    │  Deployment     │
    └─────────────────┘

External Dependencies (CDN):
    - Leaflet.js (loaded from unpkg.com)
    - OpenStreetMap tiles (loaded from OSM servers)


8.2 HTML STRUCTURE
------------------
The HTML is structured as:

<body>
  <div id="app">
    <header>                    # Top bar with title and status
    <div id="map">             # Full-screen map container
    <div id="event-list">      # Sidebar with event cards
    <div id="event-detail">    # Modal for event details
  </div>
</body>

The page uses semantic HTML5 elements and includes:
- Proper meta tags for viewport and charset
- Leaflet.js CSS and JavaScript from CDN
- Custom CSS and JavaScript files


8.3 CSS STYLING
---------------
The stylesheet provides:
- Modern dark theme (#1a1a1a background)
- Responsive flexbox layout
- Smooth transitions and hover effects
- Custom scrollbars (WebKit browsers)
- Mobile-responsive media queries
- Glassmorphism effects (blur, transparency)

Key design elements:
- Green accent color (#4CAF50) for events
- Blue color (#2196F3) for user location
- Dark gray backgrounds with transparency
- White text with varying opacity for hierarchy


8.4 JAVASCRIPT APPLICATION
---------------------------
The app.js file contains the EventsApp class with methods:

init()                    Initialize application
loadConfig()             Load configuration
initMap()                Initialize Leaflet map
getUserLocation()        Get user's geolocation
loadEvents()             Load events from JSON
calculateDistance()      Haversine distance formula
getNextSunrise()         Calculate next sunrise time
filterEvents()           Apply distance and time filters
displayEvents()          Render event cards and markers
showEventDetail()        Display event detail modal

The application is vanilla JavaScript (ES6) with no frameworks.


================================================================================
9. DEPLOYMENT
================================================================================

9.1 GITHUB PAGES SETUP
----------------------
Method 1: Deploy from static/ directory

1. Push your repository to GitHub
2. Go to repository Settings → Pages
3. Set Source to "Deploy from a branch"
4. Select branch: main (or your branch)
5. Select folder: /static
6. Click Save

Your site will be available at:
https://yourusername.github.io/repository-name/


Method 2: Deploy from root

1. Copy static files to root:
   $ cp static/index.html .
   $ cp static/events.json .
   $ cp static/config.json .
   $ cp -r static/css .
   $ cp -r static/js .

2. Commit and push changes

3. Go to repository Settings → Pages

4. Set Source to "Deploy from a branch"

5. Select branch: main

6. Select folder: / (root)

7. Click Save

Your site will be available at:
https://yourusername.github.io/repository-name/


9.2 DEPLOYMENT OPTIONS
----------------------
The .nojekyll file is already included, which tells GitHub Pages:
- Do not process files with Jekyll
- Serve files directly as-is
- No need for Jekyll build step

For custom domains:
1. Add CNAME file with your domain
2. Configure DNS records at your domain provider
3. Update repository settings in GitHub


9.3 CUSTOM DOMAIN SETUP
-----------------------
1. Create a CNAME file in the repository root:
   $ echo "events.yourdomain.com" > CNAME

2. Configure DNS at your domain provider:
   - Add CNAME record pointing to yourusername.github.io
   - Or add A records pointing to GitHub Pages IPs

3. In GitHub repository Settings → Pages:
   - Enter your custom domain
   - Enable "Enforce HTTPS" (recommended)

4. Wait for DNS propagation (up to 24 hours)


================================================================================
10. EXTENDING THE SYSTEM
================================================================================

10.1 ADDING NEW SCRAPING SOURCES
--------------------------------
Scraping Pipeline:

    ┌────────────────┐
    │  Event Source  │
    │   (Website)    │
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐     ┌─────────────────────┐
    │  Source Type?  ├────►│ RSS Feed            │
    └────────┬───────┘     │ • feedparser        │
             │             └─────────────────────┘
             │
             ├────────────►┌─────────────────────┐
             │             │ JSON API            │
             │             │ • requests + json   │
             │             └─────────────────────┘
             │
             └────────────►┌─────────────────────┐
                           │ HTML Page           │
                           │ • requests + BS4    │
                           └─────────────────────┘
                                     │
                                     ▼
                           ┌─────────────────────┐
                           │  Parse & Extract    │
                           │  • Title            │
                           │  • Description      │
                           │  • Location         │
                           │  • Date/Time        │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  Create Event       │
                           │  Object (JSON)      │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │   Pending Queue     │
                           │ (pending_events.json│
                           └─────────────────────┘

Steps to Add Source:

1. Edit config/config.json:
   {
     "name": "new_source",
     "url": "https://example.com/events",
     "type": "rss",  # or "api" or "html"
     "enabled": true
   }

2. Edit src/modules/scraper.py:
   - Implement logic in _scrape_rss(), _scrape_api(), or _scrape_html()
   - Parse source data and create event objects
   - Return list of event dictionaries

3. Install required libraries (if needed):
   $ pip install requests beautifulsoup4 feedparser

4. Test scraping:
   - Run TUI and select "Scrape New Events"
   - Check pending_events.json for scraped events


10.2 CUSTOMIZING THE INTERFACE
------------------------------
HTML Customization:
Edit src/modules/generator.py → _generate_html() method
- Modify structure in html_content variable
- Add new sections or elements
- Change text and labels

CSS Customization:
Edit src/modules/generator.py → _generate_css() method
- Modify styles in css_content variable
- Change colors, fonts, layouts
- Add new CSS rules

JavaScript Customization:
Edit src/modules/generator.py → _generate_js() method
- Modify EventsApp class methods
- Add new features or behaviors
- Change filtering logic

After making changes:
1. Run TUI and select "Generate Static Site"
2. Test changes by opening static/index.html in browser


10.3 ADDING TUI FEATURES
------------------------
To add a new menu option:

1. Edit src/main.py → show_menu():
   Add new menu item:
   print("7. My New Feature")

2. Add handler method:
   def my_new_feature(self):
       self.clear_screen()
       self.print_header()
       # Your implementation
       input("\nPress Enter to continue...")

3. Edit src/main.py → run():
   Add case for new option:
   elif choice == '7':
       self.my_new_feature()

4. Test the new feature:
   $ cd src
   $ python3 main.py


10.4 MODULE DEVELOPMENT
-----------------------
To add a new module:

1. Create new file in src/modules/:
   $ touch src/modules/mymodule.py

2. Implement your module:
   class MyModule:
       def __init__(self, config, base_path):
           self.config = config
           self.base_path = base_path
       
       def my_function(self):
           # Implementation
           pass

3. Export from src/modules/__init__.py:
   from .mymodule import MyModule
   
   __all__ = [
       'MyModule',
       # ... other exports
   ]

4. Use in main.py:
   from modules.mymodule import MyModule
   
   module = MyModule(self.config, self.base_path)
   module.my_function()


================================================================================
11. DEVELOPMENT AND DEBUGGING
================================================================================

11.1 CODE STRUCTURE
-------------------
The codebase follows these principles:
- Modular design: Each module has a single responsibility
- JSON-based: All data in plain JSON files
- No database: Filesystem-based storage
- Expandable: Easy to add new modules and features
- Minimal dependencies: Uses Python standard library where possible


11.2 DEVELOPMENT MODE
---------------------
The development mode provides:
- Pre-made example data
- Quick testing without scraping
- Sample events of various types
- Backup of existing data

To use development mode:
1. Run TUI: python3 main.py
2. Select Settings (option 5)
3. Select Load Example Data (option 2)
4. Confirm with "yes"

This loads:
- 5 published events from events_example.json
- 2 pending events from pending_events_example.json

Your original data is backed up as:
- data/events.json.backup
- data/pending_events.json.backup


11.3 EXAMPLE DATA USAGE
-----------------------
The example data demonstrates:

Published Events:
1. Community Garden Meetup (evening, nearby)
2. Open Mic Night (evening, nearby)
3. Neighborhood Book Club (evening, nearby)
4. Morning Yoga (morning, filters out after 6 AM)
5. Tech Workshop (afternoon, nearby)

Pending Events:
1. Street Food Market (needs review)
2. Bike Repair Workshop (needs review)

Test scenarios:
- View events on map with different locations
- Test distance filtering by changing coordinates
- Test time filtering by checking times before/after 6 AM
- Practice review workflow with pending events
- Test static site generation with real-looking data


11.4 TESTING WORKFLOW
---------------------
Complete testing sequence:

1. Load example data:
   TUI → Settings → Load Example Data

2. View published events:
   TUI → View Published Events
   Verify 5 events are loaded

3. Review pending events:
   TUI → Review Pending Events
   Approve one, reject one

4. Generate static site:
   TUI → Generate Static Site
   Verify files created in static/

5. Test web interface:
   Open static/index.html in browser
   Check map loads
   Check events display
   Click event markers and cards
   Test detail modal

6. Test filtering:
   Allow geolocation access
   Verify distance calculations
   Check event count updates

7. Clear data (optional):
   TUI → Settings → Clear All Data
   Type "DELETE" to confirm


================================================================================
12. TROUBLESHOOTING
================================================================================

12.1 COMMON ISSUES
------------------
Problem: TUI not starting
Solution: 
- Check Python version: python3 --version (need 3.7+)
- Check you're in src/ directory: cd src
- Check file permissions: chmod +x main.py

Problem: Module import errors
Solution:
- Verify src/modules/__init__.py exists
- Check all module files are present
- Ensure you're running from src/ directory

Problem: JSON decode errors
Solution:
- Validate JSON files at https://jsonlint.com
- Check for missing commas or quotes
- Restore from .backup files if corrupted


12.2 LOCATION PROBLEMS
----------------------
Problem: "Location unavailable" in browser
Solution:
- Enable location services in browser settings
- Use HTTPS (GitHub Pages provides this)
- Or test on localhost
- Check browser supports geolocation API

Problem: Distance calculation wrong
Solution:
- Verify event coordinates are correct (lat/lon)
- Check coordinates are in decimal degrees
- Latitude: -90 to 90
- Longitude: -180 to 180

Problem: User marker not showing
Solution:
- Check console for JavaScript errors
- Verify geolocation permission granted
- Check map is initialized before adding marker


12.3 DATA ISSUES
----------------
Problem: No events showing
Solution:
- Check events.json has events
- Verify events are before next sunrise
- Check max_distance_km setting
- Load example data for testing

Problem: Events not filtering by distance
Solution:
- Verify geolocation is enabled
- Check event coordinates are valid
- Verify max_distance_km in config.json
- Check console for calculation errors

Problem: Can't save events
Solution:
- Check file permissions in data/ directory
- Verify JSON syntax is valid
- Check disk space available


12.4 BUILD PROBLEMS
-------------------
Problem: Static site not generating
Solution:
- Check write permissions in static/ directory
- Verify modules imported correctly
- Check for Python errors in terminal
- Run: python3 main.py and test option 4

Problem: CSS/JS not loading
Solution:
- Check files exist in static/css/ and static/js/
- Verify file paths in index.html
- Check browser console for 404 errors
- Regenerate site from TUI

Problem: Map not displaying
Solution:
- Check internet connection (map tiles from OSM)
- Verify Leaflet.js CDN is accessible
- Check browser console for errors
- Try different browser


================================================================================
13. TECHNICAL REFERENCE
================================================================================

13.1 PYTHON MODULES
-------------------
modules/utils.py:

  load_config(base_path) → dict
    Load configuration from config.json

  load_events(base_path) → dict
    Load published events from events.json

  save_events(base_path, events_data) → None
    Save published events with timestamp

  load_pending_events(base_path) → dict
    Load pending events from pending_events.json

  save_pending_events(base_path, pending_data) → None
    Save pending events with timestamp

  calculate_distance(lat1, lon1, lat2, lon2) → float
    Calculate distance in km using Haversine formula

  get_next_sunrise(lat, lon) → datetime
    Calculate next sunrise time for coordinates


modules/scraper.py:

  EventScraper(config, base_path)
    Initialize scraper with config and base path

  scrape_all_sources() → list
    Scrape all enabled sources, return new events

  scrape_source(source) → list
    Scrape single source based on type

  create_manual_event(...) → dict
    Create event manually with provided details


modules/editor.py:

  EventEditor(base_path)
    Initialize editor with base path

  review_pending() → None
    Interactive review of all pending events

  _approve_event(event) → None
    Approve event and move to published

  _edit_event(event) → None
    Interactive editing of event fields


modules/generator.py:

  StaticSiteGenerator(config, base_path)
    Initialize generator with config and base path

  generate_all() → None
    Generate all static files

  _generate_html() → None
    Generate index.html

  _generate_css() → None
    Generate style.css

  _generate_js() → None
    Generate app.js

  _copy_data_files() → None
    Copy events.json and config.json to static/


13.2 JAVASCRIPT API
-------------------
class EventsApp:

  constructor()
    Initialize application state

  async init()
    Main initialization sequence

  async loadConfig()
    Load configuration from config.json

  initMap()
    Initialize Leaflet map

  getUserLocation()
    Request and handle geolocation

  async loadEvents()
    Load events from events.json

  calculateDistance(lat1, lon1, lat2, lon2) → number
    Haversine formula for distance in km

  getNextSunrise() → Date
    Calculate next sunrise time

  filterEvents() → Array
    Apply distance and time filters

  displayEvents()
    Render event cards and markers

  displayEventCard(event, container)
    Create and append event card element

  addEventMarker(event)
    Add event marker to map

  showEventDetail(event)
    Display event detail modal


13.3 DISTANCE CALCULATION
--------------------------
Haversine Formula:
Used to calculate great-circle distance between two points on Earth.

Visual Representation:

           North Pole
               ★
              /|\
             / | \
            /  |  \
           /   |   \
          / R  |    \     R = Earth's radius
         /     |     \        (6371 km)
        /      |      \
       /       |       \
    Point A ●──────────● Point B
       \       |       /
        \      |      /
         \     |     /
          \    |    /
           \   |   /
            \  |  /
             \ | /
              \|/
               ●
         Earth's Center

    Great Circle Distance (d):
    The shortest path along Earth's surface

Formula:
  a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
  c = 2 × atan2(√a, √(1-a))
  d = R × c

Where:
  R = Earth's radius (6371 km)
  Δlat = lat2 - lat1 (in radians)
  Δlon = lon2 - lon1 (in radians)
  lat1, lon1 = first point coordinates
  lat2, lon2 = second point coordinates

Example:
  User:  52.52°N, 13.40°E (Berlin, Germany)
  Event: 52.51°N, 13.38°E
  
  Δlat = 52.51 - 52.52 = -0.01° = -0.000175 rad
  Δlon = 13.38 - 13.40 = -0.02° = -0.000349 rad
  
  Distance ≈ 1.8 km

Implemented in:
- Python: modules/utils.py → calculate_distance()
- JavaScript: js/app.js → calculateDistance()


13.4 TIME FILTERING
-------------------
Sunrise Filtering Logic:

Simplified implementation:
- Assumes sunrise at 6:00 AM local time
- If current time < 6:00 AM: show events until 6:00 AM today
- If current time >= 6:00 AM: show events until 6:00 AM tomorrow

For production use:
- Install astral library: pip install astral
- Calculate accurate sunrise based on coordinates and date
- Account for daylight saving time
- Handle polar regions (midnight sun, polar night)

Example with astral:
  from astral import LocationInfo
  from astral.sun import sun
  
  city = LocationInfo("Berlin", "Germany", "Europe/Berlin", 52.52, 13.405)
  s = sun(city.observer, date=datetime.now())
  sunrise = s['sunrise']


================================================================================
14. ROADMAP AND FUTURE FEATURES
================================================================================

Planned Features:
-----------------
☐ RSS feed scraping implementation
☐ API integration for event sources  
☐ HTML scraping with BeautifulSoup
☐ Accurate sunrise/sunset calculation using astral
☐ Database backend option (SQLite, PostgreSQL)
☐ Web-based editor interface
☐ Event categories and filtering
☐ User favorites and bookmarks
☐ Event notifications
☐ Export to calendar formats (iCal, Google Calendar)
☐ Event search functionality
☐ Social sharing features
☐ Event check-ins and attendance tracking
☐ Mobile app (React Native or Flutter)
☐ Multi-language support
☐ Accessibility improvements (WCAG compliance)
☐ Event recommendations based on user preferences
☐ Integration with popular event platforms
☐ Email notification system
☐ Event comments and ratings

Technical Improvements:
-----------------------
☐ Unit tests for Python modules
☐ Integration tests for full workflow
☐ JavaScript tests with Jest
☐ CI/CD pipeline setup
☐ Docker containerization
☐ Performance optimization
☐ Caching layer for faster loading
☐ Progressive Web App (PWA) features
☐ Offline support with service workers
☐ Automated scraping scheduler
☐ Error monitoring and logging
☐ Analytics integration


================================================================================
15. LICENSE AND CREDITS
================================================================================

LICENSE
-------
This project is open source and available under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


CREDITS
-------
This project uses the following open source technologies:

Map Tiles:
  OpenStreetMap (https://www.openstreetmap.org/)
  © OpenStreetMap contributors
  Licensed under Open Data Commons Open Database License (ODbL)

Map Library:
  Leaflet.js (https://leafletjs.com/)
  Copyright (c) 2010-2023, Volodymyr Agafonkin
  Copyright (c) 2010-2011, CloudMade
  Licensed under BSD 2-Clause License

Development:
  Built with vanilla JavaScript and Python
  No frameworks or build tools required
  Standards-compliant HTML5, CSS3, and ES6


CONTRIBUTING
------------
Contributions are welcome! Please feel free to:
- Submit bug reports and feature requests via GitHub Issues
- Fork the repository and submit Pull Requests
- Improve documentation
- Add new scraping sources
- Enhance the UI/UX
- Write tests
- Translate to other languages

Contribution Guidelines:
1. Follow existing code style
2. Write clear commit messages
3. Add tests for new features
4. Update documentation
5. Keep PRs focused and small


CONTACT
-------
Project: KRWL HOF Community Events
Repository: https://github.com/feileberlin/krwl-hof
Issues: https://github.com/feileberlin/krwl-hof/issues


================================================================================
END OF DOCUMENTATION
================================================================================

For the latest version of this documentation and updates, visit:
https://github.com/feileberlin/krwl-hof

Last updated: 2025-12-08
Version: 1.0.0


================================================================================
16. DEPLOYMENT WORKFLOWS (GitHub Actions)
================================================================================

16.1 OVERVIEW
-------------
The project uses a safe two-step deployment workflow:
- MAIN BRANCH = Production (fast, optimized, real data only)
- PREVIEW BRANCH = Testing environment (debug mode, demo+real data)

Benefits:
✓ Test changes safely before production
✓ Debug mode in preview with console logging  
✓ Demo events with current timestamps for testing
✓ Maximum performance in production
✓ Easy rollback if issues found


16.2 CONFIGURATION FILES
------------------------

Production Config (config.prod.json):
- Debug mode: OFF
- Performance: Maximum speed, caching enabled
- Data source: Real events only
- Used by: main branch
- Domain: Custom domain via CNAME

Development Config (config.dev.json):
- Debug mode: ON (console logging enabled)
- Performance: Caching disabled for testing
- Data source: Both real and demo events
- Used by: preview branch
- Domain: GitHub Pages /preview/ path (no CNAME)

Data Source Options (Development Mode Only):
1. "source": "real" - Load only real scraped events
2. "source": "demo" - Load only demo events with current timestamps
3. "source": "both" - Load both real and demo events (default for dev)


16.3 WORKFLOWS
--------------

A. Production Deploy (deploy-pages.yml)
   Triggers: Push to main, manual dispatch
   
   What it does:
   - Copies static/ → publish/
   - Uses config.prod.json (optimized, no debug)
   - Includes CNAME for custom domain
   - Deploys to GitHub Pages root
   
   Result: Fast production site at custom domain

B. Preview Deploy (deploy-preview.yml)
   Triggers: Push to preview, manual dispatch
   
   What it does:
   - Copies static/ → publish/preview/
   - Generates fresh demo events from real templates
   - Uses config.dev.json (debug enabled, real+demo data)
   - NO CNAME (avoids domain conflict)
   - Injects <base href="/preview/"> tag
   - Deploys to GitHub Pages /preview/ path
   
   Result: Debug-enabled preview at yourdomain.com/preview/

C. Promote Preview (promote-preview.yml)
   Triggers: Manual dispatch only
   
   What it does:
   - Creates PR from preview → main
   - Optional auto-merge (fails gracefully with branch protection)
   
   Usage: Actions → Promote Preview to Production → Run workflow


16.4 DEVELOPER WORKFLOW
-----------------------

1. Make changes on feature branch
2. Submit PR to preview branch
3. Merge to preview → auto-deploys to /preview/
4. Test thoroughly at /preview/ (debug mode enabled)
5. Run "Promote Preview" workflow → creates PR to main
6. Review and merge PR to main
7. Production deploys automatically


16.5 DEBUG MODE FEATURES
------------------------

When debug mode is enabled (preview/dev config):

Browser Console Shows:
- [KRWL Debug] Config loaded: {...}
- [KRWL Debug] Data source mode: both
- [KRWL Debug] Loaded X real events
- [KRWL Debug] Loaded Y demo events
- [KRWL Debug] Filtering events: {...}
- [KRWL Debug] Event "Title" filtered out: reason
- [KRWL Debug] Filtered to X events

Browser Title:
- Shows "[DEBUG MODE]" indicator
- Demo events marked with [DEMO] prefix

To Enable Debug Mode:
1. Set "debug": true in config file
2. Or use config.dev.json
3. Check console for [KRWL Debug] messages


16.6 DEMO EVENTS
----------------

Demo events are automatically generated from real event templates with
current timestamps, making them perfect for testing time-based features.

Generation:
  python3 generate_demo_events.py > static/events.demo.json

Features:
- Uses real events as templates (preserves structure)
- Fresh timestamps relative to current time
- Marked with [DEMO] prefix in titles
- Includes sunrise edge cases for testing:
  * Events ending 5 min before sunrise
  * Events ending exactly at sunrise
  * Events ending after sunrise (should filter)
  * Events crossing sunrise boundary
  * All-night events ending at sunrise
  * Events far away (distance testing)

Auto-cleanup:
- Old demo files removed automatically
- Regenerated on each preview deploy
- Always fresh and useful for testing


16.7 LOCAL TESTING
------------------

Test with Debug Mode and Demo Data:

# Generate fresh demo events
python3 generate_demo_events.py > static/events.demo.json

# Use development config
cp config.dev.json static/config.json

# Serve locally
python3 -m http.server 8000
# or
npx serve static

# Access at http://localhost:8000
# Check console for [KRWL Debug] messages
# Look for [DEMO] prefix in event titles

Test with Production Config:

# Use production config
cp config.prod.json static/config.json

# Serve locally
python3 -m http.server 8000

# Check: No debug logs (fast mode)


16.8 PROMOTE PREVIEW WORKFLOW
------------------------------

How to Promote Changes to Production:

1. Navigate to GitHub Actions tab
2. Select "Promote Preview to Production"
3. Click "Run workflow"
4. Choose auto-merge option:
   - false (default): Creates PR for manual review
   - true: Attempts to merge automatically
5. Click "Run workflow"
6. Wait for completion (~30 seconds)
7. Review the created PR
8. Merge when ready → production deploys

Auto-merge Behavior:
- With branch protection: Creates PR, merge manually
- Without branch protection: Merges automatically
- Fails gracefully if blocked

When to Use Auto-merge:
✓ Solo developer with full control
✓ Hotfix needed immediately
✓ No branch protection enabled
✓ Preview fully tested

When to Use Manual Review:
✓ Team collaboration required
✓ Branch protection enabled
✓ Following standard release process
✓ Want double-check before production


16.9 FIRST TIME SETUP
---------------------

1. Disable old workflows (if any):
   mv .github/workflows/old-deploy.yml .github/workflows/old-deploy.yml.disabled

2. Create preview branch:
   git checkout -b preview
   git push -u origin preview

3. Configure GitHub Pages:
   - Repository Settings → Pages
   - Source: GitHub Actions
   - Custom domain: (if applicable)

4. Set branch protection (recommended):
   - Protect main branch
   - Require PR reviews
   - Prevent direct pushes


16.10 TROUBLESHOOTING
---------------------

Preview site shows 404:
- Check workflow logs: Actions → Deploy Preview
- Verify publish/preview/index.html exists in logs
- Base tag should be <base href="/preview/">

Production site missing config:
- Check config.prod.json exists in repo root
- Verify workflow copies it in deploy-pages.yml logs

Assets not loading in preview:
- Base tag might be missing
- Check view-source: of /preview/ page
- Should see: <base href="/preview/">

Debug mode not working:
- Check which config is loaded: Network tab → config.json
- Verify "debug": true in config
- Check console for [KRWL Debug] messages

Demo events not showing:
- Check events.demo.json exists in publish/preview/
- Verify config.json has "source": "demo" or "source": "both"
- Generate fresh demo: python3 generate_demo_events.py > static/events.demo.json
- Demo events have [DEMO] prefix in titles

Old timestamps in demo events:
- Demo events regenerated on each preview deploy
- For local testing: run python3 generate_demo_events.py > static/events.demo.json
- Old demo files auto-cleaned during generation

Production site too slow:
- Production uses config.prod.json (optimized for speed)
- Caching enabled, no debug logging
- If still slow, check:
  * Network tab for large assets
  * events.json file size
  * Browser console for errors (should be none)


16.11 SECURITY NOTES
--------------------

Never commit secrets to repository:
✗ API keys
✗ Tokens  
✗ Credentials
✗ Passwords

Use repository secrets instead:
✓ GitHub Actions secrets
✓ Environment variables
✓ Secure credential storage

Safe in repo:
✓ Public config files
✓ Sample data
✓ Static assets
✓ Demo event generator


16.12 WORKFLOW DIAGRAM
----------------------

feature-branch
     ↓
   preview (test with debug + demo data)
     ↓
   [Test at /preview/ path]
     ↓
   [Run Promote workflow]
     ↓
   PR: preview → main
     ↓
   [Review and merge]
     ↓
   main (production: fast + real data only)
     ↓
   [Production site live]


16.13 TIPS AND BEST PRACTICES
------------------------------

✓ Keep preview clean: Only merge tested features
✓ Test thoroughly: Preview has debug mode for a reason
✓ Production deploys: Only via promotion workflow
✓ Emergency fixes: Can merge directly to main if needed
✓ Check performance: Production should be noticeably faster
✓ Use demo events: Perfect for testing time-based features
✓ Monitor logs: Check workflow logs for issues
✓ Branch protection: Recommended for team workflows


16.14 PERFORMANCE OPTIMIZATIONS
--------------------------------

Production Mode (config.prod.json):
- Debug logging: OFF (no console overhead)
- Caching: ENABLED (faster repeat visits)
- Prefetching: ENABLED (anticipate user needs)
- Data source: Real only (no demo data overhead)
- Result: Maximum speed, optimal user experience

Development Mode (config.dev.json):
- Debug logging: ON (troubleshooting)
- Caching: DISABLED (see fresh changes)
- Prefetching: DISABLED (predictable testing)
- Data source: Both (real + demo for testing)
- Result: Full visibility, easy debugging


16.15 RELATED FILES
-------------------

Workflow Files:
- .github/workflows/deploy-pages.yml (production)
- .github/workflows/deploy-preview.yml (preview)
- .github/workflows/promote-preview.yml (promotion)

Configuration Files:
- config.prod.json (production config)
- config.dev.json (development config)

Scripts:
- generate_demo_events.py (demo event generator)

Documentation:
- .github/DEPLOYMENT.md (detailed deployment guide)
- .github/PROMOTE_WORKFLOW.md (promote workflow guide)
- README.md (project overview)
- README.txt (this file - complete documentation)


================================================================================
END OF DEPLOYMENT WORKFLOWS DOCUMENTATION
================================================================================

For more details, see:
- .github/DEPLOYMENT.md - Full deployment guide
- .github/PROMOTE_WORKFLOW.md - Promote workflow details
- https://github.com/feileberlin/krwl-hof

Last updated: 2025-12-08
