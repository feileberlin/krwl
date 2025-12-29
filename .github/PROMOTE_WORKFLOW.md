# Promote Preview Workflow Guide

Complete guide to promoting preview changes to production safely.

## 🆕 What's New in the Updated Workflow?

The workflow has been completely reworked with the following improvements:

✨ **Automatic Branch Creation**: If the `preview` branch doesn't exist, the workflow can create it automatically from `main`
✨ **Pre-flight Validation**: Validates that both branches exist and checks if there are changes to promote
✨ **Better Error Messages**: Clear, actionable error messages when something goes wrong
✨ **Workflow Summaries**: Beautiful summaries in GitHub Actions UI showing what happened
✨ **Structured Outputs**: PR number, URL, and action taken are available as job outputs
✨ **Updated GitHub Script**: Now uses `actions/github-script@v7` for better performance
✨ **Smart Skip Logic**: Won't create PRs when branches are identical

## What is the Promote Preview Workflow?

The **Promote Preview** workflow is an automated tool that creates a Pull Request from the `preview` branch to `main` (production). This ensures all changes are reviewed before going live.

**New Feature**: If the `preview` branch doesn't exist, the workflow can create it for you automatically!

## Why Use This Workflow?

✅ **Safety**: Changes are reviewed via PR before production
✅ **Traceability**: Clear history of what went to production and when
✅ **Testing**: Preview changes are tested before promotion
✅ **Rollback**: Easy to revert if issues are found
✅ **Team Collaboration**: Team members can review before merge

## When to Use It

Use the Promote Preview workflow when:

- ✓ You've tested changes in the preview environment
- ✓ All features work correctly at `/preview/` path
- ✓ Debug logs show no errors
- ✓ You're ready to deploy to production
- ✓ Changes are approved by your team

**Do NOT use it when:**

- ✗ Preview changes haven't been tested
- ✗ There are known bugs in preview
- ✗ You're still actively developing features
- ✗ Tests are failing

## How It Works

### Step-by-Step Process (Updated)

```
┌─────────────────────────────────────┐
│  1. Developer clicks "Run workflow" │
│     in GitHub Actions               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Validate branches exist         │
│     - Check main exists             │
│     - Check preview exists          │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   Preview          Preview
   exists           missing
       │                │
       │                ▼
       │      ┌─────────────────────┐
       │      │ Create preview from │
       │      │ main (if allowed)   │
       │      └─────────┬───────────┘
       │                │
       └────────┬───────┘
                │
                ▼
┌─────────────────────────────────────┐
│  3. Compare branches                │
│     - Check if changes exist        │
│     - Count commits ahead/behind    │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   Changes          No changes
   found            (stop here)
       │
       ▼
┌─────────────────────────────────────┐
│  4. Check for existing PR           │
│     preview → main                  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   PR exists       No PR found
       │                │
       ▼                ▼
  Update PR        Create new PR
       │                │
       └────────┬───────┘
                │
                ▼
┌─────────────────────────────────────┐
│  5. PR created/updated with:        │
│     - Title & full description      │
│     - Commits summary               │
│     - Testing checklist             │
│     - Deployment info               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  6. Optional: Auto-merge attempt    │
│     (if auto_merge = true)          │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   Merge OK      Merge blocked
       │         (branch protection)
       ▼                │
   DEPLOYED             ▼
   TO PROD         Manual merge
                    needed
```

### What the Workflow Does (Updated)

1. **Validates branch existence**: 
   - Checks that `main` branch exists
   - Checks if `preview` branch exists
   - Can create `preview` from `main` if missing (optional)
2. **Compares branches**: 
   - Determines if there are changes to promote
   - Counts commits ahead/behind
   - Skips PR creation if branches are identical
3. **Checks existing PRs**: Looks for open PR from `preview` to `main`
4. **Creates or updates PR**: 
   - Creates new PR if none exists
   - Updates existing PR with latest info
   - Includes commit counts and deployment details
5. **Adds PR description**: Includes testing checklist and deployment info
6. **Optional auto-merge**: If enabled, tries to merge automatically
7. **Graceful handling**: Fails gracefully if branch protection prevents auto-merge
8. **Workflow summaries**: Provides clear summary in GitHub Actions UI

## How to Run the Workflow

### Method 1: GitHub Web Interface (Recommended)

1. **Navigate to Actions**
   - Go to your repository on GitHub
   - Click "Actions" tab at top

2. **Select the workflow**
   - Find "Promote Preview to Production" in left sidebar
   - Click on it

