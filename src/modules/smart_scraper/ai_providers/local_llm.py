"""Ollama-backed local LLM AI provider for on-device event extraction."""

from typing import Dict, Any, Optional
from .ollama import OllamaProvider


class LocalLLMProvider(OllamaProvider):
    """Local LLM provider using Ollama for event detail extraction."""

    def extract_event_info(self, text: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Extract event information from text using local LLM.

        Uses a structured extraction prompt when no custom prompt is provided.
        """
        if prompt is None:
            prompt = self._build_event_extraction_prompt()
        return super().extract_event_info(text, prompt)

    @staticmethod
    def _build_event_extraction_prompt() -> str:
        """Build prompt for extracting structured event details."""
        return (
            "Extract key event details from the provided context and return ONLY JSON. "
            "Required fields: title, description, start_time, end_time, url, category, "
            "location (object with name, lat, lon), price. "
            "Use ISO 8601 for times. Use null (JSON) or None for unknown values."
        )


# Deprecated aliases for legacy imports (remove in next major release).
LocalLlmProvider = LocalLLMProvider
Local_llmProvider = LocalLLMProvider
