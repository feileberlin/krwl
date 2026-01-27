#!/usr/bin/env python3
"""Tests for custom source scrapers."""

import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.smart_scraper.sources.custom.date_utils import (
    extract_date_from_text,
    generate_stable_event_id
)
from modules.smart_scraper.base import SourceOptions


class TestDateUtils(unittest.TestCase):
    """Test shared date utilities."""
    
    def test_extract_date_dmy_format(self):
        """Test DD.MM.YYYY format extraction."""
        text = "Event on 15.02.2026 at 20:00"
        result = extract_date_from_text(text)
        self.assertIn('2026-02-15', result)
    
    def test_extract_date_short_year(self):
        """Test DD.MM.YY format with dynamic year handling."""
        text = "Event on 15.02.26"
        result = extract_date_from_text(text)
        # Should be in 2026 (current century + year)
        self.assertIn('2026-02-15', result)
    
    def test_extract_date_ymd_format(self):
        """Test YYYY-MM-DD format extraction."""
        text = "Event on 2026-02-15"
        result = extract_date_from_text(text)
        self.assertIn('2026-02-15', result)
    
    def test_extract_date_with_ab_prefix(self):
        """Test 'ab DD.MM.YYYY' format."""
        text = "ab 15.02.2026"
        result = extract_date_from_text(text)
        self.assertIn('2026-02-15', result)
    
    def test_extract_date_invalid_date_skipped(self):
        """Test that invalid dates are skipped."""
        text = "Event on 32.13.2026"  # Invalid day and month
        result = extract_date_from_text(text)
        # Should return default future date
        self.assertIsInstance(result, str)
    
    def test_extract_date_default_hour(self):
        """Test custom default hour."""
        text = "Event on 15.02.2026"
        result = extract_date_from_text(text, default_hour=10)
        self.assertIn('T10:00:00', result)
    
    def test_generate_stable_event_id(self):
        """Test stable ID generation."""
        id1 = generate_stable_event_id('test', 'title', '2026-02-15')
        id2 = generate_stable_event_id('test', 'title', '2026-02-15')
        # Same inputs should produce same ID
        self.assertEqual(id1, id2)
        self.assertTrue(id1.startswith('test_'))
    
    def test_generate_stable_event_id_different_inputs(self):
        """Test that different inputs produce different IDs."""
        id1 = generate_stable_event_id('test', 'title1', '2026-02-15')
        id2 = generate_stable_event_id('test', 'title2', '2026-02-15')
        self.assertNotEqual(id1, id2)


