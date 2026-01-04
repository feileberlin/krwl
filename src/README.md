# Source Code Directory

This directory contains the main application entry point and modules.

## Structure

```
src/
├── event_manager.py    # Main CLI/TUI entry point
├── modules/            # Reusable Python modules
└── tools/              # Standalone utility tools
```

## Main Entry Point

### event_manager.py

KRWL HOF Community Events Manager
A modular Python TUI for managing community events


**Usage:**
```bash
# Launch interactive TUI
python3 src/event_manager.py

# Show all commands
python3 src/event_manager.py --help

# Run specific command
python3 src/event_manager.py scrape
python3 src/event_manager.py build production
```

## Subdirectories

- **modules/** - See [modules/README.md](modules/README.md)
- **tools/** - See [tools/README.md](tools/README.md)

## Related Documentation

- **Main README**: [../README.md](../README.md)
- **Copilot Guide**: [../.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Tests**: [../tests/README.md](../tests/README.md)
