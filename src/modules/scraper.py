"""Event scraper module"""

import json
from datetime import datetime
from .utils import load_pending_events, save_pending_events


class EventScraper:
    """Scraper for community events from various sources"""
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        
    def scrape_all_sources(self):
        """Scrape events from all configured sources"""
        pending_data = load_pending_events(self.base_path)
        new_events = []
        
        for source in self.config['scraping']['sources']:
            if not source.get('enabled', False):
                print(f"Skipping disabled source: {source['name']}")
                continue
                
            print(f"Scraping from: {source['name']}")
            events = self.scrape_source(source)
            new_events.extend(events)
            
        # Add new events to pending
        for event in new_events:
            if not self._event_exists(pending_data['pending_events'], event):
                pending_data['pending_events'].append(event)
                
        save_pending_events(self.base_path, pending_data)
        return new_events
        
    def scrape_source(self, source):
        """Scrape events from a single source"""
        # This is a placeholder - in real implementation, would use
        # requests/beautifulsoup/feedparser depending on source type
        
        source_type = source.get('type', 'rss')
        
        if source_type == 'rss':
            return self._scrape_rss(source)
        elif source_type == 'api':
            return self._scrape_api(source)
        elif source_type == 'html':
            return self._scrape_html(source)
        else:
            print(f"Unknown source type: {source_type}")
            return []
            
    def _scrape_rss(self, source):
        """Scrape RSS feed"""
        # Placeholder implementation
        # Real implementation would use feedparser
        print(f"  RSS scraping from {source['url']}")
        return []
        
    def _scrape_api(self, source):
        """Scrape from API"""
        # Placeholder implementation
        # Real implementation would use requests
        print(f"  API scraping from {source['url']}")
        return []
        
    def _scrape_html(self, source):
        """Scrape HTML page"""
        # Placeholder implementation
        # Real implementation would use requests + beautifulsoup
        print(f"  HTML scraping from {source['url']}")
        return []
        
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
