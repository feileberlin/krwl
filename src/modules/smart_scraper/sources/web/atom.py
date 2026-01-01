"""Atom feed scraper."""

from typing import Dict, Any, List
from .rss import RSSSource


class AtomSource(RSSSource):
    """Scraper for Atom feeds (extends RSS scraper)."""
    
    def __init__(self, source_config: Dict[str, Any], options):
        super().__init__(source_config, options)
        # Atom feeds are parsed the same way as RSS by feedparser
