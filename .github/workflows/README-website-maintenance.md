# Unified Website Maintenance Workflow

## Overview

The `website-maintenance.yml` workflow is a **wrapper that automatically adapts to changes in `event_scraper.py`** and configuration. It dynamically discovers scraper capabilities at runtime and adjusts its behavior accordingly.

## Key Features

### 🔄 **Automatic Adaptation**
- Introspects `event_scraper.py` at runtime to discover available methods
- Reads scraping configuration from `config.json` dynamically
- Adapts to changes in enabled sources without manual workflow updates
- Detects supported source types automatically

### 🎯 **Unified Tasks**
Combines all common website maintenance tasks into one workflow:
1. **Scraping** - Automated event scraping from configured sources
2. **Building** - Full site generation or fast event updates
3. **Deployment** - GitHub Pages deployment
4. **Introspection** - Show scraper capabilities

### 🕐 **Smart Scheduling**
- Schedule automatically read from `config.json` (`scraping.schedule.times`)
- Default: 04:00 and 16:00 Europe/Berlin (03:00 and 15:00 UTC)
- Automatically adjusts if schedule is changed in configuration

## How It Works

### 1. Capability Discovery
The workflow starts by introspecting the scraper:

```bash
python3 src/event_manager.py scraper-info
```

This returns JSON with:
- Supported source types (rss, html, api, facebook)
- Enabled sources from config.json
- Scraping schedule
- SmartScraper availability
- Available methods

### 2. Conditional Execution
Based on discovered capabilities, the workflow decides:
- **Skip scraping** if no sources are enabled
- **Skip scraping** if scraping libraries are not installed
- **Choose build path**: Fast event update vs. full rebuild
- **Adjust deployment** based on changes detected

### 3. Adaptive Behavior
The workflow automatically adapts when:
- New scraping sources are added to `config.json`
- Source types are changed (html → rss, etc.)
- Scraping schedule is modified
- New methods are added to `scraper.py`

## Triggering the Workflow

### Automatic Triggers

1. **Scheduled** (from config.json)
   - Default: 04:00 and 16:00 Europe/Berlin
   - Runs scraping automatically

2. **Push to main branch**
   - On `assets/json/events.json` → Fast event update + deployment
   - On `assets/json/events.demo.json` → Fast event update
   - On `config.json` → Full rebuild (configuration changed)
   - On `src/modules/scraper.py` → Full rebuild (scraper changed)

### Manual Triggers

Via GitHub Actions UI, choose task:

- **scrape-only** - Just scrape events, don't deploy
- **scrape-and-deploy** - Scrape and deploy if changes found (default)
- **force-deploy** - Force full rebuild and deploy
- **update-events** - Fast event data update only
- **review-pending** - Review and publish pending events (NEW!)
- **info** - Show scraper capabilities (no deployment)

Options:
- `force_scrape` - Force scraping even if sources unchanged
- `event_ids` - Event IDs to publish (comma-separated, or "all" for bulk) (NEW!)
- `auto_publish_pattern` - Auto-publish events matching pattern (e.g., "pending_*") (NEW!)

## Workflow Jobs

### Job 1: `discover-capabilities`
**Purpose**: Introspect scraper at runtime

**Outputs**:
- `capabilities` - Full JSON capabilities
- `enabled_sources` - Count of enabled sources
- `source_count` - Number of sources
- `scraping_enabled` - Whether libraries are installed
- `schedule_timezone` - Timezone from config
- `schedule_times` - Schedule times from config

### Job 2: `scrape-events`
**Purpose**: Scrape events from all enabled sources

**Conditions**:
- Scheduled run OR manual trigger
- Scraping libraries installed
- At least one source enabled

**Outputs**:
- `changes_detected` - Whether new events found
- `pending_count` - Number of pending events

### Job 3: `update-events`
**Purpose**: Fast event data update (no full rebuild)

**Conditions**:
- Manual `update-events` task OR
- Push to `events.json` or `events.demo.json`

**Speed**: ~30 seconds (vs. ~2 minutes for full rebuild)

### Job 4: `full-rebuild`
**Purpose**: Complete site generation with all assets

**Conditions**:
- Manual `force-deploy` OR
- Manual `scrape-and-deploy` OR
- Push to `config.json` OR
- Push to `scraper.py`

**Includes**:
- Fetch third-party dependencies (Leaflet.js)
- Full site generation
- Asset inlining

### Job 5: `deploy`
**Purpose**: Deploy to GitHub Pages

**Conditions**:
- Either `update-events` or `full-rebuild` succeeded

### Job 6: `show-info`
**Purpose**: Display scraper capabilities

**Conditions**:
- Manual `info` task only

**Output**: Complete capability information in workflow summary

### Job 7: `review-pending` (NEW!)
**Purpose**: Review and publish pending events via GitHub Actions

**Conditions**:
- Manual `review-pending` task OR
- `auto_publish_pattern` input provided

**Capabilities**:
- List all pending events
- Publish specific events by ID
- Bulk publish all events (`event_ids: "all"`)
- Auto-publish events matching pattern (`auto_publish_pattern: "pending_*"`)
- Automatic deployment trigger when events published

