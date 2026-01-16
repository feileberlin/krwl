"""Smart scraper source modules."""

# Web sources
from . import web

# Social sources (optional)
try:
    from . import social
except ImportError:
    social = None

# Custom sources
try:
    from . import frankenpost
except ImportError:
    frankenpost = None

__all__ = ['web', 'social', 'frankenpost']
