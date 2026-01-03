#!/usr/bin/env python3
"""
Documentation Structure Validator

Validates that all README.md files follow the unified documentation standard.
See .github/DOCUMENTATION_STANDARD.md for the standard.

Usage:
    python3 scripts/validate_docs.py [--verbose] [--fix]
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


class DocValidator:
    """Validates documentation structure"""
    
    # Required sections (in order)
    REQUIRED_SECTIONS = [
        ('overview', r'## 🎯 Overview'),
        ('contents', r'## 📦 (What\'s Inside|Contents|Features)'),
        ('quickstart', r'## 🚀 (Quick Start|Usage|Getting Started)')
    ]
    
    # Standard emoji mapping
    EMOJI_MAP = {
        'overview': '🎯',
        'contents': '📦',
        'quickstart': '🚀',
        'detailed': '📚',
        'advanced': '🔧',
        'troubleshooting': '❓',
        'contributing': '🤝',
        'related': '📖'
    }
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single documentation file"""
        self.errors = []
        self.warnings = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Cannot read file: {e}")
            return False, self.errors, self.warnings
        
        lines = content.split('\n')
        
        # Check H1 header (must be exactly one)
        self._check_h1_header(lines, file_path.name)
        
        # Check one-line description
        self._check_description(lines)
        
        # Check required sections
        self._check_required_sections(content)
        
        # Check heading hierarchy
        self._check_heading_hierarchy(lines)
        
        # Check emoji consistency
        self._check_emoji_consistency(lines)
        
        # Check code blocks have language tags
        self._check_code_blocks(lines)
        
        # Check for anti-patterns
        self._check_anti_patterns(lines)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_h1_header(self, lines: List[str], filename: str):
        """Check for exactly one H1 header"""
        h1_headers = [i for i, line in enumerate(lines) if line.startswith('# ') and not line.startswith('## ')]
        
        if len(h1_headers) == 0:
            self.errors.append("Missing H1 header (# Title)")
        elif len(h1_headers) > 1:
            self.errors.append(f"Multiple H1 headers found (lines: {', '.join(str(i+1) for i in h1_headers)})")
        else:
            # Check if H1 is first non-empty line
            first_content_line = next((i for i, line in enumerate(lines) if line.strip()), 0)
            if h1_headers[0] != first_content_line:
                self.warnings.append("H1 header should be the first line")
    
    def _check_description(self, lines: List[str]):
        """Check for one-line description (blockquote after H1)"""
        h1_line = next((i for i, line in enumerate(lines) if line.startswith('# ') and not line.startswith('## ')), -1)
        
        if h1_line == -1:
            return  # Already reported by _check_h1_header
        
        # Look for blockquote in next few lines
        description_found = False
        for i in range(h1_line + 1, min(h1_line + 5, len(lines))):
            if lines[i].strip().startswith('>'):
                description_found = True
                break
            elif lines[i].strip() and not lines[i].startswith('[!['):  # Allow badges
                break
        
        if not description_found:
            self.errors.append("Missing one-line description (> blockquote after title)")
    
    def _check_required_sections(self, content: str):
        """Check for required sections"""
        for section_id, pattern in self.REQUIRED_SECTIONS:
            if not re.search(pattern, content, re.IGNORECASE):
                self.errors.append(f"Missing required section: {pattern}")
    
    def _check_heading_hierarchy(self, lines: List[str]):
        """Check heading hierarchy (no H4 or deeper)"""
        for i, line in enumerate(lines):
            if re.match(r'^#{4,}\s', line):  # H4 or deeper
                self.warnings.append(f"Line {i+1}: Heading too deep ({line[:50]}...) - use H3 maximum")
    
    def _check_emoji_consistency(self, lines: List[str]):
        """Check emoji usage in H2 headers"""
        h2_headers = [(i, line) for i, line in enumerate(lines) if re.match(r'^##\s', line)]
        
        for i, header in h2_headers:
            # H2 headers should have emoji
            if not re.match(r'^##\s[\U0001F300-\U0001F9FF]', header):
                self.warnings.append(f"Line {i+1}: H2 header missing emoji: {header}")
            
            # Check format: ## emoji space Title
            if not re.match(r'^##\s[\U0001F300-\U0001F9FF]\s+\w', header):
                self.warnings.append(f"Line {i+1}: H2 emoji format should be '## 🎯 Title': {header}")
    
    def _check_code_blocks(self, lines: List[str]):
        """Check code blocks have language tags"""
        in_code_block = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    # Check if language is specified
                    if line.strip() == '```':
                        self.warnings.append(f"Line {i+1}: Code block missing language tag (use ```bash, ```python, etc.)")
                else:
                    # Ending code block
                    in_code_block = False
    
    def _check_anti_patterns(self, lines: List[str]):
        """Check for common anti-patterns"""
        content = '\n'.join(lines)
        
        # Check for "click here" links
        if re.search(r'\[click here\]', content, re.IGNORECASE):
            self.warnings.append("Avoid 'click here' links - use descriptive link text")
        
        # Check for using # for lists instead of -
        for i, line in enumerate(lines):
            if re.match(r'^\s*#\s+[^\s]', line) and not line.startswith('#'):
                self.warnings.append(f"Line {i+1}: Use '-' for lists, not '#'")
    
    def validate_all(self, base_path: Path, exclude_patterns: List[str] = None) -> bool:
        """Validate all README.md files in the project"""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', '.git', 'venv', 'env']
        
        readme_files = []
        for pattern in ['**/README.md', '**/*.md']:
            for file_path in base_path.rglob(pattern):
                # Exclude patterns
                if any(excl in str(file_path) for excl in exclude_patterns):
                    continue
                # Only include README.md and docs/*.md
                if file_path.name == 'README.md' or 'docs/' in str(file_path):
                    readme_files.append(file_path)
        
        print("=" * 60)
        print("📚 Documentation Structure Validator")
        print("=" * 60)
        print(f"\nValidating {len(readme_files)} documentation files...\n")
        
        all_passed = True
        results = []
        
        for file_path in sorted(readme_files):
            relative_path = file_path.relative_to(base_path)
            passed, errors, warnings = self.validate_file(file_path)
            
            results.append((relative_path, passed, errors, warnings))
            
            if passed and not warnings:
                print(f"✅ {relative_path}")
            elif passed and warnings:
                print(f"⚠️  {relative_path} ({len(warnings)} warnings)")
                if self.verbose:
                    for warning in warnings:
                        print(f"      {warning}")
            else:
                print(f"❌ {relative_path} ({len(errors)} errors, {len(warnings)} warnings)")
                all_passed = False
                if self.verbose:
                    for error in errors:
                        print(f"      ERROR: {error}")
                    for warning in warnings:
                        print(f"      WARNING: {warning}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        
        total_errors = sum(len(r[2]) for r in results)
        total_warnings = sum(len(r[3]) for r in results)
        passed_count = sum(1 for r in results if r[1])
        
        print(f"Files checked: {len(results)}")
        print(f"✅ Passed: {passed_count}/{len(results)}")
        print(f"❌ Failed: {len(results) - passed_count}/{len(results)}")
        print(f"⚠️  Total warnings: {total_warnings}")
        print(f"❌ Total errors: {total_errors}")
        
        if all_passed:
            print("\n🎉 All documentation files are compliant!")
        else:
            print("\n⚠️  Some files need attention")
            print("See .github/DOCUMENTATION_STANDARD.md for the standard")
        
        print("=" * 60)
        
        return all_passed


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate documentation structure')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed errors and warnings')
    parser.add_argument('path', nargs='?', default='.', help='Path to validate (default: current directory)')
    
    args = parser.parse_args()
    
    base_path = Path(args.path).resolve()
    validator = DocValidator(verbose=args.verbose)
    
    passed = validator.validate_all(base_path)
    
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
