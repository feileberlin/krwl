#!/usr/bin/env python3
"""
Test module for component-based templating system.

Validates:
- Component loading
- Design token loading
- CSS generation
- HTML assembly
- Backward compatibility
- Semantic structure
- Z-index layering
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.site_generator import SiteGenerator


def test_component_loading():
    """Test that all components can be loaded"""
    print("\n" + "=" * 60)
    print("Testing Component Loading")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Test base components
    components = [
        'html-head.html',
        'html-body-open.html',
        'html-body-close.html',
        'map-main.html',
        'dashboard-aside.html',
        'filter-nav.html',
        'noscript-content.html'
    ]
    
    for component_path in components:
        try:
            content = generator.load_component(component_path)
            assert len(content) > 0, f"Component {component_path} is empty"
            print(f"✓ Loaded {component_path} ({len(content)} bytes)")
        except FileNotFoundError:
            print(f"✗ Component not found: {component_path}")
            return False
    
    print("✅ All components loaded successfully")
    return True


def test_design_tokens_loading():
    """Test design tokens load from config.json"""
    print("\n" + "=" * 60)
    print("Testing Design Tokens Loading")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Load design tokens
    design = generator.load_design_tokens()
    
    # Validate required sections
    required_sections = ['colors', 'typography', 'spacing', 'z_index', 
                        'shadows', 'borders', 'transitions', 'branding']
    
    for section in required_sections:
        assert section in design, f"Missing required section: {section}"
        print(f"✓ Found section: {section}")
    
    # Validate colors
    assert 'primary' in design['colors'], "Missing primary color"
    assert 'bg_primary' in design['colors'], "Missing bg_primary color"
    assert 'text_primary' in design['colors'], "Missing text_primary color"
    print(f"✓ Colors section has {len(design['colors'])} tokens")
    
    # Validate z-index
    assert 'layer_1_map' in design['z_index'], "Missing layer_1_map z-index"
    assert 'layer_3_ui' in design['z_index'], "Missing layer_3_ui z-index"
    print(f"✓ Z-index section has {len(design['z_index'])} tokens")
    
    print("✅ Design tokens loaded and validated")
    return True


def test_design_tokens_generation():
    """Test CSS generation from tokens"""
    print("\n" + "=" * 60)
    print("Testing CSS Generation")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Generate CSS
    css = generator.generate_design_tokens_css()
    
    assert len(css) > 0, "Generated CSS is empty"
    assert ':root {' in css, "Missing :root selector"
    assert '--color-primary:' in css, "Missing primary color variable"
    assert '--spacing-md:' in css, "Missing spacing variable"
    assert '--z-layer-3-ui:' in css, "Missing z-index variable"
    assert '--shadow-medium:' in css, "Missing shadow variable"
    assert '--border-radius-medium:' in css, "Missing border variable"
    assert '--transition-normal:' in css, "Missing transition variable"
    
    # Count CSS custom properties
    var_count = css.count('--')
    print(f"✓ Generated {var_count} CSS custom properties")
    print(f"✓ CSS size: {len(css) / 1024:.1f} KB")
    
    # Check for utility classes
    assert '.overlay {' in css, "Missing overlay utility class"
    assert '.overlay--layer-3 {' in css, "Missing layer-3 utility class"
    print("✓ Utility classes included")
    
    print("✅ CSS generation successful")
    return True


def test_html_assembly():
    """Test components assemble into valid HTML"""
    print("\n" + "=" * 60)
    print("Testing HTML Assembly")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Load minimal data for testing
    configs = [{'app': {'name': 'Test App'}}]
    events = []
    content_en = {'noscript': {'warning': 'JS disabled'}}
    content_de = {'noscript': {'warning': 'JS deaktiviert'}}
    stylesheets = {
        'roboto_fonts': '/* Roboto Fonts */',
        'leaflet_css': '/* Leaflet CSS */',
        'app_css': '/* App CSS */',
        'time_drawer_css': '/* Time Drawer CSS */'
    }
    scripts = {
        'leaflet_js': '// Leaflet JS',
        'i18n_js': '// i18n JS',
        'time_drawer_js': '// Time Drawer JS',
        'app_js': '// App JS',
        'lucide_js': '// Lucide JS'
    }
    marker_icons = {}
    
    # Build HTML
    try:
        html = generator.build_html_from_components(
            configs, events,
            stylesheets, scripts, marker_icons
        )
    except Exception as e:
        print(f"✗ HTML assembly failed: {e}")
        return False
    
    # Validate HTML structure
    assert '<!DOCTYPE html>' in html, "Missing DOCTYPE"
    assert '<html lang="en">' in html, "Missing html tag"
    assert '<head>' in html, "Missing head tag"
    assert '<body>' in html, "Missing body tag"
    assert '</html>' in html, "Missing closing html tag"
    print("✓ Valid HTML structure")
    
    # Validate design tokens inclusion
    assert '--color-primary:' in html, "Design tokens not included"
    print("✓ Design tokens included")
    
    # Validate semantic structure
    assert '<main id="map"' in html, "Missing main element"
    assert 'role="application"' in html, "Missing application role"
    assert '<aside id="dashboard-menu"' in html, "Missing aside element"
    assert 'role="complementary"' in html, "Missing complementary role"
    assert '<nav id="event-filter-bar"' in html, "Missing nav element"
    assert 'role="navigation"' in html, "Missing navigation role"
    print("✓ Semantic HTML5 structure")
    
    # Validate layer structure
    assert '<!-- Layer 1: Fullscreen map -->' in html, "Missing Layer 1 comment"
    assert '<!-- Layer 2: Event popups' in html, "Missing Layer 2 comment"
    assert '<!-- Layer 3: UI overlays -->' in html, "Missing Layer 3 comment"
    assert '<!-- Layer 4: Modals' in html, "Missing Layer 4 comment"
    print("✓ 4-layer architecture documented")
    
    # Validate ARIA attributes
    assert 'aria-label=' in html, "Missing ARIA labels"
    assert 'aria-hidden=' in html, "Missing aria-hidden"
    print("✓ ARIA attributes present")
    
    print(f"✓ Generated HTML size: {len(html) / 1024:.1f} KB")
    print("✅ HTML assembly successful")
    return True


def test_component_based_generation():
    """Test component-based HTML generation produces valid output"""
    print("\n" + "=" * 60)
    print("Testing Component-Based Generation")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Test that component-based generation produces valid HTML
    configs = [{'app': {'name': 'Test App'}}]
    events = []
    content_en = {'noscript': {'warning': 'JS disabled'}}
    content_de = {'noscript': {'warning': 'JS deaktiviert'}}
    stylesheets = {
        'roboto_fonts': '/* Roboto Fonts */',
        'leaflet_css': '/* Leaflet CSS */',
        'app_css': '/* App CSS */',
        'time_drawer_css': '/* Time Drawer CSS */'
    }
    scripts = {
        'leaflet_js': '// Leaflet JS',
        'i18n_js': '// i18n JS',
        'time_drawer_js': '// Time Drawer JS',
        'app_js': '// App JS',
        'lucide_js': '// Lucide JS'
    }
    marker_icons = {}
    
    # Build with components
    html_component = generator.build_html_from_components(
        configs, events,
        stylesheets, scripts, marker_icons
    )
    
    # Should be valid HTML
    assert '<!DOCTYPE html>' in html_component
    print("✓ Produces valid HTML")
    
    # Component version should have semantic structure
    assert '<main id="map"' in html_component
    print("✓ Has semantic structure")
    
    # Should have required elements
    for element in ['<head>', '<body>', 'window.APP_CONFIG', 'window.__INLINE_EVENTS_DATA__']:
        assert element in html_component, f"Missing {element} in component HTML"
    print("✓ Has all required elements")
    
    print("✅ Component-based generation validated")
    return True


def test_semantic_structure():
    """Test proper HTML5 semantic tags"""
    print("\n" + "=" * 60)
    print("Testing Semantic Structure")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Load components
    map_main = generator.load_component('map-main.html')
    dashboard = generator.load_component('dashboard-aside.html')
    filter_nav = generator.load_component('filter-nav.html')
    
    # Check semantic tags
    assert '<main' in map_main, "map-main.html should use <main> tag"
    assert 'role="application"' in map_main, "Map should have application role"
    print("✓ Map uses <main> with application role")
    
    assert '<aside' in dashboard, "dashboard should use <aside> tag"
    assert 'role="complementary"' in dashboard, "Dashboard should have complementary role"
    print("✓ Dashboard uses <aside> with complementary role")
    
    assert '<nav' in filter_nav, "filter bar should use <nav> tag"
    assert 'role="navigation"' in filter_nav, "Filter bar should have navigation role"
    print("✓ Filter bar uses <nav> with navigation role")
    
    print("✅ Semantic structure validated")
    return True


def test_z_index_layering():
    """Test 4-layer z-index system"""
    print("\n" + "=" * 60)
    print("Testing Z-Index Layering")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Load design tokens
    design = generator.load_design_tokens()
    z_index = design.get('z_index', {})
    
    # Check layer values
    assert z_index['layer_1_map'] == 0, "Layer 1 should be 0"
    assert 700 <= z_index['layer_2_leaflet_popup'] <= 1000, "Layer 2 should be 700-1000"
    assert 1500 <= z_index['layer_3_ui'] <= 1700, "Layer 3 should be 1500-1700"
    assert z_index['layer_4_modals'] >= 2000, "Layer 4 should be 2000+"
    
    print("✓ Layer 1 (map): z-index = 0")
    print("✓ Layer 2 (popups): z-index = 700-1000")
    print("✓ Layer 3 (UI): z-index = 1500-1700")
    print("✓ Layer 4 (modals): z-index = 2000+")
    
    # Generate CSS and check variables
    css = generator.generate_design_tokens_css()
    assert '--z-layer-1-map: 0;' in css
    assert '--z-layer-3-ui:' in css
    assert '--z-layer-4-modals:' in css
    print("✓ Z-index CSS variables generated")
    
    # Check overlay classes
    assert '.overlay--layer-3' in css
    assert '.overlay--layer-4' in css
    print("✓ Overlay utility classes generated")
    
    print("✅ Z-index layering validated")
    return True


def test_logo_svg_replacement():
    """Test that logo_svg placeholder is replaced in all components"""
    print("\n" + "=" * 60)
    print("Testing Logo SVG Replacement")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Load minimal data for testing
    configs = [{'app': {'name': 'Test App'}}]
    events = []
    content_en = {'noscript': {'warning': 'JS disabled'}}
    content_de = {'noscript': {'warning': 'JS deaktiviert'}}
    stylesheets = {
        'roboto_fonts': '/* Roboto Fonts */',
        'leaflet_css': '/* Leaflet CSS */',
        'app_css': '/* App CSS */',
        'time_drawer_css': '/* Time Drawer CSS */'
    }
    scripts = {
        'leaflet_js': '// Leaflet JS',
        'i18n_js': '// i18n JS',
        'time_drawer_js': '// Time Drawer JS',
        'app_js': '// App JS',
        'lucide_js': '// Lucide JS'
    }
    marker_icons = {}
    
    # Build HTML
    html = generator.build_html_from_components(
        configs, events,
        stylesheets, scripts, marker_icons
    )
    
    # Verify logo_svg placeholder is NOT present (should be replaced)
    assert '{logo_svg}' not in html, "Found unreplaced {logo_svg} placeholder in generated HTML"
    print("✓ No {logo_svg} placeholder found in generated HTML")
    
    # Verify logo SVG is present in dashboard-aside component
    assert '<div class="dashboard-logo"><svg' in html, "Logo SVG missing from dashboard-aside"
    print("✓ Logo SVG found in dashboard-aside component")
    
    # Verify logo SVG is present in filter-nav component (button with id="filter-bar-logo")
    assert 'id="filter-bar-logo"' in html, "Filter bar logo button missing"
    
    # Extract the button content to verify Lucide icon is inside
    button_start = html.find('id="filter-bar-logo"')
    button_section = html[button_start:button_start+300]
    assert 'data-lucide="megaphone"' in button_section, "Megaphone Lucide icon missing from filter-nav component"
    print("✓ Lucide megaphone icon found in filter-nav component")
    
    print("✅ Logo SVG replacement validated")
    return True


def test_repository_placeholders():
    """Test repository URL placeholder replacement"""
    print("\n" + "=" * 60)
    print("Testing Repository Placeholder Replacement")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    generator = SiteGenerator(base_path)
    
    # Test 1: All four placeholder types are correctly replaced
    print("\n1. Testing all placeholder types...")
    config = {
        'app': {
            'repository': {
                'owner': 'testowner',
                'name': 'testrepo',
                'url': 'https://github.com/testowner/testrepo'
            }
        }
    }
    
    test_content = """
    <a href="{{REPO_URL}}">Repository</a>
    <p>Owner: {{REPO_OWNER}}</p>
    <p>Name: {{REPO_NAME}}</p>
    <p>Full: {{REPO_OWNER_SLASH_NAME}}</p>
    """
    
    result = generator.replace_repository_placeholders(test_content, config)
    
    assert 'https://github.com/testowner/testrepo' in result, "{{REPO_URL}} not replaced"
    assert 'Owner: testowner' in result, "{{REPO_OWNER}} not replaced"
    assert 'Name: testrepo' in result, "{{REPO_NAME}} not replaced"
    assert 'Full: testowner/testrepo' in result, "{{REPO_OWNER_SLASH_NAME}} not replaced"
    assert '{{REPO' not in result, "Unreplaced placeholders found"
    print("✓ All four placeholder types replaced correctly")
    
    # Test 2: Placeholders work in both HTML and JavaScript contexts
    print("\n2. Testing placeholders in HTML context...")
    html_content = '<a href="{{REPO_URL}}/issues">Report Issue</a>'
    html_result = generator.replace_repository_placeholders(html_content, config)
    assert 'https://github.com/testowner/testrepo/issues' in html_result
    print("✓ HTML context works")
    
    print("3. Testing placeholders in JavaScript context...")
    js_content = "const repoUrl = '{{REPO_URL}}'; const owner = '{{REPO_OWNER}}';"
    js_result = generator.replace_repository_placeholders(js_content, config)
    assert "const repoUrl = 'https://github.com/testowner/testrepo'" in js_result
    assert "const owner = 'testowner'" in js_result
    print("✓ JavaScript context works")
    
    # Test 3: Fallback values are used when repository config is missing
    print("\n4. Testing fallback values with missing config...")
    empty_config = {}
    fallback_content = "{{REPO_URL}} {{REPO_OWNER}} {{REPO_NAME}}"
    fallback_result = generator.replace_repository_placeholders(fallback_content, empty_config)
    assert 'https://github.com/feileberlin/krwl.in' in fallback_result, "Default URL not used"
    assert 'feileberlin' in fallback_result, "Default owner not used"
    assert 'krwl.in' in fallback_result, "Default name not used"
    print("✓ Fallback values applied correctly")
    
    # Test 4: Multiple occurrences of the same placeholder are all replaced
    print("\n5. Testing multiple occurrences...")
    multi_content = """
    {{REPO_URL}}
    <a href="{{REPO_URL}}/issues">Issues</a>
    <a href="{{REPO_URL}}/pulls">PRs</a>
    Owner: {{REPO_OWNER}}, {{REPO_OWNER}}, {{REPO_OWNER}}
    """
    multi_result = generator.replace_repository_placeholders(multi_content, config)
    assert multi_result.count('https://github.com/testowner/testrepo') == 3, "Not all {{REPO_URL}} replaced"
    # Note: testowner appears in URLs (3x) AND standalone (3x) = 6 total
    assert multi_result.count('testowner') >= 3, "Not all {{REPO_OWNER}} replaced"
    assert '{{REPO' not in multi_result, "Some placeholders not replaced"
    print("✓ Multiple occurrences replaced correctly")
    
    # Test 5: Edge case - partial config
    print("\n6. Testing partial repository config...")
    partial_config = {
        'app': {
            'repository': {
                'owner': 'partialowner'
                # Missing 'name' and 'url'
            }
        }
    }
    partial_content = "{{REPO_URL}} {{REPO_OWNER}} {{REPO_NAME}}"
    partial_result = generator.replace_repository_placeholders(partial_content, partial_config)
    assert 'partialowner' in partial_result, "Partial owner not used"
    assert 'krwl.in' in partial_result, "Default name not used when missing"
    print("✓ Partial config handled correctly")
    
    # Test 6: Real-world scenario - dashboard HTML
    print("\n7. Testing real-world dashboard scenario...")
    dashboard_html = """
    <a href="{{REPO_URL}}/actions/workflows/scrape-events.yml">Review Events</a>
    <a href="{{REPO_URL}}/blob/main/README.md">README</a>
    <a href="{{REPO_URL}}">GitHub</a>
    """
    dashboard_result = generator.replace_repository_placeholders(dashboard_html, config)
    assert dashboard_result.count('https://github.com/testowner/testrepo') == 3
    assert '/actions/workflows/scrape-events.yml' in dashboard_result
    assert '/blob/main/README.md' in dashboard_result
    print("✓ Real-world dashboard scenario works")
    
    # Test 7: Empty content
    print("\n8. Testing empty content...")
    empty_result = generator.replace_repository_placeholders("", config)
    assert empty_result == "", "Empty content should remain empty"
    print("✓ Empty content handled correctly")
    
    # Test 8: Content with no placeholders
    print("\n9. Testing content without placeholders...")
    no_placeholder_content = "<p>Just regular HTML content</p>"
    no_placeholder_result = generator.replace_repository_placeholders(no_placeholder_content, config)
    assert no_placeholder_result == no_placeholder_content, "Content without placeholders should be unchanged"
    print("✓ Content without placeholders unchanged")
    
    print("\n✅ All placeholder replacement tests passed")
    return True


def run_all_tests():
    """Run all component tests"""
    print("=" * 60)
    print("🧪 COMPONENT TEMPLATING TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Component Loading", test_component_loading),
        ("Design Tokens Loading", test_design_tokens_loading),
        ("CSS Generation", test_design_tokens_generation),
        ("HTML Assembly", test_html_assembly),
        ("Component-Based Generation", test_component_based_generation),
        ("Semantic Structure", test_semantic_structure),
        ("Z-Index Layering", test_z_index_layering),
        ("Logo SVG Replacement", test_logo_svg_replacement),
        ("Repository Placeholders", test_repository_placeholders)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {test_name} FAILED")
        except AssertionError as e:
            failed += 1
            print(f"\n❌ {test_name} FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
