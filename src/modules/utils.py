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


def load_rejected_events(base_path):
    """Load rejected events from rejected_events.json"""
    rejected_path = base_path / 'data' / 'rejected_events.json'
    try:
        with open(rejected_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create empty rejected events file if it doesn't exist
        rejected_data = {'rejected_events': [], 'last_updated': datetime.now().isoformat()}
        save_rejected_events(base_path, rejected_data)
        return rejected_data


def save_rejected_events(base_path, rejected_data):
    """Save rejected events to rejected_events.json"""
    rejected_path = base_path / 'data' / 'rejected_events.json'
    rejected_data['last_updated'] = datetime.now().isoformat()
    with open(rejected_path, 'w') as f:
        json.dump(rejected_data, f, indent=2)


def is_event_rejected(rejected_events, event_title, event_source):
    """
    Check if an event with given title and source has been rejected before.
    
    Args:
        rejected_events: List of rejected event records
        event_title: Title of the event to check
        event_source: Source of the event to check
        
    Returns:
        True if event matches a rejected record, False otherwise
    """
    title_lower = event_title.lower().strip()
    source_lower = event_source.lower().strip()
    
    for rejected in rejected_events:
        rejected_title = rejected.get('title', '').lower().strip()
        rejected_source = rejected.get('source', '').lower().strip()
        
        # Match if both title and source match
        if rejected_title == title_lower and rejected_source == source_lower:
            return True
    
    return False


def add_rejected_event(base_path, event_title, event_source):
    """
    Add an event to the rejected events list.
    
    Args:
        base_path: Root path of the repository
        event_title: Title of the event to reject
        event_source: Source of the event to reject
    """
    rejected_data = load_rejected_events(base_path)
    
    # Check if already in rejected list
    if is_event_rejected(rejected_data['rejected_events'], event_title, event_source):
        return  # Already rejected
    
    # Add to rejected list
    rejected_data['rejected_events'].append({
        'title': event_title,
        'source': event_source,
        'rejected_at': datetime.now().isoformat()
    })
    
    save_rejected_events(base_path, rejected_data)


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
    
    # Simplified sunrise calculation
    # For production, use a library like astral or suntime
    now = datetime.now()
    
    # Approximate sunrise at ~6 AM local time
    # This is a simplification; real implementation should use proper solar calculations
    tomorrow = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour >= 6:
        tomorrow += timedelta(days=1)
    
    return tomorrow


def archive_old_events(base_path):
    """
    Archive events that have already passed
    Moves them from published to archived status
    Returns number of events archived
    """
    from datetime import datetime
    
    events_data = load_events(base_path)
    events = events_data.get('events', [])
    
    now = datetime.now()
    archived_count = 0
    active_events = []
    archived_events = []
    
    for event in events:
        # Parse event end time (or start time if no end time)
        event_time_str = event.get('end_time') or event.get('start_time')
        if not event_time_str:
            active_events.append(event)
            continue
        
        try:
            event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
            # Remove timezone info for comparison if present
            if event_time.tzinfo:
                event_time = event_time.replace(tzinfo=None)
            
            if event_time < now:
                # Event has passed - archive it
                event['status'] = 'archived'
                event['archived_at'] = now.isoformat()
                archived_events.append(event)
                archived_count += 1
            else:
                active_events.append(event)
        except (ValueError, AttributeError):
            # Keep event if we can't parse the time
            active_events.append(event)
    
    # Save active events
    events_data['events'] = active_events
    save_events(base_path, events_data)
    
    # Save archived events if there are any
    if archived_events:
        archive_path = base_path / 'static' / 'archived_events.json'
        try:
            with open(archive_path, 'r') as f:
                archive_data = json.load(f)
        except FileNotFoundError:
            archive_data = {'archived_events': []}
        
        archive_data['archived_events'].extend(archived_events)
        archive_data['last_updated'] = now.isoformat()
        
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)
    
    return archived_count


