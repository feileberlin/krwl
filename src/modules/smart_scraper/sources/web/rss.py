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
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions):
        super().__init__(source_config, options)
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
            description = entry.get('summary', entry.get('description', ''))
            link = entry.get('link', '')
            
            # Try to extract date
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                start_time = datetime(*published[:6]).isoformat()
            else:
                # Default to tomorrow if no date
                start_time = (datetime.now() + timedelta(days=1)).replace(
                    hour=18, minute=0).isoformat()
            
            # Get default location
            location = self.options.default_location or {
                'name': self.name,
                'lat': 50.3167,
                'lon': 11.9167
            }
            
            # Clean description
            if description:
                # Remove HTML tags
                try:
                    from bs4 import BeautifulSoup
                    description = BeautifulSoup(description, 'lxml').get_text(strip=True)
                except:
                    pass
                description = description[:500]  # Limit length
            
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
