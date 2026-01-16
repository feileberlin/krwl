#!/usr/bin/env python3
"""
Demo Event Quality Tests

Ensures demo events are unique, descriptive, and free of placeholder copy.
"""

import json
import sys
from pathlib import Path


DEMO_FILE = Path(__file__).parent.parent / "assets" / "json" / "events.demo.json"
PLACEHOLDER_TITLE = "Test Community Gathering"
PLACEHOLDER_DESCRIPTION_PHRASES = [
    "test event for approval flow testing",
]


def load_demo_events():
    """Load demo events from the assets directory."""
    if not DEMO_FILE.exists():
        print("❌ events.demo.json not found")
        return []

    with DEMO_FILE.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    return data.get("events", [])


def test_unique_titles():
    """Ensure demo event titles are unique."""
    events = load_demo_events()
    if not events:
        return False

    titles = [event.get("title", "").strip() for event in events]
    duplicates = {title for title in titles if title and titles.count(title) > 1}

    if duplicates:
        print("❌ Duplicate demo titles found:")
        for title in sorted(duplicates):
            print(f"   - {title}")
        return False

    print(f"✓ {len(titles)} unique demo titles")
    return True


def test_no_placeholder_copy():
    """Ensure placeholder demo copy has been removed."""
    events = load_demo_events()
    if not events:
        return False

    violations = []
    for event in events:
        title_text = event.get("title", "").lower()
        description_text = event.get("description", "").lower()

        if PLACEHOLDER_TITLE.lower() in title_text:
            violations.append((event.get("id", "unknown"), PLACEHOLDER_TITLE))

        for phrase in PLACEHOLDER_DESCRIPTION_PHRASES:
            if phrase.lower() in description_text:
                violations.append((event.get("id", "unknown"), phrase))

    if violations:
        for event_id, phrase in violations:
            print(f"❌ Placeholder text '{phrase}' found in {event_id}")
        return False

    print("✓ No placeholder demo copy detected")
    return True


def main():
    """Run demo event quality checks."""
    print("=" * 60)
    print("Demo Event Quality Tests")
    print("=" * 60)

    tests = [
        ("Unique demo titles", test_unique_titles),
        ("No placeholder demo copy", test_no_placeholder_copy),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
            if result:
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as exc:
            print(f"💥 ERROR: {exc}\n")
            results.append(False)

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if all(results):
        print("✅ All demo quality tests passed!")
        return 0

    print("❌ Some demo quality tests failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
