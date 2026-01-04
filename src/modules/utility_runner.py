#!/usr/bin/env python3
"""
KRWL HOF Utility Runner Module

Centralized utility execution system following KISS principles.
Provides a clean interface to run project utilities without cluttering main CLI.
"""

import subprocess
import sys
from pathlib import Path


class UtilityRunner:
    """Modular utility runner for KRWL HOF
    
    Organizes utilities into categories and provides simple execution:
    - Code quality checks (KISS, feature verification)
    - Documentation generation (README, demos)
    - Configuration management
    - Development tools
    """
    
    # Utility organization by category
    UTILITIES = {
        'quality': {
            'kiss-check': {
                'module': 'kiss_checker',
                'function': 'main',
                'description': 'Check KISS compliance',
                'supports_verbose': True,
                'supports_json': True,
            },
            'verify-features': {
                'module': 'feature_verifier',
                'function': 'main',
                'description': 'Verify features are present in codebase',
                'supports_verbose': True,
                'supports_json': True,
            },
        },
        'config': {
            'config-edit': {
                'module': 'config_editor',
                'function': 'main',
                'description': 'Launch interactive config editor',
            },
        },
    }
    
    def __init__(self, base_path: Path):
        """Initialize utility runner
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        
    def list_utilities(self):
        """List all available utilities by category"""
        print("\n" + "=" * 70)
        print("KRWL HOF Utilities")
        print("=" * 70)
        
        total_utils = 0
        for category, utilities in self.UTILITIES.items():
            print(f"\n{category.upper()} ({len(utilities)} utilities):")
            print("-" * 70)
            for name, info in utilities.items():
                print(f"  • {name:20s} - {info['description']}")
                total_utils += 1
        
        print("\n" + "=" * 70)
        print(f"Total: {total_utils} utilities available")
        print("=" * 70)
        
        print("\nUsage:")
        print("  python3 src/event_manager.py utils UTILITY_NAME [OPTIONS]")
        print("\nExamples:")
        print("  python3 src/event_manager.py utils kiss-check --verbose")
        print("  python3 src/event_manager.py utils verify-features")
        print("  python3 src/event_manager.py utils config-edit")
        print("\nNote: For documentation tasks, use 'docs' command instead")
    
    def run_utility(self, name: str, args: list = None) -> bool:
        """Run a specific utility
        
        Args:
            name: Utility name
            args: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        args = args or []
        
        # Find utility in categories
        utility = None
        for category, utilities in self.UTILITIES.items():
            if name in utilities:
                utility = utilities[name]
                break
        
        if not utility:
            print(f"\n✗ Unknown utility: '{name}'")
            print("\nUse 'utils --list' to see available utilities")
            return False
        
        print(f"\nRunning utility: {name}")
        print("=" * 70)
        
        try:
            if 'module' in utility:
                # Run from src/modules
                return self._run_module(utility, args)
            elif 'script' in utility:
                # Run standalone script
                return self._run_script(utility, args)
            else:
                print(f"✗ Invalid utility configuration: {name}")
                return False
        except Exception as e:
            print(f"\n✗ Error running utility: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_module(self, utility: dict, args: list) -> bool:
        """Run utility from src/modules
        
        Args:
            utility: Utility configuration
            args: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        module_name = utility['module']
        function_name = utility.get('function', 'main')
        
        # Import module
        try:
            sys.path.insert(0, str(self.base_path / 'src'))
            module = __import__(f'modules.{module_name}', fromlist=[function_name])
            func = getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            print(f"✗ Failed to load module: {e}")
            return False
        
        # Prepare arguments
        original_argv = sys.argv
        try:
            # Set up sys.argv for argparse
            sys.argv = ['utility_runner'] + args
            
            # Run the utility
            result = func()
            
            # Handle different return types
            if result is None:
                return True
            elif isinstance(result, bool):
                return result
            elif isinstance(result, int):
                return result == 0
            else:
                return True
                
        finally:
            sys.argv = original_argv
    
    def _run_script(self, utility: dict, args: list) -> bool:
        """Run standalone script
        
        Args:
            utility: Utility configuration
            args: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        script_path = self.base_path / utility['script']
        
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False
        
        # Run script
        cmd = [sys.executable, str(script_path)] + args
        
        result = subprocess.run(
            cmd,
            cwd=str(self.base_path),
        )
        
        return result.returncode == 0


def main():
    """Main entry point for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KRWL HOF Utility Runner')
    parser.add_argument('utility', nargs='?', default=None,
                       help='Utility name to run')
    parser.add_argument('args', nargs='*',
                       help='Additional arguments for the utility')
    parser.add_argument('--list', action='store_true',
                       help='List all available utilities')
    
    args = parser.parse_args()
    
    # Get repository root (go up two levels from src/modules/)
    base_path = Path(__file__).parent.parent.parent
    
    runner = UtilityRunner(base_path)
    
    # List utilities
    if args.list or args.utility is None:
        runner.list_utilities()
        return 0
    
    # Run specific utility
    return 0 if runner.run_utility(args.utility, args.args) else 1


if __name__ == "__main__":
    sys.exit(main())
