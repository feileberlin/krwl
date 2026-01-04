"""
Configuration Validator Module

Runtime configuration validation to catch errors before build.
Ensures configuration values are valid and provides helpful error messages.

Features:
- Schema validation
- Type checking
- Value range validation
- Helpful error messages
- CLI-friendly output

Usage:
    from config_validator import ConfigValidator
    
    validator = ConfigValidator()
    is_valid, errors = validator.validate_config(config)
"""

import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class ConfigValidator:
    """
    Configuration Validator
    
    Validates configuration dictionaries against expected schema.
    """
    
    # Valid values for enums
    VALID_ICON_MODES = ['svg-paths', 'base64']
    VALID_BUILD_MODES = ['inline-all', 'external-assets', 'hybrid']
    VALID_ENVIRONMENTS = ['development', 'production', 'auto']
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate icons section
        if 'icons' in config:
            errors.extend(self._validate_icons(config['icons']))
        
        # Validate build section
        if 'build' in config:
            errors.extend(self._validate_build(config['build']))
        
        # Validate app section
        if 'app' in config:
            errors.extend(self._validate_app(config['app']))
        
        # Validate environment
        if 'environment' in config:
            errors.extend(self._validate_environment(config['environment']))
        
        # Validate data section
        if 'data' in config:
            errors.extend(self._validate_data(config['data']))
        
        return len(errors) == 0, errors
    
    def _validate_icons(self, icons_config: Dict[str, Any]) -> List[str]:
        """Validate icons section."""
        errors = []
        
        # Check mode
        if 'mode' in icons_config:
            mode = icons_config['mode']
            if mode not in self.VALID_ICON_MODES:
                errors.append(
                    f"Invalid icons.mode: '{mode}'. "
                    f"Must be one of: {', '.join(self.VALID_ICON_MODES)}"
                )
        
        return errors
    
    def _validate_build(self, build_config: Dict[str, Any]) -> List[str]:
        """Validate build section."""
        errors = []
        
        # Check mode
        if 'mode' in build_config:
            mode = build_config['mode']
            if mode not in self.VALID_BUILD_MODES:
                errors.append(
                    f"Invalid build.mode: '{mode}'. "
                    f"Must be one of: {', '.join(self.VALID_BUILD_MODES)}"
                )
        
        # Check optimization subsection
        if 'optimization' in build_config:
            opt = build_config['optimization']
            
            # Check boolean flags
            bool_fields = [
                'remove_unused_css',
                'remove_debug_info',
                'strip_comments',
                'minify_json'
            ]
            
            for field in bool_fields:
                if field in opt:
                    if not isinstance(opt[field], bool):
                        errors.append(
                            f"Invalid build.optimization.{field}: '{opt[field]}'. "
                            "Must be boolean (true/false)"
                        )
        
        return errors
    
    def _validate_app(self, app_config: Dict[str, Any]) -> List[str]:
        """Validate app section."""
        errors = []
        
        # Check name
        if 'name' in app_config:
            if not isinstance(app_config['name'], str):
                errors.append("Invalid app.name: Must be a string")
            elif not app_config['name'].strip():
                errors.append("Invalid app.name: Cannot be empty")
        
        # Check environment (deprecated, but validate if present)
        if 'environment' in app_config:
            env = app_config['environment']
            if env not in self.VALID_ENVIRONMENTS:
                errors.append(
                    f"Invalid app.environment: '{env}'. "
                    f"Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}"
                )
        
        return errors
    
    def _validate_environment(self, environment: str) -> List[str]:
        """Validate environment value."""
        errors = []
        
        if environment not in self.VALID_ENVIRONMENTS:
            errors.append(
                f"Invalid environment: '{environment}'. "
                f"Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}"
            )
        
        return errors
    
    def _validate_data(self, data_config: Dict[str, Any]) -> List[str]:
        """Validate data section."""
        errors = []
        
        # Check source
        if 'source' in data_config:
            source = data_config['source']
            valid_sources = ['real', 'demo', 'both']
            
            if source not in valid_sources:
                errors.append(
                    f"Invalid data.source: '{source}'. "
                    f"Must be one of: {', '.join(valid_sources)}"
                )
        
        return errors
    
    def validate_and_suggest(self, config: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate configuration and provide suggestions.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, errors, suggestions)
        """
        is_valid, errors = self.validate_config(config)
        suggestions = []
        
        # Provide suggestions based on configuration
        
        # Icon mode suggestions
        if 'icons' in config and config['icons'].get('mode') == 'base64':
            suggestions.append(
                "💡 Icon mode 'base64': Good for instant rendering. "
                "Consider 'svg-paths' for smaller gzipped size."
            )
        
        # Build mode suggestions
        if 'build' in config:
            build_mode = config['build'].get('mode', 'inline-all')
            
            if build_mode == 'inline-all':
                suggestions.append(
                    "💡 Build mode 'inline-all': Best for PWA/offline. "
                    "Larger HTML but fewer HTTP requests."
                )
            elif build_mode == 'external-assets':
                suggestions.append(
                    "💡 Build mode 'external-assets': Best for HTTP/2. "
                    "Smaller HTML but more HTTP requests."
                )
            elif build_mode == 'hybrid':
                suggestions.append(
                    "💡 Build mode 'hybrid': Balanced approach. "
                    "Good for most use cases."
                )
        
        # Optimization suggestions
        if 'build' in config and 'optimization' in config['build']:
            opt = config['build']['optimization']
            
            if not opt.get('remove_unused_css', False):
                suggestions.append(
                    "💡 Consider enabling 'remove_unused_css' for smaller CSS bundles."
                )
            
            if not opt.get('remove_debug_info', False):
                suggestions.append(
                    "💡 Consider enabling 'remove_debug_info' for production builds."
                )
        
        return is_valid, errors, suggestions
    
    def print_validation_results(self, config: Dict[str, Any]) -> bool:
        """
        Print validation results to console.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        is_valid, errors, suggestions = self.validate_and_suggest(config)
        
        print("\n" + "=" * 60)
        print("🔍 Configuration Validation")
        print("=" * 60)
        
        if is_valid:
            print("✅ Configuration is valid!")
        else:
            print(f"❌ Found {len(errors)} error(s):")
            for error in errors:
                print(f"  • {error}")
        
        if suggestions:
            print()
            print(f"💡 Suggestions ({len(suggestions)}):")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
        print("=" * 60)
        
        return is_valid


# Convenience functions for common validations

def validate_icon_mode(mode: str) -> bool:
    """Check if icon mode is valid."""
    return mode in ConfigValidator.VALID_ICON_MODES


def validate_build_mode(mode: str) -> bool:
    """Check if build mode is valid."""
    return mode in ConfigValidator.VALID_BUILD_MODES


def validate_environment(env: str) -> bool:
    """Check if environment is valid."""
    return env in ConfigValidator.VALID_ENVIRONMENTS


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    import json
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config_file>")
        print("Example: python config_validator.py config.json")
        sys.exit(1)
    
    config_file = Path(sys.argv[1])
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    
    validator = ConfigValidator()
    is_valid = validator.print_validation_results(config)
    
    sys.exit(0 if is_valid else 1)
