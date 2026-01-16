#!/usr/bin/env python3
"""
Test for Event Context Aggregator.

Demonstrates how aggregating all available data helps editors make informed decisions.
"""

import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.event_context_aggregator import EventContextAggregator, get_event_context


def create_test_data_directory():
    """Create temporary directory with test data."""
    tmpdir = tempfile.mkdtemp()
    base_path = Path(tmpdir)
    assets_json = base_path / 'assets' / 'json'
    assets_json.mkdir(parents=True)
    
    # Published events
    published = {
        "events": [
            {
                "id": "pub_1",
                "title": "Jazz Concert at MAKkultur",
                "location": {"name": "MAKkultur", "lat": 50.3200, "lon": 11.9180},
                "start_time": "2025-12-15T19:00:00",
                "source": "Frankenpost"
            },
            {
                "id": "pub_2",
                "title": "Art Exhibition at Richard-Wagner-Museum",
                "location": {"name": "Richard-Wagner-Museum", "lat": 49.9440, "lon": 11.5760},
                "start_time": "2025-11-20T10:00:00",
                "source": "Frankenpost"
            }
        ]
    }
    
    # Pending events
    pending = {
        "pending_events": [
            {
                "id": "pending_1",
                "title": "Classical Concert at MAKkultur",
                "location": {"name": "MAKkultur", "lat": None, "lon": None, "needs_review": True},
                "start_time": "2026-01-25T19:00:00",
                "source": "Frankenpost"
            }
        ]
    }
    
    # Rejected events
    rejected = {
        "rejected_events": [
            {
                "id": "pending_1",  # Same ID as current pending event
                "title": "Classical Concert at MAKkultur",
                "location": {"name": "Hof", "lat": 50.3167, "lon": 11.9167},
                "start_time": "2026-01-25T19:00:00",
                "source": "Frankenpost",
                "rejected_at": "2026-01-15T10:30:00",
                "reason": "Location was generic 'Hof', not specific venue"
            }
        ]
    }
    
    # Unverified locations
    unverified = {
        "locations": {
            "MAKkultur": {
                "name": "MAKkultur",
                "lat": 50.3167,
                "lon": 11.9167,
                "occurrence_count": 12,
                "sources": ["Frankenpost", "Facebook"],
                "first_seen": "2025-11-01T08:00:00",
                "last_seen": "2026-01-15T16:00:00"
            }
        }
    }
    
    # Verified locations
    verified = {
        "locations": {
            "MAKkultur Bayreuth": {
                "name": "MAKkultur Bayreuth",
                "lat": 49.9450,
                "lon": 11.5770,
                "address": "Maximilianstraße 10, 95444 Bayreuth"
            }
        }
    }
    
    # Reviewer notes
    reviewer_notes = {
        "pending_1": [
            {
                "type": "warning",
                "message": "Location needs verification - coordinates missing",
                "created_at": "2026-01-15T16:30:00"
            }
        ]
    }
    
    # Write all test data
    with open(assets_json / 'events.json', 'w') as f:
        json.dump(published, f)
    with open(assets_json / 'pending_events.json', 'w') as f:
        json.dump(pending, f)
    with open(assets_json / 'rejected_events.json', 'w') as f:
        json.dump(rejected, f)
    with open(assets_json / 'unverified_locations.json', 'w') as f:
        json.dump(unverified, f)
    with open(assets_json / 'verified_locations.json', 'w') as f:
        json.dump(verified, f)
    with open(assets_json / 'reviewer_notes.json', 'w') as f:
        json.dump(reviewer_notes, f)
    
    return base_path


def test_context_aggregation():
    """Test context aggregation with all data sources."""
    print("\n" + "="*60)
    print("Test: Context Aggregation")
    print("="*60)
    
    base_path = create_test_data_directory()
    
    try:
        aggregator = EventContextAggregator(base_path)
        
        # Get pending event
        pending_event = aggregator.pending_events[0]
        
        # Aggregate context
        context = aggregator.aggregate_context(pending_event)
        
        # Verify context was populated
        checks = {
            "Previous rejections found": len(context.previous_rejections) > 0,
            "Similar events found": len(context.similar_events) > 0,
            "Unverified location data found": context.unverified_location_data is not None,
            "Verified location suggestions found": len(context.verified_location_suggestions) > 0,
            "Reviewer notes found": len(context.reviewer_notes) > 0,
            "Validation performed": context.validation_result is not None,
            "Attention reasons identified": len(context.needs_attention_reasons) > 0,
        }
        
        passed = sum(1 for check, result in checks.items() if result)
        failed = len(checks) - passed
        
        print("\nContext Components:")
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
        
        # Print full context summary
        print("\n" + context.get_summary())
        
        print(f"\nResults: {passed}/{len(checks)} checks passed")
        return failed == 0
        
    finally:
        import shutil
        shutil.rmtree(base_path)


