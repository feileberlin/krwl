# Implementation Notes

This directory contains **completed implementation notes** documenting work that has been finished.

## Purpose

Implementation notes serve as a historical record of:
- What was implemented and why
- Key decisions made during implementation
- Challenges encountered and solutions
- Testing and verification results
- Migration notes for significant changes

## File Naming Convention

**Required format**: `YYYY-MM-DD-description.md`

Examples:
- `2026-02-15-ai-translation-implementation.md`
- `2026-02-16-search-feature-completed.md`
- `2026-03-01-database-migration.md`

## When to Create Notes

✅ **DO create notes when:**
- Completing a major feature implementation
- Finishing a significant refactor
- Documenting a complex migration
- Recording important technical decisions
- Summarizing a multi-session implementation

❌ **DON'T create notes for:**
- Minor bug fixes (use commit messages)
- Trivial changes (use commit messages)
- Work in progress (use `/tmp/` or docs/plans/)
- General documentation (use `docs/*.md`)

## Relationship to Other Documentation

| Directory | Purpose | Timing |
|-----------|---------|--------|
| `docs/notes/` | **Implementation notes** | After completion |
| `docs/plans/` | **Implementation plans** | Before starting |
| `docs/adr/` | **Architecture decisions** | When making architectural choice |
| `docs/` | **Permanent documentation** | Ongoing, kept up-to-date |
| `/tmp/` | **Temporary scratchpad** | During work, never committed |

## Content Guidelines

Each note should include:

1. **Date and Overview** - When was this completed and what was done
2. **Implementation Details** - What code was changed
3. **Key Decisions** - Important choices made
4. **Testing/Verification** - How it was validated
5. **Related Links** - PRs, issues, ADRs, commits

## Example Structure

```markdown
# Feature Name Implementation - February 15, 2026

## Overview
Brief description of what was implemented and why.

## Implementation Details
- File changes
- Key modules modified
- New dependencies added

## Key Decisions
- Why approach X was chosen over Y
- Trade-offs considered

## Testing
- Tests added
- Manual verification performed
- Results

## Related
- PR #123
- Commit abc123
- ADR-005
```

## Migration from Root Directory

**Historical note**: Previously, summary files were created in the root directory (e.g., `AI_TRANSLATION_IMPLEMENTATION_SUMMARY.md`). These have been moved here with proper date prefixes to prevent root directory clutter.

## See Also

- `docs/plans/README.md` - For planning documentation
- `docs/adr/README.md` - For architectural decisions
- `.github/copilot-instructions.md` - Repository Cleanliness section
