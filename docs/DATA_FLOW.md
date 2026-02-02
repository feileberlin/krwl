# KRWL> - Data Flow & Dependencies

## 🚨 CRITICAL: Events Won't Display Without This

**If no events appear on the map, check this FIRST:**

```bash
# Does public/index.html exist?
ls -lh public/index.html

# If missing or outdated, run:
python3 src/event_manager.py generate
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. EVENT SOURCES                                                 │
├─────────────────────────────────────────────────────────────────┤
│  • RSS Feeds (configured in config.json)                        │
│  • HTML scrapers                                                 │
│  • API endpoints                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SCRAPING (python3 src/event_manager.py scrape)              │
├─────────────────────────────────────────────────────────────────┤
│  • src/modules/scraper.py                                       │
│  • Fetches events from sources                                  │
│  • Validates & normalizes data                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PENDING QUEUE                                                 │
├─────────────────────────────────────────────────────────────────┤
│  File: assets/json/pending_events.json                          │
│  • Events awaiting editorial review                             │
│  • NOT visible on map yet                                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. EDITORIAL REVIEW                                              │
├─────────────────────────────────────────────────────────────────┤
│  Commands:                                                       │
│  • python3 src/event_manager.py review (TUI)                    │
│  • python3 src/event_manager.py publish EVENT_ID                │
│  • python3 src/event_manager.py reject EVENT_ID                 │
│                                                                  │
│  Module: src/modules/editor.py                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. PUBLISHED EVENTS                                              │
├─────────────────────────────────────────────────────────────────┤
│  File: assets/json/events.json                                  │
│  • 150 events currently                                         │
│  • Approved & ready for display                                 │
│  • But STILL NOT visible on map!                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. ⚠️  CRITICAL STEP: GENERATE HTML ⚠️                          │
├─────────────────────────────────────────────────────────────────┤
│  Command: python3 src/event_manager.py generate                 │
│                                                                  │
│  What it does:                                                   │
│  • Loads events.json (150 events)                               │
│  • Loads CSS from assets/css/                                   │
│  • Loads JavaScript from assets/js/                             │
│  • Loads HTML templates from assets/html/                       │
│  • Embeds everything into single HTML file                      │
│  • Outputs: public/index.html (563 KB)                          │
│                                                                  │
│  Module: src/modules/site_generator.py                          │
│                                                                  │
│  ⚠️  WITHOUT THIS STEP, NO EVENTS WILL BE VISIBLE! ⚠️          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. PUBLIC HTML                                                   │
├─────────────────────────────────────────────────────────────────┤
│  File: public/index.html                                        │
│                                                                  │
│  Contains:                                                       │
│  • window.__INLINE_EVENTS_DATA__ = { "events": [...150...] }   │
│  • window.APP_CONFIG = { ... }                                  │
│  • Inlined CSS and JavaScript                                   │
│  • Self-contained, no external requests                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. BROWSER LOADS PAGE                                            │
├─────────────────────────────────────────────────────────────────┤
│  JavaScript execution:                                           │
│  1. EventsApp.init() runs                                       │
│  2. loadEvents() checks window.__INLINE_EVENTS_DATA__           │
│  3. Finds 150 events embedded in HTML                           │
│  4. Processes events with EventFilter                           │
│  5. MapManager creates Leaflet map                              │
│  6. Adds markers for each event                                 │
│                                                                  │
│  ✅ EVENTS NOW VISIBLE ON MAP!                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Common Issues & Solutions

### Issue 1: No events visible on map
**Symptom:** Map loads but shows no markers  
**Cause:** `public/index.html` missing or outdated  
**Solution:**
```bash
python3 src/event_manager.py generate
```

### Issue 2: Events in assets/json/events.json but not on map
**Symptom:** events.json has 150 events, map shows 0  
**Cause:** HTML not regenerated after events changed  
**Solution:**
```bash
# Fast update (recommended for event-only changes)
python3 src/event_manager.py update

# Full rebuild (for CSS/JS/template changes)
python3 src/event_manager.py generate
```

### Issue 3: New scraped events don't appear
**Symptom:** Scraping works, but events don't show  
**Cause:** Events are in pending queue, not published  
**Solution:**
```bash
# Review and approve events
python3 src/event_manager.py review

# Then regenerate HTML
python3 src/event_manager.py generate
```

## File Locations

| File | Purpose | Visible on Map? |
|------|---------|-----------------|
| `assets/json/pending_events.json` | Scraped, awaiting approval | ❌ NO |
| `assets/json/events.json` | Published events (150) | ❌ NO (until HTML generated) |
| `public/index.html` | Generated HTML with embedded events | ✅ YES |
| `assets/js/app.js` | Source JavaScript | ❌ (needs generation) |
| `assets/css/style.css` | Source CSS | ❌ (needs generation) |

## Deployment Checklist

When deploying to production:

- [ ] Scrape events: `python3 src/event_manager.py scrape`
- [ ] Review events: `python3 src/event_manager.py review`
- [ ] **CRITICAL**: Generate HTML: `python3 src/event_manager.py generate`
- [ ] Verify file exists: `ls -lh public/index.html`
- [ ] Commit and push: `git add public/ && git commit && git push`
- [ ] Deploy `public/` directory to web server

## Why This Architecture?

**Single-file HTML with embedded data:**
- ✅ No external API calls
- ✅ Fast page load (no AJAX)
- ✅ Works offline (PWA)
- ✅ Easy to deploy (just static files)
- ✅ No CORS issues

**Trade-off:**
- ❌ Must regenerate HTML when events change
- ❌ Large HTML file (563 KB with 150 events)
- ✅ But: Acceptable for community events scale

## Automated CI/CD

GitHub Actions automatically:
1. Runs on schedule or when events.json changes
2. Executes `python3 src/event_manager.py generate`
3. Commits updated `public/index.html`
4. Deploys to GitHub Pages

See: `.github/workflows/website-maintenance.yml`

## Key Modules

| Module | Responsibility |
|--------|----------------|
| `src/modules/scraper.py` | Fetch events from sources |
| `src/modules/editor.py` | Editorial workflow (approve/reject) |
| `src/modules/site_generator.py` | **Generate HTML** (most critical) |
| `src/modules/utils.py` | Config loading, environment detection |
| `assets/js/app.js` | Frontend event loading and display |

## Quick Reference

```bash
# One-liner to fix "no events visible":
python3 src/event_manager.py generate

# Full workflow (scrape → approve → display):
python3 src/event_manager.py scrape          # Get new events
python3 src/event_manager.py review          # Approve/reject
python3 src/event_manager.py generate        # Make them visible

# Fast event update (no full rebuild):
python3 src/event_manager.py update

# Verify setup:
ls -lh public/index.html                     # Should exist, >500 KB
grep -c "\"id\":" public/index.html          # Should show ~150+
```

## Remember

🚨 **Events in `assets/json/events.json` are NOT visible until you run `generate`!**  
🚨 **Always regenerate HTML after publishing new events!**  
🚨 **The `public/index.html` file is the single source of truth for the website!**
