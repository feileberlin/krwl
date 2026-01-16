#!/usr/bin/env python3
"""
Generate demo events with dynamic timestamps relative to current time.

FEATURE: Dynamic Event Templates with Relative Times
PURPOSE: Create demo events that always display accurate relative times like 
         "happening now" or "starting in 5 minutes" without manual updates

HOW IT WORKS:
1. Loads real events from production as templates for realistic demo data
2. Generates demo events with both:
   - Static timestamps (for backward compatibility)
   - relative_time field (for dynamic processing by frontend)

RELATIVE TIME TYPES:
1. "offset" - Relative to current time
   Example: {"type": "offset", "minutes": -30, "duration_hours": 2}
   Creates event that started 30 minutes ago, lasting 2 hours

2. "sunrise_relative" - Relative to next sunrise (simplified as 6:00 AM)
   Example: {"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}
   Creates event starting 2 hours before sunrise, ending 1 hour after

TIMEZONE SUPPORT:
Includes timezone-aware test cases to ensure proper international time handling.
Timezone offset example: {"timezone_offset": 1} generates "2026-01-02T14:07:41+01:00"

USAGE:
    python3 scripts/generate_demo_events.py > data/events.demo.json

FRONTEND INTEGRATION:
The frontend's processTemplateEvents() method in assets/js/app.js detects 
events with relative_time and calculates actual timestamps at page load.

See README.md section "Advanced Features > Dynamic Event Templates" for complete documentation.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random

DEMO_PLACEHOLDER_TITLE = "Test Community Gathering"
DEMO_PLACEHOLDER_TITLE_REPLACEMENT = "Community Meetup at Test Venue"
DEMO_PLACEHOLDER_DESCRIPTION_PHRASE = "test event for approval flow testing"
DEMO_PLACEHOLDER_DESCRIPTION_REPLACEMENT = "Friendly community meetup with introductions, snacks, and local tips."

def cleanup_old_files(base_dir="."):
    """Remove old unnecessary files before generating new ones."""
    base_path = Path(base_dir)
    
    # List of old files to remove if they exist
    old_files = [
        # Old backup/temporary demo files (but NOT the main demo file)
        "data/events.demo.json.old",
        # Old backup files
        "data/events.backup.json",
        "assets/json/events.json.backup",
        "data/pending_events.json.backup",
        "examples/events_example.json.old",
        "examples/pending_events_example.json.old",
        # Any other temporary files
        "data/events.tmp.json",
    ]
    
    removed = []
    for old_file in old_files:
        file_path = base_path / old_file
        if file_path.exists():
            file_path.unlink()
            removed.append(old_file)
    
    if removed:
        print(f"# Cleaned up {len(removed)} old demo/backup files:", file=sys.stderr)
        for f in removed:
            print(f"#   - {f}", file=sys.stderr)
    
    return removed

def load_real_events(base_dir="."):
    """Load real events from production data as templates."""
    base_path = Path(base_dir)
    
    # Try multiple locations for events file (prefer data/assets over static)
    possible_paths = [
        base_path / "data" / "events.json",
        base_path / "assets" / "json" / "events.json",
        base_path / "static" / "events.json",
        base_path / "events.json",
    ]
    
    for events_path in possible_paths:
        if events_path.exists():
            try:
                with open(events_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    events = data.get('events', [])
                    if events:
                        print(f"# Loaded {len(events)} real events from {events_path}", file=sys.stderr)
                        return events
            except Exception as e:
                print(f"# Error loading {events_path}: {e}", file=sys.stderr)
    
    print("# No real events found, using hardcoded templates", file=sys.stderr)
    return None

def create_demo_event_from_template(template, event_id, time_offset, now):
    """Create a demo event based on a real event template."""
    
    def fmt(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Calculate event times based on offset
    start_time = now + time_offset
    
    # Preserve original event duration if possible
    if 'start_time' in template and 'end_time' in template:
        try:
            orig_start = datetime.fromisoformat(template['start_time'].replace('Z', ''))
            orig_end = datetime.fromisoformat(template['end_time'].replace('Z', ''))
            duration = orig_end - orig_start
        except:
            duration = timedelta(hours=2)  # default duration
    else:
        duration = timedelta(hours=2)
    
    end_time = start_time + duration
    
    # Create demo event preserving template structure
    demo_event = {
        "id": event_id,
        "title": f"[DEMO] {template.get('title', 'Demo Event')}",
        "description": template.get('description', 'Demo event based on real data.'),
        "location": template.get('location', {
            "name": "Demo Location",
            "lat": 50.3167,
            "lon": 11.9167
        }),
        "start_time": fmt(start_time),
        "end_time": fmt(end_time),
        "url": template.get('url', 'https://example.com/demo'),
        "source": "demo",
        "status": "published",
        "published_at": fmt(now)
    }
    
    return demo_event

def normalize_demo_template(template):
    """Normalize template text for more appealing demo content."""
    title = template.get("title", "Demo Event")
    description = template.get("description", "Demo event based on real data.")

    if DEMO_PLACEHOLDER_TITLE in title:
        title = DEMO_PLACEHOLDER_TITLE_REPLACEMENT

    if DEMO_PLACEHOLDER_DESCRIPTION_PHRASE in description.lower():
        description = DEMO_PLACEHOLDER_DESCRIPTION_REPLACEMENT

    return title, description

def generate_demo_events_from_templates(real_events, now):
    """Generate demo events using real events as templates with relative time specifications."""
    
    def fmt(dt):
        """Format datetime to ISO 8601 string."""
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    def fmt_tz(dt, tz_offset_hours=0):
        """Format datetime with timezone offset for testing."""
        if tz_offset_hours == 0:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            # Add timezone offset for testing
            sign = '+' if tz_offset_hours >= 0 else '-'
            hours = abs(int(tz_offset_hours))
            minutes = int((abs(tz_offset_hours) % 1) * 60)
            return dt.strftime(f"%Y-%m-%dT%H:%M:%S{sign}{hours:02d}:{minutes:02d}")
    
    # Calculate next sunrise (simplified: 6 AM)
    next_sunrise = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour < 6:
        next_sunrise = now.replace(hour=6, minute=0, second=0, microsecond=0)
    
    # Define useful time scenarios for testing (expanded with sunrise edge cases and timezone tests)
    # Format:
    #   (offset, suffix, title_label, description, tz_offset, relative_time_spec)
    #   (offset, suffix, title_label, description, tz_offset)
    #   (offset, suffix, title_label, description)
    time_scenarios = [
        # Current time scenarios (basic functionality)
        (timedelta(minutes=-30), "happening_now", "Live now", "Live now — drop in for the current highlights", 0, {"type": "offset", "minutes": -30, "duration_hours": 2}),
        (timedelta(minutes=-5), "started_5min_ago", "Just started", "Just started — doors opened a few minutes ago", 0, {"type": "offset", "minutes": -5, "duration_hours": 2}),
        (timedelta(minutes=5), "starting_5min", "Starts in 5 min", "Starts in 5 minutes — grab your spot", 0, {"type": "offset", "minutes": 5, "duration_hours": 2}),
        (timedelta(minutes=15), "starting_15min", "Starts in 15 min", "Starts in 15 minutes — meet at the entrance", 0, {"type": "offset", "minutes": 15, "duration_hours": 2}),
        (timedelta(minutes=30), "starting_30min", "Starts in 30 min", "Starts in 30 minutes — settle in with a quick coffee", 0, {"type": "offset", "minutes": 30, "duration_hours": 2}),
        (timedelta(hours=1), "in_1hour", "Starts in 1 hour", "Starts in 1 hour — plan your evening ahead", 0, {"type": "offset", "hours": 1, "duration_hours": 2}),
        (timedelta(hours=2), "in_2hours", "Starts in 2 hours", "Starts in 2 hours — add it to your calendar", 0, {"type": "offset", "hours": 2, "duration_hours": 2}),
        (timedelta(hours=4), "this_evening", "This evening", "This evening — unwind with a relaxed session", 0, {"type": "offset", "hours": 4, "duration_hours": 2}),
        (timedelta(hours=-2, minutes=-10), "just_ended", "Just ended", "Just ended — highlights and recap available", 0, {"type": "offset", "hours": -2, "minutes": -10, "duration_hours": 2}),
        (timedelta(minutes=45), "very_soon", "Very soon", "Very soon — warm-up and introductions are underway", 0, {"type": "offset", "minutes": 45, "duration_hours": 2}),
        
        # Timezone test cases - critical for international users
        (timedelta(hours=1), "utc_plus1", "UTC+1 local time", "Timezone demo in UTC+1 — shows local start time", 1, {"type": "offset", "hours": 1, "duration_hours": 2, "timezone_offset": 1}),
        (timedelta(hours=1), "utc_plus2", "UTC+2 local time", "Timezone demo in UTC+2 — local time check", 2, {"type": "offset", "hours": 1, "duration_hours": 2, "timezone_offset": 2}),
        (timedelta(hours=1), "utc_minus5", "UTC-5 local time", "Timezone demo in UTC-5 (EST) — local time check", -5, {"type": "offset", "hours": 1, "duration_hours": 2, "timezone_offset": -5}),
        (timedelta(hours=1), "utc_plus9", "UTC+9 local time", "Timezone demo in UTC+9 (JST) — local time check", 9, {"type": "offset", "hours": 1, "duration_hours": 2, "timezone_offset": 9}),
        (timedelta(minutes=30), "utc_plus530", "UTC+5:30 local time", "Timezone demo in UTC+5:30 (IST) — local time check", 5.5, {"type": "offset", "minutes": 30, "duration_hours": 2, "timezone_offset": 5.5}),
        
        # Sunrise edge cases - critical for testing
        # Event ending 5 minutes before sunrise (should show)
        ((next_sunrise - now) - timedelta(hours=2), "before_sunrise_5min", "Ends before sunrise", "Ends 5 minutes before sunrise — late-night session", 0, {"type": "sunrise_relative", "end_offset_minutes": -5, "start_offset_hours": -2}),
        # Event ending exactly at sunrise (edge case)
        ((next_sunrise - now) - timedelta(hours=1, minutes=30), "at_sunrise", "Ends at sunrise", "Ends at sunrise — early-bird finale", 0, {"type": "sunrise_relative", "end_offset_minutes": 0, "start_offset_hours": -1.5}),
        # Event ending 5 minutes after sunrise (should NOT show)
        ((next_sunrise - now) - timedelta(hours=1), "after_sunrise_5min", "Ends after sunrise", "Ends 5 minutes after sunrise — should be filtered", 0, {"type": "sunrise_relative", "end_offset_minutes": 5, "start_offset_hours": -1}),
        # Event crossing sunrise boundary (starts before, ends after)
        ((next_sunrise - now) - timedelta(hours=3), "crossing_sunrise", "Crosses sunrise", "Crosses sunrise — spans pre-dawn into morning", 0, {"type": "sunrise_relative", "start_offset_hours": -2, "end_offset_hours": 1}),
        # Event starting just before sunrise
        ((next_sunrise - now) - timedelta(minutes=30), "starting_before_sunrise", "Starts before sunrise", "Starts 30 minutes before sunrise — early meetup", 0, {"type": "sunrise_relative", "start_offset_minutes": -30, "end_offset_minutes": 30}),
        # Event starting after sunrise (should NOT show)
        ((next_sunrise - now) + timedelta(minutes=30), "starting_after_sunrise", "Starts after sunrise", "Starts 30 minutes after sunrise — morning session", 0, {"type": "sunrise_relative", "start_offset_minutes": 30, "end_offset_hours": 2}),
        # All-night event (starts evening, ends at sunrise)
        ((next_sunrise - now) - timedelta(hours=8), "all_night", "All night", "All-night event until sunrise — overnight hangout", 0, {"type": "sunrise_relative", "start_offset_hours": -8, "end_offset_minutes": 0}),
    ]
    
    demo_events = []
    
    # Use real events as templates, cycling through them
    for i, scenario in enumerate(time_scenarios):
        if len(scenario) == 6:
            offset, suffix, title_label, scenario_description, tz_offset, relative_spec = scenario
        elif len(scenario) == 5:
            offset, suffix, title_label, scenario_description, tz_offset = scenario
            relative_spec = None
        else:
            offset, suffix, title_label, scenario_description = scenario
            tz_offset = 0
            relative_spec = None
            
        if real_events:
            # Use real events as templates, cycling through them
            template = real_events[i % len(real_events)].copy()
        else:
            # Fallback template if no real events available
            template = {
                "title": f"Demo Event {i+1}",
                "description": description,
                "location": {
                    "name": "Demo Location Hof",
                    "lat": 50.3167 + (i * 0.001),
                    "lon": 11.9167 + (i * 0.001)
                }
            }
        
        event_id = f"demo_{suffix}"
        template_title, template_description = normalize_demo_template(template)
        
        # Calculate start time
        start_time = now + offset
        
        # Special handling for sunrise edge cases to ensure proper timing
        if "sunrise" in suffix:
            if "before_sunrise_5min" in suffix:
                # Event ends 5 minutes before sunrise
                start_time = next_sunrise - timedelta(hours=2)
                end_time = next_sunrise - timedelta(minutes=5)
            elif "at_sunrise" in suffix:
                # Event ends exactly at sunrise
                start_time = next_sunrise - timedelta(hours=1, minutes=30)
                end_time = next_sunrise
            elif "after_sunrise_5min" in suffix:
                # Event ends 5 minutes after sunrise (should be filtered)
                start_time = next_sunrise - timedelta(hours=1)
                end_time = next_sunrise + timedelta(minutes=5)
            elif "crossing_sunrise" in suffix:
                # Event crosses sunrise boundary
                start_time = next_sunrise - timedelta(hours=2)
                end_time = next_sunrise + timedelta(hours=1)
            elif "starting_before_sunrise" in suffix:
                # Starts 30 min before sunrise, ends 30 min after
                start_time = next_sunrise - timedelta(minutes=30)
                end_time = next_sunrise + timedelta(minutes=30)
            elif "starting_after_sunrise" in suffix:
                # Starts after sunrise (should be filtered)
                start_time = next_sunrise + timedelta(minutes=30)
                end_time = next_sunrise + timedelta(hours=2)
            elif "all_night" in suffix:
                # All night event ending at sunrise
                start_time = next_sunrise - timedelta(hours=8)
                end_time = next_sunrise
                
            # Create event with custom times
            tz_suffix = f" (TZ: {tz_offset:+.1f})" if tz_offset != 0 else ""
            title_suffix = f" — {title_label}" if title_label else ""
            demo_event = {
                "id": event_id,
                "title": f"[DEMO] {template_title}{title_suffix}{tz_suffix}",
                "description": f"{scenario_description}. {template_description}",
                "location": template.get('location', {
                    "name": "Demo Location",
                    "lat": 50.3167,
                    "lon": 11.9167
                }),
                "start_time": fmt_tz(start_time, tz_offset),
                "end_time": fmt_tz(end_time, tz_offset),
                "url": template.get('url', 'https://example.com/demo'),
                "source": "demo",
                "status": "published",
                "published_at": fmt(now),
                "relative_time": relative_spec  # Add relative time specification
            }
        else:
            # Normal event with standard duration
            # Preserve original event duration if possible
            if 'start_time' in template and 'end_time' in template:
                try:
                    orig_start = datetime.fromisoformat(template['start_time'].replace('Z', ''))
                    orig_end = datetime.fromisoformat(template['end_time'].replace('Z', ''))
                    duration = orig_end - orig_start
                except:
                    duration = timedelta(hours=2)  # default duration
            else:
                duration = timedelta(hours=2)
            
            end_time = start_time + duration
            
            # Add timezone info to title if testing timezone
            tz_suffix = f" (TZ: {tz_offset:+.1f})" if tz_offset != 0 else ""
            
            title_suffix = f" — {title_label}" if title_label else ""
            demo_event = {
                "id": event_id,
                "title": f"[DEMO] {template_title}{title_suffix}{tz_suffix}",
                "description": f"{scenario_description}. {template_description}",
                "location": template.get('location', {
                    "name": "Demo Location",
                    "lat": 50.3167,
                    "lon": 11.9167
                }),
                "start_time": fmt_tz(start_time, tz_offset),
                "end_time": fmt_tz(end_time, tz_offset),
                "url": template.get('url', 'https://example.com/demo'),
                "source": "demo",
                "status": "published",
                "published_at": fmt(now),
                "relative_time": relative_spec  # Add relative time specification
            }
        
        demo_events.append(demo_event)
    
    # Add one far away event for distance testing (using first template)
    if real_events:
        far_template = real_events[0].copy()
        far_template['location'] = {
            "name": "Berlin Alexanderplatz (Demo - Far)",
            "lat": 52.5200,
            "lon": 13.4050
        }
    else:
        far_template = {
            "title": "Far Away Event",
            "description": "Event in Berlin for distance testing",
            "location": {
                "name": "Berlin Alexanderplatz (Demo - Far)",
                "lat": 52.5200,
                "lon": 13.4050
            }
        }
    
    far_start = now + timedelta(hours=2)
    far_end = far_start + timedelta(hours=2)
    far_title, far_description = normalize_demo_template(far_template)
    far_event = {
        "id": "demo_far_away",
        "title": f"[DEMO] {far_title} — 250 km away",
        "description": f"Distance test: 250 km away in Berlin for long-range filtering. {far_description}",
        "location": far_template['location'],
        "start_time": fmt(far_start),
        "end_time": fmt(far_end),
        "url": far_template.get('url', 'https://example.com/demo'),
        "source": "demo",
        "status": "published",
        "published_at": fmt(now),
        "relative_time": {
            "type": "offset",
            "hours": 2,
            "duration_hours": 2
        }
    }
    demo_events.append(far_event)
    
    return demo_events

def generate_demo_events(base_dir="."):
    """Generate demo events with timestamps relative to now, using real events as templates."""
    now = datetime.now()
    
    def fmt(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Load real events to use as templates
    real_events = load_real_events(base_dir)
    
    # Generate demo events
    events = generate_demo_events_from_templates(real_events, now)
    
    return {
        "events": events,
        "last_updated": fmt(now),
        "demo_generated_at": fmt(now),
        "note": "Demo events generated from real event templates with current timestamps for testing"
    }

if __name__ == "__main__":
    
    # Clean up old files first
    cleanup_old_files()
    
    # Generate and output demo events
    data = generate_demo_events()
    
    print(f"# Generated {len(data['events'])} demo events", file=sys.stderr)
    
    # Output to stdout (can be redirected to file)
    print(json.dumps(data, indent=2, ensure_ascii=False))
