# Multilanguage Support Architecture

## Overview

KRWL> Events now supports **3 languages** (German, English, Czech) with URL-based language selection and a dashboard language switcher. The implementation follows KISS principles with a handrolled i18n solution (no external dependencies) that integrates seamlessly with the existing multi-region infrastructure.

## URL Structure

### Language-Only URLs
- `/` - Auto-detect browser language → Antarctica showcase
- `/en` - English → Antarctica showcase
- `/de` - German (Deutsch) → Antarctica showcase
- `/cs` - Czech (Čeština) → Antarctica showcase

### Language + Region URLs
- `/en/hof` - English, Hof (Saale) view
- `/de/nbg` - German, Nürnberg view
- `/cs/bth` - Czech, Bayreuth view
- `/en/selb` - English, Selb view
- `/de/rehau` - German, Rehau view

### Backward Compatibility
- `/hof` - Defaults to English, Hof view (existing URLs still work)
- `/nbg` - Defaults to English, Nürnberg view

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      URL: /en/hof                           │
│                    (Language + Region)                      │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─► Language Detection
                │   ├─ Parse URL path segment: "en"
                │   ├─ Validate against supportedLanguages: ["de","en","cs"]
                │   └─ Load translation: assets/translations/en.json
                │
                └─► Region Detection (existing)
                    ├─ Parse URL path segment: "hof"
                    ├─ Load region config from config.regions.hof
                    └─ Apply map center & zoom
                    
┌─────────────────────────────────────────────────────────────┐
│                  Translation Flow                           │
└─────────────────────────────────────────────────────────────┘

   ┌──────────────┐
   │  config.json │
   │ supported-   │
   │  Languages   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────┐      ┌──────────────────┐
   │  Translation Files   │      │   i18n Module    │
   │ ────────────────────│      │  (< 200 lines)   │
   │  en.json            │─────►│  ────────────────│
   │  de.json            │      │  • Load JSON     │
   │  cs.json            │      │  • t(key)        │
   └──────────────────────┘      │  • Plurals       │
                                 │  • Variables     │
                                 └────────┬─────────┘
                                          │
                                          ▼
   ┌─────────────────────────────────────────────────────────┐
   │              UI Components (Translated)                 │
   │  ───────────────────────────────────────────────────── │
   │  • Filter Bar (filter-description-ui.js)               │
   │    - Event counts: "5 events" / "5 Veranstaltungen"   │
   │    - Time: "til sunrise" / "bis Sonnenaufgang"        │
   │    - Distance: "within 30 min walk" / "in 30 Min zu Fuß"│
   │  • Dashboard (dashboard-aside.html)                    │
   │    - Sections: "About" / "Über uns"                   │
   │    - Forms: "Your Name" / "Dein Name"                 │
   │  • Language Switcher (new)                             │
   │    - [DE] [EN] [CS] toggle buttons                    │
   └─────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Frontend (JavaScript)

#### `assets/js/i18n.js` (NEW)
**Purpose**: Simple translation module (< 200 lines, no dependencies)

**Features**:
- Load translation JSON files
- Nested key lookup: `t('filter.til_sunrise')`
- Plural forms: `t('filter.events', { count: 5 })` → "5 events" / "5 Veranstaltungen"
- Variable interpolation: `t('message', { name: 'John' })` → "Hello, John"
- Fallback to English on missing keys

**API**:
```javascript
// Initialize
const i18n = new I18n('en');
await i18n.load();

// Simple translation
i18n.t('filter.til_sunrise'); // "til sunrise"

// With variables
i18n.t('filter.events_other', { count: 5 }); // "5 events"

// Nested keys
i18n.t('dashboard.contact.your_name'); // "Your Name"
```

#### `assets/js/app.js` (MODIFIED)
**Purpose**: Add language detection alongside existing region detection

**New Methods**:
- `detectLanguageFromUrl()` - Parse `/lang/region` or `/lang` from URL
- `loadTranslations()` - Initialize i18n module with detected language
- `applyLanguageFromUrl()` - Apply language settings (similar to `applyRegionFromUrl()`)

