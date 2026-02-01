# Preventing Timestamp Merge Conflicts

> **Problem**: Automated workflows update JSON files with timestamps, causing merge conflicts when multiple updates happen concurrently.  
> **Solution**: Use `git pull --rebase` in workflows + minimal .gitattributes rules for truly regenerable files.

---

## 📋 Table of Contents

- [Overview](#overview)
- [The Real Solution: Workflow Best Practices](#the-real-solution-workflow-best-practices)
- [Affected Files](#affected-files)
- [Git Attributes Strategy](#git-attributes-strategy)
- [Workflow Requirements](#workflow-requirements)
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

## The Real Solution: Workflow Best Practices

**The primary solution is NOT merge strategies** - it's ensuring workflows follow these rules:

### ✅ Required Workflow Pattern

```yaml
- name: Pull latest changes
  run: |
    git pull --rebase origin main  # CRITICAL: Use --rebase

- name: Make changes
  run: |
    python3 src/event_manager.py scrape

- name: Check for changes
  id: check
  run: |
    git diff --exit-code assets/json/pending_events.json || echo "changes=true" >> $GITHUB_OUTPUT

- name: Commit and push
  if: steps.check.outputs.changes == 'true'
  run: |
    git add assets/json/pending_events.json  # Only specific file
    git commit -m "🤖 Auto-update [skip ci]"
    git push
```

### Why This Works

1. **`git pull --rebase`** - Applies local changes on top of remote changes, avoiding merge commits
2. **Check before commit** - Don't create empty commits if nothing changed
3. **Specific files only** - Don't accidentally commit unrelated changes
4. **[skip ci]** - Prevents infinite loop of workflow triggers

---

## Affected Files

| File | Updated By | Conflict Risk | Strategy |
|------|------------|---------------|----------|
| `reviewer_notes.json` | Event scraper | Low (regenerated) | `.gitattributes: ours` |
| `weather_cache.json` | Weather scraper | Low (regenerated) | `.gitattributes: ours` |
| `pending_events.json` | Event scraper | Medium (cumulative) | **Workflow: pull --rebase** |
| `events.json` | Editorial workflow | Medium (cumulative) | **Workflow: pull --rebase** |
| `archived_events.json` | Archive script | Low (append-only) | **Workflow: pull --rebase** |
| `rejected_events.json` | Editorial workflow | Low (rare conflicts) | **Workflow: pull --rebase** |
| `organizers.json` | Entity extraction | Low (ID-based) | **Workflow: pull --rebase** |
| `locations.json` | Location verification | Low (ID-based) | **Workflow: pull --rebase** |

---

## Git Attributes Strategy

For **regenerable files** (files that are completely replaced on each run), we use `.gitattributes`:

```gitattributes
# Files that are completely regenerated (not cumulative)
assets/json/reviewer_notes.json merge=ours
assets/json/weather_cache.json merge=ours
```

### What `merge=ours` Does

- **Keeps the current version** (the one in the branch being merged into)
- **Ignores incoming changes** from the branch being merged
- **Prevents conflicts** entirely on these files

### When to Use `merge=ours`

✅ **Use for**: Files that are completely regenerated on each run  
❌ **DON'T use for**: Files that accumulate data (events, locations, etc.)

### Why Not `merge=union`?

**Union merge breaks JSON!** It concatenates changes line-by-line, creating invalid JSON:

```json
// Branch A
{"timestamp": "10:00:00"}

// Branch B
{"timestamp": "11:00:00"}

// Union merge (INVALID JSON!)
{"timestamp": "10:00:00"}{"timestamp": "11:00:00"}
```

---

## Workflow Requirements

### ✅ Do This

```yaml
# CORRECT: Pull with rebase before pushing
- name: Update data
  run: |
    git pull --rebase origin main
    python3 src/event_manager.py scrape
    git add assets/json/pending_events.json
    git commit -m "Update events" || true
    git push
```

### ❌ Don't Do This

```yaml
# WRONG: No pull before push
- name: Update data
  run: |
    python3 src/event_manager.py scrape
    git add .
    git commit -m "Update"
    git push  # Can create conflicts!
```

```yaml
# WRONG: Pull without rebase
- name: Update data
  run: |
    git pull origin main  # Creates merge commits
    python3 src/event_manager.py scrape
    git push
```

### Handling Push Conflicts

If `git push` fails with "non-fast-forward" error:

```yaml
- name: Push with retry
  run: |
    git pull --rebase origin main
    git push || (git pull --rebase origin main && git push)
```

---

## Testing

### Test Workflow Conflict Handling

1. **Manually trigger two workflows simultaneously**:
   ```bash
   gh workflow run scheduled-scraping.yml
   gh workflow run scheduled-scraping.yml  # Immediately after
   ```

2. **Verify both workflows complete successfully**:
   ```bash
   gh run list --workflow=scheduled-scraping.yml
   ```

3. **Check no merge conflicts** in commit history:
   ```bash
   git log --oneline --grep="conflict" -10
   ```

### Test .gitattributes Rules

```bash
# Verify merge strategy is applied
git check-attr merge assets/json/reviewer_notes.json
# Expected: assets/json/reviewer_notes.json: merge: ours

git check-attr merge assets/json/weather_cache.json
# Expected: assets/json/weather_cache.json: merge: ours
```

### Simulate Concurrent Updates

```bash
# Create test scenario
git checkout -b test-workflow-a
echo '{"test": "A"}' > assets/json/reviewer_notes.json
git add assets/json/reviewer_notes.json
git commit -m "Update A"

git checkout main
git checkout -b test-workflow-b
echo '{"test": "B"}' > assets/json/reviewer_notes.json
git add assets/json/reviewer_notes.json
git commit -m "Update B"

# Merge both (should use 'ours' strategy)
git checkout main
git merge test-workflow-a
git merge test-workflow-b  # Should keep version from test-workflow-a

# Cleanup
git branch -D test-workflow-a test-workflow-b
```

---

## Troubleshooting

### Still Getting Conflicts?

**Check 1: Workflow uses rebase**

```yaml
# ✅ CORRECT
git pull --rebase origin main

# ❌ WRONG
git pull origin main
```

**Check 2: .gitattributes is committed**

```bash
git ls-files .gitattributes
# Should output: .gitattributes
```

**Check 3: Merge attribute is applied**

```bash
git check-attr merge assets/json/reviewer_notes.json
# Should output: merge: ours
```

**Check 4: Workflow commits specific files only**

```yaml
# ✅ CORRECT
git add assets/json/pending_events.json

# ❌ WRONG
git add .
```

### Conflicts on Event Data Files

If you get conflicts on `events.json`, `pending_events.json`, etc.:

**This is expected!** These files accumulate data and shouldn't use auto-merge strategies.

**Resolution**:
1. Ensure both branches used `git pull --rebase` before pushing
2. If conflict occurs during manual merge:
   ```bash
   # Keep incoming changes (usually newer)
   git checkout --theirs assets/json/pending_events.json
   # Or manually merge in editor
   ```

### Invalid JSON After Merge

If JSON is corrupted after merge:

```bash
# Validate JSON
python3 -m json.tool assets/json/events.json

# If invalid, restore from backup
git checkout HEAD~1 assets/json/events.json
```

**Prevention**: Don't use `merge=union` for JSON files!

---

## German Locale Considerations

### Git Commands (Locale-Independent)

Git merge behavior is locale-independent:

```bash
# German locale
export LANG=de_DE.UTF-8
git pull --rebase  # Works the same

# English locale
export LANG=en_US.UTF-8
git pull --rebase  # Works the same
```

### Timestamp Formats (ISO 8601)

All timestamps use **ISO 8601 format** (locale-independent):

```python
from datetime import datetime
timestamp = datetime.now().isoformat()
# Output: "2026-02-01T10:00:00.123456"
# Same format regardless of LANG setting
```

### Error Messages

Git error messages may appear in German:

```bash
# German
$ git push
Fehler: failed to push some refs

# English
$ git push
error: failed to push some refs
```

Both indicate the same issue - solution is the same regardless of language.

### Commit Messages

Use German or English freely:

```bash
git commit -m "🤖 Ereignisse automatisch gescraped"
git commit -m "🤖 Auto-scraped events"
# Both work identically with merge strategies
```

---

## Best Practices

### For Workflow Authors

1. **Always use `git pull --rebase`** before committing
2. **Check for changes** before committing (avoid empty commits)
3. **Commit specific files** only, not entire working directory
4. **Use [skip ci]** in commit messages when appropriate
5. **Add retry logic** for push failures

### Example: Complete Workflow Step

```yaml
- name: Scrape and commit events
  run: |
    # Pull latest (with rebase to avoid merge commits)
    git pull --rebase origin main
    
    # Make changes
    python3 src/event_manager.py scrape
    
    # Check if file actually changed
    if git diff --exit-code assets/json/pending_events.json; then
      echo "No changes to commit"
      exit 0
    fi
    
    # Commit specific file
    git add assets/json/pending_events.json
    git commit -m "🤖 Auto-scraped events [skip ci]"
    
    # Push with retry
    git push || (git pull --rebase origin main && git push)
```

### For Developers

1. **Don't manually edit auto-generated files** - Use workflows instead
2. **If you must edit manually**:
   ```bash
   git pull --rebase origin main  # Get latest first
   # Edit file
   git add specific_file.json
   git commit -m "Manual update"
   git push
   ```

3. **If push is rejected**:
   ```bash
   git pull --rebase origin main
   git push
   ```

---

## Related Documentation

- [Git Attributes Documentation](https://git-scm.com/docs/gitattributes)
- [Git Rebase](https://git-scm.com/docs/git-rebase)
- [Project Copilot Instructions](../../.github/copilot-instructions.md)
- [GitHub Actions Workflows](../../.github/workflows/)

---

## Summary: The Key Insight

**Merge strategies alone don't solve JSON conflicts.**

The real solution is:
1. **Primary**: Workflows must use `git pull --rebase` before pushing
2. **Secondary**: Use `.gitattributes` with `merge=ours` for regenerable files only
3. **Never**: Use `merge=union` for JSON files (breaks structure)

**For cumulative JSON files** (events, locations, etc.), conflicts are actually useful - they indicate real issues that need review.