3. **Run workflow**
   - Click "Run workflow" button (top right)
   - Select branch: `main` (default)
   - Choose workflow options:
     - **Auto-merge**: 
       - `false` (default): Creates PR for manual review
       - `true`: Attempts to merge automatically
     - **Create preview if missing**:
       - `true` (default): Creates preview branch if it doesn't exist
       - `false`: Fails if preview branch is missing
   - Click green "Run workflow" button

4. **Wait for completion**
   - Workflow runs in ~30 seconds
   - Check workflow run for PR link
   - Click PR link to review changes

### Method 2: GitHub CLI

```bash
# Create PR (manual merge, auto-create preview if missing)
gh workflow run promote-preview.yml

# Create PR and attempt auto-merge
gh workflow run promote-preview.yml -f auto_merge=true

# Fail if preview branch doesn't exist
gh workflow run promote-preview.yml -f create_preview_if_missing=false
```

### Method 3: GitHub API

```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/promote-preview.yml/dispatches \
  -d '{"ref":"main","inputs":{"auto_merge":"false","create_preview_if_missing":"true"}}'
```

## Workflow Inputs

### `auto_merge` (optional)

**Type**: String (`'true'` or `'false'`)  
**Default**: `'false'`  
**Description**: Whether to automatically merge the PR after creation

#### When to use `auto_merge: true`

✓ Use when:
- You trust the preview testing completely
- No branch protection on `main`
- Solo developer with full control
- Hotfix needed immediately

#### When to use `auto_merge: false` (default)

✓ Use when:
- Team review needed
- Branch protection enabled (required reviews)
- Want to double-check changes
- Following standard release process

### `create_preview_if_missing` (optional) 🆕

**Type**: String (`'true'` or `'false'`)  
**Default**: `'true'`  
**Description**: Whether to automatically create the `preview` branch from `main` if it doesn't exist

#### When to use `create_preview_if_missing: true` (default)

✓ Use when:
- First time setting up the workflow
- Preview branch was accidentally deleted
- You want an easy setup experience
- Starting a new project

#### When to use `create_preview_if_missing: false`

✓ Use when:
- Preview branch should already exist
- You want explicit control over branch creation
- Running in production environment
- Following strict change control processes

## Understanding the PR

### PR Title
```
Promote preview to production
```

### PR Body Contents

The PR body includes:

1. **Description**: What's being promoted
2. **Deployment info**: 
   - Config used (production vs preview)
   - Domain configuration
   - Performance notes
3. **Testing checklist**:
   - [ ] Preview site tested
   - [ ] Features working
   - [ ] No console errors
   - [ ] Performance acceptable
4. **Auto-merge status**: Whether auto-merge was attempted

### Example PR Body

```markdown
## 🚀 Promote Preview to Production

This PR promotes changes from the `preview` branch to `main` (production).

### What happens when merged:
- Production site will be updated with preview changes
- Site will use `config.prod.json` (optimized for maximum speed, no debugging)
- Custom domain (CNAME) will be preserved

### Testing checklist:
- [ ] Preview site tested at /preview/ path
- [ ] All features working correctly
- [ ] No console errors in production mode
- [ ] Performance is acceptable

---
*Auto-merge requested: false*
```

## After Running the Workflow

### If auto_merge = false (Manual Review)

1. **Workflow completes** and provides PR link
2. **Review the PR**:
   - Check "Files changed" tab
   - Review all modifications
   - Test preview one more time
   - Add comments if needed
3. **Request reviews** (if team workflow)
4. **Merge when ready**:
   - Click "Merge pull request"
   - Choose merge method (merge/squash/rebase)
   - Confirm merge
5. **Production deploys automatically**:
   - `deploy-pages.yml` workflow triggers
   - Site builds with `config.prod.json`
   - Deploys to production

### If auto_merge = true (Automatic)

#### Success Case
1. Workflow creates PR
2. Workflow merges PR automatically
3. Production deploy workflow triggers
4. Site is live in ~2 minutes

#### Blocked Case (Branch Protection)
1. Workflow creates PR
2. Auto-merge fails with message:
   ```
   ⚠ Could not auto-merge PR #123: Branch protection rules not satisfied
   This is expected if branch protection rules are enabled.
   Please merge the PR manually.
   ```
3. Follow manual review process above

## Checking Workflow Results

### View Workflow Run

1. Go to Actions tab
2. Click "Promote Preview to Production"
3. Click on the latest run
4. Check the **Summary** tab for:
   - 🆕 Beautiful formatted summary showing what happened
   - PR link (if created)
   - Action taken (created/updated/auto-merged/skipped)
   - Any warnings or errors
