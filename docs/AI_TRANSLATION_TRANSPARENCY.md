# AI Translation Transparency System

## Overview

This document describes the system for transparently disclosing AI-generated translations to users. When event descriptions are automatically translated from the source language (usually German) to other supported languages (English, Czech), users must be informed about the translation source.

**TRANSLATION SCOPE:**
- ✅ **Event descriptions** - Full explanatory text (TRANSLATED)
- ❌ **Event titles** - Proper nouns, brand names (NOT translated)
- ❌ **Location names** - Venue names, place names (NOT translated)

**Rationale:** Event names and venue names are often proper nouns or culturally specific identifiers that should remain in the original language for authenticity and clarity.

## Ethical Principles

### Why Transparency Matters

1. **User Trust**: Users have a right to know when content has been AI-translated
2. **Quality Expectations**: AI translations may contain errors or miss cultural nuances
3. **Source Verification**: Users should be able to verify against original language if needed
4. **Best Practice**: Leading organizations (EU, Google, OpenAI) require AI content disclosure

### Legal Considerations

- **EU AI Act**: Requires disclosure of AI-generated content
- **Transparency Guidelines**: Users must be able to distinguish AI from human translations
- **Accessibility**: Disclosures must be accessible to screen readers

## Implementation Design

### Event Data Schema Extension

#### Current Schema (Monolingual)
```json
{
  "id": "event_123",
  "title": "Konzert im Park",
  "description": "Ein wunderbares Musikerlebnis...",
  "location": {
    "name": "Stadtpark"
  }
}
```

#### New Schema (Multilingual with Translation Metadata)
```json
{
  "id": "event_123",
  "title": "Konzert im Park",
  "description": "Ein wunderbares Musikerlebnis...",
  "location": {
    "name": "Stadtpark"
  },
  "translations": {
    "source_language": "de",
    "fields": {
      "description": {
        "en": {
          "text": "A wonderful music experience...",
          "method": "ai",
          "service": "duckduckgo",
          "generated_at": "2026-02-15T18:30:00Z",
          "verified": false
        },
        "cs": {
          "text": "Skvělý hudební zážitek...",
          "method": "ai",
          "service": "deepl",
          "generated_at": "2026-02-15T18:30:00Z",
          "verified": false
        }
      }
    }
  }
}
```

**Note:** Only `description` field is translated. Title and location name remain in original language.

#### Translation Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | The translated text |
| `method` | enum | Translation method: `"ai"`, `"human"`, `"manual"` |
| `service` | string | AI service used: `"duckduckgo"`, `"deepl"`, `"google"`, or `null` for human |
| `generated_at` | ISO 8601 | Timestamp when translation was created |
| `verified` | boolean | Has a human reviewed/approved this translation? |
| `verified_by` | string | (Optional) Username/email of verifier |
| `verified_at` | ISO 8601 | (Optional) When it was verified |

### UI Disclosure Methods

#### 1. Footnote Symbol (Primary Method)

**In event popups and detail views, add a small footnote indicator:**

```html
<h3 class="event-title">
  Concert in the Park
  <sup class="ai-translation-indicator" 
       aria-label="AI-translated from German"
       title="AI-translated from German using DuckDuckGo AI">†</sup>
</h3>
```

**Visual design:**
- Use dagger symbol (†) or asterisk (*)
- Small, non-intrusive (font-size: 0.7em)
- Color: `var(--color-shade-50)` (subtle but visible)
- Cursor: help (indicates hover tooltip)
- ARIA label for screen readers

#### 2. Hover Tooltip (Secondary)

**On hover/focus, show detailed information:**

```
AI Translation Notice
━━━━━━━━━━━━━━━━━━━━
Source: German (original)
Target: English
Service: DuckDuckGo AI Chat
Date: Feb 15, 2026
Status: Not yet verified

Click to view original language
```

#### 3. Footer Disclosure (Tertiary)

**At bottom of event detail, add a subtle disclosure:**

```html
<div class="translation-footer">
  <i data-lucide="info" aria-hidden="true"></i>
  <span>
    This event information was automatically translated from German using AI. 
    <a href="#" class="view-original-link">View original</a>
  </span>
</div>
```

#### 4. Language Switcher Integration

**In dashboard language switcher, show translation status:**

