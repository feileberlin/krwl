#!/usr/bin/env python3
"""Test weather calculator resilience and retry logic

This test verifies that the weather calculator handles network failures gracefully
with retry logic and proper fallback to cached data.
"""

import sys
import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.weather_calculator import WeatherCalculator


class TestWeatherCalculatorResilience(unittest.TestCase):
    """Test weather calculator resilience to network failures"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = Path(__file__).parent.parent
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create necessary directories
        self.test_assets_dir = self.temp_dir / 'assets' / 'json'
        self.test_assets_dir.mkdir(parents=True)
        
        # Create test config with retry settings
        self.test_config = {
            'weather': {
                'enabled': True,
                'cache_hours': 1,
                'timeout': 5,
                'max_retries': 3,
                'retry_delay_base': 0.1  # Fast retries for testing
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_retry_on_timeout(self):
        """Test that calculator retries on timeout errors"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Mock Open-Meteo API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 10.0,
                "apparent_temperature": 8.0,
                "rain": 0.0,
                "wind_speed_10m": 10.0,
                "weather_code": 0
            }
        }
        
        call_count = [0]
        
        def mock_get(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise requests.exceptions.Timeout("Connection timeout")
            return mock_response
        
        with patch('requests.get', side_effect=mock_get):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should succeed on third attempt
            self.assertIsNotNone(result)
            self.assertIn('jacket', result['dresscode'].lower())
            self.assertEqual(call_count[0], 3)
    
    def test_retry_on_connection_error(self):
        """Test that calculator retries on connection errors"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Mock requests to fail with connection error
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection refused")):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should return fallback dresscode after all retries exhausted
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'remind the weather')
    
    def test_fallback_to_cache_on_failure(self):
        """Test that calculator falls back to cache when fresh calculation fails"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Create cache with valid, recent data (within cache window)
        from datetime import datetime, timedelta
        recent_time = datetime.now() - timedelta(minutes=30)  # 30 mins ago, within 1 hour cache
        
        cache_data = {
            "location_Test City": {
                "timestamp": recent_time.isoformat(),
                "data": {
                    "dresscode": "warm jacket needed",
                    "temperature": "5°C",
                    "location": "Test City",
                    "timestamp": recent_time.isoformat()
                }
            }
        }
        cache_file = self.test_assets_dir / 'weather_cache.json'
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        # Mock requests to fail
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection refused")):
            # Should return cached data
            result = calculator.get_weather("Test City", 50.0, 11.0)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'warm jacket needed')
            self.assertEqual(result['temperature'], '5°C')
    
    def test_no_infinite_retry(self):
        """Test that calculator doesn't retry indefinitely"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        call_count = [0]
        
        def mock_get(*args, **kwargs):
            call_count[0] += 1
            raise requests.exceptions.Timeout("Timeout")
        
        with patch('requests.get', side_effect=mock_get):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should return fallback after max_retries attempts
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'remind the weather')
            self.assertEqual(call_count[0], self.test_config['weather']['max_retries'])
    
    def test_http_error_handling(self):
        """Test that calculator handles HTTP errors properly"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        
        with patch('requests.get', return_value=mock_response):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should return fallback dresscode
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'remind the weather')
    
    def test_dresscode_generation_from_open_meteo(self):
        """Test that calculator generates correct dresscode from Open-Meteo JSON data"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Mock Open-Meteo API response with temperature/rain data for ~10°C and no rain
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 10.0,
                "apparent_temperature": 9.0,
                "rain": 0.0,
                "wind_speed_10m": 15.0,
                "weather_code": 0
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should successfully compute a warm-jacket-style dresscode from the JSON data
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'warm jacket needed')
            self.assertEqual(result['temperature'], '10°C')
    
    def test_extreme_weather_detection(self):
        """Test that calculator detects extreme weather conditions"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Test extreme cold
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": -20.0,
                "apparent_temperature": -25.0,
                "rain": 0.0,
                "wind_speed_10m": 10.0,
                "weather_code": 0
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = calculator._calculate_dresscode("Test City", 50.0, 11.0)
            
            # Should warn to stay indoors
            self.assertEqual(result['dresscode'], 'better watch TV')
    
    def test_fallback_dresscode_when_api_unavailable(self):
        """Test that calculator returns fallback dresscode when API is completely unavailable"""
        calculator = WeatherCalculator(self.temp_dir, self.test_config)
        
        # Mock complete API failure
        with patch('requests.get', side_effect=requests.exceptions.ConnectionError("No connection")):
            result = calculator.get_weather("Test City", 50.0, 11.0, force_refresh=True)
            
            # Should return fallback dresscode
            self.assertIsNotNone(result)
            self.assertEqual(result['dresscode'], 'remind the weather')
            self.assertEqual(result['temperature'], '?°C')


def run_tests(verbose=False):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWeatherCalculatorResilience)
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test weather calculator resilience')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    success = run_tests(verbose=args.verbose)
    sys.exit(0 if success else 1)
