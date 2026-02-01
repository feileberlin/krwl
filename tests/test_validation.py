#!/usr/bin/env python3
"""
Test Pydantic validation models

Tests the data validation models for events, locations, and configuration.
"""

import sys
from pathlib import Path
from pydantic import ValidationError

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.models import (
    Event, Location, ScrapingSource, MapConfig,
    validate_event_data, validate_events_list
)


class ValidationTester:
    """Tests validation model functionality"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
    
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
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
    
    def test_location_validation(self):
        """Test Location model validation"""
        print("\n=== Testing Location Validation ===")
        
        # Valid location
        try:
            Location(name="Test Location", lat=50.0, lon=11.0)
            self.assert_test(True, "Valid location accepted")
        except Exception as e:
            self.assert_test(False, "Valid location accepted", str(e))
        
        # Invalid latitude (too high)
        try:
            Location(name="Test", lat=91.0, lon=11.0)
            self.assert_test(False, "Invalid latitude rejected (>90)")
        except ValidationError:
            self.assert_test(True, "Invalid latitude rejected (>90)")
        
        # Invalid latitude (too low)
        try:
            Location(name="Test", lat=-91.0, lon=11.0)
            self.assert_test(False, "Invalid latitude rejected (<-90)")
        except ValidationError:
            self.assert_test(True, "Invalid latitude rejected (<-90)")
        
        # Invalid longitude (too high)
        try:
            Location(name="Test", lat=50.0, lon=181.0)
            self.assert_test(False, "Invalid longitude rejected (>180)")
        except ValidationError:
            self.assert_test(True, "Invalid longitude rejected (>180)")
        
        # Invalid longitude (too low)
        try:
            Location(name="Test", lat=50.0, lon=-181.0)
            self.assert_test(False, "Invalid longitude rejected (<-180)")
        except ValidationError:
            self.assert_test(True, "Invalid longitude rejected (<-180)")
        
        # Empty name
        try:
            Location(name="", lat=50.0, lon=11.0)
            self.assert_test(False, "Empty location name rejected")
        except ValidationError:
            self.assert_test(True, "Empty location name rejected")
    
    def test_event_validation(self):
        """Test Event model validation"""
        print("\n=== Testing Event Validation ===")
        
        # Valid event
        try:
            Event(
                id="test_1",
                title="Test Event",
                location=Location(name="Test Loc", lat=50.0, lon=11.0),
                start_time="2024-01-15T18:00:00",
                status="pending"
            )
            self.assert_test(True, "Valid event accepted")
        except Exception as e:
            self.assert_test(False, "Valid event accepted", str(e))
        
        # Invalid ISO datetime
        try:
            Event(
                id="test_2",
                title="Test Event",
                location=Location(name="Test Loc", lat=50.0, lon=11.0),
                start_time="not-a-date",
                status="pending"
            )
            self.assert_test(False, "Invalid datetime rejected")
        except ValueError:
            self.assert_test(True, "Invalid datetime rejected")
        
        # Invalid status
        try:
            Event(
                id="test_3",
                title="Test Event",
                location=Location(name="Test Loc", lat=50.0, lon=11.0),
                start_time="2024-01-15T18:00:00",
                status="invalid_status"
            )
            self.assert_test(False, "Invalid status rejected")
        except ValueError:
            self.assert_test(True, "Invalid status rejected")
        
        # End time before start time
        try:
            Event(
                id="test_4",
                title="Test Event",
                location=Location(name="Test Loc", lat=50.0, lon=11.0),
                start_time="2024-01-15T18:00:00",
                end_time="2024-01-15T17:00:00",  # Before start time
                status="pending"
            )
            self.assert_test(False, "End time before start time rejected")
        except ValueError:
            self.assert_test(True, "End time before start time rejected")
        
        # Title too long
        try:
            Event(
                id="test_5",
                title="x" * 600,  # Too long
                location=Location(name="Test Loc", lat=50.0, lon=11.0),
                start_time="2024-01-15T18:00:00",
                status="pending"
            )
            self.assert_test(False, "Title too long rejected")
        except ValidationError:
            self.assert_test(True, "Title too long rejected")
    
    def test_scraping_source_validation(self):
        """Test ScrapingSource model validation"""
        print("\n=== Testing ScrapingSource Validation ===")
        
        # Valid source
        try:
            ScrapingSource(
                name="Test Source",
                type="rss",
                url="https://example.com/feed.rss",
                enabled=True
            )
            self.assert_test(True, "Valid scraping source accepted")
        except Exception as e:
            self.assert_test(False, "Valid scraping source accepted", str(e))
        
        # Invalid URL (no protocol)
        try:
            ScrapingSource(
                name="Test Source",
                type="rss",
                url="example.com/feed.rss",
                enabled=True
            )
            self.assert_test(False, "Invalid URL rejected (no protocol)")
        except ValueError:
            self.assert_test(True, "Invalid URL rejected (no protocol)")
        
        # Invalid type
        try:
            ScrapingSource(
                name="Test Source",
                type="invalid_type",
                url="https://example.com/feed",
                enabled=True
            )
            self.assert_test(False, "Invalid source type rejected")
        except ValueError:
            self.assert_test(True, "Invalid source type rejected")
    
    def test_map_config_validation(self):
        """Test MapConfig model validation"""
        print("\n=== Testing MapConfig Validation ===")
        
        # Valid map config
        try:
            MapConfig(
                default_center={"lat": 50.0, "lon": 11.0},
                default_zoom=13
            )
            self.assert_test(True, "Valid map config accepted")
        except Exception as e:
            self.assert_test(False, "Valid map config accepted", str(e))
        
        # Invalid center (missing lat)
        try:
            MapConfig(
                default_center={"lon": 11.0},
                default_zoom=13
            )
            self.assert_test(False, "Invalid center rejected (missing lat)")
        except ValueError:
            self.assert_test(True, "Invalid center rejected (missing lat)")
        
        # Invalid zoom (too high)
        try:
            MapConfig(
                default_center={"lat": 50.0, "lon": 11.0},
                default_zoom=25  # Too high
            )
            self.assert_test(False, "Invalid zoom level rejected (>20)")
        except ValidationError:
            self.assert_test(True, "Invalid zoom level rejected (>20)")
    
    def test_validate_event_data_function(self):
        """Test validate_event_data function"""
        print("\n=== Testing validate_event_data Function ===")
        
        # Valid event data
        event_data = {
            "id": "test_1",
            "title": "Test Event",
            "location": {
                "name": "Test Location",
                "lat": 50.0,
                "lon": 11.0
            },
            "start_time": "2024-01-15T18:00:00",
            "status": "pending"
        }
        
        try:
            validated = validate_event_data(event_data)
            self.assert_test(isinstance(validated, Event), "validate_event_data returns Event model")
        except Exception as e:
            self.assert_test(False, "validate_event_data returns Event model", str(e))
    
    def test_validate_events_list_function(self):
        """Test validate_events_list function"""
        print("\n=== Testing validate_events_list Function ===")
        
        events_data = [
            {
                "id": "test_1",
                "title": "Valid Event 1",
                "location": {"name": "Loc 1", "lat": 50.0, "lon": 11.0},
                "start_time": "2024-01-15T18:00:00",
                "status": "pending"
            },
            {
                "id": "test_2",
                "title": "Invalid Event",
                "location": {"name": "Loc 2", "lat": 100.0, "lon": 11.0},  # Invalid lat
                "start_time": "2024-01-15T19:00:00",
                "status": "pending"
            },
            {
                "id": "test_3",
                "title": "Valid Event 2",
                "location": {"name": "Loc 3", "lat": 51.0, "lon": 12.0},
                "start_time": "2024-01-15T20:00:00",
                "status": "pending"
            }
        ]
        
        try:
            validated = validate_events_list(events_data)
            # Should skip invalid event, return 2 valid ones
            self.assert_test(len(validated) == 2, "validate_events_list skips invalid events")
        except Exception as e:
            self.assert_test(False, "validate_events_list skips invalid events", str(e))
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("=" * 60)
        print("  KRWL> Validation Tests")
        print("=" * 60)
        
        self.test_location_validation()
        self.test_event_validation()
        self.test_scraping_source_validation()
        self.test_map_config_validation()
        self.test_validate_event_data_function()
        self.test_validate_events_list_function()
        
        print("\n" + "=" * 60)
        print(f"Tests completed: {self.tests_passed} passed, {self.tests_failed} failed")
        print("=" * 60)
        
        return self.tests_failed == 0


def main():
    """Run validation tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Pydantic validation models')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    tester = ValidationTester(verbose=args.verbose)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
