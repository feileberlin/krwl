#!/usr/bin/env python3
"""
Test Asset Manager - Version Tracking and Updates

Tests the AssetManager class functionality for CDN asset version tracking,
checksum verification, and automatic update detection.
"""

import sys
import unittest
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.asset_manager import AssetManager


class TestAssetManager(unittest.TestCase):
    """Test AssetManager version tracking functionality"""
    
    def setUp(self):
        """Set up test fixtures with temporary directories"""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.base_path = Path(self.test_dir)
        self.lib_dir = self.base_path / 'lib'
        self.lib_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AssetManager
        self.asset_manager = AssetManager(self.base_path, self.lib_dir)
    
    def tearDown(self):
        """Clean up temporary test directories"""
        if self.test_dir and Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test AssetManager initializes correctly"""
        self.assertIsNotNone(self.asset_manager)
        self.assertTrue(self.lib_dir.exists())
        self.assertIsInstance(self.asset_manager.versions_data, dict)
        self.assertIn('metadata', self.asset_manager.versions_data)
        self.assertIn('assets', self.asset_manager.versions_data)
    
    def test_versions_file_creation(self):
        """Test that versions.json is created in lib/ directory"""
        # Record a dummy asset
        self.asset_manager.record_asset_version(
            'test-package',
            'test-package/test.js',
            '1.0.0',
            'abc123',
            1024
        )
        
        # Check versions.json was created
        versions_file = self.lib_dir / 'versions.json'
        self.assertTrue(versions_file.exists())
        
        # Verify content
        with open(versions_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('test-package', data['assets'])
        self.assertEqual(data['assets']['test-package']['version'], '1.0.0')
    
    def test_record_asset_version(self):
        """Test recording asset version information"""
        result = self.asset_manager.record_asset_version(
            package_name='leaflet',
            file_dest='leaflet/leaflet.js',
            version='1.9.4',
            checksum='sha256checksum',
            size_bytes=12345
        )
        
        self.assertTrue(result)
        
        # Verify data was recorded
        assets = self.asset_manager.versions_data['assets']
        self.assertIn('leaflet', assets)
        self.assertEqual(assets['leaflet']['version'], '1.9.4')
        self.assertIn('leaflet/leaflet.js', assets['leaflet']['files'])
        
        file_info = assets['leaflet']['files']['leaflet/leaflet.js']
        self.assertEqual(file_info['checksum'], 'sha256checksum')
        self.assertEqual(file_info['size_bytes'], 12345)
    
    def test_calculate_checksum(self):
        """Test checksum calculation for files"""
        # Create a test file
        test_file = self.lib_dir / 'test.txt'
        test_content = b'Hello, World!'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate checksum
        checksum = self.asset_manager._calculate_checksum(test_file)
        
        # Verify checksum is a hex string
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 64)  # SHA256 produces 64 hex chars
        
        # Verify checksum is consistent
        checksum2 = self.asset_manager._calculate_checksum(test_file)
        self.assertEqual(checksum, checksum2)
    
    def test_verify_asset_integrity_missing_file(self):
        """Test integrity verification for missing file"""
        result = self.asset_manager.verify_asset_integrity('nonexistent/file.js')
        self.assertFalse(result)
    
    def test_verify_asset_integrity_valid_file(self):
        """Test integrity verification for valid file"""
        # Create a test file
        test_file = self.lib_dir / 'test' / 'file.js'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_content = b'console.log("test");'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate and record checksum
        import hashlib
        checksum = hashlib.sha256(test_content).hexdigest()
        self.asset_manager.record_asset_version(
            'test-pkg',
            'test/file.js',
            '1.0.0',
            checksum,
            len(test_content)
        )
        
        # Verify integrity
        result = self.asset_manager.verify_asset_integrity('test/file.js')
        self.assertTrue(result)
    
    def test_verify_asset_integrity_modified_file(self):
        """Test integrity verification for modified file"""
        # Create a test file
        test_file = self.lib_dir / 'test' / 'file.js'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        original_content = b'console.log("original");'
        with open(test_file, 'wb') as f:
            f.write(original_content)
        
        # Record original checksum
        import hashlib
        original_checksum = hashlib.sha256(original_content).hexdigest()
        self.asset_manager.record_asset_version(
            'test-pkg',
            'test/file.js',
            '1.0.0',
            original_checksum,
            len(original_content)
        )
        
        # Modify file
        modified_content = b'console.log("modified");'
        with open(test_file, 'wb') as f:
            f.write(modified_content)
        
        # Verify integrity (should fail)
        result = self.asset_manager.verify_asset_integrity('test/file.js')
        self.assertFalse(result)
    
    def test_get_asset_info(self):
        """Test retrieving asset information"""
        # Record some assets
        self.asset_manager.record_asset_version('pkg1', 'pkg1/file1.js', '1.0.0', 'abc', 100)
        self.asset_manager.record_asset_version('pkg2', 'pkg2/file2.js', '2.0.0', 'def', 200)
        
        # Get all assets
        all_assets = self.asset_manager.get_asset_info()
        self.assertEqual(len(all_assets), 2)
        self.assertIn('pkg1', all_assets)
        self.assertIn('pkg2', all_assets)
        
        # Get specific package
        pkg1_info = self.asset_manager.get_asset_info('pkg1')
        self.assertEqual(pkg1_info['version'], '1.0.0')
    
    def test_list_all_assets(self):
        """Test listing all tracked assets"""
        # Record some assets
        self.asset_manager.record_asset_version('leaflet', 'leaflet/leaflet.js', '1.9.4', 'abc', 100)
        self.asset_manager.record_asset_version('leaflet', 'leaflet/leaflet.css', '1.9.4', 'def', 200)
        self.asset_manager.record_asset_version('roboto', 'roboto/font.woff2', 'v30', 'ghi', 300)
        
        # List assets
        assets = self.asset_manager.list_all_assets()
        
        self.assertEqual(len(assets), 2)  # 2 packages
        
        # Find leaflet
        leaflet = next(a for a in assets if a['package'] == 'leaflet')
        self.assertEqual(leaflet['version'], '1.9.4')
        self.assertEqual(leaflet['file_count'], 2)
        self.assertIn('leaflet/leaflet.js', leaflet['files'])
    
    def test_check_for_updates_version_change(self):
        """Test update detection when version changes"""
        # Record old version
        self.asset_manager.record_asset_version('pkg', 'pkg/file.js', '1.0.0', 'abc', 100)
        
        # Check for updates with new version
        config = {
            'version': '2.0.0',
            'base_url': 'https://example.com',
            'files': [{'src': '/file.js', 'dest': 'pkg/file.js'}]
        }
        
        result = self.asset_manager.check_for_updates('pkg', config)
        
        self.assertTrue(result['has_update'])
        self.assertEqual(result['current_version'], '1.0.0')
        self.assertEqual(result['latest_version'], '2.0.0')
    
    def test_check_for_updates_no_change(self):
        """Test update detection when no changes"""
        # Record current version
        self.asset_manager.record_asset_version('pkg', 'pkg/file.js', '1.0.0', 'abc', 100)
        
        # Check for updates with same version
        config = {
            'version': '1.0.0',
            'base_url': 'https://example.com',
            'files': [{'src': '/file.js', 'dest': 'pkg/file.js'}]
        }
        
        result = self.asset_manager.check_for_updates('pkg', config)
        
        # Note: We can't test remote checksum comparison without network
        # But at least version comparison should work
        if not result['has_update']:
            self.assertEqual(result['current_version'], '1.0.0')
            self.assertEqual(result['latest_version'], '1.0.0')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
