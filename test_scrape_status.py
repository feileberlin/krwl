#!/usr/bin/env python3
"""
Test that scraper writes correct status file
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


def test_scrape_status_file():
    """Test that scraper creates status file with correct information"""
    print("\n=== Testing Scrape Status File Generation ===")
    
    # Setup test environment
    test_dir = tempfile.mkdtemp(prefix='krwl_status_test_')
    test_path = Path(test_dir)
    
    try:
        # Add src to path
        repo_root = Path(__file__).parent
        sys.path.insert(0, str(repo_root / 'src'))
        
        from modules.scraper import EventScraper
        
        # Create static directory
        static_dir = test_path / 'static'
        static_dir.mkdir(exist_ok=True)
        
        # Create initial files
        pending_events = {
            'pending_events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(static_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        events = {
            'events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(static_dir / 'events.json', 'w') as f:
            json.dump(events, f, indent=2)
        
        # Create rejected events file
        rejected_events = {
            'rejected_events': [],
            'last_updated': datetime.now().isoformat()
        }
        with open(static_dir / 'rejected_events.json', 'w') as f:
            json.dump(rejected_events, f, indent=2)
        
        # Create test config
        config = {
            'scraping': {
                'sources': []  # No sources = no events scraped
            },
            'map': {
                'default_center': {
                    'lat': 50.3167,
                    'lon': 11.9167
                }
            }
        }
        
        # Test 1: Status file is created
        print("Test 1: Checking status file creation...")
        scraper = EventScraper(config, test_path)
        scraper.scrape_all_sources()
        
        status_file = test_path / '.scrape_status'
        if status_file.exists():
            print("✓ Status file created")
        else:
            print("✗ Status file not created")
            return False
        
        # Test 2: Status file has correct structure
        print("Test 2: Checking status file structure...")
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        required_keys = ['scraped', 'added', 'duplicates', 'rejected', 'timestamp']
        if all(key in status for key in required_keys):
            print(f"✓ Status file has all required keys: {required_keys}")
        else:
            print(f"✗ Status file missing keys. Found: {list(status.keys())}")
            return False
        
        # Test 3: Status file has correct values for empty scrape
        print("Test 3: Checking status values for empty scrape...")
        if (status['scraped'] == 0 and 
            status['added'] == 0 and 
            status['duplicates'] == 0 and 
            status['rejected'] == 0):
            print("✓ Status values correct for empty scrape")
        else:
            print(f"✗ Status values incorrect: {status}")
            return False
        
        # Test 4: Status file updates when events are added
        print("Test 4: Checking status updates with new event...")
        scraper.create_manual_event(
            title='Test Event',
            description='Test Description',
            location_name='Test Location',
            lat=50.3167,
            lon=11.9167,
            start_time=datetime.now().isoformat()
        )
        
        # Scrape again (should find no new events since we manually added)
        scraper.scrape_all_sources()
        
        with open(status_file, 'r') as f:
            status2 = json.load(f)
        
        # Since we manually added an event, scraping should find 0 new events
        if status2['added'] == 0:
            print("✓ Status correctly shows 0 new events after manual addition")
        else:
            print(f"✗ Status shows unexpected value: {status2['added']}")
            return False
        
        print("\n✓ All status file tests passed")
        return True
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_workflow_compatibility():
    """Test that status file format works with workflow bash commands"""
    print("\n=== Testing Workflow Compatibility ===")
    
    test_dir = tempfile.mkdtemp(prefix='krwl_workflow_test_')
    test_path = Path(test_dir)
    
    try:
        # Create a sample status file
        status = {
            'scraped': 5,
            'added': 2,
            'duplicates': 2,
            'rejected': 1,
            'timestamp': datetime.now().isoformat()
        }
        
        status_file = test_path / '.scrape_status'
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # Test that Python one-liner works (as used in workflow)
        import subprocess
        
        result = subprocess.run(
            ['python3', '-c', f"import json; print(json.load(open('{status_file}'))['added'])"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip() == '2':
            print("✓ Workflow Python one-liner works correctly")
            return True
        else:
            print(f"✗ Workflow command failed: {result.stderr}")
            return False
            
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    print("=" * 70)
    print("KRWL HOF Scrape Status Test Suite")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(test_scrape_status_file())
    results.append(test_workflow_compatibility())
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} test groups passed")
    print("=" * 70)
    
    sys.exit(0 if all(results) else 1)
