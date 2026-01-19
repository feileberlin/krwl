# How to Disable PR Previews

> Simple KISS methods to temporarily or permanently disable PR preview generation

## Why Disable?

You might want to disable PR previews:
- During high-volume PR periods (to save Actions minutes)
- When troubleshooting workflow issues
- To reduce notification noise
- During repository maintenance

## 🎯 Methods to Disable (Choose One)

### Method 1: Repository Variable (Recommended)

**Best for:** Long-term or team-wide disabling

**Steps:**
1. Go to repository **Settings**
2. Navigate to **Secrets and variables** → **Actions** → **Variables**
3. Click **New repository variable**
4. Name: `PR_PREVIEWS_ENABLED`
5. Value: `false`
6. Save

**To re-enable:**
- Change value to `true` or delete the variable

**Pros:**
- ✅ Affects all PRs globally
- ✅ No workflow file changes needed
- ✅ Easy to toggle on/off
- ✅ Visible to all maintainers

**Cons:**
- ❌ Requires repository admin access

---

### Method 2: Manual Workflow Dispatch

**Best for:** Quick testing or one-time disable

**Steps:**
1. Go to **Actions** tab
2. Select **PR Preview Build (KISS)** workflow
3. Click **Run workflow**
4. Choose **false** for "Enable PR previews globally"
5. Click **Run workflow**

**Note:** This only prevents manual runs. Automatic PR triggers will still work unless Method 1 is used.

**Pros:**
- ✅ Quick one-off disable
- ✅ No configuration changes
- ✅ Any contributor can use

**Cons:**
- ❌ Doesn't affect automatic PR triggers
- ❌ Only for testing

---

### Method 3: Comment in PR (Per-PR Disable)

**Best for:** Disabling preview for a specific PR only

**Steps:**
1. Add this to PR description or comment:
   ```
   [skip preview]
   ```

2. Or use Git commit message:
   ```bash
   git commit -m "fix: some change [skip preview]"
   ```

**Note:** This requires adding a check to the workflow (see "Advanced Method 4" below)

**Pros:**
- ✅ Per-PR control
- ✅ Self-service for PR authors

**Cons:**
- ❌ Requires workflow modification (not yet implemented)

---

### Method 4: Disable Workflow File (Nuclear Option)

**Best for:** Permanent removal or major troubleshooting

**Steps:**

**Option A: Disable via GitHub UI**
1. Go to **Actions** tab
2. Find **PR Preview Build (KISS)** in left sidebar
3. Click ⋯ (three dots) → **Disable workflow**

**Option B: Delete workflow file**
```bash
git rm .github/workflows/pr-preview.yml
git commit -m "chore: temporarily disable PR previews"
git push
```

**To re-enable (Option A):**
- Go to Actions → Re-enable workflow

**To re-enable (Option B):**
```bash
git revert HEAD  # Restore the file
git push
```

**Pros:**
- ✅ Complete shutdown
- ✅ Saves all Actions minutes
- ✅ Clear signal to team

**Cons:**
- ❌ Requires code change
- ❌ All or nothing (no granularity)
- ❌ Breaks workflow for everyone

---

## 📊 Comparison

| Method | Ease | Scope | Reversible | Admin Required |
|--------|------|-------|------------|----------------|
| Repository Variable | ⭐⭐⭐⭐ | Global | ✅ Instant | Yes |
| Workflow Dispatch | ⭐⭐⭐⭐⭐ | Manual runs only | ✅ Instant | No |
| Comment in PR | ⭐⭐⭐ | Per-PR | N/A | No |
| Disable Workflow | ⭐⭐ | Global | ✅ Manual | Yes |

---

## 🎛️ Recommended Workflow

### For Temporary Disable (1-7 days)
**Use Method 1: Repository Variable**

```
Settings → Actions → Variables → Add PR_PREVIEWS_ENABLED=false
```

### For Permanent Disable
**Use Method 4: Disable Workflow**

```
Actions → PR Preview Build (KISS) → Disable workflow
```

