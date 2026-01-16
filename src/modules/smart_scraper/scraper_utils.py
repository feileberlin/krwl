"""
Common Scraper Utilities Module

Reusable utilities for scrapers to avoid code duplication (KISS principle).
Provides common functionality like:
- Coordinate extraction from map iframes
- Location normalization with verified locations
- Location tracking for unverified locations
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def round_coordinate(coord: float) -> float:
    """
    Round coordinate to exactly 4 decimal places.
    
    Standard for all coordinates in this software to ensure consistency
    and prevent duplicate locations with slightly different precision.
    
    Why 4 decimal places?
    - At latitude ~50° (Hof, Germany): 
      - 4 decimals = ~11m latitude, ~7m longitude precision
      - Meets the requirement of ~10 meters accuracy
      - Perfect for venue-level location accuracy
    - Prevents duplicates when same venue scraped with slightly different coords
    
    Example:
    - Theater Hof scraped as (50.320012, 11.918034) → (50.3200, 11.9180)
    - Theater Hof scraped as (50.319987, 11.917965) → (50.3200, 11.9180)
    - Result: Both point to same location on map (no duplicates!)
    
    Args:
        coord: Coordinate value (latitude or longitude)
        
    Returns:
        Coordinate rounded to 4 decimal places
    """
    return round(coord, 4)


def validate_coordinate_precision(coord: float, name: str = "coordinate") -> float:
    """
    Validate and enforce 4 decimal place precision for coordinates.
    
    Raises ValueError if coordinate has more than 4 decimal places.
    Use this for validating verified_locations.json and config files.
    
    Args:
        coord: Coordinate value to validate
        name: Name of coordinate for error message
        
    Returns:
        Validated coordinate (rounded to 4 decimals if needed)
        
    Raises:
        ValueError: If coordinate precision is invalid
    """
    rounded = round(coord, 4)
    # Check if rounding changed the value (meaning it had > 4 decimals)
    if abs(coord - rounded) > 1e-10:  # Small tolerance for floating point
        raise ValueError(
            f"{name} must have exactly 4 decimal places. "
            f"Got {coord}, should be {rounded}"
        )
    return rounded


class CoordinateExtractor:
    """Extract coordinates from various map iframe sources."""
    
    @staticmethod
    def extract_from_iframe(iframe_src: str) -> Optional[Tuple[float, float]]:
        """
        Extract lat/lon coordinates from map iframe URL.
        
        Coordinates are automatically rounded to 4 decimal places for consistency.
        
        Supports:
        - Google Maps: ?q=lat,lon, @lat,lon, &q=lat,lon
        - OpenStreetMap: ?mlat=lat&mlon=lon, #map=zoom/lat/lon
        - Apple Maps: ll=lat,lon, ?ll=lat,lon
        
        Args:
            iframe_src: The iframe src URL string
            
        Returns:
            Tuple of (latitude, longitude) rounded to 4 decimals, or None if not found
        """
        if not iframe_src:
            return None
        
        # Google Maps patterns: ?q=lat,lon or @lat,lon
        google_match = re.search(r'[?&@]q?=?(-?\d+\.\d+),(-?\d+\.\d+)', iframe_src)
        if google_match:
            lat = round_coordinate(float(google_match.group(1)))
            lon = round_coordinate(float(google_match.group(2)))
            return lat, lon
        
        # OpenStreetMap pattern: ?mlat=lat&mlon=lon
        osm_match1 = re.search(r'mlat=(-?\d+\.\d+)&mlon=(-?\d+\.\d+)', iframe_src)
        if osm_match1:
            lat = round_coordinate(float(osm_match1.group(1)))
            lon = round_coordinate(float(osm_match1.group(2)))
            return lat, lon
        
        # OpenStreetMap pattern: #map=zoom/lat/lon
        osm_match2 = re.search(r'#map=\d+/(-?\d+\.\d+)/(-?\d+\.\d+)', iframe_src)
        if osm_match2:
            lat = round_coordinate(float(osm_match2.group(1)))
            lon = round_coordinate(float(osm_match2.group(2)))
            return lat, lon
        
        # Apple Maps pattern: ll=lat,lon or ?ll=lat,lon
        apple_match = re.search(r'[?&]?ll=(-?\d+\.\d+),(-?\d+\.\d+)', iframe_src)
        if apple_match:
            lat = round_coordinate(float(apple_match.group(1)))
            lon = round_coordinate(float(apple_match.group(2)))
            return lat, lon
        
        return None


class LocationNormalizer:
    """Normalize locations using verified locations database."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize location normalizer.
        
        Args:
            base_path: Repository root path
        """
        self.verified_locations = {}
        self.location_tracker = None
        
        if base_path:
            self._load_verified_locations(Path(base_path))
            self._init_location_tracker(Path(base_path))
    
    def _load_verified_locations(self, base_path: Path):
        """Load verified locations from JSON file."""
        verified_file = base_path / 'assets' / 'json' / 'verified_locations.json'
        
        try:
            if verified_file.exists():
                with open(verified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verified_locations = data.get('locations', {})
        except Exception as e:
            print(f"  ⚠ Warning: Could not load verified locations: {e}")
    
    def _init_location_tracker(self, base_path: Path):
        """Initialize location tracker for unverified locations."""
        try:
            from ..location_tracker import LocationTracker
            self.location_tracker = LocationTracker(base_path)
        except ImportError:
            pass  # Location tracker not available
    
    def normalize(self, location: Dict[str, Any], source_name: str = 'unknown') -> Dict[str, Any]:
        """
        Normalize location using verified database.
        
        Checks for exact or case-insensitive match in verified_locations.json.
        Tracks unverified locations for editor review.
        
        Args:
            location: Location dict with name, lat, lon
            source_name: Name of the scraper source
            
        Returns:
            Normalized location dict (verified coords if found, original otherwise)
        """
        if not location or not location.get('name'):
            return location
        
        location_name = location.get('name', '').strip()
        
        # Exact match
        if location_name in self.verified_locations:
            verified = self.verified_locations[location_name].copy()
            return verified
        
        # Case-insensitive match
        location_name_lower = location_name.lower()
        for verified_name, verified_data in self.verified_locations.items():
            if verified_name.lower() == location_name_lower:
                return verified_data.copy()
        
        # No match - track as unverified
        if self.location_tracker:
            self.location_tracker.track_location(location, source=source_name)
        
        return location
    
    def save_tracked_locations(self) -> Optional[str]:
        """
        Save tracked unverified locations and return hint message.
        
        Returns:
            Hint message if there are locations to review, None otherwise
        """
        if self.location_tracker:
            self.location_tracker.save()
            return self.location_tracker.get_hint_message()
        return None


class AddressExtractor:
    """Extract addresses from German text patterns."""
    
    # German address pattern: Street Number, ZIP City
    GERMAN_ADDRESS_PATTERN = r'([A-ZÄÖÜ][a-zäöüß\-\s\.]+\s+\d+[a-z]?\s*,\s*\d{5}\s+[A-ZÄÖÜ][a-zäöüß\-\s]+)'
    
    @staticmethod
    def extract_german_address(text: str) -> Optional[str]:
        """
        Extract German address from text.
        
        Pattern: Street Number, ZIP City
        Example: "Maximilianstraße 33, 95444 Bayreuth"
        
        Args:
            text: Text to search for address
            
        Returns:
            First address found or None
        """
        if not text:
            return None
        
        matches = re.findall(AddressExtractor.GERMAN_ADDRESS_PATTERN, text)
        return matches[0].strip() if matches else None


class VenueDetector:
    """Detect venue names from headings and text."""
    
    # Common German venue types
    # These appear in compound words (e.g., "Freiheitshalle" = Freedom Hall)
    VENUE_TYPES = [
        'Museum', 'Halle', 'Schloss', 'Galerie', 'Theater',
        'Kirche', 'Zentrum', 'Haus', 'Platz', 'Rathaus',
        'Saal', 'Kulturzentrum', 'Bibliothek', 'Stadthalle',
        'Konzerthaus', 'Oper', 'Festspielhaus', 'Dom'
    ]
    
    @staticmethod
    def contains_venue_indicator(text: str) -> bool:
        """
        Check if text contains a venue type indicator.
        
        Uses substring matching to handle German compound words where
        venue types are embedded (e.g., "Freiheitshalle" contains "halle").
        This is appropriate because German combines words: "Freiheit" + "halle" = "Freiheitshalle".
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains a venue type
        """
        if not text:
            return False
        
        text_lower = text.lower()
        return any(venue_type.lower() in text_lower for venue_type in VenueDetector.VENUE_TYPES)
    
    @staticmethod
    def extract_venue_from_headings(headings: list) -> Optional[str]:
        """
        Extract venue name from HTML headings.
        
        Args:
            headings: List of heading elements (BeautifulSoup elements)
            
        Returns:
            First heading text containing a venue type as a complete word, or None
        """
        for heading in headings:
            text = heading.get_text(strip=True)
            if VenueDetector.contains_venue_indicator(text):
                return text
        
        return None
