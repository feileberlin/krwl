"""Custom Frankenpost scraper with location extraction from detail pages."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re
import json
from pathlib import Path
from ..base import BaseSource, SourceOptions

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# Import reviewer notes system for flagging ambiguous locations
try:
    from ...reviewer_notes import (
        ReviewerNotes,
        enhance_event_with_location_confidence
    )
    REVIEWER_NOTES_AVAILABLE = True
except ImportError:
    REVIEWER_NOTES_AVAILABLE = False


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
        
        # Initialize reviewer notes system for flagging ambiguous locations
        if REVIEWER_NOTES_AVAILABLE and base_path:
            self.reviewer_notes = ReviewerNotes(Path(base_path))
        else:
            self.reviewer_notes = None
        
        # Known cities in the region for ambiguity detection
        self.known_cities = ['Bayreuth', 'Hof', 'Selb', 'Rehau', 'Kulmbach', 'Münchberg']
        
        # Initialize modular location utilities (replaces duplicate logic)
        self.location_normalizer = None
        if base_path:
            try:
                from ..scraper_utils import LocationNormalizer
                self.location_normalizer = LocationNormalizer(Path(base_path))
            except ImportError:
                pass
        
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
        
        # Save tracked unverified locations and show hints (uses modular utility)
        if self.location_normalizer:
            hint = self.location_normalizer.save_tracked_locations()
            if hint:
                print(f"\n  {hint}")
        
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
        
        # Extract location from detail page (returns location + extraction details)
        location, extraction_details = self._extract_location_from_detail(soup)
        
        # Extract description (fuller than listing)
        description = self._extract_description(soup)
        
        # Parse date
        start_time = self._extract_date(date_text)
        
        # Use hashlib for stable, consistent hash values across runs
        import hashlib
        event_id_base = f"{title}{start_time}".encode('utf-8')
        event_hash = hashlib.md5(event_id_base).hexdigest()[:16]
        
        event = {
            'id': f"html_frankenpost_{event_hash}",
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
        
        # Add location confidence and review flags if reviewer notes available
        if self.reviewer_notes and REVIEWER_NOTES_AVAILABLE:
            event = enhance_event_with_location_confidence(
                event, self.reviewer_notes, extraction_details
            )
        
        return event
    
    def _extract_location_from_detail(self, soup) -> tuple:
        """
        Extract venue location from detail page.
        
        Looks for:
        - H3 + Strong tag patterns for structured location
        - Iframe coordinates from embedded maps (Google Maps, OpenStreetMap, Apple Maps)
        - Location/Ort labels and their values
        - Address patterns (Street Number, ZIP City)
        - Venue name patterns
        
        Uses modular GeolocationResolver instead of hardcoded coordinate estimation.
        
        Returns:
            Tuple of (location dict, extraction_details dict) for confidence scoring
        """
        location_name = None
        full_address = None
        latitude = None
        longitude = None
        extraction_method = 'unknown'
        has_full_address = False
        has_venue_name = False
        
        # NEW Strategy 1: H3 + Strong Tag Pattern
        # Look for <h3>Location</h3> or <h3>Ort</h3> followed by <strong> tag
        h3_tags = soup.find_all('h3')
        for h3 in h3_tags:
            h3_text = h3.get_text(strip=True).lower()
            if 'location' in h3_text or 'ort' in h3_text:
                # Find the next strong tag after this h3
                strong_tag = h3.find_next('strong')
                if strong_tag:
                    strong_text = strong_tag.get_text(strip=True)
                    if strong_text and len(strong_text) > 3:
                        location_name = strong_text
                        extraction_method = 'h3_strong_tag'
                        has_venue_name = True
                        
                        # Also check for accompanying address in parent element
                        parent = strong_tag.parent
                        if parent:
                            parent_text = parent.get_text(strip=True)
                            # Look for address pattern in the parent
                            from ..scraper_utils import AddressExtractor
                            address = AddressExtractor.extract_german_address(parent_text)
                            if address:
                                full_address = address
                                has_full_address = True
                        break
        
        # NEW Strategy 2: Iframe Geolocation Extraction
        # Use CoordinateExtractor utility to avoid code duplication
        if not latitude or not longitude:
            from ..scraper_utils import CoordinateExtractor
            
            iframes = soup.find_all('iframe', src=True)
            for iframe in iframes:
                src = iframe.get('src', '').lower()
                if 'map' in src or 'geo' in src:
                    src_original = iframe.get('src', '')
                    coords = CoordinateExtractor.extract_from_iframe(src_original)
                    if coords:
                        latitude, longitude = coords
                        extraction_method = 'iframe_map'
                        break
        
        # Strategy 3: Look for location-related labels and fields
        if not location_name:
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
                            extraction_method = 'detail_page_label'
                            has_venue_name = True
                            break
                    
                    # Check within parent
                    parent_text = parent.get_text(strip=True)
                    # Remove the label itself from text
                    parent_text = parent_text.replace(keyword, '').strip()
                    if parent_text and len(parent_text) > 3:
                        location_name = parent_text
                        extraction_method = 'detail_page_label'
                        has_venue_name = True
                        break
        
        # Strategy 4: Look for address patterns (German format)
        if not has_full_address:
            from ..scraper_utils import AddressExtractor
            page_text = soup.get_text()
            address = AddressExtractor.extract_german_address(page_text)
            if address:
                full_address = address
                has_full_address = True
                # If we don't have a location name yet, use the address
                if not location_name:
                    location_name = full_address
                    extraction_method = 'address_pattern'
        
        # Strategy 5: Look for venue names in title/headings
        if not location_name:
            from ..scraper_utils import VenueDetector
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            venue_name = VenueDetector.extract_venue_from_headings(headings)
            if venue_name:
                location_name = venue_name
                extraction_method = 'venue_in_heading'
                has_venue_name = True
        
        # MODULAR COORDINATE RESOLUTION (replaces broken _estimate_coordinates)
        # Use GeolocationResolver instead of hardcoded city lookup with silent Hof default
        if self.location_normalizer:
            location = self.location_normalizer.resolve_coordinates(
                location_name=location_name,
                address=full_address,
                coordinates=(latitude, longitude) if latitude and longitude else None,
                source_name=self.name
            )
            
            # Check if coordinates need review
            needs_review = location.get('needs_review', False)
            resolution_method = location.get('resolution_method', 'unknown')
            
            # Update extraction method with resolution info
            if resolution_method != 'unknown':
                extraction_method = f"{extraction_method}+{resolution_method}"
        else:
            # Fallback if location_normalizer not available
            if latitude is not None and longitude is not None:
                # Use coordinates extracted from iframe
                location = {
                    'name': location_name if location_name else full_address if full_address else 'Unknown',
                    'lat': latitude,
                    'lon': longitude
                }
            elif location_name or full_address:
                # NO SILENT DEFAULT - Flag for editor review
                location = {
                    'name': location_name if location_name else full_address,
                    'lat': None,  # No coordinates = editor must review
                    'lon': None,
                    'needs_review': True
                }
            else:
                # Use default from config (only as last resort)
                default_loc = self.options.default_location
                if default_loc:
                    location = default_loc.copy()
                    location['needs_review'] = True  # Flag even default locations
                else:
                    raise ValueError("No location found and no default_location configured")
            
            needs_review = location.get('needs_review', False)
        
        # Build extraction details for confidence scoring
        extraction_details = {
            'has_full_address': has_full_address,
            'has_venue_name': has_venue_name,
            'has_coordinates': latitude is not None and longitude is not None,
            'needs_review': needs_review,
            'extraction_method': extraction_method,
            'known_cities': self.known_cities
        }
        
        return location, extraction_details
    
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
