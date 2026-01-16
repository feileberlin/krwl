# Using TUI/CLI Functionality in GitHub Actions CI

## Overview

This document explains how to leverage **TUI (Text User Interface) and CLI (Command Line Interface) functionality within GitHub Actions CI/CD workflows**.

The good news: **YES, it's absolutely possible!** The KRWL HOF project already has extensive CI integration. This guide shows you how to extend it further.

## Current CI Capabilities

The project already supports these automated workflows:

### 1. Automated Scraping
```yaml
# Triggered by schedule or manual dispatch
- Event scraping from all sources
- Weather scraping with dresscode
- Automatic commit and deployment
```

### 2. Editorial Workflow in CI
```yaml
# Review and publish events via GitHub UI
workflow_dispatch:
  inputs:
    task: 'review-pending'
    event_ids: 'pending_123,pending_456'  # Specific events
    # OR
    auto_publish_pattern: 'pending_*'      # Bulk publish
```

### 3. Scraper Setup (Custom Source Manager)
```yaml
# Generate custom source handlers
workflow_dispatch:
  inputs:
    task: 'create-source'
    source_name: 'NewEventSource'
    source_url: 'https://example.com/events'
```

## How TUI/CLI Works in CI

### Understanding the Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                         │
├─────────────────────────────────────────────────────────────┤
│  Interactive TUI:                                           │
│  $ python3 src/event_manager.py                            │
│  → Full terminal UI with menus, prompts, colors            │
│                                                             │
│  Interactive CLI:                                          │
│  $ python3 src/modules/scraper_setup_tool.py              │
│  → Step-by-step wizard with user input                    │
└─────────────────────────────────────────────────────────────┘

                            ↓↓↓
                       (Adaptation)
                            ↓↓↓

┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions CI                         │
├─────────────────────────────────────────────────────────────┤
│  Non-Interactive CLI:                                       │
│  $ python3 src/event_manager.py scrape                     │
│  $ python3 src/event_manager.py publish pending_123        │
│  → Commands with arguments (no user prompts)               │
│                                                             │
│  GitHub UI Integration:                                    │
│  workflow_dispatch inputs → CLI arguments                  │
│  → Users interact via GitHub Actions UI                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Principle: **Dual-Mode Design**

All tools should support both modes:

1. **Interactive Mode** (Local/TUI): Prompts user for input
2. **Non-Interactive Mode** (CI/Automation): Accepts all inputs as arguments

## Implementation Patterns

### Pattern 1: CLI with Optional Interactive Mode

```python
# Example: Scraper Setup Tool

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Event URL (skips prompt)')
    parser.add_argument('--name', help='Source name (skips prompt)')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Non-interactive mode for CI')
    
    args = parser.parse_args()
    
    if args.non_interactive:
        # CI Mode: Use arguments, no prompts
        if not args.url or not args.name:
            print("Error: --url and --name required in non-interactive mode")
            sys.exit(1)
        
        process_source(args.url, args.name)
    else:
        # Interactive Mode: Prompt for missing inputs
        url = args.url or prompt_for_url()
        name = args.name or prompt_for_name()
        
        process_source(url, name)
```

### Pattern 2: GitHub Actions Workflow Integration

```yaml
name: Interactive Scraper Setup (via GitHub UI)

on:
  workflow_dispatch:
    inputs:
      source_name:
        description: 'Name for the new event source'
        required: true
        type: string
      
      source_url:
        description: 'Event listing page URL'
        required: true
        type: string
      
      location_strategy:
        description: 'How to extract locations'
        required: true
        type: choice
        options:
          - detail_page
          - listing_page
          - api_field

jobs:
  setup-scraper:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run scraper setup (non-interactive)
        run: |
          python3 src/modules/custom_source_manager.py create \
            "${{ github.event.inputs.source_name }}" \
            --url "${{ github.event.inputs.source_url }}" \
            --location-strategy "${{ github.event.inputs.location_strategy }}" \
            --non-interactive
      
      - name: Commit generated source
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add src/modules/smart_scraper/sources/
          git commit -m "Add source: ${{ github.event.inputs.source_name }}"
          git push
```

