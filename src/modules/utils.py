"""Utility functions for the event manager"""

import json
import os
from pathlib import Path
from datetime import datetime


def is_ci():
    """
    Detect if running in CI environment.
    
    Checks for common CI environment variables set by:
    - GitHub Actions (GITHUB_ACTIONS, CI)
    - GitLab CI (GITLAB_CI, CI)
    - Travis CI (TRAVIS, CI)
    - CircleCI (CIRCLECI, CI)
    - Jenkins (JENKINS_HOME, JENKINS_URL)
    - Bitbucket Pipelines (BITBUCKET_BUILD_NUMBER)
    - Azure Pipelines (TF_BUILD)
    - AWS CodeBuild (CODEBUILD_BUILD_ID)
    
    Returns:
        bool: True if running in CI, False otherwise
    """
    ci_indicators = [
        'CI',                          # Generic CI flag (set by most CI systems)
        'GITHUB_ACTIONS',              # GitHub Actions
        'GITLAB_CI',                   # GitLab CI
        'TRAVIS',                      # Travis CI
        'CIRCLECI',                    # CircleCI
        'JENKINS_HOME', 'JENKINS_URL', # Jenkins
        'BITBUCKET_BUILD_NUMBER',      # Bitbucket Pipelines
        'TF_BUILD',                    # Azure Pipelines
        'CODEBUILD_BUILD_ID'           # AWS CodeBuild
    ]
    
    return any(os.environ.get(var) for var in ci_indicators)


def is_production():
    """
    Detect if running in production environment.
    
    Checks for production indicators from:
    - Explicit ENVIRONMENT=production (preferred for Python apps)
    - Legacy NODE_ENV=production (backward compatibility)
    - Vercel (VERCEL_ENV=production)
    - Netlify (NETLIFY=true + CONTEXT=production)
    - Heroku (DYNO environment variable presence)
    - Railway (RAILWAY_ENVIRONMENT=production)
    - Render (RENDER=true + IS_PULL_REQUEST!=true)
    - Fly.io (FLY_APP_NAME presence)
    - Google Cloud Run (K_SERVICE presence)
    - AWS (AWS_EXECUTION_ENV presence + not in Lambda)
    
    Returns:
        bool: True if in production, False otherwise
    """
    # Explicit production setting (check both new and legacy)
    env = os.environ.get('ENVIRONMENT') or os.environ.get('NODE_ENV')
    if env == 'production':
        return True
    
    # Vercel production
    if os.environ.get('VERCEL_ENV') == 'production':
        return True
    
    # Netlify production
    if os.environ.get('NETLIFY') == 'true' and os.environ.get('CONTEXT') == 'production':
        return True
    
    # Heroku (presence of DYNO indicates production deployment)
    if os.environ.get('DYNO'):
        return True
    
    # Railway production
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        return True
    
    # Render production (RENDER=true and not a PR preview)
    if os.environ.get('RENDER') == 'true' and os.environ.get('IS_PULL_REQUEST') != 'true':
        return True
    
    # Fly.io (presence of FLY_APP_NAME indicates production)
    if os.environ.get('FLY_APP_NAME'):
        return True
    
    # Google Cloud Run
    if os.environ.get('K_SERVICE'):
        return True
    
    # AWS (but not Lambda, as Lambda might be dev/test)
    if os.environ.get('AWS_EXECUTION_ENV') and not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        return True
    
    return False


def is_development():
    """
    Detect if running in local development environment.
    
    Development is the default mode when NOT in CI and NOT in production.
    This is the typical environment for developers working locally.
    
    Returns:
        bool: True if in development (local), False otherwise
    """
    return not is_production() and not is_ci()