**Changes**:
- Add `this.currentLanguage` state variable
- Initialize i18n before other modules
- Pass language to modules that need translations

#### `assets/js/filter-description-ui.js` (MODIFIED)
**Purpose**: Replace hardcoded English strings with `t()` calls

**Before**:
```javascript
this.TIME_DESCRIPTIONS = {
    'sunrise': 'til sunrise',
    'sunday-primetime': "til Sunday's primetime"
};
```

**After**:
```javascript
this.TIME_DESCRIPTIONS = {
    'sunrise': () => window.i18n.t('filter.til_sunrise'),
    'sunday-primetime': () => window.i18n.t('filter.til_sunday_primetime')
};
```

#### `assets/js/event-listeners.js` (MODIFIED)
**Purpose**: Translate time/distance filter dropdowns and button labels

**Changes**:
- Replace dropdown option labels with `t()` calls
- Translate aria-labels for accessibility
- Add language switcher event listener

### Frontend (HTML Templates)

#### `assets/html/dashboard-aside.html` (MODIFIED)
**Purpose**: Add language switcher section and translation placeholders

**New Section** (after "About"):
```html
<div class="dashboard-section">
  <h3>
    <i data-lucide="globe" aria-hidden="true"></i> 
    {{t.dashboard.language}}
  </h3>
  <div class="language-switcher">
    <button class="lang-btn" data-lang="de" aria-label="Deutsch">
      <span class="lang-code">DE</span>
      <span class="lang-name">Deutsch</span>
    </button>
    <button class="lang-btn active" data-lang="en" aria-label="English">
      <span class="lang-code">EN</span>
      <span class="lang-name">English</span>
    </button>
    <button class="lang-btn" data-lang="cs" aria-label="Čeština">
      <span class="lang-code">CS</span>
      <span class="lang-name">Čeština</span>
    </button>
  </div>
</div>
```

**Changes**:
- Replace hardcoded text with `{{t.key}}` placeholders
- Template processor will replace these during site generation

### Backend (Python)

#### `src/modules/site_generator.py` (MODIFIED)
**Purpose**: Generate separate HTML files per language

**New Functions**:
- `generate_multilanguage_sites()` - Generate HTML for each supported language
- `inline_translations()` - Embed translation JSON into HTML

**Output Structure**:
```
/public/
├── index.html              # Default (English)
├── de/
│   └── index.html         # German version
├── en/
│   └── index.html         # English version (explicit)
└── cs/
    └── index.html         # Czech version
```

**Changes**:
- Read `supportedLanguages` from config.json
- Loop through each language and generate HTML
- Inline appropriate translation JSON in each HTML file
- Set `<html lang="">` attribute correctly
- Update meta tags per language

#### `src/modules/template_processor.py` (MODIFIED)
**Purpose**: Process `{{t.key}}` translation placeholders

**New Features**:
- Recognize `{{t.key}}` pattern
- Load translation JSON for target language
- Replace placeholders with translated strings
- Support nested keys (e.g., `{{t.dashboard.contact.your_name}}`)

**Changes**:
- Add translation context to placeholder resolution
- Handle missing translations gracefully (fallback to English)

### Translation Files

#### `assets/translations/en.json`
```json
{
  "language": "en",
  "displayName": "English",
  "translations": {
    "filter": {
      "events_zero": "0 events",
      "events_one": "1 event",
      "events_other": "{{count}} events",
      "til_sunrise": "til sunrise",
      "til_sunday_primetime": "til Sunday's primetime",
      "til_full_moon": "til full moon",
      "within_30min_walk": "within 30 min walk",
      "within_30min_bicycle": "within 30 min bicycle ride",
      "within_30min_transit": "within 30 min public transport",
      "within_60min_car": "within 60 min car sharing",
      "from_here": "from here",
      "upcoming": "upcoming"
    },
    "dashboard": {
      "about": "About",
      "custom_locations": "Custom Locations",
      "debug_cockpit": "Debug Cockpit",
      "contact": "Contact",
      "submit_flyer": "Submit Event Flyer",
      "maintainer": "Maintainer",
      "documentation": "Documentation",
      "credits": "Credits & Attribution",
      "language": "Language",
      "your_name": "Your Name",
      "your_email": "Your Email",
      "message": "Message",
      "send_message": "Send Message"
    },
    "time": {
      "in_next_6h": "in the next 6 hours",
      "in_next_12h": "in the next 12 hours",
      "in_next_24h": "in the next 24 hours",
      "in_next_48h": "in the next 48 hours"
    }
  }
}
```

