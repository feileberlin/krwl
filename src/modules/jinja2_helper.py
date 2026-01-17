"""
Jinja2 Helper Module - JSON Templating with Full Power

Industry-standard templating using Jinja2 library.
Replaces complex dict building with declarative JSON templates.
Supports loops, conditionals, filters, and template inheritance.

Features:
- Load templates from assets/json/templates/
- Full Jinja2 syntax support (loops, conditionals, filters)
- Template inheritance for DRY code
- Custom filters for JSON-specific operations
- Graceful fallback when Jinja2 not available

Usage:
    from jinja2_helper import Jinja2TemplateHelper
    
    helper = Jinja2TemplateHelper(base_path)
    result = helper.render('runtime_config', debug=True, environment='development')
    
    # With loops
    result = helper.render('events_list', events=[...])
    
    # With conditionals
    result = helper.render('config', 
        weather_enabled=True,
        weather_data={'temp': 15}
    )
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Try to import Jinja2, fallback gracefully if not installed
try:
    from jinja2 import Environment, FileSystemLoader, BaseLoader, select_autoescape
    from jinja2.exceptions import TemplateError, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Environment = None
    FileSystemLoader = None
    TemplateError = Exception
    TemplateNotFound = FileNotFoundError
    logger.warning("Jinja2 not installed, using fallback dict building")


class Jinja2TemplateHelper:
    """
    Helper class for JSON templating using Jinja2.
    
    Provides full templating power:
    - Variable substitution: {{ variable }}
    - Conditionals: {% if condition %}...{% endif %}
    - Loops: {% for item in items %}...{% endfor %}
    - Filters: {{ value | tojson }}, {{ value | default('fallback') }}
    - Template inheritance: {% extends "base.json" %}
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize Jinja2TemplateHelper.
        
        Args:
            base_path: Base path of the repository
        """
        self.base_path = Path(base_path)
        self.templates_dir = self.base_path / 'assets' / 'json' / 'templates'
        
        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=False,  # JSON doesn't need HTML escaping
                trim_blocks=True,
                lstrip_blocks=True
            )
            # Add custom filters
            self.env.filters['tojson_safe'] = self._tojson_safe
        else:
            self.env = None
    
    @staticmethod
    def _tojson_safe(value: Any) -> str:
        """Convert value to JSON-safe string representation."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif value is None:
            return 'null'
        elif isinstance(value, str):
            return json.dumps(value)
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return json.dumps(value, ensure_ascii=False)
    
    def render(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """
        Render a template with the given parameters.
        
        Uses Jinja2 for full templating capability.
        Falls back to simple dict building if Jinja2 not available.
        
        Args:
            template_name: Name of the template file (with or without .json extension)
            **kwargs: Variables to pass to the template
            
        Returns:
            Parsed JSON as a Python dict
            
        Example:
            result = helper.render('runtime_config', 
                debug=True, 
                environment='development',
                items=[1, 2, 3]  # Can use in {% for item in items %}
            )
        """
        # Ensure .json extension
        if not template_name.endswith('.json'):
            template_name = f'{template_name}.json'
        
        if JINJA2_AVAILABLE and self.env:
            try:
                template = self.env.get_template(template_name)
                rendered = template.render(**kwargs)
                return json.loads(rendered)
            except TemplateNotFound:
                raise FileNotFoundError(f"Template not found: {template_name}")
            except TemplateError as e:
                logger.error(f"Jinja2 template error for '{template_name}': {e}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON after rendering '{template_name}': {e}")
                raise
        else:
            # Fallback: try to load and process template manually
            return self._fallback_render(template_name.replace('.json', ''), kwargs)
    
    def render_string(self, template_string: str, **kwargs) -> Dict[str, Any]:
        """
        Render a template string directly (without loading from file).
        
        Useful for inline templates that don't need to be stored in files.
        
        Args:
            template_string: JSON template string with Jinja2 syntax
            **kwargs: Variables to substitute
            
        Returns:
            Parsed JSON as a Python dict
        """
        if JINJA2_AVAILABLE:
            from jinja2 import Template
            try:
                template = Template(template_string)
                rendered = template.render(**kwargs)
                return json.loads(rendered)
            except TemplateError as e:
                logger.error(f"Jinja2 template error: {e}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON after rendering: {e}")
                raise
        else:
            return self._fallback_render_string(template_string, kwargs)
    
    def _fallback_render(self, template_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback renderer when Jinja2 is not available.
        
        Loads template file and does simple variable substitution.
        Note: Does not support loops or conditionals in fallback mode.
        
        Args:
            template_name: Template name without extension
            params: Dictionary of parameters
            
        Returns:
            Parsed JSON dict
        """
        template_path = self.templates_dir / f'{template_name}.json'
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        template = template_path.read_text(encoding='utf-8')
        return self._fallback_render_string(template, params)
    
    def _fallback_render_string(self, template: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback string renderer when Jinja2 is not available.
        
        Simple {{ variable }} replacement only.
        Does not support loops, conditionals, or filters.
        
        Args:
            template: Template string
            params: Dictionary of parameters
            
        Returns:
            Parsed JSON dict
        """
        import re
        
        result = template
        
        # Replace {{ variable }} patterns
        def replace_var(match):
            var_name = match.group(1).strip()
            if var_name in params:
                value = params[var_name]
                # For values inside quotes, return raw string
                # For values outside quotes, return JSON representation
                if isinstance(value, str):
                    return value
                elif isinstance(value, bool):
                    return 'true' if value else 'false'
                elif value is None:
                    return 'null'
                elif isinstance(value, (int, float)):
                    return str(value)
                else:
                    return json.dumps(value, ensure_ascii=False)
            return match.group(0)  # Keep original if not found
        
        result = re.sub(r'\{\{\s*(\w+)\s*\}\}', replace_var, result)
        
        return json.loads(result)
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List of template names (without .json extension)
        """
        if not self.templates_dir.exists():
            return []
        
        return [f.stem for f in self.templates_dir.glob('*.json')]
    
    def validate_template(self, template_name: str, **sample_params) -> bool:
        """
        Validate that a template has correct syntax.
        
        Args:
            template_name: Name of the template to validate
            **sample_params: Sample parameters to test rendering
            
        Returns:
            True if valid, raises exception if invalid
        """
        if not template_name.endswith('.json'):
            template_name = f'{template_name}.json'
        
        if JINJA2_AVAILABLE and self.env:
            try:
                # Just try to load/compile the template
                self.env.get_template(template_name)
                return True
            except TemplateNotFound:
                raise FileNotFoundError(f"Template not found: {template_name}")
            except TemplateError as e:
                logger.error(f"Template validation failed for '{template_name}': {e}")
                raise
        else:
            # Fallback: just check if file exists and is valid JSON structure
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            return True


class HtmlTemplateHelper:
    """
    Helper class for HTML templating using Jinja2.
    
    Loads templates from assets/html/templates/ directory.
    Provides full Jinja2 power for HTML generation.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize HtmlTemplateHelper.
        
        Args:
            base_path: Base path of the repository
        """
        self.base_path = Path(base_path)
        self.templates_dir = self.base_path / 'assets' / 'html' / 'templates'
        
        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True,  # HTML needs escaping for security
                trim_blocks=True,
                lstrip_blocks=True
            )
            # Add custom filters
            self.env.filters['tojson'] = lambda x: json.dumps(x, ensure_ascii=False)
        else:
            self.env = None
    
    def render(self, template_name: str, **kwargs) -> str:
        """
        Render an HTML template with the given parameters.
        
        Args:
            template_name: Name of the template file (e.g., 'noscript-content.html.j2')
            **kwargs: Variables to pass to the template
            
        Returns:
            Rendered HTML string
        """
        if JINJA2_AVAILABLE and self.env:
            try:
                template = self.env.get_template(template_name)
                return template.render(**kwargs)
            except TemplateNotFound:
                raise FileNotFoundError(f"Template not found: {template_name}")
            except TemplateError as e:
                logger.error(f"Jinja2 template error for '{template_name}': {e}")
                raise
        else:
            raise RuntimeError("Jinja2 not available for HTML templating")
    
    def list_templates(self) -> List[str]:
        """List all available HTML templates."""
        if not self.templates_dir.exists():
            return []
        return [f.name for f in self.templates_dir.glob('*.j2')]


def is_jinja2_available() -> bool:
    """Check if Jinja2 library is available."""
    return JINJA2_AVAILABLE


# Convenience function for one-off template rendering
def render_json_template(template_string: str, **kwargs) -> Dict[str, Any]:
    """
    Render a JSON template string with parameters.
    
    Convenience function that doesn't require instantiating the helper.
    
    Args:
        template_string: JSON template with {{ placeholders }}
        **kwargs: Variables to substitute
        
    Returns:
        Parsed JSON as dict
        
    Example:
        result = render_json_template('''
        {
            "name": "{{ app_name }}",
            "count": {{ event_count }},
            "debug": {{ debug | tojson }}
        }
        ''', app_name="MyApp", event_count=42, debug=True)
    """
    if JINJA2_AVAILABLE:
        from jinja2 import Template, Environment
        env = Environment()
        env.filters['tojson'] = lambda x: json.dumps(x)
        template = env.from_string(template_string)
        rendered = template.render(**kwargs)
        return json.loads(rendered)
    else:
        # Use fallback
        helper = Jinja2TemplateHelper(Path('.'))
        return helper._fallback_render_string(template_string, kwargs)


# Backwards compatibility aliases
JsonTemplateHelper = Jinja2TemplateHelper  # Alias for migration
is_jsonplate_available = is_jinja2_available  # Alias for migration


if __name__ == '__main__':
    # CLI for testing templates
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python jinja2_helper.py <command> [args]")
        print("Commands:")
        print("  check       - Check if Jinja2 is available")
        print("  list        - List available templates")
        print("  validate    - Validate a template")
        print("  test        - Run basic test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        if JINJA2_AVAILABLE:
            print("✅ Jinja2 is available")
        else:
            print("❌ Jinja2 is NOT available (using fallback)")
        sys.exit(0)
    
    elif command == 'list':
        base_path = Path(__file__).parent.parent.parent
        helper = Jinja2TemplateHelper(base_path)
        templates = helper.list_templates()
        if templates:
            print(f"Available templates ({len(templates)}):")
            for t in templates:
                print(f"  - {t}")
        else:
            print("No templates found in assets/json/templates/")
    
    elif command == 'validate' and len(sys.argv) > 2:
        template_name = sys.argv[2]
        base_path = Path(__file__).parent.parent.parent
        helper = Jinja2TemplateHelper(base_path)
        try:
            helper.validate_template(template_name)
            print(f"✅ Template '{template_name}' is valid")
        except Exception as e:
            print(f"❌ Template '{template_name}' is invalid: {e}")
            sys.exit(1)
    
    elif command == 'test':
        # Basic functionality test
        print("Testing Jinja2 templating...")
        
        # Test 1: Simple variable substitution
        result = render_json_template('''
{
    "app": "{{ app_name }}",
    "count": {{ event_count }},
    "debug": {{ debug | tojson }}
}
''', app_name="Test App", event_count=42, debug=True)
        
        print("Test 1 - Simple variables:")
        print(json.dumps(result, indent=2))
        assert result['app'] == 'Test App'
        assert result['count'] == 42
        assert result['debug'] is True
        print("✅ Test 1 passed")
        
        # Test 2: Conditionals (Jinja2 power!)
        result = render_json_template('''
{
    "weather": {
        "enabled": {{ enabled | tojson }}{% if enabled %},
        "data": {{ data | tojson }}{% endif %}
    }
}
''', enabled=True, data={'temp': 15, 'condition': 'sunny'})
        
        print("\nTest 2 - Conditionals:")
        print(json.dumps(result, indent=2))
        assert result['weather']['enabled'] is True
        assert result['weather']['data']['temp'] == 15
        print("✅ Test 2 passed")
        
        # Test 3: Loops (Jinja2 power!)
        result = render_json_template('''
{
    "items": [{% for item in items %}
        {{ item | tojson }}{% if not loop.last %},{% endif %}{% endfor %}
    ]
}
''', items=['apple', 'banana', 'cherry'])
        
        print("\nTest 3 - Loops:")
        print(json.dumps(result, indent=2))
        assert result['items'] == ['apple', 'banana', 'cherry']
        print("✅ Test 3 passed")
        
        print("\n✅ All tests passed!")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
