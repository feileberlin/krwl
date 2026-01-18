"""
VGN Transit Integration Module

Integrates with VGN (Verkehrsverbund Großraum Nürnberg) Open Data API
to analyze public transport reachability and suggest event sources.

This module provides:
- Station reachability analysis (which stations are reachable within X minutes)
- Municipality/region identification based on transit connectivity
- Social media source suggestions for reachable areas
- Transit time information for events

API Documentation: https://www.vgn.de/web-entwickler/open-data/
Python Library: https://github.com/becheran/vgn
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import VGN library (optional dependency)
try:
    from vgn import VGN
    VGN_AVAILABLE = True
except ImportError:
    VGN_AVAILABLE = False
    logger.warning("VGN library not installed. Install with: pip install vgn")


@dataclass
class ReachableStation:
    """Represents a station reachable via public transit"""
    name: str
    id: str
    municipality: str
    latitude: float
    longitude: float
    travel_time_minutes: int
    transfers: int
    line: Optional[str] = None


@dataclass
class RegionalSource:
    """Represents a potential event source in a reachable region"""
    name: str
    type: str  # 'facebook', 'html', 'rss', 'instagram'
    url: str
    municipality: str
    category: str
    description: str
    distance_km: float
    travel_time_minutes: int


@dataclass
class CulturalVenue:
    """Represents a cultural venue discovered near transit stations"""
    name: str
    venue_type: str  # 'museum', 'theatre', 'gallery', 'cinema', 'community_centre'
    latitude: float
    longitude: float
    address: Optional[str] = None
    website: Optional[str] = None
    nearest_station: Optional[str] = None
    distance_to_station_km: Optional[float] = None
    travel_time_minutes: Optional[int] = None
    osm_id: Optional[str] = None


class VGNTransit:
    """
    VGN Transit Integration for Reachability Analysis
    
    Analyzes public transport connectivity from a reference location
    to identify reachable stations, municipalities, and potential event sources.
    """
    
    def __init__(self, config: Dict, base_path: Path):
        """
        Initialize VGN Transit integration
        
        Args:
            config: Configuration dictionary
            base_path: Base path to project root
        """
        self.config = config
        self.base_path = base_path
        self.vgn_config = config.get('vgn', {})
        self.enabled = self.vgn_config.get('enabled', False)
        
        # Get reference location (default to Hof main station)
        map_config = config.get('map', {})
        default_center = map_config.get('default_center', {})
        self.reference_lat = self.vgn_config.get('reference_location', {}).get(
            'lat', default_center.get('lat', 50.3167)
        )
        self.reference_lon = self.vgn_config.get('reference_location', {}).get(
            'lon', default_center.get('lon', 11.9167)
        )
        
        # Initialize VGN API client if available
        self.vgn_client = None
        if VGN_AVAILABLE and self.enabled:
            try:
                self.vgn_client = VGN()
                logger.info("VGN API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize VGN client: {e}")
                self.enabled = False
    
    def is_available(self) -> bool:
        """Check if VGN integration is available and enabled"""
        return VGN_AVAILABLE and self.enabled and self.vgn_client is not None
    
    def get_reachable_stations(
        self, 
        max_travel_time_minutes: int = 30,
        max_transfers: int = 2,
        departure_time: Optional[datetime] = None
    ) -> List[ReachableStation]:
        """
        Get list of stations reachable within specified time
        
        Args:
            max_travel_time_minutes: Maximum travel time in minutes
            max_transfers: Maximum number of transfers allowed
            departure_time: Departure time (default: now)
            
        Returns:
            List of reachable stations with travel information
        """
        if not self.is_available():
            logger.warning("VGN integration not available")
            return []
        
        # Note: departure_time parameter reserved for future use with actual VGN API
        # Currently using mock data for testing
        reachable_stations = []
        
        try:
            # TODO: Implement actual VGN API calls
            # This is a placeholder - actual implementation depends on VGN library API
            logger.info(
                f"Analyzing reachability from ({self.reference_lat}, {self.reference_lon}) "
                f"within {max_travel_time_minutes} minutes"
            )
            
            # For now, return mock data for testing
            # In production, this would query the VGN API
            reachable_stations = self._get_mock_reachable_stations(max_travel_time_minutes)
            
        except Exception as e:
            logger.error(f"Error getting reachable stations: {e}")
        
        return reachable_stations
    
    def get_reachable_municipalities(
        self,
        max_travel_time_minutes: int = 30
    ) -> List[Dict[str, any]]:
        """
        Get list of municipalities/regions reachable within specified time
        
        Args:
            max_travel_time_minutes: Maximum travel time in minutes
            
        Returns:
            List of municipalities with metadata (name, stations, population, etc.)
        """
        stations = self.get_reachable_stations(max_travel_time_minutes)
        
        # Group stations by municipality
        municipalities = {}
        for station in stations:
            muni = station.municipality
            if muni not in municipalities:
                municipalities[muni] = {
                    'name': muni,
                    'stations': [],
                    'min_travel_time': station.travel_time_minutes,
                    'station_count': 0
                }
            
            municipalities[muni]['stations'].append({
                'name': station.name,
                'id': station.id,
                'travel_time': station.travel_time_minutes,
                'transfers': station.transfers
            })
            municipalities[muni]['station_count'] += 1
            municipalities[muni]['min_travel_time'] = min(
                municipalities[muni]['min_travel_time'],
                station.travel_time_minutes
            )
        
        return list(municipalities.values())
    
    def suggest_event_sources(
        self,
        max_travel_time_minutes: int = 30
    ) -> List[RegionalSource]:
        """
        Suggest potential event sources based on reachable areas
        
        Analyzes reachable municipalities and suggests social media pages,
        local news sites, and cultural venues that might publish events.
        
        Args:
            max_travel_time_minutes: Maximum travel time in minutes
            
        Returns:
            List of suggested event sources with metadata
        """
        municipalities = self.get_reachable_municipalities(max_travel_time_minutes)
        suggestions = []
        
        # Load regional source database
        regional_db = self._load_regional_source_database()
        
        for muni in municipalities:
            muni_name = muni['name']
            
            # Find sources for this municipality
            if muni_name in regional_db:
                for source_data in regional_db[muni_name]:
                    source = RegionalSource(
                        name=source_data['name'],
                        type=source_data['type'],
                        url=source_data['url'],
                        municipality=muni_name,
                        category=source_data.get('category', 'community'),
                        description=source_data.get('description', ''),
                        distance_km=source_data.get('distance_km', 0),
                        travel_time_minutes=muni['min_travel_time']
                    )
                    suggestions.append(source)
        
        return suggestions
    
    def calculate_transit_time(
        self,
        destination_lat: float,
        destination_lon: float,
        departure_time: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Calculate transit time to a specific destination
        
        Args:
            destination_lat: Destination latitude
            destination_lon: Destination longitude
            departure_time: Departure time (default: now)
            
        Returns:
            Dict with transit information or None if not reachable
        """
        if not self.is_available():
            return None
        
        try:
            # TODO: Implement actual VGN API routing call
            # Placeholder implementation
            return {
                'duration_minutes': 15,
                'transfers': 1,
                'lines': ['S1'],
                'departure': departure_time or datetime.now(),
                'arrival': (departure_time or datetime.now()) + timedelta(minutes=15)
            }
        except Exception as e:
            logger.error(f"Error calculating transit time: {e}")
            return None
    
    def _get_mock_reachable_stations(self, max_travel_time: int) -> List[ReachableStation]:
        """
        Get mock reachable stations for testing (placeholder)
        
        In production, this would be replaced with actual VGN API calls
        """
        # Mock data for Hof region
        mock_stations = [
            ReachableStation(
                name="Hof Hauptbahnhof",
                id="vgn_hof_hbf",
                municipality="Hof",
                latitude=50.308053,
                longitude=11.9233,
                travel_time_minutes=0,
                transfers=0,
                line=None
            ),
            ReachableStation(
                name="Hof Neuhof",
                id="vgn_hof_neuhof",
                municipality="Hof",
                latitude=50.325,
                longitude=11.905,
                travel_time_minutes=10,
                transfers=0,
                line="Bus 1"
            ),
            ReachableStation(
                name="Rehau",
                id="vgn_rehau",
                municipality="Rehau",
                latitude=50.2489,
                longitude=12.0364,
                travel_time_minutes=25,
                transfers=0,
                line="S4"
            ),
            ReachableStation(
                name="Selb",
                id="vgn_selb",
                municipality="Selb",
                latitude=50.1705,
                longitude=12.1328,
                travel_time_minutes=35,
                transfers=1,
                line="S4"
            )
        ]
        
        # Filter by travel time
        return [s for s in mock_stations if s.travel_time_minutes <= max_travel_time]
    
    def _load_regional_source_database(self) -> Dict[str, List[Dict]]:
        """
        Load database of regional event sources
        
        Returns database mapping municipalities to event sources
        """
        db_path = self.base_path / 'assets' / 'json' / 'regional_sources.json'
        
        if db_path.exists():
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading regional sources database: {e}")
        
        # Return default database with known sources
        return self._get_default_regional_sources()
    
    def _get_default_regional_sources(self) -> Dict[str, List[Dict]]:
        """
        Get default regional sources database
        
        Returns mapping of municipalities to potential event sources
        """
        return {
            "Hof": [
                {
                    "name": "Hof Tourist Info",
                    "type": "html",
                    "url": "https://www.hof.de/hof/hof_deu/leben/veranstaltungen.html",
                    "category": "community",
                    "description": "Official city events",
                    "distance_km": 0.0
                },
                {
                    "name": "Frankenpost Hof",
                    "type": "html",
                    "url": "https://event.frankenpost.de/index.php?kat=&community=95028+Hof&range=50",
                    "category": "news",
                    "description": "Regional newspaper events",
                    "distance_km": 0.0
                }
            ],
            "Rehau": [
                {
                    "name": "Stadt Rehau",
                    "type": "html",
                    "url": "https://rehau.bayern/de/kultur/veranstaltungen",
                    "category": "community",
                    "description": "City of Rehau events",
                    "distance_km": 8.5
                }
            ],
            "Selb": [
                {
                    "name": "Stadt Selb",
                    "type": "html",
                    "url": "https://www.selb.de/freizeit-tourismus/veranstaltungen",
                    "category": "community",
                    "description": "City of Selb events",
                    "distance_km": 18.0
                }
            ],
            "Münchberg": [
                {
                    "name": "Stadt Münchberg",
                    "type": "html",
                    "url": "https://www.muenchberg.de/veranstaltungen",
                    "category": "community",
                    "description": "City of Münchberg events",
                    "distance_km": 15.0
                }
            ],
            "Schwarzenbach": [
                {
                    "name": "Stadt Schwarzenbach",
                    "type": "html",
                    "url": "https://www.schwarzenbach-saale.de/veranstaltungen",
                    "category": "community",
                    "description": "City of Schwarzenbach events",
                    "distance_km": 10.0
                }
            ]
        }
    
    def export_analysis_report(
        self,
        max_travel_time_minutes: int = 30,
        output_path: Optional[Path] = None
    ) -> Dict:
        """
        Export comprehensive reachability analysis report
        
        Args:
            max_travel_time_minutes: Maximum travel time to analyze
            output_path: Optional path to save JSON report
            
        Returns:
            Dict containing full analysis results
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'reference_location': {
                'latitude': self.reference_lat,
                'longitude': self.reference_lon,
                'name': self.vgn_config.get('reference_location', {}).get('name', 'Hof')
            },
            'max_travel_time_minutes': max_travel_time_minutes,
            'reachable_stations': [
                {
                    'name': s.name,
                    'id': s.id,
                    'municipality': s.municipality,
                    'coordinates': {'lat': s.latitude, 'lon': s.longitude},
                    'travel_time_minutes': s.travel_time_minutes,
                    'transfers': s.transfers,
                    'line': s.line
                }
                for s in self.get_reachable_stations(max_travel_time_minutes)
            ],
            'reachable_municipalities': self.get_reachable_municipalities(max_travel_time_minutes),
            'suggested_sources': [
                {
                    'name': s.name,
                    'type': s.type,
                    'url': s.url,
                    'municipality': s.municipality,
                    'category': s.category,
                    'description': s.description,
                    'distance_km': s.distance_km,
                    'travel_time_minutes': s.travel_time_minutes
                }
                for s in self.suggest_event_sources(max_travel_time_minutes)
            ]
        }
        
        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"Analysis report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving analysis report: {e}")
        
        return report
    
    def discover_cultural_venues(
        self,
        radius_km: float = 5.0,
        max_travel_time_minutes: int = 30,
        save_to_pending: bool = True
    ) -> List[CulturalVenue]:
        """
        Discover cultural venues near reachable VGN stations (hybrid approach)
        
        Uses OpenStreetMap Overpass API to auto-discover venues, then saves
        results to unified pending.json for manual review and enrichment.
        
        Args:
            radius_km: Search radius around each station in kilometers
            max_travel_time_minutes: Maximum travel time to stations
            save_to_pending: Save discovered venues to pending.json (default: True)
            
        Returns:
            List of cultural venues with deduplication
        """
        venues = []
        
        # Get reachable stations
        stations = self.get_reachable_stations(max_travel_time_minutes)
        
        if not stations:
            logger.warning("No reachable stations found")
            return []
        
        # Query OpenStreetMap for cultural venues near each station
        discovered_venues = []
        seen_venues = set()  # For deduplication
        
        for station in stations:
            try:
                station_venues = self._query_osm_venues(
                    station.latitude,
                    station.longitude,
                    radius_km
                )
                
                for venue_data in station_venues:
                    # Create unique key for deduplication
                    venue_key = (venue_data.get('name', ''), 
                                venue_data.get('lat'), 
                                venue_data.get('lon'))
                    
                    if venue_key not in seen_venues:
                        seen_venues.add(venue_key)
                        
                        # Calculate distance to station
                        distance_km = self._calculate_distance(
                            station.latitude, station.longitude,
                            venue_data.get('lat'), venue_data.get('lon')
                        )
                        
                        venue = CulturalVenue(
                            name=venue_data.get('name', 'Unknown'),
                            venue_type=venue_data.get('type', 'unknown'),
                            latitude=venue_data.get('lat'),
                            longitude=venue_data.get('lon'),
                            address=venue_data.get('address'),
                            website=venue_data.get('website'),
                            nearest_station=station.name,
                            distance_to_station_km=round(distance_km, 2),
                            travel_time_minutes=station.travel_time_minutes,
                            osm_id=venue_data.get('osm_id')
                        )
                        discovered_venues.append(venue)
                
                logger.info(f"Found {len(station_venues)} venues near {station.name}")
                
            except Exception as e:
                logger.error(f"Error querying venues near {station.name}: {e}")
                continue
        
        # Save discovered venues to pending.json for manual review
        if discovered_venues and save_to_pending:
            self._save_venues_to_pending(discovered_venues)
            logger.info(f"Saved {len(discovered_venues)} venues to pending.json")
        
        return discovered_venues
    
    def _query_osm_venues(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> List[Dict]:
        """
        Query OpenStreetMap Overpass API for cultural venues
        
        Args:
            lat: Latitude of search center
            lon: Longitude of search center
            radius_km: Search radius in kilometers
            
        Returns:
            List of venue dictionaries
        """
        # Convert km to meters for Overpass API
        radius_m = int(radius_km * 1000)
        
        # Overpass API query for cultural venues
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["tourism"="museum"](around:{radius_m},{lat},{lon});
          node["tourism"="gallery"](around:{radius_m},{lat},{lon});
          node["tourism"="attraction"](around:{radius_m},{lat},{lon});
          node["amenity"="theatre"](around:{radius_m},{lat},{lon});
          node["amenity"="cinema"](around:{radius_m},{lat},{lon});
          node["amenity"="arts_centre"](around:{radius_m},{lat},{lon});
          node["amenity"="community_centre"](around:{radius_m},{lat},{lon});
          way["tourism"="museum"](around:{radius_m},{lat},{lon});
          way["tourism"="gallery"](around:{radius_m},{lat},{lon});
          way["amenity"="theatre"](around:{radius_m},{lat},{lon});
          way["amenity"="cinema"](around:{radius_m},{lat},{lon});
          way["amenity"="arts_centre"](around:{radius_m},{lat},{lon});
        );
        out center;
        """
        
        try:
            import requests
            overpass_url = "https://overpass-api.de/api/interpreter"
            response = requests.post(
                overpass_url,
                data={'data': overpass_query},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            venues = []
            
            for element in data.get('elements', []):
                # Get coordinates (center for ways, direct for nodes)
                if element['type'] == 'way' and 'center' in element:
                    venue_lat = element['center']['lat']
                    venue_lon = element['center']['lon']
                elif element['type'] == 'node':
                    venue_lat = element.get('lat')
                    venue_lon = element.get('lon')
                else:
                    continue
                
                tags = element.get('tags', {})
                
                # Determine venue type
                venue_type = (
                    tags.get('tourism') or
                    tags.get('amenity') or
                    'unknown'
                )
                
                venues.append({
                    'name': tags.get('name', f'Unnamed {venue_type}'),
                    'type': venue_type,
                    'lat': venue_lat,
                    'lon': venue_lon,
                    'address': tags.get('addr:street', ''),
                    'website': tags.get('website', ''),
                    'osm_id': f"{element['type']}/{element['id']}"
                })
            
            return venues
            
        except Exception as e:
            logger.error(f"Error querying OpenStreetMap: {e}")
            return []
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in kilometers
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _save_venues_to_pending(self, venues: List[CulturalVenue]):
        """
        Save discovered venues to unified pending.json for manual review
        
        This integrates VGN venue discovery with the unified data structure,
        allowing venues to go through the same editorial workflow as events.
        """
        import uuid
        pending_path = self.base_path / 'assets' / 'json' / 'pending.json'
        
        # Load existing pending items
        pending_items = []
        if pending_path.exists():
            try:
                with open(pending_path, 'r', encoding='utf-8') as f:
                    pending_items = json.load(f)
            except Exception as e:
                logger.error(f"Error loading pending.json: {e}")
                pending_items = []
        
        # Add discovered venues to pending queue
        for venue in venues:
            venue_item = {
                'id': f"loc_{uuid.uuid4().hex[:16]}",
                'type': 'location',
                'name': venue.name,
                'category': venue.venue_type,
                'lat': venue.latitude,
                'lon': venue.longitude,
                'address': venue.address,
                'website': venue.website,
                'source': 'osm_vgn',
                'osm_id': venue.osm_id,
                'nearest_station': venue.nearest_station,
                'distance_to_station_km': venue.distance_to_station_km,
                'travel_time_minutes': venue.travel_time_minutes,
                'verified': False,
                'scraping_enabled': False,
                'notes': 'Auto-discovered via VGN transit + OpenStreetMap',
                'discovered_at': datetime.now().isoformat()
            }
            pending_items.append(venue_item)
        
        # Save back to pending.json
        pending_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pending_path, 'w', encoding='utf-8') as f:
            json.dump(pending_items, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Added {len(venues)} venues to pending.json for editorial review")