def test_similar_event_detection():
    """Test detection of similar events from history."""
    print("\n" + "="*60)
    print("Test: Similar Event Detection")
    print("="*60)
    
    base_path = create_test_data_directory()
    
    try:
        aggregator = EventContextAggregator(base_path)
        pending_event = aggregator.pending_events[0]
        context = aggregator.aggregate_context(pending_event)
        
        # Should find the published jazz concert at MAKkultur
        similar_found = False
        for similar in context.similar_events:
            if similar.get('location', {}).get('name') == 'MAKkultur':
                similar_found = True
                print(f"  ✓ Found similar event: {similar.get('title')}")
                print(f"    Location: {similar.get('location', {}).get('name')}")
                print(f"    Coordinates: ({similar.get('location', {}).get('lat')}, {similar.get('location', {}).get('lon')})")
                break
        
        if similar_found:
            print("\n  💡 Editor can use coordinates from similar event!")
            return True
        else:
            print("  ✗ No similar events found (should have found MAKkultur)")
            return False
            
    finally:
        import shutil
        shutil.rmtree(base_path)


def test_location_intelligence():
    """Test location intelligence from unverified/verified data."""
    print("\n" + "="*60)
    print("Test: Location Intelligence")
    print("="*60)
    
    base_path = create_test_data_directory()
    
    try:
        aggregator = EventContextAggregator(base_path)
        pending_event = aggregator.pending_events[0]
        context = aggregator.aggregate_context(pending_event)
        
        checks = []
        
        # Check unverified location data
        if context.unverified_location_data:
            count = context.unverified_location_data.get('occurrence_count', 0)
            print(f"  ✓ Unverified location data: seen {count} times")
            checks.append(True)
        else:
            print(f"  ✗ No unverified location data")
            checks.append(False)
        
        # Check verified location suggestions
        if context.verified_location_suggestions:
            print(f"  ✓ Verified suggestions: {len(context.verified_location_suggestions)} found")
            for suggestion in context.verified_location_suggestions:
                print(f"    - {suggestion['name']}")
            checks.append(True)
        else:
            print(f"  ✗ No verified location suggestions")
            checks.append(False)
        
        return all(checks)
        
    finally:
        import shutil
        shutil.rmtree(base_path)


def test_attention_flags():
    """Test attention need analysis."""
    print("\n" + "="*60)
    print("Test: Attention Flags")
    print("="*60)
    
    base_path = create_test_data_directory()
    
    try:
        aggregator = EventContextAggregator(base_path)
        pending_event = aggregator.pending_events[0]
        context = aggregator.aggregate_context(pending_event)
        
        print(f"\n  Event needs attention for {len(context.needs_attention_reasons)} reason(s):")
        for reason in context.needs_attention_reasons:
            print(f"    - {reason}")
        
        # Should flag missing coordinates and previous rejection
        expected_flags = ['coordinates', 'rejected']
        found_flags = [
            any(expected in reason.lower() for reason in context.needs_attention_reasons)
            for expected in expected_flags
        ]
        
        if all(found_flags):
            print(f"\n  ✓ All expected attention flags present")
            return True
        else:
            print(f"\n  ✗ Some attention flags missing")
            return False
            
    finally:
        import shutil
        shutil.rmtree(base_path)


def main():
    """Run all tests."""
    print("\n" + "═"*60)
    print("EVENT CONTEXT AGGREGATOR TEST SUITE")
    print("═"*60)
    
    tests = [
        ("Context Aggregation", test_context_aggregation),
        ("Similar Event Detection", test_similar_event_detection),
        ("Location Intelligence", test_location_intelligence),
        ("Attention Flags", test_attention_flags),
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
        print("\n⚠️  Some tests failed.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        print("\n💡 Context aggregation helps editors by:")
        print("  - Showing similar events with valid coordinates")
        print("  - Highlighting previous rejections and reasons")
        print("  - Providing location intelligence from unverified/verified data")
        print("  - Flagging what needs attention")
        print("  - Validating event completeness")
        sys.exit(0)


if __name__ == '__main__':
    main()
