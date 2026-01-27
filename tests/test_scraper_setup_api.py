#!/usr/bin/env python3
"""
Tests for the Scraper Setup API module.

Tests URL analysis, configuration generation, and validation.
"""

import json
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.scraper_setup_api import ScraperSetupAPI


class TestScraperSetupAPI(unittest.TestCase):
    """Tests for ScraperSetupAPI class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.base_path = Path(__file__).parent.parent
        cls.api = ScraperSetupAPI(cls.base_path)
    
    def test_schema_fields_defined(self):
        """Test that all required schema fields are defined."""
        fields = self.api.get_schema_fields()
        
        # Check required fields exist
        self.assertIn('title', fields)
        self.assertIn('location_name', fields)
        self.assertIn('start_date', fields)
        
        # Check field structure
        for field_name, field_info in fields.items():
            self.assertIn('type', field_info)
            self.assertIn('required', field_info)
            self.assertIn('description', field_info)
            self.assertIn('selectors', field_info)
    
    def test_generate_ci_config_structure(self):
        """Test CI configuration generation."""
        field_mappings = {
            'title': {'selector': '.event-title', 'extraction_method': 'text'},
            'location_name': {'selector': '.venue', 'extraction_method': 'text'},
            'start_date': {'selector': '.date', 'extraction_method': 'datetime'}
        }
        
        config = self.api.generate_ci_config(
            source_name='TestSource',
            url='https://example.com/events',
            field_mappings=field_mappings,
            container_selector='.event'
        )
        
        # Check structure
        self.assertEqual(config['version'], '2.0')
        self.assertIn('source', config)
        self.assertIn('field_mappings', config)
        self.assertIn('metadata', config)
        
        # Check source
        self.assertEqual(config['source']['name'], 'TestSource')
        self.assertEqual(config['source']['url'], 'https://example.com/events')
        self.assertEqual(config['source']['type'], 'html')
        
        # Check field mappings
        self.assertIn('title', config['field_mappings'])
        self.assertEqual(config['field_mappings']['title']['selector'], '.event-title')
    
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        valid_config = {
            'source': {
                'name': 'TestSource',
                'url': 'https://example.com'
            },
            'field_mappings': {
                'title': {'selector': 'h1'},
                'location_name': {'selector': '.venue'},
                'start_date': {'selector': '.date'}
            }
        }
        
        is_valid, errors = self.api.validate_config(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_config_missing_source(self):
        """Test validation fails when source is missing."""
        invalid_config = {
            'field_mappings': {
                'title': {'selector': 'h1'}
            }
        }
        
        is_valid, errors = self.api.validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'source' section", errors)
    
    def test_validate_config_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        incomplete_config = {
            'source': {
                'name': 'TestSource',
                'url': 'https://example.com'
            },
            'field_mappings': {
                'title': {'selector': 'h1'}
                # Missing location_name and start_date
            }
        }
        
        is_valid, errors = self.api.validate_config(incomplete_config)
        self.assertFalse(is_valid)
        self.assertTrue(any('location_name' in e for e in errors))
        self.assertTrue(any('start_date' in e for e in errors))
    
    def test_event_container_selectors_defined(self):
        """Test that event container selectors are defined."""
        selectors = self.api.EVENT_CONTAINER_SELECTORS
        
        self.assertIsInstance(selectors, list)
        self.assertGreater(len(selectors), 0)
        
        # Check for common selectors
        selector_str = ' '.join(selectors)
        self.assertIn('.event', selector_str)
        self.assertIn('article', selector_str)
    
    def test_list_saved_configs_returns_list(self):
        """Test that listing configs returns a list."""
        configs = self.api.list_saved_configs()
        self.assertIsInstance(configs, list)
    
    def test_analyze_url_without_network(self):
        """Test URL analysis handles missing libraries gracefully."""
        # This test runs whether scraping libraries are available or not
        result = self.api.analyze_url('https://example.com')
        
        # Should return a dict with success or error
        self.assertIsInstance(result, dict)
        self.assertIn('url', result)


class TestConfigFileFormat(unittest.TestCase):
    """Tests for configuration file format."""
    
    def test_example_config_structure(self):
        """Test that example config structure is documented correctly."""
        example_config = {
            "version": "2.0",
            "source": {
                "name": "example_source",
                "url": "https://example.com/events",
                "type": "html",
                "enabled": True
            },
            "container": {
                "selector": ".event"
            },
            "field_mappings": {
                "title": {
                    "selector": ".event-title",
                    "extraction": "text",
                    "required": True
                },
                "location_name": {
                    "selector": ".venue",
                    "extraction": "text",
                    "required": True
                },
                "start_date": {
                    "selector": ".date",
                    "extraction": "datetime",
                    "required": True
                }
            },
            "metadata": {
                "created_at": "2025-01-27T19:00:00Z",
                "created_by": "scraper-setup-tool"
            }
        }
        
        # Validate structure
        self.assertIn('version', example_config)
        self.assertIn('source', example_config)
        self.assertIn('field_mappings', example_config)
        
        # Validate can be serialized to JSON
        json_str = json.dumps(example_config)
        parsed = json.loads(json_str)
        self.assertEqual(parsed, example_config)


def run_tests():
    """Run all tests and print summary."""
    print("=" * 60)
    print("Scraper Setup API Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestScraperSetupAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigFileFormat))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
