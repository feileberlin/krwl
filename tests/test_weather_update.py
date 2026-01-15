#!/usr/bin/env python3
"""Test fast weather update functionality

This test verifies that weather data can be updated in existing HTML
without triggering a full site rebuild.
"""

import sys
import unittest
import json
import tempfile
import shutil
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.site_generator import SiteGenerator
from modules.utils import load_config


class TestWeatherUpdate(unittest.TestCase):
    """Test fast weather update functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = Path(__file__).parent.parent
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Copy necessary files to temp directory
        self.test_public_dir = self.temp_dir / 'public'
        self.test_public_dir.mkdir()
        self.test_assets_dir = self.temp_dir / 'assets' / 'json'
        self.test_assets_dir.mkdir(parents=True)
        
        # Create a minimal HTML with APP_CONFIG
        self.test_html = self.test_public_dir / 'index.html'
        self.test_weather_cache = self.test_assets_dir / 'weather_cache.json'
        
        # Create initial HTML with weather data
        initial_weather_data = {
            "dresscode": "Light jacket",
            "temperature": "15°C",
            "location": "Test City",
            "timestamp": "2026-01-15T12:00:00.000000"
        }
        
        app_config = {
            "debug": False,
            "weather": {
                "enabled": True,
                "display": {"show_in_filter_bar": True},
                "data": initial_weather_data
            }
        }
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script>
window.APP_CONFIG = {json.dumps(app_config, indent=2)};
</script>
</body>
</html>"""
        
        with open(self.test_html, 'w') as f:
            f.write(html_content)
        
        # Create weather cache with updated data
        updated_weather = {
            "coords_50.3167_11.9167": {
                "timestamp": "2026-01-15T14:00:00.000000",
                "data": {
                    "dresscode": "Warm coat",
                    "temperature": "5°C",
                    "location": "Test City",
                    "timestamp": "2026-01-15T14:00:00.000000"
                }
            }
        }
        
        with open(self.test_weather_cache, 'w') as f:
            json.dump(updated_weather, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_weather_update_updates_html(self):
        """Test that weather data is updated in HTML"""
        # Create generator with test path
        generator = SiteGenerator(self.temp_dir)
        
        # Update weather
        result = generator.update_weather_data()
        
        # Verify update succeeded
        self.assertTrue(result, "Weather update should succeed")
        
        # Read updated HTML
        with open(self.test_html, 'r') as f:
            html = f.read()
        
        # Parse APP_CONFIG
        match = re.search(r'window\.APP_CONFIG\s*=\s*(\{.+?\});', html, re.DOTALL)
        self.assertIsNotNone(match, "APP_CONFIG should be found in HTML")
        
        config = json.loads(match.group(1))
        
        # Verify weather data was updated
        self.assertIn('weather', config)
        self.assertIn('data', config['weather'])
        self.assertEqual(config['weather']['data']['dresscode'], 'Warm coat')
        self.assertEqual(config['weather']['data']['temperature'], '5°C')
    
    def test_weather_update_preserves_other_config(self):
        """Test that updating weather preserves other config fields"""
        # Create generator
        generator = SiteGenerator(self.temp_dir)
        
        # Update weather
        generator.update_weather_data()
        
        # Read updated HTML
        with open(self.test_html, 'r') as f:
            html = f.read()
        
        # Parse APP_CONFIG
        match = re.search(r'window\.APP_CONFIG\s*=\s*(\{.+?\});', html, re.DOTALL)
        config = json.loads(match.group(1))
        
        # Verify other fields are preserved
        self.assertIn('debug', config)
        self.assertEqual(config['debug'], False)
        self.assertIn('weather', config)
        self.assertEqual(config['weather']['enabled'], True)
    
    def test_weather_update_fails_without_html(self):
        """Test that weather update fails gracefully without HTML"""
        # Remove HTML file
        self.test_html.unlink()
        
        # Create generator
        generator = SiteGenerator(self.temp_dir)
        
        # Update should fail
        result = generator.update_weather_data()
        self.assertFalse(result, "Weather update should fail without HTML")
    
    def test_weather_update_fails_without_cache(self):
        """Test that weather update fails gracefully without cache"""
        # Remove weather cache
        self.test_weather_cache.unlink()
        
        # Create generator
        generator = SiteGenerator(self.temp_dir)
        
        # Update should fail
        result = generator.update_weather_data()
        self.assertFalse(result, "Weather update should fail without weather cache")


def run_tests(verbose=False):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWeatherUpdate)
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test weather update functionality')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    success = run_tests(verbose=args.verbose)
    sys.exit(0 if success else 1)
