#!/usr/bin/env python3
"""
Comprehensive Documentation Validator

Validates documentation for:
1. Structure compliance (unified standard)
2. Link validity (internal and external)
3. Code examples (syntax checking)
4. Cross-references (files/commands exist)
5. Completeness (features documented)

Usage:
    python3 scripts/test_documentation.py [--fix-links] [--skip-external]
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple
import urllib.request
import urllib.error


class DocumentationTester:
    """Comprehensive documentation testing"""
    
    def __init__(self, base_path: Path, skip_external: bool = False, verbose: bool = False):
        self.base_path = base_path
        self.skip_external = skip_external
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.checked_urls = {}  # Cache for external URL checks
    
    def test_all(self) -> bool:
        """Run all documentation tests"""
        print("=" * 70)
        print("🧪 COMPREHENSIVE DOCUMENTATION TESTS")
        print("=" * 70)
        
        all_passed = True
        
        # Find all markdown files
        md_files = self._find_markdown_files()
        print(f"\n📄 Found {len(md_files)} documentation files\n")
        
        for md_file in md_files:
            relative_path = md_file.relative_to(self.base_path)
            print(f"\n{'─' * 70}")
            print(f"📝 Testing: {relative_path}")
            print(f"{'─' * 70}")
            
            content = md_file.read_text(encoding='utf-8')
            
            # Test 1: Structure compliance
            passed, errors = self._test_structure(md_file, content)
            if not passed:
                all_passed = False
                self._print_test_result("Structure", False, errors)
            else:
                self._print_test_result("Structure", True, [])
            
            # Test 2: Internal links
            passed, errors = self._test_internal_links(md_file, content)
            if not passed:
                all_passed = False
                self._print_test_result("Internal Links", False, errors)
            else:
                self._print_test_result("Internal Links", True, [])
            
            # Test 3: External links (if not skipped)
            if not self.skip_external:
                passed, errors = self._test_external_links(content)
                if not passed:
                    all_passed = False
                    self._print_test_result("External Links", False, errors)
                else:
                    self._print_test_result("External Links", True, [])
            
            # Test 4: Code blocks syntax
            passed, errors = self._test_code_blocks(content)
            if not passed:
                all_passed = False
                self._print_test_result("Code Examples", False, errors)
            else:
                self._print_test_result("Code Examples", True, [])
            
            # Test 5: File references
            passed, errors = self._test_file_references(content)
            if not passed:
                all_passed = False
                self._print_test_result("File References", False, errors)
            else:
                self._print_test_result("File References", True, [])
            
            # Test 6: Command references
            passed, errors = self._test_command_references(content)
            if not passed:
                all_passed = False
                self._print_test_result("Commands", False, errors)
            else:
                self._print_test_result("Commands", True, [])
        
        # Test 7: Cross-documentation consistency
        print(f"\n{'=' * 70}")
        print("📊 Cross-Document Tests")
        print(f"{'=' * 70}\n")
        
        passed, errors = self._test_feature_coverage()
        if not passed:
            all_passed = False
            self._print_test_result("Feature Coverage", False, errors)
        else:
            self._print_test_result("Feature Coverage", True, [])
        
        # Summary
        print(f"\n{'=' * 70}")
        if all_passed:
            print("✅ All documentation tests PASSED!")
        else:
            print("❌ Some documentation tests FAILED")
            print("\n💡 Tip: Run with --verbose for detailed error messages")
        print(f"{'=' * 70}\n")
        
        return all_passed
    
    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown documentation files"""
        md_files = []
        exclude_patterns = ['node_modules', '.git', 'venv', 'env']
        
        for pattern in ['**/README.md', '**/*.md']:
            for file_path in self.base_path.rglob(pattern):
                if any(excl in str(file_path) for excl in exclude_patterns):
                    continue
                # Only include README.md and docs/*.md
                if file_path.name == 'README.md' or 'docs/' in str(file_path) or '.github/' in str(file_path):
                    md_files.append(file_path)
        
        return sorted(md_files)
    
    def _test_structure(self, file_path: Path, content: str) -> Tuple[bool, List[str]]:
        """Test structure compliance"""
        errors = []
        lines = content.split('\n')
        
        # Check H1
        h1_headers = [i for i, line in enumerate(lines) if line.startswith('# ') and not line.startswith('## ')]
        if len(h1_headers) != 1:
            errors.append(f"Must have exactly one H1 header, found {len(h1_headers)}")
        
        # Check description
        if h1_headers:
            h1_line = h1_headers[0]
            has_desc = False
            for i in range(h1_line + 1, min(h1_line + 5, len(lines))):
                if lines[i].strip().startswith('>'):
                    has_desc = True
                    break
            if not has_desc:
                errors.append("Missing one-line description (> blockquote after title)")
        
        # Check required sections
        required = ['## 🎯 Overview', '## 📦', '## 🚀']
        for section in required:
            if not any(section in line for line in lines):
                errors.append(f"Missing required section matching: {section}")
        
        return len(errors) == 0, errors
    
    def _test_internal_links(self, file_path: Path, content: str) -> Tuple[bool, List[str]]:
        """Test internal markdown links"""
        errors = []
        
        # Find all markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        matches = link_pattern.findall(content)
        
        for link_text, link_url in matches:
            # Skip external URLs
            if link_url.startswith('http://') or link_url.startswith('https://'):
                continue
            
            # Skip anchors
            if link_url.startswith('#'):
                continue
            
            # Skip mailto and other protocols
            if ':' in link_url and not link_url.startswith('.'):
                continue
            
            # Resolve relative path
            if link_url.startswith('/'):
                target = self.base_path / link_url.lstrip('/')
            else:
                target = (file_path.parent / link_url).resolve()
            
            # Check if file exists
            if not target.exists():
                errors.append(f"Broken link: [{link_text}]({link_url}) -> {target} not found")
        
        return len(errors) == 0, errors
    
    def _test_external_links(self, content: str) -> Tuple[bool, List[str]]:
        """Test external HTTP/HTTPS links"""
        errors = []
        
        # Find all external links
        link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)')
        matches = link_pattern.findall(content)
        
        for link_text, link_url in matches:
            # Skip if already checked
            if link_url in self.checked_urls:
                if not self.checked_urls[link_url]:
                    errors.append(f"Broken external link: [{link_text}]({link_url})")
                continue
            
            # Check URL
            try:
                req = urllib.request.Request(link_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.getcode()
                    self.checked_urls[link_url] = (200 <= status < 400)
                    if not self.checked_urls[link_url]:
                        errors.append(f"External link returned {status}: [{link_text}]({link_url})")
            except Exception as e:
                self.checked_urls[link_url] = False
                errors.append(f"Cannot reach external link: [{link_text}]({link_url}) - {e}")
        
        return len(errors) == 0, errors
    
    def _test_code_blocks(self, content: str) -> Tuple[bool, List[str]]:
        """Test code block syntax"""
        errors = []
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        for i, (lang, code) in enumerate(code_blocks):
            if not lang:
                errors.append(f"Code block #{i+1}: Missing language tag")
                continue
            
            # Test bash/shell syntax
            if lang in ['bash', 'sh', 'shell']:
                # Basic check: look for common syntax errors
                if '${' in code and not '}' in code:
                    errors.append(f"Code block #{i+1}: Unclosed ${{}}")
            
            # Test Python syntax
            elif lang == 'python':
                try:
                    compile(code, f'<code_block_{i+1}>', 'exec')
                except SyntaxError as e:
                    errors.append(f"Code block #{i+1}: Python syntax error: {e}")
            
            # Test JSON syntax
            elif lang == 'json':
                import json
                try:
                    json.loads(code)
                except json.JSONDecodeError as e:
                    errors.append(f"Code block #{i+1}: JSON syntax error: {e}")
        
        return len(errors) == 0, errors
    
    def _test_file_references(self, content: str) -> Tuple[bool, List[str]]:
        """Test that referenced files exist"""
        errors = []
        
        # Find file references in code blocks and inline code
        # Patterns: `path/to/file.py`, src/module.py, etc.
        patterns = [
            r'`([a-zA-Z0-9_\-./]+\.(py|js|json|md|css|html|sh))`',
            r'([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-./]+\.(py|js|json|md|css|html|sh))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                file_path = match[0] if isinstance(match, tuple) else match
                
                # Skip URLs
                if file_path.startswith('http'):
                    continue
                
                # Try to resolve path
                target = self.base_path / file_path
                if not target.exists():
                    # Try without leading slash
                    target = self.base_path / file_path.lstrip('/')
                    if not target.exists():
                        errors.append(f"Referenced file not found: {file_path}")
        
        return len(errors) == 0, errors
    
    def _test_command_references(self, content: str) -> Tuple[bool, List[str]]:
        """Test that referenced commands exist"""
        errors = []
        
        # Find python3 commands
        python_cmd_pattern = r'python3 (src/[a-zA-Z0-9_/.]+\.py)'
        matches = re.findall(python_cmd_pattern, content)
        
        for script_path in matches:
            target = self.base_path / script_path
            if not target.exists():
                errors.append(f"Referenced script not found: {script_path}")
        
        return len(errors) == 0, errors
    
    def _test_feature_coverage(self) -> Tuple[bool, List[str]]:
        """Test that all features are documented"""
        errors = []
        
        # Load features.json
        features_file = self.base_path / 'features.json'
        if not features_file.exists():
            errors.append("features.json not found")
            return False, errors
        
        import json
        with open(features_file) as f:
            features_data = json.load(f)
        
        features = features_data.get('features', [])
        
        # Load README
        readme = self.base_path / 'README.md'
        if readme.exists():
            readme_content = readme.read_text()
            
            # Check if features are mentioned
            documented_features = 0
            for feature in features:
                feature_name = feature.get('name', '')
                feature_id = feature.get('id', '')
                
                # Check if feature is mentioned in README
                if feature_name.lower() in readme_content.lower() or feature_id in readme_content.lower():
                    documented_features += 1
            
            coverage = (documented_features / len(features) * 100) if features else 0
            if coverage < 50:
                errors.append(f"Only {documented_features}/{len(features)} features documented ({coverage:.0f}%)")
        
        return len(errors) == 0, errors
    
    def _print_test_result(self, test_name: str, passed: bool, errors: List[str]):
        """Print test result"""
        if passed:
            print(f"  ✅ {test_name}")
        else:
            print(f"  ❌ {test_name} ({len(errors)} issues)")
            if self.verbose:
                for error in errors[:3]:  # Show first 3
                    print(f"     - {error}")
                if len(errors) > 3:
                    print(f"     ... and {len(errors) - 3} more")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test documentation validity')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed error messages')
    parser.add_argument('--skip-external', action='store_true', help='Skip external URL checks')
    parser.add_argument('path', nargs='?', default='.', help='Path to test (default: current directory)')
    
    args = parser.parse_args()
    
    base_path = Path(args.path).resolve()
    tester = DocumentationTester(base_path, skip_external=args.skip_external, verbose=args.verbose)
    
    passed = tester.test_all()
    
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
