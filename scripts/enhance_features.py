#!/usr/bin/env python3
"""
Enhance features.json with new fields: used_by, breaks_if_missing, test_command

This script adds relationship tracking and impact analysis fields to all features.
"""

import json
import sys
from pathlib import Path

# Base path
BASE_PATH = Path(__file__).parent.parent

# Feature relationships and impact data
ENHANCEMENTS = {
    "event-scraping": {
        "used_by": ["facebook-flyer-ocr", "editor-workflow", "ai-categorization", "ai-event-extraction"],
        "breaks_if_missing": [
            "No events can be scraped from external sources",
            "Pending event queue remains empty",
            "Manual event entry becomes only option"
        ],
        "test_command": "python3 src/event_manager.py scrape && python3 tests/test_scraper.py --verbose"
    },
    "facebook-flyer-ocr": {
        "used_by": [],
        "breaks_if_missing": [
            "Facebook flyer images cannot be analyzed",
            "Manual event entry required for Facebook events"
        ],
        "test_command": "python3 tests/test_ocr_availability.py --verbose"
    },
    "editor-workflow": {
        "used_by": ["static-site-generation"],
        "breaks_if_missing": [
            "Events cannot be reviewed before publishing",
            "Malicious or invalid events may reach production",
            "No way to reject spam events"
        ],
        "test_command": "python3 src/event_manager.py list-pending && python3 src/event_manager.py list"
    },
    "python-tui": {
        "used_by": [],
        "breaks_if_missing": [
            "No interactive menu for manual event management",
            "Must use CLI commands only"
        ],
        "test_command": "python3 src/event_manager.py"
    },
    "cli-commands": {
        "used_by": ["github-environments", "telegram-bot-github-actions"],
        "breaks_if_missing": [
            "Automation and CI/CD workflows break",
            "Cannot run batch operations",
            "GitHub Actions workflows fail"
        ],
        "test_command": "python3 src/event_manager.py --help"
    },
    "interactive-map": {
        "used_by": ["geolocation-filtering", "custom-location", "map-markers", "draggable-speech-bubbles"],
        "breaks_if_missing": [
            "No visual map display of events",
            "Must use fallback list view",
            "Geolocation filtering unavailable"
        ],
        "test_command": "Open public/index.html and verify map loads with markers"
    },
    "geolocation-filtering": {
        "used_by": ["sunrise-filtering"],
        "breaks_if_missing": [
            "Cannot filter events by proximity to user",
            "All events shown regardless of distance",
            "Sunrise filtering may fail (depends on user location)"
        ],
        "test_command": "Open public/index.html and test geolocation permission prompt"
    },
    "sunrise-filtering": {
        "used_by": [],
        "breaks_if_missing": [
            "Cannot filter events by time until sunrise",
            "Extended time filters may be less useful"
        ],
        "test_command": "python3 src/modules/filter_tester.py --verbose"
    },
    "static-site-generation": {
        "used_by": ["preview-deployment", "production-deployment"],
        "breaks_if_missing": [
            "No HTML output to deploy",
            "Site cannot be published",
            "All deployment workflows fail"
        ],
        "test_command": "python3 src/event_manager.py generate && ls public/index.html"
    },
    "debug-mode": {
        "used_by": [],
        "breaks_if_missing": [
            "No debug UI for developers",
            "Harder to diagnose issues",
            "WCAG warnings not visible"
        ],
        "test_command": "Set debug=true in config.json, run generate, check dashboard debug section"
    },
    "demo-events": {
        "used_by": ["multi-data-sources"],
        "breaks_if_missing": [
            "No test data for development",
            "Empty map in development mode",
            "Harder to test features without real scraped events"
        ],
        "test_command": "Set data.source='both' in config.json, run generate, verify demo events appear"
    },
    "event-filters": {
        "used_by": ["geolocation-filtering", "sunrise-filtering", "extended-time-filters"],
        "breaks_if_missing": [
            "Cannot search or filter events",
            "All events shown at once",
            "Poor user experience with many events"
        ],
        "test_command": "python3 src/modules/filter_tester.py --verbose"
    },
    "backup-system": {
        "used_by": [],
        "breaks_if_missing": [
            "No event history preserved",
            "Cannot recover accidentally deleted events",
            "Data loss risk increases"
        ],
        "test_command": "Check backups/events/ directory for timestamped backups"
    },
    "custom-location": {
        "used_by": [],
        "breaks_if_missing": [
            "Users cannot override geolocation",
            "Privacy-conscious users stuck with browser location",
            "Cannot manually set preferred location"
        ],
        "test_command": "Open public/index.html, try custom location feature in dashboard"
    },
    "event-cards": {
        "used_by": ["interactive-map", "draggable-speech-bubbles"],
        "breaks_if_missing": [
            "Events cannot be displayed in UI",
            "Fallback list view unavailable",
            "Critical rendering failure"
        ],
        "test_command": "Open public/index.html and verify event cards render"
    },
    "map-markers": {
        "used_by": ["draggable-speech-bubbles"],
        "breaks_if_missing": [
            "Events not visible on map",
            "No clickable event locations",
            "Map appears empty"
        ],
        "test_command": "Open public/index.html and verify markers appear on map"
    },
    "dashboard-menu": {
        "used_by": ["debug-mode", "environment-watermark", "custom-location"],
        "breaks_if_missing": [
            "Cannot access app settings",
            "No debug information visible",
            "No way to change custom location"
        ],
        "test_command": "Open public/index.html and click logo to open dashboard"
    },
    "weather-dresscode": {
        "used_by": [],
        "breaks_if_missing": [
            "No weather information displayed",
            "Users cannot see what to wear",
            "Filter bar less informative"
        ],
        "test_command": "python3 src/event_manager.py scrape-weather && python3 src/event_manager.py update-weather"
    },
    "draggable-speech-bubbles": {
        "used_by": [],
        "breaks_if_missing": [
            "Speech bubbles fixed in position",
            "May overlap with other UI elements",
            "Users cannot reposition event details"
        ],
        "test_command": "Open public/index.html, click marker, try dragging speech bubble"
    },
    "telegram-bot": {
        "used_by": ["telegram-bot-github-actions"],
        "breaks_if_missing": [
            "No Telegram integration",
            "Cannot receive event submissions via Telegram",
            "Community engagement reduced"
        ],
        "test_command": "python3 src/telegram_bot/bot.py --test"
    },
    "event-archiving": {
        "used_by": [],
        "breaks_if_missing": [
            "Old events accumulate in active list",
            "Site performance degrades over time",
            "Event history not organized by month"
        ],
        "test_command": "python3 src/event_manager.py archive-monthly --dry-run"
    },
    "cdn-asset-version-tracking": {
        "used_by": ["static-site-generation"],
        "breaks_if_missing": [
            "Cannot detect upstream library updates",
            "No version verification for downloaded assets",
            "Potential security vulnerabilities from outdated libs"
        ],
        "test_command": "python3 src/event_manager.py dependencies check && python3 src/event_manager.py dependencies info"
    }
}

