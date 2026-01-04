# Workflow Adaptation Testing Guide

This document demonstrates how the unified workflow automatically adapts to changes in scraper.py and config.json.

## Test 1: Baseline - Current Configuration

### Current State
```bash
$ python3 src/event_manager.py scraper-info
```

**Expected Output:**
- 12 enabled sources
- 4 supported source types (rss, html, api, facebook)
- Schedule: 04:00, 16:00 Europe/Berlin
- SmartScraper available: true

### Workflow Behavior
- ✅ Scraping runs on schedule (04:00 and 16:00)
- ✅ All 12 sources are scraped
- ✅ Deploy happens if new events found

---

## Test 2: Disable All Sources

### Change Configuration
Edit `config.json`:
```json
{
  "scraping": {
    "sources": [
      {
        "name": "Wochenmarkt Hof",
        "enabled": false,  // Change from true
        ...
      }
      // Disable all sources
    ]
  }
}
```

### Expected Introspection Output
```bash
$ python3 src/event_manager.py scraper-info
```
```json
{
  "enabled_sources": [],
  "source_count": 0
}
```

### Workflow Adaptation
- ✅ `discover-capabilities` detects 0 sources
- ✅ `scrape-events` job is **SKIPPED** (condition: `source_count != '0'`)
- ✅ No unnecessary scraping attempts
- ✅ Workflow completes successfully (graceful degradation)

**Test Command:**
```bash
# In workflow YAML, job scrape-events has condition:
# if: needs.discover-capabilities.outputs.source_count != '0'
```

---

## Test 3: Add New Source Type

### Add iCal Scraper Method
Edit `src/modules/scraper.py`:

```python
def _scrape_ical(self, source):
    """Scrape events from iCal feed"""
    import icalendar
    response = self._make_request(source['url'])
    cal = icalendar.Calendar.from_ical(response.content)
    events = []
    for component in cal.walk('VEVENT'):
        event = {
            'title': str(component.get('summary')),
            'start_time': component.get('dtstart').dt.isoformat(),
            # ... more fields
        }
        events.append(event)
    return events

def get_supported_source_types(self):
    return ['rss', 'html', 'api', 'facebook', 'ical']  # Add 'ical'
```

### Add iCal Source to Config
Edit `config.json`:
```json
{
  "scraping": {
    "sources": [
      {
        "name": "Calendar Events",
        "url": "https://example.com/events.ics",
        "type": "ical",
        "enabled": true
      }
    ]
  }
}
```

### Expected Introspection Output
```bash
$ python3 src/event_manager.py scraper-info
```
```json
{
  "supported_source_types": [
    "rss", "html", "api", "facebook", "ical"
  ],
  "enabled_sources": [
    {
      "name": "Calendar Events",
      "type": "ical",
      "url": "https://example.com/events.ics"
    }
  ]
}
```

### Workflow Adaptation
- ✅ `discover-capabilities` detects new 'ical' type
- ✅ Workflow runs scraping including new iCal source
- ✅ **NO WORKFLOW FILE CHANGES NEEDED**

---

## Test 4: Change Scraping Schedule

### Modify Schedule
Edit `config.json`:
```json
{
  "scraping": {
    "schedule": {
      "timezone": "Europe/Berlin",
      "times": ["06:00", "12:00", "18:00"]  // Change from ["04:00", "16:00"]
    }
  }
}
```

### Expected Introspection Output
```bash
$ python3 src/event_manager.py scraper-info
```
```json
{
  "schedule": {
    "timezone": "Europe/Berlin",
    "times": ["06:00", "12:00", "18:00"]
  }
}
```

### Workflow Adaptation
- ✅ `discover-capabilities` reads new schedule
- ⚠️ **Note**: GitHub Actions cron is hardcoded in workflow YAML
- 📝 **Manual Step Required**: Update cron schedule in workflow file
- 💡 **Future Enhancement**: Generate workflow file dynamically