### For Testing
**Use Method 2: Workflow Dispatch**

```
Actions → Run workflow → Enable PR previews globally: false
```

---

## 🔍 Check If Previews Are Disabled

### Via Actions Tab
1. Open any PR
2. Check if **PR Preview Build (KISS)** workflow appears
3. If missing or shows "Skipped" → Previews are disabled

### Via Repository Variables
1. Go to **Settings** → **Actions** → **Variables**
2. Look for `PR_PREVIEWS_ENABLED`
3. If value is `false` → Disabled
4. If not present or `true` → Enabled

### Via Workflow Status
Check the workflow file:
```bash
cat .github/workflows/pr-preview.yml | grep "check-enabled" -A 10
```

If the check-enabled job exists → Feature can be disabled
If missing → Always enabled (older version)

---

## 🚀 Advanced: Per-PR Skip (Not Yet Implemented)

To implement per-PR skipping (Method 3), add this to the workflow:

```yaml
jobs:
  check-enabled:
    # ... existing code ...
    steps:
      - name: Check for skip marker
        run: |
          # Check PR body for [skip preview]
          PR_BODY="${{ github.event.pull_request.body }}"
          if echo "$PR_BODY" | grep -qi "\[skip preview\]"; then
            echo "enabled=false" >> $GITHUB_OUTPUT
            echo "❌ Preview skipped via [skip preview] marker"
            exit 0
          fi
```

Then use `[skip preview]` in PR description to skip that PR.

---

## 💰 Cost Considerations

### Actions Minutes Usage Per Preview
- Build: ~3-5 minutes
- Screenshots: ~2 minutes
- Color preview: ~30 seconds
- **Total: ~6-7 minutes per PR**

### When to Disable
- High PR volume (>20 PRs/day) → Consider disabling
- Limited Actions minutes → Disable temporarily
- Open source project → GitHub gives 2000 free minutes/month

### Alternative: Reduce Features
Instead of fully disabling, remove expensive steps:

```yaml
# Comment out screenshot generation
# - name: Install Playwright (for screenshots)
#   run: ...
```

This saves ~2 minutes per PR while keeping basic previews.

---

## 🔄 Re-enabling Previews

### After Method 1 (Repository Variable)
1. Delete `PR_PREVIEWS_ENABLED` variable, OR
2. Change value to `true`

### After Method 4 (Disabled Workflow)
1. Actions tab → Re-enable workflow, OR
2. `git revert` the commit that deleted the file

### Verification
1. Open a new PR (or push to existing)
2. Check Actions tab
3. **PR Preview Build (KISS)** should appear and run

---

## 📝 Communication

When disabling, inform the team:

```markdown
## 🔔 PR Previews Temporarily Disabled

PR preview generation is currently disabled to [reason].

**Alternative:** Test locally:
1. Checkout PR branch: `git checkout pr-branch`
2. Generate site: `python3 src/event_manager.py generate`
3. Test: `cd public && python3 -m http.server 8000`

Expected re-enable: [date]
```

---

## ❓ FAQ

**Q: Will disabling affect existing PR artifacts?**  
A: No, existing artifacts remain available for 90 days.

**Q: Can I disable just screenshots but keep site preview?**  
A: Yes, comment out the screenshot steps in the workflow file.

**Q: Does this affect production deployments?**  
A: No, PR previews are separate from main branch deployments.

**Q: Can individual contributors disable previews for their PRs?**  
A: Currently no (unless Method 3 is implemented). Use Method 2 for testing.

**Q: How much does it cost to run previews?**  
A: ~6-7 Actions minutes per PR. Free for public repos (2000 min/month limit).

---

## 🎯 Summary

**Quick Disable (Recommended):**
```
Settings → Actions → Variables → PR_PREVIEWS_ENABLED = false
```

**Quick Enable:**
```
Settings → Actions → Variables → PR_PREVIEWS_ENABLED = true (or delete)
```

**KISS Principle:** The simplest method is the repository variable. No code changes, instant effect, easy to reverse.

---

**Need help?** Check the workflow logs or open an issue.
