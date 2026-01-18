#!/usr/bin/env python3
"""
Test Entity Resolver

Tests for the three-tier override system in EntityResolver.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.entity_resolver import EntityResolver
from modules.entity_models import Location, Organizer


def create_test_environment():
    """Create temporary test environment with sample data"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create assets/json directory
    json_dir = temp_dir / 'assets' / 'json'
    json_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample locations library
    locations_data = {
        'locations': [
            {
                'id': 'loc_theater_hof',
                'name': 'Theater Hof',
                'lat': 50.3200,
                'lon': 11.9180,
                'address': 'Kulmbacher Str., 95030 Hof',
                'verified': True
            },
            {
                'id': 'loc_freiheitshalle',
                'name': 'Freiheitshalle Hof',
                'lat': 50.3167,
                'lon': 11.9167,
                'address': 'Freiheitshalle, Hof'
            }
        ]
    }
    
    with open(json_dir / 'locations.json', 'w', encoding='utf-8') as f:
        json.dump(locations_data, f, indent=2)
    
    # Create sample organizers library
    organizers_data = {
        'organizers': [
            {
                'id': 'org_kulturverein',
                'name': 'Kulturverein Hof',
                'website': 'https://kulturverein-hof.de',
                'verified': True
            }
        ]
    }
    
    with open(json_dir / 'organizers.json', 'w', encoding='utf-8') as f:
        json.dump(organizers_data, f, indent=2)
    
    return temp_dir


def test_tier1_reference_only():
    """Test Tier 1: Reference only resolution"""
    print("Testing Tier 1: Reference only...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    event = {
        'id': 'event_1',
        'title': 'Test Event',
        'location_id': 'loc_theater_hof'
    }
    
    resolved_location = resolver.resolve_event_location(event)
    
    assert resolved_location['id'] == 'loc_theater_hof'
    assert resolved_location['name'] == 'Theater Hof'
    assert resolved_location['lat'] == 50.3200
    assert resolved_location['lon'] == 11.9180
    assert resolved_location['verified'] == True
    
    # Check stats
    stats = resolver.get_stats()
    assert stats['location_tier1'] == 1
    assert stats['location_tier2'] == 0
    assert stats['location_tier3'] == 0
    
    print("✓ Tier 1 test passed")


def test_tier2_partial_override():
    """Test Tier 2: Partial override resolution"""
    print("Testing Tier 2: Partial override...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    event = {
        'id': 'event_2',
        'title': 'VIP Event',
        'location_id': 'loc_theater_hof',
        'location_override': {
            'name': 'Theater Hof - VIP Lounge',
            'address': 'Side entrance'
        }
    }
    
    resolved_location = resolver.resolve_event_location(event)
    
    # Base fields should be preserved
    assert resolved_location['id'] == 'loc_theater_hof'
    assert resolved_location['lat'] == 50.3200
    assert resolved_location['lon'] == 11.9180
    assert resolved_location['verified'] == True
    
    # Overridden fields should be updated
    assert resolved_location['name'] == 'Theater Hof - VIP Lounge'
    assert resolved_location['address'] == 'Side entrance'
    
    # Check stats
    stats = resolver.get_stats()
    assert stats['location_tier2'] == 1
    
    print("✓ Tier 2 test passed")


def test_tier3_full_override():
    """Test Tier 3: Full override resolution"""
    print("Testing Tier 3: Full override...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    event = {
        'id': 'event_3',
        'title': 'Pop-up Event',
        'location': {
            'name': 'Temporary Stage',
            'lat': 50.3250,
            'lon': 11.9200
        }
    }
    
    resolved_location = resolver.resolve_event_location(event)
    
    # Should use embedded location as-is
    assert resolved_location['name'] == 'Temporary Stage'
    assert resolved_location['lat'] == 50.3250
    assert resolved_location['lon'] == 11.9200
    assert 'id' not in resolved_location  # No ID for full override
    
    # Check stats
    stats = resolver.get_stats()
    assert stats['location_tier3'] == 1
    
    print("✓ Tier 3 test passed")


def test_resolve_full_event():
    """Test resolving complete event"""
    print("Testing full event resolution...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    event = {
        'id': 'event_4',
        'title': 'Full Event',
        'location_id': 'loc_freiheitshalle',
        'organizer_id': 'org_kulturverein'
    }
    
    resolved_event = resolver.resolve_event(event, clean_refs=True)
    
    # Location should be resolved
    assert resolved_event['location']['name'] == 'Freiheitshalle Hof'
    assert resolved_event['location']['lat'] == 50.3167
    
    # Organizer should be resolved
    assert resolved_event['organizer']['name'] == 'Kulturverein Hof'
    assert resolved_event['organizer']['website'] == 'https://kulturverein-hof.de'
    
    # Reference fields should be cleaned up
    assert 'location_id' not in resolved_event
    assert 'organizer_id' not in resolved_event
    
    print("✓ Full event resolution test passed")


def test_batch_resolution():
    """Test batch event resolution"""
    print("Testing batch resolution...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    events = [
        {
            'id': 'event_1',
            'location_id': 'loc_theater_hof'
        },
        {
            'id': 'event_2',
            'location_id': 'loc_freiheitshalle'
        }
    ]
    
    resolved_events = resolver.resolve_events(events)
    
    assert len(resolved_events) == 2
    assert resolved_events[0]['location']['name'] == 'Theater Hof'
    assert resolved_events[1]['location']['name'] == 'Freiheitshalle Hof'
    
    print("✓ Batch resolution test passed")


def test_usage_stats():
    """Test location usage statistics"""
    print("Testing usage statistics...")
    
    base_path = create_test_environment()
    resolver = EntityResolver(base_path)
    
    events = [
        {'id': 'event_1', 'location_id': 'loc_theater_hof'},
        {'id': 'event_2', 'location_id': 'loc_theater_hof', 'location_override': {'name': 'VIP'}},
        {'id': 'event_3', 'location_id': 'loc_freiheitshalle'},
    ]
    
    stats = resolver.get_location_usage_stats('loc_theater_hof', events)
    
    assert stats['location_id'] == 'loc_theater_hof'
    assert stats['total_uses'] == 2
    assert stats['override_count'] == 1
    assert len(stats['events']) == 2
    
    print("✓ Usage statistics test passed")


def run_all_tests():
    """Run all entity resolver tests"""
    print("=" * 70)
    print("  Entity Resolver Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_tier1_reference_only,
        test_tier2_partial_override,
        test_tier3_full_override,
        test_resolve_full_event,
        test_batch_resolution,
        test_usage_stats,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print(f"  Tests: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
