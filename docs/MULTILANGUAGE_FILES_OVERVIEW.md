# Multilanguage Support - Files Overview

## Summary

This implementation will:
- **Create**: 7 new files (~3,000 lines total)
- **Modify**: 6 existing files (~500 lines changed)
- **Total Impact**: 13 files affected

## New Files to Create

### 1. Translation Infrastructure (3 files)

#### `assets/js/i18n.js`
**Lines**: ~200
**Purpose**: Simple translation module (handrolled, no dependencies)
**Key Features**:
- Load translation JSON
- Nested key lookup
- Plural forms (zero/one/other)
- Variable interpolation
- Fallback to English

**API**:
```javascript
const i18n = new I18n('en');
await i18n.load();
i18n.t('filter.til_sunrise'); // "til sunrise"
i18n.t('filter.events', {count: 5}); // "5 events"
```

#### `assets/translations/en.json`
**Lines**: ~150
**Purpose**: English translation strings (reference language)
**Structure**:
```json
{
  "language": "en",
  "displayName": "English",
  "translations": {
    "filter": { ... },
    "dashboard": { ... },
    "time": { ... },
    "common": { ... }
  }
}
```

#### `assets/translations/de.json`
**Lines**: ~150
**Purpose**: German (Deutsch) translation strings
**Structure**: Same as en.json with German translations

#### `assets/translations/cs.json`
**Lines**: ~150
**Purpose**: Czech (Čeština) translation strings
**Structure**: Same as en.json with Czech translations

### 2. Documentation (4 files)

#### `docs/plans/20260201-multilanguage-support.md`
**Lines**: ~350
**Purpose**: Detailed 7-phase implementation plan
**Contents**:
- Objective and current state analysis
- Phase-by-phase task breakdown
- Success criteria
- Risk mitigation
- Implementation notes

#### `docs/MULTILANGUAGE_ARCHITECTURE.md`
**Lines**: ~450
**Purpose**: Technical architecture documentation
**Contents**:
- Component diagrams
- Flow diagrams
- Integration details
- API reference
- Future enhancements

#### `docs/MULTILANGUAGE_QUICK_REF.md`
**Lines**: ~300
**Purpose**: Quick reference for developers and translators
**Contents**:
- Usage examples
- Translation guidelines
- Testing checklist
- Troubleshooting

#### `docs/MULTILANGUAGE_DATA_FLOW.md`
**Lines**: ~600
**Purpose**: Visual data flow diagrams
**Contents**:
- Complete implementation flow
- Translation lookup flow
- URL routing matrix
- Error handling flow

## Files to Modify

### 1. Frontend JavaScript (3 files)

#### `assets/js/app.js`
**Current Lines**: ~800
**Lines to Add**: ~100
**Lines to Modify**: ~20

**Changes**:
```javascript
// NEW: Language detection
detectLanguageFromUrl() {
    // Parse /{lang}/{region} or /{lang}
    // Validate against supportedLanguages
    // Fall back to browser language or English
}

// NEW: Load translations
async loadTranslations() {
    this.i18n = new I18n(this.currentLanguage);
    await this.i18n.load();
    window.i18n = this.i18n; // Global access
}

// MODIFY: Constructor
constructor() {
    // ... existing code ...
    this.detectLanguageFromUrl(); // NEW
    await this.loadTranslations(); // NEW
    // ... rest of initialization ...
}

// MODIFY: applyRegionFromUrl()
applyRegionFromUrl() {
    // Update to handle /{lang}/{region} pattern
    // Extract language first, then region
    // Maintain backward compatibility with /{region}
}
```

**New State Variables**:
- `this.currentLanguage` - Detected language code
- `this.i18n` - Translation module instance

#### `assets/js/filter-description-ui.js`
**Current Lines**: ~300
**Lines to Add**: ~50
**Lines to Modify**: ~100

**Changes**:
```javascript
// BEFORE: Hardcoded strings
this.TIME_DESCRIPTIONS = {
    'sunrise': 'til sunrise',
    'sunday-primetime': "til Sunday's primetime"
};

// AFTER: Translated strings
this.TIME_DESCRIPTIONS = {
    'sunrise': () => window.i18n.t('filter.til_sunrise'),
    'sunday-primetime': () => window.i18n.t('filter.til_sunday_primetime')
};

// MODIFY: updateEventCount()
updateEventCount(count, category) {
    // Use i18n.t() with plural forms
    const text = window.i18n.t('filter.events', {count});
    // ... rest of logic ...
}

// MODIFY: updateTimeDescription()
updateTimeDescription(timeFilter) {
    const description = this.TIME_DESCRIPTIONS[timeFilter]();
    // ... rest of logic ...
}
```

