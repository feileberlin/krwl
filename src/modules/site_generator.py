"""
Site Generator Module - Platform-Agnostic

Generates static sites with runtime configuration support.
No platform-specific dependencies (GitHub, GitLab, etc.).

Responsibilities:
- Fetch third-party dependencies (Leaflet, etc.)
- Generate single-file HTML with inlined assets
- Update content without full regeneration

Naming: Functions describe WHAT they do, not implementation history.
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple


# Third-party dependencies to fetch
DEPENDENCIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {"src": "leaflet.css", "dest": "leaflet/leaflet.css"},
            {"src": "leaflet.js", "dest": "leaflet/leaflet.js"},
            {"src": "images/marker-icon.png", "dest": "leaflet/images/marker-icon.png"},
            {"src": "images/marker-icon-2x.png", "dest": "leaflet/images/marker-icon-2x.png"},
            {"src": "images/marker-shadow.png", "dest": "leaflet/images/marker-shadow.png"}
        ]
    }
}


class SiteGenerator:
    """Generates static site with runtime-configurable behavior"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.static_path = self.base_path / 'static'
        self.dependencies_dir = self.static_path / 'lib'
        self.dependencies_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== Dependency Management ====================
    
    def fetch_file_from_url(self, url: str, destination: Path) -> bool:
        """Fetch a single file from URL and save to destination"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            print(f"  Fetching {destination.name}...", end=" ", flush=True)
            
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            
            with open(destination, 'wb') as f:
                f.write(content)
            
            print(f"✓ ({len(content) / 1024:.1f} KB)")
            return True
        except Exception as e:
            print(f"✗ {e}")
            return False
    
    def fetch_dependency_files(self, name: str, config: Dict) -> bool:
        """Fetch all files for one dependency package"""
        print(f"\n📦 {name} v{config['version']}")
        base_url = config['base_url'].format(version=config['version'])
        
        all_success = True
        for file_info in config['files']:
            url = f"{base_url}/{file_info['src']}"
            dest = self.dependencies_dir / file_info['dest']
            if not self.fetch_file_from_url(url, dest):
                all_success = False
        
        status = "✅" if all_success else "⚠️ "
        print(f"{status} {name} {'complete' if all_success else 'incomplete'}")
        return all_success
    
    def fetch_all_dependencies(self) -> bool:
        """Fetch all required third-party dependencies"""
        print("=" * 60)
        print("📦 Fetching Dependencies")
        print("=" * 60)
        
        results = [
            self.fetch_dependency_files(name, cfg) 
            for name, cfg in DEPENDENCIES.items()
        ]
        
        print("\n" + "=" * 60)
        if all(results):
            print("✅ All dependencies fetched")
        else:
            print("⚠️  Some dependencies failed")
        print("=" * 60)
        return all(results)
    
    def check_dependency_files(self, name: str, config: Dict) -> Tuple[bool, List[str]]:
        """Check if all files for one dependency exist"""
        missing = []
        for file_info in config['files']:
            dest = self.dependencies_dir / file_info['dest']
            if not dest.exists():
                missing.append(file_info['dest'])
        return len(missing) == 0, missing
    
    def check_all_dependencies(self, quiet=False) -> bool:
        """Check if all dependencies are present"""
        if not quiet:
            print("=" * 60)
            print("📋 Checking Dependencies")
            print("=" * 60)
        
        all_present = True
        for name, config in DEPENDENCIES.items():
            present, missing = self.check_dependency_files(name, config)
            
            if not quiet:
                print(f"\n📋 {name} v{config['version']}")
                if present:
                    print(f"  ✓ All files present")
                else:
                    print(f"  ✗ Missing {len(missing)} files:")
                    for m in missing:
                        print(f"    - {m}")
            
            if not present:
                all_present = False
        
        if not quiet:
            print("\n" + "=" * 60)
            if all_present:
                print("✅ All dependencies present")
            else:
                print("❌ Missing dependencies")
                print("   Run: python3 src/main.py dependencies fetch")
            print("=" * 60)
        
        return all_present
    
    # ==================== Site Generation ====================
    
    def read_text_file(self, path: Path) -> str:
        """Read text file content"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_all_events(self) -> List[Dict]:
        """Load all event data (real + demo)"""
        events = []
        
        # Real events
        events_file = self.static_path / 'events.json'
        if events_file.exists():
            with open(events_file, 'r') as f:
                events.extend(json.load(f).get('events', []))
        
        # Demo events (always include - config determines if they're shown)
        demo_file = self.static_path / 'events.demo.json'
        if demo_file.exists():
            with open(demo_file, 'r') as f:
                events.extend(json.load(f).get('events', []))
        
        return events
    
    def load_all_configs(self) -> List[Dict]:
        """
        Load configuration file.
        
        Now loads unified config.json. Environment-specific overrides
        are applied by the load_config() function in utils.py.
        """
        configs = []
        config_file = 'config.json'
        path = self.base_path / config_file
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                configs.append(json.load(f))
        return configs
    
    def load_stylesheet_resources(self) -> Dict[str, str]:
        """Load all CSS resources"""
        return {
            'leaflet_css': self.read_text_file(
                self.dependencies_dir / 'leaflet' / 'leaflet.css'
            ),
            'app_css': self.read_text_file(
                self.static_path / 'css' / 'style.css'
            ),
            'time_drawer_css': self.read_text_file(
                self.static_path / 'css' / 'time-drawer.css'
            )
        }
    
    def load_script_resources(self) -> Dict[str, str]:
        """Load all JavaScript resources"""
        return {
            'leaflet_js': self.read_text_file(
                self.dependencies_dir / 'leaflet' / 'leaflet.js'
            ),
            'i18n_js': self.read_text_file(
                self.static_path / 'js' / 'i18n.js'
            ),
            'time_drawer_js': self.read_text_file(
                self.static_path / 'js' / 'time-drawer.js'
            ),
            'app_js': self.read_text_file(
                self.static_path / 'js' / 'app.js'
            )
        }
    
    def load_translation_data(self) -> Tuple[Dict, Dict]:
        """Load translation files for all languages"""
        event_data_path = self.base_path / 'event-data'
        with open(event_data_path / 'content.json', 'r') as f:
            content_en = json.load(f)
        with open(event_data_path / 'content.de.json', 'r') as f:
            content_de = json.load(f)
        return content_en, content_de
    
    def ensure_dependencies_present(self) -> bool:
        """Ensure dependencies are available, fetch if missing"""
        if not self.check_all_dependencies(quiet=True):
            print("\n⚠️  Dependencies missing - fetching now...")
            if not self.fetch_all_dependencies():
                print("❌ Failed to fetch dependencies")
                return False
            print()
        return True
    
    def generate_favicon_dataurl(self) -> str:
        """Generate base64 data URL for favicon"""
        favicon_path = self.static_path / 'favicon.svg'
        if not favicon_path.exists():
            return "favicon.svg"
        
        import base64
        svg_content = self.read_text_file(favicon_path)
        b64_data = base64.b64encode(svg_content.encode()).decode()
        return f"data:image/svg+xml;base64,{b64_data}"
    
    def build_html_structure(
        self, 
        configs: List[Dict],
        events: List[Dict],
        content_en: Dict,
        content_de: Dict,
        stylesheets: Dict[str, str],
        scripts: Dict[str, str]
    ) -> str:
        """Build complete HTML structure with embedded data"""
        
        # Use first config for basic info (they should be similar)
        primary_config = configs[0] if configs else {}
        app_name = primary_config.get('app', {}).get('name', 'KRWL HOF Community Events')
        favicon = self.generate_favicon_dataurl()
        
        # Runtime config selection script
        config_loader = '''
// Runtime configuration loader - detects environment
(function() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Determine which config to use based on environment
    let configIndex = 0; // Default to production (first config)
    
    // Development indicators
    if (hostname === 'localhost' || 
        hostname === '127.0.0.1' ||
        pathname.includes('/dev/') ||
        pathname.includes('/test/')) {
        configIndex = 1; // Use development config if available
    }
    
    // Select config (fallback to first if index out of bounds)
    window.ACTIVE_CONFIG = window.ALL_CONFIGS[configIndex] || window.ALL_CONFIGS[0];
    
    // Filter events based on active config
    if (window.ACTIVE_CONFIG.data && window.ACTIVE_CONFIG.data.source === 'real') {
        // Production: only real events (filter out demo events)
        window.ACTIVE_EVENTS = window.ALL_EVENTS.filter(e => !e.id.includes('demo_'));
    } else {
        // Development: all events
        window.ACTIVE_EVENTS = window.ALL_EVENTS;
    }
})();
'''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{app_name}</title>
<link rel="icon" href="{favicon}">
<style>{stylesheets['leaflet_css']}</style>
<style>{stylesheets['app_css']}</style>
<style>{stylesheets['time_drawer_css']}</style>
</head>
<body>
<div id="app">
<noscript>
<div style="max-width:1200px;margin:0 auto;padding:2rem;background:#1a1a1a;color:#fff">
<h1 style="color:#FF69B4">{app_name}</h1>
<p>Enable JavaScript to view events</p>
</div>
</noscript>
<div id="main-content" style="display:none">
<div id="filter-sentence">
<span id="event-count-text">0 events</span>
<span id="category-text" class="filter-part">in all categories</span>
<span id="time-text" class="filter-part">till sunrise</span>
<span id="distance-text" class="filter-part">within 5 km</span>
<span id="location-text" class="filter-part">from your location</span>
</div>
<div id="location-status"></div>
<div id="map"></div>
<div id="event-detail" class="hidden">
<div class="event-detail-content">
<button id="close-detail">&times;</button>
<h2 id="detail-title"></h2>
<p id="detail-description"></p>
<p><strong>Location:</strong> <span id="detail-location"></span></p>
<p><strong>Time:</strong> <span id="detail-time"></span></p>
<p><strong>Distance:</strong> <span id="detail-distance"></span></p>
<a id="detail-link" href="#" target="_blank">View Details</a>
</div>
</div>
</div>
<div id="env-watermark"></div>
</div>
<script>
// Embed all configurations and data
window.ALL_CONFIGS = {json.dumps(configs)};
window.ALL_EVENTS = {json.dumps(events)};
window.EMBEDDED_CONTENT_EN = {json.dumps(content_en)};
window.EMBEDDED_CONTENT_DE = {json.dumps(content_de)};

