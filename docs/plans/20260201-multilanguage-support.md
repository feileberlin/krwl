# Plan: Multilanguage Support Implementation

## Objective
Implement multilanguage support for the KRWL> Events website with:
- URL-based language selection (e.g., `/en`, `/de`, `/cs`)
- Language switcher in dashboard menu
- Support for 3 languages: German (de), English (en), Czech (cs)
- KISS principles: minimal changes, vanilla JavaScript, reuse existing patterns
- Leverage existing multi-region infrastructure pattern

## Current State Analysis

### Existing Infrastructure
✅ **Config Structure**: `supportedLanguages: ["de", "en", "cs"]` already exists in config.json
✅ **URL Pattern**: Multi-region system already uses URL path segments (`/hof`, `/nbg`, etc.)
✅ **Pattern to Follow**: `applyRegionFromUrl()` method provides routing model
✅ **English Only**: All UI strings are currently in English (not German as initially suspected)

### Key Files Involved
- **Frontend**: 
  - `assets/js/app.js` - Add language detection (similar to region detection)
  - `assets/js/filter-description-ui.js` - Filter text descriptions
  - `assets/js/event-listeners.js` - Button labels, time filters
  - `assets/html/dashboard-aside.html` - Dashboard menu (add language switcher)
  - `assets/html/filter-nav.html` - Filter bar
- **Backend**:
  - `src/modules/site_generator.py` - Generate language-specific HTML pages
  - `src/modules/template_processor.py` - Process translation placeholders
- **New Files**:
  - `assets/translations/` - Translation JSON files (de.json, en.json, cs.json)
  - `assets/js/i18n.js` - Simple translation module (< 200 lines)

### Strings to Translate (from Analysis)

**Filter Bar** (filter-nav.html, filter-description-ui.js):
- "0 events", "1 event", "N events"
- "til sunrise", "til Sunday's primetime", "til full moon"
- "within 30 min walk", "within 30 min bicycle ride", "within 30 min public transport", "within 60 min car sharing"
- "from here"
- "upcoming"

**Dashboard** (dashboard-aside.html):
- Section titles: "About", "Custom Locations", "Debug Cockpit", "Contact", "Submit Event Flyer", "Maintainer", "Documentation", "Credits & Attribution"
- Form labels: "Your Name", "Your Email", "Message", "Send Message", "Event Flyer", "Upload Flyer"
- Debug labels: "Deployment", "Data & Performance", "Warnings", "WCAG AA Compliance"
- Debug fields: "Commit", "Author", "Date", "Message", "Deployed", "Environment", "Published Events", "Pending Events", "Archived Events", "HTML Size", "Caching", "DOM Cache"

**Event Listeners** (event-listeners.js):
- Time filter options with dates/times
- Distance filter descriptions
- Status messages

## Architecture Decision

### URL Structure
Follow existing region pattern but add language prefix:
- `/{lang}` - Language-only (e.g., `/en`, `/de`, `/cs`) → Shows default region (Antarctica)
- `/{lang}/{region}` - Language + region (e.g., `/en/hof`, `/de/nbg`, `/cs/bth`)
- `/` - Root path → Auto-detect browser language or fallback to English

**Example URLs**:
- `krwl.in/` → Auto-detect language, show Antarctica
- `krwl.in/en` → English, Antarctica showcase
- `krwl.in/de` → German, Antarctica showcase
- `krwl.in/en/hof` → English, Hof view
- `krwl.in/de/nbg` → German, Nürnberg view
- `krwl.in/cs/bth` → Czech, Bayreuth view

