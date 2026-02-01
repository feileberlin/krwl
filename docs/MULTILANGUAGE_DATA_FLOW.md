# Multilanguage Support - Data Flow Diagram

## Complete Implementation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER VISITS WEBSITE                                │
│                                                                             │
│  Examples: krwl.in/en/hof  or  krwl.in/de  or  krwl.in/                   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LANGUAGE DETECTION FLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Parse URL Path                                                          │
│     └─► /en/hof → language: "en", region: "hof"                           │
│     └─► /de → language: "de", region: "antarctica"                        │
│     └─► /hof → language: null (fallback), region: "hof"                   │
│     └─► / → language: null (fallback), region: "antarctica"               │
│                                                                             │
│  2. Language Validation                                                     │
│     ├─► Check against config.supportedLanguages: ["de","en","cs"]         │
│     └─► If invalid → fallback to step 3                                    │
│                                                                             │
│  3. Browser Detection (if no valid URL language)                           │
│     ├─► navigator.language → "de-DE" → extract "de"                       │
│     ├─► Check if "de" in supportedLanguages                                │
│     └─► If not supported → fallback to step 4                              │
│                                                                             │
│  4. Default Fallback                                                        │
│     └─► Use "en" (English)                                                 │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRANSLATION LOADING FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Load Translation File                                                   │
│     └─► assets/translations/{language}.json                                │
│     └─► Embedded in HTML (no HTTP request)                                 │
│                                                                             │
│  2. Initialize i18n Module                                                  │
│     ├─► new I18n(language)                                                 │
│     ├─► Parse JSON structure                                               │
│     └─► Store in window.i18n global                                        │
│                                                                             │
│  3. Set HTML Language Attribute                                             │
│     └─► <html lang="en|de|cs">                                             │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UI RENDERING FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ FILTER BAR (filter-description-ui.js)                              │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  updateEventCount(count: 5, category: 'all')                       │  │
│  │    └─► t('filter.events', {count: 5})                              │  │
│  │        └─► Plural logic:                                            │  │
│  │            ├─► count === 0 → t('filter.events_zero')               │  │
│  │            ├─► count === 1 → t('filter.events_one')                │  │
│  │            └─► count > 1 → t('filter.events_other', {count: 5})    │  │
│  │                            → "{{count}} events"                     │  │
│  │                            → Replace {{count}} with 5               │  │
│  │                            → "5 events" (English)                   │  │
│  │                            → "5 Veranstaltungen" (German)           │  │
│  │                                                                     │  │
│  │  updateTimeDescription(timeFilter: 'sunrise')                      │  │
│  │    └─► t('filter.til_sunrise')                                     │  │
│  │        └─► "til sunrise" (English)                                 │  │
│  │        └─► "bis Sonnenaufgang" (German)                            │  │
│  │                                                                     │  │
│  │  updateDistanceDescription(maxDistance: 2)                         │  │
│  │    └─► t('filter.within_30min_walk')                               │  │
│  │        └─► "within 30 min walk" (English)                          │  │
│  │        └─► "in 30 Min zu Fuß" (German)                             │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ DASHBOARD (dashboard-aside.html + template processor)              │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  HTML Template:                                                     │  │
│  │    <h3>{{t.dashboard.about}}</h3>                                   │  │
│  │                                                                     │  │
│  │  Template Processor (site_generator.py):                           │  │
│  │    └─► Detect {{t.key}} pattern                                    │  │
│  │    └─► Load translation file for language                          │  │
│  │    └─► Look up key: translations.dashboard.about                   │  │
│  │    └─► Replace placeholder with value                              │  │
│  │                                                                     │  │
│  │  Generated HTML:                                                    │  │
│  │    <h3>About</h3> (English)                                        │  │
│  │    <h3>Über uns</h3> (German)                                      │  │
│  │    <h3>O projektu</h3> (Czech)                                     │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ LANGUAGE SWITCHER (event-listeners.js)                             │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  User clicks language button: [DE]                                 │  │
│  │    └─► Get current URL: /en/hof                                    │  │
│  │    └─► Extract region: "hof"                                       │  │
│  │    └─► Build new URL: /de/hof                                      │  │
│  │    └─► window.location = '/de/hof'                                 │  │
│  │    └─► Page reloads with German translations                       │  │
│  │                                                                     │  │
│  │  Visual Feedback:                                                   │  │
│  │    └─► Remove 'active' class from all buttons                      │  │
│  │    └─► Add 'active' class to selected button                       │  │
│  │    └─► aria-current="true" on active button                        │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND GENERATION FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Command: python3 src/event_manager.py generate                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ site_generator.py                                                   │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  1. Read config.json                                                │  │
│  │     └─► supportedLanguages: ["de", "en", "cs"]                     │  │
│  │                                                                     │  │
│  │  2. Loop through each language                                      │  │
│  │     ├─► language = "en"                                             │  │
│  │     │   ├─► Load translation: assets/translations/en.json          │  │
│  │     │   ├─► Process templates with en translations                 │  │
│  │     │   ├─► Inline en.json in HTML                                 │  │
│  │     │   ├─► Set <html lang="en">                                   │  │
│  │     │   └─► Write to: public/en/index.html                         │  │
│  │     │                                                               │  │
│  │     ├─► language = "de"                                             │  │
│  │     │   ├─► Load translation: assets/translations/de.json          │  │
│  │     │   ├─► Process templates with de translations                 │  │
│  │     │   ├─► Inline de.json in HTML                                 │  │
│  │     │   ├─► Set <html lang="de">                                   │  │
│  │     │   └─► Write to: public/de/index.html                         │  │
│  │     │                                                               │  │
│  │     └─► language = "cs"                                             │  │
│  │         ├─► Load translation: assets/translations/cs.json          │  │
│  │         ├─► Process templates with cs translations                 │  │
│  │         ├─► Inline cs.json in HTML                                 │  │
│  │         ├─► Set <html lang="cs">                                   │  │
│  │         └─► Write to: public/cs/index.html                         │  │
│  │                                                                     │  │
│  │  3. Copy default English to root                                    │  │
│  │     └─► cp public/en/index.html public/index.html                  │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Output Structure:                                                          │
│    public/                                                                  │
│    ├── index.html (default English)                                        │
│    ├── en/index.html (explicit English)                                    │
│    ├── de/index.html (German)                                              │
│    └── cs/index.html (Czech)                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRANSLATION LOOKUP FLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  i18n.t('filter.til_sunrise')                                              │
│    │                                                                        │
│    ├─► 1. Split key by '.' → ['filter', 'til_sunrise']                    │
│    │                                                                        │
│    ├─► 2. Navigate nested object:                                          │
│    │    translations → filter → til_sunrise                                │
│    │                                                                        │
│    ├─► 3. Found value: "til sunrise" (en)                                 │
│    │                 OR "bis Sonnenaufgang" (de)                           │
│    │                 OR "do východu slunce" (cs)                           │
│    │                                                                        │
│    └─► 4. Return value                                                     │
│                                                                             │
│  i18n.t('filter.events', {count: 5})                                       │
│    │                                                                        │
│    ├─► 1. Detect plural context (count provided)                           │
│    │                                                                        │
│    ├─► 2. Determine plural form:                                           │
│    │    ├─► count === 0 → lookup 'filter.events_zero'                     │
│    │    ├─► count === 1 → lookup 'filter.events_one'                      │
│    │    └─► count > 1 → lookup 'filter.events_other'                      │
│    │                                                                        │
│    ├─► 3. Get translation: "{{count}} events"                             │
│    │                                                                        │
│    ├─► 4. Replace variables:                                               │
│    │    └─► {{count}} → 5                                                  │
│    │                                                                        │
│    └─► 5. Return: "5 events" (en)                                         │
│                 OR "5 Veranstaltungen" (de)                                │
│                 OR "5 akcí" (cs)                                           │
│                                                                             │
│  i18n.t('greeting', {name: 'Alice'})                                       │
│    │                                                                        │
│    ├─► 1. Lookup key: "Hello, {{name}}!"                                  │
│    │                                                                        │
│    ├─► 2. Replace variables:                                               │
│    │    └─► {{name}} → 'Alice'                                             │
│    │                                                                        │
│    └─► 3. Return: "Hello, Alice!"                                         │
│                                                                             │
│  i18n.t('missing.key')                                                     │
│    │                                                                        │
│    ├─► 1. Try current language (e.g., 'de')                               │
│    │    └─► Not found in German translations                               │
│    │                                                                        │
│    ├─► 2. Fallback to English                                              │
│    │    └─► Lookup 'missing.key' in English translations                  │
│    │                                                                        │
│    ├─► 3. If found in English → return English value                      │
│    │    If not found → return key itself: 'missing.key'                   │
│    │                                                                        │
│    └─► 4. Log warning to console (in debug mode)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          URL ROUTING MATRIX                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  URL Path          │ Language │ Region      │ HTML File              │      │
│  ──────────────────┼──────────┼─────────────┼────────────────────────┤      │
│  /                 │ auto     │ antarctica  │ public/index.html      │      │
│  /en               │ en       │ antarctica  │ public/en/index.html   │      │
│  /de               │ de       │ antarctica  │ public/de/index.html   │      │
│  /cs               │ cs       │ antarctica  │ public/cs/index.html   │      │
│  /en/hof           │ en       │ hof         │ public/en/index.html   │      │
│  /de/hof           │ de       │ hof         │ public/de/index.html   │      │
│  /cs/hof           │ cs       │ hof         │ public/cs/index.html   │      │
│  /hof              │ en       │ hof         │ public/index.html      │      │
│  /nbg              │ en       │ nbg         │ public/index.html      │      │
│  /invalid          │ en       │ atlantis    │ public/index.html      │      │
│                                                                             │
│  Note: GitHub Pages 404.html redirects to appropriate HTML file            │
│        JavaScript then applies region settings from URL                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Translation File Structure (Visual)

