#!/bin/bash
# Pre-commit cleanliness check helper
# 
# This script can be integrated into Git pre-commit hooks to automatically
# check for repository clutter before commits.
#
# Usage:
#   1. Copy to .git/hooks/pre-commit (make executable)
#   2. Or run manually: bash scripts/pre-commit-check.sh
#   3. Or add to your CI/CD pipeline

# Fail fast on errors, undefined variables, and failed pipelines
set -euo pipefail

echo "🧹 Running repository cleanliness check..."
echo ""

# Run the Python cleanliness checker
# Temporarily disable 'errexit' so we can handle its exit code explicitly
set +e
python3 scripts/check_repository_cleanliness.py
exit_code=$?
set -e

if [ "$exit_code" -eq 0 ]; then
    echo ""
    echo "✅ Cleanliness check passed - safe to commit"
    exit 0
elif [ "$exit_code" -eq 1 ]; then
    echo ""
    echo "⚠️  Warnings found but commit allowed"
    echo "Consider fixing these issues to keep the repository clean"
    exit 0
else
    echo ""
    echo "❌ Cleanliness check failed - commit blocked"
    echo ""
    echo "Please fix the issues above before committing."
    echo "See .github/copilot-instructions.md → 'Repository Cleanliness' section"
    echo ""
    exit 1
fi
