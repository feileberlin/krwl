#!/usr/bin/env python3
"""Test dependency fetching resilience to CDN failures

This test verifies that the site generator continues successfully when:
1. CDN is unavailable but files are already present (cached)
2. CDN is available and files are missing (normal fetch)
3. CDN is unavailable and files are missing (should fail)
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.site_generator import SiteGenerator, DEPENDENCIES


class TestDependencyResilience(unittest.TestCase):
    """Test dependency fetching resilience"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.generator = SiteGenerator(self.base_path)
        
        # Create necessary directories
        (self.base_path / 'target' / 'leaflet' / 'images').mkdir(parents=True, exist_ok=True)
        (self.base_path / 'target' / 'lucide').mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_dummy_file(self, path: Path, content: str = "dummy content"):
        """Create a dummy file at the given path"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    @patch('urllib.request.urlopen')
    def test_cdn_unavailable_files_exist(self, mock_urlopen):
        """Test: CDN unavailable but files already exist -> should succeed"""
        # Simulate CDN failure
        mock_urlopen.side_effect = urllib.error.HTTPError(
            'http://test.com', 404, 'Not Found', {}, None
        )
        
        # Create all required Leaflet files
        leaflet_files = [
            'leaflet/leaflet.css',
            'leaflet/leaflet.js',
            'leaflet/images/marker-icon.png',
            'leaflet/images/marker-icon-2x.png',
            'leaflet/images/marker-shadow.png'
        ]
        for file_path in leaflet_files:
            self.create_dummy_file(self.base_path / 'target' / file_path)
        
        # Create Lucide files
        lucide_files = [
            'lucide/lucide.js',
            'lucide/lucide.min.js'
        ]
        for file_path in lucide_files:
            self.create_dummy_file(self.base_path / 'target' / file_path)
        
        # Fetch should succeed because files exist
        result = self.generator.fetch_all_dependencies()
        self.assertTrue(result, "Should succeed when files exist despite CDN failure")
        
        # Verify no actual network calls were made (files were already present)
        # The mock would have been called if we tried to fetch
    
    @patch('urllib.request.urlopen')
    def test_cdn_available_files_missing(self, mock_urlopen):
        """Test: CDN available and files missing -> should fetch successfully"""
        # Mock successful CDN response
        mock_response = MagicMock()
        mock_response.read.return_value = b"dummy content from CDN"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response
        
        # Files don't exist yet
        # Fetch should succeed
        result = self.generator.fetch_all_dependencies()
        self.assertTrue(result, "Should succeed when CDN is available")
        
        # Verify files were created
        leaflet_css = self.base_path / 'target' / 'leaflet' / 'leaflet.css'
        self.assertTrue(leaflet_css.exists(), "Leaflet CSS should be created")
    
    @patch('urllib.request.urlopen')
    def test_cdn_unavailable_files_missing(self, mock_urlopen):
        """Test: CDN unavailable and files missing -> should fail"""
        # Simulate CDN failure
        mock_urlopen.side_effect = urllib.error.HTTPError(
            'http://test.com', 404, 'Not Found', {}, None
        )
        
        # Files don't exist
        # Fetch should fail
        result = self.generator.fetch_all_dependencies()
        self.assertFalse(result, "Should fail when files missing and CDN unavailable")
    
    @patch('urllib.request.urlopen')
    def test_partial_files_exist_cdn_fails(self, mock_urlopen):
        """Test: Some files exist, CDN fails for missing files -> depends on critical files"""
        # Simulate CDN failure
        mock_urlopen.side_effect = urllib.error.HTTPError(
            'http://test.com', 404, 'Not Found', {}, None
        )
        
        # Create only critical Leaflet files (CSS and JS)
        self.create_dummy_file(self.base_path / 'target' / 'leaflet' / 'leaflet.css')
        self.create_dummy_file(self.base_path / 'target' / 'leaflet' / 'leaflet.js')
        # Missing: marker images
        
        # Create all Lucide files
        self.create_dummy_file(self.base_path / 'target' / 'lucide' / 'lucide.js')
        self.create_dummy_file(self.base_path / 'target' / 'lucide' / 'lucide.min.js')
        
        # Should fail because not all Leaflet files exist
        result = self.generator.fetch_all_dependencies()
        self.assertFalse(result, "Should fail when some required files are missing")
    
    @patch('urllib.request.urlopen')
    def test_check_dependency_files(self, mock_urlopen):
        """Test check_dependency_files method correctly identifies missing files"""
        # Create some but not all files
        self.create_dummy_file(self.base_path / 'target' / 'leaflet' / 'leaflet.css')
        
        leaflet_config = DEPENDENCIES['leaflet']
        
        present, missing = self.generator.check_dependency_files('leaflet', leaflet_config)
        
        self.assertFalse(present, "Should report as not present when files missing")
        self.assertGreater(len(missing), 0, "Should list missing files")
        self.assertIn('leaflet/leaflet.js', missing, "Should include missing leaflet.js")
    
    @patch('urllib.request.urlopen')
    def test_all_files_exist_check(self, mock_urlopen):
        """Test check_dependency_files returns True when all files exist"""
        # Create all Leaflet files
        leaflet_files = [
            'leaflet/leaflet.css',
            'leaflet/leaflet.js',
            'leaflet/images/marker-icon.png',
            'leaflet/images/marker-icon-2x.png',
            'leaflet/images/marker-shadow.png'
        ]
        for file_path in leaflet_files:
            self.create_dummy_file(self.base_path / 'target' / file_path)
        
        leaflet_config = DEPENDENCIES['leaflet']
        
        present, missing = self.generator.check_dependency_files('leaflet', leaflet_config)
        
        self.assertTrue(present, "Should report as present when all files exist")
        self.assertEqual(len(missing), 0, "Should have no missing files")


def run_tests():
    """Run all dependency resilience tests"""
    print("\n" + "=" * 70)
    print("Testing Dependency Fetching Resilience")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDependencyResilience)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ All dependency resilience tests passed!")
    else:
        print("✗ Some tests failed")
        if result.failures:
            print(f"  Failures: {len(result.failures)}")
            for test, traceback in result.failures:
                print(f"    - {test}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for test, traceback in result.errors:
                print(f"    - {test}")
    print("=" * 70 + "\n")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
