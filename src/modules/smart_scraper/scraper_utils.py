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
    """
    Normalize locations using verified database and handle ambiguous names.
    
    Enhanced with modular utilities:
    - GeolocationResolver for coordinate resolution
    - AmbiguousLocationHandler for disambiguation
    - CityDetector for city extraction
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize location normalizer.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = base_path
        self.verified_locations = {}
        self.location_tracker = None
        self.geolocation_resolver = None
        
        if base_path:
            self._load_verified_locations(Path(base_path))
            self._init_location_tracker(Path(base_path))
            self.geolocation_resolver = GeolocationResolver(Path(base_path))
    
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
        Normalize location using verified database and disambiguation.
        
        Process:
        1. Check verified locations (exact/case-insensitive match)
        2. Disambiguate ambiguous location names (append city)
        3. Track unverified locations for editor review
        
        Args:
            location: Location dict with name, lat, lon
            source_name: Name of the scraper source
            
        Returns:
            Normalized location dict
        """
        if not location or not location.get('name'):
            return location
        
        location_name = location.get('name', '').strip()
        
        # Step 1: Check verified locations (exact match)
        if location_name in self.verified_locations:
            verified = self.verified_locations[location_name].copy()
            return verified
        
        # Step 2: Check verified locations (case-insensitive match)
        location_name_lower = location_name.lower()
        for verified_name, verified_data in self.verified_locations.items():
            if verified_name.lower() == location_name_lower:
                return verified_data.copy()
        
        # Step 3: Disambiguate ambiguous locations (append city name)
        location = AmbiguousLocationHandler.disambiguate(location)
        
        # Step 4: Track as unverified for editor review
        if self.location_tracker:
            self.location_tracker.track_location(location, source=source_name)
        
        return location
    
    def resolve_coordinates(
        self,
        location_name: Optional[str] = None,
        address: Optional[str] = None,
        coordinates: Optional[Tuple[float, float]] = None,
        source_name: str = 'unknown'
    ) -> Dict[str, Any]:
        """
        Resolve location coordinates using GeolocationResolver.
        
        This is a modular replacement for scattered coordinate estimation logic.
        
        Args:
            location_name: Venue/location name
            address: Full address string
            coordinates: Tuple of (lat, lon) if already extracted
            source_name: Scraper source name
            
        Returns:
            Location dict with name, lat, lon, needs_review, resolution_method
        """
        if self.geolocation_resolver:
            return self.geolocation_resolver.resolve(
                location_name=location_name,
                address=address,
                coordinates=coordinates,
                source_name=source_name
            )
        
        # Fallback if resolver not available
        return {
            'name': location_name or address or 'Unknown',
            'lat': coordinates[0] if coordinates else None,
            'lon': coordinates[1] if coordinates else None,
            'needs_review': True,
            'resolution_method': 'fallback'
        }
    
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


