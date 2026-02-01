# Multilanguage Support - User Guide

## Overview

KRWL> Events now supports multiple languages with seamless URL-based and UI-based switching. Choose from:
- 🇩🇪 **German (de)** - Deutsche
- 🇬🇧 **English (en)** - English  
- 🇨🇿 **Czech (cs)** - Čeština

## How to Use

### URL-Based Language Switching

Visit the site with a language code in the URL:

| URL | Language | Region |
|-----|----------|--------|
| `/` | Default (de) | Antarctica (showcase) |
| `/en` | English | Antarctica |
| `/de` | German | Antarctica |
| `/cs` | Czech | Antarctica |
| `/en/hof` | English | Hof region |
| `/de/nbg` | German | Nürnberg region |
| `/cs/bth` | Czech | Bayreuth region |

**The URL structure is:** `/{language}/{region}`

### Dashboard Language Switcher

1. Click the **megaphone icon** (top-left) to open the dashboard
2. Scroll to the **"Language / Sprache / Jazyk"** section
3. Click on your preferred language
4. The page will reload in the selected language

### Language Persistence

Your language choice is automatically saved to localStorage. When you visit the site again:
- Without a language in the URL → uses your last selected language
- With a language in the URL → uses that language (and updates your preference)

## For Translators

### Adding a New Language

1. **Create translation file**
   ```bash
   cp assets/json/translations/en.json assets/json/translations/fr.json
   ```

2. **Edit the metadata**
   ```json
   {
     "_language": {
       "code": "fr",
       "name": "French",
       "native_name": "Français"
     }
   }
   ```

3. **Translate all strings**
   - Keep the JSON structure intact
   - Translate only the values, not the keys
   - Use `{{variable}}` placeholders as-is

4. **Add language to config**
   Edit `config.json`:
   ```json
   {
     "supportedLanguages": ["de", "en", "cs", "fr"]
   }
   ```

5. **Regenerate the site**
   ```bash
   python3 src/event_manager.py generate
   ```

### Translation Guidelines

- **Be concise**: Filter bar labels are short (e.g., "til sunrise", "from here")
- **Match tone**: Friendly, casual, community-focused
- **Test context**: View translations in the UI to check length/fit
- **Plural forms**: Use `{{plural}}` variable where provided
- **Regional variants**: Use standard language (e.g., "en" not "en-US")

### Translation Structure

The translation files follow this structure:

```
filter_bar/
  ├─ event_count/           Event count labels
  ├─ time_filters/          Time range descriptions
  ├─ distance_filters/      Distance descriptions
  ├─ location_filters/      Location descriptions
  └─ weather/               Weather descriptions

dashboard/
  ├─ title                  App name
  ├─ sections/
  │   ├─ about/             About section
  │   ├─ custom_locations/  Custom locations
  │   ├─ debug/             Debug cockpit
  │   ├─ contact/           Contact form
  │   └─ language_switcher/ Language switcher

map/
  ├─ fallback/              No events message
  └─ event_detail/          Event popup text

categories/                  Category names
common/                      Common strings (loading, unknown, etc.)
```

## For Developers

### Adding Translatable Strings

1. **Add to translation files** (`assets/json/translations/*.json`):
   ```json
   {
     "my_section": {
       "my_key": "My translatable text with {{variable}}"
     }
   }
   ```

2. **Use in JavaScript**:
   ```javascript
   // Get i18n instance from app
   const i18n = this.i18n;
   
   // Simple translation
   const text = i18n.t('my_section.my_key');
   
   // With variables
   const text = i18n.t('my_section.my_key', { variable: 'value' });
   ```

3. **Update all language files**:
   - Add the same key to `de.json`, `en.json`, `cs.json`
   - Translate appropriately

### Template Variables

Use `{{variable}}` syntax for dynamic values:

```json
{
  "greeting": "Hello {{name}}!",
  "count": "{{count}} event{{plural}}"
}
```

```javascript
i18n.t('greeting', { name: 'Alice' });  // "Hello Alice!"
i18n.t('count', { count: 5, plural: 's' });  // "5 events"
```

### Fallback Behavior

The i18n system uses graceful fallbacks:

1. Requested translation key exists → use it
2. Key missing → return the key itself (shows `"filter_bar.time_filters.6h"`)
3. Translations not loaded → return the key
4. i18n not initialized → use hardcoded English strings

## Technical Details

### Architecture

- **Frontend**: Vanilla JavaScript i18n module (~200 lines)
- **Backend**: Python site_generator.py embeds translations in HTML
- **Storage**: Translations in `window.TRANSLATIONS` global
- **Format**: Simple nested JSON structure
- **Loading**: All translations embedded in HTML (no extra HTTP requests)

### URL Detection

The i18n module parses the URL on page load:

```
/en/hof
 ↓
segments: ['en', 'hof']
         ↓
language: 'en'  (first segment if in supportedLanguages)
region: 'hof'    (last segment)
```

### Performance

- **~15 KB** total for 3 languages (gzipped ~5 KB)
- **0 extra HTTP requests** (embedded in HTML)
- **~5ms** initialization time
- **<1ms** per translation lookup

### Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE11+ with polyfills
- Mobile browsers (iOS Safari, Chrome Android)
- Progressive enhancement (works without JavaScript for basic content)

## Troubleshooting

### Translations not showing

1. Check browser console for errors
2. Verify `window.TRANSLATIONS` exists: `console.log(window.TRANSLATIONS)`
3. Check language code: `console.log(window.app.i18n.getCurrentLanguage())`
4. Regenerate site: `python3 src/event_manager.py generate`

### Language switcher not working

1. Check if i18n.js is loaded: `console.log(typeof I18n)`
2. Check if buttons are rendered: inspect dashboard HTML
3. Check for JavaScript errors in browser console
4. Verify Lucide icons loaded: `lucide.createIcons()` called

### URL routing issues

1. Check `.htaccess` or server config for URL rewriting
2. For GitHub Pages: ensure `404.html` redirects correctly
3. Test with explicit URLs: `/en/hof` not `/en/hof/`

### Missing translations

1. Check translation file has the key: `grep "my_key" assets/json/translations/en.json`
2. Check key path is correct: `filter_bar.time_filters.6h` not `filter_bar.time_filters.6_h`
3. Regenerate site after adding translations

## Examples

### Switching Languages

```javascript
// Get current language
const currentLang = window.app.i18n.getCurrentLanguage();  // 'en'

// Switch to German
window.app.i18n.switchLanguage('de');  // Reloads page with /de URL
```

### Custom Translations

```javascript
// Get translation with fallback
const text = window.app.i18n.t('custom.key') || 'Default text';

// With multiple variables
const message = window.app.i18n.t('notification.message', {
  user: 'Alice',
  count: 5,
  item: 'events'
});
```

### Adding New UI Text

```javascript
// In JavaScript module
class MyModule {
  constructor(i18n) {
    this.i18n = i18n;
  }
  
  showMessage() {
    const msg = this.i18n 
      ? this.i18n.t('my_module.message')
      : 'Fallback message';  // Always provide fallback
    
    alert(msg);
  }
}
```

## Contributing

To contribute translations:

1. Fork the repository
2. Add/edit translation files in `assets/json/translations/`
3. Test locally: `python3 src/event_manager.py generate`
4. Submit a pull request with:
   - Translation file changes
   - Screenshots showing the translations in use
   - Note any strings that needed context adjustments

## Credits

- i18n module: Handrolled vanilla JavaScript solution
- Translation format: Simple nested JSON (KISS principle)
- Languages: German, English, Czech (more welcome!)

---

**Need help?** Open an issue or contact the maintainers through the dashboard contact form.
