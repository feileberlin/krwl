# Content and Localization

This directory contains localized content files for the KRWL HOF Community Events application.

## Available Languages

- **English** (`content.json`) - Default
- **German** (`content.de.json`) - Deutsche Übersetzung

## How It Works

The application uses a single HTML file and dynamically loads the appropriate content JSON based on:

1. **Config setting** - Set `app.language` in `config.json`
2. **Browser language** - Auto-detects user's browser language
3. **Default fallback** - English if no match

No separate directories or routing needed - everything is handled by the `i18n.js` module.

## Quick Start

### Change Language via Config

Edit `config.json`:

```json
{
  "app": {
    "language": "de"
  }
}
```

Available values:
- `"en"` - English (loads `content.json`)
- `"de"` - German (loads `content.de.json`)
- `"auto"` - Auto-detect from browser (default)

### User Language Switcher

The language selector in the footer allows users to switch languages instantly without page reload.

## Content Structure

All UI strings, labels, and messages are organized into categories:

### App
- Application title and tagline

### Filters
- Event count messages (singular/plural)
- Category labels (all events, on stage, pub games, festivals)
- Time range options (sunrise, sunday, full moon, hours)
- Distance options (by foot, bike, public transport)
- Location options

### Burger Menu
- Action labels with icons (bookmark, copy, share, navigate, calendar)
- Active states (bookmarked/unbookmark, copied/copy)
- ARIA labels for accessibility

### Event Details
- Label texts (Location, Time, Distance)
- Default messages (no description, unknown distance)
- Format strings with placeholders

### Messages
- Geolocation messages (denied, unavailable, timeout, error)
- Event loading messages
- Share/copy feedback messages
- Library loading errors

### Accessibility
- Screen reader announcements
- Keyboard navigation instructions
- ARIA labels for all interactive elements
- Live region announcements

### NoScript
- Fallback content when JavaScript is disabled
- Static event list labels

### Event List
- Date and time formatting
- Action button labels
- Status messages (copied, failed)

### Calendar
- ICS file generation templates
- Filename patterns

## Adding a New Language

1. Copy `content.json` to `content.[locale].json` (e.g., `content.fr.json` for French)
2. Translate all string values, keeping:
   - JSON structure unchanged
   - Placeholder syntax `{variable}` intact
   - Icons (emoji) unchanged
3. Test with `python3 test_translations.py --verbose`
4. Update language selector in `static/js/i18n.js`:
   ```javascript
   getAvailableLanguages() {
       return [
           { code: 'en', name: 'English', nativeName: 'English' },
           { code: 'de', name: 'German', nativeName: 'Deutsch' },
           { code: 'fr', name: 'French', nativeName: 'Français' }  // Add here
       ];
   }
   ```
5. Add option to language selector in `index.html`:
   ```html
   <select id="language-select">
       <option value="en">English</option>
       <option value="de">Deutsch</option>
       <option value="fr">Français</option>
   </select>
   ```

## Translation Guidelines

### Placeholders
Keep placeholder syntax exactly as is:
```json
"distance_format": "{distance} km away"
"distance_format": "{distance} km entfernt"  ✓ Correct
```

### Icons
Do not translate emoji icons:
```json
"icon": "⭐"  // Keep unchanged
```

### Keys
Never translate JSON keys, only values:
```json
"bookmark": "merken"  ✓ Correct (key stays "bookmark")
```

### Length Considerations
Some languages may have longer words. Test UI to ensure:
- Buttons don't overflow
- Filter sentence reads naturally
- Mobile view still works

### Context-Aware Translation
Some English words have different German translations depending on context:
- "event" → "Veranstaltung" (noun)
- "events" → "veranstaltungen" (filter category)
- "bookmark" → "merken" (save for later)
- "share" → "teilen" (social sharing)

## Validation

### Automatic Testing

Test translation completeness:
```bash
python3 test_translations.py --verbose
```

This checks:
- All keys present in all languages
- Placeholders match across translations
- No empty strings
- Icons unchanged
- Structure consistency

### Manual Validation

Check your translation file is valid JSON:
```bash
python3 -m json.tool content.de.json > /dev/null
```

## Testing Translations

1. Change language in config.json (or use language switcher)
2. Clear browser cache (or hard reload with Ctrl+Shift+R)
3. Verify all UI elements show translated text
4. Test with screen reader for accessibility
5. Check mobile and desktop views
6. Run automated tests: `python3 test_translations.py`

## How Language Detection Works

Priority order:

1. **Config file** (`config.json` → `app.language`)
   - If set to specific language code: use that
   - If set to `"auto"`: detect from browser

2. **Browser language** (if config is "auto")
   - Reads `navigator.language`
   - Matches against available translations

3. **Default fallback**
   - English if no match found

Example:
```javascript
// User has browser set to German
navigator.language = "de-DE"

// If config.json has:
{ "app": { "language": "auto" } }

// Result: Loads content.de.json
```

## Contributing Translations

To contribute a new language translation:

1. Create `content.[locale].json` following the structure
2. Run tests: `python3 test_translations.py`
3. Test thoroughly in browser
4. Submit a pull request with:
   - New content file
   - Updated `i18n.js` (add to `getAvailableLanguages()`)
   - Updated `index.html` (add option to language selector)
   - Screenshots showing translated UI

## Troubleshooting

### Language not switching
- Check browser console for i18n errors
- Verify `content.[locale].json` exists
- Check JSON is valid
- Clear browser cache

### Content still in English
- Check browser console for "Using language from..."
- Verify content file loads without 404
- Check config.json syntax

### Missing translations
- Run `python3 test_translations.py` to find missing keys
- Check console for "Translation key not found" warnings

### Icons translated by mistake
- Run tests - they will catch icon changes
- Icons should never be translated, only labels

## Technical Details

### File Loading

The `i18n.js` module:
1. Determines language from config/browser
2. Fetches appropriate `content.[locale].json`
3. Always loads `content.json` as fallback
4. Provides `t(key, replacements)` function for translations
5. Supports plural forms and date/number formatting

### No Server-Side Configuration Needed

Unlike traditional multi-language sites that require:
- Multiple HTML files
- Server URL rewriting
- Directory structures

This approach only needs:
- One HTML file
- Multiple JSON content files
- Client-side JavaScript

Benefits:
- Simpler deployment
- Works on any static host
- Easy to add languages
- No server configuration
- Users can switch languages instantly
