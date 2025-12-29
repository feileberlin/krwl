#!/bin/bash
#
# Sync documentation to GitHub Wiki
#
# Our docs work as standalone files AND in the wiki.
# This script helps you manually sync them to the wiki repository.
# (Normally this happens automatically when merging to main!)
#
# Usage:
#   ./sync-to-wiki.sh [wiki-repo-path]
#
# If you don't specify a path, we'll use /tmp/krwl-hof.wiki
#

set -e

REPO_URL="https://github.com/feileberlin/krwl-hof.wiki.git"
WIKI_DIR="${1:-/tmp/krwl-hof.wiki}"

echo "🔄 Syncing KRWL HOF docs to GitHub Wiki..."
echo ""

# Clone or update wiki repository
if [ -d "$WIKI_DIR/.git" ]; then
    echo "📂 Wiki repo found at: $WIKI_DIR"
    echo "   Pulling latest..."
    cd "$WIKI_DIR"
    git pull
else
    echo "📦 Cloning wiki to: $WIKI_DIR"
    git clone "$REPO_URL" "$WIKI_DIR"
    cd "$WIKI_DIR"
fi

echo ""
echo "📝 Copying documentation..."

# Copy main docs
echo "   ✓ docs/ → wiki root"
cp -v ../docs/*.md . 2>/dev/null || true

# Copy root docs
echo "   ✓ Root documentation"
cp -v ../TESTING.md . 2>/dev/null || true

# Copy static docs
echo "   ✓ static/ documentation"
mkdir -p static
cp -v ../static/LOCALIZATION.md static/ 2>/dev/null || true
cp -v ../static/PWA_README.md static/ 2>/dev/null || true

# Copy .github docs
echo "   ✓ .github/ documentation"
mkdir -p .github
cp -v ../.github/DEV_ENVIRONMENT.md .github/ 2>/dev/null || true
cp -v ../.github/FEATURE_REGISTRY.md .github/ 2>/dev/null || true
cp -v ../.github/DEPLOYMENT.md .github/ 2>/dev/null || true
cp -v ../.github/PROMOTE_WORKFLOW.md .github/ 2>/dev/null || true

echo ""
echo "📊 What changed:"
git status --short

echo ""
echo "✅ Sync complete!"
echo ""
echo "Next steps:"
echo "  1. Review: cd $WIKI_DIR && git diff"
echo "  2. Commit: git commit -am 'Update docs'"
echo "  3. Push: git push"
echo ""
echo "Or all at once:"
echo "  cd $WIKI_DIR && git add . && git commit -m 'Update docs' && git push"
