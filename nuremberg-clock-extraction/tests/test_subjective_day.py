#!/usr/bin/env python3
"""
Tests for the Subjective Time (Nürnberger Uhr) module.

Tests cover:
- Sunrise/sunset calculations
- Subjective time calculations
- Day/night hour boundaries
- Edge cases (polar regions, equator)
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subjective_day import SubjectiveTime, get_subjective_day, get_sunrise_sunset


class TestSubjectiveTime(unittest.TestCase):
    """Test cases for SubjectiveTime class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Hof, Germany
        self.hof = SubjectiveTime(lat=50.3167, lon=11.9167)
        # Nuremberg, Germany
        self.nuremberg = SubjectiveTime(lat=49.4521, lon=11.0767)
        # Equator (for edge case testing)
        self.equator = SubjectiveTime(lat=0.0, lon=0.0)
    
    def test_sunrise_sunset_calculation(self):
        """Test that sunrise/sunset times are calculated correctly."""
        # Test winter day (January 24, 2026)
        winter_date = datetime(2026, 1, 24, 12, 0, 0)
        result = self.hof.get_sunrise_sunset(winter_date)
        
        self.assertFalse(result['polar'])
        self.assertIsNotNone(result['sunrise'])
        self.assertIsNotNone(result['sunset'])
        
        # In winter, day should be shorter than night
        self.assertLess(result['day_length_hours'], 12)
        self.assertGreater(result['night_length_hours'], 12)
        
        # Winter day hours should be shorter than 60 minutes
        self.assertLess(result['day_hour_length_minutes'], 60)
        # Winter night hours should be longer than 60 minutes
        self.assertGreater(result['night_hour_length_minutes'], 60)
    
    def test_summer_vs_winter(self):
        """Test that summer days are longer than winter days."""
        winter_date = datetime(2026, 1, 24, 12, 0, 0)
        summer_date = datetime(2026, 6, 21, 12, 0, 0)  # Summer solstice
        
        winter_result = self.hof.get_sunrise_sunset(winter_date)
        summer_result = self.hof.get_sunrise_sunset(summer_date)
        
        # Summer days should be longer
        self.assertGreater(
            summer_result['day_length_hours'], 
            winter_result['day_length_hours']
        )
        
        # Summer day hours should be longer than winter day hours
        self.assertGreater(
            summer_result['day_hour_length_minutes'],
            winter_result['day_hour_length_minutes']
        )
    
    def test_subjective_day_daytime(self):
        """Test subjective time calculation during daytime."""
        # Noon on a winter day
        noon = datetime(2026, 1, 24, 12, 0, 0)
        result = self.hof.get_subjective_day(noon)
        
        self.assertTrue(result['is_day'])
        self.assertEqual(result['period'], 'Tag')
        self.assertEqual(result['period_en'], 'day')
        
        # Hour should be between 1-12
        self.assertGreaterEqual(result['hour'], 1)
        self.assertLessEqual(result['hour'], 12)
        
        # Minute should be 0-59
        self.assertGreaterEqual(result['minute'], 0)
        self.assertLess(result['minute'], 60)
    
    def test_subjective_day_nighttime(self):
        """Test subjective time calculation during nighttime."""
        # Midnight
        midnight = datetime(2026, 1, 24, 0, 0, 0)
        result = self.hof.get_subjective_day(midnight)
        
        self.assertFalse(result['is_day'])
        self.assertEqual(result['period'], 'Nacht')
        self.assertEqual(result['period_en'], 'night')
        
        # Hour should be between 1-12
        self.assertGreaterEqual(result['hour'], 1)
        self.assertLessEqual(result['hour'], 12)
    
    def test_sunrise_boundary(self):
        """Test that time just after sunrise is 1st hour of day."""
        # Get sunrise for a specific date
        test_date = datetime(2026, 1, 24, 12, 0, 0)
        sun_data = self.hof.get_sunrise_sunset(test_date)
        sunrise = sun_data['sunrise']
        
        # 5 minutes after sunrise
        after_sunrise = sunrise + timedelta(minutes=5)
        result = self.hof.get_subjective_day(after_sunrise)
        
        self.assertTrue(result['is_day'])
        self.assertEqual(result['hour'], 1)
    
    def test_sunset_boundary(self):
        """Test that time just after sunset is 1st hour of night."""
        # Get sunset for a specific date
        test_date = datetime(2026, 1, 24, 12, 0, 0)
        sun_data = self.hof.get_sunrise_sunset(test_date)
        sunset = sun_data['sunset']
        
        # 5 minutes after sunset
        after_sunset = sunset + timedelta(minutes=5)
        result = self.hof.get_subjective_day(after_sunset)
        
        self.assertFalse(result['is_day'])
        self.assertEqual(result['hour'], 1)
    
    def test_full_day_hours(self):
        """Test get_full_day_hours returns 12 day and 12 night hours."""
        test_date = datetime(2026, 1, 24)
        result = self.hof.get_full_day_hours(test_date)
        
        self.assertFalse(result['polar'])
        self.assertEqual(len(result['day_hours']), 12)
        self.assertEqual(len(result['night_hours']), 12)
        
        # Check hour numbering
        for i, hour in enumerate(result['day_hours']):
            self.assertEqual(hour['hour'], i + 1)
        
        for i, hour in enumerate(result['night_hours']):
            self.assertEqual(hour['hour'], i + 1)
    
    def test_equator_equal_hours(self):
        """Test that at equator, day and night hours are roughly equal year-round."""
        # At equinox, should have roughly equal day/night
        equinox = datetime(2026, 3, 20, 12, 0, 0)
        result = self.equator.get_sunrise_sunset(equinox)
        
        # At equator on equinox, day and night should be roughly 12 hours each
        self.assertAlmostEqual(result['day_length_hours'], 12, delta=0.5)
        self.assertAlmostEqual(result['night_length_hours'], 12, delta=0.5)
    
    def test_convenience_functions(self):
        """Test the convenience functions work correctly."""
        result = get_subjective_day(50.3167, 11.9167)
        
        self.assertIn('is_day', result)
        self.assertIn('hour', result)
        self.assertIn('minute', result)
        self.assertIn('display', result)
        
        sun_result = get_sunrise_sunset(50.3167, 11.9167)
        
        self.assertIn('sunrise', sun_result)
        self.assertIn('sunset', sun_result)
    
    def test_display_strings(self):
        """Test that display strings are formatted correctly."""
        result = self.hof.get_subjective_day()
        
        self.assertIn('display', result)
        self.assertIn('display_de', result)
        self.assertIn('display_en', result)
        
        # German format: "X. Stunde des Tages/Nachts"
        self.assertIn('Stunde', result['display'])
        
        # English format should contain ordinal
        period = 'day' if result['is_day'] else 'night'
        self.assertIn(period, result['display_en'])
    
    def test_location_in_result(self):
        """Test that location is included in result."""
        result = self.hof.get_subjective_day()
        
        self.assertIn('location', result)
        self.assertEqual(result['location']['lat'], 50.3167)
        self.assertEqual(result['location']['lon'], 11.9167)
    
    def test_different_locations_different_times(self):
        """Test that different locations have different sunrise/sunset times."""
        test_date = datetime(2026, 1, 24, 12, 0, 0)
        
        hof_result = self.hof.get_sunrise_sunset(test_date)
        nuremberg_result = self.nuremberg.get_sunrise_sunset(test_date)
        
        # Different latitudes should have different day lengths
        # Hof is further north, so should have shorter winter days
        self.assertLess(
            hof_result['day_length_hours'],
            nuremberg_result['day_length_hours']
        )


