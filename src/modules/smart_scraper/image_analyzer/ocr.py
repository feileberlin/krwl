"""OCR text extraction from images.

This module provides OCR capabilities for extracting event information from images,
particularly event flyers. It's designed to be reusable across all social media scrapers.

Features:
- Text extraction via Tesseract OCR
- Date/time pattern recognition (German and English)
- Event-specific keyword extraction
- URL extraction from flyers
"""

from typing import Dict, Any, Optional, List, Union
from io import BytesIO
import re
from datetime import datetime

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def is_ocr_available() -> bool:
    """Check if OCR functionality is available.
    
    Returns:
        True if Tesseract and PIL are available
    """
    return TESSERACT_AVAILABLE and PIL_AVAILABLE


def extract_text(image_source: Union[str, bytes, BytesIO], 
                 languages: List[str] = None) -> Optional[str]:
    """Extract text from image using OCR.
    
    Args:
        image_source: Path to image file, bytes data, or BytesIO object
        languages: List of language codes (e.g., ['eng', 'deu'])
        
    Returns:
        Extracted text or None
    """
    if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
        return None
    
    try:
        # Handle different input types
        if isinstance(image_source, bytes):
            img = Image.open(BytesIO(image_source))
        elif isinstance(image_source, BytesIO):
            img = Image.open(image_source)
        else:
            img = Image.open(image_source)
        
        # Configure languages (default: English + German for this project)
        lang = '+'.join(languages) if languages else 'eng+deu'
        
        # Extract text
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"  OCR error: {e}")
        return None


def extract_text_from_url(image_url: str, languages: List[str] = None,
                          timeout: int = 10) -> Optional[str]:
    """Extract text from an image URL using OCR.
    
    Args:
        image_url: URL of the image to process
        languages: List of language codes (e.g., ['eng', 'deu'])
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text or None
    """
    if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
        return None
    
    try:
        import requests
        response = requests.get(image_url, timeout=timeout)
        response.raise_for_status()
        return extract_text(response.content, languages)
    except Exception as e:
        print(f"  OCR URL error: {e}")
        return None


def extract_dates(text: str) -> List[str]:
    """Extract date patterns from text.
    
    Supports German and English date formats commonly found on event flyers.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of date strings found
    """
    dates = []
    
    # Date patterns - ordered by specificity
    patterns = [
        # German formats
        r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
        r'\d{1,2}\.\d{1,2}\.\d{2}(?!\d)',  # DD.MM.YY
        r'\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4}',
        r'\d{1,2}\.\s*(?:Jan|Feb|Mär|Apr|Mai|Jun|Jul|Aug|Sep|Okt|Nov|Dez)\.?\s*\d{4}',
        # English formats
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD (ISO)
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY or DD/MM/YYYY
        r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}',
        # German weekday + date
        r'(?:Mo|Di|Mi|Do|Fr|Sa|So)[.,]?\s*\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})?',
        # Relative dates (German)
        r'(?:heute|morgen|übermorgen)',
        # Relative dates (English)
        r'(?:today|tomorrow|day after tomorrow)',
        # Date ranges
        r'\d{1,2}\.\s*[-–]\s*\d{1,2}\.\d{1,2}\.\d{4}',  # DD.-DD.MM.YYYY
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return dates


