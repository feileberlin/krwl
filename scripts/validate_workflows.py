#!/usr/bin/env python3
"""
Workflow Validation Script

Checks that GitHub Actions workflows follow best practices for preventing
merge conflicts on auto-generated JSON files.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def check_workflow_file(workflow_path: Path) -> List[Tuple[str, str]]:
    """
    Check a workflow file for best practices.
    
    Returns list of (severity, message) tuples:
    - "✅" = Good practice found
    - "⚠️" = Warning (potential issue)
    - "❌" = Error (violates best practice)
    """
    issues = []
    content = workflow_path.read_text()
    
    # Check 1: Does workflow commit JSON files?
    commits_json = bool(re.search(r'git\s+add.*\.json', content))
    
    if not commits_json:
        return [("ℹ️", "Workflow does not commit JSON files")]
    
    issues.append(("ℹ️", "Workflow commits JSON files - checking best practices..."))
    
    # Check 2: Uses git pull --rebase
    has_pull_rebase = bool(re.search(r'git\s+pull\s+--rebase', content))
    if has_pull_rebase:
        issues.append(("✅", "Uses 'git pull --rebase' (GOOD)"))
    else:
        has_pull = bool(re.search(r'git\s+pull\b', content))
        if has_pull:
            issues.append(("❌", "Uses 'git pull' without --rebase (BAD - creates merge commits)"))
        else:
            issues.append(("⚠️", "No 'git pull' found - may cause conflicts if concurrent runs"))
    
    # Check 3: Checks for changes before committing
    checks_changes = bool(re.search(r'git\s+diff.*--exit-code', content))
    if checks_changes:
        issues.append(("✅", "Checks for changes before committing (GOOD)"))
    else:
        issues.append(("⚠️", "No change detection - may create empty commits"))
    
    # Check 4: Commits specific files (not git add .)
    has_add_all = bool(re.search(r'git\s+add\s+\.', content))
    has_specific_add = bool(re.search(r'git\s+add\s+[^\.\s]', content))
    
    if has_add_all and not has_specific_add:
        issues.append(("⚠️", "Uses 'git add .' - may commit unintended files"))
    elif has_specific_add:
        issues.append(("✅", "Commits specific files only (GOOD)"))
    
    # Check 5: Uses [skip ci] in automated commits
    has_skip_ci = bool(re.search(r'\[skip ci\]', content))
    if has_skip_ci:
        issues.append(("✅", "Uses [skip ci] to prevent workflow loops (GOOD)"))
    else:
        issues.append(("⚠️", "No [skip ci] found - may trigger workflow loops"))
    
    # Check 6: Has retry logic for push failures
    has_push_retry = bool(re.search(r'git\s+push.*\|\|.*git\s+pull', content))
    if has_push_retry:
        issues.append(("✅", "Has retry logic for push failures (GOOD)"))
    else:
        issues.append(("ℹ️", "No push retry logic - may fail on concurrent updates"))
    
    return issues


def main():
    """Run validation on all workflow files"""
    print("="*70)
    print("GitHub Actions Workflow Validation")
    print("="*70)
    print("\nChecking for merge conflict prevention best practices...\n")
    
    repo_root = Path(__file__).parent.parent
    workflows_dir = repo_root / '.github' / 'workflows'
    
    if not workflows_dir.exists():
        print("❌ No .github/workflows directory found")
        return 1
    
    workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
    
    if not workflow_files:
        print("❌ No workflow files found")
        return 1
    
    print(f"Found {len(workflow_files)} workflow files\n")
    
    all_good = True
    
    for workflow_file in sorted(workflow_files):
        print(f"📄 {workflow_file.name}")
        print("─" * 70)
        
        issues = check_workflow_file(workflow_file)
        
        for severity, message in issues:
            print(f"   {severity} {message}")
            if severity == "❌":
                all_good = False
        
        print()
    
    print("="*70)
    if all_good:
        print("✅ All workflows follow best practices!")
    else:
        print("⚠️  Some workflows could be improved")
        print("\nSee docs/development/merge-strategies.md for guidance")
    print("="*70)
    
    return 0 if all_good else 1


if __name__ == '__main__':
    sys.exit(main())
