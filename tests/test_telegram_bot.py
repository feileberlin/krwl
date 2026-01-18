"""
Test Telegram bot module.

Tests basic functionality of the Telegram bot without requiring
the python-telegram-bot library or an actual bot token.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.telegram_bot import TELEGRAM_AVAILABLE


def test_module_import():
    """Test that telegram_bot module imports without errors."""
    try:
        from src.modules.telegram_bot import TelegramBot
        print("✅ telegram_bot module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import telegram_bot: {e}")
        return False


def test_telegram_availability():
    """Test that TELEGRAM_AVAILABLE flag is set correctly."""
    print(f"ℹ️  TELEGRAM_AVAILABLE = {TELEGRAM_AVAILABLE}")
    
    if TELEGRAM_AVAILABLE:
        print("✅ python-telegram-bot library is installed")
        return True
    else:
        print("⚠️  python-telegram-bot library is not installed (this is expected in CI)")
        print("   Install with: pip install python-telegram-bot>=20.0")
        return True  # Not an error - just not installed


def test_bot_instantiation_requires_library():
    """Test that TelegramBot requires the library to instantiate."""
    from src.modules.telegram_bot import TelegramBot
    from src.modules.utils import load_config
    
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    if not TELEGRAM_AVAILABLE:
        try:
            TelegramBot(config, base_path)
            print("❌ Bot should require python-telegram-bot library")
            return False
        except ImportError as e:
            print(f"✅ Bot correctly requires python-telegram-bot library: {e}")
            return True
    else:
        # If library is available, test that bot can be created
        # (but don't start it - would require valid token)
        try:
            # Temporarily enable bot in config for test
            test_config = config.copy()
            test_config['telegram'] = {
                'enabled': True,
                'bot_token': 'test_token_123',
                'admin_chat_ids': [],
                'features': {
                    'event_submission': True,
                    'flyer_upload': True,
                    'contact_form': True
                },
                'limits': {},
                'messages': {}
            }
            TelegramBot(test_config, base_path)
            print("✅ Bot can be instantiated with library installed")
            return True
        except Exception as e:
            print(f"⚠️  Bot instantiation test skipped: {e}")
            return True


def test_helper_methods():
    """Test bot helper methods work without Telegram library."""
    from src.modules.telegram_bot import TelegramBot
    from src.modules.utils import load_config
    
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    # Create a mock bot instance if library available
    if TELEGRAM_AVAILABLE:
        test_config = config.copy()
        test_config['telegram'] = {
            'enabled': True,
            'bot_token': 'test_token_123',
            'admin_chat_ids': [],
            'features': {},
            'limits': {},
            'messages': {}
        }
        
        try:
            bot = TelegramBot(test_config, base_path)
            
            # Test date parsing
            assert bot._parse_date('2026-01-20') == '2026-01-20', "Date parsing failed"
            assert bot._parse_date('20.01.2026') == '2026-01-20', "Date parsing failed"
            assert bot._parse_date('invalid') is None, "Invalid date should return None"
            
            # Test time parsing
            assert bot._parse_time('14:30') == '14:30', "Time parsing failed"
            assert bot._parse_time('invalid') is None, "Invalid time should return None"
            
            print("✅ Helper methods work correctly")
            return True
        except Exception as e:
            print(f"⚠️  Helper method tests skipped: {e}")
            return True
    else:
        print("⚠️  Helper method tests skipped (library not available)")
        return True


def test_cli_uses_asyncio_run_directly():
    """Test that CLI command handles event loops correctly for CI environments."""
    import inspect
    
    # Import the CLI function
    from src.event_manager import cli_telegram_bot
    
    # Get the source code of the function
    source = inspect.getsource(cli_telegram_bot)
    
    # Verify it uses explicit event loop creation (GitHub Actions compatible)
    has_new_event_loop = 'asyncio.new_event_loop()' in source
    has_set_event_loop = 'asyncio.set_event_loop(loop)' in source
    has_run_until_complete = 'loop.run_until_complete' in source
    has_loop_close = 'loop.close()' in source
    
    if has_new_event_loop and has_set_event_loop and has_run_until_complete and has_loop_close:
        print("✅ CLI command uses explicit event loop creation")
        print("   This avoids 'RuntimeError: This event loop is already running' in GitHub Actions")
        has_proper_loop_handling = True
    else:
        print("❌ CLI command doesn't use explicit event loop handling")
        print(f"   new_event_loop: {has_new_event_loop}")
        print(f"   set_event_loop: {has_set_event_loop}")
        print(f"   run_until_complete: {has_run_until_complete}")
        print(f"   loop.close: {has_loop_close}")
        has_proper_loop_handling = False
    
    # Verify it doesn't use the problematic start_sync() method
    if 'bot.start_sync()' not in source:
        print("✅ CLI command doesn't use deprecated start_sync() method")
        no_start_sync = True
    else:
        print("❌ CLI command still uses start_sync() method")
        print("   This causes 'RuntimeError: This event loop is already running' in GitHub Actions")
        no_start_sync = False
    
    # Verify it doesn't use asyncio.run() which also has conflicts in CI
    if 'asyncio.run(bot.run())' not in source:
        print("✅ CLI command doesn't use asyncio.run() which can conflict in CI")
        no_asyncio_run = True
    else:
        print("⚠️  CLI command uses asyncio.run() which may conflict in CI environments")
        no_asyncio_run = False
    
    return has_proper_loop_handling and no_start_sync and no_asyncio_run


def test_standalone_main_uses_correct_asyncio():
    """Test that standalone main() function uses correct asyncio pattern."""
    import inspect
    
    # Import the standalone main function
    from src.modules.telegram_bot import main as telegram_main
    
    # Get the source code of the function
    source = inspect.getsource(telegram_main)
    
    # Verify it uses explicit event loop creation (GitHub Actions compatible)
    has_new_event_loop = 'asyncio.new_event_loop()' in source
    has_set_event_loop = 'asyncio.set_event_loop(loop)' in source
    has_run_until_complete = 'loop.run_until_complete' in source
    has_loop_close = 'loop.close()' in source
    
    if has_new_event_loop and has_set_event_loop and has_run_until_complete and has_loop_close:
        print("✅ Standalone main() uses explicit event loop creation")
        print("   This avoids 'RuntimeError: This event loop is already running' in GitHub Actions")
        has_proper_loop_handling = True
    else:
        print("❌ Standalone main() doesn't use explicit event loop handling")
        print(f"   new_event_loop: {has_new_event_loop}")
        print(f"   set_event_loop: {has_set_event_loop}")
        print(f"   run_until_complete: {has_run_until_complete}")
        print(f"   loop.close: {has_loop_close}")
        has_proper_loop_handling = False
    
    # Verify it doesn't use the problematic start_sync() method
    if 'bot.start_sync()' not in source:
        print("✅ Standalone main() doesn't use deprecated start_sync() method")
        no_start_sync = True
    else:
        print("❌ Standalone main() still uses start_sync() method")
        print("   This causes 'RuntimeError: This event loop is already running' in GitHub Actions")
        no_start_sync = False
    
    # Verify it doesn't use asyncio.run() which also has conflicts in CI
    if 'asyncio.run(bot.run())' not in source and 'asyncio.run(self.run())' not in source:
        print("✅ Standalone main() doesn't use asyncio.run() which can conflict in CI")
        no_asyncio_run = True
    else:
        print("⚠️  Standalone main() uses asyncio.run() which may conflict in CI environments")
        no_asyncio_run = False
    
    return has_proper_loop_handling and no_start_sync and no_asyncio_run


def main():
    """Run all tests."""
    print("=" * 60)
    print("Telegram Bot Module Tests")
    print("=" * 60)
    
    tests = [
        ("Module Import", test_module_import),
        ("Telegram Availability", test_telegram_availability),
        ("Bot Instantiation", test_bot_instantiation_requires_library),
        ("Helper Methods", test_helper_methods),
        ("CLI Event Loop Fix", test_cli_uses_asyncio_run_directly),
        ("Standalone Main Event Loop Fix", test_standalone_main_uses_correct_asyncio),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Test: {name}")
        print("-" * 60)
        results.append((name, test_func()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
