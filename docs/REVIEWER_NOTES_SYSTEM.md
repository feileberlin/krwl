# Reviewer Notes System for Location Ambiguity

## Overview

The Reviewer Notes System helps editors quickly identify events with ambiguous or uncertain location information that need manual verification.

## Problem Addressed

When scraping events, some location information is ambiguous:

- **"Freiheitshalle Hof"** - Is this "Freiheitshalle" venue in "Hof" city, or just the city "Hof"?
- **"Museum Berlin"** - Is this "Museum" or "Berlin"?
- **"Theater"** - Which theater? No city specified.
- **Partial addresses** - "Hauptstraße 10" without ZIP code or city

The Reviewer Notes System automatically flags these cases for manual review.

## How It Works

### 1. Automatic Confidence Scoring

During scraping, the system assigns a confidence level to each extracted location:

- **HIGH**: Full address with coordinates (e.g., "Kunstmuseum Bayreuth, Maximilianstraße 33, 95444 Bayreuth")
- **MEDIUM**: Venue name or partial address (e.g., "Freiheitshalle Hof")
- **LOW**: Only city name or default location (e.g., "Hof")
- **UNKNOWN**: No location information found

### 2. Ambiguity Detection

The system checks for common ambiguity patterns:

- Location contains both venue indicator AND city name
- Location is only a city without specific venue
- Venue name without full address
- Coordinates are estimated (not geocoded)

### 3. Automatic Flagging

Events with LOW or MEDIUM confidence, or with detected ambiguity, are automatically flagged for review.

## Using the System

### For Scrapers (Developers)

When creating custom source handlers, use the reviewer notes system:

```python
from modules.reviewer_notes import (
    ReviewerNotes,
    enhance_event_with_location_confidence
)

# Initialize reviewer notes
reviewer_notes = ReviewerNotes(base_path)

# After extracting an event
event = scrape_event_from_page(soup)

# Provide extraction details
extraction_details = {
    'has_full_address': True,      # Did you find street + ZIP + city?
    'has_venue_name': True,         # Did you find specific venue name?
    'used_default': False,          # Did you fall back to default?
    'used_geocoding': False,        # Did you use geocoding service?
    'extraction_method': 'detail_page_label',  # How was it extracted?
    'known_cities': ['Hof', 'Bayreuth', 'Selb']
}

# Enhance event with confidence metadata
event = enhance_event_with_location_confidence(
    event, reviewer_notes, extraction_details
)
```

### For Editors (Manual Review)

When reviewing pending events, look for:

1. **Review Flag**: `event['metadata']['needs_review'] == True`
2. **Review Category**: `event['metadata']['review_category'] == 'location'`
3. **Review Reason**: Explanation of why it needs review
4. **Confidence Level**: `event['metadata']['location_confidence']['level']`

Example metadata in a flagged event:

```json
{
  "id": "html_frankenpost_12345",
  "title": "Konzert im Stadtzentrum",
  "location": {
    "name": "Freiheitshalle Hof",
    "lat": 50.3167,
    "lon": 11.9167
  },
  "metadata": {
    "needs_review": true,
    "review_category": "location",
    "review_reason": "Location needs verification: venue name found; Location contains both venue indicator and city name",
    "location_confidence": {
      "level": "medium",
      "reason": "venue name found; Location contains both venue indicator and city name: 'Freiheitshalle Hof'. Unclear if this is the venue name or just the city.",
      "extraction_method": "venue_in_heading",
      "timestamp": "2026-01-16T17:00:00"
    }
  }
}
```

## Reviewing Events in the TUI

The Event Manager TUI shows flagged events:

```bash
python3 src/event_manager.py
```

When reviewing pending events, you'll see indicators:

```
Pending Events (5 total, 2 need review)

1. [⚠ NEEDS REVIEW] Konzert im Stadtzentrum
   Location: Freiheitshalle Hof (confidence: medium)
   Reason: Location contains both venue indicator and city name
   → Review and correct if needed

2. Summer Festival
   Location: Bayreuth Hofgarten (confidence: high)
   → Looks good

3. [⚠ NEEDS REVIEW] Art Exhibition
   Location: Hof (confidence: low)
   Reason: Only city name, no specific venue
   → Needs venue details
```

