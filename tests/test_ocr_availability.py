#!/usr/bin/env python3
"""
Test to verify OCR functionality is available for Facebook flyer scraping.

This test ensures that:
1. OCR dependencies (Pillow, pytesseract) are installed
2. Tesseract OCR system binary is available
3. Image analyzer module can be imported
4. OCR extraction functions work correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_ocr_dependencies_installed():
    """Verify OCR Python dependencies are installed."""
    try:
        import pytesseract
        print(f"✓ pytesseract installed: {pytesseract.__version__}")
    except ImportError as e:
        print(f"✗ pytesseract not installed: {e}")
        print("  Install with: pip install pytesseract")
        return False
    
    try:
        from PIL import Image
        print(f"✓ Pillow installed: {Image.__version__}")
    except ImportError as e:
        print(f"✗ Pillow not installed: {e}")
        print("  Install with: pip install Pillow")
        return False
    
    return True


def test_tesseract_binary_available():
    """Verify Tesseract OCR system binary is installed."""
    import subprocess
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        version_line = result.stdout.split('\n')[0]
        print(f"✓ Tesseract OCR installed: {version_line}")
        return True
    except FileNotFoundError:
        print("✗ Tesseract OCR binary not found")
        print("  Install with:")
        print("    Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng")
        print("    macOS: brew install tesseract tesseract-lang")
        return False
    except Exception as e:
        print(f"✗ Error checking Tesseract: {e}")
        return False


def test_image_analyzer_available():
    """Verify image analyzer module can be imported."""
    try:
        from modules.smart_scraper.image_analyzer.ocr import is_ocr_available
        available = is_ocr_available()
        if available:
            print("✓ Image analyzer OCR functionality available")
        else:
            print("✗ Image analyzer OCR not available (dependencies missing)")
        return available
    except ImportError as e:
        print(f"✗ Could not import image analyzer: {e}")
        return False


def test_ocr_text_extraction():
    """Test basic OCR text extraction functions."""
    try:
        from modules.smart_scraper.image_analyzer.ocr import (
            extract_dates, extract_times, extract_event_keywords
        )
        
        # Test date extraction
        test_text = "Konzert am 15.01.2026 um 19:30 Uhr"
        dates = extract_dates(test_text)
        times = extract_times(test_text)
        keywords = extract_event_keywords(test_text)
        
        assert len(dates) > 0, "Should extract date from text"
        assert len(times) > 0, "Should extract time from text"
        assert 'konzert' in keywords.get('event_type', []), "Should extract event keywords"
        
        print(f"✓ OCR text extraction working:")
        print(f"  - Dates found: {dates}")
        print(f"  - Times found: {times}")
        print(f"  - Keywords: {keywords}")
        return True
    except Exception as e:
        print(f"✗ OCR text extraction failed: {e}")
        return False


def test_facebook_source_ocr_enabled():
    """Verify Facebook sources have OCR enabled in config."""
    import json
    config_path = Path(__file__).parent.parent / "config.json"
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        fb_sources = [s for s in config['scraping']['sources'] 
                     if s.get('type') == 'facebook']
        
        if not fb_sources:
            print("⚠ No Facebook sources configured")
            return True
        
        ocr_enabled_count = sum(1 for s in fb_sources 
                               if s.get('options', {}).get('ocr_enabled', False))
        
        print(f"✓ Facebook sources: {len(fb_sources)}")
        print(f"  - With OCR enabled: {ocr_enabled_count}")
        print(f"  - Sources: {[s['name'] for s in fb_sources]}")
        
        if ocr_enabled_count == 0:
            print("⚠ Warning: No Facebook sources have ocr_enabled=true")
            print("  Add 'ocr_enabled': true to Facebook source options in config.json")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking config: {e}")
        return False


def main():
    """Run all OCR availability tests."""
    print("=" * 70)
    print("OCR Availability Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        ("Python Dependencies", test_ocr_dependencies_installed),
        ("Tesseract Binary", test_tesseract_binary_available),
        ("Image Analyzer Module", test_image_analyzer_available),
        ("OCR Text Extraction", test_ocr_text_extraction),
        ("Facebook OCR Config", test_facebook_source_ocr_enabled),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 70)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All OCR tests passed! Facebook flyer scraping is ready to use.")
        return 0
    else:
        print("\n⚠ Some tests failed. Follow the instructions above to fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
