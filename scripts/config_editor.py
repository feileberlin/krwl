#!/usr/bin/env python3
"""
Thin wrapper for config_editor module
Maintains backward compatibility while using modular architecture
"""

import sys
from pathlib import Path

# Add src to path (go up one level from scripts/ to project root, then to src/)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.config_editor import main

if __name__ == "__main__":
    main()
