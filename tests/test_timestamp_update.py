#!/usr/bin/env python3
"""
Test that timestamp is only updated when events are actually added
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


def test_timestamp_only_on_new_events():
    """Test that timestamp is only updated when new events are added"""
    print("\n=== Testing Timestamp Update Behavior ===")
    
    # Setup test environment
    test_dir = tempfile.mkdtemp(prefix='krwl_timestamp_test_')
    test_path = Path(test_dir)
    
    try:
        # Add src to path
        repo_root = Path(__file__).parent.parent
        sys.path.insert(0, str(repo_root / 'src'))
        
        from modules.scraper import EventScraper
        
        # Create data directory (correct data location)
        event_data_dir = test_path / 'assets' / 'json'
        event_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial pending_events.json with a specific timestamp
        initial_timestamp = "2026-01-01T10:00:00"
        pending_events = {
            'pending_events': [],
            'last_scraped': initial_timestamp
        }
        with open(event_data_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        # Create events.json
        events = {
            'events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(event_data_dir / 'events.json', 'w') as f:
            json.dump(events, f, indent=2)
        
        # Create rejected_events.json
        rejected_events = {
            'rejected_events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(event_data_dir / 'rejected_events.json', 'w') as f:
            json.dump(rejected_events, f, indent=2)
        
        # Create test config with no sources (so no events will be scraped)
        config = {
            'scraping': {
                'sources': []
            },
            'map': {
                'default_center': {
                    'lat': 50.3167,
                    'lon': 11.9167
                }
            }
        }
        
        # Test 1: Scraping with no new events should NOT update timestamp
        print("Test 1: Scraping with no sources (no new events)...")
        scraper = EventScraper(config, test_path)
        scraper.scrape_all_sources()
        
        with open(event_data_dir / 'pending_events.json', 'r') as f:
            data = json.load(f)
        
        if data['last_scraped'] == initial_timestamp:
            print("✓ Timestamp NOT updated when no events added (CORRECT)")
        else:
            print(f"✗ Timestamp was updated from {initial_timestamp} to {data['last_scraped']} (WRONG)")
            return False
        
        # Test 2: Adding a manual event should update timestamp
        print("\nTest 2: Adding a manual event...")
        scraper.create_manual_event(
            title='Test Event',
            description='Test Description',
            location_name='Test Location',
            lat=50.3167,
            lon=11.9167,
            start_time=datetime.now().isoformat()
        )
        
        with open(event_data_dir / 'pending_events.json', 'r') as f:
            data = json.load(f)
        
        if data['last_scraped'] != initial_timestamp:
            print(f"✓ Timestamp updated when event added: {initial_timestamp} → {data['last_scraped']}")
        else:
            print("✗ Timestamp NOT updated when event was added (WRONG)")
            return False
        
        # Test 3: Scraping again with no new events should NOT update timestamp
        print("\nTest 3: Scraping again with no new events...")
        second_timestamp = data['last_scraped']
        scraper.scrape_all_sources()
        
        with open(event_data_dir / 'pending_events.json', 'r') as f:
            data = json.load(f)
        
        if data['last_scraped'] == second_timestamp:
            print("✓ Timestamp NOT updated on second scrape with no new events (CORRECT)")
        else:
            print(f"✗ Timestamp was updated from {second_timestamp} to {data['last_scraped']} (WRONG)")
            return False
        
        print("\n✓ All timestamp tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    print("=" * 70)
    print("KRWL> Timestamp Update Test")
    print("=" * 70)
    
    success = test_timestamp_only_on_new_events()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ Test passed")
    else:
        print("✗ Test failed")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
