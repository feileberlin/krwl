#!/usr/bin/env python3
"""
Tests for modular location utilities.

Tests CityDetector, AmbiguousLocationHandler, and GeolocationResolver modules.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.smart_scraper.scraper_utils import (
    CityDetector,
    AmbiguousLocationHandler,
    GeolocationResolver,
    LocationNormalizer
)


def test_city_detector_from_text():
    """Test city extraction from venue names and text."""
    print("\n" + "="*60)
    print("Test: CityDetector.extract_from_text()")
    print("="*60)
    
    test_cases = [
        ("Kunstmuseum Bayreuth", "Bayreuth"),
        ("Theater Hof", "Hof"),
        ("Rathaus Selb", "Selb"),
        ("Gemeindezentrum Rehau", "Rehau"),
        ("Sporthalle Kulmbach", "Kulmbach"),
        ("Restaurant am Münchberg", "Münchberg"),
        ("Richard-Wagner-Museum", None),  # No city in name
        ("Generic Venue", None),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_city in test_cases:
        result = CityDetector.extract_from_text(text)
        if result == expected_city:
            print(f"  ✓ '{text}' → '{result}'")
            passed += 1
        else:
            print(f"  ✗ '{text}' → Expected '{expected_city}', got '{result}'")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_city_detector_from_address():
    """Test city extraction from German addresses."""
    print("\n" + "="*60)
    print("Test: CityDetector.extract_from_address()")
    print("="*60)
    
    test_cases = [
        ("Maximilianstraße 33, 95444 Bayreuth", "Bayreuth"),
        ("Kulmbacher Str. 1, 95030 Hof", "Hof"),
        ("Marktplatz 1, 95100 Selb", "Selb"),
        ("Bahnhofstraße 5, 95111 Rehau", "Rehau"),
        ("Invalid address format", None),
    ]
    
    passed = 0
    failed = 0
    
    for address, expected_city in test_cases:
        result = CityDetector.extract_from_address(address)
        if result == expected_city:
            print(f"  ✓ '{address[:40]}...' → '{result}'")
            passed += 1
        else:
            print(f"  ✗ '{address[:40]}...' → Expected '{expected_city}', got '{result}'")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_city_detector_from_coordinates():
    """Test reverse geocoding from coordinates."""
    print("\n" + "="*60)
    print("Test: CityDetector.extract_from_coordinates()")
    print("="*60)
    
    test_cases = [
        # Exact city center coordinates
        (49.9440, 11.5760, "Bayreuth"),
        (50.3167, 11.9167, "Hof"),
        (50.1705, 12.1328, "Selb"),
        
        # Slightly offset from city center (within 10km)
        (50.32, 11.92, "Hof"),
        (49.95, 11.58, "Bayreuth"),
        
        # Far from any city (>10km)
        (51.0, 12.0, None),
    ]
    
    passed = 0
    failed = 0
    
    for lat, lon, expected_city in test_cases:
        result = CityDetector.extract_from_coordinates(lat, lon)
        if result == expected_city:
            print(f"  ✓ ({lat}, {lon}) → '{result}'")
            passed += 1
        else:
            print(f"  ✗ ({lat}, {lon}) → Expected '{expected_city}', got '{result}'")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_ambiguous_location_detection():
    """Test detection of ambiguous location names."""
    print("\n" + "="*60)
    print("Test: AmbiguousLocationHandler.is_ambiguous()")
    print("="*60)
    
    test_cases = [
        # Ambiguous (should return True)
        ("Sportheim", True),
        ("Bahnhof", True),
        ("Rathaus", True),
        ("Feuerwehrhaus", True),
        ("Turnhalle", True),
        ("Mehrzweckhalle", True),
        ("Kirche", True),
        
        # Not ambiguous (should return False)
        ("Richard-Wagner-Museum", False),
        ("Freiheitshalle", False),  # Specific venue name
        ("Kunstmuseum Bayreuth", False),
        ("Theater Hof", False),
        ("MAKkultur", False),
    ]
    
    passed = 0
    failed = 0
    
    for location_name, expected in test_cases:
        result = AmbiguousLocationHandler.is_ambiguous(location_name)
        if result == expected:
            print(f"  ✓ '{location_name}' → {'Ambiguous' if result else 'Unique'}")
            passed += 1
        else:
            print(f"  ✗ '{location_name}' → Expected {expected}, got {result}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_ambiguous_location_disambiguation():
    """Test appending city names to ambiguous locations."""
    print("\n" + "="*60)
    print("Test: AmbiguousLocationHandler.disambiguate()")
    print("="*60)
    
    test_cases = [
        # Ambiguous location with Hof coordinates
        (
            {"name": "Sportheim", "lat": 50.3167, "lon": 11.9167},
            "Sportheim Hof"
        ),
        # Ambiguous location with Bayreuth coordinates
        (
            {"name": "Bahnhof", "lat": 49.9440, "lon": 11.5760},
            "Bahnhof Bayreuth"
        ),
        # Ambiguous location with Selb coordinates
        (
            {"name": "Rathaus", "lat": 50.1705, "lon": 12.1328},
            "Rathaus Selb"
        ),
        # Already has city in name (should not change)
        (
            {"name": "Sportheim Rehau", "lat": 50.2489, "lon": 12.0364},
            "Sportheim Rehau"
        ),
        # Not ambiguous (should not change)
        (
            {"name": "Richard-Wagner-Museum", "lat": 49.9440, "lon": 11.5760},
            "Richard-Wagner-Museum"
        ),
        # Ambiguous but no coordinates (should not change)
        (
            {"name": "Turnhalle", "lat": None, "lon": None},
            "Turnhalle"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for location, expected_name in test_cases:
        result = AmbiguousLocationHandler.disambiguate(location)
        result_name = result.get('name')
        if result_name == expected_name:
            print(f"  ✓ '{location['name']}' → '{result_name}'")
            passed += 1
        else:
            print(f"  ✗ '{location['name']}' → Expected '{expected_name}', got '{result_name}'")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_geolocation_resolver():
    """Test geolocation resolution with multiple strategies."""
    print("\n" + "="*60)
    print("Test: GeolocationResolver.resolve()")
    print("="*60)
    
    # Create temp directory with verified locations
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        assets_json = base_path / 'assets' / 'json'
        assets_json.mkdir(parents=True)
        
        # Create verified locations database
        verified_data = {
            "locations": {
                "Theater Hof": {
                    "name": "Theater Hof",
                    "lat": 50.3200,
                    "lon": 11.9180,
                    "address": "Kulmbacher Str., 95030 Hof"
                }
            }
        }
        with open(assets_json / 'verified_locations.json', 'w') as f:
            json.dump(verified_data, f)
        
        # Create empty unverified locations file
        with open(assets_json / 'unverified_locations.json', 'w') as f:
            json.dump({"locations": {}}, f)
        
        resolver = GeolocationResolver(base_path)
        
        test_cases = [
            # Strategy 1: Provided coordinates (iframe extraction)
            {
                "input": {
                    "location_name": "Some Venue",
                    "coordinates": (50.3167, 11.9167)
                },
                "expected_method": "iframe_extraction",
                "expected_needs_review": False,
                "description": "Coordinates from iframe"
            },
            # Strategy 2: Verified database exact match
            {
                "input": {
                    "location_name": "Theater Hof",
                    "coordinates": None
                },
                "expected_method": "verified_database",
                "expected_needs_review": False,
                "description": "Verified database match"
            },
            # Strategy 3: City from address
            {
                "input": {
                    "location_name": "Some Museum",
                    "address": "Hauptstraße 1, 95444 Bayreuth",
                    "coordinates": None
                },
                "expected_method": "address_city_lookup",
                "expected_needs_review": True,  # City center, not exact
                "description": "City from address"
            },
            # Strategy 4: City from venue name
            {
                "input": {
                    "location_name": "Sporthalle Selb",
                    "coordinates": None
                },
                "expected_method": "venue_name_city_lookup",
                "expected_needs_review": True,  # City center, not exact
                "description": "City from venue name"
            },
            # Strategy 5: Unresolved (needs editor review)
            {
                "input": {
                    "location_name": "Unknown Venue",
                    "coordinates": None
                },
                "expected_method": "unresolved",
                "expected_needs_review": True,
                "description": "Unresolved - editor review needed"
            },
        ]
        
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            input_data = test_case["input"]
            result = resolver.resolve(**input_data)
            
            method_match = result['resolution_method'] == test_case["expected_method"]
            review_match = result['needs_review'] == test_case["expected_needs_review"]
            
            if method_match and review_match:
                print(f"  ✓ {test_case['description']}")
                print(f"      Method: {result['resolution_method']}, Needs review: {result['needs_review']}")
                passed += 1
            else:
                print(f"  ✗ {test_case['description']}")
                print(f"      Expected: {test_case['expected_method']}, {test_case['expected_needs_review']}")
                print(f"      Got: {result['resolution_method']}, {result['needs_review']}")
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0


def test_no_silent_defaults():
    """Test that no coordinates are assigned without flagging for review."""
    print("\n" + "="*60)
    print("Test: No Silent Defaults (CRITICAL)")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        assets_json = base_path / 'assets' / 'json'
        assets_json.mkdir(parents=True)
        
        # Create empty verified locations
        with open(assets_json / 'verified_locations.json', 'w') as f:
            json.dump({"locations": {}}, f)
        
        with open(assets_json / 'unverified_locations.json', 'w') as f:
            json.dump({"locations": {}}, f)
        
        resolver = GeolocationResolver(base_path)
        
        # Test cases that should NEVER silently default to Hof
        test_cases = [
            "Richard-Wagner-Museum",
            "MAKkultur",
            "Some Random Venue",
            "Kulturzentrum XYZ",
        ]
        
        passed = 0
        failed = 0
        
        for venue_name in test_cases:
            result = resolver.resolve(location_name=venue_name, coordinates=None)
            
            # If coordinates are assigned, needs_review MUST be True
            if result['lat'] is not None and result['lon'] is not None:
                if result['needs_review']:
                    print(f"  ✓ '{venue_name}' → Coords assigned, flagged for review ✓")
                    passed += 1
                else:
                    print(f"  ✗ '{venue_name}' → SILENT DEFAULT DETECTED! ✗")
                    print(f"      Coords: ({result['lat']}, {result['lon']})")
                    print(f"      Method: {result['resolution_method']}")
                    failed += 1
            else:
                print(f"  ✓ '{venue_name}' → No coords, needs_review={result['needs_review']} ✓")
                passed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n" + "!"*60)
            print("CRITICAL FAILURE: Silent defaults detected!")
            print("This is the bullshit behavior we're trying to eliminate.")
            print("!"*60)
        
        return failed == 0


def main():
    """Run all tests."""
    print("\n" + "═"*60)
    print("MODULAR LOCATION UTILITIES TEST SUITE")
    print("═"*60)
    
    tests = [
        ("CityDetector - Text Extraction", test_city_detector_from_text),
        ("CityDetector - Address Extraction", test_city_detector_from_address),
        ("CityDetector - Coordinate Reverse Geocoding", test_city_detector_from_coordinates),
        ("AmbiguousLocationHandler - Detection", test_ambiguous_location_detection),
        ("AmbiguousLocationHandler - Disambiguation", test_ambiguous_location_disambiguation),
        ("GeolocationResolver - Strategy Chain", test_geolocation_resolver),
        ("No Silent Defaults (CRITICAL)", test_no_silent_defaults),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ {test_name} CRASHED: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "═"*60)
    print("TEST SUMMARY")
    print("═"*60)
    
    passed_count = sum(1 for _, success in results if success)
    failed_count = len(results) - passed_count
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "═"*60)
    print(f"Total: {passed_count}/{len(results)} tests passed")
    print("═"*60)
    
    if failed_count > 0:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