```
[DE] Deutsch (Original) ✓
[EN] English (AI-translated †)
[CS] Čeština (AI-translated †)
```

### Frontend Implementation

#### JavaScript Helper Functions

**File: `assets/js/i18n.js`**

```javascript
/**
 * Get translated event field with transparency metadata
 * @param {Object} event - Event object with translations
 * @param {string} field - Field name (title, description, location_name)
 * @param {string} lang - Target language code
 * @returns {Object} { text, isTranslated, metadata }
 */
getTranslatedField(event, field, lang = this.currentLang) {
    // If current language matches source language, return original
    const sourceLang = event.translations?.source_language || 'de';
    if (lang === sourceLang) {
        return {
            text: event[field],
            isTranslated: false,
            metadata: null
        };
    }
    
    // Check if translation exists
    const translation = event.translations?.fields?.[field]?.[lang];
    if (translation) {
        return {
            text: translation.text,
            isTranslated: true,
            metadata: translation
        };
    }
    
    // Fallback to original language
    return {
        text: event[field],
        isTranslated: false,
        metadata: null,
        fallback: true
    };
}

/**
 * Create AI translation indicator HTML
 * @param {Object} metadata - Translation metadata
 * @returns {string} HTML for footnote indicator
 */
createTranslationIndicator(metadata) {
    if (!metadata || metadata.method !== 'ai') {
        return '';
    }
    
    const service = metadata.service || 'AI';
    const date = new Date(metadata.generated_at).toLocaleDateString();
    const verified = metadata.verified ? '✓ Verified' : 'Not verified';
    
    const tooltip = `AI Translation Notice\nSource: ${metadata.source_language}\nService: ${service}\nDate: ${date}\nStatus: ${verified}`;
    
    return `<sup class="ai-translation-indicator" 
                 role="img"
                 aria-label="AI-translated from ${metadata.source_language}"
                 title="${tooltip}">†</sup>`;
}
```

#### Map Popup Updates

**File: `assets/js/map.js` → `createPopupContent()` method**

```javascript
createPopupContent(event) {
    const i18n = window.app?.i18n;
    const currentLang = i18n?.getCurrentLanguage() || 'en';
    
    // Get translated title with metadata
    const titleData = i18n.getTranslatedField(event, 'title', currentLang);
    const titleIndicator = i18n.createTranslationIndicator(titleData.metadata);
    
    // Get translated description with metadata
    const descData = i18n.getTranslatedField(event, 'description', currentLang);
    const descIndicator = i18n.createTranslationIndicator(descData.metadata);
    
    const popupContent = `
        <div class="event-popup">
            <h3 class="popup-title">
                ${this.escapeHtml(titleData.text)}${titleIndicator}
            </h3>
            <p class="popup-description">
                ${this.escapeHtml(descData.text)}${descIndicator}
            </p>
            ${titleData.isTranslated ? this.createTranslationFooter(event) : ''}
        </div>
    `;
    
    return popupContent;
}

/**
 * Create translation disclosure footer
 */
createTranslationFooter(event) {
    const sourceLang = event.translations?.source_language || 'de';
    const langNames = { de: 'German', en: 'English', cs: 'Czech' };
    
    return `
        <div class="translation-footer">
            <i data-lucide="info" aria-hidden="true"></i>
            <span class="translation-notice">
                AI-translated from ${langNames[sourceLang]}. 
                <button class="view-original-btn" 
                        onclick="viewOriginalLanguage('${event.id}', '${sourceLang}')">
                    View original
                </button>
            </span>
        </div>
    `;
}
```

### CSS Styling

**File: `assets/css/style.css`**

```css
/* AI Translation Indicator */
.ai-translation-indicator {
    color: var(--color-shade-50);
    font-size: 0.7em;
    margin-left: 0.2em;
    cursor: help;
    opacity: 0.7;
    transition: opacity 0.2s ease;
}

.ai-translation-indicator:hover,
.ai-translation-indicator:focus {
    opacity: 1;
}

/* Translation Footer */
.translation-footer {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    margin-top: 0.75rem;
    background: var(--color-tint-90);
    border-radius: 4px;
    font-size: 0.85rem;
    color: var(--color-shade-50);
}

.translation-footer i {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    opacity: 0.7;
}

.translation-notice {
    flex: 1;
}

.view-original-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    text-decoration: underline;
    cursor: pointer;
    font-size: inherit;
    padding: 0;
    font-family: inherit;
}

.view-original-btn:hover {
    color: var(--color-shade-50);
}

/* Dashboard Language Switcher - Show Translation Status */
.language-option[data-translated="true"]::after {
    content: " †";
    color: var(--color-shade-50);
    font-size: 0.85em;
    opacity: 0.7;
}
```