def filter_events_by_time(events, config):
    """
    Filter events based on time rules:
    - Remove events that have already passed
    - Only show events until next sunrise
    Returns filtered list of events
    """
    from datetime import datetime
    
    now = datetime.now()
    next_sunrise = get_next_sunrise(config['map']['default_center']['lat'], 
                                     config['map']['default_center']['lon'])
    
    filtered_events = []
    
    for event in events:
        event_start_str = event.get('start_time')
        if not event_start_str:
            continue
        
        try:
            event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
            # Remove timezone info for comparison if present
            if event_start.tzinfo:
                event_start = event_start.replace(tzinfo=None)
            
            # Event must be in the future
            if event_start <= now:
                continue
            
            # Event must be before next sunrise
            if event_start <= next_sunrise:
                filtered_events.append(event)
        except (ValueError, AttributeError):
            # Skip events with invalid time format
            continue
    
    return filtered_events


def backup_published_event(base_path, event):
    """
    Backup a single published event to data/backups/events/ folder.
    Each event is saved as a separate JSON file named by event ID.
    
    Args:
        base_path: Root path of the repository
        event: Event dictionary to backup
        
    Returns:
        Path to the backup file created
    """
    import os
    
    # Create backups directory structure
    backups_dir = base_path / 'data' / 'backups' / 'events'
    backups_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from event ID and timestamp
    event_id = event.get('id', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{event_id}_{timestamp}.json"
    
    backup_path = backups_dir / filename
    
    # Add backup metadata
    backup_data = {
        'backed_up_at': datetime.now().isoformat(),
        'event': event
    }
    
    # Save backup
    with open(backup_path, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    return backup_path


def load_historical_events(base_path):
    """
    Load all historical events from data/backups/events/ folder.
    Returns a list of event dictionaries from all backup files.
    
    This is used by the scraper to check against historical data
    and prevent re-scraping events that were already published.
    
    Args:
        base_path: Root path of the repository
        
    Returns:
        List of event dictionaries
    """
    backups_dir = base_path / 'data' / 'backups' / 'events'
    historical_events = []
    
    if not backups_dir.exists():
        return historical_events
    
    # Load all backup files
    for backup_file in backups_dir.glob('*.json'):
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
                # Extract the event from backup metadata
                event = backup_data.get('event')
                if event:
                    historical_events.append(event)
        except (json.JSONDecodeError, IOError) as e:
            # Skip corrupted or unreadable backup files
            print(f"Warning: Could not load backup file {backup_file}: {e}")
            continue
    
    return historical_events


def update_events_in_html(base_path):
    """
    Update the EVENTS array in index.html with current events from events.json.
    This is called automatically after approving/publishing events.
    
    Uses regex to replace 'const EVENTS = [...];' with current event data.
    
    Args:
        base_path: Root path of the repository
        
    Returns:
        True if successful, False otherwise
    """
    import re
    
    try:
        # Load current events
        events_data = load_events(base_path)
        events = events_data.get('events', [])
        
        # Read index.html
        index_path = base_path / 'static' / 'index.html'
        if not index_path.exists():
            print(f"Error: {index_path} does not exist")
            return False
        
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert events to JSON string with proper formatting
        # Use ensure_ascii=False to handle unicode characters properly
        events_json = json.dumps(events, indent=2, ensure_ascii=False)
        
        # Replace EVENTS array using regex
        # Match: const EVENTS = [...]; (with any content between brackets)
        pattern = r'const EVENTS = \[.*?\];'
        replacement = f'const EVENTS = {events_json};'
        
        # Use DOTALL flag to match across newlines
        updated_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        
        # Verify the replacement worked
        if updated_html == html_content:
            print("Warning: EVENTS array not found or not replaced in index.html")
            return False
        
        # Write updated HTML
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"✓ Updated {len(events)} event(s) in index.html")
        return True
        
    except Exception as e:
        import traceback
        print(f"Error updating events in HTML: {e}")
        traceback.print_exc()
        return False
