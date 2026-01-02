#!/usr/bin/env python3
"""
Test module for the linter functionality.

Validates that the linter correctly identifies issues in:
- JavaScript code
- CSS stylesheets
- HTML structure
- SVG content
- Translations
- Accessibility
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.linter import Linter, LintResult


def test_javascript_linting():
    """Test JavaScript linting"""
    print("\n" + "=" * 60)
    print("Testing JavaScript Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test valid JavaScript
    valid_js = """
    const greeting = "Hello, World!";
    console.log(greeting);
    function add(a, b) {
        return a + b;
    }
    """
    result = linter.lint_javascript(valid_js, "valid.js")
    assert result.passed, "Valid JavaScript should pass"
    print("✓ Valid JavaScript passed")
    
    # Test JavaScript with eval (should error)
    eval_js = """
    const code = "alert('test')";
    eval(code);
    """
    result = linter.lint_javascript(eval_js, "eval.js")
    assert not result.passed, "JavaScript with eval() should fail"
    assert any('eval' in error.lower() for error in result.errors)
    print("✓ JavaScript with eval() correctly flagged")
    
    # Test mismatched brackets
    bad_brackets_js = """
    function test() {
        if (true) {
            console.log("test");
        }
    """
    result = linter.lint_javascript(bad_brackets_js, "brackets.js")
    assert not result.passed, "JavaScript with mismatched brackets should fail"
    print("✓ Mismatched brackets correctly detected")
    
    # Test empty JavaScript
    result = linter.lint_javascript("", "empty.js")
    assert not result.passed, "Empty JavaScript should fail"
    print("✓ Empty JavaScript correctly flagged")
    
    print("\n✅ JavaScript linting tests passed")


def test_css_linting():
    """Test CSS linting"""
    print("\n" + "=" * 60)
    print("Testing CSS Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test valid CSS
    valid_css = """
    .container {
        display: flex;
        color: #333;
        background: #fff;
    }
    """
    result = linter.lint_css(valid_css, "valid.css")
    assert result.passed, "Valid CSS should pass"
    print("✓ Valid CSS passed")
    
    # Test mismatched braces
    bad_braces_css = """
    .container {
        display: flex;
    """
    result = linter.lint_css(bad_braces_css, "braces.css")
    assert not result.passed, "CSS with mismatched braces should fail"
    print("✓ Mismatched braces correctly detected")
    
    # Test empty CSS
    result = linter.lint_css("", "empty.css")
    assert not result.passed, "Empty CSS should fail"
    print("✓ Empty CSS correctly flagged")
    
    print("\n✅ CSS linting tests passed")


def test_html_linting():
    """Test HTML linting"""
    print("\n" + "=" * 60)
    print("Testing HTML Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test valid HTML
    valid_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Test Page</title>
    </head>
    <body>
        <h1>Hello World</h1>
    </body>
    </html>
    """
    result = linter.lint_html(valid_html)
    assert result.passed, "Valid HTML should pass"
    print("✓ Valid HTML passed")
    
    # Test HTML without doctype
    no_doctype_html = """
    <html>
    <head><title>Test</title></head>
    <body><h1>Hello</h1></body>
    </html>
    """
    result = linter.lint_html(no_doctype_html)
    assert not result.passed, "HTML without DOCTYPE should fail"
    assert any('doctype' in error.lower() for error in result.errors)
    print("✓ Missing DOCTYPE correctly flagged")
    
    # Test HTML without title
    no_title_html = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body><h1>Hello</h1></body>
    </html>
    """
    result = linter.lint_html(no_title_html)
    assert not result.passed, "HTML without title should fail"
    print("✓ Missing title correctly flagged")
    
    print("\n✅ HTML linting tests passed")


def test_svg_linting():
    """Test SVG linting"""
    print("\n" + "=" * 60)
    print("Testing SVG Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test valid SVG
    valid_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <circle cx="50" cy="50" r="40" fill="red"/>
    </svg>
    """
    result = linter.lint_svg(valid_svg, "valid.svg")
    assert result.passed, "Valid SVG should pass"
    print("✓ Valid SVG passed")
    
    # Test SVG with script tag
    script_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <script>alert('XSS')</script>
        <circle cx="50" cy="50" r="40" fill="red"/>
    </svg>
    """
    result = linter.lint_svg(script_svg, "script.svg")
    assert not result.passed, "SVG with script should fail"
    assert any('script' in error.lower() for error in result.errors)
    print("✓ SVG with script tag correctly flagged")
    
    # Test SVG with event handler
    onclick_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <circle cx="50" cy="50" r="40" fill="red" onclick="alert('XSS')"/>
    </svg>
    """
    result = linter.lint_svg(onclick_svg, "onclick.svg")
    assert not result.passed, "SVG with onclick should fail"
    print("✓ SVG with event handler correctly flagged")
    
    print("\n✅ SVG linting tests passed")


def test_translation_linting():
    """Test translation linting"""
    print("\n" + "=" * 60)
    print("Testing Translation Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test valid translations
    valid_trans = {
        "app": {"name": "Test App"},
        "filters": {"time": "Time"},
        "map": {"loading": "Loading..."},
        "events": {"title": "Events"}
    }
    result = linter.lint_translations(valid_trans, "en")
    assert result.passed, "Valid translations should pass"
    print("✓ Valid translations passed")
    
    # Test empty translations
    result = linter.lint_translations({}, "en")
    assert not result.passed, "Empty translations should fail"
    print("✓ Empty translations correctly flagged")
    
    # Test translation consistency
    trans_en = {
        "app": {"name": "Test", "version": "1.0"},
        "filters": {"time": "Time"}
    }
    trans_de = {
        "app": {"name": "Test"},
        "filters": {"time": "Zeit", "extra": "Extra"}
    }
    result = linter.lint_translation_consistency(trans_en, trans_de)
    # Should have warnings about missing keys
    assert len(result.warnings) > 0, "Inconsistent translations should have warnings"
    print("✓ Translation inconsistencies correctly detected")
    
    print("\n✅ Translation linting tests passed")


def test_accessibility_linting():
    """Test accessibility linting"""
    print("\n" + "=" * 60)
    print("Testing Accessibility Linting")
    print("=" * 60)
    
    linter = Linter(verbose=True)
    
    # Test HTML with good accessibility
    good_a11y_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Accessible Page</title>
    </head>
    <body>
        <h1>Main Title</h1>
        <img src="test.jpg" alt="Description">
        <a href="https://example.com">Link Text</a>
        <label for="name">Name:</label>
        <input type="text" id="name">
    </body>
    </html>
    """
    result = linter.lint_accessibility(good_a11y_html)
    # May have warnings but should generally be good
    print(f"✓ Good a11y HTML checked (errors: {len(result.errors)}, warnings: {len(result.warnings)})")
    
    # Test HTML without lang attribute
    no_lang_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body><h1>Hello</h1></body>
    </html>
    """
    result = linter.lint_accessibility(no_lang_html)
    assert not result.passed, "HTML without lang should fail"
    assert any('lang' in error.lower() for error in result.errors)
    print("✓ Missing lang attribute correctly flagged")
    
    # Test image without alt
    no_alt_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Test</title></head>
    <body>
        <img src="test.jpg">
    </body>
    </html>
    """
    result = linter.lint_accessibility(no_alt_html)
    assert not result.passed, "Image without alt should fail"
    print("✓ Missing alt text correctly flagged")
    
    print("\n✅ Accessibility linting tests passed")


def test_complete_lint():
    """Test complete linting workflow"""
    print("\n" + "=" * 60)
    print("Testing Complete Lint Workflow")
    print("=" * 60)
    
    linter = Linter(verbose=False)
    
    # Prepare test data
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Test App</title>
    </head>
    <body>
        <h1>Test Application</h1>
        <img src="test.jpg" alt="Test image">
    </body>
    </html>
    """
    
    stylesheets = {
        "main.css": ".container { display: flex; }"
    }
    
    scripts = {
        "app.js": "const app = { init: () => { console.log('App initialized'); } };"
    }
    
    translations_en = {
        "app": {"name": "Test"},
        "filters": {"time": "Time"}
    }
    
    translations_de = {
        "app": {"name": "Test"},
        "filters": {"time": "Zeit"}
    }
    
    svg_files = {
        "icon.svg": '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="5"/></svg>'
    }
    
    result = linter.lint_all(
        html_content=html_content,
        stylesheets=stylesheets,
        scripts=scripts,
        translations_en=translations_en,
        translations_de=translations_de,
        svg_files=svg_files
    )
    
    # Should pass overall (may have warnings)
    print(f"Complete lint result: {'PASS' if result.passed else 'FAIL'}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    
    print("\n✅ Complete lint workflow test passed")


def main():
    """Run all linter tests"""
    print("\n" + "=" * 60)
    print("🧪 LINTER TEST SUITE")
    print("=" * 60)
    
    try:
        test_javascript_linting()
        test_css_linting()
        test_html_linting()
        test_svg_linting()
        test_translation_linting()
        test_accessibility_linting()
        test_complete_lint()
        
        print("\n" + "=" * 60)
        print("✅ ALL LINTER TESTS PASSED")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
