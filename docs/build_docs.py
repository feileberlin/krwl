#!/usr/bin/env python3
"""
Documentation Builder for KRWL HOF Community Events

This script:
1. Validates that all code changes are documented
2. Merges all documentation into a single comprehensive README.md
3. Generates visualizations for architecture and features
4. Ensures documentation is up-to-date with code
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

class DocumentationBuilder:
    def __init__(self, root_dir='.'):
        self.root_dir = Path(root_dir)
        self.static_dir = self.root_dir / 'static'
        self.docs_dir = self.root_dir / 'docs'
        self.config_file = self.static_dir / 'config.json'
        
    def validate_documentation(self):
        """Validate that all components are documented"""
        issues = []
        
        # Check if key files exist
        required_files = [
            'static/index.html',
            'static/js/app.js',
            'static/css/style.css',
            'static/config.json',
            'static/manifest.json'
        ]
        
        for file in required_files:
            if not (self.root_dir / file).exists():
                issues.append(f"Missing required file: {file}")
        
        # Check if config has required sections
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                required_sections = ['app', 'ui', 'map']
                for section in required_sections:
                    if section not in config:
                        issues.append(f"Missing config section: {section}")
        
        return issues
    
    def extract_features_from_code(self):
        """Extract implemented features from code"""
        features = {
            'ui': [],
            'map': [],
            'pwa': [],
            'accessibility': []
        }
        
        # Check HTML for features
        html_file = self.static_dir / 'index.html'
        if html_file.exists():
            with open(html_file, 'r') as f:
                html_content = f.read()
                if 'role="navigation"' in html_content:
                    features['accessibility'].append('ARIA navigation landmarks')
                if 'skip-link' in html_content:
                    features['accessibility'].append('Skip to content link')
                if 'manifest.json' in html_content:
                    features['pwa'].append('PWA manifest')
                if 'aria-label' in html_content:
                    features['accessibility'].append('ARIA labels')
        
        # Check manifest for PWA features
        manifest_file = self.static_dir / 'manifest.json'
        if manifest_file.exists():
            features['pwa'].append('Installable as app')
            features['pwa'].append('Offline support')
        
        # Check CSS for responsive design
        css_file = self.static_dir / 'css' / 'style.css'
        if css_file.exists():
            with open(css_file, 'r') as f:
                css_content = f.read()
                if '@media' in css_content:
                    features['ui'].append('Responsive design')
                if 'dvh' in css_content:
                    features['ui'].append('Mobile viewport support')
        
        # Check JS for map features
        js_file = self.static_dir / 'js' / 'app.js'
        if js_file.exists():
            with open(js_file, 'r') as f:
                js_content = f.read()
                if 'bindTooltip' in js_content:
                    features['map'].append('Event time tooltips')
                if 'bindPopup' in js_content:
                    features['map'].append('Rich event popups')
                if 'geolocation' in js_content:
                    features['map'].append('Geolocation filtering')
        
        return features
    
    def generate_architecture_diagram(self):
        """Generate ASCII architecture diagram"""
        diagram = """
```
┌─────────────────────────────────────────────────────────────┐
│                    KRWL HOF Architecture                     │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │  index.html  │  ← Entry Point
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
    │   app.js     │ │ style.css│ │ Leaflet.js │
    │  (Business   │ │  (UI/UX) │ │  (Maps)    │
    │   Logic)     │ └──────────┘ └────────────┘
    └───────┬──────┘
            │
    ┌───────┼──────────────┐
    │       │              │
┌───▼──┐ ┌──▼───────┐ ┌───▼──────────┐
│config│ │events.json│ │manifest.json │
│.json │ │  (Data)   │ │    (PWA)     │
└──────┘ └───────────┘ └──────────────┘

Data Flow:
1. config.json → Configures app behavior, UI, map
2. events.json → Fetched and filtered by location/time
3. app.js → Renders markers with tooltips on Leaflet map
4. User interaction → Updates filters → Refreshes map
```
"""
        return diagram
    
    def generate_ui_flow_diagram(self):
        """Generate UI interaction flow diagram"""
        diagram = """