**Outputs**:
- `published_count` - Number of events published
- `events_published` - IDs of published events

**Editorial Options**:
1. **Publish specific events**: 
   - Input: `event_ids: "pending_1,pending_2,pending_3"`
   - Publishes only specified IDs

2. **Publish all pending events**: 
   - Input: `event_ids: "all"`
   - Publishes everything in pending queue

3. **Auto-publish by pattern**: 
   - Input: `auto_publish_pattern: "pending_*"`
   - Uses bulk-publish with wildcard matching

**Workflow**:
1. Checkout latest code (including scraper changes)
2. Pull latest changes from main
3. List pending events
4. Publish based on inputs
5. Commit and push changes
6. Trigger automatic deployment

## Introspection Methods

The workflow uses these methods added to `scraper.py`:

### `get_supported_source_types()`
Returns list of supported source types.

```python
['rss', 'html', 'api', 'facebook']
```

### `get_enabled_sources()`
Returns enabled sources from configuration.

```python
[
  {
    "name": "Wochenmarkt Hof",
    "type": "html",
    "url": "https://example.com/events"
  },
  ...
]
```

### `get_scraping_schedule()`
Returns scraping schedule from configuration.

```python
{
  "timezone": "Europe/Berlin",
  "times": ["04:00", "16:00"]
}
```

### `get_scraper_capabilities()`
Returns comprehensive capabilities JSON.

```python
{
  "supported_source_types": [...],
  "enabled_sources": [...],
  "schedule": {...},
  "smart_scraper_available": true,
  "scraping_libraries_installed": true,
  "methods": {...}
}
```

## Adding New Scraper Features

When you modify `scraper.py`, the workflow automatically adapts:

### Example: Adding New Source Type

1. **Add method to `scraper.py`**:
   ```python
   def _scrape_ical(self, source):
       """Scrape events from iCal feed"""
       # Implementation
   ```

2. **Update `get_supported_source_types()`**:
   ```python
   def get_supported_source_types(self):
       return ['rss', 'html', 'api', 'facebook', 'ical']  # Add 'ical'
   ```

3. **Add source to `config.json`**:
   ```json
   {
     "name": "Calendar Feed",
     "type": "ical",
     "url": "https://example.com/events.ics",
     "enabled": true
   }
   ```

4. **Workflow automatically adapts**:
   - Discovers new source type
   - Includes it in scraping
   - No workflow file changes needed!

## Testing Locally

### Test Scraper Introspection
```bash
python3 src/event_manager.py scraper-info
```

### Test Workflow Syntax
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/website-maintenance.yml'))"
```

### Test with Different Configurations
```bash
# Disable all sources
# Edit config.json, set all sources "enabled": false

# Run scraper-info
python3 src/event_manager.py scraper-info
# Output should show: "source_count": 0

