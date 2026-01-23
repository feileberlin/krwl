#!/usr/bin/env python3
"""
Lucide Icons Generator CLI Wrapper
===================================

Thin CLI wrapper for the Lucide icons generator module.
For the actual implementation, see src/modules/lucide_generator.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.lucide_generator import main

if __name__ == '__main__':
    sys.exit(main())