class TestCustomScraperIntegration(unittest.TestCase):
    """Integration tests for custom scrapers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_path = Path(__file__).parent.parent
    
    def test_freiheitshalle_import(self):
        """Test that FreiheitshalleSource can be imported."""
        try:
            from modules.smart_scraper.sources.custom import FreiheitshalleSource
            self.assertIsNotNone(FreiheitshalleSource)
        except ImportError as e:
            self.fail(f"Failed to import FreiheitshalleSource: {e}")
    
    def test_vhs_import(self):
        """Test that VHSSource can be imported."""
        try:
            from modules.smart_scraper.sources.custom import VHSSource
            self.assertIsNotNone(VHSSource)
        except ImportError as e:
            self.fail(f"Failed to import VHSSource: {e}")
    
    def test_hof_stadt_import(self):
        """Test that HofStadtSource can be imported."""
        try:
            from modules.smart_scraper.sources.custom import HofStadtSource
            self.assertIsNotNone(HofStadtSource)
        except ImportError as e:
            self.fail(f"Failed to import HofStadtSource: {e}")
    
    def test_scraper_initialization(self):
        """Test that custom scrapers can be initialized."""
        from modules.smart_scraper.sources.custom import FreiheitshalleSource
        
        source_config = {
            'name': 'Test Freiheitshalle',
            'url': 'https://example.com',
            'type': 'html'
        }
        options = SourceOptions()
        
        scraper = FreiheitshalleSource(source_config, options)
        self.assertEqual(scraper.name, 'Test Freiheitshalle')
        self.assertEqual(scraper.url, 'https://example.com')
    
    def test_scraper_user_agent(self):
        """Test that scrapers have complete User-Agent strings."""
        from modules.smart_scraper.sources.custom import FreiheitshalleSource
        
        source_config = {
            'name': 'Test',
            'url': 'https://example.com',
            'type': 'html'
        }
        options = SourceOptions()
        
        scraper = FreiheitshalleSource(source_config, options)
        if scraper.available:
            user_agent = scraper.session.headers.get('User-Agent', '')
            # Check for complete User-Agent with Chrome version
            self.assertIn('Chrome/', user_agent)
            self.assertIn('Safari/', user_agent)
            self.assertIn('AppleWebKit/', user_agent)


class TestCustomScraperParsing(unittest.TestCase):
    """Test HTML parsing logic in custom scrapers."""
    
    def test_date_extraction_validation(self):
        """Test that date extraction validates day/month ranges."""
        # Valid date
        valid_result = extract_date_from_text("15.06.2026")
        self.assertIn('2026-06-15', valid_result)
        
        # Invalid dates should be skipped (returns future default)
        invalid_texts = [
            "32.01.2026",  # Day > 31
            "15.13.2026",  # Month > 12
            "00.06.2026",  # Day = 0
            "15.00.2026",  # Month = 0
        ]
        for text in invalid_texts:
            result = extract_date_from_text(text)
            # Should return default future date, not the invalid date
            self.assertNotIn('2026-01-32', result)
            self.assertNotIn('2026-13-15', result)


class TestVHSLocationExtraction(unittest.TestCase):
    """Test VHS scraper location extraction from HTML."""
    
    def setUp(self):
        """Set up VHS scraper for testing."""
        try:
            from modules.smart_scraper.sources.custom import VHSSource
            from bs4 import BeautifulSoup
            self.VHSSource = VHSSource
            self.BeautifulSoup = BeautifulSoup
            self.available = True
        except ImportError:
            self.available = False
    
    def _create_scraper(self):
        """Create a VHS scraper instance for testing."""
        source_config = {
            'name': 'Test VHS',
            'url': 'https://example.com',
            'type': 'html'
        }
        options = SourceOptions()
        return self.VHSSource(source_config, options)
    
    def test_extract_location_from_course_places_list(self):
        """Test extraction from course-places-list element."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li class="list-group-item course-places-list">
                <div class="row">
                    <div class="col">
                        <strong>Ort:</strong>
                        VHS Bildungszentrum Hof
                    </div>
                </div>
            </li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertIn('VHS Bildungszentrum Hof', location)
    
    def test_extract_location_from_li_element(self):
        """Test extraction from generic li element with Ort: label."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li>Ort: Stadtbibliothek Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Stadtbibliothek Hof')
    
    def test_extract_location_from_strong_element(self):
        """Test extraction from <strong>Ort:</strong> pattern."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <div><strong>Ort:</strong> Kulturzentrum Hof</div>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Kulturzentrum Hof')
    
    def test_extract_location_returns_none_when_missing(self):
        """Test that None is returned when no location is found."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <p>Some description without location</p>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNone(location)
    
    def test_parse_course_uses_extracted_location(self):
        """Test that _parse_course uses extracted location name."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Python Programmierung 15.02.2026</h3>
            <p>Learn Python basics</p>
            <li class="course-places-list">Ort: Mehrgenerationenhaus Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        event = scraper._parse_course(container)
        
        self.assertIsNotNone(event)
        self.assertEqual(event['location']['name'], 'Mehrgenerationenhaus Hof')
        # Should still have default coordinates
        self.assertEqual(event['location']['lat'], 50.3167)
        self.assertEqual(event['location']['lon'], 11.9167)
    
    def test_parse_course_fallback_to_default_location(self):
        """Test that _parse_course uses default location when none found."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Excel Kurs 20.03.2026</h3>
            <p>Learn Excel basics</p>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        event = scraper._parse_course(container)
        
        self.assertIsNotNone(event)
        self.assertEqual(event['location']['name'], 'VHS Hofer Land')
    
    def test_extract_location_case_insensitive_uppercase(self):
        """Test extraction handles uppercase 'ORT:' label."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li>ORT: Rathaus Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Rathaus Hof')
    
    def test_extract_location_case_insensitive_lowercase(self):
        """Test extraction handles lowercase 'ort:' label."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li>ort: Museum Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Museum Hof')
    
    def test_extract_location_with_space_before_colon(self):
        """Test extraction handles 'Ort :' with space before colon."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li>Ort : Sporthalle Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Sporthalle Hof')
    
    def test_extract_location_empty_after_prefix(self):
        """Test that empty location after 'Ort:' returns None."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <li>Ort:    </li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNone(location)
    
    def test_extract_location_returns_first_match(self):
        """Test that extraction returns the first location found."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <div><strong>Ort:</strong> First Location</div>
            <li>Ort: Second Location</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        # Should return first match (from strong element, which is checked first)
        self.assertEqual(location, 'First Location')
    
    def test_extract_location_strong_pattern_priority(self):
        """Test that <strong>Ort:</strong> pattern has higher priority than broad search."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <p>Some text with Ort: Incorrect Location in description</p>
            <div><strong>Ort:</strong> Correct Location</div>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        # Strong pattern is checked first, should return correct location
        self.assertEqual(location, 'Correct Location')
    
    def test_extract_location_ignores_similar_words(self):
        """Test that words like 'ortschaft:' are not matched as 'Ort:'."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course</h3>
            <div><strong>Ortschaft:</strong> Should Not Match</div>
            <li>Ort: Actual Location</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        # "Ortschaft:" should not match, only "Ort:" should
        self.assertEqual(location, 'Actual Location')