# Workflow would skip scraping automatically
```

## Monitoring

### Check Workflow Runs
- Go to repository → Actions → "Website Maintenance (Unified)"
- View run logs and summaries

### Check Scraper Status
After scheduled run:
- Review "Event Scraping Summary" in workflow summary
- Check pending events count
- Review any failed sources

### Check Deployment
- View "Deployment Complete" summary
- Verify site URL is accessible

## Troubleshooting

### Scraping Not Running
**Check**:
- Are sources enabled in `config.json`?
- Run: `python3 src/event_manager.py scraper-info`
- Look for `"source_count": 0` → No sources enabled

### Workflow Fails on Introspection
**Check**:
- Does `scraper-info` command work locally?
- Run: `python3 src/event_manager.py scraper-info`
- Check for Python errors

### Changes Not Deploying
**Check**:
- Did scraping find new events? (`changes_detected: false`)
- Was deployment job skipped? (both update-events and full-rebuild failed)
- Check workflow conditions in YAML

## Migration from Old Workflows

### Replaced Workflows
The unified workflow replaces:
1. `scrape-events.yml` - Event scraping
2. `update-events-data.yml` - Event updates
3. `deploy.yml` - Full site deployment

### Backup Location
Old workflows are backed up in:
```
.github/workflows-backup/
├── scrape-events.yml
├── update-events-data.yml
└── deploy.yml
```

### To Disable Old Workflows
Rename `.yml` to `.yml.disabled` or move to backup folder.

### To Re-enable Old Workflows
Move from backup folder back to `.github/workflows/`.

## Future Enhancements

The wrapper architecture enables easy additions:

1. **Auto-scaling** - Adjust scraping frequency based on event volume
2. **Source health monitoring** - Track failed sources over time
3. **A/B testing** - Deploy preview builds automatically
4. **Performance optimization** - Skip deployment if no user-visible changes
5. **Multi-environment** - Support staging/production workflows

---

## Editorial Workflow via GitHub Actions (NEW!)

The unified workflow now includes editorial capabilities for reviewing and publishing pending events directly from GitHub Actions, without needing local CLI access.

### Use Case 1: Review After Scheduled Scraping

**Scenario**: Automated scraping runs at 04:00 and 16:00, adding events to pending queue. You want to review and publish them.

**Steps**:
1. Go to GitHub Actions → Website Maintenance (Unified)
2. Click "Run workflow"
3. Select task: `review-pending`
4. View pending events list in workflow summary
5. Decide which to publish:
   - Option A: Publish specific IDs → `event_ids: "pending_1,pending_3"`
   - Option B: Publish all → `event_ids: "all"`
   - Option C: Use pattern → `auto_publish_pattern: "pending_*"`
6. Run workflow
7. Events are published and site is automatically deployed

### Use Case 2: Auto-Approve Events from Trusted Sources

**Scenario**: You trust certain event sources and want to auto-publish them without manual review.

**Implementation**:
1. **Tag events in scraper**: Modify `scraper.py` to add tags:
   ```python
   event['tags'] = ['trusted'] if source['name'] == 'Official Source' else []
   event['id'] = f"pending_{source['name'].lower()}_{timestamp}"
   ```

2. **Auto-publish workflow**: Schedule a workflow to auto-publish trusted events:
   ```yaml
   # Add to schedule section
   - cron: '30 4 * * *'  # 30 minutes after scraping
   ```
   
3. **Use pattern matching**:
   - Input: `auto_publish_pattern: "pending_official*"`
   - All events from official sources auto-published

### Use Case 3: Bulk Publishing for Special Events

**Scenario**: You've reviewed events locally and want to bulk publish multiple specific IDs.

**Steps**:
1. Run locally: `python3 src/event_manager.py list-pending`
2. Note event IDs: `pending_1, pending_4, pending_7, pending_12`
3. Go to GitHub Actions
4. Run workflow with: `event_ids: "pending_1,pending_4,pending_7,pending_12"`
5. All specified events published at once

### Use Case 4: Emergency Publishing

**Scenario**: Important event needs immediate publishing while you're away from development machine.

**Steps**:
1. Access GitHub from mobile or any browser
2. Actions → Website Maintenance → Run workflow
3. Task: `review-pending`
4. `event_ids: "pending_latest"` (assuming you know the ID)
5. Event published and deployed within 2-3 minutes

### Editorial Commands Reference

| Input | Example | Effect |
|-------|---------|--------|
| `event_ids: "pending_1"` | Single ID | Publish one event |
| `event_ids: "pending_1,pending_2"` | Multiple IDs | Publish specific events |
| `event_ids: "all"` | All events | Bulk publish everything |
| `auto_publish_pattern: "pending_*"` | Wildcard | Publish all matching pattern |
| `auto_publish_pattern: "pending_official*"` | Prefix match | Publish events from specific source |

### Workflow Integration

The editorial workflow integrates seamlessly:

1. **After Scraping**: `scrape-events` job outputs `pending_count`
2. **Review Trigger**: Workflow can be set to require review if `pending_count > 0`
3. **Auto-Deploy**: Publishing events automatically triggers deployment via push to `events.json`
4. **No Double Build**: Uses existing fast update path (Job 3: `update-events`)

### Security Considerations

**Who Can Publish?**
- Requires GitHub Actions write permissions
- Only repository collaborators with Actions access
- Review GitHub's branch protection and required reviews settings

**Audit Trail**:
- All publishes logged in git commits
- Commit message includes timestamp and count
- Workflow run logs show which events published
- GitHub Actions audit log tracks who triggered workflows

### Local vs. Remote Editorial

| Feature | Local (TUI/CLI) | Remote (GitHub Actions) |
|---------|-----------------|-------------------------|
| Interactive review | ✅ Yes | ❌ No (list only) |
| Edit events | ✅ Yes | ❌ No (publish as-is) |
| Batch operations | ✅ Yes | ✅ Yes |
| Access required | 💻 Dev machine | 📱 Any browser |
| Speed | ⚡ Instant | 🐢 2-3 minutes (CI) |
| Audit trail | 📝 Manual commit | ✅ Automatic |

**Best Practice**: 
- Use **local TUI** for detailed review and editing
- Use **remote workflow** for quick bulk publishing or when away from dev machine

---

## Architecture Benefits

### KISS Compliance ✅
- Single workflow file (not scattered across multiple files)
- Self-documenting via introspection
- Minimal manual configuration

### Maintainability ✅
- Add sources in config.json only (no workflow changes)
- Scraper changes automatically reflected
- Clear separation: config (sources) vs. logic (scraper) vs. automation (workflow)

### Flexibility ✅
- Easy to test locally (`scraper-info`)
- Manual trigger with options
- Conditional execution (skip unnecessary steps)

## Related Documentation

- **Scraper Module**: `src/modules/scraper.py`
- **CLI Commands**: `python3 src/event_manager.py --help`
- **Configuration**: `config.json` (scraping section)
- **Feature Registry**: `features.json` (unified-workflow-wrapper)

## Support

For issues or questions:
1. Check workflow run logs in GitHub Actions
2. Test `scraper-info` command locally
3. Review this documentation
4. Check feature registry: `features.json`
