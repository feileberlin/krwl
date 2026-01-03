# GitHub Copilot Quick Reference

> Quick links and commands for using GitHub Copilot with KRWL HOF project

## 📚 Documentation

- **[Complete Setup Guide](.github/COPILOT_SETUP.md)** - Start here for full configuration
- **[Copilot Instructions](.github/copilot-instructions.md)** - 864 lines of project guidance
- **[MCP Configuration](.github/mcp/README.md)** - Model Context Protocol setup
- **[PR Template](.github/pull_request_template.md)** - Use when creating pull requests
- **[CODEOWNERS](.github/CODEOWNERS)** - Automatic review assignments

## ⚡ Quick Start

```bash
# 1. Install Copilot extensions
code --install-extension github.copilot
code --install-extension github.copilot-chat

# 2. Open this project in VS Code
code .

# 3. Start coding - Copilot will automatically load project context
```

## 🎯 What Copilot Knows

✅ **Architecture**: Python backend + Vanilla JS frontend + Leaflet maps  
✅ **Entry Point**: Only `src/event_manager.py` (never create `src/main.py`)  
✅ **Auto-Generated**: Never edit `static/index.html`  
✅ **Source Files**: Edit in `assets/`, not `static/`  
✅ **Features**: Always update `features.json` for new features  
✅ **KISS Principles**: Keep it simple, avoid over-engineering  
✅ **Mobile First**: Design for mobile, enhance for desktop  
✅ **Testing**: Run tests before committing  

## 💬 Example Copilot Questions

```
Q: How do I add a new event source?
A: Edit config.json → scraping.sources[] → Add new source object

Q: Where do I put a new scraper function?
A: src/modules/scraper.py

Q: How do I rebuild the HTML after CSS changes?
A: python3 src/event_manager.py build production

Q: Can I create src/main.py?
A: No! Use src/event_manager.py (single entry point rule)
```

## 🚫 Anti-Patterns (Copilot Will Flag)

❌ Editing `static/index.html` directly  
❌ Creating `src/main.py`  
❌ Top-level Python files outside `src/`  
❌ Missing `features.json` updates  
❌ Hardcoded configuration values  
❌ Mixing backend and frontend code  

## ✅ Best Practices (Copilot Enforces)

✅ Edit source files in `assets/` for frontend changes  
✅ Use `config.json` for all configuration  
✅ Update `features.json` when adding features  
✅ Follow KISS principles  
✅ Test before committing  
✅ Mobile-first design  

## 🔧 Commands Reference

```bash
# Feature verification
python3 scripts/verify_features.py --verbose

# KISS compliance check
python3 scripts/check_kiss.py --verbose

# Run tests
python3 tests/test_scraper.py --verbose
python3 tests/test_filters.py --verbose

# Build production
python3 src/event_manager.py build production

# Build development (with demo events)
python3 src/event_manager.py build development
```

## 🔍 Key Files Copilot Uses

1. **`.github/copilot-instructions.md`** - Main instruction file (auto-loaded)
2. **`.github/COPILOT_SETUP.md`** - Setup guide
3. **`features.json`** - Feature registry
4. **`config.json`** - Configuration schema
5. **`README.md`** - Project overview

## 📖 More Information

See [.github/COPILOT_SETUP.md](.github/COPILOT_SETUP.md) for:
- Complete setup instructions
- Troubleshooting guide
- Advanced configuration
- PR review setup
- Best practices

---

**Quick Tip**: When you start typing in this project, Copilot automatically loads the project context and will suggest code that follows our architecture and best practices!