**Current Limitation:**
The cron schedule in the workflow YAML must be manually updated to match config.json. This is a GitHub Actions limitation (cron cannot be dynamic).

**Workaround:**
1. Update `config.json` schedule
2. Update `.github/workflows/website-maintenance.yml` cron times
3. Commit both files together

---

## Test 5: Scraping Libraries Not Installed

### Simulate Missing Libraries
```bash
$ pip uninstall beautifulsoup4 requests
```

### Expected Introspection Output
```bash
$ python3 src/event_manager.py scraper-info
```
```json
{
  "scraping_libraries_installed": false
}
```

### Workflow Adaptation
- ✅ `discover-capabilities` detects libraries not installed
- ✅ `scrape-events` job is **SKIPPED** (condition: `scraping_enabled == 'true'`)
- ✅ Workflow doesn't fail, just skips scraping
- ✅ Deployment jobs still run if triggered manually

---

## Test 6: Manual Workflow Triggers

### Test "info" Task
GitHub Actions → Website Maintenance → Run workflow → Select task: `info`

**Expected Behavior:**
- ✅ `discover-capabilities` runs
- ✅ `show-info` job runs and displays full capabilities
- ✅ All other jobs are skipped
- ✅ No deployment

### Test "scrape-only" Task
GitHub Actions → Website Maintenance → Run workflow → Select task: `scrape-only`

**Expected Behavior:**
- ✅ `discover-capabilities` runs
- ✅ `scrape-events` runs
- ✅ Events are scraped and committed
- ✅ Deployment jobs are **SKIPPED**

### Test "force-deploy" Task
GitHub Actions → Website Maintenance → Run workflow → Select task: `force-deploy`

**Expected Behavior:**
- ✅ `discover-capabilities` runs
- ✅ `full-rebuild` runs (even if no changes)
- ✅ `deploy` runs
- ✅ Site is rebuilt and deployed

---

## Test 7: Push-Triggered Deployment

### Test Event Data Change
```bash
$ git add assets/json/events.json
$ git commit -m "Update events"
$ git push
```

**Expected Workflow Behavior:**
- ✅ Trigger: `on.push.paths` matches `events.json`
- ✅ `update-events` job runs (fast path)
- ✅ `deploy` job runs
- ✅ No full rebuild needed

### Test Scraper Change
```bash
$ git add src/modules/scraper.py
$ git commit -m "Update scraper"
$ git push
```

**Expected Workflow Behavior:**
- ✅ Trigger: `on.push.paths` matches `scraper.py`
- ✅ `full-rebuild` job runs (comprehensive path)
- ✅ `deploy` job runs
- ✅ Complete site regeneration

### Test Config Change
```bash
$ git add config.json
$ git commit -m "Update config"
$ git push
```

**Expected Workflow Behavior:**
- ✅ Trigger: `on.push.paths` matches `config.json`
- ✅ `full-rebuild` job runs
- ✅ `deploy` job runs
- ✅ Site rebuilt with new configuration

---

## Test 8: Concurrent Run Protection

### Test Concurrent Scraping
Trigger workflow manually while scheduled run is in progress.

**Expected Behavior:**
- ✅ Second run waits for first to complete
- ✅ Concurrency group: `website-maintenance`
- ✅ `cancel-in-progress: false` prevents cancellation
- ✅ Both runs complete successfully (no conflicts)

---

## Test 9: Error Handling

### Test Failed Source
Add a source with invalid URL:
```json
{
  "name": "Invalid Source",
  "url": "https://invalid-domain-that-does-not-exist.com",
  "type": "html",
  "enabled": true
}
```

**Expected Behavior:**
- ✅ Scraper handles error gracefully
- ✅ Failed source is logged in scraper
- ✅ Other sources continue scraping
- ✅ Workflow completes successfully
- ⚠️ Summary shows warning about failed source

### Test Git Push Conflict
Simulate concurrent commits to main branch.

