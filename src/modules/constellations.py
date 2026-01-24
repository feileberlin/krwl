"""
Constellation Visualization Module - ASCII Art Night Sky

This module provides ASCII art visualizations of major constellations
visible from a given location, with information about their visibility
and position in the night sky.

Historical Context:
- Medieval bell ringers used star positions to tell time at night
- Orion setting before dawn in winter signaled approaching sunrise
- The position of Polaris (North Star) was used with nocturnal instruments
- Constellations helped navigate the night hours before mechanical clocks

API Usage (wttr.in style):
    curl localhost:8080/orion            # ASCII art of Orion
    curl localhost:8080/ursa-major       # Big Dipper / Great Bear
    curl localhost:8080/:list            # List all constellations
    curl localhost:8080/:help            # Help page

Python Usage:
    from src.modules.constellations import ConstellationViewer
    viewer = ConstellationViewer(lat=50.3167, lon=11.9167)
    print(viewer.get_constellation('orion'))

Start Server:
    python3 src/modules/constellations.py --serve --port 8081

References:
- https://en.wikipedia.org/wiki/Constellation
- https://en.wikipedia.org/wiki/Nocturnal_(instrument)
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import argparse


# Constants
DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi


# =============================================================================
# Navigation Stars - Used for Medieval Timekeeping
# =============================================================================
# Stars selected for brightness, visibility, and historical importance
# for navigation, timekeeping, and astronomical observation.
# 
# References:
# - https://de.wikipedia.org/wiki/Stern
# - https://en.wikipedia.org/wiki/List_of_stars_for_navigation

NAVIGATION_STARS = {
    'polaris': {
        'name': 'Polaris',
        'name_de': 'Polarstern',
        'designation': 'α Ursae Minoris',
        'constellation': 'Ursa Minor',
        'magnitude': 1.98,  # Apparent magnitude
        'spectral_type': 'F7Ib',  # Yellow-white supergiant
        'distance_ly': 433,  # Light years
        'color': 'yellow-white',
        'color_de': 'gelblich-weiß',
        'ra_hours': 2.53,
        'dec_degrees': 89.26,  # Almost exactly at North Celestial Pole
        'description': 'The North Star - appears stationary while other stars rotate around it',
        'description_de': 'Der Nordstern - erscheint stationär während andere Sterne um ihn rotieren',
        'medieval_use': 'Fixed point for nocturnal instruments; always shows true north',
        'medieval_use_de': 'Fixpunkt für Nokturnal-Instrumente; zeigt immer wahren Norden',
        'navigation': 'Latitude can be determined from Polaris altitude above horizon',
        'ascii': '''
           ★ Polaris
            (North Star)
             Always points north!
        '''
    },
    'sirius': {
        'name': 'Sirius',
        'name_de': 'Sirius (Hundsstern)',
        'designation': 'α Canis Majoris',
        'constellation': 'Canis Major',
        'magnitude': -1.46,  # Brightest star in the night sky!
        'spectral_type': 'A1V',  # White main sequence
        'distance_ly': 8.6,  # One of the closest stars
        'color': 'blue-white',
        'color_de': 'blau-weiß',
        'ra_hours': 6.75,
        'dec_degrees': -16.72,
        'description': 'Brightest star in the night sky; the "Dog Star"',
        'description_de': 'Hellster Stern am Nachthimmel; der "Hundsstern"',
        'medieval_use': 'Followed Orion; its rising signaled the flooding of the Nile (Egypt)',
        'medieval_use_de': 'Folgte Orion; sein Aufgang signalisierte die Nilflut (Ägypten)',
        'navigation': 'Important winter navigation star; visible worldwide',
        'ascii': '''
           ★★★ Sirius
          (Brightest star!)
          Mag: -1.46
        '''
    },
    'betelgeuse': {
        'name': 'Betelgeuse',
        'name_de': 'Beteigeuze',
        'designation': 'α Orionis',
        'constellation': 'Orion',
        'magnitude': 0.42,  # Variable: 0.0 to 1.6
        'spectral_type': 'M1-2Ia-ab',  # Red supergiant
        'distance_ly': 700,
        'color': 'red',
        'color_de': 'rot',
        'ra_hours': 5.92,
        'dec_degrees': 7.41,
        'description': 'Red supergiant marking Orion\'s shoulder; one of the largest known stars',
        'description_de': 'Roter Überriese an Orions Schulter; einer der größten bekannten Sterne',
        'medieval_use': 'Distinctive red color made it easy to identify Orion at night',
        'medieval_use_de': 'Auffällige rote Farbe machte Orion leicht identifizierbar',
        'navigation': 'Winter navigation; marks the hunter\'s shoulder',
        'ascii': '''
           ★ Betelgeuse
          (Red supergiant)
           Variable brightness
        '''
    },
    'rigel': {
        'name': 'Rigel',
        'name_de': 'Rigel',
        'designation': 'β Orionis',
        'constellation': 'Orion',
        'magnitude': 0.13,
        'spectral_type': 'B8Ia',  # Blue supergiant
        'distance_ly': 860,
        'color': 'blue-white',
        'color_de': 'blau-weiß',
        'ra_hours': 5.24,
        'dec_degrees': -8.20,
        'description': 'Blue supergiant at Orion\'s foot; 7th brightest star',
        'description_de': 'Blauer Überriese an Orions Fuß; 7. hellster Stern',
        'medieval_use': 'Contrasts with red Betelgeuse; helps identify Orion',
        'medieval_use_de': 'Kontrast zum roten Beteigeuze; hilft Orion zu identifizieren',
        'navigation': 'Winter navigation star',
        'ascii': '''
           ★ Rigel
          (Blue supergiant)
           Orion's foot
        '''
    },
    'vega': {
        'name': 'Vega',
        'name_de': 'Wega',
        'designation': 'α Lyrae',
        'constellation': 'Lyra',
        'magnitude': 0.03,
        'spectral_type': 'A0V',  # White main sequence
        'distance_ly': 25,
        'color': 'blue-white',
        'color_de': 'blau-weiß',
        'ra_hours': 18.62,
        'dec_degrees': 38.78,
        'description': 'Part of the Summer Triangle; 5th brightest star',
        'description_de': 'Teil des Sommerdreiecks; 5. hellster Stern',
        'medieval_use': 'Bright summer star; was the North Star ~12,000 years ago',
        'medieval_use_de': 'Heller Sommerstern; war vor ~12.000 Jahren der Nordstern',
        'navigation': 'Summer Triangle anchor star',
        'ascii': '''
           ★ Vega
          (Summer Triangle)
           Future North Star
        '''
    },
    'capella': {
        'name': 'Capella',
        'name_de': 'Kapella',
        'designation': 'α Aurigae',
        'constellation': 'Auriga',
        'magnitude': 0.08,
        'spectral_type': 'G3III + G0III',  # Yellow giant binary
        'distance_ly': 43,
        'color': 'yellow',
        'color_de': 'gelb',
        'ra_hours': 5.28,
        'dec_degrees': 45.99,
        'description': 'The "Little She-Goat"; 6th brightest star, actually a quadruple system',
        'description_de': 'Die "Kleine Ziege"; 6. hellster Stern, tatsächlich ein Vierfachsystem',
        'medieval_use': 'Circumpolar from mid-northern latitudes; visible year-round',
        'medieval_use_de': 'Zirkumpolar in mittleren nördlichen Breiten; ganzjährig sichtbar',
        'navigation': 'Year-round northern hemisphere star',
        'ascii': '''
           ★ Capella
          (The Little Goat)
           Quadruple star!
        '''
    },
    'arcturus': {
        'name': 'Arcturus',
        'name_de': 'Arktur',
        'designation': 'α Boötis',
        'constellation': 'Boötes',
        'magnitude': -0.05,
        'spectral_type': 'K1.5III',  # Orange giant
        'distance_ly': 37,
        'color': 'orange',
        'color_de': 'orange',
        'ra_hours': 14.26,
        'dec_degrees': 19.18,
        'description': '4th brightest star; "Follow the arc to Arcturus"',
        'description_de': '4. hellster Stern; "Folge dem Bogen zu Arktur"',
        'medieval_use': 'Spring star; follow Big Dipper handle arc to find it',
        'medieval_use_de': 'Frühlingsstern; folge dem Bogen der Großen-Wagen-Deichsel',
        'navigation': 'Spring navigation; found via Big Dipper',
        'ascii': '''
           ★ Arcturus
          "Arc to Arcturus"
           Orange giant
        '''
    },
    'aldebaran': {
        'name': 'Aldebaran',
        'name_de': 'Aldebaran',
        'designation': 'α Tauri',
        'constellation': 'Taurus',
        'magnitude': 0.85,
        'spectral_type': 'K5III',  # Orange giant
        'distance_ly': 65,
        'color': 'orange-red',
        'color_de': 'orange-rot',
        'ra_hours': 4.60,
        'dec_degrees': 16.51,
        'description': 'The "Follower" (of the Pleiades); the Bull\'s eye',
        'description_de': 'Der "Folger" (der Plejaden); das Auge des Stiers',
        'medieval_use': 'Rises after the Pleiades; marks late autumn/winter',
        'medieval_use_de': 'Geht nach den Plejaden auf; markiert Spätherbst/Winter',
        'navigation': 'Winter navigation star; easy to find near Pleiades',
        'ascii': '''
           ★ Aldebaran
          (Bull's Eye)
           Follows Pleiades
        '''
    },
    'antares': {
        'name': 'Antares',
        'name_de': 'Antares',
        'designation': 'α Scorpii',
        'constellation': 'Scorpius',
        'magnitude': 1.06,
        'spectral_type': 'M1.5Iab',  # Red supergiant
        'distance_ly': 550,
        'color': 'red',
        'color_de': 'rot',
        'ra_hours': 16.49,
        'dec_degrees': -26.43,
        'description': '"Rival of Mars" - red color rivals the planet; heart of the Scorpion',
        'description_de': '"Rivale des Mars" - rote Farbe rivalisiert mit dem Planeten; Herz des Skorpions',
        'medieval_use': 'Summer star; low in southern sky from Europe',
        'medieval_use_de': 'Sommerstern; tief am südlichen Himmel von Europa',
        'navigation': 'Summer navigation; marks the Scorpion\'s heart',
        'ascii': '''
           ★ Antares
          "Rival of Mars"
           Red supergiant
        '''
    },
    'deneb': {
        'name': 'Deneb',
        'name_de': 'Deneb',
        'designation': 'α Cygni',
        'constellation': 'Cygnus',
        'magnitude': 1.25,
        'spectral_type': 'A2Ia',  # White supergiant
        'distance_ly': 2600,  # Very distant!
        'color': 'blue-white',
        'color_de': 'blau-weiß',
        'ra_hours': 20.69,
        'dec_degrees': 45.28,
        'description': 'Tail of the Swan; part of Summer Triangle; one of most luminous known stars',
        'description_de': 'Schwanz des Schwans; Teil des Sommerdreiecks; einer der leuchtkräftigsten bekannten Sterne',
        'medieval_use': 'Summer Triangle star; marks the Northern Cross',
        'medieval_use_de': 'Sommerdreieck-Stern; markiert das Nördliche Kreuz',
        'navigation': 'Summer navigation; flies along the Milky Way',
        'ascii': '''
           ★ Deneb
          (Swan's Tail)
           2600 light-years!
        '''
    },
    'altair': {
        'name': 'Altair',
        'name_de': 'Atair',
        'designation': 'α Aquilae',
        'constellation': 'Aquila',
        'magnitude': 0.77,
        'spectral_type': 'A7V',  # White main sequence
        'distance_ly': 17,  # Close neighbor
        'color': 'white',
        'color_de': 'weiß',
        'ra_hours': 19.85,
        'dec_degrees': 8.87,
        'description': 'The Eagle; part of Summer Triangle; very fast rotation',
        'description_de': 'Der Adler; Teil des Sommerdreiecks; sehr schnelle Rotation',
        'medieval_use': 'Summer Triangle star; bright summer evening marker',
        'medieval_use_de': 'Sommerdreieck-Stern; heller Sommerabend-Markierer',
        'navigation': 'Summer navigation star',
        'ascii': '''
           ★ Altair
          (The Eagle)
           Only 17 ly away
        '''
    },
    'regulus': {
        'name': 'Regulus',
        'name_de': 'Regulus',
        'designation': 'α Leonis',
        'constellation': 'Leo',
        'magnitude': 1.40,
        'spectral_type': 'B8IVn',  # Blue-white subgiant
        'distance_ly': 79,
        'color': 'blue-white',
        'color_de': 'blau-weiß',
        'ra_hours': 10.14,
        'dec_degrees': 11.97,
        'description': 'The "Little King" at the Lion\'s heart; on the ecliptic',
        'description_de': 'Der "Kleine König" am Herzen des Löwen; auf der Ekliptik',
        'medieval_use': 'Spring star; one of four Royal Stars of ancient Persia',
        'medieval_use_de': 'Frühlingsstern; einer der vier Königssterne des alten Persien',
        'navigation': 'Spring navigation; lies on the ecliptic (planets pass by)',
        'ascii': '''
           ★ Regulus
          (The Little King)
           Royal Star
        '''
    }
}


class ConstellationViewer:
    """
    Viewer for constellation ASCII art and visibility information.
    
    Provides information about when and where constellations are visible
    from a given location, with ASCII art representations.
    """
    
    # Major constellations with their data
    CONSTELLATIONS = {
        'orion': {
            'name': 'Orion',
            'name_de': 'Orion (Der Jäger)',
            'latin': 'Orion',
            'ra_hours': 5.5,  # Right Ascension (center)
            'dec_degrees': 0,  # Declination (center, on celestial equator)
            'best_months': [12, 1, 2],  # December, January, February
            'magnitude': 0.5,  # Brightest star (Betelgeuse/Rigel)
            'description': 'The Hunter - One of the most recognizable constellations',
            'description_de': 'Der Jäger - Eine der bekanntesten Sternbilder',
            'medieval_use': 'Orion setting in the west before dawn signaled approaching sunrise in winter',
            'medieval_use_de': 'Orion im Westen untergehend vor der Morgendämmerung zeigte den nahenden Sonnenaufgang im Winter an',
            'ascii_art': r'''
                              .  Betelgeuse
                             /|\    *  (red supergiant)
                            / | \
                           /  |  \
                          /   |   \
                   Bellatrix    |    Meissa
                      *    \   |   /    *
                            \  |  /
                             \ | /
                    .---------***---------.
                   /    Orion's Belt       \
                  /   Alnitak Alnilam Mintaka  \
                 /           |                  \
                /            |                   \
               /             |                    \
              *              |                     *
           Saiph      Orion's Sword             Rigel
                          *  (blue supergiant)
                       M42 Nebula
                          ~~~
'''
        },
        'ursa-major': {
            'name': 'Ursa Major',
            'name_de': 'Großer Bär / Großer Wagen',
            'latin': 'Ursa Major',
            'ra_hours': 11.0,
            'dec_degrees': 55,
            'best_months': [3, 4, 5],  # March, April, May
            'magnitude': 1.8,
            'description': 'The Great Bear - Contains the Big Dipper asterism',
            'description_de': 'Der Große Bär - Enthält den Großen Wagen',
            'medieval_use': 'The two pointer stars show the way to Polaris (North Star)',
            'medieval_use_de': 'Die zwei Zeigersterne weisen den Weg zum Polarstern',
            'ascii_art': r'''
                    THE BIG DIPPER (Part of Ursa Major)
                    
                         *  Dubhe
                        / \
                       /   \  Merak  *
                      /     \       /
                     /       \     /
                    /         \   /
                   *-----------*-*
                 Megrez      Phecda
                   |
                   |
                   *  Alioth
                   |
                   |
                   *  Mizar (+ Alcor)
                    \
                     \
                      *  Alkaid
                      
        "Follow the arc to Arcturus, speed on to Spica"
'''
        },
        'ursa-minor': {
            'name': 'Ursa Minor',
            'name_de': 'Kleiner Bär / Kleiner Wagen',
            'latin': 'Ursa Minor',
            'ra_hours': 15.0,
            'dec_degrees': 75,
            'best_months': [6, 7, 8],  # Circumpolar, but best summer
            'magnitude': 2.0,
            'description': 'The Little Bear - Contains Polaris (North Star)',
            'description_de': 'Der Kleine Bär - Enthält den Polarstern',
            'medieval_use': 'Polaris was used with nocturnal instruments to tell time at night',
            'medieval_use_de': 'Der Polarstern wurde mit Nokturnal-Instrumenten zur Zeitbestimmung in der Nacht verwendet',
            'ascii_art': r'''
                    THE LITTLE DIPPER / URSA MINOR

                              *  POLARIS (North Star)
                             /    ← Always points north!
                            /
                           *  Yildun
                          /
                         /
                        *  Epsilon
                       / \
                      /   \
                     /     \
                    *-------*-------*
                  Zeta    Eta    Pherkad
                             \
                              \
                               *  Kochab
                               
        Medieval bell ringers used Polaris to tell time at night!
'''
        },
        'cassiopeia': {
            'name': 'Cassiopeia',
            'name_de': 'Kassiopeia',
            'latin': 'Cassiopeia',
            'ra_hours': 1.0,
            'dec_degrees': 60,
            'best_months': [10, 11, 12],
            'magnitude': 2.2,
            'description': 'The Queen - W-shaped constellation near Polaris',
            'description_de': 'Die Königin - W-förmiges Sternbild nahe dem Polarstern',
            'medieval_use': 'Opposite the Big Dipper around Polaris, helps find north',
            'medieval_use_de': 'Gegenüber dem Großen Wagen um den Polarstern, hilft bei der Nordfindung',
            'ascii_art': r'''
                    CASSIOPEIA - The Queen's Chair

                          *  Caph
                         / \
                        /   \
                       /     *  Schedar
                      /     /
                     *     /
                 Ruchbah  /
                      \  /
                       \/
                        *  Gamma Cas
                       /
                      /
                     *  Segin
                     
         The distinctive "W" shape rotates around Polaris
'''
        },
        'leo': {
            'name': 'Leo',
            'name_de': 'Löwe',
            'latin': 'Leo',
            'ra_hours': 10.5,
            'dec_degrees': 15,
            'best_months': [3, 4, 5],
            'magnitude': 1.4,
            'description': 'The Lion - Spring constellation with bright Regulus',
            'description_de': 'Der Löwe - Frühlingssternbild mit dem hellen Regulus',
            'medieval_use': 'When Leo rises in the evening, spring is arriving',
            'medieval_use_de': 'Wenn der Löwe abends aufgeht, naht der Frühling',
            'ascii_art': r'''
                    LEO - The Lion

                           * Algieba
                          /|
                         / |
                        /  *  Adhafera
                       /  /
                      /  /
                     *--*  The Sickle (Lion's Head)
                    /  Rasalas
                   /
               Regulus *-----------------------*  Denebola
                  (The King's Star)           (Lion's Tail)
                         \                   /
                          \                 /
                           \               /
                            *-------------*
                          Zosma      Chertan
'''
        },
        'scorpius': {
            'name': 'Scorpius',
            'name_de': 'Skorpion',
            'latin': 'Scorpius',
            'ra_hours': 16.5,
            'dec_degrees': -26,
            'best_months': [6, 7, 8],
            'magnitude': 1.0,
            'description': 'The Scorpion - Summer constellation with red Antares',
            'description_de': 'Der Skorpion - Sommersternbild mit dem roten Antares',
            'medieval_use': 'Low in southern sky during summer nights',
            'medieval_use_de': 'Tief am südlichen Himmel in Sommernächten',
            'ascii_art': r'''
                    SCORPIUS - The Scorpion

                                * Dschubba
                               / \
                              /   \
                             /     \
                    *-------*   ANTARES   *
                   Graffias  (Red Supergiant)  \
                                              \
                                               \
                                                *  Shaula
                                               /|
                                              / |
                                             /  * Lesath
                                            /  (The Stinger)
                                           *
                                        
        "Rival of Mars" - Antares' red color rivals the planet
'''
        },
        'cygnus': {
            'name': 'Cygnus',
            'name_de': 'Schwan',
            'latin': 'Cygnus',
            'ra_hours': 20.5,
            'dec_degrees': 42,
            'best_months': [7, 8, 9],
            'magnitude': 1.25,
            'description': 'The Swan - Northern Cross, flies along the Milky Way',
            'description_de': 'Der Schwan - Das Nördliche Kreuz, fliegt entlang der Milchstraße',
            'medieval_use': 'The Northern Cross was used to orient in summer nights',
            'medieval_use_de': 'Das Nördliche Kreuz wurde zur Orientierung in Sommernächten verwendet',
            'ascii_art': r'''
                    CYGNUS - The Swan / Northern Cross

                              * Deneb (tail)
                              |  (One of the brightest stars)
                              |
                              |
                    *---------*---------*
                 Gienah      |       Rukh
                   (wing)    |      (wing)
                              |
                              |
                              *  Sadr (heart)
                              |
                              |
                              |
                              * Albireo (head/beak)
                               (Beautiful double star!)
                               
        Part of the "Summer Triangle" with Vega and Altair
'''
        },
        'pleiades': {
            'name': 'Pleiades',
            'name_de': 'Plejaden / Siebengestirn',
            'latin': 'Pleiades (M45)',
            'ra_hours': 3.75,
            'dec_degrees': 24,
            'best_months': [11, 12, 1],
            'magnitude': 1.6,
            'description': 'The Seven Sisters - Famous open star cluster',
            'description_de': 'Das Siebengestirn - Berühmter offener Sternhaufen',
            'medieval_use': 'Pleiades rising in evening marked late autumn harvest time',
            'medieval_use_de': 'Das Aufgehen der Plejaden am Abend markierte die späte Herbsternte',
            'ascii_art': r'''
                    PLEIADES - The Seven Sisters (M45)

                                  * Alcyone
                                 /|\
                                / | \
                               /  |  \
                              *   *   *
                           Atlas |  Merope
                                 |
                              Electra
                             /       \
                            *         *
                        Maia       Taygeta
                           \       /
                            \     /
                             \   /
                              \ /
                               * Celaeno
                               |
                               * Sterope (Asterope)

        "Seven Sisters" - Actually 800+ stars, 440 light-years away
        Can you see 6 or 7 with naked eye? (test of eyesight!)
'''
        }
    }
    
    def __init__(self, lat: float, lon: float, tz_offset_hours: float = 1):
        """
        Initialize the constellation viewer.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            tz_offset_hours: Timezone offset from UTC
        """
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
        
        self.lat = lat
        self.lon = lon
        self.tz_offset = tz_offset_hours
    
    def get_constellation(self, name: str, dt: datetime = None) -> Dict[str, Any]:
        """
        Get information about a constellation.
        
        Args:
            name: Constellation name (e.g., 'orion', 'ursa-major')
            dt: Datetime for visibility calculation (defaults to now)
            
        Returns:
            Dict with constellation info, visibility, and ASCII art
        """
        name_lower = name.lower().replace(' ', '-').replace('_', '-')
        
        if name_lower not in self.CONSTELLATIONS:
            return {'error': f"Unknown constellation: {name}. Use :list to see available constellations."}
        
        const = self.CONSTELLATIONS[name_lower]
        
        if dt is None:
            dt = datetime.now()
        
        # Calculate visibility
        visibility = self._calculate_visibility(const, dt)
        
        return {
            'name': const['name'],
            'name_de': const['name_de'],
            'latin': const['latin'],
            'description': const['description'],
            'description_de': const['description_de'],
            'medieval_use': const['medieval_use'],
            'medieval_use_de': const['medieval_use_de'],
            'best_months': const['best_months'],
            'magnitude': const['magnitude'],
            'ascii_art': const['ascii_art'],
            'visibility': visibility,
            'location': {'lat': self.lat, 'lon': self.lon},
            'timestamp': dt.isoformat()
        }
    
    def _calculate_visibility(self, const: dict, dt: datetime) -> Dict[str, Any]:
        """
        Calculate approximate visibility of a constellation.
        
        This is a simplified calculation - real astronomical software
        would use more precise algorithms.
        """
        month = dt.month
        hour = dt.hour
        
        # Check if current month is in best viewing months
        is_best_month = month in const['best_months']
        
        # Simple visibility estimate based on declination and latitude
        dec = const['dec_degrees']
        
        # Circumpolar check (always above horizon)
        is_circumpolar = (self.lat > 0 and dec > (90 - self.lat)) or \
                         (self.lat < 0 and dec < (-90 - self.lat))
        
        # Never visible check
        never_visible = (self.lat > 0 and dec < (self.lat - 90)) or \
                        (self.lat < 0 and dec > (90 + self.lat))
        
        # Estimate current position (very simplified)
        # Local Sidereal Time approximation
        day_of_year = dt.timetuple().tm_yday
        lst_hours = ((day_of_year - 80) * 0.0657 + hour + self.lon / 15) % 24
        
        # Hour angle
        ha = lst_hours - const['ra_hours']
        if ha < -12:
            ha += 24
        if ha > 12:
            ha -= 24
        
        # Estimate altitude (very simplified)
        ha_rad = ha * 15 * DEG_TO_RAD
        dec_rad = dec * DEG_TO_RAD
        lat_rad = self.lat * DEG_TO_RAD
        
        sin_alt = math.sin(lat_rad) * math.sin(dec_rad) + \
                  math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
        altitude = math.asin(max(-1, min(1, sin_alt))) * RAD_TO_DEG
        
        # Determine direction
        if ha < -6:
            direction = 'rising in the east'
            direction_de = 'steigt im Osten auf'
        elif ha < -2:
            direction = 'in the eastern sky'
            direction_de = 'im östlichen Himmel'
        elif ha < 2:
            direction = 'near the meridian (highest point)'
            direction_de = 'nahe dem Meridian (höchster Punkt)'
        elif ha < 6:
            direction = 'in the western sky'
            direction_de = 'im westlichen Himmel'
        else:
            direction = 'setting in the west'
            direction_de = 'geht im Westen unter'
        
        # Visibility status
        if never_visible:
            status = 'never visible from this latitude'
            status_de = 'von diesem Breitengrad nie sichtbar'
            visible_now = False
        elif is_circumpolar:
            status = 'circumpolar (always above horizon)'
            status_de = 'zirkumpolar (immer über dem Horizont)'
            visible_now = altitude > 10
        elif altitude > 10:
            status = 'visible' if is_best_month else 'visible (not optimal season)'
            status_de = 'sichtbar' if is_best_month else 'sichtbar (nicht optimale Jahreszeit)'
            visible_now = True
        elif altitude > 0:
            status = 'low on horizon'
            status_de = 'tief am Horizont'
            visible_now = True
        else:
            status = 'below horizon'
            status_de = 'unter dem Horizont'
            visible_now = False
        
        return {
            'visible_now': visible_now,
            'altitude_degrees': round(altitude, 1),
            'direction': direction,
            'direction_de': direction_de,
            'status': status,
            'status_de': status_de,
            'is_circumpolar': is_circumpolar,
            'is_best_season': is_best_month,
            'best_months': [self._month_name(m) for m in const['best_months']]
        }
    
    def _month_name(self, month: int) -> str:
        """Get month name from number."""
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        return months[month] if 1 <= month <= 12 else ''
    
    def list_constellations(self) -> List[Dict[str, str]]:
        """List all available constellations."""
        result = []
        for key, const in self.CONSTELLATIONS.items():
            result.append({
                'id': key,
                'name': const['name'],
                'name_de': const['name_de'],
                'description': const['description'][:60] + '...'
            })
        return result
    
    def get_star(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a navigation star.
        
        Args:
            name: Star name (e.g., 'polaris', 'sirius', 'betelgeuse')
            
        Returns:
            Dict with star information
        """
        name_lower = name.lower().replace(' ', '-').replace('_', '-')
        
        if name_lower not in NAVIGATION_STARS:
            return {'error': f"Unknown star: {name}. Use :stars to see available stars."}
        
        star = NAVIGATION_STARS[name_lower]
        return {
            'name': star['name'],
            'name_de': star['name_de'],
            'designation': star['designation'],
            'constellation': star['constellation'],
            'magnitude': star['magnitude'],
            'spectral_type': star['spectral_type'],
            'distance_ly': star['distance_ly'],
            'color': star['color'],
            'color_de': star['color_de'],
            'description': star['description'],
            'description_de': star['description_de'],
            'medieval_use': star['medieval_use'],
            'medieval_use_de': star['medieval_use_de'],
            'navigation': star['navigation'],
            'ascii': star['ascii'],
            'location': {'lat': self.lat, 'lon': self.lon}
        }
    
    def list_stars(self) -> List[Dict[str, Any]]:
        """List all navigation stars with key information."""
        result = []
        for key, star in NAVIGATION_STARS.items():
            result.append({
                'id': key,
                'name': star['name'],
                'name_de': star['name_de'],
                'constellation': star['constellation'],
                'magnitude': star['magnitude'],
                'color': star['color'],
                'description': star['description'][:50] + '...'
            })
        # Sort by magnitude (brightest first)
        result.sort(key=lambda x: x['magnitude'])
        return result
    
    def get_stars_table(self) -> str:
        """Get formatted table of navigation stars."""
        stars = self.list_stars()
        
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║              ⭐ NAVIGATION STARS - Medieval Timekeeping ⭐                    ║")
        lines.append("╠═══════════════════════════════════════════════════════════════════════════════╣")
        lines.append("║                                                                               ║")
        lines.append("║  These stars were used by medieval navigators and bell-ringers to tell       ║")
        lines.append("║  time at night before the invention of mechanical clocks.                    ║")
        lines.append("║                                                                               ║")
        lines.append("╠═══════════════════════════════════════════════════════════════════════════════╣")
        lines.append("║  Star         │ Mag   │ Color       │ Constellation │ Medieval Use           ║")
        lines.append("╠═══════════════════════════════════════════════════════════════════════════════╣")
        
        for star in stars:
            full_star = NAVIGATION_STARS[star['id']]
            name = star['name'][:12].ljust(12)
            mag = f"{star['magnitude']:+.2f}".ljust(5)
            color = star['color'][:11].ljust(11)
            const = full_star['constellation'][:13].ljust(13)
            use = full_star['medieval_use'][:22].ljust(22)
            lines.append(f"║  {name} │ {mag} │ {color} │ {const} │ {use} ║")
        
        lines.append("╠═══════════════════════════════════════════════════════════════════════════════╣")
        lines.append("║                                                                               ║")
        lines.append("║  💡 MAGNITUDE: Lower = brighter. Sirius (-1.46) is the brightest!            ║")
        lines.append("║  🔭 SPECTRAL TYPES: O B A F G K M (Oh Be A Fine Guy/Girl Kiss Me)            ║")
        lines.append("║                                                                               ║")
        lines.append("╠═══════════════════════════════════════════════════════════════════════════════╣")
        lines.append("║  Usage:  curl localhost:PORT/star/polaris                                    ║")
        lines.append("║          curl localhost:PORT/star/sirius                                     ║")
        lines.append("║          curl localhost:PORT/:stars?format=j   (JSON)                        ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        
        return '\n'.join(lines)


# =============================================================================
# HTTP API Server (wttr.in style)
# =============================================================================

class ConstellationHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for constellation API."""
    
    viewer = None  # Set by server
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path.strip('/')
        query = parse_qs(parsed.query)
        
        # Get format parameter
        fmt = query.get('format', [''])[0].lower()
        
        # Route request
        if path == '' or path == 'orion':
            self._send_constellation('orion', fmt)
        elif path == ':help':
            self._send_help()
        elif path == ':list':
            self._send_list(fmt)
        elif path == ':about':
            self._send_about()
        elif path == ':stars':
            self._send_stars(fmt)
        elif path.startswith('star/'):
            star_name = path[5:]  # Remove 'star/' prefix
            self._send_star(star_name, fmt)
        elif path in ConstellationViewer.CONSTELLATIONS:
            self._send_constellation(path, fmt)
        elif path in NAVIGATION_STARS:
            self._send_star(path, fmt)
        else:
            # Try to match constellation name
            path_normalized = path.lower().replace(' ', '-').replace('_', '-')
            if path_normalized in ConstellationViewer.CONSTELLATIONS:
                self._send_constellation(path_normalized, fmt)
            elif path_normalized in NAVIGATION_STARS:
                self._send_star(path_normalized, fmt)
            else:
                self._send_error(404, f"Unknown: {path}\n\nUse :list for constellations, :stars for stars.")
    
    def _send_constellation(self, name: str, fmt: str):
        """Send constellation data."""
        result = self.viewer.get_constellation(name)
        
        if 'error' in result:
            self._send_error(404, result['error'])
            return
        
        if fmt in ['j', 'json']:
            self._send_json(result)
        else:
            self._send_plain_text(result)
    
    def _send_plain_text(self, result: dict):
        """Send as plain text ASCII art."""
        vis = result['visibility']
        
        # Visibility icon
        if vis['visible_now']:
            vis_icon = "✅"
            vis_text = f"Visible ({vis['direction']})"
        else:
            vis_icon = "❌"
            vis_text = vis['status']
        
        output = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⭐ {result['name']:<71} ║
║     {result['name_de']:<71} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
{result['ascii_art']}
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📍 Visibility from {result['location']['lat']:.2f}°N, {result['location']['lon']:.2f}°E                                    ║
║                                                                               ║
║  {vis_icon} {vis_text:<72} ║
║  📐 Altitude: {vis['altitude_degrees']:>5.1f}°   {'(circumpolar)' if vis['is_circumpolar'] else '              ':<30}      ║
║  📅 Best viewing: {', '.join(vis['best_months'][:3]):<54} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🏛️ Medieval Use:                                                             ║
║     {result['medieval_use'][:70]:<70} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 {result['description']:<72} ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        self._send_response(200, output, 'text/plain; charset=utf-8')
    
    def _send_json(self, data: dict):
        """Send JSON response."""
        self._send_response(200, json.dumps(data, indent=2, ensure_ascii=False), 'application/json')
    
    def _send_star(self, name: str, fmt: str):
        """Send star data."""
        result = self.viewer.get_star(name)
        
        if 'error' in result:
            self._send_error(404, result['error'])
            return
        
        if fmt in ['j', 'json']:
            self._send_json(result)
        else:
            self._send_star_plain_text(result)
    
    def _send_star_plain_text(self, star: dict):
        """Send star as plain text."""
        # Magnitude display (negative is brighter)
        mag = star['magnitude']
        if mag < 0:
            brightness = "★★★ VERY BRIGHT"
        elif mag < 1:
            brightness = "★★ Bright"
        else:
            brightness = "★ Visible"
        
        output = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ★ {star['name']:<73} ║
║    {star['name_de']:<73} ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  📍 Constellation:  {star['constellation']:<55} ║
║  🔬 Designation:    {star['designation']:<55} ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  PHYSICAL PROPERTIES                                                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  🌟 Magnitude:      {mag:+.2f}  ({brightness:<32})        ║
║  🎨 Color:          {star['color']:<55} ║
║  🔭 Spectral Type:  {star['spectral_type']:<55} ║
║  📏 Distance:       {star['distance_ly']} light-years{'':<44}║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🏛️ MEDIEVAL TIMEKEEPING USE                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  {star['medieval_use'][:75]:<75}║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🧭 NAVIGATION                                                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  {star['navigation']:<75}║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 {star['description']:<72} ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        self._send_response(200, output, 'text/plain; charset=utf-8')
    
    def _send_stars(self, fmt: str):
        """Send list of navigation stars."""
        stars = self.viewer.list_stars()
        
        if fmt in ['j', 'json']:
            self._send_json(stars)
        else:
            output = self.viewer.get_stars_table()
            self._send_response(200, output, 'text/plain; charset=utf-8')
    
    def _send_list(self, fmt: str):
        """Send list of constellations."""
        constellations = self.viewer.list_constellations()
        
        if fmt in ['j', 'json']:
            self._send_json(constellations)
        else:
            output = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⭐ Available Constellations ⭐                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
"""
            for const in constellations:
                output += f"║  • /{const['id']:<20} {const['name']:<15} {const['name_de']:<30}║\n"
            
            output += """║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Usage:                                                                       ║
║    curl localhost:PORT/orion           # Show Orion                           ║
║    curl localhost:PORT/ursa-major      # Show Ursa Major (Big Dipper)         ║
║    curl localhost:PORT/pleiades        # Show the Pleiades                    ║
║    curl localhost:PORT/:help           # Help page                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
            self._send_response(200, output, 'text/plain; charset=utf-8')
    
    def _send_help(self):
        """Send help page."""
        help_text = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⭐ Constellation & Star Viewer - Help ⭐                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  USAGE:                                                                       ║
║                                                                               ║
║    curl localhost:PORT/CONSTELLATION   # View constellation ASCII art        ║
║    curl localhost:PORT/:list           # List all constellations              ║
║    curl localhost:PORT/:stars          # List all navigation stars            ║
║    curl localhost:PORT/star/NAME       # View individual star info            ║
║    curl localhost:PORT/:help           # This help page                       ║
║    curl localhost:PORT/:about          # About this tool                      ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  CONSTELLATIONS:                                                              ║
║                                                                               ║
║    /orion              Orion the Hunter (winter)                              ║
║    /ursa-major         Big Dipper / Great Bear                                ║
║    /ursa-minor         Little Dipper / Polaris                                ║
║    /cassiopeia         The Queen (W-shape)                                    ║
║    /leo                The Lion (spring)                                      ║
║    /scorpius           The Scorpion (summer)                                  ║
║    /cygnus             The Swan / Northern Cross                              ║
║    /pleiades           Seven Sisters star cluster                             ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ★ NAVIGATION STARS (for Medieval Timekeeping):                               ║
║                                                                               ║
║    /star/polaris       North Star - fixed point for finding north             ║
║    /star/sirius        Brightest star (-1.46 mag), "Dog Star"                 ║
║    /star/betelgeuse    Red supergiant in Orion's shoulder                     ║
║    /star/vega          Summer Triangle star                                   ║
║    /star/arcturus      "Follow the arc to Arcturus"                           ║
║    /star/antares       "Rival of Mars", red heart of Scorpion                 ║
║    /:stars             Full table with magnitude, color, medieval use         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  OUTPUT FORMATS:                                                              ║
║                                                                               ║
║    ?format=j           JSON output                                            ║
║    (default)           ASCII art with visibility info                         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  EXAMPLES:                                                                    ║
║                                                                               ║
║    curl localhost:PORT/orion                                                  ║
║    curl localhost:PORT/star/sirius                                            ║
║    curl localhost:PORT/:stars?format=j                                        ║
║    curl localhost:PORT/ursa-major?format=j                                    ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🏛️ MEDIEVAL CONTEXT:                                                         ║
║                                                                               ║
║    Before mechanical clocks, people used stars to tell time:                  ║
║    • Polaris - Fixed point for nocturnal instruments                         ║
║    • Sirius - Brightest star; Egyptians based calendar on its rising         ║
║    • Orion setting before dawn → approaching sunrise (winter)                 ║
║    • Big Dipper rotating around Polaris → night hour                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        self._send_response(200, help_text, 'text/plain; charset=utf-8')
    
    def _send_about(self):
        """Send about page."""
        about_text = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⭐ Constellation Viewer - About ⭐                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  This tool displays ASCII art of major constellations with information        ║
║  about their visibility from your location.                                   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🏛️ HISTORICAL CONTEXT:                                                       ║
║                                                                               ║
║  Before mechanical clocks (14th century), people used the stars to tell       ║
║  time at night. Medieval bell ringers and watchmen knew the positions         ║
║  of constellations and used them to mark the night hours:                     ║
║                                                                               ║
║  • ORION: In winter, when Orion set in the west before dawn, it signaled      ║
║    that sunrise was approaching (time for Lauds, the dawn prayer)             ║
║                                                                               ║
║  • POLARIS & URSA MAJOR: The Big Dipper rotates around Polaris like a         ║
║    giant clock hand. Using a "nocturnal" instrument, one could read           ║
║    the night hour by the position of the pointer stars.                       ║
║                                                                               ║
║  • PLEIADES: When the Seven Sisters rose in the evening in late autumn,       ║
║    it marked harvest time and the approaching winter.                         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Related Tools:                                                               ║
║    • Subjective Day API (Nürnberger Uhr) - Medieval temporal hours            ║
║                                                                               ║
║  References:                                                                  ║
║    • https://en.wikipedia.org/wiki/Nocturnal_(instrument)                     ║
║    • https://en.wikipedia.org/wiki/Canonical_hours                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        self._send_response(200, about_text, 'text/plain; charset=utf-8')
    
    def _send_error(self, code: int, message: str):
        """Send error response."""
        self._send_response(code, f"Error {code}: {message}\n", 'text/plain')
    
    def _send_response(self, code: int, body: str, content_type: str):
        """Send HTTP response with CORS headers."""
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))


def run_server(host: str = '127.0.0.1', port: int = 8081, lat: float = 50.3167, lon: float = 11.9167):
    """Run the HTTP server."""
    ConstellationHTTPHandler.viewer = ConstellationViewer(lat, lon)
    
    server = HTTPServer((host, port), ConstellationHTTPHandler)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⭐ Constellation Viewer API ⭐                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Server running at: http://{host}:{port}/                                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Usage (like wttr.in):                                                        ║
║                                                                               ║
║    curl {host}:{port}/orion            # Orion the Hunter                         ║
║    curl {host}:{port}/ursa-major       # Big Dipper                               ║
║    curl {host}:{port}/pleiades         # Seven Sisters                            ║
║    curl {host}:{port}/:list            # List all constellations                  ║
║    curl {host}:{port}/:help            # Help page                                ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        server.shutdown()


# =============================================================================
# Demo / CLI
# =============================================================================

def demo():
    """Demo output showing constellation ASCII art."""
    viewer = ConstellationViewer(lat=50.3167, lon=11.9167)  # Hof, Germany
    
    print("=" * 60)
    print("Constellation Viewer - Demo")
    print("=" * 60)
    
    # Show Orion
    orion = viewer.get_constellation('orion')
    print(f"\n{orion['name']} ({orion['name_de']})")
    print(orion['ascii_art'])
    print(f"\nVisibility: {orion['visibility']['status']}")
    print(f"Direction: {orion['visibility']['direction']}")
    print(f"Medieval use: {orion['medieval_use']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Constellation Viewer - ASCII Art Night Sky')
    parser.add_argument('--serve', action='store_true', help='Run HTTP server')
    parser.add_argument('--port', type=int, default=8081, help='Server port (default: 8081)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host')
    parser.add_argument('--lat', type=float, default=50.3167, help='Latitude (default: Hof, Germany)')
    parser.add_argument('--lon', type=float, default=11.9167, help='Longitude (default: Hof, Germany)')
    
    args = parser.parse_args()
    
    if args.serve:
        run_server(host=args.host, port=args.port, lat=args.lat, lon=args.lon)
    else:
        demo()
