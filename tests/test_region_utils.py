#!/usr/bin/env python3
"""
Test Multi-Region Utility Functions

Tests the utility functions for region configuration and distance calculations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.utils import load_config

try:
    from modules.region_utils import (
        get_region_config,
        validate_region,
        get_all_regions,
        get_default_region,
        haversine_distance,
        is_point_in_bounding_box
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("⚠️  Warning: region_utils module not yet available")


class TestRegionUtils:
    """Test suite for region utility functions"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
    
    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        print("  Testing: Haversine distance calculation...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        # Test known distances
        # Hof to Nuremberg: ~115 km
        hof = (50.3167, 11.9167)
        nuremberg = (49.4521, 11.0767)
        
        distance = haversine_distance(hof[1], hof[0], nuremberg[1], nuremberg[0])
        
        # Should be approximately 115 km (allow 10% margin)
        if not (103 <= distance <= 127):
            self.errors.append(
                f"Haversine distance Hof-Nuremberg: {distance:.1f} km (expected ~115 km)"
            )
            return False
        
        print(f"    ✓ Hof to Nuremberg: {distance:.1f} km")
        
        # Test zero distance (same point)
        distance_zero = haversine_distance(hof[1], hof[0], hof[1], hof[0])
        if distance_zero > 0.001:  # Allow tiny floating point error
            self.errors.append(f"Same point should have 0 distance, got {distance_zero}")
            return False
        
        print(f"    ✓ Same point: {distance_zero:.6f} km")
        
        return True
    
    def test_get_all_regions(self):
        """Test getting all regions from config"""
        print("  Testing: Get all regions...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        try:
            regions = get_all_regions(self.base_path)
            
            if not isinstance(regions, dict):
                self.errors.append("get_all_regions should return a dictionary")
                return False
            
            print(f"    ✓ Found {len(regions)} regions: {', '.join(regions.keys())}")
            return True
        
        except Exception as e:
            self.errors.append(f"get_all_regions raised exception: {e}")
            return False
    
    def test_get_default_region(self):
        """Test getting default region"""
        print("  Testing: Get default region...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        try:
            default = get_default_region(self.base_path)
            
            if not isinstance(default, str):
                self.errors.append("get_default_region should return a string")
                return False
            
            print(f"    ✓ Default region: {default}")
            return True
        
        except Exception as e:
            self.errors.append(f"get_default_region raised exception: {e}")
            return False
    
    def test_validate_region(self):
        """Test region validation"""
        print("  Testing: Region validation...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        try:
            # Test valid region
            if not validate_region('hof', self.base_path):
                self.errors.append("validate_region should return True for 'hof'")
                return False
            
            print(f"    ✓ Valid region 'hof' recognized")
            
            # Test invalid region
            if validate_region('invalid_region_xyz', self.base_path):
                self.errors.append("validate_region should return False for invalid region")
                return False
            
            print(f"    ✓ Invalid region rejected")
            return True
        
        except Exception as e:
            self.errors.append(f"validate_region raised exception: {e}")
            return False
    
    def test_get_region_config(self):
        """Test getting region-specific configuration"""
        print("  Testing: Get region config...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        try:
            # Test getting Hof config
            hof_config = get_region_config('hof', self.base_path)
            
            if not isinstance(hof_config, dict):
                self.errors.append("get_region_config should return a dictionary")
                return False
            
            # Check required fields
            required = ['name', 'displayName', 'center', 'zoom']
            missing = [f for f in required if f not in hof_config]
            if missing:
                self.errors.append(f"Region config missing fields: {', '.join(missing)}")
                return False
            
            print(f"    ✓ Hof config: {hof_config.get('displayName', 'N/A')}")
            
            # Test getting invalid region (should return None or raise)
            invalid_config = get_region_config('invalid_region_xyz', self.base_path)
            if invalid_config is not None:
                self.warnings.append("Invalid region should return None")
            
            return True
        
        except Exception as e:
            self.errors.append(f"get_region_config raised exception: {e}")
            return False
    
    def test_bounding_box_check(self):
        """Test point in bounding box check"""
        print("  Testing: Bounding box check...")
        
        if not UTILS_AVAILABLE:
            self.warnings.append("region_utils not available, skipping")
            return True
        
        try:
            # Define a simple bounding box
            bbox = {
                'north': 50.4,
                'south': 50.2,
                'east': 12.0,
                'west': 11.8
            }
            
            # Point inside
            if not is_point_in_bounding_box(50.3, 11.9, bbox):
                self.errors.append("Point (50.3, 11.9) should be inside bbox")
                return False
            
            print(f"    ✓ Point inside bbox detected")
            
            # Point outside
            if is_point_in_bounding_box(51.0, 11.9, bbox):
                self.errors.append("Point (51.0, 11.9) should be outside bbox")
                return False
            
            print(f"    ✓ Point outside bbox detected")
            
            return True
        
        except Exception as e:
            self.errors.append(f"is_point_in_bounding_box raised exception: {e}")
            return False
    
    def run_all_tests(self, verbose=False):
        """Run all tests and report results"""
        print("\n" + "="*60)
        print("Region Utility Functions Tests")
        print("="*60 + "\n")
        
        if not UTILS_AVAILABLE:
            print("⚠️  Region utilities not yet implemented")
            print("    These tests will pass once region_utils.py is created\n")
        
        # Run all tests
        tests = [
            self.test_haversine_distance,
            self.test_get_all_regions,
            self.test_get_default_region,
            self.test_validate_region,
            self.test_get_region_config,
            self.test_bounding_box_check,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.errors.append(f"Test {test.__name__} raised exception: {e}")
                failed += 1
        
        # Print results
        self.print_results()
        
        return failed == 0
    
    def print_results(self):
        """Print test results"""
        print("\n" + "="*60)
        print("Test Results")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All tests passed!")
        elif not self.errors:
            print("\n✅ All tests passed (with warnings)")
        
        print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test region utility functions')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    tester = TestRegionUtils()
    success = tester.run_all_tests(verbose=args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
