# Multilanguage Support - Quick Reference

## For Users

### URL Patterns

| URL | Language | Region | Description |
|-----|----------|--------|-------------|
| `/` | Auto-detect | Antarctica | Root - detects browser language |
| `/en` | English | Antarctica | English showcase |
| `/de` | German | Antarctica | German showcase |
| `/cs` | Czech | Antarctica | Czech showcase |
| `/en/hof` | English | Hof | English, Hof view |
| `/de/nbg` | German | Nürnberg | German, Nürnberg view |
| `/cs/bth` | Czech | Bayreuth | Czech, Bayreuth view |
| `/hof` | English | Hof | Backward compatible (no lang prefix) |

### Language Switcher

**Location**: Dashboard menu → "Language" section (after "About")

**How to Use**:
1. Click menu icon (top-left)
2. Find "Language" section
3. Click language button: [DE] [EN] [CS]
4. Page reloads with new language

## For Developers

### Add New Translatable String

#### 1. Add to Translation Files

**File**: `assets/translations/en.json`
```json
{
  "translations": {
    "category": {
      "new_string_key": "English text here"
    }
  }
}
```

**File**: `assets/translations/de.json`
```json
{
  "translations": {
    "category": {
      "new_string_key": "Deutscher Text hier"
    }
  }
}
```

**File**: `assets/translations/cs.json`
```json
{
  "translations": {
    "category": {
      "new_string_key": "Český text zde"
    }
  }
}
```

#### 2. Use in JavaScript

```javascript
// Simple translation
window.i18n.t('category.new_string_key');
// → "English text here" (if language is 'en')

// With variables
window.i18n.t('greeting', { name: 'John' });
// Translation: "Hello, {{name}}!"
// → "Hello, John!"

// Plural forms
window.i18n.t('filter.events', { count: 5 });
// Uses 'events_other' key (for count > 1)
// → "5 events"
```

#### 3. Use in HTML Templates

**File**: `assets/html/dashboard-aside.html`
```html
<h3>{{t.category.new_string_key}}</h3>
```

Template processor replaces `{{t.key}}` during site generation.

### Translation Key Lookup

The i18n module uses nested object lookup:

```javascript
// Translation file structure
{
  "translations": {
    "filter": {
      "til_sunrise": "til sunrise"
    },
    "dashboard": {
      "contact": {
        "your_name": "Your Name"
      }
    }
  }
}

// JavaScript usage
i18n.t('filter.til_sunrise');           // "til sunrise"
i18n.t('dashboard.contact.your_name');  // "Your Name"
```

### Plural Forms

Support for ICU plural rules (zero/one/other):

```json
{
  "filter": {
    "events_zero": "No events",
    "events_one": "1 event",
    "events_other": "{{count}} events"
  }
}
```

```javascript
i18n.t('filter.events', { count: 0 });  // "No events"
i18n.t('filter.events', { count: 1 });  // "1 event"
i18n.t('filter.events', { count: 5 });  // "5 events"
```

### Variable Interpolation

Use `{{variable}}` in translation strings:

```json
{
  "greeting": "Hello, {{name}}!",
  "distance": "within {{minutes}} min {{mode}}"
}
```

```javascript
i18n.t('greeting', { name: 'Alice' });
// → "Hello, Alice!"

i18n.t('distance', { minutes: 30, mode: 'walk' });
// → "within 30 min walk"
```

### Fallback Behavior

1. **Missing Translation Key**: Falls back to English
   ```javascript
   // Key exists in en.json but not in de.json
   i18n.t('new_key');  // Returns English translation
   ```

2. **Invalid Language**: Falls back to English
   ```javascript
   const i18n = new I18n('invalid_lang');
   // Automatically uses 'en' as fallback
   ```

3. **Missing Variable**: Leaves placeholder
   ```javascript
   // Translation: "Hello, {{name}}!"
   i18n.t('greeting', {});  // "Hello, {{name}}!" (unchanged)
   ```

