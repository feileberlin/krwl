"""Smart Scraper - Modular event scraping system with AI and image analysis.

This package provides:
- Multi-platform scrapers (social media, web, RSS, APIs)
- AI-powered content extraction
- Image analysis with OCR and metadata extraction
- Configurable filtering and rate limiting
"""

try:
    from .core import SmartScraper
    from .base import SourceOptions, ScraperRegistry
    __all__ = ['SmartScraper', 'SourceOptions', 'ScraperRegistry']
except ImportError:
    # Allow import of package even if dependencies aren't installed
    __all__ = []

__version__ = '1.0.0'
