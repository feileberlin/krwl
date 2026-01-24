#!/usr/bin/env python3
"""
Test Region Data Files

Tests that region-specific event data files exist and are properly structured.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRegionDataFiles:
    """Test suite for region-specific data files"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.events_dir = self.base_path / "assets" / "json" / "events"
        self.config_path = self.base_path / "config.json"
        self.errors = []
        self.warnings = []
        self.config = None
    
    def load_config(self):
        """Load config to get region list"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load config: {e}")
            return False
    
    def test_events_directory_exists(self):
        """Test that events directory exists"""
        print("  Testing: Events directory exists...")
        
        if not self.events_dir.exists():
            self.errors.append(f"Events directory not found: {self.events_dir}")
            return False
        
        if not self.events_dir.is_dir():
            self.errors.append(f"Events path is not a directory: {self.events_dir}")
            return False
        
        print(f"    ✓ Directory exists: {self.events_dir}")
        return True
    
    def test_region_data_files_exist(self):
        """Test that data file exists for each region"""
        print("  Testing: Region data files exist...")
        
        if not self.config or 'regions' not in self.config:
            self.warnings.append("No regions in config, skipping data file check")
            return True
        
        regions = self.config['regions']
        all_exist = True
        
        for region_id, region_config in regions.items():
            if 'dataSource' not in region_config:
                self.warnings.append(f"Region '{region_id}' has no dataSource defined")
                continue
            
            data_source = region_config['dataSource']
            data_file = self.events_dir / data_source
            
            if not data_file.exists():
                self.errors.append(f"Data file not found for region '{region_id}': {data_file}")
                all_exist = False
            else:
                print(f"    ✓ {region_id}: {data_source}")
        
        return all_exist
    
    def test_data_files_are_valid_json(self):
        """Test that all region data files are valid JSON"""
        print("  Testing: Data files are valid JSON...")
        
        if not self.config or 'regions' not in self.config:
            return True
        
        regions = self.config['regions']
        all_valid = True
        
        for region_id, region_config in regions.items():
            if 'dataSource' not in region_config:
                continue
            
            data_source = region_config['dataSource']
            data_file = self.events_dir / data_source
            
            if not data_file.exists():
                continue
            
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check it's an array
                if not isinstance(data, list):
                    self.errors.append(f"Data file for '{region_id}' must be a JSON array")
                    all_valid = False
                else:
                    print(f"    ✓ {region_id}: {len(data)} events")
            
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in data file for '{region_id}': {e}")
                all_valid = False
            except Exception as e:
                self.errors.append(f"Error reading data file for '{region_id}': {e}")
                all_valid = False
        
        return all_valid
    
    def test_event_schema_basic(self):
        """Test that events have basic required fields"""
        print("  Testing: Events have basic schema...")
        
        if not self.config or 'regions' not in self.config:
            return True
        
        regions = self.config['regions']
        all_valid = True
        required_fields = ['id', 'title', 'start', 'location']
        
        for region_id, region_config in regions.items():
            if 'dataSource' not in region_config:
                continue
            
            data_source = region_config['dataSource']
            data_file = self.events_dir / data_source
            
            if not data_file.exists():
                continue
            
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                
                if not isinstance(events, list):
                    continue
                
                # Check first few events for schema
                sample_size = min(5, len(events))
                for i, event in enumerate(events[:sample_size]):
                    if not isinstance(event, dict):
                        self.errors.append(
                            f"Region '{region_id}' event {i} is not a dictionary"
                        )
                        all_valid = False
                        continue
                    
                    missing = [f for f in required_fields if f not in event]
                    if missing:
                        self.warnings.append(
                            f"Region '{region_id}' event {i} missing: {', '.join(missing)}"
                        )
            
            except Exception:
                # Already caught in previous test
                pass
        
        if all_valid:
            print(f"    ✓ Event schemas look good")
        
        return all_valid
    
    def test_backward_compatibility_main_events_file(self):
        """Test that main events.json still exists for backward compatibility"""
        print("  Testing: Backward compatibility - main events.json...")
        
        main_events = self.base_path / "assets" / "json" / "events.json"
        
        if not main_events.exists():
            self.warnings.append(
                "Main events.json not found - may break backward compatibility"
            )
            return True
        
        try:
            with open(main_events, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.warnings.append("Main events.json should be a JSON array")
            else:
                print(f"    ✓ Main events.json exists ({len(data)} events)")
        
        except json.JSONDecodeError:
            self.warnings.append("Main events.json has invalid JSON")
        
        return True
    
    def run_all_tests(self, verbose=False):
        """Run all tests and report results"""
        print("\n" + "="*60)
        print("Region Data Files Tests")
        print("="*60)
        
        # Load config
        print("\nLoading config.json...")
        if not self.load_config():
            self.print_results()
            return False
        
        print(f"  ✓ Config loaded successfully\n")
        
        # Run all tests
        tests = [
            self.test_events_directory_exists,
            self.test_backward_compatibility_main_events_file,
            self.test_region_data_files_exist,
            self.test_data_files_are_valid_json,
            self.test_event_schema_basic,
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
    
    parser = argparse.ArgumentParser(description='Test region data files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    tester = TestRegionDataFiles()
    success = tester.run_all_tests(verbose=args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