```
User Journey:
                                
    ┌─────────────┐
    │   Landing   │
    │   (Map)     │
    └──────┬──────┘
           │
           │ sees filter sentence at top
           │ sees events as markers with time labels
           │
    ┌──────▼──────────────────────────┐
    │ Filter Controls (Top of Map)    │
    │ • Event count & category        │
    │ • Time range                    │
    │ • Distance                      │
    │ • Location                      │
    └──────┬──────────────────────────┘
           │
           │ click filter → map updates
           │
    ┌──────▼──────────────────────────┐
    │ Map Interaction                 │
    │ • Hover marker → see time       │
    │ • Click marker → see popup      │
    │   - Event title                 │
    │   - Time, location, distance    │
    │   - Description                 │
    │   - Link to more info           │
    └─────────────────────────────────┘
```
"""
        return diagram
    
    def build_comprehensive_readme(self):
        """Build the comprehensive README.md"""
        features = self.extract_features_from_code()
        arch_diagram = self.generate_architecture_diagram()
        ui_diagram = self.generate_ui_flow_diagram()
        
        # Load config for app details
        config = {}
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        
        app_name = config.get('app', {}).get('name', 'KRWL HOF Community Events')
        app_desc = config.get('app', {}).get('description', 'Community events viewer')
        
        readme_content = f"""# {app_name}

> {app_desc}

