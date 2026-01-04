#!/usr/bin/env python3
"""
Translation Completeness Test

Validates that all translation files are complete and consistent with the base English content.
Ensures no keys are missing and all placeholder variables match across languages.

This test should be run:
- Before committing changes to content files
- In CI/CD pipeline
- After adding new UI strings
- When adding new languages
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TranslationTester:
    """Tests translation file completeness and consistency"""
    
    def __init__(self, static_dir: str = "assets/json/i18n", verbose: bool = False):
        self.static_dir = Path(static_dir)
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.base_content = None
        self.translations = {}
        
    def log(self, message: str):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition: bool, test_name: str, error_msg: str = "") -> bool:
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
    
    def load_content_files(self) -> bool:
        """Load all content files"""
        print("\n=== Loading Content Files ===")
        
        # Load base English content
        base_file = self.static_dir / "content.json"
        if not base_file.exists():
            print(f"✗ Base content file not found: {base_file}")
            return False
        
        try:
            with open(base_file, 'r', encoding='utf-8') as f:
                self.base_content = json.load(f)
            print(f"✓ Loaded base content: content.json")
            self.log(f"  Locale: {self.base_content.get('locale', 'unknown')}")
        except Exception as e:
            print(f"✗ Error loading base content: {e}")
            return False
        
        # Load all translation files
        for content_file in self.static_dir.glob("content.*.json"):
            locale = content_file.stem.split('.')[-1]
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
                print(f"✓ Loaded translation: {content_file.name}")
                self.log(f"  Locale: {self.translations[locale].get('locale', 'unknown')}")
            except Exception as e:
                print(f"✗ Error loading {content_file.name}: {e}")
                return False
        
        if not self.translations:
            print("⚠️  Warning: No translation files found (content.*.json)")
        
        return True
    
    def get_all_keys(self, obj: Dict, prefix: str = "") -> Set[str]:
        """Recursively get all keys from nested dictionary"""
        keys = set()
        
        for key, value in obj.items():
            current_path = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recurse into nested objects
                keys.update(self.get_all_keys(value, current_path))
            else:
                # Leaf node - add the full path
                keys.add(current_path)
        
        return keys
    
    def get_value_by_path(self, obj: Dict, path: str):
        """Get value from nested dictionary by dot-separated path"""
        keys = path.split('.')
        value = obj
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def extract_placeholders(self, text: str) -> Set[str]:
        """Extract placeholder names from text like {variable}"""
        if not isinstance(text, str):
            return set()
        
        return set(re.findall(r'\{(\w+)\}', text))
    
    def test_json_validity(self) -> bool:
        """Test that all JSON files are valid"""
        print("\n=== Testing JSON Validity ===")
        
        all_valid = True
        
        # Test base content
        base_file = self.static_dir / "content.json"
        if base_file.exists():
            try:
                with open(base_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.assert_test(True, "Base content.json is valid JSON", "")
            except json.JSONDecodeError as e:
                self.assert_test(False, "Base content.json is valid JSON", str(e))
                all_valid = False
        
        # Test all translations
        for content_file in self.static_dir.glob("content.*.json"):
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.assert_test(True, f"{content_file.name} is valid JSON", "")
            except json.JSONDecodeError as e:
                self.assert_test(False, f"{content_file.name} is valid JSON", str(e))
                all_valid = False
        
        return all_valid
    
    def test_locale_field(self) -> bool:
        """Test that locale field matches filename"""
        print("\n=== Testing Locale Fields ===")
        
        all_correct = True
        
        # Test base content
        base_locale = self.base_content.get('locale')
        if self.assert_test(
            base_locale == 'en',
            "Base content has locale='en'",
            f"Expected 'en', got '{base_locale}'"
        ):
            pass
        else:
            all_correct = False
        
        # Test translations
        for locale, content in self.translations.items():
            file_locale = content.get('locale')
            if self.assert_test(
                file_locale == locale,
                f"Translation {locale} has correct locale field",
                f"Expected '{locale}', got '{file_locale}'"
            ):
                pass
            else:
                all_correct = False
        
        return all_correct
    
    def test_key_completeness(self) -> bool:
        """Test that all translations have all keys from base content"""
        print("\n=== Testing Key Completeness ===")
        
        base_keys = self.get_all_keys(self.base_content)
        self.log(f"Base content has {len(base_keys)} keys")
        
        all_complete = True
        
        for locale, translation in self.translations.items():
            translation_keys = self.get_all_keys(translation)
            self.log(f"Translation {locale} has {len(translation_keys)} keys")
            
            # Find missing keys
            missing_keys = base_keys - translation_keys
            extra_keys = translation_keys - base_keys
            
            if missing_keys:
                self.assert_test(
                    False,
                    f"Translation {locale} has all keys",
                    f"Missing {len(missing_keys)} keys: {', '.join(sorted(list(missing_keys)[:5]))}{'...' if len(missing_keys) > 5 else ''}"
                )
                all_complete = False
            else:
                self.assert_test(True, f"Translation {locale} has all keys", "")
            
            if extra_keys:
                self.log(f"Warning: Translation {locale} has {len(extra_keys)} extra keys: {', '.join(sorted(list(extra_keys)[:5]))}")
        
        return all_complete
    
    def test_placeholder_consistency(self) -> bool:
        """Test that placeholders match across translations"""
        print("\n=== Testing Placeholder Consistency ===")
        
        all_consistent = True
        
        for locale, translation in self.translations.items():
            base_keys = self.get_all_keys(self.base_content)
            
            inconsistent_keys = []
            
            for key in base_keys:
                base_value = self.get_value_by_path(self.base_content, key)
                trans_value = self.get_value_by_path(translation, key)
                
                if base_value is None or trans_value is None:
                    continue
                
                base_placeholders = self.extract_placeholders(base_value)
                trans_placeholders = self.extract_placeholders(trans_value)
                
                if base_placeholders != trans_placeholders:
                    inconsistent_keys.append({
                        'key': key,
                        'base': base_placeholders,
                        'trans': trans_placeholders
                    })
            
            if inconsistent_keys:
                examples = []
                for item in inconsistent_keys[:3]:
                    examples.append(
                        f"{item['key']}: base={{{','.join(item['base'])}}} vs trans={{{','.join(item['trans'])}}}"
                    )
                
                self.assert_test(
                    False,
                    f"Translation {locale} placeholders match",
                    f"Found {len(inconsistent_keys)} mismatches. Examples: {'; '.join(examples)}"
                )
                all_consistent = False
            else:
                self.assert_test(True, f"Translation {locale} placeholders match", "")
        
        return all_consistent
    
    def test_non_empty_values(self) -> bool:
        """Test that no translation values are empty strings"""
        print("\n=== Testing Non-Empty Values ===")
        
        all_non_empty = True
        
        # Check base content
        empty_in_base = []
        for key in self.get_all_keys(self.base_content):
            value = self.get_value_by_path(self.base_content, key)
            if isinstance(value, str) and value.strip() == "":
                empty_in_base.append(key)
        
        if empty_in_base:
            self.assert_test(
                False,
                "Base content has no empty strings",
                f"Found {len(empty_in_base)} empty values: {', '.join(empty_in_base[:5])}"
            )
            all_non_empty = False
        else:
            self.assert_test(True, "Base content has no empty strings", "")
        
        # Check translations
        for locale, translation in self.translations.items():
            empty_in_trans = []
            for key in self.get_all_keys(translation):
                value = self.get_value_by_path(translation, key)
                if isinstance(value, str) and value.strip() == "":
                    empty_in_trans.append(key)
            
            if empty_in_trans:
                self.assert_test(
                    False,
                    f"Translation {locale} has no empty strings",
                    f"Found {len(empty_in_trans)} empty values: {', '.join(empty_in_trans[:5])}"
                )
                all_non_empty = False
            else:
                self.assert_test(True, f"Translation {locale} has no empty strings", "")
        
        return all_non_empty
    
    def test_structure_consistency(self) -> bool:
        """Test that structure (nested objects) matches across translations"""
        print("\n=== Testing Structure Consistency ===")
        
        def get_structure(obj, prefix=""):
            """Get dictionary structure (keys and types)"""
            structure = {}
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    structure[path] = "object"
                    structure.update(get_structure(value, path))
                else:
                    structure[path] = type(value).__name__
            return structure
        
        base_structure = get_structure(self.base_content)
        
        all_consistent = True
        
        for locale, translation in self.translations.items():
            trans_structure = get_structure(translation)
            
            mismatches = []
            for key, base_type in base_structure.items():
                trans_type = trans_structure.get(key)
                if trans_type != base_type:
                    mismatches.append(f"{key}: {base_type} vs {trans_type}")
            
            if mismatches:
                self.assert_test(
                    False,
                    f"Translation {locale} structure matches base",
                    f"Found {len(mismatches)} type mismatches: {'; '.join(mismatches[:3])}"
                )
                all_consistent = False
            else:
                self.assert_test(True, f"Translation {locale} structure matches base", "")
        
        return all_consistent
    
    def test_icon_consistency(self) -> bool:
        """Test that emoji icons are not translated"""
        print("\n=== Testing Icon Consistency ===")
        
        all_consistent = True
        
        # Find all icon fields in base content
        icon_keys = [key for key in self.get_all_keys(self.base_content) if key.endswith('.icon')]
        
        self.log(f"Found {len(icon_keys)} icon fields")
        
        for locale, translation in self.translations.items():
            mismatched_icons = []
            
            for key in icon_keys:
                base_icon = self.get_value_by_path(self.base_content, key)
                trans_icon = self.get_value_by_path(translation, key)
                
                if base_icon != trans_icon:
                    mismatched_icons.append(f"{key}: '{base_icon}' vs '{trans_icon}'")
            
            if mismatched_icons:
                self.assert_test(
                    False,
                    f"Translation {locale} icons unchanged",
                    f"Found {len(mismatched_icons)} changed icons: {'; '.join(mismatched_icons[:3])}"
                )
                all_consistent = False
            else:
                self.assert_test(True, f"Translation {locale} icons unchanged", "")
        
        return all_consistent
    
    def generate_translation_report(self) -> str:
        """Generate a detailed translation status report"""
        report = []
        report.append("\n" + "=" * 70)
        report.append("Translation Completeness Report")
        report.append("=" * 70)
        
        base_keys = self.get_all_keys(self.base_content)
        report.append(f"\nBase content (English): {len(base_keys)} keys")
        
        for locale, translation in self.translations.items():
            translation_keys = self.get_all_keys(translation)
            missing_keys = base_keys - translation_keys
            extra_keys = translation_keys - base_keys
            
            report.append(f"\nTranslation: {locale}")
            report.append(f"  Total keys: {len(translation_keys)}")
            report.append(f"  Missing keys: {len(missing_keys)}")
            report.append(f"  Extra keys: {len(extra_keys)}")
            report.append(f"  Completeness: {((len(translation_keys) - len(extra_keys)) / len(base_keys) * 100):.1f}%")
            
            if missing_keys:
                report.append(f"  Missing: {', '.join(sorted(list(missing_keys)[:10]))}")
        
        report.append("\n" + "=" * 70)
        return '\n'.join(report)
    
    def run_all_tests(self) -> bool:
        """Run all translation tests"""
        print("=" * 70)
        print("Translation Completeness Test Suite")
        print("=" * 70)
        
        # Load content files
        if not self.load_content_files():
            print("\n✗ Failed to load content files")
            return False
        
        # Run all tests
        self.test_json_validity()
        self.test_locale_field()
        self.test_key_completeness()
        self.test_placeholder_consistency()
        self.test_non_empty_values()
        self.test_structure_consistency()
        self.test_icon_consistency()
        
        # Generate report
        if self.verbose:
            print(self.generate_translation_report())
        
        # Summary
        print("\n" + "=" * 70)
        print(f"Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
        print("=" * 70)
        
        return self.tests_failed == 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test translation file completeness and consistency',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test_translations.py
  python3 test_translations.py --verbose
  python3 test_translations.py --static-dir static
        """
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--static-dir',
        default='assets/json/i18n',
        help='Path to static directory containing content files (default: static)'
    )
    
    args = parser.parse_args()
    
    tester = TranslationTester(static_dir=args.static_dir, verbose=args.verbose)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
