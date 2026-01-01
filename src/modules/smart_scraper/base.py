"""Base classes and registry for smart scraper system.

Provides:
- SourceOptions: Per-source configuration
- BaseSource: Abstract base class for scrapers
- ScraperRegistry: Registry for source type handlers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import re


@dataclass
class SourceOptions:
    """Per-source configuration options."""
    
    # Filtering options
    filter_ads: bool = False
    exclude_keywords: List[str] = field(default_factory=list)
    include_keywords: List[str] = field(default_factory=list)
    
    # Date filtering
    max_days_ahead: Optional[int] = 60
    min_days_ahead: Optional[int] = 0
    
    # Location validation
    validate_location: bool = False
    location_radius_km: Optional[float] = None
    
    # Event metadata
    category: Optional[str] = None
    default_location: Optional[Dict[str, Any]] = None
    
    # AI provider override
    ai_provider: Optional[str] = None
    ai_prompt: Optional[str] = None
    
    # Deduplication
    dedup_enabled: bool = True
    dedup_fields: List[str] = field(default_factory=lambda: ['title', 'start_time'])
    
    # Rate limiting (overrides global settings)
    rate_limit_delay: Optional[float] = None
    max_retries: int = 3
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SourceOptions':
        """Create SourceOptions from dictionary."""
        # Only use keys that are defined in SourceOptions
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
    
    def should_filter(self, text: str) -> bool:
        """Check if text should be filtered out based on keywords."""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check exclude keywords
        if self.exclude_keywords:
            for keyword in self.exclude_keywords:
                if keyword.lower() in text_lower:
                    return True
        
        # Check include keywords (if specified, must match at least one)
        if self.include_keywords:
            has_match = any(
                keyword.lower() in text_lower 
                for keyword in self.include_keywords
            )
            if not has_match:
                return True
        
        # Check for common ad patterns if filter_ads enabled
        if self.filter_ads:
            ad_patterns = [
                r'\b(ad|sponsored|werbung|anzeige|gewinnspiel)\b',
                r'\bwin\s+(tickets|prizes)\b',
                r'\b(buy|shop|sale|discount)\b'
            ]
            for pattern in ad_patterns:
                if re.search(pattern, text_lower):
                    return True
        
        return False


class BaseSource(ABC):
    """Abstract base class for all source scrapers."""
    
    def __init__(self, source_config: Dict[str, Any], options: SourceOptions):
        """Initialize source scraper.
        
        Args:
            source_config: Source configuration from config.json
            options: SourceOptions instance
        """
        self.source_config = source_config
        self.options = options
        self.name = source_config.get('name', 'Unknown')
        self.url = source_config.get('url', '')
        self.source_type = source_config.get('type', 'unknown')
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from this source.
        
        Returns:
            List of event dictionaries
        """
        pass
    
    def filter_event(self, event: Dict[str, Any]) -> bool:
        """Check if event should be filtered out.
        
        Args:
            event: Event dictionary
            
        Returns:
            True if event should be filtered out, False otherwise
        """
        # Check title and description against keywords
        title = event.get('title', '')
        description = event.get('description', '')
        combined_text = f"{title} {description}"
        
        return self.options.should_filter(combined_text)


class ScraperRegistry:
    """Registry for source type handlers."""
    
    def __init__(self):
        """Initialize empty registry."""
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, source_type: str, handler: Callable):
        """Register a handler for a source type.
        
        Args:
            source_type: Source type identifier (e.g., 'facebook', 'rss')
            handler: Callable that returns a BaseSource instance
        """
        self._handlers[source_type] = handler
    
    def get_handler(self, source_type: str) -> Optional[Callable]:
        """Get handler for a source type.
        
        Args:
            source_type: Source type identifier
            
        Returns:
            Handler callable or None if not found
        """
        return self._handlers.get(source_type)
    
    def list_types(self) -> List[str]:
        """List all registered source types.
        
        Returns:
            List of source type identifiers
        """
        return list(self._handlers.keys())
    
    def is_registered(self, source_type: str) -> bool:
        """Check if a source type is registered.
        
        Args:
            source_type: Source type identifier
            
        Returns:
            True if registered, False otherwise
        """
        return source_type in self._handlers
