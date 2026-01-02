# GitHub Wiki Setup Guide

## The Issue

After implementing GitHub Wiki-compatible documentation in PR #31, the Wiki tab shows up in the repository but the documentation doesn't appear yet. This is a **normal situation** that requires a one-time initialization step.

## Why This Happens

GitHub Wiki is actually a **separate Git repository** (`feileberlin/krwl-hof.wiki.git`) from your main repository. Until someone manually creates the first Wiki page through GitHub's UI, this repository doesn't exist yet, and automated workflows cannot push documentation to it.

## Solution: Initialize the Wiki

**Repository owner needs to perform this ONE-TIME setup:**

### Option 1: Via GitHub UI (Recommended - Simplest)

1. Go to https://github.com/feileberlin/krwl-hof/wiki
2. Click the **"Create the first page"** button
3. Enter any title (e.g., "Home") and content (e.g., "Initializing wiki...")
4. Click **"Save Page"**

That's it! The Wiki repository is now initialized. The automated workflow will sync all documentation on the next push to `main`, or you can trigger it manually.

### Option 2: Manual Sync (For immediate update)

After initializing via Option 1, or if you want to sync immediately:

```bash
# From repository root
./scripts/sync-to-wiki.sh

# Follow the prompts:
# 1. Review changes shown
# 2. Commit: cd /tmp/krwl-hof.wiki && git commit -am 'Initial documentation sync'
# 3. Push: git push
```

### Option 3: Trigger Automated Workflow

The workflow `.github/workflows/docs.yml` syncs documentation automatically, but you can also trigger it manually:

1. Go to https://github.com/feileberlin/krwl-hof/actions/workflows/docs.yml
2. Click **"Run workflow"**
3. Select branch: `main`
4. Enable **"Sync documentation to GitHub Wiki"** (should be `true` by default)
5. Click **"Run workflow"**

## What Gets Synced

Once initialized, the following documentation will appear in the Wiki:

### Main Documentation Files (from `docs/` directory)
- `Home.md` - Wiki home page with project overview
- `SETUP.md` - Development setup guide
- `SCRAPING.md` - Event scraping guide
- `DEPLOYMENT.md` - Deployment workflows
- `LEAFLET_I18N.md` - Map internationalization
- `WIKI_SETUP.md` - This guide
- `_Sidebar.md` - Wiki navigation sidebar
- `_Footer.md` - Wiki footer

### Root Documentation
- `TESTING.md` - Testing guide

### Static Documentation (flattened with prefix)
- `Static-LOCALIZATION.md` - Application i18n guide (from `static/LOCALIZATION.md`)
- `Static-PWA.md` - Progressive Web App features (from `static/PWA_README.md`)

### GitHub Documentation (flattened with prefix)
- `Dev-Environment.md` - Development environment setup (from `.github/DEV_ENVIRONMENT.md`)
- `Dev-Feature-Registry.md` - Feature registry system (from `.github/FEATURE_REGISTRY.md`)
- `Dev-Deployment.md` - Deployment guide (from `.github/DEPLOYMENT.md`)
- `Dev-Promote-Workflow.md` - Promote preview workflow (from `.github/PROMOTE_WORKFLOW.md`)

> **Note**: GitHub Wiki requires all pages at the root level. Files from subdirectories are copied with prefixes to maintain organization while staying flat.

## Automated Sync

After initialization, documentation is automatically synced to Wiki:

- **Trigger**: Push to `main` branch that modifies documentation files
- **Workflow**: `.github/workflows/docs.yml` (lines 88-134)
- **Process**:
  1. Detect documentation changes in `main` branch
  2. Clone Wiki repository to `/tmp/wiki`
  3. Copy all documentation files
  4. Commit and push to Wiki repository
  5. Documentation appears in https://github.com/feileberlin/krwl-hof/wiki

## Troubleshooting

### "Wiki tab shows but is empty"
✅ **Solution**: Follow Option 1 above - you just need to initialize the Wiki once.

### "Workflow says 'Wiki is up to date' but pages are missing"
✅ **Solution**: The Wiki might have been initialized but needs a fresh sync. Use Option 2 (manual sync) or Option 3 (trigger workflow).

### "Permission denied when pushing to wiki"
✅ **Solution**: The automated workflow uses `GITHUB_TOKEN` which has required permissions. If using manual sync, ensure you're authenticated: `gh auth login`

### "Can't find the Wiki tab"
✅ **Solution**: 
1. Check repository settings → Features → ensure "Wikis" is checked
2. Repository must be public (Wiki feature is enabled for this public repo)

## Verification

After initialization and sync, verify:

1. Visit https://github.com/feileberlin/krwl-hof/wiki
2. You should see:
   - **Home page** with project overview
   - **Sidebar** with navigation links  
   - **Footer** with community information
   - All documentation files listed

## Dual-Format Design

Our documentation works both **standalone** and in **Wiki format**:

✅ **Standalone**: Browse `docs/` directory on GitHub or locally  
✅ **Wiki**: Auto-synced to https://github.com/feileberlin/krwl-hof/wiki

No special setup needed for standalone use - documentation is already there! Wiki is just an additional convenient way to browse it.

## Technical Notes

### Wiki Repository Details
- **Repository**: `https://github.com/feileberlin/krwl-hof.wiki.git`
- **Type**: Separate Git repository (not a branch of main repo)
- **Authentication**: Uses GitHub Actions `GITHUB_TOKEN` for automated sync
- **Manual Clone**: `git clone https://github.com/feileberlin/krwl-hof.wiki.git`

### Sync Script (`sync-to-wiki.sh`)
- Clones wiki to `/tmp/krwl-hof.wiki` by default
- Copies all documentation maintaining directory structure
- Shows diff before commit
- Supports custom wiki directory path

### Workflow Configuration
```yaml
# .github/workflows/docs.yml
- name: Sync documentation to Wiki
  if: |
    github.event_name == 'push' && 
    github.ref == 'refs/heads/main' && 
    (steps.docs_changed.outputs.changed == 'true' || github.event.inputs.sync_to_wiki == 'true')
```

## Summary

**For Repository Owner**: Just visit the Wiki tab and click "Create the first page" once. Everything else happens automatically! 🚀

**For Contributors**: Documentation changes in PRs to `main` will automatically sync to Wiki after merge. No action needed.
