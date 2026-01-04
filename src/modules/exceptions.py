"""
Custom exception classes for the event manager

This module defines custom exceptions for better error handling and reporting.
"""

from typing import Any


class EventManagerError(Exception):
    """Base exception for all event manager errors"""
    pass


class ScraperError(EventManagerError):
    """Base exception for scraper errors"""
    pass


class SourceUnavailableError(ScraperError):
    """Raised when a scraping source is unavailable"""
    
    def __init__(self, source_name: str, url: str, reason: str):
        self.source_name = source_name
        self.url = url
        self.reason = reason
        super().__init__(
            f"Source '{source_name}' at {url} is unavailable: {reason}. "
            "Check your network connection or disable this source in config.json"
        )


class ValidationError(EventManagerError):
    """Raised when data validation fails"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(
            f"Validation failed for field '{field}' with value '{value}': {reason}"
        )


class ConfigurationError(EventManagerError):
    """Raised when configuration is invalid"""
    
    def __init__(self, config_field: str, reason: str):
        self.config_field = config_field
        self.reason = reason
        super().__init__(
            f"Configuration error in '{config_field}': {reason}. "
            "Please check your config.json file."
        )


class NetworkError(ScraperError):
    """Raised when network request fails"""
    
    def __init__(self, url: str, reason: str, status_code: int = None):
        self.url = url
        self.reason = reason
        self.status_code = status_code
        status_msg = f" (HTTP {status_code})" if status_code else ""
        super().__init__(
            f"Network request failed for {url}{status_msg}: {reason}"
        )


class ParsingError(ScraperError):
    """Raised when parsing scraped data fails"""
    
    def __init__(self, source_type: str, reason: str, data_sample: str = None):
        self.source_type = source_type
        self.reason = reason
        self.data_sample = data_sample
        sample_msg = f"\nData sample: {data_sample[:100]}..." if data_sample else ""
        super().__init__(
            f"Failed to parse {source_type} data: {reason}{sample_msg}"
        )
