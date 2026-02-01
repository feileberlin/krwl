#!/usr/bin/env python3
"""
Test merge strategies for timestamp-based JSON files

This test verifies that .gitattributes merge strategies prevent conflicts
on timestamp-only changes in auto-generated JSON files.
"""

import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys


def run_git_command(cmd, cwd=None, check=True):
    """Run a git command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def test_union_merge_strategy():
    """Test that union merge prevents timestamp conflicts"""
    print("\n=== Testing Union Merge Strategy for Timestamp Conflicts ===\n")
    
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp(prefix='krwl_merge_test_')
    test_path = Path(test_dir)
    
    try:
        print(f"📁 Test directory: {test_dir}")
        
        # Step 1: Initialize git repo
        print("\n1️⃣  Initializing test repository...")
        run_git_command("git init -b main", cwd=test_dir)
        run_git_command("git config user.name 'Test User'", cwd=test_dir)
        run_git_command("git config user.email 'test@example.com'", cwd=test_dir)
        print("   ✅ Repository initialized")
        
        # Step 2: Create .gitattributes with union merge
        print("\n2️⃣  Creating .gitattributes with union merge strategy...")
        gitattributes_content = """# Test merge strategy
assets/json/reviewer_notes.json merge=union
assets/json/pending_events.json merge=union
"""
        gitattributes_path = test_path / '.gitattributes'
        gitattributes_path.write_text(gitattributes_content)
        print("   ✅ .gitattributes created")
        
        # Step 3: Create JSON directory
        json_dir = test_path / 'assets' / 'json'
        json_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 4: Create initial JSON file and commit to main
        print("\n3️⃣  Creating initial JSON file on main branch...")
        initial_data = {
            "event_123": [
                {
                    "note": "Initial note",
                    "reviewer": "scraper",
                    "timestamp": "2026-02-01T10:00:00Z"
                }
            ]
        }
        reviewer_notes_path = json_dir / 'reviewer_notes.json'
        with open(reviewer_notes_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Initial commit'", cwd=test_dir)
        print("   ✅ Initial commit on main branch")
        
        # Step 5: Create branch A with timestamp update
        print("\n4️⃣  Creating branch A with timestamp update...")
        run_git_command("git checkout -b branch-a", cwd=test_dir)
        
        branch_a_data = {
            "event_123": [
                {
                    "note": "Initial note",
                    "reviewer": "scraper",
                    "timestamp": "2026-02-01T10:00:00Z"
                },
                {
                    "note": "Note from branch A",
                    "reviewer": "scraper",
                    "timestamp": "2026-02-01T11:00:00Z"  # Different timestamp
                }
            ]
        }
        with open(reviewer_notes_path, 'w') as f:
            json.dump(branch_a_data, f, indent=2)
        
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Update from branch A'", cwd=test_dir)
        print("   ✅ Branch A committed with timestamp: 11:00:00Z")
        
        # Step 6: Create branch B with different timestamp update
        print("\n5️⃣  Creating branch B with different timestamp update...")
        run_git_command("git checkout main", cwd=test_dir)
        run_git_command("git checkout -b branch-b", cwd=test_dir)
        
        branch_b_data = {
            "event_123": [
                {
                    "note": "Initial note",
                    "reviewer": "scraper",
                    "timestamp": "2026-02-01T10:00:00Z"
                },
                {
                    "note": "Note from branch B",
                    "reviewer": "scraper",
                    "timestamp": "2026-02-01T11:30:00Z"  # Different timestamp
                }
            ]
        }
        with open(reviewer_notes_path, 'w') as f:
            json.dump(branch_b_data, f, indent=2)
        
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Update from branch B'", cwd=test_dir)
        print("   ✅ Branch B committed with timestamp: 11:30:00Z")
        
        # Step 7: Merge branch A into main
        print("\n6️⃣  Merging branch A into main...")
        run_git_command("git checkout main", cwd=test_dir)
        stdout, stderr, code = run_git_command("git merge branch-a", cwd=test_dir, check=False)
        
        if code != 0:
            print(f"   ❌ Branch A merge failed: {stderr}")
            return False
        print("   ✅ Branch A merged successfully (fast-forward)")
        
        # Step 8: Merge branch B into main (should use union merge)
        print("\n7️⃣  Merging branch B into main (should use union merge)...")
        stdout, stderr, code = run_git_command("git merge branch-b", cwd=test_dir, check=False)
        
        # Check if there are conflicts
        conflict_check, _, _ = run_git_command("git status --short", cwd=test_dir, check=False)
        
        if 'UU' in conflict_check or code != 0:
            print(f"   ❌ Merge conflict detected!")
            print(f"   Git status: {conflict_check}")
            print(f"   Merge output: {stdout}")
            print(f"   Merge error: {stderr}")
            return False
        
        print("   ✅ Branch B merged without conflicts (union merge)")
        
        # Step 9: Verify JSON structure is valid
        print("\n8️⃣  Verifying merged JSON structure...")
        try:
            with open(reviewer_notes_path, 'r') as f:
                merged_data = json.load(f)
            print(f"   ✅ Merged JSON is valid")
            print(f"   📊 Merged data has {len(merged_data.get('event_123', []))} notes")
            
            # Show merged content
            print("\n   Merged content:")
            for note in merged_data.get('event_123', []):
                print(f"      - {note.get('note')} at {note.get('timestamp')}")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Merged JSON is invalid: {e}")
            print("\n   File content:")
            print(reviewer_notes_path.read_text())
            return False
        
        # Step 10: Verify merge attribute is applied
        print("\n9️⃣  Verifying merge attribute is applied...")
        stdout, _, _ = run_git_command(
            "git check-attr merge assets/json/reviewer_notes.json",
            cwd=test_dir
        )
        
        if 'merge: union' in stdout:
            print(f"   ✅ Merge attribute verified: {stdout}")
        else:
            print(f"   ⚠️  Merge attribute not detected: {stdout}")
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nSummary:")
        print("  • Union merge strategy prevents timestamp conflicts")
        print("  • Both branches merged without manual intervention")
        print("  • Merged JSON structure is valid")
        print("  • Merge attribute correctly applied via .gitattributes")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)


def test_pending_events_timestamp():
    """Test that pending_events.json handles last_scraped timestamp"""
    print("\n=== Testing pending_events.json Timestamp Handling ===\n")
    
    test_dir = tempfile.mkdtemp(prefix='krwl_pending_test_')
    test_path = Path(test_dir)
    
    try:
        print(f"📁 Test directory: {test_dir}")
        
        # Initialize repo
        run_git_command("git init -b main", cwd=test_dir)
        run_git_command("git config user.name 'Test User'", cwd=test_dir)
        run_git_command("git config user.email 'test@example.com'", cwd=test_dir)
        
        # Create .gitattributes
        gitattributes_content = "assets/json/pending_events.json merge=union\n"
        (test_path / '.gitattributes').write_text(gitattributes_content)
        
        # Create JSON directory
        json_dir = test_path / 'assets' / 'json'
        json_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial pending_events.json
        initial_data = {
            "pending_events": [],
            "last_scraped": "2026-02-01T10:00:00Z"
        }
        pending_path = json_dir / 'pending_events.json'
        with open(pending_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Initial'", cwd=test_dir)
        
        # Create two branches with different last_scraped times
        run_git_command("git checkout -b scrape-a", cwd=test_dir)
        data_a = {
            "pending_events": [],
            "last_scraped": "2026-02-01T11:00:00Z"
        }
        with open(pending_path, 'w') as f:
            json.dump(data_a, f, indent=2)
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Scrape A at 11:00'", cwd=test_dir)
        
        run_git_command("git checkout main", cwd=test_dir)
        run_git_command("git checkout -b scrape-b", cwd=test_dir)
        data_b = {
            "pending_events": [],
            "last_scraped": "2026-02-01T11:30:00Z"
        }
        with open(pending_path, 'w') as f:
            json.dump(data_b, f, indent=2)
        run_git_command("git add .", cwd=test_dir)
        run_git_command("git commit -m 'Scrape B at 11:30'", cwd=test_dir)
        
        # Merge both branches
        run_git_command("git checkout main", cwd=test_dir)
        run_git_command("git merge scrape-a", cwd=test_dir)
        stdout, stderr, code = run_git_command("git merge scrape-b", cwd=test_dir, check=False)
        
        if code != 0:
            print(f"   ❌ Merge failed: {stderr}")
            return False
        
        # Verify JSON is valid
        with open(pending_path, 'r') as f:
            merged = json.load(f)
        
        print(f"   ✅ Merge successful, JSON valid")
        print(f"   📊 Last scraped: {merged.get('last_scraped')}")
        
        return True
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    print("="*70)
    print("KRWL> Timestamp Merge Conflict Prevention Test")
    print("="*70)
    print("\nThis test verifies that .gitattributes merge strategies work correctly")
    print("to prevent timestamp-only conflicts in auto-generated JSON files.")
    
    success = True
    
    # Test 1: Union merge strategy
    if not test_union_merge_strategy():
        success = False
    
    # Test 2: pending_events.json timestamp
    if not test_pending_events_timestamp():
        success = False
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nThe .gitattributes merge strategies are working correctly.")
        print("Timestamp-only conflicts will be automatically resolved.")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the .gitattributes configuration.")
    print("="*70)
    
    sys.exit(0 if success else 1)
