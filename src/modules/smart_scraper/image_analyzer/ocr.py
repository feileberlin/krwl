"""OCR text extraction from images."""

from typing import Dict, Any, Optional, List
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


def extract_text(image_path: str, languages: List[str] = None) -> Optional[str]:
    """Extract text from image using OCR.
    
    Args:
        image_path: Path to image file
        languages: List of language codes (e.g., ['eng', 'deu'])
        
    Returns:
        Extracted text or None
    """
    if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
        return None
    
    try:
        img = Image.open(image_path)
        
        # Configure languages
        lang = '+'.join(languages) if languages else 'eng'
        
        # Extract text
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"  OCR error: {e}")
        return None


def extract_dates(text: str) -> List[str]:
    """Extract date/time patterns from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of date strings found
    """
    dates = []
    
    # Date patterns
    patterns = [
        r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # DD Month YYYY
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return dates


def extract_times(text: str) -> List[str]:
    """Extract time patterns from text.
    
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
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)
