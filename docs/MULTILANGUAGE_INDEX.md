# Multilanguage Support - Documentation Index

## Overview

This directory contains comprehensive documentation for implementing multilanguage support in KRWL> Events. The implementation follows KISS principles with a handrolled i18n solution that extends the existing multi-region infrastructure.

**Status**: Planning complete, ready for implementation
**Languages**: German (de), English (en), Czech (cs)
**Approach**: URL-based language selection + dashboard switcher

## Documentation Files

### 1. Implementation Plan ⭐ START HERE
📄 **[20260201-multilanguage-support.md](plans/20260201-multilanguage-support.md)** (15 KB)

**Purpose**: Detailed 7-phase implementation plan with task-by-task breakdown

**Contents**:
- Objective and current state analysis
- 7 phases with atomic tasks and checkboxes
- Success criteria
- Risk mitigation strategies
- Open questions to resolve
- Timeline estimates (10-15 hours)

**When to use**: Planning implementation, tracking progress

---

### 2. Technical Architecture
📄 **[MULTILANGUAGE_ARCHITECTURE.md](MULTILANGUAGE_ARCHITECTURE.md)** (19 KB)

**Purpose**: Technical design and architecture documentation

**Contents**:
- URL structure and routing
- Component responsibilities (frontend + backend)
- Translation file structure
- Language detection flow
- Integration with existing features
- Performance considerations
- Accessibility requirements

**When to use**: Understanding technical design, implementing components

---

### 3. Quick Reference Guide
📄 **[MULTILANGUAGE_QUICK_REF.md](MULTILANGUAGE_QUICK_REF.md)** (11 KB)

**Purpose**: Developer and translator quick reference

**Contents**:
- For Users: URL patterns, language switcher usage
- For Developers: Adding translatable strings, API reference
- For Translators: Translation guidelines, best practices
- For Site Builders: Build commands, configuration
- Testing checklist
- Troubleshooting guide

**When to use**: Daily development, adding translations, testing

---

### 4. Data Flow Diagrams
📄 **[MULTILANGUAGE_DATA_FLOW.md](MULTILANGUAGE_DATA_FLOW.md)** (35 KB)

**Purpose**: Visual data flow and system diagrams

**Contents**:
- Complete implementation flow (visual)
- Language detection flow diagram
- Translation lookup flow
- Backend generation flow
- URL routing matrix
- Translation file structure (visual)
- Error handling scenarios
- Performance characteristics

**When to use**: Understanding system flow, debugging, onboarding

---

### 5. Files Impact Analysis
📄 **[MULTILANGUAGE_FILES_OVERVIEW.md](MULTILANGUAGE_FILES_OVERVIEW.md)** (18 KB)

**Purpose**: Complete file-by-file impact analysis

**Contents**:
- Summary of files to create (7 new files)
- Summary of files to modify (6 existing files)
- Before/after code examples for each file
- File size impact analysis
- Build output structure changes
- Git commit strategy
- Rollback strategy
- Maintenance overhead estimates

**When to use**: Code review, understanding scope, estimating effort

---

## Quick Start

### For Implementers

1. **Read the plan**: Start with `plans/20260201-multilanguage-support.md`
2. **Understand architecture**: Review `MULTILANGUAGE_ARCHITECTURE.md`
3. **Check file impact**: Review `MULTILANGUAGE_FILES_OVERVIEW.md`
4. **Begin Phase 1**: Create i18n infrastructure
5. **Use quick reference**: Keep `MULTILANGUAGE_QUICK_REF.md` handy during development

### For Reviewers

1. **Review scope**: Read `MULTILANGUAGE_FILES_OVERVIEW.md` for impact analysis
2. **Review architecture**: Check `MULTILANGUAGE_ARCHITECTURE.md` for design decisions
3. **Review flow**: Study `MULTILANGUAGE_DATA_FLOW.md` for system behavior
4. **Review plan**: Check `plans/20260201-multilanguage-support.md` for implementation strategy

### For Translators

1. **Read guidelines**: See "For Translators" section in `MULTILANGUAGE_QUICK_REF.md`
2. **Understand structure**: Check translation file structure in `MULTILANGUAGE_ARCHITECTURE.md`
3. **Follow best practices**: Use the examples and tips in the quick reference

## Key Decisions

### URL Structure
- `/{lang}` - Language only (e.g., `/en`, `/de`, `/cs`)
- `/{lang}/{region}` - Language + region (e.g., `/en/hof`, `/de/nbg`)
- `/` - Auto-detect browser language or default to English
- `/{region}` - Backward compatible (defaults to English)

