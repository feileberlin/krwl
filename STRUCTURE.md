# KRWL HOF - Final Project Structure

> Hugo/Jekyll-inspired Static Site Generator following web standards

## 🎯 Structure Philosophy

This project follows **Static Site Generator (SSG)** conventions used by Hugo, Jekyll, 11ty, and other industry-standard tools.

## 📦 Directory Structure

```
krwl-hof/
├── layouts/          # HTML templates (like Hugo/Jekyll _layouts)
│   ├── index.html           # Main template
│   └── components/          # Reusable HTML components (8 files)
│
├── assets/           # Source files to be processed (like Hugo/Jekyll assets)
│   ├── css/                 # CSS source modules (9 files)
│   └── js/                  # JavaScript source files (3 files)
│
├── content/          # Data and content (like Hugo content, Jekyll _data)
│   ├── events/              # Event data (JSON files)
│   └── i18n/                # Translations
│
├── static/           # Static assets (copied as-is, like Hugo/Jekyll static)
│   ├── markers/             # SVG markers (78 files)
│   ├── leaflet/             # Leaflet.js library
│   ├── lucide/              # Lucide icons library
│   └── *.svg                # Icons, logos
│
├── public/           # Build output (like Hugo public, Jekyll _site)
│   └── index.html           # Generated static site
│
├── src/              # Python build system (generator code)
│   ├── modules/             # Python modules
│   ├── tools/               # Build tools
│   ├── event_manager.py     # Main CLI
│   └── design-tokens.css    # Generated tokens
│
├── tests/            # Test files
├── scripts/          # Utility scripts
├── docs/             # Documentation
├── config.json       # Configuration (root level, standard)
└── .github/          # GitHub Actions
```

## 🏗️ Comparison with Industry Standards

| Directory | KRWL HOF | Hugo | Jekyll | 11ty |
|-----------|----------|------|--------|------|
| Templates | `layouts/` | `layouts/` | `_layouts/` | `_includes/` |
| Content/Data | `content/` | `content/` | `_data/` | `_data/` |
| Source Assets | `assets/` | `assets/` | `assets/` | `assets/` |
| Static Files | `public/` | `public/` | `public/` | `public/` |
| Build Output | `public/` | `public/` | `_site/` | `_site/` |
| Generator Code | `src/` | (Go binary) | (Ruby gem) | (npm package) |

**Perfect alignment with SSG conventions!** ✅

## 📂 Directory Purposes

### layouts/ - HTML Templates
Contains all HTML template files that define the structure of generated pages.
- **Purpose**: Define page structure
- **Processed**: Yes, by generator
- **Output**: Combined into `public/index.html`

### assets/ - Source Files
Source CSS and JavaScript that may be processed, minified, or bundled.
- **Purpose**: Source code for styles and scripts
- **Processed**: Yes, inlined into HTML
- **Output**: Embedded in `public/index.html`

### content/ - Data & Content
Event data, translations, and other content files in structured formats (JSON).
- **Purpose**: Application data
- **Processed**: Yes, loaded and rendered
- **Output**: Embedded as JSON in HTML

### static/ - Static Assets
Files copied as-is without processing. Images, fonts, third-party libraries.
- **Purpose**: Static files (images, libraries, icons)
- **Processed**: No, copied as-is
- **Output**: May be referenced or copied to `public/`

### public/ - Build Output
Generated static site ready for deployment. Never edit manually!
- **Purpose**: Deployment artifact
- **Processed**: This IS the final output
- **Deploy**: This directory to web server

### src/ - Generator (Python)
The build system itself. Python code that reads content/layouts/assets and generates public/.
- **Purpose**: Build system code
- **Language**: Python
- **Not deployed**: Only used during build

## 🚀 Build Process Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  layouts/   │────▶│              │     │   public/   │
│  HTML       │     │              │     │             │
├─────────────┤     │   src/       │────▶│ index.html  │
│  assets/    │────▶│  Generator   │     │             │
│  CSS + JS   │     │              │     │ (Ready to   │
├─────────────┤     │  (Python)    │     │  deploy)    │
│  content/   │────▶│              │     │             │
│  Data/JSON  │     │              │     │             │
├─────────────┤     └──────────────┘     └─────────────┘
│  static/    │──────────────┬──────────────────▶
│  Assets     │              │            (May reference
└─────────────┘              │             static files)
                             │
                             ▼
                        Copied or
                        referenced
```

## 📝 Common Operations

### Edit Templates
```bash
vim assets/html/filter-nav.html
vim layouts/index.html
```

### Edit Styles
```bash
vim assets/css/map.css
vim assets/css/dashboard.css
```

### Edit Scripts
```bash
vim assets/js/app.js
vim assets/js/i18n.js
```

### Edit Content/Data
```bash
vim content/events/events.json
vim content/i18n/content.de.json
vim config.json
```

### Build Site
```bash
python3 src/event_manager.py generate
# Output: public/index.html
```

### Deploy
```bash
# Deploy public/ directory
cd public && python3 -m http.server 8000
# Or: Deploy public/ to GitHub Pages, Netlify, etc.
```

## ✅ Benefits of This Structure

### 1. Industry Standard
- Follows Hugo, Jekyll, 11ty conventions
- Immediately familiar to SSG developers
- Well-documented patterns

### 2. Clear Separation
- **Templates**: `layouts/`
- **Source**: `assets/`
- **Data**: `content/`
- **Static**: `public/`
- **Output**: `public/`
- **Generator**: `src/`

### 3. KISS Compliant
- One directory, one purpose
- No nesting beyond 2 levels
- Clear naming conventions

### 4. Scalable
- Easy to add new templates
- Easy to add new CSS/JS modules
- Easy to add new content

### 5. Tool-Friendly
- Standard names work with common tools
- IDE/editors recognize structure
- CI/CD pipelines expect this layout

## 🔄 Deployment

### GitHub Pages
```yaml
# .github/workflows/deploy.yml
- name: Build site
  run: python3 src/event_manager.py generate

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    publish_dir: ./public  # Deploy this directory
```

### Netlify
```toml
# netlify.toml
[build]
  command = "python3 src/event_manager.py generate"
  publish = "public"  # Deploy this directory
```

### Vercel
```json
{
  "buildCommand": "python3 src/event_manager.py generate",
  "outputDirectory": "public"
}
```

## 📚 Further Reading

- [Hugo Directory Structure](https://gohugo.io/getting-started/directory-structure/)
- [Jekyll Structure](https://jekyllrb.com/docs/structure/)
- [11ty Structure](https://www.11ty.dev/docs/config/#input-directory)

---

**Status**: ✅ Industry-standard SSG structure  
**Date**: January 2026  
**Follows**: Hugo, Jekyll, 11ty conventions
