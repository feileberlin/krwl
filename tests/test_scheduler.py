#!/usr/bin/env python3
"""
Tests for the scheduler module
"""

import sys
import unittest
import json
import tempfile
from pathlib import Path
from src.modules.scheduler import ScheduleConfig


class TestSchedulerModule(unittest.TestCase):
    """Test the scheduler configuration module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary config file
        self.test_config = {
            "app": {
                "name": "Test App"
            },
            "scraping": {
                "schedule": {
                    "timezone": "America/New_York",
                    "times": ["06:00", "18:00"]
                },
                "sources": []
            }
        }
        
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json',
            delete=False
        )
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_load_config(self):
        """Test loading configuration from file"""
        scheduler = ScheduleConfig(self.temp_file.name)
        self.assertIsNotNone(scheduler.config)
        self.assertEqual(scheduler.config['app']['name'], 'Test App')
    
    def test_get_timezone(self):
        """Test getting configured timezone"""
        scheduler = ScheduleConfig(self.temp_file.name)
        timezone = scheduler.get_timezone()
        self.assertEqual(timezone, 'America/New_York')
    
    def test_get_times(self):
        """Test getting configured times"""
        scheduler = ScheduleConfig(self.temp_file.name)
        times = scheduler.get_times()
        self.assertEqual(times, ["06:00", "18:00"])
    
    def test_get_schedule(self):
        """Test getting full schedule configuration"""
        scheduler = ScheduleConfig(self.temp_file.name)
        schedule = scheduler.get_schedule()
        self.assertIn('timezone', schedule)
        self.assertIn('times', schedule)
        self.assertEqual(schedule['timezone'], 'America/New_York')
        self.assertEqual(schedule['times'], ["06:00", "18:00"])
    
    def test_log_schedule(self):
        """Test schedule logging returns correct data"""
        scheduler = ScheduleConfig(self.temp_file.name)
        result = scheduler.log_schedule()
        self.assertIn('timezone', result)
        self.assertIn('times', result)
        self.assertIn('current_utc', result)
        self.assertEqual(result['timezone'], 'America/New_York')
        self.assertEqual(result['times'], ["06:00", "18:00"])
    
    def test_default_values(self):
        """Test default values when schedule not configured"""
        config = {"app": {"name": "Test"}, "scraping": {}}
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(config, temp_file)
        temp_file.close()
        
        try:
            scheduler = ScheduleConfig(temp_file.name)
            self.assertEqual(scheduler.get_timezone(), 'UTC')
            self.assertEqual(scheduler.get_times(), [])
        finally:
            Path(temp_file.name).unlink(missing_ok=True)
    
    def test_missing_config_file(self):
        """Test handling of missing config file"""
        scheduler = ScheduleConfig('/nonexistent/path/config.json')
        # Should not crash, should return defaults
        self.assertEqual(scheduler.get_timezone(), 'UTC')
        self.assertEqual(scheduler.get_times(), [])


if __name__ == '__main__':
    # Run tests
    print("Running Scheduler Module Tests...")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSchedulerModule)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Scheduler Module Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All scheduler module tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some scheduler module tests failed!")
        sys.exit(1)
