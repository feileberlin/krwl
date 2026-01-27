"""
RSS Feed Generator Module

Generates per-region RSS 2.0 feeds showing events until next sunrise.
Mirrors the frontend's "sunrise filtering" behavior.

Functions:
- generate_sunrise_feeds() - Generate RSS feeds for all regions
- create_rss_feed() - Create RSS 2.0 XML string for events
"""

import logging
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configure module logger
logger = logging.getLogger(__name__)


def _parse_event_timestamp(event: Dict) -> datetime:
    """
    Parse event start_time to datetime object.
    
    Handles ISO format timestamps with or without 'Z' suffix.
    Removes timezone info for naive datetime comparison.
    
    Args:
        event: Event dictionary containing 'start_time' field
        
    Returns:
        Timezone-naive datetime object, or None if parsing fails
        
    Raises:
        ValueError: If timestamp format is invalid
        AttributeError: If start_time field is missing
    """
    start_str = event.get('start_time')
    if not start_str:
        raise AttributeError("Event missing start_time field")
    
    # Handle ISO format with or without 'Z' suffix
    if start_str.endswith('Z'):
        start_str = start_str[:-1] + '+00:00'
    
    start_dt = datetime.fromisoformat(start_str)
    
    # Remove timezone info for comparison if present
    if start_dt.tzinfo:
        start_dt = start_dt.replace(tzinfo=None)
    
    return start_dt


def generate_sunrise_feeds(base_path: Path) -> None:
    """
    Generate RSS feeds with events until next sunrise for each region.
    
    Process:
    1. Load all regions from config
    2. Load all published events
    3. For each region:
       - Calculate next sunrise based on region center coordinates
       - Filter events occurring between now and next sunrise
       - Generate RSS 2.0 XML feed
       - Save to assets/feeds/{region_id}-til-sunrise.xml
    
    Args:
        base_path: Base path of the project
        
    Returns:
        None (prints status messages)
    """
    from .utils import load_config, load_events, get_next_sunrise
    from .region_utils import get_all_regions
    
    print("\n📡 Generating RSS feeds...")
    
    # Load configuration and events
    config = load_config(base_path)
    events_data = load_events(base_path)
    all_events = events_data.get('events', [])
    
    # Load regions
    regions = get_all_regions(base_path)
    
    if not regions:
        print("⚠️  No regions found in configuration")
        return
    
    # Create feeds directory if it doesn't exist
    feeds_dir = base_path / 'assets' / 'feeds'
    feeds_dir.mkdir(parents=True, exist_ok=True)
    
    # Get base URL from config
    base_url = config.get('app', {}).get('url', 'https://krwl.in')
    
    # Generate feed for each region
    for region_id, region_config in regions.items():
        try:
            # Get region center coordinates
            center = region_config.get('center', {})
            lat = center.get('lat')
            lon = center.get('lng')  # Note: config uses 'lng', not 'lon'
            
            if lat is None or lon is None:
                logger.warning(f"Skipping region {region_id}: missing coordinates")
                print(f"  ⚠️  Skipping region {region_id}: missing coordinates")
                continue
            
            # Calculate next sunrise for this region
            next_sunrise = get_next_sunrise(lat, lon)
            
            # Filter events until next sunrise
            now = datetime.now()
            sunrise_events = []
            
            for event in all_events:
                # Skip if no start_time
                if 'start_time' not in event or not event['start_time']:
                    continue
                
                try:
                    # Parse event start time using helper function
                    event_start = _parse_event_timestamp(event)
                    
                    # Filter: events starting between now and next sunrise
                    if now < event_start <= next_sunrise:
                        sunrise_events.append(event)
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Skipping event {event.get('id', 'unknown')}: invalid timestamp - {e}")
                    continue
            
            # Deduplicate events by ID (keep first occurrence)
            seen_ids = set()
            deduplicated_events = []
            for event in sunrise_events:
                event_id = event.get('id')
                if event_id and event_id not in seen_ids:
                    seen_ids.add(event_id)
                    deduplicated_events.append(event)
            sunrise_events = deduplicated_events
            
            # Generate RSS feed
            region_display_name = region_config.get('displayName', region_id)
            feed_title = f"Events Until Sunrise - {region_display_name}"
            feed_description = f"Community events in {region_display_name} happening until the next sunrise"
            
            rss_xml = create_rss_feed(
                title=feed_title,
                description=feed_description,
                events=sunrise_events,
                region_id=region_id,
                base_url=base_url
            )
            
            # Save feed to file
            feed_filename = f"{region_id}-til-sunrise.xml"
            feed_path = feeds_dir / feed_filename
            
            with open(feed_path, 'w', encoding='utf-8') as f:
                f.write(rss_xml)
            
            print(f"  ✓ Generated feed: {feed_filename} ({len(sunrise_events)} events)")
            
        except Exception as e:
            logger.error(f"Failed to generate feed for region {region_id}: {e}")
            print(f"  ⚠️  Failed to generate feed for {region_id}: {e}")
            continue
    
    print("✓ RSS feeds generated")


