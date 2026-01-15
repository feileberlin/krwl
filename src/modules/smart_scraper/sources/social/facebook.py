"""Facebook events scraper without API.

This module scrapes Facebook public pages for events and posts that may contain
event information. It uses web scraping techniques and integrates with the
image_analyzer module to extract event data from posted flyers via OCR.

Note: This scraper works with public pages only and does not require
Facebook API credentials. It respects rate limits and follows ethical
scraping practices.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import re
import json
import hashlib
from ...base import BaseSource, SourceOptions
from ...date_utils import resolve_relative_date, extract_time_from_text, resolve_year_for_date
from ...source_cache import SourceCache

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# Import image analyzer for OCR-based flyer extraction
try:
    from ...image_analyzer import ImageAnalyzer
    from ...image_analyzer.ocr import extract_event_data_from_image, is_ocr_available
    IMAGE_ANALYZER_AVAILABLE = True
except ImportError:
    IMAGE_ANALYZER_AVAILABLE = False


class FacebookSource(BaseSource):
    """Facebook events scraper using web scraping (no API required).
    
    This scraper extracts events from:
    1. Public Facebook event pages (/events URLs)
    2. Regular posts that may contain event flyers (analyzed via OCR)
    3. Mobile Facebook pages (m.facebook.com) for lighter HTML
    
    Features:
    - OCR scanning of posted images for event flyers
    - Date/time extraction from post text and images
    - German and English language support
    - When scan_posts is enabled, processes the full timeline feed
    """
    
    DEFAULT_TITLE_PREFIX = "Event from "
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path: Optional[Path] = None,
                 ai_providers: Optional[Dict[str, Any]] = None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = SCRAPING_AVAILABLE
        options_config = source_config.get('options') or {}
        self.scan_posts = bool(options_config.get('scan_posts', False))
        self.force_scan = bool(options_config.get('force_scan', False))
        self.post_cache = self._init_post_cache()
        
        # Initialize session with realistic headers
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
        
        # Initialize image analyzer for OCR
        self.image_analyzer = None
        if IMAGE_ANALYZER_AVAILABLE:
            try:
                img_config = {
                    'ocr_enabled': True,
                    'languages': ['eng', 'deu']
                }
                self.image_analyzer = ImageAnalyzer(img_config, ai_providers=self.ai_providers)
            except Exception as e:
                print(f"    ⚠ Image analyzer init failed: {e}")
        
        # OCR settings
        self.ocr_enabled = options_config.get('ocr_enabled', True)
        self.min_ocr_confidence = options_config.get('min_ocr_confidence', 0.3)
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Facebook page.
        
        Returns:
            List of event dictionaries
        """
        if not self.available:
            print(f"    ⚠ Requests/BeautifulSoup not available")
            return []
        
        events = []
        
        # Determine the type of URL and scrape accordingly
        url_type = self._detect_url_type(self.url)
        
        if url_type == 'events':
            # Direct events page
            events.extend(self._scrape_events_page())
            if self.scan_posts:
                page_url = self._get_page_url(self.url)
                events.extend(self._scrape_page_posts(page_url=page_url))
        elif url_type == 'page':
            # Regular page - look for posts with event info
            events.extend(self._scrape_page_posts())
        elif url_type == 'profile':
            # Profile page
            events.extend(self._scrape_profile_posts())
        else:
            # Try both approaches
            events.extend(self._scrape_events_page())
            events.extend(self._scrape_page_posts())
        
        # Deduplicate events
        events = self._deduplicate_events(events)
        
        print(f"    📸 OCR enabled: {self.ocr_enabled and IMAGE_ANALYZER_AVAILABLE}")
        print(f"    📊 Found {len(events)} potential events")
        
        return events
    
    def _detect_url_type(self, url: str) -> str:
        """Detect the type of Facebook URL.
        
        Args:
            url: Facebook URL to analyze
            
        Returns:
            URL type: 'events', 'page', 'profile', or 'unknown'
        """
        url_lower = url.lower()
        
        if '/events' in url_lower:
            return 'events'
        elif '/people/' in url_lower or 'profile.php' in url_lower:
            return 'profile'
        elif any(x in url_lower for x in ['/pages/', 'facebook.com/']):
            return 'page'
        
        return 'unknown'
    
    def _scrape_events_page(self) -> List[Dict[str, Any]]:
        """Scrape events from a Facebook events page.
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        # Try mobile version first (lighter HTML)
        mobile_url = self._get_mobile_url(self.url)
        
        try:
            response = self.session.get(mobile_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try to find event containers
            events.extend(self._extract_events_from_html(soup))
            
        except Exception as e:
            print(f"    ⚠ Events page scrape error: {e}")
        
        return events
    
    def _scrape_page_posts(self, page_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape posts from a Facebook page that may contain event info.
        
        Returns:
            List of event dictionaries extracted from posts
        """
        events = []
        
        # Try mobile version
        base_url = page_url or self.url
        mobile_url = self._get_mobile_url(base_url)
        
        try:
            response = self.session.get(mobile_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract posts
            posts = self._extract_posts(soup)
            
            # Process each post for event information
            events.extend(self._process_posts(posts))
            
        except Exception as e:
            print(f"    ⚠ Page posts scrape error: {e}")
        
        return events
    
    def _scrape_profile_posts(self) -> List[Dict[str, Any]]:
        """Scrape posts from a Facebook profile.
        
        Returns:
            List of event dictionaries
        """
        # Similar to page posts, but normalize to base profile URL
        return self._scrape_page_posts(page_url=self._get_page_url(self.url))
    
    def _get_mobile_url(self, url: str) -> str:
        """Convert URL to mobile Facebook version.
        
        Args:
            url: Original Facebook URL
            
        Returns:
            Mobile Facebook URL
        """
        return url.replace('www.facebook.com', 'm.facebook.com').replace('facebook.com', 'm.facebook.com')
    
    def _get_page_url(self, url: str) -> str:
        """Convert event URLs to base page URLs for post scraping."""
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]
        if 'events' in path_parts:
            path_parts = path_parts[:path_parts.index('events')]
        if 'upcoming_hosted_events' in path_parts:
            path_parts = path_parts[:path_parts.index('upcoming_hosted_events')]
        new_path = f"/{'/'.join(path_parts)}" if path_parts else ''
        return parsed._replace(path=new_path, params='', query='', fragment='').geturl()
    
    def _init_post_cache(self) -> Optional[SourceCache]:
        """Initialize persistent cache for processed posts."""
        if not self.base_path:
            return None
        
        cache_dir = self.base_path / "data" / "scraper_cache"
        source_slug = self.name.lower().replace(' ', '_')
        cache_path = cache_dir / f"facebook_posts_{source_slug}.json"
        cache = SourceCache(cache_path=cache_path)
        cache.load()
        return cache
    
    def _get_post_cache_key(self, post: Dict[str, Any]) -> Optional[str]:
        """Build a stable cache key for a post."""
        text = post.get('text', '') or ''
        timestamp = post.get('timestamp') or ''
        links = post.get('links', []) or []
        images = post.get('images', []) or []
        if not any([text, timestamp, links, images]):
            return None
        
        payload = {
            "name": self.name,
            "timestamp": timestamp,
            "text": text,
            "links": links,
            "images": images
        }
        hash_input = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    
    def _should_skip_post(self, post_key: Optional[str]) -> bool:
        """Check if post should be skipped based on cache."""
        if not post_key or not self.post_cache or self.force_scan:
            return False
        return self.post_cache.is_processed(post_key)
    
    def _process_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert posts to events with caching."""
        events = []
        
        for post in posts:
            post_key = self._get_post_cache_key(post)
            if self._should_skip_post(post_key):
                continue
            
            event = self._convert_post_to_event(post)
            if event:
                events.append(event)
                if self.post_cache and post_key:
                    self.post_cache.mark_processed(post_key)
        
        if self.post_cache:
            self.post_cache.save()
        
        return events
    
    def _is_future_event(self, start_time: Optional[str]) -> bool:
        """Check if start_time is in the future."""
        if not start_time:
            return True
        
        try:
            event_date = datetime.fromisoformat(str(start_time).replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            return False
        
        if event_date.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(event_date.tzinfo)
        return event_date >= now
    
    def _is_past_start_time(self, start_time: Optional[str]) -> bool:
        """Check if start_time exists and is in the past."""
        return bool(start_time) and not self._is_future_event(start_time)
    
    def _extract_events_from_html(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract events from HTML soup.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        # Common event container selectors
        selectors = [
            '[data-testid="event-row"]',
            '.event',
            '[class*="event"]',
            'a[href*="/events/"]',
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    event = self._parse_event_element(item)
                    if event:
                        events.append(event)
                if events:
                    break
        
        return events
    
    def _extract_posts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract posts from page HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of post data dictionaries
        """
        posts = []
        
        # Mobile Facebook post selectors
        selectors = [
            'article',
            '[data-ft]',
            '.story',
            '[role="article"]',
            'div[class*="userContent"]',
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    post = self._parse_post_element(item)
                    if post:
                        posts.append(post)
                if posts:
                    break
        
        return posts
    
    def _parse_event_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse an event HTML element into event data.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Event dictionary or None
        """
        try:
            # Extract title
            title = None
            for tag in ['h2', 'h3', 'h4', 'a', 'span']:
                title_elem = element.find(tag)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 3:
                        break
            
            if not title:
                return None
            
            # Extract URL
            url = None
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if '/events/' in href:
                    url = urljoin('https://www.facebook.com', href)
            
            # Extract date/time from text
            text = element.get_text()
            start_time = self._extract_datetime_from_text(text)
            
            # Extract description
            description = self._clean_text(text)[:500]
            
            # Generate unique ID
            event_id = self._generate_event_id(title, start_time)
            
            return {
                'id': event_id,
                'title': title[:200],
                'description': description,
                'location': self._get_default_location(),
                'start_time': start_time,
                'end_time': None,
                'url': url or self.url,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending',
                'extraction_method': 'html_event'
            }
        except Exception as e:
            print(f"      Error parsing event element: {e}")
            return None
    
    def _parse_post_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse a post HTML element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Post data dictionary or None
        """
        try:
            post = {
                'text': '',
                'images': [],
                'links': [],
                'timestamp': None
            }
            
            # Extract text content
            text_elem = element.find(['p', 'div', 'span'])
            if text_elem:
                post['text'] = text_elem.get_text(strip=True)
            
            # Extract images
            for img in element.find_all('img', src=True):
                src = img.get('src', '') or img.get('data-src', '')
                if src and 'emoji' not in src.lower() and 'icon' not in src.lower():
                    post['images'].append(src)
            
            # Extract links
            for link in element.find_all('a', href=True):
                href = link['href']
                if href and not href.startswith('#'):
                    post['links'].append(href)
            
            # Look for timestamp
            time_elem = element.find('abbr') or element.find('time')
            if time_elem:
                post['timestamp'] = time_elem.get('data-utime') or time_elem.get('datetime')
            
            return post if post['text'] or post['images'] else None
            
        except Exception as e:
            print(f"      Error parsing post element: {e}")
            return None
    
    def _convert_post_to_event(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a post to an event if it contains event information.
        
        This method analyzes post text and images to determine if the post
        is about an event, and extracts event details.
        
        Args:
            post: Post data dictionary
            
        Returns:
            Event dictionary or None if not an event
        """
        # Check if post text contains event indicators
        text = post.get('text', '')
        has_event_indicators = self._has_event_indicators(text)
        
        # Analyze images for event flyers using OCR
        image_event_data = None
        if self.ocr_enabled and self.image_analyzer and post.get('images'):
            image_event_data = self._analyze_post_images(post['images'])
        
        # Decide if this is an event
        if not has_event_indicators and not image_event_data:
            return None
        
        # Build event from combined data
        event = self._build_event_from_post(post, image_event_data)
        return event
    
    def _has_event_indicators(self, text: str) -> bool:
        """Check if text contains event-related keywords.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if event indicators found
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Event keywords (German + English)
        event_keywords = [
            # German
            'veranstaltung', 'konzert', 'live', 'party', 'festival',
            'ausstellung', 'vernissage', 'lesung', 'workshop', 'theater',
            'eintritt', 'einlass', 'beginn', 'uhr', 'tickets',
            'kommt vorbei', 'wir laden ein', 'freuen uns',
            # English
            'event', 'concert', 'show', 'exhibition', 'opening',
            'admission', 'entry', 'doors', 'tickets', 'join us',
        ]
        
        # Check for keywords
        keyword_count = sum(1 for kw in event_keywords if kw in text_lower)
        
        # Check for date/time patterns
        has_date = bool(re.search(r'\d{1,2}\.\d{1,2}\.(\d{4}|\d{2})?', text))
        has_time = bool(re.search(r'\d{1,2}[:.]\d{2}\s*(?:uhr)?|\d{1,2}\s*uhr', text_lower))
        
        return keyword_count >= 2 or (keyword_count >= 1 and (has_date or has_time))
    
    def _analyze_post_images(self, image_urls: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze post images for event flyer content using OCR.
        
        Args:
            image_urls: List of image URLs
            
        Returns:
            Best event data extracted from images or None
        """
        if not self.image_analyzer:
            return None
        
        best_result = None
        best_confidence = 0.0
        
        for url in image_urls[:3]:  # Limit to first 3 images
            try:
                result = self.image_analyzer.analyze_url(url, timeout=10)
                if result and result.get('ocr_confidence', 0) > best_confidence:
                    best_confidence = result.get('ocr_confidence', 0)
                    best_result = result
            except Exception as e:
                print(f"      OCR analysis error: {e}")
                continue
        
        # Only return if confidence is above threshold
        if best_result and best_confidence >= self.min_ocr_confidence:
            return best_result
        
        return None
    
    def _build_event_from_post(self, post: Dict[str, Any], 
                                image_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build event dictionary from post and image analysis data.
        
        Args:
            post: Post data
            image_data: OCR analysis data from images
            
        Returns:
            Event dictionary
        """
        # Extract title - prefer OCR title hint, fallback to first line of post
        title = None
        if image_data and image_data.get('title_hint'):
            title = image_data['title_hint']
        elif post.get('text'):
            # Use first meaningful line as title
            lines = post['text'].split('\n')
            for line in lines:
                line = line.strip()
                if line and 3 < len(line) < 150:
                    title = line
                    break
        
        if not title:
            title = self._default_event_title()
        
        # Extract date/time - combine text and image data
        start_time = None
        
        # Try image OCR data first (usually more accurate for flyers)
        if image_data:
            if image_data.get('dates_found'):
                date_str = image_data['dates_found'][0]
                time_str = image_data['times_found'][0] if image_data.get('times_found') else None
                start_time = self._parse_date_time(date_str, time_str)
        
        # Fallback to post text
        if not start_time:
            start_time = self._extract_datetime_from_text(post.get('text', ''))
        
        if self._is_past_start_time(start_time):
            return None
        
        if not start_time:
            ai_text = ' '.join(
                value for value in [
                    post.get('text', ''),
                    image_data.get('ocr_text') if image_data else ''
                ] if value
            )
            ai_details = self._ai_extract_event_details(ai_text)
            if ai_details:
                start_time = ai_details.get('start_time')
                if title == self._default_event_title() and ai_details.get('title'):
                    title = ai_details['title']
                if self._is_past_start_time(start_time):
                    return None
        
        # Default to next week if no date found
        if not start_time:
            start_time = (datetime.now() + timedelta(days=7)).replace(hour=20, minute=0).isoformat()
        
        # Build description
        description_parts = []
        if post.get('text'):
            description_parts.append(post['text'][:300])
        if image_data and image_data.get('ocr_text'):
            description_parts.append(f"\n[From flyer]: {image_data['ocr_text'][:200]}")
        
        description = '\n'.join(description_parts)[:500]
        
        # Extract category from keywords
        category = self.options.category
        if not category and image_data and image_data.get('keywords'):
            keywords = image_data['keywords']
            if keywords.get('event_type'):
                category = keywords['event_type'][0]
            elif keywords.get('music_genre'):
                category = 'music'
        
        # Generate ID
        event_id = self._generate_event_id(title, start_time)
        
        link_url = self._get_post_link(post)
        
        return {
            'id': event_id,
            'title': title[:200],
            'description': description,
            'location': self._get_default_location(),
            'start_time': start_time,
            'end_time': None,
            'url': link_url or self.url,
            'source': self.name,
            'category': category,
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending',
            'extraction_method': 'ocr_flyer' if image_data else 'text_analysis',
            'ocr_confidence': image_data.get('ocr_confidence') if image_data else None
        }
    
    def _default_event_title(self) -> str:
        """Build the default event title string."""
        return f"{self.DEFAULT_TITLE_PREFIX}{self.name}"
    
    def _get_post_link(self, post: Dict[str, Any]) -> Optional[str]:
        """Get first link from post data."""
        links = post.get('links') or []
        return links[0] if links else None
    
    def _get_ai_provider(self):
        """Get configured AI provider for extraction."""
        if not self.ai_providers:
            return None
        
        provider = None
        if self.options.ai_provider:
            provider = self.ai_providers.get(self.options.ai_provider)
        if not provider:
            provider = next(iter(self.ai_providers.values()), None)
        if not provider:
            return None
        
        if hasattr(provider, 'is_available') and not provider.is_available():
            return None
        
        return provider
    
    def _ai_extract_event_details(self, text: str) -> Optional[Dict[str, Any]]:
        """Use AI provider to extract event details from text."""
        if not text:
            return None
        
        provider = self._get_ai_provider()
        if not provider:
            return None
        
        prompt = self.options.ai_prompt or (
            "Extract event details and return JSON with fields: title, start_time, "
            "end_time, url, location. Convert relative dates like 'tomorrow' to "
            "ISO datetime."
        )
        
        try:
            return provider.extract_event_info(text, prompt)
        except Exception as e:
            print(f"      AI extraction error: {e}")
            return None
    
    def _extract_datetime_from_text(self, text: str) -> Optional[str]:
        """Extract datetime from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            ISO formatted datetime or None
        """
        if not text:
            return None
        
        # Date patterns
        date_patterns = [
            (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', 'DMY4'),
            (r'(\d{1,2})\.(\d{1,2})\.(\d{2})(?!\d)', 'DMY2'),
            (r'(\d{4})-(\d{2})-(\d{2})', 'YMD'),
            (r'(\d{1,2})\.(\d{1,2})(?:\.(?!\d)|$)', 'DM'),
        ]
        
        date_match = None
        date_format = None
        
        for pattern, fmt in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_match = match
                date_format = fmt
                break
        
        if not date_match:
            relative_date = resolve_relative_date(text)
            if not relative_date:
                return None
            
            hour, minute = 20, 0  # Default time
            time_match = extract_time_from_text(text)
            if time_match:
                hour, minute = time_match
            
            dt = datetime(relative_date.year, relative_date.month, relative_date.day, hour, minute)
            return dt.isoformat()
        
        # Parse date
        try:
            groups = date_match.groups()
            if date_format == 'DMY4':
                day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
            elif date_format == 'DMY2':
                day, month, year = int(groups[0]), int(groups[1]), 2000 + int(groups[2])
            elif date_format == 'DM':
                day, month = int(groups[0]), int(groups[1])
                year = resolve_year_for_date(month, day)
            else:  # YMD
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            
            # Extract time
            hour, minute = 20, 0  # Default time
            time_match = extract_time_from_text(text)
            if time_match:
                hour, minute = time_match
            
            dt = datetime(year, month, day, hour, minute)
            return dt.isoformat()
            
        except (ValueError, IndexError):
            return None
    
    def _parse_date_time(self, date_str: str, time_str: str = None) -> Optional[str]:
        """Parse date and time strings into ISO format.
        
        Args:
            date_str: Date string (various formats)
            time_str: Time string (optional)
            
        Returns:
            ISO formatted datetime or None
        """
        try:
            # Try to parse date
            day, month, year = None, None, None
            
            relative_date = resolve_relative_date(date_str)
            if relative_date:
                hour, minute = 20, 0
                if time_str:
                    time_match = extract_time_from_text(time_str)
                    if time_match:
                        hour, minute = time_match
                
                dt = datetime(relative_date.year, relative_date.month, relative_date.day, hour, minute)
                return dt.isoformat()
            
            # DD.MM.YYYY or DD.MM.YY
            match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})', date_str)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                if year < 100:
                    year += 2000
            
            if not all([day, month, year]):
                match = re.match(r'(\d{1,2})\.(\d{1,2})(?:\.(?!\d)|$)', date_str)
                if match:
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = resolve_year_for_date(month, day)
            
            if not all([day, month, year]):
                return None
            
            # Parse time
            hour, minute = 20, 0
            if time_str:
                time_match = extract_time_from_text(time_str)
                if time_match:
                    hour, minute = time_match
            
            dt = datetime(year, month, day, hour, minute)
            return dt.isoformat()
            
        except (ValueError, AttributeError):
            return None
    
    def _generate_event_id(self, title: str, start_time: str) -> str:
        """Generate a unique event ID.
        
        Args:
            title: Event title
            start_time: Event start time
            
        Returns:
            Unique event ID
        """
        hash_input = f"{self.name}_{title}_{start_time}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        source_slug = self.name.lower().replace(' ', '_')[:20]
        return f"fb_{source_slug}_{hash_value}"
    
    def _get_default_location(self) -> Dict[str, Any]:
        """Get default location for events.
        
        Returns:
            Location dictionary
        """
        return self.options.default_location or {
            'name': self.name,
            'lat': 50.3167,
            'lon': 11.9167
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ''
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common social media artifacts
        text = re.sub(r'See more|Mehr anzeigen|·|\u200b', '', text)
        return text.strip()
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events.
        
        Args:
            events: List of events
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []
        
        for event in events:
            # Create dedup key from title and date
            key = (
                event.get('title', '').lower()[:50],
                event.get('start_time', '')[:10]  # Just the date part
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(event)
        
        return unique
