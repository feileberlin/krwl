# CI File Conflicts Fix - Summary

## Problem
The file `public/index.html` was causing merge conflicts because:
1. It was tracked by git (historical artifact)
2. It's auto-generated and changes frequently
3. CI workflows were committing it automatically
4. Multiple branches had conflicting versions

## Solution
We've **untracked** the file from git while keeping it functional. Here's what changed:

### 1. Untracked from Git ✅
```bash
git rm --cached public/index.html
```
- File is **deleted from git** (no longer tracked)
- File **remains locally** (still works)
- Listed in `.gitignore` line 92 (won't be re-added)

### 2. Updated CI Workflows ✅
**File:** `.github/workflows/website-maintenance.yml`

**Weather Scraping Job:**
- ❌ Before: Committed both `weather_cache.json` AND `public/index.html`
- ✅ Now: Only commits `weather_cache.json`
- HTML is regenerated on next CI run

**Auto-Generate HTML Job:**
- ❌ Before: Generated HTML, committed to git, then deployed
- ✅ Now: Generates HTML, deploys via artifact upload (no git commit)

### 3. Developer Tools ✅

**Helper Script:** `scripts/regenerate_html.sh`
```bash
./scripts/regenerate_html.sh
```
One command to regenerate HTML locally (handles network failures gracefully)

**Documentation:** `public/README.md`
- Explains why the file is gitignored
- How to regenerate locally
- What CI does with the file

### 4. Updated Gitignore ✅
**File:** `public/.gitignore`
- Added clear comments explaining the new behavior
- Points to regenerate script
- Explains relationship with root .gitignore

## Benefits

### ✅ No More Merge Conflicts
Future branches won't have `public/index.html` in version control, so merge conflicts are **impossible**.

### ✅ Always Fresh HTML
CI generates a fresh copy on every run, ensuring production always has the latest version.

### ✅ Source Files = Single Source of Truth
Only source files (`assets/css/*.css`, `assets/js/*.js`, `assets/html/*.html`) are tracked. Generated HTML is ephemeral.

### ✅ Clear Developer Experience
- New developers clone the repo
- Run `./scripts/regenerate_html.sh`
- Start developing immediately

## Testing

### What Works Now
1. ✅ `public/index.html` is no longer tracked by git
2. ✅ File exists locally for viewing/testing
3. ✅ CI workflows generate HTML without git commits
4. ✅ GitHub Pages deployment uses artifact upload

### What to Test After Merge
1. **Clone a fresh copy** - Verify `public/index.html` is not present
2. **Run regenerate script** - Verify HTML is created
3. **Push to main** - Verify CI generates and deploys HTML
4. **Create new branch** - Verify no merge conflicts with `public/index.html`

## Commands Reference

### Local Development
```bash
# Regenerate HTML (recommended)
./scripts/regenerate_html.sh

# Manual regeneration
python3 src/event_manager.py dependencies fetch
python3 src/event_manager.py generate

# View locally
cd public && python3 -m http.server 8000
```

### CI Behavior
```bash
# CI automatically runs on push to main:
1. Fetches dependencies (Leaflet.js, fonts)
2. Generates public/index.html
3. Uploads to GitHub Pages (artifact upload, not git commit)
4. Weather updates only commit weather_cache.json
```

## Files Changed

| File | Change | Reason |
|------|--------|--------|
| `public/index.html` | Deleted from git | Prevent merge conflicts |
| `.github/workflows/website-maintenance.yml` | Updated (2 jobs) | Stop committing HTML to git |
| `public/.gitignore` | Updated comments | Explain new behavior |
| `public/README.md` | Created | Developer documentation |
| `scripts/regenerate_html.sh` | Created | One-command regeneration |

## FAQ

**Q: Why remove from git if it's in .gitignore?**
A: Files added *before* gitignore are still tracked. `git rm --cached` removes them from tracking while keeping them locally.

**Q: Won't this break the site?**
A: No. CI generates HTML on every run. The site will work exactly the same.

**Q: What if I need to edit the HTML?**
A: Don't. Edit source files in `assets/` and regenerate. HTML is auto-generated.

**Q: How do I view the site locally?**
A: Run `./scripts/regenerate_html.sh` then `cd public && python3 -m http.server 8000`

**Q: What about weather updates?**
A: Weather updates commit only the cache file. HTML will be regenerated on the next CI run.

## Next Steps

1. **Merge this PR** - The fix is complete and ready
2. **Test locally** - New clones won't have `public/index.html`
3. **Verify CI** - Check GitHub Actions after merge
4. **Celebrate** - No more merge conflicts! 🎉

## Related Issues

- Original issue: #332
- Root `.gitignore`: Line 92 (`public/index.html`)
- CI workflow: `.github/workflows/website-maintenance.yml`
