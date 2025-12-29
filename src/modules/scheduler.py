"""Schedule configuration module for event scraping"""

import json
from datetime import datetime, timezone
from pathlib import Path


class ScheduleConfig:
    """Handle schedule configuration for automated scraping"""
    
    def __init__(self, config_path=None):
        """Initialize with config file path"""
        if config_path is None:
            # Default to config.prod.json in repo root
            base_path = Path(__file__).parent.parent.parent
            config_path = base_path / 'config.prod.json'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            return {}
    
    def get_schedule(self):
        """Get schedule configuration"""
        return self.config.get('scraping', {}).get('schedule', {})
    
    def get_timezone(self):
        """Get configured timezone"""
        schedule = self.get_schedule()
        return schedule.get('timezone', 'UTC')
    
    def get_times(self):
        """Get configured scraping times"""
        schedule = self.get_schedule()
        return schedule.get('times', [])
    
    def log_schedule(self):
        """Log schedule configuration for visibility"""
        tz = self.get_timezone()
        times = self.get_times()
        current_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        print("📅 Schedule Configuration:")
        print(f"  Timezone: {tz}")
        print(f"  Scheduled times: {', '.join(times)}")
        print(f"  Current UTC time: {current_utc}")
        
        return {
            'timezone': tz,
            'times': times,
            'current_utc': current_utc
        }


def main():
    """Command-line interface for schedule logging"""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    scheduler = ScheduleConfig(config_path)
    scheduler.log_schedule()


if __name__ == '__main__':
    main()
