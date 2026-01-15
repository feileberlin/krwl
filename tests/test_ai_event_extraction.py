"""
Test Local AI Event Extraction Module.

Validates that aggregated context is built correctly and AI responses are
normalized into event-friendly fields without requiring actual AI services.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.smart_scraper.ai_event_extractor import LocalEventExtractor


class StubProvider:
    """Stub AI provider for testing extraction."""

    def __init__(self, response):
        self.response = response
        self.last_text = None
        self.last_prompt = None

    def is_available(self):
        return True

    def extract_event_info(self, text, prompt=None):
        self.last_text = text
        self.last_prompt = prompt
        return self.response


def test_context_aggregation():
    """Test aggregated context includes post, OCR, and metadata hints."""
    print("\n" + "=" * 60)
    print("TEST 1: Context Aggregation")
    print("=" * 60)

    provider = StubProvider(response={})
    extractor = LocalEventExtractor({'local_llm': provider})

    image_data = {
        'ocr_text': 'Flyer headline\nMain hall',
        'dates_found': ['12.03.2026'],
        'times_found': ['20:00'],
        'urls_found': ['https://example.com/tickets'],
        'prices_found': ['10€'],
        'keywords': {'event_type': ['concert'], 'music_genre': ['rock']},
        'location': {'name': 'Main Hall', 'lat': 50.1, 'lon': 11.2},
        'metadata': {'camera': 'TestCam'}
    }
    image_metadata = [{'alt': 'Poster alt text', 'title': 'Poster title'}]
    post_links = ['https://example.com/event']

    context = extractor.build_context(
        post_text="Post description",
        image_data=image_data,
        image_metadata=image_metadata,
        post_links=post_links
    )

    checks = [
        ("Post text included", "Post text:" in context),
        ("OCR text included", "OCR text:" in context),
        ("Dates hint included", "Dates found:" in context),
        ("Times hint included", "Times found:" in context),
        ("URLs hint included", "URLs found:" in context),
        ("Prices hint included", "Prices found:" in context),
        ("Keywords included", "Keywords:" in context),
        ("Location hint included", "Location hint:" in context),
        ("Image metadata included", "Image metadata text:" in context),
        ("Post links included", "Post links:" in context),
    ]

    failed = 0
    for label, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {label}")
        if not passed:
            failed += 1

    return failed == 0


def test_event_normalization():
    """Test AI response normalization into event fields."""
    print("\n" + "=" * 60)
    print("TEST 2: Event Detail Normalization")
    print("=" * 60)

    response = {
        'title': 'Local Rock Night',
        'description': 'Live bands all evening.',
        'start_time': '2026-03-12T20:00:00',
        'end_time': '2026-03-12T23:00:00',
        'url': 'https://example.com/event',
        'category': 'music',
        'location_name': 'Main Hall',
        'location_lat': '50.1',
        'location_lon': 11.2
    }
    provider = StubProvider(response=response)
    extractor = LocalEventExtractor({'local_llm': provider})

    result = extractor.extract_event_details(
        post_text="Post text",
        image_data={'ocr_text': 'Flyer text'}
    )

    checks = [
        ("Result returned", result is not None),
        ("Title normalized", result.get('title') == 'Local Rock Night'),
        ("Category validated", result.get('category') == 'music'),
        ("Location normalized", isinstance(result.get('location'), dict)),
        ("Location lat parsed", result.get('location', {}).get('lat') == 50.1),
        ("Prompt used", provider.last_prompt is not None)
    ]

    failed = 0
    for label, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {label}")
        if not passed:
            failed += 1

    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AI EVENT EXTRACTION TEST SUITE")
    print("=" * 60)

    results = [
        ("Context Aggregation", test_context_aggregation()),
        ("Event Normalization", test_event_normalization()),
    ]

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✓ All tests passed!")
        return 0

    print("\n✗ Some tests failed")
    return 1


if __name__ == '__main__':
    sys.exit(main())
