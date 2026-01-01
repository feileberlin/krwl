"""Base AI provider and rate limiting."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import random


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 5.0,
                 max_requests_per_session: int = 10):
        """Initialize rate limiter.
        
        Args:
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            max_requests_per_session: Max requests before rotation
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_requests_per_session = max_requests_per_session
        self.request_count = 0
        self.last_request_time = 0
        self.retry_after = 0
    
    def wait(self):
        """Wait appropriate amount before next request."""
        now = time.time()
        
        # Check if we're in a retry-after period
        if self.retry_after > now:
            wait_time = self.retry_after - now
            print(f"  ⏱ Rate limit: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
            self.retry_after = 0
        
        # Calculate delay since last request
        elapsed = now - self.last_request_time
        
        # Random delay between min and max
        target_delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < target_delay:
            wait_time = target_delay - elapsed
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def handle_rate_limit(self, retry_after: float = 60):
        """Handle rate limit response.
        
        Args:
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = time.time() + retry_after
        print(f"  ⚠ Rate limited, waiting {retry_after}s")
    
    def should_rotate(self) -> bool:
        """Check if session should be rotated."""
        return self.request_count >= self.max_requests_per_session
    
    def reset(self):
        """Reset request counter."""
        self.request_count = 0


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        
        # Setup rate limiting
        rate_limit = config.get('rate_limit', {})
        self.rate_limiter = RateLimiter(
            min_delay=rate_limit.get('min_delay', 1.0),
            max_delay=rate_limit.get('max_delay', 5.0),
            max_requests_per_session=rate_limit.get('max_requests_per_session', 10)
        )
    
    @abstractmethod
    def extract_event_info(self, text: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract event information from text using AI.
        
        Args:
            text: Text to analyze
            prompt: Optional custom prompt
            
        Returns:
            Extracted event data or None
        """
        pass
    
    @abstractmethod
    def analyze_image(self, image_data: bytes, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Analyze image to extract event information.
        
        Args:
            image_data: Image binary data
            prompt: Optional custom prompt
            
        Returns:
            Extracted event data or None
        """
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available.
        
        Returns:
            True if provider can be used
        """
        return True
    
    def get_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name
        """
        return self.__class__.__name__
