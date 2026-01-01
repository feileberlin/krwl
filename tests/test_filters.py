#!/usr/bin/env python3
"""
KRWL HOF Filter Testing Script (Wrapper)

Thin wrapper that delegates to src/modules/filter_tester.py
Maintains backward compatibility with existing scripts and CI workflows.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import and delegate to module
from modules.filter_tester import main

if __name__ == "__main__":
    main()
