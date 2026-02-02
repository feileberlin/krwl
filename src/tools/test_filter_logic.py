#!/usr/bin/env python3
"""
Test filter logic with actual event data
Simulates what happens when the page loads
"""
import json
from datetime import datetime, timedelta

# Load events
with open('assets/json/events.json', 'r') as f:
    data = json.load(f)
    events = data['events']

print(f"Total events loaded: {len(events)}")

# Check event times
now = datetime.now()
print(f"\nCurrent time: {now}")

# Simulate default filter: "sunrise" which is ~6-7 hours from now
sunrise_time = now + timedelta(hours=7)
print(f"Sunrise filter (default): events until {sunrise_time}")

# Count events by time
future_events = 0
past_events = 0
within_sunrise = 0

for event in events:
    start_time_str = event.get('start_time', '')
    if start_time_str:
        try:
            event_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            
            if event_time > now:
                future_events += 1
                if event_time <= sunrise_time:
                    within_sunrise += 1
            else:
                past_events += 1
        except:
            pass

print(f"\n📊 Event Distribution:")
print(f"  Past events (already happened): {past_events}")
print(f"  Future events (not yet started): {future_events}")
print(f"  Within sunrise window (next ~7 hours): {within_sunrise}")

if within_sunrise == 0:
    print(f"\n❌ PROBLEM FOUND!")
    print(f"   With default 'sunrise' filter, {within_sunrise} events will be shown")
    print(f"   All {past_events} past events are filtered out")
    print(f"   All {future_events - within_sunrise} future events are too far ahead")
    print(f"\n💡 SOLUTION:")
    print(f"   1. Use 'relative_time' feature to make events always current")
    print(f"   2. OR: Change default filter to '24h' or '7d' instead of 'sunrise'")
    print(f"   3. OR: Regenerate demo events with current timestamps")

# Check if events use relative_time
events_with_relative_time = sum(1 for e in events if 'relative_time' in e)
print(f"\n📌 Events with relative_time feature: {events_with_relative_time}/{len(events)}")

if events_with_relative_time > 0:
    print(f"   ⚠️  relative_time should make events appear current")
    print(f"   Check if JavaScript is processing them correctly")

# Check locations (for distance filter)
print(f"\n📍 Location check:")
default_center = {"lat": 50.3167, "lon": 11.9167}  # Hof default
events_near_hof = 0
events_at_antarctica = 0

for event in events:
    loc = event.get('location', {})
    lat = loc.get('lat', 0)
    lon = loc.get('lon', 0)
    
    # Simple distance check (rough)
    if abs(lat - default_center['lat']) < 1 and abs(lon - default_center['lon']) < 1:
        events_near_hof += 1
    elif lat < -60:  # Antarctica
        events_at_antarctica += 1

print(f"  Events near Hof ({default_center['lat']}, {default_center['lon']}): {events_near_hof}")
print(f"  Events in Antarctica: {events_at_antarctica}")
print(f"  Other locations: {len(events) - events_near_hof - events_at_antarctica}")

if events_near_hof == 0 and events_at_antarctica > 0:
    print(f"\n⚠️  Most events are in Antarctica, but default region is 'hof'")
    print(f"   With distance filter, events might be too far away")
    print(f"   User needs to switch to 'antarctica' region or increase distance")
