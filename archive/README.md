# Archive Directory

This directory contains backup and legacy files that are preserved for historical reference but are not actively used in the project.

## Purpose

- **Historical reference** - Preserves previous implementations for comparison
- **Recovery** - Allows reverting changes if needed
- **Documentation** - Shows evolution of the codebase

## Contents

### js_backups/
Legacy JavaScript files that have been replaced by current implementations:
- `app-old.js` - Previous version of main app
- `app-original.js` - Original implementation before refactoring
- `app-before-filter-ui.js` - Version before filter UI redesign
- `app.js.backup` - Backup before latest changes
- `event-listeners-old.js` - Previous event listener implementation
- `utils-before-template.js` - Utils before template engine integration

### json_backups/
Backup data files:
- `events.json.backup` - Event data backup
- `pending_events.json.backup` - Pending events backup

## Guidelines

1. **Do not reference these files** in active code
2. **Do not import** from these files
3. **Consult only for reference** when understanding historical decisions
4. Files in this directory are NOT maintained or tested

## Active Files

For current implementations, see:
- JavaScript: `assets/js/app.js`, `assets/js/*.js` (without -old/-backup suffixes)
- JSON: `assets/json/*.json` (without .backup extension)
