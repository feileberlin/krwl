#!/usr/bin/env python3
"""
KRWL HOF Test Runner Module

Centralized test execution system that integrates with the main application CLI.
Provides category-based test organization and flexible execution options.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class TestRunner:
    """Modular test runner for KRWL HOF
    
    Organizes tests into categories and provides flexible execution options:
    - Run all tests
    - Run tests by category (core, features, infrastructure)
    - Run individual tests
    - Verbose/quiet output modes
    - Test listing functionality
    """
    
    # Test organization by category
    TEST_CATEGORIES = {
        'core': [
            'test_scraper',
            'test_scrape_status',
            'test_timestamp_update',
            'test_filters',
            'test_event_schema',
        ],
        'features': [
            'test_translations',
            'test_bulk_operations',
            'test_rejected_events',
            'test_scheduler',
            'test_smart_scraper',
        ],
        'infrastructure': [
            'test_cdn_fallback',
            'test_dev_environment',
            'test_linter',
            'test_validation',
            'test_dependency_resilience',
            'test_dependency_url_construction',
            'test_leaflet_compatibility',
            'test_lucide_compatibility',
            'test_lucide_cdn',
            'test_components',
            'test_pending_count',
            'test_environment_override',
            'test_relative_times',
            'test_watermark_simplification',
        ],
    }
    
    def __init__(self, base_path: Path, verbose: bool = False):
        """Initialize test runner
        
        Args:
            base_path: Repository root path
            verbose: Enable verbose output
        """
        self.base_path = Path(base_path)
        self.tests_dir = self.base_path / 'tests'
        self.verbose = verbose
        
    def list_tests(self):
        """List all available test categories and tests"""
        print("\n" + "=" * 70)
        print("KRWL HOF Test Suite")
        print("=" * 70)
        
        total_tests = 0
        for category, tests in self.TEST_CATEGORIES.items():
            print(f"\n{category.upper()} ({len(tests)} tests):")
            print("-" * 70)
            for test in tests:
                test_file = self.tests_dir / f"{test}.py"
                status = "✓" if test_file.exists() else "✗"
                print(f"  {status} {test}")
                if test_file.exists():
                    total_tests += 1
        
        print("\n" + "=" * 70)
        print(f"Total: {total_tests} tests available")
        print("=" * 70)
        
    def run_single(self, test_name: str) -> bool:
        """Run a single test
        
        Args:
            test_name: Name of the test (e.g., 'test_scraper' or 'scraper')
            
        Returns:
            True if test passed, False otherwise
        """
        # Normalize test name
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        
        test_file = self.tests_dir / f"{test_name}.py"
        
        if not test_file.exists():
            print(f"\n✗ Test '{test_name}' not found")
            print(f"  Expected: {test_file}")
            print("\nUse 'test --list' to see available tests")
            return False
        
        print(f"\nRunning test: {test_name}")
        print("=" * 70)
        
        result = self._run_test_file(test_file)
        
        if result['success']:
            print(f"\n✓ Test '{test_name}' PASSED")
        else:
            print(f"\n✗ Test '{test_name}' FAILED")
            
        return result['success']
    
    def run_category(self, category: str) -> Dict:
        """Run all tests in a category
        
        Args:
            category: Category name ('core', 'features', 'infrastructure')
            
        Returns:
            Dictionary with test results
        """
        if category not in self.TEST_CATEGORIES:
            print(f"\n✗ Unknown test category: '{category}'")
            print(f"\nAvailable categories: {', '.join(self.TEST_CATEGORIES.keys())}")
            return {'success': False, 'results': []}
        
        tests = self.TEST_CATEGORIES[category]
        
        print(f"\nRunning {category.upper()} tests ({len(tests)} tests)")
        print("=" * 70)
        
        results = []
        for test_name in tests:
            test_file = self.tests_dir / f"{test_name}.py"
            
            if not test_file.exists():
                print(f"\n⚠ Skipping '{test_name}' (file not found)")
                results.append({
                    'name': test_name,
                    'success': False,
                    'skipped': True
                })
                continue
            
            result = self._run_test_file(test_file)
            result['name'] = test_name
            results.append(result)
        
        return self._print_summary(results, category)
    
    def run_all(self) -> bool:
        """Run all tests across all categories
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("\n" + "=" * 70)
        print("KRWL HOF Test Suite - Running All Tests")
        print("=" * 70)
        
        all_results = []
        
        for category in ['core', 'features', 'infrastructure']:
            print(f"\n{'=' * 70}")
            print(f"Category: {category.upper()}")
            print('=' * 70)
            
            tests = self.TEST_CATEGORIES[category]
            
            for test_name in tests:
                test_file = self.tests_dir / f"{test_name}.py"
                
                if not test_file.exists():
                    print(f"\n⚠ Skipping '{test_name}' (file not found)")
                    all_results.append({
                        'name': test_name,
                        'category': category,
                        'success': False,
                        'skipped': True
                    })
                    continue
                
                result = self._run_test_file(test_file)
                result['name'] = test_name
                result['category'] = category
                all_results.append(result)
        
        return self._print_summary(all_results, 'all')['success']
    
    def _run_test_file(self, test_file: Path) -> Dict:
        """Run a single test file
        
        Args:
            test_file: Path to test file
            
        Returns:
            Dictionary with test result
        """
        try:
            # Run test with appropriate verbosity
            cmd = [sys.executable, str(test_file)]
            if self.verbose:
                cmd.append('--verbose')
            
            # Run test and capture output
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout per test
            )
            
            # Print output if verbose or if test failed
            if self.verbose or result.returncode != 0:
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
            else:
                # In quiet mode, just show pass/fail
                test_name = test_file.stem
                if result.returncode == 0:
                    print(f"  ✓ {test_name}")
                else:
                    print(f"  ✗ {test_name}")
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'skipped': False
            }
            
        except subprocess.TimeoutExpired:
            print(f"\n✗ Test timed out after 60 seconds")
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test timed out',
                'skipped': False
            }
        except Exception as e:
            print(f"\n✗ Error running test: {e}")
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'skipped': False
            }
    
    def _print_summary(self, results: List[Dict], scope: str) -> Dict:
        """Print test results summary
        
        Args:
            results: List of test results
            scope: Scope of tests ('all' or category name)
            
        Returns:
            Dictionary with overall success status
        """
        total = len(results)
        passed = sum(1 for r in results if r['success'] and not r.get('skipped', False))
        failed = sum(1 for r in results if not r['success'] and not r.get('skipped', False))
        skipped = sum(1 for r in results if r.get('skipped', False))
        
        print("\n" + "=" * 70)
        print(f"Test Summary: {scope.upper()}")
        print("=" * 70)
        print(f"  Total:   {total}")
        print(f"  Passed:  {passed}")
        print(f"  Failed:  {failed}")
        print(f"  Skipped: {skipped}")
        
        # List failed tests
        if failed > 0:
            print("\nFailed tests:")
            for result in results:
                if not result['success'] and not result.get('skipped', False):
                    print(f"  ✗ {result['name']}")
        
        # List skipped tests
        if skipped > 0:
            print("\nSkipped tests:")
            for result in results:
                if result.get('skipped', False):
                    print(f"  ⚠ {result['name']}")
        
        print("=" * 70)
        
        success = failed == 0 and skipped == 0
        
        if success:
            print("✓ All tests PASSED!")
        else:
            print("✗ Some tests FAILED or were SKIPPED")
        
        return {
            'success': success,
            'results': results,
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped
        }


def main():
    """Main entry point for standalone testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KRWL HOF Test Runner')
    parser.add_argument('category', nargs='?', default=None,
                       help='Test category or test name to run')
    parser.add_argument('--list', action='store_true',
                       help='List all available tests')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get repository root (go up two levels from src/modules/)
    base_path = Path(__file__).parent.parent.parent
    
    runner = TestRunner(base_path, verbose=args.verbose)
    
    # List tests
    if args.list:
        runner.list_tests()
        return 0
    
    # Run specific category or test
    if args.category:
        # Check if it's a category
        if args.category in runner.TEST_CATEGORIES:
            result = runner.run_category(args.category)
            return 0 if result['success'] else 1
        # Otherwise try as individual test
        else:
            return 0 if runner.run_single(args.category) else 1
    
    # Run all tests
    return 0 if runner.run_all() else 1


if __name__ == "__main__":
    sys.exit(main())
