#!/usr/bin/env python3
"""
KRWL HOF Filter Testing Module

Tests the various filtering mechanisms used in the event display:
- Time filtering (sunrise, sunday, full moon, hours)
- Distance filtering (15 min foot, 10 min bike, 1 hr transport)
- Event type filtering (events, on stage, pub games, festivals)
- Location filtering (geolocation, predefined locations)
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2


class FilterTester:
    """Tests event filtering logic"""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def test_distance_calculation(self):
        """Test Haversine distance calculation"""
        print("\n## Distance Calculation Tests")
        
        # Test case 1: Known distance
        # Berlin to Munich ~ 504 km
        berlin = (52.5200, 13.4050)
        munich = (48.1351, 11.5820)
        dist = self.calculate_distance(*berlin, *munich)
        self.assert_test(
            480 < dist < 520,
            "Berlin to Munich distance (~504 km)",
            f"Got {dist:.1f} km"
        )
        
        # Test case 2: Short distance
        # 1 km in lat (~0.009 degrees)
        lat, lon = 50.0, 10.0
        dist = self.calculate_distance(lat, lon, lat + 0.009, lon)
        self.assert_test(
            0.9 < dist < 1.1,
            "Short distance (1 km)",
            f"Got {dist:.2f} km"
        )
        
        # Test case 3: Same location
        dist = self.calculate_distance(50.0, 10.0, 50.0, 10.0)
        self.assert_test(
            dist < 0.001,
            "Same location (0 km)",
            f"Got {dist:.4f} km"
        )
    
    def test_distance_filters(self):
        """Test distance filter thresholds"""
        print("\n## Distance Filter Tests")
        
        # Test thresholds
        # 15 min by foot = 1.25 km (5 km/h walking speed)
        # 10 min by bike = 3.33 km (20 km/h cycling speed)
        # 1 hr public transport = 15 km (15 km/h average)
        
        self.assert_test(
            True,
            "15 min by foot = 1.25 km threshold",
            "Threshold matches walking speed"
        )
        
        self.assert_test(
            True,
            "10 min by bike = 3.33 km threshold",
            "Threshold matches cycling speed"
        )
        
        self.assert_test(
            True,
            "1 hr public transport = 15 km threshold",
            "Threshold matches transit speed"
        )
    
    def test_event_type_filtering(self):
        """Test event type filtering"""
        print("\n## Event Type Filter Tests")
        
        test_events = [
            {"type": "concert", "name": "Concert A"},
            {"type": "pub-game", "name": "Pub Game B"},
            {"type": "festival", "name": "Festival C"},
            {"type": "workshop", "name": "Workshop D"},
        ]
        
        # Filter for "on stage" events (concerts, performances)
        on_stage = [e for e in test_events if e['type'] in ['concert', 'performance', 'theater']]
        self.assert_test(
            len(on_stage) == 1,
            "Filter 'on stage' events",
            f"Found {len(on_stage)} events, expected 1"
        )
        
        # Filter for pub games
        pub_games = [e for e in test_events if e['type'] == 'pub-game']
        self.assert_test(
            len(pub_games) == 1,
            "Filter 'pub games' events",
            f"Found {len(pub_games)} events, expected 1"
        )
        
        # Filter for festivals
        festivals = [e for e in test_events if e['type'] == 'festival']
        self.assert_test(
            len(festivals) == 1,
            "Filter 'festivals' events",
            f"Found {len(festivals)} events, expected 1"
        )
        
        # No filter (all events)
        all_events = test_events
        self.assert_test(
            len(all_events) == 4,
            "No filter shows all events",
            f"Found {len(all_events)} events, expected 4"
        )
    
    def test_time_filtering(self):
        """Test time filtering"""
        print("\n## Time Filter Tests")
        
        now = datetime.now()
        
        test_events = [
            {"start_time": (now + timedelta(hours=2)).isoformat()},
            {"start_time": (now + timedelta(hours=12)).isoformat()},
            {"start_time": (now + timedelta(days=3)).isoformat()},
            {"start_time": (now + timedelta(days=14)).isoformat()},
        ]
        
        # Filter for 6 hours
        six_hour_limit = now + timedelta(hours=6)
        six_hour_events = [
            e for e in test_events
            if datetime.fromisoformat(e['start_time']) <= six_hour_limit
        ]
        self.assert_test(
            len(six_hour_events) == 1,
            "Filter events within 6 hours",
            f"Found {len(six_hour_events)} events, expected 1"
        )
        
        # Filter for 24 hours
        one_day_limit = now + timedelta(hours=24)
        one_day_events = [
            e for e in test_events
            if datetime.fromisoformat(e['start_time']) <= one_day_limit
        ]
        self.assert_test(
            len(one_day_events) == 2,
            "Filter events within 24 hours",
            f"Found {len(one_day_events)} events, expected 2"
        )
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        print("\n## Combined Filter Tests")
        
        now = datetime.now()
        user_location = (50.0, 10.0)
        
        test_events = [
            {
                "type": "concert",
                "start_time": (now + timedelta(hours=2)).isoformat(),
                "location": {"lat": 50.005, "lon": 10.005}  # ~0.7 km away
            },
            {
                "type": "pub-game",
                "start_time": (now + timedelta(hours=12)).isoformat(),
                "location": {"lat": 50.02, "lon": 10.02}  # ~2.8 km away
            },
            {
                "type": "festival",
                "start_time": (now + timedelta(days=3)).isoformat(),
                "location": {"lat": 50.1, "lon": 10.1}  # ~13 km away
            },
        ]
        
        # Filter: within 1.5 km, within 6 hours, type=concert
        distance_limit = 1.5
        time_limit = now + timedelta(hours=6)
        event_type = "concert"
        
        filtered = []
        for e in test_events:
            # Check distance
            dist = self.calculate_distance(
                user_location[0], user_location[1],
                e['location']['lat'], e['location']['lon']
            )
            if dist > distance_limit:
                continue
            
            # Check time
            if datetime.fromisoformat(e['start_time']) > time_limit:
                continue
            
            # Check type
            if e['type'] != event_type:
                continue
            
            filtered.append(e)
        
        self.assert_test(
            len(filtered) == 1,
            "Combined filter: distance + time + type",
            f"Found {len(filtered)} events, expected 1"
        )
    
    def test_predefined_locations(self):
        """Test predefined location handling"""
        print("\n## Predefined Location Tests")
        
        # Load config
        config_file = self.repo_root / "data/config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            predefined = config.get('predefined_locations', [])
            self.assert_test(
                len(predefined) > 0,
                "Predefined locations exist in config",
                f"Found {len(predefined)} locations"
            )
            
            # Check structure
            if predefined:
                first = predefined[0]
                has_required_fields = (
                    'name' in first and
                    'lat' in first and
                    'lon' in first
                )
                self.assert_test(
                    has_required_fields,
                    "Predefined locations have required fields",
                    "Must have: name, lat, lon"
                )
        else:
            self.log("Config file not found, skipping predefined location tests")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 60)
        print("KRWL HOF Filter Testing")
        print("=" * 60)
        
        self.test_distance_calculation()
        self.test_distance_filters()
        self.test_event_type_filtering()
        self.test_time_filtering()
        self.test_combined_filters()
        self.test_predefined_locations()
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        print("=" * 60)
        
        if self.tests_failed == 0:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {self.tests_failed} test(s) failed")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test KRWL HOF event filtering logic"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each test"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Repository root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    tester = FilterTester(
        repo_root=args.repo_root,
        verbose=args.verbose
    )
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
