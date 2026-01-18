#!/usr/bin/env python3
"""
KRWL HOF Rejected Events Testing Module

Tests the auto-reject functionality for recurring events:
- Loading and saving rejected events
- Checking if an event is rejected
- Adding events to rejected list
- Integration with scraper to auto-reject matching events
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


class RejectedEventsTester:
    """Tests rejected events functionality"""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Add src to path for imports
        sys.path.insert(0, str(self.repo_root / 'src'))
        
        # Create temporary test directory
        self.test_dir = None
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            print(f"✓ {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            return False
    
    def setup_test_environment(self):
        """Create temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix='krwl_rejected_test_')
        test_path = Path(self.test_dir)
        
        # Create assets/json directory (for events and rejected_events.json)
        assets_json_dir = test_path / 'assets' / 'json'
        assets_json_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial files
        pending_events = {
            'pending_events': [],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(assets_json_dir / 'pending_events.json', 'w') as f:
            json.dump(pending_events, f, indent=2)
        
        events = {
            'events': [],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(assets_json_dir / 'events.json', 'w') as f:
            json.dump(events, f, indent=2)
        
        return test_path
        
    def cleanup_test_environment(self):
        """Clean up temporary test environment"""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
            
    def test_load_rejected_events(self):
        """Test loading rejected events (creates file if not exists)"""
        test_path = self.setup_test_environment()
        
        try:
            from modules.utils import load_rejected_events
            
            # Load rejected events (should create file if not exists)
            rejected_data = load_rejected_events(test_path)
            
            self.assert_test(
                'rejected_events' in rejected_data,
                "Load rejected events creates structure",
                "Missing 'rejected_events' key"
            )
            
            self.assert_test(
                isinstance(rejected_data['rejected_events'], list),
                "Rejected events is a list",
                "rejected_events is not a list"
            )
            
            # Check file was created
            rejected_file = test_path / 'assets' / 'json' / 'rejected_events.json'
            self.assert_test(
                rejected_file.exists(),
                "Rejected events file created",
                f"File not found at {rejected_file}"
            )
            
        finally:
            self.cleanup_test_environment()
            
    def test_add_rejected_event(self):
        """Test adding an event to rejected list"""
        test_path = self.setup_test_environment()
        
        try:
            from modules.utils import add_rejected_event, load_rejected_events
            
            # Add a rejected event
            add_rejected_event(test_path, "Spam Event", "Spam Source")
            
            # Load and verify
            rejected_data = load_rejected_events(test_path)
            rejected_list = rejected_data['rejected_events']
            
            self.assert_test(
                len(rejected_list) == 1,
                "Rejected event added to list",
                f"Expected 1 event, found {len(rejected_list)}"
            )
            
            if len(rejected_list) > 0:
                event = rejected_list[0]
                self.assert_test(
                    event['title'] == "Spam Event",
                    "Rejected event has correct title"
                )
                self.assert_test(
                    event['source'] == "Spam Source",
                    "Rejected event has correct source"
                )
                self.assert_test(
                    'rejected_at' in event,
                    "Rejected event has timestamp"
                )
            
        finally:
            self.cleanup_test_environment()
            
    def test_is_event_rejected(self):
        """Test checking if an event is rejected"""
        test_path = self.setup_test_environment()
        
        try:
            from modules.utils import add_rejected_event, is_event_rejected, load_rejected_events
            
            # Add rejected events
            add_rejected_event(test_path, "Spam Event", "Spam Source")
            add_rejected_event(test_path, "Another Spam", "Another Source")
            
            rejected_data = load_rejected_events(test_path)
            rejected_list = rejected_data['rejected_events']
            
            # Test exact match
            self.assert_test(
                is_event_rejected(rejected_list, "Spam Event", "Spam Source"),
                "Detects rejected event (exact match)"
            )
            
            # Test case insensitive match
            self.assert_test(
                is_event_rejected(rejected_list, "SPAM EVENT", "spam source"),
                "Detects rejected event (case insensitive)"
            )
            
            # Test whitespace handling
            self.assert_test(
                is_event_rejected(rejected_list, "  Spam Event  ", "  Spam Source  "),
                "Detects rejected event (with whitespace)"
            )
            
            # Test non-matching event
            self.assert_test(
                not is_event_rejected(rejected_list, "Good Event", "Good Source"),
                "Does not match non-rejected event"
            )
            
            # Test partial match (should not match)
            self.assert_test(
                not is_event_rejected(rejected_list, "Spam Event", "Different Source"),
                "Does not match partial (different source)"
            )
            
            self.assert_test(
                not is_event_rejected(rejected_list, "Different Title", "Spam Source"),
                "Does not match partial (different title)"
            )
            
        finally:
            self.cleanup_test_environment()
            
    def test_duplicate_rejection(self):
        """Test that adding same event twice doesn't create duplicates"""
        test_path = self.setup_test_environment()
        
        try:
            from modules.utils import add_rejected_event, load_rejected_events
            
            # Add same event twice
            add_rejected_event(test_path, "Spam Event", "Spam Source")
            add_rejected_event(test_path, "Spam Event", "Spam Source")
            
            rejected_data = load_rejected_events(test_path)
            rejected_list = rejected_data['rejected_events']
            
            self.assert_test(
                len(rejected_list) == 1,
                "No duplicate rejected events",
                f"Expected 1 event, found {len(rejected_list)}"
            )
            
        finally:
            self.cleanup_test_environment()
            
    def test_scraper_integration(self):
        """Test scraper filters out rejected events"""
        test_path = self.setup_test_environment()
        
        try:
            from modules.utils import add_rejected_event, is_event_rejected, load_rejected_events
            
            # Add rejected event
            add_rejected_event(test_path, "Recurring Spam", "Test Source")
            
            rejected_data = load_rejected_events(test_path)
            rejected_list = rejected_data['rejected_events']
            
            # Simulate scraper checking events
            test_events = [
                {"title": "Recurring Spam", "source": "Test Source"},
                {"title": "Good Event", "source": "Test Source"},
                {"title": "Another Event", "source": "Other Source"}
            ]
            
            filtered_events = [
                e for e in test_events 
                if not is_event_rejected(rejected_list, e['title'], e['source'])
            ]
            
            self.assert_test(
                len(filtered_events) == 2,
                "Scraper filters rejected events",
                f"Expected 2 events after filtering, found {len(filtered_events)}"
            )
            
            self.assert_test(
                not any(e['title'] == "Recurring Spam" for e in filtered_events),
                "Rejected event not in filtered results"
            )
            
        finally:
            self.cleanup_test_environment()
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("KRWL HOF Rejected Events Tests")
        print("=" * 60 + "\n")
        
        print("Testing rejected events functionality...")
        print("-" * 60)
        
        self.test_load_rejected_events()
        self.test_add_rejected_event()
        self.test_is_event_rejected()
        self.test_duplicate_rejection()
        self.test_scraper_integration()
        
        print("\n" + "=" * 60)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print("=" * 60 + "\n")
        
        return self.tests_failed == 0


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test rejected events functionality'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--repo-root',
        type=str,
        default=None,
        help='Path to repository root (default: current directory)'
    )
    
    args = parser.parse_args()
    
    tester = RejectedEventsTester(
        repo_root=args.repo_root,
        verbose=args.verbose
    )
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
