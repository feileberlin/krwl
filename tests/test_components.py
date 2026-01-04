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
            configs, events, content_en, content_de,
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
        configs, events, content_en, content_de,
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
        configs, events, content_en, content_de,
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
    
    # Extract the button content to verify SVG is inside
    button_start = html.find('id="filter-bar-logo"')
    button_section = html[button_start:button_start+200]
    assert '<svg' in button_section, "Logo SVG missing from filter-nav component"
    print("✓ Logo SVG found in filter-nav component")
    
    print("✅ Logo SVG replacement validated")
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
        ("Logo SVG Replacement", test_logo_svg_replacement)
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
