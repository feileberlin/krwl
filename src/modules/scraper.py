"""Event scraper module with robust error handling and retry logic"""

import json
import logging
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from .utils import load_pending_events, save_pending_events
from .exceptions import SourceUnavailableError, NetworkError, ParsingError

# Configure module logger
logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    import feedparser
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
    SCRAPING_ENABLED = True
    
    # Define retry decorator for use in class methods
    def make_retry_decorator():
        return retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout)),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
    
except ImportError as e:
    SCRAPING_ENABLED = False
    SCRAPING_IMPORT_ERROR = e  # Store error for later reporting
    # Note: Warning is printed only when scraping is actually attempted,
    # not at import time to avoid interference with other modules
    
    # Dummy decorator when libraries not available
    def make_retry_decorator():
        def dummy_decorator(func):
            return func
        return dummy_decorator

# Try to import SmartScraper for enhanced functionality
try:
    from .smart_scraper import SmartScraper
    SMART_SCRAPER_AVAILABLE = True
except ImportError:
    SMART_SCRAPER_AVAILABLE = False


class EventScraper:
    """Scraper for community events from various sources with robust error handling"""
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.failed_sources = []  # Track failed sources for reporting
        self._scraping_warning_shown = False  # Track if warning has been shown
        
        # Try to initialize SmartScraper for enhanced functionality
        self.smart_scraper = None
        if SMART_SCRAPER_AVAILABLE:
            try:
                self.smart_scraper = SmartScraper(config, base_path)
                logger.info("Enhanced scraping enabled (SmartScraper)")
            except Exception as e:
                logger.warning(f"SmartScraper initialization failed: {e}")
                self.smart_scraper = None
        
        if not SCRAPING_ENABLED:
            # Delay warning until scraping is actually attempted (not during capabilities check)
            self.session = None
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            # Set default timeout for all requests
            self.timeout = 30
    
    def _check_scraping_available(self):
        """Check if scraping libraries are available and show warning if not."""
        if not SCRAPING_ENABLED and not self._scraping_warning_shown:
            logger.error("Scraping libraries not installed.")
            logger.error("Install with: pip install -r requirements.txt")
            logger.error("Or install directly: pip install requests beautifulsoup4 lxml feedparser")
            self._scraping_warning_shown = True
            return False
        return SCRAPING_ENABLED
        
    def _write_scrape_status(self, scraped_count, added_count, duplicate_count, rejected_count, error=None):
        """Write scrape status file for workflow automation"""
        status = {
            'scraped': scraped_count,
            'added': added_count,
            'duplicates': duplicate_count,
            'rejected': rejected_count,
            'timestamp': datetime.now().isoformat()
        }
        if error:
            status['error'] = error
        
        status_file = self.base_path / '.scrape_status'
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def _write_pending_count(self):
        """
        Update pending count in events.json
        This allows frontend to read pending count from the same file it already loads
        """
        from .utils import update_pending_count_in_events
        update_pending_count_in_events(self.base_path)
        
        # Get the count for logging
        pending_data = load_pending_events(self.base_path)
        pending_count = len(pending_data.get('pending_events', []))
        logger.info(f"Updated pending count in events.json: {pending_count} events")
    
    def scrape_all_sources(self):
        """Scrape events from all configured sources with graceful degradation"""
        if not self._check_scraping_available():
            # Write status file even if scraping is disabled
            self._write_scrape_status(0, 0, 0, 0, error='Scraping libraries not installed')
            # Still generate pending count JSON even if scraping failed
            self._write_pending_count()
            return []
        
        logger.info("Starting event scraping from all sources")
        pending_data = load_pending_events(self.base_path)
        new_events = []
        self.failed_sources = []
        
        for source in self.config['scraping']['sources']:
            if not source.get('enabled', False):
                logger.debug(f"Skipping disabled source: {source['name']}")
                continue
            
            logger.info(f"Scraping from: {source['name']}")
            try:
                events = self.scrape_source(source)
                new_events.extend(events)
                logger.info(f"Found {len(events)} events from {source['name']}")
            except SourceUnavailableError as e:
                logger.error(f"Source unavailable: {e}")
                self.failed_sources.append({
                    'name': source['name'],
                    'error': str(e),
                    'type': 'unavailable'
                })
            except NetworkError as e:
                logger.error(f"Network error: {e}")
                self.failed_sources.append({
                    'name': source['name'],
                    'error': str(e),
                    'type': 'network'
                })
            except ParsingError as e:
                logger.error(f"Parsing error: {e}")
                self.failed_sources.append({
                    'name': source['name'],
                    'error': str(e),
                    'type': 'parsing'
                })
            except Exception as e:
                logger.exception(f"Unexpected error scraping {source['name']}: {e}")
                self.failed_sources.append({
                    'name': source['name'],
                    'error': str(e),
                    'type': 'unknown'
                })
        
        # Report on failed sources
        if self.failed_sources:
            logger.warning(f"{len(self.failed_sources)} source(s) failed to scrape")
            for failed in self.failed_sources:
                logger.warning(f"  - {failed['name']}: {failed['error']}")
        
        # Load historical events for deduplication
        from .utils import load_historical_events, load_events, load_rejected_events, is_event_rejected
        historical_events = load_historical_events(self.base_path)
        published_events = load_events(self.base_path).get('events', [])
        
        # Load rejected events
        rejected_data = load_rejected_events(self.base_path)
        rejected_events = rejected_data.get('rejected_events', [])
        
        # OPTIMIZATION: Build lookup sets once for all duplicate checks
        # This avoids rebuilding sets for every scraped event
        pending_keys = {
            (event.get('title'), event.get('start_time'))
            for event in pending_data['pending_events']
        }
        published_keys = {
            (event.get('title'), event.get('start_time'))
            for event in published_events
        }
        historical_keys = {
            (event.get('title'), event.get('start_time'))
            for event in historical_events
        }
        rejected_keys = {
            (rejected.get('title', '').lower().strip(), 
             rejected.get('source', '').lower().strip())
            for rejected in rejected_events
        }
        
        # Add new events to pending (check against pending, published, historical, and rejected)
        added_count = 0
        skipped_duplicate = 0
        skipped_rejected = 0
        skipped_invalid = 0
        
        for event in new_events:
            # Check if event was previously rejected (using pre-built set)
            event_key_rejected = (
                event.get('title', '').lower().strip(),
                event.get('source', '').lower().strip()
            )
            if event_key_rejected in rejected_keys:
                skipped_rejected += 1
                continue
            
            # Check for duplicates using pre-built sets (O(1) lookups)
            event_key = (event.get('title'), event.get('start_time'))
            
            if event_key in pending_keys:
                skipped_duplicate += 1
                continue
            
            if event_key in published_keys:
                skipped_duplicate += 1
                continue
            
            if event_key in historical_keys:
                skipped_duplicate += 1
                continue
            
            # Validate and add event (this ensures data integrity)
            if self._validate_and_add_event(event, pending_data):
                added_count += 1
                # Update the pending_keys set so we don't add duplicates within this batch
                pending_keys.add(event_key)
            else:
                skipped_invalid += 1
        
        # Only save (and update timestamp) if events were actually added
        if added_count > 0:
            save_pending_events(self.base_path, pending_data)
        
        logger.info(
            f"Scraping complete: {len(new_events)} scraped, "
            f"{added_count} new, {skipped_duplicate} duplicates, "
            f"{skipped_rejected} rejected, {skipped_invalid} invalid"
        )
        
        # Write scrape status for workflow automation
        error_summary = None
        if self.failed_sources:
            error_summary = f"{len(self.failed_sources)} sources failed"
        self._write_scrape_status(
            len(new_events), added_count, skipped_duplicate, 
            skipped_rejected, error=error_summary
        )
        
        # Write pending count JSON for frontend notifications
        self._write_pending_count()
        
        return new_events
        
    def scrape_source(self, source):
        """Scrape events from a single source with error handling"""
        if not SCRAPING_ENABLED:
            return []
        
        # Try SmartScraper first for enhanced functionality
        if self.smart_scraper:
            try:
                return self.smart_scraper.scrape_source(source)
            except Exception as e:
                logger.warning(f"SmartScraper failed for {source['name']}, falling back to legacy: {e}")
                # Fall through to legacy scraper
            
        # Legacy scraper
        source_type = source.get('type', 'rss')
        
        try:
            if source_type == 'rss':
                return self._scrape_rss(source)
            elif source_type == 'api':
                return self._scrape_api(source)
            elif source_type == 'html':
                return self._scrape_html(source)
            elif source_type == 'facebook':
                return self._scrape_facebook(source)
            else:
                logger.warning(f"Unknown source type: {source_type}")
                return []
        except requests.exceptions.Timeout:
            raise NetworkError(source['url'], "Request timed out", None)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(source['url'], f"Connection failed: {e}", None)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            raise NetworkError(source['url'], f"HTTP error: {e}", status_code)
        except Exception as e:
            raise SourceUnavailableError(source['name'], source['url'], str(e))
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> 'requests.Response':
        """
        Make HTTP request with retry logic
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If request fails after retries
        """
        # Apply retry decorator dynamically
        @make_retry_decorator()
        def _do_request():
            # Set timeout if not provided
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout

            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        try:
            return _do_request()
        except requests.exceptions.Timeout as e:
            # Raised after all retry attempts are exhausted
            raise NetworkError(url, "Request timed out after retries", None) from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(url, f"Connection failed after retries: {e}", None) from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if getattr(e, "response", None) is not None else None
            raise NetworkError(url, f"HTTP error after retries: {e}", status_code) from e
        except requests.exceptions.RequestException as e:
            # Fallback for other request-related errors after retries
            raise NetworkError(url, f"Request failed after retries: {e}", None) from e
            
    def _scrape_rss(self, source):
        """Scrape RSS feed with error handling"""
        events = []
        try:
            logger.debug(f"Parsing RSS feed: {source['url']}")
            feed = feedparser.parse(source['url'])
            
            if feed.bozo and not feed.entries:
                # Feed has parsing errors and no entries
                raise ParsingError('RSS', f"Feed parse error: {feed.bozo_exception}", None)
            
            for entry in feed.entries:
                try:
                    event = self._parse_rss_entry(entry, source)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse RSS entry: {e}", extra={
                        'source': source['name'],
                        'entry_title': entry.get('title', 'Unknown')
                    })
            
            logger.debug(f"Successfully parsed {len(events)} events from RSS")
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError('RSS', str(e), None)
        
        return events
        
    def _scrape_api(self, source):
        """Scrape from API with error handling and retry logic"""
        events = []
        try:
            logger.debug(f"Fetching from API: {source['url']}")
            response = self._make_request(source['url'])
            data = response.json()
            
            # API-specific parsing would go here
            # This is a generic handler
            if isinstance(data, list):
                for item in data:
                    try:
                        event = self._parse_api_item(item, source)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to parse API item: {e}", extra={
                            'source': source['name'],
                            'item': str(item)[:100]
                        })
            
            logger.debug(f"Successfully parsed {len(events)} events from API")
        except NetworkError:
            raise
        except Exception as e:
            raise ParsingError('API', str(e), str(data)[:200] if 'data' in locals() else None)
        
        return events
        
    def _scrape_html(self, source):
        """Scrape HTML page with error handling and retry logic"""
        events = []
        try:
            logger.debug(f"Fetching HTML page: {source['url']}")
            response = self._make_request(source['url'])
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Generic HTML event scraping
            # Looks for common patterns in event listings
            events = self._extract_events_from_html(soup, source)
            logger.debug(f"Successfully parsed {len(events)} events from HTML")
        except NetworkError:
            raise
        except Exception as e:
            content_sample = response.content[:200].decode('utf-8', errors='ignore') if 'response' in locals() else None
            raise ParsingError('HTML', str(e), content_sample)
        
        return events
        
    def _scrape_facebook(self, source):
        """Scrape Facebook page (requires authentication)"""
        # Note: Direct Facebook scraping is difficult due to authentication
        # This is a placeholder that attempts basic scraping
        # For production, consider using Facebook Graph API with proper credentials
        logger.warning(f"Facebook scraping requires authentication for {source['name']}")
        logger.info("Consider using manual event creation or Graph API")
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
            logger.warning(f"Error parsing RSS entry: {e}", extra={
                'source': source['name'],
                'entry_title': entry.get('title', 'Unknown')
            })
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
            logger.warning(f"Error parsing API item: {e}", extra={
                'source': source['name'],
                'item': str(item)[:100]
            })
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
            logger.warning(f"Error parsing HTML element: {e}", extra={
                'source': source['name']
            })
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
        
    def _validate_and_add_event(self, event_data: dict, pending_data: dict) -> bool:
        """
        Validate event data using Pydantic and add to pending if valid
        
        Uses AI categorization (if enabled) to assign category before validation.
        
        Args:
            event_data: Event dictionary to validate
            pending_data: Pending events data structure
            
        Returns:
            True if event was added, False otherwise
        """
        try:
            from .models import validate_event_data
            from .event_schema import EventSchema
            
            # Add category using AI if not already present
            if 'category' not in event_data or not event_data['category']:
                # Initialize EventSchema with AI categorization
                schema = EventSchema(self.config, self.base_path)
                
                # Infer category (uses AI if available)
                event_data['category'] = schema._infer_category(
                    event_data.get('title', ''),
                    event_data.get('description', '')
                )
            
            # Validate event structure
            validated_event = validate_event_data(event_data)
            
            # Convert back to dict for storage
            event_dict = validated_event.model_dump()
            pending_data['pending_events'].append(event_dict)
            
            logger.debug(f"Event validated and added: {event_dict['title']} (category: {event_dict.get('category', 'none')})")
            return True
            
        except ValueError as e:
            logger.warning(f"Event validation failed: {e}", extra={
                'event_title': event_data.get('title', 'Unknown'),
                'event_id': event_data.get('id', 'Unknown')
            })
            return False
    
    def _clean_html(self, html_text):
        """Remove HTML tags from text"""
        if not html_text:
            return ''
        soup = BeautifulSoup(html_text, 'lxml')
        return soup.get_text(strip=True)
        
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
    
    def get_supported_source_types(self):
        """
        Get list of supported source types for workflow introspection
        
        Returns:
            list: Supported source types (e.g., ['rss', 'html', 'api', 'facebook'])
        """
        return ['rss', 'html', 'api', 'facebook']
    
    def get_enabled_sources(self):
        """
        Get list of enabled sources from configuration
        
        Returns:
            list: Enabled source names and types
        """
        enabled = []
        for source in self.config.get('scraping', {}).get('sources', []):
            if source.get('enabled', False):
                enabled.append({
                    'name': source['name'],
                    'type': source.get('type', 'rss'),
                    'url': source['url']
                })
        return enabled
    
    def get_scraping_schedule(self):
        """
        Get scraping schedule from configuration for workflow setup
        
        Returns:
            dict: Schedule information (timezone, times)
        """
        return self.config.get('scraping', {}).get('schedule', {
            'timezone': 'Europe/Berlin',
            'times': ['04:00', '16:00']
        })
    
    def get_scraper_capabilities(self):
        """
        Get comprehensive scraper capabilities for workflow adaptation
        
        Returns:
            dict: Scraper capabilities including source types, methods, and configuration
        """
        capabilities = {
            'supported_source_types': self.get_supported_source_types(),
            'enabled_sources': self.get_enabled_sources(),
            'schedule': self.get_scraping_schedule(),
            'smart_scraper_available': SMART_SCRAPER_AVAILABLE,
            'scraping_libraries_installed': SCRAPING_ENABLED,
            'methods': {
                'scrape_all_sources': 'Main method to scrape all configured sources',
                'scrape_source': 'Scrape a single source',
                'create_manual_event': 'Create event manually without scraping'
            }
        }
        return capabilities