### Backend Translation System

#### Translation Service Integration

**File: `src/modules/event_translator.py`** (NEW)

```python
"""
Event Translation Module

Automatically translates event content using free AI services.
Adds transparency metadata to track translation source and method.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EventTranslator:
    """Translates event content with transparency metadata"""
    
    def __init__(self, config):
        self.config = config
        self.supported_languages = config.get('supportedLanguages', ['de', 'en', 'cs'])
        self.default_language = config.get('defaultLanguage', 'de')
        
    def translate_event(self, event: Dict, target_languages: List[str] = None) -> Dict:
        """
        Translate event content to target languages
        
        Args:
            event: Event dictionary with title, description, location.name
            target_languages: List of language codes to translate to (default: all supported)
            
        Returns:
            Event with added translations field
        """
        if target_languages is None:
            target_languages = [lang for lang in self.supported_languages 
                              if lang != self.default_language]
        
        # Detect source language (assume default if not specified)
        source_lang = event.get('translations', {}).get('source_language', self.default_language)
        
        # Initialize translations structure
        if 'translations' not in event:
            event['translations'] = {
                'source_language': source_lang,
                'fields': {}
            }
        
        # Translate each field
        fields_to_translate = [
            ('title', event.get('title')),
            ('description', event.get('description')),
            ('location_name', event.get('location', {}).get('name'))
        ]
        
        for field_name, source_text in fields_to_translate:
            if not source_text:
                continue
                
            if field_name not in event['translations']['fields']:
                event['translations']['fields'][field_name] = {}
            
            for target_lang in target_languages:
                # Skip if already translated
                if target_lang in event['translations']['fields'][field_name]:
                    logger.info(f"Skipping {field_name} for {target_lang} - already translated")
                    continue
                
                # Perform translation
                translated_text = self.translate_text(
                    text=source_text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                
                if translated_text:
                    event['translations']['fields'][field_name][target_lang] = {
                        'text': translated_text,
                        'method': 'ai',
                        'service': 'duckduckgo',  # or 'deepl'
                        'generated_at': datetime.utcnow().isoformat() + 'Z',
                        'verified': False
                    }
                    logger.info(f"Translated {field_name} to {target_lang}")
        
        return event
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text using AI service
        
        This is a placeholder - implement with actual AI service
        """
        # TODO: Implement with DuckDuckGo AI or DeepL
        logger.warning("Translation not yet implemented - returning placeholder")
        return f"[{target_lang.upper()}] {text}"
```

#### Scraper Integration

**File: `src/modules/scraper.py` → Update `scrape_all()` method**

```python
def scrape_all(self):
    """Scrape all sources with automatic translation"""
    from .event_translator import EventTranslator
    
    # Scrape events (existing logic)
    scraped_events = self._scrape_all_sources()
    
    # Initialize translator
    translator = EventTranslator(self.config)
    
    # Translate each event
    translated_events = []
    for event in scraped_events:
        try:
            translated_event = translator.translate_event(event)
            translated_events.append(translated_event)
        except Exception as e:
            logger.error(f"Translation failed for event {event.get('id')}: {e}")
            translated_events.append(event)  # Keep untranslated
    
    return translated_events
```

### Translation Strings

**Add to `assets/json/translations/*.json`:**

```json
{
  "translation_notice": {
    "ai_translated": "AI-translated from {{language}}",
    "view_original": "View original",
    "not_verified": "Not yet verified by human translator",
    "verified": "Verified by human translator",
    "service_label": "Translation service: {{service}}",
    "date_label": "Translated on {{date}}",
    "footer_text": "This content was automatically translated from {{language}} using AI.",
    "quality_disclaimer": "AI translations may contain errors. When in doubt, check the original language."
  }
}
```

## User Interface Examples

### Example 1: Event Popup (English)

