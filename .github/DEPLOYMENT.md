# Deployment Guide

Simple two-step deployment workflow: **preview** → **production**

## Overview

This repository uses a safe two-step deployment process:

- **`main` branch** = Production site (deployed to root via GitHub Pages)
- **`preview` branch** = Preview environment (self-contained HTML file)

## Quick Start

### Making Changes

1. **Create feature branch** from `preview`
2. **Make your changes** and test locally
3. **Submit PR to `preview`** branch
4. **Merge to preview** → auto-generates `preview/index.html`
5. **Download and test** `preview/index.html` locally
6. **Run "Promote Preview"** workflow → creates PR to `main`
7. **Merge to main** → deploys production + makes preview available at `/preview/`

## Configuration Files

### Production (`config.prod.json`)
- **Debug mode**: OFF
- **Performance**: Maximum speed
- **Caching**: Enabled
- **Data source**: Real events only
- **Used by**: `main` branch static files
- **Domain**: Custom domain via CNAME

### Preview (`config.preview.json`)
- **Debug mode**: ON (console logging)
- **Performance**: Caching disabled for testing
- **Data source**: Both real and demo events
- **Used by**: Embedded in `preview/index.html`
- **Deployment**: Self-contained single HTML file

### Data Source Options (Preview Only)

Preview mode supports three data source configurations:

1. **`"source": "real"`** - Load only real scraped events
2. **`"source": "demo"`** - Load only demo events with current timestamps
3. **`"source": "both"`** - Load both real and demo events (default for preview)

Demo events are automatically generated from real event templates with fresh timestamps, making them perfect for testing time-based features.

## Workflows

### 1. Production Deploy
**Method**: GitHub Pages configured to deploy from `main` branch

**What it does**:
- Serves `static/` directory at root
- Uses `config.prod.json` (optimized, no debug)
- Includes CNAME for custom domain
- Serves `preview/index.html` at `/preview/` (if present)

**Result**: Fast production site at `krwl.in` + preview at `krwl.in/preview/`

### 2. Preview Generation (`generate-preview.yml`)
**Triggers**: Push to `preview` branch, manual dispatch

**What it does**:
- Generates fresh demo events from real event templates
- Runs `scripts/generate_preview.py` to create self-contained HTML
- Inlines all CSS, JavaScript, config, and event data
- Commits `preview/index.html` to preview branch (single file, ~260KB)

**Result**: Self-contained HTML file - NO DEPLOYMENT, just download and open

**To test preview**:
1. Download `preview/index.html` from preview branch
2. Open in browser (works completely offline, no server needed)
3. OR merge to main to make it available at `krwl.in/preview/`

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
