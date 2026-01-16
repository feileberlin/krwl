"""
Location Tracker Module

Collects and manages unverified locations from scrapers for editor review.
This keeps scraper code simple (KISS) while providing location management features.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class LocationTracker:
    """
    Tracks unverified locations for editor review.
    
    Collects locations that are not in verified_locations.json so editors can
    review them and add verified entries to prevent duplicate location entries.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize location tracker.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        self.unverified_file = self.base_path / 'assets' / 'json' / 'unverified_locations.json'
        self.verified_file = self.base_path / 'assets' / 'json' / 'verified_locations.json'
        self.unverified_locations = {}
        self.verified_locations = {}
        self._load_data()
    
    def _load_data(self):
        """Load existing unverified and verified locations."""
        # Load unverified locations
        if self.unverified_file.exists():
            try:
                with open(self.unverified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unverified_locations = data.get('locations', {})
            except Exception as e:
                print(f"  ⚠ Warning: Could not load unverified locations: {e}")
        
        # Load verified locations
        if self.verified_file.exists():
            try:
                with open(self.verified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verified_locations = data.get('locations', {})
            except Exception as e:
                print(f"  ⚠ Warning: Could not load verified locations: {e}")
    
    def is_verified(self, location_name: str) -> bool:
        """
        Check if a location is already verified.
        
        Args:
            location_name: Name of the location
            
        Returns:
            True if location is in verified database
        """
        if not location_name:
            return False
        
        name_lower = location_name.strip().lower()
        return any(vname.lower() == name_lower for vname in self.verified_locations.keys())
    
    def track_location(self, location: Dict[str, Any], source: str = 'unknown'):
        """
        Track an unverified location.
        
        Coordinates are automatically rounded to 4 decimal places for consistency.
        
        Args:
            location: Location dict with name, lat, lon
            source: Source scraper name (for reference)
        """
        if not location or not location.get('name'):
            return
        
        location_name = location.get('name', '').strip()
        
        # Skip if already verified
        if self.is_verified(location_name):
            return
        
        # Skip generic/default locations
        generic_names = ['Unknown', 'Hof', 'Bayreuth', 'Selb', 'Rehau', 'Kulmbach', 'Münchberg']
        if location_name in generic_names:
            return
        
        # Round coordinates to 4 decimal places with type safety
        raw_lat = location.get('lat')
        raw_lon = location.get('lon')
        lat: Optional[float] = None
        lon: Optional[float] = None
        if raw_lat is not None:
            try:
                lat = round(float(raw_lat), 4)
            except (TypeError, ValueError):
                lat = None
        if raw_lon is not None:
            try:
                lon = round(float(raw_lon), 4)
            except (TypeError, ValueError):
                lon = None
        
        # Add or update entry
        if location_name not in self.unverified_locations:
            self.unverified_locations[location_name] = {
                'name': location_name,
                'lat': lat,
                'lon': lon,
                'address': location.get('address'),
                'occurrence_count': 1,
                'sources': [source],
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
        else:
            # Update existing entry
            entry = self.unverified_locations[location_name]
            entry['occurrence_count'] = entry.get('occurrence_count', 0) + 1
            entry['last_seen'] = datetime.now().isoformat()
            
            # Add source if not already listed
            if source not in entry.get('sources', []):
                entry.setdefault('sources', []).append(source)
            
            # Update coordinates if provided (rounded to 4 decimals)
            if lat is not None and lon is not None:
                entry['lat'] = lat
                entry['lon'] = lon
    
    def save(self):
        """Save unverified locations to JSON file."""
        if not self.unverified_locations:
            return
        
        try:
            # Sort by occurrence count (most frequent first)
            sorted_locations = dict(sorted(
                self.unverified_locations.items(),
                key=lambda x: x[1].get('occurrence_count', 0),
                reverse=True
            ))
            
            total_occurrences = sum(
                loc.get('occurrence_count', 0) 
                for loc in sorted_locations.values()
            )
            
            data = {
                '_comment': 'Unverified locations collected during scraping',
                '_description': 'Review these and add verified entries to verified_locations.json',
                '_stats': {
                    'total_locations': len(sorted_locations),
                    'total_occurrences': total_occurrences
                },
                'locations': sorted_locations
            }
            
            with open(self.unverified_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"  ⚠ Warning: Could not save unverified locations: {e}")
    
    def get_hint_message(self) -> Optional[str]:
        """
        Get editor hint message about unverified locations.
        
        Returns:
            Hint message if there are enough unverified locations, None otherwise
        """
        if not self.unverified_locations:
            return None
        
        total_occurrences = sum(
            loc.get('occurrence_count', 0) 
            for loc in self.unverified_locations.values()
        )
        
        # Show hint if >= 5 locations or >= 10 occurrences
        if len(self.unverified_locations) >= 5 or total_occurrences >= 10:
            return (
                f"💡 {len(self.unverified_locations)} unverified locations "
                f"({total_occurrences} occurrences). "
                f"Review: assets/json/unverified_locations.json"
            )
        
        return None
