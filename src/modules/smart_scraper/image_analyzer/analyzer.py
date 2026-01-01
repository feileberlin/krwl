"""Main image analyzer combining OCR, metadata, and AI."""

from typing import Dict, Any, Optional
from .metadata import extract_metadata
from .ocr import extract_text, extract_dates, extract_times, extract_urls


class ImageAnalyzer:
    """Analyzes images to extract event information."""
    
    def __init__(self, config: Dict[str, Any], ai_providers: Dict[str, Any]):
        """Initialize image analyzer.
        
        Args:
            config: Image analysis configuration
            ai_providers: Dictionary of available AI providers
        """
        self.config = config
        self.ai_providers = ai_providers
        self.ocr_enabled = config.get('ocr_enabled', True)
        self.ocr_provider = config.get('ocr_provider', 'tesseract')
        self.languages = config.get('languages', ['eng', 'deu'])
    
    def analyze(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Analyze image to extract event information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted event data or None
        """
        result = {}
        
        # Extract metadata (GPS, datetime, etc.)
        metadata = extract_metadata(image_path)
        if metadata:
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
        
        # Extract text with OCR
        if self.ocr_enabled:
            text = extract_text(image_path, self.languages)
            if text:
                result['ocr_text'] = text
                
                # Extract structured data from text
                dates = extract_dates(text)
                if dates:
                    result['dates_found'] = dates
                
                times = extract_times(text)
                if times:
                    result['times_found'] = times
                
                urls = extract_urls(text)
                if urls:
                    result['urls_found'] = urls
                
                # Use AI to extract structured event info
                if self.ai_providers:
                    ai_result = self._ai_extract(text, image_path)
                    if ai_result:
                        result.update(ai_result)
        
        return result if result else None
    
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
            result = provider.extract_event_info(text)
            if result:
                return result
        
        # Try image analysis if provider supports it
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            result = provider.analyze_image(image_data)
            return result
        except Exception as e:
            print(f"  AI image analysis error: {e}")
            return None