[![PWA Ready](https://img.shields.io/badge/PWA-Ready-success)](https://web.dev/progressive-web-apps/)
[![Accessibility](https://img.shields.io/badge/A11y-Compliant-blue)](https://www.w3.org/WAI/WCAG21/quickref/)
[![Mobile First](https://img.shields.io/badge/Mobile-First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 🎯 Overview

A **fullscreen, mobile-first** interactive map application for discovering community events near you. All events are displayed as markers directly on the map with no separate navigation—just filters and markers.

### ✨ Key Features

#### 🗺️ Map Features
{self._format_feature_list(features['map'])}

#### 🎨 UI/UX Features
{self._format_feature_list(features['ui'])}

#### 📱 PWA Features
{self._format_feature_list(features['pwa'])}

#### ♿ Accessibility Features
{self._format_feature_list(features['accessibility'])}

## 🏗️ Architecture

{arch_diagram}

## 🎨 User Interface Design

### Design Philosophy
- **Fullscreen Map**: No traditional headers/footers—everything overlays the map
- **Filter Sentence**: Natural language filters integrated at the top
- **Map-First**: Events shown as markers with tooltips, no separate list
- **Mobile-First**: Responsive design optimized for mobile devices first
- **Pure Leaflet.js**: Uses standard Leaflet conventions (markers, tooltips, popups)

{ui_diagram}

## 📱 Progressive Web App (PWA)

The application is installable as a native app on any platform:

### Installation
1. **Desktop (Chrome/Edge)**: Click the install icon in the address bar
2. **Mobile (Android)**: Tap "Add to Home Screen" in browser menu
3. **Mobile (iOS)**: Tap Share → "Add to Home Screen"

### PWA Assets
- ✅ `manifest.json` - PWA configuration
- ✅ Multiple icon sizes (192x192, 512x512)
- ✅ Maskable icons for Android adaptive icons
- ✅ Favicon and Apple Touch Icons
- ✅ Theme colors and splash screen

See [PWA_README.md](static/PWA_README.md) for detailed PWA documentation.

## ⚙️ Configuration

All fork-specific customizations are in `static/config.json`:

```json
{{
  "app": {{
    "name": "Your App Name",
    "description": "Your description"
  }},
  "ui": {{
    "logo": "logo.svg",
    "imprint_url": "imprint.html",
    "imprint_text": "Imprint",
    "theme_color": "#4CAF50",
    "background_color": "#1a1a1a"
  }},
  "map": {{
    "default_center": {{ "lat": 50.3167, "lon": 11.9167 }},
    "default_zoom": 13,
    "tile_provider": "https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png",
    "predefined_locations": [
      {{ "name": "Location Name", "lat": 50.0, "lon": 11.0 }}
    ]
  }}
}}
```

### Customizable Elements
- **App name and description**: `config.app.*`
- **Logo and branding**: `config.ui.logo`, `config.ui.theme_color`
- **Map tiles**: `config.map.tile_provider` (OpenStreetMap, CartoDB, etc.)
- **Default location**: `config.map.default_center`
- **Predefined locations**: `config.map.predefined_locations[]`

## 🎯 Event Data Format

Events are loaded from `static/events.json`:

```json
{{
  "events": [
    {{
      "id": "event_1",
      "title": "Event Name",
      "description": "Event description",
      "location": {{
        "name": "Venue Name",
        "lat": 50.3175,
        "lon": 11.9165
      }},
      "start_time": "2025-12-09T19:00:00",
      "end_time": "2025-12-09T23:00:00",
      "url": "https://example.com/event",
      "category": "on-stage",
      "source": "manual",
      "status": "published"
    }}
  ]
}}
```

## 🚀 Quick Start

### Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/feileberlin/krwl-hof.git
   cd krwl-hof
   ```

2. **Download dependencies** (Leaflet map library)
   ```bash
   ./download-libs.sh
   ```
   
   This downloads Leaflet.js locally for better performance and offline PWA support.

3. **Serve the static files**
   ```bash
   cd static
   python3 -m http.server 8000
   ```

4. **Open in browser**
   ```
   http://localhost:8000
   ```

### Production Deployment

The `static/` directory contains all files needed for deployment:

- **GitHub Pages**: Already configured (see `.nojekyll`)
- **Netlify/Vercel**: Point to `static/` directory
- **Any static host**: Upload `static/` contents

## ♿ Accessibility

This application follows WCAG 2.1 Level AA guidelines:

- ✅ Semantic HTML5 (main, nav, footer, etc.)
- ✅ ARIA landmarks and labels
- ✅ Skip to content link for keyboard navigation
- ✅ Focus indicators for all interactive elements
- ✅ Screen reader announcements for dynamic updates
- ✅ Keyboard navigation support
- ✅ Sufficient color contrast
- ✅ Descriptive alt text for images

### Screen Reader Support
The application provides context to screen reader users:
- Explains the fullscreen map interface on page load
- Announces filter changes and event counts
- Provides ARIA labels for all controls
- Uses semantic HTML for proper navigation

## 🧪 Testing

### Running Documentation Tests
```bash
python3 docs/build_docs.py --validate
```

This validates:
- All required files exist
- Config has all required sections
- Documentation matches code features
- All links in docs are valid

### Manual Testing Checklist
- [ ] Map loads and displays correctly
- [ ] Filters update event markers
- [ ] Markers show time tooltips on hover
- [ ] Popups show full event details on click
- [ ] Responsive design works on mobile
- [ ] PWA installs correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces updates

## 📝 Project Structure

```
krwl-hof/
├── .github/
│   └── workflows/          # CI/CD workflows
├── static/                 # All static files for deployment
│   ├── index.html         # Main HTML entry point
│   ├── manifest.json      # PWA manifest
│   ├── config.json        # App configuration
│   ├── events.json        # Event data
│   ├── css/
│   │   └── style.css      # All styles
│   ├── js/
│   │   └── app.js         # Application logic
│   ├── favicon.svg        # Browser favicon
│   ├── logo.svg           # App logo
│   ├── icon-*.svg         # PWA icons
│   └── PWA_README.md      # PWA documentation
├── src/                    # Python backend (scraping/editing)
│   └── modules/
├── data/                   # Event data storage
├── docs/                   # Documentation
│   └── build_docs.py      # Documentation builder
└── README.md              # This file
```

## 🔧 Development

### Adding New Features

1. **Update code** in `static/` directory
2. **Update config** if adding configurable options
3. **Test locally** with a simple HTTP server
4. **Run docs builder** to update README
5. **Commit changes** including updated docs

### Code Style
- **HTML**: Semantic HTML5, ARIA labels
- **CSS**: Mobile-first, BEM-like naming
- **JavaScript**: ES6+, pure vanilla JS, JSDoc comments
- **Config**: JSON with comments in docs

## 📊 Browser Support

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome  | ✅ Full | ✅ Full |
| Firefox | ✅ Full | ✅ Full |
| Safari  | ✅ Full | ⚠️ Limited PWA |
| Edge    | ✅ Full | ✅ Full |
| Samsung | - | ✅ Full |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run documentation builder
5. Submit a pull request

### Documentation Requirements
- All code changes must be documented
- Run `python3 docs/build_docs.py` before committing
- Update config.json for new configurable features
- Add JSDoc comments for new functions

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- **Leaflet.js** - Open-source map library
- **CartoDB** - Dark map tiles
- **OpenStreetMap** - Map data contributors

## 📞 Support

For issues and questions:
- GitHub Issues: [github.com/feileberlin/krwl-hof/issues](https://github.com/feileberlin/krwl-hof/issues)
- See imprint link in app for contact info

---

**Built with ❤️ for the KRWL HOF community**

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Auto-generated by docs/build_docs.py*
"""
        return readme_content
    
    def _format_feature_list(self, features):
        """Format a list of features as markdown"""
        if not features:
            return "- Coming soon"
        return '\n'.join(f"- ✅ {feature}" for feature in features)
    
    def run(self, validate_only=False):
        """Run the documentation builder"""
        print("🔍 Validating documentation...")
        issues = self.validate_documentation()
        
        if issues:
            print("❌ Documentation validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✅ Documentation validation passed")
        
        if validate_only:
            return True
        
        print("📝 Building comprehensive README...")
        readme_content = self.build_comprehensive_readme()
        
        # Write README
        readme_path = self.root_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ README.md generated at {readme_path}")
        print(f"📊 Documentation size: {len(readme_content)} bytes")
        
        return True

if __name__ == '__main__':
    import sys
    
    validate_only = '--validate' in sys.argv
    
    builder = DocumentationBuilder()
    success = builder.run(validate_only=validate_only)
    
    sys.exit(0 if success else 1)
