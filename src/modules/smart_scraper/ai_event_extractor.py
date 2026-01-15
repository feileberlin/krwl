"""
Local AI Event Extraction Module

Aggregates post text, OCR results, image metadata, and other hints into a single
context prompt for local AI extraction. Designed for SmartScraper social sources
to enrich event data while keeping all processing local.
"""

from datetime import datetime
import logging
from typing import Dict, Any, Optional, List, Iterable, Tuple

from ..event_schema import EVENT_CATEGORIES

logger = logging.getLogger(__name__)

LOCAL_PROVIDER_ORDER: Tuple[str, ...] = ("local_llm", "ollama")


class LocalEventExtractor:
    """Aggregate event context and extract structured details via local AI."""

    def __init__(self, ai_providers: Optional[Dict[str, Any]] = None,
                 max_context_chars: int = 4000):
        """
        Initialize the local event extractor.

        Args:
            ai_providers: Mapping of available AI providers.
            max_context_chars: Max context length to send to AI.
        """
        self.ai_providers = ai_providers or {}
        self.max_context_chars = max_context_chars

    def extract_event_details(
        self,
        post_text: str = "",
        image_data: Optional[Dict[str, Any]] = None,
        image_metadata: Optional[List[Dict[str, str]]] = None,
        post_links: Optional[List[str]] = None,
        provider_name: Optional[str] = None,
        prompt_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured event details from aggregated context.

        Args:
            post_text: Text content from the post.
            image_data: OCR/image analysis output.
            image_metadata: Image metadata (alt text, titles, captions).
            post_links: List of links found in the post.
            provider_name: Optional provider override (per-source).
            prompt_override: Optional custom AI prompt.

        Returns:
            Normalized event details dictionary or None.
        """
        provider = self._select_provider(provider_name)
        if not provider:
            return None

        context = self.build_context(
            post_text=post_text,
            image_data=image_data,
            image_metadata=image_metadata,
            post_links=post_links
        )
        if not context:
            return None

        prompt = prompt_override or self._build_prompt()
        try:
            result = provider.extract_event_info(context, prompt)
        except Exception as exc:
            logger.warning(f"AI event extraction failed: {exc}")
            return None

        return self._normalize_result(result)

    def build_context(
        self,
        post_text: str = "",
        image_data: Optional[Dict[str, Any]] = None,
        image_metadata: Optional[List[Dict[str, str]]] = None,
        post_links: Optional[List[str]] = None
    ) -> str:
        """Build a single context string from all available inputs."""
        parts: List[str] = []

        if post_text:
            parts.append(f"Post text:\n{post_text.strip()}")

        if image_data:
            ocr_text = image_data.get('ocr_text')
            if ocr_text:
                parts.append(f"OCR text:\n{ocr_text.strip()}")

            self._append_list_hint(parts, "Dates found", image_data.get('dates_found'))
            self._append_list_hint(parts, "Times found", image_data.get('times_found'))
            self._append_list_hint(parts, "URLs found", image_data.get('urls_found'))
            self._append_list_hint(parts, "Prices found", image_data.get('prices_found'))

            keywords = image_data.get('keywords') or {}
            if keywords:
                parts.append(f"Keywords: {self._format_keywords(keywords)}")

            location_hint = image_data.get('location')
            if location_hint:
                parts.append(f"Location hint: {self._format_location_hint(location_hint)}")

            metadata = image_data.get('metadata')
            if metadata:
                parts.append(f"Image metadata: {metadata}")

        metadata_text = self._collect_metadata_text(image_metadata or [])
        if metadata_text:
            parts.append(f"Image metadata text:\n{metadata_text}")

        if post_links:
            unique_links = self._unique_values(post_links)
            parts.append(f"Post links: {', '.join(unique_links)}")

        context = "\n\n".join(part for part in parts if part).strip()
        if len(context) > self.max_context_chars:
            context = context[:self.max_context_chars].rstrip()
        return context

    def _build_prompt(self) -> str:
        """Build default AI prompt for event extraction."""
        today = datetime.utcnow().date().isoformat()
        return (
            "You are a local event extraction assistant. "
            "Extract key event details from the provided context. "
            f"Today's date is {today}. "
            "Return ONLY JSON with these fields: "
            "title, description, start_time, end_time, url, category, "
            "location (object with name, lat, lon), and price. "
            "Use ISO 8601 for times. Use null when unknown."
        )

    def _select_provider(self, provider_name: Optional[str] = None):
        """Pick an available local provider in priority order."""
        if provider_name:
            provider = self.ai_providers.get(provider_name)
            if provider and self._is_available(provider):
                return provider

        for name in LOCAL_PROVIDER_ORDER:
            provider = self.ai_providers.get(name)
            if provider and self._is_available(provider):
                return provider

        return None

    @staticmethod
    def _is_available(provider: Any) -> bool:
        """Check provider availability (best-effort)."""
        if hasattr(provider, 'is_available'):
            return provider.is_available()
        return True

    @staticmethod
    def _append_list_hint(parts: List[str], label: str, values: Optional[Iterable[Any]]) -> None:
        """Append a formatted list hint if values present."""
        if not values:
            return
        cleaned = [str(value).strip() for value in values if str(value).strip()]
        if cleaned:
            parts.append(f"{label}: {', '.join(cleaned)}")

    @staticmethod
    def _format_keywords(keywords: Dict[str, List[str]]) -> str:
        """Format keyword dict for prompt context."""
        formatted = []
        for key, values in keywords.items():
            if not values:
                continue
            formatted.append(f"{key}={', '.join(values)}")
        return "; ".join(formatted)

    @staticmethod
    def _collect_metadata_text(image_metadata: List[Dict[str, str]]) -> str:
        """Collect unique metadata text from image metadata list."""
        values: List[str] = []
        for metadata in image_metadata:
            for key in ('alt', 'title', 'aria_label', 'caption'):
                value = metadata.get(key)
                if value and value not in values:
                    values.append(value)
        return "\n".join(values).strip()

    @staticmethod
    def _format_location_hint(location_hint: Dict[str, Any]) -> str:
        """Format a location hint for prompt context."""
        name = location_hint.get('name')
        lat = location_hint.get('lat')
        lon = location_hint.get('lon')
        if name and lat is not None and lon is not None:
            return f"{name} ({lat}, {lon})"
        if name:
            return name
        if lat is not None and lon is not None:
            return f"{lat}, {lon}"
        return str(location_hint)

    def _normalize_result(self, result: Any) -> Optional[Dict[str, Any]]:
        """Normalize AI response into expected event detail keys."""
        if not isinstance(result, dict):
            return None

        normalized: Dict[str, Any] = {}
        for key in ('title', 'description', 'start_time', 'end_time', 'url', 'price'):
            value = result.get(key)
            if value:
                normalized[key] = value

        category = result.get('category')
        if category in EVENT_CATEGORIES:
            normalized['category'] = category

        location = self._normalize_location(result)
        if location:
            normalized['location'] = location

        return normalized or None

    @staticmethod
    def _normalize_location(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize location data from AI result."""
        location = result.get('location')
        if isinstance(location, dict):
            normalized = {
                key: location.get(key)
                for key in ('name', 'lat', 'lon', 'address')
                if location.get(key) is not None
            }
            return normalized or None

        name = result.get('location_name') or result.get('location')
        lat = LocalEventExtractor._coerce_float(result.get('location_lat'))
        lon = LocalEventExtractor._coerce_float(result.get('location_lon'))

        if name or lat is not None or lon is not None:
            normalized = {}
            if name:
                normalized['name'] = name
            if lat is not None:
                normalized['lat'] = lat
            if lon is not None:
                normalized['lon'] = lon
            return normalized or None

        return None

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        """Convert numeric strings to float when possible."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _unique_values(values: Iterable[str]) -> List[str]:
        """Return unique values preserving order."""
        seen = set()
        unique = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                unique.append(value)
        return unique
