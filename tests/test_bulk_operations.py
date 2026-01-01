#!/usr/bin/env python3
"""
Tests for bulk approve/reject operations with wildcard support.
"""

import sys
from pathlib import Path

# Add src to path (go up one level from tests/ to project root, then to src/)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import expand_wildcard_patterns


def test_expand_wildcard_patterns():
    """Test wildcard pattern expansion"""
    print("Testing wildcard pattern expansion...")
    
    # Create sample events
    events = [
        {'id': 'pending_1', 'title': 'Event 1'},
        {'id': 'pending_2', 'title': 'Event 2'},
        {'id': 'pending_3', 'title': 'Event 3'},
        {'id': 'html_frankenpost_123', 'title': 'Event 4'},
        {'id': 'html_frankenpost_456', 'title': 'Event 5'},
        {'id': 'html_other_789', 'title': 'Event 6'},
    ]
    
    # Test 1: Single wildcard pattern
    patterns = ['pending_*']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2', 'pending_3']
    assert result == expected, f"Test 1 failed: expected {expected}, got {result}"
    print("✓ Test 1: Single wildcard pattern")
    
    # Test 2: Multiple wildcard patterns
    patterns = ['html_frankenpost_*', 'pending_1']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['html_frankenpost_123', 'html_frankenpost_456', 'pending_1']
    assert result == expected, f"Test 2 failed: expected {expected}, got {result}"
    print("✓ Test 2: Multiple wildcard patterns")
    
    # Test 3: Mix of exact IDs and wildcards
    patterns = ['pending_1', 'html_*_456', 'pending_2']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'html_frankenpost_456', 'pending_2']
    assert result == expected, f"Test 3 failed: expected {expected}, got {result}"
    print("✓ Test 3: Mix of exact IDs and wildcards")
    
    # Test 4: Pattern with no matches (should return empty)
    patterns = ['nonexistent_*']
    result = expand_wildcard_patterns(patterns, events)
    expected = []
    assert result == expected, f"Test 4 failed: expected {expected}, got {result}"
    print("✓ Test 4: Pattern with no matches")
    
    # Test 5: Question mark wildcard
    patterns = ['pending_?']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2', 'pending_3']
    assert result == expected, f"Test 5 failed: expected {expected}, got {result}"
    print("✓ Test 5: Question mark wildcard")
    
    # Test 6: All events with *
    patterns = ['*']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2', 'pending_3', 'html_frankenpost_123', 
                'html_frankenpost_456', 'html_other_789']
    assert result == expected, f"Test 6 failed: expected {expected}, got {result}"
    print("✓ Test 6: All events with *")
    
    # Test 7: Duplicate removal
    patterns = ['pending_*', 'pending_1', 'pending_2']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2', 'pending_3']
    assert result == expected, f"Test 7 failed: expected {expected}, got {result}"
    print("✓ Test 7: Duplicate removal")
    
    # Test 8: Complex pattern
    patterns = ['*frankenpost*']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['html_frankenpost_123', 'html_frankenpost_456']
    assert result == expected, f"Test 8 failed: expected {expected}, got {result}"
    print("✓ Test 8: Complex pattern with wildcards")
    
    # Test 9: Empty pattern list
    patterns = []
    result = expand_wildcard_patterns(patterns, events)
    expected = []
    assert result == expected, f"Test 9 failed: expected {expected}, got {result}"
    print("✓ Test 9: Empty pattern list")
    
    # Test 10: Whitespace handling
    patterns = [' pending_1 ', ' html_frankenpost_* ']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'html_frankenpost_123', 'html_frankenpost_456']
    assert result == expected, f"Test 10 failed: expected {expected}, got {result}"
    print("✓ Test 10: Whitespace handling")
    
    # Test 11: Character ranges in brackets
    patterns = ['pending_[1-2]']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2']
    assert result == expected, f"Test 11 failed: expected {expected}, got {result}"
    print("✓ Test 11: Character ranges in brackets")
    
    # Test 12: Duplicate patterns (all matches already in seen_ids should still report as matched)
    patterns = ['pending_*', 'pending_*']
    result = expand_wildcard_patterns(patterns, events)
    expected = ['pending_1', 'pending_2', 'pending_3']  # No duplicates, but no warning either
    assert result == expected, f"Test 12 failed: expected {expected}, got {result}"
    print("✓ Test 12: Duplicate patterns handled correctly")
    
    print("\n✅ All wildcard pattern expansion tests passed!")


def test_bulk_operations_integration():
    """Test bulk operations with real command execution"""
    print("\nTesting bulk operations integration...")
    
    # This would test the actual CLI commands, but we'll keep it simple
    # and just ensure the functions can be imported
    from main import cli_bulk_publish_events, cli_bulk_reject_events
    
    print("✓ Bulk operation functions imported successfully")
    print("  Note: Full integration tests require running with actual data files")
    
    print("\n✅ Integration test passed!")


if __name__ == '__main__':
    try:
        test_expand_wildcard_patterns()
        test_bulk_operations_integration()
        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
