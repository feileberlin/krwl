#!/usr/bin/env python3
"""
Test Lucide Compatibility - Ensures Lucide inline implementation works correctly

This test suite validates:
1. Our icon usage matches the inline DASHBOARD_ICONS_MAP
2. No conflicts between our code and the minimal Lucide implementation
3. Icon availability and usage patterns
4. The inline implementation provides the expected API

Note: Since we no longer use the full Lucide CDN library, this test validates
the inline SVG implementation in lucide_markers.py and site_generator.py.
"""

import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class LucideCompatibilityTester:
    """Test suite for Lucide inline icon implementation compatibility"""
    
    # Lucide icons provided by our inline implementation (DASHBOARD_ICONS_MAP)
    # These are the only icons available in the minimal implementation
    INLINE_ICONS = {
        'alert-triangle',  # Dashboard: Pending events notification
        'book-open',       # Dashboard: About section
        'book-text',       # Dashboard: Documentation
        'bug',             # Dashboard: Debug info
        'git-commit',      # Dashboard: Git info
        'heart',           # Dashboard: Thanks to / Bookmarks
        'megaphone',       # Filter bar: Events button
        'user',            # Dashboard: Maintainer
    }
    
    # Lucide API methods we provide in our minimal implementation
    MINIMAL_API_METHODS = {
        'createIcons',      # Initialize all icons
        'icons',           # Icon data object
    }
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.app_js_path = self.base_path / 'assets' / 'js' / 'app.js'
        self.lucide_markers_path = self.base_path / 'src' / 'modules' / 'lucide_markers.py'
        self.errors = []
        self.warnings = []
        
    def run_all_tests(self):
        """Run all compatibility tests"""
        print("🧪 Testing Lucide Inline Icon Implementation Compatibility\n")
        print("=" * 70)
        
        self.test_lucide_markers_exists()
        self.test_app_js_exists()
        self.test_minimal_api_used()
        self.test_icon_availability()
        self.test_no_deprecated_methods()
        self.test_initialization_pattern()
        self.test_inline_icons_defined()
        
        print("\n" + "=" * 70)
        self.print_results()
        
        return len(self.errors) == 0
    
    def test_lucide_markers_exists(self):
        """Test that lucide_markers.py file exists"""
        print("📁 Test: Lucide markers module exists...")
        if not self.lucide_markers_path.exists():
            self.errors.append(f"Lucide markers not found: {self.lucide_markers_path}")
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
    
    def test_minimal_api_used(self):
        """Test that we only use methods available in our minimal API"""
        print("🔍 Test: Only minimal Lucide API methods used...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all lucide.* or window.lucide.* method calls
        lucide_calls = set(re.findall(r'(?:window\.)?lucide\.(\w+)', content))
        
        # Check for methods not in our minimal implementation
        unsupported = lucide_calls - self.MINIMAL_API_METHODS
        
        if unsupported:
            self.errors.append(
                f"API methods used but not in minimal implementation: {', '.join(unsupported)}. "
                f"Available methods: {', '.join(self.MINIMAL_API_METHODS)}"
            )
            print("   ❌ FAILED")
        else:
            print(f"   ✅ PASSED ({len(lucide_calls)} API methods used)")
    
    def test_icon_availability(self):
        """Test that all icons used are available in our inline implementation"""
        print("🎨 Test: All used icons are in inline implementation...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all data-lucide="icon-name" attributes
        found_icons = set(re.findall(r'data-lucide=["\']([^"\']+)["\']', content))
        
        # Check if any icons are used that aren't in our inline implementation
        unavailable = found_icons - self.INLINE_ICONS
        if unavailable:
            self.errors.append(
                f"Icons used but not in inline implementation: {', '.join(unavailable)}. "
                f"Add these to DASHBOARD_ICONS_MAP in lucide_markers.py"
            )
            print(f"   ❌ FAILED ({len(unavailable)} icons missing)")
        else:
            print(f"   ✅ PASSED ({len(found_icons)} icons available)")
    
    def test_no_deprecated_methods(self):
        """Test that we don't use deprecated Lucide methods"""
        print("🚫 Test: No deprecated Lucide methods used...")
        
        if not self.app_js_path.exists():
            return
        
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Deprecated patterns (these were never in our minimal implementation anyway)
        deprecated_patterns = {
            'lucide.replace': 'Deprecated (use createIcons instead)',
            'new lucide.Icon': 'Deprecated (not supported in minimal implementation)',
            'lucide.createElement': 'Not supported in minimal implementation',
        }
        
        deprecated_found = []
        for pattern, message in deprecated_patterns.items():
            if pattern in content:
                deprecated_found.append(f"{pattern} - {message}")
        
        if deprecated_found:
            self.errors.append(
                f"Deprecated/unsupported Lucide methods found: {'; '.join(deprecated_found)}"
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
    
    def test_inline_icons_defined(self):
        """Test that DASHBOARD_ICONS_MAP contains all expected icons"""
        print("📌 Test: Inline icons properly defined...")
        
        if not self.lucide_markers_path.exists():
            self.warnings.append("lucide_markers.py not found - can't check icons")
            print("   ⚠️  WARNING")
            return
        
        try:
            from modules.lucide_markers import DASHBOARD_ICONS_MAP
            
            # Check that all expected icons are present
            missing = self.INLINE_ICONS - set(DASHBOARD_ICONS_MAP.keys())
            
            if missing:
                self.errors.append(f"Missing icons in DASHBOARD_ICONS_MAP: {', '.join(missing)}")
                print("   ❌ FAILED")
            else:
                print(f"   ✅ PASSED ({len(DASHBOARD_ICONS_MAP)} icons defined)")
                
        except ImportError as e:
            self.warnings.append(f"Could not import lucide_markers: {e}")
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
            print("\n✅ All tests passed! Lucide inline implementation is working correctly.")
        elif not self.errors:
            print("\n✅ No errors, but please review warnings.")
        else:
            print("\n❌ Tests failed! Fix errors in lucide_markers.py or app.js.")
        
        print("\n💡 Tip: To add new icons, update DASHBOARD_ICONS_MAP in lucide_markers.py")


def main():
    """Main entry point"""
    base_path = Path(__file__).parent.parent
    tester = LucideCompatibilityTester(base_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