### Technology Stack
- **Frontend**: Handrolled i18n module (~200 lines, no dependencies)
- **Translation files**: Simple JSON (assets/translations/*.json)
- **Backend**: Python site generator (modified)
- **No external libraries**: Zero npm or pip dependencies

### KISS Principles
✅ Handrolled i18n (no frameworks)
✅ Simple JSON format
✅ Page reload on language switch (no SPA complexity)
✅ Inline translations (no HTTP requests)
✅ Minimal JavaScript (~5KB overhead)

## Implementation Phases

| Phase | Description | Duration | Visibility |
|-------|-------------|----------|------------|
| 1 | Create infrastructure | 2-3 hours | No change |
| 2 | Add language detection | 1-2 hours | No change |
| 3 | Translate UI components | 3-4 hours | No change* |
| 4 | Add language switcher | 1-2 hours | **Visible** |
| 5 | Generate multi-language HTML | 2-3 hours | **Visible** |
| 6 | Update routing & testing | 2-3 hours | No change |
| 7 | Tests & documentation | 1-2 hours | No change |

*Phase 3 has no visible changes if translations match existing English text

**Total**: 10-15 hours of focused work

## Open Questions

Before implementation, decide:

1. **Root URL behavior**: Auto-detect browser language or default to English?
   - **Recommendation**: Auto-detect (better UX)

2. **Language preference**: Store in localStorage for repeat visits?
   - **Recommendation**: Not in Phase 1 (keep simple)

3. **Existing URLs**: Redirect `/hof` to `/en/hof`?
   - **Recommendation**: No redirect, silent fallback

4. **Translation quality**: Use Google Translate initially?
   - **Recommendation**: Yes, refine with native speakers later

5. **Missing translations**: Fallback to English or show key name?
   - **Recommendation**: Fallback to English (graceful degradation)

## Success Criteria

Implementation is complete when:

- [ ] All 3 languages (de, en, cs) fully translated
- [ ] URL-based language selection works
- [ ] Language + region combinations work
- [ ] Language switcher in dashboard
- [ ] Current language highlighted
- [ ] All filter descriptions translated
- [ ] All dashboard content translated
- [ ] Browser language detection works
- [ ] Backward compatibility maintained
- [ ] All tests pass
- [ ] Documentation updated
- [ ] features.json updated
- [ ] Zero JavaScript errors
- [ ] Accessible (lang attributes, aria-labels)

## File Statistics

| Category | Files | Total Size |
|----------|-------|------------|
| **Documentation** | 5 | 98 KB |
| ├─ Plans | 1 | 15 KB |
| ├─ Architecture | 1 | 19 KB |
| ├─ Quick Reference | 1 | 11 KB |
| ├─ Data Flow | 1 | 35 KB |
| └─ Files Overview | 1 | 18 KB |

## Related Documentation

- **Multi-Region Infrastructure**: See `MULTI_REGION_INFRASTRUCTURE.md`
- **Feature Registry**: See `features.json` (line 610: `supportedLanguages`)
- **Project Instructions**: See `.github/copilot-instructions.md`

## Maintainer Notes

### Adding New Languages

1. Create `assets/translations/{lang}.json` (~30 min to translate)
2. Add language code to `config.json` `supportedLanguages` array
3. Regenerate site: `python3 src/event_manager.py generate`
4. Test all UI components in new language

**Total time**: ~40 minutes per language

### Updating Translations

1. Edit appropriate `assets/translations/{lang}.json` file
2. Regenerate site: `python3 src/event_manager.py generate`
3. Verify changes in browser

**Total time**: ~5 minutes per translation update

### Rollback Strategy

If needed, revert in < 5 minutes:

1. Remove new files (7 files)
2. Revert modified files: `git checkout main -- {files}`
3. Regenerate site: `python3 src/event_manager.py generate`

## Contact

For questions about this documentation or implementation:
- Review the plan and architecture docs first
- Check the quick reference for common questions
- Check the data flow diagrams for system behavior
- Check the files overview for implementation details

## Version History

- **2026-02-01**: Initial documentation created
  - Complete 7-phase implementation plan
  - Technical architecture documentation
  - Quick reference guide for developers
  - Visual data flow diagrams
  - Files impact analysis

---

**Status**: 📋 Planning complete, ready for implementation
**Next Step**: Review plan and approve to begin Phase 1
**Estimated Timeline**: 10-15 hours total
**Risk Level**: Low (backward compatible, extensive testing planned)
