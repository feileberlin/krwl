# KRWL HOF Community Events

A community events scraper and viewer with geolocation filtering. This system allows you to scrape community events, review and publish them through a Python TUI, and display them on an interactive fullscreen map showing only events until the next sunrise that are nearby to the user's location.

## Features

- 🔍 **Event Scraping**: Scrape events from RSS feeds, APIs, and HTML pages
- ✅ **Editor Workflow**: Review, edit, approve, or reject events before publishing
- 🗺️ **Interactive Map**: Fullscreen map interface with Leaflet.js
- 📍 **Geolocation Filtering**: Shows only events near the user's location
- 🌅 **Sunrise Filtering**: Displays events only until the next sunrise
- 📝 **JSON-based**: Plain JSON for configuration and data storage
- 🐍 **Python TUI**: Single modular Python terminal interface
- 🌐 **Static Site**: Generates static files for GitHub Pages deployment
- 🚀 **No Jekyll**: Includes `.nojekyll` for direct GitHub Pages hosting
- 🐛 **Debug Mode**: Development config with console logging for troubleshooting
- ⚡ **Performance**: Production config optimized for maximum speed

## Project Structure

```
krwl-hof/
├── .nojekyll              # GitHub Pages configuration
├── config/
│   └── config.json        # Application configuration
├── data/
│   ├── events.json        # Published events
│   └── pending_events.json # Events awaiting review
├── src/
│   ├── main.py           # Python TUI entry point
│   └── modules/
│       ├── __init__.py
│       ├── scraper.py    # Event scraping module
│       ├── editor.py     # Event editing/approval module
│       ├── generator.py  # Static site generator
│       └── utils.py      # Utility functions
└── static/               # Generated static site files
    ├── index.html
    ├── events.json
    ├── config.json
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Quick Start

### 1. Set Up the Environment

```bash
# Clone the repository
git clone https://github.com/feileberlin/krwl-hof.git
cd krwl-hof

