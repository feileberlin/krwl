"""Simple cache for tracking processed source items."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class SourceCache:
    """Persistent cache of processed item keys for a source."""
    cache_path: Optional[Path]
    max_entries: int = 500
    processed_keys: List[str] = field(default_factory=list)

    def load(self) -> None:
        """Load cache from disk."""
        if not self.cache_path or not self.cache_path.exists():
            return
        
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        
        self.processed_keys = data.get("processed_keys", [])
    
    def is_processed(self, key: str) -> bool:
        """Check if key was already processed."""
        return key in self.processed_keys
    
    def mark_processed(self, key: str) -> None:
        """Record a processed key."""
        if key in self.processed_keys:
            return
        self.processed_keys.append(key)
        if len(self.processed_keys) > self.max_entries:
            self.processed_keys = self.processed_keys[-self.max_entries:]
    
    def save(self) -> None:
        """Persist cache to disk."""
        if not self.cache_path:
            return
        
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "processed_keys": self.processed_keys,
            "updated_at": datetime.now().isoformat()
        }
        self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
