"""Custom scraper for VHS Hofer Land (Volkshochschule)."""

from typing import Dict, Any, List, Optional
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
        Extract location from text that starts with 'Ort:' (case-insensitive).
        
        Handles variations like 'ORT:', 'ort:', 'Ort :', etc.
        
        Args:
            text: Text that may contain 'Ort:' prefix
            
        Returns:
            Location name or None if not found or empty
        """
        # Normalize: strip whitespace and check case-insensitively
        normalized = text.strip()
        lower_text = normalized.lower()
        
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
        Check if text is specifically the 'Ort:' label (case-insensitive).
        
        Only matches 'ort', 'Ort', 'ORT' followed by optional spaces and colon.
        Does NOT match 'ortschaft:', 'ortsangabe:', etc.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is specifically 'Ort:' (with optional spacing)
        """
        normalized = text.strip().lower()
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
    
    def _parse_course(self, container) -> Optional[Dict[str, Any]]:
        """Parse course from HTML container."""
        # Extract title
        title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a', 'strong'])
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        
        if not title or len(title) < 5:
            return None
        
        # Skip if it's just a header
        if title.lower() in ['kurse', 'veranstaltungen', 'termine']:
            return None
        
        # Extract description
        desc_elem = container.find(['p', '.description', 'td'])
        description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''
        
        # Extract URL
        link_elem = container.find('a', href=True)
        event_url = urljoin(self.url, link_elem['href']) if link_elem else self.url
        
        # Extract date using shared utility
        date_text = container.get_text()
        start_time = extract_date_from_text(date_text, default_hour=18)
        
        # Extract location from HTML, fall back to default if not found
        default_location = self.options.default_location or {
            'name': 'VHS Hofer Land',
            'lat': 50.3167,
            'lon': 11.9167
        }
        
        extracted_location_name = self._extract_location(container)
        if extracted_location_name:
            # Use extracted location name with default coordinates
            location = {
                'name': extracted_location_name,
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
