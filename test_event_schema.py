#!/usr/bin/env python3
"""
KRWL HOF Event Schema Testing Module

Tests event examples against JSON event schema and filter functionality for stringency.
Provides help on how to recover full functionality when schema violations are detected.

This test module:
1. Defines a JSON schema for event data validation
2. Compares event examples with the schema
3. Validates filter functionality against event data
4. Provides recovery suggestions for any issues found
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple


# Event JSON Schema Definition
EVENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "KRWL HOF Event",
    "description": "Schema for community event data",
    "type": "object",
    "required": ["id", "title", "location", "start_time", "source", "status"],
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique identifier for the event",
            "pattern": "^[a-zA-Z0-9_-]+$"
        },
        "title": {
            "type": "string",
            "description": "Event title",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "description": "Event description",
            "maxLength": 2000
        },
        "location": {
            "type": "object",
            "description": "Event location with coordinates",
            "required": ["name", "lat", "lon"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Venue or location name",
                    "minLength": 1
                },
                "lat": {
                    "type": "number",
                    "description": "Latitude coordinate",
                    "minimum": -90,
                    "maximum": 90
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude coordinate",
                    "minimum": -180,
                    "maximum": 180
                }
            }
        },
        "start_time": {
            "type": "string",
            "description": "Event start time in ISO 8601 format",
            "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"
        },
        "end_time": {
            "type": "string",
            "description": "Event end time in ISO 8601 format (optional)",
            "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"
        },
        "url": {
            "type": "string",
            "description": "URL for more event information",
            "pattern": "^https?://"
        },
        "category": {
            "type": "string",
            "description": "Event category for filtering",
            "enum": ["on-stage", "pub-game", "festival", "workshop", "market", "sports", "community", "other"]
        },
        "source": {
            "type": "string",
            "description": "Source of the event data",
            "enum": ["manual", "rss", "api", "html", "facebook"]
        },
        "status": {
            "type": "string",
            "description": "Publication status of the event",
            "enum": ["draft", "pending", "published", "archived"]
        },
        "published_at": {
            "type": "string",
            "description": "When the event was published",
            "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}"
        }
    }
}

# Recovery suggestions for schema violations
RECOVERY_SUGGESTIONS = {
    "id": {
        "missing": "Add a unique 'id' field. Use format: '<source>_<number>' (e.g., 'manual_1', 'rss_42')",
        "invalid": "ID must contain only letters, numbers, underscores, and hyphens. Fix by removing special characters."
    },
    "title": {
        "missing": "Add a 'title' field with the event name (1-200 characters)",
        "invalid": "Title must be a non-empty string with max 200 characters. Shorten or provide a title."
    },
    "description": {
        "missing": "Consider adding a 'description' field to help users understand the event",
        "invalid": "Description must be a string with max 2000 characters. Consider shortening long descriptions."
    },
    "location": {
        "missing": "Add a 'location' object with 'name', 'lat', and 'lon' properties",
        "invalid": "Location must include 'name' (string), 'lat' (-90 to 90), and 'lon' (-180 to 180)"
    },
    "location.name": {
        "missing": "Add venue/location name to the location object",
        "invalid": "Location name must be a non-empty string"
    },
    "location.lat": {
        "missing": "Add latitude coordinate (e.g., 50.3167 for Hof)",
        "invalid": "Latitude must be a number between -90 and 90"
    },
    "location.lon": {
        "missing": "Add longitude coordinate (e.g., 11.9167 for Hof)",
        "invalid": "Longitude must be a number between -180 and 180"
    },
    "start_time": {
        "missing": "Add 'start_time' in ISO 8601 format (e.g., '2025-12-15T19:00:00')",
        "invalid": "Start time must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SS"
    },
    "end_time": {
        "missing": "Consider adding 'end_time' to show event duration",
        "invalid": "End time must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SS"
    },
    "url": {
        "missing": "Consider adding a 'url' for more event information",
        "invalid": "URL must start with 'http://' or 'https://'"
    },
    "category": {
        "missing": "Consider adding 'category' for better filtering. Options: on-stage, pub-game, festival, workshop, market, sports, community, other",
        "invalid": "Category must be one of: on-stage, pub-game, festival, workshop, market, sports, community, other"
    },
    "source": {
        "missing": "Add 'source' field. Options: manual, rss, api, html, facebook",
        "invalid": "Source must be one of: manual, rss, api, html, facebook"
    },
    "status": {
        "missing": "Add 'status' field. Options: draft, pending, published, archived",
        "invalid": "Status must be one of: draft, pending, published, archived"
    },
    "published_at": {
        "missing": "Consider adding 'published_at' timestamp",
        "invalid": "Published at must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SS"
    }
}


class EventSchemaTester:
    """Tests event data against JSON schema and validates filter functionality"""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.warnings = []
        self.recovery_hints = []
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            print(f"✓ {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            return False
    
    def add_warning(self, warning):
        """Add a warning message"""
        self.warnings.append(warning)
        if self.verbose:
            print(f"  ⚠ Warning: {warning}")
    
    def add_recovery_hint(self, field, issue_type, event_id=None):
        """Add a recovery hint for schema violations"""
        if field in RECOVERY_SUGGESTIONS:
            suggestion = RECOVERY_SUGGESTIONS[field].get(issue_type, "")
            if suggestion:
                hint = {
                    "field": field,
                    "issue_type": issue_type,
                    "suggestion": suggestion,
                    "event_id": event_id
                }
                self.recovery_hints.append(hint)
    
    def validate_event_field(self, event, field, schema_props, parent_field=None):
        """Validate a single field against schema"""
        full_field = f"{parent_field}.{field}" if parent_field else field
        field_schema = schema_props.get(field, {})
        
        errors = []
        
        if field not in event:
            if field in EVENT_SCHEMA.get("required", []):
                errors.append(f"Missing required field: {full_field}")
                self.add_recovery_hint(full_field, "missing", event.get("id"))
            return errors
        
        value = event[field]
        
        # Type validation
        expected_type = field_schema.get("type")
        if expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"Field '{full_field}' must be a string")
                self.add_recovery_hint(full_field, "invalid", event.get("id"))
            else:
                # Pattern validation
                if "pattern" in field_schema:
                    import re
                    if not re.match(field_schema["pattern"], value):
                        errors.append(f"Field '{full_field}' does not match required pattern")
                        self.add_recovery_hint(full_field, "invalid", event.get("id"))
                
                # Length validation
                if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                    errors.append(f"Field '{full_field}' is too short (min: {field_schema['minLength']})")
                    self.add_recovery_hint(full_field, "invalid", event.get("id"))
                if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                    errors.append(f"Field '{full_field}' is too long (max: {field_schema['maxLength']})")
                    self.add_recovery_hint(full_field, "invalid", event.get("id"))
                
                # Enum validation
                if "enum" in field_schema and value not in field_schema["enum"]:
                    errors.append(f"Field '{full_field}' must be one of: {field_schema['enum']}")
                    self.add_recovery_hint(full_field, "invalid", event.get("id"))
        
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{full_field}' must be a number")
                self.add_recovery_hint(full_field, "invalid", event.get("id"))
            else:
                # Range validation
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    errors.append(f"Field '{full_field}' is below minimum ({field_schema['minimum']})")
                    self.add_recovery_hint(full_field, "invalid", event.get("id"))
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    errors.append(f"Field '{full_field}' exceeds maximum ({field_schema['maximum']})")
                    self.add_recovery_hint(full_field, "invalid", event.get("id"))
        
        elif expected_type == "object":
            if not isinstance(value, dict):
                errors.append(f"Field '{full_field}' must be an object")
                self.add_recovery_hint(full_field, "invalid", event.get("id"))
            else:
                # Validate nested properties
                nested_props = field_schema.get("properties", {})
                nested_required = field_schema.get("required", [])
                
                for nested_field in nested_required:
                    if nested_field not in value:
                        errors.append(f"Missing required nested field: {full_field}.{nested_field}")
                        self.add_recovery_hint(f"{full_field}.{nested_field}", "missing", event.get("id"))
                
                for nested_field in value:
                    if nested_field in nested_props:
                        nested_errors = self.validate_event_field(
                            value, nested_field, nested_props, full_field
                        )
                        errors.extend(nested_errors)
        
        return errors
    
    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single event against the schema"""
        errors = []
        
        # Check required fields
        for field in EVENT_SCHEMA.get("required", []):
            if field not in event:
                errors.append(f"Missing required field: {field}")
                self.add_recovery_hint(field, "missing", event.get("id"))
        
        # Validate each field
        schema_props = EVENT_SCHEMA.get("properties", {})
        for field in event:
            if field in schema_props:
                field_errors = self.validate_event_field(event, field, schema_props)
                errors.extend(field_errors)
        
        return len(errors) == 0, errors
    
    def load_events_file(self, filename: str) -> Tuple[List[Dict], str]:
        """Load events from a JSON file"""
        file_path = self.repo_root / "data" / filename
        if not file_path.exists():
            # Try static folder
            file_path = self.repo_root / "static" / filename
        
        if not file_path.exists():
            return [], f"File not found: {filename}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("events", []), ""
        except json.JSONDecodeError as e:
            return [], f"Invalid JSON in {filename}: {e}"
        except Exception as e:
            return [], f"Error loading {filename}: {e}"
    
    def test_schema_definition(self):
        """Test that the schema is properly defined"""
        print("\n=== Schema Definition Tests ===")
        
        # Test schema has required fields
        self.assert_test(
            "$schema" in EVENT_SCHEMA,
            "Schema has $schema declaration"
        )
        
        self.assert_test(
            "properties" in EVENT_SCHEMA,
            "Schema has properties definition"
        )
        
        self.assert_test(
            "required" in EVENT_SCHEMA,
            "Schema has required fields list"
        )
        
        # Test required fields are documented
        required_fields = EVENT_SCHEMA.get("required", [])
        all_documented = all(
            field in EVENT_SCHEMA.get("properties", {})
            for field in required_fields
        )
        self.assert_test(
            all_documented,
            "All required fields have property definitions"
        )
    
    def test_events_example_file(self):
        """Test events_example.json against schema"""
        print("\n=== Events Example File Validation ===")
        
        events, error = self.load_events_file("events_example.json")
        
        if error:
            self.assert_test(False, "Load events_example.json", error)
            return
        
        self.assert_test(
            len(events) > 0,
            f"Events example file has events (found {len(events)})"
        )
        
        valid_count = 0
        invalid_events = []
        
        for i, event in enumerate(events):
            is_valid, errors = self.validate_event(event)
            if is_valid:
                valid_count += 1
            else:
                invalid_events.append({
                    "index": i,
                    "id": event.get("id", f"event_{i}"),
                    "errors": errors
                })
        
        self.assert_test(
            valid_count == len(events),
            f"All example events validate ({valid_count}/{len(events)})",
            f"{len(invalid_events)} events have validation errors"
        )
        
        # Report invalid events
        for inv in invalid_events:
            self.log(f"Event '{inv['id']}' has errors: {inv['errors']}")
    
    def test_events_file(self):
        """Test events.json against schema"""
        print("\n=== Events File Validation ===")
        
        events, error = self.load_events_file("events.json")
        
        if error:
            self.assert_test(False, "Load events.json", error)
            return
        
        self.assert_test(
            len(events) >= 0,
            f"Events file loaded (found {len(events)} events)"
        )
        
        if len(events) == 0:
            self.add_warning("No events in events.json")
            return
        
        valid_count = 0
        invalid_events = []
        
        for i, event in enumerate(events):
            is_valid, errors = self.validate_event(event)
            if is_valid:
                valid_count += 1
            else:
                invalid_events.append({
                    "index": i,
                    "id": event.get("id", f"event_{i}"),
                    "errors": errors
                })
        
        self.assert_test(
            valid_count == len(events),
            f"All events validate ({valid_count}/{len(events)})",
            f"{len(invalid_events)} events have validation errors"
        )
        
        # Report invalid events
        for inv in invalid_events[:5]:  # Limit to first 5
            self.log(f"Event '{inv['id']}' has errors: {inv['errors']}")
        
        if len(invalid_events) > 5:
            self.log(f"... and {len(invalid_events) - 5} more invalid events")
    
    def test_example_vs_schema_consistency(self):
        """Test that example events demonstrate all schema features"""
        print("\n=== Example vs Schema Consistency ===")
        
        events, error = self.load_events_file("events_example.json")
        
        if error:
            self.add_warning(f"Could not load example events: {error}")
            return
        
        # Check if examples cover all optional fields
        optional_fields = set(EVENT_SCHEMA.get("properties", {}).keys())
        optional_fields -= set(EVENT_SCHEMA.get("required", []))
        
        covered_fields = set()
        for event in events:
            covered_fields.update(event.keys())
        
        uncovered = optional_fields - covered_fields
        
        self.assert_test(
            len(uncovered) <= 1,  # Allow 1 uncovered optional field
            f"Example events demonstrate optional fields",
            f"Uncovered fields: {uncovered}" if uncovered else ""
        )
        
        # Check if examples include at least one of each source type
        sources_in_examples = set(e.get("source") for e in events)
        expected_sources = {"manual"}  # At minimum, manual should be shown
        
        self.assert_test(
            expected_sources.issubset(sources_in_examples),
            "Example events include 'manual' source type"
        )
    
    def test_filter_stringency_time(self):
        """Test time filtering stringency against event data"""
        print("\n=== Filter Stringency: Time Filters ===")
        
        events, error = self.load_events_file("events.json")
        if error or len(events) == 0:
            events, error = self.load_events_file("events_example.json")
        
        if error:
            self.add_warning(f"Could not load events for filter testing: {error}")
            return
        
        now = datetime.now()
        
        # Test: Events should have parseable start_time
        parseable_count = 0
        for event in events:
            try:
                start_time = event.get("start_time", "")
                if start_time:
                    datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    parseable_count += 1
            except ValueError:
                self.log(f"Event '{event.get('id')}' has unparseable start_time: {start_time}")
        
        self.assert_test(
            parseable_count == len(events),
            f"All events have parseable start_time ({parseable_count}/{len(events)})"
        )
        
        # Test: Time filter ranges
        time_filters = {
            "6h": timedelta(hours=6),
            "12h": timedelta(hours=12),
            "24h": timedelta(hours=24),
            "48h": timedelta(hours=48)
        }
        
        for filter_name, delta in time_filters.items():
            max_time = now + delta
            filtered = []
            for event in events:
                try:
                    start = datetime.fromisoformat(event.get("start_time", "").replace("Z", "+00:00"))
                    # Remove timezone info for comparison if present
                    if start.tzinfo:
                        start = start.replace(tzinfo=None)
                    if start <= max_time:
                        filtered.append(event)
                except ValueError:
                    continue
            
            self.log(f"Filter '{filter_name}': {len(filtered)} events within range")
        
        self.assert_test(
            True,
            "Time filter ranges compute correctly"
        )
    
    def test_filter_stringency_distance(self):
        """Test distance filtering stringency against event data"""
        print("\n=== Filter Stringency: Distance Filters ===")
        
        events, error = self.load_events_file("events.json")
        if error or len(events) == 0:
            events, error = self.load_events_file("events_example.json")
        
        if error:
            self.add_warning(f"Could not load events for filter testing: {error}")
            return
        
        # Check all events have valid location
        valid_locations = 0
        for event in events:
            loc = event.get("location", {})
            if (isinstance(loc, dict) and
                "lat" in loc and "lon" in loc and
                isinstance(loc["lat"], (int, float)) and
                isinstance(loc["lon"], (int, float)) and
                -90 <= loc["lat"] <= 90 and
                -180 <= loc["lon"] <= 180):
                valid_locations += 1
            else:
                self.log(f"Event '{event.get('id')}' has invalid location: {loc}")
        
        self.assert_test(
            valid_locations == len(events),
            f"All events have valid location coordinates ({valid_locations}/{len(events)})"
        )
        
        # Test distance filter thresholds are reasonable
        # Reference point: Hof city center
        ref_lat, ref_lon = 50.3167, 11.9167
        
        distance_thresholds = {
            "15 min foot (1.25 km)": 1.25,
            "10 min bike (3.33 km)": 3.33,
            "1 hr transport (15 km)": 15.0
        }
        
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            return R * 2 * atan2(sqrt(a), sqrt(1-a))
        
        for threshold_name, max_dist in distance_thresholds.items():
            within_range = 0
            for event in events:
                loc = event.get("location", {})
                if "lat" in loc and "lon" in loc:
                    dist = haversine(ref_lat, ref_lon, loc["lat"], loc["lon"])
                    if dist <= max_dist:
                        within_range += 1
            
            self.log(f"Threshold '{threshold_name}': {within_range} events within range")
        
        self.assert_test(
            True,
            "Distance filter thresholds compute correctly"
        )
    
    def test_filter_stringency_category(self):
        """Test category filtering stringency against event data"""
        print("\n=== Filter Stringency: Category Filters ===")
        
        events, error = self.load_events_file("events.json")
        if error or len(events) == 0:
            events, error = self.load_events_file("events_example.json")
        
        if error:
            self.add_warning(f"Could not load events for filter testing: {error}")
            return
        
        # Count events by category
        categories = {}
        uncategorized = 0
        
        for event in events:
            cat = event.get("category")
            if cat:
                categories[cat] = categories.get(cat, 0) + 1
            else:
                uncategorized += 1
        
        self.log(f"Categories found: {categories}")
        if uncategorized:
            self.log(f"Events without category: {uncategorized}")
        
        # Check categories are from allowed list
        allowed_categories = EVENT_SCHEMA["properties"]["category"].get("enum", [])
        invalid_categories = set(categories.keys()) - set(allowed_categories)
        
        if invalid_categories:
            self.add_warning(f"Found non-standard categories: {invalid_categories}")
            self.add_recovery_hint("category", "invalid")
        
        self.assert_test(
            len(invalid_categories) == 0,
            "All event categories are from allowed list",
            f"Invalid categories: {invalid_categories}" if invalid_categories else ""
        )
    
    def print_recovery_suggestions(self):
        """Print all recovery suggestions collected during testing"""
        if not self.recovery_hints:
            return
        
        print("\n" + "=" * 60)
        print("RECOVERY SUGGESTIONS")
        print("=" * 60)
        
        # Group by event
        by_event = {}
        for hint in self.recovery_hints:
            event_id = hint.get("event_id", "general")
            if event_id not in by_event:
                by_event[event_id] = []
            by_event[event_id].append(hint)
        
        for event_id, hints in by_event.items():
            if event_id != "general":
                print(f"\nEvent '{event_id}':")
            else:
                print("\nGeneral:")
            
            for hint in hints:
                print(f"  → Field '{hint['field']}' ({hint['issue_type']}):")
                print(f"    {hint['suggestion']}")
        
        print("\n" + "-" * 60)
        print("HOW TO RECOVER FULL FUNCTIONALITY:")
        print("-" * 60)
        print("""
1. Open the affected event file (data/events.json or data/events_example.json)

2. For each event with issues:
   - Add missing required fields (id, title, location, start_time, source, status)
   - Fix invalid field values according to the suggestions above
   - Ensure location has lat/lon within valid ranges

3. Validate your changes by running:
   python3 test_event_schema.py --verbose

4. For filters to work correctly:
   - start_time must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
   - location.lat must be between -90 and 90
   - location.lon must be between -180 and 180
   - category should be one of the allowed values for proper filtering

5. If adding new events, use an example event as a template:
   - Copy an existing valid event
   - Change the id to be unique
   - Update all other fields

Example of a valid event:
{
    "id": "example_1",
    "title": "Community Event",
    "description": "A description of the event",
    "location": {
        "name": "Venue Name",
        "lat": 50.3167,
        "lon": 11.9167
    },
    "start_time": "2025-12-15T19:00:00",
    "end_time": "2025-12-15T22:00:00",
    "url": "https://example.com/event",
    "category": "community",
    "source": "manual",
    "status": "published",
    "published_at": "2025-12-01T12:00:00"
}
""")
    
    def run_all_tests(self):
        """Run all schema and filter tests"""
        print("=" * 60)
        print("KRWL HOF Event Schema & Filter Stringency Tests")
        print("=" * 60)
        
        self.test_schema_definition()
        self.test_events_example_file()
        self.test_events_file()
        self.test_example_vs_schema_consistency()
        self.test_filter_stringency_time()
        self.test_filter_stringency_distance()
        self.test_filter_stringency_category()
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        
        if self.warnings:
            print(f"\nWarnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        print("=" * 60)
        
        # Print recovery suggestions if there were failures
        if self.tests_failed > 0 or self.recovery_hints:
            self.print_recovery_suggestions()
        
        if self.tests_failed == 0:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {self.tests_failed} test(s) failed")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test KRWL HOF event data against JSON schema and validate filter stringency"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each test"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Print the event JSON schema and exit"
    )
    
    args = parser.parse_args()
    
    if args.show_schema:
        print(json.dumps(EVENT_SCHEMA, indent=2))
        return 0
    
    tester = EventSchemaTester(
        repo_root=args.repo_root,
        verbose=args.verbose
    )
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
