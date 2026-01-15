"""RSS feed scraper."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from ...base import BaseSource, SourceOptions

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False


class RSSSource(BaseSource):
    """Scraper for RSS feeds."""
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None):
        super().__init__(source_config, options, base_path=base_path)
        self.available = FEEDPARSER_AVAILABLE
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from RSS feed."""
        if not self.available:
            print("  ⚠ Feedparser not available")
            return []
        
        events = []
        try:
            feed = feedparser.parse(self.url)
            for entry in feed.entries:
                event = self._parse_entry(entry)
                if event and not self.filter_event(event):
                    events.append(event)
        except Exception as e:
            print(f"    RSS error: {str(e)}")
        
        return events
    
    def _parse_entry(self, entry) -> Dict[str, Any]:
        """Parse RSS entry into event format."""
        try:
            # Extract basic info
            title = entry.get('title', 'Untitled Event')
            description = self._extract_description(entry)
            link = entry.get('link', '')
            start_time = self._extract_start_time(entry)
            location = self._get_default_location()
            
            return {
                'id': f"rss_{self.name.lower().replace(' ', '_')}_{hash(title + start_time)}",
                'title': title,
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': None,
                'url': link,
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        except Exception as e:
            print(f"      Error parsing RSS entry: {str(e)}")
            return None
    
    def _extract_description(self, entry) -> str:
        """Extract and clean description from RSS entry."""
        description = entry.get('summary', entry.get('description', ''))
        if not description:
            return ''
        
        # Remove HTML tags
        try:
            from bs4 import BeautifulSoup
            description = BeautifulSoup(description, 'lxml').get_text(strip=True)
        except:
            pass
        
        return description[:500]  # Limit length
    
    def _extract_start_time(self, entry) -> str:
        """Extract start time from RSS entry."""
        published = entry.get('published_parsed') or entry.get('updated_parsed')
        if published:
            return datetime(*published[:6]).isoformat()
        
        # Default to tomorrow if no date
        return (datetime.now() + timedelta(days=1)).replace(
            hour=18, minute=0).isoformat()
    
    def _get_default_location(self) -> Dict[str, Any]:
        """Get default location for events."""
        return self.options.default_location or {
            'name': self.name,
            'lat': 50.3167,
            'lon': 11.9167
        }
