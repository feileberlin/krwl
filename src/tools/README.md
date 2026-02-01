# Tools Directory

Standalone Python utility tools for KRWL> project.

## Contents

### Design & Build Tools
- **generate_design_tokens.py** - Generate CSS design tokens from config.json
- **migrate_css_to_tokens.py** - Migrate existing CSS to use design tokens
- **update_dependencies.py** - Update third-party dependency versions

### Demo & Testing Tools
- **generate_demo_events.py** - Generate demo events with dynamic timestamps for testing
- **generate_screenshots.py** - Generate screenshots of the app for documentation

### Documentation Tools
- **docstring_readme.py** - Generate README from Python docstrings
- **cleanup_old_docs.py** - Remove obsolete documentation HTML files
- **lint_markdown.py** - Lint markdown files for consistency
- **test_documentation.py** - Test documentation completeness
- **validate_docs.py** - Validate documentation structure

### Maintenance Tools
- **cleanup_obsolete.py** - Remove obsolete files from the project

## Usage

All tools can be run from the project root directory:

```bash
# Design tokens
python3 src/tools/generate_design_tokens.py

# Demo events
python3 src/tools/generate_demo_events.py > assets/json/events.antarctica.json

# Screenshots
python3 src/tools/generate_screenshots.py --verbose

# Documentation
python3 src/tools/docstring_readme.py
python3 src/tools/lint_markdown.py --all --fix
python3 src/tools/cleanup_old_docs.py --dry-run

# Maintenance
python3 src/tools/cleanup_obsolete.py --dry-run
```

## Integration with event_manager.py

Some tools are also accessible via the event_manager CLI:

```bash
# Documentation tasks
python3 src/event_manager.py docs build
python3 src/event_manager.py docs lint-markdown --all

# Utilities
python3 src/event_manager.py utils <utility-name>
```

## Tool Categories

### Design Tools
These tools manage the visual design system and CSS architecture.

### Demo Tools  
These tools generate test data and visual documentation.

### Documentation Tools
These tools maintain documentation quality and consistency.

### Maintenance Tools
These tools keep the project clean and organized.

## See Also

- **Modules**: [`../modules/`](../modules/) - Reusable Python modules integrated into event_manager
- **Main Application**: [`../event_manager.py`](../event_manager.py) - CLI/TUI entry point
- **Scripts**: [`../../scripts/`](../../scripts/) - Shell scripts for hosting setup
- **Tests**: [`../../tests/`](../../tests/) - Test suite
