"""
Weather Calculator - KISS Implementation

Simple dresscode calculator using Open-Meteo free API.
Generates 3-word dresscode based on feels-like temperature.
Updated twice daily (12-hour cache).
"""

import os
import json
import requests
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)


class WeatherCalculator:
    """Simple weather dresscode calculator."""
    
    def __init__(self, base_path=None, config=None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config = config or {}
        
        # Paths
        json_dir = os.path.join(self.base_path, 'assets', 'json')
        self.cache_file = os.path.join(json_dir, 'weather_cache.json')
        
        # Config
        weather_config = self.config.get('weather', {})
        self.cache_hours = weather_config.get('cache_hours', 12)  # Twice daily
        self.timeout = weather_config.get('timeout', 10)
        self.max_retries = weather_config.get('max_retries', 3)
        self.retry_delay_base = weather_config.get('retry_delay_base', 1.0)
    
    def get_weather(self, location_name=None, lat=None, lon=None, force_refresh=False):
        """Get weather dresscode, using cache if available."""
        # Check cache
        if not force_refresh:
            cached = self._get_from_cache(location_name, lat, lon)
            if cached:
                return cached
        
        # Calculate fresh dresscode
        weather_data = self._calculate_dresscode(location_name, lat, lon)
        
        # Save to cache
        if weather_data:
            self._save_to_cache(location_name, lat, lon, weather_data)
        
        return weather_data
    
    def _calculate_dresscode(self, location_name, lat=None, lon=None):
        """Calculate dresscode from weather API."""
        for attempt in range(self.max_retries):
            try:
                # Get weather from Open-Meteo (free, no API key)
                weather = self._fetch_weather(lat, lon)
                if not weather:
                    continue
                
                # Extract feels-like temperature and rain
                current = weather.get('current', {})
                feels_like = current.get('apparent_temperature', current.get('temperature_2m', 15))
                rain = current.get('rain', 0)
                temp = current.get('temperature_2m', feels_like)
                
                # Generate simple 3-word dresscode
                dresscode = self._simple_dresscode(feels_like, rain)
                
                return {
                    'dresscode': dresscode,
                    'temperature': f"{round(temp)}°C",
                    'location': location_name,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay_base * (2 ** attempt))
        
        # Fallback dresscode when no data available
        logger.warning("No weather data available, using fallback dresscode")
        return {
            'dresscode': 'remind the weather',
            'temperature': '?°C',
            'location': location_name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fetch_weather(self, lat, lon):
        """Fetch weather from Open-Meteo API."""
        if not lat or not lon:
            lat, lon = 50.3167, 11.9167  # Default: Hof
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,apparent_temperature,rain',
            'timezone': 'auto'
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def _simple_dresscode(self, feels_like, rain):
        """Generate 3-word dresscode from feels-like temp and rain."""
        # Rain takes priority
        if rain > 0:
            if feels_like < 10:
                return "warm rain jacket"
            else:
                return "light rain jacket"
        
        # Temperature-based (simple thresholds)
        if feels_like < 0:
            return "heavy winter coat"
        elif feels_like < 10:
            return "warm jacket needed"
        elif feels_like < 15:
            return "light jacket recommended"
        elif feels_like < 20:
            return "sweater or cardigan"
        elif feels_like < 25:
            return "light summer clothes"
        else:
            # Hot weather - sun protection
            return "sunscreen and shade"
    
    def _get_from_cache(self, location_name, lat, lon):
        """Get weather from cache if valid."""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # Find matching entry
            key = self._cache_key(location_name, lat, lon)
            entry = cache.get(key)
            
            if not entry:
                return None
            
            # Check if expired
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time >= timedelta(hours=self.cache_hours):
                return None
            
            return entry['data']
        except Exception as e:
            logger.error(f"Cache read failed: {e}")
            return None
    
    def _save_to_cache(self, location_name, lat, lon, weather_data):
        """Save weather to cache."""
        try:
            # Load existing cache
            cache = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            # Add/update entry
            key = self._cache_key(location_name, lat, lon)
            cache[key] = {
                'timestamp': datetime.now().isoformat(),
                'data': weather_data
            }
            
            # Save
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Cache save failed: {e}")
    
    def _cache_key(self, location_name, lat, lon):
        """Generate cache key."""
        if location_name:
            return f"location_{location_name}"
        elif lat and lon:
            lat_rounded = round(float(lat), 4)
            lon_rounded = round(float(lon), 4)
            return f"coords_{lat_rounded}_{lon_rounded}"
        return "default"
