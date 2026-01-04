"""
Event Data Schema Module

Defines the canonical event data structure with validation, migration,
and category-to-icon mapping. This is the single source of truth for
event data format across the entire application.

Schema-Driven Architecture:
- Event categories define icon requirements (tree-shaking source)
- Automatic migration from old formats
- Validation ensures data quality
- Category-to-icon mapping for markers

Usage:
    from event_schema import EventSchema, EVENT_CATEGORIES, CATEGORY_ICON_MAP
    
    schema = EventSchema()
    is_valid, errors = schema.validate_event(event_data)
    migrated = schema.migrate_event(old_event)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

# Canonical list of valid event categories (60+ categories)
EVENT_CATEGORIES = [
    # Performance & Stage
    "on-stage", "music", "opera-house", "theatre", "concert",
    
    # Social & Community
    "pub-games", "festivals", "community", "social", "meetup",
    
    # Learning & Skills
    "workshops", "school", "education", "training", "seminar",
    
    # Shopping & Commerce
    "shopping", "market", "bazaar", "fair", "trade-show",
    
    # Sports & Fitness
    "sports", "sports-field", "swimming", "fitness", "athletics",
    
    # Arts & Culture
    "arts", "museum", "gallery", "exhibition", "cultural",
    
    # Food & Drink
    "food", "restaurant", "cafe", "dining", "culinary",
    
    # Religious & Spiritual
    "church", "religious", "spiritual", "worship", "ceremony",
    
    # Indigenous & Traditional
    "traditional-oceanic", "indigenous", "heritage", "folklore",
    
    # Historical & Monuments
    "castle", "monument", "tower", "ruins", "palace",
    
    # Parks & Nature
    "park", "nature", "garden", "outdoors", "recreation",
    
    # Government & Civic
    "parliament", "mayors-office", "civic", "government", "public-office",
    
    # Education & Research
    "library", "national-archive", "research", "academic", "study",
    
    # Technology & Innovation
    "tech", "innovation", "startup", "hackathon", "coding",
    
    # Health & Wellness
    "health", "wellness", "medical", "therapy", "healing",
    
    # Family & Kids
    "family", "kids", "children", "youth", "playground",
    
    # Business & Networking
    "business", "networking", "conference", "corporate", "professional",
    
    # Default fallback
    "default", "other", "miscellaneous", "general"
]

# Category to Lucide icon mapping (source of truth for tree-shaking)
CATEGORY_ICON_MAP = {
    # Performance & Stage
    "on-stage": "drama",
    "music": "music",
    "opera-house": "landmark",
    "theatre": "drama",
    "concert": "music",
    
    # Social & Community
    "pub-games": "beer",
    "festivals": "star",
    "community": "users",
    "social": "users",
    "meetup": "users",
    
    # Learning & Skills
    "workshops": "presentation",
    "school": "graduation-cap",
    "education": "graduation-cap",
    "training": "presentation",
    "seminar": "presentation",
    
    # Shopping & Commerce
    "shopping": "shopping-bag",
    "market": "shopping-bag",
    "bazaar": "shopping-bag",
    "fair": "star",
    "trade-show": "presentation",
    
    # Sports & Fitness
    "sports": "trophy",
    "sports-field": "ticket",
    "swimming": "waves",
    "fitness": "trophy",
    "athletics": "trophy",
    
    # Arts & Culture
    "arts": "palette",
    "museum": "landmark",
    "gallery": "palette",
    "exhibition": "landmark",
    "cultural": "landmark",
    
    # Food & Drink
    "food": "utensils",
    "restaurant": "utensils",
    "cafe": "beer",
    "dining": "utensils",
    "culinary": "utensils",
    
    # Religious & Spiritual
    "church": "church",
    "religious": "church",
    "spiritual": "flame",
    "worship": "church",
    "ceremony": "church",
    
    # Indigenous & Traditional
    "traditional-oceanic": "flame",
    "indigenous": "flame",
    "heritage": "landmark",
    "folklore": "flame",
    
    # Historical & Monuments
    "castle": "castle",
    "monument": "pilcrow",
    "tower": "triangle",
    "ruins": "blocks",
    "palace": "crown",
    
    # Parks & Nature
    "park": "tree-pine",
    "nature": "tree-pine",
    "garden": "tree-pine",
    "outdoors": "tree-pine",
    "recreation": "tree-pine",
    
    # Government & Civic
    "parliament": "landmark",
    "mayors-office": "building",
    "civic": "building",
    "government": "landmark",
    "public-office": "building",
    
    # Education & Research
    "library": "book-open",
    "national-archive": "archive",
    "research": "book-open",
    "academic": "graduation-cap",
    "study": "book-open",
    
    # Technology & Innovation
    "tech": "cpu",
    "innovation": "lightbulb",
    "startup": "rocket",
    "hackathon": "code",
    "coding": "code",
    
    # Health & Wellness
    "health": "heart-pulse",
    "wellness": "heart",
    "medical": "cross",
    "therapy": "heart-pulse",
    "healing": "heart",
    
    # Family & Kids
    "family": "users",
    "kids": "baby",
    "children": "baby",
    "youth": "users",
    "playground": "tree-pine",
    
    # Business & Networking
    "business": "briefcase",
    "networking": "network",
    "conference": "presentation",
    "corporate": "building",
    "professional": "briefcase",
    
    # Default fallback
    "default": "map-pin",
    "other": "map-pin",
    "miscellaneous": "help-circle",
    "general": "map-pin",
    
    # Geolocation marker (special)
    "geolocation": "locate"
}


class EventSchema:
    """
    Event Data Schema Manager
    
    Handles event validation, migration, and schema enforcement.
    Provides category-to-icon mapping for tree-shaking.
    """
    
    def __init__(self):
        self.categories = EVENT_CATEGORIES
        self.icon_map = CATEGORY_ICON_MAP
    
    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate event against canonical schema.
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['id', 'title', 'location', 'start_time', 'source']
        for field in required_fields:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        # Location structure
        if 'location' in event:
            if not isinstance(event['location'], dict):
                errors.append("Location must be a dictionary")
            else:
                if 'name' not in event['location']:
                    errors.append("Location missing 'name' field")
                if 'lat' not in event['location']:
                    errors.append("Location missing 'lat' field")
                if 'lon' not in event['location']:
                    errors.append("Location missing 'lon' field")
        
        # Category validation (if present)
        if 'category' in event:
            if event['category'] not in self.categories:
                errors.append(f"Invalid category: {event['category']}. Must be one of {len(self.categories)} valid categories")
        
        # Date format validation
        if 'start_time' in event:
            try:
                # Should be ISO 8601 format
                if isinstance(event['start_time'], str):
                    datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            except ValueError as e:
                errors.append(f"Invalid start_time format: {e}")
        
        return len(errors) == 0, errors
    
    def migrate_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate event from old format to new schema.
        
        Handles:
        - Adding missing fields with defaults
        - Inferring category from title/description
        - Normalizing date formats
        
        Args:
            event: Event in old format
            
        Returns:
            Event in new schema format
        """
        migrated = event.copy()
        
        # Add category if missing (default)
        if 'category' not in migrated:
            # Try to infer from title/description
            migrated['category'] = self._infer_category(
                migrated.get('title', ''),
                migrated.get('description', '')
            )
        
        # Ensure status field
        if 'status' not in migrated:
            migrated['status'] = 'published'
        
        # Add scraped_at if missing
        if 'scraped_at' not in migrated:
            migrated['scraped_at'] = datetime.now().isoformat()
        
        # Normalize end_time
        if 'end_time' not in migrated:
            migrated['end_time'] = None
        
        return migrated
    
    def _infer_category(self, title: str, description: str) -> str:
        """
        Infer event category from title and description.
        
        Uses keyword matching to guess the most likely category.
        Falls back to 'default' if no match found.
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            Category string
        """
        text = f"{title} {description}".lower()
        
        # Keyword to category mapping
        keyword_map = {
            'music': ['music', 'concert', 'band', 'orchestra'],
            'sports': ['sport', 'game', 'match', 'tournament'],
            'food': ['food', 'restaurant', 'dining', 'culinary'],
            'arts': ['art', 'exhibition', 'gallery', 'paint'],
            'workshops': ['workshop', 'class', 'training', 'learn'],
            'festivals': ['festival', 'celebration', 'carnival'],
            'theatre': ['theatre', 'theater', 'play', 'drama'],
            'museum': ['museum', 'history', 'heritage'],
            'community': ['community', 'meetup', 'gathering'],
            'shopping': ['market', 'shopping', 'bazaar', 'sale'],
        }
        
        for category, keywords in keyword_map.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'default'
    
    def get_icon_for_category(self, category: str) -> str:
        """
        Get Lucide icon name for a category.
        
        Args:
            category: Event category
            
        Returns:
            Lucide icon name (e.g., 'music', 'drama')
        """
        return self.icon_map.get(category, 'map-pin')
    
    def get_used_categories(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of categories actually used in events.
        
        This is used by tree-shaking to determine which icons are needed.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of unique category strings
        """
        categories = set()
        for event in events:
            category = event.get('category', 'default')
            categories.add(category)
        
        # Always include default and geolocation
        categories.add('default')
        categories.add('geolocation')
        
        return sorted(list(categories))
    
    def get_required_icons(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of icon names required for the given events.
        
        This is the key function for icon tree-shaking.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of unique Lucide icon names needed
        """
        categories = self.get_used_categories(events)
        icons = set()
        
        for category in categories:
            icon = self.get_icon_for_category(category)
            icons.add(icon)
        
        return sorted(list(icons))
    
    def export_schema_documentation(self, output_path: Path) -> None:
        """
        Export schema documentation as Markdown.
        
        Args:
            output_path: Path to write documentation file
        """
        doc = []
        doc.append("# Event Data Schema")
        doc.append("")
        doc.append("Auto-generated schema documentation for KRWL HOF Community Events.")
        doc.append("")
        doc.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")
        
        doc.append("## Event Structure")
        doc.append("")
        doc.append("```json")
        doc.append(json.dumps({
            "id": "unique_event_id",
            "title": "Event Title",
            "description": "Event description",
            "location": {
                "name": "Venue Name",
                "lat": 52.5200,
                "lon": 13.4050
            },
            "start_time": "2026-01-15T19:00:00",
            "end_time": "2026-01-15T22:00:00",
            "url": "https://example.com/event",
            "source": "source_name",
            "category": "music",
            "status": "published",
            "scraped_at": "2026-01-01T12:00:00",
            "published_at": "2026-01-01T12:05:00"
        }, indent=2))
        doc.append("```")
        doc.append("")
        
        doc.append("## Valid Categories")
        doc.append("")
        doc.append(f"Total: {len(self.categories)} categories")
        doc.append("")
        
        # Group by theme
        themes = {
            "Performance & Stage": ["on-stage", "music", "opera-house", "theatre", "concert"],
            "Social & Community": ["pub-games", "festivals", "community", "social", "meetup"],
            "Learning & Skills": ["workshops", "school", "education", "training", "seminar"],
            "Shopping & Commerce": ["shopping", "market", "bazaar", "fair", "trade-show"],
            "Sports & Fitness": ["sports", "sports-field", "swimming", "fitness", "athletics"],
            "Arts & Culture": ["arts", "museum", "gallery", "exhibition", "cultural"],
            "Food & Drink": ["food", "restaurant", "cafe", "dining", "culinary"],
        }
        
        for theme, cats in themes.items():
            doc.append(f"### {theme}")
            doc.append("")
            for cat in cats:
                if cat in self.categories:
                    icon = self.get_icon_for_category(cat)
                    doc.append(f"- `{cat}` → Lucide icon: `{icon}`")
            doc.append("")
        
        doc.append("## Category to Icon Mapping")
        doc.append("")
        doc.append("This mapping is used for tree-shaking to determine which icons are needed.")
        doc.append("")
        doc.append("| Category | Lucide Icon |")
        doc.append("|----------|-------------|")
        for category in sorted(self.icon_map.keys())[:20]:  # Show first 20
            icon = self.icon_map[category]
            doc.append(f"| `{category}` | `{icon}` |")
        doc.append(f"| ... | ({len(self.icon_map)} total mappings) |")
        doc.append("")
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('\n'.join(doc))
        logger.info(f"Schema documentation exported to {output_path}")


def validate_events_file(file_path: Path) -> Tuple[bool, List[str], List[Dict]]:
    """
    Validate all events in a JSON file.
    
    Args:
        file_path: Path to events.json file
        
    Returns:
        Tuple of (all_valid, list_of_errors, list_of_invalid_events)
    """
    schema = EventSchema()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        events = data.get('events', [])
        all_errors = []
        invalid_events = []
        
        for i, event in enumerate(events):
            is_valid, errors = schema.validate_event(event)
            if not is_valid:
                all_errors.extend([f"Event #{i} ({event.get('id', 'unknown')}): {err}" for err in errors])
                invalid_events.append(event)
        
        return len(all_errors) == 0, all_errors, invalid_events
        
    except Exception as e:
        return False, [f"Failed to load events file: {e}"], []


def migrate_events_file(file_path: Path, backup: bool = True) -> int:
    """
    Migrate all events in a file to new schema.
    
    Args:
        file_path: Path to events.json file
        backup: Whether to create backup before migration
        
    Returns:
        Number of events migrated
    """
    schema = EventSchema()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Backup if requested
        if backup:
            backup_path = file_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Backup created: {backup_path}")
        
        # Migrate events
        events = data.get('events', [])
        migrated_events = []
        
        for event in events:
            migrated = schema.migrate_event(event)
            migrated_events.append(migrated)
        
        # Update data
        data['events'] = migrated_events
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Migrated {len(migrated_events)} events in {file_path}")
        return len(migrated_events)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 0


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python event_schema.py <command>")
        print("Commands:")
        print("  categories - List all valid categories")
        print("  icons - List all icon mappings")
        print("  validate <file> - Validate events file")
        print("  migrate <file> - Migrate events file to new schema")
        sys.exit(1)
    
    command = sys.argv[1]
    schema = EventSchema()
    
    if command == 'categories':
        print(f"Valid categories ({len(schema.categories)}):")
        for cat in schema.categories:
            print(f"  - {cat}")
    
    elif command == 'icons':
        print(f"Icon mappings ({len(schema.icon_map)}):")
        for cat, icon in sorted(schema.icon_map.items()):
            print(f"  {cat:30s} → {icon}")
    
    elif command == 'validate' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        is_valid, errors, invalid = validate_events_file(file_path)
        if is_valid:
            print(f"✅ All events in {file_path} are valid!")
        else:
            print(f"❌ Found {len(errors)} validation errors:")
            for error in errors:
                print(f"  - {error}")
    
    elif command == 'migrate' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        count = migrate_events_file(file_path)
        print(f"✅ Migrated {count} events in {file_path}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
