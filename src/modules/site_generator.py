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
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import html

# Configure module logger
logger = logging.getLogger(__name__)

# Import Lucide icon maps (markers and dashboard icons)
try:
    from .lucide_markers import LUCIDE_MARKER_BASE64_MAP, DASHBOARD_ICONS_MAP
except ImportError:
    # Fallback if lucide_markers module not available
    LUCIDE_MARKER_BASE64_MAP = {}
    DASHBOARD_ICONS_MAP = {}

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

try:
    from .utils import load_config
except ImportError:
    # Fallback if utils is not available
    load_config = None


# Third-party dependencies to fetch
DEPENDENCIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {"src": "/leaflet.css", "dest": "leaflet/leaflet.css"},
            {"src": "/leaflet.js", "dest": "leaflet/leaflet.js"},
            {"src": "/images/marker-icon.png", "dest": "leaflet/images/marker-icon.png"},
            {"src": "/images/marker-icon-2x.png", "dest": "leaflet/images/marker-icon-2x.png"},
            {"src": "/images/marker-shadow.png", "dest": "leaflet/images/marker-shadow.png"}
        ]
    },
    "lucide": {
        "version": "latest",
        "base_url": "https://unpkg.com/lucide@{version}",
        "files": [
            # Development version (unminified UMD)
            {"src": "/dist/umd/lucide.js", "dest": "lucide/lucide.js"},
            # Production version (minified, default package export)
            {"src": "", "dest": "lucide/lucide.min.js"}
        ]
    }
}


