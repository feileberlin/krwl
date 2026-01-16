"""
Event Validator Module

Validates events have complete basic data before publishing.
Prevents incomplete events from being published (individual or bulk).

Required basic data:
- id (event identifier)
- title (non-empty string)
- teaser (short description)
- description (full description)
- location (name, address, lat, lon)
- start_time (valid ISO format)
- category (at least one category)
- source (link/url to event source)
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import re


class ValidationError:
    """Represents a validation error for an event field."""
    
    def __init__(self, field: str, message: str, severity: str = 'error'):
        """
        Initialize validation error.
        
        Args:
            field: Field name that failed validation
            message: Human-readable error message
            severity: 'error' (blocks publish) or 'warning' (advisory)
        """
        self.field = field
        self.message = message
        self.severity = severity
    
    def __repr__(self):
        return f"ValidationError(field='{self.field}', message='{self.message}', severity='{self.severity}')"
    
    def __str__(self):
        icon = "✗" if self.severity == 'error' else "⚠"
        return f"{icon} {self.field}: {self.message}"


class ValidationResult:
    """Result of event validation."""
    
    def __init__(self, is_valid: bool, errors: List[ValidationError], warnings: List[ValidationError]):
        """
        Initialize validation result.
        
        Args:
            is_valid: True if event can be published, False otherwise
            errors: List of validation errors (block publishing)
            warnings: List of validation warnings (advisory only)
        """
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_summary(self) -> str:
        """Get human-readable summary of validation result."""
        if self.is_valid and not self.has_warnings():
            return "✓ Event is valid and ready to publish"
        
        lines = []
        if not self.is_valid:
            lines.append(f"✗ Event CANNOT be published ({len(self.errors)} error(s)):")
            for error in self.errors:
                lines.append(f"  {error}")
        
        if self.has_warnings():
            lines.append(f"⚠ Event has {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                lines.append(f"  {warning}")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"ValidationResult(is_valid={self.is_valid}, errors={len(self.errors)}, warnings={len(self.warnings)})"


class EventValidator:
    """
    Validate events have complete basic data.
    
    Enforces strict validation to ensure no incomplete events are published.
    """
    
    # Required fields that MUST be present and valid
    REQUIRED_FIELDS = ['id', 'title', 'teaser', 'description', 'location', 'start_time', 'category', 'source']
    
    # Fields that should be present but can be empty/None
    OPTIONAL_FIELDS = ['end_time', 'url', 'image']
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize event validator.
        
        Args:
            strict_mode: If True, enforces strict validation (recommended)
        """
        self.strict_mode = strict_mode
    
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single event.
        
        Args:
            event: Event dictionary to validate
            
        Returns:
            ValidationResult with is_valid flag and error/warning lists
        """
        errors = []
        warnings = []
        
        # Validate required fields exist
        for field in self.REQUIRED_FIELDS:
            if field not in event:
                errors.append(ValidationError(
                    field,
                    f"Required field '{field}' is missing",
                    severity='error'
                ))
        
        # Validate ID
        if 'id' in event:
            id_error = self._validate_id(event['id'])
            if id_error:
                errors.append(id_error)
        
        # Validate title
        if 'title' in event:
            title_error = self._validate_title(event['title'])
            if title_error:
                errors.append(title_error)
        
        # Validate teaser
        if 'teaser' in event:
            teaser_error = self._validate_teaser(event['teaser'])
            if teaser_error:
                errors.append(teaser_error)
        
        # Validate description
        if 'description' in event:
            desc_error = self._validate_description(event['description'])
            if desc_error:
                errors.append(desc_error)
        
        # Validate location (CRITICAL)
        if 'location' in event:
            location_errors, location_warnings = self._validate_location(event['location'])
            errors.extend(location_errors)
            warnings.extend(location_warnings)
        
        # Validate start_time
        if 'start_time' in event:
            time_error = self._validate_datetime(event['start_time'], 'start_time')
            if time_error:
                errors.append(time_error)
        
        # Validate end_time (optional, but if present must be valid)
        if 'end_time' in event and event['end_time'] is not None:
            time_error = self._validate_datetime(event['end_time'], 'end_time')
            if time_error:
                errors.append(time_error)
            
            # Validate end_time is after start_time
            if 'start_time' in event and event.get('end_time'):
                try:
                    start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
                    if end <= start:
                        errors.append(ValidationError(
                            'end_time',
                            'End time must be after start time',
                            severity='error'
                        ))
                except:
                    pass  # Already caught by datetime validation
        
        # Validate category
        if 'category' in event:
            category_error = self._validate_category(event['category'])
            if category_error:
                errors.append(category_error)
        
        # Validate source
        if 'source' in event:
            source_error = self._validate_source(event['source'])
            if source_error:
                errors.append(source_error)
        
        # Check for needs_review flag (warning only)
        if event.get('location', {}).get('needs_review'):
            warnings.append(ValidationError(
                'location',
                'Location coordinates need editor verification',
                severity='warning'
            ))
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def validate_bulk(self, events: List[Dict[str, Any]]) -> Tuple[List[str], List[str], Dict[str, ValidationResult]]:
        """
        Validate multiple events for bulk operations.
        
        Args:
            events: List of event dictionaries to validate
            
        Returns:
            Tuple of (valid_event_ids, invalid_event_ids, validation_results)
        """
        valid_ids = []
        invalid_ids = []
        results = {}
        
        for event in events:
            event_id = event.get('id', 'unknown')
            result = self.validate(event)
            results[event_id] = result
            
            if result.is_valid:
                valid_ids.append(event_id)
            else:
                invalid_ids.append(event_id)
        
        return valid_ids, invalid_ids, results
    
    def _validate_id(self, event_id: Any) -> Optional[ValidationError]:
        """Validate event ID."""
        if not event_id:
            return ValidationError('id', 'Event ID cannot be empty', severity='error')
        
        if not isinstance(event_id, str):
            return ValidationError('id', f'Event ID must be string, got {type(event_id).__name__}', severity='error')
        
        # ID should have reasonable length
        if len(event_id) > 200:
            return ValidationError('id', f'Event ID too long ({len(event_id)} chars, max 200)', severity='error')
        
        return None
    
    def _validate_title(self, title: Any) -> Optional[ValidationError]:
        """Validate event title."""
        if not title:
            return ValidationError('title', 'Event title cannot be empty', severity='error')
        
        if not isinstance(title, str):
            return ValidationError('title', f'Event title must be string, got {type(title).__name__}', severity='error')
        
        # Title should have reasonable length
        if len(title) < 3:
            return ValidationError('title', f'Event title too short ({len(title)} chars, min 3)', severity='error')
        
        if len(title) > 200:
            return ValidationError('title', f'Event title too long ({len(title)} chars, max 200)', severity='error')
        
        return None
    
    def _validate_teaser(self, teaser: Any) -> Optional[ValidationError]:
        """Validate event teaser (short description)."""
        if not teaser:
            return ValidationError('teaser', 'Event teaser cannot be empty', severity='error')
        
        if not isinstance(teaser, str):
            return ValidationError('teaser', f'Event teaser must be string, got {type(teaser).__name__}', severity='error')
        
        # Teaser should be short (10-300 chars)
        if len(teaser) < 10:
            return ValidationError('teaser', f'Event teaser too short ({len(teaser)} chars, min 10)', severity='error')
        
        if len(teaser) > 300:
            return ValidationError('teaser', f'Event teaser too long ({len(teaser)} chars, max 300)', severity='error')
        
        return None
    
    def _validate_description(self, description: Any) -> Optional[ValidationError]:
        """Validate event description (full description)."""
        if not description:
            return ValidationError('description', 'Event description cannot be empty', severity='error')
        
        if not isinstance(description, str):
            return ValidationError('description', f'Event description must be string, got {type(description).__name__}', severity='error')
        
        # Description should be substantial (20+ chars)
        if len(description) < 20:
            return ValidationError('description', f'Event description too short ({len(description)} chars, min 20)', severity='error')
        
        if len(description) > 5000:
            return ValidationError('description', f'Event description too long ({len(description)} chars, max 5000)', severity='error')
        
        return None
    
    def _validate_category(self, category: Any) -> Optional[ValidationError]:
        """Validate event category (at least one category required)."""
        if not category:
            return ValidationError('category', 'Event must have at least one category', severity='error')
        
        # Category can be a string or list
        if isinstance(category, str):
            if len(category.strip()) == 0:
                return ValidationError('category', 'Category cannot be empty string', severity='error')
        elif isinstance(category, list):
            if len(category) == 0:
                return ValidationError('category', 'Category list cannot be empty', severity='error')
            # Check that all categories are non-empty strings
            for i, cat in enumerate(category):
                if not isinstance(cat, str):
                    return ValidationError('category', f'Category[{i}] must be string, got {type(cat).__name__}', severity='error')
                if len(cat.strip()) == 0:
                    return ValidationError('category', f'Category[{i}] cannot be empty string', severity='error')
        else:
            return ValidationError('category', f'Category must be string or list, got {type(category).__name__}', severity='error')
        
        return None
    
    def _validate_location(self, location: Any) -> Tuple[List[ValidationError], List[ValidationError]]:
        """
        Validate event location (CRITICAL validation).
        
        Location MUST have:
        - name (non-empty string)
        - address (full German address) - REQUIRED unless address_hidden=true
        - lat (valid latitude -90 to 90)
        - lon (valid longitude -180 to 180)
        
        Special Cases:
        - address_hidden=true: Address not required (underground/secret events)
        - needs_review=true: Validation passes but warns editor
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        if not location:
            errors.append(ValidationError('location', 'Location cannot be empty', severity='error'))
            return errors, warnings
        
        if not isinstance(location, dict):
            errors.append(ValidationError('location', f'Location must be dict, got {type(location).__name__}', severity='error'))
            return errors, warnings
        
        # Check for special flags
        address_hidden = location.get('address_hidden', False)
        
        # Validate location name
        if 'name' not in location:
            errors.append(ValidationError('location.name', 'Location name is required', severity='error'))
        elif not location['name']:
            errors.append(ValidationError('location.name', 'Location name cannot be empty', severity='error'))
        elif not isinstance(location['name'], str):
            errors.append(ValidationError('location.name', f'Location name must be string, got {type(location["name"]).__name__}', severity='error'))
        else:
            # Check for generic/placeholder names
            generic_names = ['Unknown', 'Unknown Location', 'Hof', 'Bayreuth', 'Selb']
            if location['name'] in generic_names and not address_hidden:
                warnings.append(ValidationError('location.name', f'Generic location name "{location["name"]}" should be more specific', severity='warning'))
        
        # Validate address (REQUIRED unless address_hidden=true)
        if address_hidden:
            # Underground/secret event - address intentionally hidden
            if location.get('address'):
                warnings.append(ValidationError('location.address', 'Address marked as hidden but provided (will be hidden from public)', severity='warning'))
            else:
                warnings.append(ValidationError('location.address', 'Address intentionally hidden (underground/secret event)', severity='warning'))
        else:
            # Normal event - address required
            if 'address' not in location:
                errors.append(ValidationError('location.address', 'Address is required (use address_hidden=true for secret events)', severity='error'))
            elif not location['address']:
                errors.append(ValidationError('location.address', 'Address cannot be empty (use address_hidden=true for secret events)', severity='error'))
            elif not isinstance(location['address'], str):
                errors.append(ValidationError('location.address', f'Address must be string, got {type(location["address"]).__name__}', severity='error'))
            else:
                # Validate address format (German: Street Number, ZIP City)
                address = location['address']
                # Check for basic address components
                has_number = any(char.isdigit() for char in address)
                has_comma = ',' in address
                if not (has_number and has_comma):
                    warnings.append(ValidationError('location.address', 'Address should include street number and city (format: Street Number, ZIP City)', severity='warning'))
        
        # Validate latitude
        if 'lat' not in location:
            errors.append(ValidationError('location.lat', 'Latitude is required', severity='error'))
        elif location['lat'] is None:
            errors.append(ValidationError('location.lat', 'Latitude cannot be None', severity='error'))
        else:
            try:
                lat = float(location['lat'])
                if lat < -90 or lat > 90:
                    errors.append(ValidationError('location.lat', f'Latitude must be between -90 and 90, got {lat}', severity='error'))
            except (TypeError, ValueError):
                errors.append(ValidationError('location.lat', f'Latitude must be number, got {type(location["lat"]).__name__}', severity='error'))
        
        # Validate longitude
        if 'lon' not in location:
            errors.append(ValidationError('location.lon', 'Longitude is required', severity='error'))
        elif location['lon'] is None:
            errors.append(ValidationError('location.lon', 'Longitude cannot be None', severity='error'))
        else:
            try:
                lon = float(location['lon'])
                if lon < -180 or lon > 180:
                    errors.append(ValidationError('location.lon', f'Longitude must be between -180 and 180, got {lon}', severity='error'))
            except (TypeError, ValueError):
                errors.append(ValidationError('location.lon', f'Longitude must be number, got {type(location["lon"]).__name__}', severity='error'))
        
        return errors, warnings
    
    def _validate_datetime(self, dt_string: Any, field_name: str) -> Optional[ValidationError]:
        """Validate datetime string."""
        if not dt_string:
            return ValidationError(field_name, f'{field_name} cannot be empty', severity='error')
        
        if not isinstance(dt_string, str):
            return ValidationError(field_name, f'{field_name} must be string, got {type(dt_string).__name__}', severity='error')
        
        # Try to parse as ISO format
        try:
            datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError as e:
            return ValidationError(field_name, f'Invalid datetime format: {str(e)}', severity='error')
        
        return None
    
    def _validate_source(self, source: Any) -> Optional[ValidationError]:
        """Validate event source (link/url)."""
        if not source:
            return ValidationError('source', 'Event source (link/url) cannot be empty', severity='error')
        
        if not isinstance(source, str):
            return ValidationError('source', f'Event source must be string, got {type(source).__name__}', severity='error')
        
        # Check if source looks like a URL
        source_lower = source.lower()
        if not (source_lower.startswith('http://') or source_lower.startswith('https://') or source_lower.startswith('www.')):
            return ValidationError('source', f'Event source should be a URL (http://, https://, or www.)', severity='error')
        
        return None


def validate_event(event: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate a single event.
    
    Args:
        event: Event dictionary to validate
        
    Returns:
        ValidationResult
    """
    validator = EventValidator(strict_mode=True)
    return validator.validate(event)


def validate_events(events: List[Dict[str, Any]]) -> Tuple[List[str], List[str], Dict[str, ValidationResult]]:
    """
    Convenience function to validate multiple events.
    
    Args:
        events: List of event dictionaries to validate
        
    Returns:
        Tuple of (valid_event_ids, invalid_event_ids, validation_results)
    """
    validator = EventValidator(strict_mode=True)
    return validator.validate_bulk(events)
