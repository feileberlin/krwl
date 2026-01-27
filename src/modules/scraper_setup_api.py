"""
Scraper Setup API - Backend for Visual Drag'n'Drop Scraper Configuration

This module provides API endpoints and utilities for the visual scraper setup tool.
It enables non-technical editors to configure event scrapers through a web interface
that can analyze HTML pages and map selectors to event schema fields.

Features:
- URL analysis and HTML structure detection
- Automatic selector suggestions based on common patterns
- Field mapping configuration generation
- CI/CD integration via GitHub Actions compatible output

Usage:
    # Analyze a URL for scraper setup
    from modules.scraper_setup_api import ScraperSetupAPI
    
    api = ScraperSetupAPI(base_path)
    analysis = api.analyze_url('https://example.com/events')
    
    # Generate CI-compatible configuration
    config = api.generate_ci_config(analysis, field_mappings)
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup, Tag
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    # Placeholder types when BeautifulSoup is not available
    BeautifulSoup = None
    Tag = None


class ScraperSetupAPI:
    """
    API for visual scraper configuration.
    
    Provides methods to analyze HTML pages and generate scraper configurations
    that work with GitHub Actions CI/CD pipelines.
    """
    
    # Event schema fields for mapping
    SCHEMA_FIELDS = {
        'title': {
            'type': 'text',
            'required': True,
            'description': 'Event title/name',
            'selectors': ['h1', 'h2', 'h3', '.title', '.event-name', '[class*="title"]', 'article h2']
        },
        'description': {
            'type': 'text',
            'required': False,
            'description': 'Event description',
            'selectors': ['p', '.description', '.event-description', 'article p', '[class*="desc"]']
        },
        'location_name': {
            'type': 'text',
            'required': True,
            'description': 'Venue/location name',
            'selectors': ['.location', '.venue', '[class*="ort"]', '[class*="location"]', '[class*="venue"]']
        },
        'location_address': {
            'type': 'text',
            'required': False,
            'description': 'Full address',
            'selectors': ['.address', '.adresse', '[class*="address"]', '[class*="adresse"]', 'address']
        },
        'start_date': {
            'type': 'datetime',
            'required': True,
            'description': 'Start date/time',
            'selectors': ['.date', '.datetime', 'time', '[class*="date"]', '[datetime]', '[class*="zeit"]']
        },
        'end_date': {
            'type': 'datetime',
            'required': False,
            'description': 'End date/time',
            'selectors': ['.end-date', '.end-time', '[class*="end"]']
        },
        'url': {
            'type': 'link',
            'required': False,
            'description': 'Event detail page URL',
            'selectors': ['a[href*="detail"]', 'a[href*="event"]', '.more-info a', 'a.event-link']
        },
        'image': {
            'type': 'image',
            'required': False,
            'description': 'Event image/poster',
            'selectors': ['img', '.event-image img', '[class*="image"] img', 'figure img']
        },
        'category': {
            'type': 'text',
            'required': False,
            'description': 'Event category',
            'selectors': ['.category', '.type', '[class*="category"]', '[class*="type"]', '[class*="tag"]']
        },
        'price': {
            'type': 'text',
            'required': False,
            'description': 'Price information',
            'selectors': ['.price', '.cost', '[class*="price"]', '[class*="cost"]', '[class*="eintritt"]']
        }
    }
    
    # Common container selectors for event listings
    EVENT_CONTAINER_SELECTORS = [
        '.event', '.veranstaltung', 'article.event', '[class*="event"]',
        '.calendar-item', '.event-item', '.listing-item', '.item',
        'article', '.entry', '[itemtype*="Event"]'
    ]
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.mappings_dir = self.base_path / 'config' / 'scraper_mappings'
        self.mappings_dir.mkdir(parents=True, exist_ok=True)
        
        if SCRAPING_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        else:
            self.session = None
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a URL for scraper configuration.
        
        Fetches the page, analyzes its HTML structure, and returns
        suggestions for event container and field selectors.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Analysis result with detected structure and suggestions
        """
        if not SCRAPING_AVAILABLE:
            return {
                'success': False,
                'error': 'Scraping libraries not available. Install requests and beautifulsoup4.',
                'url': url
            }
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            # Use html.parser as fallback if lxml is not available
            try:
                soup = BeautifulSoup(response.content, 'lxml')
            except Exception:
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # Analyze page structure
            analysis = {
                'success': True,
                'url': url,
                'analyzed_at': datetime.now().isoformat(),
                'page_title': soup.title.string if soup.title else None,
                'structure': self._analyze_structure(soup, url),
                'suggestions': self._generate_suggestions(soup),
                'detected_containers': self._detect_event_containers(soup),
                'sample_elements': self._extract_sample_elements(soup, url)
            }
            
            return analysis
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to fetch URL: {str(e)}',
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'url': url
            }
    
    def _analyze_structure(self, soup: 'BeautifulSoup', url: str) -> Dict[str, Any]:
        """Analyze the HTML structure of the page."""
        structure = {
            'total_elements': len(soup.find_all()),
            'headings': {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4'))
            },
            'links': len(soup.find_all('a', href=True)),
            'images': len(soup.find_all('img')),
            'articles': len(soup.find_all('article')),
            'common_classes': self._get_common_classes(soup),
            'has_schema_org': bool(soup.find(attrs={'itemtype': True})),
            'has_json_ld': bool(soup.find('script', type='application/ld+json'))
        }
        
        return structure
    
    def _get_common_classes(self, soup: 'BeautifulSoup', limit: int = 15) -> List[Dict[str, Any]]:
        """Get most common CSS classes on the page."""
        from collections import Counter
        
        all_classes = []
        for tag in soup.find_all(class_=True):
            all_classes.extend(tag.get('class', []))
        
        common = Counter(all_classes).most_common(limit)
        return [{'class': cls, 'count': count} for cls, count in common]
    
    def _detect_event_containers(self, soup: 'BeautifulSoup') -> List[Dict[str, Any]]:
        """Detect potential event container elements."""
        containers = []
        
        for selector in self.EVENT_CONTAINER_SELECTORS:
            elements = soup.select(selector)
            if elements:
                # Get sample content from first element
                sample = elements[0]
                sample_text = sample.get_text(strip=True)[:150]
                
                containers.append({
                    'selector': selector,
                    'count': len(elements),
                    'sample_text': sample_text,
                    'has_links': bool(sample.find('a', href=True)),
                    'has_dates': self._contains_date_pattern(sample.get_text()),
                    'confidence': self._calculate_container_confidence(sample)
                })
        
        # Sort by confidence
        containers.sort(key=lambda x: x['confidence'], reverse=True)
        return containers[:5]  # Return top 5
    
    def _contains_date_pattern(self, text: str) -> bool:
        """Check if text contains date patterns."""
        patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}\s+(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _calculate_container_confidence(self, element: 'Tag') -> float:
        """Calculate confidence score for an element being an event container."""
        score = 0.0
        
        # Check for typical event structure
        if element.find(['h1', 'h2', 'h3', 'h4']):
            score += 0.2
        
        if element.find('a', href=True):
            score += 0.15
        
        if element.find('time') or element.find(attrs={'datetime': True}):
            score += 0.25
        
        if self._contains_date_pattern(element.get_text()):
            score += 0.2
        
        # Check for location indicators
        location_classes = ['location', 'venue', 'ort', 'address']
        for cls in element.get('class', []):
            if any(loc in cls.lower() for loc in location_classes):
                score += 0.1
                break
        
        # Check element size (events usually have substantial content)
        text_length = len(element.get_text(strip=True))
        if 50 < text_length < 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_suggestions(self, soup: 'BeautifulSoup') -> Dict[str, List[Dict[str, Any]]]:
        """Generate selector suggestions for each schema field."""
        suggestions = {}
        
        for field_name, field_info in self.SCHEMA_FIELDS.items():
            field_suggestions = []
            
            for selector in field_info['selectors']:
                elements = soup.select(selector)
                if elements:
                    # Get sample from first element
                    sample = elements[0]
                    
                    if field_info['type'] == 'link':
                        value = sample.get('href', '')
                    elif field_info['type'] == 'image':
                        value = sample.get('src', '')
                    else:
                        value = sample.get_text(strip=True)[:100]
                    
                    field_suggestions.append({
                        'selector': selector,
                        'count': len(elements),
                        'sample_value': value,
                        'tag': sample.name,
                        'classes': sample.get('class', [])
                    })
            
            suggestions[field_name] = field_suggestions
        
        return suggestions
    
    def _extract_sample_elements(self, soup: 'BeautifulSoup', base_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract sample elements for drag-and-drop preview."""
        samples = []
        
        # Find likely event containers
        for selector in self.EVENT_CONTAINER_SELECTORS:
            containers = soup.select(selector)[:limit]
            
            for container in containers:
                sample = {
                    'selector': selector,
                    'html_preview': str(container)[:500],
                    'fields': {}
                }
                
                # Try to extract field values
                for field_name, field_info in self.SCHEMA_FIELDS.items():
                    for field_selector in field_info['selectors']:
                        element = container.select_one(field_selector)
                        if element:
                            if field_info['type'] == 'link':
                                href = element.get('href', '')
                                value = urljoin(base_url, href) if href else ''
                            elif field_info['type'] == 'image':
                                src = element.get('src', '')
                                value = urljoin(base_url, src) if src else ''
                            else:
                                value = element.get_text(strip=True)[:200]
                            
                            sample['fields'][field_name] = {
                                'selector': field_selector,
                                'value': value
                            }
                            break
                
                if sample['fields']:
                    samples.append(sample)
                    
            if samples:
                break  # Stop after finding a working container type
        
        return samples[:5]  # Return max 5 samples
    
    def generate_ci_config(self, source_name: str, url: str, 
                          field_mappings: Dict[str, Dict[str, str]],
                          container_selector: str = None) -> Dict[str, Any]:
        """
        Generate CI-compatible scraper configuration.
        
        Args:
            source_name: Name for the source
            url: Source URL
            field_mappings: Dict of field_name -> {selector, extraction_method}
            container_selector: Optional container selector for event listings
            
        Returns:
            CI configuration dict
        """
        config = {
            'version': '2.0',
            'source': {
                'name': source_name,
                'url': url,
                'type': 'html',
                'enabled': True
            },
            'container': {
                'selector': container_selector or '.event'
            },
            'field_mappings': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'created_by': 'scraper-setup-tool',
                'version': '1.0'
            }
        }
        
        for field_name, mapping in field_mappings.items():
            config['field_mappings'][field_name] = {
                'selector': mapping.get('selector', ''),
                'extraction': mapping.get('extraction_method', 'text'),
                'required': self.SCHEMA_FIELDS.get(field_name, {}).get('required', False)
            }
        
        return config
    
    def save_ci_config(self, config: Dict[str, Any], source_name: str) -> Path:
        """
        Save CI configuration to file.
        
        Args:
            config: CI configuration dict
            source_name: Source name for filename
            
        Returns:
            Path to saved file
        """
        filename = f"{source_name.lower().replace(' ', '_')}_ci_config.json"
        filepath = self.mappings_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        return filepath
    
    def list_saved_configs(self) -> List[Dict[str, Any]]:
        """List all saved CI configurations."""
        configs = []
        
        for config_file in self.mappings_dir.glob('*_ci_config.json'):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                configs.append({
                    'filename': config_file.name,
                    'path': str(config_file),
                    'source_name': data.get('source', {}).get('name', 'Unknown'),
                    'url': data.get('source', {}).get('url', ''),
                    'created_at': data.get('metadata', {}).get('created_at', '')
                })
            except Exception:
                continue
        
        return configs
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a CI configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required structure
        if 'source' not in config:
            errors.append("Missing 'source' section")
        else:
            if not config['source'].get('name'):
                errors.append("Missing source name")
            if not config['source'].get('url'):
                errors.append("Missing source URL")
        
        if 'field_mappings' not in config:
            errors.append("Missing 'field_mappings' section")
        else:
            mappings = config['field_mappings']
            
            # Check required fields
            for field_name, field_info in self.SCHEMA_FIELDS.items():
                if field_info['required'] and field_name not in mappings:
                    errors.append(f"Missing required field mapping: {field_name}")
        
        return len(errors) == 0, errors
    
    def get_schema_fields(self) -> Dict[str, Any]:
        """Get schema field definitions for frontend use."""
        return self.SCHEMA_FIELDS.copy()


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scraper Setup API - Analyze URLs for scraper configuration'
    )
    parser.add_argument('--analyze', metavar='URL', help='Analyze a URL')
    parser.add_argument('--list', action='store_true', help='List saved configurations')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent.parent
    api = ScraperSetupAPI(base_path)
    
    if args.analyze:
        result = api.analyze_url(args.analyze)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result['success']:
                print(f"\n✓ URL Analysis: {result['url']}")
                print(f"\nPage Title: {result['page_title']}")
                print(f"\nStructure:")
                print(f"  - Total elements: {result['structure']['total_elements']}")
                print(f"  - Links: {result['structure']['links']}")
                print(f"  - Images: {result['structure']['images']}")
                
                print(f"\nDetected Event Containers:")
                for container in result['detected_containers']:
                    print(f"  - {container['selector']} ({container['count']} found, confidence: {container['confidence']:.2f})")
                
                print(f"\nField Suggestions:")
                for field, suggestions in result['suggestions'].items():
                    if suggestions:
                        print(f"  {field}: {suggestions[0]['selector']} ({suggestions[0]['count']} found)")
            else:
                print(f"\n✗ Analysis failed: {result['error']}")
                
    elif args.list:
        configs = api.list_saved_configs()
        if args.json:
            print(json.dumps(configs, indent=2))
        else:
            if configs:
                print("\nSaved CI Configurations:")
                for config in configs:
                    print(f"  - {config['source_name']}: {config['url']}")
            else:
                print("\nNo saved configurations found.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
