#!/usr/bin/env python3
"""
Test Watermark Simplification - KISS Principles

This test verifies that the watermark implementation follows KISS principles:
- Single function responsible for watermark updates
- No complex conditional logic
- Always visible (no hiding)
- Simple, predictable format
"""

import re
import sys
from pathlib import Path

def test_watermark_simplification():
    """Verify watermark implementation follows KISS principles"""
    
    base_path = Path(__file__).parent.parent
    app_js_path = base_path / 'assets' / 'js' / 'app.js'
    style_css_path = base_path / 'assets' / 'css' / 'style.css'
    
    print("=" * 60)
    print("Watermark Simplification Tests")
    print("=" * 60)
    print()
    
    # Read files
    with open(app_js_path, 'r') as f:
        app_js = f.read()
    
    with open(style_css_path, 'r') as f:
        style_css = f.read()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: updateWatermark function exists
    print("Test 1: updateWatermark() function exists")
    if 'updateWatermark()' in app_js and 'watermark.textContent' in app_js:
        print("✓ PASS: updateWatermark() function found")
        tests_passed += 1
    else:
        print("✗ FAIL: updateWatermark() function not found")
        tests_failed += 1
    print()
    
    # Test 2: Old complex functions removed
    print("Test 2: Old complex functions removed")
    old_functions = ['displayEnvironmentWatermark', 'updateWatermarkFilterStats', 'updateLocationStatus']
    found_old = [fn for fn in old_functions if fn in app_js]
    if not found_old:
        print("✓ PASS: All old functions removed")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Found old functions: {', '.join(found_old)}")
        tests_failed += 1
    print()
    
    # Test 3: CSS simplified (no complex classes)
    print("Test 3: CSS simplified (no watermark-specific helper classes)")
    old_classes = ['.location-status', '.env-text', '.filter-stats', '#env-watermark.hidden', 
                   '#env-watermark.production', '#env-watermark.development']
    found_old_css = [cls for cls in old_classes if cls in style_css]
    if not found_old_css:
        print("✓ PASS: Old CSS classes removed")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Found old CSS classes: {', '.join(found_old_css)}")
        tests_failed += 1
    print()
    
    # Test 4: Simple watermark format with i18n support
    print("Test 4: Simple watermark format (ENVIRONMENT | X/Y eventWord) with i18n")
    # Check for the format pattern with eventWord variable (supports i18n)
    format_pattern = r'`\$\{.*\}\s*\|\s*\$\{.*\}/\$\{.*\}\s*\$\{.*\}`'
    has_format = re.search(format_pattern, app_js)
    # Also check for i18n usage
    has_i18n = 'window.i18n' in app_js and 'event_word' in app_js
    if has_format and has_i18n:
        print("✓ PASS: Simple format with i18n support found")
        tests_passed += 1
    else:
        print("✗ FAIL: Simple format with i18n support not found")
        tests_failed += 1
    print()
    
    # Test 5: Single watermark CSS rule (simplified)
    print("Test 5: Single simplified CSS rule for #env-watermark")
    # Count occurrences of #env-watermark in CSS (should be just 1 main rule)
    watermark_rules = style_css.count('#env-watermark')
    if watermark_rules <= 2:  # Allow for potential media query
        print(f"✓ PASS: Simplified CSS (found {watermark_rules} rule(s))")
        tests_passed += 1
    else:
        print(f"✗ FAIL: CSS not simplified (found {watermark_rules} rules)")
        tests_failed += 1
    print()
    
    # Test 6: No dynamic DOM manipulation for watermark
    print("Test 6: No dynamic DOM creation (createElement, appendChild)")
    watermark_section = app_js[app_js.find('updateWatermark'):app_js.find('updateWatermark') + 500]
    if 'createElement' not in watermark_section and 'appendChild' not in watermark_section:
        print("✓ PASS: No dynamic DOM manipulation")
        tests_passed += 1
    else:
        print("✗ FAIL: Dynamic DOM manipulation found")
        tests_failed += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")
    print("=" * 60)
    
    if tests_failed > 0:
        print()
        print("✗ Some tests failed")
        sys.exit(1)
    else:
        print()
        print("✓ All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    test_watermark_simplification()
