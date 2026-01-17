#!/usr/bin/env python3
"""
Config Validation Script

Validates config.json to prevent common mistakes that could lead to
production issues (e.g., demo events on production map).

Usage:
    python3 scripts/validate_config.py
    
Exit codes:
    0 - Config is valid
    1 - Config validation failed
"""

import json
import sys
from pathlib import Path


def load_config():
    """Load config.json from repository root"""
    config_path = Path(__file__).parent.parent / 'config.json'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: config.json not found at {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in config.json: {e}")
        return None


def validate_environment_setting(config):
    """
    Validate the environment setting in config.json.
    
    CRITICAL CHECK: Ensure environment is set to "auto" in the main branch
    to prevent demo events from appearing on production.
    
    Returns:
        (bool, str): (is_valid, error_message)
    """
    env = config.get('environment')
    
    # Check if environment field exists
    if env is None:
        return False, "Missing 'environment' field in config.json"
    
    # Valid values
    valid_values = ['auto', 'development', 'production']
    if env not in valid_values:
        return False, f"Invalid environment value '{env}'. Must be one of: {valid_values}"
    
    # CRITICAL: Warn if not using auto-detection
    # This is the primary cause of demo events on production
    if env != 'auto':
        return False, (
            f"⚠️  CRITICAL: environment='{env}' will bypass auto-detection!\n"
            f"    This means:\n"
            f"    - If env='development': Demo events will show in production/CI\n"
            f"    - If env='production': Real events will show in local development\n"
            f"\n"
            f"    RECOMMENDATION: Use environment='auto' to let the system detect\n"
            f"    the environment automatically based on where code is running.\n"
            f"\n"
            f"    Only use 'development' or 'production' for temporary testing,\n"
            f"    and ALWAYS reset to 'auto' before committing to main branch."
        )
    
    return True, None


def validate_config():
    """
    Main validation function.
    
    Returns:
        bool: True if config is valid, False otherwise
    """
    print("=" * 70)
    print("🔍 Validating config.json")
    print("=" * 70)
    
    # Load config
    config = load_config()
    if config is None:
        return False
    
    # Run validation checks
    checks = [
        ("Environment Setting", validate_environment_setting),
    ]
    
    all_valid = True
    for check_name, check_func in checks:
        is_valid, error_msg = check_func(config)
        
        if is_valid:
            print(f"✅ {check_name}: OK")
        else:
            print(f"❌ {check_name}: FAILED")
            print(f"   {error_msg}")
            all_valid = False
    
    print("=" * 70)
    
    if all_valid:
        print("✅ Config validation passed")
        return True
    else:
        print("❌ Config validation failed")
        print("\nPlease fix the issues above before committing.")
        return False


if __name__ == '__main__':
    is_valid = validate_config()
    sys.exit(0 if is_valid else 1)
