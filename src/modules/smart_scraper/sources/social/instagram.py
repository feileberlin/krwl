"""Instagram events scraper without API.

This module scrapes public Instagram profiles for posts that may contain
event information. It uses web scraping techniques and integrates with the
image_analyzer module to extract event data from posted flyers via OCR.

Note: This scraper works with public profiles only and does not require
Instagram API credentials. It respects rate limits and follows ethical
scraping practices.

Key features:
- Public profile scraping via mobile Instagram web
- OCR scanning of posted images for event flyers
- Date/time extraction from post captions and images
- Web search fallback when direct scraping fails (e.g., CI environments)
- German and English language support

Future accounts can be added by adding new entries to config.json:
    {
        "name": "YourAccountName",
        "url": "https://www.instagram.com/your_account_handle/",
        "type": "instagram",
        "enabled": true,
        "notes": "Description of events",
        "options": {
            "filter_ads": true,
            "ocr_enabled": true,
            "max_days_ahead": 90,
            "category": "music",
            "default_location": {
                "name": "Venue Name",
                "lat": 50.3167,
                "lon": 11.9167
            }
        }
    }
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
import json
import hashlib
import time
from ...base import BaseSource, SourceOptions
from ...date_utils import resolve_relative_date, extract_time_from_text, resolve_year_for_date
from ...source_cache import SourceCache
from ...ai_event_extractor import LocalEventExtractor

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


class InstagramSource(BaseSource):
    """Instagram events scraper using web scraping (no API required).
    
    This scraper extracts events from:
    1. Public Instagram profiles via mobile web interface
    2. Post captions containing event information
    3. Posted images analyzed via OCR for event flyers
    4. **Web search fallback** - Uses search to find event info when direct access fails
    
    Features:
    - OCR scanning of posted images for event flyers
    - Date/time extraction from post captions and images
    - German and English language support
    - Image caching to avoid re-downloading
    - **Web search fallback** for network-restricted environments (CI/testing)
    
    Adding new Instagram accounts:
    Simply add a new source entry to config.json with type "instagram".
    See module docstring for configuration example.
    """
    
    PLATFORM_NAME = "instagram"
    DEFAULT_TITLE_PREFIX = "Event from "
    USE_WEB_SEARCH_FALLBACK = True  # Enable web search when direct scraping fails
    
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
        self.post_cache = self._init_post_cache()
        
        # Initialize session with realistic headers to avoid detection
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
            # Set timeout for all requests
            self.request_timeout = 15
            # Add delay between requests (in seconds)
            self.request_delay = 3  # Instagram is more sensitive than Facebook
        
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
        self.event_extractor = LocalEventExtractor(self.ai_providers)
    
    def _init_post_cache(self) -> Optional[SourceCache]:
        """Initialize post cache for deduplication."""
        if not self.base_path:
            return None
        try:
            return SourceCache(self.base_path, f"instagram_{self.name}")
        except Exception:
            return None
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Instagram profile.
        
        Returns:
            List of event dictionaries
        """
        if not self.available:
            print(f"    ⚠ Requests/BeautifulSoup not available")
            # Try web search fallback even without requests
            if self.USE_WEB_SEARCH_FALLBACK:
                return self._scrape_via_web_search()
            return []
        
        events = []
        direct_scraping_failed = False
        
        try:
            # Scrape public profile posts
            events.extend(self._scrape_profile_posts())
        except Exception as e:
            print(f"    ⚠ Direct scraping failed: {type(e).__name__}: {str(e)}")
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("Full traceback:", exc_info=True)
            direct_scraping_failed = True
        
        # If direct scraping returned no events or failed, try web search fallback
        if (len(events) == 0 or direct_scraping_failed) and self.USE_WEB_SEARCH_FALLBACK:
            print(f"    🔍 Trying web search fallback...")
            search_events = self._scrape_via_web_search()
            events.extend(search_events)
        
        # Deduplicate events
        events = self._deduplicate_events(events)
        
        print(f"    📸 OCR enabled: {self.ocr_enabled and IMAGE_ANALYZER_AVAILABLE}")
        print(f"    📊 Found {len(events)} potential events")
        
        return events
    
    def _make_request(self, url: str, delay: bool = True) -> Optional['requests.Response']:
        """Make HTTP request with anti-scraping measures.
        
        Args:
            url: URL to fetch
            delay: Whether to add delay before request (default True)
            
        Returns:
            Response object or None on error
        """
        if delay and hasattr(self, 'request_delay'):
            time.sleep(self.request_delay)
        
        try:
            timeout = getattr(self, 'request_timeout', 15)
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"      Request error: {e}")
            return None
    
    def _scrape_profile_posts(self) -> List[Dict[str, Any]]:
        """Scrape posts from Instagram profile.
        
        Returns:
            List of event dictionaries extracted from posts
        """
        events = []
        
        try:
            response = self._make_request(self.url)
            if not response:
                return events
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try to extract data from page
            posts = self._extract_posts_from_html(soup)
            
            # Also try to extract from embedded JSON
            json_posts = self._extract_posts_from_json(soup)
            posts.extend(json_posts)
            
            # Process each post for event information
            events.extend(self._process_posts(posts))
            
        except Exception as e:
            print(f"    ⚠ Profile posts scrape error: {e}")
        
        return events
    
    def _extract_posts_from_html(self, soup: 'BeautifulSoup') -> List[Dict[str, Any]]:
        """Extract posts from Instagram HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        # Instagram uses various selectors for posts
        # Try different approaches based on page structure
        
        # Look for post containers (Instagram web structure varies)
        post_selectors = [
            'article',
            'div[role="presentation"]',
            '.v1Nh3',  # Historical Instagram class
            'a[href*="/p/"]',  # Links to posts
        ]
        
        for selector in post_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements[:10]:  # Limit to 10 posts
                    post = self._parse_post_element(elem)
                    if post:
                        posts.append(post)
                break
        
        return posts
    
    def _parse_post_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse a post HTML element into structured data.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Post dictionary or None
        """
        try:
            post = {
                'text': '',
                'images': [],
                'links': [],
                'image_metadata': [],
                'post_id': None,
                'timestamp': None
            }
            
            # Extract text content
            text_elem = element.find('div', class_=re.compile(r'caption|comment'))
            if text_elem:
                post['text'] = text_elem.get_text(strip=True)
            
            # Also check for alt text descriptions
            alt_texts = []
            for img in element.find_all('img'):
                alt = img.get('alt', '')
                if alt and 'photo by' not in alt.lower():
                    alt_texts.append(alt)
                    
                # Get image URL
                src = img.get('src') or img.get('data-src')
                if src and 'instagram' in src:
                    post['images'].append(src)
                    post['image_metadata'].append({
                        'url': src,
                        'alt': alt,
                        'title': img.get('title', '')
                    })
            
            if alt_texts:
                post['text'] = ' '.join(alt_texts) + ' ' + post['text']
            
            # Extract post link
            for link in element.find_all('a', href=True):
                href = link['href']
                if '/p/' in href:  # Instagram post URL pattern
                    if not href.startswith('http'):
                        href = f"https://www.instagram.com{href}"
                    post['links'].append(href)
                    
                    # Extract post ID from URL
                    match = re.search(r'/p/([A-Za-z0-9_-]+)', href)
                    if match:
                        post['post_id'] = match.group(1)
            
            # Only return if we have content
            if post['text'] or post['images']:
                return post
            
        except Exception as e:
            print(f"      Parse error: {e}")
        
        return None
    
    def _extract_posts_from_json(self, soup: 'BeautifulSoup') -> List[Dict[str, Any]]:
        """Extract posts from embedded JSON data in the page.
        
        Instagram sometimes embeds post data as JSON in script tags.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        # Look for JSON data in script tags
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    posts.extend(self._parse_json_data(data))
                elif isinstance(data, list):
                    for item in data:
                        posts.extend(self._parse_json_data(item))
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Also check for window._sharedData pattern (historical Instagram)
        for script in soup.find_all('script'):
            if script.string and 'window._sharedData' in script.string:
                try:
                    match = re.search(r'window\._sharedData\s*=\s*(\{.*?\});', script.string, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                        posts.extend(self._parse_shared_data(data))
                except (json.JSONDecodeError, TypeError):
                    continue
        
        return posts
    
    def _parse_json_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Instagram JSON-LD data for post information.
        
        Args:
            data: JSON-LD data object
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        if data.get('@type') == 'ImageObject' or data.get('@type') == 'MediaObject':
            post = {
                'text': data.get('caption', '') or data.get('description', ''),
                'images': [data.get('contentUrl')] if data.get('contentUrl') else [],
                'links': [data.get('url')] if data.get('url') else [],
                'image_metadata': [],
                'post_id': None,
                'timestamp': data.get('uploadDate')
            }
            if post['text'] or post['images']:
                posts.append(post)
        
        return posts
    
    def _parse_shared_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Instagram window._sharedData for posts.
        
        Args:
            data: Shared data object
            
        Returns:
            List of post dictionaries
        """
        posts = []
        
        try:
            # Navigate to profile page data
            profile = data.get('entry_data', {}).get('ProfilePage', [{}])[0]
            user = profile.get('graphql', {}).get('user', {})
            media = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            
            for edge in media[:10]:  # Limit to 10 posts
                node = edge.get('node', {})
                post = {
                    'text': self._get_caption_from_node(node),
                    'images': [node.get('display_url')] if node.get('display_url') else [],
                    'links': [f"https://www.instagram.com/p/{node.get('shortcode')}/"] if node.get('shortcode') else [],
                    'image_metadata': [],
                    'post_id': node.get('shortcode'),
                    'timestamp': node.get('taken_at_timestamp')
                }
                if post['text'] or post['images']:
                    posts.append(post)
                    
        except (KeyError, IndexError, TypeError):
            pass
        
        return posts
    
    def _get_caption_from_node(self, node: Dict[str, Any]) -> str:
        """Extract caption text from Instagram node data.
        
        Args:
            node: Instagram media node
            
        Returns:
            Caption text
        """
        edges = node.get('edge_media_to_caption', {}).get('edges', [])
        if edges:
            return edges[0].get('node', {}).get('text', '')
        return ''
    
    def _process_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process posts to extract events.
        
        Args:
            posts: List of post dictionaries
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        for post in posts:
            # Check if already processed (cached)
            if self.post_cache and post.get('post_id'):
                if self.post_cache.is_cached(post['post_id']):
                    continue
            
            event = self._extract_event_from_post(post)
            if event:
                events.append(event)
                
                # Cache the processed post
                if self.post_cache and post.get('post_id'):
                    self.post_cache.add(post['post_id'], event)
        
        return events
    
    def _extract_event_from_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract event information from a single post.
        
        Args:
            post: Post dictionary
            
        Returns:
            Event dictionary or None
        """
        # Try OCR analysis if images are present
        image_data = None
        if self.ocr_enabled and IMAGE_ANALYZER_AVAILABLE and post.get('images'):
            image_data = self._analyze_post_images(
                post['images'],
                post_id=post.get('post_id'),
                image_metadata=post.get('image_metadata', [])
            )
        
        # Try AI extraction for structured data
        ai_details = self._ai_extract_event_details(post, image_data)
        
        # Combine data sources to build event
        text = post.get('text', '')
        
        # Extract title
        title = None
        if ai_details and ai_details.get('title'):
            title = ai_details['title']
        elif image_data and image_data.get('title'):
            title = image_data['title']
        else:
            # Try to extract from text
            title = self._extract_title_from_text(text)
        
        if not title:
            title = self._default_event_title()
        
        # Extract date/time
        start_time = None
        if ai_details and ai_details.get('start_time'):
            start_time = ai_details['start_time']
        elif image_data and image_data.get('date'):
            start_time = image_data['date']
        else:
            start_time = self._extract_datetime_from_text(text)
        
        # Skip if no date found (likely not an event)
        if not start_time:
            # If we have strong OCR confidence, still include
            if not (image_data and image_data.get('ocr_confidence', 0) > 0.5):
                return None
            # Default to next week
            start_time = (datetime.now() + timedelta(days=7)).replace(hour=20, minute=0).isoformat()
        
        # Build description
        description_parts = []
        if text:
            description_parts.append(text[:300])
        if image_data and image_data.get('ocr_text'):
            description_parts.append(f"\n[From flyer]: {image_data['ocr_text'][:200]}")
        
        description = '\n'.join(description_parts)[:500]
        
        # Extract category
        category = self.options.category
        if not category and image_data and image_data.get('keywords'):
            keywords = image_data['keywords']
            if keywords.get('event_type'):
                category = keywords['event_type'][0]
            elif keywords.get('music_genre'):
                category = 'music'
        if not category and ai_details:
            category = ai_details.get('category')
        
        # Generate ID
        event_id = self._generate_event_id(title, start_time)
        
        # Get link URL
        link_url = post.get('links', [None])[0]
        if not link_url and image_data:
            urls = image_data.get('urls_found') or []
            if urls:
                link_url = urls[0]
        if not link_url and ai_details:
            link_url = ai_details.get('url')
        
        # Get location
        location = self._get_default_location() or {}
        if image_data and image_data.get('location'):
            location = image_data['location']
        if ai_details and isinstance(ai_details.get('location'), dict):
            for key, value in ai_details['location'].items():
                existing_value = location.get(key)
                if value is not None and (key not in location or existing_value in (None, "")):
                    location[key] = value
        
        return {
            'id': event_id,
            'title': title[:200],
            'description': description,
            'location': location,
            'start_time': start_time,
            'end_time': ai_details.get('end_time') if ai_details else None,
            'url': link_url or self.url,
            'source': self.name,
            'category': category,
            'scraped_at': datetime.now().isoformat(),
            'status': 'pending',
            'extraction_method': 'ocr_flyer' if image_data else 'text_analysis',
            'ocr_confidence': image_data.get('ocr_confidence') if image_data else None
        }
    
    def _analyze_post_images(self, image_urls: List[str], post_id: Optional[str] = None,
                            image_metadata: Optional[List[Dict[str, str]]] = None) -> Optional[Dict[str, Any]]:
        """Analyze post images for event content using OCR.
        
        Args:
            image_urls: List of image URLs
            post_id: Optional post ID for caching
            image_metadata: Optional list of metadata dicts
            
        Returns:
            Best event data extracted from images or None
        """
        if not self.image_analyzer:
            return None
        
        best_result = None
        best_confidence = 0.0
        
        for idx, url in enumerate(image_urls[:3]):  # Limit to first 3 images
            try:
                # Get metadata for this image if available
                metadata = None
                if image_metadata and idx < len(image_metadata):
                    metadata = image_metadata[idx]
                
                # Analyze image URL
                result = self.image_analyzer.analyze_url(url, timeout=10)
                if result:
                    # Enhance with metadata
                    if metadata:
                        result = self._enhance_ocr_with_metadata(result, metadata)
                    
                    if result.get('ocr_confidence', 0) > best_confidence:
                        best_confidence = result.get('ocr_confidence', 0)
                        best_result = result
                        
            except Exception as e:
                print(f"      OCR analysis error: {e}")
                continue
        
        # Only return if confidence is above threshold
        if best_result and best_confidence >= self.min_ocr_confidence:
            return best_result
        
        return None
    
    def _enhance_ocr_with_metadata(self, ocr_result: Dict[str, Any], 
                                  metadata: Dict[str, str]) -> Dict[str, Any]:
        """Enhance OCR results with image metadata.
        
        Args:
            ocr_result: OCR analysis result
            metadata: Image metadata
            
        Returns:
            Enhanced OCR result
        """
        if not metadata:
            return ocr_result
        
        metadata_text = []
        for key in ['alt', 'title', 'aria_label', 'caption']:
            if metadata.get(key):
                metadata_text.append(metadata[key])
        
        if metadata_text:
            combined_text = ocr_result.get('text', '')
            if combined_text:
                combined_text += '\n' + '\n'.join(metadata_text)
            else:
                combined_text = '\n'.join(metadata_text)
            
            ocr_result['text'] = combined_text
            ocr_result['has_metadata'] = True
        
        return ocr_result
    
    def _extract_title_from_text(self, text: str) -> Optional[str]:
        """Extract a potential event title from text.
        
        Args:
            text: Post text
            
        Returns:
            Extracted title or None
        """
        if not text:
            return None
        
        # Take first line or sentence as title
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # Limit length and clean up
            if len(first_line) > 10 and len(first_line) < 100:
                # Remove emojis and excess whitespace
                title = re.sub(r'[^\w\s\-.,!?&äöüÄÖÜß]', '', first_line)
                title = ' '.join(title.split())
                if title:
                    return title
        
        return None
    
    def _default_event_title(self) -> str:
        """Build the default event title string."""
        return f"{self.DEFAULT_TITLE_PREFIX}{self.name}"
    
    def _ai_extract_event_details(self, post: Dict[str, Any],
                                  image_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Use local AI to extract event details from post and OCR context."""
        if not self.event_extractor:
            return None

        try:
            return self.event_extractor.extract_event_details(
                post_text=post.get('text', ''),
                image_data=image_data,
                image_metadata=post.get('image_metadata'),
                post_links=post.get('links'),
                provider_name=self.options.ai_provider,
                prompt_override=self.options.ai_prompt
            )
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
    
    def _generate_event_id(self, title: str, start_time: str) -> str:
        """Generate unique event ID.
        
        Args:
            title: Event title
            start_time: Event start time
            
        Returns:
            Unique event ID
        """
        # Create hash from title and time
        content = f"{title}{start_time}{self.name}"
        hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"instagram_{self.name.lower().replace(' ', '_')}_{hash_val}"
    
    def _get_default_location(self) -> Optional[Dict[str, Any]]:
        """Get default location from source options.
        
        Returns:
            Location dictionary or None
        """
        if self.options.default_location:
            return self.options.default_location
        
        # Try from source config
        default_loc = self.source_config.get('options', {}).get('default_location')
        if default_loc:
            return default_loc
        
        return None
    
    def _scrape_via_web_search(self) -> List[Dict[str, Any]]:
        """Fallback scraping method using web search when direct access fails.
        
        This method searches for event information about the Instagram account
        using web search APIs which can work even when direct Instagram access
        is blocked (e.g., in CI environments).
        
        Note: This returns an empty list by design. The logged queries can be
        processed by external automation that has access to web_search tools.
        
        Returns:
            List of events found through web search (currently empty)
        """
        events = []
        
        # Extract account name from URL
        account_name = self._extract_account_name_from_url(self.url)
        if not account_name:
            print(f"    ⚠ Cannot extract account name from URL for web search")
            return events
        
        print(f"    🔍 Web search for: {account_name}")
        
        # Log search query for external processing
        search_query = f"{account_name} instagram events upcoming Germany"
        print(f"    💡 Web search query: '{search_query}'")
        print(f"    💡 To scrape manually: Use web search with this query")
        print(f"    💡 External automation can process this query automatically")
        
        return events
    
    def _extract_account_name_from_url(self, url: str) -> Optional[str]:
        """Extract Instagram account name from URL.
        
        Args:
            url: Instagram URL
            
        Returns:
            Account name or None
        """
        # Remove protocol and www
        url = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Extract account name from URL patterns
        patterns = [
            r'instagram\.com/([^/\?]+)',  # instagram.com/username
            r'instagr\.am/([^/\?]+)',      # instagr.am/username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                account_name = match.group(1)
                # Clean up account name
                account_name = account_name.replace('_', ' ').replace('.', ' ')
                # Remove common suffixes
                account_name = re.sub(r'\s*(official|hof|berlin)$', '', account_name, flags=re.IGNORECASE)
                return account_name.strip()
        
        return None
    
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