def enhance_features():
    """Add used_by, breaks_if_missing, and test_command to features.json"""
    
    features_path = BASE_PATH / "features.json"
    
    # Load existing features
    with open(features_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data['features'])} features from features.json")
    
    # Enhance features
    enhanced_count = 0
    for feature in data['features']:
        feature_id = feature['id']
        
        if feature_id in ENHANCEMENTS:
            enhancement = ENHANCEMENTS[feature_id]
            
            # Add new fields
            feature['used_by'] = enhancement['used_by']
            feature['breaks_if_missing'] = enhancement['breaks_if_missing']
            
            # Only override test_command if it doesn't exist or is generic
            if 'test_command' not in feature or feature.get('test_method') in ['check_files_exist', 'check_code_patterns']:
                feature['test_command'] = enhancement['test_command']
            
            enhanced_count += 1
            print(f"✓ Enhanced: {feature_id}")
        else:
            # Add empty fields for features not in ENHANCEMENTS
            if 'used_by' not in feature:
                feature['used_by'] = []
            if 'breaks_if_missing' not in feature:
                feature['breaks_if_missing'] = ["Impact not yet documented"]
            if 'test_command' not in feature:
                feature['test_command'] = f"Manual testing required for {feature['name']}"
            
            print(f"⚠ Partial enhancement: {feature_id} (needs manual review)")
    
    # Write back to file
    with open(features_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Enhanced {enhanced_count} features with full metadata")
    print(f"⚠️  {len(data['features']) - enhanced_count} features have placeholder metadata (needs manual review)")
    print(f"\n📝 Updated: {features_path}")
    
    return True

if __name__ == "__main__":
    try:
        success = enhance_features()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
