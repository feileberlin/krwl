"""
Nürnberger Uhr (Nuremberg Clock) - Subjective Time Calculator

This module implements the historical "Nürnberger Uhr" timekeeping system,
which uses "unequal hours" (temporal hours) based on sunrise and sunset.

Historical Background:
- Used in Nuremberg and other medieval cities
- Day is divided into 12 equal "day hours" (sunrise to sunset)
- Night is divided into 12 equal "night hours" (sunset to sunrise)
- Hour length varies throughout the year (longer summer days, shorter winter days)
- In Nuremberg's latitude, day hours range from ~42-45 min (winter) to ~77-80 min (summer)

API Usage:
- Local CLI: python3 src/event_manager.py subjective-time --lat 50.3167 --lon 11.9167
- HTTP API: GET /api/subjective-time?lat=50.3167&lon=11.9167
- Python: from src.modules.subjective_day import SubjectiveTime

References:
- https://de.wikipedia.org/wiki/Nürnberger_Uhr
- https://nuernberginfos.de/nuernberg-mix/nuernberger-uhr.php
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
    
    def __init__(self, lat: float, lon: float, tz_offset_hours: float = None):
        """
        Initialize the Nürnberger Uhr calculator.
        
        Args:
            lat: Latitude in decimal degrees (positive = North, range: -90 to 90)
            lon: Longitude in decimal degrees (positive = East, range: -180 to 180)
            tz_offset_hours: Timezone offset from UTC in hours (auto-detected if None)
        
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
        if sunrise <= dt < sunset:
            # Daytime
            is_day = True
            period = "Tag"
            period_en = "day"
            
            # Calculate position within day
            day_length = (sunset - sunrise).total_seconds()
            elapsed = (dt - sunrise).total_seconds()
            
            # Each day hour
            hour_length = day_length / 12
            
            # Current hour (1-12)
            hour_float = elapsed / hour_length
            hour = int(hour_float) + 1
            if hour > 12:
                hour = 12
            
            # Minutes within hour (scaled to 0-59)
            minute_fraction = hour_float - int(hour_float)
            minute = int(minute_fraction * 60)
            
            hour_length_minutes = hour_length / 60
            
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
            
            # Each night hour
            hour_length = night_length / 12
            
            # Current hour (1-12)
            hour_float = elapsed / hour_length
            hour = int(hour_float) + 1
            if hour > 12:
                hour = 12
            
            # Minutes within hour (scaled to 0-59)
            minute_fraction = hour_float - int(hour_float)
            minute = int(minute_fraction * 60)
            
            hour_length_minutes = hour_length / 60
        
        # Generate ordinal suffix for English
        ordinal_suffix = self._get_ordinal_suffix(hour)
        
        # Build result
        return {
            'polar': False,
            'is_day': is_day,
            'hour': hour,
            'minute': minute,
            'hour_length_minutes': round(hour_length_minutes, 2),
            'period': period,
            'period_en': period_en,
            'display': f"{hour}. Stunde des {period}s",
            'display_de': f"{hour}. Stunde des {period}s ({hour_length_minutes:.1f} min/Std)",
            'display_en': f"{hour}{ordinal_suffix} hour of {period_en} ({hour_length_minutes:.1f} min/hr)",
            'time_formatted': f"{hour}:{minute:02d}",
            'timestamp': dt.isoformat(),
            'location': {'lat': self.lat, 'lon': self.lon},
            'sunrise': sunrise.strftime('%H:%M'),
            'sunset': sunset.strftime('%H:%M'),
            'day_hour_length_minutes': round(sun_data['day_hour_length_minutes'], 2),
            'night_hour_length_minutes': round(sun_data['night_hour_length_minutes'], 2)
        }
    
    def _get_ordinal_suffix(self, n: int) -> str:
        """Get English ordinal suffix for a number."""
        if 11 <= n <= 13:
            return 'th'
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    
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
    Run a simple HTTP API server for subjective time.
    
    Endpoints:
    - GET /api/subjective-time?lat=<lat>&lon=<lon>
    - GET /api/sunrise-sunset?lat=<lat>&lon=<lon>
    - GET /api/day-hours?lat=<lat>&lon=<lon>
    
    Args:
        host: Host to bind to (default: 127.0.0.1 for local only)
        port: Port to listen on (default: 8080)
    """
    import http.server
    import urllib.parse
    import json as json_module
    
    class SubjectiveTimeHandler(http.server.BaseHTTPRequestHandler):
        def _send_response(self, status_code: int, data: dict):
            """Send JSON response with appropriate headers."""
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json_module.dumps(data, indent=2).encode())
        
        def _send_error(self, status_code: int, message: str):
            """Send error response."""
            self._send_response(status_code, {'error': message})
        
        def do_GET(self):
            # Parse URL
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            
            try:
                # Get and validate coordinates from query params
                try:
                    lat = float(query.get('lat', [50.3167])[0])  # Default: Hof
                    lon = float(query.get('lon', [11.9167])[0])
                except (ValueError, TypeError):
                    self._send_error(400, "Invalid coordinates: lat and lon must be numbers")
                    return
                
                # Validate coordinate ranges
                if not -90 <= lat <= 90:
                    self._send_error(400, f"Invalid latitude: must be between -90 and 90, got {lat}")
                    return
                if not -180 <= lon <= 180:
                    self._send_error(400, f"Invalid longitude: must be between -180 and 180, got {lon}")
                    return
                
                uhr = SubjectiveTime(lat, lon)
                
                if parsed.path == '/api/subjective-time':
                    result = uhr.get_subjective_day()
                elif parsed.path == '/api/sunrise-sunset':
                    result = uhr.get_sunrise_sunset()
                    # Convert datetime objects to strings
                    if result.get('sunrise'):
                        result['sunrise'] = result['sunrise'].strftime('%H:%M:%S')
                    if result.get('sunset'):
                        result['sunset'] = result['sunset'].strftime('%H:%M:%S')
                elif parsed.path == '/api/day-hours':
                    result = uhr.get_full_day_hours()
                elif parsed.path == '/api/health':
                    result = {'status': 'ok', 'service': 'nuernberger-uhr'}
                else:
                    self._send_error(404, 'Unknown endpoint. Available: /api/subjective-time, /api/sunrise-sunset, /api/day-hours, /api/health')
                    return
                
                self._send_response(200, result)
                
            except ValueError as e:
                # Validation errors (e.g., invalid coordinates)
                self._send_error(400, str(e))
            except Exception:
                # Log internally but don't expose details to client
                import traceback
                traceback.print_exc()
                self._send_error(500, "Internal server error")
        
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
╔═══════════════════════════════════════════════════════════════╗
║              Nürnberger Uhr - Subjective Time API             ║
╠═══════════════════════════════════════════════════════════════╣
║  Server running at: http://{host}:{port}                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Endpoints:                                                   ║
║    GET /api/subjective-time?lat=50.3&lon=11.9                ║
║    GET /api/sunrise-sunset?lat=50.3&lon=11.9                 ║
║    GET /api/day-hours?lat=50.3&lon=11.9                      ║
║    GET /api/health                                            ║
╠═══════════════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                                         ║
╚═══════════════════════════════════════════════════════════════╝
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
