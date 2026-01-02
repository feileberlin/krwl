# Quick Reference: Documentation & GitHub About

## Generate README.md

```bash
# Generate README.md only
python3 scripts/generate_readme.py

# Generate README.md AND update GitHub About section
export GITHUB_TOKEN='your_token_here'
python3 scripts/generate_readme.py --update-github-about
```

## Get GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Update Repository Details"
4. Scope: Check "repo" (Full control of private repositories)
5. Click "Generate token"
6. Copy the token and export it:
   ```bash
   export GITHUB_TOKEN='ghp_your_token_here'
   ```

## What Gets Updated

When using `--update-github-about`:

- **Repository Description**: 
  Community events scraper and viewer with geolocation filtering. Mobile-first PWA for discovering local events in Hof, Bavaria. Live at krwl.in

- **Homepage URL**: 
  https://krwl.in

- **Topics** (11 tags):
  pwa, progressive-web-app, events, community, geolocation, leaflet, python, javascript, mobile-first, accessibility, i18n

## Features

- ✅ Single command for everything
- ✅ Auto-generates README from config.json
- ✅ Includes CLI help dynamically
- ✅ Updates GitHub via API
- ✅ Graceful degradation (works without token)
- ✅ Clear error messages

## Files

- `scripts/generate_readme.py` - The unified generator script
- `.github/ABOUT.md` - Documentation for manual setup
- `.github/repository-settings.json` - Reference configuration (read-only)

## KISS Principle

One script, one command, everything integrated. No separate tools needed.