{config_loader}

// Intercept fetch calls to return embedded data
(function() {{
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
        if (url.includes('config.json')) {{
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve(window.ACTIVE_CONFIG)
            }});
        }}
        if (url.includes('events.json')) {{
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve({{events: window.ACTIVE_EVENTS}})
            }});
        }}
        if (url.includes('content.json')) {{
            const content = url.includes('.de.') ? window.EMBEDDED_CONTENT_DE : window.EMBEDDED_CONTENT_EN;
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve(content)
            }});
        }}
        return originalFetch.apply(this, arguments);
    }};
}})();

{scripts['leaflet_js']}
{scripts['i18n_js']}
{scripts['time_drawer_js']}
{scripts['app_js']}

document.getElementById('main-content').style.display = 'block';
</script>
</body>
</html>'''
        return html
    
    def generate_site(self) -> bool:
        """Generate complete static site with runtime configuration"""
        print("=" * 60)
        print("🔨 Generating Site")
        print("=" * 60)
        
        if not self.ensure_dependencies_present():
            return False
        
        print("\nLoading configurations...")
        configs = self.load_all_configs()
        
        print("Loading stylesheets...")
        stylesheets = self.load_stylesheet_resources()
        
        print("Loading scripts...")
        scripts = self.load_script_resources()
        
        print("Loading content data...")
        events = self.load_all_events()
        
        print("Loading translations...")
        content_en, content_de = self.load_translation_data()
        
        print(f"Building HTML ({len(events)} total events)...")
        html = self.build_html_structure(
            configs, events, content_en, content_de,
            stylesheets, scripts
        )
        
        output_file = self.static_path / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Site generated successfully!")
        print(f"   Output: {output_file}")
        print(f"   Size: {len(html) / 1024:.1f} KB")
        print(f"   Total events: {len(events)}")
        print(f"   Configs: {len(configs)} (runtime-selected)")
        print("\n" + "=" * 60)
        return True
    
    # ==================== Content Updates ====================
    
    def detect_embedded_config_count(self, html: str) -> int:
        """Detect how many configs are embedded in HTML"""
        marker = 'window.ALL_CONFIGS = '
        start = html.find(marker)
        if start == -1:
            return 0
        start += len(marker)
        end = html.find('];', start)
        if end == -1:
            return 0
        try:
            configs = json.loads(html[start:end+1])
            return len(configs) if isinstance(configs, list) else 0
        except:
            return 0
    
    def find_events_data_position(self, html: str) -> Tuple[int, int]:
        """Find position of events data in HTML"""
        marker = 'window.ALL_EVENTS = '
        start = html.find(marker)
        if start == -1:
            return -1, -1
        
        start += len(marker)
        end = html.find('];', start)
        return start, end
    
    def update_events_data(self) -> bool:
        """Update events data in existing HTML (fast update)"""
        print("=" * 60)
        print("⚡ Updating Events Data")
        print("=" * 60)
        
        html_file = self.static_path / 'index.html'
        if not html_file.exists():
            print("\n❌ Error: index.html not found")
            print("   Run: python3 src/main.py generate")
            return False
        
        print("\nReading existing HTML...")
        html = self.read_text_file(html_file)
        
        print("Loading current events...")
        events = self.load_all_events()
        
        print("Updating events data...")
        start, end = self.find_events_data_position(html)
        if start == -1 or end == -1:
            print("\n⚠️  Warning: Events data marker not found")
            return False
        
        new_html = html[:start] + json.dumps(events) + html[end:]
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        config_count = self.detect_embedded_config_count(html)
        
        print(f"\n✅ Events data updated!")
        print(f"   Output: {html_file}")
        print(f"   Events: {len(events)}")
        print(f"   Runtime configs: {config_count}")
        print("\n" + "=" * 60)
        return True
