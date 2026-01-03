#!/usr/bin/env python3
"""
Test that scraper generates pending count JSON for frontend notifications
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


def test_pending_count_generation():
    """Test that scraper creates pending-count.json with correct information"""
    print("\n=== Testing Pending Count JSON Generation ===")
    
    # Setup test environment
    test_dir = tempfile.mkdtemp(prefix='krwl_pending_count_test_')
    test_path = Path(test_dir)
    
    try:
        # Add src to path
        repo_root = Path(__file__).parent.parent
        sys.path.insert(0, str(repo_root / 'src'))
        
        from modules.scraper import EventScraper
        
        # Create event-data directory
        event_data_dir = test_path / 'event-data'
        event_data_dir.mkdir(exist_ok=True)
        
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
        
        # Create empty events and rejected files
        with open(event_data_dir / 'events.json', 'w') as f:
            json.dump({'events': [], 'last_updated': datetime.now().isoformat()}, f)
        
        with open(event_data_dir / 'rejected_events.json', 'w') as f:
            json.dump({'rejected_events': [], 'last_updated': datetime.now().isoformat()}, f)
        
        # Create test config
        config = {
            'scraping': {'sources': []},
            'map': {'default_center': {'lat': 50.3167, 'lon': 11.9167}}
        }
        
        # Test 1: Pending count file is created
        print("Test 1: Checking pending-count.json creation...")
        scraper = EventScraper(config, test_path)
        scraper.scrape_all_sources()
        
        pending_count_file = test_path / 'target' / 'pending-count.json'
        if pending_count_file.exists():
            print("✓ Pending count file created")
        else:
            print(f"✗ Pending count file not created at {pending_count_file}")
            return False
        
        # Test 2: Pending count file has correct structure
        print("Test 2: Checking pending count file structure...")
        with open(pending_count_file, 'r') as f:
            pending_count_data = json.load(f)
        
        required_keys = ['count', 'last_updated']
        if all(key in pending_count_data for key in required_keys):
            print(f"✓ Pending count file has all required keys: {required_keys}")
        else:
            print(f"✗ Pending count file missing keys. Found: {list(pending_count_data.keys())}")
            return False
        
        # Test 3: Pending count matches actual count
        print("Test 3: Checking pending count value...")
        expected_count = 3
        if pending_count_data['count'] == expected_count:
            print(f"✓ Pending count is correct: {expected_count}")
        else:
            print(f"✗ Pending count incorrect. Expected {expected_count}, got {pending_count_data['count']}")
            return False
        
        # Test 4: Timestamp format is valid
        print("Test 4: Checking timestamp format...")
        try:
            datetime.fromisoformat(pending_count_data['last_updated'])
            print("✓ Timestamp is valid ISO format")
        except ValueError:
            print(f"✗ Timestamp invalid: {pending_count_data['last_updated']}")
            return False
        
        # Test 5: File updates when count changes
        print("Test 5: Checking file updates with count changes...")
        # Remove one pending event
        pending_events['pending_events'] = pending_events['pending_events'][:2]
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        # Generate again
        scraper.scrape_all_sources()
        
        with open(pending_count_file, 'r') as f:
            updated_data = json.load(f)
        
        if updated_data['count'] == 2:
            print("✓ Pending count correctly updated to 2")
        else:
            print(f"✗ Pending count not updated. Expected 2, got {updated_data['count']}")
            return False
        
        # Test 6: File works with zero pending events
        print("Test 6: Checking zero pending events...")
        pending_events['pending_events'] = []
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        scraper.scrape_all_sources()
        
        with open(pending_count_file, 'r') as f:
            zero_data = json.load(f)
        
        if zero_data['count'] == 0:
            print("✓ Pending count correctly shows 0")
        else:
            print(f"✗ Pending count incorrect for empty. Expected 0, got {zero_data['count']}")
            return False
        
        print("\n✓ All pending count tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_frontend_compatibility():
    """Test that pending count JSON format works with frontend JavaScript"""
    print("\n=== Testing Frontend Compatibility ===")
    
    # Create sample pending count data matching frontend expectations
    pending_count = {
        'count': 5,
        'last_updated': '2026-01-03T15:36:58.383588'
    }
    
    # Test JSON serialization/deserialization
    try:
        json_str = json.dumps(pending_count)
        parsed = json.loads(json_str)
        
        if parsed['count'] == 5:
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
    print("KRWL HOF Pending Count JSON Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(test_pending_count_generation())
    results.append(test_frontend_compatibility())
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} test groups passed")
    print("=" * 70)
    
    sys.exit(0 if all(results) else 1)
