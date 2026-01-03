#!/usr/bin/env python3
"""
Test Dashboard Implementation - KISS Principles

This test verifies that the dashboard implementation follows KISS principles:
- Replaces watermark with dashboard menu
- Single function responsible for dashboard updates
- No complex conditional logic
- Simple, predictable format
- Mobile-first and responsive
"""

import re
import sys
from pathlib import Path

def test_dashboard_implementation():
    """Verify dashboard implementation follows KISS principles and replaces watermark"""
    
    base_path = Path(__file__).parent.parent
    app_js_path = base_path / 'assets' / 'js' / 'app.js'
    style_css_path = base_path / 'assets' / 'css' / 'style.css'
    template_path = base_path / 'src' / 'templates' / 'index.html'
    
    print("=" * 60)
    print("Dashboard Implementation Tests")
    print("=" * 60)
    print()
    
    # Read files
    with open(app_js_path, 'r') as f:
        app_js = f.read()
    
    with open(style_css_path, 'r') as f:
        style_css = f.read()
    
    with open(template_path, 'r') as f:
        template_html = f.read()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: updateDashboard function exists (replaces updateWatermark)
    print("Test 1: updateDashboard() function exists")
    if 'updateDashboard()' in app_js and 'debug-environment' in app_js:
        print("✓ PASS: updateDashboard() function found")
        tests_passed += 1
    else:
        print("✗ FAIL: updateDashboard() function not found")
        tests_failed += 1
    print()
    
    # Test 2: Old watermark functions removed
    print("Test 2: Old watermark functions removed")
    watermark_func_pattern = re.compile(r'\bfunction\s+updateWatermark\s*\(|\bupdateWatermark\s*\(')
    has_old_watermark_function = bool(watermark_func_pattern.search(app_js))
    has_old_watermark_reference = 'environment-badge' in app_js
    if not has_old_watermark_function and not has_old_watermark_reference:
        print("✓ PASS: Old watermark functions removed")
        tests_passed += 1
    else:
        print("✗ FAIL: Old watermark functions still present")
        tests_failed += 1
    print()
    
    # Test 3: Dashboard HTML structure exists
    print("Test 3: Dashboard HTML structure in template")
    required_elements = ['id="dashboard-menu"', 'dashboard-content', 'close-dashboard']
    missing_elements = [elem for elem in required_elements if elem not in template_html]
    if not missing_elements:
        print("✓ PASS: Dashboard HTML structure found")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Missing elements: {', '.join(missing_elements)}")
        tests_failed += 1
    print()
    
    # Test 4: Dashboard CSS exists and watermark CSS removed
    print("Test 4: Dashboard CSS exists, watermark CSS removed")
    has_dashboard_css = '#dashboard-menu' in style_css and '.dashboard-content' in style_css
    no_watermark_css = '#environment-badge' not in style_css
    if has_dashboard_css and no_watermark_css:
        print("✓ PASS: Dashboard CSS present, watermark CSS removed")
        tests_passed += 1
    else:
        print("✗ FAIL: CSS not properly updated")
        tests_failed += 1
    print()
    
    # Test 5: Logo is clickable
    print("Test 5: Logo has click handler")
    if 'dashboardLogo.addEventListener' in app_js and 'dashboard-menu' in app_js:
        print("✓ PASS: Logo click handler found")
        tests_passed += 1
    else:
        print("✗ FAIL: Logo click handler not found")
        tests_failed += 1
    print()
    
    # Test 6: Mobile-first responsive CSS
    print("Test 6: Mobile-first responsive design")
    has_mobile_query = '@media (max-width: 768px)' in style_css or '@media (max-width: 480px)' in style_css
    if has_mobile_query:
        print("✓ PASS: Mobile media queries found")
        tests_passed += 1
    else:
        print("✗ FAIL: Mobile media queries not found")
        tests_failed += 1
    print()
    
    # Test 7: Keyboard accessibility
    print("Test 7: Keyboard accessibility (ESC, Enter, Space)")
    has_esc = 'Escape' in app_js and 'dashboard-menu' in app_js
    has_enter_space = 'Enter' in app_js or 'Space' in app_js
    if has_esc and has_enter_space:
        print("✓ PASS: Keyboard accessibility implemented")
        tests_passed += 1
    else:
        print("✗ FAIL: Keyboard accessibility incomplete")
        tests_failed += 1
    print()
    
    # Test 8: Dashboard sections present
    print("Test 8: Dashboard sections (About, Debug, Maintainer, Docs, Thanks)")
    sections = ['About', 'Debug Info', 'Maintainer', 'Documentation', 'Thanks To']
    missing_sections = [sec for sec in sections if sec not in template_html]
    if not missing_sections:
        print("✓ PASS: All dashboard sections found")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Missing sections: {', '.join(missing_sections)}")
        tests_failed += 1
    print()
    
    # Test 9: No watermark in template
    print("Test 9: Watermark element removed from template")
    if 'environment-badge' not in template_html:
        print("✓ PASS: Watermark element removed")
        tests_passed += 1
    else:
        print("✗ FAIL: Watermark element still in template")
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
    test_dashboard_implementation()

