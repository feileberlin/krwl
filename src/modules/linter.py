"""
Linter Module for Site Generation

Validates scripts, stylesheets, HTML, SVG, translations, and accessibility
during the HTML export process.

Uses Python standard library only - no external dependencies required.
"""

import re
import json
import html.parser
from typing import Dict, List, Tuple, Any
from pathlib import Path


class LintResult:
    """Container for lint results"""
    def __init__(self, passed: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.passed = passed
        self.errors = errors or []
        self.warnings = warnings or []
        # Structured warnings with context for clickable UI
        self.structured_warnings = []
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str, category: str = None, rule: str = None, context: str = None):
        """
        Add a warning with optional structured metadata.
        
        Args:
            message: Warning message
            category: Category (e.g., "accessibility", "css", "javascript", "html")
            rule: WCAG rule or lint rule (e.g., "WCAG 1.1.1", "bracket-matching")
            context: Additional context (e.g., file location, code snippet)
        """
        self.warnings.append(message)
        # Add structured version for clickable UI
        self.structured_warnings.append({
            'message': message,
            'category': category or 'general',
            'rule': rule or '',
            'context': context or ''
        })
    
    def merge(self, other: 'LintResult'):
        """Merge another result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if hasattr(other, 'structured_warnings'):
            self.structured_warnings.extend(other.structured_warnings)
        if not other.passed:
            self.passed = False
    
    def to_json(self) -> Dict[str, Any]:
        """Export lint results as JSON for embedding in HTML"""
        return {
            'passed': self.passed,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'structured_warnings': self.structured_warnings
        }
    
    def __bool__(self):
        return self.passed


class HTMLValidator(html.parser.HTMLParser):
    """Simple HTML validator using standard library"""
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.structured_warnings = []
        self.tag_stack = []
        self.self_closing_tags = {'meta', 'link', 'br', 'hr', 'img', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
    
    def handle_starttag(self, tag, attrs):
        if tag not in self.self_closing_tags:
            self.tag_stack.append(tag)
        
        # Check for required attributes
        if tag == 'img':
            attr_dict = dict(attrs)
            if 'alt' not in attr_dict:
                warning_msg = f"Image tag missing 'alt' attribute (accessibility issue)"
                self.warnings.append(warning_msg)
                self.structured_warnings.append({
                    'message': warning_msg,
                    'category': 'accessibility',
                    'rule': 'WCAG 1.1.1',
                    'context': 'All images must have alt attributes for screen reader accessibility'
                })
        
        if tag == 'a':
            attr_dict = dict(attrs)
            if 'href' in attr_dict and attr_dict['href'].startswith('http'):
                # External link - check for security attributes
                if 'rel' not in attr_dict or 'noopener' not in attr_dict.get('rel', ''):
                    warning_msg = f"External link missing 'rel=\"noopener noreferrer\"' (security issue)"
                    self.warnings.append(warning_msg)
                    self.structured_warnings.append({
                        'message': warning_msg,
                        'category': 'security',
                        'rule': 'Security Best Practice',
                        'context': 'External links should have rel="noopener noreferrer" to prevent tab-nabbing attacks'
                    })
    
    def handle_endtag(self, tag):
        if tag in self.self_closing_tags:
            return
        
        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag: </{tag}>")
            return
        
        if self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        else:
            self.errors.append(f"Mismatched tag: expected </{self.tag_stack[-1]}>, got </{tag}>")
    
    def validate(self, html_content: str) -> LintResult:
        """Validate HTML structure"""
        self.errors = []
        self.warnings = []
        self.structured_warnings = []
        self.tag_stack = []
        
        try:
            self.feed(html_content)
        except Exception as e:
            self.errors.append(f"HTML parsing error: {str(e)}")
        
        # Check for unclosed tags
        if self.tag_stack:
            self.errors.append(f"Unclosed tags: {', '.join(self.tag_stack)}")
        
        result = LintResult(passed=len(self.errors) == 0)
        result.errors = self.errors
        result.warnings = self.warnings
        result.structured_warnings = self.structured_warnings
        return result


class Linter:
    """Main linter class for validating site generation output"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.html_validator = HTMLValidator()
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"  [Lint] {message}")
    
    # ==================== JavaScript Validation ====================
    
    def lint_javascript(self, js_content: str, filename: str = "script") -> LintResult:
        """
        Validate JavaScript syntax and common issues.
        Uses regex patterns to detect common problems.
        """
        result = LintResult()
        self.log(f"Linting JavaScript: {filename}")
        
        if not js_content or not js_content.strip():
            result.add_error(f"{filename}: JavaScript content is empty")
            return result
        
        # Check for console.log in production (warning only)
        console_logs = re.findall(r'console\.log\(', js_content)
        if console_logs:
            result.add_warning(f"{filename}: Found {len(console_logs)} console.log statements (consider removing for production)")
        
        # Check for eval() usage (security risk)
        if re.search(r'\beval\s*\(', js_content):
            result.add_error(f"{filename}: Found eval() usage (security risk)")
        
        # Check for alert() usage (poor UX)
        if re.search(r'\balert\s*\(', js_content):
            result.add_warning(f"{filename}: Found alert() usage (consider better UX)")
        
        # Check for proper semicolons (basic check)
        lines = js_content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip empty lines, comments, and block statements
            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.endswith('{') or stripped.endswith('}'):
                continue
            # Check if line needs semicolon
            if stripped and not stripped.endswith((';', ',', '{', '}', ')', ']')) and not stripped.startswith(('if', 'for', 'while', 'function', 'class', 'const', 'let', 'var', 'return', 'break', 'continue', 'case', 'default', 'else', '}')):
                # This is a very basic check - many false positives possible
                pass
        
        # Check for undefined variables (very basic)
        # Look for assignments and declarations
        declared_vars = set()
        for match in re.finditer(r'\b(?:const|let|var)\s+(\w+)', js_content):
            declared_vars.add(match.group(1))
        
        # Check bracket matching
        if js_content.count('{') != js_content.count('}'):
            result.add_error(f"{filename}: Mismatched curly braces")
        if js_content.count('(') != js_content.count(')'):
            result.add_error(f"{filename}: Mismatched parentheses")
        if js_content.count('[') != js_content.count(']'):
            result.add_error(f"{filename}: Mismatched square brackets")
        
        return result
    
    # ==================== CSS Validation ====================
    
    def lint_css(self, css_content: str, filename: str = "stylesheet") -> LintResult:
        """
        Validate CSS syntax and common issues.
        """
        result = LintResult()
        self.log(f"Linting CSS: {filename}")
        
        if not css_content or not css_content.strip():
            result.add_error(f"{filename}: CSS content is empty")
            return result
        
        # Check bracket matching
        open_braces = css_content.count('{')
        close_braces = css_content.count('}')
        if open_braces != close_braces:
            result.add_error(f"{filename}: Mismatched curly braces in CSS (open: {open_braces}, close: {close_braces})")
        
        # Check for empty rules
        empty_rules = re.findall(r'[^}]*\{\s*\}', css_content)
        if empty_rules:
            result.add_warning(f"{filename}: Found {len(empty_rules)} empty CSS rules")
        
        # Check for !important overuse
        important_count = len(re.findall(r'!important', css_content))
        if important_count > 10:
            result.add_warning(f"{filename}: High usage of !important ({important_count} occurrences) - consider refactoring")
        
        # Check for valid color codes (simplified - only check for obvious invalid patterns)
        # Look for # followed by non-hex or wrong length, but be lenient
        # Skip this check as it's too prone to false positives in minified CSS
        
        # Check for proper semicolons in declarations
        # Look for missing semicolons before closing braces
        # Skip this check as it's too prone to false positives
        
        return result
    
    # ==================== HTML Validation ====================
    
    def lint_html(self, html_content: str) -> LintResult:
        """
        Validate HTML structure and semantics.
        """
        result = LintResult()
        self.log("Linting HTML structure")
        
        if not html_content or not html_content.strip():
            result.add_error("HTML content is empty")
            return result
        
        # Use HTML parser for structural validation
        parse_result = self.html_validator.validate(html_content)
        result.merge(parse_result)
        
        # Check for doctype
        if not re.search(r'<!DOCTYPE\s+html>', html_content, re.IGNORECASE):
            result.add_error("Missing <!DOCTYPE html> declaration")
        
        # Check for required HTML structure
        if '<html' not in html_content.lower():
            result.add_error("Missing <html> tag")
        if '<head' not in html_content.lower():
            result.add_error("Missing <head> tag")
        if '<body' not in html_content.lower():
            result.add_error("Missing <body> tag")
        
        # Check for charset
        if 'charset' not in html_content.lower():
            result.add_warning(
                "Missing charset declaration (e.g., <meta charset=\"UTF-8\">)",
                category="html",
                rule="HTML Best Practice",
                context="Character encoding should be declared early in the document to prevent encoding issues"
            )
        
        # Check for viewport meta tag (mobile-first)
        if 'viewport' not in html_content.lower():
            result.add_warning(
                "Missing viewport meta tag for mobile responsiveness",
                category="html",
                rule="Mobile Best Practice",
                context="Viewport meta tag is essential for proper mobile display: <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
            )
        
        # Check for title
        if '<title>' not in html_content.lower() or '</title>' not in html_content.lower():
            result.add_error("Missing <title> tag")
        
        return result
    
    # ==================== SVG Validation ====================
    
    def lint_svg(self, svg_content: str, filename: str = "svg") -> LintResult:
        """
        Validate SVG content for security and structure.
        """
        result = LintResult()
        self.log(f"Linting SVG: {filename}")
        
        if not svg_content or not svg_content.strip():
            result.add_error(f"{filename}: SVG content is empty")
            return result
        
        # Check for script tags (security risk)
        if re.search(r'<script[^>]*>', svg_content, re.IGNORECASE):
            result.add_error(f"{filename}: SVG contains <script> tags (security risk)")
        
        # Check for event handlers (security risk)
        event_handlers = ['onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout']
        for handler in event_handlers:
            if re.search(f'{handler}\\s*=', svg_content, re.IGNORECASE):
                result.add_error(f"{filename}: SVG contains '{handler}' event handler (security risk)")
        
        # Check for external references (security risk)
        if re.search(r'xlink:href\s*=\s*["\']https?://', svg_content, re.IGNORECASE):
            result.add_warning(f"{filename}: SVG contains external references (potential security risk)")
        
        # Check for proper SVG structure
        if '<svg' not in svg_content.lower():
            result.add_error(f"{filename}: Missing <svg> root tag")
        
        # Check xmlns attribute
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            result.add_warning(f"{filename}: Missing or incorrect xmlns attribute")
        
        return result
    
    # ==================== Translation Validation ====================
    
    def lint_translations(self, translations: Dict[str, Any], lang: str = "en") -> LintResult:
        """
        Validate translation completeness and structure.
        """
        result = LintResult()
        self.log(f"Linting translations: {lang}")
        
        if not translations:
            result.add_error(f"Translation file for '{lang}' is empty")
            return result
        
        # Check for required sections
        required_sections = ['app', 'filters', 'map', 'events']
        for section in required_sections:
            if section not in translations:
                result.add_warning(f"Translation '{lang}' missing section: {section}")
        
        # Check for empty translations
        def check_empty_values(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and not value.strip():
                        result.add_warning(f"Translation '{lang}' has empty value at: {current_path}")
                    elif isinstance(value, (dict, list)):
                        check_empty_values(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_empty_values(item, f"{path}[{i}]")
        
        check_empty_values(translations)
        
        return result
    
    def lint_translation_consistency(self, trans_en: Dict, trans_de: Dict) -> LintResult:
        """
        Check consistency between English and German translations.
        """
        result = LintResult()
        self.log("Checking translation consistency between en and de")
        
        def get_keys(obj: Any, prefix: str = "") -> set:
            """Recursively get all keys from nested dict"""
            keys = set()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_key = f"{prefix}.{key}" if prefix else key
                    keys.add(current_key)
                    if isinstance(value, dict):
                        keys.update(get_keys(value, current_key))
            return keys
        
        en_keys = get_keys(trans_en)
        de_keys = get_keys(trans_de)
        
        # Find missing keys
        missing_in_de = en_keys - de_keys
        missing_in_en = de_keys - en_keys
        
        for key in missing_in_de:
            result.add_warning(f"Translation key '{key}' exists in EN but missing in DE")
        
        for key in missing_in_en:
            result.add_warning(f"Translation key '{key}' exists in DE but missing in EN")
        
        return result
    
    # ==================== Accessibility Validation ====================
    
    def lint_accessibility(self, html_content: str) -> LintResult:
        """
        Validate accessibility (a11y) issues in HTML.
        Checks WCAG 2.1 Level AA compliance where possible.
        """
        result = LintResult()
        self.log("Linting accessibility (a11y)")
        
        if not html_content:
            result.add_error("HTML content is empty")
            return result
        
        # Check for lang attribute
        if not re.search(r'<html[^>]*\slang\s*=', html_content, re.IGNORECASE):
            result.add_error("Missing 'lang' attribute on <html> tag (WCAG 3.1.1)")
        
        # Check for images without alt text
        img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
        for img in img_tags:
            if 'alt=' not in img.lower():
                result.add_error(f"Image missing 'alt' attribute (WCAG 1.1.1)")
        
        # Check for empty alt text on decorative images (this is actually OK)
        decorative_imgs = re.findall(r'<img[^>]*alt\s*=\s*["\']["\'][^>]*>', html_content, re.IGNORECASE)
        if decorative_imgs:
            self.log(f"Found {len(decorative_imgs)} images with empty alt (OK for decorative images)")
        
        # Check for links without text content
        link_matches = re.finditer(r'<a\s+[^>]*href\s*=\s*["\'][^"\']*["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
        for match in link_matches:
            link_content = match.group(1).strip()
            # Remove HTML tags to check text content
            text_content = re.sub(r'<[^>]+>', '', link_content).strip()
            if not text_content:
                result.add_error("Link without text content (WCAG 2.4.4)")
        
        # Check for form inputs without labels
        input_tags = re.findall(r'<input[^>]*>', html_content, re.IGNORECASE)
        for input_tag in input_tags:
            # Skip hidden and submit buttons
            if 'type="hidden"' in input_tag.lower() or 'type="submit"' in input_tag.lower() or 'type="button"' in input_tag.lower():
                continue
            # Check for aria-label or id (for label association)
            if 'aria-label=' not in input_tag.lower() and 'id=' not in input_tag.lower():
                result.add_warning(
                    "Form input should have aria-label or associated label (WCAG 3.3.2)",
                    category="accessibility",
                    rule="WCAG 3.3.2",
                    context="Form inputs must be properly labeled for screen readers"
                )
        
        # Check for proper heading hierarchy (h1, h2, h3, etc.)
        headings = re.findall(r'<h([1-6])[^>]*>', html_content, re.IGNORECASE)
        if headings:
            heading_levels = [int(h) for h in headings]
            # Check if h1 exists
            if 1 not in heading_levels:
                result.add_warning(
                    "Missing <h1> heading for page title",
                    category="accessibility",
                    rule="WCAG 1.3.1",
                    context="Every page should have exactly one h1 tag for the main heading"
                )
            # Check for skipped levels (e.g., h1 -> h3)
            for i in range(len(heading_levels) - 1):
                if heading_levels[i+1] > heading_levels[i] + 1:
                    result.add_warning(
                        f"Heading hierarchy skip: h{heading_levels[i]} -> h{heading_levels[i+1]} (WCAG 1.3.1)",
                        category="accessibility",
                        rule="WCAG 1.3.1",
                        context="Heading levels should not be skipped (e.g., h1 -> h2 -> h3, not h1 -> h3)"
                    )
        
        # Check for ARIA attributes
        if 'aria-' not in html_content.lower():
            result.add_warning(
                "No ARIA attributes found - consider adding for better accessibility",
                category="accessibility",
                rule="ARIA Best Practices",
                context="ARIA attributes help screen readers understand dynamic content and interactive elements"
            )
        
        # Check for sufficient color contrast (can only check if colors are defined)
        # This would require actual color analysis - skip for now
        
        # Check for keyboard accessibility indicators
        if 'tabindex' not in html_content.lower():
            self.log("No tabindex found - ensure interactive elements are keyboard accessible")
        
        # Check for skip links
        if 'skip' not in html_content.lower() or 'main-content' not in html_content.lower():
            result.add_warning(
                "Consider adding skip navigation links for keyboard users",
                category="accessibility",
                rule="WCAG 2.4.1",
                context="Skip links allow keyboard users to bypass repetitive navigation and go directly to main content"
            )
        
        return result
    
    # ==================== Complete Lint ====================
    
    def lint_all(
        self,
        html_content: str,
        stylesheets: Dict[str, str],
        scripts: Dict[str, str],
        translations_en: Dict = None,
        translations_de: Dict = None,
        svg_files: Dict[str, str] = None
    ) -> LintResult:
        """
        Run all linting checks and combine results.
        
        Args:
            html_content: Complete HTML content
            stylesheets: Dict of CSS content {filename: content}
            scripts: Dict of JavaScript content {filename: content}
            translations_en: Optional English translation dict (deprecated)
            translations_de: Optional German translation dict (deprecated)
            svg_files: Optional dict of SVG content {filename: content}
        
        Returns:
            Combined LintResult
        """
        print("\n" + "=" * 60)
        print("🔍 Running Linting Checks")
        print("=" * 60)
        
        combined_result = LintResult()
        
        # Lint HTML
        print("\n📄 Validating HTML...")
        html_result = self.lint_html(html_content)
        combined_result.merge(html_result)
        self._print_result(html_result, "HTML")
        
        # Lint CSS
        print("\n🎨 Validating CSS...")
        for filename, content in stylesheets.items():
            css_result = self.lint_css(content, filename)
            combined_result.merge(css_result)
            self._print_result(css_result, f"CSS - {filename}")
        
        # Lint JavaScript
        print("\n📜 Validating JavaScript...")
        for filename, content in scripts.items():
            js_result = self.lint_javascript(content, filename)
            combined_result.merge(js_result)
            self._print_result(js_result, f"JS - {filename}")
        
        # Lint SVG (if provided)
        if svg_files:
            print("\n🖼️  Validating SVG files...")
            for filename, content in svg_files.items():
                svg_result = self.lint_svg(content, filename)
                combined_result.merge(svg_result)
                self._print_result(svg_result, f"SVG - {filename}")
        
        # Lint Translations (skip if not provided - i18n removed)
        if translations_en is not None and translations_de is not None:
            print("\n🌐 Validating Translations...")
            en_result = self.lint_translations(translations_en, "en")
            de_result = self.lint_translations(translations_de, "de")
            consistency_result = self.lint_translation_consistency(translations_en, translations_de)
            combined_result.merge(en_result)
            combined_result.merge(de_result)
            combined_result.merge(consistency_result)
            self._print_result(en_result, "Translations - EN")
            self._print_result(de_result, "Translations - DE")
            self._print_result(consistency_result, "Translation Consistency")
        else:
            print("\n🌐 Skipping Translation Validation (i18n removed)")
        
        # Lint Accessibility
        print("\n♿ Validating Accessibility...")
        a11y_result = self.lint_accessibility(html_content)
        combined_result.merge(a11y_result)
        self._print_result(a11y_result, "Accessibility")
        
        # Print summary
        print("\n" + "=" * 60)
        if combined_result.passed:
            print("✅ All linting checks passed!")
        else:
            print("❌ Linting checks failed")
            print(f"   Errors: {len(combined_result.errors)}")
        if combined_result.warnings:
            print(f"   Warnings: {len(combined_result.warnings)}")
        print("=" * 60)
        
        return combined_result
    
    def _print_result(self, result: LintResult, name: str):
        """Print individual lint result"""
        if result.passed and not result.warnings:
            print(f"  ✓ {name}")
        elif result.passed and result.warnings:
            print(f"  ⚠ {name} ({len(result.warnings)} warnings)")
            if self.verbose:
                for warning in result.warnings:
                    print(f"      Warning: {warning}")
        else:
            print(f"  ✗ {name} ({len(result.errors)} errors, {len(result.warnings)} warnings)")
            if self.verbose:
                for error in result.errors:
                    print(f"      Error: {error}")
                for warning in result.warnings:
                    print(f"      Warning: {warning}")
    
    # ==================== Component-Specific Linting ====================
    
    def lint_component(self, component_html: str, component_name: str) -> LintResult:
        """
        Lint an individual component template.
        
        Validates:
        - Valid HTML structure
        - Proper use of template variables
        - Semantic HTML tags
        - ARIA attributes
        
        Args:
            component_html: Component template content
            component_name: Name of component for error messages
        
        Returns:
            LintResult with validation results
        """
        result = LintResult()
        
        # Check for template variables (should have {var_name} placeholders)
        template_vars = re.findall(r'\{(\w+)\}', component_html)
        if self.verbose:
            print(f"  Component '{component_name}' uses {len(template_vars)} template variables")
        
        # Validate semantic tags based on component type
        if 'map-main' in component_name:
            if '<main' not in component_html:
                result.add_error(f"{component_name}: Should use <main> semantic tag")
            if 'role="application"' not in component_html:
                result.add_warning(f"{component_name}: Missing application role for map")
        
        elif 'dashboard-aside' in component_name:
            if '<aside' not in component_html:
                result.add_error(f"{component_name}: Should use <aside> semantic tag")
            if 'role="complementary"' not in component_html:
                result.add_warning(f"{component_name}: Missing complementary role")
        
        elif 'filter-nav' in component_name:
            if '<nav' not in component_html:
                result.add_error(f"{component_name}: Should use <nav> semantic tag")
            if 'role="navigation"' not in component_html:
                result.add_warning(f"{component_name}: Missing navigation role")
        
        # Check for ARIA labels on interactive elements
        if 'button' in component_html or 'role="button"' in component_html:
            if 'aria-label=' not in component_html:
                result.add_warning(f"{component_name}: Interactive elements should have aria-label")
        
        return result
    
    def lint_all_components(self, components_dir: Path) -> LintResult:
        """
        Lint all components in a directory.
        
        Args:
            components_dir: Path to components directory
        
        Returns:
            Combined LintResult for all components
        """
        result = LintResult()
        
        if not components_dir.exists():
            result.add_error(f"Components directory not found: {components_dir}")
            return result
        
        # Find all HTML component files
        component_files = list(components_dir.rglob('*.html'))
        
        if not component_files:
            result.add_warning(f"No component files found in {components_dir}")
            return result
        
        print(f"\n🧩 Linting {len(component_files)} components...")
        
        for component_file in component_files:
            relative_path = component_file.relative_to(components_dir)
            try:
                content = component_file.read_text(encoding='utf-8')
                component_result = self.lint_component(content, str(relative_path))
                result.merge(component_result)
                
                if component_result.passed and not component_result.warnings:
                    print(f"  ✓ {relative_path}")
                elif component_result.passed:
                    print(f"  ⚠ {relative_path} ({len(component_result.warnings)} warnings)")
                else:
                    print(f"  ✗ {relative_path} ({len(component_result.errors)} errors)")
            except Exception as e:
                result.add_error(f"Failed to lint {relative_path}: {e}")
        
        return result
    
    def lint_design_tokens(self, design_config: Dict) -> LintResult:
        """
        Validate design token structure from config.
        
        Validates:
        - Required sections present
        - Color values are valid hex
        - Spacing values have units
        - Z-index values are integers
        
        Args:
            design_config: Design section from config.json
        
        Returns:
            LintResult with validation results
        """
        result = LintResult()
        
        if not design_config:
            result.add_error("No design configuration provided")
            return result
        
        # Check required sections
        required_sections = ['colors', 'typography', 'spacing', 'z_index',
                           'shadows', 'borders', 'transitions', 'branding']
        
        for section in required_sections:
            if section not in design_config:
                result.add_warning(f"Missing design section: {section}")
        
        # Validate colors
        if 'colors' in design_config:
            colors = design_config['colors']
            hex_pattern = re.compile(r'^#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?$')
            
            for key, value in colors.items():
                if not hex_pattern.match(value):
                    result.add_warning(f"Color '{key}' has invalid hex value: {value}")
            
            # Check required colors
            required_colors = ['primary', 'bg_primary', 'text_primary']
            for color in required_colors:
                if color not in colors:
                    result.add_error(f"Missing required color: {color}")
        
        # Validate spacing
        if 'spacing' in design_config:
            spacing = design_config['spacing']
            unit_pattern = re.compile(r'^\d+(\.\d+)?(px|rem|em|%)$')
            
            for key, value in spacing.items():
                if not unit_pattern.match(value):
                    result.add_warning(f"Spacing '{key}' missing unit: {value}")
        
        # Validate z-index
        if 'z_index' in design_config:
            z_index = design_config['z_index']
            
            for key, value in z_index.items():
                if key.startswith('_'):  # Skip comment keys
                    continue
                if not isinstance(value, int):
                    result.add_error(f"Z-index '{key}' must be integer: {value}")
            
            # Validate layer ordering
            if all(k in z_index for k in ['layer_1_map', 'layer_2_event_popups', 
                                          'layer_3_ui', 'layer_4_modals']):
                if not (z_index['layer_1_map'] < z_index['layer_2_event_popups'] < 
                       z_index['layer_3_ui'] < z_index['layer_4_modals']):
                    result.add_error("Z-index layers not in correct order (1 < 2 < 3 < 4)")
        
        return result
    
    def lint_semantic_structure(self, html: str) -> LintResult:
        """
        Validate semantic HTML5 structure.
        
        Checks for:
        - Proper use of landmark elements
        - ARIA roles match semantic tags
        - Heading hierarchy
        - Required ARIA attributes
        
        Args:
            html: Complete HTML document
        
        Returns:
            LintResult with validation results
        """
        result = LintResult()
        
        # Check for semantic landmarks
        landmarks = {
            '<main': 'main',
            '<nav': 'navigation',
            '<aside': 'complementary content',
            '<header': 'header',
            '<footer': 'footer'
        }
        
        for tag, description in landmarks.items():
            if tag in html:
                if self.verbose:
                    print(f"  ✓ Found {description} landmark")
            else:
                if tag == '<main':  # main is required
                    result.add_error(f"Missing required {description} landmark")
        
        # Check for ARIA roles matching semantic tags
        if '<main' in html and 'role="application"' not in html and 'role="main"' not in html:
            result.add_warning("Main element should have appropriate ARIA role")
        
        if '<nav' in html and 'role="navigation"' not in html:
            result.add_warning("Nav element missing navigation role")
        
        if '<aside' in html and 'role="complementary"' not in html:
            result.add_warning("Aside element missing complementary role")
        
        # Check heading hierarchy
        headings = re.findall(r'<h([1-6])', html)
        if headings:
            heading_levels = [int(h) for h in headings]
            # Check if hierarchy starts at 1 and doesn't skip levels
            if heading_levels[0] != 1:
                result.add_warning(f"Heading hierarchy should start with h1, found h{heading_levels[0]}")
            
            for i in range(1, len(heading_levels)):
                if heading_levels[i] > heading_levels[i-1] + 1:
                    result.add_warning(f"Heading hierarchy skips level: h{heading_levels[i-1]} to h{heading_levels[i]}")
        
        # Check for live regions
        if 'aria-live=' in html:
            if self.verbose:
                print("  ✓ Found ARIA live regions")
        
        # Check for proper button labels
        button_pattern = re.compile(r'<button[^>]*>', re.IGNORECASE)
        buttons = button_pattern.findall(html)
        for button in buttons:
            if 'aria-label=' not in button and '>' in button:
                # Check if button has text content
                button_end = html.find('</button>', html.find(button))
                button_content = html[html.find(button):button_end]
                if not re.search(r'>[^<]+<', button_content):
                    result.add_warning("Button should have aria-label or text content")
        
        return result