5. Check logs for detailed output:
   - Branch validation steps
   - PR creation/update confirmation
   - PR number and URL
   - Auto-merge status
   - Any errors

### 🆕 New Workflow Summary Feature

The workflow now provides a beautiful summary in the GitHub Actions UI:

**When preview branch is created:**
```
✓ Preview Branch Created
━━━━━━━━━━━━━━━━━━━━━━━
The `preview` branch was created from `main`.

📝 Note: Both branches are currently identical.
💡 Next steps: Make changes to the preview branch, test them, then run this workflow again.
```

**When no changes to promote:**
```
⚠️ No Changes to Promote
━━━━━━━━━━━━━━━━━━━━━━━
The `preview` and `main` branches are identical.

💡 Next steps: Make changes to the preview branch, test them, then run this workflow again.
```

**When PR is created:**
```
✓ PR Created
━━━━━━━━━━━━━━━━━━━━━━━
PR #42 is ready for review.

Commits to merge: 5
→ Review and Merge PR
```

**When auto-merge succeeds:**
```
✓ Auto-merge Successful
━━━━━━━━━━━━━━━━━━━━━━━
PR #42 was automatically merged to production.

→ View PR
```

**When auto-merge is blocked:**
```
⚠️ Auto-merge Blocked
━━━━━━━━━━━━━━━━━━━━━━━
PR #42 was created but could not be automatically merged.

Reason: Branch protection rule requires review
This is normal if branch protection is enabled. Please review and merge manually.

→ Review and Merge PR
```

### Sample Success Log

```
🔍 Validating repository setup...
✓ Base branch 'main' exists
✓ Head branch 'preview' exists
📊 Comparison: 5 ahead, 0 behind
✓ Validation complete - ready to create PR
🔍 Checking for existing PRs...
📝 Creating new PR...
✓ Created new PR #42: https://github.com/owner/repo/pull/42
```

### Sample Blocked Log

```
📝 Updating existing PR #42
✓ Updated existing PR #42: https://github.com/owner/repo/pull/42
🤖 Attempting auto-merge...
⚠️  Could not auto-merge PR #42: Review required
This is expected if branch protection rules are enabled.
Please merge the PR manually.
```

## Troubleshooting

### "Preview branch does not exist" 🆕

**Problem**: The `preview` branch hasn't been created yet

**Solution**:
- **Automatic (Recommended)**: Set `create_preview_if_missing: true` (default) and run workflow
- **Manual**: Create preview branch first:
  ```bash
  git checkout main
  git pull
  git checkout -b preview
  git push -u origin preview
  ```
- The workflow will create the branch automatically by default

### "No commits between preview and main" 🆕

**Problem**: Branches are in sync, nothing to promote

**Solution**:
- This is normal when first setting up or when branches are synchronized
- Make changes on `preview` branch first
- Push changes to `preview`
- Test at `/preview/` path
- Then run promote workflow again
- The workflow now automatically skips PR creation in this case

### "Pull request already exists"

**Problem**: PR already open

**Solution**:
- This is normal! Workflow updates existing PR
- Check the PR link in workflow logs or summary
- Review and merge existing PR
- The workflow now shows this clearly in the summary

### "Conflict detected"

**Problem**: `preview` and `main` have conflicting changes

**Solution**:
1. Workflow still creates PR
2. GitHub shows conflict warning
3. Resolve conflicts manually:
   ```bash
   git checkout preview
   git pull origin main
   # Resolve conflicts
   git commit
   git push
   ```
4. PR will update automatically

### "Auto-merge failed"

**Problem**: Branch protection prevents auto-merge

**Solution**:
- This is expected and safe
- Review PR manually
- Get required approvals
- Merge when ready

### "Workflow not found"

**Problem**: Workflow file missing or renamed

**Solution**:
- Check `.github/workflows/promote-preview.yml` exists
- Verify workflow is on `main` branch
- Push workflow file if missing

## Best Practices

### Before Promoting

- [ ] Test all features in preview environment
- [ ] Check browser console for errors (should be none)
- [ ] Verify debug mode works (if `config.dev.json` used)
- [ ] Test on mobile device
- [ ] Check performance is acceptable
- [ ] Review all changes in git diff

### During Promotion

- [ ] Use descriptive commit messages in PR
- [ ] Add notes about major changes
- [ ] Tag relevant team members for review
- [ ] Link to related issues/PRs
- [ ] Update documentation if needed

### After Promotion

