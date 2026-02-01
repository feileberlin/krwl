#!/usr/bin/env python3
"""
KRWL> Feature Verification Module

This module verifies that all documented features in features.json are still
present in the codebase. Designed for use in CI/CD and local development.

Supports three execution modes:
- CLI Mode: Non-interactive, scriptable (default)
- TUI Mode: Interactive menu-driven interface (--tui)
- Daemon Mode: Continuous monitoring with file watching (--daemon)
"""

import json
import os
import re
import sys
import time
import signal
from pathlib import Path


class FeatureVerifier:
    """Verifies presence of documented features in codebase"""
    
    # Default value for 'implemented' field in features.json
    DEFAULT_IMPLEMENTED = True
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.features_file = self.repo_root / "features.json"
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "features": []
        }
    
    def log(self, message, level="INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def load_features(self):
        """Load feature registry from features.json"""
        if not self.features_file.exists():
            print(f"ERROR: Feature registry not found at {self.features_file}")
            sys.exit(1)
        
        with open(self.features_file, 'r') as f:
            return json.load(f)
    
    def _check_single_file(self, file_path):
        """Check if a single file exists"""
        full_path = self.repo_root / file_path
        return full_path.exists()
    
    def check_files_exist(self, feature):
        """Check if all required files exist"""
        if 'files' not in feature:
            return True, []
        
        missing = [f for f in feature['files'] if not self._check_single_file(f)]
        return len(missing) == 0, missing
    
    def _search_pattern_in_file(self, file_path, pattern_str):
        """Search for a pattern in a file"""
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return False, "file not found"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = re.compile(pattern_str)
            if pattern.search(content):
                return True, None
            return False, "pattern not found"
        except Exception as e:
            return False, f"error reading file: {e}"
    
    def check_code_patterns(self, feature):
        """Check if code patterns exist in specified files"""
        if 'code_patterns' not in feature:
            return True, []
        
        missing = []
        for pattern_def in feature['code_patterns']:
            file_path = pattern_def['file']
            pattern = pattern_def['pattern']
            desc = pattern_def.get('description', pattern)
            
            found, reason = self._search_pattern_in_file(file_path, pattern)
            if not found:
                missing.append({
                    'file': file_path,
                    'pattern': pattern,
                    'description': desc,
                    'reason': reason
                })
        
        return len(missing) == 0, missing
    
    def _check_config_key_in_file(self, config_file, key):
        """Check if a config key exists in a JSON file"""
        full_path = self.repo_root / config_file
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Support nested keys like "map.center"
            keys = key.split('.')
            value = config
            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    return False
                value = value[k]
            return True
        except Exception:
            return False
    
    def check_config_keys(self, feature):
        """Check if required config keys exist"""
        if 'config_keys' not in feature:
            return True, []
        
        missing = []
        for key_def in feature['config_keys']:
            # Handle both string format and object format
            if isinstance(key_def, str):
                # Simple string format: "config.key"
                key = key_def
                # Check unified config file
                if not self._check_config_key_in_file('config.json', key):
                    missing.append(key)
            else:
                # Object format: {"file": "config.json", "key": "config.key"}
                file_path = key_def['file']
                key = key_def['key']
                if not self._check_config_key_in_file(file_path, key):
                    missing.append(f"{file_path}:{key}")
        
        return len(missing) == 0, missing
    
    def verify_feature(self, feature):
        """Verify a single feature"""
        feature_id = feature.get('id', 'unknown')
        feature_name = feature.get('name', 'Unknown')
        
        self.log(f"Verifying feature: {feature_name} ({feature_id})")
        
        result = {
            'id': feature_id,
            'name': feature_name,
            'category': feature.get('category', 'unknown'),
            'status': 'passed',
            'checks': []
        }
        
        # Check files
        files_exist, missing_files = self.check_files_exist(feature)
        result['checks'].append({
            'type': 'files',
            'passed': files_exist,
            'missing_files': missing_files
        })
        if not files_exist:
            result['status'] = 'failed'
            self.log(f"  Files check FAILED: {len(missing_files)} missing", "ERROR")
        else:
            self.log("  Files check PASSED")
        
        # Check code patterns
        patterns_found, missing_patterns = self.check_code_patterns(feature)
        result['checks'].append({
            'type': 'code_patterns',
            'passed': patterns_found,
            'missing_patterns': missing_patterns
        })
        if not patterns_found:
            result['status'] = 'failed'
            self.log(f"  Patterns check FAILED: {len(missing_patterns)} missing", "ERROR")
        else:
            self.log("  Patterns check PASSED")
        
        # Check config keys
        config_valid, missing_keys = self.check_config_keys(feature)
        result['checks'].append({
            'type': 'config',
            'passed': config_valid,
            'missing_keys': missing_keys
        })
        if not config_valid:
            result['status'] = 'failed'
            self.log(f"  Config check FAILED: {len(missing_keys)} missing", "ERROR")
        else:
            self.log("  Config check PASSED")
        
        return result
    
    def verify_all(self):
        """Verify all features from the registry"""
        data = self.load_features()
        features = data.get('features', [])
        
        self.results['total'] = len(features)
        
        for feature in features:
            # Skip features that are not implemented
            if not feature.get('implemented', self.DEFAULT_IMPLEMENTED):
                self.log(f"Skipping feature: {feature.get('name', 'Unknown')} (not implemented)")
                result = {
                    'id': feature.get('id', 'unknown'),
                    'name': feature.get('name', 'Unknown'),
                    'category': feature.get('category', 'unknown'),
                    'status': 'skipped',
                    'checks': []
                }
                self.results['features'].append(result)
                self.results['skipped'] += 1
                continue
            
            result = self.verify_feature(feature)
            self.results['features'].append(result)
            
            if result['status'] == 'passed':
                self.results['passed'] += 1
            else:
                self.results['failed'] += 1
        
        return self.results
    
    def print_summary(self, results):
        """Print human-readable summary"""
        print("=" * 60)
        print("Feature Verification Summary")
        print("=" * 60)
        
        skipped_count = results.get('skipped', 0)
        
        print(f"\nTotal Features: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped (Not Implemented): {skipped_count}")
        
        if skipped_count > 0:
            print("\nSkipped features (not implemented):")
            skipped_features = [f for f in results['features'] if f['status'] == 'skipped']
            for feature in skipped_features:
                print(f"  ⊝ {feature['name']} ({feature['id']})")
        
        if results['failed'] > 0:
            print("\nFailed features:")
            for feature in results['features']:
                if feature['status'] != 'failed':
                    continue
                
                print(f"\n  ✗ {feature['name']} ({feature['id']})")
                for check in feature['checks']:
                    if check['passed']:
                        continue
                    
                    print(f"    - {check['type']}: FAILED")
                    
                    if 'missing_files' in check and check['missing_files']:
                        for f in check['missing_files']:
                            print(f"      Missing file: {f}")
                    
                    if 'missing_patterns' in check and check['missing_patterns']:
                        for p in check['missing_patterns']:
                            print(f"      Missing pattern: {p['description']}")
                            print(f"        in {p['file']}: {p['reason']}")
                    
                    if 'missing_keys' in check and check['missing_keys']:
                        for k in check['missing_keys']:
                            print(f"      Missing config key: {k}")
        
        print("=" * 60)
        
        if results['failed'] == 0:
            if skipped_count > 0:
                print(f"\n✓ All implemented features verified successfully!")
                print(f"  ({skipped_count} feature(s) marked as not implemented)")
            else:
                print("\n✓ All features verified successfully!")
            return 0
        else:
            print(f"\n✗ {results['failed']} feature(s) failed verification")
            return 1


def run_tui(verifier):
    """Run interactive TUI mode for feature verification"""
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header():
        print("=" * 70)
        print("  KRWL> Feature Verifier - Interactive Mode")
        print("=" * 70)
        print()
    
    def print_footer(context="main"):
        """Print contextual help tooltips"""
        tooltips = {
            "main": "💡 Tip: Feature registry tracks 27 features | Use CLI mode for CI/CD automation",
            "verify": "💡 Tip: Verification checks file existence, code patterns, and config keys | Exit code 0 = all pass",
            "category": "💡 Tip: Categories: TUI, CLI, frontend, backend, deployment, testing, documentation",
            "missing": "💡 Tip: Missing features may indicate refactoring broke functionality | Check recent commits",
            "export": "💡 Tip: JSON exports can be parsed by CI/CD tools | Use for automated reports",
        }
        print()
        print("─" * 70)
        print(tooltips.get(context, tooltips["main"]))
        print("─" * 70)
    
    while True:
        clear_screen()
        print_header()
        print("Options:")
        print("-" * 70)
        print("1. Verify All Features")
        print("2. Verify Specific Feature Category")
        print("3. View Feature Registry")
        print("4. Check for Missing Features")
        print("5. Export Results to JSON")
        print("6. Exit")
        print("-" * 70)
        print_footer("main")
        print()
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == '1':
            clear_screen()
            print_header()
            print("Verifying all features...\n")
            results = verifier.verify_all()
            verifier.print_summary(results)
            print_footer("verify")
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            clear_screen()
            print_header()
            features_data = verifier.load_features()
            categories = list(features_data.get("features", {}).keys())
            
            print("Available categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            print_footer("category")
            print()
            
            try:
                cat_choice = int(input(f"Select category (1-{len(categories)}): ").strip())
                if 1 <= cat_choice <= len(categories):
                    category = categories[cat_choice - 1]
                    print(f"\nVerifying {category} features...\n")
                    results = verifier.verify_all()
                    # Filter results for selected category
                    filtered = {
                        k: v for k, v in results.items()
                        if k in ['total', 'passed', 'failed', 'features']
                    }
                    if 'features' in filtered:
                        filtered['features'] = [
                            f for f in filtered['features']
                            if f.get('category') == category
                        ]
                    verifier.print_summary(filtered)
                else:
                    print("Invalid selection")
            except (ValueError, IndexError):
                print("Invalid input")
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            clear_screen()
            print_header()
            features_data = verifier.load_features()
            print("Feature Registry:")
            print("-" * 70)
            for category, feats in features_data.get("features", {}).items():
                print(f"\n{category.upper()} ({len(feats)} features):")
                for feat in feats:
                    print(f"  • {feat.get('name', 'Unknown')}")
            print_footer("main")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            clear_screen()
            print_header()
            print("Checking for missing features...\n")
            results = verifier.verify_all()
            if results['failed'] > 0:
                print(f"Found {results['failed']} missing or broken features:\n")
                for feat in results['features']:
                    if feat['status'] == 'failed':
                        print(f"❌ {feat['name']}")
                        if feat.get('reason'):
                            print(f"   Reason: {feat['reason']}")
            else:
                print("✅ All features are present and working!")
            print_footer("missing")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            clear_screen()
            print_header()
            results = verifier.verify_all()
            filename = f"feature_verification_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results exported to: {filename}")
            print_footer("export")
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            print("\nExiting...")
            break
        
        else:
            print("Invalid option")
            time.sleep(1)


def run_daemon(verifier, interval=300, watch=False):
    """Run in daemon mode with continuous monitoring"""
    print(f"Starting Feature Verifier Daemon (interval: {interval}s, watch: {watch})")
    print("Press Ctrl+C to stop")
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\nShutting down daemon...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    last_check = 0
    iteration = 0
    
    while True:
        current_time = time.time()
        
        # Check if it's time to run
        if current_time - last_check >= interval:
            iteration += 1
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] Running verification check #{iteration}")
            
            results = verifier.verify_all()
            
            if results['failed'] > 0:
                print(f"⚠️  WARNING: {results['failed']} features failed verification")
                for feat in results['features']:
                    if feat['status'] == 'failed':
                        print(f"  ❌ {feat['name']}: {feat.get('reason', 'Unknown')}")
            else:
                print(f"✅ All {results['passed']} features verified successfully")
            
            last_check = current_time
        
        # Sleep for 1 second before checking again
        time.sleep(1)


def main():
    """Main entry point supporting CLI, TUI, and Daemon modes"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify KRWL> features are present in codebase"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each feature check"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Launch interactive TUI mode"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run in daemon mode (continuous monitoring)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds for daemon mode (default: 300)"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch file system for changes (daemon mode only)"
    )
    
    args = parser.parse_args()
    
    # Initialize verifier
    verifier = FeatureVerifier(
        repo_root=args.repo_root,
        verbose=args.verbose
    )
    
    # Launch appropriate mode
    if args.tui:
        # Interactive TUI mode
        run_tui(verifier)
        sys.exit(0)
    
    elif args.daemon:
        # Daemon mode
        run_daemon(verifier, interval=args.interval, watch=args.watch)
        sys.exit(0)
    
    else:
        # Standard CLI mode
        results = verifier.verify_all()
        
        if args.json:
            print("\n" + json.dumps(results, indent=2))
            sys.exit(0 if results['failed'] == 0 else 1)
        else:
            exit_code = verifier.print_summary(results)
            sys.exit(exit_code)



if __name__ == "__main__":
    main()