class TestOrdinalSuffix(unittest.TestCase):
    """Test ordinal suffix generation."""
    
    def test_ordinal_suffixes(self):
        """Test that ordinal suffixes are correct."""
        uhr = SubjectiveTime(50.0, 10.0)
        
        self.assertEqual(uhr._get_ordinal_suffix(1), 'st')
        self.assertEqual(uhr._get_ordinal_suffix(2), 'nd')
        self.assertEqual(uhr._get_ordinal_suffix(3), 'rd')
        self.assertEqual(uhr._get_ordinal_suffix(4), 'th')
        self.assertEqual(uhr._get_ordinal_suffix(11), 'th')
        self.assertEqual(uhr._get_ordinal_suffix(12), 'th')


class TestInputValidation(unittest.TestCase):
    """Test input validation for coordinates."""
    
    def test_valid_coordinates(self):
        """Test that valid coordinates are accepted."""
        # Valid latitude and longitude
        uhr = SubjectiveTime(lat=50.0, lon=10.0)
        self.assertEqual(uhr.lat, 50.0)
        self.assertEqual(uhr.lon, 10.0)
        
        # Edge cases - poles and international date line
        uhr_north_pole = SubjectiveTime(lat=90.0, lon=0.0)
        self.assertEqual(uhr_north_pole.lat, 90.0)
        
        uhr_south_pole = SubjectiveTime(lat=-90.0, lon=0.0)
        self.assertEqual(uhr_south_pole.lat, -90.0)
        
        uhr_date_line = SubjectiveTime(lat=0.0, lon=180.0)
        self.assertEqual(uhr_date_line.lon, 180.0)
        
        uhr_date_line_west = SubjectiveTime(lat=0.0, lon=-180.0)
        self.assertEqual(uhr_date_line_west.lon, -180.0)
    
    def test_invalid_latitude(self):
        """Test that invalid latitude raises ValueError."""
        with self.assertRaises(ValueError):
            SubjectiveTime(lat=91.0, lon=0.0)
        
        with self.assertRaises(ValueError):
            SubjectiveTime(lat=-91.0, lon=0.0)
    
    def test_invalid_longitude(self):
        """Test that invalid longitude raises ValueError."""
        with self.assertRaises(ValueError):
            SubjectiveTime(lat=0.0, lon=181.0)
        
        with self.assertRaises(ValueError):
            SubjectiveTime(lat=0.0, lon=-181.0)


