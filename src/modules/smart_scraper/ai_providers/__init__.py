"""AI Providers - Multiple AI backends for content extraction."""

from typing import Dict, Any, Optional
import sys


def get_available_providers(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get all available and configured AI providers.
    
    Args:
        config: AI configuration section
        
    Returns:
        Dictionary of provider_name -> provider_instance
    """
    providers = {}
    
    # Try DuckDuckGo AI (free)
    if 'duckduckgo' in config:
        try:
            from .duckduckgo import DuckDuckGoProvider
            providers['duckduckgo'] = DuckDuckGoProvider(config['duckduckgo'])
        except ImportError:
            pass
    
    # Try Bing AI (free)
    if 'bing' in config:
        try:
            from .bing import BingProvider
            providers['bing'] = BingProvider(config['bing'])
        except ImportError:
            pass
    
    # Try Google AI (free tier)
    if 'google' in config:
        try:
            from .google import GoogleProvider
            providers['google'] = GoogleProvider(config['google'])
        except ImportError:
            pass
    
    # Try Ollama (local)
    if 'ollama' in config:
        try:
            from .ollama import OllamaProvider
            providers['ollama'] = OllamaProvider(config['ollama'])
        except ImportError:
            pass
    
    # Try OpenAI (paid)
    if 'openai' in config:
        try:
            from .openai_provider import OpenAIProvider
            providers['openai'] = OpenAIProvider(config['openai'])
        except ImportError:
            pass
    
    # Try Anthropic (paid)
    if 'anthropic' in config:
        try:
            from .anthropic_provider import AnthropicProvider
            providers['anthropic'] = AnthropicProvider(config['anthropic'])
        except ImportError:
            pass
    
    # Try Groq (fast inference)
    if 'groq' in config:
        try:
            from .groq_provider import GroqProvider
            providers['groq'] = GroqProvider(config['groq'])
        except ImportError:
            pass
    
    # Try local LLM (generic)
    if 'local_llm' in config:
        try:
            from .local_llm import LocalLLMProvider
            providers['local_llm'] = LocalLLMProvider(config['local_llm'])
        except ImportError:
            pass
    
    return providers


__all__ = ['get_available_providers']
