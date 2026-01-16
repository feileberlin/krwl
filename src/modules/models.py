"""
Data validation models using Pydantic

This module defines validation schemas for events, locations, and configuration.
It ensures data integrity throughout the scraping, editing, and publishing pipeline.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class Location(BaseModel):
    """Location model with coordinate and address validation"""
    name: str = Field(..., min_length=1, description="Location name")
    address: Optional[str] = Field(None, description="Full address (required unless address_hidden=true)")
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    address_hidden: bool = Field(default=False, description="If true, address is intentionally hidden (underground events)")
    needs_review: bool = Field(default=False, description="If true, location needs editor verification")
    resolution_method: Optional[str] = Field(None, description="How coordinates were determined")
    
    @model_validator(mode='after')
    def validate_address_or_hidden(self) -> 'Location':
        """Validate that address is provided unless address_hidden is true"""
        if not self.address_hidden and not self.address:
            raise ValueError("Address is required unless address_hidden=true for underground/secret events")
        return self


class Event(BaseModel):
    """Event model with comprehensive validation"""
    id: str = Field(..., min_length=1, description="Unique event identifier")
    title: str = Field(..., min_length=3, max_length=200, description="Event title")
    teaser: str = Field(..., min_length=10, max_length=300, description="Short description/teaser")
    description: str = Field(..., min_length=20, max_length=5000, description="Full event description")
    location: Location = Field(..., description="Event location with coordinates")
    start_time: str = Field(..., description="Event start time in ISO format")
    end_time: Optional[str] = Field(None, description="Event end time in ISO format")
    category: str | List[str] = Field(..., description="Event category (at least one required)")
    status: str = Field(default="pending", description="Event status (pending/published)")
    source: str = Field(..., description="Source URL of the event")
    url: Optional[str] = Field(None, description="Additional event URL")
    tags: Optional[List[str]] = Field(default_factory=list, description="Event tags")
    
    @field_validator('teaser')
    @classmethod
    def validate_teaser(cls, v: str) -> str:
        """Validate teaser length"""
        if len(v) < 10:
            raise ValueError(f"Teaser must be at least 10 characters, got {len(v)}")
        if len(v) > 300:
            raise ValueError(f"Teaser must be at most 300 characters, got {len(v)}")
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description length"""
        if len(v) < 20:
            raise ValueError(f"Description must be at least 20 characters, got {len(v)}")
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str | List[str]) -> str | List[str]:
        """Validate category is not empty"""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Category cannot be empty string")
        elif isinstance(v, list):
            if len(v) == 0:
                raise ValueError("Category list cannot be empty")
            for cat in v:
                if not isinstance(cat, str) or not cat.strip():
                    raise ValueError("All categories must be non-empty strings")
        else:
            raise ValueError("Category must be a string or list of strings")
        return v
    
    @field_validator('source')
    @classmethod
    def validate_source_url(cls, v: str) -> str:
        """Validate source is a URL"""
        if not v:
            raise ValueError("Source URL cannot be empty")
        if not (v.startswith('http://') or v.startswith('https://') or v.startswith('www.')):
            raise ValueError(f"Source must be a valid URL (http://, https://, or www.), got: {v}")
        return v
    
    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_iso_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate datetime is in ISO format"""
        if v is None:
            return v
        
        try:
            # Try parsing ISO format (with or without Z suffix)
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Time must be in ISO format (YYYY-MM-DDTHH:MM:SS), got: {v}") from e
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values"""
        allowed_statuses = ['pending', 'published', 'rejected', 'draft']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}, got: {v}")
        return v
    
    @model_validator(mode='after')
    def validate_time_order(self) -> 'Event':
        """Validate end_time is after start_time if both are present"""
        if self.end_time and self.start_time:
            try:
                start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
                if end <= start:
                    raise ValueError(f"end_time must be after start_time")
            except ValueError as e:
                if "end_time must be after start_time" in str(e):
                    raise
                # If parsing fails, skip this validation (will be caught by field validator)
                logger.debug(
                    "Skipping time order validation due to parsing error in Event model: %s",
                    e,
                )
        return self


class ScrapingSource(BaseModel):
    """Scraping source configuration model"""
    name: str = Field(..., min_length=1, description="Source name")
    type: str = Field(..., description="Source type (rss, api, html, facebook)")
    url: str = Field(..., description="Source URL")
    enabled: bool = Field(default=True, description="Whether source is enabled")
    
    @field_validator('type')
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Validate source type is supported"""
        allowed_types = ['rss', 'api', 'html', 'facebook']
        if v not in allowed_types:
            raise ValueError(f"Source type must be one of {allowed_types}, got: {v}")
        return v
    
    @field_validator('url')
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError(f"URL must start with http:// or https://, got: {v}")
        return v


class MapConfig(BaseModel):
    """Map configuration model"""
    default_center: Dict[str, float] = Field(..., description="Default map center")
    default_zoom: int = Field(..., ge=1, le=20, description="Default zoom level (1-20)")
    
    @field_validator('default_center')
    @classmethod
    def validate_center_coordinates(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate map center has valid lat/lon"""
        if 'lat' not in v or 'lon' not in v:
            raise ValueError("default_center must have 'lat' and 'lon' keys")
        
        lat = v['lat']
        lon = v['lon']
        
        if not -90 <= lat <= 90:
            raise ValueError(f"Center latitude must be between -90 and 90, got {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Center longitude must be between -180 and 180, got {lon}")
        
        return v


def validate_event_data(event_data: dict) -> Event:
    """
    Validate event data and return a Pydantic Event model
    
    Args:
        event_data: Dictionary containing event data
        
    Returns:
        Validated Event model
        
    Raises:
        ValueError: If validation fails
    """
    try:
        return Event(**event_data)
    except Exception as e:
        logger.error(f"Event validation failed: {e}", extra={'event_data': event_data})
        raise ValueError(f"Invalid event data: {e}") from e


def validate_events_list(events_data: List[dict]) -> List[Event]:
    """
    Validate a list of events and return validated models
    
    Args:
        events_data: List of event dictionaries
        
    Returns:
        List of validated Event models (invalid events are skipped with warning)
    """
    validated_events = []
    for idx, event_data in enumerate(events_data):
        try:
            validated_event = validate_event_data(event_data)
            validated_events.append(validated_event)
        except ValueError as e:
            logger.warning(
                f"Skipping invalid event at index {idx}: {e}",
                extra={'event_index': idx, 'event_title': event_data.get('title', 'Unknown')}
            )
    
    return validated_events


def validate_location_data(location_data: dict) -> Location:
    """
    Validate location data and return a Pydantic Location model
    
    Args:
        location_data: Dictionary containing location data
        
    Returns:
        Validated Location model
        
    Raises:
        ValueError: If validation fails
    """
    try:
        return Location(**location_data)
    except Exception as e:
        logger.error(f"Location validation failed: {e}", extra={'location_data': location_data})
        raise ValueError(f"Invalid location data: {e}") from e