class TestVHSConcatenatedTitleParsing(unittest.TestCase):
    """Test VHS scraper concatenated title parsing."""
    
    def setUp(self):
        """Set up VHS scraper for testing."""
        try:
            from modules.smart_scraper.sources.custom import VHSSource
            from bs4 import BeautifulSoup
            self.VHSSource = VHSSource
            self.BeautifulSoup = BeautifulSoup
            self.available = True
        except ImportError:
            self.available = False
    
    def _create_scraper(self):
        """Create a VHS scraper instance for testing."""
        source_config = {
            'name': 'Test VHS',
            'url': 'https://example.com',
            'type': 'html'
        }
        options = SourceOptions()
        return self.VHSSource(source_config, options)
    
    def test_parse_concatenated_title_with_location(self):
        """Test parsing concatenated title with embedded location."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        # Test case from the issue: title with date and location concatenated
        raw_title = "Interkultureller ChorChorprobenDo. 08.01.2026 19:00Ludwigstraße 7, 95028 Hof"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Interkultureller ChorChorproben")
        self.assertEqual(date_string, "08.01.2026")
        self.assertEqual(location, "Ludwigstraße 7, 95028 Hof")
    
    def test_parse_concatenated_title_schwarzenbach(self):
        """Test parsing with Schwarzenbach location."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "Training für den Körper 1Fr. 16.01.2026 16:30Philipp-Wolfrum-Haus, Marktplatz 17, 95131 Schwarzenbach a.Wald"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Training für den Körper 1")
        self.assertEqual(date_string, "16.01.2026")
        self.assertEqual(location, "Philipp-Wolfrum-Haus, Marktplatz 17, 95131 Schwarzenbach a.Wald")
    
    def test_parse_concatenated_title_online_location(self):
        """Test parsing with Online as location."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "KI-Selfies: Künstliche Intelligenz als FotografMi. 04.02.2026 17:00Online"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "KI-Selfies: Künstliche Intelligenz als Fotograf")
        self.assertEqual(date_string, "04.02.2026")
        self.assertEqual(location, "Online")
    
    def test_parse_concatenated_title_vhs_naila(self):
        """Test parsing with VHS Naila location."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "Kommunikationstraining für ZuwanderinnenWorkshopMo. 19.01.2026 10:00VHS Naila"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Kommunikationstraining für ZuwanderinnenWorkshop")
        self.assertEqual(date_string, "19.01.2026")
        self.assertEqual(location, "VHS Naila")
    
    def test_parse_concatenated_title_no_time(self):
        """Test parsing with date but no time."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "Test KursDi. 15.02.2026Test Location"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Test Kurs")
        self.assertEqual(date_string, "15.02.2026")
        self.assertEqual(location, "Test Location")
    
    def test_parse_concatenated_title_no_date_pattern(self):
        """Test parsing with no date pattern returns original title."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "Simple Course Title Without Date"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Simple Course Title Without Date")
        self.assertIsNone(date_string)
        self.assertIsNone(location)
    
    def test_parse_concatenated_title_short_year(self):
        """Test parsing with short year format (YY)."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        raw_title = "Excel KursMi. 20.03.26 14:00Büro Zentrum"
        
        clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
        
        self.assertEqual(clean_title, "Excel Kurs")
        self.assertEqual(date_string, "20.03.26")
        self.assertEqual(location, "Büro Zentrum")
    
    def test_parse_concatenated_title_all_weekdays(self):
        """Test parsing works for all German weekday abbreviations."""
        if not self.available:
            self.skipTest("VHSSource not available")
        
        scraper = self._create_scraper()
        
        weekdays = ['Mo.', 'Di.', 'Mi.', 'Do.', 'Fr.', 'Sa.', 'So.']
        for weekday in weekdays:
            raw_title = f"Test Kurs{weekday} 15.02.2026 10:00Test Location"
            
            clean_title, date_string, location = scraper._parse_concatenated_title(raw_title)
            
            self.assertEqual(clean_title, "Test Kurs", f"Failed for weekday {weekday}")
            self.assertEqual(date_string, "15.02.2026", f"Failed for weekday {weekday}")
            self.assertEqual(location, "Test Location", f"Failed for weekday {weekday}")
    
    def test_parse_course_uses_title_location_fallback(self):
        """Test that _parse_course uses location from title when not found in HTML."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Python KursFr. 15.02.2026 18:00Schulungszentrum Hof</h3>
            <p>Learn Python basics</p>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        event = scraper._parse_course(container)
        
        self.assertIsNotNone(event)
        # Title should be cleaned
        self.assertEqual(event['title'], 'Python Kurs')
        # Location should be extracted from concatenated title
        self.assertEqual(event['location']['name'], 'Schulungszentrum Hof')
    
    def test_ort_raum_header_extraction(self):
        """Test extraction from 'Ort / Raum:' tabular header format."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        html = '''
        <div class="course-item">
            <h3>Test Course 15.02.2026</h3>
            <li>Ort / Raum: Raum 201, VHS Hof</li>
        </div>
        '''
        soup = self.BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='course-item')
        
        scraper = self._create_scraper()
        location = scraper._extract_location(container)
        
        self.assertIsNotNone(location)
        self.assertEqual(location, 'Raum 201, VHS Hof')
    
    def test_ort_raum_header_variations(self):
        """Test variations of 'Ort / Raum' header."""
        if not self.available:
            self.skipTest("BeautifulSoup not available")
        
        scraper = self._create_scraper()
        
        # Test various patterns
        test_cases = [
            ('Ort / Raum: Raum 101', 'Raum 101'),
            ('Ort / Raum:Hauptgebäude', 'Hauptgebäude'),
            ('ort / raum: Keller', 'Keller'),
            ('ORT / RAUM: Seminarraum', 'Seminarraum'),
            ('Ort/Raum: Saal A', 'Saal A'),
        ]
        
        for text, expected in test_cases:
            result = scraper._extract_location_from_text(text)
            self.assertEqual(result, expected, f"Failed for input: {text}")


def main():
    """Run tests."""
    # Run with verbose output
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    main()
