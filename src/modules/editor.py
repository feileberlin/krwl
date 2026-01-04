"""Event editor module for reviewing and publishing events"""

import logging
from datetime import datetime
from .utils import (load_pending_events, save_pending_events, load_events, 
                   save_events, add_rejected_event)

# Configure module logger
logger = logging.getLogger(__name__)


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
        
        # Load historical events once for all reviews
        from .utils import load_historical_events
        historical_events = load_historical_events(self.base_path)
            
        i = 0
        while i < len(pending_events):
            event = pending_events[i]
            
            print("\n" + "=" * 60)
            print(f"Event {i + 1} of {len(pending_events)}")
            print("=" * 60)
            self._display_event(event)
            
            # Show similar historical events
            similar_events = self._find_similar_events(event, historical_events)
            if similar_events:
                print("\n" + "─" * 60)
                print("📚 Similar Historical Events Found:")
                print("─" * 60)
                for idx, similar in enumerate(similar_events[:3], 1):  # Show top 3
                    print(f"\n{idx}. {similar['event'].get('title', 'N/A')}")
                    print(f"   Location: {similar['event'].get('location', {}).get('name', 'N/A')}")
                    print(f"   Time: {similar['event'].get('start_time', 'N/A')}")
                    if similar['event'].get('description'):
                        desc = similar['event'].get('description', '')
                        desc_preview = desc[:100] + '...' if len(desc) > 100 else desc
                        print(f"   Description: {desc_preview}")
                    print(f"   Similarity: {similar['score']:.0%}")
            
            print("-" * 60)
            print("Options:")
            print("  (a) Approve and publish")
            print("  (e) Edit event")
            print("  (r) Reject and delete")
            print("  (s) Skip to next")
            print("  (b) Batch select mode")
            print("  (q) Quit review")
            print("-" * 60)
            self._print_review_footer()
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 'a':
                self._approve_event(event)
                pending_events.pop(i)
                print("\nEvent approved and published!")
            elif choice == 'e':
                self._edit_event(event)
                i += 1
            elif choice == 'r':
                self._reject_event(event)
                pending_events.pop(i)
                print("\nEvent rejected and saved to rejected list!")
            elif choice == 's':
                i += 1
            elif choice == 'b':
                # Enter batch selection mode
                self._batch_selection_mode(pending_events, i)
                # Reload pending events as they may have changed
                pending_data = load_pending_events(self.base_path)
                pending_events = pending_data['pending_events']
                i = 0  # Restart from beginning
            elif choice == 'q':
                break
            else:
                print("\nInvalid choice. Try again.")
                
        # Save updated pending events
        save_pending_events(self.base_path, pending_data)
    
    def _batch_selection_mode(self, pending_events, current_index):
        """Interactive batch selection mode for bulk operations"""
        print("\n" + "=" * 80)
        print("📦 BATCH SELECTION MODE")
        print("=" * 80)
        print("Select events for batch operations using checkboxes")
        print("-" * 80)
        
        # Display all events with selection checkboxes
        selected = set()
        
        while True:
            print("\n" + "─" * 80)
            print("📋 All Pending Events:")
            print("─" * 80)
            
            for idx, event in enumerate(pending_events):
                checkbox = "☑" if idx in selected else "☐"
                title = event.get('title', 'N/A')[:50]
                event_id = event.get('id', 'N/A')
                source = event.get('source', 'N/A')
                print(f"{idx + 1:3}. {checkbox} {title}")
                print(f"      ID: {event_id} | Source: {source}")
            
            print("\n" + "─" * 80)
            print(f"Selected: {len(selected)} event(s)")
            print("─" * 80)
            print("Commands:")
            print("  [number]      Toggle selection (e.g., '1' or '1,3,5')")
            print("  all           Select all events")
            print("  none          Clear selection")
            print("  range N-M     Select range (e.g., 'range 1-5')")
            print("  pattern WORD  Select by title pattern (e.g., 'pattern concert')")
            print("  approve       Batch approve selected events")
            print("  reject        Batch reject selected events")
            print("  show          Show details of selected events")
            print("  back          Exit batch mode")
            print("─" * 80)
            
            choice = input("\nCommand: ").strip().lower()
            
            if choice == 'back':
                break
            elif choice == 'all':
                selected = set(range(len(pending_events)))
                print(f"✓ Selected all {len(selected)} events")
            elif choice == 'none':
                selected.clear()
                print("✓ Cleared selection")
            elif choice.startswith('range '):
                try:
                    range_str = choice.split(' ', 1)[1]
                    start, end = map(int, range_str.split('-'))
                    selected.update(range(start - 1, end))
                    print(f"✓ Selected events {start} to {end}")
                except Exception as e:
                    print(f"❌ Invalid range format: {e}")
            elif choice.startswith('pattern '):
                pattern = choice.split(' ', 1)[1].lower()
                matched = 0
                for idx, event in enumerate(pending_events):
                    title = event.get('title', '').lower()
                    if pattern in title:
                        selected.add(idx)
                        matched += 1
                print(f"✓ Selected {matched} events matching '{pattern}'")
            elif choice == 'approve':
                if not selected:
                    print("❌ No events selected")
                    continue
                
                confirm = input(f"\n⚠️  Approve {len(selected)} event(s)? (yes/no): ")
                if confirm.lower() == 'yes':
                    self._batch_approve(pending_events, selected)
                    print(f"✅ Approved {len(selected)} event(s)")
                    break
            elif choice == 'reject':
                if not selected:
                    print("❌ No events selected")
                    continue
                
                confirm = input(f"\n⚠️  Reject {len(selected)} event(s)? (yes/no): ")
                if confirm.lower() == 'yes':
                    self._batch_reject(pending_events, selected)
                    print(f"✅ Rejected {len(selected)} event(s)")
                    break
            elif choice == 'show':
                if not selected:
                    print("❌ No events selected")
                    continue
                
                print("\n" + "=" * 80)
                print("📋 Selected Events Details:")
                print("=" * 80)
                for idx in sorted(selected):
                    event = pending_events[idx]
                    print(f"\n{idx + 1}. {event.get('title', 'N/A')}")
                    print(f"   ID: {event.get('id', 'N/A')}")
                    print(f"   Source: {event.get('source', 'N/A')}")
                    print(f"   Time: {event.get('start_time', 'N/A')}")
                input("\nPress Enter to continue...")
            else:
                # Try to parse as number(s)
                try:
                    # Handle comma-separated numbers
                    if ',' in choice:
                        numbers = [int(n.strip()) - 1 for n in choice.split(',')]
                    else:
                        numbers = [int(choice) - 1]
                    
                    for num in numbers:
                        if 0 <= num < len(pending_events):
                            if num in selected:
                                selected.remove(num)
                                print(f"☐ Deselected event {num + 1}")
                            else:
                                selected.add(num)
                                print(f"☑ Selected event {num + 1}")
                        else:
                            print(f"❌ Invalid event number: {num + 1}")
                except ValueError:
                    print("❌ Invalid command. Type 'back' to exit batch mode.")
    
    def _batch_approve(self, pending_events, selected_indices):
        """Batch approve selected events"""
        events_data = load_events(self.base_path)
        
        # Sort in reverse order to safely remove from list
        for idx in sorted(selected_indices, reverse=True):
            event = pending_events[idx]
            self._approve_event(event)
            pending_events.pop(idx)
        
        # Save changes
        save_events(self.base_path, events_data)
        pending_data = {'pending_events': pending_events}
        save_pending_events(self.base_path, pending_data)
        
        # Update HTML
        from .utils import update_events_in_html
        update_events_in_html(self.base_path)
    
    def _batch_reject(self, pending_events, selected_indices):
        """Batch reject selected events"""
        # Sort in reverse order to safely remove from list
        for idx in sorted(selected_indices, reverse=True):
            event = pending_events[idx]
            self._reject_event(event)
            pending_events.pop(idx)
        
        # Save changes
        pending_data = {'pending_events': pending_events}
        save_pending_events(self.base_path, pending_data)
    
    def _print_review_footer(self):
        """Print footer with editorial tooltips"""
        print()
        print("─" * 60)
        print("💡 Editorial Tip: Approved events publish to website | Edit to fix details")
        print("   Reject saves to auto-reject list (prevents re-scraping of recurring spam)")
        print("─" * 60)
        
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
        """Approve and publish an event with validation"""
        try:
            # Validate event before publishing
            from .models import validate_event_data
            validated_event = validate_event_data(event)
            event_dict = validated_event.model_dump()
            
            event_dict['status'] = 'published'
            event_dict['published_at'] = datetime.now().isoformat()
            
            # Backup the published event
            from .utils import backup_published_event
            backup_path = backup_published_event(self.base_path, event_dict)
            print(f"  ✓ Event backed up to: {backup_path.relative_to(self.base_path)}")
            
            # Add to published events
            events_data = load_events(self.base_path)
            events_data['events'].append(event_dict)
            save_events(self.base_path, events_data)
            
            logger.info(f"Event approved and published: {event_dict['title']}", extra={
                'event_id': event_dict['id'],
                'event_title': event_dict['title']
            })
            
            # Update the original event dict for removal from pending
            event.update(event_dict)
            
        except ValueError as e:
            logger.error(f"Event validation failed during approval: {e}", extra={
                'event_title': event.get('title', 'Unknown')
            })
            print(f"\n⚠ Validation error: {e}")
            print("Event was not approved. Please edit and fix the issues.")
            raise
        
    def _reject_event(self, event):
        """Reject an event and add it to the rejected events list"""
        # Add to rejected events to prevent future scraping of same event
        event_title = event.get('title', '')
        event_source = event.get('source', '')
        
        if event_title and event_source:
            add_rejected_event(self.base_path, event_title, event_source)
            logger.info(f"Event rejected: {event_title}", extra={
                'event_title': event_title,
                'event_source': event_source
            })
        else:
            logger.warning("Rejected event missing title or source", extra={
                'event': event
            })
        
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
    
    def _find_similar_events(self, event, historical_events):
        """
        Find similar events in historical data based on title and location.
        Returns a list of similar events sorted by similarity score.
        """
        if not historical_events:
            return []
        
        similar = []
        event_title = event.get('title', '').lower()
        event_location = event.get('location', {}).get('name', '').lower()
        event_lat = event.get('location', {}).get('lat')
        event_lon = event.get('location', {}).get('lon')
        
        for historical in historical_events:
            score = 0.0
            
            # Compare titles (word overlap)
            hist_title = historical.get('title', '').lower()
            if hist_title and event_title:
                event_words = set(event_title.split())
                hist_words = set(hist_title.split())
                if event_words and hist_words:
                    common_words = event_words.intersection(hist_words)
                    title_score = len(common_words) / max(len(event_words), len(hist_words))
                    score += title_score * 0.6  # Title is 60% of score
            
            # Compare locations (string similarity)
            hist_location = historical.get('location', {}).get('name', '').lower()
            if hist_location and event_location:
                if event_location in hist_location or hist_location in event_location:
                    score += 0.3  # Location match is 30% of score
                elif any(word in hist_location for word in event_location.split()):
                    score += 0.15  # Partial location match
            
            # Compare coordinates (distance-based)
            hist_lat = historical.get('location', {}).get('lat')
            hist_lon = historical.get('location', {}).get('lon')
            if all([event_lat, event_lon, hist_lat, hist_lon]):
                try:
                    from .utils import calculate_distance
                    distance = calculate_distance(event_lat, event_lon, hist_lat, hist_lon)
                    if distance < 1.0:  # Within 1 km
                        score += 0.1  # Proximity is 10% of score
                except:
                    pass
            
            # Only include if similarity score is above threshold
            if score > 0.3:  # 30% similarity threshold
                similar.append({
                    'event': historical,
                    'score': score
                })
        
        # Sort by similarity score (highest first)
        similar.sort(key=lambda x: x['score'], reverse=True)
        
        return similar
