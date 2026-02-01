# Merge Strategies for Automated Files

> **Problem**: Automated workflows update JSON files with timestamps, causing merge conflicts when multiple updates happen concurrently.  
> **Solution**: Use Git attributes to define merge strategies that prevent timestamp-only conflicts.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Affected Files](#affected-files)
- [Merge Strategies](#merge-strategies)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [German Locale Considerations](#german-locale-considerations)

---

## Overview

This project uses automated workflows (GitHub Actions) to regularly update data files:

- **Event scraping** - Runs twice daily, updates `pending_events.json`
- **Weather scraping** - Runs hourly, updates `weather_cache.json`
- **Location verification** - Updates `reviewer_notes.json`, `locations.json`
- **Entity extraction** - Updates `organizers.json`, entity reports

When these workflows run concurrently or from different branches, they can create merge conflicts on timestamp fields **even when the actual data hasn't changed**.

### Example Conflict

```json
<<<<<<< HEAD
{
  "last_scraped": "2026-02-01T10:00:00Z"
}
=======
{
  "last_scraped": "2026-02-01T10:01:00Z"
}
>>>>>>> feature-branch
```

This is a **meaningless conflict** - the timestamp difference doesn't matter, but Git sees it as a conflict.

---

## Affected Files

| File | Updated By | Timestamp Field | Merge Strategy |
|------|------------|-----------------|----------------|
| `reviewer_notes.json` | Event scraper | `timestamp` per note | **Union** - Keep all notes |
| `weather_cache.json` | Weather scraper | `timestamp` in cache | **Union** - Accept both |
| `pending_events.json` | Event scraper | `last_scraped` | **Union** - Prefer latest |
| `events.json` | Editorial workflow | `last_updated` | **Union** - Keep all events |
| `archived_events.json` | Archive script | `last_updated` | **Union** - Keep all events |
| `rejected_events.json` | Editorial workflow | `last_updated` | **Union** - Keep all events |
| `organizers.json` | Entity extraction | `updated_at` | **Union** - Keep all entities |
| `locations.json` | Location verification | `last_modified` | **Union** - Keep all locations |

---

## Merge Strategies

### Union Merge

**Strategy**: `merge=union`

**What it does**: When both branches modify the same file, Git combines both versions by concatenating the changes.

**When to use**: Files where having both versions is acceptable and won't break functionality.

**Example**: `reviewer_notes.json`

```json
// Branch A adds note at 10:00
{
  "event_123": [
    {"note": "Location ambiguous", "timestamp": "2026-02-01T10:00:00Z"}
  ]
}

// Branch B adds note at 10:01
{
  "event_123": [
    {"note": "Location ambiguous", "timestamp": "2026-02-01T10:01:00Z"}
  ]
}

// After union merge - BOTH notes kept
{
  "event_123": [
    {"note": "Location ambiguous", "timestamp": "2026-02-01T10:00:00Z"},
    {"note": "Location ambiguous", "timestamp": "2026-02-01T10:01:00Z"}
  ]
}
```

**Why this is safe**:
- Duplicate notes are harmless (reviewed events are filtered)
- Application code deduplicates events by ID
- Timestamps are informational only

### Theirs Strategy (Manual)

**Strategy**: `git merge -X theirs branch-name`

**What it does**: Prefers incoming changes over local changes.

**When to use**: Manual merges where you want the latest data to win.

**Example**: Merging a feature branch that has old scrape data

```bash
# Feature branch has stale scrape data from 3 days ago
# Main branch has fresh scrape data from 1 hour ago
git merge -X theirs origin/main  # Use main's newer data
```

---

## How It Works

### 1. Configuration

The `.gitattributes` file in the repository root defines merge strategies:

```gitattributes
# Reviewer notes use union merge
assets/json/reviewer_notes.json merge=union

# Weather cache uses union merge
assets/json/weather_cache.json merge=union

# Events use union merge
assets/json/events.json merge=union
```

### 2. Automatic Application

When Git merges branches, it automatically applies the configured strategy:

```bash
# Normal merge
git merge feature-branch

# Git sees reviewer_notes.json changed in both branches
# Instead of creating a conflict, it applies 'union' strategy
# Result: Both changes are kept, no manual resolution needed
```

### 3. Workflow Integration

Automated workflows pull with rebase to avoid merge commits:

```yaml
- name: Pull latest changes
  run: |
    git pull --rebase origin main
```

This ensures linear history and applies merge strategies when needed.

---

## Testing

### Test Union Merge

```bash
# 1. Create test branches
git checkout -b test-branch-a main
# Update reviewer_notes.json with timestamp A
git add assets/json/reviewer_notes.json
git commit -m "Update A"

git checkout -b test-branch-b main
# Update reviewer_notes.json with timestamp B
git add assets/json/reviewer_notes.json
git commit -m "Update B"

# 2. Merge both branches
git checkout main
git merge test-branch-a  # First merge (fast-forward)
git merge test-branch-b  # Second merge (should use union strategy)

# 3. Verify no conflicts
git status  # Should show "nothing to commit"

# 4. Validate JSON structure
python3 -m json.tool assets/json/reviewer_notes.json

# 5. Cleanup
git branch -D test-branch-a test-branch-b
```

### Test in CI/CD

Simulate concurrent workflow runs:

```bash
# Terminal 1: Trigger manual scrape
gh workflow run scheduled-scraping.yml

# Terminal 2: Trigger weather update (at same time)
gh workflow run scheduled-scraping.yml

# Both workflows commit to same files
# Merge strategies prevent conflicts
```

---

## Troubleshooting

### Conflicts Still Happening

**Check if .gitattributes is committed:**

```bash
git ls-files .gitattributes
# Should output: .gitattributes
```

**Verify merge strategy is applied:**

```bash
git check-attr merge assets/json/reviewer_notes.json
# Should output: assets/json/reviewer_notes.json: merge: union
```

**Re-apply .gitattributes:**

```bash
# If .gitattributes was added recently, clear cache
git rm --cached -r .
git reset --hard
```

### Invalid JSON After Merge

**Cause**: Union merge can create invalid JSON if both branches modify the same object.

**Example**:

```json
// Branch A
{"key": "value1"}

// Branch B  
{"key": "value2"}

// After union merge (INVALID)
{"key": "value1"}{"key": "value2"}
```

**Solution**: Run JSON validation after merge:

```bash
python3 -m json.tool assets/json/reviewer_notes.json
# If invalid, manually fix the JSON structure
```

**Prevention**: Ensure JSON files use array-based structure at root level:

```json
// Good - Array at root
[
  {"id": "1", "data": "A"},
  {"id": "2", "data": "B"}
]

// Better - Object with arrays
{
  "items": [
    {"id": "1", "data": "A"}
  ],
  "metadata": {
    "last_updated": "2026-02-01T10:00:00Z"
  }
}
```

### Workflow Still Shows Conflicts

**Check workflow uses pull with rebase:**

```yaml
- name: Pull latest changes
  run: |
    git pull --rebase origin main  # ✅ Correct
    # NOT: git pull origin main    # ❌ Wrong - creates merge commits
```

**Check workflow commits correct files:**

```yaml
- name: Commit changes
  run: |
    git add assets/json/pending_events.json  # ✅ Specific file
    # NOT: git add .                         # ❌ Wrong - adds everything
```

---

## German Locale Considerations

### Git Merge Strategies (Locale-Independent)

Git merge strategies work the same regardless of system locale:

```bash
# German locale
export LANG=de_DE.UTF-8
git merge feature-branch  # Merge strategies still work

# English locale
export LANG=en_US.UTF-8
git merge feature-branch  # Same behavior
```

### Timestamp Formats (ISO 8601)

All timestamps in this project use **ISO 8601 format**, which is locale-independent:

```python
# Python code (locale-independent)
from datetime import datetime
timestamp = datetime.now().isoformat()
# Output: "2026-02-01T10:00:00.123456"
```

```json
// JSON data (always ISO 8601)
{
  "timestamp": "2026-02-01T10:00:00Z",
  "last_scraped": "2026-02-01T10:00:00+01:00"
}
```

### Git Commit Messages (Can Use German)

Commit messages can use German without affecting merge behavior:

```bash
# German commit message
git commit -m "🤖 Ereignisse automatisch gescraped [geplant]"

# English commit message
git commit -m "🤖 Auto-scraped events [scheduled]"

# Both work with merge strategies
```

### Error Messages

Git error messages may appear in German if `LANG=de_DE.UTF-8`:

```bash
# German
$ git merge feature
Automatisches Merging von assets/json/reviewer_notes.json

# English
$ git merge feature
Auto-merging assets/json/reviewer_notes.json
```

**Important**: Merge strategies work regardless of error message language.

---

## Best Practices

### For Developers

1. **Always pull with rebase** before pushing:
   ```bash
   git pull --rebase origin main
   git push
   ```

2. **Validate JSON after manual merges**:
   ```bash
   python3 -m json.tool assets/json/events.json
   ```

3. **Use specific file commits** in workflows:
   ```bash
   git add assets/json/pending_events.json  # Good
   # Avoid: git add .                       # Bad
   ```

### For Workflow Maintainers

1. **Check for changes before committing**:
   ```yaml
   - name: Check for changes
     id: check
     run: |
       git diff --exit-code assets/json/pending_events.json || echo "changes=true" >> $GITHUB_OUTPUT
   ```

2. **Only commit if changes exist**:
   ```yaml
   - name: Commit changes
     if: steps.check.outputs.changes == 'true'
     run: |
       git add assets/json/pending_events.json
       git commit -m "Auto-update"
   ```

3. **Use [skip ci] for automated commits**:
   ```yaml
   git commit -m "🤖 Auto-scraped events [skip ci]"
   ```

---

## Related Documentation

- [Git Attributes Documentation](https://git-scm.com/docs/gitattributes)
- [Merge Strategies](https://git-scm.com/docs/merge-strategies)
- [Project Copilot Instructions](../../.github/copilot-instructions.md)
- [GitHub Actions Workflows](../../.github/workflows/)

---

## Questions or Issues?

If you encounter merge conflicts that shouldn't happen:

1. Check `.gitattributes` is committed and up to date
2. Verify merge strategy: `git check-attr merge path/to/file`
3. Validate JSON structure: `python3 -m json.tool file.json`
4. Check workflow logs for error messages
5. Open an issue with details: branch names, conflict content, workflow run URL

**Remember**: Merge strategies prevent **timestamp-only** conflicts. If the actual data conflicts (different event details, different location data), you'll still need to resolve manually.
