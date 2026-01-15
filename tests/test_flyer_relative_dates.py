#!/usr/bin/env python3
"""
Tests for flyer relative date parsing and AI fallback extraction.
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.smart_scraper.base import SourceOptions
from modules.smart_scraper.sources.social.facebook import FacebookSource


class FakeAIProvider:
    """Simple AI provider stub for tests."""

    def __init__(self, start_time: str):
        self.start_time = start_time

    def is_available(self) -> bool:
        return True

    def extract_event_info(self, text, prompt=None):
        return {
            "start_time": self.start_time,
            "title": "AI Event"
        }


def build_source(ai_providers=None, options=None, base_path=None):
    """Create a FacebookSource instance for tests."""
    source_config = {
        "name": "Test Source",
        "url": "https://facebook.com/test",
        "type": "facebook"
    }
    return FacebookSource(
        source_config,
        options or SourceOptions(),
        base_path=base_path,
        ai_providers=ai_providers
    )


def test_relative_date_parsing_from_text():
    """Ensure relative dates in flyer text resolve to concrete datetimes."""
    source = build_source()
    now = datetime.now()

    cases = [
        ("Morgen 19 Uhr", now + timedelta(days=1), 19, 0),
        ("tomorrow 20:30", now + timedelta(days=1), 20, 30),
        ("übermorgen 18:00", now + timedelta(days=2), 18, 0),
    ]

    for text, expected_date, hour, minute in cases:
        iso_value = source._extract_datetime_from_text(text)
        assert iso_value is not None
        parsed = datetime.fromisoformat(iso_value)
        assert parsed.date() == expected_date.date()
        assert parsed.hour == hour
        assert parsed.minute == minute


def test_month_day_without_year():
    """Handle DD.MM format without year for upcoming month events."""
    source = build_source()
    target_date = datetime.now() + timedelta(days=10)
    text = target_date.strftime("%d.%m.")

    iso_value = source._extract_datetime_from_text(f"{text} 19 Uhr")
    assert iso_value is not None
    parsed = datetime.fromisoformat(iso_value)
    assert parsed.date() == target_date.date()
    assert parsed.hour == 19


def test_ai_fallback_for_missing_date():
    """Use AI provider when no explicit date is found."""
    start_time = (datetime.now() + timedelta(days=3)).replace(
        hour=19, minute=30, second=0, microsecond=0
    ).isoformat()
    provider = FakeAIProvider(start_time)
    options = SourceOptions(ai_provider="fake")
    source = build_source(ai_providers={"fake": provider}, options=options)

    post = {"text": "Live Konzert im Club"}
    event = source._build_event_from_post(post, None)

    assert event["start_time"] == start_time


def test_scan_posts_for_event_pages():
    """Ensure scan_posts enables post scraping for /events URLs."""
    class SpyFacebookSource(FacebookSource):
        def __init__(self, source_config, options, base_path=None, available=True):
            super().__init__(
                source_config,
                options,
                base_path=base_path,
                ai_providers=None
            )
            self.posts_called_with = None
            self.available = available

        def _scrape_events_page(self):
            return []

        def _scrape_page_posts(self, page_url=None):
            self.posts_called_with = page_url
            return []

    source_config = {
        "name": "Test Events Page",
        "url": "https://www.facebook.com/TestPage/events",
        "type": "facebook",
        "options": {"scan_posts": True}
    }
    source = SpyFacebookSource(source_config, SourceOptions())
    source.scrape()

    assert source.posts_called_with == source._get_page_url(source_config["url"])


def test_post_cache_skips_processed_posts(tmp_path):
    """Ensure processed posts are skipped unless forced."""
    source = build_source(base_path=tmp_path)
    posts = [
        {"text": "Morgen 19 Uhr", "images": [], "links": [], "timestamp": "1"}
    ]
    post_key = source._get_post_cache_key(posts[0])

    first_run = source._process_posts(posts)
    second_run = source._process_posts(posts)

    assert len(first_run) == 1
    assert second_run == []

    cache_path = (
        tmp_path / "data" / "scraper_cache" / "facebook_posts_test_source.json"
    )
    assert cache_path.exists()
    cached = json.loads(cache_path.read_text())
    assert post_key in cached.get("processed_keys", [])

    new_source = build_source(base_path=tmp_path)
    assert new_source.post_cache.is_processed(post_key)

    source.force_scan = True
    third_run = source._process_posts(posts)
    assert len(third_run) == 1
