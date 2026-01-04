# KRWL HOF Documentation

> Styled HTML documentation with Barbie Pink theme and emoji icons

## 📚 Overview

This directory contains auto-generated HTML documentation from the Markdown files in `/docs`. The documentation uses the same Barbie Pink color scheme (#FF69B4) and design tokens as the main application for visual consistency.

## 🎨 Features

- **Barbie Pink Color Scheme**: Signature #FF69B4 pink for headings, links, and branding
- **Dark Theme**: High-contrast dark backgrounds for comfortable reading
- **Emoji Icons**: Colorful emoji icons for each documentation topic
- **Sidebar Navigation**: Fixed sidebar with all documentation topics
- **Responsive Design**: Mobile-first approach with collapsible sidebar on small screens
- **Syntax Highlighting**: Code blocks styled with Pygments Monokai theme
- **Styled Tables**: Formatted tables with pink headers
- **Markdown Support**: Full Markdown rendering with extensions (tables, code, TOC)

## 🔄 Regenerating Documentation

The HTML files in this directory are **auto-generated**. Do not edit them directly!

To regenerate after updating Markdown files in `/docs`:

```bash
# Using the CLI command
python3 src/event_manager.py docs html-docs

# Or run the generator directly
python3 src/modules/docs_generator.py
```

## 📝 Adding New Documentation

1. Create a new Markdown file in `/docs` directory
2. Run the regeneration command (see above)
3. The new page will automatically appear in the sidebar navigation
4. Commit both the source `.md` and generated `.html` files

## 🎨 Customizing Colors

The documentation automatically pulls design tokens from `config.json`. To change colors:

1. Edit `config.json` → `design.colors` section
2. Regenerate documentation: `python3 src/event_manager.py docs html-docs`
3. All documentation will use the new color scheme

## 🌐 Deployment

This directory is deployed alongside the main application at:
- **Production**: https://krwl.in/docs/
- **Local**: http://localhost:8000/docs/ (when running local server)

## 📂 File Structure

```
public/docs/
├── README.md                      # This file
├── index.html                     # Documentation homepage
├── CHANGELOG.html                 # Changelog documentation
├── COLOR_SCHEME_BARBIE_PINK.html  # Color scheme guide
├── DEPENDENCY_UPDATE_GUIDE.html   # Dependency update guide
├── EASY_DEPENDENCY_UPDATES.html   # Easy update guide
├── IMPLEMENTATION_COMPLETE_OLD.html # Implementation notes
├── KISS_IMPROVEMENTS.html         # KISS principles guide
├── LEAFLET_BEST_PRACTICES.html    # Leaflet best practices
├── LEAFLET_UPDATE_GUIDE.html      # Leaflet update guide
├── LUCIDE_UPDATE_GUIDE.html       # Lucide update guide
├── MARKDOWN_LINTING.html          # Markdown linting guide
├── PROOF_SINGLE_PAGE.html         # Single page proof
├── PYTHON_WEB_STANDARDS.html      # Python web standards
├── QUICK_REFERENCE.html           # Quick reference
└── SSG_DIRECTORY_STANDARD.html    # SSG directory standard
```

## 🛠️ Technical Details

- **Generator**: `/src/modules/docs_generator.py`
- **Markdown Parser**: Python `markdown` library with extensions
- **Syntax Highlighter**: Pygments with Monokai theme
- **Design Tokens**: Loaded from `config.json` at generation time
- **Icons**: Emoji for offline compatibility (no CDN dependencies)

## 🔗 Related Documentation

- **Main README**: `/README.md` - Project overview
- **Source Docs**: `/docs/` - Markdown source files
- **Config**: `/config.json` - Design tokens and configuration
- **Generator**: `/src/modules/docs_generator.py` - Documentation generator

---

**Last Updated**: Auto-generated documentation system
**Maintained By**: KRWL HOF Project
