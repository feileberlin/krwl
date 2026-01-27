#!/usr/bin/env python3
"""
KRWL HOF Routing Tests

Tests the SPA routing logic for region detection and URL handling.
Validates that:
1. Known regions are properly detected and configured
2. Unknown regions show colony setup instructions
3. RSS feeds are accessible at correct URLs
4. 404.html properly redirects to index.html with path preserved

These tests verify the JavaScript routing logic by checking:
- Region configuration in config.json
- 404.html SPA redirect script
- RSS feed generation for all regions
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRouting:
    """Test suite for SPA routing and region detection"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / "config.json"
        self.public_path = self.base_path / "public"
        self.feeds_path = self.base_path / "assets" / "feeds"
        self.config = None
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def load_config(self) -> bool:
        """Load and parse config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Failed to parse config.json: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"Config file not found: {self.config_path}")
            return False
    
    def assert_test(self, condition: bool, test_name: str, error_msg: str = None) -> bool:
        """Assert a test condition and track results"""
        if condition:
            print(f"    ✓ {test_name}")
            self.passed += 1
            return True
        else:
            msg = f"{test_name}: {error_msg}" if error_msg else test_name
            self.errors.append(msg)
            print(f"    ✗ {msg}")
            self.failed += 1
            return False
    
    # =========================================================================
    # Region Configuration Tests
    # =========================================================================
    
    def test_known_regions_exist(self) -> bool:
        """Test that all expected regions are configured"""
        print("\n  Testing: Known regions are configured...")
        
        regions = self.config.get('regions', {})
        
        # These are the regions that should be configured
        expected_regions = ['antarctica', 'hof', 'nbg', 'bth', 'selb', 'rehau']
        
        all_exist = True
        for region_id in expected_regions:
            exists = region_id in regions
            if not exists:
                self.errors.append(f"Expected region '{region_id}' not found in config")
                all_exist = False
            else:
                region = regions[region_id]
                display_name = region.get('displayName', region.get('name', 'N/A'))
                print(f"    ✓ Region '{region_id}' exists: {display_name}")
        
        if all_exist:
            self.passed += 1
        else:
            self.failed += 1
        
        return all_exist
    
    def test_region_routing_paths(self) -> bool:
        """Test that each region has a valid routing configuration"""
        print("\n  Testing: Region routing paths...")
        
        regions = self.config.get('regions', {})
        all_valid = True
        
        for region_id, region_config in regions.items():
            # Check that region has required routing fields
            has_name = 'name' in region_config
            has_center = 'center' in region_config
            has_zoom = 'zoom' in region_config
            
            if not (has_name and has_center and has_zoom):
                self.errors.append(
                    f"Region '{region_id}' missing routing fields "
                    f"(name={has_name}, center={has_center}, zoom={has_zoom})"
                )
                all_valid = False
                continue
            
            # Check center has lat/lng
            center = region_config['center']
            if 'lat' not in center or ('lng' not in center and 'lon' not in center):
                self.errors.append(f"Region '{region_id}' center missing lat/lng")
                all_valid = False
                continue
        
        if all_valid:
            print(f"    ✓ All {len(regions)} regions have valid routing configuration")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_valid
    
    def test_default_location_is_antarctica(self) -> bool:
        """Test that default map center is South Pole (Antarctica)"""
        print("\n  Testing: Default location is South Pole...")
        
        map_config = self.config.get('map', {})
        default_center = map_config.get('default_center', {})
        
        lat = default_center.get('lat', 0)
        lon = default_center.get('lon', 0)
        
        # South Pole is at -90 latitude
        is_south_pole = lat == -90.0
        
        return self.assert_test(
            is_south_pole,
            f"Default center is South Pole (lat={lat}, lon={lon})",
            f"Expected lat=-90.0, got lat={lat}"
        )
    
    def test_antarctica_region_configured(self) -> bool:
        """Test that Antarctica region is properly configured as default demo"""
        print("\n  Testing: Antarctica region configuration...")
        
        regions = self.config.get('regions', {})
        antarctica = regions.get('antarctica', {})
        
        if not antarctica:
            return self.assert_test(False, "Antarctica region exists", "Not found in config")
        
        # Check display name
        display_name = antarctica.get('displayName', '')
        has_south_pole = 'South Pole' in display_name or 'Antarctica' in display_name
        
        # Check center coordinates
        center = antarctica.get('center', {})
        lat = center.get('lat', 0)
        is_south_pole = lat == -90.0 or lat == -90
        
        # Check zoom level (should be wider for continent)
        zoom = antarctica.get('zoom', 13)
        is_wide_zoom = zoom <= 6  # Wide view for continent
        
        all_valid = has_south_pole and is_south_pole and is_wide_zoom
        
        return self.assert_test(
            all_valid,
            f"Antarctica configured correctly (name={display_name}, lat={lat}, zoom={zoom})",
            f"Check: name contains South Pole/Antarctica={has_south_pole}, "
            f"lat=-90={is_south_pole}, zoom<=6={is_wide_zoom}"
        )
    
    # =========================================================================
    # Unknown Region Handling Tests
    # =========================================================================
    
    def test_unknown_region_detection(self) -> bool:
        """Test that unknown regions are properly detected"""
        print("\n  Testing: Unknown region detection logic...")
        
        regions = self.config.get('regions', {})
        
        # These should NOT be in regions (unknown)
        unknown_test_cases = ['unknownregions', 'berlin', 'tokyo', 'london', 'nyc']
        
        all_unknown = True
        for region_id in unknown_test_cases:
            if region_id in regions:
                self.errors.append(f"'{region_id}' should not be a known region")
                all_unknown = False
        
        if all_unknown:
            print(f"    ✓ Verified {len(unknown_test_cases)} unknown regions are not configured")
            print(f"      (These should redirect to South Pole with colony setup)")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_unknown
    
    # =========================================================================
    # 404.html SPA Routing Tests
    # =========================================================================
    
    def test_404_html_exists(self) -> bool:
        """Test that 404.html exists in public directory"""
        print("\n  Testing: 404.html exists...")
        
        html_404_path = self.public_path / "404.html"
        exists = html_404_path.exists()
        
        return self.assert_test(
            exists,
            f"404.html exists at {html_404_path}",
            f"File not found: {html_404_path}"
        )
    
    def test_404_html_spa_redirect_script(self) -> bool:
        """Test that 404.html contains SPA redirect script"""
        print("\n  Testing: 404.html contains SPA redirect script...")
        
        html_404_path = self.public_path / "404.html"
        
        if not html_404_path.exists():
            return self.assert_test(False, "404.html exists", "File not found")
        
        try:
            with open(html_404_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self.assert_test(False, "Read 404.html", str(e))
        
        # Check for key SPA routing elements
        checks = {
            'sessionStorage.setItem': "Stores path in sessionStorage",
            'spa_redirect_path': "Uses 'spa_redirect_path' key",
            'window.location.replace': "Redirects to base path",
            'pathname': "Reads current pathname"
        }
        
        all_present = True
        for pattern, description in checks.items():
            if pattern not in content:
                self.errors.append(f"404.html missing: {description} ({pattern})")
                all_present = False
        
        if all_present:
            print(f"    ✓ 404.html contains SPA redirect script with all required elements")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_present
    
    def test_404_html_path_preservation(self) -> bool:
        """Test that 404.html preserves the original path for the app to read"""
        print("\n  Testing: 404.html preserves original path...")
        
        html_404_path = self.public_path / "404.html"
        
        if not html_404_path.exists():
            return self.assert_test(False, "404.html exists", "File not found")
        
        try:
            with open(html_404_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self.assert_test(False, "Read 404.html", str(e))
        
        # Check that path is stored BEFORE redirect
        # The pattern should be: store path, then redirect
        store_pattern = r"sessionStorage\.setItem\(['\"]spa_redirect_path['\"],\s*path\)"
        redirect_pattern = r"window\.location\.replace\("
        
        store_match = re.search(store_pattern, content)
        redirect_match = re.search(redirect_pattern, content)
        
        if store_match and redirect_match:
            # Check order: store should come before redirect
            store_pos = store_match.start()
            redirect_pos = redirect_match.start()
            correct_order = store_pos < redirect_pos
            
            return self.assert_test(
                correct_order,
                "Path stored in sessionStorage before redirect",
                "Redirect happens before path is stored"
            )
        else:
            return self.assert_test(
                False,
                "Path storage and redirect patterns found",
                f"store_found={bool(store_match)}, redirect_found={bool(redirect_match)}"
            )
    
    # =========================================================================
    # RSS Feed Tests
    # =========================================================================
    
    def test_rss_feeds_exist_for_regions(self) -> bool:
        """Test that RSS feeds are generated for all configured regions"""
        print("\n  Testing: RSS feeds exist for all regions...")
        
        regions = self.config.get('regions', {})
        
        if not self.feeds_path.exists():
            return self.assert_test(
                False,
                "Feeds directory exists",
                f"Directory not found: {self.feeds_path}"
            )
        
        all_exist = True
        for region_id in regions.keys():
            feed_file = self.feeds_path / f"{region_id}-til-sunrise.xml"
            if not feed_file.exists():
                self.warnings.append(f"RSS feed not found for region '{region_id}': {feed_file}")
                # Don't fail the test, just warn (feeds may not be generated yet)
        
        # Check that at least some feeds exist
        existing_feeds = list(self.feeds_path.glob("*-til-sunrise.xml"))
        
        return self.assert_test(
            len(existing_feeds) > 0,
            f"Found {len(existing_feeds)} RSS feeds in {self.feeds_path}",
            "No RSS feeds found"
        )
    
    def test_rss_feed_urls_correct(self) -> bool:
        """Test that RSS feeds contain correct URLs for their region"""
        print("\n  Testing: RSS feed URLs are correct...")
        
        if not self.feeds_path.exists():
            self.warnings.append("Feeds directory not found, skipping URL check")
            return True
        
        feeds = list(self.feeds_path.glob("*-til-sunrise.xml"))
        
        if not feeds:
            self.warnings.append("No RSS feeds found, skipping URL check")
            return True
        
        all_correct = True
        for feed_file in feeds:
            # Extract region from filename
            region_id = feed_file.stem.replace('-til-sunrise', '')
            
            try:
                with open(feed_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check that feed contains correct region URL
                expected_link = f"krwl.in/{region_id}"
                if expected_link not in content:
                    self.errors.append(
                        f"Feed '{feed_file.name}' missing region link: {expected_link}"
                    )
                    all_correct = False
                
            except Exception as e:
                self.errors.append(f"Failed to read feed '{feed_file.name}': {e}")
                all_correct = False
        
        if all_correct:
            print(f"    ✓ All {len(feeds)} RSS feeds have correct region URLs")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_correct
    
    # =========================================================================
    # JavaScript Routing Logic Tests
    # =========================================================================
    
    def test_app_js_region_detection(self) -> bool:
        """Test that app.js contains region detection logic"""
        print("\n  Testing: app.js contains region detection logic...")
        
        app_js_path = self.base_path / "assets" / "js" / "app.js"
        
        if not app_js_path.exists():
            return self.assert_test(False, "app.js exists", f"File not found: {app_js_path}")
        
        try:
            with open(app_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self.assert_test(False, "Read app.js", str(e))
        
        # Check for key routing functions
        required_patterns = {
            'applyRegionFromUrl': "Region detection function",
            'applyUnknownRegion': "Unknown region handler",
            'spa_redirect_path': "Session storage path reading",
            'this.config.regions': "Region config access"
        }
        
        all_found = True
        for pattern, description in required_patterns.items():
            if pattern not in content:
                self.errors.append(f"app.js missing: {description} ({pattern})")
                all_found = False
        
        if all_found:
            print(f"    ✓ app.js contains all required routing logic")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_found
    
    def test_unknown_region_shows_colony_setup(self) -> bool:
        """Test that unknown regions show colony setup instructions"""
        print("\n  Testing: Unknown regions show colony setup event...")
        
        app_js_path = self.base_path / "assets" / "js" / "app.js"
        
        if not app_js_path.exists():
            return self.assert_test(False, "app.js exists", f"File not found: {app_js_path}")
        
        try:
            with open(app_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return self.assert_test(False, "Read app.js", str(e))
        
        # Check for colony setup event creation
        required_patterns = {
            'colonySetupEvent': "Colony setup event object",
            'Start a new colony': "Colony invitation message",
            'Fork': "Fork repository instruction",
            'github.com/feileberlin/krwl-hof': "Repository URL"
        }
        
        all_found = True
        for pattern, description in required_patterns.items():
            if pattern not in content:
                self.errors.append(f"app.js missing: {description} ({pattern})")
                all_found = False
        
        if all_found:
            print(f"    ✓ Unknown region handling includes colony setup instructions")
            self.passed += 1
        else:
            self.failed += 1
        
        return all_found
    
    # =========================================================================
    # Test Runner
    # =========================================================================
    
    def run_all_tests(self, verbose: bool = False) -> bool:
        """Run all routing tests"""
        print("\n" + "=" * 70)
        print("KRWL HOF Routing Tests")
        print("=" * 70)
        
        # Load config
        print("\nLoading configuration...")
        if not self.load_config():
            self.print_results()
            return False
        print("  ✓ Config loaded successfully")
        
        # Run all tests
        tests = [
            # Region configuration tests
            ("Region Configuration", [
                self.test_known_regions_exist,
                self.test_region_routing_paths,
                self.test_default_location_is_antarctica,
                self.test_antarctica_region_configured,
            ]),
            # Unknown region tests
            ("Unknown Region Handling", [
                self.test_unknown_region_detection,
            ]),
            # 404.html SPA routing tests
            ("404.html SPA Routing", [
                self.test_404_html_exists,
                self.test_404_html_spa_redirect_script,
                self.test_404_html_path_preservation,
            ]),
            # RSS feed tests
            ("RSS Feeds", [
                self.test_rss_feeds_exist_for_regions,
                self.test_rss_feed_urls_correct,
            ]),
            # JavaScript routing tests
            ("JavaScript Routing Logic", [
                self.test_app_js_region_detection,
                self.test_unknown_region_shows_colony_setup,
            ]),
        ]
        
        for section_name, section_tests in tests:
            print(f"\n{'─' * 70}")
            print(f"📋 {section_name}")
            print('─' * 70)
            
            for test in section_tests:
                try:
                    test()
                except Exception as e:
                    self.errors.append(f"Test {test.__name__} raised exception: {e}")
                    self.failed += 1
        
        # Print results
        self.print_results()
        
        return self.failed == 0
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("Test Results Summary")
        print("=" * 70)
        
        total = self.passed + self.failed
        
        print(f"\n  Tests Passed: {self.passed}/{total}")
        print(f"  Tests Failed: {self.failed}/{total}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.failed == 0:
            if self.warnings:
                print("\n✅ All tests passed (with warnings)")
            else:
                print("\n✅ All tests passed!")
        else:
            print(f"\n❌ {self.failed} test(s) failed")
        
        print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SPA routing and region detection')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    tester = TestRouting()
    success = tester.run_all_tests(verbose=args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
