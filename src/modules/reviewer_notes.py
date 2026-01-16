"""
Reviewer Notes System for Event Location Ambiguity

This module adds a review notes system to flag events with ambiguous or uncertain
location extraction for manual verification.

Key features:
- Confidence scoring for location extraction
- Reviewer flags for ambiguous cases
- Notes system for editors
- Auto-flagging of edge cases
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class LocationConfidence:
    """Confidence levels for location extraction."""
    HIGH = "high"       # Clear venue + address with coordinates
    MEDIUM = "medium"   # Venue name or address found
    LOW = "low"         # Only city name or default location
    UNKNOWN = "unknown" # No location information found


class ReviewerNotes:
    """
    System for adding reviewer notes to events with ambiguous location data.
    
    This helps editors quickly identify events that need manual location verification.
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.notes_file = self.base_path / 'assets' / 'json' / 'reviewer_notes.json'
        
        # Ensure directory exists
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)
    
    def add_location_confidence(self, event: Dict[str, Any], 
                               confidence: str,
                               reason: str,
                               extraction_method: str = None) -> Dict[str, Any]:
        """
        Add location confidence metadata to an event.
        
        Args:
            event: Event dictionary
            confidence: Confidence level (high/medium/low/unknown)
            reason: Why this confidence level was assigned
            extraction_method: How location was extracted
            
        Returns:
            Event with added metadata
        """
        if 'metadata' not in event:
            event['metadata'] = {}
        
        event['metadata']['location_confidence'] = {
            'level': confidence,
            'reason': reason,
            'extraction_method': extraction_method or 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Flag for review if confidence is low or medium
        if confidence in [LocationConfidence.LOW, LocationConfidence.MEDIUM]:
            event['metadata']['needs_review'] = True
            event['metadata']['review_reason'] = f"Location confidence: {confidence} - {reason}"
        
        return event
    
    def flag_for_review(self, event: Dict[str, Any], 
                       reason: str,
                       category: str = "location") -> Dict[str, Any]:
        """
        Flag an event for manual review.
        
        Args:
            event: Event dictionary
            reason: Why this needs review
            category: Category of issue (location/date/duplicate/spam)
            
        Returns:
            Event with review flag
        """
        if 'metadata' not in event:
            event['metadata'] = {}
        
        event['metadata']['needs_review'] = True
        event['metadata']['review_category'] = category
        event['metadata']['review_reason'] = reason
        event['metadata']['flagged_at'] = datetime.now().isoformat()
        
        return event
    
    def add_reviewer_note(self, event_id: str, note: str, 
                         reviewer: str = "scraper") -> None:
        """
        Add a note about an event for reviewers to see.
        
        Args:
            event_id: Event ID
            note: Note text
            reviewer: Who added the note
        """
        notes = self._load_notes()
        
        if event_id not in notes:
            notes[event_id] = []
        
        notes[event_id].append({
            'note': note,
            'reviewer': reviewer,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_notes(notes)
    
    def get_reviewer_notes(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all reviewer notes for an event."""
        notes = self._load_notes()
        return notes.get(event_id, [])
    
    def get_events_needing_review(self, category: Optional[str] = None) -> List[str]:
        """
        Get list of event IDs that need review.
        
        Args:
            category: Optional filter by category (location/date/duplicate/spam)
            
        Returns:
            List of event IDs
        """
        notes = self._load_notes()
        
        if category:
            return [
                event_id for event_id, event_notes in notes.items()
                if any(n.get('review_category') == category for n in event_notes)
            ]
        
        return list(notes.keys())
    
    def _load_notes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load reviewer notes from file."""
        if not self.notes_file.exists():
            return {}
        
        try:
            with open(self.notes_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_notes(self, notes: Dict[str, List[Dict[str, Any]]]):
        """Save reviewer notes to file."""
        with open(self.notes_file, 'w') as f:
            json.dump(notes, f, indent=2)


class LocationExtractionHelper:
    """
    Helper functions for location extraction with confidence scoring.
    
    Use these in custom source handlers to automatically flag ambiguous cases.
    """
    
    @staticmethod
    def detect_ambiguous_location(location_name: str, 
                                  known_cities: List[str]) -> Optional[str]:
        """
        Detect if a location name is ambiguous.
        
        Examples of ambiguous cases:
        - "Freiheitshalle Hof" - Is this "Freiheitshalle" in "Hof" or just "Hof"?
        - "Museum Berlin" - Is this "Museum" or "Berlin"?
        - "City Hall" - Which city?
        
        Args:
            location_name: Location text to check
            known_cities: List of known city names
            
        Returns:
            Reason string if ambiguous, None otherwise
        """
        location_lower = location_name.lower()
        
        # Check if location contains both a venue indicator and a city name
        venue_indicators = [
            'halle', 'museum', 'galerie', 'theater', 'kirche', 
            'zentrum', 'haus', 'platz', 'rathaus', 'saal',
            'hall', 'gallery', 'church', 'center', 'house'
        ]
        
        has_venue = any(indicator in location_lower for indicator in venue_indicators)
        has_city = any(city.lower() in location_lower for city in known_cities)
        
        if has_venue and has_city:
            return f"Location contains both venue indicator and city name: '{location_name}'. Unclear if this is the venue name or just the city."
        
        # Check if location is only a city name without venue
        if location_name in known_cities:
            return f"Location is only a city name without specific venue: '{location_name}'"
        
        # Check if location has no address details (no street number/ZIP)
        import re
        has_address = re.search(r'\d+.*\d{5}', location_name)  # Number + ZIP pattern
        if not has_address and has_venue:
            return f"Venue name without full address: '{location_name}'. Coordinates may be imprecise."
        
        return None
    
    @staticmethod
    def calculate_confidence(location: Dict[str, Any],
                           has_full_address: bool = False,
                           has_venue_name: bool = False,
                           used_default: bool = False,
                           used_geocoding: bool = False) -> str:
        """
        Calculate confidence level for location extraction.
        
        Args:
            location: Location dictionary
            has_full_address: Whether full street address was found
            has_venue_name: Whether specific venue name was found
            used_default: Whether default/fallback location was used
            used_geocoding: Whether geocoding service was used
            
        Returns:
            Confidence level (high/medium/low/unknown)
        """
        if used_default:
            return LocationConfidence.LOW
        
        if has_full_address and used_geocoding:
            return LocationConfidence.HIGH
        
        if has_full_address or (has_venue_name and used_geocoding):
            return LocationConfidence.MEDIUM
        
        if has_venue_name:
            return LocationConfidence.MEDIUM
        
        if location.get('name') and location.get('name') != 'Unknown':
            return LocationConfidence.LOW
        
        return LocationConfidence.UNKNOWN
    
    @staticmethod
    def should_flag_for_review(confidence: str, 
                              ambiguity_reason: Optional[str] = None) -> bool:
        """
        Determine if event should be flagged for review based on location confidence.
        
        Args:
            confidence: Confidence level
            ambiguity_reason: Reason from detect_ambiguous_location()
            
        Returns:
            True if should be flagged for review
        """
        # Always flag unknown or low confidence
        if confidence in [LocationConfidence.UNKNOWN, LocationConfidence.LOW]:
            return True
        
        # Flag medium confidence if there's an ambiguity reason
        if confidence == LocationConfidence.MEDIUM and ambiguity_reason:
            return True
        
        return False


def enhance_event_with_location_confidence(
    event: Dict[str, Any],
    reviewer_notes: ReviewerNotes,
    extraction_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhance an event with location confidence and review flags.
    
    This is a convenience function to add location metadata and reviewer flags
    to events during scraping.
    
    Args:
        event: Event dictionary
        reviewer_notes: ReviewerNotes instance
        extraction_details: Details about how location was extracted:
            - has_full_address: bool
            - has_venue_name: bool
            - used_default: bool
            - used_geocoding: bool
            - extraction_method: str
            - known_cities: List[str]
    
    Returns:
        Enhanced event with metadata
    
    Example:
        ```python
        event = scrape_event_from_page(soup)
        
        extraction_details = {
            'has_full_address': True,
            'has_venue_name': True,
            'used_default': False,
            'used_geocoding': False,
            'extraction_method': 'detail_page_label',
            'known_cities': ['Hof', 'Bayreuth', 'Selb']
        }
        
        event = enhance_event_with_location_confidence(
            event, reviewer_notes, extraction_details
        )
        ```
    """
    location = event.get('location', {})
    location_name = location.get('name', '')
    
    # Calculate confidence
    confidence = LocationExtractionHelper.calculate_confidence(
        location,
        has_full_address=extraction_details.get('has_full_address', False),
        has_venue_name=extraction_details.get('has_venue_name', False),
        used_default=extraction_details.get('used_default', False),
        used_geocoding=extraction_details.get('used_geocoding', False)
    )
    
    # Check for ambiguity
    known_cities = extraction_details.get('known_cities', [])
    ambiguity_reason = LocationExtractionHelper.detect_ambiguous_location(
        location_name, known_cities
    )
    
    # Build reason text
    reason_parts = []
    if extraction_details.get('has_full_address'):
        reason_parts.append("full address found")
    elif extraction_details.get('has_venue_name'):
        reason_parts.append("venue name found")
    elif extraction_details.get('used_default'):
        reason_parts.append("used default location")
    
    if ambiguity_reason:
        reason_parts.append(ambiguity_reason)
    
    reason = "; ".join(reason_parts) if reason_parts else "location extracted"
    
    # Add confidence metadata
    event = reviewer_notes.add_location_confidence(
        event,
        confidence=confidence,
        reason=reason,
        extraction_method=extraction_details.get('extraction_method', 'unknown')
    )
    
    # Flag for review if needed
    should_flag = LocationExtractionHelper.should_flag_for_review(
        confidence, ambiguity_reason
    )
    
    if should_flag:
        flag_reason = f"Location needs verification: {reason}"
        event = reviewer_notes.flag_for_review(
            event, flag_reason, category="location"
        )
        
        # Add note for reviewer
        reviewer_notes.add_reviewer_note(
            event['id'],
            f"Location extraction confidence: {confidence}. {reason}",
            reviewer="auto_scraper"
        )
    
    return event


# Export main classes and functions
__all__ = [
    'ReviewerNotes',
    'LocationConfidence',
    'LocationExtractionHelper',
    'enhance_event_with_location_confidence'
]
