# Location Detection Fix - Complete Solution Summary

## Problem Statement

Events from the "Frankenpost" source (Regionalzeitung) were displaying incorrect locations:
- Location name set to "Frankenpost" (the source name itself)
- Or generic "Hof" (default city)
- Instead of actual venue names and addresses

**Root Cause**: Location information exists on detail pages, but the scraper was only reading the listing page.

## Solution Overview

This PR implements a comprehensive 3-part solution:

### 1. Custom Frankenpost Scraper (Fixes Core Issue)
**File**: `src/modules/smart_scraper/sources/frankenpost.py`

**What it does**:
- Two-step scraping: Listing page → Detail pages
- Extracts venue information from detail pages using 3 strategies:
  1. **Label extraction**: Finds "Ort:", "Veranstaltungsort:", "Adresse:" labels
  2. **Address patterns**: Regex for German addresses (Street Number, ZIP City)
  3. **Venue names**: Looks for venue indicators in headings (Halle, Museum, Schloss, etc.)
- Estimates coordinates using city lookup table

**Result**: Events now get proper venue names like:
- ✅ "Kunstmuseum Bayreuth, Maximilianstraße 33, 95444 Bayreuth"
- ✅ "Freiheitshalle Hof"
- ✅ "Schloss Carolinenruhe, Colmdorf 8, 95448 Bayreuth"

Instead of:
- ❌ "Frankenpost"
- ❌ "Hof"

### 2. Custom Source Manager (Makes Future Sources Easy)
**File**: `src/modules/custom_source_manager.py`

**What it does**:
- CLI tool to generate custom source handlers from templates
- Supports 3 scraping strategies:
  - Detail page scraping (like Frankenpost)
  - Listing page scraping (all info on one page)
  - API scraping (JSON endpoints)
- Auto-generates documentation
- Includes testing utilities

**Usage**:
```bash
# Create a new custom source
python3 src/modules/custom_source_manager.py create MyNewSource \
  --url https://example.com/events \
  --location-strategy detail_page

# List all custom sources
python3 src/modules/custom_source_manager.py list

# Test a source
python3 src/modules/custom_source_manager.py test MyNewSource
```

**Result**: Anyone can add new sources without deep knowledge of the scraper architecture!

### 3. Reviewer Notes System (Handles Edge Cases)
**Files**: 
- `src/modules/reviewer_notes.py`
- `docs/REVIEWER_NOTES_SYSTEM.md`

**What it does**:
- Automatically detects ambiguous location extractions
- Assigns confidence scores (HIGH/MEDIUM/LOW/UNKNOWN)
- Flags events for manual review
- Addresses edge cases like "Freiheitshalle Hof":
  - Is it "Freiheitshalle" venue in "Hof" city?
  - Or just the city "Hof"?

**How it works**:
1. During scraping, tracks extraction quality
2. Detects ambiguity patterns:
   - Location contains both venue indicator AND city name
   - Only city without venue
   - Venue without full address
3. Adds metadata to events:
   ```json
   {
     "metadata": {
       "needs_review": true,
       "location_confidence": {
         "level": "medium",
         "reason": "Location contains both venue indicator and city name"
       }
     }
   }
   ```
4. Editors see flagged events in review interface

**Result**: Editors can quickly identify and verify ambiguous locations!

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Event Scraping Workflow                       │
└─────────────────────────────────────────────────────────┘

1. Scrape Listing Page
   ↓
2. Extract Event Links + Dates
   ↓
3. Fetch Detail Pages (one by one)
   ↓
4. Extract Location Using 3 Strategies:
   │
   ├─→ Strategy 1: Find location labels
   │   (Ort:, Adresse:, Veranstaltungsort:)
   │
   ├─→ Strategy 2: Extract address patterns
   │   (Street Number, ZIP City)
   │
   └─→ Strategy 3: Find venue in headings
       (Museum, Halle, Schloss, etc.)
   ↓
5. Calculate Location Confidence
   │
   ├─→ HIGH: Full address + coordinates
   ├─→ MEDIUM: Venue name or partial address
   ├─→ LOW: Only city name
   └─→ UNKNOWN: No location found
   ↓
6. Detect Ambiguity
   │
   ├─→ Venue + City in same string?
   ├─→ Only city without venue?
   └─→ Venue without address?
   ↓
