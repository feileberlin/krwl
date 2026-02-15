#!/usr/bin/env python3
"""
Repository Cleanliness Validator

Checks for file clutter and enforces repository organization rules.
Run this before committing to ensure no clutter files are introduced.

Usage:
    python3 scripts/check_repository_cleanliness.py
    python3 scripts/check_repository_cleanliness.py --strict

Exit codes:
    0 - Repository is clean
    1 - Issues found (warnings)
    2 - Critical issues found (errors)
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Allowed markdown files in root directory
ALLOWED_ROOT_MD_FILES = {
    'README.md',
    'CHANGELOG.md'
}

# Patterns that indicate backup/clutter files
BACKUP_PATTERNS = [
    r'.*-old\.[^/]+$',
    r'.*-original\.[^/]+$',
    r'.*-backup\.[^/]+$',
    r'.*-refactored\.[^/]+$',
    r'.*_OLD\.[^/]+$',
    r'.*_BACKUP\.[^/]+$',
    r'.*\.backup$',
    r'.*\.bak$',
    r'.*\.tmp$',
]

# Files/patterns to exclude from backup checks (legitimate use cases)
BACKUP_PATTERN_EXCEPTIONS = [
    r'.*before-after\.(png|jpg|jpeg|gif)$',  # Comparison screenshots
    r'.*-comparison\.(png|jpg|jpeg|gif)$',   # Comparison images
]

# Summary/implementation file patterns (should be in docs/notes or docs/plans)
# Note: These patterns use ^ anchor for filename-only matching (not full paths).
# This is correct since we check root directory files using REPO_ROOT.iterdir()
# which only returns direct children (basenames), not subdirectories.
SUMMARY_PATTERNS = [
    r'.*_SUMMARY\.md$',
    r'.*_IMPLEMENTATION\.md$',
    r'.*_NOTES\.md$',
    r'.*SUMMARY.*\.md$',
    r'.*IMPLEMENTATION.*\.md$',
    r'.*NOTES.*\.md$',
    r'^AI_.*\.md$',
    r'^FEATURE_.*\.md$',
]

# Directories to exclude from checks
EXCLUDED_DIRS = {
    '.git',
    'node_modules',
    '__pycache__',
    'venv',
    '.venv',
    'archive',  # Archive is intentionally for old files
    'lib',       # Generated dependencies
    'public',    # Generated output
}


class CleanlinessChecker:
    """Validates repository cleanliness."""
    
    def __init__(self, strict=False):
        self.strict = strict
        self.warnings = []
        self.errors = []
    
    def check_backup_files(self) -> List[str]:
        """Find backup files that shouldn't exist."""
        issues = []
        
        for root, dirs, files in os.walk(REPO_ROOT):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for filename in files:
                filepath = Path(root) / filename
                relative_path = filepath.relative_to(REPO_ROOT)
                
                # Check if this is an exception (legitimate use)
                is_exception = False
                for exception_pattern in BACKUP_PATTERN_EXCEPTIONS:
                    if re.match(exception_pattern, filename):
                        is_exception = True
                        break
                
                if is_exception:
                    continue
                
                # Check against backup patterns
                for pattern in BACKUP_PATTERNS:
                    if re.match(pattern, filename):
                        issues.append(str(relative_path))
                        break
        
        return issues
    
    def check_root_summary_files(self) -> List[str]:
        """Find summary/implementation files in root that should be in docs/."""
        issues = []
        
        # Check root directory only
        for item in REPO_ROOT.iterdir():
            if not item.is_file():
                continue
            
            filename = item.name
            
            # Skip allowed files
            if filename in ALLOWED_ROOT_MD_FILES:
                continue
            
            # Check against summary patterns
            for pattern in SUMMARY_PATTERNS:
                if re.match(pattern, filename):
                    issues.append(filename)
                    break
        
        return issues
    
    def check_root_markdown_files(self) -> List[str]:
        """Find markdown files in root that should be in docs/."""
        issues = []
        
        # Check root directory only
        for item in REPO_ROOT.iterdir():
            if not item.is_file():
                continue
            
            filename = item.name
            
            # Only check .md files
            if not filename.endswith('.md'):
                continue
            
            # Skip allowed files
            if filename in ALLOWED_ROOT_MD_FILES:
                continue
            
            # Any other .md file in root is suspicious
            issues.append(filename)
        
        return issues
    
    def check_temp_files_in_repo(self) -> List[str]:
        """Find temporary files that shouldn't be committed."""
        issues = []
        temp_patterns = [
            r'.*~$',
            r'\.DS_Store$',
            r'Thumbs\.db$',
        ]
        
        for root, dirs, files in os.walk(REPO_ROOT):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for filename in files:
                filepath = Path(root) / filename
                relative_path = filepath.relative_to(REPO_ROOT)
                
                # Check against temp patterns
                for pattern in temp_patterns:
                    if re.match(pattern, filename):
                        issues.append(str(relative_path))
                        break
        
        return issues
    
    def run_all_checks(self) -> Tuple[int, str]:
        """Run all cleanliness checks and return exit code and report."""
        
        print("🧹 Checking repository cleanliness...\n")
        
        # Check 1: Backup files
        backup_files = self.check_backup_files()
        if backup_files:
            self.errors.append("❌ Found backup files (use git instead):")
            for f in backup_files:
                self.errors.append(f"   - {f}")
            self.errors.append("")
            self.errors.append("   Fix: Delete these files and use git history")
            self.errors.append("")
        
        # Check 2: Root summary files
        summary_files = self.check_root_summary_files()
        if summary_files:
            self.errors.append("❌ Found summary/implementation files in root:")
            for f in summary_files:
                self.errors.append(f"   - {f}")
            self.errors.append("")
            self.errors.append("   Fix: Move to docs/notes/ with date prefix:")
            self.errors.append("   mv FILE.md docs/notes/YYYY-MM-DD-description.md")
            self.errors.append("")
        
        # Check 3: Other markdown files in root
        root_md_files = self.check_root_markdown_files()
        if root_md_files:
            if self.strict:
                self.errors.append("❌ Found unexpected markdown files in root:")
                for f in root_md_files:
                    self.errors.append(f"   - {f}")
                self.errors.append("")
                self.errors.append("   Fix: Move to docs/ or docs/notes/ as appropriate")
                self.errors.append("")
            else:
                self.warnings.append("⚠️  Found markdown files in root (allowed but discouraged):")
                for f in root_md_files:
                    self.warnings.append(f"   - {f}")
                self.warnings.append("")
                self.warnings.append("   Consider: Move to docs/ for better organization")
                self.warnings.append("")
        
        # Check 4: Temp files
        temp_files = self.check_temp_files_in_repo()
        if temp_files:
            self.warnings.append("⚠️  Found temporary files:")
            for f in temp_files:
                self.warnings.append(f"   - {f}")
            self.warnings.append("")
            self.warnings.append("   Fix: Add to .gitignore or delete")
            self.warnings.append("")
        
        # Generate report
        report = self._generate_report()
        
        # Determine exit code
        if self.errors:
            exit_code = 2
        elif self.warnings:
            exit_code = 1
        else:
            exit_code = 0
        
        return exit_code, report
    
    def _generate_report(self) -> str:
        """Generate human-readable report."""
        lines = []
        
        if self.errors:
            lines.extend(self.errors)
        
        if self.warnings:
            lines.extend(self.warnings)
        
        if not self.errors and not self.warnings:
            lines.append("✅ Repository is clean!")
            lines.append("")
            lines.append("No backup files, summary files in root, or clutter detected.")
        
        return "\n".join(lines)


def main():
    """Main entry point."""
    strict = '--strict' in sys.argv
    
    checker = CleanlinessChecker(strict=strict)
    exit_code, report = checker.run_all_checks()
    
    print(report)
    
    if exit_code == 0:
        print("\n🎉 Repository cleanliness check passed!")
    elif exit_code == 1:
        print("\n⚠️  Warnings found (not blocking)")
    else:
        print("\n❌ Errors found - please fix before committing")
        print("\nSee .github/copilot-instructions.md → 'Repository Cleanliness' section")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
