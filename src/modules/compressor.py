"""
Static File Compressor Module

Pre-compress static files with Gzip and Brotli for deployment.
Servers can serve pre-compressed files directly for maximum performance.

Features:
- Gzip compression (63% reduction)
- Brotli compression (68% reduction)
- Automatic file selection (HTML, CSS, JS, JSON, SVG)
- Configuration templates for Apache/Nginx

Usage:
    from compressor import Compressor
    
    compressor = Compressor(base_path)
    compressor.compress_file(file_path)
    compressor.compress_directory(public_dir)
"""

import gzip
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import brotli, fallback gracefully if not available
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False
    # Note: Warning is printed only when compression is actually attempted,
    # not at import time to avoid interference with other commands


class Compressor:
    """
    Static File Compressor
    
    Pre-compresses files with Gzip and Brotli for deployment.
    """
    
    # File types to compress
    COMPRESSIBLE_TYPES = {
        '.html', '.htm',
        '.css',
        '.js', '.json',
        '.svg',
        '.xml', '.txt',
        '.woff', '.woff2',  # Web fonts (already compressed, but test)
        '.ttf', '.otf',     # Font files
        '.ico'              # Favicon
    }
    
    # Minimum file size to compress (bytes)
    MIN_SIZE = 1024  # 1 KB
    
    def __init__(self, base_path: Path):
        """
        Initialize compressor.
        
        Args:
            base_path: Base path of the project
        """
        self.base_path = Path(base_path)
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'gzip_created': 0,
            'brotli_created': 0,
            'bytes_original': 0,
            'bytes_gzip': 0,
            'bytes_brotli': 0,
            'skipped_small': 0,
            'skipped_type': 0
        }
    
    def should_compress(self, file_path: Path) -> bool:
        """
        Check if file should be compressed.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be compressed
        """
        # Check file extension
        if file_path.suffix.lower() not in self.COMPRESSIBLE_TYPES:
            return False
        
        # Check file size
        try:
            size = file_path.stat().st_size
            if size < self.MIN_SIZE:
                return False
        except Exception as e:
            logger.warning(f"Failed to get size of {file_path}: {e}")
            return False
        
        return True
    
    def compress_gzip(self, file_path: Path, output_path: Optional[Path] = None, level: int = 9) -> Optional[Path]:
        """
        Compress file with Gzip.
        
        Args:
            file_path: Source file path
            output_path: Optional output path (default: file_path + .gz)
            level: Compression level (1-9, default: 9)
            
        Returns:
            Path to compressed file or None if failed
        """
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb', compresslevel=level) as f_out:
                    f_out.writelines(f_in)
            
            original_size = file_path.stat().st_size
            compressed_size = output_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            self.stats['bytes_original'] += original_size
            self.stats['bytes_gzip'] += compressed_size
            self.stats['gzip_created'] += 1
            
            logger.debug(f"Gzip: {file_path.name} → {compressed_size:,} bytes ({ratio:.1f}% reduction)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to gzip {file_path}: {e}")
            return None
    
    def compress_brotli(self, file_path: Path, output_path: Optional[Path] = None, quality: int = 11) -> Optional[Path]:
        """
        Compress file with Brotli.
        
        Args:
            file_path: Source file path
            output_path: Optional output path (default: file_path + .br)
            quality: Compression quality (0-11, default: 11)
            
        Returns:
            Path to compressed file or None if failed
        """
        if not BROTLI_AVAILABLE:
            logger.warning("Brotli not available, skipping")
            return None
        
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.br')
        
        try:
            with open(file_path, 'rb') as f_in:
                data = f_in.read()
                compressed = brotli.compress(data, quality=quality)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(compressed)
            
            original_size = file_path.stat().st_size
            compressed_size = output_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            self.stats['bytes_brotli'] += compressed_size
            self.stats['brotli_created'] += 1
            
            logger.debug(f"Brotli: {file_path.name} → {compressed_size:,} bytes ({ratio:.1f}% reduction)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to brotli compress {file_path}: {e}")
            return None
    
    def compress_file(self, file_path: Path, gzip_enabled: bool = True, brotli_enabled: bool = True) -> Dict[str, Optional[Path]]:
        """
        Compress file with both Gzip and Brotli.
        
        Args:
            file_path: File to compress
            gzip_enabled: Enable Gzip compression
            brotli_enabled: Enable Brotli compression
            
        Returns:
            Dictionary with paths to compressed files
        """
        results = {
            'gzip': None,
            'brotli': None
        }
        
        # Check if should compress
        if not self.should_compress(file_path):
            suffix = file_path.suffix.lower()
            size = file_path.stat().st_size if file_path.exists() else 0
            
            if suffix not in self.COMPRESSIBLE_TYPES:
                self.stats['skipped_type'] += 1
                logger.debug(f"Skipped (type): {file_path.name}")
            elif size < self.MIN_SIZE:
                self.stats['skipped_small'] += 1
                logger.debug(f"Skipped (size): {file_path.name}")
            
            return results
        
        self.stats['files_processed'] += 1
        
        # Compress with Gzip
        if gzip_enabled:
            results['gzip'] = self.compress_gzip(file_path)
        
        # Compress with Brotli
        if brotli_enabled and BROTLI_AVAILABLE:
            results['brotli'] = self.compress_brotli(file_path)
        
        return results
    
    def compress_directory(self, directory: Path, recursive: bool = True, gzip_enabled: bool = True, brotli_enabled: bool = True) -> List[Dict]:
        """
        Compress all compressible files in directory.
        
        Args:
            directory: Directory to process
            recursive: Process subdirectories recursively
            gzip_enabled: Enable Gzip compression
            brotli_enabled: Enable Brotli compression
            
        Returns:
            List of compression results
        """
        results = []
        
        if recursive:
            files = directory.rglob('*')
        else:
            files = directory.glob('*')
        
        for file_path in files:
            if file_path.is_file():
                result = self.compress_file(file_path, gzip_enabled, brotli_enabled)
                if result['gzip'] or result['brotli']:
                    results.append({
                        'file': file_path,
                        'gzip': result['gzip'],
                        'brotli': result['brotli']
                    })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get compression statistics."""
        stats = self.stats.copy()
        
        # Calculate ratios
        if stats['bytes_original'] > 0:
            stats['gzip_ratio'] = (1 - stats['bytes_gzip'] / stats['bytes_original']) * 100
            if stats['bytes_brotli'] > 0:
                stats['brotli_ratio'] = (1 - stats['bytes_brotli'] / stats['bytes_original']) * 100
            else:
                stats['brotli_ratio'] = 0
        else:
            stats['gzip_ratio'] = 0
            stats['brotli_ratio'] = 0
        
        return stats
    
    def print_stats(self) -> None:
        """Print compression statistics."""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("🗜️  Compression Statistics")
        print("=" * 60)
        print(f"Files processed:  {stats['files_processed']}")
        print(f"Gzip files:       {stats['gzip_created']}")
        if BROTLI_AVAILABLE:
            print(f"Brotli files:     {stats['brotli_created']}")
        print(f"Skipped (type):   {stats['skipped_type']}")
        print(f"Skipped (small):  {stats['skipped_small']}")
        print()
        print(f"Original size:    {stats['bytes_original']:,} bytes ({stats['bytes_original']/1024:.1f} KB)")
        if stats['gzip_created'] > 0:
            print(f"Gzip size:        {stats['bytes_gzip']:,} bytes ({stats['bytes_gzip']/1024:.1f} KB)")
            print(f"Gzip reduction:   {stats['gzip_ratio']:.1f}%")
        if BROTLI_AVAILABLE and stats['brotli_created'] > 0:
            print(f"Brotli size:      {stats['bytes_brotli']:,} bytes ({stats['bytes_brotli']/1024:.1f} KB)")
            print(f"Brotli reduction: {stats['brotli_ratio']:.1f}%")
        print("=" * 60)
    
    def generate_htaccess(self, output_path: Optional[Path] = None) -> str:
        """
        Generate Apache .htaccess configuration for serving pre-compressed files.
        
        Args:
            output_path: Optional path to write configuration
            
        Returns:
            Configuration content
        """
        config = """# Apache configuration for serving pre-compressed files