### Pattern 3: Reviewer Feedback in CI

```yaml
name: Review Pending Events (GitHub UI)

on:
  workflow_dispatch:
    inputs:
      action:
        description: 'Review action'
        required: true
        type: choice
        options:
          - list-pending
          - publish-event
          - reject-event
          - bulk-publish
      
      event_id:
        description: 'Event ID (for publish/reject)'
        required: false
        type: string
      
      pattern:
        description: 'Pattern for bulk operations (e.g., pending_*)'
        required: false
        type: string
      
      confidence_threshold:
        description: 'Publish only events with this confidence or higher'
        required: false
        type: choice
        options:
          - high
          - medium
          - low

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: List pending events (if selected)
        if: github.event.inputs.action == 'list-pending'
        run: |
          echo "## Pending Events" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo '```' >> $GITHUB_STEP_SUMMARY
          python3 src/event_manager.py list-pending --format markdown >> $GITHUB_STEP_SUMMARY
          echo '```' >> $GITHUB_STEP_SUMMARY
      
      - name: Publish specific event
        if: github.event.inputs.action == 'publish-event'
        run: |
          python3 src/event_manager.py publish "${{ github.event.inputs.event_id }}"
      
      - name: Bulk publish with confidence filter
        if: github.event.inputs.action == 'bulk-publish'
        run: |
          # Get confidence threshold
          CONFIDENCE="${{ github.event.inputs.confidence_threshold }}"
          PATTERN="${{ github.event.inputs.pattern }}"
          
          # Bulk publish with filters
          python3 src/event_manager.py bulk-publish \
            --pattern "$PATTERN" \
            --min-confidence "$CONFIDENCE" \
            --ci-mode
      
      - name: Commit changes
        run: |
          if [[ -n $(git status --porcelain) ]]; then
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add assets/json/
            git commit -m "Editorial: ${{ github.event.inputs.action }} via GitHub Actions"
            git push
          fi
```

## Advanced: Field Mapping in CI

The new **Scraper Setup Tool** can be used both locally (interactive) and in CI (automated):

### Local Usage (Interactive TUI)

```bash
# Step-by-step wizard
$ python3 src/modules/scraper_setup_tool.py

# Wizard guides you through:
# 1. Enter URL
# 2. Analyze page structure
# 3. Map each field interactively
# 4. Test mappings
# 5. Save configuration
```

### CI Usage (Automated)

```yaml
name: Setup Scraper with Field Mapping

on:
  workflow_dispatch:
    inputs:
      source_name:
        description: 'Source name'
        required: true
      
      source_url:
        description: 'Events page URL'
        required: true
      
      mapping_json:
        description: 'Field mapping JSON (optional, can be created manually)'
        required: false

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: Create field mapping (if not provided)
        if: github.event.inputs.mapping_json == ''
        run: |
          # Analyze page and create basic mapping
          python3 src/modules/scraper_setup_tool.py analyze \
            --url "${{ github.event.inputs.source_url }}" \
            --output mapping.json \
            --non-interactive
      
      - name: Use provided mapping
        if: github.event.inputs.mapping_json != ''
        run: |
          echo '${{ github.event.inputs.mapping_json }}' > mapping.json
      
      - name: Generate source handler with mapping
        run: |
          python3 src/modules/custom_source_manager.py create \
            "${{ github.event.inputs.source_name }}" \
            --url "${{ github.event.inputs.source_url }}" \
            --mapping-file mapping.json \
            --non-interactive
      
      - name: Commit
        run: |
          git add src/modules/smart_scraper/sources/
          git add config/scraper_mappings/
          git commit -m "Add source: ${{ github.event.inputs.source_name }}"
          git push
```

## Best Practices for CI Integration

### 1. **Always Support Both Modes**

```python
def process_events(event_ids=None, interactive=True):
    if interactive:
        # Prompt for missing inputs
        if not event_ids:
            event_ids = prompt_for_event_ids()
    else:
        # CI mode: require all inputs
        if not event_ids:
            raise ValueError("event_ids required in non-interactive mode")
    
    # Process events...
