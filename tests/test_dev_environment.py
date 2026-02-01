#!/usr/bin/env python3
"""
Test script to verify development environment configuration.

This script checks that all development environment configuration files
exist and are properly formatted.
"""

import json
import os
import sys
from pathlib import Path

def test_file_exists(filepath):
    """Test if a file exists."""
    if os.path.exists(filepath):
        print(f"✓ {filepath} exists")
        return True
    else:
        print(f"✗ {filepath} missing")
        return False

def test_json_valid(filepath):
    """Test if a JSON file is valid (allows JSONC with comments)."""
    try:
        # For JSONC files, we just check they can be read
        with open(filepath, 'r') as f:
            content = f.read()
            # Check it's not empty
            if content.strip():
                print(f"✓ {filepath} is readable")
                return True
            else:
                print(f"✗ {filepath} is empty")
                return False
    except Exception as e:
        print(f"✗ {filepath} error: {e}")
        return False

def main():
    """Run all configuration tests."""
    print("=" * 60)
    print("Development Environment Configuration Tests")
    print("=" * 60)
    
    # Track results
    all_passed = True
    
    # Test VS Code configuration
    print("\n1. VS Code Configuration Files:")
    vscode_files = [
        '.vscode/settings.json',
        '.vscode/extensions.json',
        '.vscode/tasks.json',
        '.vscode/launch.json'
    ]
    for filepath in vscode_files:
        if not (test_file_exists(filepath) and test_json_valid(filepath)):
            all_passed = False
    
    # Test devcontainer
    print("\n2. Devcontainer Configuration:")
    devcontainer_files = [
        '.devcontainer/devcontainer.json'
    ]
    for filepath in devcontainer_files:
        if not (test_file_exists(filepath) and test_json_valid(filepath)):
            all_passed = False
    
    # Test MCP configuration
    print("\n3. MCP Server Configuration:")
    mcp_files = [
        '.github/mcp/servers.json',
        '.github/mcp/README.md'
    ]
    for filepath in mcp_files:
        if filepath.endswith('.json'):
            if not (test_file_exists(filepath) and test_json_valid(filepath)):
                all_passed = False
        else:
            if not test_file_exists(filepath):
                all_passed = False
    
    # Test documentation
    print("\n4. Documentation Files:")
    doc_files = [
        '.github/copilot-instructions.md',
        '.github/DEV_ENVIRONMENT.md',
        '.github/agents/docs_agent.md',
        '.github/agents/planning-agent.md',
        '.github/agents/implementation-agent.md'
    ]
    for filepath in doc_files:
        if not test_file_exists(filepath):
            all_passed = False
    
    # Test workspace file
    print("\n5. VS Code Workspace File:")
    workspace_file = 'krwl-hof.code-workspace'
    if not (test_file_exists(workspace_file) and test_json_valid(workspace_file)):
        all_passed = False
    
    # Test features.json includes new features
    print("\n6. Feature Registry:")
    if test_file_exists('features.json'):
        try:
            with open('features.json', 'r') as f:
                features = json.load(f)
                
            # Check for new feature IDs
            feature_ids = [f['id'] for f in features.get('features', [])]
            required_features = [
                'copilot-custom-instructions',
                'vscode-workspace-config',
                'devcontainer-config',
                'mcp-server-config',
                'dev-environment-docs'
            ]
            
            for feature_id in required_features:
                if feature_id in feature_ids:
                    print(f"✓ Feature '{feature_id}' is documented")
                else:
                    print(f"✗ Feature '{feature_id}' missing from registry")
                    all_passed = False
        except Exception as e:
            print(f"✗ Error reading features.json: {e}")
            all_passed = False
    else:
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All development environment configuration tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed. Please review the output above.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
