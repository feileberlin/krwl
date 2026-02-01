# Architectural Decision Records (ADRs)

## What Are ADRs?

Architectural Decision Records (ADRs) document significant architectural and design decisions made during the development of KRWL HOF. They capture the **context**, **decision**, and **consequences** of each choice to help future contributors understand why things are the way they are.

## Why ADRs?

- **Preserve Context**: Understand WHY decisions were made, not just WHAT was implemented
- **Avoid Repeating Debates**: Document the reasoning behind choices to prevent revisiting settled discussions
- **Onboarding**: Help new contributors understand architectural philosophy quickly
- **Change Management**: Make it clear when and why to revisit old decisions

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-XXX: [Title]

**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Date**: YYYY-MM-DD
**Deciders**: [Who made this decision]
**Tags**: [Relevant tags: frontend, backend, infrastructure, etc.]

## Context

What is the issue we're addressing? What factors are we considering?

## Decision

What did we decide to do? Be specific and clear.

## Consequences

### Positive
- What benefits do we get from this decision?

### Negative
- What trade-offs or limitations does this impose?

### Neutral
- What else changes as a result?

## Alternatives Considered

What other options did we evaluate and why were they rejected?

## Related Decisions

Links to related ADRs or features.json entries.
```

## ADR Index

### Active ADRs

- [ADR-001: Fallback List When Map Fails](./001-fallback-list-when-map-fails.md) - Progressive enhancement for map failures
- [ADR-002: Vanilla JS Over Frameworks](./002-vanilla-js-over-frameworks.md) - KISS principle for frontend
- [ADR-003: Single Entry Point](./003-single-entry-point.md) - Unified CLI/TUI architecture

### Deprecated ADRs

*(None yet)*

## Creating New ADRs

1. Copy the template: `cp docs/adr/template.md docs/adr/XXX-kebab-case-title.md`
2. Number sequentially (next available: ADR-004)
3. Fill in all sections with specific details
4. Update this index (add link below)
5. Link from relevant documentation (README, features.json, etc.)

See [template.md](./template.md) for the complete ADR structure.

## ADR Lifecycle

- **Proposed**: Under discussion, not yet implemented
- **Accepted**: Decision made and implemented
- **Deprecated**: No longer follows current practice
- **Superseded**: Replaced by a newer ADR (link to successor)

## References

- [ADR GitHub Org](https://adr.github.io/) - More about the ADR pattern
- [features.json](../../features.json) - Feature registry with dependencies
- [DEPENDENCIES.md](../../DEPENDENCIES.md) - Module dependency maps
- [.github/copilot-instructions.md](../../.github/copilot-instructions.md) - Project conventions
