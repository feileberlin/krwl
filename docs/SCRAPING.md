# Event Scraping Guide

## Overview

The KRWL HOF event manager includes a comprehensive web scraping system that automatically collects events from configured sources. The scraper supports multiple formats and handles deduplication automatically.

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client for fetching web pages and APIs
- `beautifulsoup4` - HTML parsing and data extraction
- `lxml` - Fast HTML parser backend
- `feedparser` - RSS/Atom feed parsing

## Supported Source Types

### 1. RSS Feeds (`type: "rss"`)
Parses RSS/Atom feeds to extract events.

**Example configuration:**
```json
{
  "name": "Community Calendar Feed",
  "url": "https://example.com/events.rss",
  "type": "rss",
  "enabled": true
}
```

**What it extracts:**
- Title from `<title>`
- Description from `<description>` or `<summary>`
- Link from `<link>`
- Date from `<pubDate>` or `<updated>`

### 2. HTML Pages (`type: "html"`)
Scrapes event information from HTML pages using pattern matching.

**Example configuration:**
```json
{
  "name": "City Events Page",
  "url": "https://example.com/events",
  "type": "html",
  "enabled": true,
  "notes": "City community events"
}
```

**What it looks for:**
- Common selectors: `.event`, `.veranstaltung`, `[class*="event"]`, `article`
- Title from `<h1>`, `<h2>`, `<h3>`, or `<a>`
- Description from `<p>`, `<div>`, `<span>`
- Links from `<a href>`
- Dates using patterns: `DD.MM.YYYY`, `YYYY-MM-DD`

### 3. JSON APIs (`type: "api"`)
Fetches and parses JSON API responses.

**Example configuration:**
```json
{
  "name": "Event API",
  "url": "https://api.example.com/events",
  "type": "api",
  "enabled": true
}
```

**Expected API format:**
```json
[
  {
    "title": "Event Name",
    "description": "Event description",
    "date": "2024-12-15T18:00:00",
    "location": {
      "name": "Venue Name",
      "lat": 50.3167,
      "lon": 11.9167
    },
    "url": "https://example.com/event/123"
  }
]
```

### 4. Facebook Pages (`type: "facebook"`)
**Note:** Facebook scraping requires authentication and is not fully implemented.

**Alternatives:**
- Use Facebook Graph API with proper credentials
- Manually create events from Facebook pages
- Use RSS feeds if available

## Configuration

Edit `config/config.json` to add or modify sources:

```json
{
  "scraping": {
    "sources": [
      {
        "name": "Source Name",
        "url": "https://example.com/events",
        "type": "html",
        "enabled": true,
        "notes": "Description of source"
      }
    ],
    "interval_minutes": 60
  }
}
```

## Usage

### Manual Scraping

Run the scraper manually:

```bash
python3 src/main.py scrape
```

This will:
1. Load configuration from `config/config.json`
2. Scrape all enabled sources
3. Save events to `static/pending_events.json`
4. Show summary of scraped events

### Automated Scraping

Set up a cron job to run scraping automatically:

```bash
# Every hour
0 * * * * cd /path/to/krwl-hof && python3 src/main.py scrape

# Every 6 hours
0 */6 * * * cd /path/to/krwl-hof && python3 src/main.py scrape

# Daily at 6am
0 6 * * * cd /path/to/krwl-hof && python3 src/main.py scrape
```

### GitHub Actions Workflow

Create `.github/workflows/scrape-events.yml`:

```yaml
name: Scrape Events

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run scraper
        run: python3 src/main.py scrape
      
      - name: Commit new events
        run: |
          git config user.name "Event Scraper Bot"
          git config user.email "bot@example.com"
          git add static/pending_events.json
          git add backups/
          git commit -m "Auto-scraped events" || exit 0
          git push
```

## Event Processing Workflow

1. **Scraping** → Events saved to `static/pending_events.json`
2. **Review** → Use TUI or GitHub UI workflow to review pending events
3. **Approval** → Approve events to move them to `static/events.json`
4. **Backup** → Each approved event backed up to `backups/events/`
5. **Publishing** → Approved events appear on the map (GitHub Pages serves `static/` directly)

## Deduplication

The scraper automatically prevents duplicates by checking:
- Event title
- Start time

Events with matching title and start time are not added again.

## Data Format

Scraped events are stored in this format:

```json
{
  "id": "html_source_name_12345",
  "title": "Event Title",
  "description": "Event description (max 500 chars)",
  "location": {
    "name": "Venue Name",
    "lat": 50.3167,
    "lon": 11.9167
  },
  "start_time": "2024-12-15T18:00:00",
  "end_time": null,
  "url": "https://example.com/event",
  "source": "Source Name",
  "scraped_at": "2024-12-09T12:00:00",
  "status": "pending"
}
```

## Troubleshooting

### Scraper returns no events

1. Check source is enabled: `"enabled": true`
2. Verify URL is accessible
3. Run with verbose output: `python3 src/main.py scrape --verbose`
4. Check HTML structure matches expected patterns

### Dependencies not installed

```bash
pip install -r requirements.txt
```

### Import errors

Make sure you're running from the repository root:

```bash
cd /path/to/krwl-hof
python3 src/main.py scrape
```

### Rate limiting / blocking

Some sites may block automated requests. Solutions:
- Add delays between requests
- Use different User-Agent headers
- Contact site owner for API access
- Use RSS feeds if available

## Adding Custom Scrapers

To add a scraper for a specific site:

1. Edit `src/modules/scraper.py`
2. Add a new method like `_scrape_custom_site()`
3. Parse the site's specific structure
4. Return list of event dictionaries

Example:

```python
def _scrape_custom_site(self, source):
    """Scrape from custom site"""
    events = []
    response = self.session.get(source['url'])
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Custom parsing logic
    for item in soup.select('.custom-event-class'):
        event = {
            'id': f"custom_{hash(item.text)}",
            'title': item.select_one('h2').text,
            'description': item.select_one('.desc').text,
            # ... more fields
        }
        events.append(event)
    
    return events
```

## Testing

Run scraper tests:

```bash
python3 tests/test_scraper.py --verbose
```

This tests:
- Manual event creation
- Deduplication logic
- Data validation
- Error handling

## Best Practices

1. **Start with RSS** - Easiest to parse reliably
2. **Test thoroughly** - Verify scraped data is accurate
3. **Respect robots.txt** - Check site's scraping policy
4. **Add delays** - Don't overwhelm servers
5. **Monitor errors** - Check logs regularly
6. **Update selectors** - Sites change, scraper may need updates
7. **Manual review** - Always review scraped events before publishing

## Example Sources

See `config/config.json` for real examples:
- City event pages (HTML)
- Cultural centers (HTML)
- Facebook pages (manual)
- Local newspapers (HTML)
- Educational institutions (HTML)

## Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Feedparser Documentation](https://feedparser.readthedocs.io/)
- [RSS Specification](https://www.rssboard.org/rss-specification)
