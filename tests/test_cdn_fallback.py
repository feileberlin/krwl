#!/usr/bin/env python3
"""Test CDN fallback functionality in cdn_inliner.py

This test verifies that the CDN inliner properly falls back to local files
when CDN resources are unavailable (e.g., no internet connection).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from modules.cdn_inliner import CDNInliner
from modules.utils import load_config


class TestCDNFallback(unittest.TestCase):
    """Test CDN fallback functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = Path(__file__).parent
        self.config = load_config(self.base_path)
        self.inliner = CDNInliner(self.config, self.base_path)
    
    def test_local_files_exist(self):
        """Test that local fallback files exist"""
        leaflet_css = self.base_path / 'static' / 'lib' / 'leaflet' / 'leaflet.css'
        leaflet_js = self.base_path / 'static' / 'lib' / 'leaflet' / 'leaflet.js'
        
        self.assertTrue(leaflet_css.exists(), 
                       f"Local Leaflet CSS not found at {leaflet_css}")
        self.assertTrue(leaflet_js.exists(), 
                       f"Local Leaflet JS not found at {leaflet_js}")
        
        # Check files are not empty
        self.assertGreater(leaflet_css.stat().st_size, 0,
                          "Local Leaflet CSS is empty")
        self.assertGreater(leaflet_js.stat().st_size, 0,
                          "Local Leaflet JS is empty")
    
    @patch('urllib.request.urlopen')
    def test_cdn_fallback_on_network_error(self, mock_urlopen):
        """Test fallback to local files when CDN is unreachable"""
        # Simulate network error
        mock_urlopen.side_effect = urllib.error.URLError("No address associated with hostname")
        
        # Get Leaflet CSS (should fallback to local)
        css_content = self.inliner.get_leaflet_css()
        self.assertIsNotNone(css_content)
        self.assertGreater(len(css_content), 0)
        self.assertIn('leaflet', css_content.lower())
        
        # Get Leaflet JS (should fallback to local)
        js_content = self.inliner.get_leaflet_js()
        self.assertIsNotNone(js_content)
        self.assertGreater(len(js_content), 0)
        self.assertIn('leaflet', js_content.lower())
    
    @patch('urllib.request.urlopen')
    def test_cdn_fallback_on_timeout(self, mock_urlopen):
        """Test fallback to local files when CDN times out"""
        # Simulate timeout
        mock_urlopen.side_effect = urllib.error.URLError("timed out")
        
        # Should still work with local files
        css_content = self.inliner.get_leaflet_css()
        self.assertIsNotNone(css_content)
        
        js_content = self.inliner.get_leaflet_js()
        self.assertIsNotNone(js_content)
    
    @patch('urllib.request.urlopen')
    def test_cdn_success(self, mock_urlopen):
        """Test successful CDN fetch"""
        # Mock successful CDN response
        mock_response = MagicMock()
        mock_response.read.return_value = b"/* CDN Leaflet CSS */"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        # Should use CDN content
        css_content = self.inliner.get_leaflet_css()
        self.assertIn("CDN Leaflet CSS", css_content)
    
    def test_read_local_app_files(self):
        """Test reading local app CSS and JS files"""
        app_css_path = self.base_path / 'static' / 'css' / 'style.css'
        app_js_path = self.base_path / 'static' / 'js' / 'app.js'
        
        # Check files exist
        self.assertTrue(app_css_path.exists(), 
                       f"App CSS not found at {app_css_path}")
        self.assertTrue(app_js_path.exists(), 
                       f"App JS not found at {app_js_path}")
        
        # Read files
        app_css = self.inliner.read_local_file(app_css_path)
        app_js = self.inliner.read_local_file(app_js_path)
        
        self.assertIsNotNone(app_css)
        self.assertIsNotNone(app_js)
        self.assertGreater(len(app_css), 0)
        self.assertGreater(len(app_js), 0)
    
    @patch('urllib.request.urlopen')
    def test_full_generation_with_fallback(self, mock_urlopen):
        """Test full HTML generation with CDN fallback"""
        # Simulate network error for full integration test
        mock_urlopen.side_effect = urllib.error.URLError("No connection")
        
        # Should still generate HTML using local files
        html = self.inliner.generate_inline_html()
        
        self.assertIsNotNone(html)
        self.assertGreater(len(html), 0)
        
        # Check HTML contains expected elements
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html', html)
        self.assertIn('leaflet', html.lower())
        self.assertIn('const EVENTS =', html)
        self.assertIn('class EventsApp', html)


def run_tests():
    """Run all CDN fallback tests"""
    print("\n" + "=" * 70)
    print("Testing CDN Fallback Functionality")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCDNFallback)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ All CDN fallback tests passed!")
    else:
        print("✗ Some tests failed")
        if result.failures:
            print(f"  Failures: {len(result.failures)}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
    print("=" * 70 + "\n")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
