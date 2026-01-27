#!/usr/bin/env python3
"""
Tests for RSS feed generation
"""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.rss_generator import create_rss_feed


class TestRSSFeedGeneration(unittest.TestCase):
    """Test RSS feed generation functionality"""
    
    def test_create_rss_feed_basic(self):
        """Test basic RSS feed creation"""
        events = [
            {
                'id': 'test_1',
                'title': 'Test Event',
                'description': 'Test Description',
                'start_time': '2026-01-27T20:00:00',
                'location': {'name': 'Test Location', 'address': '123 Test St'},
                'category': 'test',
                'url': 'https://example.com'
            }
        ]
        
        rss_xml = create_rss_feed(
            title='Test Feed',
            description='Test Feed Description',
            events=events,
            region_id='test',
            base_url='https://example.com'
        )
        
        # Should return non-empty string
        self.assertIsInstance(rss_xml, str)
        self.assertGreater(len(rss_xml), 0)
        
        # Should be valid XML
        root = ET.fromstring(rss_xml)
        self.assertEqual(root.tag, 'rss')
        self.assertEqual(root.get('version'), '2.0')
    
    def test_rss_feed_structure(self):
        """Test RSS feed has correct structure"""
        events = [
            {
                'id': 'test_1',
                'title': 'Test Event',
                'description': 'Test Description',
                'start_time': '2026-01-27T20:00:00',
                'location': {'name': 'Test Location'},
                'category': 'test'
            }
        ]
        
        rss_xml = create_rss_feed(
            title='Test Feed',
            description='Test Description',
            events=events,
            region_id='test',
            base_url='https://example.com'
        )
        
        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        
        # Check required channel elements
        self.assertIsNotNone(channel)
        self.assertIsNotNone(channel.find('title'))
        self.assertIsNotNone(channel.find('link'))
        self.assertIsNotNone(channel.find('description'))
        self.assertIsNotNone(channel.find('language'))
        
        # Check items
        items = channel.findall('item')
        self.assertEqual(len(items), 1)
        
        # Check first item structure
        item = items[0]
        self.assertIsNotNone(item.find('title'))
        self.assertIsNotNone(item.find('guid'))
        self.assertIsNotNone(item.find('description'))
    
    def test_rss_feed_empty_events(self):
        """Test RSS feed with no events"""
        rss_xml = create_rss_feed(
            title='Empty Feed',
            description='Empty Description',
            events=[],
            region_id='test',
            base_url='https://example.com'
        )
        
        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        items = channel.findall('item')
        
        # Should have no items but still be valid
        self.assertEqual(len(items), 0)
    
    def test_rss_feed_multiple_events(self):
        """Test RSS feed with multiple events"""
        events = [
            {
                'id': f'test_{i}',
                'title': f'Test Event {i}',
                'description': f'Description {i}',
                'start_time': '2026-01-27T20:00:00',
                'category': 'test'
            }
            for i in range(5)
        ]
        
        rss_xml = create_rss_feed(
            title='Multi Event Feed',
            description='Multiple Events',
            events=events,
            region_id='test',
            base_url='https://example.com'
        )
        
        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        items = channel.findall('item')
        
        # Should have all 5 events
        self.assertEqual(len(items), 5)
    
    def test_rss_feed_with_category(self):
        """Test RSS feed includes category"""
        events = [
            {
                'id': 'test_1',
                'title': 'Music Event',
                'start_time': '2026-01-27T20:00:00',
                'category': 'music'
            }
        ]
        
        rss_xml = create_rss_feed(
            title='Test Feed',
            description='Test',
            events=events,
            region_id='test',
            base_url='https://example.com'
        )
        
        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        item = channel.find('item')
        category = item.find('category')
        
        # Should have category element
        self.assertIsNotNone(category)
        self.assertEqual(category.text, 'music')
    
    def test_feeds_directory_exists(self):
        """Test that feeds directory exists after generation"""
        base_path = Path(__file__).parent.parent
        feeds_dir = base_path / 'assets' / 'feeds'
        
        # Directory should exist
        self.assertTrue(feeds_dir.exists())
        self.assertTrue(feeds_dir.is_dir())
    
    def test_generated_feeds_are_valid(self):
        """Test that generated feed files are valid XML"""
        base_path = Path(__file__).parent.parent
        feeds_dir = base_path / 'assets' / 'feeds'
        
        feed_files = list(feeds_dir.glob('*-til-sunrise.xml'))
        
        # Should have at least one feed
        self.assertGreater(len(feed_files), 0)
        
        # Each feed should be valid XML
        for feed_file in feed_files:
            with open(feed_file, 'r') as f:
                content = f.read()
            
            # Should parse without error
            root = ET.fromstring(content)
            self.assertEqual(root.tag, 'rss')
            self.assertEqual(root.get('version'), '2.0')
    
    def test_public_feeds_directory_exists_after_generation(self):
        """Test that feeds are copied to public/assets/feeds/ after site generation"""
        base_path = Path(__file__).parent.parent
        public_feeds_dir = base_path / 'public' / 'assets' / 'feeds'
        source_feeds_dir = base_path / 'assets' / 'feeds'
        
        # If public feeds directory doesn't exist, skip this test
        # (only valid after running 'python3 src/event_manager.py generate')
        if not public_feeds_dir.exists():
            self.skipTest("public/assets/feeds/ not yet created (run 'generate' command first)")
        
        # Directory should exist and contain feeds
        self.assertTrue(public_feeds_dir.is_dir())
        
        # Get source and public feed files
        source_feeds = set(f.name for f in source_feeds_dir.glob('*.xml'))
        public_feeds = set(f.name for f in public_feeds_dir.glob('*.xml'))
        
        # All source feeds should be in public
        for feed_name in source_feeds:
            self.assertIn(feed_name, public_feeds, 
                f"Feed {feed_name} not copied to public/assets/feeds/")
        
        # Each public feed should be valid XML
        for feed_file in public_feeds_dir.glob('*.xml'):
            with open(feed_file, 'r') as f:
                content = f.read()
            root = ET.fromstring(content)
            self.assertEqual(root.tag, 'rss')


if __name__ == '__main__':
    # Run with verbose output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRSSFeedGeneration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
