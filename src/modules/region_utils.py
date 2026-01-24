"""
Region Utilities Module

Helper functions for multi-region support:
- Get region configuration
- Validate regions
- Calculate distances (Haversine)
- Check if point is in bounding box

All regions share the same events.json data file.
URL path just centers map on different locations with region-specific settings.
"""

import json
import math
from pathlib import Path
from typing import Dict, Optional, List


def load_config(base_path: Path) -> Dict:
    """Load configuration from config.json"""
    config_path = base_path / "config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {e}")


def get_all_regions(base_path: Path) -> Dict:
    """
    Get all available regions from configuration.
    
    Args:
        base_path: Base path of the project
        
    Returns:
        Dictionary of regions {region_id: region_config}
    """
    config = load_config(base_path)
    
    if 'regions' not in config:
        # Fallback: return empty dict if no regions configured
        return {}
    
    return config['regions']


def get_default_region(base_path: Path) -> str:
    """
    Get the default region from configuration.
    
    Args:
        base_path: Base path of the project
        
    Returns:
        Default region ID (e.g., 'hof')
    """
    config = load_config(base_path)
    
    if 'defaultRegion' in config:
        return config['defaultRegion']
    
    # Fallback: use first region or 'hof'
    if 'regions' in config and config['regions']:
        return list(config['regions'].keys())[0]
    
    return 'hof'


def validate_region(region_name: str, base_path: Path) -> bool:
    """
    Check if a region exists in configuration.
    
    Args:
        region_name: Region ID to validate (e.g., 'hof', 'nbg')
        base_path: Base path of the project
        
    Returns:
        True if region exists, False otherwise
    """
    regions = get_all_regions(base_path)
    return region_name in regions


def get_region_config(region_name: str, base_path: Path) -> Optional[Dict]:
    """
    Get configuration for a specific region.
    
    Args:
        region_name: Region ID (e.g., 'hof', 'nbg')
        base_path: Base path of the project
        
    Returns:
        Region configuration dictionary, or None if not found
    """
    regions = get_all_regions(base_path)
    return regions.get(region_name)


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate distance in kilometers between two points on Earth using Haversine formula.
    
    Args:
        lon1: Longitude of first point
        lat1: Latitude of first point
        lon2: Longitude of second point
        lat2: Latitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return c * r


def is_point_in_bounding_box(lat: float, lon: float, bbox: Dict) -> bool:
    """
    Check if a point (lat, lon) is inside a bounding box.
    
    Args:
        lat: Latitude of the point
        lon: Longitude of the point
        bbox: Bounding box dictionary with keys: north, south, east, west
        
    Returns:
        True if point is inside bounding box, False otherwise
    """
    return (
        bbox['south'] <= lat <= bbox['north'] and
        bbox['west'] <= lon <= bbox['east']
    )


def filter_events_by_region(events: List[Dict], region_name: str, base_path: Path) -> List[Dict]:
    """
    Filter events by region bounding box.
    
    Note: This is optional - you can show all events regardless of region.
    Use this if you want to limit events to those within the region's bounding box.
    
    Args:
        events: List of event dictionaries
        region_name: Region ID
        base_path: Base path of the project
        
    Returns:
        Filtered list of events within region's bounding box
    """
    region_config = get_region_config(region_name, base_path)
    
    if not region_config or 'boundingBox' not in region_config:
        # No bounding box defined, return all events
        return events
    
    bbox = region_config['boundingBox']
    filtered = []
    
    for event in events:
        if 'location' not in event:
            continue
        
        location = event['location']
        if 'lat' not in location or 'lon' not in location:
            continue
        
        lat = location['lat']
        lon = location['lon']
        
        if is_point_in_bounding_box(lat, lon, bbox):
            filtered.append(event)
    
    return filtered


def get_custom_filters_for_region(region_name: str, base_path: Path) -> List[Dict]:
    """
    Get custom filter presets for a region (e.g., neighborhoods, districts).
    
    Args:
        region_name: Region ID
        base_path: Base path of the project
        
    Returns:
        List of custom filter dictionaries
    """
    region_config = get_region_config(region_name, base_path)
    
    if not region_config:
        return []
    
    return region_config.get('customFilters', [])


def get_region_center(region_name: str, base_path: Path) -> Optional[Dict]:
    """
    Get map center coordinates for a region.
    
    Args:
        region_name: Region ID
        base_path: Base path of the project
        
    Returns:
        Dictionary with 'lat' and 'lng' keys, or None if not found
    """
    region_config = get_region_config(region_name, base_path)
    
    if not region_config:
        return None
    
    return region_config.get('center')


def get_region_zoom(region_name: str, base_path: Path) -> Optional[int]:
    """
    Get default zoom level for a region.
    
    Args:
        region_name: Region ID
        base_path: Base path of the project
        
    Returns:
        Zoom level (integer), or None if not found
    """
    region_config = get_region_config(region_name, base_path)
    
    if not region_config:
        return None
    
    return region_config.get('zoom')
