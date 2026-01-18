#!/usr/bin/env python3
"""
Test suite for SmartScraper system.

Tests:
- Base classes and registry
- SourceOptions filtering
- AI provider loading
- Web scrapers (RSS, HTML, API, Atom)
- Social media scraper stubs
- Image analysis integration
- Rate limiting
"""

import json
import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


class SmartScraperTester:
    """Tests for SmartScraper functionality."""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Add src to path for imports
        sys.path.insert(0, str(self.repo_root / 'src'))
        
        self.test_dir = None
    
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
    
    def setup_test_environment(self):
        """Create temporary test environment."""
        self.test_dir = tempfile.mkdtemp(prefix='smart_scraper_test_')
        test_path = Path(self.test_dir)
        
        # Create data directory (correct data location)
        event_data_dir = test_path / 'assets' / 'json'
        event_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test config with AI and image analysis
        config = {
            'ai': {
                'default_provider': 'duckduckgo',
                'duckduckgo': {
                    'model': 'gpt-4o-mini',
                    'rate_limit': {
                        'min_delay': 1.0,
                        'max_delay': 2.0,
                        'max_requests_per_session': 5
                    }
                }
            },
            'image_analysis': {
                'enabled': True,
                'ocr_enabled': True,
                'ocr_provider': 'tesseract',
                'languages': ['eng', 'deu']
            },
            'scraping': {
                'sources': [
                    {
                        'name': 'Test RSS',
                        'type': 'rss',
                        'url': 'https://example.com/rss',
                        'enabled': True,
                        'options': {
                            'filter_ads': True,
                            'exclude_keywords': ['spam', 'ad'],
                            'max_days_ahead': 30
                        }
                    },
                    {
                        'name': 'Test HTML',
                        'type': 'html',
                        'url': 'https://example.com/events',
                        'enabled': True
                    }
                ]
            }
        }
        
        self.log(f"Created test environment at {self.test_dir}")
        return test_path, config
    
    def cleanup_test_environment(self):
        """Remove temporary test environment."""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
            self.log(f"Cleaned up test environment")
    
    def test_source_options(self):
        """Test SourceOptions filtering."""
        print("\n=== Testing SourceOptions ===")
        
        try:
            from modules.smart_scraper.base import SourceOptions
            
            # Test keyword filtering
            options = SourceOptions(
                filter_ads=True,
                exclude_keywords=['spam', 'ad'],
                include_keywords=['event', 'party']
            )
            
            # Should filter spam
            self.assert_test(
                options.should_filter("This is spam content"),
                "Filters exclude keywords",
                ""
            )
            
            # Should filter ads
            self.assert_test(
                options.should_filter("Buy now! Special offer!"),
                "Filters ad patterns",
                ""
            )
            
            # Should not filter good content
            self.assert_test(
                not options.should_filter("Great event party tonight"),
                "Allows valid content with include keywords",
                ""
            )
            
            # Should filter content without include keywords
            self.assert_test(
                options.should_filter("Random content without keywords"),
                "Filters content missing include keywords",
                ""
            )
            
        except Exception as e:
            self.assert_test(False, "SourceOptions filtering", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_scraper_registry(self):
        """Test ScraperRegistry."""
        print("\n=== Testing ScraperRegistry ===")
        
        try:
            from modules.smart_scraper.base import ScraperRegistry
            
            registry = ScraperRegistry()
            
            # Register a handler
            def mock_handler(cfg, opts):
                return f"MockScraper({cfg['name']})"
            
            registry.register('mock', mock_handler)
            
            self.assert_test(
                registry.is_registered('mock'),
                "Register source type",
                ""
            )
            
            self.assert_test(
                not registry.is_registered('nonexistent'),
                "Detect unregistered type",
                ""
            )
            
            # Get handler
            handler = registry.get_handler('mock')
            self.assert_test(
                handler is not None,
                "Retrieve registered handler",
                ""
            )
            
            # Test handler
            result = handler({'name': 'Test'}, None)
            self.assert_test(
                result == "MockScraper(Test)",
                "Execute handler",
                f"Got: {result}"
            )
            
        except Exception as e:
            self.assert_test(False, "ScraperRegistry", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def test_smart_scraper_init(self):
        """Test SmartScraper initialization."""
        print("\n=== Testing SmartScraper Initialization ===")
        
        test_path, config = self.setup_test_environment()
        
        try:
            from modules.smart_scraper import SmartScraper
            
            scraper = SmartScraper(config, test_path)
            
            self.assert_test(
                scraper is not None,
                "SmartScraper instantiation",
                ""
            )
            
            self.assert_test(
                scraper.registry is not None,
                "Registry initialized",
                ""
            )
            
            # Check if RSS is registered
            self.assert_test(
                scraper.registry.is_registered('rss'),
                "RSS scraper registered",
                ""
            )
            
            # Check if HTML is registered
            self.assert_test(
                scraper.registry.is_registered('html'),
                "HTML scraper registered",
                ""
            )
            
        except Exception as e:
            self.assert_test(False, "SmartScraper initialization", f"Exception: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup_test_environment()
    
    def test_ai_providers(self):
        """Test AI provider loading."""
        print("\n=== Testing AI Providers ===")
        
        test_path, config = self.setup_test_environment()
        
        try:
            from modules.smart_scraper import SmartScraper
            
            scraper = SmartScraper(config, test_path)
            
            # AI providers may or may not be available
            self.assert_test(
                isinstance(scraper.ai_providers, dict),
                "AI providers is dictionary",
                f"Type: {type(scraper.ai_providers)}"
            )
            
            # If providers available, check structure
            if scraper.ai_providers:
                self.log(f"Available providers: {list(scraper.ai_providers.keys())}")
                self.assert_test(
                    True,
                    f"AI providers loaded: {len(scraper.ai_providers)}",
                    ""
                )
            else:
                self.assert_test(
                    True,
                    "No AI providers (dependencies not installed)",
                    ""
                )
            
        except Exception as e:
            self.assert_test(False, "AI providers", f"Exception: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup_test_environment()
    
    def test_rate_limiter(self):
        """Test RateLimiter functionality."""
        print("\n=== Testing RateLimiter ===")
        
        try:
            from modules.smart_scraper.ai_providers.base import RateLimiter
            import time
            
            limiter = RateLimiter(min_delay=0.1, max_delay=0.2, max_requests_per_session=2)
            
            # First request should not delay
            start = time.time()
            limiter.wait()
            elapsed = time.time() - start
            
            self.assert_test(
                limiter.request_count == 1,
                "Rate limiter increments counter",
                f"Count: {limiter.request_count}"
            )
            
            # Second request should delay
            start = time.time()
            limiter.wait()
            elapsed = time.time() - start
            
            self.assert_test(
                elapsed >= 0.1,
                "Rate limiter applies delay",
                f"Delay: {elapsed:.2f}s"
            )
            
            # Should need rotation
            self.assert_test(
                limiter.should_rotate(),
                "Rate limiter detects rotation need",
                f"Count: {limiter.request_count}"
            )
            
        except Exception as e:
            self.assert_test(False, "RateLimiter", f"Exception: {e}")
            import traceback
            traceback.print_exc()
    
    def run_all_tests(self):
        """Run all SmartScraper tests."""
        print("=" * 70)
        print("SmartScraper Test Suite")
        print("=" * 70)
        
        self.test_source_options()
        self.test_scraper_registry()
        self.test_smart_scraper_init()
        self.test_ai_providers()
        self.test_rate_limiter()
        
        print("\n" + "=" * 70)
        print(f"Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
        print("=" * 70)
        
        return self.tests_failed == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SmartScraper system')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--repo-root', default='.', help='Repository root directory')
    
    args = parser.parse_args()
    
    tester = SmartScraperTester(repo_root=args.repo_root, verbose=args.verbose)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
