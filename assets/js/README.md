# JavaScript Directory

JavaScript modules for the KRWL HOF application.

## Files

### app.js
Main application logic including:
- Map initialization and event rendering
- Event filtering (distance, time, category)
- User interaction handlers
- Geolocation and UI updates

### i18n.js
Internationalization (i18n) module:
- Language detection (browser, user preference)
- Translation loading (English, German)
- Dynamic content translation
- Fallback handling

## Philosophy

**Vanilla JavaScript** - No frameworks, no build step complexity
- ES6+ features for modern browsers
- Progressive enhancement approach
- Works without JavaScript (noscript fallback)

## Usage

These files are inlined into the final HTML by the site generator:

```bash
python3 src/event_manager.py build production
```

## Code Style

- Use ES6+ features (arrow functions, async/await, modules)
- Keep functions small and focused (KISS principle)
- Document complex logic with comments
- Test on multiple browsers

## Related

- **Styles**: [../css/style.css](../css/style.css)
- **HTML Templates**: [../html/](../html/)
- **Site Generator**: [../../src/modules/site_generator.py](../../src/modules/site_generator.py)
