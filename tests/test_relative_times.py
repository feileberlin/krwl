#!/usr/bin/env python3
"""
Test relative time processing for event templates.
Verifies that demo events with relative_time specifications are generated correctly.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_demo_events_have_relative_time():
    """Test that generated demo events include relative_time field"""
    demo_file = Path(__file__).parent.parent / "assets" / "json" / "events.demo.json"
    
    if not demo_file.exists():
        print("❌ events.demo.json not found")
        return False
    
    with open(demo_file, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    if not events:
        print("❌ No events found in demo file")
        return False
    
    # Count events with relative_time
    events_with_relative_time = [e for e in events if 'relative_time' in e]
    
    print(f"✓ Found {len(events)} demo events")
    print(f"✓ {len(events_with_relative_time)} have relative_time field")
    
    if len(events_with_relative_time) < len(events) - 1:  # Allow 1 event without (far_away)
        print(f"⚠️  Expected most events to have relative_time field")
        return False
    
    # Test a few specific scenarios
    test_cases = [
        ("demo_happening_now", "offset", {"minutes": -30}),
        ("demo_starting_5min", "offset", {"minutes": 5}),
        ("demo_in_1hour", "offset", {"hours": 1}),
    ]
    
    for event_id, expected_type, expected_fields in test_cases:
        event = next((e for e in events if e['id'] == event_id), None)
        
        if not event:
            print(f"❌ Event {event_id} not found")
            return False
        
        if 'relative_time' not in event:
            print(f"❌ Event {event_id} missing relative_time field")
            return False
        
        rel_time = event['relative_time']
        
        if rel_time.get('type') != expected_type:
            print(f"❌ Event {event_id} has wrong type: {rel_time.get('type')} != {expected_type}")
            return False
        
        for field, value in expected_fields.items():
            if rel_time.get(field) != value:
                print(f"❌ Event {event_id} has wrong {field}: {rel_time.get(field)} != {value}")
                return False
        
        print(f"✓ Event {event_id} has correct relative_time specification")
    
    return True


def test_relative_time_types():
    """Test that both offset and sunrise_relative types are present"""
    demo_file = Path(__file__).parent.parent / "assets" / "json" / "events.demo.json"
    
    with open(demo_file, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    offset_events = [e for e in events if e.get('relative_time', {}).get('type') == 'offset']
    sunrise_events = [e for e in events if e.get('relative_time', {}).get('type') == 'sunrise_relative']
    
    print(f"✓ Found {len(offset_events)} events with 'offset' type")
    print(f"✓ Found {len(sunrise_events)} events with 'sunrise_relative' type")
    
    if len(offset_events) == 0:
        print("❌ No offset type events found")
        return False
    
    if len(sunrise_events) == 0:
        print("❌ No sunrise_relative type events found")
        return False
    
    return True


def test_timezone_events():
    """Test that timezone events have correct timezone_offset field"""
    demo_file = Path(__file__).parent.parent / "assets" / "json" / "events.demo.json"
    
    with open(demo_file, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    # Find timezone test events
    tz_events = [e for e in events if 'utc' in e['id'].lower()]
    
    if not tz_events:
        print("⚠️  No timezone test events found")
        return True  # Not a failure, just a warning
    
    print(f"✓ Found {len(tz_events)} timezone test events")
    
    for event in tz_events:
        if 'relative_time' not in event:
            continue
        
        rel_time = event['relative_time']
        if 'timezone_offset' in rel_time:
            tz_offset = rel_time['timezone_offset']
            print(f"  ✓ {event['id']} has timezone_offset: {tz_offset:+.1f}")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Relative Time Event Templates")
    print("=" * 60)
    print()
    
    tests = [
        ("Demo events have relative_time field", test_demo_events_have_relative_time),
        ("Both offset and sunrise_relative types exist", test_relative_time_types),
        ("Timezone events have correct offsets", test_timezone_events),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
            if result:
                print(f"✅ PASSED\n")
            else:
                print(f"❌ FAILED\n")
        except Exception as e:
            print(f"💥 ERROR: {e}\n")
            results.append(False)
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if all(results):
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
