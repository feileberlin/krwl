## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🎨 UI/UX improvement
- [ ] ♻️ Code refactoring
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test addition or improvement
- [ ] 🔧 Configuration change
- [ ] 🏗️ Infrastructure/Build change

## Checklist

<!-- Check all items that apply to your PR -->

### Pre-Implementation ✅

- [ ] Read through the [Copilot Instructions](.github/copilot-instructions.md)
- [ ] Identified which module(s) need changes
- [ ] Checked if similar functionality already exists
- [ ] Reviewed KISS principles

### Implementation ✅

- [ ] Edited source files only (never auto-generated files like `static/index.html`)
- [ ] Added/updated tests in `tests/` directory
- [ ] Followed existing code style and patterns
- [ ] Kept changes minimal and focused
- [ ] Added docstrings for complex functions
- [ ] Used `src/event_manager.py` for CLI commands (never created `src/main.py`)

### Post-Implementation ✅

- [ ] Updated `features.json` if adding new features
- [ ] Ran relevant tests: `python3 tests/test_*.py --verbose`
- [ ] Verified KISS compliance: `python3 src/modules/kiss_checker.py` (if applicable)
- [ ] Ran feature verification: `python3 src/modules/feature_verifier.py --verbose`
- [ ] If frontend changes: Ran `python3 src/event_manager.py build production`
- [ ] Tested manually (TUI, generated HTML, etc.)
- [ ] Updated documentation if needed

### Pull Request Requirements ✅

- [ ] All tests pass
- [ ] No references to `src/main.py` exist
- [ ] `features.json` is up to date (if applicable)
- [ ] Auto-generated files are committed if changed
- [ ] KISS principles followed
- [ ] Ready for code review

## Critical Checks (Auto-Validation)

<!-- These are automatically validated by project rules -->

### File Edit Policy

- [ ] ✅ **Did NOT** edit `static/index.html` directly
- [ ] ✅ **Did NOT** create `src/main.py` (duplicate entry point)
- [ ] ✅ **Did NOT** create top-level Python files outside `src/`
- [ ] ✅ **DID** edit source files in `assets/` for frontend changes
- [ ] ✅ **DID** update `features.json` for new features

### Architecture Compliance

- [ ] Backend changes are in `src/modules/` (not in `src/event_manager.py` unless CLI/TUI related)
- [ ] Frontend changes are in `assets/` directory
- [ ] Configuration changes use `config.json` (not hardcoded)
- [ ] Layers are properly separated (no HTML in scraper, etc.)

## Testing

<!-- Describe the testing you performed -->

### Test Commands Run

```bash
# Example - replace with actual commands you ran
python3 tests/test_scraper.py --verbose
python3 tests/test_filters.py --verbose
```

### Manual Testing

<!-- Describe manual testing performed -->

- [ ] Tested in development mode
- [ ] Tested in production mode
- [ ] Tested on mobile viewport (if UI changes)
- [ ] Tested keyboard navigation (if UI changes)
- [ ] Verified accessibility (if UI changes)

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

## Related Issues

<!-- Link to related issues or PRs -->

Closes #
Related to #

## Additional Context

<!-- Add any other context about the PR here -->

## Reviewer Notes

<!-- Specific things you want reviewers to focus on -->

---

**For Reviewers**: Please verify:
- [ ] Changes follow [Copilot Instructions](.github/copilot-instructions.md)
- [ ] No anti-patterns detected (see copilot-instructions.md)
- [ ] KISS principles maintained
- [ ] Tests are comprehensive
- [ ] Documentation is updated

**GitHub Copilot**: Automated review enabled. Copilot will comment based on project best practices defined in `.github/copilot-instructions.md`.
