"""
Event Context Aggregator Module

Aggregates ALL available data about an event to inform editors during review.

Collects:
- Current scraped event data
- Historical editor decisions (previous edits, rejections)
- Similar past events (same venue, same source)
- Unverified location data
- Reviewer notes and flags
- Validation results

This provides editors with complete context to make informed decisions.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pathlib import Path
import json
import re


class EventContext:
    """
    Aggregated context for a single event.
    
    Provides editors with complete information to make informed decisions.
    """
    
    def __init__(self, event: Dict[str, Any]):
        """
        Initialize event context.
        
        Args:
            event: The current event being reviewed
        """
        self.event = event
        self.event_id = event.get('id', 'unknown')
        
        # Historical data
        self.previous_versions: List[Dict[str, Any]] = []
        self.previous_rejections: List[Dict[str, Any]] = []
        self.similar_events: List[Dict[str, Any]] = []
        
        # Location intelligence
        self.unverified_location_data: Optional[Dict[str, Any]] = None
        self.verified_location_suggestions: List[Dict[str, Any]] = []
        
        # Review metadata
        self.reviewer_notes: List[Dict[str, Any]] = []
        self.validation_result = None
        self.needs_attention_reasons: List[str] = []
        
        # Source intelligence
        self.source_history: Dict[str, Any] = {}
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of event context.
        
        Returns:
            Formatted summary for editor display
        """
        lines = []
        lines.append("═" * 60)
        lines.append(f"EVENT CONTEXT: {self.event.get('title', 'Unknown')[:50]}")
        lines.append("═" * 60)
        
        # Basic event info
        lines.append(f"\n📍 Location: {self.event.get('location', {}).get('name', 'Unknown')}")
        lines.append(f"📅 Start: {self.event.get('start_time', 'Unknown')}")
        lines.append(f"🔗 Source: {self.event.get('source', 'Unknown')}")
        lines.append(f"🆔 ID: {self.event_id}")
        
        # Validation status
        if self.validation_result:
            lines.append(f"\n✓ Validation: {self.validation_result.is_valid}")
            if self.validation_result.has_errors():
                lines.append(f"  Errors: {len(self.validation_result.errors)}")
                for error in self.validation_result.errors[:3]:
                    lines.append(f"    {error}")
            if self.validation_result.has_warnings():
                lines.append(f"  Warnings: {len(self.validation_result.warnings)}")
                for warning in self.validation_result.warnings[:3]:
                    lines.append(f"    {warning}")
        
        # Location intelligence
        if self.unverified_location_data:
            lines.append(f"\n📊 Location Intelligence:")
            lines.append(f"  Seen {self.unverified_location_data.get('occurrence_count', 0)} times from {', '.join(self.unverified_location_data.get('sources', []))}")
            lines.append(f"  First seen: {self.unverified_location_data.get('first_seen', 'Unknown')[:10]}")
        
        if self.verified_location_suggestions:
            lines.append(f"\n💡 Verified Location Suggestions:")
            for suggestion in self.verified_location_suggestions[:3]:
                lines.append(f"  - {suggestion['name']} ({suggestion['lat']}, {suggestion['lon']})")
        
        # Historical context
        if self.previous_rejections:
            lines.append(f"\n⚠️  Previous Rejections: {len(self.previous_rejections)}")
            for rejection in self.previous_rejections[-2:]:
                lines.append(f"  - {rejection.get('rejected_at', 'Unknown')[:10]}: {rejection.get('reason', 'No reason')[:50]}")
        
        if self.similar_events:
            lines.append(f"\n🔄 Similar Past Events: {len(self.similar_events)}")
            for similar in self.similar_events[:3]:
                lines.append(f"  - {similar.get('title', 'Unknown')[:40]} @ {similar.get('location', {}).get('name', 'Unknown')[:30]}")
        
        # Reviewer notes
        if self.reviewer_notes:
            lines.append(f"\n📝 Reviewer Notes: {len(self.reviewer_notes)}")
            for note in self.reviewer_notes[-3:]:
                lines.append(f"  - [{note.get('type', 'note')}] {note.get('message', 'No message')[:60]}")
        
        # Attention flags
        if self.needs_attention_reasons:
            lines.append(f"\n⚠️  Needs Attention:")
            for reason in self.needs_attention_reasons:
                lines.append(f"  - {reason}")
        
        lines.append("═" * 60)
        return "\n".join(lines)


