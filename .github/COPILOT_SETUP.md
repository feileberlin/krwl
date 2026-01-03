# GitHub Copilot Configuration Guide

> Complete guide to setting up GitHub Copilot for project-aware code reviews and development

## 🎯 Overview

This project is fully configured for GitHub Copilot with comprehensive custom instructions that teach Copilot about the project's architecture, best practices, coding standards, and workflows. This guide shows you how to enable and use Copilot effectively with this project.

## 📦 What's Already Configured

This repository includes:

✅ **Comprehensive Copilot Instructions** (`.github/copilot-instructions.md`)
- 864 lines of project-specific guidance
- Architecture overview and technology stack
- Decision trees for code placement
- Anti-patterns and best practices
- Testing requirements and workflows
- Complete CLI command reference

✅ **MCP Configuration** (`.github/mcp/servers.json`)
- Model Context Protocol setup
- Automatic context file loading
- GitHub, filesystem, and memory servers

✅ **VS Code Integration** (`.vscode/settings.json`)
- Copilot enabled for all relevant file types
- Auto-completion enabled
- Recommended extensions list

✅ **Feature Registry** (`features.json`)
- Complete documentation of all project features
- Automatic validation and verification

## 🚀 Quick Start

### Step 1: Enable GitHub Copilot for Your Account

