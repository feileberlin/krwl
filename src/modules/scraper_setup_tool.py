"""
Interactive Scraper Setup Tool with Field Mapping

This tool allows editors to interactively map HTML/CSS selectors to event schema fields
by analyzing live pages and providing a visual/textual interface for field mapping.

It adds "human understanding" to the scraping process by allowing non-technical editors
to configure scrapers through an intuitive interface.

Usage:
    # Interactive mode (TUI)
    python3 src/modules/scraper_setup_tool.py

    # Wizard mode with URL
    python3 src/modules/scraper_setup_tool.py --url https://example.com/events

    # Test existing mapping
    python3 src/modules/scraper_setup_tool.py --test frankenpost

    # Export mapping for CI/automation
    python3 src/modules/scraper_setup_tool.py --export frankenpost
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("⚠️  Scraping libraries not available. Install with: pip install requests beautifulsoup4 lxml")


class ScraperFieldMapper:
    """
    Interactive tool for mapping HTML/CSS selectors to event schema fields.
    
    Allows editors to "teach" the scraper by:
    1. Analyzing a live event page
    2. Identifying HTML elements for each field
    3. Saving the mapping configuration
    4. Testing the mapping on sample data
    """
    
    # Event schema fields that can be mapped
    SCHEMA_FIELDS = {
        'title': {
            'type': 'text',
            'required': True,
            'description': 'Event title/name',
            'hints': ['h1', 'h2', 'h3', '.title', '.event-name', '[class*="title"]']
        },
        'description': {
            'type': 'text',
            'required': False,
            'description': 'Event description/details',
            'hints': ['p', '.description', '.event-description', 'article', '[class*="desc"]']
        },
        'location_name': {
            'type': 'text',
            'required': True,
            'description': 'Venue/location name',
            'hints': ['.location', '.venue', '[class*="ort"]', '[class*="location"]']
        },
        'location_address': {
            'type': 'text',
            'required': False,
            'description': 'Full address (Street, ZIP, City)',
            'hints': ['.address', '.adresse', '[class*="address"]', '[class*="adresse"]']
        },
        'start_date': {
            'type': 'text',
            'required': True,
            'description': 'Start date/time',
            'hints': ['.date', '.datetime', 'time', '[class*="date"]', '[datetime]']
        },
        'end_date': {
            'type': 'text',
            'required': False,
            'description': 'End date/time',
            'hints': ['.end-date', '.end-time', '[class*="end"]']
        },
        'url': {
            'type': 'link',
            'required': False,
            'description': 'Event detail page URL',
            'hints': ['a[href*="detail"]', 'a[href*="event"]', '.more-info a']
        },
        'image': {
            'type': 'image',
            'required': False,
            'description': 'Event image/poster',
            'hints': ['img', '.event-image img', '[class*="image"] img']
        },
        'category': {
            'type': 'text',
            'required': False,
            'description': 'Event category/type',
            'hints': ['.category', '.type', '[class*="category"]', '[class*="type"]']
        },
        'price': {
            'type': 'text',
            'required': False,
            'description': 'Price/cost information',
            'hints': ['.price', '.cost', '[class*="price"]', '[class*="cost"]']
        }
    }
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.mappings_dir = self.base_path / 'config' / 'scraper_mappings'
        self.mappings_dir.mkdir(parents=True, exist_ok=True)
    
    def interactive_setup(self, url: Optional[str] = None):
        """
        Interactive wizard for setting up scraper field mapping.
        
        Guides the user through:
        1. Entering the event source URL
        2. Fetching and analyzing the page
        3. Identifying selectors for each field
        4. Testing the mapping
        5. Saving the configuration
        """
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║        Interactive Scraper Setup & Field Mapping Tool         ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        
        # Step 1: Get source information
        if not url:
            url = self._prompt_for_url()
        
        source_name = self._prompt_for_source_name()
        
        print(f"\n📡 Fetching page: {url}")
        soup = self._fetch_page(url)
        
        if not soup:
            print("❌ Failed to fetch page. Please check the URL and try again.")
            return
        
        print("✓ Page fetched successfully")
        
        # Step 2: Analyze page structure
        print("\n🔍 Analyzing page structure...")
        self._analyze_page_structure(soup)
        
        # Step 3: Interactive field mapping
        print("\n📝 Now let's map fields to HTML selectors")
        print("   (For each field, you'll provide a CSS selector)")
        print()
        
        field_mapping = self._interactive_field_mapping(soup, url)
        
        # Step 4: Test the mapping
        print("\n🧪 Testing field mapping...")
        test_results = self._test_mapping(soup, field_mapping)
        self._display_test_results(test_results)
        
        # Step 5: Save configuration
        if self._confirm("Save this mapping configuration?"):
            config_file = self._save_mapping(source_name, url, field_mapping)
            print(f"\n✓ Configuration saved to: {config_file}")
            print(f"\nYou can now use this mapping with:")
            print(f"  python3 src/modules/custom_source_manager.py create {source_name} \\")
            print(f"    --url {url} \\")
            print(f"    --mapping-file {config_file}")
        else:
            print("\n❌ Configuration not saved")
    
    def _prompt_for_url(self) -> str:
        """Prompt user for event listing URL."""
        print("Step 1: Enter the event source URL")
        print("  (This should be the main events listing page)")
        print()
        
        while True:
            url = input("Event listing URL: ").strip()
            if url and (url.startswith('http://') or url.startswith('https://')):
                return url
            print("❌ Please enter a valid HTTP(S) URL")
    
    def _prompt_for_source_name(self) -> str:
        """Prompt user for source name."""
        print("\nStep 2: Enter a name for this event source")
        print("  (e.g., 'LocalNews', 'CityEvents', 'CommunityCalendar')")
        print()
        
        while True:
            name = input("Source name: ").strip()
            if name and name.replace('_', '').replace('-', '').isalnum():
                return name
            print("❌ Please enter a valid name (letters, numbers, _, - only)")
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse URL."""
        if not SCRAPING_AVAILABLE:
            return None
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def _analyze_page_structure(self, soup: BeautifulSoup):
        """Analyze and display page structure to help with field mapping."""
        print("\n  Page Structure Analysis:")
        print("  " + "─" * 60)
        
        # Count common elements
        event_containers = len(soup.select('.event, article, .item, [class*="event"]'))
        headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4']))
        links = len(soup.find_all('a', href=True))
        images = len(soup.find_all('img'))
        
        print(f"  Potential event containers: {event_containers}")
        print(f"  Headings (h1-h4): {headings}")
        print(f"  Links: {links}")
        print(f"  Images: {images}")
        print("  " + "─" * 60)
        
        # Show some common classes
        all_classes = []
        for tag in soup.find_all(class_=True):
            all_classes.extend(tag.get('class', []))
        
        from collections import Counter
        common_classes = Counter(all_classes).most_common(10)
        
        if common_classes:
            print("\n  Most common CSS classes (might be useful):")
            for cls, count in common_classes:
                print(f"    .{cls} ({count} times)")
    
    def _interactive_field_mapping(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Interactive field-by-field mapping.
        
        For each schema field, prompts user for CSS selector and validates.
        """
        field_mapping = {
            'source_url': url,
            'created_at': datetime.now().isoformat(),
            'fields': {}
        }
        
        for field_name, field_info in self.SCHEMA_FIELDS.items():
            print(f"\n{'='*60}")
            print(f"Field: {field_name}")
            print(f"Description: {field_info['description']}")
            print(f"Required: {'Yes' if field_info['required'] else 'No'}")
            print(f"\nSuggested selectors to try:")
            for hint in field_info['hints'][:5]:
                print(f"  • {hint}")
            print()
            
            # Prompt for selector
            selector = input(f"CSS selector for '{field_name}' (or 'skip'): ").strip()
            
            if selector.lower() == 'skip':
                if field_info['required']:
                    print("⚠️  This is a required field, but you can configure it later")
                continue
            
            if not selector:
                continue
            
            # Test selector on page
            print(f"  Testing selector: {selector}")
            elements = soup.select(selector)
            
            if not elements:
                print(f"  ⚠️  No elements found with selector: {selector}")
                retry = input("  Try a different selector? (y/n): ").strip().lower()
                if retry == 'y':
                    # Recursive call for this field
                    selector = input(f"  New selector for '{field_name}': ").strip()
                    elements = soup.select(selector)
            
            if elements:
                print(f"  ✓ Found {len(elements)} element(s)")
                
                # Show first few matches
                print(f"  First match preview:")
                first_elem = elements[0]
                content = first_elem.get_text(strip=True)[:100]
                print(f"    {content}...")
                
                # Ask for extraction method
                extraction_method = self._prompt_extraction_method(field_info['type'])
                
                # Save mapping
                field_mapping['fields'][field_name] = {
                    'selector': selector,
                    'extraction_method': extraction_method,
                    'field_type': field_info['type'],
                    'required': field_info['required']
                }
                
                print(f"  ✓ Mapping saved for '{field_name}'")
        
        return field_mapping
    
    def _prompt_extraction_method(self, field_type: str) -> str:
        """Prompt for how to extract data from element."""
        if field_type == 'text':
            print("  How to extract text?")
            print("    1. get_text() - Extract all text content")
            print("    2. strip_html - Remove HTML tags")
            print("    3. inner_html - Keep HTML formatting")
            choice = input("  Choice (1-3) [default: 1]: ").strip() or '1'
            return {'1': 'get_text', '2': 'strip_html', '3': 'inner_html'}.get(choice, 'get_text')
        
        elif field_type == 'link':
            print("  Extract link from:")
            print("    1. href attribute")
            print("    2. text content (if URL is in text)")
            choice = input("  Choice (1-2) [default: 1]: ").strip() or '1'
            return 'href' if choice == '1' else 'text'
        
        elif field_type == 'image':
            return 'src'  # Always extract from src attribute
        
        return 'get_text'
    
    def _test_mapping(self, soup: BeautifulSoup, field_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Test the field mapping on the sample page."""
        results = {}
        
        for field_name, mapping in field_mapping['fields'].items():
            selector = mapping['selector']
            extraction_method = mapping['extraction_method']
            
            try:
                elements = soup.select(selector)
                if elements:
                    elem = elements[0]
                    
                    # Extract based on method
                    if extraction_method == 'get_text':
                        value = elem.get_text(strip=True)
                    elif extraction_method == 'strip_html':
                        value = elem.get_text(strip=True)
                    elif extraction_method == 'inner_html':
                        value = str(elem)
                    elif extraction_method == 'href':
                        value = elem.get('href', '')
                    elif extraction_method == 'src':
                        value = elem.get('src', '')
                    else:
                        value = elem.get_text(strip=True)
                    
                    results[field_name] = {
                        'success': True,
                        'value': value[:200],  # Limit length
                        'element_count': len(elements)
                    }
                else:
                    results[field_name] = {
                        'success': False,
                        'error': 'No elements found',
                        'element_count': 0
                    }
            except Exception as e:
                results[field_name] = {
                    'success': False,
                    'error': str(e),
                    'element_count': 0
                }
        
        return results
    
    def _display_test_results(self, results: Dict[str, Any]):
        """Display test results in a readable format."""
        print("\n" + "="*60)
        print("Test Results:")
        print("="*60)
        
        for field_name, result in results.items():
            if result['success']:
                print(f"\n✓ {field_name}")
                print(f"  Found: {result['element_count']} element(s)")
                print(f"  Value: {result['value']}")
            else:
                print(f"\n✗ {field_name}")
                print(f"  Error: {result['error']}")
    
    def _save_mapping(self, source_name: str, url: str, field_mapping: Dict[str, Any]) -> Path:
        """Save field mapping configuration to file."""
        config = {
            'source_name': source_name,
            'source_url': url,
            'created_at': datetime.now().isoformat(),
            'field_mappings': field_mapping['fields'],
            'notes': f"Created via interactive scraper setup tool on {datetime.now().strftime('%Y-%m-%d')}"
        }
        
        filename = f"{source_name.lower().replace(' ', '_')}_mapping.json"
        filepath = self.mappings_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        return filepath
    
    def _confirm(self, message: str) -> bool:
        """Prompt for yes/no confirmation."""
        response = input(f"\n{message} (y/n): ").strip().lower()
        return response in ['y', 'yes']
    
    def list_mappings(self):
        """List all saved field mappings."""
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║              Saved Scraper Field Mappings                      ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        
        mappings = list(self.mappings_dir.glob('*_mapping.json'))
        
        if not mappings:
            print("No saved mappings found.")
            print(f"Create one with: python3 {sys.argv[0]}")
            return
        
        for i, mapping_file in enumerate(mappings, 1):
            try:
                with open(mapping_file, 'r') as f:
                    config = json.load(f)
                
                print(f"{i}. {config['source_name']}")
                print(f"   URL: {config['source_url']}")
                print(f"   Fields mapped: {len(config['field_mappings'])}")
                print(f"   Created: {config.get('created_at', 'Unknown')}")
                print(f"   File: {mapping_file.name}")
                print()
            except Exception as e:
                print(f"{i}. {mapping_file.name}")
                print(f"   Error loading: {e}")
                print()
    
    def export_for_ci(self, source_name: str):
        """
        Export mapping configuration in a format suitable for CI/automation.
        
        Generates a compact JSON file that can be used in GitHub Actions.
        """
        input_mapping_file = self.mappings_dir / f"{source_name.lower()}_mapping.json"
        
        if not input_mapping_file.exists():
            print(f"❌ No mapping found for: {source_name}")
            print(f"   Looking for: {input_mapping_file}")
            return
        
        with open(input_mapping_file, 'r') as f:
            config = json.load(f)
        
        # Create CI-friendly format
        ci_config = {
            'version': '1.0',
            'source': {
                'name': config['source_name'],
                'url': config['source_url'],
                'type': 'html'
            },
            'selectors': {
                field: mapping['selector']
                for field, mapping in config['field_mappings'].items()
            },
            'extraction_methods': {
                field: mapping['extraction_method']
                for field, mapping in config['field_mappings'].items()
            }
        }
        
        output_file = self.mappings_dir / f"{source_name.lower()}_ci.json"
        with open(output_file, 'w') as f:
            json.dump(ci_config, f, indent=2)
        
        print(f"✓ CI configuration exported to: {output_file}")
        print(f"\nYou can use this in GitHub Actions:")
        print(f"  - Add to repository: config/scraper_mappings/{output_file.name}")
        print(f"  - Reference in workflow: scraper-mappings/{output_file.name}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Interactive Scraper Setup & Field Mapping Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Interactive mode (recommended for first-time setup)
  %(prog)s

  # Quick setup with URL
  %(prog)s --url https://example.com/events

  # List all saved mappings
  %(prog)s --list

  # Export mapping for CI/automation
  %(prog)s --export MySource

  # Test existing mapping
  %(prog)s --test MySource
        '''
    )
    
    parser.add_argument('--url', help='Event listing URL (skips URL prompt)')
    parser.add_argument('--list', action='store_true', help='List all saved mappings')
    parser.add_argument('--export', metavar='SOURCE', help='Export mapping for CI/automation')
    parser.add_argument('--test', metavar='SOURCE', help='Test existing mapping')
    
    args = parser.parse_args()
    
    # Get base path (repo root)
    base_path = Path(__file__).parent.parent.parent
    mapper = ScraperFieldMapper(base_path)
    
    if args.list:
        mapper.list_mappings()
    elif args.export:
        mapper.export_for_ci(args.export)
    elif args.test:
        print("Test functionality coming soon!")
        print(f"To test {args.test}, use the Custom Source Manager test command")
    else:
        # Interactive setup
        if not SCRAPING_AVAILABLE:
            print("❌ Scraping libraries not available")
            print("Install with: pip install requests beautifulsoup4 lxml")
            sys.exit(1)
        
        mapper.interactive_setup(url=args.url)


if __name__ == '__main__':
    main()
