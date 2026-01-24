# Scripts Directory

This directory contains shell scripts for hosting setup and configuration.

## Contents

### Shell Scripts
- **setup-hosting-gitignore.sh** - Setup .gitignore for different hosting platforms (GitHub Pages, Netlify, Vercel)
- **sync-to-wiki.sh** - Sync documentation to GitHub Wiki

### Python Scripts
- **validate_config.py** - Validate config.json to prevent production issues (e.g., demo events on production)

### Configuration Templates
- **.gitignore.hosting.example** - Example .gitignore configurations for various hosting platforms

## Telegram Bot (Moved to src/modules/)

**Telegram bot scripts have been consolidated with scraper modules for code sharing:**

- ✅ `telegram_bot.py` → **MOVED** to `src/modules/telegram_bot_simple.py`
- ✅ `manage_pins.py` → **DELETED** (duplicate of `src/modules/pin_manager.py`)

The Telegram integration now shares OCR infrastructure with social media scrapers (Instagram, Facebook, etc.).

See [Telegram Integration Documentation](../docs/TELEGRAM_INTEGRATION.md) for full details.

**Run the bot:**
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
export GITHUB_TOKEN="your_github_pat"
export GITHUB_REPOSITORY="owner/repo"

# Run bot (from repository root)
python3 src/modules/telegram_bot_simple.py
```

**Manage PINs (via integrated CLI):**
```bash
# Generate new random PIN
python3 src/event_manager.py pin-generate

# Show hash for existing PIN
python3 src/event_manager.py pin-hash 1234

# Or use the TUI
python3 src/event_manager.py
# → Choose option 9: "🔐 Manage Organizer PINs"
```

## Python Tools Moved

**All Python utility scripts have been moved to `src/tools/` or converted to modules:**

- ✅ `check_kiss.py` → **DELETED** (wrapper for `src/modules/kiss_checker.py`)
- ✅ `verify_features.py` → **DELETED** (wrapper for `src/modules/feature_verifier.py`)
- ✅ `config_editor.py` → **DELETED** (wrapper for `src/modules/config_editor.py`)
- ✅ `generate_demo_events.py` → **MOVED** to `src/tools/generate_demo_events.py`
- ✅ `generate_screenshots.py` → **MOVED** to `src/tools/generate_screenshots.py`
- ✅ `cleanup_obsolete.py` → **MOVED** to `src/tools/cleanup_obsolete.py`
- ✅ `cleanup_old_docs.py` → **MOVED** to `src/tools/cleanup_old_docs.py`
- ✅ `docstring_readme.py` → **MOVED** to `src/tools/docstring_readme.py`
- ✅ `lint_markdown.py` → **MOVED** to `src/tools/lint_markdown.py`
- ✅ `test_documentation.py` → **MOVED** to `src/tools/test_documentation.py`
- ✅ `validate_docs.py` → **MOVED** to `src/tools/validate_docs.py`
- ✅ `telegram_bot.py` → **MOVED** to `src/modules/telegram_bot_simple.py`
- ✅ `manage_pins.py` → **DELETED** (duplicate of `src/modules/pin_manager.py`)

## Usage

### Shell Scripts

```bash
# Setup .gitignore for GitHub Pages
bash scripts/setup-hosting-gitignore.sh github-pages

# Setup .gitignore for Netlify
bash scripts/setup-hosting-gitignore.sh netlify

# Sync docs to wiki
bash scripts/sync-to-wiki.sh
```

### Config Validation (CRITICAL)

**ALWAYS run before committing changes to config.json:**

```bash
# Validate config.json
python3 scripts/validate_config.py
```

**What it checks:**
- ✅ `environment` field must be `"auto"` (not `"development"` or `"production"`)
- ✅ Prevents demo events from appearing on production
- ✅ Ensures proper environment auto-detection

**Why this matters:**
- `environment: "development"` → Demo events load in production/CI ❌
- `environment: "production"` → Real events load in local dev ❌
- `environment: "auto"` → Automatic detection (correct) ✅

This validation runs automatically in CI (see `.github/workflows/config-validation.yml`).

### Python Tools (Use from src/tools/)

```bash
# Generate demo events
python3 src/tools/generate_demo_events.py > assets/json/events.demo.json

# Generate screenshots
python3 src/tools/generate_screenshots.py

# Cleanup old docs
python3 src/tools/cleanup_old_docs.py --dry-run

# Lint markdown
python3 src/tools/lint_markdown.py --all
```

### Or Use CLI Commands (Recommended)

Many tools are accessible via the event_manager CLI:

```bash
# Feature verification
python3 src/event_manager.py check

# KISS compliance
python3 -m modules.kiss_checker --verbose

# Documentation tasks
python3 src/event_manager.py docs <task>

# Tests
python3 src/event_manager.py test <suite>
```

## See Also

- **Python Tools**: [`../src/tools/`](../src/tools/) - Standalone Python utilities
- **Modules**: [`../src/modules/`](../src/modules/) - Reusable Python modules  
- **Main Application**: [`../src/event_manager.py`](../src/event_manager.py) - CLI/TUI entry point
- **Tests**: [`../tests/`](../tests/) - Test suite
