# Nürnberger Uhr (Nuremberg Clock)

🕐 **Subjective Time Calculator** - Historical "unequal hours" timekeeping system

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

The **Nürnberger Uhr** (Nuremberg Clock) was a medieval timekeeping system used in Nuremberg and other Central European cities. Unlike modern equal hours, it divides:

- **Day hours**: Sunrise to sunset → 12 equal parts
- **Night hours**: Sunset to sunrise → 12 equal parts

This means hour lengths vary seasonally:
- **Winter**: Day hours ~45 min, night hours ~75 min
- **Summer**: Day hours ~75 min, night hours ~45 min
- **Equinox**: Both ~60 min

## Features

- 🐍 **Python API Server** - Full-featured HTTP server with multiple output formats
- 🌐 **JavaScript Client** - Browser-based calculator (GitHub Pages compatible)
- 📊 **Sunrise/Sunset Calculations** - Accurate solar position algorithms
- 🌍 **Any Location** - Works worldwide (handles polar regions)
- 📱 **Smartwatch Format** - Compact display for wearables

## Quick Start

### Python

```bash
# Run as API server
python3 src/subjective_day.py --serve --port 8080

# API usage (wttr.in style)
curl "http://localhost:8080/Nuremberg"
curl "http://localhost:8080/50.3,11.9"
curl "http://localhost:8080/Berlin?format=json"
```

### JavaScript

```html
<script src="src/subjective-day.js"></script>
<script>
  const calc = new SubjectiveDay(50.3167, 11.9167);  // Nuremberg
  const result = calc.getSubjectiveTime();
  console.log(result.display_en);  // "3rd hour of day (52.4 min/hr)"
</script>
```

### Python Module

```python
from src.subjective_day import SubjectiveTime

uhr = SubjectiveTime(lat=50.3167, lon=11.9167)
result = uhr.get_subjective_day()
print(result['display'])  # "3. Stunde des Tages"
```

## API Endpoints (wttr.in style)

| Endpoint | Description |
|----------|-------------|
| `GET /` | Default location (Hof) |
| `GET /Berlin` | City name lookup |
| `GET /52.52,13.40` | Coordinates (lat,lon) |
| `GET /munich?format=j` | JSON output |
| `GET /hof?format=table` | Hour table for the day |
| `GET /:help` | Help page |
| `GET /:about` | Historical information |
| `GET /:nocturnal` | Digital star clock |

### Output Formats

Add `?format=` parameter:
- `plain` (default) - Human readable ASCII art
- `json` or `j` - JSON format
- `table` or `t` - Full day hour table
- `1` or `oneline` - Single line (for scripts)
- `watch` or `w` - Smartwatch format

## Project Structure

```
nuremberg-clock/
├── src/
│   ├── subjective_day.py     # Python implementation + API server
│   └── subjective-day.js     # JavaScript implementation
├── tests/
│   └── test_subjective_day.py  # Test suite
├── examples/
│   └── subjective-day-demo.html  # Interactive demo
├── docs/
│   └── historical-background.md  # Historical context
├── README.md
├── requirements.txt
└── LICENSE
```

## Installation

### Python

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/nuremberg-clock.git
cd nuremberg-clock

# No dependencies required! Uses only Python standard library
python3 src/subjective_day.py --serve
```

### Static Hosting (GitHub Pages)

1. Copy `src/subjective-day.js` and `examples/subjective-day-demo.html` to your site
2. Update script path in HTML
3. Deploy to GitHub Pages, Netlify, Vercel, etc.

## Running Tests

```bash
cd tests
python3 test_subjective_day.py -v
```

## Historical Background

From Friedrich Nicolai (1783):

> "Zu den Gewohnheiten, welche bloß beybehalten werden, weil sie alt sind,
> gehört auch die sogenannte große Uhr. Man nennt in Nürnberg die sonst
> gewöhnliche Art von 1 bis 12 zu schlagen die kleine Uhr."

Translation:
> "Among customs preserved merely because they are old, is the so-called
> große Uhr (great clock). In Nuremberg, the usual way of striking 1 to 12
> is called the kleine Uhr (small clock)."

### The System

- **Große Uhr**: The Nuremberg seasonal hour system (8-16 variable hour counts)
- **Kleine Uhr**: The standard 12-hour system we use today
- **Wendetage**: 16 adjustment days per year to align hours with sunrise/sunset
- **Garaus**: Horn signal for closing city gates at sunset
- **Türmer**: Tower watchmen who rang bells using sundials, water clocks, and stars

## References

- [Nürnberger Uhr - Wikipedia (DE)](https://de.wikipedia.org/wiki/Nürnberger_Uhr)
- [Nuremberg Info](https://nuernberginfos.de/nuernberg-mix/nuernberger-uhr.php)
- [Chemie-Schule](https://www.chemie-schule.de/KnowHow/Nürnberger_Uhr)
- Friedrich Nicolai: "Beschreibung einer Reise durch Deutschland" (1783)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Extracted from [KRWL HOF Community Events](https://github.com/feileberlin/krwl-hof)*
