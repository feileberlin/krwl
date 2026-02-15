# Repository Cleanliness System

**Purpose**: Prevent repository clutter from accumulating by enforcing file placement rules and providing automated validation.

## Problem Statement

Previous repository cleanups showed that backup files, summary files, and temporary files accumulate over time without proper guidelines and enforcement. This creates:
- Confusion about which files are current
- Cluttered search results (`grep`, IDE search)
- Difficulty onboarding new contributors
- Wasted repository space

## Solution

A comprehensive three-layer approach:

### Layer 1: Documentation & Guidelines

**Location**: `.github/copilot-instructions.md` → "Repository Cleanliness" section

**Provides**:
- ✅ Clear DO/DON'T rules for file creation
- ✅ File placement decision tree
- ✅ Naming conventions for notes and plans
- ✅ Workflow examples with bash commands
- ✅ Pre-commit checklist

### Layer 2: Enforcement Tools

**Files**:
- `scripts/check_repository_cleanliness.py` - Automated validator
- `scripts/pre-commit-check.sh` - Pre-commit hook helper

**Capabilities**:
```bash
# Check for issues
python3 scripts/check_repository_cleanliness.py

# Use strict mode (markdown files in root = error)
python3 scripts/check_repository_cleanliness.py --strict

# Integrate with git hooks
bash scripts/pre-commit-check.sh
```

**Exit Codes**:
- `0` - Clean repository ✅
- `1` - Warnings (allowed but discouraged) ⚠️
- `2` - Errors (must fix) ❌

**What It Checks**:
- ❌ Backup files: `*-old.*`, `*-backup.*`, `*.bak`, `*.tmp`
- ❌ Summary files in root: `*_SUMMARY.md`, `*_IMPLEMENTATION.md`, `AI_*.md`
- ❌ Unexpected markdown files in root (only `README.md` and `CHANGELOG.md` allowed)
- ❌ Temporary files: `*~`, `.DS_Store`, `Thumbs.db`

**Exceptions**:
- ✅ Comparison screenshots: `*-before-after.png`, `*-comparison.png`
- ✅ Archive directory: Intentionally for old files
- ✅ Generated directories: `lib/`, `public/`

### Layer 3: CI/CD Integration

**Workflow**: `.github/workflows/ci-tests.yml` → `cleanliness-check` job

**Runs automatically on**:
- Pull requests (opened, synchronize, reopened)
- Pushes to main branch

**Blocks PRs if**:
- Backup files detected
- Summary files in root
- Misplaced markdown files (strict mode)

## File Placement Rules

### ❌ NEVER Create

```
❌ /IMPLEMENTATION_SUMMARY.md          # Root summaries
❌ /AI_TRANSLATION_NOTES.md            # Root AI notes
❌ app-old.js                          # Backup files
❌ config.json.backup                  # Backup configs
❌ /debug.txt                          # Temp files in repo
```

### ✅ ALWAYS Use

| File Type | Correct Location | Example |
|-----------|-----------------|---------|
| Implementation notes | `docs/notes/` | `docs/notes/2026-02-15-feature-name.md` |
| Implementation plans | `docs/plans/` | `docs/plans/20260215-feature-plan.md` |
| Architectural decisions | `docs/adr/` | `docs/adr/005-decision-title.md` |
| Temporary files | `/tmp/` | `/tmp/debug-output.txt` |
| Version snapshots | Git commits | `git commit -m "Snapshot"` |

## File Naming Conventions

### Implementation Notes (`docs/notes/`)

**Format**: `YYYY-MM-DD-description.md`

Examples:
- `2026-02-15-ai-translation-implementation.md`
- `2026-02-16-search-feature-completed.md`

### Implementation Plans (`docs/plans/`)

**Format**: `YYYYMMDD-feature-name.md` or `feature-name-plan.md`

Examples:
- `20260201-multilanguage-support.md`
- `search-feature-plan.md`

### Architectural Decision Records (`docs/adr/`)

**Format**: `NNN-decision-title.md` (numbered)

