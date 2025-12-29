"""Static site generator module

⚠️  IMPORTANT: This module generates static HTML/CSS/JS files
    
The templates in this file are the SINGLE SOURCE OF TRUTH for:
  - static/index.html
  - static/css/style.css
  - static/js/app.js

DO NOT edit those files directly - edit the templates here instead.

The generator includes protection against overwriting manual changes:
  - check_manual_changes() detects differences before regeneration
  - User is prompted to confirm before overwriting
  - Generated files include AUTO-GENERATED comments at the top

To regenerate: python3 src/main.py generate
"""

import json
from pathlib import Path
from .utils import load_events


class StaticSiteGenerator:
    """Generator for static site files
    
    This class manages generation of static HTML, CSS, and JavaScript files
    from templates defined in this module. All edits to the static site
    structure should be made here, not in the static/ directory directly.
    """
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.static_path = base_path / 'static'
    
    def check_manual_changes(self):
        """Check if static files differ from what templates would generate.
        Returns True if manual changes detected, False otherwise."""
        import tempfile
        import filecmp
        
        # Generate templates to temp location
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Generate to temp files
            html_content = self._get_html_content()
            css_content = self._get_css_content()
            js_content = self._get_js_content()
            
            (tmp_path / 'index.html').write_text(html_content)
            (tmp_path / 'style.css').write_text(css_content)
            (tmp_path / 'app.js').write_text(js_content)
            
            # Compare with existing static files
            files_differ = []
            if (self.static_path / 'index.html').exists():
                if not filecmp.cmp(tmp_path / 'index.html', self.static_path / 'index.html', shallow=False):
                    files_differ.append('index.html')
            
            if (self.static_path / 'css' / 'style.css').exists():
                if not filecmp.cmp(tmp_path / 'style.css', self.static_path / 'css' / 'style.css', shallow=False):
                    files_differ.append('css/style.css')
            
            if (self.static_path / 'js' / 'app.js').exists():
                if not filecmp.cmp(tmp_path / 'app.js', self.static_path / 'js' / 'app.js', shallow=False):
                    files_differ.append('js/app.js')
            
            if files_differ:
                print("\n⚠️  WARNING: Manual changes detected in static files!")
                print("The following files differ from generator templates:")
                for f in files_differ:
                    print(f"  - static/{f}")
                print("\nThese changes will be OVERWRITTEN if you continue.")
                return True
            
            return False
        
    def generate_all(self, skip_check=False):
        """Generate all static files.
        Returns True if generation completed, False if cancelled."""
        from .utils import archive_old_events
        
        # Check for manual changes unless explicitly skipped
        if not skip_check:
            if self.check_manual_changes():
                response = input("\nContinue anyway? (yes/no): ").strip().lower()
                if response != 'yes':
                    print("Generation cancelled.")
                    return False
        
        print("Archiving old events...")
        archived_count = archive_old_events(self.base_path)
        if archived_count > 0:
            print(f"  Archived {archived_count} past event(s)")
        
        print("Generating HTML...")
        self._generate_html()
        
        print("Generating CSS...")
        self._generate_css()
        
        print("Generating JavaScript...")
        self._generate_js()
        
        print("Copying data files...")
        self._copy_data_files()
        
        print("Creating warning notice...")
        self._create_warning_notice()
        
        print("\n✓ Generation complete!")
        return True
    
    def _get_html_content(self):
        """Get HTML content from template"""
        # Load events for noscript fallback and inline data
        events_data = load_events(self.base_path)
        events = events_data.get('events', []) if isinstance(events_data, dict) else []
        
        # Serialize events data for inline injection
        import json
        events_json = json.dumps(events_data)
        
        # Generate noscript event cards
        noscript_events_html = ""
        if events and len(events) > 0:
            for event in events[:20]:  # Limit to 20 events for performance
                # Format date
                try:
                    from datetime import datetime
                    event_date = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                    formatted_date = event_date.strftime('%A, %B %d, %Y at %I:%M %p')
                except:
                    formatted_date = event.get('start_time', 'Date TBA')
                
                location_name = event.get('location', {}).get('name', 'Location TBA')
                category = event.get('category', 'other')
                
                noscript_events_html += f'''
                    <div class="noscript-event-card">
                        <h3>{event.get('title', 'Untitled Event')}</h3>
                        <p><strong>📅 When:</strong> {formatted_date}</p>
                        <p><strong>📍 Where:</strong> {location_name}</p>
                        <p><strong>🏷️ Category:</strong> {category}</p>
                        {f'<p>{event.get("description", "")}</p>' if event.get('description') else ''}
                        {f'<p><a href="{event.get("url", "#")}" target="_blank" rel="noopener">More information →</a></p>' if event.get('url') else ''}
                    </div>'''
        else:
            noscript_events_html = '''
                    <div class="noscript-no-events">
                        <p>No events currently scheduled.</p>
                        <p style="font-size: 0.9rem; margin-top: 1rem;">Events will appear here when they are added by organizers.</p>
                    </div>'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KRWL HOF - Community Events</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body>
    <!-- AUTO-GENERATED: This file is generated from src/modules/generator.py -->
    <!-- DO NOT EDIT: Manual changes will be overwritten on next build -->
    <!-- To modify: Edit templates in src/modules/generator.py, then run: python3 src/main.py generate -->
    
    <div id="app">
        <noscript>
            <style>
                #noscript-fallback {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #1a1a1a;
                    color: #fff;
                }}
                #noscript-fallback header {{
                    text-align: center;
                    margin-bottom: 2rem;
                }}
                #noscript-fallback h1 {{
                    color: #FF69B4;
                    margin-bottom: 0.5rem;
                }}
                .noscript-filter-sentence {{
                    padding: 1rem;
                    background: rgba(30, 30, 30, 0.95);
                    border: 2px solid #FF69B4;
                    border-radius: 8px;
                    margin-bottom: 2rem;
                    color: #FF69B4;
                    line-height: 1.6;
                }}
                .noscript-events-list {{
                    display: grid;
                    gap: 1.5rem;
                }}
                .noscript-event-card {{
                    background: rgba(30, 30, 30, 0.95);
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 1.5rem;
                    transition: border-color 0.2s;
                }}
                .noscript-event-card:hover {{
                    border-color: #FF69B4;
                }}
                .noscript-event-card h3 {{
                    color: #FF69B4;
                    margin-bottom: 0.5rem;
                }}
                .noscript-event-card p {{
                    margin: 0.5rem 0;
                    color: #ccc;
                }}
                .noscript-event-card strong {{
                    color: #fff;
                }}
                .noscript-event-card a {{
                    color: #FF69B4;
                    text-decoration: none;
                }}
                .noscript-event-card a:hover {{
                    text-decoration: underline;
                }}
                .noscript-no-events {{
                    text-align: center;
                    padding: 3rem;
                    color: #aaa;
                }}
            </style>
            <div id="noscript-fallback">
                <header>
                    <h1>KRWL HOF Community Events</h1>
                    <p style="color: #aaa;">This is a static version. Enable JavaScript for the interactive map and filters.</p>
                </header>
                
                <div class="noscript-filter-sentence">
                    All upcoming community events in all categories
                </div>
                
                <div class="noscript-events-list">
                    {noscript_events_html}
                </div>
                
                <footer style="text-align: center; margin-top: 3rem; padding: 2rem; border-top: 1px solid #555;">
                    <p style="color: #aaa; font-size: 0.9rem;">For the best experience with interactive filters and maps, please enable JavaScript.</p>
                </footer>
            </div>
        </noscript>
        
        <div id="map">
            <div id="map-overlay">
                <!-- Interactive filter sentence -->
                <div id="filter-sentence">
                    <!-- Logo: Inline SVG megaphone (gray stroke, transitions to pink on hover) -->
                    <!-- Source: Generated from src/modules/generator.py template -->
                    <a href="imprint.html" id="imprint-link">
                        <svg xmlns="http://www.w3.org/2000/svg" id="site-logo" width="20" height="20" viewBox="0 0 20 20">
                            <g transform="translate(1, 1.5)">
                                <path style="fill:none;stroke:#cccccc;stroke-width:1.2;" 
                                      d="M 4.43,15.8 H 3.81 c -0.64,-0.19 -0.9,-4.46 -0.02,-5.45 0.61,-0.06 3.81,-0.06 3.81,-0.06 0,0 2.37,0.19 7.44,-3.62 0,0 0.17,0.02 0.85,4.58 0,0 1.42,1.76 -0.11,3.71 0,0 -0.27,3.6 -0.7,4.52 0,0 -4.17,-3.43 -8.8,-3.73 l -0.04,3.58 c -0.07,0.43 -1.71,0.37 -1.72,0 z" />
                            </g>
                        </svg>
                    </a>
                    
                    <span id="event-count-text">0 events</span>
                    
                    <span id="category-text" class="filter-part" title="Click to change category">in all categories</span>
                    
                    <span id="time-text" class="filter-part" title="Click to change time range">till sunrise</span>
                    
                    <span id="distance-text" class="filter-part" title="Click to change distance">within 15 minutes walk</span>
                    
                    <span id="location-text" class="filter-part" title="Click to change location">from your location</span>
                    
                    <button id="reset-filters-btn" class="reset-icon" title="Reset all filters">⟲</button>
                </div>
                
                <!-- Environment watermark (bottom-left) -->
                <div id="env-watermark" class="hidden"></div>
                
                <!-- SVG container for arrows connecting markers to detail boxes -->
                <div id="event-arrows-container"></div>
            </div>
        </div>
        
        <div id="event-detail" class="hidden">
            <div class="detail-content">
                <button id="close-detail">&times;</button>
                <h2 id="detail-title"></h2>
                <p id="detail-description"></p>
                <div id="detail-info">
                    <p><strong>Location:</strong> <span id="detail-location"></span></p>
                    <p><strong>Time:</strong> <span id="detail-time"></span></p>
                    <p><strong>Distance:</strong> <span id="detail-distance"></span></p>
                </div>
                <a id="detail-link" href="#" target="_blank">More Info</a>
            </div>
        </div>
    </div>
    
    <!-- Inline events data -->
    <script>
        window.__INLINE_EVENTS_DATA__ = {events_json};
    </script>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
'''
    
    def _generate_html(self):
        """Generate index.html"""
        html_content = self._get_html_content()
        html_path = self.static_path / 'index.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
            
    def _get_css_content(self):
        """Get CSS content from template"""
        return '''/* AUTO-GENERATED: This file is generated from src/modules/generator.py */
/* DO NOT EDIT: Manual changes will be overwritten on next build */
/* To modify: Edit templates in src/modules/generator.py, then run: python3 src/main.py generate */

/*
MONOCHROME COLOR PALETTE:
- Accent (Barbie Red): #FF69B4
- Accent Glow: rgba(255, 105, 180, 0.3-0.5)
- Backgrounds: #1a1a1a, #2d2d2d, #2a2a2a (dark grays)
- Text Primary: #ffffff, #ccc (light grays)
- Text Secondary: #aaa, #888 (medium grays)
- Borders/Accents: All use #FF69B4 or gray shades
- NO other colors used (no green, blue, yellow, etc.)
*/

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: #1a1a1a;
    color: #ffffff;
    overflow: hidden;
}

#app {
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header is removed from UI but styles kept for backwards compatibility */
header {
    display: none;
}

#map {
    flex: 1;
    position: relative;
    z-index: 1;
    background: #2a2a2a;
}

/* Set dark gray background for unloaded map tiles */
.leaflet-container {
    background: #2a2a2a;
}

.leaflet-tile-container {
    background: #2a2a2a;
}

#map-overlay {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    pointer-events: none;
    z-index: 1000;
}

#map-overlay > * {
    pointer-events: auto;
}

/* Interactive filter sentence */
#filter-sentence {
    position: absolute;
    top: 0;
    left: 0;
    right: auto;
    max-width: calc(100vw - 80px); /* Mobile first: adapt to screen width */
    font-size: 0.95rem;
    font-weight: 500;
    color: #FF69B4;
    padding: 0.8rem;
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    border: 2px solid #FF69B4;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5),
                0 0 10px rgba(255, 105, 180, 0.3);
    text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    align-items: center;
    word-break: break-word;
}

#filter-sentence .filter-part {
    cursor: pointer;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 3px;
    transition: all 0.2s;
    position: relative;
}

#filter-sentence .filter-part:hover {
    color: #ffffff;
    text-shadow: 0 0 15px rgba(255, 105, 180, 0.8);
    text-decoration-style: solid;
}

#filter-sentence .filter-part.active {
    color: #ffffff;
    background: rgba(255, 105, 180, 0.2);
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
}

#reset-filters-btn {
    background: none;
    border: none;
    color: #FF69B4;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0 0.3rem;
    margin-left: 0.3rem;
    transition: all 0.2s;
}

#reset-filters-btn:hover {
    color: #ffffff;
    transform: rotate(-90deg);
}

/* Filter dropdowns */
.filter-dropdown {
    position: fixed;
    background: rgba(30, 30, 30, 0.98);
    backdrop-filter: blur(10px);
    border: 2px solid #FF69B4;
    border-radius: 8px;
    padding: 0.8rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5),
                0 0 10px rgba(255, 105, 180, 0.3);
    z-index: 2000;
    min-width: 200px;
    white-space: normal;
}

.filter-dropdown select,
.filter-dropdown input[type="range"],
.filter-dropdown input[type="number"],
.filter-dropdown button {
    width: 100%;
    margin: 0.3rem 0;
    padding: 0.5rem;
    background: #2a2a2a;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 4px;
    font-size: 0.9rem;
}

.filter-dropdown select:focus,
.filter-dropdown input:focus,
.filter-dropdown button:focus {
    outline: none;
    border-color: #FF69B4;
}

.filter-dropdown label {
    display: block;
    color: #ccc;
    margin: 0.5rem 0;
    font-size: 0.85rem;
}

.filter-dropdown input[type="checkbox"] {
    width: auto;
    margin-right: 0.5rem;
}

#distance-value {
    color: #FF69B4;
    font-weight: 600;
    margin-left: 0.5rem;
}

#imprint-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.2rem;
    margin-right: 0.5rem;
    background: none;
    color: #ccc;
    text-decoration: none;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s;
}

#imprint-link:hover {
    background: rgba(255, 105, 180, 0.1);
    color: #FF69B4;
}

#site-logo {
    height: 20px;
    width: 20px;
    display: block;
}

#site-logo path {
    stroke: #ccc !important;
    transition: stroke 0.2s;
}

#imprint-link:hover #site-logo path {
    stroke: #FF69B4 !important;
}

#imprint-text {
    display: none;
}

#env-watermark {
    position: absolute;
    bottom: 0;
    left: 0;
    padding: 0.5rem 1rem;
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    text-transform: uppercase;
    font-family: 'Courier New', monospace;
}

#env-watermark.hidden {
    display: none;
}

/* All environment markers use same monochrome style */
#env-watermark.production,
#env-watermark.preview,
#env-watermark.testing,
#env-watermark.development {
    border: 2px solid #FF69B4;
    color: #FF69B4;
    text-shadow: 0 0 5px rgba(255, 105, 180, 0.5);
}

#event-list {
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    width: 350px;
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(10px);
    padding: 1.5rem;
    overflow-y: auto;
    box-shadow: -5px 0 20px rgba(0, 0, 0, 0.3);
    z-index: 999;
}

#event-list.hidden {
    display: none;
}

    background: rgba(100, 100, 100, 0.2);
    color: #aaa;
    border: 1px solid #555;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    transition: all 0.2s;
}

#reset-filters:hover {
    background: rgba(100, 100, 100, 0.3);
    border-color: #888;
    color: #ccc;
}

#distance-value {
    color: #FF69B4;
    font-weight: bold;
    font-size: 0.9rem;
}

.location-override label {
    display: flex;
    align-items: center;
    cursor: pointer;
}

.location-override input[type="checkbox"] {
    margin-right: 0.5rem;
    cursor: pointer;
}

.event-card {
    background: rgba(45, 45, 45, 0.9);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    border-left: 3px solid #FF69B4;
}

.event-card:hover {
    transform: translateX(-5px);
    box-shadow: 0 5px 15px rgba(255, 105, 180, 0.3);
    background: rgba(55, 55, 55, 0.9);
}

.event-card h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: #FF69B4;
}

.event-card p {
    font-size: 0.85rem;
    color: #ccc;
    margin-bottom: 0.3rem;
}

.event-card .distance {
    color: #888;
    font-size: 0.8rem;
}

#event-detail {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

#event-detail.hidden {
    display: none;
}

.detail-content {
    background: #2d2d2d;
    border-radius: 12px;
    padding: 2rem;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
    border: 2px solid #FF69B4;
    box-shadow: 0 0 20px rgba(255, 105, 180, 0.3);
}

#close-detail {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    color: #ccc;
    font-size: 2rem;
    cursor: pointer;
    line-height: 1;
    transition: color 0.2s;
}

#close-detail:hover {
    color: #FF69B4;
}

.detail-content h2 {
    margin-bottom: 1rem;
    color: #FF69B4;
    text-shadow: 0 0 10px rgba(255, 105, 180, 0.3);
}

.detail-content p {
    line-height: 1.6;
    margin-bottom: 1rem;
    color: #ccc;
}

#detail-info {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    border: 1px solid rgba(255, 105, 180, 0.2);
}

#detail-link {
    display: inline-block;
    background: #FF69B4;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    text-decoration: none;
    transition: all 0.2s;
    box-shadow: 0 0 10px rgba(255, 105, 180, 0.3);
}

#detail-link:hover {
    background: #ff4da6;
    box-shadow: 0 0 15px rgba(255, 105, 180, 0.5);
}

/* Edge-positioned event details with arrows */
.event-detail-edge {
    position: fixed;
    background: rgba(30, 30, 30, 0.98);
    backdrop-filter: blur(10px);
    border: 2px solid #FF69B4;
    border-radius: 8px;
    padding: 1rem;
    max-width: 280px;
    z-index: 1500;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5),
                0 0 10px rgba(255, 105, 180, 0.3);
    pointer-events: auto;
}

.event-detail-edge h3 {
    color: #FF69B4;
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.event-detail-edge p {
    color: #ccc;
    font-size: 0.85rem;
    margin: 0.3rem 0;
    line-height: 1.4;
}

.event-detail-edge .detail-time {
    color: #aaa;
    font-size: 0.8rem;
}

.event-detail-edge .detail-distance {
    color: #888;
    font-size: 0.75rem;
    margin-top: 0.5rem;
}

/* SVG arrow container */
#event-arrows-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1400;
}

#event-arrows-container svg {
    width: 100%;
    height: 100%;
}

/* Leaflet customization */
.leaflet-popup-content-wrapper {
    background: #2d2d2d;
    color: white;
    border: 2px solid #FF69B4;
}

.leaflet-popup-tip {
    background: #2d2d2d;
    border-color: #FF69B4;
}

/* Monochrome marker glow - barbie red instead of green */
.leaflet-marker-icon {
    filter: drop-shadow(0 0 2px #FF69B4);
    transition: filter 0.2s ease;
}

.leaflet-marker-icon:hover {
    filter: drop-shadow(0 0 4px #FF69B4) 
            drop-shadow(0 0 8px #FF69B4);
}

/* Scrollbar styling - monochrome */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}

::-webkit-scrollbar-thumb {
    background: #FF69B4;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #ff4da6;
}

@media (max-width: 768px) {
    #filter-sentence {
        max-width: calc(100vw - 40px); /* More space on mobile */
        font-size: 0.85rem;
    }
    
    #event-list {
        width: 100%;
        top: auto;
        bottom: 0;
        height: 40vh;
    }
    
    #map {
        height: 60vh;
    }
}

@media (max-width: 480px) {
    #filter-sentence {
        max-width: calc(100vw - 30px);
        font-size: 0.8rem;
        padding: 0.6rem;
        gap: 0.2rem;
    }
    
    .filter-dropdown {
        max-width: calc(100vw - 40px);
        font-size: 0.85rem;
    }
}
'''
    
    def _generate_css(self):
        """Generate style.css"""
        css_content = self._get_css_content()
        css_path = self.static_path / 'css' / 'style.css'
        with open(css_path, 'w') as f:
            f.write(css_content)
    
    def _get_js_content(self):
        """Get JavaScript content from template"""
        return '''// AUTO-GENERATED: This file is generated from src/modules/generator.py
// DO NOT EDIT: Manual changes will be overwritten on next build
// To modify: Edit templates in src/modules/generator.py, then run: python3 src/main.py generate

// KRWL HOF Community Events App
class EventsApp {
    constructor() {
        this.map = null;
        this.userLocation = null;
        this.events = [];
        this.markers = [];
        this.config = null;
        this.currentEdgeDetail = null;
        this.filters = {
            maxDistance: 5,
            timeFilter: 'sunrise',
            category: 'all',
            useCustomLocation: false,
            customLat: null,
            customLon: null
        };
        
        this.init();
    }
    
    // Debug logging helper
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[KRWL Debug]', message, ...args);
        }
    }
    
    async init() {
        // Load configuration
        await this.loadConfig();
        
        this.log('App initialized', 'Config:', this.config);
        
        // Display environment watermark if configured
        this.displayEnvironmentWatermark();
        
        // Initialize map (wrapped in try-catch to handle missing Leaflet)
        try {
            this.initMap();
        } catch (error) {
            console.warn('Map initialization failed:', error.message);
        }
        
        // Get user location
        this.getUserLocation();
        
        // Load events
        await this.loadEvents();
        
        // Setup event listeners (always run, even if map fails)
        this.setupEventListeners();
    }
    
    displayEnvironmentWatermark() {
        const watermark = document.getElementById('env-watermark');
        if (!watermark) return;
        
        // Check if watermark is enabled in config
        const watermarkConfig = this.config.watermark || {};
        const enabled = watermarkConfig.enabled !== undefined ? watermarkConfig.enabled : false;
        
        if (!enabled) {
            watermark.classList.add('hidden');
            return;
        }
        
        // Get environment info
        const environment = this.config.app?.environment || 'unknown';
        const envText = watermarkConfig.text || environment.toUpperCase();
        
        // Get build info (commit, PR)
        const buildInfo = this.config.build_info || {};
        let text = envText;
        
        // Add commit info if available
        if (buildInfo.commit_short) {
            text += ` • ${buildInfo.commit_short}`;
        }
        
        // Add PR number if available
        if (buildInfo.pr_number && buildInfo.pr_number !== '') {
            text += ` • PR#${buildInfo.pr_number}`;
        }
        
        // Set watermark text and style
        watermark.textContent = text;
        watermark.classList.remove('hidden', 'production', 'preview', 'testing', 'development');
        watermark.classList.add(environment.toLowerCase());
        
        // Make watermark clickable to show more details if available
        if (buildInfo.commit_sha) {
            watermark.style.cursor = 'pointer';
            watermark.title = `Click for build details\\nCommit: ${buildInfo.commit_sha}\\nDeployed: ${buildInfo.deployed_at || 'N/A'}\\nDeployed by: ${buildInfo.deployed_by || 'N/A'}`;
            watermark.onclick = () => {
                const details = [
                    `Environment: ${environment}`,
                    `Commit: ${buildInfo.commit_sha}`,
                    buildInfo.pr_number ? `PR: #${buildInfo.pr_number}` : null,
                    `Deployed: ${buildInfo.deployed_at || 'N/A'}`,
                    `Deployed by: ${buildInfo.deployed_by || 'N/A'}`,
                    `Ref: ${buildInfo.ref || 'N/A'}`
                ].filter(Boolean).join('\\n');
                alert(details);
            };
        }
    }
    
    async loadConfig() {
        try {
            const response = await fetch('config.json');
            this.config = await response.json();
        } catch (error) {
            console.error('Error loading config:', error);
            // Use defaults
            this.config = {
                map: {
                    default_center: { lat: 52.52, lon: 13.405 },
                    default_zoom: 13
                },
                filtering: {
                    max_distance_km: 5.0,
                    show_until: "next_sunrise"
                }
            };
        }
    }
    
    initMap() {
        const center = this.config.map.default_center;
        // Disable zoom controls - use keyboard shortcuts (+ / -) or pinch zoom on mobile
        this.map = L.map('map', {
            zoomControl: false,
            attributionControl: false
        }).setView([center.lat, center.lon], this.config.map.default_zoom);
        
        L.tileLayer(this.config.map.tile_provider, {
            attribution: this.config.map.attribution
        }).addTo(this.map);
    }
    
    getUserLocation() {
        const statusEl = document.getElementById('location-status');
        
        if ('geolocation' in navigator) {
            if (statusEl) statusEl.textContent = 'Getting your location...';
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    // Center map on user location (if map is initialized)
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                        
                        // Add user marker with custom geolocation icon
                        // Support customization from config or use default
                        const userMarkerConfig = this.config.map.user_location_marker || {};
                        const userIconUrl = userMarkerConfig.icon || 'markers/marker-geolocation.svg';
                        const userIconSize = userMarkerConfig.size || [32, 48];
                        const userIconAnchor = userMarkerConfig.anchor || [userIconSize[0] / 2, userIconSize[1]];
                        const userPopupAnchor = userMarkerConfig.popup_anchor || [0, -userIconSize[1]];
                        
                        const userIcon = L.icon({
                            iconUrl: userIconUrl,
                            iconSize: userIconSize,
                            iconAnchor: userIconAnchor,
                            popupAnchor: userPopupAnchor
                        });
                        
                        L.marker([this.userLocation.lat, this.userLocation.lon], {
                            icon: userIcon
                        }).addTo(this.map).bindPopup('You are here');
                    }
                    
                    if (statusEl) statusEl.textContent = '📍 Location found';
                    
                    // Update events display
                    this.displayEvents();
                },
                (error) => {
                    console.error('Location error:', error);
                    if (statusEl) statusEl.textContent = '⚠️ Location unavailable - using default location';
                    
                    // Use config default location as fallback
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    // Center map on default location (if map is initialized)
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    }
                    
                    // Still display events with fallback location
                    this.displayEvents();
                }
            );
        } else {
            if (statusEl) statusEl.textContent = '⚠️ Geolocation not supported - using default location';
            
            // Use config default location as fallback
            const defaultCenter = this.config.map.default_center;
            this.userLocation = {
                lat: defaultCenter.lat,
                lon: defaultCenter.lon
            };
            
            this.displayEvents();
        }
    }
    
    async loadEvents() {
        try {
            this.log('Loading events...', 'Data source:', this.config.data?.source);
            
            // Check for inline events data first
            if (window.__INLINE_EVENTS_DATA__) {
                this.log('Using inline events data');
                const data = window.__INLINE_EVENTS_DATA__;
                this.events = data.events || [];
                this.log(`Loaded ${this.events.length} events from inline data`);
                this.populateCategories();
                return;
            }
            
            // Fallback to fetching events if no inline data
            // Determine which data source(s) to load
            const dataSource = this.config.data?.source || 'real';
            const dataSources = this.config.data?.sources || {};
            
            let allEvents = [];
            
            if (dataSource === 'both' && dataSources.both?.urls) {
                // Load from multiple sources and combine
                this.log('Loading from multiple sources:', dataSources.both.urls);
                for (const url of dataSources.both.urls) {
                    try {
                        const response = await fetch(url);
                        const data = await response.json();
                        const events = data.events || [];
                        allEvents = allEvents.concat(events);
                        this.log(`Loaded ${events.length} events from ${url}`);
                    } catch (err) {
                        console.warn(`Failed to load events from ${url}:`, err);
                    }
                }
            } else {
                // Load from single source
                const sourceConfig = dataSources[dataSource];
                const url = sourceConfig?.url || 'events.json';
                this.log('Loading from single source:', url);
                
                const response = await fetch(url);
                const data = await response.json();
                allEvents = data.events || [];
                this.log(`Loaded ${allEvents.length} events from ${url}`);
            }
            
            this.events = allEvents;
            
            // Extract unique categories from events
            this.populateCategories();
        } catch (error) {
            console.error('Error loading events:', error);
            this.events = [];
        }
    }
    
    populateCategories() {
        const categories = new Set();
        this.events.forEach(event => {
            if (event.category) {
                categories.add(event.category);
            }
        });
        
        // Populate category filter dropdown
        const categoryFilter = document.getElementById('category-filter');
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }
    
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    getMaxEventTime() {
        const now = new Date();
        const timeFilter = this.filters.timeFilter;
        
        switch (timeFilter) {
            case 'sunrise':
                // Simplified: next sunrise at 6 AM
                const sunrise = new Date(now);
                sunrise.setHours(6, 0, 0, 0);
                if (now.getHours() >= 6) {
                    sunrise.setDate(sunrise.getDate() + 1);
                }
                return sunrise;
                
            case '6h':
                return new Date(now.getTime() + 6 * 60 * 60 * 1000);
                
            case '12h':
                return new Date(now.getTime() + 12 * 60 * 60 * 1000);
                
            case '24h':
                return new Date(now.getTime() + 24 * 60 * 60 * 1000);
                
            case '48h':
                return new Date(now.getTime() + 48 * 60 * 60 * 1000);
                
            case 'all':
                // Return a date far in the future
                return new Date(now.getFullYear() + 10, 11, 31);
                
            default:
                return this.getNextSunrise();
        }
    }
    
    getNextSunrise() {
        // Simplified: next sunrise at 6 AM
        const now = new Date();
        const sunrise = new Date(now);
        sunrise.setHours(6, 0, 0, 0);
        
        if (now.getHours() >= 6) {
            sunrise.setDate(sunrise.getDate() + 1);
        }
        
        return sunrise;
    }
    
    filterEvents() {
        const maxEventTime = this.getMaxEventTime();
        const maxDistance = this.filters.maxDistance;
        const category = this.filters.category;
        
        // Determine which location to use for distance calculation
        let referenceLocation = this.userLocation;
        if (this.filters.useCustomLocation && this.filters.customLat && this.filters.customLon) {
            referenceLocation = {
                lat: this.filters.customLat,
                lon: this.filters.customLon
            };
        }
        
        const filtered = this.events.filter(event => {
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                return false;
            }
            
            // Filter by category
            if (category !== 'all' && event.category !== category) {
                return false;
            }
            
            // Filter by distance if location is available
            if (referenceLocation && event.location) {
                const distance = this.calculateDistance(
                    referenceLocation.lat,
                    referenceLocation.lon,
                    event.location.lat,
                    event.location.lon
                );
                event.distance = distance;
                
                if (distance > maxDistance) {
                    return false;
                }
            }
            
            return true;
        });
        
        return filtered;
    }
    
    fitMapToMarkers() {
        if (this.markers.length === 0) {
            return;
        }
        
        // Create bounds from all marker positions
        const bounds = L.latLngBounds();
        
        this.markers.forEach(marker => {
            bounds.extend(marker.getLatLng());
        });
        
        // Add user location to bounds if available
        if (this.userLocation) {
            bounds.extend([this.userLocation.lat, this.userLocation.lon]);
        }
        
        // Fit the map to show all markers with some padding
        this.map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 15
        });
    }
    
    displayEvents() {
        const filteredEvents = this.filterEvents();
        
        // Update count with descriptive sentence
        this.updateFilterDescription(filteredEvents.length);
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        if (filteredEvents.length === 0) {
            // No events to display on map
            return;
        }
        
        // Sort by distance
        filteredEvents.sort((a, b) => (a.distance || 0) - (b.distance || 0));
        
        // Display events as markers on the map
        filteredEvents.forEach(event => {
            this.addEventMarker(event);
        });
        
        // Fit map to show all markers
        this.fitMapToMarkers();
    }
    
    updateFilterDescription(count) {
        // Update individual parts of the filter sentence
        const eventCountText = document.getElementById('event-count-text');
        const categoryText = document.getElementById('category-text');
        const timeText = document.getElementById('time-text');
        const distanceText = document.getElementById('distance-text');
        const locationText = document.getElementById('location-text');
        
        // Event count
        if (eventCountText) {
            eventCountText.textContent = `${count} event${count !== 1 ? 's' : ''}`;
        }
        
        // Category description
        if (categoryText) {
            if (this.filters.category !== 'all') {
                categoryText.textContent = `in ${this.filters.category}`;
            } else {
                categoryText.textContent = 'in all categories';
            }
        }
        
        // Time description
        if (timeText) {
            let timeDescription = '';
            switch (this.filters.timeFilter) {
                case 'sunrise':
                    timeDescription = 'till sunrise';
                    break;
                case '6h':
                    timeDescription = 'in the next 6 hours';
                    break;
                case '12h':
                    timeDescription = 'in the next 12 hours';
                    break;
                case '24h':
                    timeDescription = 'in the next 24 hours';
                    break;
                case '48h':
                    timeDescription = 'in the next 48 hours';
                    break;
                case 'all':
                    timeDescription = 'upcoming';
                    break;
            }
            timeText.textContent = timeDescription;
        }
        
        // Distance description (approximate travel time)
        if (distanceText) {
            const distance = this.filters.maxDistance;
            let distanceDescription = '';
            if (distance <= 1) {
                distanceDescription = 'within walking distance';
            } else if (distance <= 5) {
                const minutes = Math.round(distance * 3); // ~3 min per km walking
                distanceDescription = `within ${minutes} minutes walk`;
            } else if (distance <= 15) {
                const minutes = Math.round(distance * 4); // ~4 min per km by bike
                distanceDescription = `within ${minutes} minutes by bike`;
            } else {
                distanceDescription = `within ${distance} km`;
            }
            distanceText.textContent = distanceDescription;
        }
        
        // Location description
        if (locationText) {
            let locDescription = 'from your location';
            if (this.filters.useCustomLocation && this.filters.customLat && this.filters.customLon) {
                locDescription = 'from custom location';
            } else if (!this.userLocation) {
                locDescription = 'from default location';
            }
            locationText.textContent = locDescription;
        }
    }
    
    displayEventCard(event, container) {
        const card = document.createElement('div');
        card.className = 'event-card';
        
        const title = document.createElement('h3');
        title.textContent = event.title;
        
        const location = document.createElement('p');
        location.textContent = `📍 ${event.location.name}`;
        
        const time = document.createElement('p');
        const eventDate = new Date(event.start_time);
        time.textContent = `🕐 ${eventDate.toLocaleString()}`;
        
        card.appendChild(title);
        card.appendChild(location);
        card.appendChild(time);
        
        if (event.distance !== undefined) {
            const distance = document.createElement('p');
            distance.className = 'distance';
            distance.textContent = `📏 ${event.distance.toFixed(1)} km away`;
            card.appendChild(distance);
        }
        
        card.addEventListener('click', () => this.showEventDetail(event));
        
        container.appendChild(card);
    }
    
    getMarkerIconForCategory(category) {
        // Return SVG marker paths for different event categories
        const iconMap = {
            'on-stage': 'markers/marker-on-stage.svg',        // Diamond with microphone
            'pub-game': 'markers/marker-pub-games.svg',       // Hexagon with beer mug
            'festival': 'markers/marker-festivals.svg',       // Star with flag
            'workshop': 'markers/marker-workshops.svg',       // Workshop icon
            'market': 'markers/marker-shopping.svg',          // Shopping bag for markets
            'sports': 'markers/marker-sports.svg',            // Sports icon
            'community': 'markers/marker-community.svg',      // Community icon
            'other': 'markers/marker-default.svg'             // Default teardrop pin
        };
        
        return iconMap[category] || iconMap['other'];
    }
    
    addEventMarker(event) {
        if (!event.location) return;
        
        // Check if event has custom marker icon, otherwise use category-based icon
        const iconUrl = event.marker_icon || this.getMarkerIconForCategory(event.category);
        
        // Support custom marker size if specified in event data
        const iconSize = event.marker_size || [32, 48];
        const iconAnchor = event.marker_anchor || [iconSize[0] / 2, iconSize[1]];
        const popupAnchor = event.marker_popup_anchor || [0, -iconSize[1]];
        
        // Create custom SVG icon using Leaflet's L.icon
        const customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: iconSize,
            iconAnchor: iconAnchor,
            popupAnchor: popupAnchor
        });
        
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: customIcon
        }).addTo(this.map);
        
        // Show edge detail on hover
        marker.on('mouseover', () => {
            this.showEventDetailAtEdge(event, marker);
        });
        
        // Hide edge detail when mouse leaves (with slight delay)
        marker.on('mouseout', () => {
            setTimeout(() => {
                // Only hide if not hovering over the detail box
                const edgeDetail = document.getElementById('current-edge-detail');
                if (edgeDetail && !edgeDetail.matches(':hover')) {
                    this.hideEventDetailAtEdge();
                }
            }, 200);
        });
        
        // Click shows full modal
        marker.on('click', () => this.showEventDetail(event));
        
        this.markers.push(marker);
    }
    
    showEventDetail(event) {
        const detail = document.getElementById('event-detail');
        
        document.getElementById('detail-title').textContent = event.title;
        document.getElementById('detail-description').textContent = event.description || 'No description available.';
        document.getElementById('detail-location').textContent = event.location.name;
        
        const eventDate = new Date(event.start_time);
        document.getElementById('detail-time').textContent = eventDate.toLocaleString();
        
        if (event.distance !== undefined) {
            document.getElementById('detail-distance').textContent = `${event.distance.toFixed(1)} km away`;
        } else {
            document.getElementById('detail-distance').textContent = 'Unknown';
        }
        
        const link = document.getElementById('detail-link');
        if (event.url) {
            link.href = event.url;
            link.style.display = 'inline-block';
        } else {
            link.style.display = 'none';
        }
        
        detail.classList.remove('hidden');
    }
    
    // Edge-positioned event details with SVG arrows
    showEventDetailAtEdge(event, markerElement) {
        // Remove any existing edge details
        this.hideEventDetailAtEdge();
        
        if (!this.map || !markerElement) return;
        
        // Get marker position on screen
        const markerLatLng = markerElement.getLatLng();
        const markerPoint = this.map.latLngToContainerPoint(markerLatLng);
        
        // Create detail box
        const detailBox = document.createElement('div');
        detailBox.className = 'event-detail-edge';
        detailBox.id = 'current-edge-detail';
        
        // Format event data
        const eventDate = new Date(event.start_time);
        const timeStr = eventDate.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const distanceStr = event.distance !== undefined 
            ? `${event.distance.toFixed(1)} km away` 
            : '';
        
        detailBox.innerHTML = `
            <h3>${event.title}</h3>
            <p class="detail-time">🕐 ${timeStr}</p>
            <p>📍 ${event.location.name}</p>
            ${distanceStr ? `<p class="detail-distance">📏 ${distanceStr}</p>` : ''}
        `;
        
        // Add to overlay
        const mapOverlay = document.getElementById('map-overlay');
        mapOverlay.appendChild(detailBox);
        
        // Determine best edge position
        const position = this.calculateEdgePosition(markerPoint, detailBox);
        
        // Position the detail box
        detailBox.style.top = position.top + 'px';
        detailBox.style.left = position.left + 'px';
        
        // Draw SVG arrow
        this.drawArrowToDetailBox(markerPoint, position, detailBox);
        
        // Store reference
        this.currentEdgeDetail = {
            box: detailBox,
            event: event,
            marker: markerElement
        };
        
        // Click to show full detail modal
        detailBox.addEventListener('click', () => this.showEventDetail(event));
        
        // Keep detail visible when hovering over it
        detailBox.addEventListener('mouseenter', () => {
            // Cancel any pending hide timeout
            if (this.hideEdgeDetailTimeout) {
                clearTimeout(this.hideEdgeDetailTimeout);
                this.hideEdgeDetailTimeout = null;
            }
        });
        
        // Hide when mouse leaves the detail box
        detailBox.addEventListener('mouseleave', () => {
            this.hideEdgeDetailTimeout = setTimeout(() => {
                this.hideEventDetailAtEdge();
            }, 300);
        });
    }
    
    calculateEdgePosition(markerPoint, detailBox) {
        const mapContainer = document.getElementById('map');
        const mapRect = mapContainer.getBoundingClientRect();
        const boxRect = detailBox.getBoundingClientRect();
        
        const margin = 20;
        const boxWidth = 280;
        const boxHeight = boxRect.height || 120;
        
        let top, left, edge;
        
        // Determine which edge is closest
        const distToLeft = markerPoint.x;
        const distToRight = mapRect.width - markerPoint.x;
        const distToTop = markerPoint.y;
        const distToBottom = mapRect.height - markerPoint.y;
        
        const minDist = Math.min(distToLeft, distToRight, distToTop, distToBottom);
        
        if (minDist === distToRight) {
            // Position on right edge
            left = mapRect.width - boxWidth - margin;
            top = Math.max(margin, Math.min(markerPoint.y - boxHeight / 2, mapRect.height - boxHeight - margin));
            edge = 'right';
        } else if (minDist === distToLeft) {
            // Position on left edge
            left = margin;
            top = Math.max(margin, Math.min(markerPoint.y - boxHeight / 2, mapRect.height - boxHeight - margin));
            edge = 'left';
        } else if (minDist === distToBottom) {
            // Position on bottom edge
            top = mapRect.height - boxHeight - margin;
            left = Math.max(margin, Math.min(markerPoint.x - boxWidth / 2, mapRect.width - boxWidth - margin));
            edge = 'bottom';
        } else {
            // Position on top edge
            top = margin + 80; // Account for filter sentence at top
            left = Math.max(margin, Math.min(markerPoint.x - boxWidth / 2, mapRect.width - boxWidth - margin));
            edge = 'top';
        }
        
        return { top, left, edge, markerPoint };
    }
    
    drawArrowToDetailBox(markerPoint, position, detailBox) {
        const arrowContainer = document.getElementById('event-arrows-container');
        if (!arrowContainer) return;
        
        // Clear existing arrows
        arrowContainer.innerHTML = '';
        
        // Create SVG
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.pointerEvents = 'none';
        
        // Calculate detail box center
        const boxRect = detailBox.getBoundingClientRect();
        const boxCenterX = boxRect.left + boxRect.width / 2;
        const boxCenterY = boxRect.top + boxRect.height / 2;
        
        // Calculate connection points for smoother arrows
        let boxX, boxY;
        const dx = boxCenterX - markerPoint.x;
        const dy = boxCenterY - markerPoint.y;
        const angle = Math.atan2(dy, dx);
        
        // Find edge point on box
        if (Math.abs(dx) > Math.abs(dy)) {
            // Connect to left or right edge
            boxX = dx > 0 ? boxRect.left : boxRect.right;
            boxY = boxCenterY;
        } else {
            // Connect to top or bottom edge
            boxX = boxCenterX;
            boxY = dy > 0 ? boxRect.top : boxRect.bottom;
        }
        
        // Create curved path
        const midX = (markerPoint.x + boxX) / 2;
        const midY = (markerPoint.y + boxY) / 2;
        
        // Create path with quadratic curve
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const pathData = `M ${markerPoint.x} ${markerPoint.y} Q ${midX} ${midY} ${boxX} ${boxY}`;
        path.setAttribute('d', pathData);
        path.setAttribute('stroke', '#FF69B4');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-dasharray', '5,5');
        path.style.filter = 'drop-shadow(0 0 3px rgba(255, 105, 180, 0.5))';
        
        svg.appendChild(path);
        
        // Add arrowhead at box end
        const arrowhead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        const arrowSize = 8;
        const arrowAngle = Math.atan2(boxY - midY, boxX - midX);
        
        const p1x = boxX + arrowSize * Math.cos(arrowAngle + Math.PI * 0.8);
        const p1y = boxY + arrowSize * Math.sin(arrowAngle + Math.PI * 0.8);
        const p2x = boxX;
        const p2y = boxY;
        const p3x = boxX + arrowSize * Math.cos(arrowAngle - Math.PI * 0.8);
        const p3y = boxY + arrowSize * Math.sin(arrowAngle - Math.PI * 0.8);
        
        arrowhead.setAttribute('points', `${p1x},${p1y} ${p2x},${p2y} ${p3x},${p3y}`);
        arrowhead.setAttribute('fill', '#FF69B4');
        arrowhead.style.filter = 'drop-shadow(0 0 3px rgba(255, 105, 180, 0.5))';
        
        svg.appendChild(arrowhead);
        arrowContainer.appendChild(svg);
    }
    
    hideEventDetailAtEdge() {
        if (this.currentEdgeDetail) {
            if (this.currentEdgeDetail.box && this.currentEdgeDetail.box.parentElement) {
                this.currentEdgeDetail.box.remove();
            }
            this.currentEdgeDetail = null;
        }
        
        // Clear arrows
        const arrowContainer = document.getElementById('event-arrows-container');
        if (arrowContainer) {
            arrowContainer.innerHTML = '';
        }
    }
    
    setupEventListeners() {
        // Interactive filter sentence parts
        const categoryTextEl = document.getElementById('category-text');
        const timeTextEl = document.getElementById('time-text');
        const distanceTextEl = document.getElementById('distance-text');
        const locationTextEl = document.getElementById('location-text');
        
        // Store references to active dropdowns
        this.activeDropdown = null;
        this.activeFilterEl = null;
        
        // Helper to hide all dropdowns
        const hideAllDropdowns = () => {
            if (this.activeDropdown && this.activeDropdown.parentElement) {
                this.activeDropdown.remove();
                this.activeDropdown = null;
            }
            
            if (categoryTextEl) categoryTextEl.classList.remove('active');
            if (timeTextEl) timeTextEl.classList.remove('active');
            if (distanceTextEl) distanceTextEl.classList.remove('active');
            if (locationTextEl) locationTextEl.classList.remove('active');
            
            this.activeFilterEl = null;
        };
        
        // Helper to create and position dropdown
        const createDropdown = (content, targetEl) => {
            hideAllDropdowns();
            
            const dropdown = document.createElement('div');
            dropdown.className = 'filter-dropdown';
            dropdown.innerHTML = content;
            
            // Add to body for proper positioning
            document.body.appendChild(dropdown);
            
            // Position below the target element
            const rect = targetEl.getBoundingClientRect();
            dropdown.style.position = 'fixed';
            dropdown.style.top = (rect.bottom + 5) + 'px';
            dropdown.style.left = rect.left + 'px';
            
            // Adjust if dropdown goes off screen
            const dropdownRect = dropdown.getBoundingClientRect();
            if (dropdownRect.right > window.innerWidth) {
                dropdown.style.left = (window.innerWidth - dropdownRect.width - 10) + 'px';
            }
            if (dropdownRect.bottom > window.innerHeight) {
                dropdown.style.top = (rect.top - dropdownRect.height - 5) + 'px';
            }
            
            this.activeDropdown = dropdown;
            this.activeFilterEl = targetEl;
            targetEl.classList.add('active');
            
            return dropdown;
        };
        
        // Category filter click
        if (categoryTextEl) {
            categoryTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === categoryTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                // Build category options from events
                let optionsHTML = '<option value="all">All Categories</option>';
                const categories = new Set();
                this.events.forEach(event => {
                    if (event.category) categories.add(event.category);
                });
                categories.forEach(cat => {
                    const selected = cat === this.filters.category ? ' selected' : '';
                    optionsHTML += `<option value="${cat}"${selected}>${cat}</option>`;
                });
                
                const content = `<select id="category-filter">${optionsHTML}</select>`;
                const dropdown = createDropdown(content, categoryTextEl);
                
                // Add event listener to select
                const select = dropdown.querySelector('#category-filter');
                select.value = this.filters.category;
                select.addEventListener('change', (e) => {
                    this.filters.category = e.target.value;
                    this.displayEvents();
                    hideAllDropdowns();
                });
            });
        }
        
        // Time filter click
        if (timeTextEl) {
            timeTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === timeTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const content = `
                    <select id="time-filter">
                        <option value="sunrise">Next Sunrise (6 AM)</option>
                        <option value="6h">Next 6 hours</option>
                        <option value="12h">Next 12 hours</option>
                        <option value="24h">Next 24 hours</option>
                        <option value="48h">Next 48 hours</option>
                        <option value="all">All upcoming events</option>
                    </select>
                `;
                const dropdown = createDropdown(content, timeTextEl);
                
                const select = dropdown.querySelector('#time-filter');
                select.value = this.filters.timeFilter;
                select.addEventListener('change', (e) => {
                    this.filters.timeFilter = e.target.value;
                    this.displayEvents();
                    hideAllDropdowns();
                });
            });
        }
        
        // Distance filter click
        if (distanceTextEl) {
            distanceTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === distanceTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const content = `
                    <input type="range" id="distance-filter" min="1" max="50" value="${this.filters.maxDistance}" step="0.5">
                    <span id="distance-value">${this.filters.maxDistance} km</span>
                `;
                const dropdown = createDropdown(content, distanceTextEl);
                
                const slider = dropdown.querySelector('#distance-filter');
                const valueDisplay = dropdown.querySelector('#distance-value');
                slider.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    this.filters.maxDistance = value;
                    valueDisplay.textContent = `${value} km`;
                    this.displayEvents();
                });
            });
        }
        
        // Location filter click
        if (locationTextEl) {
            locationTextEl.addEventListener('click', (e) => {
                e.stopPropagation();
                
                if (this.activeDropdown && this.activeFilterEl === locationTextEl) {
                    hideAllDropdowns();
                    return;
                }
                
                const latValue = this.filters.customLat || (this.userLocation ? this.userLocation.lat.toFixed(4) : '');
                const lonValue = this.filters.customLon || (this.userLocation ? this.userLocation.lon.toFixed(4) : '');
                const checked = this.filters.useCustomLocation ? ' checked' : '';
                const inputsHidden = !this.filters.useCustomLocation ? ' hidden' : '';
                
                const content = `
                    <label>
                        <input type="checkbox" id="use-custom-location"${checked}>
                        Use custom location
                    </label>
                    <div id="custom-location-inputs" class="${inputsHidden}">
                        <input type="number" id="custom-lat" placeholder="Latitude" step="0.0001" value="${latValue}">
                        <input type="number" id="custom-lon" placeholder="Longitude" step="0.0001" value="${lonValue}">
                        <button id="apply-custom-location">Apply</button>
                    </div>
                `;
                const dropdown = createDropdown(content, locationTextEl);
                
                const checkbox = dropdown.querySelector('#use-custom-location');
                const inputs = dropdown.querySelector('#custom-location-inputs');
                const applyBtn = dropdown.querySelector('#apply-custom-location');
                
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        inputs.classList.remove('hidden');
                        // Pre-fill with current location if available
                        if (this.userLocation) {
                            dropdown.querySelector('#custom-lat').value = this.userLocation.lat.toFixed(4);
                            dropdown.querySelector('#custom-lon').value = this.userLocation.lon.toFixed(4);
                        }
                    } else {
                        inputs.classList.add('hidden');
                        this.filters.useCustomLocation = false;
                        this.filters.customLat = null;
                        this.filters.customLon = null;
                        this.displayEvents();
                        hideAllDropdowns();
                    }
                });
                
                applyBtn.addEventListener('click', () => {
                    const lat = parseFloat(dropdown.querySelector('#custom-lat').value);
                    const lon = parseFloat(dropdown.querySelector('#custom-lon').value);
                    
                    if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                        this.filters.useCustomLocation = true;
                        this.filters.customLat = lat;
                        this.filters.customLon = lon;
                        
                        // Update map view to custom location
                        if (this.map) {
                            this.map.setView([lat, lon], 13);
                        }
                        
                        this.displayEvents();
                        hideAllDropdowns();
                    } else {
                        alert('Please enter valid latitude (-90 to 90) and longitude (-180 to 180) values.');
                    }
                });
            });
        }
        
        // Click outside to close dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#filter-sentence') && !e.target.closest('.filter-dropdown')) {
                hideAllDropdowns();
            }
        });
        
        // Reset filters button
        const resetFilters = document.getElementById('reset-filters-btn');
        if (resetFilters) {
            resetFilters.addEventListener('click', (e) => {
                e.stopPropagation();
                // Reset all filters to defaults
                this.filters.maxDistance = 5;
                this.filters.timeFilter = 'sunrise';
                this.filters.category = 'all';
                this.filters.useCustomLocation = false;
                this.filters.customLat = null;
                this.filters.customLon = null;
                
                // Reset map view
                if (this.userLocation && this.map) {
                    this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                }
                
                this.displayEvents();
                hideAllDropdowns();
            });
        }
        
        // Event detail close listeners
        const closeDetail = document.getElementById('close-detail');
        const eventDetail = document.getElementById('event-detail');
        
        if (closeDetail) {
            closeDetail.addEventListener('click', () => {
                if (eventDetail) eventDetail.classList.add('hidden');
            });
        }
        
        if (eventDetail) {
            eventDetail.addEventListener('click', (e) => {
                if (e.target.id === 'event-detail') {
                    eventDetail.classList.add('hidden');
                }
            });
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EventsApp();
});
'''
    
    def _generate_js(self):
        """Generate app.js"""
        js_content = self._get_js_content()
        js_path = self.static_path / 'js' / 'app.js'
        with open(js_path, 'w') as f:
            f.write(js_content)
    
    def _create_warning_notice(self):
        """Create a warning notice in static folder about auto-generation"""
        notice_path = self.static_path / 'DO_NOT_EDIT_README.txt'
        notice_content = '''⚠️  WARNING: AUTO-GENERATED FILES ⚠️
=======================================

The following files in this directory are AUTO-GENERATED by the build system:
  - index.html
  - css/style.css
  - js/app.js

These files are regenerated from templates in:
  src/modules/generator.py

🚫 DO NOT manually edit these files directly!
   Any manual changes will be OVERWRITTEN during the next build.

✅ To make changes:
   1. Edit the templates in src/modules/generator.py
   2. Run: python3 src/main.py generate
   3. Commit both the template changes AND generated files

📋 Other files (config.json, events.json, etc.) are data files and safe to edit.

Last generated: ''' + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''

For more information, see the project README.md
'''
        with open(notice_path, 'w') as f:
            f.write(notice_content)
            
    def _copy_data_files(self):
        """Copy data and config files to static directory"""
        import shutil
        
        # Copy events.json
        events_src = self.base_path / 'data' / 'events.json'
        events_dst = self.static_path / 'events.json'
        shutil.copy(events_src, events_dst)
        
        # Copy config.json
        config_src = self.base_path / 'config' / 'config.json'
        config_dst = self.static_path / 'config.json'
        shutil.copy(config_src, config_dst)
