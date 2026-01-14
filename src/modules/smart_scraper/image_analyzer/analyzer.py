"""Main image analyzer combining OCR, metadata, and AI.

This module provides a unified interface for extracting event information
from images (particularly event flyers). It combines:
- OCR text extraction with enhanced pattern matching
- EXIF metadata extraction (GPS, datetime)
- Optional AI-powered content analysis

Designed to be reusable across all social media scrapers.
"""

from typing import Dict, Any, Optional, Union
from io import BytesIO
from .metadata import extract_metadata
from .ocr import (
    extract_text, extract_text_from_url, extract_dates, extract_times,
    extract_urls, extract_prices, extract_event_keywords,
    extract_event_data_from_image, is_ocr_available
)


class ImageAnalyzer:
    """Analyzes images to extract event information.
    
    This class is designed to be used by all social media scrapers to extract
    event data from posted images/flyers. It provides both simple analysis
    and comprehensive event extraction.
    
    Example usage:
        analyzer = ImageAnalyzer(config, ai_providers)
        
        # Analyze from file path
        result = analyzer.analyze('/path/to/flyer.jpg')
        
        # Analyze from URL
        result = analyzer.analyze_url('https://example.com/flyer.jpg')
        
        # Analyze from bytes (e.g., downloaded image)
        result = analyzer.analyze_bytes(image_bytes)
    """
    
    def __init__(self, config: Dict[str, Any], ai_providers: Dict[str, Any] = None):
        """Initialize image analyzer.
        
        Args:
            config: Image analysis configuration
            ai_providers: Dictionary of available AI providers (optional)
        """
        self.config = config
        self.ai_providers = ai_providers or {}
        self.ocr_enabled = config.get('ocr_enabled', True)
        self.ocr_provider = config.get('ocr_provider', 'tesseract')
        self.languages = config.get('languages', ['eng', 'deu'])
    
    @staticmethod
    def is_available() -> bool:
        """Check if image analysis is available.
        
        Returns:
            True if OCR dependencies are installed
        """
        return is_ocr_available()
    
    def analyze(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Analyze image file to extract event information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted event data or None
        """
        result = {}
        
        # Extract metadata (GPS, datetime, etc.)
        self._extract_image_metadata(image_path, result)
        
        # Extract text with OCR
        if self.ocr_enabled:
            self._extract_text_data(image_path, result)
        
        return result if result else None
    
    def analyze_url(self, image_url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Analyze image from URL to extract event information.
        
        This is useful for social media scrapers that get image URLs from posts.
        
        Args:
            image_url: URL of the image to analyze
            timeout: Request timeout in seconds
            
        Returns:
            Extracted event data or None
        """
        if not self.ocr_enabled:
            return None
        
        result = {}
        
        # Extract text directly from URL
        ocr_data = extract_event_data_from_image_url(image_url, self.languages, timeout)
        if ocr_data:
            result.update(self._format_ocr_result(ocr_data))
        
        # Use AI if available and confidence is low
        if self.ai_providers and ocr_data.get('confidence', 0) < 0.5:
            ai_result = self._ai_extract_from_url(image_url)
            if ai_result:
                result.update(ai_result)
        
        return result if result else None
    
    def analyze_bytes(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Analyze image from bytes to extract event information.
        
        This is useful when you already have the image data in memory.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Extracted event data or None
        """
        if not self.ocr_enabled:
            return None
        
        result = {}
        
        # Extract comprehensive event data
        ocr_data = extract_event_data_from_image(image_data, self.languages)
        if ocr_data:
            result.update(self._format_ocr_result(ocr_data))
        
        # Use AI if available and confidence is low
        if self.ai_providers and ocr_data.get('confidence', 0) < 0.5:
            ai_result = self._ai_extract_from_bytes(image_data)
            if ai_result:
                result.update(ai_result)
        
        return result if result else None
    
    def extract_event_from_flyer(self, image_source: Union[str, bytes],
                                  source_name: str = None) -> Optional[Dict[str, Any]]:
        """Extract event data from a flyer image optimized for event creation.
        
        This is the main method for social media scrapers to use when they
        find images in posts that might be event flyers.
        
        Args:
            image_source: Path to image, URL, or bytes
            source_name: Name of the source (for attribution)
            
        Returns:
            Event-ready dictionary or None
        """
        # Determine source type and analyze
        if isinstance(image_source, bytes):
            raw_result = self.analyze_bytes(image_source)
        elif image_source.startswith(('http://', 'https://')):
            raw_result = self.analyze_url(image_source)
        else:
            raw_result = self.analyze(image_source)
        
        if not raw_result:
            return None
        
        # Convert to event format
        event = self._convert_to_event_format(raw_result, source_name)
        return event
    
    def _format_ocr_result(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format OCR extraction result for unified output.
        
        Args:
            ocr_data: Raw OCR extraction data
            
        Returns:
            Formatted result dictionary
        """
        result = {}
        
        if ocr_data.get('text'):
            result['ocr_text'] = ocr_data['text']
        if ocr_data.get('dates'):
            result['dates_found'] = ocr_data['dates']
        if ocr_data.get('times'):
            result['times_found'] = ocr_data['times']
        if ocr_data.get('urls'):
            result['urls_found'] = ocr_data['urls']
        if ocr_data.get('prices'):
            result['prices_found'] = ocr_data['prices']
        if ocr_data.get('keywords'):
            result['keywords'] = ocr_data['keywords']
        if ocr_data.get('confidence'):
            result['ocr_confidence'] = ocr_data['confidence']
        
        return result
    
    def _convert_to_event_format(self, raw_result: Dict[str, Any],
                                  source_name: str = None) -> Optional[Dict[str, Any]]:
        """Convert raw analysis result to event format.
        
        Args:
            raw_result: Raw analysis result
            source_name: Name of the source
            
        Returns:
            Event-ready dictionary or None
        """
        event = {}
        
        # Try to extract title from text (first line often is title)
        if raw_result.get('ocr_text'):
            lines = raw_result['ocr_text'].strip().split('\n')
            # Use first non-empty line as potential title
            for line in lines:
                line = line.strip()
                if line and len(line) > 3 and len(line) < 200:
                    event['title_hint'] = line
                    break
        
        # Use first date found
        if raw_result.get('dates_found'):
            event['date_hint'] = raw_result['dates_found'][0]
        
        # Use first time found
        if raw_result.get('times_found'):
            event['time_hint'] = raw_result['times_found'][0]
        
        # Use location from GPS if available
        if raw_result.get('location'):
            event['location'] = raw_result['location']
        
        # Include URLs
        if raw_result.get('urls_found'):
            event['urls'] = raw_result['urls_found']
        
        # Include prices
        if raw_result.get('prices_found'):
            event['prices'] = raw_result['prices_found']
        
        # Include keywords for categorization
        if raw_result.get('keywords'):
            event['keywords'] = raw_result['keywords']
        
        # Include full OCR text for reference
        if raw_result.get('ocr_text'):
            event['ocr_text'] = raw_result['ocr_text']
        
        # Include confidence score
        if raw_result.get('ocr_confidence'):
            event['confidence'] = raw_result['ocr_confidence']
        
        # Add source attribution
        if source_name:
            event['image_source'] = source_name
        
        return event if event else None
    
    def _extract_image_metadata(self, image_path: str, result: Dict[str, Any]) -> None:
        """Extract and process image metadata.
        
        Args:
            image_path: Path to image file
            result: Dictionary to update with extracted data
        """
        metadata = extract_metadata(image_path)
        if not metadata:
            return
        
        result['metadata'] = metadata
        
        # Use GPS coordinates if available
        if 'gps' in metadata:
            result['location'] = {
                'name': 'From image GPS',
                'lat': metadata['gps']['lat'],
                'lon': metadata['gps']['lon']
            }
        
        # Use EXIF datetime if available
        if 'datetime' in metadata:
            result['start_time'] = metadata['datetime']
    
    def _extract_text_data(self, image_path: str, result: Dict[str, Any]) -> None:
        """Extract text data from image using OCR.
        
        Args:
            image_path: Path to image file
            result: Dictionary to update with extracted data
        """
        # Use comprehensive extraction
        ocr_data = extract_event_data_from_image(image_path, self.languages)
        if not ocr_data or not ocr_data.get('text'):
            return
        
        result.update(self._format_ocr_result(ocr_data))
        
        # Use AI to extract structured event info if confidence is low
        if self.ai_providers and ocr_data.get('confidence', 0) < 0.5:
            ai_result = self._ai_extract(ocr_data.get('text', ''), image_path)
            if ai_result:
                result.update(ai_result)
    
    def _ai_extract(self, text: str, image_path: str) -> Optional[Dict[str, Any]]:
        """Use AI to extract structured event information.
        
        Args:
            text: OCR extracted text
            image_path: Path to image
            
        Returns:
            Extracted event data or None
        """
        # Try to get default AI provider
        default_provider = self.config.get('ai_provider')
        provider = None
        
        if default_provider and default_provider in self.ai_providers:
            provider = self.ai_providers[default_provider]
        elif self.ai_providers:
            # Use first available provider
            provider = next(iter(self.ai_providers.values()), None)
        
        if not provider:
            return None
        
        # Try text extraction first (faster)
        if text:
            try:
                result = provider.extract_event_info(text)
                if result:
                    return result
            except Exception as e:
                print(f"  AI text extraction error: {e}")
        
        # Try image analysis if provider supports it
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            result = provider.analyze_image(image_data)
            return result
        except Exception as e:
            print(f"  AI image analysis error: {e}")
            return None
    
    def _ai_extract_from_url(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Use AI to extract event info from image URL.
        
        Args:
            image_url: URL of the image
            
        Returns:
            Extracted event data or None
        """
        provider = self._get_ai_provider()
        if not provider:
            return None
        
        try:
            import requests
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            return provider.analyze_image(response.content)
        except Exception as e:
            print(f"  AI URL analysis error: {e}")
            return None
    
    def _ai_extract_from_bytes(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Use AI to extract event info from image bytes.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Extracted event data or None
        """
        provider = self._get_ai_provider()
        if not provider:
            return None
        
        try:
            return provider.analyze_image(image_data)
        except Exception as e:
            print(f"  AI bytes analysis error: {e}")
            return None
    
    def _get_ai_provider(self):
        """Get the configured AI provider.
        
        Returns:
            AI provider instance or None
        """
        if not self.ai_providers:
            return None
        
        default_provider = self.config.get('ai_provider')
        if default_provider and default_provider in self.ai_providers:
            return self.ai_providers[default_provider]
        
        return next(iter(self.ai_providers.values()), None)


def extract_event_data_from_image_url(image_url: str, languages: List = None,
                                       timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Extract event data from an image URL.
    
    Convenience function for scrapers that need to analyze images by URL.
    
    Args:
        image_url: URL of the image
        languages: OCR languages
        timeout: Request timeout
        
    Returns:
        Event data dictionary or None
    """
    try:
        import requests
        response = requests.get(image_url, timeout=timeout)
        response.raise_for_status()
        return extract_event_data_from_image(response.content, languages)
    except Exception as e:
        print(f"  Image URL extraction error: {e}")
        return None
