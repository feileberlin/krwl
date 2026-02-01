#!/usr/bin/env python3
"""
Integration test for CDN asset version tracking and updates

Tests the complete workflow:
1. Fetch dependencies
2. Check versions
3. Detect updates
4. Update dependencies
"""

import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.site_generator import SiteGenerator


class TestAssetVersioningIntegration(unittest.TestCase):
    """Integration tests for asset version tracking"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = Path(__file__).parent.parent
        self.generator = SiteGenerator(self.base_path)
    
    def test_workflow_fetch_check_info(self):
        """Test complete workflow: fetch → check → info"""
        # Step 1: Fetch dependencies (should use cached files)
        print("\n=== Step 1: Fetch Dependencies ===")
        result = self.generator.fetch_all_dependencies()
        self.assertTrue(result, "Fetch should succeed")
        
        # Step 2: Check dependencies
        print("\n=== Step 2: Check Dependencies ===")
        result = self.generator.check_all_dependencies(quiet=True)
        self.assertTrue(result, "All dependencies should be present")
        
        # Step 3: Show asset info
        print("\n=== Step 3: Show Asset Info ===")
        if self.generator.asset_manager:
            assets = self.generator.asset_manager.list_all_assets()
            self.assertGreater(len(assets), 0, "Should have tracked assets")
            
            # Verify each asset has version info
            for asset in assets:
                self.assertIn('package', asset)
                self.assertIn('version', asset)
                self.assertIn('file_count', asset)
                self.assertGreater(asset['file_count'], 0, 
                                 f"Package {asset['package']} should have files")
    
    def test_update_check_when_up_to_date(self):
        """Test update check when dependencies are up to date"""
        if not self.generator.asset_manager:
            self.skipTest("AssetManager not available")
        
        print("\n=== Test: Update Check (Up to Date) ===")
        
        # Fetch to ensure we have current versions
        self.generator.fetch_all_dependencies()
        
        # Check for updates
        updates = self.generator.check_for_updates(quiet=True)
        
        # Should return dict with package info
        self.assertIsInstance(updates, dict)
        
        # All packages should be up to date (or not tracked yet)
        for package_name, update_info in updates.items():
            self.assertIn('has_update', update_info)
            self.assertIn('current_version', update_info)
            self.assertIn('latest_version', update_info)
    
    def test_verify_local_first_serving(self):
        """Test that local files are always preferred over CDN"""
        print("\n=== Test: Local-First Serving ===")
        
        # Fetch dependencies
        result = self.generator.fetch_all_dependencies()
        self.assertTrue(result)
        
        # Check that lib directory exists and has files
        lib_dir = self.base_path / 'lib'
        self.assertTrue(lib_dir.exists(), "lib/ directory should exist")
        
        # Check that versions.json exists
        versions_file = lib_dir / 'versions.json'
        self.assertTrue(versions_file.exists(), "versions.json should exist")
        
        # Verify local files exist for key dependencies
        leaflet_js = lib_dir / 'leaflet' / 'leaflet.js'
        if leaflet_js.exists():
            # If leaflet.js exists, verify it has a size > 0
            self.assertGreater(leaflet_js.stat().st_size, 0,
                             "Leaflet.js should have content")
    
    def test_asset_integrity_verification(self):
        """Test that asset integrity can be verified"""
        if not self.generator.asset_manager:
            self.skipTest("AssetManager not available")
        
        print("\n=== Test: Asset Integrity Verification ===")
        
        # Fetch dependencies
        self.generator.fetch_all_dependencies()
        
        # Get tracked assets
        assets = self.generator.asset_manager.list_all_assets()
        
        # Verify integrity of each tracked file
        for asset in assets:
            for file_path in asset['files']:
                # Check if file exists
                full_path = self.base_path / 'lib' / file_path
                if full_path.exists():
                    # Verify integrity
                    is_valid = self.generator.asset_manager.verify_asset_integrity(file_path)
                    self.assertTrue(is_valid, 
                                  f"Integrity check should pass for {file_path}")


if __name__ == '__main__':
    print("=" * 70)
    print("CDN Asset Version Tracking - Integration Tests")
    print("=" * 70)
    
    # Run tests with verbose output
    unittest.main(verbosity=2)
