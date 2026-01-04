"""
Build Optimization Module

Optimize builds with unused CSS removal, debug info stripping,
and comment removal for production.

Features:
- Unused CSS removal (HTML-based scanning)
- Debug info removal (console.log, etc.)
- Comment stripping
- JSON minification
- Build modes (inline-all, external-assets, hybrid)

Usage:
    from build_optimizer import BuildOptimizer
    
    optimizer = BuildOptimizer(base_path)
    optimized_css = optimizer.remove_unused_css(css, html)
    clean_js = optimizer.remove_debug_info(js)
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

logger = logging.getLogger(__name__)


class BuildOptimizer:
    """
    Build Optimization Manager
    
    Optimizes builds by removing unused code, debug info, and comments.
    """
    
    # Build modes
    BUILD_MODES = ['inline-all', 'external-assets', 'hybrid']
    
    def __init__(self, base_path: Path):
        """
        Initialize build optimizer.
        
        Args:
            base_path: Base path of the project
        """
        self.base_path = Path(base_path)
        
        # Statistics
        self.stats = {
            'css_rules_removed': 0,
            'css_bytes_saved': 0,
            'debug_statements_removed': 0,
            'comments_removed': 0
        }
    
    def extract_css_selectors(self, css: str) -> Set[str]:
        """
        Extract all CSS selectors from stylesheet.
        
        Args:
            css: CSS content
            
        Returns:
            Set of selector strings
        """
        selectors = set()
        
        # Match CSS rules (selector { ... })
        pattern = r'([^{]+)\s*\{'
        matches = re.finditer(pattern, css)
        
        for match in matches:
            selector_group = match.group(1).strip()
            
            # Split comma-separated selectors
            for selector in selector_group.split(','):
                selector = selector.strip()
                
                # Clean up pseudo-classes and pseudo-elements
                selector = re.sub(r':[a-z-]+(\([^)]*\))?', '', selector)
                selector = re.sub(r'::[a-z-]+', '', selector)
                
                if selector:
                    selectors.add(selector)
        
        return selectors
    
    def extract_html_classes_and_ids(self, html: str) -> Set[str]:
        """
        Extract all class names and IDs from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            Set of class and ID selectors
        """
        used = set()
        
        # Extract class names
        class_pattern = r'class=["\']([^"\']+)["\']'
        for match in re.finditer(class_pattern, html, re.IGNORECASE):
            classes = match.group(1).split()
            for cls in classes:
                used.add(f'.{cls}')
        
        # Extract IDs
        id_pattern = r'id=["\']([^"\']+)["\']'
        for match in re.finditer(id_pattern, html, re.IGNORECASE):
            id_name = match.group(1).strip()
            used.add(f'#{id_name}')
        
        # Extract tag names
        tag_pattern = r'<(\w+)'
        for match in re.finditer(tag_pattern, html, re.IGNORECASE):
            tag = match.group(1).lower()
            used.add(tag)
        
        return used
    
    def is_selector_used(self, selector: str, used_selectors: Set[str]) -> bool:
        """
        Check if a CSS selector is used in HTML.
        
        Args:
            selector: CSS selector
            used_selectors: Set of used selectors from HTML
            
        Returns:
            True if selector is used
        """
        # Universal selector always used
        if selector == '*':
            return True
        
        # Exact match
        if selector in used_selectors:
            return True
        
        # Check component parts (e.g., .class1.class2 → .class1, .class2)
        parts = re.split(r'[\s>+~]', selector)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Remove pseudo-classes/elements
            part = re.sub(r':[a-z-]+(\([^)]*\))?', '', part)
            part = re.sub(r'::[a-z-]+', '', part)
            
            # Check if base selector used
            if part in used_selectors:
                return True
            
            # Check tag.class → both tag and .class
            if '.' in part or '#' in part:
                # Extract tag
                tag_match = re.match(r'^([a-z]+)', part, re.IGNORECASE)
                if tag_match and tag_match.group(1) in used_selectors:
                    return True
                
                # Extract classes
                class_matches = re.findall(r'\.([a-z0-9_-]+)', part, re.IGNORECASE)
                for cls in class_matches:
                    if f'.{cls}' in used_selectors:
                        return True
                
                # Extract IDs
                id_matches = re.findall(r'#([a-z0-9_-]+)', part, re.IGNORECASE)
                for id_name in id_matches:
                    if f'#{id_name}' in used_selectors:
                        return True
        
        return False
    
    def remove_unused_css(self, css: str, html: str) -> str:
        """
        Remove unused CSS rules based on HTML content.
        
        Args:
            css: CSS content
            html: HTML content to scan for used selectors
            
        Returns:
            CSS with unused rules removed
        """
        if not css or not html:
            return css
        
        original_size = len(css)
        
        # Extract used selectors from HTML
        used_selectors = self.extract_html_classes_and_ids(html)
        logger.debug(f"Found {len(used_selectors)} used selectors in HTML")
        
        # Split CSS into rules
        result = []
        current_rule = []
        brace_count = 0
        in_media_query = False
        media_query_content = []
        
        for line in css.split('\n'):
            # Track brace depth
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            # Check for media queries
            if '@media' in line:
                in_media_query = True
                media_query_content = [line]
                continue
            
            if in_media_query:
                media_query_content.append(line)
                if brace_count == 0:
                    # End of media query - keep all media queries for now
                    # (more complex to parse nested rules)
                    result.extend(media_query_content)
                    in_media_query = False
                    media_query_content = []
                continue
            
            # Accumulate lines for current rule
            current_rule.append(line)
            
            # End of rule
            if brace_count == 0 and current_rule:
                rule_text = '\n'.join(current_rule)
                
                # Extract selector (everything before {)
                match = re.match(r'([^{]+)\{', rule_text)
                if match:
                    selector_group = match.group(1).strip()
                    
                    # Check if any selector in group is used
                    selectors = [s.strip() for s in selector_group.split(',')]
                    used = any(self.is_selector_used(sel, used_selectors) for sel in selectors)
                    
                    if used:
                        result.extend(current_rule)
                    else:
                        self.stats['css_rules_removed'] += 1
                        logger.debug(f"Removed unused CSS rule: {selector_group[:50]}...")
                else:
                    # Not a rule (comment, etc.), keep it
                    result.extend(current_rule)
                
                current_rule = []
        
        # Join result
        optimized_css = '\n'.join(result)
        optimized_size = len(optimized_css)
        
        self.stats['css_bytes_saved'] += (original_size - optimized_size)
        
        logger.info(f"CSS optimization: {self.stats['css_rules_removed']} rules removed, {original_size - optimized_size} bytes saved")
        
        return optimized_css
    
    def remove_debug_info(self, js: str, aggressive: bool = False) -> str:
        """
        Remove debug statements from JavaScript.
        
        Removes:
        - console.log, console.debug, console.info
        - console.warn, console.error (if aggressive)
        - debugger statements
        - Debug comments
        
        Args:
            js: JavaScript content
            aggressive: If True, also removes console.warn and console.error
            
        Returns:
            JavaScript with debug info removed
        """
        if not js:
            return ""
        
        original_size = len(js)
        
        # Remove console.log, console.debug, console.info
        patterns = [
            r'console\.(log|debug|info)\([^;]*\);?',
            r'debugger;?',
        ]
        
        if aggressive:
            patterns.extend([
                r'console\.(warn|error)\([^;]*\);?',
            ])
        
        for pattern in patterns:
            before = len(js)
            js = re.sub(pattern, '', js)
            after = len(js)
            if before > after:
                self.stats['debug_statements_removed'] += 1
        
        optimized_size = len(js)
        logger.debug(f"Debug info removed: {original_size - optimized_size} bytes saved")
        
        return js
    
    def strip_comments(self, content: str, content_type: str = 'html') -> str:
        """
        Strip comments from content.
        
        Args:
            content: Content to process
            content_type: Type of content (html, css, js)
            
        Returns:
            Content with comments removed
        """
        if not content:
            return ""
        
        original_count = self.stats['comments_removed']
        
        if content_type == 'html':
            # Remove HTML comments (preserve conditional comments)
            content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
        
        elif content_type == 'css':
            # Remove CSS comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        elif content_type == 'js':
            # Remove single-line comments (but preserve URLs)
            content = re.sub(r'//(?![:/]).*', '', content)
            # Remove multi-line comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        self.stats['comments_removed'] += 1
        
        return content
    
    def analyze_build_mode(self, mode: str) -> Dict:
        """
        Analyze build mode characteristics.
        
        Args:
            mode: Build mode (inline-all, external-assets, hybrid)
            
        Returns:
            Dictionary with mode characteristics
        """
        characteristics = {
            'inline-all': {
                'html_size': 'Large (180 KB)',
                'files': 1,
                'http_requests': 1,
                'offline': True,
                'best_for': 'PWA, offline-first apps',
                'strategy': 'Inline all CSS, JS, and assets'
            },
            'external-assets': {
                'html_size': 'Small (40 KB)',
                'files': '4-6',
                'http_requests': '5-7',
                'offline': False,
                'best_for': 'Traditional web apps with HTTP/2',
                'strategy': 'External CSS, JS, keep HTML minimal'
            },
            'hybrid': {
                'html_size': 'Medium (80 KB)',
                'files': '2-3',
                'http_requests': '3-4',
                'offline': 'Partial',
                'best_for': 'Performance-focused apps',
                'strategy': 'Inline critical CSS, external JS'
            }
        }
        
        return characteristics.get(mode, {})
    
    def get_stats(self) -> Dict:
        """Get optimization statistics."""
        return self.stats.copy()
    
    def print_stats(self) -> None:
        """Print optimization statistics."""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("⚡ Build Optimization Statistics")
        print("=" * 60)
        print(f"CSS rules removed:         {stats['css_rules_removed']}")
        print(f"CSS bytes saved:           {stats['css_bytes_saved']:,} bytes")
        print(f"Debug statements removed:  {stats['debug_statements_removed']}")
        print(f"Comments removed:          {stats['comments_removed']}")
        print("=" * 60)
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.stats = {
            'css_rules_removed': 0,
            'css_bytes_saved': 0,
            'debug_statements_removed': 0,
            'comments_removed': 0
        }


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_optimizer.py <command> [args]")
        print("Commands:")
        print("  unused-css <css_file> <html_file> - Remove unused CSS")
        print("  debug <js_file> - Remove debug info from JS")
        print("  analyze <mode> - Analyze build mode")
        sys.exit(1)
    
    command = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent
    optimizer = BuildOptimizer(base_path)
    
    if command == 'unused-css' and len(sys.argv) > 3:
        css_file = Path(sys.argv[2])
        html_file = Path(sys.argv[3])
        
        if not css_file.exists() or not html_file.exists():
            print("❌ File(s) not found")
            sys.exit(1)
        
        css = css_file.read_text(encoding='utf-8')
        html = html_file.read_text(encoding='utf-8')
        
        print(f"Removing unused CSS...")
        print(f"CSS: {css_file.name} ({len(css)} bytes)")
        print(f"HTML: {html_file.name} ({len(html)} bytes)")
        
        optimized = optimizer.remove_unused_css(css, html)
        
        print(f"✅ Optimized: {len(optimized)} bytes")
        optimizer.print_stats()
    
    elif command == 'debug' and len(sys.argv) > 2:
        js_file = Path(sys.argv[2])
        
        if not js_file.exists():
            print(f"❌ File not found: {js_file}")
            sys.exit(1)
        
        js = js_file.read_text(encoding='utf-8')
        
        print(f"Removing debug info from: {js_file.name}")
        print(f"Original: {len(js)} bytes")
        
        clean = optimizer.remove_debug_info(js)
        
        print(f"✅ Cleaned: {len(clean)} bytes")
        optimizer.print_stats()
    
    elif command == 'analyze' and len(sys.argv) > 2:
        mode = sys.argv[2]
        
        if mode not in BuildOptimizer.BUILD_MODES:
            print(f"❌ Invalid mode: {mode}")
            print(f"Valid modes: {', '.join(BuildOptimizer.BUILD_MODES)}")
            sys.exit(1)
        
        characteristics = optimizer.analyze_build_mode(mode)
        
        print(f"\n📊 Build Mode Analysis: {mode}")
        print("=" * 60)
        for key, value in characteristics.items():
            print(f"{key:20s}: {value}")
        print("=" * 60)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
