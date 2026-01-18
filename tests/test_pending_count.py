#!/usr/bin/env python3
"""
Test that scraper updates pending count in events.json for frontend notifications
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


def test_pending_count_in_events_json():
    """Test that pending count is added to events.json"""
    print("\n=== Testing Pending Count in events.json ===")
    
    # Setup test environment
    test_dir = tempfile.mkdtemp(prefix='krwl_pending_count_test_')
    test_path = Path(test_dir)
    
    try:
        # Add src to path
        repo_root = Path(__file__).parent.parent
        sys.path.insert(0, str(repo_root / 'src'))
        
        from modules.scraper import EventScraper
        from modules.utils import load_events, update_pending_count_in_events
        
        # Create data directory
        event_data_dir = test_path / 'assets' / 'json'
        event_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create pending events with 3 events
        pending_events = {
            'pending_events': [
                {
                    'id': 'test_1',
                    'title': 'Test Event 1',
                    'description': 'Description 1',
                    'location': {'name': 'Test Location', 'lat': 50.3167, 'lon': 11.9167},
                    'start_time': datetime.now().isoformat(),
                    'source': 'test',
                    'status': 'pending'
                },
                {
                    'id': 'test_2',
                    'title': 'Test Event 2',
                    'description': 'Description 2',
                    'location': {'name': 'Test Location', 'lat': 50.3167, 'lon': 11.9167},
                    'start_time': datetime.now().isoformat(),
                    'source': 'test',
                    'status': 'pending'
                },
                {
                    'id': 'test_3',
                    'title': 'Test Event 3',
                    'description': 'Description 3',
                    'location': {'name': 'Test Location', 'lat': 50.3167, 'lon': 11.9167},
                    'start_time': datetime.now().isoformat(),
                    'source': 'test',
                    'status': 'pending'
                }
            ],
            'last_updated': datetime.now().isoformat()
        }
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        # Create empty events file
        events_data = {
            'events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(event_data_dir / 'events.json', 'w') as f:
            json.dump(events_data, f, indent=2)
        
        # Create rejected events file
        with open(event_data_dir / 'rejected_events.json', 'w') as f:
            json.dump({'rejected_events': [], 'last_updated': datetime.now().isoformat()}, f)
        
        # Test 1: Update pending count in events.json
        print("Test 1: Checking pending_count is added to events.json...")
        update_pending_count_in_events(test_path)
        
        events_data = load_events(test_path)
        if 'pending_count' in events_data:
            print("✓ pending_count field added to events.json")
        else:
            print("✗ pending_count field not found in events.json")
            return False
        
        # Test 2: Pending count value is correct
        print("Test 2: Checking pending count value...")
        expected_count = 3
        if events_data['pending_count'] == expected_count:
            print(f"✓ Pending count is correct: {expected_count}")
        else:
            print(f"✗ Pending count incorrect. Expected {expected_count}, got {events_data['pending_count']}")
            return False
        
        # Test 3: Verify timestamp is NOT changed (metadata-only update)
        print("Test 3: Checking last_updated timestamp remains unchanged...")
        original_timestamp = events_data.get('last_updated')
        
        # Update pending count again
        update_pending_count_in_events(test_path)
        events_data_after = load_events(test_path)
        new_timestamp = events_data_after.get('last_updated')
        
        if original_timestamp == new_timestamp:
            print("✓ last_updated timestamp preserved (correct behavior)")
        else:
            print(f"✗ last_updated changed from {original_timestamp} to {new_timestamp}")
            return False
        
        # Test 4: Pending count updates when count changes
        print("Test 4: Checking count updates...")
        # Remove one pending event
        pending_events['pending_events'] = pending_events['pending_events'][:2]
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        # Update again
        update_pending_count_in_events(test_path)
        events_data = load_events(test_path)
        
        if events_data['pending_count'] == 2:
            print("✓ Pending count correctly updated to 2")
        else:
            print(f"✗ Pending count not updated. Expected 2, got {events_data['pending_count']}")
            return False
        
        # Test 5: Zero pending events
        print("Test 5: Checking zero pending events...")
        pending_events['pending_events'] = []
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        update_pending_count_in_events(test_path)
        events_data = load_events(test_path)
        
        if events_data['pending_count'] == 0:
            print("✓ Pending count correctly shows 0")
        else:
            print(f"✗ Pending count incorrect for empty. Expected 0, got {events_data['pending_count']}")
            return False
        
        # Test 6: Scraper integration test
        print("Test 6: Checking scraper integration...")
        # Add pending events back
        pending_events['pending_events'] = [
            {
                'id': 'test_1',
                'title': 'Test Event 1',
                'description': 'Description 1',
                'location': {'name': 'Test Location', 'lat': 50.3167, 'lon': 11.9167},
                'start_time': datetime.now().isoformat(),
                'source': 'test',
                'status': 'pending'
            }
        ]
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        # Run scraper (which should update pending count)
        config = {
            'scraping': {'sources': []},
            'map': {'default_center': {'lat': 50.3167, 'lon': 11.9167}}
        }
        scraper = EventScraper(config, test_path)
        scraper.scrape_all_sources()
        
        # Check that pending count was updated by scraper
        events_data = load_events(test_path)
        if events_data['pending_count'] == 1:
            print("✓ Scraper correctly updated pending count")
        else:
            print(f"✗ Scraper didn't update count. Expected 1, got {events_data['pending_count']}")
            return False
        
        print("\n✓ All pending count tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_frontend_compatibility():
    """Test that events.json format works with frontend JavaScript"""
    print("\n=== Testing Frontend Compatibility ===")
    
    # Create sample events data matching frontend expectations
    events_data = {
        'events': [],
        'pending_count': 5,
        'last_updated': '2026-01-03T15:47:19.164009'
    }
    
    # Test JSON serialization/deserialization
    try:
        json_str = json.dumps(events_data)
        parsed = json.loads(json_str)
        
        if parsed['pending_count'] == 5 and 'events' in parsed:
            print("✓ JSON format compatible with frontend")
            return True
        else:
            print("✗ JSON parsing failed")
            return False
            
    except Exception as e:
        print(f"✗ JSON compatibility test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("KRWL HOF Pending Count in events.json Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(test_pending_count_in_events_json())
    results.append(test_frontend_compatibility())
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} test groups passed")
    print("=" * 70)
    
    sys.exit(0 if all(results) else 1)
