"""
Test suite for Jinja2 template helper module.

Tests the JSON templating functionality using Jinja2 library.
"""

import json
import sys
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.jinja2_helper import (
    Jinja2TemplateHelper,
    render_json_template,
    is_jinja2_available
)


class TestJinja2Helper(unittest.TestCase):
    """Test cases for Jinja2TemplateHelper class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.base_path = Path(__file__).parent.parent
        cls.helper = Jinja2TemplateHelper(cls.base_path)
    
    def test_jinja2_available(self):
        """Test that Jinja2 library is available."""
        self.assertTrue(is_jinja2_available())
    
    def test_list_templates(self):
        """Test listing available templates."""
        templates = self.helper.list_templates()
        
        # Should have our core templates
        self.assertIn('runtime_config_base', templates)
        self.assertIn('time_filters', templates)
        self.assertIn('weather_config', templates)
    
    def test_render_runtime_config_base(self):
        """Test rendering runtime_config_base template."""
        result = self.helper.render(
            'runtime_config_base',
            debug_enabled=True,
            environment='development',
            map_config={'zoom': 13},
            data_source='both',
            data_sources={'real': {}, 'demo': {}}
        )
        
        # Check structure
        self.assertIn('debug', result)
        self.assertIn('app', result)
        self.assertIn('map', result)
        self.assertIn('data', result)
        
        # Check values
        self.assertTrue(result['debug'])
        self.assertEqual(result['app']['environment'], 'development')
        self.assertEqual(result['data']['source'], 'both')
    
    def test_render_time_filters(self):
        """Test rendering time_filters template."""
        result = self.helper.render(
            'time_filters',
            days_until_full_moon=15,
            full_moon_enabled=True,
            days_until_sunday=3,
            sunday_date_iso='2026-01-18',
            sunday_date_formatted='January 18',
            sunday_enabled=True
        )
        
        # Check structure
        self.assertIn('full_moon', result)
        self.assertIn('sunday', result)
        
        # Check values
        self.assertEqual(result['full_moon']['days_until'], 15)
        self.assertTrue(result['full_moon']['enabled'])
        self.assertEqual(result['sunday']['date_iso'], '2026-01-18')
    
    def test_render_weather_config(self):
        """Test rendering weather_config template."""
        weather_data = {'temperature': '15°C', 'dresscode': 'Light jacket'}
        
        result = self.helper.render(
            'weather_config',
            weather_enabled=True,
            display_config={'show_in_filter_bar': True},
            weather_data=weather_data
        )
        
        # Check structure
        self.assertIn('enabled', result)
        self.assertIn('display', result)
        self.assertIn('data', result)
        
        # Check values
        self.assertTrue(result['enabled'])
        self.assertEqual(result['data']['temperature'], '15°C')
    
    def test_render_string_simple(self):
        """Test rendering a simple inline template."""
        template = '{"name": "{{ app_name }}", "count": {{ event_count }}}'
        
        result = self.helper.render_string(
            template,
            app_name='Test App',
            event_count=42
        )
        
        self.assertEqual(result['name'], 'Test App')
        self.assertEqual(result['count'], 42)
    
    def test_render_string_boolean(self):
        """Test rendering template with boolean values."""
        template = '{"enabled": {{ is_enabled | tojson }}, "disabled": {{ is_disabled | tojson }}}'
        
        result = self.helper.render_string(
            template,
            is_enabled=True,
            is_disabled=False
        )
        
        self.assertTrue(result['enabled'])
        self.assertFalse(result['disabled'])
    
    def test_render_string_nested(self):
        """Test rendering template with nested objects."""
        template = '{"outer": {{ inner_value | tojson }}}'
        
        result = self.helper.render_string(
            template,
            inner_value={'key': 'value'}
        )
        
        self.assertEqual(result['outer']['key'], 'value')
    
    def test_template_not_found(self):
        """Test error handling for missing templates."""
        with self.assertRaises(FileNotFoundError):
            self.helper.render('nonexistent_template')


class TestJinja2Conditionals(unittest.TestCase):
    """Test Jinja2's conditional capabilities (power over jsonplate)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.base_path = Path(__file__).parent.parent
        cls.helper = Jinja2TemplateHelper(cls.base_path)
    
    def test_conditional_inclusion(self):
        """Test conditional content inclusion."""
        template = '''
{
    "base": "value"{% if include_extra %},
    "extra": {{ extra_data | tojson }}{% endif %}
}
'''
        # With extra
        result = self.helper.render_string(
            template,
            include_extra=True,
            extra_data={'key': 'value'}
        )
        self.assertIn('extra', result)
        
        # Without extra
        result = self.helper.render_string(
            template,
            include_extra=False,
            extra_data={}
        )
        self.assertNotIn('extra', result)


