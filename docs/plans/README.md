# Implementation Plans

This directory contains **implementation plans** for features and changes that are being planned or are in progress.

## Purpose

Implementation plans serve as blueprints for:
- Feature development roadmaps
- Complex refactoring strategies
- Multi-phase implementations
- Architectural changes
- Breaking changes that need careful planning

## File Naming Convention

**Required format**: `YYYYMMDD-feature-name.md` or `feature-name-plan.md`

Examples:
- `20260201-multilanguage-support.md`
- `20260215-search-feature-plan.md`
- `database-migration-plan.md`

## When to Create Plans

✅ **DO create plans when:**
- Starting a major feature
- Planning a complex refactor
- Designing a multi-phase implementation
- Coordinating work across multiple sessions
- Breaking down large changes into tasks

❌ **DON'T create plans for:**
- Simple bug fixes (just fix them)
- Trivial changes (commit and document)
- Brainstorming (use `/tmp/` or work in-memory)

## Relationship to Other Documentation

| Directory | Purpose | Timing |
|-----------|---------|--------|
| `docs/plans/` | **Implementation plans** | Before starting work |
| `docs/notes/` | **Implementation notes** | After completion |
| `docs/adr/` | **Architecture decisions** | When making architectural choice |
| `docs/` | **Permanent documentation** | Ongoing, kept up-to-date |

## Lifecycle

1. **Create** - Before starting implementation
2. **Update** - As work progresses (mark phases as complete)
3. **Complete** - All tasks finished
4. **Archive** - Move to `docs/notes/` or delete if superseded by permanent docs

## Plan Structure

Use this template for new plans:

```markdown
# Feature Name Implementation Plan

**Created**: YYYY-MM-DD  
**Status**: Planning / In Progress / Complete  
**Owner**: @username (optional)

## Overview
Brief description of what will be implemented and why.

## Goals
- Goal 1
- Goal 2
- Goal 3

## Non-Goals
- What this plan does NOT cover

## Implementation Phases

### Phase 1: Foundation
- [ ] Task 1.1
- [ ] Task 1.2

### Phase 2: Core Features
- [ ] Task 2.1
- [ ] Task 2.2

### Phase 3: Testing & Polish
- [ ] Task 3.1
- [ ] Task 3.2

## Technical Approach
Key technical decisions and approach.

## Risks & Mitigation
- Risk 1: Mitigation strategy
- Risk 2: Mitigation strategy

## Testing Strategy
How this will be tested.

## Related
- Issue #123
- ADR-005
- Related plan: other-plan.md
```

## Agent Integration

This directory is used by GitHub Copilot agents:
- **planning-agent.md** - Creates structured plans here
- **implementation-agent.md** - References plans during implementation
- **unified-agent.md** - Creates and executes plans

## Checklist Format

Plans use markdown checklists (`- [ ]` / `- [x]`) for tracking progress:

```markdown
## Phase 1: Setup
- [x] Task 1 (completed)
- [x] Task 2 (completed)
- [ ] Task 3 (in progress)

## Phase 2: Implementation  
- [ ] Task 4 (not started)
- [ ] Task 5 (not started)
```

## Updating Plans

Plans are **living documents** during implementation:
- ✅ Mark tasks as complete: `- [x]`
- ✅ Add discovered tasks as needed
- ✅ Update status in header
- ✅ Add notes about blockers or decisions

## Archiving Completed Plans

When a plan is fully executed:

**Option 1**: Move to docs/notes/
```bash
mv docs/plans/feature-plan.md docs/notes/2026-02-15-feature-completed.md
```

**Option 2**: Delete if documented elsewhere
```bash
# If feature is documented in permanent docs (docs/*.md)
git rm docs/plans/obsolete-plan.md
```

## See Also

- `docs/notes/README.md` - For completed implementation notes
- `docs/adr/README.md` - For architectural decisions
- `.github/agents/planning-agent.md` - Planning agent instructions
- `.github/copilot-instructions.md` - Repository Cleanliness section