**Pattern**: Replace ~20 hardcoded strings with `t()` calls

#### `assets/js/event-listeners.js`
**Current Lines**: ~600
**Lines to Add**: ~80
**Lines to Modify**: ~50

**Changes**:
```javascript
// NEW: Language switcher event listener
setupLanguageSwitcher() {
    const languageButtons = document.querySelectorAll('.lang-btn');
    languageButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const newLang = e.target.dataset.lang;
            this.changeLanguage(newLang);
        });
    });
}

// NEW: Change language function
changeLanguage(newLang) {
    const currentUrl = window.location.pathname;
    const segments = currentUrl.split('/').filter(Boolean);
    
    // Extract region if present
    const region = this.app.activeRegion;
    
    // Build new URL
    let newUrl = `/${newLang}`;
    if (region && region !== 'antarctica') {
        newUrl += `/${region}`;
    }
    
    // Redirect
    window.location.href = newUrl;
}

// MODIFY: setupTimeFilter()
setupTimeFilter() {
    // Use i18n.t() for dropdown option labels
    options.forEach(opt => {
        opt.label = window.i18n.t(`time.${opt.key}`);
    });
    // ... rest of logic ...
}

// MODIFY: setupDistanceFilter()
setupDistanceFilter() {
    // Use i18n.t() for dropdown option labels
    options.forEach(opt => {
        opt.label = window.i18n.t(`distance.${opt.key}`);
    });
    // ... rest of logic ...
}
```

**New Methods**: 2 (setupLanguageSwitcher, changeLanguage)
**Modified Methods**: 5-7 (translate dropdown options, button labels)

### 2. Frontend HTML (1 file)

#### `assets/html/dashboard-aside.html`
**Current Lines**: ~290
**Lines to Add**: ~40
**Lines to Modify**: ~80

**Changes**:

**NEW: Language switcher section** (after "About" section):
```html
<div class="dashboard-section">
  <h3>
    <i class="dashboard-section-icon" data-lucide="globe" aria-hidden="true"></i>
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

**MODIFY: Replace hardcoded text with placeholders**:
```html
<!-- BEFORE -->
<h3><i data-lucide="book-open"></i> About</h3>

<!-- AFTER -->
<h3><i data-lucide="book-open"></i> {{t.dashboard.about}}</h3>

<!-- Apply to ~30 strings across all sections -->
```

### 3. Backend Python (2 files)

#### `src/modules/site_generator.py`
**Current Lines**: ~2000
**Lines to Add**: ~200
**Lines to Modify**: ~50

**Changes**:

**NEW: Multi-language site generation**:
```python
def generate_multilanguage_sites(config, events):
    """Generate separate HTML for each supported language"""
    supported_languages = config.get('supportedLanguages', ['en'])
    
    for language in supported_languages:
        print(f"Generating site for language: {language}")
        
        # Load translation file
        translation_path = f"assets/translations/{language}.json"
        with open(translation_path) as f:
            translations = json.load(f)
        
        # Generate HTML with translations
        html = generate_html(config, events, language, translations)
        
        # Write to language-specific directory
        output_dir = f"public/{language}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/index.html"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    # Copy default language to root
    default_lang = config.get('defaultLanguage', 'en')
    shutil.copy(f"public/{default_lang}/index.html", "public/index.html")
```

**NEW: Inline translations in HTML**:
```python
def inline_translations(html, translations):
    """Embed translation JSON in HTML for instant access"""
    translation_script = f"""
    <script>
      window.TRANSLATIONS = {json.dumps(translations, ensure_ascii=False)};
    </script>
    """
    # Insert before closing </head>
    html = html.replace('</head>', f'{translation_script}\n</head>')
    return html
```

**MODIFY: generate_site() function**:
```python
def generate_site(config_path):
    # ... existing code ...
    
    # NEW: Generate multi-language sites
    generate_multilanguage_sites(config, events)
    
    # ... existing code ...
