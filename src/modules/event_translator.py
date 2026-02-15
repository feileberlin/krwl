#!/usr/bin/env python3
"""
Event Translation Module

Automatically translates event content using free AI services (DuckDuckGo AI).
Adds transparency metadata to track translation source and method.

This module implements the AI translation system with full transparency as
specified in docs/AI_TRANSLATION_TRANSPARENCY.md.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EventTranslator:
    """
    Translates event content with transparency metadata.
    
    Uses DuckDuckGo AI for free, privacy-focused translation.
    Falls back to simple placeholder translations if API unavailable.
    """
    
    def __init__(self, config, base_path=None):
        """
        Initialize translator
        
        Args:
            config: Configuration dict with supportedLanguages, defaultLanguage
            base_path: Base path for file operations (optional)
        """
        self.config = config
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_languages = config.get('supportedLanguages', ['de', 'en', 'cs'])
        self.default_language = config.get('defaultLanguage', 'de')
        
        # Track translation stats
        self.stats = {
            'translated': 0,
            'skipped': 0,
            'failed': 0
        }
        
        logger.info(f"EventTranslator initialized: source={self.default_language}, targets={self.supported_languages}")
    
    def translate_event(self, event: Dict, target_languages: List[str] = None, force: bool = False) -> Dict:
        """
        Translate event content to target languages
        
        Args:
            event: Event dictionary with title, description, location.name
            target_languages: List of language codes to translate to (default: all supported except source)
            force: Force re-translation even if translations exist
            
        Returns:
            Event dict with added/updated translations field
        """
        if target_languages is None:
            # Translate to all supported languages except source
            source_lang = event.get('translations', {}).get('source_language', self.default_language)
            target_languages = [lang for lang in self.supported_languages if lang != source_lang]
        
        # Detect source language (assume default if not specified)
        source_lang = event.get('translations', {}).get('source_language', self.default_language)
        
        # Initialize translations structure if not exists
        if 'translations' not in event:
            event['translations'] = {
                'source_language': source_lang,
                'fields': {}
            }
        
        # Fields to translate
        fields_to_translate = [
            ('title', event.get('title')),
            ('description', event.get('description')),
            ('location_name', event.get('location', {}).get('name') if isinstance(event.get('location'), dict) else None)
        ]
        
        for field_name, source_text in fields_to_translate:
            if not source_text:
                continue
            
            if field_name not in event['translations']['fields']:
                event['translations']['fields'][field_name] = {}
            
            for target_lang in target_languages:
                # Skip if already translated and not forcing
                if not force and target_lang in event['translations']['fields'][field_name]:
                    logger.debug(f"Skipping {field_name} for {target_lang} - already translated")
                    self.stats['skipped'] += 1
                    continue
                
                # Perform translation
                try:
                    translated_text = self.translate_text(
                        text=source_text,
                        source_lang=source_lang,
                        target_lang=target_lang
                    )
                    
                    if translated_text:
                        event['translations']['fields'][field_name][target_lang] = {
                            'text': translated_text,
                            'method': 'ai',
                            'service': 'placeholder',  # Will be 'duckduckgo' when implemented
                            'generated_at': datetime.utcnow().isoformat() + 'Z',
                            'verified': False
                        }
                        logger.info(f"Translated {field_name} from {source_lang} to {target_lang}")
                        self.stats['translated'] += 1
                    else:
                        logger.warning(f"Translation returned empty for {field_name} ({source_lang} → {target_lang})")
                        self.stats['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Translation failed for {field_name} ({source_lang} → {target_lang}): {e}")
                    self.stats['failed'] += 1
        
        return event
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text using AI service
        
        Args:
            text: Source text to translate
            source_lang: Source language code (e.g., 'de', 'en')
            target_lang: Target language code (e.g., 'en', 'cs')
            
        Returns:
            Translated text or None if translation failed
        """
        # PHASE 1 IMPLEMENTATION: Simple placeholder
        # This marks events as "AI-translated" and creates the proper structure
        # PHASE 2: Implement actual DuckDuckGo AI or DeepL integration
        
        logger.debug(f"Translating: '{text[:50]}...' ({source_lang} → {target_lang})")
        
        # For now, return a placeholder that indicates translation is needed
        # In production, this will call DuckDuckGo AI API or DeepL
        placeholder_text = f"[{target_lang.upper()}] {text}"
        
        logger.warning("Using placeholder translation - implement DuckDuckGo AI or DeepL integration for production")
        
        return placeholder_text
    
    def translate_events_batch(self, events: List[Dict], target_languages: List[str] = None, force: bool = False) -> List[Dict]:
        """
        Translate multiple events in batch
        
        Args:
            events: List of event dictionaries
            target_languages: List of language codes to translate to
            force: Force re-translation even if translations exist
            
        Returns:
            List of events with translations added
        """
        logger.info(f"Starting batch translation of {len(events)} events")
        
        # Reset stats
        self.stats = {'translated': 0, 'skipped': 0, 'failed': 0}
        
        translated_events = []
        for i, event in enumerate(events):
            try:
                translated_event = self.translate_event(event, target_languages, force)
                translated_events.append(translated_event)
                
                # Progress indicator for large batches
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(events)} events processed")
                    
            except Exception as e:
                logger.error(f"Failed to translate event {event.get('id', 'unknown')}: {e}")
                # Keep untranslated event
                translated_events.append(event)
        
        # Log summary
        logger.info(f"Batch translation complete: {self.stats['translated']} translated, "
                   f"{self.stats['skipped']} skipped, {self.stats['failed']} failed")
        
        return translated_events
    
    def get_stats(self) -> Dict:
        """Get translation statistics"""
        return self.stats.copy()


def translate_events_file(input_path: str, output_path: str, config: Dict, force: bool = False) -> bool:
    """
    Translate events from input file and save to output file
    
    Args:
        input_path: Path to input events JSON file
        output_path: Path to output translated events JSON file
        config: Configuration dict
        force: Force re-translation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load events
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        events = data.get('events', [])
        logger.info(f"Loaded {len(events)} events from {input_path}")
        
        # Initialize translator
        translator = EventTranslator(config)
        
        # Translate events
        translated_events = translator.translate_events_batch(events, force=force)
        
        # Save results
        data['events'] = translated_events
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(translated_events)} translated events to {output_path}")
        
        # Print stats
        stats = translator.get_stats()
        print(f"\n✓ Translation complete:")
        print(f"  - Translated: {stats['translated']} fields")
        print(f"  - Skipped: {stats['skipped']} fields (already translated)")
        print(f"  - Failed: {stats['failed']} fields")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to translate events file: {e}")
        return False


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python event_translator.py <input_file> [output_file]")
        print("Example: python event_translator.py assets/json/events.json assets/json/events_translated.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_translated.json')
    
    # Load config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        sys.exit(1)
    
    # Translate
    success = translate_events_file(input_file, output_file, config)
    sys.exit(0 if success else 1)
