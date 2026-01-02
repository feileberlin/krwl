#!/bin/bash
#
# Sync documentation to GitHub Wiki
#
# Simple sync: Copy all .md files from docs/ directory to wiki.
# The docs/ directory is already flat, so this is straightforward.
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
echo "📝 Copying documentation from docs/ directory..."
echo "   (GitHub Wiki uses flat structure, docs/ is already flat)"

# Copy all markdown files from docs/ directory
cp -v ../docs/*.md . 2>/dev/null || true

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
