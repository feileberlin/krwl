#!/usr/bin/env python3
"""
Test for Frankenpost custom scraper location extraction
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.smart_scraper.sources.frankenpost import FrankenpostSource
from modules.smart_scraper.base import SourceOptions
from bs4 import BeautifulSoup


def test_location_extraction():
    """Test location extraction from various HTML patterns"""
    
    print("Testing Frankenpost location extraction...")
    
    # Setup scraper
    config = {
        'name': 'Frankenpost',
        'url': 'https://event.frankenpost.de/index.php',
        'type': 'frankenpost'
    }
    options = SourceOptions()
    # Set default location to avoid ValueError when no location is found
    options.default_location = {
        'name': 'Hof',
        'lat': 50.3167,
        'lon': 11.9167
    }
    scraper = FrankenpostSource(config, options)
    
    # Test cases with different HTML patterns
    test_cases = [
        {
            'name': 'Address pattern in text',
            'html': '''
            <html>
                <body>
                    <h1>Test Event</h1>
                    <p>Das Event findet statt in der Maximilianstraße 33, 95444 Bayreuth.</p>
                </body>
            </html>
            ''',
            'expected_name_contains': 'Maximilianstraße'
        },
        {
            'name': 'Location label with value',
            'html': '''
            <html>
                <body>
                    <h1>Test Event</h1>
                    <div>
                        <span>Ort:</span>
                        <span>Kunstmuseum Bayreuth, Maximilianstraße 33, 95444 Bayreuth</span>
                    </div>
                </body>
            </html>
            ''',
            'expected_name_contains': 'Kunstmuseum'
        },
        {
            'name': 'Venue in heading',
            'html': '''
            <html>
                <body>
                    <h2>Freiheitshalle Hof</h2>
                    <p>Beschreibung des Events</p>
                </body>
            </html>
            ''',
            'expected_name_contains': 'Freiheitshalle'
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] Testing: {test_case['name']}")
        soup = BeautifulSoup(test_case['html'], 'lxml')
        
        try:
            location, extraction_details = scraper._extract_location_from_detail(soup)
            
            # Check if location was extracted
            if not location or not location.get('name'):
                print(f"  ✗ No location extracted")
                failed += 1
                continue
            
            location_name = location['name']
            expected_substring = test_case['expected_name_contains']
            
            if expected_substring.lower() in location_name.lower():
                print(f"  ✓ Location: {location_name}")
                print(f"  ✓ Coordinates: {location['lat']}, {location['lon']}")
                passed += 1
            else:
                print(f"  ✗ Expected '{expected_substring}' in location name")
                print(f"  ✗ Got: {location_name}")
                failed += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


def test_coordinate_estimation():
    """Test coordinate estimation for known cities"""
    
    print("\n\nTesting coordinate estimation...")
    
    config = {
        'name': 'Frankenpost',
        'url': 'https://event.frankenpost.de/index.php',
        'type': 'frankenpost'
    }
    options = SourceOptions()
    # Set default location to avoid ValueError
    options.default_location = {
        'name': 'Hof',
        'lat': 50.3167,
        'lon': 11.9167
    }
    scraper = FrankenpostSource(config, options)
    
    test_cities = [
        ('Kunstmuseum Bayreuth, Maximilianstraße 33, 95444 Bayreuth', 'bayreuth', 49.9440),
        ('Freiheitshalle Hof, Kulmbacher Str., 95030 Hof', 'hof', 50.3167),
        ('Rathaus Selb, Marktplatz 1, 95100 Selb', 'selb', 50.1705),
    ]
    
    passed = 0
    failed = 0
    
    for i, (location_text, expected_city, expected_lat) in enumerate(test_cities, 1):
        print(f"\n[{i}] Testing: {location_text}")
        
        try:
            location = scraper._estimate_coordinates(location_text)
            
            city_match = expected_city in location_text.lower()
            lat_match = abs(location['lat'] - expected_lat) < 0.1  # Within 0.1 degrees
            
            if city_match and lat_match:
                print(f"  ✓ Location: {location['name']}")
                print(f"  ✓ Coordinates: {location['lat']}, {location['lon']}")
                passed += 1
            else:
                print(f"  ✗ Coordinate mismatch")
                print(f"  Expected lat ~{expected_lat}, got {location['lat']}")
                failed += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == '__main__':
    try:
        result1 = test_location_extraction()
        result2 = test_coordinate_estimation()
        
        if result1 and result2:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