#### `assets/translations/de.json`
```json
{
  "language": "de",
  "displayName": "Deutsch",
  "translations": {
    "filter": {
      "events_zero": "0 Veranstaltungen",
      "events_one": "1 Veranstaltung",
      "events_other": "{{count}} Veranstaltungen",
      "til_sunrise": "bis Sonnenaufgang",
      "til_sunday_primetime": "bis Sonntag Primetime",
      "til_full_moon": "bis Vollmond",
      "within_30min_walk": "in 30 Min zu Fuß",
      "within_30min_bicycle": "in 30 Min mit Fahrrad",
      "within_30min_transit": "in 30 Min mit ÖPNV",
      "within_60min_car": "in 60 Min mit Auto",
      "from_here": "von hier",
      "upcoming": "kommend"
    },
    "dashboard": {
      "about": "Über uns",
      "custom_locations": "Eigene Orte",
      "debug_cockpit": "Debug-Cockpit",
      "contact": "Kontakt",
      "submit_flyer": "Event-Flyer einreichen",
      "maintainer": "Betreuer",
      "documentation": "Dokumentation",
      "credits": "Credits & Danksagungen",
      "language": "Sprache",
      "your_name": "Dein Name",
      "your_email": "Deine E-Mail",
      "message": "Nachricht",
      "send_message": "Nachricht senden"
    }
  }
}
```

#### `assets/translations/cs.json`
```json
{
  "language": "cs",
  "displayName": "Čeština",
  "translations": {
    "filter": {
      "events_zero": "0 akcí",
      "events_one": "1 akce",
      "events_other": "{{count}} akcí",
      "til_sunrise": "do východu slunce",
      "til_sunday_primetime": "do neděle prime time",
      "til_full_moon": "do úplňku",
      "within_30min_walk": "do 30 min chůze",
      "within_30min_bicycle": "do 30 min na kole",
      "within_30min_transit": "do 30 min MHD",
      "within_60min_car": "do 60 min autem",
      "from_here": "odtud",
      "upcoming": "nadcházející"
    },
    "dashboard": {
      "about": "O projektu",
      "custom_locations": "Vlastní místa",
      "debug_cockpit": "Debug Cockpit",
      "contact": "Kontakt",
      "submit_flyer": "Odeslat leták akce",
      "maintainer": "Správce",
      "documentation": "Dokumentace",
      "credits": "Poděkování",
      "language": "Jazyk",
      "your_name": "Vaše jméno",
      "your_email": "Váš e-mail",
      "message": "Zpráva",
      "send_message": "Odeslat zprávu"
    }
  }
}
```

## Language Detection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User visits URL                          │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─► /en/hof
                │   ├─ Language: "en" (from URL)
                │   └─ Region: "hof" (from URL)
                │
                ├─► /hof
                │   ├─ Language: "en" (default, no lang in URL)
                │   └─ Region: "hof" (from URL)
                │
                ├─► /de
                │   ├─ Language: "de" (from URL)
                │   └─ Region: "antarctica" (default)
                │
                └─► /
                    ├─ Language: navigator.language → "de-DE" → "de"
                    │   OR "en" if unsupported/unavailable
                    └─ Region: "antarctica" (default)