1. Go to [GitHub Copilot Settings](https://github.com/settings/copilot)
2. Subscribe to GitHub Copilot (if not already subscribed)
3. Enable Copilot for this repository

### Step 2: Install GitHub Copilot Extensions

For **VS Code** users:
```bash
# Install recommended extensions
code --install-extension github.copilot
code --install-extension github.copilot-chat
```

Or install via VS Code:
1. Open VS Code
2. Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
3. Type `ext install github.copilot`
4. Repeat for `github.copilot-chat`

For **other editors**, see: https://docs.github.com/en/copilot/using-github-copilot

### Step 3: Verify Configuration

1. Open this project in your editor
2. Open any Python or JavaScript file
3. Start typing - Copilot suggestions should appear
4. Try Copilot Chat with a project-specific question

### Step 4: Enable Copilot Pull Request Reviews (Optional)

GitHub Copilot can automatically review your pull requests:

1. Go to repository settings: https://github.com/feileberlin/krwl-hof/settings
2. Navigate to "Code and automation" → "Actions" → "General"
3. Ensure "Allow GitHub Actions to create and approve pull requests" is enabled
4. In "Pull Requests" settings, enable "Copilot for Pull Requests" (if available)

**Note**: This feature is being rolled out gradually and may not be available to all repositories yet.

## 📚 How Copilot Uses Project Instructions

### Automatic Context Loading

When you use Copilot in this project, it automatically:

1. **Reads `.github/copilot-instructions.md`** - Main instruction file
   - Understands project architecture (Python backend + Vanilla JS frontend)
   - Knows about the single entry point rule (`src/event_manager.py`)
   - Follows KISS principles
   - Respects auto-generated file policies

2. **Loads Context Files** via MCP:
   - `features.json` - What features exist
   - `config.json` - Configuration schema
   - `README.md` - Project overview
   - File structure and organization

3. **Applies Coding Standards**:
   - Python style (no type hints required, docstrings for complex functions)
   - JavaScript style (ES6+, vanilla JS only)
   - CSS style (mobile-first, CSS variables)
   - KISS principles enforcement

### What Copilot Knows About This Project

✅ **Architecture**:
- Python 3.x backend with modular design
- Vanilla JavaScript frontend (no frameworks)
- Leaflet.js for interactive maps
- Static site generation workflow

✅ **Critical Rules**:
- Never edit `static/index.html` (auto-generated)
- Always update `features.json` when adding features
- Use `src/event_manager.py` as single entry point (never create `src/main.py`)
- Edit source files in `assets/`, not `static/`

✅ **Workflows**:
- Event scraping → pending queue → editorial review → publication
- Build process: `python3 src/event_manager.py build production`
- Test requirements before committing
- Feature verification system

✅ **Best Practices**:
- KISS principles (Keep It Simple, Stupid)
- Mobile-first design
- Accessibility compliance (WCAG 2.1 Level AA)
- No hardcoded values (use config files)

## 🔧 Advanced Configuration

### Customizing Copilot Instructions

To add project-specific guidance:

1. Edit `.github/copilot-instructions.md`
2. Follow the existing structure
3. Add specific examples for common patterns
4. Document any new architectural decisions

### Adding Context Files

To add more context for Copilot:

1. Edit `.github/mcp/servers.json`
2. Add file paths to the `contextFiles` array:
   ```json
   {
     "settings": {
       "contextFiles": [
         ".github/copilot-instructions.md",
         "your-new-context-file.md"
       ]
     }
   }
   ```

### Excluding Files from Context

To reduce noise:

1. Edit `.github/mcp/servers.json`
2. Add patterns to `excludePatterns`:
   ```json
   {
     "settings": {
       "excludePatterns": [
         "**/__pycache__/**",
         "**/your-exclude-pattern/**"
       ]
     }
   }
   ```

## 💡 Using Copilot Effectively

### In Code Editor

**Inline Suggestions**:
- Start typing and Copilot will suggest completions
- Press `Tab` to accept, `Esc` to dismiss
- Copilot knows about project structure and will suggest correct paths

**Copilot Chat**:
- Press `Ctrl+I` (Windows/Linux) or `Cmd+I` (Mac) for inline chat
- Ask project-specific questions like:
  - "How do I add a new event source?"
  - "Where should I put this new scraper function?"
  - "What's the correct way to add a new frontend feature?"

**Example Questions**:
```
Q: How do I regenerate the HTML after editing CSS?
A: Run: python3 src/event_manager.py build production

Q: Where do I add a new scraping source?
A: Edit config.json, add to scraping.sources[] array

Q: Can I edit static/index.html directly?
A: No, it's auto-generated. Edit source files in assets/ instead.
```

### For Pull Request Reviews

When Copilot reviews are enabled:

1. **Automatic Reviews**: Copilot will comment on PRs with suggestions
2. **Context-Aware**: Comments follow project best practices
3. **KISS Compliance**: Copilot checks for over-engineering
4. **Architecture Alignment**: Ensures changes match project structure

**Copilot will flag**:
- ❌ Editing auto-generated files
- ❌ Creating `src/main.py` (duplicate entry point)
- ❌ Missing `features.json` updates
- ❌ Hardcoded configuration values
- ❌ Violating KISS principles

## ❓ Troubleshooting

### Copilot Not Suggesting Code

**Check**:
1. Is Copilot enabled in your editor settings?
2. Is your GitHub account subscribed to Copilot?
3. Is the file type supported? (Check `.vscode/settings.json`)
4. Try reloading the editor window

**Solution**:
```bash
# VS Code: Reload window
Ctrl+Shift+P → "Developer: Reload Window"

# Or restart your editor
```

### Copilot Suggestions Don't Follow Project Style

**Check**:
1. Is `.github/copilot-instructions.md` present?
2. Is MCP configuration correct?
3. Are you working in the repository root?

**Solution**:
- Ensure you opened the repository folder, not a subdirectory
- Verify `.github/mcp/servers.json` exists
- Try restarting your editor

### Copilot Chat Doesn't Know Project Context

**Check**:
1. MCP servers running? (They start automatically)
2. Context files accessible?
3. GitHub token set (for GitHub MCP server)?

**Solution**:
```bash
# Set GitHub token (optional, for GitHub MCP features)
export GITHUB_TOKEN=your_github_personal_access_token

# Verify context files exist
ls -la .github/copilot-instructions.md
ls -la .github/mcp/servers.json
```

### Copilot PR Reviews Not Working

**Common reasons**:
- Feature not yet available for your repository (gradual rollout)
- Repository settings don't allow Actions to create PR comments
- GitHub Copilot subscription doesn't include PR reviews

**Check**:
1. Repository Settings → Actions → General
2. Enable "Allow GitHub Actions to create and approve pull requests"
3. Check your Copilot subscription tier

## 🤝 Best Practices for Working with Copilot

### DO ✅

- **Ask specific questions** in Copilot Chat about project structure
- **Accept suggestions** that follow project patterns
- **Use Copilot** to generate boilerplate following project style
- **Review suggestions** before accepting (Copilot can make mistakes)
- **Keep instructions updated** as project evolves

### DON'T ❌

- **Blindly accept** all suggestions without review
- **Override** project conventions because Copilot suggests it
- **Skip testing** code generated by Copilot
- **Ignore** project-specific rules in copilot-instructions.md
- **Edit** copilot-instructions.md without team consensus

## 📖 Related Documentation

- [Copilot Instructions](.github/copilot-instructions.md) - Complete project guide for Copilot
- [MCP Configuration](.github/mcp/README.md) - Model Context Protocol setup
- [Features Registry](../features.json) - All implemented features
- [README](../README.md) - Project overview and setup
- [GitHub Copilot Docs](https://docs.github.com/en/copilot) - Official documentation

## 🎓 Learning Resources

### GitHub Copilot Documentation
- [Getting Started](https://docs.github.com/en/copilot/getting-started-with-github-copilot)
- [Using Copilot Chat](https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide)
- [Copilot for Pull Requests](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat-in-github)

### Model Context Protocol (MCP)
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

### Project-Specific
- [KISS Principles Checker](../src/modules/kiss_checker.py)
- [Feature Verification](../src/modules/feature_verifier.py)
- [Testing Guide](../README.md#testing)

---

**Questions or Issues?**

- Review the [Copilot Instructions](.github/copilot-instructions.md)
- Check the [Features Registry](../features.json)
- Ask in project discussions or issues

Last updated: 2026-01-03