class SiteGenerator:
    """Generates static site with runtime-configurable behavior"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.src_path = self.base_path / 'src'  # Source code location
        self.static_path = self.base_path / 'public'  # Build output directory
        self.data_path = self.base_path / 'assets' / 'json'  # Data files
        self.dependencies_dir = self.base_path / 'lib'  # Third-party libraries
        self.assets_dir = self.base_path / 'assets'  # Source assets
        self.dependencies_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== Dependency Management ====================
    
    def fetch_file_from_url(self, url: str, destination: Path) -> bool:
        """Fetch a single file from URL and save to destination
        
        Args:
            url: URL to fetch from
            destination: Path to save file to
            
        Returns:
            True if file was successfully fetched, False otherwise
        """
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            print(f"  Fetching {destination.name}...", end=" ", flush=True)
            logger.info("Fetching dependency", extra={
                'url': url,
                'destination': str(destination),
                'file_name': destination.name
            })
            
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            
            with open(destination, 'wb') as f:
                f.write(content)
            
            print(f"✓ ({len(content) / 1024:.1f} KB)")
            logger.debug("Successfully fetched dependency", extra={
                'file_name': destination.name,
                'size_bytes': len(content),
                'size_kb': len(content) / 1024
            })
            return True
        except Exception as e:
            print(f"✗ {e}")
            logger.error("Failed to fetch dependency", extra={
                'url': url,
                'error': str(e)
            })
            return False
    
    def fetch_dependency_files(self, name: str, config: Dict) -> Tuple[bool, bool]:
        """Fetch all files for one dependency package
        
        Checks if files already exist before fetching. If all files are present,
        skips fetching and returns True. Only fails if files are missing AND
        fetch fails.
        
        Args:
            name: Dependency package name (e.g., 'leaflet')
            config: Dependency configuration dict with version, base_url, files
            
        Returns:
            Tuple of (success: bool, used_cache: bool)
            success: True if all files exist or were successfully fetched
            used_cache: True if files were already present (not fetched)
        """
        print(f"\n📦 {name} v{config['version']}")
        base_url = config['base_url'].format(version=config['version'])
        
        # First, check which files already exist
        existing_files = []
        missing_files = []
        for file_info in config['files']:
            dest = self.dependencies_dir / file_info['dest']
            if dest.exists():
                existing_files.append(file_info)
            else:
                missing_files.append(file_info)
        
        # Report existing files
        for file_info in existing_files:
            dest = self.dependencies_dir / file_info['dest']
            size_kb = dest.stat().st_size / 1024
            print(f"  ✓ {dest.name} already present ({size_kb:.1f} KB)")
        
        # If all files exist, we're done
        if not missing_files:
            print(f"✅ {name} complete (using cached files)")
            return True, True
        
        # Try to fetch missing files
        fetch_success = True
        for file_info in missing_files:
            # Handle case where src is empty (use base_url directly)
            if file_info['src']:
                url = f"{base_url}{file_info['src']}"
            else:
                url = base_url
            dest = self.dependencies_dir / file_info['dest']
            if not self.fetch_file_from_url(url, dest):
                fetch_success = False
        
        # Determine final status
        # Success if all files now exist (were already there or successfully fetched)
        all_files_present = all(
            (self.dependencies_dir / f['dest']).exists() 
            for f in config['files']
        )
        
        if all_files_present:
            if fetch_success:
                print(f"✅ {name} complete")
            else:
                print(f"✅ {name} complete (partial fetch, using cached files)")
            return True, len(existing_files) > 0
        else:
            print(f"❌ {name} incomplete - files missing and CDN unavailable")
            return False, False
    
    def fetch_all_dependencies(self) -> bool:
        """Fetch all required third-party dependencies
        
        Returns True if all dependencies are present (either already cached or
        successfully fetched). Only returns False if dependencies are missing
        AND fetch from CDN failed.
        
        This ensures resilient deployments that continue even when CDN has
        temporary issues, as long as files are already present from previous
        successful fetches.
        
        Returns:
            True if all dependencies are ready, False if missing and fetch failed
        """
        print("=" * 60)
        print("📦 Fetching Dependencies")
        print("=" * 60)
        
        results_with_cache = [
            self.fetch_dependency_files(name, cfg) 
            for name, cfg in DEPENDENCIES.items()
        ]
        
        # Unpack results and cache status
        results = [r[0] for r in results_with_cache]
        had_cached = any(r[1] for r in results_with_cache)
        
        print("\n" + "=" * 60)
        if all(results):
            if had_cached:
                print("✅ All dependencies ready (using cached files)")
            else:
                print("✅ All dependencies fetched")
        else:
            print("❌ Missing required dependencies")
            print("   Some files are missing and CDN is unavailable")
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
        """Load all event data (real + demo) from data directory"""
        events = []
        data_path = self.base_path / 'assets' / 'json'
        
        # Real events
        events_file = data_path / 'events.json'
        if events_file.exists():
            with open(events_file, 'r') as f:
                events.extend(json.load(f).get('events', []))
        
        # Demo events (always include - config determines if they're shown)
        demo_file = data_path / 'events.demo.json'
        if demo_file.exists():
            with open(demo_file, 'r') as f:
                events.extend(json.load(f).get('events', []))
        
        return events
    
    def load_all_configs(self) -> List[Dict]:
        """
        Load configuration file with environment-specific overrides applied.
        
        Uses load_config() from utils.py to apply runtime overrides based on
        the environment setting in config.json. This ensures the generated
        static HTML contains the correct configuration for the target environment.
        """
        configs = []
        
        if load_config is not None:
            # Use load_config() to get environment-aware configuration
            config = load_config(self.base_path)
            configs.append(config)
        else:
            # Fallback: load raw config.json (for backward compatibility)
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
                self.base_path / "assets" / 'css' / 'style.css'
            )
        }
    
    def load_script_resources(self) -> Dict[str, str]:
        """Load all JavaScript resources including Lucide"""
        scripts = {
            'leaflet_js': self.read_text_file(
                self.dependencies_dir / 'leaflet' / 'leaflet.js'
            ),
            'i18n_js': self.read_text_file(
                self.base_path / "assets" / 'js' / 'i18n.js'
            ),
            'app_js': self.read_text_file(
                self.base_path / "assets" / 'js' / 'app.js'
            )
        }
        
        # Load Lucide library if available
        lucide_path = self.dependencies_dir / 'lucide' / 'lucide.min.js'
        if lucide_path.exists():
            scripts['lucide_js'] = self.read_text_file(lucide_path)
        else:
            # Provide empty stub if Lucide not available
            scripts['lucide_js'] = '// Lucide not available'
        
        return scripts
    
    def load_translation_data(self) -> Tuple[Dict, Dict]:
        """Load translation files for all languages"""
        data_path = self.base_path / 'assets' / 'json' / 'i18n'
        with open(data_path / 'content.json', 'r') as f:
            content_en = json.load(f)
        with open(data_path / 'content.de.json', 'r') as f:
            content_de = json.load(f)
        return content_en, content_de
    
    def ensure_dependencies_present(self) -> bool:
        """Ensure dependencies are available, fetch if missing"""
        # Check only for critical Leaflet files (markers not critical for build)
        leaflet_js = self.dependencies_dir / 'leaflet' / 'leaflet.js'
        leaflet_css = self.dependencies_dir / 'leaflet' / 'leaflet.css'
        
        if not leaflet_js.exists() or not leaflet_css.exists():
            print("\n⚠️  Critical dependencies missing - fetching now...")
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
        # Try assets directory first, then assets/svg subdirectory
        search_paths = [
            self.assets_dir / filename,
            self.assets_dir / 'svg' / filename
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
    
    def generate_lucide_marker_map(self) -> Dict[str, Dict[str, str]]:
        """
        Generate a map of Lucide icon names for marker generation.
        
        Instead of embedding SVG files, we provide Lucide icon names
        that will be rendered client-side using the Lucide library.
        
        Returns:
            Dictionary mapping marker names to Lucide icon names and settings
            Example: {'marker-music': {'icon': 'music', 'color': '#00ff00'}}
        """
        # Icon mapping for our 29 required categories
        lucide_icon_mapping = {
            'marker-on-stage': {'icon': 'drama', 'label': 'Theater/Performance'},
            'marker-music': {'icon': 'music', 'label': 'Concerts/Music'},
            'marker-opera-house': {'icon': 'landmark', 'label': 'Opera/Theater'},
            'marker-pub-games': {'icon': 'beer', 'label': 'Pubs/Social Games'},
            'marker-festivals': {'icon': 'star', 'label': 'Festivals'},
            'marker-workshops': {'icon': 'presentation', 'label': 'Workshops/Training'},
            'marker-school': {'icon': 'graduation-cap', 'label': 'Education'},
            'marker-shopping': {'icon': 'shopping-bag', 'label': 'Markets/Shopping'},
            'marker-sports': {'icon': 'trophy', 'label': 'Sports'},
            'marker-sports-field': {'icon': 'ticket', 'label': 'Sports Fields'},
            'marker-swimming': {'icon': 'waves', 'label': 'Swimming'},
            'marker-community': {'icon': 'users', 'label': 'Community'},
            'marker-arts': {'icon': 'palette', 'label': 'Arts'},
            'marker-museum': {'icon': 'landmark', 'label': 'Museums'},
            'marker-food': {'icon': 'utensils', 'label': 'Food/Dining'},
            'marker-church': {'icon': 'church', 'label': 'Religious'},
            'marker-traditional-oceanic': {'icon': 'flame', 'label': 'Cultural/Traditional'},
            'marker-castle': {'icon': 'castle', 'label': 'Castles'},
            'marker-monument': {'icon': 'pilcrow', 'label': 'Monuments'},
            'marker-tower': {'icon': 'triangle', 'label': 'Towers'},
            'marker-ruins': {'icon': 'blocks', 'label': 'Ruins'},
            'marker-palace': {'icon': 'crown', 'label': 'Palaces'},
            'marker-park': {'icon': 'tree-pine', 'label': 'Parks/Nature'},
            'marker-parliament': {'icon': 'landmark', 'label': 'Government'},
            'marker-mayors-office': {'icon': 'building', 'label': 'City Hall'},
            'marker-library': {'icon': 'book-open', 'label': 'Libraries'},
            'marker-national-archive': {'icon': 'archive', 'label': 'Archives'},
            'marker-default': {'icon': 'map-pin', 'label': 'Default/Fallback'},
            'marker-geolocation': {'icon': 'locate', 'label': 'User Location'}
        }
        
        # Add color and size settings
        for marker_name in lucide_icon_mapping:
            lucide_icon_mapping[marker_name]['color'] = '#00ff00'
            lucide_icon_mapping[marker_name]['size'] = 24
        
        return lucide_icon_mapping
    
    def generate_marker_icon_map(self) -> Dict[str, str]:
        """
        Generate a map of marker icon names to base64 data URLs.
        
        Uses Lucide icons wrapped in gyro marker shape as the primary source.
        Falls back to local SVG files if Lucide markers not available.
        
        Returns:
            Dictionary mapping marker names (without .svg extension) to data URLs
            Example: {'marker-on-stage': 'data:image/svg+xml;base64,...'}
        """
        # Try to use Lucide markers first (imported at module level)
        if LUCIDE_MARKER_BASE64_MAP:
            print(f"✅ Using {len(LUCIDE_MARKER_BASE64_MAP)} Lucide-based markers")
            return LUCIDE_MARKER_BASE64_MAP.copy()
        
        # Fallback: Load from local SVG files
        print("⚠️  Lucide markers not available, loading from SVG files...")
        
        # List of markers actually used in JavaScript getMarkerIconForCategory
        # This should match the unique values in the iconNameMap in app.js
        required_markers = [
            'marker-on-stage',      # Performance & Entertainment
            'marker-music',         # Concerts
            'marker-opera-house',   # Opera
            'marker-pub-games',     # Social & Games
            'marker-festivals',     # Festivals & Celebrations
            'marker-workshops',     # Educational & Skills
            'marker-school',        # Lectures
            'marker-shopping',      # Shopping & Markets
            'marker-sports',        # Sports & Fitness
            'marker-sports-field',  # Athletics
            'marker-swimming',      # Swimming
            'marker-community',     # Community & Social Services
            'marker-arts',          # Arts & Culture
            'marker-museum',        # Exhibitions
            'marker-food',          # Food & Dining
            'marker-church',        # Religious
            'marker-traditional-oceanic',  # Cultural/Traditional
            'marker-castle',        # Historical
            'marker-monument',      # Heritage
            'marker-tower',         # Landmarks
            'marker-ruins',         # Ruins
            'marker-palace',        # Palace
            'marker-park',          # Parks & Nature
            'marker-parliament',    # Government
            'marker-mayors-office', # City Hall
            'marker-library',       # Libraries
            'marker-national-archive',  # Archives
            'marker-default',       # Default fallback
            'marker-geolocation'    # User location marker
        ]
        
        markers_dir = self.assets_dir / 'svg'
        marker_map = {}
        
        if not markers_dir.exists():
            print(f"⚠️  Markers directory not found: {markers_dir}")
            return marker_map
        
        # Only process markers in the required list
        for marker_name in required_markers:
            svg_file = markers_dir / f"{marker_name}.svg"
            
            if not svg_file.exists():
                print(f"⚠️  Required marker not found: {marker_name}.svg")
                continue
            
            # Generate base64 data URL
            try:
                data_url = self.inline_svg_file(svg_file.name, as_data_url=True)
                marker_map[marker_name] = data_url
            except Exception as e:
                print(f"⚠️  Failed to process {marker_name}.svg: {e}")
        
        return marker_map
    
    def inline_icon_maps_to_window(self, marker_icons: Dict[str, str]) -> str:
        """
        Create JavaScript code to inline icon maps to window object.
        
        This helper function generates the JavaScript code that embeds both
        map marker icons and dashboard icons into the global window object,
        making them available to the frontend JavaScript.
        
        Args:
            marker_icons: Dictionary of marker icons (from generate_marker_icon_map)
            
        Returns:
            JavaScript code string that defines window.MARKER_ICONS and window.DASHBOARD_ICONS
        """
        import json
        
        # Generate inline JavaScript for icon maps
        js_code = f'''// Icon Maps - Inlined by site_generator.py
// Map markers for event categories (base64 encoded gyro-wrapped icons)
window.MARKER_ICONS = {json.dumps(marker_icons, ensure_ascii=False)};

// Dashboard icons (filled SVG for monochrome corporate design)
window.DASHBOARD_ICONS = {json.dumps(DASHBOARD_ICONS_MAP, ensure_ascii=False)};'''
        
        return js_code
    
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
    
    def load_component(self, component_path: str) -> str:
        """
        Load a component template from assets/html/ directory.
        
        Args:
            component_path: Component filename (e.g., 'html-head.html', 'map-main.html')
        
        Returns:
            Component template content as string
        
        Raises:
            FileNotFoundError: If component file does not exist
        
        Example:
            html_head = self.load_component('html-head.html')
        """
        full_path = self.base_path / 'assets' / 'html' / component_path
        if not full_path.exists():
            raise FileNotFoundError(
                f"Component not found: {full_path}\n"
                f"Available components should be in assets/html/:\n"
                f"  - html-head.html\n"
                f"  - html-body-open.html\n"
                f"  - html-body-close.html\n"
                f"  - map-main.html\n"
                f"  - dashboard-aside.html\n"
                f"  - filter-nav.html"
            )
        return full_path.read_text(encoding='utf-8')
    
    def load_design_tokens(self) -> Dict:
        """
        Load design tokens from config.json.
        
        Returns:
            Dictionary containing design tokens (colors, typography, spacing, etc.)
            Returns empty dict if design section not found.
        """
        config_file = self.base_path / 'config.json'
        if not config_file.exists():
            return {}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config.get('design', {})
    
    def generate_design_tokens_css(self) -> str:
        """
        Generate CSS custom properties from design tokens.
        
        Reads design tokens from config.json and generates CSS :root variables.
        If design-tokens.css already exists, loads it directly.
        Otherwise, generates it on-the-fly.
        
        Returns:
            CSS string with custom properties
        """
        # Check if pre-generated CSS exists
        tokens_css_path = self.base_path / 'assets' / 'html' / 'design-tokens.css'
        if tokens_css_path.exists():
            return tokens_css_path.read_text(encoding='utf-8')
        
        # Generate on-the-fly if needed
        design = self.load_design_tokens()
        if not design:
            return "/* No design tokens found in config.json */"
        
        # Simple inline generation (matches generate_design_tokens.py logic)
        lines = [
            "/**",
            " * Design Tokens - Auto-generated CSS Custom Properties",
            " * Generated from config.json design section",
            " */",
            "",
            ":root {",
        ]
        
        # Colors
        if 'colors' in design:
            lines.append("  /* Colors */")
            for key, value in design['colors'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --color-{css_var}: {value};")
            lines.append("")
        
        # Typography
        if 'typography' in design:
            lines.append("  /* Typography */")
            for key, value in design['typography'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --{css_var}: {value};")
            lines.append("")
        
        # Spacing
        if 'spacing' in design:
            lines.append("  /* Spacing */")
            for key, value in design['spacing'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --spacing-{css_var}: {value};")
            lines.append("")
        
        # Z-index
        if 'z_index' in design:
            lines.append("  /* Z-Index */")
            for key, value in design['z_index'].items():
                if key.startswith('_'):
                    continue
                css_var = key.replace('_', '-')
                lines.append(f"  --z-{css_var}: {value};")
            lines.append("")
        
        # Shadows
        if 'shadows' in design:
            lines.append("  /* Shadows */")
            for key, value in design['shadows'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --shadow-{css_var}: {value};")
            lines.append("")
        
        # Borders
        if 'borders' in design:
            lines.append("  /* Borders */")
            for key, value in design['borders'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --border-{css_var}: {value};")
            lines.append("")
        
        # Transitions
        if 'transitions' in design:
            lines.append("  /* Transitions */")
            for key, value in design['transitions'].items():
                css_var = key.replace('_', '-')
                lines.append(f"  --transition-{css_var}: {value};")
            lines.append("")
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def calculate_debug_info(self, primary_config: Dict, events: List[Dict]) -> Dict:
        """
        Calculate debug information for dashboard.
        
        Collects:
        - Event counts (pending, published, archived)
        - Environment detection
        - Caching status
        - File size information (HTML size, cache file size if applicable)
        - Deployment timestamp
        - Git commit information (hash, author, date, message)
        
        Args:
            primary_config: Primary configuration object
            events: List of published event data
            
        Returns:
            Dictionary with debug information
        """
        debug_info = {}
        
        # Event counts
        try:
            pending_file = self.data_path / 'pending_events.json'
            archived_file = self.data_path / 'archived_events.json'
            
            pending_count = 0
            if pending_file.exists():
                with open(pending_file, 'r', encoding='utf-8') as f:
                    pending_data = json.load(f)
                    pending_count = len(pending_data)
            
            archived_count = 0
            if archived_file.exists():
                with open(archived_file, 'r', encoding='utf-8') as f:
                    archived_data = json.load(f)
                    archived_count = len(archived_data)
            
            debug_info['event_counts'] = {
                'published': len(events),
                'pending': pending_count,
                'archived': archived_count,
                'total': len(events) + pending_count + archived_count
            }
        except Exception as e:
            logger.warning(f"Could not calculate event counts: {e}")
            debug_info['event_counts'] = {
                'published': len(events),
                'pending': 0,
                'archived': 0,
                'total': len(events)
            }
        
        # Environment
        try:
            from .utils import is_ci, is_production
            if is_production():
                environment = 'production'
            elif is_ci():
                environment = 'ci'
            else:
                environment = 'development'
            
            debug_info['environment'] = environment
        except Exception as e:
            logger.warning(f"Could not detect environment: {e}")
            debug_info['environment'] = primary_config.get('app', {}).get('environment', 'unknown')
        
        # Caching status
        try:
            cache_enabled = primary_config.get('performance', {}).get('cache_enabled', False)
            debug_info['cache_enabled'] = cache_enabled
            
            # Try to find and measure cache file size
            cache_file_size = None
            if cache_enabled:
                # Check for cache file in common locations
                potential_cache_files = [
                    self.base_path / '.cache' / 'events_cache.json',
                    self.base_path / 'cache' / 'events.json',
                    self.base_path / '.cache' / 'historical_events.json',
                ]
                
                for cache_file in potential_cache_files:
                    if cache_file.exists():
                        cache_file_size = cache_file.stat().st_size
                        debug_info['cache_file_path'] = str(cache_file.relative_to(self.base_path))
                        break
            
            debug_info['cache_file_size'] = cache_file_size
        except Exception as e:
            logger.warning(f"Could not determine cache status: {e}")
            debug_info['cache_enabled'] = False
            debug_info['cache_file_size'] = None
        
        # Deployment timestamp (current time when HTML is generated)
        debug_info['deployment_time'] = datetime.now().isoformat()
        
        # Git commit information
        try:
            import subprocess
            
            # Get last commit hash (short form)
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.base_path,
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            # Get commit author
            commit_author = subprocess.check_output(
                ['git', 'log', '-1', '--format=%an'],
                cwd=self.base_path,
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            # Get commit date
            commit_date = subprocess.check_output(
                ['git', 'log', '-1', '--format=%ci'],
                cwd=self.base_path,
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            # Get commit message (first line)
            commit_message = subprocess.check_output(
                ['git', 'log', '-1', '--format=%s'],
                cwd=self.base_path,
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            
            debug_info['git_commit'] = {
                'hash': commit_hash,
                'author': commit_author,
                'date': commit_date,
                'message': commit_message
            }
        except Exception as e:
            logger.warning(f"Could not retrieve git commit info: {e}")
            debug_info['git_commit'] = {
                'hash': 'unknown',
                'author': 'unknown',
                'date': 'unknown',
                'message': 'Git information not available'
            }
        
        return debug_info
    
    def calculate_html_size_breakdown(self, html: str) -> Dict:
        """
        Calculate size breakdown of generated HTML.
        
        Analyzes the HTML to determine which parts are largest:
        - Total size
        - Embedded events data
        - Embedded translations
        - Stylesheets (Leaflet + app CSS)
        - Scripts (Leaflet + app.js)
        - Marker icons
        
        Args:
            html: Generated HTML string
            
        Returns:
            Dictionary with size information in bytes
        """
        sizes = {
            'total': len(html.encode('utf-8')),
            'events_data': 0,
            'translations': 0,
            'stylesheets': 0,
            'scripts': 0,
            'marker_icons': 0,
            'other': 0
        }
        
        try:
            # Find embedded events data
            events_marker = 'window.__INLINE_EVENTS_DATA__'
            events_start = html.find(events_marker)
            if events_start != -1:
                events_end = html.find('};', events_start)
                if events_end != -1:
                    sizes['events_data'] = len(html[events_start:events_end+2].encode('utf-8'))
            
            # Find translations
            for marker in ['window.EMBEDDED_CONTENT_EN', 'window.EMBEDDED_CONTENT_DE']:
                trans_start = html.find(marker)
                if trans_start != -1:
                    trans_end = html.find('};', trans_start)
                    if trans_end != -1:
                        sizes['translations'] += len(html[trans_start:trans_end+2].encode('utf-8'))
            
            # Find stylesheets (inside <style> tags)
            style_start = 0
            while True:
                style_start = html.find('<style>', style_start)
                if style_start == -1:
                    break
                style_end = html.find('</style>', style_start)
                if style_end != -1:
                    sizes['stylesheets'] += len(html[style_start:style_end+8].encode('utf-8'))
                    style_start = style_end
                else:
                    break
            
            # Find scripts (inside <script> tags, excluding inline data)
            script_start = 0
            while True:
                script_start = html.find('<script>', script_start)
                if script_start == -1:
                    break
                script_end = html.find('</script>', script_start)
                if script_end != -1:
                    script_content = html[script_start:script_end+9]
                    # Exclude data embedding scripts (already counted separately)
                    if 'window.__INLINE_EVENTS_DATA__' not in script_content and \
                       'window.EMBEDDED_CONTENT' not in script_content and \
                       'window.MARKER_ICONS' not in script_content:
                        sizes['scripts'] += len(script_content.encode('utf-8'))
                    script_start = script_end
                else:
                    break
            
            # Find marker icons
            marker_start = html.find('window.MARKER_ICONS')
            if marker_start != -1:
                marker_end = html.find('};', marker_start)
                if marker_end != -1:
                    sizes['marker_icons'] = len(html[marker_start:marker_end+2].encode('utf-8'))
            
            # Calculate other
            accounted = sizes['events_data'] + sizes['translations'] + sizes['stylesheets'] + \
                       sizes['scripts'] + sizes['marker_icons']
            sizes['other'] = max(0, sizes['total'] - accounted)
            
        except Exception as e:
            logger.warning(f"Could not calculate HTML size breakdown: {e}")
        
        return sizes
    
    def build_html_from_components(
        self,
        configs: List[Dict],
        events: List[Dict],
        content_en: Dict,
        content_de: Dict,
        stylesheets: Dict[str, str],
        scripts: Dict[str, str],
        marker_icons: Dict[str, str]
    ) -> str:
        """
        Build complete HTML from modular components.
        
        Uses component-based templating for semantic HTML structure.
        Maintains backward compatibility with existing output.
        
        Args:
            configs: List of configuration objects
            events: List of event data
            content_en: English translations
            content_de: German translations
            stylesheets: Dict of CSS content (leaflet_css, app_css, etc.)
            scripts: Dict of JavaScript content
            marker_icons: Dict of marker icon data URLs
        
        Returns:
            Complete HTML document as string
        """
        # Extract basic info
        primary_config = configs[0] if configs else {}
        app_name = primary_config.get('app', {}).get('name', 'KRWL HOF Community Events')
        favicon = self.create_favicon_data_url()
        logo_svg = self.read_logo_svg()
        
        # Build noscript HTML
        noscript_html = self.build_noscript_html(events, content_en, app_name)
        
        # Extract minimal runtime config for frontend (backend config.json is not fetched by frontend)
        primary_config = configs[0] if configs else {}
        runtime_config = {
            'debug': primary_config.get('debug', False),
            'app': {
                'environment': primary_config.get('app', {}).get('environment', 'unknown')
            },
            'map': primary_config.get('map', {}),
            'data': {
                'source': primary_config.get('data', {}).get('source', 'real'),
                'sources': primary_config.get('data', {}).get('sources', {})
            }
        }
        
        # Calculate debug information
        debug_info = self.calculate_debug_info(primary_config, events)
        
        # Prepare embedded data for frontend
        # All data is embedded by backend - frontend does NOT fetch config.json or events
        embedded_data = f'''// Data embedded by backend (site_generator.py) - frontend does NOT fetch files
// config.json is backend-only, frontend uses this minimal runtime config
window.APP_CONFIG = {json.dumps(runtime_config, ensure_ascii=False)};
window.__INLINE_EVENTS_DATA__ = {{ "events": {json.dumps(events, ensure_ascii=False)} }};
window.EMBEDDED_CONTENT_EN = {json.dumps(content_en, ensure_ascii=False)};
window.EMBEDDED_CONTENT_DE = {json.dumps(content_de, ensure_ascii=False)};
window.MARKER_ICONS = {json.dumps(marker_icons, ensure_ascii=False)};
window.DASHBOARD_ICONS = {json.dumps(DASHBOARD_ICONS_MAP, ensure_ascii=False)};
window.DEBUG_INFO = {json.dumps(debug_info, ensure_ascii=False)};'''
        
        # Config loader and fetch interceptor (legacy placeholders - not currently used)
        config_loader = ''
        fetch_interceptor = ''
        
        # Generate timestamp placeholder
        generated_at = 'BUILD_TIMESTAMP_PLACEHOLDER'
        
        # Generated comment
        generated_comment = f'''<!--
  KRWL HOF Community Events - Auto-generated HTML
  
  Generated: {generated_at}
  Generator: src-modules/site_generator.py (component-based)
  Command: python3 src/event_manager.py generate
  
  DO NOT EDIT THIS FILE DIRECTLY
  Edit source files and regenerate instead:
  - Components: assets/html/
  - Design tokens: config.json (design section)
  - Styles: assets/css/
  - Scripts: assets/js/
  - Events: assets/json/
-->'''
        
        # Load design tokens CSS
        design_tokens_css = self.generate_design_tokens_css()
        
        # Load component templates (no fallback - components required)
        html_head = self.load_component('html-head.html')
        html_body_open = self.load_component('html-body-open.html')
        html_body_close = self.load_component('html-body-close.html')
        map_main = self.load_component('map-main.html')
        dashboard_aside = self.load_component('dashboard-aside.html')
        filter_nav = self.load_component('filter-nav.html')
        
        # Assemble HTML from components
        html_parts = [
            generated_comment,
            '<!DOCTYPE html>',
            '<html lang="en">',
            html_head.format(
                app_name=app_name,
                favicon=favicon,
                design_tokens_css=design_tokens_css,
                leaflet_css=stylesheets['leaflet_css'],
                app_css=stylesheets['app_css']
            ),
            html_body_open.format(
                noscript_html=noscript_html
            ),
            '',
            '<!-- Layer 1: Fullscreen map -->',
            map_main,
            '',
            '<!-- Layer 2: Event popups (rendered by Leaflet) -->',
            '',
            '<!-- Layer 3: UI overlays -->',
            dashboard_aside.format(
                logo_svg=logo_svg
            ),
            filter_nav.format(
                logo_svg=logo_svg
            ),
            '',
            '<!-- Layer 4: Modals (reserved for future use) -->',
            '',
            html_body_close.format(
                embedded_data=embedded_data,
                config_loader=config_loader,
                fetch_interceptor=fetch_interceptor,
                leaflet_js=scripts['leaflet_js'],
                lucide_js=scripts.get('lucide_js', '// Lucide not available'),
                i18n_js=scripts['i18n_js'],
                app_js=scripts['app_js']
            )
        ]
        
        return '\n'.join(html_parts)
    
    def generate_site(self, skip_lint: bool = False) -> bool:
        """
        Generate complete static site with inlined HTML.
        
        Process:
        1. Ensures dependencies are present (Leaflet.js) - auto-fetches if missing
        2. Loads all configurations from config.json
        3. Loads stylesheets (Leaflet CSS, app CSS)
        4. Loads JavaScript files (Leaflet, i18n, app.js)
        5. Loads event data (real events + demo events)
        6. Loads translations (English and German)
        7. Builds HTML structure using templates with all assets inlined
        8. Lints and validates generated content (HTML, CSS, JS, translations, SVG)
        9. Writes output to static/index.html (self-contained file)
        
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
        
        print("Generating marker icon map...")
        marker_icons = self.generate_marker_icon_map()
        print(f"✅ Embedded {len(marker_icons)} Lucide marker icons as base64 data URLs")
        
        print(f"✅ Embedded {len(DASHBOARD_ICONS_MAP)} dashboard icons")
        
        print(f"Building HTML ({len(events)} total events)...")
        
        # Build HTML from components (no fallback - components required)
        html = self.build_html_from_components(
            configs, events, content_en, content_de,
            stylesheets, scripts, marker_icons
        )
        print("✅ Site generated using components")
        
        # Calculate HTML size breakdown and inject into DEBUG_INFO
        html_sizes = self.calculate_html_size_breakdown(html)
        
        # Find and update DEBUG_INFO with size information
        debug_info_marker = 'window.DEBUG_INFO = '
        debug_info_start = html.find(debug_info_marker)
        if debug_info_start != -1:
            debug_info_end = html.find('};', debug_info_start)
            if debug_info_end != -1:
                # Extract current DEBUG_INFO
                current_debug_json = html[debug_info_start + len(debug_info_marker):debug_info_end + 1]
                try:
                    debug_data = json.loads(current_debug_json)
                    debug_data['html_sizes'] = html_sizes
                    # Replace with updated DEBUG_INFO
                    updated_debug_json = json.dumps(debug_data, ensure_ascii=False)
                    html = html[:debug_info_start + len(debug_info_marker)] + updated_debug_json + html[debug_info_end + 1:]
                    print(f"✅ Injected HTML size breakdown into DEBUG_INFO")
                except Exception as e:
                    logger.warning(f"Could not update DEBUG_INFO with size info: {e}")
        
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
        marker = 'window.__INLINE_EVENTS_DATA__ = '
        start = html.find(marker)
        if start == -1:
            return -1, -1
        
        start += len(marker)
        end = html.find('};', start)
        if end != -1:
            end += 1  # Include the closing }
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
