#!/usr/bin/env python3
"""
Test Region Data Files

Tests that the shared events.json file exists and is properly structured.
All regions share the same event data - no data splitting by region.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRegionDataFiles:
    """Test suite for shared event data file (regions share same data)"""
    
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
        """Test that events directory exists (for archived events)"""
        print("  Testing: Events directory exists (for archived events)...")
        
        # Note: This directory is for archived events, not region-specific data
        # All regions share the main events.json file
        if not self.events_dir.exists():
            self.warnings.append(f"Events directory not found: {self.events_dir} (will be created when archiving)")
            return True
        
        if not self.events_dir.is_dir():
            self.errors.append(f"Events path is not a directory: {self.events_dir}")
            return False
        
        print(f"    ✓ Directory exists: {self.events_dir}")
        return True
    
    def test_region_data_files_exist(self):
        """Test that all regions point to valid data source (shared events.json)"""
        print("  Testing: Regions point to shared data source...")
        
        if not self.config or 'regions' not in self.config:
            self.warnings.append("No regions in config, skipping data source check")
            return True
        
        regions = self.config['regions']
        all_valid = True
        
        # Check that all regions point to the same shared data source
        data_sources = set()
        
        for region_id, region_config in regions.items():
            if 'dataSource' not in region_config:
                # dataSource is optional - regions can share default events.json
                continue
            
            data_source = region_config['dataSource']
            data_sources.add(data_source)
        
        if len(data_sources) > 1:
            self.warnings.append(
                f"Multiple data sources found: {data_sources}. "
                "Consider using single shared events.json for all regions."
            )
        
        # Check that main events.json exists
        main_events = self.base_path / "assets" / "json" / "events.json"
        if not main_events.exists():
            self.errors.append(f"Main events.json not found: {main_events}")
            all_valid = False
        else:
            print(f"    ✓ Shared data source: events.json")
        
        return all_valid
    
    def test_data_files_are_valid_json(self):
        """Test that shared events.json is valid JSON"""
        print("  Testing: Shared events.json is valid JSON...")
        
        main_events = self.base_path / "assets" / "json" / "events.json"
        
        if not main_events.exists():
            self.errors.append("Main events.json not found")
            return False
        
        try:
            with open(main_events, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structure - can be array or object with "events" key
            if isinstance(data, list):
                events = data
                print(f"    ✓ events.json: {len(events)} events (array format)")
            elif isinstance(data, dict) and 'events' in data:
                events = data['events']
                if not isinstance(events, list):
                    self.errors.append("events.json 'events' field must be an array")
                    return False
                print(f"    ✓ events.json: {len(events)} events (object format, shared by all regions)")
            else:
                self.errors.append("events.json must be array or object with 'events' key")
                return False
            
            return True
        
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in events.json: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading events.json: {e}")
            return False
    
    def test_event_schema_basic(self):
        """Test that events have basic required fields"""
        print("  Testing: Events have basic schema...")
        
        main_events = self.base_path / "assets" / "json" / "events.json"
        
        if not main_events.exists():
            return True  # Already caught in previous test
        
        all_valid = True
        required_fields = ['id', 'title', 'start_time', 'location']
        
        try:
            with open(main_events, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both array and object format
            if isinstance(data, list):
                events = data
            elif isinstance(data, dict) and 'events' in data:
                events = data['events']
            else:
                return True  # Already caught in previous test
            
            if not isinstance(events, list):
                return True  # Already caught in previous test
            
            # Check first few events for schema
            sample_size = min(5, len(events))
            for i, event in enumerate(events[:sample_size]):
                if not isinstance(event, dict):
                    self.errors.append(f"Event {i} is not a dictionary")
                    all_valid = False
                    continue
                
                missing = [f for f in required_fields if f not in event]
                if missing:
                    self.warnings.append(
                        f"Event {i} (id: {event.get('id', 'unknown')}) missing: {', '.join(missing)}"
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
            
            # Handle both formats
            if isinstance(data, list):
                print(f"    ✓ Main events.json exists ({len(data)} events, array format)")
            elif isinstance(data, dict) and 'events' in data:
                events = data['events']
                if isinstance(events, list):
                    print(f"    ✓ Main events.json exists ({len(events)} events, object format)")
                else:
                    self.warnings.append("Main events.json 'events' field should be an array")
            else:
                self.warnings.append("Main events.json has unexpected structure")
        
        except json.JSONDecodeError:
            self.warnings.append("Main events.json has invalid JSON")
        
        return True
    
    def run_all_tests(self, verbose=False):
        """Run all tests and report results"""
        print("\n" + "="*60)
        print("Shared Event Data Tests (All Regions Use Same Data)")
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
