"""Custom scraper for VHS Hofer Land (Volkshochschule)."""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin
from pathlib import Path
from ...base import BaseSource, SourceOptions
from .date_utils import extract_date_from_text, generate_stable_event_id

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# German weekday abbreviations pattern (Mo., Di., Mi., Do., Fr., Sa., So.)
# This pattern matches: "Mo. DD.MM.YYYY HH:MM" format commonly used in VHS listings
WEEKDAY_DATE_TIME_PATTERN = re.compile(
    r'(Mo\.|Di\.|Mi\.|Do\.|Fr\.|Sa\.|So\.)\s*'  # Weekday abbreviation with dot
    r'(\d{1,2}\.\d{1,2}\.\d{2,4})\s*'           # Date: DD.MM.YY or DD.MM.YYYY
    r'(\d{1,2}:\d{2})?'                          # Optional time: HH:MM
)


class VHSSource(BaseSource):
    """
    Custom scraper for VHS Hofer Land last-minute courses.
    
    VHS (Volkshochschule) is an adult education center offering various
    courses and workshops. This scraper focuses on last-minute course offerings.
    """
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path: Optional[Path] = None, ai_providers: Optional[Dict[str, Any]] = None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = SCRAPING_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                )
            })
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape courses from VHS."""
        if not self.available:
            print("  ⚠ Requests/BeautifulSoup not available")
            return []
        
        events = []
        try:
            response = self.session.get(self.url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Look for course containers
            # VHS sites often use table layouts or list items for courses
            course_containers = (
                soup.select('.course-item') or
                soup.select('.kurs') or
                soup.select('tr[class*="course"]') or
                soup.select('li[class*="course"]') or
                soup.select('article') or
                soup.select('.item')[:20]  # Fallback
            )
            
            if not course_containers:
                print(f"    No courses found on page")
                return []
            
            print(f"    Found {len(course_containers)} potential courses")
            
            for i, container in enumerate(course_containers[:20], 1):
                try:
                    event = self._parse_course(container)
                    if event and not self.filter_event(event):
                        events.append(event)
                        print(f"    [{i}/{min(len(course_containers), 20)}] ✓ {event['title'][:50]}")
                except Exception as e:
                    print(f"    [{i}] ✗ Parse error: {str(e)[:50]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {str(e)}")
        except Exception as e:
            print(f"    Scraping error: {str(e)}")
        
        return events
    
    def _extract_location_from_text(self, text: str) -> Optional[str]:
        """
        Extract location from text that starts with location prefix (case-insensitive).
        
        Handles variations like:
        - 'Ort:' / 'ORT:' / 'ort:'
        - 'Ort / Raum:' (tabular header format)
        - 'Ort :' (with space before colon)
        
        Args:
            text: Text that may contain location prefix
            
        Returns:
            Location name or None if not found or empty
        """
        # Normalize: strip whitespace and check case-insensitively
        normalized = text.strip()
        lower_text = normalized.lower()
        
        # Check for "ort / raum" pattern first (tabular header format)
        ort_raum_pattern = re.match(r'^ort\s*/\s*raum\s*:?\s*', lower_text)
        if ort_raum_pattern:
            location_text = normalized[ort_raum_pattern.end():].strip()
            if location_text:
                return location_text
        
        # Check for "ort" followed by optional spaces and then colon
        if lower_text.startswith('ort'):
            # Get remainder after "ort", strip any spaces, check for colon
            rest = normalized[3:].lstrip()
            if rest.startswith(':'):
                location_text = rest[1:].strip()
                if location_text:
                    return location_text
        return None
    
    def _is_ort_label(self, text: str) -> bool:
        """
        Check if text is specifically a location label (case-insensitive).
        
        Matches:
        - 'ort', 'Ort', 'ORT' followed by optional spaces and colon
        - 'Ort / Raum' followed by optional spaces and colon
        
        Does NOT match 'ortschaft:', 'ortsangabe:', etc.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is a location label
        """
        normalized = text.strip().lower()
        
        # Check for "ort / raum" pattern
        if re.match(r'^ort\s*/\s*raum\s*:?$', normalized):
            return True
        
        # Must be exactly "ort" followed by optional spaces and colon
        if normalized.startswith('ort'):
            rest = normalized[3:].lstrip()
            return rest.startswith(':') or rest == ''
        return False
    
    def _extract_location(self, container) -> Optional[str]:
        """
        Extract location name from VHS course HTML container.
        
        Strategies are ordered from most specific to least specific:
        1. <strong>Ort:</strong> pattern (most precise)
        2. Elements with class 'course-places-list' (VHS standard format)
        3. Fallback: any li/div/span/td/p with 'Ort:' prefix (limited search)
        
        Args:
            container: BeautifulSoup element containing course data
            
        Returns:
            Location name string or None if not found
        """
        # Strategy 1: Check for <strong>Ort:</strong> pattern (most specific)
        strong_elems = container.find_all('strong')
        for strong in strong_elems:
            strong_text = strong.get_text(strip=True)
            # Check if this strong element is specifically the "Ort:" label
            if self._is_ort_label(strong_text):
                # Get text from parent element
                parent = strong.parent
                if parent:
                    full_text = parent.get_text(strip=True)
                    location = self._extract_location_from_text(full_text)
                    if location:
                        return location
        
        # Strategy 2: VHS standard format - 'course-places-list' element
        places_elem = container.find(class_='course-places-list')
        if places_elem:
            text = places_elem.get_text(strip=True)
            location = self._extract_location_from_text(text)
            if location:
                return location
        
        # Strategy 3: Fallback - broad search with limit for performance
        for elem in container.find_all(['li', 'div', 'span', 'td', 'p'], limit=30):
            text = elem.get_text(strip=True)
            location = self._extract_location_from_text(text)
            if location:
                return location
        
        return None
    
    def _parse_concatenated_title(self, raw_title: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Parse concatenated VHS title text to extract clean title, date, and location.
        
        VHS listings often have titles in format:
        "[Course Title][Optional Type][Weekday. DD.MM.YYYY HH:MM][Location/Address]"
        
        Examples:
        - "Interkultureller ChorChorprobenDo. 08.01.2026 19:00Ludwigstraße 7, 95028 Hof"
        - "Training für den Körper 1Fr. 16.01.2026 16:30Philipp-Wolfrum-Haus, Marktplatz 17, 95131 Schwarzenbach a.Wald"
        - "KI-Selfies: Künstliche Intelligenz als FotografMi. 04.02.2026 17:00Online"
        
        Args:
            raw_title: The concatenated title text from the HTML
            
        Returns:
            Tuple of (clean_title, date_string, location_name)
            - clean_title: Title before the weekday abbreviation
            - date_string: Date in DD.MM.YYYY format (or None if not found)
            - location_name: Location after the time (or None if not found)
        """
        # Find the weekday pattern in the title
        match = WEEKDAY_DATE_TIME_PATTERN.search(raw_title)
        
        if not match:
            # No date pattern found, return original title
            return raw_title.strip(), None, None
        
        # Extract the title before the weekday pattern
        title_end_pos = match.start()
        clean_title = raw_title[:title_end_pos].strip()
        
        # Extract the date portion
        date_string = match.group(2)  # DD.MM.YYYY
        
        # Extract location: everything after the match (after time or date)
        location_start_pos = match.end()
        location_text = raw_title[location_start_pos:].strip()
        
        # Clean up the location text
        location_name = location_text if location_text else None
        
        return clean_title, date_string, location_name
    
    def _parse_course(self, container) -> Optional[Dict[str, Any]]:
        """Parse course from HTML container."""
        # Extract title
        title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a', 'strong'])
        if not title_elem:
            return None
        raw_title = title_elem.get_text(strip=True)
        
        if not raw_title or len(raw_title) < 5:
            return None
        
        # Skip if it's just a header
        if raw_title.lower() in ['kurse', 'veranstaltungen', 'termine']:
            return None
        
        # Parse concatenated title to extract clean title, date, and location
        clean_title, parsed_date, title_location = self._parse_concatenated_title(raw_title)
        
        # Use clean title or fallback to raw title if parsing failed
        title = clean_title if clean_title else raw_title
        
        # Extract description
        desc_elem = container.find(['p', '.description', 'td'])
        description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''
        
        # Extract URL
        link_elem = container.find('a', href=True)
        event_url = urljoin(self.url, link_elem['href']) if link_elem else self.url
        
        # Extract date using shared utility, prefer parsed date from title
        if parsed_date:
            # Use the date extracted from title
            start_time = extract_date_from_text(parsed_date, default_hour=18)
        else:
            # Fallback to container text
            date_text = container.get_text()
            start_time = extract_date_from_text(date_text, default_hour=18)
        
        # Extract location from HTML, fall back to default if not found
        default_location = self.options.default_location or {
            'name': 'VHS Hofer Land',
            'lat': 50.3167,
            'lon': 11.9167
        }
        
        # Priority for location extraction:
        # 1. Location from "Ort / Raum" or "Ort:" in HTML (most precise)
        # 2. Location extracted from concatenated title (training day location)
        # 3. Default location
        extracted_location_name = self._extract_location(container)
        
        if extracted_location_name:
            # Use extracted location name from HTML
            location = {
                'name': extracted_location_name,
                'lat': default_location.get('lat', 50.3167),
                'lon': default_location.get('lon', 11.9167)
            }
        elif title_location:
            # Use location extracted from concatenated title
            location = {
                'name': title_location,
                'lat': default_location.get('lat', 50.3167),
                'lon': default_location.get('lon', 11.9167)
            }
        else:
            location = default_location
        
        return {
            'id': generate_stable_event_id('vhs', title, start_time),
            'title': title[:200],
            'description': description,
            'location': location,
            'start_time': start_time,
            'end_time': None,
            'url': event_url,
            'source': self.name,
            'category': self.options.category or 'education',
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending'
        }
