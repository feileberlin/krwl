# ADR-003: Single Entry Point (event_manager.py)

**Status**: Accepted  
**Date**: 2026-02-01  
**Deciders**: @feileberlin, Development Team  
**Tags**: backend, architecture, cli, tui

## Context

Python CLI applications often have multiple entry points:
- `main.py` - Primary entry point
- `cli.py` - Command-line interface
- `tui.py` - Text user interface
- `app.py` - Application logic

This creates confusion:
- "Which file do I run?"
- Duplicated initialization code
- Inconsistent argument parsing
- Multiple import paths

The KRWL HOF project needs:
- Interactive TUI for manual event management
- CLI commands for automation and CI/CD
- Single, obvious way to run the application
- Consistent initialization across all modes

## Decision

We use **`src/event_manager.py` as the single entry point** for all backend operations.

**Architecture:**
```
src/event_manager.py
├── main() - Parses CLI arguments
├── EventManagerTUI - Interactive menu system
└── cli_*() functions - Individual CLI commands
```

**Usage Patterns:**
```bash
# Launch TUI (no arguments)
python3 src/event_manager.py

# Run CLI commands
python3 src/event_manager.py scrape
python3 src/event_manager.py generate
python3 src/event_manager.py publish EVENT_ID
python3 src/event_manager.py --help
```

**Key Implementation Details:**
- `if __name__ == "__main__":` calls `main()`
- `main()` uses `argparse` to detect CLI vs TUI mode
- No arguments → Launch TUI
- With arguments → Execute CLI command
- All commands share same config loading and initialization

## Consequences

### Positive

- **Zero Confusion**: One obvious entry point, documented everywhere
- **Consistent Initialization**: All modes use same config loading
- **Easy Documentation**: "Run `python3 src/event_manager.py`" works for everyone
- **Simpler Testing**: One file to test for CLI/TUI behavior
- **No Duplication**: Single `main()` function handles all entry logic
- **Better Error Handling**: Centralized exception handling and logging

### Negative

- **Large File**: `event_manager.py` is ~1000 lines (still manageable)
- **Mixed Concerns**: CLI and TUI code in same file (but clearly separated)
- **Merge Conflicts**: Single file means more potential conflicts (mitigated by clear sections)

### Neutral

- **Module Structure**: Business logic still separated in `src/modules/`
- **Testability**: Individual modules tested independently

## Alternatives Considered

### 1. Separate main.py and event_manager.py
**Rejected**: Creates "which file do I run?" confusion, seen in early project history

### 2. CLI and TUI in Separate Files
**Rejected**: Requires shared initialization code, more files to maintain

### 3. Click or Typer Framework
**Rejected**: Adds dependency, `argparse` sufficient for our needs, violates KISS principle

### 4. setuptools Entry Points
**Rejected**: Overengineering for development tool, not a published package

## Implementation Rules

**CRITICAL**: These rules are enforced in `.github/copilot-instructions.md`:

✅ **DO:**
- Add new CLI commands as `cli_command_name()` functions in `event_manager.py`
- Add new TUI menus in `EventManagerTUI` class methods
- Use `main()` for argument parsing

❌ **DON'T:**
- Create `src/main.py` (does not exist and should never be created)
- Create separate entry point files
- Duplicate initialization logic

## File Organization

```python
# src/event_manager.py structure:

# 1. Imports
import argparse, sys, os

# 2. EventManagerTUI Class
class EventManagerTUI:
    def show_menu(self): ...
    def handle_scrape(self): ...
    # ... other TUI methods

# 3. CLI Command Functions
def cli_scrape(base_path, config): ...
def cli_generate(base_path, config): ...
# ... other CLI commands

# 4. Main Entry Point
def main():
    parser = argparse.ArgumentParser(...)
    # Parse args, route to TUI or CLI
    
if __name__ == "__main__":
    main()
```

## Related Decisions

- **ADR-002**: Vanilla JS Over Frameworks - Same KISS philosophy for backend
- **features.json**: `python-tui` (id: python-tui) and `cli-commands` (id: cli-commands)
- **.github/copilot-instructions.md**: Section "⚠️ CRITICAL: Single Entry Point"
- **DEPENDENCIES.md**: Backend module map shows `event_manager.py` at top

## Migration Notes

**Historical Context:**
- Early project had references to `src/main.py` in documentation
- `src/main.py` never actually existed in the codebase
- Documentation was updated to remove phantom references (2026-01-15)
- All current code uses `event_manager.py` correctly

**If you see `src/main.py` references:**
- They are outdated and should be replaced with `src/event_manager.py`
- Update documentation, scripts, and instructions accordingly

## Verification

Validate single entry point:
```bash
# This should NOT exist:
ls src/main.py  # Should fail

# This should exist:
ls src/event_manager.py  # Should succeed

# Should show help:
python3 src/event_manager.py --help

# Should launch TUI:
python3 src/event_manager.py
```

## When to Revisit

Consider splitting if:
- `event_manager.py` exceeds 2000 lines (currently ~1000)
- Team consistently experiences merge conflicts in this file
- Need to publish as standalone CLI tool (setuptools entry points)

**As of 2026-02-01**: File size is manageable, no issues reported.

## References

- [Python Application Layouts](https://realpython.com/python-application-layouts/)
- [Argparse Documentation](https://docs.python.org/3/library/argparse.html)
- Project: `.github/copilot-instructions.md` - Enforces this decision
- Project: `src/event_manager.py` - Implementation