class EventContextAggregator:
    """
    Aggregates context for events from multiple sources.
    
    Provides editors with complete historical and contextual information
    to make informed decisions about pending events.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize context aggregator.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        self.assets_json = self.base_path / 'assets' / 'json'
        
        # Load all data sources
        self.published_events = self._load_json('events.json', key='events')
        self.pending_events = self._load_json('pending_events.json', key='pending_events')
        self.rejected_events = self._load_json('rejected_events.json', key='rejected_events')
        self.archived_events = self._load_archived_events()
        self.unverified_locations = self._load_json('unverified_locations.json', key='locations')
        self.verified_locations = self._load_json('verified_locations.json', key='locations')
        self.reviewer_notes = self._load_json('reviewer_notes.json')
    
    def _load_json(self, filename: str, key: Optional[str] = None) -> Any:
        """Load JSON file."""
        filepath = self.assets_json / filename
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(key, data) if key else data
            return [] if key else {}
        except Exception as e:
            print(f"  ⚠ Warning: Could not load {filename}: {e}")
            return [] if key else {}
    
    def _load_archived_events(self) -> List[Dict[str, Any]]:
        """Load all archived events from archive directory."""
        archived = []
        archive_dir = self.assets_json / 'events' / 'archived'
        
        if archive_dir.exists():
            for archive_file in archive_dir.glob('*.json'):
                try:
                    with open(archive_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        events = data.get('events', [])
                        archived.extend(events)
                except Exception as e:
                    print(f"  ⚠ Warning: Could not load {archive_file.name}: {e}")
        
        return archived
    
    def aggregate_context(self, event: Dict[str, Any]) -> EventContext:
        """
        Aggregate all available context for an event.
        
        Args:
            event: Event to aggregate context for
            
        Returns:
            EventContext with complete aggregated data
        """
        context = EventContext(event)
        
        # Get event identifiers for matching
        event_id = event.get('id', '')
        title = event.get('title', '').lower()
        location_name = event.get('location', {}).get('name', '').lower()
        source = event.get('source', '').lower()
        
        # Find previous rejections of same event
        context.previous_rejections = self._find_previous_rejections(event_id, title)
        
        # Find similar events (same venue, same source)
        context.similar_events = self._find_similar_events(title, location_name, source, event_id)
        
        # Get location intelligence
        if location_name:
            context.unverified_location_data = self._get_unverified_location_data(location_name)
            context.verified_location_suggestions = self._get_verified_location_suggestions(location_name)
        
        # Get reviewer notes
        context.reviewer_notes = self._get_reviewer_notes(event_id)
        
        # Add validation
        context.validation_result = self._validate_event(event)
        
        # Determine what needs attention
        context.needs_attention_reasons = self._analyze_attention_needs(event, context)
        
        return context
    
    def aggregate_bulk_context(self, events: List[Dict[str, Any]]) -> Dict[str, EventContext]:
        """
        Aggregate context for multiple events (bulk operation).
        
        Args:
            events: List of events to aggregate context for
            
        Returns:
            Dict mapping event_id to EventContext
        """
        contexts = {}
        for event in events:
            event_id = event.get('id', 'unknown')
            contexts[event_id] = self.aggregate_context(event)
        return contexts
    
    def _find_previous_rejections(self, event_id: str, title: str) -> List[Dict[str, Any]]:
        """Find previous rejections of the same event."""
        rejections = []
        
        for rejected in self.rejected_events:
            rejected_id = rejected.get('id', '')
            rejected_title = rejected.get('title', '').lower()
            
            # Match by ID or very similar title
            if rejected_id == event_id or (title and rejected_title and self._similarity_score(title, rejected_title) > 0.8):
                rejections.append(rejected)
        
        return rejections
    
    def _find_similar_events(self, title: str, location_name: str, source: str, exclude_id: str) -> List[Dict[str, Any]]:
        """Find similar events from history."""
        similar = []
        
        # Search in published, archived, and other pending events
        all_events = self.published_events + self.archived_events
        
        for event in all_events:
            if event.get('id') == exclude_id:
                continue
            
            event_title = event.get('title', '').lower()
            event_location = event.get('location', {}).get('name', '').lower()
            event_source = event.get('source', '').lower()
            
            # Same venue and source = highly similar
            if location_name and event_location and location_name == event_location and source == event_source:
                similar.append(event)
            # Same venue different source = similar
            elif location_name and event_location and location_name == event_location:
                similar.append(event)
            # Similar title and same source = possibly similar
            elif title and event_title and self._similarity_score(title, event_title) > 0.7 and source == event_source:
                similar.append(event)
        
        # Sort by most recent first
        similar.sort(key=lambda e: e.get('start_time', ''), reverse=True)
        return similar[:10]  # Limit to 10 most recent
    
    def _get_unverified_location_data(self, location_name: str) -> Optional[Dict[str, Any]]:
        """Get unverified location intelligence."""
        if not self.unverified_locations or not location_name:
            return None
        
        # Exact match
        if location_name in self.unverified_locations:
            return self.unverified_locations[location_name]
        
        # Case-insensitive match
        location_name_lower = location_name.lower()
        for name, data in self.unverified_locations.items():
            if name.lower() == location_name_lower:
                return data
        
        return None
    
    def _get_verified_location_suggestions(self, location_name: str) -> List[Dict[str, Any]]:
        """Get verified location suggestions based on name similarity."""
        suggestions = []
        
        if not self.verified_locations or not location_name:
            return suggestions
        
        location_name_lower = location_name.lower()
        
        for name, data in self.verified_locations.items():
            name_lower = name.lower()
            
            # Exact match
            if name_lower == location_name_lower:
                suggestions.append(data)
            # Partial match (e.g., "Museum" matches "Richard-Wagner-Museum")
            elif location_name_lower in name_lower or name_lower in location_name_lower:
                suggestions.append(data)
        
        return suggestions
    
    def _get_reviewer_notes(self, event_id: str) -> List[Dict[str, Any]]:
        """Get reviewer notes for event."""
        if not self.reviewer_notes or not event_id:
            return []
        
        notes = self.reviewer_notes.get(event_id, [])
        return notes if isinstance(notes, list) else []
    
    def _validate_event(self, event: Dict[str, Any]):
        """Validate event and return result."""
        try:
            from .event_validator import validate_event
            return validate_event(event)
        except ImportError:
            return None
    
    def _analyze_attention_needs(self, event: Dict[str, Any], context: EventContext) -> List[str]:
        """Analyze what needs editor attention."""
        reasons = []
        
        # Validation errors
        if context.validation_result and not context.validation_result.is_valid:
            reasons.append(f"❌ Validation errors: {len(context.validation_result.errors)}")
        
        # Missing coordinates
        location = event.get('location', {})
        if location.get('lat') is None or location.get('lon') is None:
            reasons.append("📍 Missing valid coordinates")
        
        # Needs review flag
        if location.get('needs_review'):
            reasons.append("🔍 Location needs verification")
        
        # Previously rejected
        if context.previous_rejections:
            reasons.append(f"⚠️  Previously rejected {len(context.previous_rejections)} time(s)")
        
        # Generic location
        generic_names = ['Hof', 'Bayreuth', 'Selb', 'Rehau', 'Kulmbach', 'Münchberg', 'Unknown']
        if location.get('name') in generic_names:
            reasons.append(f"⚠️  Generic location: '{location.get('name')}'")
        
        # Unverified location with high occurrence
        if context.unverified_location_data:
            count = context.unverified_location_data.get('occurrence_count', 0)
            if count >= 3:
                reasons.append(f"📊 Location seen {count} times, needs verification")
        
        return reasons
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate simple similarity score between two strings."""
        if not str1 or not str2:
            return 0.0
        
        # Simple word overlap scoring
        words1 = set(re.findall(r'\w+', str1.lower()))
        words2 = set(re.findall(r'\w+', str2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0


def get_event_context(event: Dict[str, Any], base_path: Path) -> EventContext:
    """
    Convenience function to get context for a single event.
    
    Args:
        event: Event to get context for
        base_path: Repository root path
        
    Returns:
        EventContext with aggregated data
    """
    aggregator = EventContextAggregator(base_path)
    return aggregator.aggregate_context(event)


def get_bulk_event_context(events: List[Dict[str, Any]], base_path: Path) -> Dict[str, EventContext]:
    """
    Convenience function to get context for multiple events.
    
    Args:
        events: Events to get context for
        base_path: Repository root path
        
    Returns:
        Dict mapping event_id to EventContext
    """
    aggregator = EventContextAggregator(base_path)
    return aggregator.aggregate_bulk_context(events)
