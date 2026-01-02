"""AI Providers - Multiple AI backends for content extraction."""

from typing import Dict, Any


# Provider registry: name -> (module, class_name)
PROVIDER_REGISTRY = {
    'duckduckgo': ('duckduckgo', 'DuckDuckGoProvider'),
    'bing': ('bing', 'BingProvider'),
    'google': ('google', 'GoogleProvider'),
    'ollama': ('ollama', 'OllamaProvider'),
    'openai': ('openai_provider', 'OpenAIProvider'),
    'anthropic': ('anthropic_provider', 'AnthropicProvider'),
    'groq': ('groq_provider', 'GroqProvider'),
    'local_llm': ('local_llm', 'LocalLLMProvider'),
}


def _load_provider(name: str, module_name: str, class_name: str, provider_config: Dict[str, Any]):
    """Load a single AI provider.
    
    Args:
        name: Provider name
        module_name: Python module to import from
        class_name: Class name in the module
        provider_config: Provider configuration
        
    Returns:
        Provider instance or None if import fails
    """
    try:
        module = __import__(f'.{module_name}', fromlist=[class_name], package=__package__)
        provider_class = getattr(module, class_name)
        return provider_class(provider_config)
    except (ImportError, AttributeError):
        return None


def get_available_providers(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get all available and configured AI providers.
    
    Args:
        config: AI configuration section
        
    Returns:
        Dictionary of provider_name -> provider_instance
    """
    providers = {}
    
    for name, (module_name, class_name) in PROVIDER_REGISTRY.items():
        if name in config:
            provider = _load_provider(name, module_name, class_name, config[name])
            if provider:
                providers[name] = provider
    
    return providers


__all__ = ['get_available_providers']