7. Flag for Review (if needed)
   │
   └─→ Add metadata for editors
   ↓
8. Save to Pending Events
```

## Configuration

Add Frankenpost source to `config.json`:

```json
{
  "name": "Frankenpost",
  "url": "https://event.frankenpost.de/index.php?kat=&community=95028+Hof&range=50",
  "type": "frankenpost",  // ← Uses custom handler
  "enabled": true,
  "options": {
    "category": "community",
    "default_location": {
      "name": "Hof",
      "lat": 50.3167,
      "lon": 11.9167
    }
  }
}
```

The custom handler is automatically registered in SmartScraper when the source name contains "frankenpost".

## Usage

### For Developers

When creating new custom sources:

```bash
# Generate source handler template
python3 src/modules/custom_source_manager.py create NewSource \
  --url https://example.com \
  --location-strategy detail_page

# Edit the generated file:
# - Customize CSS selectors
# - Add known locations
# - Configure extraction patterns

# Test it
python3 src/modules/custom_source_manager.py test NewSource

# Add to config.json
# Run scraper
python3 src/event_manager.py scrape
```

### For Editors

When reviewing events:

1. Open TUI: `python3 src/event_manager.py`
2. Navigate to "Review Pending Events"
3. Look for `[⚠ NEEDS REVIEW]` indicators
4. Check `location_confidence` metadata
5. Verify and correct flagged locations
6. Approve or reject events

## Testing

Run tests to validate location extraction:

```bash
# Test Frankenpost location extraction
python3 tests/test_frankenpost_location.py

# Test general scraper functionality
python3 tests/test_scraper.py --verbose

# Test with real events
python3 src/event_manager.py scrape
```

## Benefits

### 1. Immediate Fix
- Frankenpost events now get proper venue locations
- No more "Regionalzeitung" or generic "Hof" locations

### 2. Scalable Solution
- Custom Source Manager makes adding new sources trivial
- Templates include location extraction best practices
- No GitHub Copilot required for future sources

### 3. Quality Assurance
- Reviewer Notes System catches edge cases
- Automatic confidence scoring
- Editors can quickly focus on problematic events

### 4. Maintainable
- Well-documented with comprehensive guides
- Modular design (separate concerns)
- Easy to extend and customize

## Files Changed/Added

### Core Implementation
- `src/modules/smart_scraper/sources/frankenpost.py` ⭐ Custom Frankenpost scraper
- `src/modules/smart_scraper/core.py` - Registered custom handler
- `src/modules/smart_scraper/sources/__init__.py` - Exports

### Tools & Utilities
- `src/modules/custom_source_manager.py` ⭐ Source handler generator
- `src/modules/reviewer_notes.py` ⭐ Reviewer notes system

### Documentation
- `docs/REVIEWER_NOTES_SYSTEM.md` - Complete guide for reviewer system
- `docs/source_templates/` - Auto-generated guides (created by manager)

### Tests
- `tests/test_frankenpost_location.py` - Location extraction tests

## Future Enhancements

Potential improvements (not in this PR):

1. **Geocoding Integration**
   - Use Nominatim/Google Maps API for precise coordinates
   - Replace coordinate estimation with real geocoding

2. **Venue Database**
   - Maintain database of known venues
   - Auto-correct common venues (Freiheitshalle, Kunstmuseum, etc.)

3. **ML-based Location Extraction**
   - Train model on corrected events
   - Auto-improve extraction patterns

4. **Web UI for Review**
   - Batch review interface
   - Side-by-side comparison
   - One-click corrections

## Questions?

See documentation:
- **Reviewer Notes System**: `docs/REVIEWER_NOTES_SYSTEM.md`
- **Custom Source Manager**: Run `python3 src/modules/custom_source_manager.py --help`
- **General Scraping**: `.github/copilot-instructions.md` (Scraping section)

## Summary

This PR completely solves the Frankenpost location issue AND provides tools to prevent similar issues with future sources. The three-part solution (custom scraper + source manager + reviewer notes) creates a robust, maintainable system for event location extraction.

✅ **Problem Solved**: Frankenpost events now display correct venue locations
✅ **Future-Proofed**: Easy to add new sources without deep technical knowledge
✅ **Quality Assured**: Automatic flagging of ambiguous cases for review