def extract_times(text: str) -> List[str]:
    """Extract time patterns from text.
    
    Supports German and English time formats commonly found on event flyers.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of time strings found
    """
    times = []
    
    # Time patterns
    patterns = [
        r'\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?',  # HH:MM or HH:MM AM/PM
        r'\d{1,2}\s*[Uu]hr',  # German: 18 Uhr
        r'\d{1,2}\s*h(?:\d{2})?',  # 18h or 18h30
        r'(?:ab|von|um)\s*\d{1,2}(?::\d{2})?\s*(?:Uhr)?',  # German: ab 18 Uhr, um 20:00
        r'(?:Einlass|Beginn|Start)[\s:]+\d{1,2}(?::\d{2})?\s*(?:Uhr)?',  # Einlass: 19:00
        r'\d{1,2}(?::\d{2})?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:Uhr)?',  # Time ranges: 18-22 Uhr
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        times.extend(matches)
    
    return times


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of URLs found
    """
    url_pattern = r'https?://[^\s<>"\']+'
    return re.findall(url_pattern, text)


def extract_prices(text: str) -> List[str]:
    """Extract price information from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of price strings found
    """
    prices = []
    
    patterns = [
        r'\d+[,.]?\d*\s*€',  # 10€, 10,50€
        r'€\s*\d+[,.]?\d*',  # € 10, € 10.50
        r'\d+[,.]?\d*\s*EUR',  # 10 EUR
        r'(?:Eintritt|VVK|AK|Vorverkauf|Abendkasse)[\s:]+(?:frei|kostenlos|\d+[,.]?\d*\s*€?)',
        r'(?:free|kostenlos|Eintritt frei)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        prices.extend(matches)
    
    return prices


def extract_event_keywords(text: str) -> Dict[str, List[str]]:
    """Extract event-related keywords from text.
    
    Identifies common event terms like venue types, music genres, etc.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with categorized keywords found
    """
    keywords = {
        'event_type': [],
        'music_genre': [],
        'venue_hints': [],
        'ticket_info': []
    }
    
    text_lower = text.lower()
    
    # Event types (German + English)
    event_types = [
        'konzert', 'concert', 'live', 'party', 'festival', 'ausstellung',
        'exhibition', 'vernissage', 'lesung', 'reading', 'workshop',
        'theater', 'comedy', 'kabarett', 'open air', 'openair',
        'release', 'premiere', 'afterparty', 'after party'
    ]
    for term in event_types:
        if term in text_lower:
            keywords['event_type'].append(term)
    
    # Music genres
    genres = [
        'punk', 'rock', 'metal', 'jazz', 'blues', 'hip hop', 'hiphop',
        'electronic', 'techno', 'house', 'indie', 'folk', 'acoustic',
        'klassik', 'classical', 'pop', 'reggae', 'ska', 'hardcore',
        'alternative', 'singer-songwriter', 'ambient', 'experimental'
    ]
    for genre in genres:
        if genre in text_lower:
            keywords['music_genre'].append(genre)
    
    # Venue hints
    venues = [
        'club', 'bar', 'kneipe', 'galerie', 'gallery', 'theater',
        'halle', 'hall', 'saal', 'bühne', 'stage', 'keller', 'basement',
        'biergarten', 'beer garden', 'café', 'cafe', 'restaurant'
    ]
    for venue in venues:
        if venue in text_lower:
            keywords['venue_hints'].append(venue)
    
    # Ticket info patterns
    ticket_patterns = [
        r'vvk', r'ak', r'vorverkauf', r'abendkasse', r'tickets',
        r'eintritt', r'entry', r'admission', r'reservierung', r'reservation'
    ]
    for pattern in ticket_patterns:
        if re.search(pattern, text_lower):
            keywords['ticket_info'].append(pattern)
    
    return keywords


def extract_event_data_from_image(image_source: Union[str, bytes, BytesIO],
                                   languages: List[str] = None) -> Dict[str, Any]:
    """Extract comprehensive event data from an image.
    
    This is the main function for extracting event information from flyers.
    It combines OCR text extraction with pattern matching for dates, times,
    prices, and event keywords.
    
    Args:
        image_source: Path to image file, bytes data, or BytesIO object
        languages: List of language codes (default: ['eng', 'deu'])
        
    Returns:
        Dictionary with extracted event data:
        - text: Full OCR text
        - dates: List of date strings
        - times: List of time strings
        - urls: List of URLs
        - prices: List of price strings
        - keywords: Event-related keywords
        - confidence: Estimated confidence score
    """
    result = {
        'text': None,
        'dates': [],
        'times': [],
        'urls': [],
        'prices': [],
        'keywords': {},
        'confidence': 0.0
    }
    
    # Extract text
    text = extract_text(image_source, languages or ['eng', 'deu'])
    if not text:
        return result
    
    result['text'] = text
    
    # Extract structured data
    result['dates'] = extract_dates(text)
    result['times'] = extract_times(text)
    result['urls'] = extract_urls(text)
    result['prices'] = extract_prices(text)
    result['keywords'] = extract_event_keywords(text)
    
    # Calculate confidence score based on found data
    confidence = 0.0
    if result['dates']:
        confidence += 0.3
    if result['times']:
        confidence += 0.2
    if result['keywords'].get('event_type'):
        confidence += 0.2
    if result['prices']:
        confidence += 0.1
    if len(text) > 50:  # Reasonable amount of text
        confidence += 0.2
    
    result['confidence'] = min(confidence, 1.0)
    
    return result
