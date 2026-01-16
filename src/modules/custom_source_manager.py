#!/usr/bin/env python3
"""
Custom Source Handler Manager

This tool helps create and manage custom source handlers for event scraping.
It provides templates and utilities to make it easy to add new sources without
requiring deep knowledge of the scraper architecture.

Usage:
    # Create a new custom source handler
    python3 src/modules/custom_source_manager.py create MySource --url https://example.com

    # List all custom sources
    python3 src/modules/custom_source_manager.py list

    # Test a custom source handler
    python3 src/modules/custom_source_manager.py test MySource

    # Generate documentation for a source
    python3 src/modules/custom_source_manager.py document MySource
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


class CustomSourceManager:
    """
    Manager for custom source handlers.
    
    Provides utilities to:
    - Create new custom source handlers from templates
    - Register custom sources in the SmartScraper system
    - Test custom source handlers
    - Document extraction patterns
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.sources_dir = self.base_path / 'src' / 'modules' / 'smart_scraper' / 'sources'
        self.custom_sources_dir = self.sources_dir / 'custom'
        self.templates_dir = self.base_path / 'docs' / 'source_templates'
        
        # Ensure directories exist
        self.custom_sources_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def create_source(self, name: str, url: str, source_type: str = 'html',
                     location_strategy: str = 'detail_page') -> Path:
        """
        Create a new custom source handler from template.
        
        Args:
            name: Source name (e.g., "MyNewsSource")
            url: Base URL for the source
            source_type: Type of source ('html', 'rss', 'api')
            location_strategy: How to extract locations:
                - 'detail_page': Follow links to detail pages to extract location
                - 'listing_page': Extract location from listing page
                - 'api_field': Extract from API response fields
                - 'geocode': Use geocoding service with address text
        
        Returns:
            Path to created source file
        """
        print(f"Creating custom source handler: {name}")
        
        # Generate filename
        filename = self._to_snake_case(name) + '.py'
        filepath = self.custom_sources_dir / filename
        
        if filepath.exists():
            response = input(f"Source {name} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return filepath
        
        # Generate source code from template
        source_code = self._generate_source_code(name, url, source_type, location_strategy)
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write(source_code)
        
        print(f"✓ Created source handler: {filepath}")
        
        # Update __init__.py to include new source
        self._register_source(name, filename)
        
        # Create documentation
        self._create_documentation(name, url, source_type, location_strategy)
        
        print(f"\n{'='*60}")
        print("Next steps:")
        print(f"1. Edit {filepath}")
        print(f"2. Customize the extraction methods for your source")
        print(f"3. Test with: python3 src/modules/custom_source_manager.py test {name}")
        print(f"4. Add to config.json with type: '{self._to_snake_case(name)}'")
        print(f"{'='*60}")
        
        return filepath
    
    def _generate_source_code(self, name: str, url: str, source_type: str,
                             location_strategy: str) -> str:
        """Generate source handler code from template."""
        class_name = self._to_pascal_case(name) + 'Source'
        
        # Select template based on location strategy
        if location_strategy == 'detail_page':
            template = self._get_detail_page_template(class_name, name, url)
        elif location_strategy == 'listing_page':
            template = self._get_listing_page_template(class_name, name, url)
        elif location_strategy == 'api_field':
            template = self._get_api_template(class_name, name, url)
        else:
            template = self._get_basic_template(class_name, name, url)
        
        return template
    
    def _get_detail_page_template(self, class_name: str, name: str, url: str) -> str:
        """Template for sources that need detail page scraping (like Frankenpost)."""
        return f'''"""Custom source handler for {name}."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re
from ...base import BaseSource, SourceOptions

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


class {class_name}(BaseSource):
    """
    Custom scraper for {name}.
    
    This source requires two-step scraping:
    1. List page: Get event titles, dates, and detail URLs
    2. Detail pages: Extract actual venue location information
    
    Usage in config.json:
    {{
        "name": "{name}",
        "url": "{url}",
        "type": "{self._to_snake_case(name)}",
        "enabled": true,
        "options": {{
            "category": "community",
            "default_location": {{
                "name": "Default City",
                "lat": 50.0,
                "lon": 11.0
            }}
        }}
    }}
    """
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None, ai_providers=None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = SCRAPING_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }})
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from {name} with location extraction."""
        if not self.available:
            print("  ⚠ Requests/BeautifulSoup not available")
            return []
        
        events = []
        try:
            # Step 1: Get list of events from main page
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract basic event info from listing
            event_links = self._extract_event_links(soup)
            print(f"    Found {{len(event_links)}} event links")
            
            # Step 2: Fetch each detail page to get location
            for i, (title, detail_url, date_text) in enumerate(event_links[:20], 1):
                try:
                    event = self._scrape_detail_page(title, detail_url, date_text)
                    if event and not self.filter_event(event):
                        events.append(event)
                        print(f"    [{{i}}/{{min(len(event_links), 20)}}] ✓ {{title[:50]}}")
                except Exception as e:
                    print(f"    [{{i}}/{{min(len(event_links), 20)}}] ✗ Error: {{str(e)[:50]}}")
                    
        except Exception as e:
            print(f"    {name} scraping error: {{str(e)}}")
        
        return events
    
    def _extract_event_links(self, soup) -> List[tuple]:
        """
        Extract event links from listing page.
        
        TODO: Customize these selectors for your source!
        Common patterns:
        - '.event' - events with class "event"
        - 'article' - HTML5 article tags
        - '[class*="event"]' - any class containing "event"
        - 'a[href*="detail"]' - links to detail pages
        
        Returns:
            List of tuples: (title, detail_url, date_text)
        """
        event_links = []
        
        # TODO: Customize these selectors for your specific source
        selectors = [
            '.event',              # Events with class "event"
            '.veranstaltung',      # German: "veranstaltung" = event
            '[class*="event"]',    # Any class containing "event"
            'article',             # HTML5 article elements
            '.item',               # Generic item class
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    # Extract title
                    title_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract detail page URL
                    # TODO: Customize this link selector for your source
                    link = elem.find('a', href=lambda x: x and 'detail' in str(x).lower())
                    if not link:
                        link = elem if elem.name == 'a' else None
                    
                    if not link or not link.get('href'):
                        continue
                    
                    detail_url = urljoin(self.url, link['href'])
                    
                    # Extract date text (will be parsed later)
                    date_text = elem.get_text()
                    
                    event_links.append((title, detail_url, date_text))
                
                if event_links:
                    break  # Found events with this selector
        
        return event_links
    
    def _scrape_detail_page(self, title: str, url: str, date_text: str) -> Dict[str, Any]:
        """
        Scrape event detail page to extract location and other info.
        
        Args:
            title: Event title from listing
            url: Detail page URL
            date_text: Date text from listing
            
        Returns:
            Complete event dictionary with location
        """
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract location from detail page
        location = self._extract_location_from_detail(soup)
        
        # Extract description
        description = self._extract_description(soup)
        
        # Parse date
        start_time = self._extract_date(date_text)
        
        return {{
            'id': f"html_{{self.name.lower().replace(' ', '_')}}_{{hash(title + start_time)}}",
            'title': title[:200],
            'description': description,
            'location': location,
            'start_time': start_time,
            'end_time': None,
            'url': url,
            'source': self.name,
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending'
        }}
    
    def _extract_location_from_detail(self, soup) -> Dict[str, Any]:
        """
        Extract venue location from detail page.
        
        TODO: Customize these patterns for your source!
        
        This method uses multiple strategies to find location information:
        1. Look for location labels (Ort:, Location:, etc.)
        2. Look for address patterns (Street Number, ZIP City)
        3. Look for venue names in headings
        
        Returns:
            Location dict with name, lat, lon
        """
        location_name = None
        full_address = None
        
        # Strategy 1: Look for location-related labels
        # TODO: Add keywords specific to your source
        location_keywords = [
            'Ort:', 'Veranstaltungsort:', 'Location:', 'Adresse:', 
            'Venue:', 'Place:', 'Address:', 'Where:'
        ]
        
        for keyword in location_keywords:
            label = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if label and label.parent:
                parent = label.parent
                
                # Check next sibling
                next_elem = parent.find_next_sibling()
                if next_elem:
                    location_text = next_elem.get_text(strip=True)
                    if location_text and len(location_text) > 3:
                        location_name = location_text
                        break
                
                # Check within parent
                parent_text = parent.get_text(strip=True)
                parent_text = parent_text.replace(keyword, '').strip()
                if parent_text and len(parent_text) > 3:
                    location_name = parent_text
                    break
        
        # Strategy 2: Look for address patterns
        # TODO: Adjust pattern for your region/country
        page_text = soup.get_text()
        
        # German address pattern: Street Number, ZIP City
        address_pattern = r'([A-ZÄÖÜ][a-zäöüß\\-\\s\\.]+\\s+\\d+[a-z]?\\s*,\\s*\\d{{5}}\\s+[A-ZÄÖÜ][a-zäöüß\\-\\s]+)'
        addresses = re.findall(address_pattern, page_text)
        
        if addresses:
            full_address = addresses[0].strip()
            if not location_name:
                location_name = full_address
        
        # Strategy 3: Look for venue names in headings
        # TODO: Add venue indicators for your region
        if not location_name:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            venue_indicators = [
                'Museum', 'Halle', 'Schloss', 'Galerie', 'Theater',
                'Kirche', 'Zentrum', 'Haus', 'Platz', 'Rathaus',
                'Hall', 'Center', 'Castle', 'Gallery', 'Church'
            ]
            for heading in headings:
                text = heading.get_text(strip=True)
                if any(indicator in text for indicator in venue_indicators):
                    location_name = text
                    break
        
        # Fallback to default if no location found
        if not location_name and not full_address:
            if self.options.default_location:
                return self.options.default_location
            return {{'name': 'Unknown Location', 'lat': 50.0, 'lon': 11.0}}
        
        # Estimate coordinates based on location text
        return self._estimate_coordinates(location_name or full_address)
    
    def _estimate_coordinates(self, location_text: str) -> Dict[str, Any]:
        """
        Estimate coordinates based on known locations.
        
        TODO: Add cities/venues specific to your region!
        
        For production, consider using a geocoding service like:
        - Nominatim (OpenStreetMap)
        - Google Geocoding API
        - Mapbox Geocoding API
        """
        if not location_text:
            return {{'name': 'Unknown', 'lat': 50.0, 'lon': 11.0}}
        
        location_text_lower = location_text.lower()
        
        # TODO: Add known locations for your region
        known_locations = {{
            'example city': {{'lat': 50.0, 'lon': 11.0}},
            # Add more cities here:
            # 'berlin': {{'lat': 52.5200, 'lon': 13.4050}},
            # 'munich': {{'lat': 48.1351, 'lon': 11.5820}},
        }}
        
        for city, coords in known_locations.items():
            if city in location_text_lower:
                return {{
                    'name': location_text,
                    'lat': coords['lat'],
                    'lon': coords['lon']
                }}
        
        # Default coordinates if city not recognized
        return {{
            'name': location_text,
            'lat': 50.0,
            'lon': 11.0
        }}
    
    def _extract_description(self, soup) -> str:
        """
        Extract event description from detail page.
        
        TODO: Customize selectors for your source!
        """
        desc_selectors = [
            '.description',
            '.event-description',
            '.beschreibung',
            '[class*="description"]',
            'article p',
            '.content p'
        ]
        
        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)[:500]
        
        # Fallback: get first paragraph
        first_p = soup.find('p')
        if first_p:
            return first_p.get_text(strip=True)[:500]
        
        return ''
    
    def _extract_date(self, text: str) -> str:
        """
        Extract date from text using patterns.
        
        TODO: Add date patterns specific to your source!
        """
        patterns = [
            (r'(\\d{{1,2}})\\.(\\d{{1,2}})\\.(\\d{{4}})', 'DMY'),  # DD.MM.YYYY
            (r'(\\d{{4}})-(\\d{{2}})-(\\d{{2}})', 'YMD'),  # YYYY-MM-DD
            (r'(\\d{{1,2}})/(\\d{{1,2}})/(\\d{{4}})', 'MDY'),  # MM/DD/YYYY
        ]
        
        for pattern, format_type in patterns:
            match = re.search(pattern, text)
            if match:
                date = self._parse_date_match(match.groups(), format_type)
                if date:
                    return date
        
        # Default to next week if no date found
        return (datetime.now() + timedelta(days=7)).replace(hour=18, minute=0).isoformat()
    
    def _parse_date_match(self, groups: tuple, format_type: str) -> str:
        """Parse matched date groups into ISO format."""
        try:
            if format_type == 'DMY':
                day, month, year = groups
                date = datetime(int(year), int(month), int(day), 18, 0)
            elif format_type == 'MDY':
                month, day, year = groups
                date = datetime(int(year), int(month), int(day), 18, 0)
            else:  # YMD
                year, month, day = groups
                date = datetime(int(year), int(month), int(day), 18, 0)
            return date.isoformat()
        except ValueError:
            return None
'''
    
    def _get_listing_page_template(self, class_name: str, name: str, url: str) -> str:
        """Template for sources where location is on the listing page."""
        return f'''"""Custom source handler for {name}."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import re
from ...base import BaseSource, SourceOptions

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


class {class_name}(BaseSource):
    """
    Custom scraper for {name}.
    
    This source extracts all information (including location) from the listing page.
    No need for detail page scraping.
    
    Usage in config.json:
    {{
        "name": "{name}",
        "url": "{url}",
        "type": "{self._to_snake_case(name)}",
        "enabled": true
    }}
    """
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None, ai_providers=None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = SCRAPING_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }})
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from {name}."""
        if not self.available:
            print("  ⚠ Requests/BeautifulSoup not available")
            return []
        
        events = []
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            events = self._extract_events(soup)
            
        except Exception as e:
            print(f"    {name} error: {{str(e)}}")
        
        return events
    
    def _extract_events(self, soup) -> List[Dict[str, Any]]:
        """
        Extract events from listing page.
        
        TODO: Customize selectors and extraction logic for your source!
        """
        events = []
        
        # TODO: Customize event selectors
        selectors = ['.event', 'article', '.item']
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:20]:  # Limit to 20
                    event = self._parse_event_element(item)
                    if event and not self.filter_event(event):
                        events.append(event)
                break
        
        return events
    
    def _parse_event_element(self, element) -> Dict[str, Any]:
        """
        Parse single event element.
        
        TODO: Customize extraction logic!
        """
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
            
            # Extract description
            desc_elem = element.find(['p', 'div', 'span'])
            description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''
            
            # Extract location
            # TODO: Customize location extraction
            location = self._extract_location(element)
            
            # Extract date
            date_text = element.get_text()
            start_time = self._extract_date(date_text)
            
            # Extract URL
            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else self.url
            
            if not title or title == 'Untitled':
                return None
            
            return {{
                'id': f"html_{{self.name.lower().replace(' ', '_')}}_{{hash(title + start_time)}}",
                'title': title[:200],
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': None,
                'url': url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }}
        except Exception as e:
            print(f"      Error parsing element: {{str(e)}}")
            return None
    
    def _extract_location(self, element) -> Dict[str, Any]:
        """
        Extract location from event element.
        
        TODO: Customize for your source!
        """
        # Try to find location in element
        location_elem = element.find(class_=lambda x: x and 'location' in str(x).lower())
        if location_elem:
            location_name = location_elem.get_text(strip=True)
            if location_name:
                return self._estimate_coordinates(location_name)
        
        # Fallback to default
        if self.options.default_location:
            return self.options.default_location
        
        return {{'name': 'Unknown', 'lat': 50.0, 'lon': 11.0}}
    
    def _estimate_coordinates(self, location_text: str) -> Dict[str, Any]:
        """
        Estimate coordinates.
        
        TODO: Add known locations for your region!
        """
        # Add your known locations here
        known_locations = {{}}
        
        location_text_lower = location_text.lower()
        for city, coords in known_locations.items():
            if city in location_text_lower:
                return {{
                    'name': location_text,
                    'lat': coords['lat'],
                    'lon': coords['lon']
                }}
        
        return {{'name': location_text, 'lat': 50.0, 'lon': 11.0}}
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text."""
        # TODO: Add date patterns for your source
        patterns = [
            (r'(\\d{{1,2}})\\.(\\d{{1,2}})\\.(\\d{{4}})', 'DMY'),
            (r'(\\d{{4}})-(\\d{{2}})-(\\d{{2}})', 'YMD'),
        ]
        
        for pattern, format_type in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if format_type == 'DMY':
                        day, month, year = match.groups()
                        date = datetime(int(year), int(month), int(day), 18, 0)
                    else:
                        year, month, day = match.groups()
                        date = datetime(int(year), int(month), int(day), 18, 0)
                    return date.isoformat()
                except ValueError:
                    pass
        
        return (datetime.now() + timedelta(days=7)).replace(hour=18, minute=0).isoformat()
'''
    
    def _get_api_template(self, class_name: str, name: str, url: str) -> str:
        """Template for API sources."""
        return f'''"""Custom source handler for {name} API."""

from typing import Dict, Any, List
from datetime import datetime
from ...base import BaseSource, SourceOptions

try:
    import requests
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


class {class_name}(BaseSource):
    """
    Custom scraper for {name} API.
    
    Usage in config.json:
    {{
        "name": "{name}",
        "url": "{url}",
        "type": "{self._to_snake_case(name)}",
        "enabled": true
    }}
    """
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None, ai_providers=None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = SCRAPING_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            # TODO: Add API authentication headers if needed
            self.session.headers.update({{
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }})
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from {name} API."""
        if not self.available:
            print("  ⚠ Requests library not available")
            return []
        
        events = []
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # TODO: Customize based on API response structure
            events = self._parse_api_response(data)
            
        except Exception as e:
            print(f"    {name} API error: {{str(e)}}")
        
        return events
    
    def _parse_api_response(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse API response into event list.
        
        TODO: Customize based on your API's response structure!
        """
        events = []
        
        # TODO: Adjust based on whether data is a list or nested object
        items = data if isinstance(data, list) else data.get('events', [])
        
        for item in items:
            event = self._parse_api_item(item)
            if event and not self.filter_event(event):
                events.append(event)
        
        return events
    
    def _parse_api_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse single API item into event format.
        
        TODO: Map API fields to event fields!
        """
        try:
            # TODO: Adjust field names based on your API
            title = item.get('title') or item.get('name') or 'Untitled'
            description = item.get('description', '')[:500]
            start_time = item.get('start_time') or item.get('date')
            url = item.get('url') or item.get('link') or self.url
            
            # Extract location
            location = self._extract_location_from_api(item)
            
            return {{
                'id': f"api_{{self.name.lower().replace(' ', '_')}}_{{item.get('id', hash(title))}}",
                'title': title[:200],
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': item.get('end_time'),
                'url': url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }}
        except Exception as e:
            print(f"      Error parsing API item: {{str(e)}}")
            return None
    
    def _extract_location_from_api(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract location from API response.
        
        TODO: Adjust field names based on your API!
        """
        # Check if location is a nested object
        if 'location' in item and isinstance(item['location'], dict):
            loc = item['location']
            return {{
                'name': loc.get('name', 'Unknown'),
                'lat': loc.get('lat') or loc.get('latitude', 50.0),
                'lon': loc.get('lon') or loc.get('longitude', 11.0)
            }}
        
        # Check for separate fields
        if 'venue' in item:
            return {{
                'name': item['venue'],
                'lat': item.get('latitude', 50.0),
                'lon': item.get('longitude', 11.0)
            }}
        
        # Fallback
        if self.options.default_location:
            return self.options.default_location
        
        return {{'name': 'Unknown', 'lat': 50.0, 'lon': 11.0}}
'''
    
    def _get_basic_template(self, class_name: str, name: str, url: str) -> str:
        """Basic template for simple sources."""
        return self._get_listing_page_template(class_name, name, url)
    
    def _register_source(self, name: str, filename: str):
        """Register source in __init__.py."""
        init_file = self.custom_sources_dir / '__init__.py'
        
        # Create __init__.py if it doesn't exist
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Custom source handlers."""\n\n')
        
        # Add import statement
        module_name = filename.replace('.py', '')
        import_line = f"from . import {module_name}\n"
        
        with open(init_file, 'r') as f:
            content = f.read()
        
        if import_line not in content:
            with open(init_file, 'a') as f:
                f.write(import_line)
            print(f"✓ Registered {name} in __init__.py")
    
    def _create_documentation(self, name: str, url: str, source_type: str,
                             location_strategy: str):
        """Create documentation file for the source."""
        doc_file = self.templates_dir / f"{self._to_snake_case(name)}_guide.md"
        
        doc_content = f"""# {name} Custom Source Handler

## Overview
- **Source Name**: {name}
- **URL**: {url}
- **Type**: {source_type}
- **Location Strategy**: {location_strategy}
- **Created**: {datetime.now().isoformat()}

## Location Extraction Strategy

This source uses the **{location_strategy}** strategy:

"""
        
        if location_strategy == 'detail_page':
            doc_content += """
### Detail Page Strategy

1. **List Page**: Scrape event titles and links to detail pages
2. **Detail Pages**: Follow each link to extract:
   - Full event description
   - Venue name and address
   - Precise location coordinates (if available)

### Customization Points

Edit the following methods in your source file:

1. `_extract_event_links(soup)` - Customize selectors for event listing
2. `_extract_location_from_detail(soup)` - Customize location extraction patterns
3. `_estimate_coordinates(location_text)` - Add known venues/cities
4. `_extract_description(soup)` - Customize description extraction
5. `_extract_date(text)` - Add date patterns specific to this source

### Example: Finding Location Selectors

```python
# Open the detail page in a browser
# Right-click on location text → Inspect
# Note the CSS classes/IDs used
# Add them to _extract_location_from_detail()

# Example patterns:
location_keywords = [
    'Ort:',              # German: Location
    'Veranstaltungsort:', # German: Venue
    'Adresse:',          # German: Address
    'Location:',         # English
]
```
"""
        
        doc_content += f"""

## Configuration

Add this to your `config.json`:

```json
{{
  "name": "{name}",
  "url": "{url}",
  "type": "{self._to_snake_case(name)}",
  "enabled": true,
  "options": {{
    "filter_ads": true,
    "exclude_keywords": ["advertisement", "sponsored"],
    "max_days_ahead": 90,
    "category": "community",
    "default_location": {{
      "name": "Default City Name",
      "lat": 50.0,
      "lon": 11.0
    }}
  }}
}}
```

## Testing

```bash
# Test the source handler
python3 src/modules/custom_source_manager.py test {name}

# Run with event manager
python3 src/event_manager.py scrape
```

## Troubleshooting

### No events scraped
1. Check if selectors match the HTML structure
2. Verify the URL is correct
3. Check network connectivity
4. Look for error messages in console

### Wrong locations extracted
1. Inspect detail pages in browser
2. Find CSS selectors for location elements
3. Update `_extract_location_from_detail()` method
4. Add known venues to `_estimate_coordinates()`

### Date parsing issues
1. Check date format on the website
2. Add appropriate regex pattern to `_extract_date()`
3. Test with various date formats

## Further Customization

See the source file for detailed TODO comments marking customization points.
"""
        
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        print(f"✓ Created documentation: {doc_file}")
    
    def list_sources(self):
        """List all custom source handlers."""
        print("Custom Source Handlers:")
        print("="*60)
        
        sources = list(self.custom_sources_dir.glob('*.py'))
        sources = [s for s in sources if s.name != '__init__.py']
        
        if not sources:
            print("No custom sources found.")
            print(f"Create one with: python3 {sys.argv[0]} create SourceName --url URL")
            return
        
        for i, source_file in enumerate(sources, 1):
            name = source_file.stem
            print(f"{i}. {name}")
            print(f"   File: {source_file}")
            
            # Check if registered in core
            registered = self._check_if_registered(name)
            if registered:
                print(f"   Status: ✓ Registered in SmartScraper")
            else:
                print(f"   Status: ⚠ Not registered (add to core.py)")
            print()
    
    def _check_if_registered(self, name: str) -> bool:
        """Check if source is registered in SmartScraper core."""
        core_file = self.base_path / 'src' / 'modules' / 'smart_scraper' / 'core.py'
        if not core_file.exists():
            return False
        
        with open(core_file, 'r') as f:
            content = f.read()
        
        return name.lower() in content.lower()
    
    def test_source(self, name: str):
        """Test a custom source handler."""
        print(f"Testing custom source: {name}")
        print("="*60)
        
        # Find source file
        source_file = self.custom_sources_dir / f"{self._to_snake_case(name)}.py"
        if not source_file.exists():
            print(f"✗ Source file not found: {source_file}")
            return
        
        # Try to import and test
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(name, source_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            print(f"✓ Source module loaded successfully")
            
            # Find the source class
            class_name = self._to_pascal_case(name) + 'Source'
            if not hasattr(module, class_name):
                print(f"✗ Class {class_name} not found in module")
                return
            
            print(f"✓ Found class: {class_name}")
            
            # Try to instantiate
            from modules.smart_scraper.base import SourceOptions
            test_config = {
                'name': name,
                'url': 'https://example.com',
                'type': self._to_snake_case(name)
            }
            test_options = SourceOptions()
            
            SourceClass = getattr(module, class_name)
            source = SourceClass(test_config, test_options)
            
            print(f"✓ Source instantiated successfully")
            print(f"✓ Scraping available: {source.available}")
            
            print("\n" + "="*60)
            print("Next steps:")
            print("1. Add source to config.json")
            print("2. Run: python3 src/event_manager.py scrape")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Error testing source: {e}")
            import traceback
            traceback.print_exc()
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Replace spaces and special chars with underscores
        name = re.sub(r'[^\w]', '_', name)
        # Insert underscore before uppercase letters
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        # Split on spaces, underscores, hyphens
        parts = re.split(r'[\s_-]+', name)
        # Capitalize each part
        return ''.join(p.capitalize() for p in parts if p)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Custom Source Handler Manager',
        epilog='Examples:\n'
               '  %(prog)s create MyNews --url https://news.example.com\n'
               '  %(prog)s list\n'
               '  %(prog)s test MyNews\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', choices=['create', 'list', 'test', 'document'],
                       help='Command to execute')
    parser.add_argument('name', nargs='?', help='Source name (for create/test)')
    parser.add_argument('--url', help='Source URL (for create)')
    parser.add_argument('--type', default='html', choices=['html', 'rss', 'api'],
                       help='Source type (default: html)')
    parser.add_argument('--location-strategy', default='detail_page',
                       choices=['detail_page', 'listing_page', 'api_field', 'geocode'],
                       help='Location extraction strategy (default: detail_page)')
    
    args = parser.parse_args()
    
    # Get base path (repo root)
    base_path = Path(__file__).parent.parent.parent
    manager = CustomSourceManager(base_path)
    
    if args.command == 'create':
        if not args.name:
            print("Error: Source name required for create command")
            sys.exit(1)
        if not args.url:
            print("Error: --url required for create command")
            sys.exit(1)
        
        manager.create_source(args.name, args.url, args.type, args.location_strategy)
    
    elif args.command == 'list':
        manager.list_sources()
    
    elif args.command == 'test':
        if not args.name:
            print("Error: Source name required for test command")
            sys.exit(1)
        
        manager.test_source(args.name)
    
    elif args.command == 'document':
        print("Documentation feature coming soon!")
        print("See docs/source_templates/ for existing guides.")


if __name__ == '__main__':
    main()
