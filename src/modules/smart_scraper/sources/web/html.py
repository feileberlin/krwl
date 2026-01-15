"""HTML page scraper."""

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


class HTMLSource(BaseSource):
    """Scraper for HTML pages."""
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None):
        super().__init__(source_config, options, base_path=base_path)
        self.available = SCRAPING_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from HTML page."""
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
            print(f"    HTML error: {str(e)}")
        
        return events
    
    def _extract_events(self, soup) -> List[Dict[str, Any]]:
        """Extract events from HTML using common patterns."""
        events = []
        
        # Common selectors for event listings
        selectors = [
            '.event', '.veranstaltung', '[class*="event"]',
            '[class*="calendar"]', 'article', '.item'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:20]:  # Limit to 20 events
                    event = self._parse_element(item)
                    if event and not self.filter_event(event):
                        events.append(event)
                break  # Stop after first matching selector
        
        return events
    
    def _parse_element(self, element) -> Dict[str, Any]:
        """Parse HTML element into event format."""
        try:
            # Extract basic fields
            title = self._extract_title(element)
            description = self._extract_description(element)
            url = self._extract_url(element)
            
            # Extract date
            date_text = element.get_text()
            start_time = self._extract_date(date_text)
            
            # Use default location
            location = self._get_default_location()
            
            # Return event if valid title
            if not title or title == 'Untitled Event':
                return None
            
            return {
                'id': f"html_{self.name.lower().replace(' ', '_')}_{hash(title + start_time)}",
                'title': title[:200],
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': None,
                'url': url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        except Exception as e:
            print(f"      Error parsing HTML element: {str(e)}")
            return None
    
    def _extract_title(self, element) -> str:
        """Extract title from HTML element."""
        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
        return title_elem.get_text(strip=True) if title_elem else 'Untitled Event'
    
    def _extract_description(self, element) -> str:
        """Extract description from HTML element."""
        desc_elem = element.find(['p', 'div', 'span'])
        return desc_elem.get_text(strip=True)[:500] if desc_elem else ''
    
    def _extract_url(self, element) -> str:
        """Extract URL from HTML element."""
        link_elem = element.find('a', href=True)
        return urljoin(self.url, link_elem['href']) if link_elem else self.url
    
    def _get_default_location(self) -> Dict[str, Any]:
        """Get default location for events."""
        return self.options.default_location or {
            'name': self.name,
            'lat': 50.3167,
            'lon': 11.9167
        }
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text using patterns."""
        patterns = [
            (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'DMY'),  # DD.MM.YYYY
            (r'(\d{4})-(\d{2})-(\d{2})', 'YMD'),  # YYYY-MM-DD
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
        """Parse matched date groups into ISO format.
        
        Args:
            groups: Regex match groups
            format_type: 'DMY' or 'YMD'
            
        Returns:
            ISO formatted date string or None if invalid
        """
        try:
            if format_type == 'DMY':
                day, month, year = groups
                date = datetime(int(year), int(month), int(day), 18, 0)
            else:  # YMD
                year, month, day = groups
                date = datetime(int(year), int(month), int(day), 18, 0)
            return date.isoformat()
        except ValueError:
            return None
