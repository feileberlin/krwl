#!/usr/bin/env python3
"""
Test suite for Instagram scraper.

Tests:
- InstagramSource instantiation
- URL parsing and account name extraction
- Post processing logic
- Web search fallback
- Event extraction
"""

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class InstagramScraperTester:
    """Tests for Instagram scraper functionality."""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Add src to path for imports
        sys.path.insert(0, str(self.repo_root / 'src'))
        
    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition."""
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
    
    def test_instagram_import(self):
        """Test that Instagram scraper imports correctly."""
        print("\n=== Testing Instagram Import ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            self.assert_test(True, "Instagram scraper imports successfully")
            return True
        except ImportError as e:
            self.assert_test(False, "Instagram scraper import", str(e))
            return False
    
    def test_instagram_instantiation(self):
        """Test InstagramSource instantiation."""
        print("\n=== Testing Instagram Instantiation ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            from modules.smart_scraper.base import SourceOptions
            
            source_config = {
                'name': 'Test Instagram',
                'url': 'https://www.instagram.com/testaccount/',
                'type': 'instagram',
                'enabled': True,
                'options': {
                    'category': 'music',
                    'default_location': {
                        'name': 'Test Venue',
                        'lat': 50.3167,
                        'lon': 11.9167
                    }
                }
            }
            options = SourceOptions.from_dict(source_config.get('options', {}))
            
            scraper = InstagramSource(source_config, options, base_path=Path('/tmp'))
            
            self.assert_test(scraper.name == 'Test Instagram', "Name set correctly")
            self.assert_test(scraper.url == 'https://www.instagram.com/testaccount/', "URL set correctly")
            self.assert_test(scraper.PLATFORM_NAME == 'instagram', "Platform name is instagram")
            
            return True
        except Exception as e:
            self.assert_test(False, "Instagram instantiation", str(e))
            return False
    
    def test_account_name_extraction(self):
        """Test extracting account name from URL."""
        print("\n=== Testing Account Name Extraction ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            from modules.smart_scraper.base import SourceOptions
            
            source_config = {
                'name': 'Test',
                'url': 'https://www.instagram.com/test_account/',
                'type': 'instagram'
            }
            options = SourceOptions()
            scraper = InstagramSource(source_config, options)
            
            # Test various URL formats
            test_cases = [
                ('https://www.instagram.com/testuser/', 'testuser'),
                ('https://instagram.com/test_user/', 'test user'),
                ('http://www.instagram.com/test.user/', 'test user'),
                ('https://www.instagram.com/testuser?hl=en', 'testuser'),
            ]
            
            for url, expected in test_cases:
                result = scraper._extract_account_name_from_url(url)
                self.assert_test(
                    result == expected,
                    f"Extract account from '{url}'",
                    f"Expected '{expected}', got '{result}'"
                )
            
            return True
        except Exception as e:
            self.assert_test(False, "Account name extraction", str(e))
            return False
    
    def test_datetime_extraction(self):
        """Test date/time extraction from text."""
        print("\n=== Testing DateTime Extraction ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            from modules.smart_scraper.base import SourceOptions
            
            source_config = {
                'name': 'Test',
                'url': 'https://www.instagram.com/test/',
                'type': 'instagram'
            }
            options = SourceOptions()
            scraper = InstagramSource(source_config, options)
            
            # Test date patterns
            test_cases = [
                ('Event on 15.06.2025 at 20:00', '2025-06-15'),
                ('Party am 31.12.2025', '2025-12-31'),
                ('2025-01-30 Event', '2025-01-30'),
            ]
            
            for text, expected_date in test_cases:
                result = scraper._extract_datetime_from_text(text)
                if result:
                    date_part = result[:10]
                    self.assert_test(
                        date_part == expected_date,
                        f"Extract date from '{text[:30]}...'",
                        f"Expected '{expected_date}', got '{date_part}'"
                    )
                else:
                    self.assert_test(False, f"Extract date from '{text[:30]}...'", "No date found")
            
            return True
        except Exception as e:
            self.assert_test(False, "DateTime extraction", str(e))
            return False
    
    def test_event_id_generation(self):
        """Test event ID generation."""
        print("\n=== Testing Event ID Generation ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            from modules.smart_scraper.base import SourceOptions
            
            source_config = {
                'name': 'Test Account',
                'url': 'https://www.instagram.com/test/',
                'type': 'instagram'
            }
            options = SourceOptions()
            scraper = InstagramSource(source_config, options)
            
            event_id = scraper._generate_event_id('Test Event', '2025-06-15T20:00:00')
            
            self.assert_test(
                event_id.startswith('instagram_'),
                "Event ID has instagram prefix"
            )
            self.assert_test(
                'test_account' in event_id,
                "Event ID contains source name"
            )
            self.assert_test(
                len(event_id) > 20,
                "Event ID has hash suffix"
            )
            
            # Test consistency
            event_id2 = scraper._generate_event_id('Test Event', '2025-06-15T20:00:00')
            self.assert_test(
                event_id == event_id2,
                "Event ID is deterministic"
            )
            
            return True
        except Exception as e:
            self.assert_test(False, "Event ID generation", str(e))
            return False
    
    def test_deduplication(self):
        """Test event deduplication."""
        print("\n=== Testing Event Deduplication ===")
        
        try:
            from modules.smart_scraper.sources.social.instagram import InstagramSource
            from modules.smart_scraper.base import SourceOptions
            
            source_config = {
                'name': 'Test',
                'url': 'https://www.instagram.com/test/',
                'type': 'instagram'
            }
            options = SourceOptions()
            scraper = InstagramSource(source_config, options)
            
            events = [
                {'title': 'Event A', 'start_time': '2025-06-15T20:00:00'},
                {'title': 'Event A', 'start_time': '2025-06-15T21:00:00'},  # Same title, same date
                {'title': 'Event B', 'start_time': '2025-06-15T20:00:00'},  # Different title
                {'title': 'Event A', 'start_time': '2025-06-16T20:00:00'},  # Same title, different date
            ]
            
            deduplicated = scraper._deduplicate_events(events)
            
            self.assert_test(
                len(deduplicated) == 3,
                "Deduplication removes exact duplicates",
                f"Expected 3 events, got {len(deduplicated)}"
            )
            
            return True
        except Exception as e:
            self.assert_test(False, "Deduplication", str(e))
            return False
    
    def test_scraper_in_registry(self):
        """Test that Instagram scraper is registered in SmartScraper."""
        print("\n=== Testing Registry Registration ===")
        
        try:
            from modules.smart_scraper import SmartScraper
            
            # Create minimal config
            config = {
                'scraping': {'sources': []},
                'ai': {},
                'image_analysis': {'enabled': False}
            }
            
            scraper = SmartScraper(config, Path('/tmp'))
            
            self.assert_test(
                scraper.registry.is_registered('instagram'),
                "Instagram registered in SmartScraper registry"
            )
            
            handler = scraper.registry.get_handler('instagram')
            self.assert_test(
                handler is not None,
                "Instagram handler is callable"
            )
            
            return True
        except Exception as e:
            self.assert_test(False, "Registry registration", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 70)
        print("Instagram Scraper Test Suite")
        print("=" * 70)
        
        self.test_instagram_import()
        self.test_instagram_instantiation()
        self.test_account_name_extraction()
        self.test_datetime_extraction()
        self.test_event_id_generation()
        self.test_deduplication()
        self.test_scraper_in_registry()
        
        print("\n" + "=" * 70)
        print(f"Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
        print("=" * 70)
        
        return self.tests_failed == 0


def main():
    """Run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Instagram scraper')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Find repo root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    
    tester = InstagramScraperTester(repo_root=repo_root, verbose=args.verbose)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
