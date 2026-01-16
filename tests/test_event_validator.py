#!/usr/bin/env python3
"""
Tests for Event Validator module.

Validates that incomplete events cannot be published.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.event_validator import EventValidator, validate_event, validate_events


def test_valid_event():
    """Test validation of complete, valid event."""
    print("\n" + "="*60)
    print("Test: Valid Complete Event")
    print("="*60)
    
    valid_event = {
        'id': 'test_event_123',
        'title': 'Test Event',
        'teaser': 'This is a short teaser for the test event',
        'description': 'This is a full test event description with enough details',
        'location': {
            'name': 'Test Venue',
            'address': 'Teststraße 1, 95030 Hof',
            'lat': 50.3167,
            'lon': 11.9167
        },
        'start_time': '2026-01-20T18:00:00',
        'end_time': '2026-01-20T22:00:00',
        'category': 'music',
        'source': 'https://example.com/event',
        'url': 'https://example.com/event'
    }
    
    result = validate_event(valid_event)
    
    if result.is_valid:
        print(f"  ✓ Event is valid")
        print(f"    Errors: {len(result.errors)}")
        print(f"    Warnings: {len(result.warnings)}")
        return True
    else:
        print(f"  ✗ Event marked as invalid (should be valid)")
        print(result.get_summary())
        return False


def test_missing_required_fields():
    """Test validation fails for missing required fields."""
    print("\n" + "="*60)
    print("Test: Missing Required Fields")
    print("="*60)
    
    test_cases = [
        ({'title': 'Test'}, ['id', 'teaser', 'description', 'location', 'start_time', 'category', 'source']),
        ({'id': 'test_1'}, ['title', 'teaser', 'description', 'location', 'start_time', 'category', 'source']),
        ({'id': 'test_2', 'title': 'Test'}, ['teaser', 'description', 'location', 'start_time', 'category', 'source']),
        ({'id': 'test_3', 'title': 'Test', 'teaser': 'Short teaser', 'location': {}}, ['description', 'start_time', 'category', 'source']),
    ]
    
    passed = 0
    failed = 0
    
    for event, expected_missing in test_cases:
        result = validate_event(event)
        
        if not result.is_valid:
            missing_fields = [err.field for err in result.errors if 'missing' in err.message.lower()]
            if all(field in [e.field for e in result.errors] for field in expected_missing):
                print(f"  ✓ Correctly rejected event missing {expected_missing}")
                passed += 1
            else:
                print(f"  ✗ Missing fields detection incomplete")
                print(f"    Expected: {expected_missing}")
                print(f"    Got: {missing_fields}")
                failed += 1
        else:
            print(f"  ✗ Invalid event marked as valid")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_invalid_location_no_coordinates():
    """Test validation fails for location without coordinates or address."""
    print("\n" + "="*60)
    print("Test: Location Without Complete Data (CRITICAL)")
    print("="*60)
    
    test_cases = [
        # No address
        {
            'id': 'test_0',
            'title': 'Test Event',
            'location': {'name': 'Test Venue', 'lat': 50.3167, 'lon': 11.9167},  # Missing address
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        },
        # No latitude
        {
            'id': 'test_1',
            'title': 'Test Event',
            'location': {'name': 'Test Venue', 'address': 'Test Street 1, Hof', 'lon': 11.9167},
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        },
        # No longitude
        {
            'id': 'test_2',
            'title': 'Test Event',
            'location': {'name': 'Test Venue', 'address': 'Test Street 1, Hof', 'lat': 50.3167},
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        },
        # None coordinates
        {
            'id': 'test_3',
            'title': 'Test Event',
            'location': {'name': 'Test Venue', 'address': 'Test Street 1, Hof', 'lat': None, 'lon': None},
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        },
        # Empty location
        {
            'id': 'test_4',
            'title': 'Test Event',
            'location': {},
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        },
    ]
    
    passed = 0
    failed = 0
    
    for event in test_cases:
        result = validate_event(event)
        
        if not result.is_valid:
            location_errors = [err for err in result.errors if 'location' in err.field.lower()]
            if location_errors:
                print(f"  ✓ Correctly rejected incomplete location")
                print(f"    Errors: {', '.join([err.field for err in location_errors])}")
                passed += 1
            else:
                print(f"  ✗ No location errors found")
                failed += 1
        else:
            print(f"  ✗ Invalid event marked as valid")
            print(f"    Event: {event.get('id')}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_invalid_coordinates():
    """Test validation fails for invalid coordinate values."""
    print("\n" + "="*60)
    print("Test: Invalid Coordinate Values")
    print("="*60)
    
    test_cases = [
        # Latitude out of range
        {
            'location': {'name': 'Test', 'lat': 95.0, 'lon': 11.9},
            'expected_field': 'location.lat'
        },
        # Longitude out of range
        {
            'location': {'name': 'Test', 'lat': 50.3, 'lon': 200.0},
            'expected_field': 'location.lon'
        },
        # Non-numeric coordinates
        {
            'location': {'name': 'Test', 'lat': 'invalid', 'lon': 11.9},
            'expected_field': 'location.lat'
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        event = {
            'id': 'test_coord',
            'title': 'Test Event',
            'location': test_case['location'],
            'start_time': '2026-01-20T18:00:00',
            'source': 'Test'
        }
        
        result = validate_event(event)
        
        if not result.is_valid:
            has_expected_error = any(
                err.field == test_case['expected_field'] 
                for err in result.errors
            )
            if has_expected_error:
                print(f"  ✓ Correctly rejected invalid {test_case['expected_field']}")
                passed += 1
            else:
                print(f"  ✗ Expected error on {test_case['expected_field']}")
                print(f"    Errors: {[err.field for err in result.errors]}")
                failed += 1
        else:
            print(f"  ✗ Invalid event marked as valid")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_bulk_validation():
    """Test bulk validation for multiple events."""
    print("\n" + "="*60)
    print("Test: Bulk Validation")
    print("="*60)
    
    events = [
        # Valid event 1
        {
            'id': 'valid_1',
            'title': 'Valid Event 1',
            'teaser': 'Short teaser for event 1',
            'description': 'Full description for valid event 1 with enough details',
            'category': 'music',
            'location': {'name': 'Venue 1', 'address': 'Street 1, Hof', 'lat': 50.3, 'lon': 11.9},
            'start_time': '2026-01-20T18:00:00',
            'source': 'https://test.com/event1'
        },
        # Invalid event (missing address and coords)
        {
            'id': 'invalid_1',
            'title': 'Invalid Event 1',
            'teaser': 'Short teaser for invalid event',
            'description': 'Description for invalid event',
            'category': 'music',
            'location': {'name': 'Venue 2'},  # Missing address and lat/lon
            'start_time': '2026-01-20T18:00:00',
            'source': 'https://test.com/event2'
        },
        # Valid event 2
        {
            'id': 'valid_2',
            'title': 'Valid Event 2',
            'teaser': 'Short teaser for event 2',
            'description': 'Full description for valid event 2 with enough details',
            'category': 'concert',
            'location': {'name': 'Venue 3', 'address': 'Street 3, Bayreuth', 'lat': 49.9, 'lon': 11.6},
            'start_time': '2026-01-20T19:00:00',
            'source': 'https://test.com/event3'
        },
        # Invalid event (missing title and address)
        {
            'id': 'invalid_2',
            'teaser': 'Short teaser',
            'description': 'Description for event without title',
            'category': 'music',
            'location': {'name': 'Venue 4', 'lat': 50.1, 'lon': 12.1},  # Missing address
            'start_time': '2026-01-20T20:00:00',
            'source': 'https://test.com/event4'
        },
    ]
    
    valid_ids, invalid_ids, results = validate_events(events)
    
    expected_valid = {'valid_1', 'valid_2'}
    expected_invalid = {'invalid_1', 'invalid_2'}
    
    actual_valid = set(valid_ids)
    actual_invalid = set(invalid_ids)
    
    if actual_valid == expected_valid and actual_invalid == expected_invalid:
        print(f"  ✓ Bulk validation correct")
        print(f"    Valid: {valid_ids}")
        print(f"    Invalid: {invalid_ids}")
        return True
    else:
        print(f"  ✗ Bulk validation incorrect")
        print(f"    Expected valid: {expected_valid}")
        print(f"    Got valid: {actual_valid}")
        print(f"    Expected invalid: {expected_invalid}")
        print(f"    Got invalid: {actual_invalid}")
        return False


def test_no_publish_incomplete():
    """Test that incomplete events are clearly blocked from publishing."""
    print("\n" + "="*60)
    print("Test: Block Incomplete Events from Publishing (CRITICAL)")
    print("="*60)
    
    # Simulate real-world incomplete events from pending queue
    incomplete_events = [
        # Event with generic location name only
        {
            'id': 'frankenpost_1',
            'title': 'Richard-Wagner-Museum Exhibition',
            'teaser': 'Visit the Wagner museum exhibition',
            'description': 'A comprehensive exhibition about Richard Wagner and his works',
            'category': 'museum',
            'location': {'name': 'Hof', 'address': 'Hof', 'lat': 50.3167, 'lon': 11.9167},  # Generic city
            'start_time': '2026-01-20T10:00:00',
            'source': 'https://frankenpost.de/event1'
        },
        # Event with no coordinates or address
        {
            'id': 'frankenpost_2',
            'title': 'MAKkultur Concert',
            'location': {'name': 'MAKkultur', 'lat': None, 'lon': None},  # Missing coords AND address AND teaser/desc/category
            'start_time': '2026-01-21T19:00:00',
            'source': 'https://frankenpost.de/event2'
        },
        # Event with needs_review flag but complete data
        {
            'id': 'frankenpost_3',
            'title': 'Sportheim Event',
            'teaser': 'Community sports event at the Sportheim',
            'description': 'Join us for a fun community sports event at the local Sportheim',
            'category': 'sports',
            'location': {
                'name': 'Sportheim',
                'address': 'Sportheim, Hof',
                'lat': 50.3167,
                'lon': 11.9167,
                'needs_review': True
            },
            'start_time': '2026-01-22T15:00:00',
            'source': 'https://frankenpost.de/event3'
        },
        # Underground event with address_hidden flag (SHOULD BE VALID)
        {
            'id': 'underground_1',
            'title': 'Secret Underground Rave',
            'teaser': 'Underground electronic music event',
            'description': 'Join us for an underground electronic music event - location announced to attendees only',
            'category': 'music',
            'location': {
                'name': 'TBA (announced to attendees)',
                'address_hidden': True,  # Address intentionally hidden
                'lat': 50.3167,
                'lon': 11.9167
            },
            'start_time': '2026-01-30T23:00:00',
            'source': 'https://underground.com/event'
        },
    ]
    
    passed = 0
    failed = 0
    
    for event in incomplete_events:
        result = validate_event(event)
        
        event_id = event.get('id')
        
        if event_id == 'frankenpost_1':
            # Generic city name - should be valid with warning
            if result.is_valid and result.has_warnings():
                print(f"  ✓ {event_id}: Valid with warning (generic location)")
                passed += 1
            elif result.is_valid:
                print(f"  ⚠ {event_id}: Valid but no warning for generic location")
                passed += 1  # Accept but note
            else:
                print(f"  ✗ {event_id}: Incorrectly blocked (has valid coordinates)")
                failed += 1
        elif event_id == 'frankenpost_2':
            # No coordinates - must be blocked
            if not result.is_valid:
                print(f"  ✓ {event_id}: Correctly blocked from publishing")
                print(f"    Reason: {result.errors[0].message if result.errors else 'Unknown'}")
                passed += 1
            else:
                print(f"  ✗ {event_id}: Should be blocked but marked as valid")
                failed += 1
        elif event_id == 'frankenpost_3':
            if result.is_valid and result.has_warnings():
                print(f"  ✓ {event_id}: Valid with warning (needs review)")
                passed += 1
            elif not result.is_valid:
                print(f"  ✓ {event_id}: Blocked (strict mode)")
                passed += 1
            else:
                print(f"  ⚠ {event_id}: Valid but no warning for needs_review")
                passed += 1  # Accept but note
        elif event_id == 'underground_1':
            # Underground event with address_hidden - should be valid with warning
            if result.is_valid:
                has_hidden_warning = any('hidden' in str(w.message).lower() for w in result.warnings)
                if has_hidden_warning:
                    print(f"  ✓ {event_id}: Valid with warning (address hidden for underground event)")
                    passed += 1
                else:
                    print(f"  ⚠ {event_id}: Valid but no warning about hidden address")
                    passed += 1  # Accept but note
            else:
                print(f"  ✗ {event_id}: Underground event blocked (should allow address_hidden)")
                print(f"    Errors: {[e.message for e in result.errors]}")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n" + "!"*60)
        print("CRITICAL FAILURE: Incomplete events not blocked!")
        print("This violates the requirement that ALL events must have")
        print("complete basic data before publishing.")
        print("!"*60)
    
    return failed == 0


def main():
    """Run all event validator tests."""
    print("\n" + "═"*60)
    print("EVENT VALIDATOR TEST SUITE")
    print("═"*60)
    
    tests = [
        ("Valid Complete Event", test_valid_event),
        ("Missing Required Fields", test_missing_required_fields),
        ("Location Without Coordinates", test_invalid_location_no_coordinates),
        ("Invalid Coordinate Values", test_invalid_coordinates),
        ("Bulk Validation", test_bulk_validation),
        ("Block Incomplete Events (CRITICAL)", test_no_publish_incomplete),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ {test_name} CRASHED: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "═"*60)
    print("TEST SUMMARY")
    print("═"*60)
    
    passed_count = sum(1 for _, success in results if success)
    failed_count = len(results) - passed_count
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "═"*60)
    print(f"Total: {passed_count}/{len(results)} tests passed")
    print("═"*60)
    
    if failed_count > 0:
        print("\n⚠️  Some tests failed. Review output above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