## For Translators

### Translation Files Location

```
assets/
└── translations/
    ├── en.json  ← English (reference)
    ├── de.json  ← German (Deutsch)
    └── cs.json  ← Czech (Čeština)
```

### File Structure

```json
{
  "language": "en",
  "displayName": "English",
  "translations": {
    "filter": { ... },
    "dashboard": { ... },
    "time": { ... },
    "distance": { ... },
    "common": { ... }
  }
}
```

### Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `filter.*` | Filter bar strings | "til sunrise", "from here" |
| `dashboard.*` | Dashboard menu | "About", "Contact", "Your Name" |
| `time.*` | Time-related | "in the next 6 hours" |
| `distance.*` | Distance-related | "within 30 min walk" |
| `common.*` | Shared strings | "Close", "Cancel", "Submit" |

### Best Practices

#### 1. Keep Context
```json
// ❌ BAD: Ambiguous
"submit": "Submit"

// ✅ GOOD: Clear context
"contact.submit": "Send Message",
"flyer.submit": "Upload Flyer"
```

#### 2. Preserve Placeholders
```json
// English
"events_other": "{{count}} events"

// German - KEEP {{count}}
"events_other": "{{count}} Veranstaltungen"
```

#### 3. Match Plural Forms
English uses: `_zero`, `_one`, `_other`

All translations must provide the same suffixes:
```json
// ✅ CORRECT
"events_zero": "...",
"events_one": "...",
"events_other": "..."
```

#### 4. Preserve HTML Entities
If source has `&times;`, `&nbsp;`, etc., keep them:
```json
"close_button": "Close &times;"
```

#### 5. Test Length
Some languages are longer (German often 30% longer than English):
- Check UI doesn't break with longer text
- Test button labels fit on mobile

### Common Phrases

| English | German | Czech |
|---------|--------|-------|
| event/events | Veranstaltung/Veranstaltungen | akce/akcí |
| until/til | bis | do |
| from | von | od |
| within | in | do |
| upcoming | kommend | nadcházející |
| close | schließen | zavřít |
| send | senden | odeslat |
| your | dein(e) | váš/vaše |
| name | Name | jméno |
| email | E-Mail | e-mail |
| message | Nachricht | zpráva |

## For Site Builders

### Generate Multi-Language Site

```bash
# Generate all language versions
python3 src/event_manager.py generate

# Output structure
public/
├── index.html       # Default (English)
├── en/index.html    # English
├── de/index.html    # German
└── cs/index.html    # Czech
```

### Configuration

**File**: `config.json`
```json
{
  "supportedLanguages": ["de", "en", "cs"],
  "defaultLanguage": "en"
}
```

To add a new language:
1. Add language code to `supportedLanguages`
2. Create translation file: `assets/translations/{lang}.json`
3. Regenerate site: `python3 src/event_manager.py generate`

### Template Processing

The template processor handles two placeholder types:

#### 1. Config Variables
```html
<!-- Before -->
<h2>{{app_name}}</h2>

<!-- After -->
<h2>KRWL> Events</h2>
```

#### 2. Translation Keys
```html
<!-- Before -->
<h3>{{t.dashboard.about}}</h3>

<!-- After (English) -->
<h3>About</h3>

<!-- After (German) -->
<h3>Über uns</h3>
```

### Inline Translations

Each language version embeds its translation JSON:

```html
<script>
  window.TRANSLATIONS = {
    "language": "en",
    "translations": { ... }
  };
</script>
```

No extra HTTP requests for translations!

## Testing Checklist

### URL Routing
- [ ] `/` → Auto-detects browser language or defaults to English
- [ ] `/en` → Shows English, Antarctica
- [ ] `/de` → Shows German, Antarctica
- [ ] `/cs` → Shows Czech, Antarctica
- [ ] `/en/hof` → English + Hof region
- [ ] `/de/nbg` → German + Nürnberg region
- [ ] `/hof` → English (backward compatible)
- [ ] `/invalid` → 404 or fallback to English

