#!/usr/bin/env python3
"""
Cleanup Script - Remove Obsolete Files

This script identifies and optionally removes files that are no longer needed
after the architecture simplification (generator.py → cdn_inliner.py).

SAFE TO RUN: Only shows files by default. Use --delete to actually remove.
"""

import argparse
import os
import shutil
from pathlib import Path


def find_obsolete_files(base_path):
    """Find files that are no longer needed"""
    obsolete = {
        'python_cache': [],
        'test_temp': [],
        'backup_files': [],
        'already_removed': []
    }
    
    # Python cache directories
    for pattern in ['__pycache__', '*.pyc', '*.pyo']:
        for path in base_path.rglob(pattern):
            if '.git' not in str(path):
                obsolete['python_cache'].append(path)
    
    # Test temp files
    temp_dir = Path('/tmp')
    if temp_dir.exists():
        for pattern in ['test_*.json', '*_test.json']:
            for path in temp_dir.glob(pattern):
                obsolete['test_temp'].append(path)
    
    # Backup files (.backup, .bak, ~)
    for pattern in ['*.backup', '*.bak', '*~']:
        for path in base_path.rglob(pattern):
            if '.git' not in str(path):
                obsolete['backup_files'].append(path)
    
    # Already removed files (for documentation)
    obsolete['already_removed'] = [
        'src/modules/generator.py (2185 lines - deleted ✓)',
    ]
    
    return obsolete


def calculate_size(paths):
    """Calculate total size of files"""
    total = 0
    for path in paths:
        try:
            if path.is_file():
                total += path.stat().st_size
            elif path.is_dir():
                total += sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        except:
            pass
    return total


def format_size(bytes):
    """Format bytes as human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def clean_files(obsolete, dry_run=True):
    """Remove obsolete files"""
    removed = {'count': 0, 'size': 0}
    
    for category, paths in obsolete.items():
        if category == 'already_removed':
            continue
            
        for path in paths:
            try:
                size = 0
                if path.is_file():
                    size = path.stat().st_size
                elif path.is_dir():
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                
                if not dry_run:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    print(f"  ✓ Removed: {path}")
                
                removed['count'] += 1
                removed['size'] += size
            except Exception as e:
                print(f"  ✗ Error removing {path}: {e}")
    
    return removed


def main():
    parser = argparse.ArgumentParser(
        description='Clean up obsolete files after architecture simplification'
    )
    parser.add_argument(
        '--delete', 
        action='store_true',
        help='Actually delete files (default: dry-run, just show files)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all files, not just summary'
    )
    args = parser.parse_args()
    
    base_path = Path(__file__).parent
    
    print("=" * 70)
    print("KRWL HOF Cleanup - Obsolete Files")
    print("=" * 70)
    print()
    
    # Find obsolete files
    print("Scanning for obsolete files...")
    obsolete = find_obsolete_files(base_path)
    
    # Show summary
    print()
    print("=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print()
    
    # Already removed
    if obsolete['already_removed']:
        print("✓ Already Removed (Previous Cleanup):")
        for item in obsolete['already_removed']:
            print(f"  - {item}")
        print()
    
    # Python cache
    if obsolete['python_cache']:
        size = calculate_size(obsolete['python_cache'])
        print(f"Python Cache Files: {len(obsolete['python_cache'])} files ({format_size(size)})")
        if args.verbose:
            for path in obsolete['python_cache'][:5]:
                print(f"  - {path}")
            if len(obsolete['python_cache']) > 5:
                print(f"  ... and {len(obsolete['python_cache']) - 5} more")
        print()
    
    # Test temp
    if obsolete['test_temp']:
        size = calculate_size(obsolete['test_temp'])
        print(f"Test Temp Files: {len(obsolete['test_temp'])} files ({format_size(size)})")
        if args.verbose:
            for path in obsolete['test_temp']:
                print(f"  - {path}")
        print()
    
    # Backup files
    if obsolete['backup_files']:
        size = calculate_size(obsolete['backup_files'])
        print(f"Backup Files: {len(obsolete['backup_files'])} files ({format_size(size)})")
        if args.verbose:
            for path in obsolete['backup_files']:
                print(f"  - {path}")
        print()
    
    # Total
    total_files = sum(len(paths) for cat, paths in obsolete.items() if cat != 'already_removed')
    total_size = sum(calculate_size(paths) for cat, paths in obsolete.items() if cat != 'already_removed')
    
    print("-" * 70)
    print(f"Total: {total_files} files ({format_size(total_size)})")
    print()
    
    # Action
    if args.delete:
        print("=" * 70)
        print("REMOVING FILES...")
        print("=" * 70)
        print()
        
        removed = clean_files(obsolete, dry_run=False)
        
        print()
        print("=" * 70)
        print(f"✓ Removed {removed['count']} files ({format_size(removed['size'])})")
        print("=" * 70)
    else:
        print("=" * 70)
        print("DRY RUN - No files removed")
        print("=" * 70)
        print()
        print("To actually remove these files, run:")
        print(f"  python3 {Path(__file__).name} --delete")
        print()
        print("Files are safe to remove:")
        print("  - Python cache: Regenerated automatically")
        print("  - Test temp: No longer needed")
        print("  - Backup files: Accidental backups")
    
    print()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
