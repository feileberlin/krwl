"""CLI commands for scraper management.

Provides command-line interface for:
- Adding new sources
- Editing sources
- Testing sources
- Listing sources
- Fixing broken scrapers
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def list_sources(config_path: str = 'config.json'):
    """List all configured sources."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        sources = config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("⚠ No sources configured.")
            return
        
        print("\n=== CONFIGURED SOURCES ===\n")
        
        for i, source in enumerate(sources, 1):
            status = "✓ ENABLED" if source.get('enabled', False) else "⊘ DISABLED"
            print(f"{i}. {source.get('name', 'Unnamed')} [{status}]")
            print(f"   Type: {source.get('type', 'unknown')}")
            print(f"   URL: {source.get('url', 'N/A')}")
            if source.get('notes'):
                print(f"   Notes: {source.get('notes')}")
            print()
            
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def add_source(name: str, url: str, source_type: str = 'html',
               enabled: bool = True, config_path: str = 'config.json',
               **options):
    """Add a new scraping source.
    
    Args:
        name: Source name
        url: Source URL
        source_type: Source type (rss, html, api, etc.)
        enabled: Enable source
        config_path: Path to config file
        **options: Additional source options
    """
    try:
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create source
        source = {
            'name': name,
            'type': source_type,
            'url': url,
            'enabled': enabled
        }
        
        # Add options
        if options:
            source['options'] = {k: v for k, v in options.items() if v is not None}
        
        # Add to config
        if 'scraping' not in config:
            config['scraping'] = {}
        if 'sources' not in config['scraping']:
            config['scraping']['sources'] = []
        
        config['scraping']['sources'].append(source)
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Added source: {name}")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def test_source(name: str, config_path: str = 'config.json',
                base_path: str = '.'):
    """Test a scraping source.
    
    Args:
        name: Source name to test
        config_path: Path to config file
        base_path: Base path for data files
    """
    try:
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Find source
        sources = config.get('scraping', {}).get('sources', [])
        source = None
        for s in sources:
            if s.get('name') == name:
                source = s
                break
        
        if not source:
            print(f"✗ Source not found: {name}", file=sys.stderr)
            sys.exit(1)
        
        # Test scraper
        print(f"🔍 Testing: {source['name']}")
        print(f"Type: {source['type']}")
        print(f"URL: {source['url']}")
        
        # Import here to avoid dependency issues
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from modules.scraper import EventScraper
        
        scraper = EventScraper(config, base_path)
        events = scraper.scrape_source(source)
        
        if events:
            print(f"\n✓ Success! Found {len(events)} event(s)")
            if events:
                print("\nFirst event:")
                print(f"  Title: {events[0].get('title', 'N/A')}")
                print(f"  Date: {events[0].get('start_time', 'N/A')}")
                print(f"  Location: {events[0].get('location', {}).get('name', 'N/A')}")
        else:
            print("\n⚠ No events found")
            
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def enable_source(name: str, config_path: str = 'config.json'):
    """Enable a source."""
    _toggle_source(name, True, config_path)


def disable_source(name: str, config_path: str = 'config.json'):
    """Disable a source."""
    _toggle_source(name, False, config_path)


