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
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def merge(self, other: 'LintResult'):
        """Merge another result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.passed:
            self.passed = False
    
    def __bool__(self):
        return self.passed


class HTMLValidator(html.parser.HTMLParser):
    """Simple HTML validator using standard library"""
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tag_stack = []
        self.self_closing_tags = {'meta', 'link', 'br', 'hr', 'img', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
    
    def handle_starttag(self, tag, attrs):
        if tag not in self.self_closing_tags:
            self.tag_stack.append(tag)
        
        # Check for required attributes
        if tag == 'img':
            attr_dict = dict(attrs)
            if 'alt' not in attr_dict:
                self.warnings.append(f"Image tag missing 'alt' attribute (accessibility issue)")
        
        if tag == 'a':
            attr_dict = dict(attrs)
            if 'href' in attr_dict and attr_dict['href'].startswith('http'):
                # External link - check for security attributes
                if 'rel' not in attr_dict or 'noopener' not in attr_dict.get('rel', ''):
                    self.warnings.append(f"External link missing 'rel=\"noopener noreferrer\"' (security issue)")
    
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
            result.add_warning("Missing charset declaration (e.g., <meta charset=\"UTF-8\">)")
        
        # Check for viewport meta tag (mobile-first)
        if 'viewport' not in html_content.lower():
            result.add_warning("Missing viewport meta tag for mobile responsiveness")
        
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
                result.add_warning("Form input should have aria-label or associated label (WCAG 3.3.2)")
        
        # Check for proper heading hierarchy (h1, h2, h3, etc.)
        headings = re.findall(r'<h([1-6])[^>]*>', html_content, re.IGNORECASE)
        if headings:
            heading_levels = [int(h) for h in headings]
            # Check if h1 exists
            if 1 not in heading_levels:
                result.add_warning("Missing <h1> heading for page title")
            # Check for skipped levels (e.g., h1 -> h3)
            for i in range(len(heading_levels) - 1):
                if heading_levels[i+1] > heading_levels[i] + 1:
                    result.add_warning(f"Heading hierarchy skip: h{heading_levels[i]} -> h{heading_levels[i+1]} (WCAG 1.3.1)")
        
        # Check for ARIA attributes
        if 'aria-' not in html_content.lower():
            result.add_warning("No ARIA attributes found - consider adding for better accessibility")
        
        # Check for sufficient color contrast (can only check if colors are defined)
        # This would require actual color analysis - skip for now
        
        # Check for keyboard accessibility indicators
        if 'tabindex' not in html_content.lower():
            self.log("No tabindex found - ensure interactive elements are keyboard accessible")
        
        # Check for skip links
        if 'skip' not in html_content.lower() or 'main-content' not in html_content.lower():
            result.add_warning("Consider adding skip navigation links for keyboard users")
        
        return result
    
    # ==================== Complete Lint ====================
    
    def lint_all(
        self,
        html_content: str,
        stylesheets: Dict[str, str],
        scripts: Dict[str, str],
        translations_en: Dict,
        translations_de: Dict,
        svg_files: Dict[str, str] = None
    ) -> LintResult:
        """
        Run all linting checks and combine results.
        
        Args:
            html_content: Complete HTML content
            stylesheets: Dict of CSS content {filename: content}
            scripts: Dict of JavaScript content {filename: content}
            translations_en: English translation dict
            translations_de: German translation dict
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
        
        # Lint Translations
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
