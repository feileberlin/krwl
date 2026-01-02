# Documentation Guide

This directory contains the documentation for the KRWL HOF community events platform.

## 📖 Documentation Philosophy

Our docs are built on one principle: **Keep It Simple & Accessible**

Just like the KRWL HOF platform itself serves the local community without barriers, our documentation should work for everyone - whether you're browsing on GitHub, reading locally, or using the wiki. No special tools, no complex setup. Just markdown files that work everywhere.

## 🎯 How It Works

The documentation works in **two modes** without any extra work:

1. **Standalone Markdown** (default - always works)
   - Browse files directly on GitHub
   - Read in any text editor
   - Clone the repo and read offline
   - Standard markdown links work everywhere
   - **No special setup needed!**

2. **GitHub Wiki** (automatically synced)
   - Optional wiki navigation sidebar
   - Same files, different view
   - Auto-synced when code is merged to `main`
   - You don't have to do anything!

**The key**: We write standard markdown. It works as files, and it works in wiki. Simple!

## 📁 File Structure

```
docs/
├── README.md              # This file - documentation guide
├── Home.md                # Wiki home page (also works standalone)
├── _Sidebar.md            # Wiki sidebar navigation (ignored by GitHub file browser)
├── _Footer.md             # Wiki footer (ignored by GitHub file browser)
├── SETUP.md               # Development setup guide
├── SCRAPING.md            # Event scraping guide
├── DEPLOYMENT.md          # Deployment guide
├── LEAFLET_I18N.md        # Leaflet internationalization
├── build_docs.py          # Documentation builder (generates README.md)
└── config.yml             # Documentation configuration
```

## 🔗 Cross-References

All documentation uses **standard markdown links** for maximum compatibility:

```markdown
[Testing Guide](../TESTING.md)
[Setup](SETUP.md)
[Deployment](../.github/DEPLOYMENT.md)
```

These links work:
- ✅ On GitHub (file browser)
- ✅ In VS Code and other editors
- ✅ In GitHub Wiki
- ✅ Locally after cloning
- ✅ In generated static sites

## 🌐 For Wiki Users

The wiki is automatically synced when changes are merged to `main`. You don't need to do anything!

**First-time setup?** If you're the repository owner and the Wiki needs to be initialized, see **[Wiki Setup Guide](WIKI_SETUP.md)** for the one-time setup step.

Want to manually sync? We have a script for that:

```bash
# From repository root
./scripts/sync-to-wiki.sh
```

The script copies all docs to the wiki repository and shows you what changed. Then you can review and push.

## 📝 Writing Documentation

Keep it simple and accessible! Like serving the Hof community, write docs that anyone can understand.

### The Rules

1. **Use standard markdown links**
   - ✅ `[Setup Guide](SETUP.md)`
   - ✅ `[Testing](../TESTING.md)`
   - ❌ Don't use `[[Wiki Style]]` in normal content

2. **Use relative paths**
   - Same directory: `[Setup](SETUP.md)`
   - Parent directory: `[Testing](../TESTING.md)`
   - It just works!

3. **Write clearly**
   - Use simple language
   - Explain technical terms
   - Remember: community first, not complexity

4. **Test your links**
   - Click them on GitHub - do they work?
   - Open in VS Code preview - do they work?
   - If yes to both, you're good!

### Adding New Documentation

1. Create `.md` file in appropriate location
2. Use standard markdown links
3. Add entry to `_Sidebar.md` (for wiki navigation)
4. Reference from relevant existing docs
5. Test links work on GitHub file browser

## 🔍 Documentation Structure

### Getting Started
- **[Home](Home.md)** - Overview and quick start
- **[Setup](SETUP.md)** - Development environment setup
- **[Testing](../TESTING.md)** - Comprehensive testing guide

### Core Documentation
- **[Scraping](SCRAPING.md)** - Event scraping and management
- **[Deployment](DEPLOYMENT.md)** - Deployment workflows
- **[Leaflet i18n](LEAFLET_I18N.md)** - Map internationalization
- **[Localization](../static/LOCALIZATION.md)** - App localization
- **[PWA](../static/PWA_README.md)** - Progressive Web App features

### Development
- **[Dev Environment](../.github/DEV_ENVIRONMENT.md)** - VS Code, Copilot, MCP
- **[Feature Registry](../.github/FEATURE_REGISTRY.md)** - Feature documentation
- **[Deployment Guide](../.github/DEPLOYMENT.md)** - Production deployment
- **[Promote Workflow](../.github/PROMOTE_WORKFLOW.md)** - Preview to production

## 🛠️ Documentation Builder

The `build_docs.py` script generates the main README.md from templates:

```bash
# Validate documentation
python3 docs/build_docs.py --validate

# Generate README.md
python3 docs/build_docs.py
```

This is separate from the wiki functionality - the builder creates the repository README.

## ✅ Quick Tips

1. **Docs work standalone** - Always! No wiki required
2. **Use standard links** - `[Text](file.md)` not `[[Wiki Style]]`
3. **Test locally** - Preview in your editor before committing
4. **Keep it simple** - Clear language, simple structure (KISS principle!)
5. **Wiki syncs automatically** - Merge to main, done!

## 🆘 Troubleshooting

### "My links don't work on GitHub!"

Check:
- Did you include the `.md` extension? (`SETUP.md` not just `SETUP`)
- Is the relative path correct? (count the `../` carefully)
- Does the file actually exist?

### "I want to update the wiki manually"

```bash
./scripts/sync-to-wiki.sh
cd /tmp/krwl-hof.wiki
git push
```

### "Where's the sidebar when I browse files?"

`_Sidebar.md` only shows up in the wiki. When browsing files on GitHub, just use the links in each document. Both ways work!

## 📚 Additional Resources

- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [GitHub Wiki Documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Remember**: Documentation should always work standalone. Wiki is just an optional enhancement!