class CityDetector:
    """
    Extract city names from addresses, venue names, or coordinates.
    
    Modular utility for identifying which city an event is in.
    Used for:
    - Disambiguating ambiguous location names (e.g., "Sportheim" → "Sportheim Hof")
    - Reverse geocoding coordinates to city names
    - Extracting city from German addresses
    """
    
    # Known cities in the region with coordinates
    KNOWN_CITIES = {
        'bayreuth': {'name': 'Bayreuth', 'lat': 49.9440, 'lon': 11.5760},
        'hof': {'name': 'Hof', 'lat': 50.3167, 'lon': 11.9167},
        'selb': {'name': 'Selb', 'lat': 50.1705, 'lon': 12.1328},
        'rehau': {'name': 'Rehau', 'lat': 50.2489, 'lon': 12.0364},
        'kulmbach': {'name': 'Kulmbach', 'lat': 50.1050, 'lon': 11.4458},
        'münchberg': {'name': 'Münchberg', 'lat': 50.1900, 'lon': 11.7900},
    }
    
    @staticmethod
    def extract_from_text(text: str) -> Optional[str]:
        """
        Extract city name from text (venue name or address).
        
        Uses word boundary matching to avoid false matches
        (e.g., "Bahnhof" should NOT match "Hof").
        
        Args:
            text: Text to search for city name
            
        Returns:
            City name if found, None otherwise
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Check for city names as complete words (word boundaries)
        # This prevents "Bahnhof" from matching "Hof"
        for city_key, city_data in CityDetector.KNOWN_CITIES.items():
            # Use word boundary regex to match complete words only
            pattern = r'\b' + re.escape(city_key) + r'\b'
            if re.search(pattern, text_lower):
                return city_data['name']
        
        return None
    
    @staticmethod
    def extract_from_address(address: str) -> Optional[str]:
        """
        Extract city name from German address.
        
        Pattern: Street Number, ZIP City
        Example: "Maximilianstraße 33, 95444 Bayreuth" → "Bayreuth"
        
        Args:
            address: German address string
            
        Returns:
            City name if found, None otherwise
        """
        if not address:
            return None
        
        # Extract city from end of address (after ZIP code)
        # Pattern: ZIP City at end
        match = re.search(r'\d{5}\s+([A-ZÄÖÜ][a-zäöüß\-\s]+)$', address.strip())
        if match:
            return match.group(1).strip()
        
        # Fallback: look for known city names
        return CityDetector.extract_from_text(address)
    
    @staticmethod
    def extract_from_coordinates(lat: float, lon: float, tolerance_km: float = 10.0) -> Optional[str]:
        """
        Reverse geocode coordinates to nearest city.
        
        Uses simple distance calculation to nearest known city.
        This is a lightweight alternative to full geocoding APIs.
        
        Args:
            lat: Latitude
            lon: Longitude
            tolerance_km: Maximum distance to consider (default: 10km)
            
        Returns:
            Nearest city name if within tolerance, None otherwise
        """
        if lat is None or lon is None:
            return None
        
        # Simple distance calculation (good enough for nearby cities)
        # Haversine formula would be more accurate but this is sufficient
        min_distance = float('inf')
        nearest_city = None
        
        for city_data in CityDetector.KNOWN_CITIES.values():
            city_lat = city_data['lat']
            city_lon = city_data['lon']
            
            # Approximate distance in km (simplified calculation)
            # At latitude ~50°: 1° lat ≈ 111km, 1° lon ≈ 71km
            lat_diff = abs(lat - city_lat) * 111
            lon_diff = abs(lon - city_lon) * 71
            distance = (lat_diff**2 + lon_diff**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest_city = city_data['name']
        
        if min_distance <= tolerance_km:
            return nearest_city
        
        return None
    
    @staticmethod
    def get_city_coordinates(city_name: str) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a known city.
        
        Args:
            city_name: City name
            
        Returns:
            Dict with lat/lon if city known, None otherwise
        """
        if not city_name:
            return None
        
        city_lower = city_name.lower()
        if city_lower in CityDetector.KNOWN_CITIES:
            city_data = CityDetector.KNOWN_CITIES[city_lower]
            return {'lat': city_data['lat'], 'lon': city_data['lon']}
        
        return None


