"""Utility functions for the event manager"""

import json
from pathlib import Path
from datetime import datetime


def load_config(base_path):
    """Load configuration from config.json"""
    config_path = base_path / 'config' / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)


def load_events(base_path):
    """Load published events from events.json"""
    events_path = base_path / 'data' / 'events.json'
    with open(events_path, 'r') as f:
        return json.load(f)


def save_events(base_path, events_data):
    """Save published events to events.json"""
    events_path = base_path / 'data' / 'events.json'
    events_data['last_updated'] = datetime.now().isoformat()
    with open(events_path, 'w') as f:
        json.dump(events_data, f, indent=2)


def load_pending_events(base_path):
    """Load pending events from pending_events.json"""
    pending_path = base_path / 'data' / 'pending_events.json'
    with open(pending_path, 'r') as f:
        return json.load(f)


def save_pending_events(base_path, pending_data):
    """Save pending events to pending_events.json"""
    pending_path = base_path / 'data' / 'pending_events.json'
    pending_data['last_scraped'] = datetime.now().isoformat()
    with open(pending_path, 'w') as f:
        json.dump(pending_data, f, indent=2)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth radius in kilometers
    R = 6371.0
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def get_next_sunrise(lat, lon):
    """
    Calculate next sunrise time for given coordinates
    Returns datetime object
    """
    from datetime import datetime, timedelta
    import math
    
    # Simplified sunrise calculation
    # For production, use a library like astral or suntime
    now = datetime.now()
    
    # Approximate sunrise at ~6 AM local time
    # This is a simplification; real implementation should use proper solar calculations
    tomorrow = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour >= 6:
        tomorrow += timedelta(days=1)
    
    return tomorrow
