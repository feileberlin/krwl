"""Custom Frankenpost scraper with location extraction from detail pages."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re
from ..base import BaseSource, SourceOptions

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


class FrankenpostSource(BaseSource):
    """
    Custom scraper for Frankenpost event portal.
    
    Frankenpost requires two-step scraping:
    1. List page: Get event titles, dates, and detail URLs
    2. Detail pages: Extract actual venue location information
    
    This fixes the issue where events were showing "Frankenpost" or generic
    "Hof" as location instead of actual venue names and addresses.
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
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Frankenpost with location extraction."""
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
            print(f"    Found {len(event_links)} event links")
            
            # Step 2: Fetch each detail page to get location
            for i, (title, url, date_text) in enumerate(event_links[:20], 1):  # Limit to 20
                try:
                    event = self._scrape_detail_page(title, url, date_text)
                    if event and not self.filter_event(event):
                        events.append(event)
                        print(f"    [{i}/{min(len(event_links), 20)}] ✓ {title[:50]}")
                except Exception as e:
                    print(f"    [{i}/{min(len(event_links), 20)}] ✗ Error: {str(e)[:50]}")
                    
        except Exception as e:
            print(f"    Frankenpost scraping error: {str(e)}")
        
        return events
    
    def _extract_event_links(self, soup) -> List[tuple]:
        """
        Extract event links from listing page.
        
        Returns:
            List of tuples: (title, detail_url, date_text)
        """
        event_links = []
        
        # Try common event listing selectors
        selectors = [
            '.event', '.veranstaltung', '[class*="event"]',
            'article', '.item', 'tr[onclick]', 'a[href*="detail.php"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    # Extract title (from link or heading)
                    title_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract detail page URL
                    link = elem.find('a', href=lambda x: x and 'detail.php' in x)
                    if not link:
                        # Check if element itself is a link
                        link = elem if elem.name == 'a' and 'detail.php' in elem.get('href', '') else None
                    
                    if not link or 'event_id=' not in link.get('href', ''):
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
        
        # Extract description (fuller than listing)
        description = self._extract_description(soup)
        
        # Parse date
        start_time = self._extract_date(date_text)
        
        return {
            'id': f"html_frankenpost_{hash(title + start_time)}",
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
    
    def _extract_location_from_detail(self, soup) -> Dict[str, Any]:
        """
        Extract venue location from detail page.
        
        Looks for:
        - Location/Ort labels and their values
        - Address patterns (Street Number, ZIP City)
        - Venue name patterns
        
        Returns:
            Location dict with name, lat, lon (coordinates may be estimated)
        """
        location_name = None
        full_address = None
        
        # Strategy 1: Look for location-related labels and fields
        location_keywords = ['Ort:', 'Veranstaltungsort:', 'Location:', 'Adresse:', 'Venue:']
        for keyword in location_keywords:
            # Find label with keyword
            label = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if label and label.parent:
                # Try to find adjacent/sibling element with location value
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
                # Remove the label itself from text
                parent_text = parent_text.replace(keyword, '').strip()
                if parent_text and len(parent_text) > 3:
                    location_name = parent_text
                    break
        
        # Strategy 2: Look for address patterns (German format)
        # Pattern: Street Number, ZIP City (e.g., "Maximilianstraße 33, 95444 Bayreuth")
        page_text = soup.get_text()
        address_pattern = r'([A-ZÄÖÜ][a-zäöüß\-\s\.]+\s+\d+[a-z]?\s*,\s*\d{5}\s+[A-ZÄÖÜ][a-zäöüß\-\s]+)'
        addresses = re.findall(address_pattern, page_text)
        
        if addresses:
            # Use first address found
            full_address = addresses[0].strip()
            # If we don't have a location name yet, use the address
            if not location_name:
                location_name = full_address
        
        # Strategy 3: Look for venue names in title/headings
        if not location_name:
            # Check for venue patterns in headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                text = heading.get_text(strip=True)
                # Look for venue indicators (Museum, Halle, Schloss, etc.)
                venue_indicators = ['Museum', 'Halle', 'Schloss', 'Galerie', 'Theater', 
                                  'Kirche', 'Zentrum', 'Haus', 'Platz', 'Rathaus', 
                                  'Saal', 'Kulturzentrum', 'Bibliothek']
                if any(indicator in text for indicator in venue_indicators):
                    location_name = text
                    break
        
        # Parse location to extract coordinates if possible
        # Check if we have a full address or just a venue name
        location = self._estimate_coordinates(location_name if location_name else '')
        
        # If no location found at all, use default from config
        if not location_name and not full_address:
            default_loc = self.options.default_location
            if default_loc:
                return default_loc
            else:
                return {
                    'name': 'Hof',
                    'lat': 50.3167,
                    'lon': 11.9167
                }
        
        # If we have a full address, use it as the name
        if full_address and not location_name:
            location = self._estimate_coordinates(full_address)
        
        return location
    
    def _estimate_coordinates(self, location_text: str) -> Dict[str, Any]:
        """
        Estimate coordinates based on known locations.
        
        For now, uses a simple lookup table for common cities in the region.
        In the future, this could be replaced with a geocoding service.
        """
        location_text_lower = location_text.lower()
        
        # Known location coordinates (city centers)
        known_locations = {
            'bayreuth': {'lat': 49.9440, 'lon': 11.5760},
            'hof': {'lat': 50.3167, 'lon': 11.9167},
            'selb': {'lat': 50.1705, 'lon': 12.1328},
            'rehau': {'lat': 50.2489, 'lon': 12.0364},
            'kulmbach': {'lat': 50.1050, 'lon': 11.4458},
            'münchberg': {'lat': 50.1900, 'lon': 11.7900},
        }
        
        for city, coords in known_locations.items():
            if city in location_text_lower:
                return {
                    'name': location_text,
                    'lat': coords['lat'],
                    'lon': coords['lon']
                }
        
        # Default to Hof if city not recognized
        return {
            'name': location_text,
            'lat': 50.3167,
            'lon': 11.9167
        }
    
    def _extract_description(self, soup) -> str:
        """Extract event description from detail page."""
        # Look for description in common places
        desc_selectors = [
            '.description', '.event-description', '.beschreibung',
            '[class*="description"]', 'article p', '.content p'
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
        """Parse matched date groups into ISO format."""
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