def _toggle_source(name: str, enabled: bool, config_path: str):
    """Toggle source enabled/disabled."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        sources = config.get('scraping', {}).get('sources', [])
        found = False
        
        for source in sources:
            if source.get('name') == name:
                source['enabled'] = enabled
                found = True
                break
        
        if not found:
            print(f"✗ Source not found: {name}", file=sys.stderr)
            sys.exit(1)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        status = "enabled" if enabled else "disabled"
        print(f"✓ Source '{name}' {status}!")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def test_all_sources(config_path: str = 'config.json',
                     base_path: str = '.'):
    """Test all configured sources."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        sources = config.get('scraping', {}).get('sources', [])
        
        if not sources:
            print("⚠ No sources configured.")
            return
        
        print("Testing all sources...\n")
        
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from modules.scraper import EventScraper
        scraper = EventScraper(config, base_path)
        
        working = []
        broken = []
        
        for source in sources:
            if not source.get('enabled', False):
                continue
            
            name = source.get('name', 'Unnamed')
            print(f"Testing {name}...", end=' ')
            
            try:
                events = scraper.scrape_source(source)
                if events is None or len(events) == 0:
                    print("⚠ No events")
                    broken.append((name, "No events found"))
                else:
                    print(f"✓ OK ({len(events)} events)")
                    working.append(name)
            except Exception as e:
                print(f"✗ FAILED")
                broken.append((name, str(e)))
        
        print(f"\n{'='*60}")
        print(f"Results: {len(working)} working, {len(broken)} broken")
        
        if broken:
            print(f"\n⚠ Broken sources:")
            for name, error in broken:
                print(f"  - {name}: {error}")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scraper management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all sources
  python3 -m modules.scraper_cli list

  # Add new source
  python3 -m modules.scraper_cli add "City Events" https://example.com/events --type html

  # Test source
  python3 -m modules.scraper_cli test "City Events"

  # Test all sources
  python3 -m modules.scraper_cli test-all

  # Enable/disable source
  python3 -m modules.scraper_cli enable "City Events"
  python3 -m modules.scraper_cli disable "City Events"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all sources')
    list_parser.add_argument('--config', default='config.json',
                            help='Config file path')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new source')
    add_parser.add_argument('name', help='Source name')
    add_parser.add_argument('url', help='Source URL')
    add_parser.add_argument('--type', dest='source_type', default='html',
                           choices=['rss', 'html', 'api', 'atom', 'facebook',
                                   'instagram', 'tiktok', 'x', 'telegram'],
                           help='Source type')
    add_parser.add_argument('--disabled', action='store_false', dest='enabled',
                           help='Add as disabled')
    add_parser.add_argument('--config', default='config.json',
                           help='Config file path')
    add_parser.add_argument('--filter-ads', action='store_true',
                           help='Enable ad filtering')
    add_parser.add_argument('--exclude-keywords', help='Exclude keywords (comma-separated)')
    add_parser.add_argument('--max-days-ahead', type=int, help='Max days ahead')
    add_parser.add_argument('--ai-provider', help='AI provider')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a source')
    test_parser.add_argument('name', help='Source name')
    test_parser.add_argument('--config', default='config.json',
                            help='Config file path')
    test_parser.add_argument('--base-path', default='.',
                            help='Base path for data files')
    
    # Test all command
    test_all_parser = subparsers.add_parser('test-all', help='Test all sources')
    test_all_parser.add_argument('--config', default='config.json',
                                help='Config file path')
    test_all_parser.add_argument('--base-path', default='.',
                                help='Base path for data files')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a source')
    enable_parser.add_argument('name', help='Source name')
    enable_parser.add_argument('--config', default='config.json',
                              help='Config file path')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a source')
    disable_parser.add_argument('name', help='Source name')
    disable_parser.add_argument('--config', default='config.json',
                               help='Config file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'list':
        list_sources(args.config)
    elif args.command == 'add':
        options = {}
        if args.filter_ads:
            options['filter_ads'] = True
        if args.exclude_keywords:
            options['exclude_keywords'] = [k.strip() for k in args.exclude_keywords.split(',')]
        if args.max_days_ahead:
            options['max_days_ahead'] = args.max_days_ahead
        if args.ai_provider:
            options['ai_provider'] = args.ai_provider
        
        add_source(args.name, args.url, args.source_type, args.enabled,
                  args.config, **options)
    elif args.command == 'test':
        test_source(args.name, args.config, args.base_path)
    elif args.command == 'test-all':
        test_all_sources(args.config, args.base_path)
    elif args.command == 'enable':
        enable_source(args.name, args.config)
    elif args.command == 'disable':
        disable_source(args.name, args.config)


if __name__ == '__main__':
    main()
