"""Event editor module for reviewing and publishing events"""

from datetime import datetime
from .utils import load_pending_events, save_pending_events, load_events, save_events


class EventEditor:
    """Editor for reviewing and publishing events"""
    
    def __init__(self, base_path):
        self.base_path = base_path
        
    def review_pending(self):
        """Review all pending events"""
        pending_data = load_pending_events(self.base_path)
        pending_events = pending_data['pending_events']
        
        if not pending_events:
            print("No pending events to review.")
            input("\nPress Enter to continue...")
            return
            
        i = 0
        while i < len(pending_events):
            event = pending_events[i]
            
            print("\n" + "=" * 60)
            print(f"Event {i + 1} of {len(pending_events)}")
            print("=" * 60)
            self._display_event(event)
            print("-" * 60)
            print("Options:")
            print("  (a) Approve and publish")
            print("  (e) Edit event")
            print("  (r) Reject and delete")
            print("  (s) Skip to next")
            print("  (q) Quit review")
            print("-" * 60)
            
            choice = input("Your choice: ").strip().lower()
            
            if choice == 'a':
                self._approve_event(event)
                pending_events.pop(i)
                print("\nEvent approved and published!")
            elif choice == 'e':
                self._edit_event(event)
                i += 1
            elif choice == 'r':
                pending_events.pop(i)
                print("\nEvent rejected and deleted!")
            elif choice == 's':
                i += 1
            elif choice == 'q':
                break
            else:
                print("\nInvalid choice. Try again.")
                
        # Save updated pending events
        save_pending_events(self.base_path, pending_data)
        
    def _display_event(self, event):
        """Display event details"""
        print(f"\nTitle: {event.get('title', 'N/A')}")
        print(f"Description: {event.get('description', 'N/A')}")
        print(f"Location: {event.get('location', {}).get('name', 'N/A')}")
        print(f"  Coordinates: {event.get('location', {}).get('lat', 'N/A')}, "
              f"{event.get('location', {}).get('lon', 'N/A')}")
        print(f"Start Time: {event.get('start_time', 'N/A')}")
        print(f"End Time: {event.get('end_time', 'N/A')}")
        print(f"URL: {event.get('url', 'N/A')}")
        print(f"Source: {event.get('source', 'N/A')}")
        
    def _approve_event(self, event):
        """Approve and publish an event"""
        event['status'] = 'published'
        event['published_at'] = datetime.now().isoformat()
        
        # Add to published events
        events_data = load_events(self.base_path)
        events_data['events'].append(event)
        save_events(self.base_path, events_data)
        
    def _edit_event(self, event):
        """Edit event details"""
        print("\n" + "=" * 60)
        print("Edit Event (press Enter to keep current value)")
        print("=" * 60)
        
        # Title
        new_title = input(f"Title [{event.get('title', '')}]: ").strip()
        if new_title:
            event['title'] = new_title
            
        # Description
        new_desc = input(f"Description [{event.get('description', '')}]: ").strip()
        if new_desc:
            event['description'] = new_desc
            
        # Location name
        loc = event.get('location', {})
        new_loc_name = input(f"Location name [{loc.get('name', '')}]: ").strip()
        if new_loc_name:
            if 'location' not in event:
                event['location'] = {}
            event['location']['name'] = new_loc_name
            
        # Coordinates
        new_lat = input(f"Latitude [{loc.get('lat', '')}]: ").strip()
        if new_lat:
            try:
                if 'location' not in event:
                    event['location'] = {}
                event['location']['lat'] = float(new_lat)
            except ValueError:
                print("Invalid latitude, keeping old value")
                
        new_lon = input(f"Longitude [{loc.get('lon', '')}]: ").strip()
        if new_lon:
            try:
                if 'location' not in event:
                    event['location'] = {}
                event['location']['lon'] = float(new_lon)
            except ValueError:
                print("Invalid longitude, keeping old value")
                
        # Start time
        new_start = input(f"Start time (ISO format) [{event.get('start_time', '')}]: ").strip()
        if new_start:
            event['start_time'] = new_start
            
        # End time
        new_end = input(f"End time (ISO format) [{event.get('end_time', '')}]: ").strip()
        if new_end:
            event['end_time'] = new_end
            
        # URL
        new_url = input(f"URL [{event.get('url', '')}]: ").strip()
        if new_url:
            event['url'] = new_url
            
        print("\nEvent updated!")
