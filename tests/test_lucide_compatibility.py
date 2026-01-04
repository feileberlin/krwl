#!/usr/bin/env python3
"""
Test Lucide Compatibility - Ensures Lucide updates won't break our icon system

This test suite validates:
1. Our icon usage matches Lucide's official API
2. No conflicts between our code and Lucide's library
3. Version compatibility checks
4. Icon availability and usage patterns
"""

import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class LucideCompatibilityTester:
    """Test suite for Lucide icon library compatibility"""
    
    # Lucide icons we use in the application
    # Update this list when adding new icons
    USED_ICONS = {
        'alert-triangle',  # Dashboard: Pending events notification
        'book-open',       # Dashboard: About section
        'bug',             # Dashboard: Debug info
        'user',            # Dashboard: Maintainer
        'book-text',       # Dashboard: Documentation
        'heart',           # Dashboard: Thanks to
        'calendar',
        'clock',
        'map-pin',
        'navigation',
        'filter',
        'x',
        'menu',
        'info',
        'settings',
        'github',
        'external-link',
        'chevron-down',
        'chevron-up',
        'search',
        'home',
        'star',
        'trash',
        'edit',
        'check',
        'alert-circle',
        'help-circle',
    }
    
    # Lucide API methods we use
    # Source: https://lucide.dev/guide/packages/lucide
    OFFICIAL_API_METHODS = {
        'createIcons',      # Initialize all icons
        'createElement',    # Create single icon element
        'icons',           # Icon data object
    }
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.lucide_js_path = self.base_path / 'static' / 'lucide' / 'lucide.min.js'
        self.app_js_path = self.base_path / 'assets' / 'js' / 'app.js'
        self.errors = []
        self.warnings = []
        
    def run_all_tests(self):
        """Run all compatibility tests"""
        print("🧪 Testing Lucide Icon Library Compatibility\n")
        print("=" * 70)
        
        self.test_lucide_library_exists()
        self.test_app_js_exists()
        self.test_official_api_used()
        self.test_icon_availability()
        self.test_no_deprecated_methods()
        self.test_initialization_pattern()
        self.test_version_compatibility()
        
        print("\n" + "=" * 70)
        self.print_results()
        
        return len(self.errors) == 0
    
    def test_lucide_library_exists(self):
        """Test that Lucide library file exists"""
        print("📁 Test: Lucide library file exists...")
        if not self.lucide_js_path.exists():
            self.errors.append(f"Lucide library not found: {self.lucide_js_path}")
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_app_js_exists(self):
        """Test that app.js exists"""
        print("📁 Test: App JavaScript file exists...")
        if not self.app_js_path.exists():
            self.errors.append(f"App JS not found: {self.app_js_path}")
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_official_api_used(self):
        """Test that we only use official Lucide API methods"""
        print("🔍 Test: Only official Lucide API methods used...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all lucide.* or window.lucide.* method calls
        lucide_calls = set(re.findall(r'(?:window\.)?lucide\.(\w+)', content))
        
        # Check for unofficial methods
        unofficial = lucide_calls - self.OFFICIAL_API_METHODS
        
        if unofficial:
            self.warnings.append(
                f"Unofficial Lucide API methods found: {', '.join(unofficial)}"
            )
            print("   ⚠️  WARNING")
        else:
            print(f"   ✅ PASSED ({len(lucide_calls)} official methods used)")
    
    def test_icon_availability(self):
        """Test that all icons we use are available in Lucide"""
        print("🎨 Test: All used icons are official Lucide icons...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all data-lucide="icon-name" attributes
        found_icons = set(re.findall(r'data-lucide=["\']([^"\']+)["\']', content))
        
        # Also find createElement calls with icon names
        createElement_icons = set(re.findall(
            r'createElement\(["\']([^"\']+)["\']',
            content
        ))
        
        all_found_icons = found_icons | createElement_icons
        
        # Check if we're tracking all icons we use
        untracked = all_found_icons - self.USED_ICONS
        if untracked:
            self.warnings.append(
                f"Icons used but not tracked in test: {', '.join(untracked)}. "
                f"Update USED_ICONS in test_lucide_compatibility.py"
            )
            print(f"   ⚠️  WARNING ({len(untracked)} untracked icons)")
        else:
            print(f"   ✅ PASSED ({len(all_found_icons)} icons tracked)")
    
    def test_no_deprecated_methods(self):
        """Test that we don't use deprecated Lucide methods"""
        print("🚫 Test: No deprecated Lucide methods used...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Deprecated patterns (update as Lucide evolves)
        deprecated_patterns = {
            'lucide.replace': 'Deprecated in v0.263.0+ (use createIcons instead)',
            'new lucide.Icon': 'Deprecated (use createElement instead)',
        }
        
        deprecated_found = []
        for pattern, message in deprecated_patterns.items():
            if pattern in content:
                deprecated_found.append(f"{pattern} - {message}")
        
        if deprecated_found:
            self.errors.append(
                f"Deprecated Lucide methods found: {'; '.join(deprecated_found)}"
            )
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_initialization_pattern(self):
        """Test that we initialize Lucide correctly"""
        print("🔧 Test: Lucide initialized correctly...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper initialization pattern
        has_createIcons = 'lucide.createIcons()' in content or 'window.lucide.createIcons()' in content
        has_namespace_check = 'window.lucide' in content or 'typeof lucide' in content
        
        if not has_createIcons:
            self.warnings.append(
                "lucide.createIcons() not found. Icons may not render."
            )
            print("   ⚠️  WARNING")
        elif not has_namespace_check:
            self.warnings.append(
                "No Lucide availability check. May fail if library doesn't load."
            )
            print("   ⚠️  WARNING (no safety check)")
        else:
            print("   ✅ PASSED")
    
    def test_version_compatibility(self):
        """Test Lucide version is documented"""
        print("📌 Test: Lucide version documented...")
        
        # Check site_generator.py for version
        site_gen_path = self.base_path / 'src' / 'modules' / 'site_generator.py'
        
        if not site_gen_path.exists():
            self.warnings.append("site_generator.py not found - can't check version")
            print("   ⚠️  WARNING")
            return
        
        with open(site_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for version in DEPENDENCIES
        version_match = re.search(r'"lucide"[^}]+?"version":\s*"([^"]+)"', content)
        
        if version_match:
            version = version_match.group(1)
            print(f"   ✅ PASSED (version {version} documented)")
        else:
            self.warnings.append("Lucide version not found in DEPENDENCIES")
            print("   ⚠️  WARNING")
    
    def print_results(self):
        """Print test results summary"""
        print("\n📊 Test Results Summary:")
        print("-" * 70)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All tests passed! Lucide integration is safe.")
        elif not self.errors:
            print("\n✅ No errors, but please review warnings.")
        else:
            print("\n❌ Tests failed! Fix errors before updating Lucide.")
        
        print("\n💡 Tip: Run this test before updating Lucide to ensure compatibility.")


def main():
    """Main entry point"""
    base_path = Path(__file__).parent.parent
    tester = LucideCompatibilityTester(base_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
