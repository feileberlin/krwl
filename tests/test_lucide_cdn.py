#!/usr/bin/env python3
"""
Test Lucide CDN Configuration

Verifies that the Lucide icon library CDN URLs are correctly configured
according to the problem statement:
- Development: https://unpkg.com/lucide@latest/dist/umd/lucide.js
- Production: https://unpkg.com/lucide@latest
"""

import sys
from pathlib import Path

# Add src/modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'modules'))

from site_generator import DEPENDENCIES


def test_lucide_cdn_configuration():
    """Test that Lucide CDN configuration matches the expected URLs"""
    print("=" * 60)
    print("Testing Lucide CDN Configuration")
    print("=" * 60)
    
    # Get Lucide configuration
    lucide_config = DEPENDENCIES.get('lucide')
    if not lucide_config:
        print("❌ Lucide configuration not found in DEPENDENCIES")
        return False
    
    # Expected values
    expected_version = "latest"
    expected_base_url = "https://unpkg.com/lucide@{version}"
    expected_dev_url = "https://unpkg.com/lucide@latest/dist/umd/lucide.js"
    expected_prod_url = "https://unpkg.com/lucide@latest"
    
    # Test version
    print(f"\n1. Testing version...")
    if lucide_config['version'] == expected_version:
        print(f"   ✓ Version is '{expected_version}'")
    else:
        print(f"   ❌ Version is '{lucide_config['version']}', expected '{expected_version}'")
        return False
    
    # Test base URL
    print(f"\n2. Testing base URL...")
    if lucide_config['base_url'] == expected_base_url:
        print(f"   ✓ Base URL is correct")
    else:
        print(f"   ❌ Base URL is '{lucide_config['base_url']}'")
        print(f"      Expected: '{expected_base_url}'")
        return False
    
    # Test file configurations
    print(f"\n3. Testing file configurations...")
    if len(lucide_config['files']) != 2:
        print(f"   ❌ Expected 2 files, found {len(lucide_config['files'])}")
        return False
    
    # Construct URLs
    base_url = lucide_config['base_url'].format(version=lucide_config['version'])
    
    # Test development file (lucide.js)
    dev_file = lucide_config['files'][0]
    if dev_file['src']:
        dev_url = f"{base_url}{dev_file['src']}"
    else:
        dev_url = base_url
    
    print(f"\n   a) Development file (lucide.js):")
    print(f"      Destination: {dev_file['dest']}")
    print(f"      URL: {dev_url}")
    if dev_url == expected_dev_url and dev_file['dest'] == 'lucide/lucide.js':
        print(f"      ✓ Correct")
    else:
        print(f"      ❌ Expected URL: {expected_dev_url}")
        print(f"      ❌ Expected dest: lucide/lucide.js")
        return False
    
    # Test production file (lucide.min.js)
    prod_file = lucide_config['files'][1]
    if prod_file['src']:
        prod_url = f"{base_url}{prod_file['src']}"
    else:
        prod_url = base_url
    
    print(f"\n   b) Production file (lucide.min.js):")
    print(f"      Destination: {prod_file['dest']}")
    print(f"      URL: {prod_url}")
    if prod_url == expected_prod_url and prod_file['dest'] == 'lucide/lucide.min.js':
        print(f"      ✓ Correct")
    else:
        print(f"      ❌ Expected URL: {expected_prod_url}")
        print(f"      ❌ Expected dest: lucide/lucide.min.js")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All Lucide CDN configuration tests passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = test_lucide_cdn_configuration()
    sys.exit(0 if success else 1)