## Configuration

No configuration needed - the system works automatically when:

1. The custom source handler uses the reviewer notes API
2. The base_path is provided when initializing the scraper

## Files

- **`src/modules/reviewer_notes.py`** - Main reviewer notes system
- **`assets/json/reviewer_notes.json`** - Stored notes (auto-created)
- **Event metadata** - Confidence data stored directly in events

## API Reference

### ReviewerNotes Class

```python
class ReviewerNotes:
    def __init__(self, base_path: Path)
    
    def add_location_confidence(event, confidence, reason, extraction_method)
    def flag_for_review(event, reason, category='location')
    def add_reviewer_note(event_id, note, reviewer='scraper')
    def get_reviewer_notes(event_id)
    def get_events_needing_review(category=None)
```

### LocationExtractionHelper Class

```python
class LocationExtractionHelper:
    @staticmethod
    def detect_ambiguous_location(location_name, known_cities)
    
    @staticmethod
    def calculate_confidence(location, has_full_address, has_venue_name, 
                            used_default, used_geocoding)
    
    @staticmethod
    def should_flag_for_review(confidence, ambiguity_reason=None)
```

### Helper Function

```python
def enhance_event_with_location_confidence(event, reviewer_notes, extraction_details)
```

## Examples

### Example 1: High Confidence (No Review Needed)

```python
event = {
    "title": "Art Exhibition",
    "location": {
        "name": "Kunstmuseum Bayreuth, Maximilianstraße 33, 95444 Bayreuth",
        "lat": 49.944,
        "lon": 11.576
    }
}

extraction_details = {
    'has_full_address': True,
    'has_venue_name': True,
    'used_default': False,
    'used_geocoding': True,
    'extraction_method': 'address_pattern',
    'known_cities': ['Bayreuth', 'Hof']
}

# Result: confidence = HIGH, no review flag
```

### Example 2: Medium Confidence (Review Needed - Ambiguous)

```python
event = {
    "title": "Concert",
    "location": {
        "name": "Freiheitshalle Hof",
        "lat": 50.3167,
        "lon": 11.9167
    }
}

extraction_details = {
    'has_full_address': False,
    'has_venue_name': True,
    'used_default': False,
    'used_geocoding': False,
    'extraction_method': 'venue_in_heading',
    'known_cities': ['Bayreuth', 'Hof']
}

# Result: confidence = MEDIUM
# Ambiguity: "Contains both venue indicator and city name"
# → Flagged for review
```

### Example 3: Low Confidence (Review Needed - Insufficient Info)

```python
event = {
    "title": "Theater Show",
    "location": {
        "name": "Hof",
        "lat": 50.3167,
        "lon": 11.9167
    }
}

extraction_details = {
    'has_full_address': False,
    'has_venue_name': False,
    'used_default': False,
    'used_geocoding': False,
    'extraction_method': 'city_name_only',
    'known_cities': ['Bayreuth', 'Hof']
}

# Result: confidence = LOW
# Reason: "Only city name without specific venue"
# → Flagged for review
```

## Future Enhancements

Potential improvements:

1. **Geocoding Integration** - Use Nominatim/Google Maps for precise coordinates
2. **Venue Database** - Maintain database of known venues with coordinates
3. **ML-based Ambiguity Detection** - Machine learning to detect edge cases
4. **Batch Review Interface** - Web UI for reviewing multiple flagged events
5. **Auto-correction Suggestions** - Suggest corrections based on similar past events

## See Also

- **Custom Source Manager** - `src/modules/custom_source_manager.py`
- **Frankenpost Custom Scraper** - `src/modules/smart_scraper/sources/frankenpost.py`
- **Event Schema** - `src/modules/models.py`
- **Editorial Workflow** - `src/modules/editor.py`