- [ ] Verify production site loads
- [ ] Check production uses correct config (no debug mode)
- [ ] Test key features in production
- [ ] Monitor for errors in next 24 hours
- [ ] Update any documentation
- [ ] Close related issues

## Integration with Branch Protection

### Recommended Branch Protection for `main`

```yaml
Rules:
  - Require pull request before merging: ✓
  - Require approvals: 1+
  - Dismiss stale reviews: ✓
  - Require review from Code Owners: ○ (optional)
  - Require status checks: ✓
    - Check: deploy-pages / deploy
  - Require branches to be up to date: ✓
  - Require conversation resolution: ✓
  - Include administrators: ○ (your choice)
```

With these rules:
- ✓ Promote workflow creates PR automatically
- ✗ Auto-merge fails (requires approval)
- ✓ Manual merge after review

## Comparison: Manual vs Auto-merge

| Aspect | Manual (default) | Auto-merge |
|--------|------------------|------------|
| **Safety** | ✓✓✓ High | ✓✓ Medium |
| **Speed** | Slower (review time) | ✓✓✓ Fast |
| **Team review** | ✓✓✓ Yes | ✗ Skipped |
| **Compliance** | ✓✓✓ Audit trail | ✓✓ Less oversight |
| **Rollback** | ✓✓✓ Easy (PR visible) | ✓✓ Must check history |
| **Best for** | Teams, prod sites | Solo, test sites |

## Example Workflow Scenarios

### Scenario 1: Team with Reviews (Recommended)

```
1. Dev makes changes on feature branch
2. Dev merges to preview branch
3. Preview deploys automatically with debug
4. Team tests at /preview/
5. Dev runs: Promote Preview (auto_merge=false)
6. Team reviews PR, approves
7. Dev merges PR
8. Production deploys automatically
```

### Scenario 2: Solo Developer, Careful

```
1. Make changes on preview branch
2. Preview deploys with debug
3. Test thoroughly at /preview/
4. Run: Promote Preview (auto_merge=false)
5. Review your own PR one last time
6. Merge PR
7. Production deploys
```

### Scenario 3: Solo Developer, Fast

```
1. Make changes on preview branch
2. Quick test at /preview/
3. Run: Promote Preview (auto_merge=true)
4. PR created and merged automatically
5. Production deploys
6. Monitor for issues
```

### Scenario 4: Hotfix

```
1. Create hotfix on preview
2. Minimal testing (urgent!)
3. Run: Promote Preview (auto_merge=true)
4. If blocked by protection: manual merge ASAP
5. Monitor production closely
6. Create follow-up PR if needed
```

## Security Considerations

### Secrets and Tokens

The workflow uses `GITHUB_TOKEN`:
- ✓ Automatically provided by GitHub
- ✓ Scoped to repository only
- ✓ Expires after workflow
- ✓ No manual token management needed

### Permissions Required

```yaml
permissions:
  contents: write      # To access code
  pull-requests: write # To create/update PRs
  pages: write         # For GitHub Pages
  id-token: write      # For deployment
```

### What Can Go Wrong?

❌ **Workflow cannot**:
- Delete branches
- Modify repository settings
- Access other repositories
- Expose secrets
- Bypass required reviews (when enabled)

✅ **Workflow can only**:
- Read code
- Create/update PRs
- Trigger deployments
- Add PR comments

## Related Documentation

- [DEPLOYMENT.md](.github/DEPLOYMENT.md) - Full deployment guide
- [README.md](../README.md) - Project overview and setup
- [deploy-pages.yml](workflows/deploy-pages.yml) - Production deploy workflow
- [deploy-preview.yml](workflows/deploy-preview.yml) - Preview deploy workflow

## Questions?

**"When should I use this?"**
→ After testing changes in preview, before going to production

**"Can I skip preview?"**
→ Not recommended. Preview = safety net with debug mode

**"What if I need to rush a fix?"**
→ Use auto_merge=true, but monitor closely

**"How do I rollback?"**
→ Create new PR reverting changes, or use git revert

**"Can I customize the PR description?"**
→ Edit the workflow file's script section

**"What if workflow fails?"**
→ Check workflow logs, verify branches exist, ensure permissions are correct

## Summary

The Promote Preview workflow is a **simple, safe tool** for moving changes from testing to production:

1. **Run workflow** (one click)
2. **Review PR** (or auto-merge)
3. **Merge to deploy** (automatic)

Keep it simple:
- Test in preview with debug mode
- Promote when ready
- Review changes
- Merge to production

That's it! 🚀
