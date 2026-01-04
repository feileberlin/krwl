"""
Template Processor Module

Conditional rendering based on icon mode, build mode, and configuration.
Placeholder-based templating system for flexible HTML generation.

Features:
- Placeholder replacement ({{VARIABLE}})
- Conditional blocks ({{IF condition}}...{{ENDIF}})
- Template validation
- Mode-specific rendering

Usage:
    from template_processor import TemplateProcessor
    
    processor = TemplateProcessor(base_path)
    html = processor.process_template(template, context)
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """
    Template Processor
    
    Processes HTML templates with placeholders and conditional rendering.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize template processor.
        
        Args:
            base_path: Base path of the project
        """
        self.base_path = Path(base_path)
    
    def process_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process template with context variables.
        
        Supports:
        - Simple placeholders: {{VARIABLE}}
        - Conditional blocks: {{IF condition}}...{{ENDIF}}
        - Nested conditions: {{IF outer}}{{IF inner}}...{{ENDIF}}{{ENDIF}}
        
        Args:
            template: Template string
            context: Dictionary of variables
            
        Returns:
            Processed template
        """
        if not template:
            return ""
        
        # Process conditionals first (before simple replacements)
        template = self._process_conditionals(template, context)
        
        # Replace simple placeholders
        template = self._replace_placeholders(template, context)
        
        return template
    
    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process conditional blocks.
        
        Syntax: {{IF condition}}...{{ENDIF}}
        
        Args:
            template: Template string
            context: Context variables
            
        Returns:
            Template with conditionals processed
        """
        # Pattern: {{IF variable}}...{{ENDIF}}
        pattern = r'\{\{IF\s+(\w+)\}\}(.*?)\{\{ENDIF\}\}'
        
        def replace_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # Check if variable is truthy
            value = context.get(var_name, False)
            
            # Support string checks
            if isinstance(value, str):
                # Check for specific values
                if '=' in var_name:
                    # Format: {{IF mode=svg-paths}}
                    parts = var_name.split('=')
                    var_name = parts[0].strip()
                    expected = parts[1].strip()
                    value = context.get(var_name)
                    return content if str(value) == expected else ''
                else:
                    return content if value and value.lower() not in ['false', '0', 'no', 'none'] else ''
            
            return content if value else ''
        
        # Process recursively (for nested conditionals)
        max_iterations = 10
        iteration = 0
        
        while '{{IF' in template and iteration < max_iterations:
            prev = template
            template = re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
            
            if template == prev:
                break
            
            iteration += 1
        
        if iteration >= max_iterations:
            logger.warning("Maximum conditional nesting depth reached")
        
        return template
    
    def _replace_placeholders(self, template: str, context: Dict[str, Any]) -> str:
        """
        Replace simple placeholders.
        
        Syntax: {{VARIABLE}}
        
        Args:
            template: Template string
            context: Context variables
            
        Returns:
            Template with placeholders replaced
        """
        # Pattern: {{VARIABLE}}
        pattern = r'\{\{(\w+)\}\}'
        
        def replace_placeholder(match):
            var_name = match.group(1)
            value = context.get(var_name, '')
            
            # Convert to string
            if value is None:
                return ''
            elif isinstance(value, bool):
                return str(value).lower()
            else:
                return str(value)
        
        return re.sub(pattern, replace_placeholder, template)
    
    def extract_placeholders(self, template: str) -> List[str]:
        """
        Extract all placeholders from template.
        
        Args:
            template: Template string
            
        Returns:
            List of placeholder names
        """
        # Find all {{VARIABLE}} patterns
        simple_pattern = r'\{\{(\w+)\}\}'
        simple = re.findall(simple_pattern, template)
        
        # Find all {{IF condition}} patterns
        conditional_pattern = r'\{\{IF\s+(\w+)\}\}'
        conditional = re.findall(conditional_pattern, template)
        
        # Combine and deduplicate
        all_placeholders = list(set(simple + conditional))
        
        return sorted(all_placeholders)
    
    def validate_template(self, template: str) -> Tuple[bool, List[str]]:
        """
        Validate template syntax.
        
        Checks:
        - Balanced {{IF}}...{{ENDIF}} blocks
        - No unclosed placeholders
        - Valid placeholder names
        
        Args:
            template: Template string
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check balanced IF/ENDIF
        if_count = template.count('{{IF')
        endif_count = template.count('{{ENDIF}}')
        
        if if_count != endif_count:
            errors.append(f"Unbalanced IF/ENDIF: {if_count} IF vs {endif_count} ENDIF")
        
        # Check for malformed placeholders
        malformed = re.findall(r'\{\{[^\}]*$', template)
        if malformed:
            errors.append(f"Unclosed placeholders found: {len(malformed)}")
        
        # Check for invalid placeholder names
        placeholders = self.extract_placeholders(template)
        for placeholder in placeholders:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', placeholder):
                errors.append(f"Invalid placeholder name: {placeholder}")
        
        return len(errors) == 0, errors
    
    def preview_template(self, template: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview template processing without rendering.
        
        Args:
            template: Template string
            context: Context variables
            
        Returns:
            Dictionary with preview information
        """
        placeholders = self.extract_placeholders(template)
        is_valid, errors = self.validate_template(template)
        
        # Check which context variables will be used
        used_vars = {k: v for k, v in context.items() if k in placeholders}
        missing_vars = [p for p in placeholders if p not in context]
        
        return {
            'valid': is_valid,
            'errors': errors,
            'placeholders': placeholders,
            'used_vars': used_vars,
            'missing_vars': missing_vars,
            'template_size': len(template)
        }


def create_build_context(icon_mode: str = 'svg-paths', build_mode: str = 'inline-all', debug: bool = False) -> Dict[str, Any]:
    """
    Create context for template processing.
    
    Args:
        icon_mode: Icon mode (svg-paths or base64)
        build_mode: Build mode (inline-all, external-assets, hybrid)
        debug: Debug mode enabled
        
    Returns:
        Context dictionary
    """
    return {
        # Icon mode
        'icon_mode': icon_mode,
        'icon_mode_svg': icon_mode == 'svg-paths',
        'icon_mode_base64': icon_mode == 'base64',
        
        # Build mode
        'build_mode': build_mode,
        'build_inline_all': build_mode == 'inline-all',
        'build_external': build_mode == 'external-assets',
        'build_hybrid': build_mode == 'hybrid',
        
        # Debug
        'debug': debug,
        'production': not debug,
        
        # Feature flags (can be extended)
        'pwa_enabled': True,
        'offline_support': build_mode == 'inline-all',
    }


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python template_processor.py <command> [args]")
        print("Commands:")
        print("  validate <file> - Validate template")
        print("  placeholders <file> - List placeholders")
        print("  preview <file> - Preview with default context")
        sys.exit(1)
    
    command = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent
    processor = TemplateProcessor(base_path)
    
    if command == 'validate' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        template = file_path.read_text(encoding='utf-8')
        is_valid, errors = processor.validate_template(template)
        
        print(f"Validating: {file_path.name}")
        
        if is_valid:
            print("✅ Template is valid")
        else:
            print("❌ Template has errors:")
            for error in errors:
                print(f"  - {error}")
    
    elif command == 'placeholders' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        template = file_path.read_text(encoding='utf-8')
        placeholders = processor.extract_placeholders(template)
        
        print(f"Placeholders in {file_path.name}:")
        for placeholder in placeholders:
            print(f"  - {{{{{}}}}}".format(placeholder))
    
    elif command == 'preview' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        template = file_path.read_text(encoding='utf-8')
        context = create_build_context()
        
        preview = processor.preview_template(template, context)
        
        print(f"\n📋 Template Preview: {file_path.name}")
        print("=" * 60)
        print(f"Valid: {preview['valid']}")
        if preview['errors']:
            print(f"Errors: {', '.join(preview['errors'])}")
        print(f"Placeholders: {len(preview['placeholders'])}")
        print(f"Used vars: {len(preview['used_vars'])}")
        if preview['missing_vars']:
            print(f"Missing vars: {', '.join(preview['missing_vars'])}")
        print(f"Template size: {preview['template_size']:,} bytes")
        print("=" * 60)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