```
assets/translations/en.json
{
  "language": "en",
  "displayName": "English",
  "translations": {
    ┌────────────────────────────────────────────────────────┐
    │ "filter": {                                            │
    │   "events_zero": "No events",            ◄──────────── Plural: zero
    │   "events_one": "1 event",               ◄──────────── Plural: one
    │   "events_other": "{{count}} events",    ◄──────────── Plural: other (with variable)
    │   "til_sunrise": "til sunrise",          ◄──────────── Simple string
    │   "within_30min_walk": "within 30 min walk"
    │ }
    └────────────────────────────────────────────────────────┘
    ┌────────────────────────────────────────────────────────┐
    │ "dashboard": {                                         │
    │   "about": "About",                                    │
    │   "contact": {                            ◄──────────── Nested category
    │     "your_name": "Your Name",                          │
    │     "your_email": "Your Email"                         │
    │   }                                                    │
    │ }                                                      │
    └────────────────────────────────────────────────────────┘
  }
}
```

## Key Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                      DEPENDENCY GRAPH                           │
└─────────────────────────────────────────────────────────────────┘

config.json (supportedLanguages)
      │
      ├──────────────────┬──────────────────┐
      ▼                  ▼                  ▼
   en.json            de.json            cs.json
      │                  │                  │
      └──────────────────┴──────────────────┘
                         │
                         ▼
                    i18n.js
                    (loads JSON, provides t() API)
                         │
      ┏━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━┓
      ▼                                     ▼