### Language Switcher
- [ ] Appears in dashboard menu
- [ ] Current language highlighted
- [ ] Clicking language reloads page
- [ ] URL updates correctly (preserves region)
- [ ] Keyboard accessible (Tab + Enter)
- [ ] Aria-labels correct

### UI Translations
- [ ] Filter bar: All text translated
- [ ] Dashboard sections: All headers translated
- [ ] Form labels: All inputs translated
- [ ] Debug cockpit: All labels translated
- [ ] Button text: All buttons translated
- [ ] Plural forms: "0 events", "1 event", "5 events" correct
- [ ] Variables replaced: "{{count}} events" → "5 events"

### Accessibility
- [ ] `<html lang="">` attribute correct per language
- [ ] Aria-labels translated
- [ ] Focus management preserved
- [ ] Screen reader announces language correctly

### Performance
- [ ] Translation JSON inlined (no extra HTTP requests)
- [ ] Page load time < 2 seconds
- [ ] No JavaScript errors in console
- [ ] No layout shift when translations load

## Troubleshooting

### Translation Not Showing

**Check**:
1. Key exists in translation file?
2. Translation file loaded correctly?
3. `i18n.t('key')` syntax correct?
4. Browser cache cleared?
5. Site regenerated after translation update?

**Debug**:
```javascript
// Check loaded language
console.log(window.i18n.language);

// Check if translation exists
console.log(window.i18n.translations);

// Test translation lookup
console.log(window.i18n.t('filter.til_sunrise'));
```

### Wrong Language Loading

**Check**:
1. URL path correct? (`/en/hof` not `/hof/en`)
2. Language code valid? (must be in `supportedLanguages`)
3. Browser language detection working?
4. Correct HTML file served? (check `/de/index.html` vs `/index.html`)

**Debug**:
```javascript
// Check detected language
console.log(window.location.pathname);
console.log(app.currentLanguage);

// Check browser language
console.log(navigator.language);
```

### Plural Form Not Working

**Check**:
1. All three forms defined? (`_zero`, `_one`, `_other`)
2. Using `count` parameter? `t('key', { count: 5 })`
3. Variable name correct? Must be `{{count}}`

**Example**:
```json
// ✅ CORRECT
"events_zero": "No events",
"events_one": "1 event",
"events_other": "{{count}} events"

// ❌ WRONG - missing _zero
"events_one": "1 event",
"events_other": "{{count}} events"

// ❌ WRONG - typo in variable
"events_other": "{{cnt}} events"
```

### Variable Not Replaced

**Check**:
1. Variable name matches? `{{name}}` → `{ name: 'value' }`
2. Using correct syntax? Double curly braces `{{ }}`
3. Variable passed to `t()` function?

**Example**:
```javascript
// ❌ WRONG - no variables passed
i18n.t('greeting');
// → "Hello, {{name}}!" (unchanged)

// ✅ CORRECT
i18n.t('greeting', { name: 'Alice' });
// → "Hello, Alice!"
```

## Command Reference

```bash
# Generate site (all languages)
python3 src/event_manager.py generate

# Update events only (preserves existing translations)
python3 src/event_manager.py update

# Verify feature implementation
python3 src/event_manager.py verify-features

# Run tests
python3 -m pytest tests/

# Test specific translation
python3 -c "
import json
with open('assets/translations/en.json') as f:
    t = json.load(f)
    print(t['translations']['filter']['til_sunrise'])
"
```

## Additional Resources

- **Full Plan**: `docs/plans/20260201-multilanguage-support.md`
- **Architecture**: `docs/MULTILANGUAGE_ARCHITECTURE.md`
- **Multi-Region Docs**: `docs/MULTI_REGION_INFRASTRUCTURE.md`
- **Config**: `config.json` (line 610: `supportedLanguages`)
- **i18n Module**: `assets/js/i18n.js`
- **Translation Files**: `assets/translations/*.json`