def load_config(base_path):
    """
    Load data/config.json with environment override support.
    
    Environment can be:
    1. Explicitly set in data/config.json ("development" or "production") - bypasses auto-detection
    2. Set to "auto" - uses automatic environment detection (default)
    
    Auto-detection checks os.environ for:
    - **Development (Local)**: debug=true, data.source="both" (real+demo), watermark="DEV"
    - **CI/Production**: debug=false, data.source="real", watermark="PRODUCTION"
    
    Args:
        base_path: Root path of the repository
        
    Returns:
        dict: Configuration dictionary with environment-specific overrides applied
    """
    # SSG Standard: config.json at root level (like Hugo's config.toml, Jekyll's _config.yml)
    config_path = base_path / 'config.json'
    
    # Load base configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check for explicit environment override
    env_override = config.get('environment', 'auto')
    
    if env_override in ('development', 'production'):
        # Explicit override - use it directly
        env_is_dev = (env_override == 'development')
        env_name = env_override
        print(f"🎯 Environment forced to: {env_name} (from data/config.json)")
    else:
        # Auto-detection mode
        env_is_dev = is_development()
        env_is_ci = is_ci()
        
        if env_is_dev:
            env_name = 'development'
        elif env_is_ci:
            env_name = 'ci'
        else:
            env_name = 'production'
        
        print(f"🚀 Environment auto-detected: {env_name}")
    
    # Apply environment-specific overrides
    # These values are HARDCODED based on environment - not read from config.json
    # This prevents confusion from config.json values that would be silently ignored
    if env_is_dev:
        # Development mode: Optimized for local testing and debugging
        config['debug'] = True
        config['data']['source'] = 'both'  # Include demo events for testing
        
        # Create watermark field if it doesn't exist
        if 'watermark' not in config:
            config['watermark'] = {}
        config['watermark']['text'] = 'DEV'
        
        config['app']['environment'] = 'development'
        # Add [DEV] suffix if not already present
        if '[DEV]' not in config['app']['name']:
            config['app']['name'] = config['app']['name'] + ' [DEV]'
        
        # Create performance fields if they don't exist
        if 'performance' not in config:
            config['performance'] = {}
        config['performance']['cache_enabled'] = False  # Fresh data each time
        config['performance']['prefetch_events'] = False  # On-demand loading
    else:
        # Production/CI mode
        config['debug'] = False
        config['data']['source'] = 'real'  # Real events only
        
        # Create watermark field if it doesn't exist
        if 'watermark' not in config:
            config['watermark'] = {}
        config['watermark']['text'] = 'PRODUCTION'
        
        config['app']['environment'] = env_name
        # Remove [DEV] suffix if present
        config['app']['name'] = config['app']['name'].replace(' [DEV]', '')
        
        # Create performance fields if they don't exist
        if 'performance' not in config:
            config['performance'] = {}
        config['performance']['cache_enabled'] = True  # Enable caching
        config['performance']['prefetch_events'] = True  # Preload for speed
    
    print(f"   → debug: {config['debug']}, data source: {config['data']['source']}")
    
    return config


def load_events(base_path):
    """Load published events from events.json"""
    events_path = base_path / 'event-data' / 'events.json'
    with open(events_path, 'r') as f:
        return json.load(f)


def save_events(base_path, events_data):
    """Save published events to events.json"""
    events_path = base_path / 'event-data' / 'events.json'
    events_data['last_updated'] = datetime.now().isoformat()
    with open(events_path, 'w') as f:
        json.dump(events_data, f, indent=2)


def update_pending_count_in_events(base_path):
    """
    Update the pending_count field in events.json
    This allows the frontend to read pending count from the same file it already loads
    
    Note: This does NOT update the last_updated timestamp since it's only metadata,
    not a change to the actual events data.
    """
    pending_data = load_pending_events(base_path)
    events_data = load_events(base_path)
    
    # Add or update pending_count field
    events_data['pending_count'] = len(pending_data.get('pending_events', []))
    
    # Save back to events.json WITHOUT updating timestamp
    events_path = base_path / 'event-data' / 'events.json'
    with open(events_path, 'w') as f:
        json.dump(events_data, f, indent=2)


def load_pending_events(base_path):
    """Load pending events from pending_events.json"""
    pending_path = base_path / 'event-data' / 'pending_events.json'
    with open(pending_path, 'r') as f:
        return json.load(f)


def save_pending_events(base_path, pending_data):
    """Save pending events to pending_events.json"""
    pending_path = base_path / 'event-data' / 'pending_events.json'
    pending_data['last_scraped'] = datetime.now().isoformat()
    with open(pending_path, 'w') as f:
        json.dump(pending_data, f, indent=2)


def load_rejected_events(base_path):
    """Load rejected events from rejected_events.json"""
    rejected_path = base_path / 'event-data' / 'rejected_events.json'
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
    rejected_path = base_path / 'event-data' / 'rejected_events.json'
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
        archive_path = base_path / 'target' / 'archived_events.json'
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
    Backup a single published event to data/old/ folder.
    Each event is saved as a separate JSON file named by event ID.
    
    Args:
        base_path: Root path of the repository
        event: Event dictionary to backup
        
    Returns:
        Path to the backup file created
    """
    import os
    
    # Create old directory structure
    old_dir = base_path / 'event-data' / 'old'
    old_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from event ID and timestamp
    event_id = event.get('id', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{event_id}_{timestamp}.json"
    
    backup_path = old_dir / filename
    
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
    Load all historical events from data/old/ folder.
    Returns a list of event dictionaries from all backup files.
    
    This is used by the scraper to check against historical data
    and prevent re-scraping events that were already published.
    
    Args:
        base_path: Root path of the repository
        
    Returns:
        List of event dictionaries
    """
    old_dir = base_path / 'event-data' / 'old'
    historical_events = []
    
    if not old_dir.exists():
        return historical_events
    
    # Load all backup files
    for backup_file in old_dir.glob('*.json'):
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
        index_path = base_path / 'target' / 'index.html'
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
