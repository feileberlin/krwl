"""openai_provider AI provider (stub)."""

from typing import Dict, Any, Optional
from .base import BaseAIProvider


class Openai_providerProvider(BaseAIProvider):
    """Openai_provider provider - not yet implemented."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.available = False
    
    def is_available(self) -> bool:
        return False
    
    def extract_event_info(self, text: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return None
    
    def analyze_image(self, image_data: bytes, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return None
