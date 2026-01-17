#!/usr/bin/env python3
"""
Test filter sentence typing effect configuration and UI hooks.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.utils import validate_config
from modules.exceptions import ConfigurationError


def test_filter_sentence_config_valid():
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as handle:
        config = json.load(handle)
    try:
        validate_config(config)
        return True, "✓ filter_sentence config validated"
    except Exception as exc:
        return False, f"✗ filter_sentence config validation failed: {exc}"


def test_filter_sentence_config_invalid():
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as handle:
        config = json.load(handle)
    invalid_effect_rejected = False
    invalid_speed_rejected = False
    config['filter_sentence']['effect'] = 'neon'
    try:
        validate_config(config)
        return False, "✗ invalid filter_sentence effect was accepted"
    except ConfigurationError:
        invalid_effect_rejected = True
    config['filter_sentence']['effect'] = 'terminal'
    config['filter_sentence']['typing_speed_ms'] = -5
    try:
        validate_config(config)
        return False, "✗ invalid typing_speed_ms was accepted"
    except ConfigurationError:
        invalid_speed_rejected = True
    if invalid_effect_rejected and invalid_speed_rejected:
        return True, "✓ invalid filter_sentence values rejected"
    return False, "✗ invalid filter_sentence values were not rejected"


def test_filter_sentence_ui_hooks():
    js_path = Path(__file__).parent.parent / 'assets' / 'js' / 'filter-description-ui.js'
    content = js_path.read_text(encoding='utf-8')
    required_tokens = ['filterEffect', 'prefers-reduced-motion', 'typeText']
    missing = [token for token in required_tokens if token not in content]
    if missing:
        return False, f"✗ missing UI hooks in filter-description-ui.js: {', '.join(missing)}"
    return True, "✓ filter sentence UI hooks present"


def main():
    tests = [
        test_filter_sentence_config_valid,
        test_filter_sentence_config_invalid,
        test_filter_sentence_ui_hooks,
    ]
    results = []
    for test in tests:
        ok, message = test()
        print(message)
        results.append(ok)
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
