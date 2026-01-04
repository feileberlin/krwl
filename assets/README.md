# Assets Directory

Frontend assets including CSS, JavaScript, HTML templates, JSON data, and SVG icons.

## Structure

```
assets/
├── css/        # Stylesheets
├── js/         # JavaScript modules
├── html/       # HTML component templates
├── json/       # Data files and translations
└── svg/        # SVG icons and graphics
```

## Subdirectories

### css/
Stylesheet files for the application. See [css/README.md](css/README.md)

### js/
JavaScript application logic and i18n. See [js/README.md](js/README.md) if exists.

### html/
HTML component templates for site generation. See [html/README.md](html/README.md)

### json/
JSON data files including:
- `events.json` - Published events
- `pending_events.json` - Events awaiting review
- `rejected_events.json` - Rejected events log
- `events.demo.json` - Demo events for development
- `manifest.json` - PWA manifest
- `i18n/` - Translation files
- `events/` - Event data backups

See [json/events/README.md](json/events/README.md) for event data documentation.

### svg/
SVG icons and graphics including favicon, PWA icons, and map markers.
See [svg/README.md](svg/README.md)

## Usage

These assets are used by the site generator (`src/modules/site_generator.py`) to build the final HTML output.

### Build Process

1. CSS files are inlined into HTML
2. JavaScript modules are bundled and inlined
3. HTML templates are assembled
4. JSON data is embedded or linked
5. SVG icons are embedded or referenced

## Related Documentation

- **Site Generator**: [../src/modules/site_generator.py](../src/modules/site_generator.py)
- **Build Guide**: See main [../README.md](../README.md)
