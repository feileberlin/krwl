#!/bin/bash

# Test script for branch deletion workflow logic
# This script simulates the workflow steps locally without actually deleting branches
# Use this to verify the logic before running the actual GitHub Actions workflow

set -e

echo "🧪 Testing Branch Deletion Workflow Logic"
echo "=========================================="
echo ""

# Step 1: List all remote branches
echo "📋 Step 1: Listing all remote branches..."
echo ""

BRANCHES=$(git ls-remote --heads origin | \
  awk '{print $2}' | \
  sed 's|refs/heads/||' | \
  grep -v '^main$')

BRANCH_COUNT=$(echo "$BRANCHES" | grep -c . || echo "0")

echo "✓ Found $BRANCH_COUNT branches (excluding main)"
echo ""

# Step 2: Display statistics
echo "📊 Step 2: Statistics"
echo "---------------------"
echo "Total branches (including main): $((BRANCH_COUNT + 1))"
echo "Branches to delete: $BRANCH_COUNT"
echo "Branches to keep: 1 (main)"
echo ""

# Step 3: Show branches to delete
if [ "$BRANCH_COUNT" -gt 0 ]; then
  echo "🗑️  Step 3: Branches that would be deleted"
  echo "-----------------------------------------"
  echo "$BRANCHES" | head -10
  
  if [ "$BRANCH_COUNT" -gt 10 ]; then
    echo "... and $((BRANCH_COUNT - 10)) more branches"
  fi
  echo ""
fi

# Step 4: Show deletion commands (dry run)
echo "🔧 Step 4: Commands that would be executed"
echo "------------------------------------------"
echo "$BRANCHES" | head -5 | while IFS= read -r branch; do
  if [ -n "$branch" ]; then
    echo "git push origin --delete $branch"
  fi
done

if [ "$BRANCH_COUNT" -gt 5 ]; then
  echo "... and $((BRANCH_COUNT - 5)) more deletion commands"
fi
echo ""

# Step 5: Verify main branch exists
echo "✅ Step 5: Verifying main branch exists"
echo "---------------------------------------"
if git ls-remote --heads origin main | grep -q 'refs/heads/main'; then
  echo "✓ Main branch exists and will be preserved"
else
  echo "❌ ERROR: Main branch not found!"
  exit 1
fi
echo ""

# Summary
echo "📝 Summary"
echo "=========="
echo "✅ Test completed successfully"
echo "✅ Main branch is protected"
echo "✅ $BRANCH_COUNT branches identified for deletion"
echo ""
echo "🚀 Ready to run the GitHub Actions workflow!"
echo ""
echo "Next steps:"
echo "1. Go to: Actions → '🗑️ Delete All Branches Except Main' → Run workflow"
echo "2. Start with dry_run=true to preview"
echo "3. Then run with dry_run=false to execute"
echo ""
