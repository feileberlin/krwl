"""Event scraper module"""

import json
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from .utils import load_pending_events, save_pending_events

try:
    import requests
    from bs4 import BeautifulSoup
    import feedparser
    SCRAPING_ENABLED = True
except ImportError:
    SCRAPING_ENABLED = False
    # Note: Warning is printed only when scraping is actually attempted,
    # not at import time to avoid interference with other modules

# Try to import SmartScraper for enhanced functionality
try:
    from .smart_scraper import SmartScraper
    SMART_SCRAPER_AVAILABLE = True
except ImportError:
    SMART_SCRAPER_AVAILABLE = False


class EventScraper:
    """Scraper for community events from various sources"""
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        
        # Try to initialize SmartScraper for enhanced functionality
        self.smart_scraper = None
        if SMART_SCRAPER_AVAILABLE:
            try:
                self.smart_scraper = SmartScraper(config, base_path)
                print("✓ Enhanced scraping enabled (SmartScraper)")
            except Exception as e:
                print(f"⚠ SmartScraper initialization failed: {e}")
                self.smart_scraper = None
        
        if not SCRAPING_ENABLED:
            # Print warning when scraper is instantiated without required libraries
            print("Warning: Scraping libraries not installed.", file=sys.stderr)
            print("Install with: pip install -r requirements.txt", file=sys.stderr)
            print("Or install directly: pip install requests beautifulsoup4 lxml feedparser", file=sys.stderr)
            self.session = None
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        
    def scrape_all_sources(self):
        """Scrape events from all configured sources"""
        if not SCRAPING_ENABLED:
            print("ERROR: Scraping libraries not installed. Cannot scrape events.", file=sys.stderr)
            print("Install with: pip install -r requirements.txt", file=sys.stderr)
            print("Or install directly: pip install requests beautifulsoup4 lxml feedparser", file=sys.stderr)
            
            # Still write status file even if scraping is disabled
            status = {
                'scraped': 0,
                'added': 0,
                'duplicates': 0,
                'rejected': 0,
                'timestamp': datetime.now().isoformat(),
                'error': 'Scraping libraries not installed'
            }
            status_file = self.base_path / '.scrape_status'
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            return []
            
        pending_data = load_pending_events(self.base_path)
        new_events = []
        
        for source in self.config['scraping']['sources']:
            if not source.get('enabled', False):
                print(f"⊘ Skipping disabled source: {source['name']}")
                continue
                
            print(f"🔍 Scraping from: {source['name']}")
            try:
                events = self.scrape_source(source)
                new_events.extend(events)
                print(f"  ✓ Found {len(events)} events")
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
        
        # Load historical events for deduplication
        from .utils import load_historical_events, load_events, load_rejected_events, is_event_rejected
        historical_events = load_historical_events(self.base_path)
        published_events = load_events(self.base_path).get('events', [])
        
        # Load rejected events
        rejected_data = load_rejected_events(self.base_path)
        rejected_events = rejected_data.get('rejected_events', [])
        
        # Add new events to pending (check against pending, published, historical, and rejected)
        added_count = 0
        skipped_duplicate = 0
        skipped_rejected = 0
        for event in new_events:
            # Check if event was previously rejected
            if is_event_rejected(rejected_events, event.get('title', ''), event.get('source', '')):
                skipped_rejected += 1
                continue
            
            # Check if event exists in pending queue
            if self._event_exists(pending_data['pending_events'], event):
                skipped_duplicate += 1
                continue
            
            # Check if event exists in currently published events
            if self._event_exists(published_events, event):
                skipped_duplicate += 1
                continue
            
            # Check if event exists in historical backups
            if self._event_exists(historical_events, event):
                skipped_duplicate += 1
                continue
            
            # Event is new - add to pending
            pending_data['pending_events'].append(event)
            added_count += 1
                
        save_pending_events(self.base_path, pending_data)
        print(f"\n📊 Total: {len(new_events)} scraped, {added_count} new, {skipped_duplicate} duplicates skipped, {skipped_rejected} rejected")
        
        # Write scrape status for workflow automation
        status = {
            'scraped': len(new_events),
            'added': added_count,
            'duplicates': skipped_duplicate,
            'rejected': skipped_rejected,
            'timestamp': datetime.now().isoformat()
        }
        status_file = self.base_path / '.scrape_status'
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        return new_events
        
    def scrape_source(self, source):
        """Scrape events from a single source"""
        if not SCRAPING_ENABLED:
            return []
        
        # Try SmartScraper first for enhanced functionality
        if self.smart_scraper:
            try:
                return self.smart_scraper.scrape_source(source)
            except Exception as e:
                print(f"  ⚠ SmartScraper failed, falling back to legacy: {e}")
                # Fall through to legacy scraper
            
        # Legacy scraper
        source_type = source.get('type', 'rss')
        
        if source_type == 'rss':
            return self._scrape_rss(source)
        elif source_type == 'api':
            return self._scrape_api(source)
        elif source_type == 'html':
            return self._scrape_html(source)
        elif source_type == 'facebook':
            return self._scrape_facebook(source)
        else:
            print(f"  ⚠ Unknown source type: {source_type}")
            return []
            
    def _scrape_rss(self, source):
        """Scrape RSS feed"""
        events = []
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries:
                event = self._parse_rss_entry(entry, source)
                if event:
                    events.append(event)
        except Exception as e:
            print(f"    RSS error: {str(e)}")
        return events
        
    def _scrape_api(self, source):
        """Scrape from API"""
        events = []
        try:
            response = self.session.get(source['url'], timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # API-specific parsing would go here
            # This is a generic handler
            if isinstance(data, list):
                for item in data:
                    event = self._parse_api_item(item, source)
                    if event:
                        events.append(event)
        except Exception as e:
            print(f"    API error: {str(e)}")
        return events
        
    def _scrape_html(self, source):
        """Scrape HTML page"""
        events = []
        try:
            response = self.session.get(source['url'], timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Generic HTML event scraping
            # Looks for common patterns in event listings
            events = self._extract_events_from_html(soup, source)
        except Exception as e:
            print(f"    HTML error: {str(e)}")
        return events
        
    def _scrape_facebook(self, source):
        """Scrape Facebook page"""
        # Note: Direct Facebook scraping is difficult due to authentication
        # This is a placeholder that attempts basic scraping
        # For production, consider using Facebook Graph API with proper credentials
        print(f"    ⚠ Facebook scraping requires authentication")
        print(f"    → Consider using manual event creation or Graph API")
        return []
        
    def _parse_rss_entry(self, entry, source):
        """Parse RSS feed entry into event format"""
        try:
            # Extract basic info
            title = entry.get('title', 'Untitled Event')
            description = entry.get('summary', entry.get('description', ''))
            link = entry.get('link', '')
            
            # Try to extract date
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                start_time = datetime(*published[:6]).isoformat()
            else:
                # Default to tomorrow if no date
                start_time = (datetime.now() + timedelta(days=1)).replace(hour=18, minute=0).isoformat()
            
            # Try to extract location from description or use default
            location = self._extract_location_from_text(description, source)
            
            return {
                'id': f"rss_{source['name'].lower().replace(' ', '_')}_{hash(title + start_time)}",
                'title': title,
                'description': self._clean_html(description)[:500],  # Limit description
                'location': location,
                'start_time': start_time,
                'end_time': None,
                'url': link,
                'source': source['name'],
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        except Exception as e:
            print(f"      Error parsing RSS entry: {str(e)}")
            return None
            
    def _parse_api_item(self, item, source):
        """Parse API response item into event format"""
        # Generic API parsing - would need to be customized per API
        try:
            return {
                'id': f"api_{source['name'].lower().replace(' ', '_')}_{item.get('id', hash(str(item)))}",
                'title': item.get('title', item.get('name', 'Untitled Event')),
                'description': item.get('description', '')[:500],
                'location': self._extract_location_from_api(item, source),
                'start_time': item.get('start_time', item.get('date')),
                'end_time': item.get('end_time'),
                'url': item.get('url', item.get('link')),
                'source': source['name'],
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        except Exception as e:
            print(f"      Error parsing API item: {str(e)}")
            return None
            
    def _extract_events_from_html(self, soup, source):
        """Extract events from HTML page using common patterns"""
        events = []
        
        # Common selectors for event listings
        selectors = [
            '.event', '.veranstaltung', '[class*="event"]',
            '[class*="calendar"]', 'article', '.item'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items[:20]:  # Limit to 20 events per page
                    event = self._parse_html_event(item, source)
                    if event:
                        events.append(event)
                break  # Stop after finding first matching selector
                
        return events
        
    def _parse_html_event(self, element, source):
        """Parse HTML element into event format"""
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else 'Untitled Event'
            
            # Extract description
            desc_elem = element.find(['p', 'div', 'span'])
            description = desc_elem.get_text(strip=True)[:500] if desc_elem else ''
            
            # Extract link
            link_elem = element.find('a', href=True)
            url = urljoin(source['url'], link_elem['href']) if link_elem else source['url']
            
            # Extract date (look for date patterns)
            date_text = element.get_text()
            start_time = self._extract_date_from_text(date_text)
            
            # Use default location from config or source
            location = self._extract_location_from_text(description, source)
            
            if title and title != 'Untitled Event':
                return {
                    'id': f"html_{source['name'].lower().replace(' ', '_')}_{hash(title + start_time)}",
                    'title': title[:200],
                    'description': description,
                    'location': location,
                    'start_time': start_time,
                    'end_time': None,
                    'url': url,
                    'source': source['name'],
                    'scraped_at': datetime.now().isoformat(),
                    'status': 'pending'
                }
        except Exception as e:
            print(f"      Error parsing HTML element: {str(e)}")
        return None
        
    def _extract_date_from_text(self, text):
        """Extract date from text using patterns"""
        # Look for common date patterns
        patterns = [
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if '.' in pattern:
                        day, month, year = match.groups()
                        date = datetime(int(year), int(month), int(day), 18, 0)
                    else:
                        year, month, day = match.groups()
                        date = datetime(int(year), int(month), int(day), 18, 0)
                    return date.isoformat()
                except ValueError:
                    pass
        
        # Default to next week if no date found
        return (datetime.now() + timedelta(days=7)).replace(hour=18, minute=0).isoformat()
        
    def _extract_location_from_text(self, text, source):
        """Extract location from text or use default"""
        # Try to find addresses or location names
        # For now, use default location from config
        default_loc = self.config.get('map', {}).get('default_center', {})
        return {
            'name': source.get('notes', source['name']),
            'lat': default_loc.get('lat', 50.3167),
            'lon': default_loc.get('lon', 11.9167)
        }
        
    def _extract_location_from_api(self, item, source):
        """Extract location from API response"""
        if 'location' in item:
            loc = item['location']
            return {
                'name': loc.get('name', source['name']),
                'lat': loc.get('lat', loc.get('latitude', 50.3167)),
                'lon': loc.get('lon', loc.get('longitude', 11.9167))
            }
        return self._extract_location_from_text('', source)
        
    def _clean_html(self, html_text):
        """Remove HTML tags from text"""
        if not html_text:
            return ''
        soup = BeautifulSoup(html_text, 'lxml')
        return soup.get_text(strip=True)
        
    def _event_exists(self, events, new_event):
        """Check if event already exists in list"""
        for event in events:
            if (event.get('title') == new_event.get('title') and
                event.get('start_time') == new_event.get('start_time')):
                return True
        return False
        
    def create_manual_event(self, title, description, location_name, lat, lon, 
                           start_time, end_time=None, url=None):
        """Create an event manually"""
        event = {
            'id': f"manual_{datetime.now().timestamp()}",
            'title': title,
            'description': description,
            'location': {
                'name': location_name,
                'lat': lat,
                'lon': lon
            },
            'start_time': start_time,
            'end_time': end_time,
            'url': url,
            'source': 'manual',
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Add to pending events
        pending_data = load_pending_events(self.base_path)
        pending_data['pending_events'].append(event)
        save_pending_events(self.base_path, pending_data)
        
        return event
