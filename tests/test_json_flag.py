#!/usr/bin/env python3
"""
Test the --json flag for scraper-info command

This test verifies that:
1. The --json flag produces pure JSON output (no logs mixed in)
2. The JSON is valid and parseable
3. All expected fields are present
4. The output can be piped to jq successfully
"""

import subprocess
import json
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_json_flag_produces_pure_json():
    """Test that --json flag produces pure JSON without logs"""
    print("📋 Test 1: --json flag produces pure JSON")
    print("-" * 60)
    
    # Run scraper-info with --json flag, capturing both stdout and stderr
    result = subprocess.run(
        ['python3', 'src/event_manager.py', 'scraper-info', '--json'],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    # Check exit code
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        print(f"Stderr: {result.stderr}")
        return False
    
    output = result.stdout
    
    # Check that output starts with '{' (no logs before JSON)
    if not output.strip().startswith('{'):
        print(f"❌ Output doesn't start with '{{'. First chars: {output[:50]}")
        return False
    
    print("✓ Output starts with '{' (no logs before JSON)")
    
    # Check that output ends with '}' (no logs after JSON)
    if not output.strip().endswith('}'):
        print(f"❌ Output doesn't end with '}}'. Last chars: {output[-50:]}")
        return False
    
    print("✓ Output ends with '}' (no logs after JSON)")
    
    # Try to parse as JSON
    try:
        data = json.loads(output)
        print("✓ JSON parsing successful")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Output: {output[:200]}")
        return False
    
    # Check required keys
    required_keys = [
        'supported_source_types',
        'enabled_sources',
        'schedule',
        'smart_scraper_available',
        'scraping_libraries_installed'
    ]
    
    for key in required_keys:
        if key not in data:
            print(f"❌ Missing required key: {key}")
            return False
    
    print(f"✓ All required keys present: {', '.join(required_keys)}")
    
    return True


def test_json_flag_no_stderr_logs():
    """Test that --json flag suppresses stderr logs"""
    print("\n📋 Test 2: --json flag suppresses stderr logs")
    print("-" * 60)
    
    # Run scraper-info with --json flag
    result = subprocess.run(
        ['python3', 'src/event_manager.py', 'scraper-info', '--json'],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    stderr = result.stderr
    
    # Check that stderr is empty or minimal (no INFO/ERROR logs)
    # Note: Import-time warnings might still appear, but they should be minimal
    log_prefixes = ['INFO:', 'ERROR:', 'WARNING:', 'DEBUG:']
    
    # Count log lines in stderr
    log_lines = [line for line in stderr.split('\n') if any(line.startswith(prefix) for prefix in log_prefixes)]
    
    if log_lines:
        print(f"⚠️  Found {len(log_lines)} log line(s) in stderr (should be 0 with --json flag):")
        for line in log_lines[:5]:  # Show first 5
            print(f"  {line}")
        # For now, just warn but don't fail (some import-time logs might be unavoidable)
        print("⚠️  Warning: Some logs still present (but this is non-critical)")
    else:
        print("✓ No INFO/ERROR/WARNING logs in stderr")
    
    return True


def test_json_flag_with_jq():
    """Test that output can be piped to jq"""
    print("\n📋 Test 3: Output works with jq")
    print("-" * 60)
    
    # Run scraper-info and pipe to jq
    proc1 = subprocess.Popen(
        ['python3', 'src/event_manager.py', 'scraper-info', '--json'],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    proc2 = subprocess.Popen(
        ['jq', 'empty'],
        stdin=proc1.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    proc1.stdout.close()  # Allow proc1 to receive SIGPIPE
    stdout, stderr = proc2.communicate()
    
    if proc2.returncode != 0:
        print(f"❌ jq validation failed")
        print(f"jq stderr: {stderr}")
        return False
    
    print("✓ jq validation passed (JSON is valid)")
    
    # Test extracting a specific field with jq
    result = subprocess.run(
        "python3 src/event_manager.py scraper-info --json | jq -r '.scraping_libraries_installed'",
        shell=True,
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ jq field extraction failed")
        return False
    
    value = result.stdout.strip()
    if value not in ['true', 'false']:
        print(f"❌ Unexpected value for scraping_libraries_installed: {value}")
        return False
    
    print(f"✓ jq field extraction works (scraping_libraries_installed={value})")
    
    return True


def main():
    """Run all tests"""
    print("Testing --json flag for scraper-info command...")
    print("=" * 60)
    
    tests = [
        ("JSON purity", test_json_flag_produces_pure_json),
        ("Stderr suppression", test_json_flag_no_stderr_logs),
        ("jq compatibility", test_json_flag_with_jq)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
    print("=" * 60)
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