def create_rss_feed(title: str, description: str, events: List[Dict], 
                    region_id: str, base_url: str) -> str:
    """
    Create RSS 2.0 XML string for events.
    
    Args:
        title: Feed title
        description: Feed description
        events: List of event dictionaries
        region_id: Region identifier (e.g., 'hof', 'nbg')
        base_url: Base URL for links (e.g., 'https://krwl.in')
        
    Returns:
        Pretty-printed RSS 2.0 XML string
    """
    # Create RSS root element
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    # Create channel element
    channel = ET.SubElement(rss, 'channel')
    
    # Channel metadata
    ET.SubElement(channel, 'title').text = title
    ET.SubElement(channel, 'link').text = f"{base_url}/{region_id}"
    ET.SubElement(channel, 'description').text = description
    ET.SubElement(channel, 'language').text = 'de'
    ET.SubElement(channel, 'lastBuildDate').text = _format_rfc822_date(datetime.now())
    
    # Self-reference link for feed discovery
    atom_link = ET.SubElement(channel, 'atom:link')
    atom_link.set('href', f"{base_url}/assets/feeds/{region_id}-til-sunrise.xml")
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    # Add events as items
    for event in events:
        item = ET.SubElement(channel, 'item')
        
        # Title
        event_title = event.get('title', 'Untitled Event')
        ET.SubElement(item, 'title').text = event_title
        
        # Link - use event URL or fallback to region page
        event_url = event.get('url') or event.get('source') or f"{base_url}/{region_id}"
        ET.SubElement(item, 'link').text = event_url
        
        # GUID (using event ID)
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'false')
        guid.text = event.get('id', event_title)
        
        # Description - formatted with location and time
        description_parts = []
        
        # Add event description/teaser
        if event.get('description'):
            description_parts.append(event['description'])
        elif event.get('teaser'):
            description_parts.append(event['teaser'])
        
        # Add location
        if 'location' in event and event['location']:
            location = event['location']
            location_name = location.get('name', '')
            location_address = location.get('address', '')
            
            if location_name:
                description_parts.append(f"\n\nLocation: {location_name}")
            if location_address:
                description_parts.append(f"Address: {location_address}")
        
        # Add time
        if event.get('start_time'):
            try:
                start_dt = _parse_event_timestamp(event)
                time_str = start_dt.strftime('%A, %B %d, %Y at %H:%M')
                description_parts.append(f"\n\nTime: {time_str}")
            except (ValueError, AttributeError):
                # Silently skip if timestamp parsing fails - event still included without time
                pass
        
        description_text = '\n'.join(description_parts)
        ET.SubElement(item, 'description').text = description_text
        
        # PubDate - event start time in RFC 822 format
        if event.get('start_time'):
            try:
                start_dt = _parse_event_timestamp(event)
                ET.SubElement(item, 'pubDate').text = _format_rfc822_date(start_dt)
            except (ValueError, AttributeError):
                # Silently skip if timestamp parsing fails - item still valid without pubDate
                pass
        
        # Category
        if event.get('category'):
            ET.SubElement(item, 'category').text = event['category']
    
    # Convert to string and pretty-print
    xml_string = ET.tostring(rss, encoding='unicode')
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    return '\n'.join(lines)


def _format_rfc822_date(dt: datetime) -> str:
    """
    Format datetime as RFC 822 date string for RSS.
    
    Args:
        dt: Datetime object (timezone-naive, assumed local time)
        
    Returns:
        RFC 822 formatted date string (e.g., 'Mon, 27 Jan 2025 14:30:00 +0100')
    """
    # RFC 822 format: Day, DD Mon YYYY HH:MM:SS +ZONE
    # Using strftime with manual timezone (assuming CET/CEST for Germany)
    import time
    
    # Get timezone offset
    if time.daylight:
        offset_sec = time.altzone
    else:
        offset_sec = time.timezone
    
    # Convert to +/-HHMM format
    offset_hours = -offset_sec // 3600
    offset_mins = abs(-offset_sec % 3600) // 60
    tz_str = f"{offset_hours:+03d}{offset_mins:02d}"
    
    # Format date
    return dt.strftime(f'%a, %d %b %Y %H:%M:%S {tz_str}')
