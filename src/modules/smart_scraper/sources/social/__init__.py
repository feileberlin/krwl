"""Social media source scrapers."""

try:
    from .facebook import FacebookSource
except ImportError:
    FacebookSource = None

try:
    from .instagram import InstagramSource
except ImportError:
    InstagramSource = None

try:
    from .tiktok import TikTokSource
except ImportError:
    TikTokSource = None

try:
    from .x_twitter import XTwitterSource
except ImportError:
    XTwitterSource = None

try:
    from .telegram import TelegramSource
except ImportError:
    TelegramSource = None

try:
    from .whatsapp import WhatsAppSource
except ImportError:
    WhatsAppSource = None

__all__ = [
    'FacebookSource',
    'InstagramSource', 
    'TikTokSource',
    'XTwitterSource',
    'TelegramSource',
    'WhatsAppSource'
]
