#!/usr/bin/env python3
"""
Unit Tests for Entity Management System

Tests entity_models, entity_resolver, location_manager, and organizer_manager modules.
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.entity_models import Location, Organizer, generate_location_id, generate_organizer_id
from modules.entity_resolver import EntityResolver
from modules.location_manager import LocationManager
from modules.organizer_manager import OrganizerManager


class TestEntityModels:
    """Test entity_models.py"""
    
    def test_generate_location_id(self):
        """Test location ID generation"""
        print("  Testing location ID generation...")
        
        # Simple case
        id1 = generate_location_id("Theater Hof", 50.3200, 11.9180)
        assert id1 == "loc_theater_hof", f"Expected 'loc_theater_hof', got '{id1}'"
        
        # Consistency check
        id2 = generate_location_id("Theater Hof", 50.3200, 11.9180)
        assert id1 == id2, "IDs should be consistent for same input"
        
        # Special characters
        id3 = generate_location_id("Café & Bar", 50.0, 11.0)
        assert id3.startswith("loc_"), "ID should start with 'loc_'"
        assert "caf" in id3.lower(), "ID should contain cleaned name"
        
        print("    ✓ Location ID generation works")
    
    def test_generate_organizer_id(self):
        """Test organizer ID generation"""
        print("  Testing organizer ID generation...")
        
        # Simple case
        id1 = generate_organizer_id("Theater Hof")
        assert id1 == "org_theater_hof", f"Expected 'org_theater_hof', got '{id1}'"
        
        # Consistency check
        id2 = generate_organizer_id("Theater Hof")
        assert id1 == id2, "IDs should be consistent for same input"
        
        print("    ✓ Organizer ID generation works")
    
    def test_location_dataclass(self):
        """Test Location dataclass"""
        print("  Testing Location dataclass...")
        
        # Create location
        loc = Location(
            id="loc_test",
            name="Test Location",
            lat=50.0,
            lon=11.0,
            address="Test Street 1",
            verified=True
        )
        
        # Check fields
        assert loc.id == "loc_test"
        assert loc.name == "Test Location"
        assert loc.lat == 50.0
        assert loc.verified is True
        
        # Check timestamp auto-generation
        assert loc.created_at is not None
        assert loc.updated_at is not None
        
        # Test to_dict
        loc_dict = loc.to_dict()
        assert loc_dict['id'] == "loc_test"
        assert loc_dict['name'] == "Test Location"
        
        # Test from_dict
        loc2 = Location.from_dict(loc_dict)
        assert loc2.id == loc.id
        assert loc2.name == loc.name
        
        # Test matches_name
        assert loc.matches_name("test") is True
        assert loc.matches_name("Test Location") is True
        assert loc.matches_name("nonexistent") is False
        
        print("    ✓ Location dataclass works")
    
    def test_organizer_dataclass(self):
        """Test Organizer dataclass"""
        print("  Testing Organizer dataclass...")
        
        # Create organizer
        org = Organizer(
            id="org_test",
            name="Test Organizer",
            verified=True,
            email="test@example.com"
        )
        
        # Check fields
        assert org.id == "org_test"
        assert org.name == "Test Organizer"
        assert org.verified is True
        assert org.email == "test@example.com"
        
        # Test to_dict and from_dict
        org_dict = org.to_dict()
        org2 = Organizer.from_dict(org_dict)
        assert org2.id == org.id
        
        print("    ✓ Organizer dataclass works")


class TestEntityResolver:
    """Test entity_resolver.py"""
    
    def setup(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create assets/json directory
        (self.base_path / 'assets' / 'json').mkdir(parents=True, exist_ok=True)
        
        # Create test locations.json
        locations_data = {
            'locations': {
                'loc_test1': {
                    'id': 'loc_test1',
                    'name': 'Test Location 1',
                    'lat': 50.0,
                    'lon': 11.0,
                    'address': 'Test Street 1',
                    'verified': True,
                    'aliases': [],
                    'usage_count': 0
                }
            }
        }
        
        with open(self.base_path / 'assets' / 'json' / 'locations.json', 'w') as f:
            json.dump(locations_data, f)
        
        # Create test organizers.json
        organizers_data = {
            'organizers': {
                'org_test1': {
                    'id': 'org_test1',
                    'name': 'Test Organizer 1',
                    'verified': True,
                    'aliases': [],
                    'usage_count': 0
                }
            }
        }
        
        with open(self.base_path / 'assets' / 'json' / 'organizers.json', 'w') as f:
            json.dump(organizers_data, f)
    
    def test_tier_1_reference_only(self):
        """Test Tier 1: Reference only"""
        print("  Testing Tier 1: Reference only...")
        
        self.setup()
        resolver = EntityResolver(self.base_path)
        
        # Event with location_id only
        event = {'location_id': 'loc_test1'}
        resolved_location = resolver.resolve_event_location(event)
        
        assert resolved_location is not None
        assert resolved_location['name'] == 'Test Location 1'
        assert resolved_location['lat'] == 50.0
        
        print("    ✓ Tier 1 reference resolution works")
    
    def test_tier_2_partial_override(self):
        """Test Tier 2: Partial override"""
        print("  Testing Tier 2: Partial override...")
        
        self.setup()
        resolver = EntityResolver(self.base_path)
        
        # Event with location_id + location_override
        event = {
            'location_id': 'loc_test1',
            'location_override': {
                'name': 'Test Location 1 - VIP Area'
            }
        }
        
        resolved_location = resolver.resolve_event_location(event)
        
        assert resolved_location is not None
        assert resolved_location['name'] == 'Test Location 1 - VIP Area'  # Overridden
        assert resolved_location['lat'] == 50.0  # From base
        assert resolved_location['address'] == 'Test Street 1'  # From base
        
        print("    ✓ Tier 2 partial override works")
    
    def test_tier_3_full_embedded(self):
        """Test Tier 3: Full embedded"""
        print("  Testing Tier 3: Full embedded...")
        
        self.setup()
        resolver = EntityResolver(self.base_path)
        
        # Event with embedded location
        event = {
            'location': {
                'name': 'Pop-Up Stage',
                'lat': 51.0,
                'lon': 12.0
            }
        }
        
        resolved_location = resolver.resolve_event_location(event)
        
        assert resolved_location is not None
        assert resolved_location['name'] == 'Pop-Up Stage'
        assert resolved_location['lat'] == 51.0
        
        print("    ✓ Tier 3 full embedded works")
    
    def test_resolve_events_batch(self):
        """Test batch event resolution"""
        print("  Testing batch event resolution...")
        
        self.setup()
        resolver = EntityResolver(self.base_path)
        
        events = [
            {'id': 'e1', 'location_id': 'loc_test1'},
            {'id': 'e2', 'location': {'name': 'Embedded', 'lat': 52.0, 'lon': 13.0}},
            {'id': 'e3', 'organizer_id': 'org_test1'}
        ]
        
        resolved = resolver.resolve_events(events)
        
        assert len(resolved) == 3
        assert resolved[0]['location']['name'] == 'Test Location 1'
        assert resolved[1]['location']['name'] == 'Embedded'
        assert resolved[2]['organizer']['name'] == 'Test Organizer 1'
        
        print("    ✓ Batch resolution works")
    
    def test_entity_coverage_analysis(self):
        """Test entity coverage analysis"""
        print("  Testing entity coverage analysis...")
        
        self.setup()
        resolver = EntityResolver(self.base_path)
        
        events = [
            {'id': 'e1', 'location_id': 'loc_test1'},  # Tier 1
            {'id': 'e2', 'location_id': 'loc_test1', 'location_override': {'name': 'Override'}},  # Tier 2
            {'id': 'e3', 'location': {'name': 'Embedded', 'lat': 52.0, 'lon': 13.0}},  # Tier 3
        ]
        
        stats = resolver.analyze_entity_coverage(events)
        
        assert stats['total_events'] == 3
        assert stats['locations']['tier_1_reference'] == 1
        assert stats['locations']['tier_2_override'] == 1
        assert stats['locations']['tier_3_embedded'] == 1
        
        print("    ✓ Entity coverage analysis works")


class TestLocationManager:
    """Test location_manager.py"""
    
    def setup(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create assets/json directory
        (self.base_path / 'assets' / 'json').mkdir(parents=True, exist_ok=True)
    
    def test_add_location(self):
        """Test adding a location"""
        print("  Testing location add...")
        
        self.setup()
        manager = LocationManager(self.base_path)
        
        loc = manager.add("Test Location", 50.0, 11.0, address="Test St 1")
        
        assert loc.name == "Test Location"
        assert loc.lat == 50.0
        assert loc.id.startswith("loc_")
        
        # Verify it's saved
        assert len(manager.locations) == 1
        
        print("    ✓ Location add works")
    
    def test_list_locations(self):
        """Test listing locations"""
        print("  Testing location list...")
        
        self.setup()
        manager = LocationManager(self.base_path)
        
        manager.add("Location 1", 50.0, 11.0, verified=True)
        manager.add("Location 2", 51.0, 12.0, verified=False)
        
        all_locs = manager.list()
        assert len(all_locs) == 2
        
        verified_locs = manager.list(verified_only=True)
        assert len(verified_locs) == 1
        assert verified_locs[0].name == "Location 1"
        
        print("    ✓ Location list works")
    
    def test_search_locations(self):
        """Test searching locations"""
        print("  Testing location search...")
        
        self.setup()
        manager = LocationManager(self.base_path)
        
        manager.add("Theater Hof", 50.0, 11.0)
        manager.add("Freiheitshalle", 50.1, 11.1)
        
        results = manager.search("Theater")
        assert len(results) == 1
        assert results[0].name == "Theater Hof"
        
        print("    ✓ Location search works")
    
    def test_verify_location(self):
        """Test verifying a location"""
        print("  Testing location verify...")
        
        self.setup()
        manager = LocationManager(self.base_path)
        
        loc = manager.add("Test", 50.0, 11.0, verified=False)
        assert loc.verified is False
        
        manager.verify(loc.id)
        verified_loc = manager.get(loc.id)
        assert verified_loc.verified is True
        
        print("    ✓ Location verify works")
    
    def test_statistics(self):
        """Test location statistics"""
        print("  Testing location statistics...")
        
        self.setup()
        manager = LocationManager(self.base_path)
        
        manager.add("Loc 1", 50.0, 11.0, verified=True, address="Street 1")
        manager.add("Loc 2", 51.0, 12.0, verified=False)
        
        stats = manager.get_statistics()
        
        assert stats['total_locations'] == 2
        assert stats['verified_locations'] == 1
        assert stats['unverified_locations'] == 1
        assert stats['locations_with_address'] == 1
        
        print("    ✓ Location statistics work")


def run_all_tests(verbose=False):
    """Run all entity system tests"""
    print("\n" + "=" * 70)
    print("Entity Management System - Unit Tests")
    print("=" * 70)
    
    test_classes = [
        ("Entity Models", TestEntityModels),
        ("Entity Resolver", TestEntityResolver),
        ("Location Manager", TestLocationManager),
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for class_name, test_class in test_classes:
        print(f"\n{class_name}:")
        print("-" * 70)
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                failed_tests += 1
                print(f"  ✗ {method_name} FAILED")
                if verbose:
                    print(f"    Error: {e}")
                    import traceback
                    traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Failed: {failed_tests} ✗")
    
    if failed_tests == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed_tests} test(s) failed")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Test entity management system'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    return run_all_tests(verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())
