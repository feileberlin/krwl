# KRWL HOF Community Events - Documentation

Welcome to the documentation for the KRWL HOF community events platform!

> 📖 **Note**: This documentation works both as standalone markdown files and in GitHub Wiki format.

## 🎯 What is KRWL HOF?

A **grassroots, mobile-first** web app for discovering local community events in Hof and surrounding region (Bavaria, Germany). Built by and for the local community - from punk concerts at Galeriehaus to farmers markets, from Off-Theater performances to VHS courses.

### ✨ Features

- 📱 **Progressive Web App**: Install on your phone like a native app
- 🗺️ **Interactive Map**: Visual overview of all events in your area
- 📱 **Mobile-First**: Designed for on-the-go event discovery
- 🌍 **Location-Based**: Filter by distance from your current location or central points (Hauptbahnhof, Rathaus)
- 🔍 **Smart Filtering**: Time-based (till sunrise, till Sunday, till full moon) and distance-based filters
- 🌐 **Bilingual**: German and English interface

## 🚀 Quick Start for Developers

Want to contribute or run it locally?

```bash
# Clone and setup
git clone https://github.com/feileberlin/krwl-hof.git
cd krwl-hof
./download-libs.sh

# Run locally
cd static
python3 -m http.server 8000
```

Open http://localhost:8000 in your browser

## 📚 Documentation

### Getting Started
- **[Setup Guide](SETUP.md)** - Complete setup instructions for development
- **[Testing](../TESTING.md)** - Comprehensive testing guide

### Core Documentation
- **[Event Scraping](SCRAPING.md)** - Guide to scraping and managing events
- **[Deployment](DEPLOYMENT.md)** - Deployment workflows and configuration
- **[Leaflet i18n](LEAFLET_I18N.md)** - Internationalization for Leaflet maps
- **[Localization](../static/LOCALIZATION.md)** - Application localization guide
- **[PWA](../static/PWA_README.md)** - Progressive Web App features

### Development
- **[Development Environment](../.github/DEV_ENVIRONMENT.md)** - Dev environment setup with VS Code, Copilot, and MCP
- **[Feature Registry](../.github/FEATURE_REGISTRY.md)** - Feature documentation and verification
- **[Deployment Guide](../.github/DEPLOYMENT.md)** - Production and preview deployment
- **[Promote Workflow](../.github/PROMOTE_WORKFLOW.md)** - Promoting changes from preview to production

## 🏗️ Project Structure

```
krwl-hof/
├── static/          # Frontend (HTML, CSS, JS) - the actual web app
├── src/             # Python backend (scraping, generation)
├── docs/            # Documentation (you are here!)
├── .github/         # GitHub workflows and configs
├── data/            # Scraped event data
└── README.md        # Project overview (auto-generated)
```

## ⚙️ Configuration

Event sources, map settings, filters - all in `static/config.json`:
- **Development**: `config.dev.json` (debug enabled, demo events for testing)
- **Production**: `config.prod.json` (optimized, real events from local venues)

## 🤝 Contributing

We welcome contributions! Whether you're adding event sources, fixing bugs, or improving the UI:

1. Fork the repository
2. Create a feature branch from `preview`
3. Make your changes (keep it simple - we follow KISS principles!)
4. Run tests: `python3 test_scraper.py --verbose`
5. Submit a pull request to `preview` branch

Know a local venue that should be included? Found a bug? Open an issue!

## 📝 About This Documentation

### Works Anywhere!
All documentation files are standard markdown that work:
- ✅ On GitHub (just browse the files)
- ✅ In your text editor (VS Code, vim, whatever you use)
- ✅ Locally after cloning
- ✅ In GitHub Wiki (automatically synced)

No special setup needed. Click links and read!

### Automatically Synced to Wiki
When changes are merged to `main`, documentation is automatically synced to the [GitHub Wiki](https://github.com/feileberlin/krwl-hof/wiki). You can read it either way - same content, your choice.

## 🔗 Links

- **Repository**: https://github.com/feileberlin/krwl-hof
- **Issues**: https://github.com/feileberlin/krwl-hof/issues
- **Pull Requests**: https://github.com/feileberlin/krwl-hof/pulls
- **Wiki**: https://github.com/feileberlin/krwl-hof/wiki

---

*For more information, see the sidebar navigation or browse the repository.*