class TestJinja2Loops(unittest.TestCase):
    """Test Jinja2's loop capabilities (power over jsonplate)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.base_path = Path(__file__).parent.parent
        cls.helper = Jinja2TemplateHelper(cls.base_path)
    
    def test_simple_loop(self):
        """Test simple list loop."""
        template = '''
{
    "items": [{% for item in items %}
        {{ item | tojson }}{% if not loop.last %},{% endif %}{% endfor %}
    ]
}
'''
        result = self.helper.render_string(
            template,
            items=['apple', 'banana', 'cherry']
        )
        self.assertEqual(result['items'], ['apple', 'banana', 'cherry'])
    
    def test_object_loop(self):
        """Test loop with objects."""
        template = '''
{
    "events": [{% for event in events %}
        {"name": "{{ event.name }}", "id": {{ event.id }}}{% if not loop.last %},{% endif %}{% endfor %}
    ]
}
'''
        result = self.helper.render_string(
            template,
            events=[
                {'name': 'Event A', 'id': 1},
                {'name': 'Event B', 'id': 2}
            ]
        )
        self.assertEqual(len(result['events']), 2)
        self.assertEqual(result['events'][0]['name'], 'Event A')


class TestRenderJsonTemplateFunction(unittest.TestCase):
    """Test cases for render_json_template convenience function."""
    
    def test_simple_template(self):
        """Test simple template rendering."""
        result = render_json_template(
            '{"key": "{{ value }}"}',
            value='test'
        )
        
        self.assertEqual(result['key'], 'test')
    
    def test_numeric_values(self):
        """Test template with numeric values."""
        result = render_json_template(
            '{"count": {{ num }}, "ratio": {{ ratio_val }}}',
            num=42,
            ratio_val=3.14
        )
        
        self.assertEqual(result['count'], 42)
        self.assertAlmostEqual(result['ratio'], 3.14)
    
    def test_null_value(self):
        """Test template with null value passed as object."""
        result = render_json_template(
            '{"data": {{ data_value | tojson }}}',
            data_value=None
        )
        
        self.assertIsNone(result['data'])


class TestSiteGeneratorIntegration(unittest.TestCase):
    """Integration tests with SiteGenerator."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.base_path = Path(__file__).parent.parent
        sys.path.insert(0, str(cls.base_path / 'src'))
    
    def test_site_generator_jinja2_method(self):
        """Test SiteGenerator.build_runtime_config_with_jinja2 method."""
        from modules.site_generator import SiteGenerator
        
        gen = SiteGenerator(self.base_path)
        
        # Test with minimal config
        primary_config = {
            'debug': True,
            'app': {'environment': 'test'},
            'map': {'zoom': 13},
            'data': {'source': 'demo', 'sources': {}},
            'weather': {'enabled': False}
        }
        
        result = gen.build_runtime_config_with_jinja2(primary_config, None)
        
        # Verify basic structure
        self.assertIn('debug', result)
        self.assertIn('app', result)
        self.assertIn('map', result)
        self.assertIn('data', result)
        self.assertIn('weather', result)
        self.assertIn('time_filters', result)
        
        # Verify values
        self.assertTrue(result['debug'])
        self.assertEqual(result['app']['environment'], 'test')
        self.assertEqual(result['data']['source'], 'demo')
        self.assertFalse(result['weather']['enabled'])
    
    def test_site_generator_with_weather(self):
        """Test SiteGenerator with weather enabled."""
        from modules.site_generator import SiteGenerator
        
        gen = SiteGenerator(self.base_path)
        
        primary_config = {
            'debug': False,
            'app': {'environment': 'production'},
            'map': {},
            'data': {'source': 'real', 'sources': {}},
            'weather': {
                'enabled': True,
                'display': {'show_in_filter_bar': True}
            }
        }
        
        weather_cache = {
            'hof': {
                'data': {
                    'temperature': '10°C',
                    'dresscode': 'Warm jacket'
                }
            }
        }
        
        result = gen.build_runtime_config_with_jinja2(primary_config, weather_cache)
        
        # Verify weather is properly populated
        self.assertTrue(result['weather']['enabled'])
        self.assertEqual(result['weather']['data']['dresscode'], 'Warm jacket')


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
