#!/usr/bin/env python3
"""
Test script to verify environment override functionality in config.json.

This test validates that:
1. Setting "environment": "development" forces dev mode
2. Setting "environment": "production" forces prod mode
3. Setting "environment": "auto" uses auto-detection
4. All environment-dependent settings follow the override
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path


class EnvironmentOverrideTester:
    """Tests environment override functionality"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path.cwd()
        
        # Add src to path for imports
        sys.path.insert(0, str(self.repo_root / 'src'))
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            print(f"✓ {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            return False
    
    def test_development_override(self):
        """Test that environment='development' forces dev mode"""
        print("\n1. Testing 'development' override:")
        
        # Create temporary config with development override
        temp_dir = Path(tempfile.mkdtemp())
        config_path = temp_dir / 'config.json'
        
        try:
            # Load base config
            with open(self.repo_root / 'config.json', 'r') as f:
                config = json.load(f)
            
            # Override to development
            config['environment'] = 'development'
            
            # Save temp config
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Load with utils (temporarily replace config path)
            from modules.utils import load_config
            
            # Capture stdout to check log message
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                loaded_config = load_config(temp_dir)
            
            output = f.getvalue()
            
            # Verify force message appears
            self.assert_test(
                '🎯 Environment forced to: development' in output,
                "Force message shown for development override"
            )
            
            # Verify development settings
            self.assert_test(
                loaded_config['debug'] == True,
                "debug=True in development mode",
                f"Expected True, got {loaded_config['debug']}"
            )
            
            self.assert_test(
                loaded_config['data']['source'] == 'both',
                "data.source='both' in development mode",
                f"Expected 'both', got {loaded_config['data']['source']}"
            )
            
            self.assert_test(
                loaded_config['watermark']['text'] == 'DEV',
                "watermark.text='DEV' in development mode",
                f"Expected 'DEV', got {loaded_config['watermark']['text']}"
            )
            
            self.assert_test(
                '[DEV]' in loaded_config['app']['name'],
                "app.name contains '[DEV]' in development mode",
                f"Expected [DEV] in name, got {loaded_config['app']['name']}"
            )
            
            self.assert_test(
                loaded_config['performance']['cache_enabled'] == False,
                "cache_enabled=False in development mode",
                f"Expected False, got {loaded_config['performance']['cache_enabled']}"
            )
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
    
    def test_production_override(self):
        """Test that environment='production' forces prod mode"""
        print("\n2. Testing 'production' override:")
        
        # Create temporary config with production override
        temp_dir = Path(tempfile.mkdtemp())
        config_path = temp_dir / 'config.json'
        
        try:
            # Load base config
            with open(self.repo_root / 'config.json', 'r') as f:
                config = json.load(f)
            
            # Override to production
            config['environment'] = 'production'
            
            # Save temp config
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Load with utils
            from modules.utils import load_config
            
            # Capture stdout to check log message
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                loaded_config = load_config(temp_dir)
            
            output = f.getvalue()
            
            # Verify force message appears
            self.assert_test(
                '🎯 Environment forced to: production' in output,
                "Force message shown for production override"
            )
            
            # Verify production settings
            self.assert_test(
                loaded_config['debug'] == False,
                "debug=False in production mode",
                f"Expected False, got {loaded_config['debug']}"
            )
            
            self.assert_test(
                loaded_config['data']['source'] == 'real',
                "data.source='real' in production mode",
                f"Expected 'real', got {loaded_config['data']['source']}"
            )
            
            self.assert_test(
                loaded_config['watermark']['text'] == 'PRODUCTION',
                "watermark.text='PRODUCTION' in production mode",
                f"Expected 'PRODUCTION', got {loaded_config['watermark']['text']}"
            )
            
            self.assert_test(
                '[DEV]' not in loaded_config['app']['name'],
                "app.name does not contain '[DEV]' in production mode",
                f"Expected no [DEV] in name, got {loaded_config['app']['name']}"
            )
            
            self.assert_test(
                loaded_config['performance']['cache_enabled'] == True,
                "cache_enabled=True in production mode",
                f"Expected True, got {loaded_config['performance']['cache_enabled']}"
            )
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
    
    def test_auto_detection(self):
        """Test that environment='auto' uses auto-detection"""
        print("\n3. Testing 'auto' detection:")
        
        # Create temporary config with auto detection
        temp_dir = Path(tempfile.mkdtemp())
        config_path = temp_dir / 'config.json'
        
        try:
            # Load base config
            with open(self.repo_root / 'config.json', 'r') as f:
                config = json.load(f)
            
            # Set to auto
            config['environment'] = 'auto'
            
            # Save temp config
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Load with utils
            from modules.utils import load_config
            
            # Capture stdout to check log message
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                loaded_config = load_config(temp_dir)
            
            output = f.getvalue()
            
            # Verify auto-detection message appears
            self.assert_test(
                '🚀 Environment auto-detected:' in output,
                "Auto-detection message shown when environment='auto'"
            )
            
            # In CI, should be production-like settings
            # We can't test specific values since they depend on actual environment
            self.assert_test(
                loaded_config['debug'] in (True, False),
                "debug is boolean (auto-detected correctly)"
            )
            
            self.assert_test(
                loaded_config['data']['source'] in ('real', 'both'),
                "data.source is valid (auto-detected correctly)",
                f"Expected 'real' or 'both', got {loaded_config['data']['source']}"
            )
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
    
    def test_default_is_auto(self):
        """Test that default config has environment='auto'"""
        print("\n4. Testing default config:")
        
        # Load real config
        with open(self.repo_root / 'config.json', 'r') as f:
            config = json.load(f)
        
        self.assert_test(
            'environment' in config,
            "environment field exists in config.json"
        )
        
        self.assert_test(
            config.get('environment') == 'auto',
            "Default environment is 'auto'",
            f"Expected 'auto', got {config.get('environment')}"
        )
    
    def run_all_tests(self):
        """Run all environment override tests"""
        print("=" * 70)
        print("Environment Override Tests")
        print("=" * 70)
        
        self.test_default_is_auto()
        self.test_development_override()
        self.test_production_override()
        self.test_auto_detection()
        
        # Summary
        print("\n" + "=" * 70)
        total_tests = self.tests_passed + self.tests_failed
        print(f"Tests Passed: {self.tests_passed}/{total_tests}")
        print(f"Tests Failed: {self.tests_failed}/{total_tests}")
        
        if self.tests_failed == 0:
            print("✓ All environment override tests passed!")
            print("=" * 70)
            return 0
        else:
            print("✗ Some tests failed. Please review the output above.")
            print("=" * 70)
            return 1


def main():
    """Main test entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test environment override functionality')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    tester = EnvironmentOverrideTester(verbose=args.verbose)
    return tester.run_all_tests()


if __name__ == '__main__':
    sys.exit(main())
