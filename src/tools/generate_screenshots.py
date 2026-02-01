#!/usr/bin/env python3
"""
Generate PWA screenshots for KRWL> Events from here til sunrise app.

FEATURE: Screenshot Generation with App Ready Signal
PURPOSE: Capture reliable screenshots after the app is fully initialized
         (config loaded, map initialized, events loaded, map tiles rendered)

HOW IT WORKS:
This script uses Playwright to:
1. Navigate to the app URL
2. Wait for the app-ready signal (body[data-app-ready="true"] attribute)
3. Wait additional 2 seconds for map tiles to finish loading
4. Capture screenshots at mobile (640×1136) and desktop (1280×800) sizes

APP READY SIGNAL:
The frontend emits a ready signal via two methods:
1. Body attribute: <body data-app-ready="true">
2. Custom event: window 'app-ready' event with metadata

This signal is emitted after all async operations complete:
- Config loaded
- Map initialized
- Geolocation requested (or skipped)
- Events loaded and processed
- Event listeners set up

Note: Map tiles load asynchronously after the ready signal, hence the 2s wait.

REQUIREMENTS:
    pip install playwright
    playwright install chromium

USAGE:
    python3 scripts/generate_screenshots.py
    python3 scripts/generate_screenshots.py --url http://localhost:8000
    python3 scripts/generate_screenshots.py --output-dir assets --verbose

OTHER AUTOMATION TOOLS:
This pattern works with any browser automation tool:
- Playwright (Python/Node.js) - Used in this script
- Puppeteer (Node.js) - Similar API
- Selenium (Python/Java/etc.) - Via WebDriverWait for selector

For examples with other tools, see README.md section "Advanced Features > Screenshot Generation"
"""

import argparse
import sys
from pathlib import Path

def check_playwright():
    """Check if Playwright is installed"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("❌ Playwright is not installed.")
        print("\nTo install:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

def generate_screenshots(url='http://localhost:8000', output_dir='assets', verbose=False):
    """Generate mobile and desktop screenshots"""
    
    if not check_playwright():
        return False
    
    from playwright.sync_api import sync_playwright
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            if verbose:
                print("🚀 Launching browser...")
            browser = p.chromium.launch(headless=True)
            
            # Mobile screenshot (narrow form factor)
            print("\n📱 Generating mobile screenshot...")
            print(f"   Size: 640×1136 (narrow form factor)")
            page_mobile = browser.new_page()
            page_mobile.set_viewport_size({"width": 640, "height": 1136})
            
            if verbose:
                print(f"   Navigating to {url}...")
            page_mobile.goto(url, timeout=30000)
            
            if verbose:
                print("   Waiting for app-ready signal...")
            page_mobile.wait_for_selector('body[data-app-ready="true"]', timeout=30000)
            
            if verbose:
                print("   Waiting for map tiles to load...")
            page_mobile.wait_for_timeout(2000)  # Wait for map tiles
            
            mobile_path = output_path / 'screenshot-mobile.png'
            page_mobile.screenshot(path=str(mobile_path))
            page_mobile.close()
            print(f"   ✅ Saved: {mobile_path}")
            
            # Desktop screenshot (wide form factor)
            print("\n🖥️  Generating desktop screenshot...")
            print(f"   Size: 1280×800 (wide form factor)")
            page_desktop = browser.new_page()
            page_desktop.set_viewport_size({"width": 1280, "height": 800})
            
            if verbose:
                print(f"   Navigating to {url}...")
            page_desktop.goto(url, timeout=30000)
            
            if verbose:
                print("   Waiting for app-ready signal...")
            page_desktop.wait_for_selector('body[data-app-ready="true"]', timeout=30000)
            
            if verbose:
                print("   Waiting for map tiles to load...")
            page_desktop.wait_for_timeout(2000)  # Wait for map tiles
            
            desktop_path = output_path / 'screenshot-desktop.png'
            page_desktop.screenshot(path=str(desktop_path))
            page_desktop.close()
            print(f"   ✅ Saved: {desktop_path}")
            
            browser.close()
            
            print("\n✅ All screenshots generated successfully!")
            print(f"\n📁 Output directory: {output_path.absolute()}")
            print(f"   • {mobile_path.name} (640×1136)")
            print(f"   • {desktop_path.name} (1280×800)")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error generating screenshots: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Generate PWA screenshots for KRWL> Events from here til sunrise',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate screenshots from local server
  python3 scripts/generate_screenshots.py
  
  # Specify custom URL
  python3 scripts/generate_screenshots.py --url http://localhost:3000
  
  # Specify output directory
  python3 scripts/generate_screenshots.py --output-dir assets
  
  # Verbose output
  python3 scripts/generate_screenshots.py --verbose

Note: The app must be running and accessible at the specified URL.
      Start the local server with:
        cd static && python3 -m http.server 8000
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='URL of the running app (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='assets',
        help='Output directory for screenshots (default: assets)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("KRWL> - Screenshot Generator")
    print("=" * 70)
    print(f"\n📍 URL: {args.url}")
    print(f"📁 Output: {args.output_dir}")
    
    success = generate_screenshots(
        url=args.url,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    if success:
        print("\n💡 Tip: Update assets/json/manifest.json if screenshot filenames changed")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