```
┌──────────────────────────────────┐
│ Konzert im Park                  │
│                                  │
│ A wonderful music experience in  │
│ the city center. Join us! †      │
│                                  │
│ 📍 Stadtpark                     │
│ 🕐 Feb 20, 8:00 PM               │
│                                  │
│ ℹ️ AI-translated from German.    │
│    View original                 │
└──────────────────────────────────┘
```

**Note:** Title and location remain in original German. Only description shows † indicator.

### Example 2: Dashboard Language Switcher

```
Language / Sprache / Jazyk
━━━━━━━━━━━━━━━━━━━━━━━━━━

○ Deutsch (Original) ✓
● English (AI-translated †)
○ Čeština (AI-translated †)
```

### Example 3: Hover Tooltip

```
┌────────────────────────────────┐
│ AI Translation Notice          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Source: German (original)      │
│ Target: English                │
│ Service: DuckDuckGo AI Chat    │
│ Date: Feb 15, 2026             │
│ Status: Not yet verified       │
│                                │
│ Click to view original language│
└────────────────────────────────┘
```

## Testing Requirements

### Manual Testing Checklist

- [ ] AI translation indicator (†) visible on translated content
- [ ] Hover tooltip shows translation metadata
- [ ] Translation footer appears at bottom of translated events
- [ ] "View original" button switches to source language
- [ ] Screen readers announce "AI-translated" via ARIA labels
- [ ] Language switcher shows translation status
- [ ] No indicator on original language content
- [ ] Human-verified translations show different indicator (optional)

### Automated Tests

**File: `tests/test_translation_transparency.py`** (NEW)

```python
def test_translation_metadata_required():
    """Test that AI-translated events have required metadata"""
    event = load_test_event_with_translation()
    
    assert 'translations' in event
    assert event['translations']['source_language'] == 'de'
    assert 'fields' in event['translations']
    
    for field in ['title', 'description', 'location_name']:
        assert field in event['translations']['fields']
        en_translation = event['translations']['fields'][field]['en']
        
        assert 'text' in en_translation
        assert en_translation['method'] == 'ai'
        assert 'service' in en_translation
        assert 'generated_at' in en_translation
        assert 'verified' in en_translation

def test_transparency_indicator_in_ui():
    """Test that UI includes transparency indicators"""
    html = render_event_popup(test_event_with_translation)
    
    assert '†' in html or '*' in html  # Footnote indicator
    assert 'AI-translated' in html or 'ai-translation-indicator' in html
    assert 'View original' in html
```

## Privacy Considerations

### Data Handling

1. **No Personal Data**: Only translate public event information
2. **No Tracking**: Don't send user IDs or personal data to AI services
3. **Rate Limiting**: Respect AI service rate limits
4. **Caching**: Cache translations to minimize API calls
5. **Opt-Out**: Allow event organizers to opt out of auto-translation

### AI Service Selection

| Service | Pros | Cons | Privacy |
|---------|------|------|---------|
| DuckDuckGo AI | Free, privacy-focused | Limited features | ✅ Best |
| DeepL Free | Best quality | 500k char/month limit | ⚠️ Good |
| Google Translate | Fast, reliable | Data collection | ❌ Concern |

**Recommendation**: Use DuckDuckGo AI for maximum privacy, DeepL for quality when needed.

## Future Enhancements

### Phase 2: Human Verification

- Add "Verify Translation" button in editorial workflow
- Track which translations have been reviewed by humans
- Show different indicator for verified translations (✓ instead of †)

### Phase 3: Community Corrections

- Allow users to suggest translation improvements
- Crowdsource translation quality checks
- Build up verified translation database

### Phase 4: Context-Aware Translation

- Preserve formatting (bold, italic, links)
- Handle cultural references (holidays, idioms)
- Translate category names consistently

## References

### Standards & Guidelines

- EU AI Act (Transparency Requirements)
- WCAG 2.1 AA (Accessibility)
- ISO 17100:2015 (Translation services)
- Common Sense Media AI Transparency Guidelines

### Technical Resources

- DuckDuckGo AI Chat API (if available)
- DeepL API Documentation
- Google Translate API (reference)

---

**Last Updated:** February 2026  
**Status:** Design Phase - Implementation Pending  
**Maintained by:** KRWL> Development Team
