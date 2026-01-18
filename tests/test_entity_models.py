#!/usr/bin/env python3
"""
Test Entity Models

Tests for entity data models (Location, Organizer) and ID generation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.entity_models import (
    Location, Organizer, generate_location_id, generate_organizer_id
)


def test_location_creation():
    """Test Location dataclass creation"""
    print("Testing Location creation...")
    
    location = Location(
        id="loc_theater_hof",
        name="Theater Hof",
        lat=50.3200,
        lon=11.9180,
        address="Kulmbacher Str., 95030 Hof"
    )
    
    assert location.id == "loc_theater_hof"
    assert location.name == "Theater Hof"
    assert location.lat == 50.3200
    assert location.lon == 11.9180
    assert location.address == "Kulmbacher Str., 95030 Hof"
    assert location.verified == False
    assert location.address_hidden == False
    
    print("✓ Location creation test passed")


def test_location_to_dict():
    """Test Location to_dict conversion"""
    print("Testing Location to_dict...")
    
    location = Location(
        id="loc_test",
        name="Test Location",
        lat=50.0,
        lon=11.0,
        verified=True
    )
    
    data = location.to_dict()
    
    assert isinstance(data, dict)
    assert data['id'] == "loc_test"
    assert data['name'] == "Test Location"
    assert data['verified'] == True
    # None values should be excluded
    assert 'address' not in data
    
    print("✓ Location to_dict test passed")


def test_location_from_dict():
    """Test Location from_dict creation"""
    print("Testing Location from_dict...")
    
    data = {
        'id': 'loc_test',
        'name': 'Test Location',
        'lat': 50.0,
        'lon': 11.0,
        'verified': True,
        'extra_field': 'ignored'  # Should be ignored
    }
    
    location = Location.from_dict(data)
    
    assert location.id == 'loc_test'
    assert location.name == 'Test Location'
    assert location.verified == True
    # extra_field should not cause an error
    
    print("✓ Location from_dict test passed")


def test_organizer_creation():
    """Test Organizer dataclass creation"""
    print("Testing Organizer creation...")
    
    organizer = Organizer(
        id="org_kulturverein_hof",
        name="Kulturverein Hof",
        website="https://kulturverein-hof.de",
        email="info@kulturverein-hof.de"
    )
    
    assert organizer.id == "org_kulturverein_hof"
    assert organizer.name == "Kulturverein Hof"
    assert organizer.website == "https://kulturverein-hof.de"
    assert organizer.email == "info@kulturverein-hof.de"
    assert organizer.verified == False
    
    print("✓ Organizer creation test passed")


def test_generate_location_id():
    """Test location ID generation"""
    print("Testing generate_location_id...")
    
    test_cases = [
        ("Theater Hof", "loc_theater_hof"),
        ("RW21 Volkshochschule", "loc_rw21_volkshochschule"),
        ("Café am Markt", "loc_caf_am_markt"),  # Special chars like 'é' are stripped by the implementation
        ("Some-Place  With    Spaces", "loc_some_place_with_spaces"),
    ]
    
    for name, expected_id in test_cases:
        result = generate_location_id(name)
        assert result == expected_id, f"Expected {expected_id}, got {result}"
    
    print("✓ generate_location_id test passed")


def test_generate_organizer_id():
    """Test organizer ID generation"""
    print("Testing generate_organizer_id...")
    
    test_cases = [
        ("Kulturverein Hof", "org_kulturverein_hof"),
        ("Theater Hof", "org_theater_hof"),
        ("Some-Organization  Name", "org_some_organization_name"),
    ]
    
    for name, expected_id in test_cases:
        result = generate_organizer_id(name)
        assert result == expected_id, f"Expected {expected_id}, got {result}"
    
    print("✓ generate_organizer_id test passed")


def run_all_tests():
    """Run all entity model tests"""
    print("=" * 70)
    print("  Entity Models Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_location_creation,
        test_location_to_dict,
        test_location_from_dict,
        test_organizer_creation,
        test_generate_location_id,
        test_generate_organizer_id,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"  Tests: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
