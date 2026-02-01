#!/usr/bin/env python3
"""
Event Archiving Module - KISS Implementation

Simple monthly event archiving based on config.json settings.
Archives old events to keep the active list manageable.

KISS simplifications (what this module *does not* handle on purpose):
- Uses month-based grouping only (per-file buckets like ``YYYYMM.json`` or ``YYYY-MM.json``),
  no quarter/year/week archive structures or nested directory layouts.
- Relies on smart defaults from ``config.json`` when archiving keys/sections are missing
  instead of strict schema validation or failing hard on partial configuration.
- Stores archives as flat JSON files on disk (no database, indexing, or search layer).
- Treats dates with straightforward ``datetime`` parsing and basic ISO/date formats only,
  without advanced timezone, locale, or calendar edge-case handling.

This keeps the implementation small and predictable while being "good enough" for the
KRWL> event history use case.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class EventArchiver:
    """Simple event archiver based on config.json settings."""
    
    def __init__(self, config, base_path):
        """Initialize archiver with config and paths."""
        self.config = config
        self.base_path = Path(base_path)
        
        # Get archiving config (with defaults if missing)
        arch_cfg = config.get('archiving', {})
        self.enabled = arch_cfg.get('enabled', True)
        self.retention_days = arch_cfg.get('retention', {}).get('active_window_days', 60)
        
        # Setup archive path
        org_cfg = arch_cfg.get('organization', {})
        archive_path = org_cfg.get('path', 'assets/json/events/archived')
        self.archive_path = self.base_path / archive_path
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        self.format = org_cfg.get('format', 'YYYYMM')
        
        logger.info(f"Archiver ready: {self.retention_days} days retention")
    
    def get_config_info(self):
        """Get archiving configuration as dict."""
        schedule = self.config.get('archiving', {}).get('schedule', {})
        return {
            'enabled': self.enabled,
            'retention_days': self.retention_days,
            'schedule': schedule,
            'archive_path': str(self.archive_path)
        }
    
    def _get_archive_filename(self, event_date):
        """Get archive filename for an event date (e.g., 202601.json)."""
        if self.format == 'YYYY-MM':
            return f"{event_date.strftime('%Y-%m')}.json"
        # Default YYYYMM format
        return f"{event_date.strftime('%Y%m')}.json"
    
    def _load_archive_file(self, filename):
        """Load archive file or return empty structure."""
        filepath = self.archive_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Corrupt archive: {filename}")
        
        return {'archived_events': [], 'last_updated': datetime.now().isoformat()}
    
    def _save_archive_file(self, filename, data):
        """Save archive data to file."""
        filepath = self.archive_path / filename
        data['last_updated'] = datetime.now().isoformat()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {filename}: {len(data.get('archived_events', []))} events")
    
    def archive_events(self, dry_run=False):
        """
        Archive old events based on retention window.
        
        Args:
            dry_run: If True, report what would be archived without changing files
            
        Returns:
            Dict with results: total_events, archived_count, active_count, etc.
        """
        if not self.enabled:
            return {'enabled': False, 'message': 'Archiving disabled in config'}
        
        # Load events
        events_path = self.base_path / 'assets' / 'json' / 'events.json'
        try:
            with open(events_path, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Cannot load events: {e}")
            return {'error': str(e), 'archived_count': 0}
        
        events = events_data.get('events', [])
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        logger.info(f"Archiving events before {cutoff_date.date()} ({self.retention_days} days)")
        
        # Separate active from old events
        active_events = []
        to_archive = []
        
        for event in events:
            event_date = self._parse_event_date(event.get('start'))
            if event_date and event_date < cutoff_date:
                to_archive.append((event, event_date))
            else:
                active_events.append(event)
        
        # Save archives (if not dry run)
        if not dry_run and to_archive:
            self._save_to_archives(to_archive)
            
            # Update events.json with only active events
            events_data['events'] = active_events
            events_data['last_updated'] = datetime.now().isoformat()
            with open(events_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Archived {len(to_archive)}, {len(active_events)} remain active")
        
        return {
            'enabled': True,
            'dry_run': dry_run,
            'total_events': len(events),
            'archived_count': len(to_archive),
            'active_count': len(active_events),
            'cutoff_date': cutoff_date.isoformat(),
            'retention_days': self.retention_days
        }
    
    def _parse_event_date(self, start_str):
        """Parse event start date string to datetime, return None if invalid."""
        if not start_str:
            return None
        try:
            if 'T' in start_str:
                return datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(start_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _save_to_archives(self, events_with_dates):
        """Group events by period and save to archive files."""
        archives = {}
        
        # Group events by archive filename
        for event, event_date in events_with_dates:
            filename = self._get_archive_filename(event_date)
            if filename not in archives:
                archives[filename] = self._load_archive_file(filename)
            archives[filename]['archived_events'].append(event)
        
        # Save all archives
        for filename, archive_data in archives.items():
            self._save_archive_file(filename, archive_data)
    
    def list_archives(self):
        """
        List all archive files with metadata.
        
        Returns:
            List of dicts with filename, period, event_count, last_updated
        """
        archives = []
        for archive_file in sorted(self.archive_path.glob('*.json')):
            try:
                with open(archive_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                archives.append({
                    'filename': archive_file.name,
                    'period': archive_file.stem,
                    'event_count': len(data.get('archived_events', [])),
                    'last_updated': data.get('last_updated', 'unknown')
                })
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Cannot read archive {archive_file.name}: {e}")
        return archives


def print_config_info(archiver):
    """Print archiving configuration in human-readable format."""
    info = archiver.get_config_info()
    schedule = info.get('schedule', {})
    
    print("\n" + "=" * 60)
    print("EVENT ARCHIVING CONFIGURATION")
    print("=" * 60)
    print(f"Status: {'ENABLED' if info['enabled'] else 'DISABLED'}")
    print(f"\nRetention Window: {info['retention_days']} days")
    print(f"  → Events older than {info['retention_days']} days are archived")
    print(f"\nSchedule:")
    print(f"  Day of Month: {schedule.get('day_of_month', 1)}")
    print(f"  Time: {schedule.get('time', '02:00')}")
    print(f"  Timezone: {schedule.get('timezone', 'UTC')}")
    print(f"\nArchive Location: {info['archive_path']}")
    print("=" * 60 + "\n")


def main():
    """
    CLI entry point for testing the archiver.
    
    Usage:
        python3 src/modules/archive_events.py [--dry-run]
    
    Shows current configuration and runs a test archiving operation.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from modules.utils import load_config
    
    base_path = Path(__file__).parent.parent.parent
    config = load_config(base_path)
    archiver = EventArchiver(config, base_path)
    
    # Print configuration
    print_config_info(archiver)
    
    # Run dry-run archiving
    print("Running test archiving (dry-run mode)...")
    print("-" * 60)
    results = archiver.archive_events(dry_run=True)
    
    print(f"Total events: {results.get('total_events', 0)}")
    print(f"Would archive: {results.get('archived_count', 0)}")
    print(f"Would remain active: {results.get('active_count', 0)}")
    
    # List existing archives
    archives = archiver.list_archives()
    if archives:
        print(f"\nExisting archives: {len(archives)}")
        for arch in archives:
            print(f"  {arch['filename']}: {arch['event_count']} events")


if __name__ == '__main__':
    main()