```

### 2. **Use GitHub STEP_SUMMARY for Output**

```bash
# Instead of printing to console, write to summary
echo "## Results" >> $GITHUB_STEP_SUMMARY
echo "Events published: $COUNT" >> $GITHUB_STEP_SUMMARY
```

### 3. **Export Configurations for Reuse**

```python
# After interactive setup, export for CI
def export_for_ci(config):
    """Export configuration in CI-friendly format."""
    ci_config = {
        'version': '1.0',
        'non_interactive_args': [
            f"--url {config['url']}",
            f"--name {config['name']}",
            f"--strategy {config['strategy']}"
        ]
    }
    save_json('ci_config.json', ci_config)
```

### 4. **Provide Dry-Run Mode**

```bash
# Always test before committing
python3 src/event_manager.py publish pending_* --dry-run
```

## Real-World Examples

### Example 1: Daily Automated Scraping

Already implemented in `.github/workflows/website-maintenance.yml`:

```yaml
on:
  schedule:
    - cron: '0 3 * * *'   # Daily at 3 AM UTC

jobs:
  scrape:
    steps:
      - run: python3 src/event_manager.py scrape
      - run: python3 src/event_manager.py scrape-weather
      - run: git add . && git commit && git push
```

### Example 2: Editorial Review via GitHub UI

Already implemented in `.github/workflows/website-maintenance.yml`:

```yaml
workflow_dispatch:
  inputs:
    task: 'review-pending'
    event_ids: 'pending_123,pending_456'
```

Users can:
1. Go to GitHub Actions tab
2. Select "Website Maintenance" workflow
3. Click "Run workflow"
4. Fill in the form
5. Submit

### Example 3: Setup New Source via GitHub UI

**NEW** - Can be added based on the scraper setup tool:

```yaml
workflow_dispatch:
  inputs:
    source_name: 'NewSource'
    source_url: 'https://example.com/events'
    
    # Field mapping (can be pre-configured or generated)
    title_selector: '.event-title'
    location_selector: '.venue-name'
    date_selector: '.event-date'
```

## Limitations & Workarounds

### Limitation 1: No Real-Time Interaction in CI

**Problem**: Can't prompt user during workflow execution

**Workaround**: Use `workflow_dispatch` inputs to collect data upfront

### Limitation 2: No Visual TUI in CI

**Problem**: Terminal colors/menus don't work in GitHub Actions logs

**Workaround**: Use GitHub STEP_SUMMARY for formatted output (supports Markdown)

### Limitation 3: Long-Running Processes

**Problem**: GitHub Actions has 6-hour job timeout

**Workaround**: Break into multiple jobs with artifacts

## Summary: Yes, TUI/CLI Functionality IS Possible in CI!

**What works well:**
- ✅ Non-interactive CLI commands with arguments
- ✅ GitHub UI as input collection interface (`workflow_dispatch`)
- ✅ Automated processing (scraping, publishing, archiving)
- ✅ Markdown summaries for results
- ✅ Git commits from workflows

**What requires adaptation:**
- ⚠️ Interactive prompts → GitHub UI form inputs
- ⚠️ Terminal colors/menus → Markdown formatting
- ⚠️ Real-time feedback → Step summaries and logs

**Recommended approach:**
1. Build CLI with `--non-interactive` flag
2. Accept all inputs as arguments in non-interactive mode
3. Create GitHub Actions workflow with `workflow_dispatch` inputs
4. Map GitHub UI inputs to CLI arguments
5. Use `$GITHUB_STEP_SUMMARY` for results

**Bottom line**: The infrastructure is already in place. You just need to add `--non-interactive` support to new tools and create corresponding GitHub Actions workflows!

## See Also

- **Current workflows**: `.github/workflows/website-maintenance.yml`
- **CLI tools**: `src/event_manager.py`, `src/modules/custom_source_manager.py`
- **New tool**: `src/modules/scraper_setup_tool.py` (with interactive + CI modes)
