# PR Preview - Simple KISS Approach

> How to preview Pull Requests before merging to production

## 🎯 Overview

This project uses a **KISS (Keep It Simple, Stupid)** approach to PR previews:
- ✅ **No external services** (Netlify, Vercel, etc.)
- ✅ **No deployment complexity** - Just download and test
- ✅ **Pure GitHub** - Uses GitHub Actions artifacts
- ✅ **Automatic** - Builds on every PR update
- ✅ **Self-contained** - Download once, test offline
- ✅ **Includes** - Site preview, color variables, screenshots

## 🎛️ Control Panel

**Want to disable previews temporarily?** See [How to Disable PR Previews](./PR_PREVIEW_DISABLE.md)

**Quick disable:**
```
Repository Settings → Actions → Variables → Add:
Name: PR_PREVIEWS_ENABLED
Value: false
```

**Why disable?** To save Actions minutes during high-volume PR periods or maintenance.

---

## 🚀 How It Works

### Automatic Build

When you open or update a PR, GitHub Actions automatically:

1. **Builds the site** in development mode (with demo events)
2. **Uploads as artifact** - Available for 90 days
3. **Comments on PR** with download link and instructions

### Preview Modes

- **Development Mode** (PR Previews):
  - Includes demo events (pink markers)
  - Shows DEV watermark
  - Debug features enabled
  - Perfect for testing changes

- **Production Mode** (Main branch):
  - Real events only
  - No watermark
  - Optimized for performance
  - Deployed to GitHub Pages

## 📥 How to Test a PR Preview

### Option 1: Quick File Test (Simplest)

1. Go to the PR on GitHub
2. Click the comment from "github-actions" bot with preview link
3. Click **"Download Preview Artifact"**
4. Extract the ZIP file
5. Open `public/index.html` in your browser
6. Done! ✅

**Pros:**
- Fastest method
- No commands needed
- Works offline after download

**Cons:**
- Some features may need a local server (e.g., service worker)

### Option 2: Local Server (Recommended)

```bash
# After downloading and extracting the artifact
cd public
python3 -m http.server 8000

# Open http://localhost:8000 in your browser
```

**Pros:**
- Full feature testing
- Simulates real server environment
- Better for testing fetch/AJAX

**Cons:**
- Requires one extra command

## 🔍 What to Check in Preview

When testing a PR preview, verify:

- [ ] **Map loads** - Leaflet tiles and markers appear
- [ ] **Events display** - Event markers show on map
- [ ] **Filters work** - Distance, time, category filters
- [ ] **Speech bubbles** - Event details pop up correctly
- [ ] **Mobile view** - Resize browser to mobile width
- [ ] **Console clean** - No errors in browser DevTools (F12)
- [ ] **Accessibility** - Keyboard navigation works

## 🎨 Understanding Development Mode

PR previews use development mode, which means:

| Feature | Development | Production |
|---------|-------------|------------|
| Demo Events | ✅ Yes (pink markers) | ❌ No |
| Watermark | ✅ "DEV" badge | ✅ "PRODUCTION" |
| Debug Logging | ✅ Verbose | ❌ Minimal |
| Data Source | Both real + demo | Real only |

**This is intentional!** Demo events help test the map without relying on real event data.

## ⏱️ Artifact Retention

- **Retention:** 90 days
- **Storage:** GitHub Actions artifacts
- **Cleanup:** Automatic after expiration
- **Cost:** Free (within GitHub Actions limits)

## 🔄 Updating Preview

Every time you push to a PR branch:

1. Old preview artifact is **cancelled** (if still building)
2. New preview is built with latest changes
3. New artifact replaces the old one
4. New comment appears on PR with updated link

## 🆚 Comparison: KISS vs Other Methods

### Our Approach (KISS)
```
PR → GitHub Actions → Build → Upload Artifact → Download → Test
```
**Pros:** Simple, free, no setup, no external services
**Cons:** Manual download required

### Netlify/Vercel Approach
```
PR → External Service → Deploy → Live URL → Test
```
**Pros:** Instant live URL
**Cons:** Requires account, configuration, external dependency

### GitHub Pages Per-Branch Approach
```
PR → Build → Deploy to gh-pages-pr-123 → Live URL → Test
```
**Pros:** Live URL in GitHub
**Cons:** Complex workflow, many branches, cleanup needed

## 💡 Why This Approach?

We chose GitHub Actions artifacts because:

1. **KISS Philosophy** - Minimal moving parts
2. **No External Dependencies** - Pure GitHub
3. **No Configuration** - Works out of the box
4. **No Cleanup Needed** - Artifacts auto-expire
5. **Full Control** - Test locally, at your pace
6. **Privacy** - No external services see your code

## 🛠️ Technical Details

### Workflow File

Location: `.github/workflows/pr-preview.yml`

Triggers on:
- PR opened
- PR synchronized (new commits)
- PR reopened

Builds:
- Python environment
- Install dependencies
- Fetch Leaflet.js
- Generate static site
- Upload as artifact

### Environment Variables

For preview builds, the workflow forces:

```bash
ENVIRONMENT=development
```

This ensures:
- `config.json` uses development settings
- Demo events are included
- Debug mode is enabled

### File Structure

Artifact contains:
```
public/
├── index.html          # Main app (self-contained)
├── PREVIEW_INFO.txt    # Build metadata
└── [other assets]      # Any additional files
```

## 🐛 Troubleshooting

### "Map Loading..." Never Finishes

**Cause:** Leaflet.js not loading
**Solution:** Use local server method (Option 2)

### Demo Events Don't Appear

**Cause:** Development mode not active
**Solution:** Check PREVIEW_INFO.txt - should say "DEVELOPMENT mode"

### Artifact Download Link Missing

**Cause:** Build failed or still in progress
**Solution:** Check Actions tab for build status

### Preview is Outdated

**Cause:** New commits pushed to PR
**Solution:** Wait for new build (check Actions tab)

## 📚 Further Reading

- [GitHub Actions Artifacts Documentation](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [Project Copilot Instructions](.github/copilot-instructions.md)
- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)

## 🤝 Contributing

If you have ideas to improve the preview workflow while maintaining KISS principles:

1. Open an issue with your proposal
2. Explain how it stays simple
3. Discuss trade-offs
4. Submit a PR if approved

**Remember:** Simpler is better! 🎯
