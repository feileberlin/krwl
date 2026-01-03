#!/bin/bash
# ==============================================================================
# Hosting Environment Setup Script
# ==============================================================================
# This script sets up production-specific git ignore rules on your hosting server
# It prevents production files from being overwritten during git pull/sync
# 
# USAGE:
#   1. SSH into your hosting server
#   2. cd /path/to/your/app
#   3. bash scripts/setup-hosting-gitignore.sh
# 
# WHAT IT DOES:
#   - Configures git to use hosting-specific .gitignore
#   - Creates production .env file template
#   - Sets up production-only directories
#   - Protects production data from being overwritten
# ==============================================================================

set -e  # Exit on error

echo "===================================================================="
echo "  Hosting Environment Git Configuration Setup"
echo "===================================================================="
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Please run this script from your project root"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Copy hosting .gitignore
echo "Step 1: Setting up hosting-specific .gitignore..."
if [ -f "scripts/.gitignore.hosting.example" ]; then
    cp scripts/.gitignore.hosting.example .gitignore.hosting
    echo "✅ Created .gitignore.hosting"
else
    echo "⚠️  Warning: scripts/.gitignore.hosting.example not found"
    echo "   Skipping this step..."
fi
echo ""

# Step 2: Configure git to use hosting .gitignore
echo "Step 2: Configuring git to use hosting .gitignore..."
if [ -f ".gitignore.hosting" ]; then
    git config core.excludesFile .gitignore.hosting
    echo "✅ Git configured to use .gitignore.hosting"
    echo "   This prevents production files from being overwritten during git pull"
else
    echo "⚠️  Skipping git config (no .gitignore.hosting file)"
fi
echo ""

# Step 3: Create production .env if it doesn't exist
echo "Step 3: Checking production .env file..."
if [ ! -f ".env" ]; then
    echo "Creating production .env file..."
    cat > .env << 'EOF'
# ==============================================================================
# PRODUCTION ENVIRONMENT VARIABLES
# ==============================================================================
# This file is specific to this hosting environment and will NOT be overwritten
# by git pull (protected by .gitignore.hosting)

# Force production mode (usually auto-detected, but this ensures it)
ENVIRONMENT=production

# Legacy support (still works for backward compatibility)
# NODE_ENV=production

# Add your production-specific variables below:
# DATABASE_URL=postgresql://...
# API_KEY=your-production-api-key
# SECRET_KEY=your-production-secret

# ==============================================================================
EOF
    echo "✅ Created .env file"
    echo "   ⚠️  IMPORTANT: Edit .env and add your production secrets!"
else
    echo "✅ .env file already exists (not overwriting)"
fi
echo ""

# Step 4: Create production-only directories
echo "Step 4: Creating production-only directories..."
mkdir -p logs
mkdir -p backups
mkdir -p data/backups
mkdir -p data/old
mkdir -p ssl
mkdir -p cache
echo "✅ Created production directories"
echo ""

# Step 5: Create .server-id file
echo "Step 5: Creating server identity file..."
SERVER_ID="server-$(date +%s)-$(hostname)"
echo "$SERVER_ID" > .server-id
echo "✅ Created .server-id: $SERVER_ID"
echo "   This helps identify this specific hosting instance"
echo ""

# Step 6: Verify configuration
echo "Step 6: Verifying configuration..."
echo ""
echo "Git configuration:"
git config core.excludesFile
echo ""

echo "Files protected from git pull:"
if [ -f ".gitignore.hosting" ]; then
    echo "  - .env"
    echo "  - .env.production"
    echo "  - .env.local"
    echo "  - logs/"
    echo "  - backups/"
    echo "  - ssl/"
    echo "  - config.local.json"
    echo "  - .server-id"
    echo "  - (and more, see .gitignore.hosting)"
fi
echo ""

# Step 7: Test git status
echo "Step 7: Testing git status..."
echo ""
echo "Files that will be ignored by git (should NOT show .env, .server-id, etc.):"
git status --short
echo ""

# Success message
echo "===================================================================="
echo "✅ Hosting environment setup complete!"
echo "===================================================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Edit .env file with your production secrets:"
echo "   nano .env"
echo ""
echo "2. Generate the site:"
echo "   python3 src/event_manager.py generate"
echo ""
echo "3. Test that git pull won't overwrite your production files:"
echo "   git pull origin main"
echo "   (Your .env and production files should remain unchanged)"
echo ""
echo "4. Set up automated deployments (optional):"
echo "   - Use git hooks for auto-pull on push"
echo "   - Or set up CI/CD pipeline"
echo ""
echo "IMPORTANT NOTES:"
echo "- Your .env file is now protected from git pull"
echo "- Production logs and backups will not sync to git"
echo "- You can safely run 'git pull' without losing production data"
echo "- To reset this configuration: git config --unset core.excludesFile"
echo ""
echo "===================================================================="