### Translation File Structure
JSON format for easy parsing and KISS approach:

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
      "from_here": "from here",
      "upcoming": "upcoming"
    },
    "dashboard": {
      "about": "About",
      "custom_locations": "Custom Locations",
      "contact": "Contact",
      "your_name": "Your Name",
      "your_email": "Your Email"
    }
  }
}
```

### i18n Module Design (KISS)
Simple translation module without dependencies:
- Load translation JSON on page load
- Store current language in app state
- Provide `t(key)` function for lookups
- Support plural forms (zero/one/other)
- Support variable interpolation `{{var}}`
- No complex features (no date/time formatting, no RTL, etc.)

## Phase 1: Create Translation Infrastructure

### Task 1.1: Create i18n Module
- [ ] Create `assets/js/i18n.js` with simple translation class
- [ ] Support JSON loading
- [ ] Support nested keys (e.g., `t('filter.til_sunrise')`)
- [ ] Support pluralization (zero/one/other)
- [ ] Support variable interpolation `{{variable}}`
- [ ] Export global `window.I18n` for other modules

### Task 1.2: Create Translation Files
- [ ] Create `assets/translations/` directory
- [ ] Create `assets/translations/en.json` (current English strings)
- [ ] Create `assets/translations/de.json` (German translations)
- [ ] Create `assets/translations/cs.json` (Czech translations)
- [ ] Add all identified strings with proper nesting

### Task 1.3: Update features.json
- [ ] Add new feature entry for `multilanguage-support`
- [ ] Dependencies: `event-scraping`, `site-generator`
- [ ] Files: `assets/js/i18n.js`, `assets/translations/*.json`
- [ ] Config keys: `supportedLanguages`

## Phase 2: Implement Frontend Language Detection

### Task 2.1: Add Language Detection to app.js
- [ ] Create `detectLanguageFromUrl()` method (similar to `applyRegionFromUrl()`)
- [ ] Parse URL structure: `/{lang}` or `/{lang}/{region}`
- [ ] Validate language against `supportedLanguages` array
- [ ] Fall back to browser language detection (`navigator.language`)
- [ ] Default to English if unsupported language
- [ ] Store language in `this.currentLanguage`

### Task 2.2: Load Translation on Init
- [ ] Load i18n module in app.js constructor
- [ ] Initialize i18n with detected language
- [ ] Fetch translation JSON file
- [ ] Handle loading errors gracefully (fallback to English)

### Task 2.3: Update URL Handling
- [ ] Modify `applyRegionFromUrl()` to support `/{lang}/{region}` pattern
- [ ] Update region detection to work after language extraction
- [ ] Maintain backward compatibility with existing `/region` URLs
- [ ] Update `history.replaceState()` to preserve language path

## Phase 3: Translate UI Components

### Task 3.1: Translate Filter Bar
- [ ] Update `filter-description-ui.js` to use `t()` function
- [ ] Replace hardcoded strings in `TIME_DESCRIPTIONS` object
- [ ] Replace hardcoded strings in `DISTANCE_DESCRIPTIONS` object
- [ ] Update `updateEventCount()` to use translated plurals
- [ ] Update `updateTimeDescription()` for translated time ranges
- [ ] Update `updateDistanceDescription()` for translated distances

### Task 3.2: Translate Dashboard Menu
- [ ] Update `dashboard-aside.html` to use translation placeholders
- [ ] Add placeholders like `{{t.dashboard.about}}`
- [ ] Update template processor to support translation placeholders
- [ ] Translate section titles
- [ ] Translate form labels
- [ ] Translate debug section labels

### Task 3.3: Translate Event Listeners
- [ ] Update `event-listeners.js` to use `t()` function
- [ ] Translate time filter dropdown options
- [ ] Translate distance filter dropdown options
- [ ] Translate button aria-labels for accessibility
- [ ] Translate status/error messages

## Phase 4: Add Language Switcher UI

### Task 4.1: Design Language Switcher Component
- [ ] Add language switcher section to `dashboard-aside.html`
- [ ] Position after "About" section (high visibility)
- [ ] Use flag icons or language codes (de/en/cs)
- [ ] Style consistent with existing dashboard sections
- [ ] Add aria-labels for accessibility

### Task 4.2: Implement Language Switcher Logic
- [ ] Add event listener for language switcher in `event-listeners.js`
- [ ] On language change: update URL path
- [ ] Preserve current region in URL (e.g., `/en/hof` → `/de/hof`)
- [ ] Reload page with new language (simple approach, no SPA complexity)
- [ ] Store language preference in localStorage (optional enhancement)

### Task 4.3: Visual Feedback
- [ ] Highlight current language in switcher
- [ ] Add visual indicator (checkmark or bold text)
- [ ] Update dashboard close button to preserve language

## Phase 5: Backend Site Generation

### Task 5.1: Generate Multi-Language HTML Files
- [ ] Update `site_generator.py` to generate separate HTML per language
- [ ] Generate `/public/index.html` (default English)
- [ ] Generate `/public/de/index.html` (German)
- [ ] Generate `/public/cs/index.html` (Czech)
- [ ] Generate `/public/en/index.html` (explicit English)
- [ ] Each file embeds appropriate translation JSON inline

### Task 5.2: Update Template Processor
- [ ] Add support for `{{t.key}}` placeholder format
- [ ] Replace translation placeholders during generation
- [ ] Inline appropriate translation JSON in each HTML file
- [ ] Update `<html lang="">` attribute per language
- [ ] Update meta tags (description, title) per language

### Task 5.3: Update Build Script
- [ ] Modify `event_manager.py generate` command to create all language versions
- [ ] Copy static assets to each language subdirectory
- [ ] Update deployment workflow if needed
- [ ] Test all language versions generate correctly

## Phase 6: GitHub Pages Routing

### Task 6.1: Update 404.html for SPA Routing
- [ ] Update `404.html` to handle `/{lang}` and `/{lang}/{region}` paths
- [ ] Extract language from URL before region
- [ ] Store both in sessionStorage
- [ ] Redirect to appropriate language HTML file

### Task 6.2: Test URL Patterns
- [ ] Test `/en` redirects to `/en/index.html`
- [ ] Test `/en/hof` loads English with Hof region
- [ ] Test `/de/nbg` loads German with Nürnberg region
- [ ] Test invalid language falls back to English
- [ ] Test backward compatibility with `/hof` (no language prefix)

## Phase 7: Testing & Documentation

### Task 7.1: Manual Testing
- [ ] Test language detection from URL
- [ ] Test browser language detection (no URL language)
- [ ] Test language switcher in dashboard
- [ ] Test all translations render correctly
- [ ] Test filter descriptions in all languages
- [ ] Test dashboard content in all languages
- [ ] Test region + language combinations

### Task 7.2: Update Documentation
- [ ] Update README.md with multilanguage info
- [ ] Document URL structure in docs/
- [ ] Create ADR for multilanguage architecture
- [ ] Update features.json with implementation status
- [ ] Add translation contribution guide

### Task 7.3: Create Tests
- [ ] Add test for language detection
- [ ] Add test for translation loading
- [ ] Add test for plural forms
- [ ] Add test for variable interpolation
- [ ] Update existing tests to handle language param

## Success Criteria

- [ ] All 3 languages (de, en, cs) fully translated
- [ ] URL-based language selection works (`/en`, `/de`, `/cs`)
- [ ] Language + region combinations work (`/en/hof`, `/de/nbg`)
- [ ] Language switcher appears in dashboard menu
- [ ] Current language highlighted in switcher
- [ ] All filter descriptions translated
- [ ] All dashboard content translated
- [ ] Browser language detection works for root path
- [ ] Backward compatibility maintained for existing URLs
- [ ] All tests pass
- [ ] Documentation updated
- [ ] features.json updated
- [ ] Zero JavaScript errors in console
- [ ] Accessible (proper lang attributes, aria-labels)

## Technical Constraints

### KISS Principles
- ✅ No external i18n libraries (handrolled < 200 lines)
- ✅ Simple JSON translation files
- ✅ No complex interpolation (just `{{var}}` replacement)
- ✅ No date/time formatting (keep using existing utils)
- ✅ Page reload on language switch (no SPA complexity)

### Backward Compatibility
- ✅ Existing `/region` URLs still work (default to English)
- ✅ Root `/` detects browser language or defaults to English
- ✅ Existing bookmarks continue to work

### Performance
- ✅ Inline translations in HTML (no extra HTTP requests)
- ✅ Minimal JavaScript overhead (< 5KB minified)
- ✅ No runtime translation lookups (precompiled in HTML where possible)

## Implementation Notes

### Language Detection Priority
1. URL path (`/en`, `/de`, `/cs`)
2. Browser language (`navigator.language`)
3. Default to English

### Translation Key Naming Convention
Use dot notation with category prefixes:
- `filter.*` - Filter bar related
- `dashboard.*` - Dashboard menu related
- `time.*` - Time-related strings
- `distance.*` - Distance-related strings
- `common.*` - Shared/common strings

### Plural Forms
Support ICU plural rules for German, English, Czech:
- `events_zero` - No events
- `events_one` - 1 event
- `events_other` - 2+ events

### Future Enhancements (Out of Scope)
- Date/time formatting per locale
- Number formatting per locale
- RTL language support
- Language preference cookie
- Per-region language defaults
- Translation management UI
- Crowdsourced translations
- Dynamic translation loading

## Dependencies

### External
- None (handrolled i18n)

### Internal
- Existing multi-region infrastructure
- Existing URL routing pattern
- Template processor
- Site generator

## Rollout Strategy

1. **Phase 1-2**: Create infrastructure (no visible changes)
2. **Phase 3**: Replace English strings with `t()` calls (no visible changes if translations match)
3. **Phase 4**: Add language switcher (visible to users)
4. **Phase 5-6**: Deploy multi-language HTML files
5. **Phase 7**: Testing and polish

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Translation quality | Start with Google Translate, refine later |
| URL routing complexity | Follow existing region pattern closely |
| Breaking existing URLs | Maintain backward compatibility, test extensively |
| Performance impact | Inline translations, minimal JS overhead |
| Browser compatibility | Use vanilla JS, no modern features required |

## Open Questions

1. Should root `/` detect browser language or always default to English?
   - **Decision**: Detect browser language, fallback to English
2. Should we store language preference in localStorage?
   - **Decision**: Not in initial implementation (keep it simple)
3. Should existing `/region` URLs redirect to `/en/region`?
   - **Decision**: No redirect, just default to English silently
4. Should translation files be committed or generated?
   - **Decision**: Committed (easier to review and edit)

## References

- Multi-region infrastructure: `docs/MULTI_REGION_INFRASTRUCTURE.md`
- URL routing: `applyRegionFromUrl()` in `assets/js/app.js`
- Config: `config.json` line 610 (`supportedLanguages`)
- Template processor: `src/modules/template_processor.py`
- Site generator: `src/modules/site_generator.py`