```

#### `src/modules/template_processor.py`
**Current Lines**: ~400
**Lines to Add**: ~100
**Lines to Modify**: ~30

**Changes**:

**NEW: Translation placeholder processing**:
```python
def process_translation_placeholders(template, translations):
    """Replace {{t.key}} placeholders with translated strings"""
    import re
    
    # Pattern: {{t.category.key}}
    pattern = r'\{\{t\.([a-zA-Z0-9_.]+)\}\}'
    
    def replace_translation(match):
        key = match.group(1)
        value = get_translation_value(translations, key)
        return value if value else match.group(0)  # Keep placeholder if not found
    
    return re.sub(pattern, replace_translation, template)

def get_translation_value(translations, key):
    """Navigate nested object to get translation value"""
    keys = key.split('.')
    value = translations.get('translations', {})
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return None
    
    return value
```

**MODIFY: process_template() function**:
```python
def process_template(template, context, translations=None):
    # ... existing placeholder processing ...
    
    # NEW: Process translation placeholders
    if translations:
        template = process_translation_placeholders(template, translations)
    
    return template
```

## CSS Styling (Minor Addition)

#### `assets/html/design-tokens.css`
**Lines to Add**: ~50

**NEW: Language switcher styles**:
```css
.language-switcher {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.lang-btn {
  flex: 1;
  min-width: 80px;
  padding: 8px 12px;
  border: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary);
}

.lang-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  font-weight: 500;
}

.lang-code {
  font-weight: 700;
  font-size: 14px;
}

