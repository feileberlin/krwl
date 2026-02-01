"""
Asset Manager Module - CDN Asset Version Tracking

Handles version tracking, checksum verification, and automatic updates
for third-party CDN assets (Leaflet.js, fonts, etc.).

Features:
- Track asset versions and checksums locally
- Check for upstream version updates
- Verify asset integrity with checksums
- Maintain version history

Integrates with existing site_generator.py DEPENDENCIES structure.
"""

import json
import hashlib
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages CDN asset versions, checksums, and updates"""
    
    VERSIONS_FILE = 'versions.json'
    
    def __init__(self, base_path: Path, dependencies_dir: Path):
        """
        Initialize AssetManager.
        
        Args:
            base_path: Base path to repository
            dependencies_dir: Path to lib/ directory where assets are stored
        """
        self.base_path = Path(base_path)
        self.dependencies_dir = Path(dependencies_dir)
        self.versions_file = self.dependencies_dir / self.VERSIONS_FILE
        
        # Ensure dependencies directory exists
        self.dependencies_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize version tracking
        self.versions_data = self._load_versions()
    
    def _load_versions(self) -> Dict:
        """
        Load version tracking data from versions.json.
        
        Returns:
            Dictionary with version tracking data
        """
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load versions.json: {e}")
                return self._create_empty_versions()
        else:
            return self._create_empty_versions()
    
    def _create_empty_versions(self) -> Dict:
        """Create empty version tracking structure"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            "assets": {}
        }
    
    def _save_versions(self) -> bool:
        """
        Save version tracking data to versions.json.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.versions_data["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(self.versions_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save versions.json: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 checksum as hex string
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def _fetch_remote_checksum(self, url: str) -> Tuple[Optional[str], int]:
        """
        Fetch remote file and calculate its checksum without saving.
        
        Args:
            url: URL to fetch
        
        Returns:
            Tuple of (checksum, size_bytes) or (None, 0) on error
        """
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
                checksum = hashlib.sha256(content).hexdigest()
                return checksum, len(content)
        except Exception as e:
            logger.warning(f"Failed to fetch remote checksum from {url}: {e}")
            return None, 0
    
    def record_asset_version(self, package_name: str, file_dest: str, 
                            version: str, checksum: str, size_bytes: int) -> bool:
        """
        Record version information for an asset file.
        
        Args:
            package_name: Package name (e.g., 'leaflet')
            file_dest: Destination path relative to lib/ (e.g., 'leaflet/leaflet.js')
            version: Version string (e.g., '1.9.4')
            checksum: SHA256 checksum
            size_bytes: File size in bytes
        
        Returns:
            True if successful, False otherwise
        """
        # Initialize package entry if doesn't exist
        if package_name not in self.versions_data["assets"]:
            self.versions_data["assets"][package_name] = {
                "version": version,
                "files": {}
            }
        
        # Update package version
        self.versions_data["assets"][package_name]["version"] = version
        
        # Record file information
        self.versions_data["assets"][package_name]["files"][file_dest] = {
            "checksum": checksum,
            "size_bytes": size_bytes,
            "last_verified": datetime.now().isoformat()
        }
        
        return self._save_versions()
    
    def verify_asset_integrity(self, file_dest: str) -> bool:
        """
        Verify integrity of a local asset file using stored checksum.
        
        Args:
            file_dest: Destination path relative to lib/ (e.g., 'leaflet/leaflet.js')
        
        Returns:
            True if file exists and checksum matches, False otherwise
        """
        file_path = self.dependencies_dir / file_dest
        
        # Check if file exists
        if not file_path.exists():
            logger.debug(f"Asset file not found: {file_dest}")
            return False
        
        # Find stored checksum
        stored_checksum = None
        for package_name, package_data in self.versions_data["assets"].items():
            if file_dest in package_data.get("files", {}):
                stored_checksum = package_data["files"][file_dest].get("checksum")
                break
        
        if not stored_checksum:
            logger.debug(f"No stored checksum for {file_dest}")
            return False
        
        # Calculate current checksum and compare
        current_checksum = self._calculate_checksum(file_path)
        is_valid = current_checksum == stored_checksum
        
        if not is_valid:
            logger.warning(f"Checksum mismatch for {file_dest}")
        
        return is_valid
    
    def check_for_updates(self, package_name: str, config: Dict) -> Dict:
        """
        Check if a package has updates available upstream.
        
        Compares configured version in DEPENDENCIES with stored local version.
        
        Args:
            package_name: Package name (e.g., 'leaflet')
            config: Package configuration from DEPENDENCIES dict
        
        Returns:
            Dictionary with update information:
            {
                'has_update': bool,
                'current_version': str,
                'latest_version': str,
                'files_changed': List[str]
            }
        """
        result = {
            'has_update': False,
            'current_version': None,
            'latest_version': config.get('version'),
            'files_changed': []
        }
        
        # Get current version
        if package_name in self.versions_data["assets"]:
            result['current_version'] = self.versions_data["assets"][package_name].get('version')
        
        # Check if version changed
        if result['current_version'] != result['latest_version']:
            result['has_update'] = True
            logger.info(f"Version update available for {package_name}: "
                       f"{result['current_version']} → {result['latest_version']}")
            return result
        
        # Check if any files have different checksums (file content changed)
        if package_name in self.versions_data["assets"]:
            base_url = config['base_url'].format(version=config['version'])
            stored_files = self.versions_data["assets"][package_name].get('files', {})
            
            for file_info in config.get('files', []):
                file_dest = file_info['dest']
                
                # Build URL
                if file_info.get('src'):
                    url = f"{base_url}{file_info['src']}"
                else:
                    url = base_url
                
                # Get remote checksum
                remote_checksum, _ = self._fetch_remote_checksum(url)
                
                if remote_checksum and file_dest in stored_files:
                    local_checksum = stored_files[file_dest].get('checksum')
                    if remote_checksum != local_checksum:
                        result['has_update'] = True
                        result['files_changed'].append(file_dest)
                        logger.info(f"File changed: {file_dest} (checksum mismatch)")
        
        return result
    
    def get_asset_info(self, package_name: str = None) -> Dict:
        """
        Get version information for assets.
        
        Args:
            package_name: Optional package name to filter by
        
        Returns:
            Dictionary with asset information
        """
        if package_name:
            return self.versions_data["assets"].get(package_name, {})
        else:
            return self.versions_data["assets"]
    
    def list_all_assets(self) -> List[Dict]:
        """
        List all tracked assets with their version information.
        
        Returns:
            List of dictionaries with asset information
        """
        assets = []
        for package_name, package_data in self.versions_data["assets"].items():
            assets.append({
                'package': package_name,
                'version': package_data.get('version'),
                'file_count': len(package_data.get('files', {})),
                'files': list(package_data.get('files', {}).keys())
            })
        return assets
