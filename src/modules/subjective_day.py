"""
Nürnberger Uhr (Nuremberg Clock) - Subjective Time Calculator

Die Nürnberger Uhr / The Nuremberg Clock System

This module implements the historical "Nürnberger Uhr" timekeeping system,
which uses "unequal hours" (temporale Stunden) based on sunrise and sunset.

Historical Background (from Friedrich Nicolai, 1783):
    "Zu den Gewohnheiten, welche bloß beybehalten werden, weil sie alt sind,
     gehört auch die sogenannte große Uhr. Man nennt in Nürnberg die sonst
     gewöhnliche Art von 1 bis 12 zu schlagen die kleine Uhr."
    
    (Among customs preserved merely because they are old, is the so-called
     große Uhr. In Nuremberg, the usual way of striking 1 to 12 is called
     the kleine Uhr.)

The System:
- "Große Uhr" (great clock): The Nürnberger seasonal hour system
- "Kleine Uhr" (small clock): The standard 12-hour system we use today
- Wendetage: 16 adjustment days per year to keep hours aligned with sunrise/sunset
- Garaus: The horn signal for closing city gates at sunset
- Türmer: Tower watchmen who rang the bells using sundials, water clocks, and stars

Implementation Note:
    This implementation uses the simplified "temporal hours" system (12/12 division),
    which is the more widely recognized interpretation of medieval timekeeping.
    The historical Nuremberg system actually used variable hour counts:
    - Winter Solstice: 8 Tagstunden + 16 Nachtstunden
    - Summer Solstice: 16 Tagstunden + 8 Nachtstunden
    Our 12/12 system keeps hour COUNT constant but varies hour LENGTH seasonally,
    which is the approach used by most temporal hour implementations today.

Seasonal Variation (in our 12/12 implementation):
- Day hours range from ~40-45 min (winter) to ~75-80 min (summer)
- Night hours range from ~75-80 min (winter) to ~40-45 min (summer)
- At equinox: both day and night hours ≈ 60 min each

API Usage (wttr.in style):
    curl localhost:8080/Berlin            # Plain text output
    curl localhost:8080/50.3,11.9         # Coordinates
    curl localhost:8080/munich?format=j   # JSON output
    curl localhost:8080/hof?format=watch  # Smartwatch format
    curl localhost:8080/:help             # Help page
    curl localhost:8080/:about            # Historical information
    curl localhost:8080/:learn            # Tutorial & lessons
    curl localhost:8080/:nocturnal        # Digital star clock

Python Usage:
    from src.modules.subjective_day import SubjectiveTime
    uhr = SubjectiveTime(lat=50.3167, lon=11.9167)
    result = uhr.get_subjective_day()

Start Server:
    python3 src/modules/subjective_day.py --serve --port 8080

References:
- Friedrich Nicolai: "Beschreibung einer Reise durch Deutschland" (1783)
- https://nuernberginfos.de/nuernberg-mix/nuernberger-uhr.php
- https://de.wikipedia.org/wiki/Nürnberger_Uhr
- https://www.chemie-schule.de/KnowHow/Nürnberger_Uhr
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple


# Constants for sunrise/sunset calculations
DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi


class SubjectiveTime:
    """
    Calculator for Nürnberger Uhr (Nuremberg Clock) subjective time.
    
    This implements the historical unequal hours system where:
    - 12 "day hours" span from sunrise to sunset
    - 12 "night hours" span from sunset to sunrise
    - Hour lengths vary seasonally
    
    Example:
        >>> uhr = SubjectiveTime(lat=50.3167, lon=11.9167)  # Hof, Germany
        >>> result = uhr.get_subjective_day()
        >>> print(result['display'])
        '3. Stunde des Tages (3rd hour of day)'
    """
    
    def __init__(self, lat: float, lon: float, tz_offset_hours: float = None, system: str = "kleine"):
        """
        Initialize the Nürnberger Uhr calculator.
        
        Args:
            lat: Latitude in decimal degrees (positive = North, range: -90 to 90)
            lon: Longitude in decimal degrees (positive = East, range: -180 to 180)
            tz_offset_hours: Timezone offset from UTC in hours (auto-detected if None)
            system: Clock system to use:
                - "kleine" (default): Simplified 12/12 system - always 12 day + 12 night hours
                - "große" or "grosse": Historical Nuremberg system - 8-16 variable hour counts
        
        Raises:
            ValueError: If latitude or longitude is out of valid range
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
        
        self.lat = lat
        self.lon = lon
        self._last_polar_type = None
        
        # Set clock system
        system_lower = system.lower() if system else "kleine"
        if system_lower in ("große", "grosse", "gross", "big", "historical"):
            self.system = "große"
        else:
            self.system = "kleine"
        
        # Auto-detect timezone offset if not provided
        if tz_offset_hours is None:
            # Central European Time approximation (Germany)
            # Use CET (UTC+1) in winter, CEST (UTC+2) in summer
            now = datetime.now()
            # European DST: last Sunday of March to last Sunday of October
            self.tz_offset_hours = self._get_cet_offset(now)
        else:
            self.tz_offset_hours = tz_offset_hours
    
    def _get_cet_offset(self, dt: datetime) -> int:
        """
        Get Central European Time offset for a given date.
        
        European DST runs from the last Sunday of March (02:00) 
        to the last Sunday of October (03:00).
        
        Args:
            dt: Datetime to check
            
        Returns:
            1 for CET (winter), 2 for CEST (summer)
        """
        year = dt.year
        
        # Find last Sunday of March
        march_last_day = datetime(year, 3, 31)
        march_last_sunday = march_last_day - timedelta(days=(march_last_day.weekday() + 1) % 7)
        dst_start = march_last_sunday.replace(hour=2, minute=0, second=0, microsecond=0)
        
        # Find last Sunday of October
        october_last_day = datetime(year, 10, 31)
        october_last_sunday = october_last_day - timedelta(days=(october_last_day.weekday() + 1) % 7)
        dst_end = october_last_sunday.replace(hour=3, minute=0, second=0, microsecond=0)
        
        # Check if in DST period
        if dst_start <= dt < dst_end:
            return 2  # CEST (summer time)
        else:
            return 1  # CET (winter time)
    
    def _calculate_julian_day(self, dt: datetime) -> float:
        """
        Calculate Julian Day Number from datetime.
        
        Args:
            dt: Datetime object
            
        Returns:
            Julian Day Number as float
        """
        year = dt.year
        month = dt.month
        day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return jd
    
    def _calculate_sun_position(self, jd: float) -> Tuple[float, float]:
        """
        Calculate sun declination and equation of time.
        
        Args:
            jd: Julian Day Number
            
        Returns:
            Tuple of (declination in degrees, equation of time in minutes)
        """
        # Days since J2000.0
        n = jd - 2451545.0
        
        # Mean solar longitude (degrees)
        L = (280.460 + 0.9856474 * n) % 360
        
        # Mean anomaly (degrees)
        g = (357.528 + 0.9856003 * n) % 360
        g_rad = g * DEG_TO_RAD
        
        # Ecliptic longitude (degrees)
        lambda_sun = L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
        
        # Obliquity of ecliptic (degrees)
        epsilon = 23.439 - 0.0000004 * n
        epsilon_rad = epsilon * DEG_TO_RAD
        
        # Solar declination
        lambda_rad = lambda_sun * DEG_TO_RAD
        declination = math.asin(math.sin(epsilon_rad) * math.sin(lambda_rad)) * RAD_TO_DEG
        
        # Equation of time (minutes)
        y = math.tan(epsilon_rad / 2) ** 2
        L_rad = L * DEG_TO_RAD
        eot = 4 * RAD_TO_DEG * (y * math.sin(2 * L_rad) 
                                - 2 * 0.01671 * math.sin(g_rad) 
                                + 4 * 0.01671 * y * math.sin(g_rad) * math.cos(2 * L_rad)
                                - 0.5 * y * y * math.sin(4 * L_rad)
                                - 1.25 * 0.01671 * 0.01671 * math.sin(2 * g_rad))
        
        return declination, eot
    
    def _calculate_sunrise_sunset(self, dt: datetime) -> Tuple[datetime, datetime]:
        """
        Calculate sunrise and sunset times for a given date.
        
        Args:
            dt: Datetime (only date portion is used)
            
        Returns:
            Tuple of (sunrise_datetime, sunset_datetime) or (None, None, polar_type) for polar regions
        """
        # Use noon on the given day for calculation
        noon = dt.replace(hour=12, minute=0, second=0, microsecond=0)
        jd = self._calculate_julian_day(noon)
        
        # Get sun position
        declination, eot = self._calculate_sun_position(jd)
        
        # Hour angle at sunrise/sunset (degrees)
        # Using standard refraction of -0.833 degrees
        lat_rad = self.lat * DEG_TO_RAD
        decl_rad = declination * DEG_TO_RAD
        
        cos_hour_angle = (math.sin(-0.833 * DEG_TO_RAD) - 
                          math.sin(lat_rad) * math.sin(decl_rad)) / \
                         (math.cos(lat_rad) * math.cos(decl_rad))
        
        # Store polar type for later reference
        self._last_polar_type = None
        
        # Handle polar day/night
        if cos_hour_angle > 1:
            # Polar night - sun never rises (cos > 1 means sun is always below horizon)
            self._last_polar_type = 'night'
            return None, None
        elif cos_hour_angle < -1:
            # Polar day - sun never sets (cos < -1 means sun is always above horizon)
            self._last_polar_type = 'day'
            return None, None
        
        hour_angle = math.acos(cos_hour_angle) * RAD_TO_DEG
        
        # Solar noon (local time)
        solar_noon_minutes = 720 - 4 * self.lon - eot + self.tz_offset_hours * 60
        
        # Sunrise and sunset in minutes from midnight
        sunrise_minutes = solar_noon_minutes - hour_angle * 4
        sunset_minutes = solar_noon_minutes + hour_angle * 4
        
        # Convert to datetime
        base_date = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        
        sunrise = base_date + timedelta(minutes=sunrise_minutes)
        sunset = base_date + timedelta(minutes=sunset_minutes)
        
        return sunrise, sunset
    
    def get_sunrise_sunset(self, dt: datetime = None) -> Dict[str, Any]:
        """
        Get sunrise and sunset times for a given date.
        
        Args:
            dt: Datetime (defaults to now)
            
        Returns:
            Dict with sunrise, sunset, day_length, night_length
        """
        if dt is None:
            dt = datetime.now()
        
        sunrise, sunset = self._calculate_sunrise_sunset(dt)
        
        if sunrise is None or sunset is None:
            polar_type = getattr(self, '_last_polar_type', 'night')
            return {
                'polar': True,
                'polar_type': polar_type,
                'sunrise': None,
                'sunset': None
            }
        
        day_length = (sunset - sunrise).total_seconds()
        night_length = 86400 - day_length  # 24 hours minus day length
        
        return {
            'polar': False,
            'sunrise': sunrise,
            'sunset': sunset,
            'day_length_hours': day_length / 3600,
            'night_length_hours': night_length / 3600,
            'day_hour_length_minutes': (day_length / 12) / 60,
            'night_hour_length_minutes': (night_length / 12) / 60
        }
    
    def _get_grosse_uhr_hours(self, day_length_hours: float) -> Tuple[int, int]:
        """
        Calculate the number of day and night hours for the Große Uhr system.
        
        The historical Nuremberg system divided the 24-hour period into day and night
        hours based on actual daylight. The number of hours varied from 8 to 16:
        
        - Winter solstice (~8h daylight): 8 day hours, 16 night hours
        - Summer solstice (~16h daylight): 16 day hours, 8 night hours
        - Equinox (~12h daylight): 12 day hours, 12 night hours
        
        The Wendetage (turning days) adjusted in 1-hour steps, about 16 times per year.
        
        Args:
            day_length_hours: Length of day in hours (sunrise to sunset)
            
        Returns:
            Tuple of (day_hours, night_hours) - sum is always 24
        """
        # Calculate proportion of day vs total
        # Map day length (roughly 8-16 hours in central Europe) to 8-16 hour counts
        # Using linear interpolation: 8h daylight -> 8 day hours, 16h daylight -> 16 day hours
        
        # Clamp to reasonable range (8-16 hours of daylight)
        clamped_day = max(8.0, min(16.0, day_length_hours))
        
        # Round to nearest whole hour for the historical step-based system
        day_hours = round(clamped_day)
        
        # Ensure we stay in valid range
        day_hours = max(8, min(16, day_hours))
        night_hours = 24 - day_hours
        
        return day_hours, night_hours
    
    def get_subjective_day(self, dt: datetime = None) -> Dict[str, Any]:
        """
        Calculate the subjective time according to Nürnberger Uhr.
        
        Args:
            dt: Datetime to calculate for (defaults to now)
            
        Returns:
            Dict containing:
                - is_day: bool - True if during day hours
                - hour: int - Current hour (1-12)
                - minute: int - Minutes within current hour (0-59 equivalent scale)
                - hour_length_minutes: float - Length of current hour in real minutes
                - period: str - "Tag" (day) or "Nacht" (night)
                - display: str - Human-readable display string
                - display_de: str - German display string
                - display_en: str - English display string
                - timestamp: str - ISO format of calculation time
                - location: dict - Lat/lon used
                - sunrise: str - Today's sunrise
                - sunset: str - Today's sunset
        """
        if dt is None:
            dt = datetime.now()
        
        # Get today's sunrise and sunset
        sun_data = self.get_sunrise_sunset(dt)
        
        if sun_data['polar']:
            return {
                'polar': True,
                'polar_type': sun_data['polar_type'],
                'is_day': sun_data['polar_type'] == 'day',
                'hour': 0,
                'minute': 0,
                'display': 'Polar ' + sun_data['polar_type'],
                'display_de': 'Polarer ' + ('Tag' if sun_data['polar_type'] == 'day' else 'Nacht'),
                'display_en': 'Polar ' + sun_data['polar_type'],
                'timestamp': dt.isoformat(),
                'location': {'lat': self.lat, 'lon': self.lon}
            }
        
        sunrise = sun_data['sunrise']
        sunset = sun_data['sunset']
        
        # Get previous day's sunset and next day's sunrise for night calculation
        yesterday = dt - timedelta(days=1)
        tomorrow = dt + timedelta(days=1)
        
        _, yesterday_sunset = self._calculate_sunrise_sunset(yesterday)
        tomorrow_sunrise, _ = self._calculate_sunrise_sunset(tomorrow)
        
        # Determine if it's day or night and calculate subjective hour
        # Calculate hour counts based on system
        day_length_real = (sunset - sunrise).total_seconds()
        day_length_hours = day_length_real / 3600
        
        if self.system == "große":
            # Historical Große Uhr: variable hour counts (8-16)
            num_day_hours, num_night_hours = self._get_grosse_uhr_hours(day_length_hours)
        else:
            # Simplified Kleine Uhr: always 12/12
            num_day_hours, num_night_hours = 12, 12
        
        if sunrise <= dt < sunset:
            # Daytime
            is_day = True
            period = "Tag"
            period_en = "day"
            
            # Calculate position within day
            day_length = day_length_real
            elapsed = (dt - sunrise).total_seconds()
            remaining = day_length - elapsed
            
            # Each day hour (divide by actual number of hours for this system)
            hour_length = day_length / num_day_hours
            
            # Current hour (1 to num_day_hours)
            hour_float = elapsed / hour_length
            hour = int(hour_float) + 1
            if hour > num_day_hours:
                hour = num_day_hours
            
            # Minutes within hour (scaled to 0-59)
            minute_fraction = hour_float - int(hour_float)
            minute = int(minute_fraction * 60)
            
            hour_length_minutes = hour_length / 60
            
            # Calculate hours since sunrise and until sunset (rounded)
            hours_since_sunrise = round(elapsed / 3600)
            hours_until_sunset = round(remaining / 3600)
            
        else:
            # Nighttime
            is_day = False
            period = "Nacht"
            period_en = "night"
            
            # Determine which night period we're in
            if dt >= sunset:
                # After sunset today - night until tomorrow's sunrise
                night_start = sunset
                night_end = tomorrow_sunrise
            else:
                # Before sunrise today - night from yesterday's sunset
                night_start = yesterday_sunset
                night_end = sunrise
            
            night_length = (night_end - night_start).total_seconds()
            elapsed = (dt - night_start).total_seconds()
            
            # Each night hour (divide by actual number of hours for this system)
            hour_length = night_length / num_night_hours
            
            # Current hour (1 to num_night_hours)
            hour_float = elapsed / hour_length
            hour = int(hour_float) + 1
            if hour > num_night_hours:
                hour = num_night_hours
            
            # Minutes within hour (scaled to 0-59)
            minute_fraction = hour_float - int(hour_float)
            minute = int(minute_fraction * 60)
            
            hour_length_minutes = hour_length / 60
            
            # Calculate hours until sunrise (rounded)
            time_until_sunrise = (night_end - dt).total_seconds()
            hours_until_sunrise = round(time_until_sunrise / 3600)
        
        # Generate ordinal suffix for English
        ordinal_suffix = self._get_ordinal_suffix(hour)
        
        # Get canonical hour (Horae Canonicae)
        canonical = self._get_canonical_hour(hour, is_day)
        
        # Build result
        result = {
            'polar': False,
            'is_day': is_day,
            'hour': hour,
            'minute': minute,
            'max_hours': num_day_hours if is_day else num_night_hours,  # Max hours for this period
            'hour_length_minutes': round(hour_length_minutes, 2),
            'period': period,
            'period_en': period_en,
            'system': self.system,  # "große" or "kleine"
            'system_name_de': "Große Uhr" if self.system == "große" else "Kleine Uhr",
            'system_name_en': "Great Clock" if self.system == "große" else "Small Clock",
            'display': f"{hour}. Stunde des {period}s",
            'display_de': f"{hour}. Stunde des {period}s ({hour_length_minutes:.1f} min/Std)",
            'display_en': f"{hour}{ordinal_suffix} hour of {period_en} ({hour_length_minutes:.1f} min/hr)",
            'time_formatted': f"{hour}:{minute:02d}",
            'timestamp': dt.isoformat(),
            'location': {'lat': self.lat, 'lon': self.lon},
            'sunrise': sunrise.strftime('%H:%M'),
            'sunset': sunset.strftime('%H:%M'),
            'num_day_hours': num_day_hours,
            'num_night_hours': num_night_hours,
            'day_hour_length_minutes': round((day_length_real / num_day_hours) / 60, 2),
            'night_hour_length_minutes': round(((86400 - day_length_real) / num_night_hours) / 60, 2),
            # Canonical hour (Horae Canonicae)
            'canonical_latin': canonical['latin'],
            'canonical_german': canonical['german'],
            'canonical_english': canonical['english'],
            'canonical_description': canonical['description']
        }
        
        # Add hours info for daytime
        if is_day:
            result['hours_since_sunrise'] = hours_since_sunrise
            result['hours_until_sunset'] = hours_until_sunset
            
            # German and English descriptions
            if hours_since_sunrise == 1:
                result['since_sunrise_de'] = "1 Stunde seit Sonnenaufgang"
                result['since_sunrise_en'] = "1 hour since sunrise"
            else:
                result['since_sunrise_de'] = f"{hours_since_sunrise} Stunden seit Sonnenaufgang"
                result['since_sunrise_en'] = f"{hours_since_sunrise} hours since sunrise"
            
            if hours_until_sunset == 1:
                result['until_sunset_de'] = "Noch 1 Stunde bis Sonnenuntergang"
                result['until_sunset_en'] = "1 hour until sunset"
            else:
                result['until_sunset_de'] = f"Noch {hours_until_sunset} Stunden bis Sonnenuntergang"
                result['until_sunset_en'] = f"{hours_until_sunset} hours until sunset"
        
        # Add hours until sunrise for nighttime
        if not is_day:
            result['hours_until_sunrise'] = hours_until_sunrise
            if hours_until_sunrise == 1:
                result['until_sunrise_de'] = "Noch 1 Stunde bis Sonnenaufgang"
                result['until_sunrise_en'] = "1 hour until sunrise"
            else:
                result['until_sunrise_de'] = f"Noch {hours_until_sunrise} Stunden bis Sonnenaufgang"
                result['until_sunrise_en'] = f"{hours_until_sunrise} hours until sunrise"
        
        return result
    
    def _get_ordinal_suffix(self, n: int) -> str:
        """Get English ordinal suffix for a number."""
        if 11 <= n <= 13:
            return 'th'
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    
    def _get_canonical_hour(self, hour: int, is_day: bool) -> Dict[str, str]:
        """
        Get the canonical hour (Horae Canonicae) for the current subjective hour.
        
        The canonical hours were the fixed times of daily prayer in medieval 
        monastic tradition. They map approximately to the temporal hours:
        
        Day Hours (Horae Diurnae):
            - Prima (1st hour) - Sunrise, beginning of work
            - Tertia (3rd hour) - Mid-morning prayer
            - Sexta (6th hour) - Noon prayer (origin: Latin "sixth")
            - Nona (9th hour) - Afternoon prayer (origin of English "noon")
            - Vesper (12th hour) - Evening prayer at sunset
            
        Night Hours (Horae Nocturnae):
            - Compline (1st night hour) - Before sleep
            - Matins/Vigils (6th night hour) - Midnight prayer, deepest night
            - Lauds (12th night hour) - Dawn prayer, praise at first light
        
        Returns:
            Dict with 'latin', 'german', 'english', 'description' keys
        """
        if is_day:
            # Day canonical hours
            canonical_hours = {
                1: {'latin': 'Prima', 'german': 'Prim', 'english': 'Prime',
                    'description': 'Erste Tagstunde / First hour of day'},
                2: {'latin': 'Hora Secunda', 'german': 'Zweite Stunde', 'english': 'Second Hour',
                    'description': 'Zweite Tagstunde'},
                3: {'latin': 'Tertia', 'german': 'Terz', 'english': 'Terce',
                    'description': 'Dritte Tagstunde / Mid-morning prayer'},
                4: {'latin': 'Hora Quarta', 'german': 'Vierte Stunde', 'english': 'Fourth Hour',
                    'description': 'Vierte Tagstunde'},
                5: {'latin': 'Hora Quinta', 'german': 'Fünfte Stunde', 'english': 'Fifth Hour',
                    'description': 'Fünfte Tagstunde'},
                6: {'latin': 'Sexta', 'german': 'Sext', 'english': 'Sext',
                    'description': 'Mittag / Noon - Sixth hour prayer'},
                7: {'latin': 'Hora Septima', 'german': 'Siebte Stunde', 'english': 'Seventh Hour',
                    'description': 'Siebte Tagstunde'},
                8: {'latin': 'Hora Octava', 'german': 'Achte Stunde', 'english': 'Eighth Hour',
                    'description': 'Achte Tagstunde'},
                9: {'latin': 'Nona', 'german': 'Non', 'english': 'None',
                    'description': 'Neunte Tagstunde / Afternoon prayer (origin of "noon")'},
                10: {'latin': 'Hora Decima', 'german': 'Zehnte Stunde', 'english': 'Tenth Hour',
                     'description': 'Zehnte Tagstunde'},
                11: {'latin': 'Hora Undecima', 'german': 'Elfte Stunde', 'english': 'Eleventh Hour',
                     'description': 'Elfte Tagstunde'},
                12: {'latin': 'Vesper', 'german': 'Vesper', 'english': 'Vespers',
                     'description': 'Abendgebet bei Sonnenuntergang / Evening prayer at sunset'}
            }
        else:
            # Night canonical hours
            canonical_hours = {
                1: {'latin': 'Completorium', 'german': 'Komplet', 'english': 'Compline',
                    'description': 'Nachtgebet vor dem Schlaf / Night prayer before sleep'},
                2: {'latin': 'Hora Secunda Noctis', 'german': 'Zweite Nachtstunde', 'english': 'Second Night Hour',
                    'description': 'Zweite Nachtstunde'},
                3: {'latin': 'Hora Tertia Noctis', 'german': 'Dritte Nachtstunde', 'english': 'Third Night Hour',
                    'description': 'Dritte Nachtstunde'},
                4: {'latin': 'Hora Quarta Noctis', 'german': 'Vierte Nachtstunde', 'english': 'Fourth Night Hour',
                    'description': 'Vierte Nachtstunde'},
                5: {'latin': 'Hora Quinta Noctis', 'german': 'Fünfte Nachtstunde', 'english': 'Fifth Night Hour',
                    'description': 'Fünfte Nachtstunde'},
                6: {'latin': 'Matutinum', 'german': 'Matutin (Vigilien)', 'english': 'Matins (Vigils)',
                    'description': 'Mitternachtsgebet / Midnight prayer - deepest night'},
                7: {'latin': 'Hora Septima Noctis', 'german': 'Siebte Nachtstunde', 'english': 'Seventh Night Hour',
                    'description': 'Siebte Nachtstunde'},
                8: {'latin': 'Hora Octava Noctis', 'german': 'Achte Nachtstunde', 'english': 'Eighth Night Hour',
                    'description': 'Achte Nachtstunde'},
                9: {'latin': 'Hora Nona Noctis', 'german': 'Neunte Nachtstunde', 'english': 'Ninth Night Hour',
                    'description': 'Neunte Nachtstunde'},
                10: {'latin': 'Hora Decima Noctis', 'german': 'Zehnte Nachtstunde', 'english': 'Tenth Night Hour',
                     'description': 'Zehnte Nachtstunde'},
                11: {'latin': 'Hora Undecima Noctis', 'german': 'Elfte Nachtstunde', 'english': 'Eleventh Night Hour',
                     'description': 'Elfte Nachtstunde'},
                12: {'latin': 'Laudes', 'german': 'Laudes', 'english': 'Lauds',
                     'description': 'Morgenlob bei Tagesanbruch / Dawn prayer - praise at first light'}
            }
        
        return canonical_hours.get(hour, {'latin': '', 'german': '', 'english': '', 'description': ''})
    
    def get_full_day_hours(self, dt: datetime = None) -> Dict[str, Any]:
        """
        Get all 24 subjective hours for a given day.
        
        Args:
            dt: Date to calculate for (defaults to today)
            
        Returns:
            Dict with day_hours (12) and night_hours (12), each with start/end times
        """
        if dt is None:
            dt = datetime.now()
        
        sun_data = self.get_sunrise_sunset(dt)
        
        if sun_data['polar']:
            return {
                'polar': True,
                'polar_type': sun_data['polar_type'],
                'day_hours': [],
                'night_hours': []
            }
        
        sunrise = sun_data['sunrise']
        sunset = sun_data['sunset']
        
        # Get next day's sunrise for night hours
        tomorrow = dt + timedelta(days=1)
        tomorrow_sunrise, _ = self._calculate_sunrise_sunset(tomorrow)
        
        # Calculate day hours
        day_length = (sunset - sunrise).total_seconds()
        day_hour_length = day_length / 12
        
        day_hours = []
        for i in range(12):
            start = sunrise + timedelta(seconds=i * day_hour_length)
            end = sunrise + timedelta(seconds=(i + 1) * day_hour_length)
            day_hours.append({
                'hour': i + 1,
                'start': start.strftime('%H:%M:%S'),
                'end': end.strftime('%H:%M:%S'),
                'length_minutes': round(day_hour_length / 60, 2)
            })
        
        # Calculate night hours (sunset to next sunrise)
        night_length = (tomorrow_sunrise - sunset).total_seconds()
        night_hour_length = night_length / 12
        
        night_hours = []
        for i in range(12):
            start = sunset + timedelta(seconds=i * night_hour_length)
            end = sunset + timedelta(seconds=(i + 1) * night_hour_length)
            night_hours.append({
                'hour': i + 1,
                'start': start.strftime('%H:%M:%S'),
                'end': end.strftime('%H:%M:%S'),
                'length_minutes': round(night_hour_length / 60, 2)
            })
        
        return {
            'polar': False,
            'date': dt.strftime('%Y-%m-%d'),
            'sunrise': sunrise.strftime('%H:%M'),
            'sunset': sunset.strftime('%H:%M'),
            'day_hours': day_hours,
            'night_hours': night_hours,
            'day_hour_length_minutes': round(day_hour_length / 60, 2),
            'night_hour_length_minutes': round(night_hour_length / 60, 2)
        }