.lang-name {
  font-size: 12px;
  color: var(--text-secondary);
}
```

## Build Output Structure

### Before (Current)
```
public/
├── index.html
└── docs/
```

### After (With Multilanguage)
```
public/
├── index.html (default English)
├── en/
│   └── index.html (explicit English)
├── de/
│   └── index.html (German)
├── cs/
│   └── index.html (Czech)
└── docs/
```

## File Size Impact

### New Files
| File | Size | Description |
|------|------|-------------|
| `assets/js/i18n.js` | ~6 KB | Translation module |
| `assets/translations/en.json` | ~4 KB | English strings |
| `assets/translations/de.json` | ~4 KB | German strings |
| `assets/translations/cs.json` | ~4 KB | Czech strings |
| Documentation (4 files) | ~80 KB | Plans, architecture, guides |

**Total New Files**: ~98 KB (90 KB is documentation)

### Modified Files
| File | Current | After | Change |
|------|---------|-------|--------|
| `assets/js/app.js` | ~30 KB | ~35 KB | +5 KB |
| `assets/js/filter-description-ui.js` | ~10 KB | ~12 KB | +2 KB |
| `assets/js/event-listeners.js` | ~25 KB | ~28 KB | +3 KB |
| `assets/html/dashboard-aside.html` | ~12 KB | ~14 KB | +2 KB |
| `src/modules/site_generator.py` | ~60 KB | ~70 KB | +10 KB |
| `src/modules/template_processor.py` | ~15 KB | ~20 KB | +5 KB |

**Total Change in Existing Files**: +27 KB

### Generated Output
| File | Size | Notes |
|------|------|-------|
| `public/index.html` (English) | ~200 KB | +5 KB for translations |
| `public/de/index.html` (German) | ~200 KB | +5 KB for translations |
| `public/cs/index.html` (Czech) | ~200 KB | +5 KB for translations |

**Total Output Impact**: +15 KB per language (inlined translations)

## Update features.json

### New Feature Entry

```json
{
  "id": "multilanguage-support",
  "name": "Multilanguage Support",
  "description": "URL-based language selection with dashboard language switcher. Supports German (de), English (en), and Czech (cs).",
  "category": "frontend",
  "implemented": true,
  "files": [
    "assets/js/i18n.js",
    "assets/translations/en.json",
    "assets/translations/de.json",
    "assets/translations/cs.json",
    "assets/js/app.js (modified)",
    "assets/js/filter-description-ui.js (modified)",
    "assets/js/event-listeners.js (modified)",
    "assets/html/dashboard-aside.html (modified)",
    "src/modules/site_generator.py (modified)",
    "src/modules/template_processor.py (modified)"
  ],
  "depends_on": ["event-scraping", "site-generator", "dashboard-menu"],
  "config_keys": ["supportedLanguages", "defaultLanguage"],
  "test_method": "check_files_exist",
  "test_file": "tests/test_multilanguage.py"
}
```

## Testing Files (To Create)

### `tests/test_multilanguage.py`
**Lines**: ~200
**Purpose**: Unit tests for i18n functionality

**Test Cases**:
- Language detection from URL
- Translation loading
- Nested key lookup
- Plural forms
- Variable interpolation
- Fallback to English
- Invalid language handling
- Missing translation key handling

## Git Commit Strategy

### Recommended Commit Sequence

1. **Phase 1: Infrastructure**
   ```
   feat(i18n): Add multilanguage translation infrastructure
   
   - Create i18n.js module
   - Create translation files (en, de, cs)
   - Update features.json
   ```

2. **Phase 2: Frontend Detection**
   ```
   feat(i18n): Add language detection and loading
   
   - Add detectLanguageFromUrl() to app.js
   - Load translations on init
   - Update URL routing for /{lang}/{region}
   ```

3. **Phase 3: UI Translation**
   ```
   feat(i18n): Translate UI components
   
   - Update filter-description-ui.js with t() calls
   - Update dashboard-aside.html with {{t.key}} placeholders
   - Update event-listeners.js for dropdown translations
   ```

4. **Phase 4: Language Switcher**
   ```
   feat(i18n): Add language switcher to dashboard
   
   - Add language switcher UI section
   - Implement language change logic
   - Add CSS styling
   ```

5. **Phase 5: Backend Generation**
   ```
   feat(i18n): Generate multi-language HTML files
   
   - Update site_generator.py for multi-language output
   - Update template_processor.py for {{t.key}} placeholders
   - Generate /en, /de, /cs subdirectories
   ```

6. **Phase 6: Testing & Docs**
   ```
   docs(i18n): Add multilanguage documentation
   
   - Add implementation plan
   - Add architecture guide
   - Add quick reference
   - Add data flow diagrams
   
   test(i18n): Add multilanguage tests
   
   - Add unit tests for i18n module
   - Add integration tests
   ```

## Dependencies

### No New External Dependencies
- ✅ **Zero npm packages** - Handrolled solution
- ✅ **Zero Python packages** - Uses standard library
- ✅ **Zero build tools** - Simple JSON parsing

### Internal Dependencies
- Existing multi-region infrastructure
- Existing template processor
- Existing site generator
- Existing event system

## Rollback Strategy

If implementation needs to be reverted:

1. **Remove new files** (7 files total):
   - `assets/js/i18n.js`
   - `assets/translations/*.json` (3 files)
   - Documentation files (can keep)

2. **Revert modified files** (6 files):
   - `git checkout main -- assets/js/app.js`
   - `git checkout main -- assets/js/filter-description-ui.js`
   - `git checkout main -- assets/js/event-listeners.js`
   - `git checkout main -- assets/html/dashboard-aside.html`
   - `git checkout main -- src/modules/site_generator.py`
   - `git checkout main -- src/modules/template_processor.py`

3. **Regenerate site**:
   - `python3 src/event_manager.py generate`

**Total Rollback Time**: < 5 minutes

## Maintenance Overhead

### Adding New Translatable Strings
1. Add to all 3 translation files (en, de, cs) - ~5 minutes
2. Use `t()` call in JavaScript or `{{t.key}}` in HTML - ~2 minutes
3. Test in all languages - ~5 minutes

**Total**: ~12 minutes per new string

### Adding New Language
1. Create `assets/translations/{lang}.json` - ~30 minutes (translate ~80 strings)
2. Add to `config.supportedLanguages` array - ~1 minute
3. Regenerate site - ~10 seconds
4. Test - ~10 minutes

**Total**: ~40 minutes per new language

### Updating Translation
1. Edit translation file - ~2 minutes
2. Regenerate site - ~10 seconds
3. Verify - ~2 minutes

**Total**: ~5 minutes per translation update

## Summary

**Impact**: Moderate (13 files affected)
**Complexity**: Low-Medium (KISS approach, no frameworks)
**Risk**: Low (backward compatible, extensive tests)
**Benefit**: High (native language support for users)
**Maintenance**: Low (simple JSON files, clear API)

Ready to implement! 🚀