class TestDSTCalculation(unittest.TestCase):
    """Test DST calculation for Central European Time."""
    
    def test_winter_time(self):
        """Test that winter dates get CET (UTC+1)."""
        uhr = SubjectiveTime(lat=50.0, lon=10.0)
        
        # January should be CET
        january = datetime(2026, 1, 15, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(january), 1)
        
        # December should be CET
        december = datetime(2026, 12, 15, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(december), 1)
    
    def test_summer_time(self):
        """Test that summer dates get CEST (UTC+2)."""
        uhr = SubjectiveTime(lat=50.0, lon=10.0)
        
        # July should be CEST
        july = datetime(2026, 7, 15, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(july), 2)
        
        # June should be CEST
        june = datetime(2026, 6, 15, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(june), 2)
    
    def test_dst_transitions(self):
        """Test DST transition dates."""
        uhr = SubjectiveTime(lat=50.0, lon=10.0)
        
        # 2026: DST starts March 29, ends October 25
        # Before DST starts (March 28)
        before_dst = datetime(2026, 3, 28, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(before_dst), 1)
        
        # After DST starts (March 30)
        after_dst_start = datetime(2026, 3, 30, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(after_dst_start), 2)
        
        # Before DST ends (October 24)
        before_dst_end = datetime(2026, 10, 24, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(before_dst_end), 2)
        
        # After DST ends (October 26)
        after_dst_end = datetime(2026, 10, 26, 12, 0, 0)
        self.assertEqual(uhr._get_cet_offset(after_dst_end), 1)


if __name__ == '__main__':
    print("=" * 60)
    print("Subjective Time (Nürnberger Uhr) - Test Suite")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2)