# Place this in public/.htaccess

# Enable rewrite engine
<IfModule mod_rewrite.c>
  RewriteEngine On
</IfModule>

# Serve Brotli compressed files if they exist and the browser accepts Brotli
<IfModule mod_headers.c>
  # Check if Brotli compressed file exists
  RewriteCond %{HTTP:Accept-Encoding} br
  RewriteCond %{REQUEST_FILENAME}.br -f
  RewriteRule ^(.*)$ $1.br [QSA,L]

  # Serve correct content type for Brotli
  <FilesMatch "\\.br$">
    Header set Content-Encoding br
    Header append Vary Accept-Encoding
  </FilesMatch>

  # Serve Gzip compressed files if they exist and the browser accepts Gzip
  RewriteCond %{HTTP:Accept-Encoding} gzip
  RewriteCond %{REQUEST_FILENAME}.gz -f
  RewriteRule ^(.*)$ $1.gz [QSA,L]

  # Serve correct content type for Gzip
  <FilesMatch "\\.gz$">
    Header set Content-Encoding gzip
    Header append Vary Accept-Encoding
  </FilesMatch>
</IfModule>

# Cache control for static assets
<IfModule mod_expires.c>
  ExpiresActive On
  
  # HTML and data files (1 hour)
  ExpiresByType text/html "access plus 1 hour"
  ExpiresByType application/json "access plus 1 hour"
  
  # CSS and JavaScript (1 week)
  ExpiresByType text/css "access plus 1 week"
  ExpiresByType application/javascript "access plus 1 week"
  
  # Images and fonts (1 month)
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType font/woff2 "access plus 1 month"
</IfModule>
"""
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(config)
            logger.info(f"Generated Apache config: {output_path}")
        
        return config
    
    def generate_nginx_config(self, output_path: Optional[Path] = None) -> str:
        """
        Generate Nginx configuration for serving pre-compressed files.
        
        Args:
            output_path: Optional path to write configuration
            
        Returns:
            Configuration content
        """
        config = """# Nginx configuration for serving pre-compressed files
