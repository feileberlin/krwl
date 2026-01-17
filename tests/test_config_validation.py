#!/usr/bin/env python3
"""
Test Config Validation

Ensures the config validation script correctly catches environment issues.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def test_validation_passes_with_auto():
    """Test that validation passes when environment='auto'"""
    result = subprocess.run(
        ['python3', 'scripts/validate_config.py'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Validation should pass with environment='auto', but failed: {result.stdout}"
    assert "✅ Config validation passed" in result.stdout
    print("✅ Test passed: Validation accepts environment='auto'")


def test_validation_fails_with_development():
    """Test that validation fails when environment='development'"""
    # Load config
    config_path = Path('config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Modify environment to development
    config['environment'] = 'development'
    
    # Create temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        temp_path = f.name
    
    try:
        # Run validation on temp config
        result = subprocess.run(
            ['python3', '-c', f'''
import sys
from pathlib import Path

# Patch config path
original_code = open("scripts/validate_config.py").read()
patched_code = original_code.replace(
    "config_path = Path(__file__).parent.parent / 'config.json'",
    "config_path = Path('{temp_path}')"
)

exec(patched_code)
'''],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, f"Validation should fail with environment='development', but passed: {result.stdout}"
        assert "CRITICAL" in result.stdout or "FAILED" in result.stdout
        print("✅ Test passed: Validation rejects environment='development'")
    finally:
        # Clean up temp file
        Path(temp_path).unlink()


def test_validation_fails_with_production():
    """Test that validation fails when environment='production'"""
    # Load config
    config_path = Path('config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Modify environment to production
    config['environment'] = 'production'
    
    # Create temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        temp_path = f.name
    
    try:
        # Run validation on temp config
        result = subprocess.run(
            ['python3', '-c', f'''
import sys
from pathlib import Path

# Patch config path
original_code = open("scripts/validate_config.py").read()
patched_code = original_code.replace(
    "config_path = Path(__file__).parent.parent / 'config.json'",
    "config_path = Path('{temp_path}')"
)

exec(patched_code)
'''],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, f"Validation should fail with environment='production', but passed: {result.stdout}"
        assert "CRITICAL" in result.stdout or "FAILED" in result.stdout
        print("✅ Test passed: Validation rejects environment='production'")
    finally:
        # Clean up temp file
        Path(temp_path).unlink()


if __name__ == '__main__':
    print("Testing config validation...")
    print("=" * 70)
    
    try:
        test_validation_passes_with_auto()
        test_validation_fails_with_development()
        test_validation_fails_with_production()
        
        print("=" * 70)
        print("✅ All config validation tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print("=" * 70)
        print(f"❌ Test failed: {e}")
        sys.exit(1)
