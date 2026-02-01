#!/usr/bin/env python3
"""
Test the SPA content routing system.

KRWL is a single-page application serving three content types:
1. Showcase (Antarctica) - Project information and setup guide
2. Error-handling (Atlantis) - Humorous 404 handler
3. Production (Real regions) - Live event calendars

This test validates that event files are properly structured and the
site generator loads all three content sources correctly.
"""

import json
import pytest
from pathlib import Path


def test_event_files_exist():
    """Verify all three event files exist"""
    base_path = Path(__file__).parent.parent
    
    events_json = base_path / 'assets' / 'json' / 'events.json'
    antarctica_json = base_path / 'assets' / 'json' / 'events.antarctica.json'
    atlantis_json = base_path / 'assets' / 'json' / 'events.atlantis.json'
    
    assert events_json.exists(), "events.json missing"
    assert antarctica_json.exists(), "events.antarctica.json missing"
    assert atlantis_json.exists(), "events.atlantis.json missing"


def test_events_json_no_antarctica():
    """Verify events.json contains no Antarctica events"""
    base_path = Path(__file__).parent.parent
    events_path = base_path / 'assets' / 'json' / 'events.json'
    
    with open(events_path, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    # Check no events have Antarctica-related locations
    antarctica_events = []
    for event in events:
        location = event.get('location', {})
        lat = location.get('lat', 0)
        
        # Antarctica is below -60 latitude
        if lat < -60:
            antarctica_events.append({
                'id': event.get('id'),
                'lat': lat,
                'title': event.get('title', '')[:50]
            })
        
        # Check source field
        source = event.get('source', '')
        if 'antarctica' in source.lower():
            antarctica_events.append({
                'id': event.get('id'),
                'source': source,
                'title': event.get('title', '')[:50]
            })
    
    assert len(antarctica_events) == 0, \
        f"Found {len(antarctica_events)} Antarctica events in events.json: {antarctica_events}"


def test_antarctica_events_structure():
    """Verify Antarctica events have correct structure and theme"""
    base_path = Path(__file__).parent.parent
    antarctica_path = base_path / 'assets' / 'json' / 'events.antarctica.json'
    
    with open(antarctica_path, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    assert len(events) > 0, "Antarctica should have showcase events"
    
    errors = []
    for event in events:
        event_id = event.get('id', 'unknown')
        
        # Verify location is in Antarctica
        location = event.get('location', {})
        lat = location.get('lat', 0)
        if not (lat < -60):
            errors.append(f"Event {event_id} not in Antarctica region (lat={lat})")
        
        # Verify source tag
        source = event.get('source', '')
        if source not in ['antarctica', 'demo']:
            errors.append(f"Event {event_id} has wrong source: {source}")
        
        # Verify has setup/fork hints in description or title
        text = (event.get('title', '') + event.get('description', '')).lower()
        has_setup_info = any(keyword in text for keyword in [
            'fork', 'clone', 'setup', 'github', 'repository', 'your own'
        ])
        if not has_setup_info:
            errors.append(f"Event {event_id} should contain setup hints")
    
    assert len(errors) == 0, f"Antarctica events validation failed:\n" + "\n".join(errors)


def test_atlantis_events_structure():
    """Verify Atlantis events have correct structure and humor"""
    base_path = Path(__file__).parent.parent
    atlantis_path = base_path / 'assets' / 'json' / 'events.atlantis.json'
    
    with open(atlantis_path, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    assert len(events) > 0, "Atlantis should have 404 events"
    
    errors = []
    for event in events:
        event_id = event.get('id', 'unknown')
        
        # Verify location is near Mid-Atlantic Ridge
        location = event.get('location', {})
        lat = location.get('lat', 0)
        lon = location.get('lon', 0)
        
        # Atlantis coordinates: ~31°N, 24°W
        if not (20 < lat < 40):
            errors.append(f"Event {event_id} not near Atlantis latitude (lat={lat})")
        if not (-30 < lon < -20):
            errors.append(f"Event {event_id} not near Atlantis longitude (lon={lon})")
        
        # Verify source tag
        source = event.get('source', '')
        if source != 'atlantis':
            errors.append(f"Event {event_id} should have atlantis source, got: {source}")
        
        # Verify has humor and hints
        text = (event.get('title', '') + event.get('description', '')).lower()
        has_atlantis_theme = any(keyword in text for keyword in [
            'atlantis', 'sunken', 'underwater', 'poseidon', 'plato', 'sunk', 'waves'
        ])
        has_hints = any(keyword in text for keyword in [
            'fork', 'github', '/', 'south pole', 'antarctica', 'dry land'
        ])
        
        if not (has_atlantis_theme or has_hints):
            errors.append(f"Event {event_id} should have Atlantis theme or setup hints")
    
    assert len(errors) == 0, f"Atlantis events validation failed:\n" + "\n".join(errors)


def test_site_generator_loads_all_events():
    """Verify site generator loads all three event sources"""
    base_path = Path(__file__).parent.parent
    
    # Import site generator
    import sys
    sys.path.insert(0, str(base_path / 'src'))
    from modules.site_generator import SiteGenerator
    
    generator = SiteGenerator(base_path)
    
    # Load config
    configs = generator.load_all_configs()
    primary_config = configs[0] if configs else {}
    
    # Load all events
    all_events = generator.load_all_events(primary_config)
    
    # Check we have events from all three sources
    sources = set(event.get('source', '') for event in all_events)
    
    # Should contain at least: real events, antarctica, atlantis
    assert 'antarctica' in sources or 'demo' in sources, \
        f"Missing Antarctica events. Found sources: {sources}"
    assert 'atlantis' in sources, \
        f"Missing Atlantis events. Found sources: {sources}"
    
    # Verify total count is reasonable (>10 events from all sources combined)
    assert len(all_events) > 10, \
        f"Expected >10 events, got {len(all_events)}"
    
    # Count events by source
    source_counts = {}
    for event in all_events:
        source = event.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\nEvent counts by source: {source_counts}")


def test_no_duplicate_events():
    """Verify no duplicate events across the three files"""
    base_path = Path(__file__).parent.parent
    
    events_json = base_path / 'assets' / 'json' / 'events.json'
    antarctica_json = base_path / 'assets' / 'json' / 'events.antarctica.json'
    atlantis_json = base_path / 'assets' / 'json' / 'events.atlantis.json'
    
    all_event_ids = set()
    duplicates = []
    
    for file_path in [events_json, antarctica_json, atlantis_json]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        events = data.get('events', [])
        for event in events:
            event_id = event.get('id')
            if event_id in all_event_ids:
                duplicates.append((event_id, file_path.name))
            all_event_ids.add(event_id)
    
    assert len(duplicates) == 0, \
        f"Found duplicate event IDs: {duplicates}"


def test_config_has_regions():
    """Verify config.json has antarctica and real regions configured"""
    base_path = Path(__file__).parent.parent
    config_path = base_path / 'config.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    regions = config.get('regions', {})
    
    # Should have antarctica region
    assert 'antarctica' in regions, "Missing antarctica region in config"
    
    # Should have at least one real region
    real_regions = [r for r in regions.keys() if r != 'antarctica']
    assert len(real_regions) > 0, "Should have at least one real region"
    
    # Antarctica should have South Pole coordinates
    antarctica = regions['antarctica']
    center = antarctica.get('center', {})
    assert center.get('lat') == -90.0, "Antarctica should be at South Pole"


def test_config_data_section():
    """Verify config.json data section defines all three content types"""
    base_path = Path(__file__).parent.parent
    config_path = base_path / 'config.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check that data section exists
    assert 'data' in config, "Missing data section in config"
    data = config['data']
    
    # Check that sources are defined for all three content types:
    # Showcase (real), Error-handling (antarctica), Production (atlantis)
    sources = data.get('sources', {})
    assert 'real' in sources, "Missing real source in config.data.sources"
    assert 'antarctica' in sources, "Missing antarctica source in config.data.sources"
    assert 'atlantis' in sources, "Missing atlantis source in config.data.sources"


if __name__ == '__main__':
    # Run tests with verbose output
    import sys
    sys.exit(pytest.main([__file__, '-v']))