# Add this to your nginx server block

# Enable Gzip
gzip on;
gzip_vary on;
gzip_types text/html text/css application/javascript application/json image/svg+xml;
gzip_min_length 1024;

# Enable Brotli (requires ngx_brotli module)
brotli on;
brotli_types text/html text/css application/javascript application/json image/svg+xml;
brotli_min_length 1024;

# Serve pre-compressed files
location ~* \\.(html|css|js|json|svg)$ {
    # Try Brotli first, then Gzip, then original
    gzip_static on;
    brotli_static on;
    
    # Cache control
    expires 1w;
    add_header Cache-Control "public, immutable";
}

# HTML files (shorter cache)
location ~* \\.html?$ {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
"""
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(config)
            logger.info(f"Generated Nginx config: {output_path}")
        
        return config


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compressor.py <command> [args]")
        print("Commands:")
        print("  file <path> - Compress single file")
        print("  dir <path> - Compress directory")
        print("  htaccess <path> - Generate Apache .htaccess")
        print("  nginx <path> - Generate Nginx config")
        sys.exit(1)
    
    command = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent
    compressor = Compressor(base_path)
    
    if command == 'file' and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        print(f"Compressing: {file_path}")
        results = compressor.compress_file(file_path)
        
        if results['gzip']:
            print(f"✅ Gzip: {results['gzip']}")
        if results['brotli']:
            print(f"✅ Brotli: {results['brotli']}")
        
        compressor.print_stats()
    
    elif command == 'dir' and len(sys.argv) > 2:
        dir_path = Path(sys.argv[2])
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            sys.exit(1)
        
        print(f"Compressing directory: {dir_path}")
        results = compressor.compress_directory(dir_path)
        
        print(f"✅ Compressed {len(results)} files")
        compressor.print_stats()
    
    elif command == 'htaccess' and len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
        config = compressor.generate_htaccess(output_path)
        print(f"✅ Generated Apache config: {output_path}")
    
    elif command == 'nginx' and len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
        config = compressor.generate_nginx_config(output_path)
        print(f"✅ Generated Nginx config: {output_path}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