# (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install optional dependencies if needed
# pip install -r requirements.txt
```

### 2. Run the Python TUI

```bash
cd src
python3 main.py
```

### 3. Using the TUI

The TUI provides the following options:

1. **Scrape New Events**: Fetch events from configured sources
2. **Review Pending Events**: Approve/reject/edit scraped events
3. **View Published Events**: See all approved events
4. **Generate Static Site**: Create static files for deployment
5. **Settings**: View current configuration
6. **Exit**: Close the application

### 4. Deploy to GitHub Pages

This project uses a **two-step deployment workflow** for safe releases:

#### Quick Deploy Guide

1. **Make changes** and push to `preview` branch → auto-deploys to `/preview/` with debug mode
2. **Test thoroughly** at `yourdomain.com/preview/` (debug logs in console)
3. **Run "Promote Preview" workflow** → creates PR from `preview` to `main`
4. **Merge PR** → deploys to production with maximum performance

#### Configuration Files

- **`config.prod.json`**: Production (fast, no debugging, caching enabled)
- **`config.dev.json`**: Preview/Development (debug logs, caching disabled)

#### Full Documentation

See [.github/DEPLOYMENT.md](.github/DEPLOYMENT.md) for complete deployment guide including:
- Workflow details
- Debug mode features
- Local testing
- Troubleshooting
- Security notes

## Configuration

The system uses different configs for different environments:

### Development/Preview (`config.dev.json`)

```json
{
  "app": {
    "name": "KRWL HOF Community Events [PREVIEW]"
  },
  "debug": true,
  "performance": {
    "cache_enabled": false,
    "prefetch_events": false
  }
}
```

### Production (`config.prod.json`)

```json
{
  "app": {
    "name": "KRWL HOF Community Events"
  },
  "debug": false,
  "performance": {
    "cache_enabled": true,
    "prefetch_events": true
  }
}
```

### Base Config Structure

Edit config files to customize:

```json
{
  "app": {
    "name": "KRWL HOF Community Events"
  },
  "debug": false,
  "performance": {
    "cache_enabled": true,
    "prefetch_events": true
  },
  "scraping": {
    "sources": [
      {
        "name": "example_source",
        "url": "https://example.com/events",
        "type": "rss",
        "enabled": false
      }
    ]
  },
  "filtering": {
    "max_distance_km": 5.0,
    "show_until": "next_sunrise"
  },
  "map": {
    "default_center": {
      "lat": 52.52,
      "lon": 13.405
    },
    "default_zoom": 13
  }
}
```

## Event Data Format

Events are stored in JSON with the following structure:

```json
{
  "events": [
    {
      "id": "unique_id",
      "title": "Event Title",
      "description": "Event description",
      "location": {
        "name": "Venue Name",
        "lat": 52.52,
        "lon": 13.405
      },
      "start_time": "2024-01-01T18:00:00",
      "end_time": "2024-01-01T22:00:00",
      "url": "https://example.com/event",
      "source": "manual",
      "status": "published"
    }
  ]
}
```

## Features in Detail

### Geolocation Filtering

The web interface automatically:
1. Requests the user's location
2. Calculates distance to each event
3. Filters events beyond the configured `max_distance_km`
4. Displays remaining distance for each event

### Sunrise Filtering

Events are filtered to show only those occurring before the next sunrise:
- If current time is before 6 AM, shows events until 6 AM today
- If current time is after 6 AM, shows events until 6 AM tomorrow
- Can be enhanced with proper solar calculation libraries

### Editor Workflow

The TUI provides a complete workflow for event curation:
1. **Scrape**: Events are collected and added to pending queue
2. **Review**: Editor reviews each event individually
3. **Actions**: Approve (publish), Edit (modify), Reject (delete), or Skip
4. **Publish**: Approved events are moved to published list

### Static Site Generation

The generator creates:
- **index.html**: Full-featured single-page application
- **style.css**: Modern, responsive dark theme
- **app.js**: Vanilla JavaScript with no framework dependencies
- **Data files**: Copies of events.json and config.json

### Map Interface

Features:
- Fullscreen Leaflet.js map
- User location marker (blue)
- Event markers (green)
- Click markers or event cards to view details
- Responsive design for mobile devices
- Dark theme with modern styling

## Extending the System

### Adding New Scraping Sources

1. Edit `config/config.json` and add a new source:

```json
{
  "name": "my_source",
  "url": "https://example.com/events.rss",
  "type": "rss",
  "enabled": true
}
```

2. Implement scraping logic in `src/modules/scraper.py`

### Customizing the Interface

- **HTML**: Edit template in `src/modules/generator.py` → `_generate_html()`
- **CSS**: Edit styles in `src/modules/generator.py` → `_generate_css()`
- **JavaScript**: Edit app logic in `src/modules/generator.py` → `_generate_js()`

### Adding New TUI Features

Add new menu options in `src/main.py` by:
1. Adding menu item in `show_menu()`
2. Creating handler method
3. Adding case in `run()` method

## Development

### Code Structure

The codebase is modular and expandable:

- **main.py**: Entry point and TUI orchestration
- **scraper.py**: Event scraping from various sources
- **editor.py**: Event review and approval workflow
- **generator.py**: Static site generation
- **utils.py**: Shared utility functions

### Best Practices

- Use JSON for all data storage
- Keep modules independent and reusable
- Follow the single responsibility principle
- Maintain backward compatibility with data formats

## Debug Mode

### Enabling Debug Mode

Set `"debug": true` in config file (automatically enabled in `config.dev.json`):

```json
{
  "debug": true
}
```

### Debug Features

When debug mode is enabled:
- **Browser title** shows `[DEBUG MODE]`
- **Console logs** prefixed with `[KRWL Debug]` show:
  - Config loading
  - Event loading and count
  - Filter operations and reasons
  - Distance calculations
- **Performance** optimizations disabled for testing

### Viewing Debug Logs

1. Open browser console (F12)
2. Look for `[KRWL Debug]` messages
3. Filter by "KRWL" to see only app logs

## Troubleshooting

### Location not working

The browser needs HTTPS or localhost to access geolocation. When deploying to GitHub Pages, this is handled automatically.

### No events showing

1. **Enable debug mode** to see filtering reasons
2. Check if events exist in `data/events.json`
3. Verify events are within the time filter (before next sunrise)
4. Check if events are within distance filter (if location is enabled)
5. Review console logs for `[KRWL Debug]` filter messages

### Static site not updating

Run "Generate Static Site" from the TUI menu after making any changes to events or configuration.

### Preview site debugging

1. Visit `/preview/` path on your GitHub Pages site
2. Check that title shows `[PREVIEW]`
3. Open console - debug logs should appear
4. See [.github/DEPLOYMENT.md](.github/DEPLOYMENT.md) for more help

### Production site too slow

Production uses `config.prod.json` which is optimized for speed:
- Caching enabled
- No debug logging
- Prefetching enabled

If it's still slow, check:
1. Network tab for large assets
2. Events.json file size
3. Browser console for errors (should be none)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Roadmap

- [ ] RSS feed scraping implementation
- [ ] API integration for event sources
- [ ] HTML scraping with BeautifulSoup
- [ ] Accurate sunrise/sunset calculation using astral
- [ ] Database backend option
- [ ] Web-based editor interface
- [ ] Event categories and filtering
- [ ] User favorites and notifications
- [ ] Export to calendar formats (iCal, etc.)

## Credits

- Map tiles from [OpenStreetMap](https://www.openstreetmap.org/)
- Map library: [Leaflet.js](https://leafletjs.com/)
- Built with vanilla JavaScript and Python