def get_subjective_day(lat: float, lon: float, dt: datetime = None) -> Dict[str, Any]:
    """
    Convenience function to get subjective time for a location.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        dt: Datetime (defaults to now)
        
    Returns:
        Dict with subjective time information
    """
    uhr = SubjectiveTime(lat, lon)
    return uhr.get_subjective_day(dt)


def get_sunrise_sunset(lat: float, lon: float, dt: datetime = None) -> Dict[str, Any]:
    """
    Convenience function to get sunrise/sunset for a location.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        dt: Datetime (defaults to now)
        
    Returns:
        Dict with sunrise/sunset information
    """
    uhr = SubjectiveTime(lat, lon)
    return uhr.get_sunrise_sunset(dt)


# Simple HTTP API server for local use
def run_api_server(host: str = '127.0.0.1', port: int = 8080):
    """
    Run a simple HTTP API server for subjective time (wttr.in style).
    
    Usage (curl-friendly):
        curl localhost:8080/50.3,11.9          # Plain text output
        curl localhost:8080/50.3,11.9?format=j # JSON output
        curl localhost:8080/:help              # Show help
    
    Args:
        host: Host to bind to (default: 127.0.0.1 for local only)
        port: Port to listen on (default: 8080)
    """
    import http.server
    import urllib.parse
    import json as json_module
    
    # Known city coordinates for friendly URLs
    KNOWN_CITIES = {
        'hof': (50.3167, 11.9167),
        'nuremberg': (49.4521, 11.0767),
        'nürnberg': (49.4521, 11.0767),
        'nuernberg': (49.4521, 11.0767),
        'berlin': (52.5200, 13.4050),
        'munich': (48.1351, 11.5820),
        'münchen': (48.1351, 11.5820),
        'muenchen': (48.1351, 11.5820),
        'frankfurt': (50.1109, 8.6821),
        'hamburg': (53.5511, 9.9937),
        'cologne': (50.9375, 6.9603),
        'köln': (50.9375, 6.9603),
        'koeln': (50.9375, 6.9603),
        'vienna': (48.2082, 16.3738),
        'wien': (48.2082, 16.3738),
        'zurich': (47.3769, 8.5417),
        'zürich': (47.3769, 8.5417),
        'prague': (50.0755, 14.4378),
        'prag': (50.0755, 14.4378),
        'amsterdam': (52.3676, 4.9041),
        'paris': (48.8566, 2.3522),
        'london': (51.5074, -0.1278),
        'rome': (41.9028, 12.4964),
        'rom': (41.9028, 12.4964),
        'madrid': (40.4168, -3.7038),
        'barcelona': (41.3851, 2.1734),
        'new york': (40.7128, -74.0060),
        'tokyo': (35.6762, 139.6503),
        'sydney': (-33.8688, 151.2093),
    }
    
    def get_help_text():
        """Generate wttr.in-style help text."""
        return f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🕐 Subjective Day - Nürnberger Uhr API                     ║