Examples:
- `001-fallback-list-when-map-fails.md`
- `005-translation-approach.md`

## Integration with Agents

### Complexity Manager
- References cleanliness rules when coordinating work
- Checks for proper file placement before suggesting changes

### Implementation Agent
- MUST follow cleanliness rules during implementation
- Required to run cleanliness check before completing work
- Places notes in `docs/notes/` with proper naming

### Planning Agent
- Creates plans in `docs/plans/`
- Uses consistent naming conventions

## Migration History

### February 2026 Cleanup

**Actions taken**:
1. Moved root summary files to `docs/notes/`:
   - `AI_TRANSLATION_IMPLEMENTATION_SUMMARY.md` → `docs/notes/2026-02-15-ai-translation-implementation.md`
   - `MULTILANGUAGE_ENHANCEMENT_SUMMARY.md` → `docs/notes/2026-02-15-multilanguage-enhancement.md`
   - `TRANSLATION_SCOPE_CHANGE_SUMMARY.md` → `docs/notes/2026-02-15-translation-scope-change.md`

2. Created enforcement infrastructure:
   - Cleanliness validation script
   - Pre-commit hook helper
   - CI/CD integration

3. Updated documentation:
   - Added comprehensive guidelines to copilot-instructions.md
   - Created docs/notes/README.md
   - Created docs/plans/README.md
   - Updated agent instructions

### Previous Cleanup (Documented in `docs/BACKUP_CLEANUP_NOTES.md`)

**Actions taken**:
- Moved backup files to `archive/` directory
- Cleaned up JavaScript backups
- Cleaned up JSON backups
- Established archive structure

## Verification

### Manual Check
```bash
# Check current status
python3 scripts/check_repository_cleanliness.py

# Strict mode (for CI)
python3 scripts/check_repository_cleanliness.py --strict
```

### Automated Check
- Runs on every PR via CI/CD
- Blocks merges if issues found
- Provides clear error messages with fixes

## Best Practices

### For Developers

1. **Never create backup files** - Use git branches/commits instead
2. **Use /tmp/ for temporary work** - Never commit temp files
3. **Place notes in docs/notes/** - With proper date prefix
4. **Run cleanliness check before PR** - Catch issues early
5. **Follow naming conventions** - Makes files discoverable

### For AI Assistants

1. **Check guidelines first** - Before creating any files
2. **Use proper locations** - docs/notes/, docs/plans/, /tmp/
3. **Run validation** - Before completing work
4. **Reference documentation** - Point users to relevant sections
5. **Update .gitignore** - If new patterns emerge

## Troubleshooting

### Issue: Cleanliness check fails with backup files

**Solution**:
```bash
# Delete the backup files
rm file-old.js file.backup

# Use git instead
git log -- file.js  # View history
git diff HEAD~1 file.js  # Compare with previous version
```

### Issue: Summary file in root directory

**Solution**:
```bash
# Move to proper location with date prefix
mv IMPLEMENTATION_SUMMARY.md docs/notes/2026-02-15-implementation.md
```

### Issue: Temporary files detected

**Solution**:
```bash
# Delete or move to /tmp
rm debug.txt
# Or add to .gitignore if needed
echo "debug.txt" >> .gitignore
```

## Related Documentation

- `.github/copilot-instructions.md` → "Repository Cleanliness" section (comprehensive guide)
- `docs/notes/README.md` - Implementation notes guidelines
- `docs/plans/README.md` - Implementation plans guidelines
- `docs/BACKUP_CLEANUP_NOTES.md` - Previous cleanup history
- `.gitignore` - Pattern definitions

## Success Metrics

✅ **Working well when**:
- CI checks pass consistently
- No backup files in main branch
- Root directory contains only essential files
- Contributors know where to place files
- Search results are relevant

❌ **Needs attention when**:
- CI checks failing repeatedly
- Backup files accumulating
- Root directory cluttered
- Contributors confused about file placement

---

**Status**: ✅ System fully operational as of February 15, 2026

**Maintenance**: Review annually, update patterns as needed
