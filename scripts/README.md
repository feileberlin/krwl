# Scripts Directory

This directory contains shell scripts and standalone Python scripts for hosting setup, configuration, and Telegram bot management.

## Contents

### Telegram Bot Scripts (NEW)

- **telegram_bot.py** - Simple Telegram bot for event submissions (✅ Active - replaces old bot)
- **manage_pins.py** - PIN management helper for trusted organizers

See [Telegram Integration Documentation](../docs/TELEGRAM_INTEGRATION.md) for full details.

### Shell Scripts
- **setup-hosting-gitignore.sh** - Setup .gitignore for different hosting platforms (GitHub Pages, Netlify, Vercel)
- **sync-to-wiki.sh** - Sync documentation to GitHub Wiki

### Python Scripts
- **validate_config.py** - Validate config.json to prevent production issues (e.g., demo events on production)

### Configuration Templates
- **.gitignore.hosting.example** - Example .gitignore configurations for various hosting platforms

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

## Usage

### Telegram Bot Scripts

#### Run Simple Telegram Bot

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
export GITHUB_TOKEN="your_github_pat"
export GITHUB_REPOSITORY="owner/repo"

# Run bot
python3 scripts/telegram_bot.py
```

**Features:**
- 📸 Flyer uploads → cached and dispatched for OCR processing
- 💬 Contact messages → create GitHub issues
- 🔐 PIN publishing → direct to production (trusted organizers only)

See [Telegram Integration Documentation](../docs/TELEGRAM_INTEGRATION.md)

#### Manage PINs for Trusted Organizers

```bash
# Generate new random PIN
python3 scripts/manage_pins.py generate

# Show hash for existing PIN
python3 scripts/manage_pins.py hash 1234

# Validate PIN format
python3 scripts/manage_pins.py validate 5678

# Help
python3 scripts/manage_pins.py --help
```

**Security:**
- Never commit PINs to repository
- Store only SHA256 hashes in GitHub Secrets
- Rotate PINs regularly

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