║                                                                               ║
║  Usage: curl {host}:{port}/LOCATION                                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  LOCATION can be:                                                             ║
║    • City name:     curl {host}:{port}/Berlin                                   ║
║    • Coordinates:   curl {host}:{port}/50.3,11.9                                ║
║    • Default (Hof): curl {host}:{port}/                                         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Output Formats:                                                              ║
║    (default)       Plain text / ASCII art                                     ║
║    ?format=j       JSON output                                                ║
║    ?format=1       One-line output (for scripts)                              ║
║    ?format=table   Hour table for the day                                     ║
║    ?format=watch   ⌚ Smartwatch complication data (minimal JSON)             ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🕐 CLOCK SYSTEMS (Große Uhr vs Kleine Uhr)                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║    ?system=kleine  (default) Simplified 12/12 system - always 12 hours        ║
║    ?system=grosse  Historical 8-16 system - variable hour counts              ║
║                                                                               ║
║  Examples:                                                                    ║
║    curl {host}:{port}/hof?system=grosse    # Historical Große Uhr             ║
║    curl {host}:{port}/hof?system=kleine    # Modern Kleine Uhr (default)      ║
║                                                                               ║
║  KLEINE UHR (small clock): Always 12 day + 12 night hours                     ║
║    • Hour LENGTH varies (winter days ~45 min/hr, summer ~75 min/hr)           ║
║    • Modern interpretation used in most temporal hour systems                 ║
║                                                                               ║
║  GROßE UHR (great clock): Variable hour counts (8-16)                         ║
║    • Winter: 8 day hours + 16 night hours                                     ║
║    • Summer: 16 day hours + 8 night hours                                     ║
║    • Historical Nuremberg system until 1806 (as described by Nicolai)         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ⌚ SMARTWATCH APPS                                                           ║
║    curl {host}:{port}/berlin?format=watch                                       ║
║                                                                               ║
║    Returns minimal JSON for watch complications:                              ║
║    {{"hour":3,"period":"night","time":"3:16","canonical":"Tertia",...}}          ║
║    Fields: hour, minute, period, icon, time, canonical, hr_len,               ║
║            sunrise, sunset, to_sunrise/to_sunset, short, medium               ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📚 LEARNING & TOOLS                                                          ║
║    /:learn         Tutorial on the Nürnberger Uhr system                      ║
║    /:nocturnal     ⭐ Digital Nocturnal instrument (star clock)               ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Examples:                                                                    ║
║    curl {host}:{port}/nuremberg                                                 ║
║    curl {host}:{port}/52.52,13.40                                               ║
║    curl {host}:{port}/berlin?format=j                                           ║
║    curl {host}:{port}/munich?format=watch                                       ║
║    curl {host}:{port}/hof?format=table                                          ║
║    curl {host}:{port}/hof?system=grosse                                         ║
║    curl {host}:{port}/:nocturnal                                                ║
║    curl {host}:{port}/:learn                                                    ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Special Pages:                                                               ║
║    /:help          This help page                                             ║
║    /:about         About the Nürnberger Uhr system                            ║
║    /:learn         📚 Tutorial & lessons (for learning)                       ║
║    /:nocturnal     ⭐ Digital nocturnal instrument                            ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Supported Cities:                                                            ║
║    Hof, Nuremberg, Berlin, Munich, Frankfurt, Hamburg, Cologne                ║
║    Vienna, Zurich, Prague, Amsterdam, Paris, London, Rome, Madrid             ║
║    Barcelona, New York, Tokyo, Sydney  (or use coordinates)                   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  What is Nürnberger Uhr?                                                      ║
║    A medieval timekeeping system where:                                       ║
║    • Day (sunrise→sunset) is divided into 12 equal "day hours"                ║
║    • Night (sunset→sunrise) is divided into 12 equal "night hours"            ║
║    • Hour lengths vary seasonally (winter day hours ~45 min)                  ║
║                                                                               ║
║  Reference: https://de.wikipedia.org/wiki/Nürnberger_Uhr                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

    def get_watch_data(result: dict) -> dict:
        """
        Generate minimal data for smartwatch apps.
        
        Designed for watch complications and small displays:
        - Minimal data for efficient transfer
        - Essential info only (hour, period, time remaining)
        - Icon hints for watch face rendering
        """
        watch = {
            'hour': result['hour'],
            'minute': result.get('minute', 0),
            'period': 'day' if result['is_day'] else 'night',
            'icon': '☀️' if result['is_day'] else '🌙',
            'time': result['time_formatted'],
            'canonical': result.get('canonical_latin', ''),
            'hr_len': round(result['hour_length_minutes']),
            'sunrise': result['sunrise'],
            'sunset': result['sunset'],
        }
        
        # Add time remaining info
        if result['is_day']:
            watch['to_sunset'] = result.get('hours_until_sunset', 0)
            watch['from_sunrise'] = result.get('hours_since_sunrise', 0)
        else:
            watch['to_sunrise'] = result.get('hours_until_sunrise', 0)
        
        # Complication-ready short strings
        watch['short'] = f"{result['hour']}{'d' if result['is_day'] else 'n'}"
        watch['medium'] = f"{result['time_formatted']} {'☀️' if result['is_day'] else '🌙'}"
        
        return watch
    
    def get_learn_text():
        """Generate learning mode content for understanding the system."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║              📚 LEARNING MODE - Nürnberger Uhr / Nocturnal                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  🎯 WHAT IS THIS?                                                             ║
║                                                                               ║
║  Before mechanical clocks, people used a different time system:               ║
║  • DAYLIGHT (sunrise → sunset) = 12 "day hours"                               ║
║  • NIGHT (sunset → sunrise) = 12 "night hours"                                ║
║                                                                               ║
║  This means hour LENGTH changes with seasons!                                 ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 LESSON 1: Seasonal Hours                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  WINTER (December):                                                           ║
║    Day hours = SHORT (~40-45 minutes)                                         ║
║    Night hours = LONG (~75-80 minutes)                                        ║
║                                                                               ║
║  SUMMER (June):                                                               ║
║    Day hours = LONG (~75-80 minutes)                                          ║
║    Night hours = SHORT (~40-45 minutes)                                       ║
║                                                                               ║
║  EQUINOX (March/September):                                                   ║
║    Day hours = Night hours ≈ 60 minutes each                                  ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 LESSON 2: The Canonical Hours (Church Bells)                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Medieval bells rang at these times (still used in monasteries):              ║
║                                                                               ║
║  DAY HOURS:                                                                   ║
║    1st Hour: PRIMA (Prime) .......... Sunrise - start of work day             ║
║    3rd Hour: TERTIA (Terce) ......... Mid-morning prayer                      ║
║    6th Hour: SEXTA (Sext) ........... Noon - midday rest                      ║
║    9th Hour: NONA (None) ............ Afternoon (origin of "noon"!)           ║
║   12th Hour: VESPER (Vespers) ....... Sunset - evening prayer                 ║
║                                                                               ║
║  NIGHT HOURS:                                                                 ║
║    1st Hour: COMPLINE ............... Bedtime prayer                          ║
║    6th Hour: MATINS ................. Midnight vigil (monks awake!)           ║
║   12th Hour: LAUDS .................. Dawn praise (before sunrise)            ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 LESSON 3: The Nocturnal Instrument                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Before clocks, how did people tell time at night?                            ║
║                                                                               ║
║  The NOCTURNAL was a handheld tool that used STARS:                           ║
║                                                                               ║
║         ⭐ POLARIS (North Star)                                                ║
║              │                                                                ║
║         ╭────┼────╮                                                           ║
║        ╱     │     ╲   ← Big Dipper rotates around Polaris                    ║
║       │  ▫  │  ▫   │                                                          ║
║        ╲     │     ╱                                                          ║
║         ╰────┼────╯                                                           ║
║              │                                                                ║
║                                                                               ║
║  HOW IT WORKED:                                                               ║
║    1. Align the instrument to Polaris (through center hole)                   ║
║    2. Rotate arm to point at the "pointer stars" of Big Dipper                ║
║    3. Read the hour from the scale                                            ║
║                                                                               ║
║  The stars rotate ~15° per hour, completing 360° in 24 hours!                 ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📖 LESSON 4: Reading the Stars                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Medieval bell ringers used these patterns:                                   ║
║                                                                               ║
║  ORION (Winter):                                                              ║
║    • Rising in the east = Early evening (1st-3rd night hour)                  ║
║    • High in the south = Midnight (MATINS time)                               ║
║    • Setting in the west = Dawn approaching (LAUDS time)                      ║
║                                                                               ║
║  URSA MAJOR (Big Dipper):                                                     ║
║    • Always visible in northern sky                                           ║
║    • Points to Polaris (North Star)                                           ║
║    • Position indicates the night hour                                        ║
║                                                                               ║
║  PLEIADES (Seven Sisters):                                                    ║
║    • Autumn rising = Harvest time                                             ║
║    • Used for seasonal calendar                                               ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🎮 PRACTICE                                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Try these API calls to practice:                                             ║
║                                                                               ║
║    curl localhost:PORT/hof                # Your current subjective time      ║
║    curl localhost:PORT/hof?format=table   # All 24 hours for today            ║
║    curl localhost:PORT/hof?format=watch   # Watch complication data           ║
║                                                                               ║
║  Constellation viewer (separate server):                                      ║
║    curl localhost:8081/orion              # See Orion pattern                 ║
║    curl localhost:8081/ursa-major         # See Big Dipper                    ║
║    curl localhost:8081/:list              # All constellations                ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  💡 FUN FACT                                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  The word "NOON" comes from Latin "NONA" (9th hour).                          ║
║                                                                               ║
║  Originally, noon was the 9th hour after sunrise (~3 PM in modern time).      ║
║  Over centuries, the meaning shifted to midday (12 PM).                       ║
║                                                                               ║
║  This happened because monks moved the Nona prayer earlier so they            ║
║  could eat their main meal sooner! 🍽️                                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def get_nocturnal_text(lat: float = 50.3167, lon: float = 11.9167):
        """Generate nocturnal instrument display."""
        uhr = SubjectiveTime(lat, lon)
        result = uhr.get_subjective_day()
        
        # Determine dial position (0-360 degrees based on time of night)
        if not result['is_day']:
            # Night time - calculate rotation
            night_progress = (result['hour'] - 1 + result['minute'] / 60) / 12.0
            rotation = int(night_progress * 360)
        else:
            rotation = 0
        
        # Generate dial visualization
        pointer_positions = {
            0: "   ▲   ", 30: "  ▲    ", 60: " ▲     ", 90: "▲      ",
            120: "▲      ", 150: " ▲     ", 180: "  ▲    ", 210: "   ▲   ",
            240: "    ▲  ", 270: "     ▲ ", 300: "      ▲", 330: "     ▲ "
        }
        nearest = min(pointer_positions.keys(), key=lambda x: abs(x - rotation))
        pointer = pointer_positions[nearest]
        
        hour_display = f"{result['hour']}:{result['minute']:02d}"
        period = "Night" if not result['is_day'] else "Day"
        canonical = result.get('canonical_latin', '')
        
        return f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ⭐ NOCTURNAL INSTRUMENT ⭐                                  ║
║                     Digital Star Clock                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                           ✦ POLARIS ✦                                         ║
║                               │                                               ║
║                        ╭──────┼──────╮                                        ║
║                       ╱   12  │  1    ╲                                       ║
║                      │ 11    ─┼─    2  │                                      ║
║                      │ 10    {pointer}   3  │                                 ║
║                      │  9    ─┼─    4  │                                      ║
║                       ╲   8   │  5    ╱                                       ║
║                        ╰──────┼──────╯                                        ║
║                               │                                               ║
║                           ☆  ☆  ☆                                             ║
║                        BIG DIPPER                                             ║
║                        (pointer stars)                                        ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║     📍 Current Reading:                                                       ║
║                                                                               ║
║        ┌────────────────────────────────┐                                     ║
║        │  {period:^5} Hour: {hour_display:^5}             │                   ║
║        │  {canonical:^30} │                                                   ║
║        └────────────────────────────────┘                                     ║
║                                                                               ║
║     ☀️  Sunrise: {result['sunrise']:<8}                                        ║
║     🌅 Sunset:  {result['sunset']:<8}                                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  HOW TO USE A REAL NOCTURNAL:                                                 ║
║                                                                               ║
║  1. Hold instrument vertically at arm's length                                ║
║  2. Look through center hole to sight Polaris                                 ║
║  3. Rotate the arm to align with the "pointer stars"                          ║
║     (two stars at end of Big Dipper that point to Polaris)                    ║
║  4. Read the hour where the arm crosses the date ring                         ║
║                                                                               ║
║  The stars complete one full circle every 23h 56m (sidereal day)              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

    def get_about_text():
        """Generate about page with historical information from nuernberginfos.de."""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        🕐 DIE NÜRNBERGER UHR                                  ║
║                    (The Nuremberg Clock System)                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  The Nürnberger Uhr was a unique historical timekeeping method used in        ║
║  Nuremberg and neighboring cities from the Middle Ages. Its distinctive       ║
║  feature was adapting to the changing length of daylight across seasons.      ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📜 FRIEDRICH NICOLAI (1783)                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  "Zu den Gewohnheiten, welche bloß beybehalten werden, weil sie alt sind,     ║
║   gehört auch die sogenannte große Uhr. Man nennt in Nürnberg die sonst       ║
║   gewöhnliche Art von 1 bis 12 zu schlagen die kleine Uhr, welche auch        ║
║   von verschiedenen Thürmen in der Stadt schlägt. [...]                       ║
║                                                                               ║
║   Da kein mechanisches Uhrwerk in der Lage war, dem entsprechenden            ║
║   Tag-/Nachtrhythmus zu folgen, musste die Zeit durch Turmwächter             ║
║   angeschlagen werden, die auf den Kirchtürmen von St. Sebald und             ║
║   St. Lorenz, sowie auf dem Weißen Turm und dem Laufer Schlagturm             ║
║   positioniert waren."                                                        ║
║                                                                               ║
║  Translation:                                                                 ║
║  "Among the customs preserved merely because they are old, is the so-called   ║
║   große Uhr (great clock). In Nuremberg, the usual way of striking 1 to 12    ║
║   is called the kleine Uhr (small clock), which also strikes from various     ║
║   towers in the city. [...]                                                   ║
║                                                                               ║
║   Since no mechanical clockwork was able to follow the corresponding          ║
║   day/night rhythm, the time had to be struck by tower watchmen who were      ║
║   positioned on the church towers of St. Sebald and St. Lorenz, as well as    ║
║   on the White Tower (Weißer Turm) and the Laufer Schlagturm."                ║
║                                                                               ║
║  — Friedrich Nicolai, "Beschreibung einer Reise durch Deutschland             ║
║    und die Schweiz im Jahre 1781" (published 1783)                            ║
║                                                                               ║
║  NOTE: The "kleine Uhr" (since 1436 at St. Katharina) became standard,        ║
║  while the "große Uhr" remained in use until Nuremberg joined Bavaria (1806). ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📅 TEMPORALE STUNDEN (Seasonal/Unequal Hours)                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  THE HISTORICAL NUREMBERG SYSTEM varied the NUMBER of hours:                  ║
║                                                                               ║
║    ❄️  WINTER (around Dec 21):                                                 ║
║        • 8 Tagstunden (day hours) - SHORT                                     ║
║        • 16 Nachtstunden (night hours) - LONG                                 ║
║                                                                               ║
║    ☀️  SUMMER (around Jun 21):                                                 ║
║        • 16 Tagstunden (day hours) - LONG                                     ║
║        • 8 Nachtstunden (night hours) - SHORT                                 ║
║                                                                               ║
║    🌗 EQUINOX (Mar 21 / Sep 21):                                               ║
║        • 12 Tagstunden = 12 Nachtstunden (equal length, ~60 min each)         ║
║                                                                               ║
║  THIS API uses the simplified 12/12 "temporal hours" interpretation:          ║
║    • Always 12 day hours + 12 night hours                                     ║
║    • Hour LENGTH varies seasonally (not count)                                ║
║    • Winter day hours: ~45 min, night hours: ~75 min                          ║
║    • Summer day hours: ~75 min, night hours: ~45 min                          ║
║    • This is the more common modern interpretation of "unequal hours"         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🔄 WENDETAGE (Turning Days)                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  To keep hours as "even" as possible, adjustments called "Wendetage" were     ║
║  made about 16 times per year. The number of day/night hours changed in       ║
║  one-hour steps to match sunrise and sunset times.                            ║
║                                                                               ║
║  This gradual transition ensured the system remained practical for daily      ║
║  life while following the natural rhythm of the sun.                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  🔔 TÜRMER UND GLOCKEN (Tower Watchmen & Bells)                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Early mechanical clocks could not easily accommodate changing intervals.     ║
║  Instead, time was announced by the city's TÜRMER (tower watchmen), who       ║
║  rang bells at the appropriate intervals using:                               ║
║                                                                               ║
║    • Sundials (during daylight)                                               ║
║    • Water clocks / Clepsydra (at night)                                      ║
║    • Candle clocks with hour markings                                         ║
║    • Star positions (nocturnal instrument)                                    ║
║                                                                               ║
║  📯 THE GARAUS:                                                                ║
║  The closing of city gates followed sunset, announced by horn from the        ║
║  city towers. Events were commonly scheduled "one hour after sunset"          ║
║  (which fell at different times by season).                                   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ⚙️  TRANSITION TO MECHANICAL CLOCKS                                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  The Nürnberger Uhr was a blend between the old system of "temporale          ║
║  Stunden" and the new mechanical clocks based on "äquinoktiale Stunden"       ║
║  (equal hours), which became dominant across Europe in the early modern era.  ║
║                                                                               ║
║  🥚 THE NÜRNBERGER EI (Nuremberg Egg):                                         ║
║  Nuremberg became famous in the 16th century for portable timepieces          ║
║  created by PETER HENLEIN. These early pocket watches ("Nürnberger Ei")       ║
║  marked the transition to personal, standardized timekeeping - though         ║
║  they no longer used seasonal hours.                                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  💡 WHY THIS SYSTEM MADE SENSE                                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Before artificial lighting, this system was deeply practical:                ║
║                                                                               ║
║    • Work hours naturally aligned with available daylight                     ║
║    • "First hour of day" always meant sunrise (start of work)                 ║
║    • "Twelfth hour of day" always meant sunset (end of work)                  ║
║    • Church prayers (canonical hours) followed the sun                        ║
║    • Sundials automatically showed temporal hours                             ║
║                                                                               ║
║  Medieval people didn't count minutes - the bell's ring was the reference.    ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  📚 REFERENCES                                                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  • https://nuernberginfos.de/nuernberg-mix/nuernberger-uhr.php                ║
║  • https://de.wikipedia.org/wiki/Nürnberger_Uhr                               ║
║  • https://www.chemie-schule.de/KnowHow/Nürnberger_Uhr                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

    def format_plain_text(result: dict, location_name: str) -> str:
        """Format result as plain text ASCII art."""
        period_icon = "☀️" if result['is_day'] else "🌙"
        
        # Add time progress line
        progress_line = ""
        if result['is_day'] and 'hours_since_sunrise' in result:
            progress_line = f"\n│     ⏰ {result['since_sunrise_en']} · {result['until_sunset_en']:<20} │"
        elif not result['is_day'] and 'hours_until_sunrise' in result:
            progress_line = f"\n│     ⏰ {result['until_sunrise_en']:<49} │"
        
        # Add canonical hour line
        canonical_line = ""
        if result.get('canonical_latin'):
            canonical_line = f"\n│     ⛪ {result['canonical_latin']} ({result['canonical_english']})                              │"
        
        return f"""
