"""
Icon Mode TUI Module

Interactive Text User Interface for switching between icon modes.
Provides a simple menu for selecting svg-paths or base64 mode.

Features:
- Interactive mode selection
- Mode comparison display
- Configuration update
- Automatic validation

Usage:
    from icon_mode_tui import IconModeTUI
    
    tui = IconModeTUI(base_path)
    tui.run()
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IconModeTUI:
    """
    Icon Mode TUI
    
    Interactive interface for selecting and switching icon modes.
    """
    
    # Icon mode characteristics
    MODE_INFO = {
        'svg-paths': {
            'name': 'SVG Paths (Default)',
            'description': 'Inline SVG paths - smallest when gzipped',
            'size': '~3 KB gzipped',
            'rendering': 'Browser native (fast)',
            'best_for': 'Production builds, smallest transfer size'
        },
        'base64': {
            'name': 'Base64 Data URLs',
            'description': 'Pre-encoded data URLs - instant rendering',
            'size': '~5 KB gzipped',
            'rendering': 'Instant (pre-rendered)',
            'best_for': 'Development, instant visual feedback'
        }
    }
    
    def __init__(self, base_path: Path, config_path: Optional[Path] = None):
        """
        Initialize icon mode TUI.
        
        Args:
            base_path: Base path of the project
            config_path: Optional path to config.json (default: base_path/config.json)
        """
        self.base_path = Path(base_path)
        self.config_path = config_path or self.base_path / 'config.json'
        
        # Load current config
        self.config = self._load_config()
        self.current_mode = self.config.get('icons', {}).get('mode', 'svg-paths')
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def _clear_screen(self):
        """Clear terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """Print TUI header."""
        print("=" * 60)
        print("  🎨 Icon Mode Selection")
        print("=" * 60)
        print()
    
    def _print_mode_comparison(self):
        """Print mode comparison table."""
        print("Mode Comparison:")
        print("-" * 60)
        
        for mode, info in self.MODE_INFO.items():
            current = " (CURRENT)" if mode == self.current_mode else ""
            print(f"\n{mode.upper()}{current}")
            print(f"  Name:        {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Size:        {info['size']}")
            print(f"  Rendering:   {info['rendering']}")
            print(f"  Best for:    {info['best_for']}")
        
        print()
        print("-" * 60)
    
    def _print_menu(self):
        """Print menu options."""
        print("\nOptions:")
        print("1. Switch to svg-paths mode")
        print("2. Switch to base64 mode")
        print("3. Compare modes")
        print("4. Exit")
        print()
    
    def run(self) -> Optional[str]:
        """
        Run interactive TUI.
        
        Returns:
            Selected mode or None if cancelled
        """
        self._clear_screen()
        self._print_header()
        
        print(f"Current mode: {self.current_mode}")
        print()
        
        self._print_mode_comparison()
        self._print_menu()
        
        while True:
            try:
                choice = input("Enter choice (1-4): ").strip()
                
                if choice == '1':
                    return self._switch_mode('svg-paths')
                elif choice == '2':
                    return self._switch_mode('base64')
                elif choice == '3':
                    self._clear_screen()
                    self._print_header()
                    self._print_mode_comparison()
                    self._print_menu()
                elif choice == '4':
                    print("Cancelled. No changes made.")
                    return None
                else:
                    print("Invalid choice. Please enter 1-4.")
            
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None
    
    def _switch_mode(self, new_mode: str) -> Optional[str]:
        """
        Switch to new icon mode.
        
        Args:
            new_mode: New mode to switch to
            
        Returns:
            New mode if successful, None otherwise
        """
        if new_mode == self.current_mode:
            print(f"Already in {new_mode} mode.")
            return new_mode
        
        print(f"\nSwitching from {self.current_mode} to {new_mode}...")
        
        # Update config
        if 'icons' not in self.config:
            self.config['icons'] = {}
        
        self.config['icons']['mode'] = new_mode
        
        # Save config
        if self._save_config():
            print(f"✅ Successfully switched to {new_mode} mode")
            print(f"   Config updated: {self.config_path}")
            print()
            print("⚠️  Remember to rebuild:")
            print("   python3 src/event_manager.py generate")
            return new_mode
        else:
            print(f"❌ Failed to save config")
            return None


def switch_icon_mode_cli(base_path: Path, mode: str, config_path: Optional[Path] = None) -> bool:
    """
    Switch icon mode via CLI (non-interactive).
    
    Args:
        base_path: Base path of the project
        mode: Mode to switch to (svg-paths or base64)
        config_path: Optional path to config.json
        
    Returns:
        True if successful, False otherwise
    """
    tui = IconModeTUI(base_path, config_path)
    
    if mode not in IconModeTUI.MODE_INFO:
        print(f"❌ Invalid mode: {mode}")
        print(f"   Valid modes: {', '.join(IconModeTUI.MODE_INFO.keys())}")
        return False
    
    result = tui._switch_mode(mode)
    return result is not None


def compare_icon_modes():
    """Print icon mode comparison (CLI helper)."""
    print("\n" + "=" * 60)
    print("🎨 Icon Mode Comparison")
    print("=" * 60)
    
    for mode, info in IconModeTUI.MODE_INFO.items():
        print(f"\n{mode.upper()}")
        print(f"  Name:        {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Size:        {info['size']}")
        print(f"  Rendering:   {info['rendering']}")
        print(f"  Best for:    {info['best_for']}")
    
    print()
    print("=" * 60)
    print()
    print("💡 Recommendation:")
    print("  • Use 'svg-paths' for production (smallest gzipped size)")
    print("  • Use 'base64' for development (instant rendering)")
    print()


if __name__ == '__main__':
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python icon_mode_tui.py <command> [args]")
        print("Commands:")
        print("  interactive - Run interactive TUI")
        print("  compare - Compare icon modes")
        print("  set <mode> - Set mode directly (svg-paths or base64)")
        sys.exit(1)
    
    command = sys.argv[1]
    base_path = Path(__file__).parent.parent.parent
    
    if command == 'interactive':
        tui = IconModeTUI(base_path)
        result = tui.run()
        
        if result:
            print(f"\n✅ Mode set to: {result}")
        else:
            print("\nNo changes made.")
    
    elif command == 'compare':
        compare_icon_modes()
    
    elif command == 'set' and len(sys.argv) > 2:
        mode = sys.argv[2]
        success = switch_icon_mode_cli(base_path, mode)
        
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