Frontend Components                Backend Components
├─ app.js                          ├─ site_generator.py
├─ filter-description-ui.js        ├─ template_processor.py
├─ event-listeners.js              └─ event_manager.py
└─ dashboard-aside.html
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE METRICS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Initial Load Time:                                             │
│    ├─ HTML file size: +5KB per language (inlined translations) │
│    ├─ JavaScript: +5KB (i18n.js minified)                      │
│    └─ Total overhead: ~10KB per language                       │
│                                                                 │
│  Translation Lookup:                                            │
│    ├─ Complexity: O(1) (object property access)                │
│    ├─ Average time: < 0.1ms                                    │
│    └─ No network requests (JSON inlined)                       │
│                                                                 │
│  Language Switch:                                               │
│    ├─ Action: Full page reload                                 │
│    ├─ Time: ~1-2 seconds (normal page load)                    │
│    └─ User experience: Brief but acceptable                    │
│                                                                 │
│  Build Time:                                                    │
│    ├─ Single language: ~5-10 seconds                           │
│    ├─ Three languages: ~15-30 seconds                          │
│    └─ Impact: One-time cost during deployment                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     ERROR SCENARIOS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Invalid Language in URL: /xx/hof                            │
│     └─► Language not in supportedLanguages                      │
│         ├─ Fall back to browser language detection             │
│         └─ If still invalid → fallback to English              │
│                                                                 │
│  2. Missing Translation Key: t('missing.key')                   │
│     └─► Key not in current language file                       │
│         ├─ Try English translation file                        │
│         ├─ If found → return English value                     │
│         ├─ If not found → return key name 'missing.key'        │
│         └─ Log warning (in debug mode)                         │
│                                                                 │
│  3. Translation File Load Error                                 │
│     └─► JSON parse error or file not found                     │
│         ├─ Catch error gracefully                              │
│         ├─ Fall back to English translations                   │
│         └─ Log error to console                                │
│                                                                 │
│  4. Missing Variable in Translation                             │
│     └─► Translation has {{name}} but no {name: 'value'} passed │
│         ├─ Leave placeholder unchanged: "Hello, {{name}}!"     │
│         └─ Log warning (in debug mode)                         │
│                                                                 │
│  5. Corrupt Translation JSON                                    │
│     └─► Invalid JSON syntax                                    │
│         ├─ Catch at load time                                  │
│         ├─ Show error message in dashboard (debug mode)        │
│         └─ Fall back to English                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

This diagram provides a complete visual reference for understanding how multilanguage support works from user interaction through backend generation and error handling.