class AmbiguousLocationHandler:
    """
    Handle ambiguous location names by appending city names.
    
    Prevents confusion when multiple venues share the same generic name
    (e.g., "Sportheim" exists in multiple cities).
    
    Examples:
    - "Sportheim" + Hof coordinates → "Sportheim Hof"
    - "Bahnhof" + Bayreuth coordinates → "Bahnhof Bayreuth"
    - "Rathaus" + Selb coordinates → "Rathaus Selb"
    """
    
    # Ambiguous location types (generic names that appear in multiple places)
    AMBIGUOUS_TYPES = [
        # Sports facilities
        'Sportheim', 'Sportplatz', 'Sportzentrum', 'Stadion', 'Turnhalle',
        'Sporthalle', 'Schwimmhalle', 'Freibad', 'Hallenbad',
        
        # Public buildings
        'Bahnhof', 'Rathaus', 'Feuerwehrhaus', 'Bürgerhaus', 'Gemeindehaus',
        'Mehrzweckhalle', 'Veranstaltungshalle', 'Stadthalle',
        
        # Cultural/social venues
        'Vereinsheim', 'Dorfgemeinschaftshaus', 'Kulturzentrum', 'Jugendzentrum',
        'Bürgerzentrum', 'Gemeindezentrum',
        
        # Religious
        'Kirche', 'Kapelle', 'Pfarrheim', 'Gemeindehaus',
        
        # Educational
        'Schule', 'Grundschule', 'Gymnasium', 'Kindergarten',
        
        # Other
        'Marktplatz', 'Friedhof', 'Parkplatz'
    ]
    
    @staticmethod
    def is_ambiguous(location_name: str) -> bool:
        """
        Check if a location name is ambiguous.
        
        Args:
            location_name: Location name to check
            
        Returns:
            True if location name is ambiguous (needs city suffix)
        """
        if not location_name:
            return False
        
        name_lower = location_name.lower()
        
        # Check if location name contains any ambiguous type
        # Use word boundary matching to avoid false positives
        # (e.g., "Freiheitshalle" should not match "halle")
        for ambiguous_type in AmbiguousLocationHandler.AMBIGUOUS_TYPES:
            type_lower = ambiguous_type.lower()
            
            # Exact match or at start/end of compound word
            if (name_lower == type_lower or 
                name_lower.startswith(type_lower + ' ') or
                name_lower.endswith(' ' + type_lower) or
                name_lower.startswith(type_lower + '-') or
                name_lower.endswith('-' + type_lower)):
                return True
        
        return False
    
    @staticmethod
    def disambiguate(location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Disambiguate location by appending city name if ambiguous.
        
        Uses coordinates to determine city, then appends city name.
        
        Args:
            location: Location dict with name, lat, lon
            
        Returns:
            Updated location dict with city suffix if needed
        """
        if not location or not location.get('name'):
            return location
        
        location_name = location.get('name', '').strip()
        
        # Check if location is ambiguous
        if not AmbiguousLocationHandler.is_ambiguous(location_name):
            return location
        
        # Check if city name already in location name
        city_from_name = CityDetector.extract_from_text(location_name)
        if city_from_name:
            # City already in name, no need to disambiguate
            return location
        
        # Determine city from coordinates
        lat = location.get('lat')
        lon = location.get('lon')
        if lat is not None and lon is not None:
            city = CityDetector.extract_from_coordinates(lat, lon)
            if city:
                # Append city name
                disambiguated_name = f"{location_name} {city}"
                return {
                    **location,
                    'name': disambiguated_name
                }
        
        # Could not disambiguate (no coordinates or no nearby city)
        return location


class GeolocationResolver:
    """
    Resolve event geolocations using multiple strategies.
    
    Modular replacement for scattered coordinate estimation logic.
    
    Resolution strategies (in order):
    1. Verified locations database (exact matches)
    2. Extracted iframe coordinates (from embedded maps)
    3. Geocoding from address (if available)
    4. City lookup from venue name
    5. Editor review flag (never silent default)
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize geolocation resolver.
        
        Args:
            base_path: Repository root path for loading verified locations
        """
        self.verified_locations = {}
        self.location_tracker = None
        
        if base_path:
            self._load_verified_locations(Path(base_path))
            self._init_location_tracker(Path(base_path))
    
    def _load_verified_locations(self, base_path: Path):
        """Load verified locations database."""
        verified_file = base_path / 'assets' / 'json' / 'verified_locations.json'
        
        try:
            if verified_file.exists():
                with open(verified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verified_locations = data.get('locations', {})
        except Exception as e:
            print(f"  ⚠ Warning: Could not load verified locations: {e}")
    
    def _init_location_tracker(self, base_path: Path):
        """Initialize location tracker."""
        try:
            from ..location_tracker import LocationTracker
            self.location_tracker = LocationTracker(base_path)
        except ImportError:
            pass
    
    def resolve(
        self,
        location_name: Optional[str] = None,
        address: Optional[str] = None,
        coordinates: Optional[Tuple[float, float]] = None,
        source_name: str = 'unknown'
    ) -> Dict[str, Any]:
        """
        Resolve location to coordinates using multiple strategies.
        
        Returns location dict with:
        - name: Location name
        - address: Full address (REQUIRED)
        - lat, lon: Coordinates (rounded to 4 decimals)
        - needs_review: True if coordinates are estimated/flagged
        - resolution_method: How coordinates were determined
        
        Args:
            location_name: Venue/location name
            address: Full address string (REQUIRED for complete validation)
            coordinates: Tuple of (lat, lon) if already extracted
            source_name: Scraper source name
            
        Returns:
            Location dict with name, address, lat, lon, needs_review, resolution_method
        """
        result = {
            'name': location_name or address or 'Unknown Location',
            'address': address,  # REQUIRED - will be None if not provided
            'lat': None,
            'lon': None,
            'needs_review': False,
            'resolution_method': 'unknown'
        }
        
        # Strategy 1: Use provided coordinates (from iframe extraction)
        if coordinates and coordinates[0] is not None and coordinates[1] is not None:
            result['lat'] = round_coordinate(coordinates[0])
            result['lon'] = round_coordinate(coordinates[1])
            result['resolution_method'] = 'iframe_extraction'
            result['needs_review'] = False
            
            # If we have coordinates but no address, extract from location name
            if not result['address'] and location_name:
                # Try to extract city and build basic address
                city = CityDetector.extract_from_text(location_name)
                if city:
                    result['address'] = f"{location_name}, {city}"
                    result['needs_review'] = True  # Address needs verification
            
            return result
        
        # Strategy 2: Check verified locations database (exact match)
        if location_name and location_name in self.verified_locations:
            verified = self.verified_locations[location_name].copy()
            result.update(verified)
            result['resolution_method'] = 'verified_database'
            result['needs_review'] = False
            return result
        
        # Strategy 3: Extract city from address and use city coordinates
        if address:
            city = CityDetector.extract_from_address(address)
            if city:
                city_coords = CityDetector.get_city_coordinates(city)
                if city_coords:
                    result['lat'] = city_coords['lat']
                    result['lon'] = city_coords['lon']
                    result['address'] = address  # Keep provided address
                    result['resolution_method'] = 'address_city_lookup'
                    result['needs_review'] = True  # City center, not exact venue
                    
                    # Track for editor review
                    if self.location_tracker:
                        self.location_tracker.track_location(result, source=source_name)
                    
                    return result
        
        # Strategy 4: Extract city from venue name
        if location_name:
            city = CityDetector.extract_from_text(location_name)
            if city:
                city_coords = CityDetector.get_city_coordinates(city)
                if city_coords:
                    result['lat'] = city_coords['lat']
                    result['lon'] = city_coords['lon']
                    # Build basic address from venue name and city
                    result['address'] = f"{location_name}, {city}"
                    result['resolution_method'] = 'venue_name_city_lookup'
                    result['needs_review'] = True  # City center, not exact venue
                    
                    # Track for editor review
                    if self.location_tracker:
                        self.location_tracker.track_location(result, source=source_name)
                    
                    return result
        
        # Strategy 5: No coordinates found - flag for editor review
        result['needs_review'] = True
        result['resolution_method'] = 'unresolved'
        
        # Track for editor review
        if self.location_tracker and location_name:
            self.location_tracker.track_location(result, source=source_name)
        
        return result
    
    def save_tracked_locations(self) -> Optional[str]:
        """Save tracked locations and return hint message."""
        if self.location_tracker:
            self.location_tracker.save()
            return self.location_tracker.get_hint_message()
        return None
