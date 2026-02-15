#!/usr/bin/env python3
"""
Tests for repository cleanliness validation script.

Tests coverage includes:
- Detection of each backup pattern
- Exception handling for legitimate files
- Proper directory exclusion
- Exit codes (0, 1, 2)
- Strict vs non-strict mode behavior
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.check_repository_cleanliness import CleanlinessChecker, REPO_ROOT


class TestCleanlinessChecker(unittest.TestCase):
    """Test suite for repository cleanliness validation."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_repo_root = REPO_ROOT
        # Patch REPO_ROOT for testing
        import scripts.check_repository_cleanliness as checker_module
        checker_module.REPO_ROOT = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        # Restore original REPO_ROOT
        import scripts.check_repository_cleanliness as checker_module
        checker_module.REPO_ROOT = self.original_repo_root
    
    def _create_file(self, relative_path, content="test"):
        """Helper to create a test file."""
        file_path = Path(self.test_dir) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    def test_clean_repository_returns_exit_code_0(self):
        """Test that a clean repository returns exit code 0."""
        # Create allowed files only
        self._create_file("README.md")
        self._create_file("CHANGELOG.md")
        self._create_file("src/main.py")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_backup_file_detection_dash_old(self):
        """Test detection of *-old.* backup files."""
        self._create_file("app-old.js")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("app-old.js", report)
        self.assertIn("backup files", report.lower())
    
    def test_backup_file_detection_dash_backup(self):
        """Test detection of *-backup.* files."""
        self._create_file("config-backup.json")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("config-backup.json", report)
    
    def test_backup_file_detection_dot_backup(self):
        """Test detection of *.backup files."""
        self._create_file("data.json.backup")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("data.json.backup", report)
    
    def test_backup_file_detection_dot_bak(self):
        """Test detection of *.bak files."""
        self._create_file("config.bak")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("config.bak", report)
    
    def test_backup_file_detection_dot_tmp(self):
        """Test detection of *.tmp files."""
        self._create_file("temp.tmp")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("temp.tmp", report)
    
    def test_backup_file_detection_underscore_old(self):
        """Test detection of *_OLD.* files."""
        self._create_file("script_OLD.py")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("script_OLD.py", report)
    
    def test_exception_for_before_after_screenshots(self):
        """Test that before-after comparison screenshots are allowed."""
        self._create_file("docs/screenshots/feature-before-after.png")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_exception_for_comparison_images(self):
        """Test that comparison images are allowed."""
        self._create_file("docs/screenshots/ui-comparison.jpg")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_archive_directory_excluded(self):
        """Test that archive directory is excluded from checks."""
        self._create_file("archive/old-file.js")
        self._create_file("archive/backup.bak")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_lib_directory_excluded(self):
        """Test that lib directory is excluded from checks."""
        self._create_file("lib/library-old.js")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_public_directory_excluded(self):
        """Test that public directory is excluded from checks."""
        self._create_file("public/build-old.html")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_root_summary_file_detection(self):
        """Test detection of summary files in root directory."""
        self._create_file("IMPLEMENTATION_SUMMARY.md")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("IMPLEMENTATION_SUMMARY.md", report)
        self.assertIn("summary", report.lower())
    
    def test_root_ai_file_detection(self):
        """Test detection of AI_* files in root directory."""
        self._create_file("AI_TRANSLATION_NOTES.md")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("AI_TRANSLATION_NOTES.md", report)
    
    def test_root_feature_file_detection(self):
        """Test detection of FEATURE_* files in root directory."""
        self._create_file("FEATURE_IMPLEMENTATION.md")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("FEATURE_IMPLEMENTATION.md", report)
    
    def test_allowed_root_markdown_files(self):
        """Test that README.md and CHANGELOG.md are allowed in root."""
        self._create_file("README.md")
        self._create_file("CHANGELOG.md")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_non_strict_mode_allows_other_markdown_in_root(self):
        """Test that non-strict mode allows other markdown files in root with warning."""
        self._create_file("README.md")
        self._create_file("CONTRIBUTING.md")  # Not in allowed list
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 1)  # Warning, not error
        self.assertIn("CONTRIBUTING.md", report)
        self.assertIn("⚠️", report)  # Warning symbol
    
    def test_strict_mode_blocks_other_markdown_in_root(self):
        """Test that strict mode blocks other markdown files in root."""
        self._create_file("README.md")
        self._create_file("CONTRIBUTING.md")  # Not in allowed list
        
        checker = CleanlinessChecker(strict=True)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)  # Error, not warning
        self.assertIn("CONTRIBUTING.md", report)
    
    def test_temp_file_detection_tilde(self):
        """Test detection of *~ temporary files."""
        self._create_file("file.txt~")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 1)  # Temp files are warnings
        self.assertIn("file.txt~", report)
    
    def test_temp_file_detection_ds_store(self):
        """Test detection of .DS_Store files."""
        self._create_file(".DS_Store")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 1)  # Temp files are warnings
        self.assertIn(".DS_Store", report)
    
    def test_multiple_issues_detected(self):
        """Test detection of multiple issues at once."""
        self._create_file("app-old.js")
        self._create_file("SUMMARY.md")
        self._create_file("temp.tmp")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)  # Errors take precedence
        self.assertIn("app-old.js", report)
        self.assertIn("SUMMARY.md", report)
        self.assertIn("temp.tmp", report)
    
    def test_docs_notes_files_allowed(self):
        """Test that files in docs/notes/ are allowed."""
        self._create_file("docs/notes/2026-02-15-implementation.md")
        self._create_file("docs/notes/SUMMARY.md")  # Even summary names are OK here
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_docs_plans_files_allowed(self):
        """Test that files in docs/plans/ are allowed."""
        self._create_file("docs/plans/20260215-feature-plan.md")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Repository is clean", report)
    
    def test_subdirectory_backup_files_detected(self):
        """Test that backup files in subdirectories are detected."""
        self._create_file("src/modules/scraper-old.py")
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)
        self.assertIn("scraper-old.py", report)
    
    def test_exit_code_precedence_errors_over_warnings(self):
        """Test that errors take precedence over warnings."""
        self._create_file("app-old.js")  # Error
        self._create_file(".DS_Store")  # Warning
        
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        self.assertEqual(exit_code, 2)  # Error code, not warning


class TestActualRepository(unittest.TestCase):
    """Test the actual repository for cleanliness."""
    
    def test_actual_repository_is_clean(self):
        """Test that the actual repository passes cleanliness checks."""
        checker = CleanlinessChecker(strict=False)
        exit_code, report = checker.run_all_checks()
        
        # Should be clean or at most have warnings
        self.assertIn(exit_code, [0, 1])
        
        if exit_code == 0:
            self.assertIn("Repository is clean", report)


def main():
    """Run tests with verbose output."""
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
