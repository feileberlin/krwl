"""JSON API scraper."""

from typing import Dict, Any, List
from datetime import datetime
from ...base import BaseSource, SourceOptions

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class APISource(BaseSource):
    """Scraper for JSON APIs."""
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions,
                 base_path=None, ai_providers=None):
        super().__init__(
            source_config,
            options,
            base_path=base_path,
            ai_providers=ai_providers
        )
        self.available = REQUESTS_AVAILABLE
        
        if self.available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'KRWL HOF Event Scraper/1.0',
                'Accept': 'application/json'
            })
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from JSON API."""
        if not self.available:
            print("  ⚠ Requests not available")
            return []
        
        events = []
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # Try common keys for event arrays
                items = data.get('events', data.get('data', data.get('items', [])))
            else:
                items = []
            
            for item in items:
                event = self._parse_item(item)
                if event and not self.filter_event(event):
                    events.append(event)
                    
        except Exception as e:
            print(f"    API error: {str(e)}")
        
        return events
    
    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API item into event format."""
        try:
            location = self._extract_location(item)
            
            return {
                'id': f"api_{self.name.lower().replace(' ', '_')}_{item.get('id', hash(str(item)))}",
                'title': item.get('title', item.get('name', 'Untitled Event')),
                'description': item.get('description', '')[:500],
                'location': location,
                'start_time': item.get('start_time', item.get('date')),
                'end_time': item.get('end_time'),
                'url': item.get('url', item.get('link')),
                'source': self.name,
                'scraped_at': datetime.now().isoformat(),
                'status': 'pending'
            }
        except Exception as e:
            print(f"      Error parsing API item: {str(e)}")
            return None
    
    def _extract_location(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract location from API item."""
        # Try to extract location from item
        if 'location' in item:
            loc = item['location']
            if isinstance(loc, dict):
                return {
                    'name': loc.get('name', self.name),
                    'lat': loc.get('lat', loc.get('latitude', 50.3167)),
                    'lon': loc.get('lon', loc.get('longitude', 11.9167))
                }
        
        # Fall back to default
        return self.options.default_location or {
            'name': self.name,
            'lat': 50.3167,
            'lon': 11.9167
        }
