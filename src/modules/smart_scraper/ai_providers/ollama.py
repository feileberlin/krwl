"""Ollama provider (local LLM)."""

from typing import Dict, Any, Optional
import json
from .base import BaseAIProvider

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class OllamaProvider(BaseAIProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get('host', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.2')
        self.available = REQUESTS_AVAILABLE and self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running."""
        if not REQUESTS_AVAILABLE:
            return False
        try:
            import requests
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def is_available(self) -> bool:
        return self.available
    
    def extract_event_info(self, text: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.available:
            return None
        self.rate_limiter.wait()
        # Stub - implement Ollama API call
        return None
    
    def analyze_image(self, image_data: bytes, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.available:
            return None
        self.rate_limiter.wait()
        # Stub - implement with vision model
        return None