**Expected Behavior:**
- ✅ Git pull --rebase handles merge
- ✅ If rebase fails, workflow stops with clear error
- ✅ Manual intervention message shown
- ❌ Workflow fails (expected - requires manual resolution)

---

## Test 10: Capability Display

### View in Workflow Summary
Run workflow with `info` task.

**Expected Output in Summary:**
```markdown
## 🔍 Complete Scraper Capabilities

```json
{
  "supported_source_types": [...],
  "enabled_sources": [...],
  "schedule": {...},
  "smart_scraper_available": true,
  "scraping_libraries_installed": true,
  "methods": {...}
}
```

### Key Information
- Enabled Sources: 12
- Scraping Libraries: true
- Schedule: 04:00, 16:00 (Europe/Berlin)
```

---

## Summary: Adaptation Scenarios

| Scenario | Detects Automatically | Adapts Workflow | Requires Manual Update |
|----------|----------------------|-----------------|------------------------|
| Add/remove sources | ✅ Yes | ✅ Yes | ❌ No |
| Change source types | ✅ Yes | ✅ Yes | ❌ No |
| Add new scraper methods | ✅ Yes | ✅ Yes | ❌ No |
| Change schedule times | ✅ Yes (in summary) | ⚠️ Partial | ⚠️ Yes (cron in YAML) |
| Disable all sources | ✅ Yes | ✅ Yes (skips scraping) | ❌ No |
| Missing libraries | ✅ Yes | ✅ Yes (skips scraping) | ❌ No |
| Config changes | ✅ Yes | ✅ Yes (triggers rebuild) | ❌ No |
| Scraper changes | ✅ Yes | ✅ Yes (triggers rebuild) | ❌ No |

---

## Running Tests Locally

### Test Introspection
```bash
# Get current capabilities
python3 src/event_manager.py scraper-info

# Pretty print
python3 src/event_manager.py scraper-info | python3 -m json.tool

# Extract specific field
python3 src/event_manager.py scraper-info | jq '.source_count'
```

### Test Workflow Syntax
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/website-maintenance.yml'))"

# Check job conditions
grep -A 5 "if:" .github/workflows/website-maintenance.yml
```

### Simulate Workflow Logic
```bash
# Get capabilities as workflow would
CAPABILITIES=$(python3 src/event_manager.py scraper-info)
SOURCE_COUNT=$(echo "$CAPABILITIES" | jq -r '.enabled_sources | length')
echo "Source count: $SOURCE_COUNT"

# Check condition
if [ "$SOURCE_COUNT" -ne "0" ]; then
  echo "✅ Scraping would run"
else
  echo "⚠️ Scraping would be skipped"
fi
```

---

## Continuous Testing

Add to your development workflow:

```bash
# Before committing scraper changes
python3 src/event_manager.py scraper-info

# Verify output is valid JSON
python3 src/event_manager.py scraper-info | python3 -m json.tool

# Check workflow syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/website-maintenance.yml'))"
```

---

## Future Enhancements

### Dynamic Cron Scheduling
Generate workflow file with correct cron times based on config.json:

```python
# scripts/generate_workflow.py
import json
import yaml
from datetime import datetime

config = json.load(open('config.json'))
schedule = config['scraping']['schedule']
times = schedule['times']
timezone = schedule['timezone']

# Convert times to UTC cron format
# Generate .github/workflows/website-maintenance.yml
```

### Health Monitoring
Track failed sources over time:

```python
# Add to scraper.py
def get_source_health_stats(self):
    """Return success/failure stats for each source"""
    return {
        'success_rate': 0.95,
        'failed_sources': ['Source A', 'Source B'],
        'last_successful_scrape': '2024-01-01T00:00:00Z'
    }
```

### A/B Testing
Deploy to preview environment first:

```yaml
# Add to workflow
deploy-preview:
  if: github.event.inputs.deploy_mode == 'preview'
  # Deploy to /preview/ path for testing
```
