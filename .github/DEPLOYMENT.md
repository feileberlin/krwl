# Deployment Guide

Simple two-step deployment workflow: **preview** → **production**

## Overview

This repository uses a safe two-step deployment process:

- **`main` branch** = Production site (fast, optimized, no debugging)
- **`preview` branch** = Shared preview environment (debugging enabled, published at `/preview/`)

## Quick Start

### Making Changes

1. **Create feature branch** from `preview`
2. **Make your changes** and test locally
3. **Submit PR to `preview`** branch
4. **Merge to preview** → auto-deploys to `/preview/` path
5. **Test preview site** thoroughly
6. **Run "Promote Preview"** workflow → creates PR to `main`
7. **Merge to main** → deploys to production

## Configuration Files

### Production (`config.prod.json`)
- **Debug mode**: OFF
- **Performance**: Maximum speed
- **Caching**: Enabled
- **Data source**: Real events only
- **Used by**: `main` branch
- **Domain**: Custom domain via CNAME

### Development (`config.dev.json`)
- **Debug mode**: ON (console logging)
- **Performance**: Caching disabled for testing
- **Data source**: Both real and demo events
- **Used by**: `preview` branch
- **Domain**: GitHub Pages `/preview/` path (no CNAME)

### Data Source Options (Dev Mode Only)

Development mode supports three data source configurations:

1. **`"source": "real"`** - Load only real scraped events
2. **`"source": "demo"`** - Load only demo events with current timestamps
3. **`"source": "both"`** - Load both real and demo events (default for dev)

Demo events are automatically generated from real event templates with fresh timestamps, making them perfect for testing time-based features.

## Workflows

### 1. Production Deploy (`deploy-pages.yml`)
**Triggers**: Push to `main`, manual dispatch

**What it does**:
- Copies `static/` → `publish/`
- Uses `config.prod.json` (optimized, no debug)
- Includes CNAME for custom domain
- Deploys to GitHub Pages root

**Result**: Fast production site at custom domain

### 2. Preview Deploy (`deploy-preview.yml`)
**Triggers**: Push to `preview`, manual dispatch

**What it does**:
- Copies `static/` → `publish/preview/`
- **Generates fresh demo events** from real event templates
- Uses `config.dev.json` (debug enabled, real+demo data)
- NO CNAME (avoids domain conflict)
- Injects `<base href="/preview/">` tag
- Deploys to GitHub Pages `/preview/` path

**Result**: Debug-enabled preview at `yourdomain.com/preview/` with fresh demo events

### 3. Promote Preview (`promote-preview.yml`)
**Triggers**: Manual dispatch only

**What it does**:
- Creates PR from `preview` → `main`
- Optional auto-merge (fails gracefully with branch protection)

**Usage**:
```
Actions → Promote Preview to Production → Run workflow
```

**📚 Detailed Guide**: See [PROMOTE_WORKFLOW.md](PROMOTE_WORKFLOW.md) for complete documentation on:
- How the workflow works internally
- When and how to use it
- Auto-merge vs manual review
- Troubleshooting
- Best practices

## Debugging Features

### In Preview Mode
When using `config.dev.json` (preview branch):

- **Debug logs** appear in browser console with `[KRWL Debug]` prefix
- **Title shows** `[DEBUG MODE]` indicator
- **Data source** shows which events are loaded (real/demo/both)
- **Demo events** are marked with `[DEMO]` prefix in titles
- **Fresh timestamps** on demo events (regenerated on each deploy)
- **Console logs**:
  - Config loaded
  - Data source mode
  - Events loading/filtering
  - Distance calculations
  - Filter reasons

### In Production Mode
When using `config.prod.json` (main branch):

- **No debug logs** (maximum performance)
- **Caching enabled**
- **Optimized for speed**

## Local Testing

### Test with Debug Mode and Demo Data
```bash
# Generate fresh demo events
python3 generate_demo_events.py > static/events.demo.json

# Serve static/ directory locally
python3 -m http.server 8000

# Or use any local server
npx serve static
```

**Use development config**:
```bash
cp config.dev.json static/config.json
```

**Access**: `http://localhost:8000`
**Check console**: Debug logs should appear
**Demo events**: Look for [DEMO] prefix in event titles

### Test with Production Config
```bash
cp config.prod.json static/config.json
```

**Check**: No debug logs should appear (fast mode)

## Security Notes

⚠️ **Never commit secrets** to repository

- API keys → Use repository secrets
- Tokens → GitHub Actions secrets
- Credentials → Environment variables

✓ **Safe in repo**:
- Public config files
- Sample data
- Static assets

## Troubleshooting

### Preview site shows 404
- Check workflow logs: `Actions → Deploy Preview`
- Verify `publish/preview/index.html` exists in logs
- Base tag should be `<base href="/preview/">`

### Production site missing config
- Check `config.prod.json` exists in repo root
- Verify workflow copies it: see `deploy-pages.yml` logs

### Assets not loading in preview
- Base tag might be missing
- Check: `view-source:` of `/preview/` page
- Should see: `<base href="/preview/">`

### Debug mode not working
- Check which config is loaded: Network tab → `config.json`
- Verify `"debug": true` in config
- Check console for `[KRWL Debug]` messages

## Manual Steps After Setup

### First Time Setup

1. **Disable old workflows** (if any):
   ```bash
   mv .github/workflows/old-deploy.yml .github/workflows/old-deploy.yml.disabled
   ```

2. **Create preview branch**:
   ```bash
   git checkout -b preview
   git push -u origin preview
   ```

3. **Configure GitHub Pages**:
   - Repository Settings → Pages
   - Source: GitHub Actions
   - Custom domain: (if applicable)

4. **Set branch protection** (recommended):
   - Protect `main` branch
   - Require PR reviews
   - Prevent direct pushes

## Workflow Diagram

```
feature-branch
     ↓
   preview (test here with debug enabled)
     ↓
   [Test thoroughly at /preview/]
     ↓
   [Run Promote workflow]
     ↓
   PR: preview → main
     ↓
   main (production with max performance)
     ↓
   [Production site live]
```

## Tips

- **Keep preview clean**: Only merge tested features
- **Test thoroughly**: Preview has debug mode for a reason
- **Production deploys**: Only via promotion workflow
- **Emergency fixes**: Can merge directly to main if needed
- **Check performance**: Production should be noticeably faster

## Questions?

- Check workflow logs in Actions tab
- Review this guide
- Test locally first
- Use debug mode to troubleshoot
