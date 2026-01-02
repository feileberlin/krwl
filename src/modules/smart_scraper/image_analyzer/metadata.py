"""EXIF and metadata extraction from images."""

from typing import Dict, Any, Optional
from datetime import datetime

try:
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def extract_metadata(image_path: str) -> Dict[str, Any]:
    """Extract EXIF and metadata from image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with metadata
    """
    metadata = {}
    
    # Try EXIF extraction
    if EXIF_AVAILABLE:
        _extract_exif_data(image_path, metadata)
    
    # Get image dimensions with PIL
    if PIL_AVAILABLE:
        _extract_pil_data(image_path, metadata)
    
    return metadata


def _extract_exif_data(image_path: str, metadata: Dict[str, Any]) -> None:
    """Extract EXIF data from image.
    
    Args:
        image_path: Path to image file
        metadata: Dictionary to update with extracted data
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            
            # Extract GPS coordinates
            _extract_gps_coordinates(tags, metadata)
            
            # Extract date/time
            _extract_datetime(tags, metadata)
    except Exception as e:
        print(f"  EXIF extraction error: {e}")


def _extract_gps_coordinates(tags: Dict, metadata: Dict[str, Any]) -> None:
    """Extract GPS coordinates from EXIF tags.
    
    Args:
        tags: EXIF tags dictionary
        metadata: Dictionary to update with GPS data
    """
    if 'GPS GPSLatitude' not in tags or 'GPS GPSLongitude' not in tags:
        return
    
    lat = _convert_to_degrees(tags['GPS GPSLatitude'])
    lon = _convert_to_degrees(tags['GPS GPSLongitude'])
    
    # Handle N/S and E/W
    if 'GPS GPSLatitudeRef' in tags and tags['GPS GPSLatitudeRef'].values[0] == 'S':
        lat = -lat
    if 'GPS GPSLongitudeRef' in tags and tags['GPS GPSLongitudeRef'].values[0] == 'W':
        lon = -lon
    
    metadata['gps'] = {'lat': lat, 'lon': lon}


def _extract_datetime(tags: Dict, metadata: Dict[str, Any]) -> None:
    """Extract datetime from EXIF tags.
    
    Args:
        tags: EXIF tags dictionary
        metadata: Dictionary to update with datetime
    """
    if 'EXIF DateTimeOriginal' not in tags:
        return
    
    date_str = str(tags['EXIF DateTimeOriginal'])
    try:
        dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        metadata['datetime'] = dt.isoformat()
    except ValueError:
        pass


def _extract_pil_data(image_path: str, metadata: Dict[str, Any]) -> None:
    """Extract image dimensions using PIL.
    
    Args:
        image_path: Path to image file
        metadata: Dictionary to update with image dimensions
    """
    try:
        with Image.open(image_path) as img:
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['format'] = img.format
    except Exception as e:
        print(f"  PIL metadata error: {e}")


def _convert_to_degrees(value) -> float:
    """Convert GPS coordinates to degrees."""
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)
