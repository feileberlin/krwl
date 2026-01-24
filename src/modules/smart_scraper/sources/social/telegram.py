"""Telegram source for event scraping and flyer processing.

This module provides Telegram integration for the smart scraper:
1. Processing uploaded flyers with shared OCR infrastructure
2. (Future) Scraping public Telegram channels for event announcements

The flyer processing uses the same image_analyzer that Instagram, Facebook,
and other social media scrapers use, ensuring consistent event extraction.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from io import BytesIO
from datetime import datetime
import logging

from ...base import BaseSource, SourceOptions
from ...image_analyzer import ImageAnalyzer
from ...image_analyzer.ocr import extract_event_data_from_image, is_ocr_available

logger = logging.getLogger(__name__)


class TelegramSource(BaseSource):
    """Telegram events scraper and flyer processor.
    
    This source can:
    1. Process uploaded flyers (via process_flyer method)
    2. Scrape public Telegram channels (future implementation)
    
    Example usage:
        # Process an uploaded flyer
        source = TelegramSource(config, options)
        event = source.process_flyer('/path/to/flyer.jpg', user_id='123', username='user')
        
        # Scrape public channel (future)
        events = source.scrape()
    """
    
    def __init__(self, config: Dict[str, Any], options: SourceOptions):
        """Initialize Telegram source.
        
        Args:
            config: Smart scraper configuration
            options: Source options
        """
        super().__init__(config, options)
        
        # Initialize image analyzer for flyer processing
        image_config = config.get('image_analysis', {})
        self.image_analyzer = ImageAnalyzer(image_config)
        
        # Cache directory for downloaded files
        self.cache_dir = Path(options.cache_path or '.cache/telegram')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape events from Telegram public channels.
        
        Note: Full channel scraping requires Telegram API access.
        For now, this returns events from cached flyer uploads.
        
        Returns:
            List of scraped events
        """
        events = []
        
        # Check for any cached flyers that haven't been processed
        for flyer_path in self.cache_dir.glob('flyer_*.jpg'):
            metadata_path = flyer_path.with_suffix('.json')
            if metadata_path.exists():
                # Already processed, skip
                continue
            
            try:
                event = self.process_flyer(str(flyer_path))
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error processing cached flyer {flyer_path}: {e}")
        
        if not events:
            print(f"    ℹ️ No new Telegram flyers to process")
            print(f"    → Upload flyers via Telegram bot or manually add to {self.cache_dir}")
        
        return events
    
    def process_flyer(self, image_source: Union[str, bytes, Path],
                      user_id: str = None,
                      username: str = None,
                      caption: str = None,
                      file_name: str = None) -> Optional[Dict[str, Any]]:
        """Process an uploaded flyer image using shared OCR infrastructure.
        
        This method uses the same ImageAnalyzer that Instagram, Facebook,
        and other scrapers use, ensuring consistent event extraction.
        
        Args:
            image_source: Path to image file, or bytes data
            user_id: Telegram user ID who uploaded the flyer
            username: Telegram username
            caption: Original caption from the message
            file_name: Original file name
            
        Returns:
            Extracted event dictionary or None
        """
        if not is_ocr_available():
            logger.warning("OCR not available - cannot process flyer")
            return None
        
        try:
            # Use shared image analyzer
            if isinstance(image_source, bytes):
                result = self.image_analyzer.analyze_bytes(image_source)
            else:
                result = self.image_analyzer.analyze(str(image_source))
            
            if not result:
                logger.warning("No event data extracted from flyer")
                return None
            
            # Convert to event format
            timestamp = datetime.now().isoformat()
            event = {
                'id': f'telegram_flyer_{user_id or "unknown"}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'title': result.get('title_hint', 'Telegram Flyer Submission'),
                'description': result.get('ocr_text', caption or ''),
                'teaser': caption or 'Event submitted via Telegram flyer upload',
                'location': result.get('location', {
                    'name': 'Hof',  # Default location
                    'lat': 50.3167,
                    'lon': 11.9167
                }),
                'start_time': self._parse_date_hint(result.get('date_hint'), result.get('time_hint')),
                'end_time': None,
                'url': result.get('urls', [None])[0] if result.get('urls') else None,
                'source': 'telegram',
                'scraped_at': timestamp,
                'status': 'pending',
                'category': self._categorize_event(result.get('keywords', {})),
                'metadata': {
                    'telegram_user_id': user_id,
                    'telegram_username': username,
                    'telegram_file_name': file_name,
                    'telegram_caption': caption,
                    'submitted_via': 'telegram_flyer_ocr',
                    'ocr_confidence': result.get('ocr_confidence', 0),
                    'dates_found': result.get('dates_found', []),
                    'times_found': result.get('times_found', []),
                    'prices_found': result.get('prices_found', []),
                    'needs_review': True
                }
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Error processing flyer: {e}")
            return None
    
    def _parse_date_hint(self, date_hint: str, time_hint: str) -> str:
        """Parse date and time hints into ISO format.
        
        Args:
            date_hint: Date string from OCR
            time_hint: Time string from OCR
            
        Returns:
            ISO format datetime string
        """
        # For now, return current time as placeholder
        # The editorial review will set the correct date
        return datetime.now().isoformat()
    
    def _categorize_event(self, keywords: Dict[str, List[str]]) -> str:
        """Categorize event based on extracted keywords.
        
        Args:
            keywords: Extracted keyword categories
            
        Returns:
            Event category string
        """
        event_types = keywords.get('event_type', [])
        music_genres = keywords.get('music_genre', [])
        
        # Map keywords to categories
        if any(t in ['konzert', 'concert', 'live'] for t in event_types):
            return 'music'
        if any(t in ['party', 'festival'] for t in event_types):
            return 'nightlife'
        if any(t in ['ausstellung', 'exhibition', 'vernissage'] for t in event_types):
            return 'art'
        if any(t in ['theater', 'comedy', 'kabarett'] for t in event_types):
            return 'culture'
        if any(t in ['workshop', 'lesung', 'reading'] for t in event_types):
            return 'education'
        if music_genres:
            return 'music'
        
        return 'community'  # Default category


def process_telegram_flyer(image_path: str, 
                           user_id: str = None,
                           username: str = None,
                           caption: str = None) -> Optional[Dict[str, Any]]:
    """Convenience function to process a Telegram flyer.
    
    This function can be used by the GitHub Actions workflow to process
    uploaded flyers without instantiating the full source class.
    
    Args:
        image_path: Path to the flyer image
        user_id: Telegram user ID
        username: Telegram username
        caption: Original caption
        
    Returns:
        Extracted event dictionary or None
    """
    config = {}
    options = SourceOptions(name='telegram')
    source = TelegramSource(config, options)
    return source.process_flyer(image_path, user_id, username, caption)
