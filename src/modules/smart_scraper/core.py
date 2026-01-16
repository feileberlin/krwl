"""SmartScraper orchestrator - coordinates scrapers, AI, and image analysis."""

import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base import SourceOptions, ScraperRegistry

# Configure module logger
logger = logging.getLogger(__name__)


class SmartScraper:
    """Main orchestrator for the modular scraper system."""
    
    def __init__(self, config: Dict[str, Any], base_path: str):
        """Initialize SmartScraper.
        
        Args:
            config: Full configuration dictionary
            base_path: Base path for data files
        """
        self.config = config
        self.base_path = base_path
        self.registry = ScraperRegistry()
        self.ai_providers = {}
        self.image_analyzer = None
        
        # Initialize components
        self._init_ai_providers()
        self._init_image_analyzer()
        self._register_sources()
    
    def _init_ai_providers(self):
        """Initialize AI providers based on configuration."""
        ai_config = self.config.get('ai', {})
        if not ai_config:
            return
        
        # Try to import and initialize AI providers
        try:
            from .ai_providers import get_available_providers
            providers = get_available_providers(ai_config)
            self.ai_providers = providers
            if providers:
                logger.info(f"Initialized {len(providers)} AI provider(s)")
        except ImportError:
            logger.debug("AI providers not available (optional)")
        except Exception as e:
            logger.warning(f"AI provider initialization warning: {e}")
    
    def _init_image_analyzer(self):
        """Initialize image analyzer if enabled."""
        img_config = self.config.get('image_analysis', {})
        if not img_config.get('enabled', False):
            return
        
        try:
            from .image_analyzer import ImageAnalyzer
            self.image_analyzer = ImageAnalyzer(img_config, self.ai_providers)
            logger.info("Initialized image analyzer")
        except ImportError:
            logger.debug("Image analysis not available (optional)")
        except Exception as e:
            logger.warning(f"Image analyzer initialization warning: {e}")
    
    def _register_sources(self):
        """Register all available source types."""
        # Register traditional web sources
        self._register_web_sources()
        
        # Register social media sources
        self._register_social_sources()
        
        # Register custom source handlers
        self._register_custom_sources()
    
    def _register_web_sources(self):
        """Register traditional web source handlers."""
        try:
            from .sources.web import rss, html, api, atom
            
            # Register with factory functions
            self.registry.register('rss', 
                lambda cfg, opts, base_path=self.base_path,
                ai_providers=self.ai_providers: rss.RSSSource(
                    cfg, opts, base_path=base_path, ai_providers=ai_providers
                ))
            self.registry.register('html', 
                lambda cfg, opts, base_path=self.base_path,
                ai_providers=self.ai_providers: html.HTMLSource(
                    cfg, opts, base_path=base_path, ai_providers=ai_providers
                ))
            self.registry.register('api', 
                lambda cfg, opts, base_path=self.base_path,
                ai_providers=self.ai_providers: api.APISource(
                    cfg, opts, base_path=base_path, ai_providers=ai_providers
                ))
            self.registry.register('atom', 
                lambda cfg, opts, base_path=self.base_path,
                ai_providers=self.ai_providers: atom.AtomSource(
                    cfg, opts, base_path=base_path, ai_providers=ai_providers
                ))
        except ImportError as e:
            logger.warning(f"Some web sources unavailable: {e}")
    
    def _register_social_sources(self):
        """Register social media source handlers."""
        try:
            from .sources import social
            
            # Try to register each social platform
            social_platforms = [
                ('facebook', 'FacebookSource'),
                ('instagram', 'InstagramSource'),
                ('tiktok', 'TikTokSource'),
                ('x', 'XTwitterSource'),
                ('twitter', 'XTwitterSource'),  # Alias
                ('telegram', 'TelegramSource'),
                ('whatsapp', 'WhatsAppSource')
            ]
            
            for platform_type, class_name in social_platforms:
                try:
                    source_class = getattr(social, class_name, None)
                    if source_class:
                        self.registry.register(
                            platform_type,
                            lambda cfg, opts, cls=source_class, base_path=self.base_path,
                            ai_providers=self.ai_providers: cls(
                                cfg, opts, base_path=base_path, ai_providers=ai_providers
                            )
                        )
                except AttributeError:
                    pass  # Platform not yet implemented
        except ImportError:
            pass  # Social sources not yet implemented
    
    def _register_custom_sources(self):
        """Register custom source handlers for specific sites."""
        try:
            from .sources import frankenpost
            
            # Register Frankenpost custom handler
            # This will be used instead of generic HTML scraper for Frankenpost
            self.registry.register('frankenpost',
                lambda cfg, opts, base_path=self.base_path,
                ai_providers=self.ai_providers: frankenpost.FrankenpostSource(
                    cfg, opts, base_path=base_path, ai_providers=ai_providers
                ))
        except ImportError as e:
            logger.debug(f"Custom sources unavailable: {e}")
    
    def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape events from all enabled sources.
        
        Returns:
            List of scraped event dictionaries
        """
        all_events = []
        sources = self.config.get('scraping', {}).get('sources', [])
        
        for source in sources:
            if not source.get('enabled', False):
                print(f"⊘ Skipping disabled source: {source['name']}")
                continue
            
            print(f"🔍 Scraping from: {source['name']}")
            try:
                events = self.scrape_source(source)
                
                # Apply filtering
                events = self._filter_events(events, source)
                
                all_events.extend(events)
                print(f"  ✓ Found {len(events)} events")
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
        
        return all_events
    
    def scrape_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape events from a single source.
        
        Args:
            source: Source configuration dictionary
            
        Returns:
            List of event dictionaries
        """
        source_type = source.get('type', 'html')
        source_name = str(source.get('name', '')).strip().lower()
        
        # Check for custom source handlers first (by exact source name)
        # This allows overriding default handlers for specific sites while
        # avoiding accidental matches when names merely contain "frankenpost".
        if source_name == 'frankenpost':
            source_type = 'frankenpost'
        
        # Get source-specific options
        options = SourceOptions.from_dict(source.get('options', {}))
        
        # Get handler from registry
        handler_factory = self.registry.get_handler(source_type)
        if not handler_factory:
            print(f"  ⚠ No handler for source type: {source_type}")
            # Fall back to legacy scraper
            return self._fallback_scraper(source)
        
        # Create source instance and scrape
        try:
            source_instance = handler_factory(source, options)
            events = source_instance.scrape()
            return events
        except Exception as e:
            print(f"    Error in {source_type} scraper: {e}")
            return []
    
    def _filter_events(self, events: List[Dict[str, Any]], 
                      source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filtering to scraped events.
        
        Args:
            events: List of event dictionaries
            source: Source configuration
            
        Returns:
            Filtered list of events
        """
        options = SourceOptions.from_dict(source.get('options', {}))
        filtered_events = []
        
        for event in events:
            # Apply keyword filtering
            if options.should_filter(
                f"{event.get('title', '')} {event.get('description', '')}"
            ):
                continue
            
            # Apply date range filtering if configured
            if not self._check_date_range(event, options):
                continue
            
            # Apply location validation if configured
            if options.validate_location and not self._validate_location(event, options):
                continue
            
            # Add category if specified
            if options.category and 'category' not in event:
                event['category'] = options.category
            
            filtered_events.append(event)
        
        return filtered_events
    
    def _check_date_range(self, event: Dict[str, Any], 
                         options: SourceOptions) -> bool:
        """Check if event is within configured date range.
        
        Args:
            event: Event dictionary
            options: Source options
            
        Returns:
            True if event is in range, False otherwise
        """
        if options.max_days_ahead is None and options.min_days_ahead == 0:
            return True
        
        try:
            start_time = event.get('start_time')
            if not start_time:
                return True  # No date filtering if no start time
            
            event_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            now = datetime.now(event_date.tzinfo)
            days_ahead = (event_date - now).days
            
            if options.min_days_ahead > 0 and days_ahead < options.min_days_ahead:
                return False
            
            if options.max_days_ahead and days_ahead > options.max_days_ahead:
                return False
            
            return True
        except (ValueError, TypeError):
            return True  # Don't filter if date parsing fails
    
    def _validate_location(self, event: Dict[str, Any], 
                          options: SourceOptions) -> bool:
        """Validate event location is within radius.
        
        Args:
            event: Event dictionary
            options: Source options
            
        Returns:
            True if location is valid, False otherwise
        """
        if not options.location_radius_km:
            return True
        
        # Location validation would require haversine distance calc
        # For now, always pass if location exists
        return 'location' in event and event['location']
    
    def _fallback_scraper(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback to legacy scraper for unsupported source types.
        
        Args:
            source: Source configuration
            
        Returns:
            List of events (empty if not supported)
        """
        print(f"  ℹ Using fallback scraper (limited functionality)")
        
        # Import legacy scraper
        try:
            from ..scraper import EventScraper
            legacy_scraper = EventScraper(self.config, self.base_path)
            return legacy_scraper.scrape_source(source)
        except Exception as e:
            print(f"    Fallback scraper error: {e}")
            return []
    
    def analyze_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Analyze an image to extract event information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted event data or None
        """
        if not self.image_analyzer:
            print("⚠ Image analysis not available")
            return None
        
        try:
            return self.image_analyzer.analyze(image_path)
        except Exception as e:
            print(f"✗ Image analysis error: {e}")
            return None
    
    def get_ai_provider(self, provider_name: Optional[str] = None) -> Optional[Any]:
        """Get an AI provider by name or default.
        
        Args:
            provider_name: Name of provider or None for default
            
        Returns:
            AI provider instance or None
        """
        if not self.ai_providers:
            return None
        
        if provider_name:
            return self.ai_providers.get(provider_name)
        
        # Return default provider
        default_name = self.config.get('ai', {}).get('default_provider')
        if default_name:
            return self.ai_providers.get(default_name)
        
        # Return first available
        return next(iter(self.ai_providers.values()), None)
