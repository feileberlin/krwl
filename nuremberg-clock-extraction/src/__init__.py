"""
Nürnberger Uhr (Nuremberg Clock) - Subjective Time Calculator

Calculate subjective time based on the historical Nuremberg Clock system,
which uses "unequal hours" (temporale Stunden) based on sunrise and sunset.

Usage:
    from src.subjective_day import SubjectiveTime
    
    uhr = SubjectiveTime(lat=50.3167, lon=11.9167)  # Hof, Germany
    result = uhr.get_subjective_day()
    print(result['display'])  # "3. Stunde des Tages"
"""

from .subjective_day import SubjectiveTime, get_subjective_day, get_sunrise_sunset

__version__ = "1.0.0"
__all__ = ["SubjectiveTime", "get_subjective_day", "get_sunrise_sunset"]