┌───────────────────────────────────────────────────────────┐
│  🕐 Subjective Time for {location_name:<32} │
├───────────────────────────────────────────────────────────┤
│                                                           │
│     {period_icon}  {result['display_en']:<47} │
│                                                           │
│     Subjective Time:  {result['time_formatted']:>5} ({result['period_en']})                      │{progress_line}{canonical_line}
│                                                           │
├───────────────────────────────────────────────────────────┤
│  ☀️  Sunrise:  {result['sunrise']:<8}    🌅 Sunset:  {result['sunset']:<8}        │
├───────────────────────────────────────────────────────────┤
│  Day hour:   {result['day_hour_length_minutes']:>5.1f} min    Night hour:  {result['night_hour_length_minutes']:>5.1f} min     │
├───────────────────────────────────────────────────────────┤
│  📍 {result['location']['lat']:.4f}°N, {result['location']['lon']:.4f}°E                               │
│  🕐 {result['timestamp'][:19]}                            │
└───────────────────────────────────────────────────────────┘
"""

    def format_one_line(result: dict) -> str:
        """Format result as one line for scripts."""
        period = "day" if result['is_day'] else "night"
        base = f"{result['hour']}:{result['minute']:02d} {period} ({result['hour_length_minutes']:.1f}min/hr) | ☀️{result['sunrise']} 🌅{result['sunset']}"
        
        # Add time progress info
        if result['is_day'] and 'hours_until_sunset' in result:
            base += f" | ⏰{result['hours_until_sunset']}h to sunset"
        elif not result['is_day'] and 'hours_until_sunrise' in result:
            base += f" | ⏰{result['hours_until_sunrise']}h to sunrise"
        
        return base + "\n"

    def format_table(day_hours: dict, location_name: str) -> str:
        """Format day hours as ASCII table."""
        lines = [
            f"┌─────────────────────────────────────────────────────────────────────┐",
            f"│  🕐 Hour Table for {location_name:<47} │",
            f"│     {day_hours['date']}  (☀️ {day_hours['sunrise']} → 🌅 {day_hours['sunset']})                          │",
            f"├─────────────────────────────────────────────────────────────────────┤",
            f"│  Hour │   Day Start  →  End    │  Night Start  →  End   │  Length  │",
            f"├───────┼────────────────────────┼────────────────────────┼──────────┤",
        ]
        
        for i in range(12):
            dh = day_hours['day_hours'][i]
            nh = day_hours['night_hours'][i]
            lines.append(
                f"│  {i+1:>2}   │  {dh['start'][:5]} → {dh['end'][:5]}      │  {nh['start'][:5]} → {nh['end'][:5]}       │  {dh['length_minutes']:>5.1f}m  │"
            )
        
        lines.extend([
            f"├───────┴────────────────────────┴────────────────────────┴──────────┤",
            f"│  Day hour: {day_hours['day_hour_length_minutes']:.1f} min   │   Night hour: {day_hours['night_hour_length_minutes']:.1f} min                  │",
            f"└─────────────────────────────────────────────────────────────────────┘",
        ])
        
        return "\n".join(lines) + "\n"

    def parse_location(path: str) -> Tuple[float, float, str]:
        """Parse location from URL path. Returns (lat, lon, name)."""
        # Remove leading slash
        location = path.lstrip('/')
        
        # Handle empty path (default to Hof)
        if not location or location == '/':
            return 50.3167, 11.9167, "Hof, Germany"
        
        # Check for coordinates format: "lat,lon"
        if ',' in location:
            try:
                parts = location.split(',')
                lat = float(parts[0])
                lon = float(parts[1])
                return lat, lon, f"{lat:.4f}°N, {lon:.4f}°E"
            except (ValueError, IndexError):
                pass
        
        # Check for known city names
        city_lower = location.lower().strip()
        if city_lower in KNOWN_CITIES:
            lat, lon = KNOWN_CITIES[city_lower]
            return lat, lon, location.title()
        
        # Default to Hof if unknown
        return 50.3167, 11.9167, f"{location} (unknown, using Hof)"

    class SubjectiveTimeHandler(http.server.BaseHTTPRequestHandler):
        def _send_text(self, status_code: int, text: str):
            """Send plain text response."""
            self.send_response(status_code)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(text.encode('utf-8'))
        
        def _send_json(self, status_code: int, data: dict):
            """Send JSON response."""
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_module.dumps(data, indent=2).encode())
        
        def do_GET(self):
            # Parse URL
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            path = parsed.path
            
            # Get format parameter
            fmt = query.get('format', [''])[0].lower()
            
            # Get system parameter (große/kleine Uhr)
            system_param = query.get('system', query.get('uhr', ['kleine']))[0].lower()
            
            try:
                # Handle special pages
                if path in ['/:help', '/help', '/:h']:
                    self._send_text(200, get_help_text())
                    return
                
                if path in ['/:about', '/about']:
                    self._send_text(200, get_about_text())
                    return
                
                if path in ['/:learn', '/learn', '/:tutorial']:
                    self._send_text(200, get_learn_text())
                    return
                
                if path in ['/:nocturnal', '/nocturnal', '/:stars']:
                    # Parse optional location from query
                    lat_param = query.get('lat', ['50.3167'])[0]
                    lon_param = query.get('lon', ['11.9167'])[0]
                    try:
                        lat = float(lat_param)
                        lon = float(lon_param)
                    except ValueError:
                        lat, lon = 50.3167, 11.9167
                    self._send_text(200, get_nocturnal_text(lat, lon))
                    return
                
                # Parse location from path
                lat, lon, location_name = parse_location(path)
                
                # Validate coordinates
                if not -90 <= lat <= 90:
                    self._send_text(400, f"Error: Invalid latitude {lat} (must be -90 to 90)\n")
                    return
                if not -180 <= lon <= 180:
                    self._send_text(400, f"Error: Invalid longitude {lon} (must be -180 to 180)\n")
                    return
                
                # Calculate subjective time with selected system
                uhr = SubjectiveTime(lat, lon, system=system_param)
                
                # Handle different formats
                if fmt in ['j', 'json']:
                    result = uhr.get_subjective_day()
                    self._send_json(200, result)
                elif fmt in ['1', 'oneline', 'one']:
                    result = uhr.get_subjective_day()
                    self._send_text(200, format_one_line(result))
                elif fmt in ['table', 't', 'hours']:
                    day_hours = uhr.get_full_day_hours()
                    self._send_text(200, format_table(day_hours, location_name))
                elif fmt in ['w', 'watch', 'complication']:
                    # Smartwatch-optimized minimal JSON
                    result = uhr.get_subjective_day()
                    watch_data = get_watch_data(result)
                    self._send_json(200, watch_data)
                else:
                    # Default: plain text ASCII art
                    result = uhr.get_subjective_day()
                    self._send_text(200, format_plain_text(result, location_name))
                
            except ValueError as e:
                self._send_text(400, f"Error: {str(e)}\n")
            except Exception:
                import traceback
                traceback.print_exc()
                self._send_text(500, "Error: Internal server error\n")
        
        def do_OPTIONS(self):
            """Handle CORS preflight requests."""
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        
        def log_message(self, format, *args):
            """Override to show cleaner log messages."""
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🕐 Subjective Day - Nürnberger Uhr API                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Server running at: http://{host}:{port}/                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Usage (like wttr.in):                                                        ║
║                                                                               ║
║    curl {host}:{port}/                      # Default (Hof)                      ║
║    curl {host}:{port}/Berlin                # City name                          ║
║    curl {host}:{port}/52.52,13.40           # Coordinates                        ║
║    curl {host}:{port}/munich?format=j       # JSON output                        ║
║    curl {host}:{port}/hof?format=1          # One-line (for scripts)             ║
║    curl {host}:{port}/nuremberg?format=table # Hour table                        ║
║    curl {host}:{port}/:help                 # Help page                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")
    
    server = http.server.HTTPServer((host, port), SubjectiveTimeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == '__main__':
    import sys
    
    # If run with --serve, start the API server
    if '--serve' in sys.argv:
        host = '127.0.0.1'
        port = 8080
        
        # Parse optional host/port
        for i, arg in enumerate(sys.argv):
            if arg == '--host' and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
            if arg == '--port' and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        
        run_api_server(host, port)
    else:
        # Demo mode
        print("=" * 60)
        print("Nürnberger Uhr - Subjective Time Calculator")
        print("=" * 60)
        
        # Example locations
        locations = [
            ("Hof, Germany", 50.3167, 11.9167),
            ("Nuremberg, Germany", 49.4521, 11.0767),
            ("Berlin, Germany", 52.5200, 13.4050),
            ("Munich, Germany", 48.1351, 11.5820),
        ]
        
        now = datetime.now()
        print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for name, lat, lon in locations:
            uhr = SubjectiveTime(lat, lon)
            result = uhr.get_subjective_day(now)
            
            print(f"📍 {name} ({lat}°N, {lon}°E)")
            print(f"   ☀️ Sunrise: {result['sunrise']} | Sunset: {result['sunset']}")
            print(f"   🕐 {result['display_en']}")
            print(f"   🕐 {result['display_de']}")
            print(f"   ⏱️ Day hour: {result['day_hour_length_minutes']:.1f} min | Night hour: {result['night_hour_length_minutes']:.1f} min")
            print()
        
        print("-" * 60)
        print("To start the API server: python3 src/modules/subjective_day.py --serve")
        print("To specify host/port: --host 0.0.0.0 --port 8000")
