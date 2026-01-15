"""Shared date parsing helpers for smart scrapers."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re


RELATIVE_OFFSETS = [
    ('übermorgen', 2),
    ('day after tomorrow', 2),
    ('tomorrow', 1),
    ('morgen', 1),
    ('today', 0),
    ('heute', 0)
]


def resolve_relative_date(text: str, base_date: Optional[datetime] = None) -> Optional[datetime]:
    """Resolve relative date expressions like 'tomorrow' into a date."""
    if not text:
        return None
    
    text_lower = text.lower()
    base_date = base_date or datetime.now()
    
    for phrase, offset in RELATIVE_OFFSETS:
        if re.search(rf'\b{re.escape(phrase)}\b', text_lower):
            target = base_date + timedelta(days=offset)
            return datetime(target.year, target.month, target.day)
    
    return None


def extract_time_from_text(text: str) -> Optional[Tuple[int, int]]:
    """Extract time from text, returning (hour, minute) if found."""
    if not text:
        return None
    
    time_patterns = [
        r'(\d{1,2})[:\.](\d{2})\s*(?:uhr)?',
        r'(\d{1,2})\s*uhr',
    ]
    
    for pattern in time_patterns:
        for time_match in re.finditer(pattern, text.lower()):
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.lastindex and time_match.group(2) else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
    
    return None


def resolve_year_for_date(month: int, day: int, base_date: Optional[datetime] = None) -> int:
    """Resolve year for dates missing year, preferring upcoming dates."""
    base_date = base_date or datetime.now()
    year = base_date.year
    candidate = datetime(year, month, day)
    if candidate.date() < base_date.date():
        return year + 1
    return year
