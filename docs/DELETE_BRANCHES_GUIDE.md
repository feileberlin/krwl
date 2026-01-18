# 🗑️ Branch Deletion Workflow Guide

## Overview

This guide explains how to use the automated GitHub Actions workflow to delete all branches in the repository except `main`.

**⚠️ WARNING:** This action is irreversible! All deleted branches cannot be recovered unless you have local copies.

## When to Use This

Use this workflow when you need to clean up accumulated branches, such as:
- Old feature branches that have been merged
- Copilot-generated branches that are no longer needed
- Maintenance cleanup to reduce repository clutter

## How It Works

The workflow uses GitHub Actions to:
1. Fetch all remote branches
2. Filter out the `main` branch (protected)
3. Delete all other branches via `git push origin --delete`

## Usage Instructions

### Step 1: Navigate to GitHub Actions

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. Find the workflow: **🗑️ Delete All Branches Except Main**
4. Click **Run workflow**

### Step 2: Preview with Dry Run (Recommended)

**First, always run in dry-run mode to see what will be deleted:**

1. Set **Dry run mode** to: `true` ✅
2. Type in confirmation field: `DELETE ALL BRANCHES` (exact spelling required)
3. Click **Run workflow**
4. Wait for completion and review the summary

The dry run will show:
- Total number of branches
- List of all branches that would be deleted
- Commands that would be executed

**No branches are deleted in dry-run mode!**

### Step 3: Execute Live Deletion

**Only after reviewing the dry run results:**

1. Click **Run workflow** again
2. Set **Dry run mode** to: `false` ❌
3. Type in confirmation field: `DELETE ALL BRANCHES` (exact spelling, case-sensitive)
4. Click **Run workflow**
5. Confirm you want to proceed

The workflow will:
- Delete all branches except `main`
- Report success/failure for each branch
- Verify that `main` still exists at the end

### Step 4: Review Results

After completion, check the workflow summary:
- **Successfully deleted:** Number of branches removed
- **Failed:** Any branches that couldn't be deleted
- **Main branch preserved:** Confirmation that `main` is safe

## Safety Features

### 1. Manual Trigger Only
- Workflow must be manually triggered
- Will never run automatically on schedule or push

### 2. Dry Run Default
- Dry run mode is enabled by default
- Must be explicitly disabled to delete branches

### 3. Confirmation Required
- Must type exact phrase: `DELETE ALL BRANCHES`
- Case-sensitive confirmation (typos prevent deletion)

### 4. Main Branch Protection
- Main branch is explicitly filtered out
- Final verification step ensures `main` exists
- Workflow fails if `main` is accidentally deleted

### 5. Detailed Logging
- Lists all branches before deletion
- Reports success/failure for each branch
- Provides comprehensive summary

## Troubleshooting

### Confirmation Failed
**Error:** "Confirmation failed - must type exactly: DELETE ALL BRANCHES"

**Solution:** Ensure you type the exact phrase with correct capitalization:
- ✅ Correct: `DELETE ALL BRANCHES`
- ❌ Wrong: `delete all branches`
- ❌ Wrong: `Delete All Branches`
- ❌ Wrong: `DELETE_ALL_BRANCHES`

### Permission Denied
**Error:** "failed to push some refs"

**Solution:** Ensure the workflow has `contents: write` permission:
- This is already configured in the workflow file
- Check repository settings → Actions → General → Workflow permissions
- Should be set to "Read and write permissions"

### Some Branches Failed to Delete
**Warning:** "Failed: X branches"

**Possible causes:**
1. **Protected branches** - Check branch protection rules in Settings → Branches
2. **Open pull requests** - Close or merge PRs before deleting branches
3. **Network issues** - Retry the workflow

**Solution:** Check the logs for specific branch names and investigate why they couldn't be deleted.

### Main Branch Deleted (Critical Error)
**Error:** "CRITICAL ERROR: Main branch was deleted!"

**This should never happen** due to the filtering logic, but if it does:

1. **Stop immediately** - Don't push any changes
2. **Contact repository maintainer**
3. **Check if main exists locally:**
   ```bash
   git branch -a | grep main
   ```
4. **Restore from local copy:**
   ```bash
   git checkout main
   git push origin main
   ```

## Manual Alternative (Local Git)

If you prefer to delete branches manually from your local machine:

```bash
# Fetch all branches
git fetch --all

# List branches to delete (review this list!)
git branch -r | grep -v 'main' | grep -v 'HEAD' | sed 's/origin\///'

# Delete branches one by one (example)
git push origin --delete copilot/branch-name

# Or delete multiple branches using a script
for branch in $(git branch -r | grep 'copilot/' | sed 's/origin\///'); do
  if [ "$branch" != "main" ]; then
    git push origin --delete "$branch"
  fi
done
```

## Best Practices

1. **Always run dry run first** - Never skip the preview step
2. **Review the branch list** - Make sure no important branches are included
3. **Check open PRs** - Close or merge PRs before deleting branches
4. **Backup locally** - If you might need branches later, clone them locally first
5. **Run during low activity** - Avoid conflicts with ongoing development
6. **Communicate with team** - Let team members know before mass deletion

## Workflow Configuration

The workflow file is located at:
```
.github/workflows/delete-branches.yml
```

Key settings:
- **Permissions:** `contents: write` (required for branch deletion)
- **Trigger:** `workflow_dispatch` (manual only)
- **Dry run default:** `true` (safe by default)
- **Protected branch:** `main` (hardcoded exclusion)

## Example Workflow Run

### Dry Run Output
```
📊 Branch Statistics
- Total branches (including main): 67
- Branches to delete: 66
- Branches to keep: 1 (main)

🗑️ Branches to Delete
copilot/add-dashboard-menu-functionality
copilot/add-environment-override-config
copilot/add-inline-html-ci-action
... (63 more branches)

✅ Dry run complete - No branches were deleted
```

### Live Deletion Output
```
⚠️ LIVE DELETION MODE - Deleting branches...

Deleting: copilot/add-dashboard-menu-functionality
  ✓ Deleted: copilot/add-dashboard-menu-functionality
Deleting: copilot/add-environment-override-config
  ✓ Deleted: copilot/add-environment-override-config
... (64 more branches)

✅ Deletion Results
- Successfully deleted: 66 branches
- Failed: 0 branches

✅ Main branch preserved - Workflow complete
```

## After Deletion

Once branches are deleted:
1. **Local branches remain** - Developers still have local copies
2. **Git history preserved** - Commit history in `main` is unchanged
3. **No recovery from remote** - Deleted remote branches cannot be restored
4. **Clean repository** - Only `main` branch visible on GitHub

## Questions?

If you encounter issues or have questions:
1. Check the workflow logs in the Actions tab
2. Review this guide for troubleshooting steps
3. Contact repository maintainer for assistance

---

**Last Updated:** January 2026  
**Workflow Version:** 1.0.0  
**Repository:** feileberlin/krwl-hof
