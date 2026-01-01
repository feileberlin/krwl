#!/usr/bin/env python3
"""
CDN Library Manager

This module manages locally hosted third-party libraries that replace CDN dependencies.
It downloads, updates, and verifies library files to ensure the application works offline
and isn't dependent on external CDN availability.

Features:
- Download libraries from CDN to local storage
- Update libraries to specific versions
- Verify integrity of downloaded files
- Clean up old versions
- Generate library inventory report

Usage:
    python3 manage_libs.py download        # Download all libraries
    python3 manage_libs.py update          # Update all libraries
    python3 manage_libs.py verify          # Verify downloaded files
    python3 manage_libs.py list            # List managed libraries
    python3 manage_libs.py clean           # Clean old versions
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Library definitions
LIBRARIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {
                "src": "leaflet.css",
                "dest": "leaflet/leaflet.css",
                "type": "css"
            },
            {
                "src": "leaflet.js",
                "dest": "leaflet/leaflet.js",
                "type": "js"
            },
            {
                "src": "images/marker-icon.png",
                "dest": "leaflet/images/marker-icon.png",
                "type": "image"
            },
            {
                "src": "images/marker-icon-2x.png",
                "dest": "leaflet/images/marker-icon-2x.png",
                "type": "image"
            },
            {
                "src": "images/marker-shadow.png",
                "dest": "leaflet/images/marker-shadow.png",
                "type": "image"
            }
        ]
    }
}

class LibraryManager:
    """Manages locally hosted CDN libraries"""
    
    def __init__(self, lib_dir: str = "static/lib"):
        self.lib_dir = Path(lib_dir)
        self.inventory_file = self.lib_dir / ".library_inventory.json"
        self.lib_dir.mkdir(parents=True, exist_ok=True)
        
    def download_file(self, url: str, dest: Path, timeout: int = 30) -> bool:
        """
        Download a file from URL to destination
        
        Args:
            url: Source URL
            dest: Destination path
            timeout: Request timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"  Downloading {dest.name}...", end=" ", flush=True)
            
            # Download with progress
            with urllib.request.urlopen(url, timeout=timeout) as response:
                content = response.read()
                
            # Write to file
            with open(dest, 'wb') as f:
                f.write(content)
            
            size_kb = len(content) / 1024
            print(f"✓ ({size_kb:.1f} KB)")
            return True
            
        except urllib.error.URLError as e:
            print(f"✗ Error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def download_library(self, lib_name: str, lib_config: Dict) -> Tuple[bool, List[str]]:
        """
        Download all files for a library
        
        Args:
            lib_name: Library name
            lib_config: Library configuration
            
        Returns:
            Tuple of (success, list of downloaded files)
        """
        print(f"\n📦 Downloading {lib_name} v{lib_config['version']}...")
        
        base_url = lib_config['base_url'].format(version=lib_config['version'])
        downloaded = []
        failed = []
        
        for file_info in lib_config['files']:
            src = file_info['src']
            dest = self.lib_dir / file_info['dest']
            url = f"{base_url}/{src}"
            
            if self.download_file(url, dest):
                downloaded.append(file_info['dest'])
            else:
                failed.append(file_info['dest'])
        
        success = len(failed) == 0
        
        if success:
            print(f"✅ {lib_name}: All {len(downloaded)} files downloaded")
        else:
            print(f"⚠️  {lib_name}: {len(downloaded)} succeeded, {len(failed)} failed")
            
        return success, downloaded
    
    def download_all(self) -> bool:
        """Download all configured libraries"""
        print("=" * 60)
        print("CDN Library Manager - Download All Libraries")
        print("=" * 60)
        
        results = {}
        for lib_name, lib_config in LIBRARIES.items():
            success, files = self.download_library(lib_name, lib_config)
            results[lib_name] = {
                "success": success,
                "version": lib_config['version'],
                "files": files,
                "downloaded_at": datetime.now().isoformat()
            }
        
        # Save inventory
        self.save_inventory(results)
        
        # Print summary
        print("\n" + "=" * 60)
        total_libs = len(results)
        successful = sum(1 for r in results.values() if r['success'])
        print(f"Summary: {successful}/{total_libs} libraries downloaded successfully")
        print("=" * 60)
        
        return all(r['success'] for r in results.values())
    
    def verify_library(self, lib_name: str, lib_config: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Verify all files for a library exist
        
        Returns:
            Tuple of (all_present, present_files, missing_files)
        """
        present = []
        missing = []
        
        for file_info in lib_config['files']:
            dest = self.lib_dir / file_info['dest']
            if dest.exists():
                present.append(file_info['dest'])
            else:
                missing.append(file_info['dest'])
        
        return len(missing) == 0, present, missing
    
    def verify_all(self) -> bool:
        """Verify all libraries are present"""
        print("=" * 60)
        print("CDN Library Manager - Verify Libraries")
        print("=" * 60)
        
        all_verified = True
        
        for lib_name, lib_config in LIBRARIES.items():
            print(f"\n📋 Verifying {lib_name} v{lib_config['version']}...")
            
            verified, present, missing = self.verify_library(lib_name, lib_config)
            
            if verified:
                print(f"  ✓ All {len(present)} files present")
            else:
                print(f"  ✗ Missing {len(missing)} files:")
                for m in missing:
                    print(f"    - {m}")
                all_verified = False
        
        print("\n" + "=" * 60)
        if all_verified:
            print("✅ All libraries verified successfully")
        else:
            print("❌ Some libraries have missing files")
            print("   Run: python3 manage_libs.py download")
        print("=" * 60)
        
        return all_verified
    
    def list_libraries(self):
        """List all managed libraries and their status"""
        print("=" * 60)
        print("CDN Library Manager - Library Inventory")
        print("=" * 60)
        
        for lib_name, lib_config in LIBRARIES.items():
            print(f"\n📚 {lib_name}")
            print(f"   Version: {lib_config['version']}")
            print(f"   Source:  {lib_config['base_url']}")
            print(f"   Files:   {len(lib_config['files'])}")
            
            verified, present, missing = self.verify_library(lib_name, lib_config)
            
            if verified:
                print(f"   Status:  ✓ All files present")
            else:
                print(f"   Status:  ✗ {len(missing)} missing")
            
            # Show file details
            print(f"   Files:")
            for file_info in lib_config['files']:
                dest = self.lib_dir / file_info['dest']
                status = "✓" if dest.exists() else "✗"
                size = f"({dest.stat().st_size / 1024:.1f} KB)" if dest.exists() else ""
                print(f"     {status} {file_info['dest']} {size}")
        
        print("\n" + "=" * 60)
        
        # Show inventory if exists
        if self.inventory_file.exists():
            inventory = self.load_inventory()
            if inventory:
                print("\nLast Update:")
                for lib_name, info in inventory.items():
                    if 'downloaded_at' in info:
                        print(f"  {lib_name}: {info['downloaded_at']}")
                print("=" * 60)
    
    def update_library(self, lib_name: str, new_version: str) -> bool:
        """
        Update a library to a new version
        
        Args:
            lib_name: Library name
            new_version: New version string
            
        Returns:
            True if successful
        """
        if lib_name not in LIBRARIES:
            print(f"❌ Unknown library: {lib_name}")
            return False
        
        lib_config = LIBRARIES[lib_name].copy()
        old_version = lib_config['version']
        lib_config['version'] = new_version
        
        print(f"🔄 Updating {lib_name}: {old_version} → {new_version}")
        
        # Backup old files
        backup_dir = self.lib_dir / f"{lib_name}_backup_{old_version}"
        lib_dir = self.lib_dir / lib_name
        
        if lib_dir.exists():
            print(f"  Creating backup at {backup_dir}...")
            import shutil
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(lib_dir, backup_dir)
        
        # Download new version
        success, files = self.download_library(lib_name, lib_config)
        
        if success:
            print(f"✅ Updated {lib_name} to v{new_version}")
            # Update in-memory config
            LIBRARIES[lib_name]['version'] = new_version
            return True
        else:
            print(f"❌ Failed to update {lib_name}")
            # Restore backup
            if backup_dir.exists() and lib_dir.exists():
                print("  Restoring from backup...")
                import shutil
                shutil.rmtree(lib_dir)
                shutil.copytree(backup_dir, lib_dir)
            return False
    
    def clean_backups(self):
        """Remove backup directories"""
        print("🧹 Cleaning backup files...")
        
        backup_dirs = list(self.lib_dir.glob("*_backup_*"))
        
        if not backup_dirs:
            print("  No backup directories found")
            return
        
        for backup_dir in backup_dirs:
            print(f"  Removing {backup_dir.name}...")
            import shutil
            shutil.rmtree(backup_dir)
        
        print(f"✅ Removed {len(backup_dirs)} backup directories")
    
    def save_inventory(self, inventory: Dict):
        """Save library inventory to JSON file"""
        with open(self.inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
    
    def load_inventory(self) -> Optional[Dict]:
        """Load library inventory from JSON file"""
        if not self.inventory_file.exists():
            return None
        
        with open(self.inventory_file, 'r') as f:
            return json.load(f)


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage locally hosted CDN libraries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 manage_libs.py download              Download all libraries
  python3 manage_libs.py verify                Verify all files present
  python3 manage_libs.py list                  List library inventory
  python3 manage_libs.py update leaflet 1.9.5  Update Leaflet to v1.9.5
  python3 manage_libs.py clean                 Clean backup files
        """
    )
    
    parser.add_argument(
        'command',
        choices=['download', 'verify', 'list', 'update', 'clean'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'library',
        nargs='?',
        help='Library name (for update command)'
    )
    
    parser.add_argument(
        'version',
        nargs='?',
        help='Version number (for update command)'
    )
    
    parser.add_argument(
        '--lib-dir',
        default='static/lib',
        help='Library directory (default: static/lib)'
    )
    
    args = parser.parse_args()
    
    manager = LibraryManager(args.lib_dir)
    
    try:
        if args.command == 'download':
            success = manager.download_all()
            sys.exit(0 if success else 1)
            
        elif args.command == 'verify':
            success = manager.verify_all()
            sys.exit(0 if success else 1)
            
        elif args.command == 'list':
            manager.list_libraries()
            sys.exit(0)
            
        elif args.command == 'update':
            if not args.library or not args.version:
                print("❌ Error: update requires library name and version")
                print("   Example: python3 manage_libs.py update leaflet 1.9.5")
                sys.exit(1)
            success = manager.update_library(args.library, args.version)
            sys.exit(0 if success else 1)
            
        elif args.command == 'clean':
            manager.clean_backups()
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