```

## Language Switcher Flow

```
┌─────────────────────────────────────────────────────────────┐
│           User clicks language button in dashboard          │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─► Current URL: /en/hof
                │   ├─ User clicks "DE" button
                │   ├─ Extract region: "hof"
                │   ├─ Build new URL: /de/hof
                │   ├─ Set window.location = /de/hof
                │   └─ Page reloads with German translations
                │
                └─► Current URL: /cs
                    ├─ User clicks "EN" button
                    ├─ No region to preserve
                    ├─ Build new URL: /en
                    ├─ Set window.location = /en
                    └─ Page reloads with English translations
```

## Integration with Existing Features

### Multi-Region Support
- **Compatible**: Language detection happens before region detection
- **URL Pattern**: `/{lang}/{region}` extends existing `/{region}` pattern
- **Backward Compatible**: Existing `/region` URLs work (default to English)

### URL Routing (404.html)
- **Update Required**: Parse language segment before region segment
- **Redirect Logic**: Store both language and region in sessionStorage
- **Fallback**: Invalid language → redirect to English version

### Template System
- **Extends**: Existing `{{VARIABLE}}` placeholder system
- **New Pattern**: `{{t.key}}` for translations
- **Processor**: template_processor.py handles both types

### Site Generation
- **Extends**: Generate multiple HTML files (one per language)
- **Inline**: Embed translation JSON in HTML (no extra HTTP requests)
- **Performance**: Each language version is pre-rendered

## Testing Strategy

### Unit Tests
- [ ] Language detection from various URL patterns
- [ ] Translation loading and fallback
- [ ] Plural form selection
- [ ] Variable interpolation
- [ ] Nested key lookup

### Integration Tests
- [ ] Full app initialization with each language
- [ ] Region + language combinations
- [ ] Language switcher functionality
- [ ] Backward compatibility with existing URLs

### Manual Testing
- [ ] All filter descriptions in all languages
- [ ] All dashboard sections in all languages
- [ ] Language switcher visual feedback
- [ ] Browser language detection
- [ ] Invalid language handling

## Performance Considerations

### Bundle Size
- **i18n.js**: ~5KB minified (< 200 lines)
- **Translation JSON**: ~3-5KB each (inline, no HTTP request)
- **Total Overhead**: < 10KB per language

### Runtime Performance
- **Translation Lookup**: O(1) object property access
- **No Reactivity**: Static translations loaded once
- **Page Reload**: Language switch causes full reload (acceptable for rare action)

### Build Time
- **Site Generation**: 3x longer (one per language)
- **Expected**: ~15-30 seconds total (5-10 sec per language)
- **Acceptable**: One-time cost during deployment

## Accessibility

### Language Attributes
- `<html lang="en|de|cs">` - Set correctly per language version
- Assistive technologies use correct pronunciation

### ARIA Labels
- Language switcher buttons: `aria-label="Deutsch"`, `aria-label="English"`, etc.
- Current language button: `aria-current="true"`
- Filter buttons: Translated aria-labels

### Keyboard Navigation
- Language switcher: Fully keyboard accessible
- Tab order preserved
- Focus indicators visible

## Future Enhancements (Out of Scope)

### Phase 2 Features
- [ ] Date/time formatting per locale
- [ ] Number formatting (1,000 vs 1.000)
- [ ] Relative time strings ("2 hours ago" → "vor 2 Stunden")
- [ ] Translation management UI
- [ ] Crowdsourced translations
- [ ] Language preference cookie/localStorage

### Phase 3 Features
- [ ] RTL language support (Arabic, Hebrew)
- [ ] Dynamic translation loading (reduce bundle size)
- [ ] Translation key usage analyzer
- [ ] Missing translation reporter
- [ ] A/B testing different translations

## References

- **Plan**: `docs/plans/20260201-multilanguage-support.md`
- **Multi-Region**: `docs/MULTI_REGION_INFRASTRUCTURE.md`
- **Config**: `config.json` (line 610: `supportedLanguages`)
- **URL Routing**: `assets/js/app.js` (`applyRegionFromUrl()`)
- **Template Processor**: `src/modules/template_processor.py`
- **Site Generator**: `src/modules/site_generator.py`
