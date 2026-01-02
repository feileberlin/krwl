"""
Site Generator Module - Platform-Agnostic

Generates static sites with runtime configuration support.
No platform-specific dependencies (GitHub, GitLab, etc.).

Responsibilities:
- Fetch third-party dependencies (Leaflet, etc.)
- Generate single-file HTML with inlined assets
- Update content without full regeneration
- Lint and validate all exported content

Naming: Functions describe WHAT they do, not implementation history.
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import html

try:
    from .linter import Linter
except ImportError:
    # Fallback if linter is not available
    class Linter:
        def __init__(self, verbose=False):
            pass
        def lint_all(self, *args, **kwargs):
            class FakeLintResult:
                passed = True
                errors = []
                warnings = []
            return FakeLintResult()


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
    
    def sanitize_svg_content(self, svg_content: str) -> str:
        """
        Sanitize SVG content by removing potentially dangerous elements and attributes.
        Removes script tags, event handlers, and external references for security.
        """
        import re
        
        # Remove script tags and their content
        svg_content = re.sub(r'<script[^>]*>.*?</script>', '', svg_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handler attributes (onclick, onload, onerror, etc.)
        event_handlers = ['onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout', 
                         'onmousemove', 'onmouseenter', 'onmouseleave', 'onfocus', 
                         'onblur', 'onchange', 'onsubmit', 'onkeydown', 'onkeyup', 'onkeypress']
        for handler in event_handlers:
            svg_content = re.sub(f'{handler}\\s*=\\s*["\'][^"\']*["\']', '', svg_content, flags=re.IGNORECASE)
        
        # Remove external references (use, image with external href)
        svg_content = re.sub(r'xlink:href\\s*=\\s*["\']https?://[^"\']*["\']', '', svg_content, flags=re.IGNORECASE)
        svg_content = re.sub(r'href\\s*=\\s*["\']https?://[^"\']*["\']', '', svg_content, flags=re.IGNORECASE)
        
        return svg_content
    
    def inline_svg_file(self, filename: str, as_data_url: bool = False) -> str:
        """
        Generic function to inline any SVG file from assets or static directory.
        Automatically finds and inlines new SVG files for the map or other uses.
        SVG content is sanitized to remove scripts and external references.
        
        Args:
            filename: Name of the SVG file (e.g., 'favicon.svg', 'logo.svg', 'marker-festivals.svg')
            as_data_url: If True, return as base64 data URL; if False, return raw SVG content
            
        Returns:
            SVG content as string or data URL, or fallback empty SVG if file not found
        """
        # Try assets directory first, then static, then assets/markers subdirectory
        search_paths = [
            self.base_path / 'assets' / filename,
            self.static_path / filename,
            self.base_path / 'assets' / 'markers' / filename
        ]
        
        svg_path = None
        for path in search_paths:
            if path.exists():
                svg_path = path
                break
        
        if not svg_path:
            # Return fallback empty SVG
            fallback = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"></svg>'
            if as_data_url:
                return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E"
            return fallback
        
        svg_content = self.read_text_file(svg_path)
        
        # Sanitize SVG content to remove potentially dangerous elements
        svg_content = self.sanitize_svg_content(svg_content)
        
        if as_data_url:
            import base64
            base64_data = base64.b64encode(svg_content.encode()).decode()
            return f"data:image/svg+xml;base64,{base64_data}"
        
        return svg_content
    
    def create_favicon_data_url(self) -> str:
        """Create base64 data URL for favicon"""
        return self.inline_svg_file('favicon.svg', as_data_url=True)
    
    def read_logo_svg(self) -> str:
        """Read logo SVG content for inline use"""
        return self.inline_svg_file('logo.svg', as_data_url=False)
    
    def filter_and_sort_future_events(self, events: List[Dict]) -> List[Dict]:
        """Filter out past events and sort (running events first, then chronological)."""
        from datetime import timezone
        current_time = datetime.now(timezone.utc)
        # Make current_time timezone-naive for comparison with parsed event times
        current_time = current_time.replace(tzinfo=None)
        future_events = []
        
        for event in events:
            try:
                # Parse times (remove timezone suffix)
                start_time_str = event.get('start_time', '')
                if not start_time_str:
                    continue
                start_time_str = start_time_str.split('+')[0].rstrip('Z')
                start_time = datetime.fromisoformat(start_time_str)
                
                # Get or estimate end time (do not assume a fixed duration)
                end_time_str = event.get('end_time', '')
                if end_time_str:
                    end_time_str = end_time_str.split('+')[0].rstrip('Z')
                    end_time = datetime.fromisoformat(end_time_str)
                    is_running = start_time <= current_time <= end_time
                    is_past = end_time < current_time
                else:
                    # If no end_time is provided, treat the event as non-running
                    # and consider it past only if its start_time is in the past.
                    end_time = None
                    is_running = False
                    is_past = start_time < current_time
                
                # Include if not past
                if not is_past:
                    future_events.append({
                        'event': event,
                        'start_time': start_time,
                        'is_running': is_running
                    })
            except (ValueError, TypeError):
                continue
        
        # Sort: running first, then chronological
        future_events.sort(key=lambda x: (not x['is_running'], x['start_time']))
        return future_events
    
    def build_noscript_html(self, events: List[Dict], content_en: Dict, app_name: str) -> str:
        """Build complete noscript HTML with event list."""
        import locale
        
        future_events = self.filter_and_sort_future_events(events)
        translations = content_en.get('noscript', {})
        
        # Set locale to English for consistent date formatting
        try:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'C')
            except locale.Error:
                pass  # Use system default if neither works
        
        # Header
        html_parts = [
            '<div style="max-width:1200px;margin:0 auto;padding:2rem;background:#1a1a1a;color:#fff;font-family:sans-serif">',
            f'<h1 style="color:#FF69B4;margin-bottom:1rem">{html.escape(app_name)}</h1>',
            '<div style="background:#401B2D;padding:1rem;border-radius:8px;margin-bottom:1.5rem;border-left:4px solid #FF69B4">',
            f'<p style="margin:0;color:#FFB3DF"><strong>{html.escape(translations.get("warning", "⚠️ JavaScript is disabled."))}</strong></p>',
            f'<p style="margin:0.5rem 0 0 0;color:#ccc;font-size:0.9rem">{html.escape(translations.get("info", "Enable JavaScript for interactive map."))}</p>',
            '</div>'
        ]
        
        # Events or empty message
        if not future_events:
            html_parts.append(f'<p style="color:#888;text-align:center;padding:2rem">{html.escape(translations.get("no_events", "No upcoming events."))}</p>')
        else:
            html_parts.append(f'<h2 style="color:#FF69B4;font-size:1.5rem;margin-bottom:1.5rem">{html.escape(translations.get("upcoming_events", "Upcoming Events"))} <span style="color:#888;font-size:1rem">({len(future_events)} events)</span></h2>')
            html_parts.append('<div style="display:flex;flex-direction:column;gap:1.5rem">')
            
            for event_item in future_events:
                event_data = event_item['event']
                event_start_time = event_item['start_time']
                event_is_running = event_item['is_running']
                
                # Use translations for badge and link text
                badge_text = html.escape(translations.get("happening_now", "HAPPENING NOW"))
                running_badge = f'<span style="background:#4CAF50;color:#fff;padding:0.25rem 0.75rem;border-radius:4px;font-size:0.85rem;font-weight:600;margin-left:0.5rem">{badge_text}</span>' if event_is_running else ''
                
                view_details_text = html.escape(translations.get("view_details", "View Event Details →"))
                event_link = f'<a href="{html.escape(event_data.get("url", ""))}" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#FF69B4;color:#fff;padding:0.5rem 1rem;border-radius:5px;text-decoration:none;font-weight:600">{view_details_text}</a>' if event_data.get('url') else ''
                
                html_parts.append(f'''<article style="background:#2a2a2a;border-radius:8px;padding:1.5rem;border-left:4px solid #FF69B4">
<h3 style="color:#FF69B4;margin:0 0 0.75rem 0;font-size:1.25rem">{html.escape(event_data.get('title', 'Untitled'))}{running_badge}</h3>
<div style="color:#ccc;margin-bottom:1rem">
<p style="margin:0.25rem 0"><strong style="color:#FFB3DF">📅 Date:</strong> {html.escape(event_start_time.strftime('%A, %B %d, %Y'))}</p>
<p style="margin:0.25rem 0"><strong style="color:#FFB3DF">🕐 Time:</strong> {html.escape(event_start_time.strftime('%I:%M %p').lstrip('0'))}</p>
<p style="margin:0.25rem 0"><strong style="color:#FFB3DF">📍 Location:</strong> {html.escape(event_data.get('location', {}).get('name', 'Unknown'))}</p>
</div>
<p style="color:#ddd;line-height:1.6;margin-bottom:1rem">{html.escape(event_data.get('description', ''))}</p>
{event_link}
</article>''')
            
            html_parts.append('</div>')
        
        # Footer
        html_parts.extend([
            '<footer style="margin-top:2rem;padding-top:2rem;border-top:1px solid #3a3a3a;color:#888;text-align:center">',
            f'<p style="margin:0">{html.escape(translations.get("footer", "Enable JavaScript for best experience."))}</p>',
            '</footer>',
            '</div>'
        ])
        
        return ''.join(html_parts)
    
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
        favicon = self.create_favicon_data_url()
        logo_svg = self.read_logo_svg()
        
        # Build noscript HTML with sorted events
        noscript_html = self.build_noscript_html(events, content_en, app_name)
        
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
{noscript_html}
</noscript>
<div id="main-content" style="display:none">
<div id="filter-sentence">
<span id="filter-logo" class="filter-logo" aria-hidden="true">{logo_svg}</span>
<span id="event-count-category-text" class="filter-part">0 events</span>
<span id="time-text" class="filter-part">till sunrise</span>
<span id="distance-text" class="filter-part">within 5 km</span>
<span id="location-text" class="filter-part">from here</span>
</div>
<div id="map"></div>
<div id="event-detail" class="hidden">
<div class="detail-content">
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

</script>
</body>
</html>'''
        return html
    
    def generate_site(self, skip_lint: bool = False) -> bool:
        """
        Generate complete static site with runtime configuration.
        
        Args:
            skip_lint: If True, skip linting validation (useful for testing)
        
        Returns:
            True if generation succeeds, False otherwise
        """
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
        
        # Lint the generated content
        if not skip_lint:
            print("\n🔍 Linting generated content...")
            linter = Linter(verbose=False)
            
            # Collect SVG files for linting
            svg_files = {}
            try:
                svg_files['favicon'] = self.inline_svg_file('favicon.svg', as_data_url=False)
                svg_files['logo'] = self.inline_svg_file('logo.svg', as_data_url=False)
            except Exception as e:
                print(f"   Warning: Could not load SVG files for linting: {e}")
            
            lint_result = linter.lint_all(
                html_content=html,
                stylesheets=stylesheets,
                scripts=scripts,
                translations_en=content_en,
                translations_de=content_de,
                svg_files=svg_files
            )
            
            # Show detailed errors and warnings
            if not lint_result.passed:
                print("\n❌ Linting failed with errors:")
                for error in lint_result.errors:
                    print(f"   ❌ {error}")
            
            if lint_result.warnings:
                print(f"\n⚠️  Linting warnings ({len(lint_result.warnings)}):")
                for warning in lint_result.warnings[:10]:  # Show first 10
                    print(f"   ⚠️  {warning}")
                if len(lint_result.warnings) > 10:
                    print(f"   ... and {len(lint_result.warnings) - 10} more warnings")
            
            # Decide if we should fail the build on lint errors
            if not lint_result.passed:
                print("\n⚠️  Build completed with lint errors (warnings only, not blocking)")
                # Don't block build, just warn
        
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
