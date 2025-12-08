#!/usr/bin/env python3
"""
KRWL HOF Feature Verification Script

This script verifies that all documented features in features.json are still
present in the codebase. It can be run locally or in CI to ensure features
don't get accidentally removed during refactoring.

Usage:
    python3 verify_features.py [--verbose] [--json]

Options:
    --verbose    Show detailed output for each feature check
    --json       Output results in JSON format
"""

import json
import os
import re
import sys
from pathlib import Path


class FeatureVerifier:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.repo_root = Path(__file__).parent
        self.features_file = self.repo_root / "features.json"
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
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
    
    def check_files_exist(self, feature):
        """Check if all required files for a feature exist"""
        files = feature.get("files", [])
        missing_files = []
        
        for file_path in files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.log(f"  ✗ Missing file: {file_path}", "ERROR")
            else:
                self.log(f"  ✓ Found file: {file_path}")
        
        return len(missing_files) == 0, missing_files
    
    def check_code_patterns(self, feature):
        """Check if code patterns exist in specified files"""
        patterns = feature.get("code_patterns", [])
        missing_patterns = []
        
        for pattern_spec in patterns:
            file_path = self.repo_root / pattern_spec["file"]
            pattern = pattern_spec["pattern"]
            description = pattern_spec.get("description", pattern)
            
            if not file_path.exists():
                missing_patterns.append({
                    "file": pattern_spec["file"],
                    "pattern": pattern,
                    "description": description,
                    "reason": "File not found"
                })
                self.log(f"  ✗ File not found: {pattern_spec['file']}", "ERROR")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(pattern, content):
                    self.log(f"  ✓ Found pattern in {pattern_spec['file']}: {description}")
                else:
                    missing_patterns.append({
                        "file": pattern_spec["file"],
                        "pattern": pattern,
                        "description": description,
                        "reason": "Pattern not found in file"
                    })
                    self.log(f"  ✗ Pattern not found in {pattern_spec['file']}: {description}", "ERROR")
            
            except Exception as e:
                missing_patterns.append({
                    "file": pattern_spec["file"],
                    "pattern": pattern,
                    "description": description,
                    "reason": f"Error reading file: {str(e)}"
                })
                self.log(f"  ✗ Error checking {pattern_spec['file']}: {str(e)}", "ERROR")
        
        return len(missing_patterns) == 0, missing_patterns
    
    def check_config_keys(self, feature):
        """Check if config keys are present in config files"""
        config_keys = feature.get("config_keys", [])
        if not config_keys:
            return True, []
        
        missing_keys = []
        config_files = ["config.dev.json", "config.prod.json"]
        
        for key in config_keys:
            found_in_any_config = False
            
            for config_file in config_files:
                config_path = self.repo_root / config_file
                if not config_path.exists():
                    continue
                
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Navigate nested keys (e.g., "filtering.max_distance_km")
                    keys = key.split('.')
                    value = config
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            value = None
                            break
                    
                    if value is not None:
                        found_in_any_config = True
                        self.log(f"  ✓ Found config key '{key}' in {config_file}")
                        break
                
                except Exception as e:
                    self.log(f"  ! Error reading {config_file}: {str(e)}", "WARN")
            
            if not found_in_any_config:
                missing_keys.append(key)
                self.log(f"  ✗ Config key not found: {key}", "ERROR")
        
        return len(missing_keys) == 0, missing_keys
    
    def verify_feature(self, feature):
        """Verify a single feature"""
        feature_id = feature.get("id", "unknown")
        feature_name = feature.get("name", feature_id)
        test_method = feature.get("test_method", "check_files_exist")
        
        self.log(f"\nVerifying feature: {feature_name} ({feature_id})")
        
        result = {
            "id": feature_id,
            "name": feature_name,
            "category": feature.get("category", "unknown"),
            "implemented": feature.get("implemented", False),
            "status": "unknown",
            "checks": []
        }
        
        all_passed = True
        
        # Always check if files exist
        if "files" in feature:
            files_exist, missing_files = self.check_files_exist(feature)
            result["checks"].append({
                "type": "files_exist",
                "passed": files_exist,
                "missing_files": missing_files
            })
            if not files_exist:
                all_passed = False
        
        # Check code patterns if specified
        if test_method == "check_code_patterns" and "code_patterns" in feature:
            patterns_found, missing_patterns = self.check_code_patterns(feature)
            result["checks"].append({
                "type": "code_patterns",
                "passed": patterns_found,
                "missing_patterns": missing_patterns
            })
            if not patterns_found:
                all_passed = False
        
        # Check config keys if specified
        if "config_keys" in feature:
            keys_found, missing_keys = self.check_config_keys(feature)
            result["checks"].append({
                "type": "config_keys",
                "passed": keys_found,
                "missing_keys": missing_keys
            })
            if not keys_found:
                all_passed = False
        
        result["status"] = "passed" if all_passed else "failed"
        return result
    
    def verify_all(self):
        """Verify all features in the registry"""
        print("=" * 60)
        print("KRWL HOF Feature Verification")
        print("=" * 60)
        
        feature_data = self.load_features()
        features = feature_data.get("features", [])
        
        print(f"\nLoaded {len(features)} features from registry")
        print(f"Registry version: {feature_data.get('version', 'unknown')}\n")
        
        self.results["total"] = len(features)
        
        for feature in features:
            result = self.verify_feature(feature)
            self.results["features"].append(result)
            
            if result["status"] == "passed":
                self.results["passed"] += 1
                status_icon = "✓"
            else:
                self.results["failed"] += 1
                status_icon = "✗"
            
            if not self.verbose:
                print(f"{status_icon} {result['name']} ({result['id']})")
        
        return self.results
    
    def print_summary(self, results):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total features: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        
        if results['failed'] > 0:
            print("\nFailed features:")
            for feature in results['features']:
                if feature['status'] == 'failed':
                    print(f"\n  ✗ {feature['name']} ({feature['id']})")
                    for check in feature['checks']:
                        if not check['passed']:
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
            print("\n✓ All features verified successfully!")
            return 0
        else:
            print(f"\n✗ {results['failed']} feature(s) failed verification")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify KRWL HOF features are present in codebase"
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
    
    args = parser.parse_args()
    
    verifier = FeatureVerifier(verbose=args.verbose)
    results = verifier.verify_all()
    
    if args.json:
        print("\n" + json.dumps(results, indent=2))
        sys.exit(0 if results['failed'] == 0 else 1)
    else:
        exit_code = verifier.print_summary(results)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
