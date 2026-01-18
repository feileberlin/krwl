"""
Entity Data Models

All dataclasses for the entity system:
- Location (venues/places)
- Organizer (event organizers)
- Helper functions (ID generation, validation)
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import re


@dataclass
class Location:
    """Verified location entity"""
    id: str
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    address_hidden: bool = False
    category: Optional[str] = None
    verified: bool = False
    verified_at: Optional[str] = None
    verified_by: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    accessibility: Optional[Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values"""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        """Create Location from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Organizer:
    """Verified organizer entity"""
    id: str
    name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    verified: bool = False
    verified_at: Optional[str] = None
    verified_by: Optional[str] = None
    description: Optional[str] = None
    social_media: Dict[str, str] = field(default_factory=dict)
    address: Optional[str] = None
    contact_person: Optional[str] = None
    logo_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values"""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Organizer':
        """Create Organizer from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def generate_location_id(name: str) -> str:
    """
    Generate unique location ID from name
    
    Examples:
        "Theater Hof" → "loc_theater_hof"
        "RW21 Volkshochschule" → "loc_rw21_volkshochschule"
        "Café am Markt" → "loc_caf_am_markt"
    """
    clean_name = re.sub(r'[^\w\s-]', '', name.lower(), flags=re.ASCII)
    clean_name = re.sub(r'[-\s]+', '_', clean_name)
    return f"loc_{clean_name}"


def generate_organizer_id(name: str) -> str:
    """
    Generate unique organizer ID from name
    
    Examples:
        "Kulturverein Hof" → "org_kulturverein_hof"
        "Theater Hof" → "org_theater_hof"
    """
    clean_name = re.sub(r'[^\w\s-]', '', name.lower(), flags=re.ASCII)
    clean_name = re.sub(r'[-\s]+', '_', clean_name)
    return f"org_{clean_name}"
