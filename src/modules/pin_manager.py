"""
PIN Management Module for Telegram Bot Trusted Organizers

Provides CLI and TUI interfaces for managing 4-digit PINs that allow
trusted organizers to publish events directly via Telegram without editorial review.
"""

import hashlib
import secrets
import os
from pathlib import Path
from typing import Optional, Tuple


class PINManager:
    """Manage PINs for Telegram bot trusted organizers."""
    
    def __init__(self, base_path: Path):
        """
        Initialize PIN manager.
        
        Args:
            base_path: Base path to repository root
        """
        self.base_path = base_path
    
    def generate_pin(self) -> str:
        """
        Generate a random 4-digit PIN using cryptographically secure random.
        
        Returns:
            4-digit PIN as string
        """
        return f"{secrets.randbelow(10000):04d}"
    
    def compute_hash(self, pin: str) -> str:
        """
        Compute SHA256 hash of PIN.
        
        Args:
            pin: 4-digit PIN
            
        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(pin.encode()).hexdigest()
    
    def validate_pin_format(self, pin: str) -> Tuple[bool, Optional[str]]:
        """
        Validate PIN format (4 digits).
        
        Args:
            pin: PIN to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pin:
            return False, "PIN cannot be empty"
        
        if not pin.isdigit():
            return False, "PIN must contain only digits"
        
        if len(pin) != 4:
            return False, f"PIN must be exactly 4 digits (got {len(pin)})"
        
        return True, None
    
    def get_github_secrets_instructions(self) -> str:
        """
        Get instructions for adding PIN hash to GitHub Secrets.
        
        Returns:
            Formatted instructions
        """
        return """
To add PIN hash to GitHub Secrets:

1. Go to your repository on GitHub
2. Navigate to: Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Name: ORGANIZER_PIN_HASH_1 (or _2, _3 for additional organizers)
5. Value: Paste the hash from above
6. Click "Add secret"

Security Notes:
- Never commit PINs to the repository
- Store only hashes in GitHub Secrets
- Share PINs with trusted organizers securely (encrypted message)
- Rotate PINs regularly
- Revoke compromised PINs immediately (delete secret, generate new)
"""
    
    def check_existing_hashes(self) -> dict:
        """
        Check which PIN hash slots are configured in environment.
        
        Returns:
            Dict with slot status
        """
        slots = {}
        for i in range(1, 4):
            env_var = f"ORGANIZER_PIN_HASH_{i}"
            slots[i] = {
                'slot': i,
                'env_var': env_var,
                'configured': env_var in os.environ,
                'hash_preview': os.environ.get(env_var, '')[:8] + '...' if env_var in os.environ else 'Not set'
            }
        return slots
    
    def display_generate_result(self, pin: str, pin_hash: str):
        """
        Display PIN generation result in a formatted way.
        
        Args:
            pin: Generated PIN
            pin_hash: Computed hash
        """
        print()
        print("=" * 70)
        print("Generated New PIN")
        print("=" * 70)
        print()
        print(f"📌 PIN: {pin}")
        print(f"🔐 Hash: {pin_hash}")
        print()
        print("=" * 70)
        print("Next Steps")
        print("=" * 70)
        print()
        print("1. Share PIN with trusted organizer (securely, e.g., encrypted message)")
        print("2. Add hash to GitHub Secrets:")
        print(self.get_github_secrets_instructions())
        print("3. Trusted organizer can now publish via Telegram:")
        print("   Format:")
        print("   PIN:1234")
        print("   {")
        print('     "title": "Event Title",')
        print('     "start_time": "2026-01-25T18:00:00",')
        print("     ...")
        print("   }")
        print()
        print("⚠️  SECURITY WARNINGS:")
        print("   - Never commit PINs to repository")
        print("   - Never share PINs in public channels")
        print("   - Rotate PINs regularly")
        print("   - Revoke compromised PINs immediately")
        print()
    
    def display_hash_result(self, pin: str, pin_hash: str):
        """
        Display hash computation result.
        
        Args:
            pin: PIN
            pin_hash: Computed hash
        """
        print()
        print("=" * 70)
        print("PIN Hash")
        print("=" * 70)
        print()
        print(f"📌 PIN: {pin}")
        print(f"🔐 Hash: {pin_hash}")
        print()
        print("Use this hash in GitHub Secrets:")
        print("  ORGANIZER_PIN_HASH_1 (or _2, _3)")
        print()
    
    def display_slots_status(self):
        """Display current PIN hash slot configuration status."""
        slots = self.check_existing_hashes()
        
        print()
        print("=" * 70)
        print("PIN Hash Slot Status")
        print("=" * 70)
        print()
        
        for i in range(1, 4):
            slot = slots[i]
            status = "✅ Configured" if slot['configured'] else "❌ Not configured"
            print(f"Slot {i} ({slot['env_var']}): {status}")
            if slot['configured']:
                print(f"   Hash preview: {slot['hash_preview']}")
        
        print()
        print("Note: PIN hashes are stored in GitHub Secrets and loaded as")
        print("environment variables. They are not visible in this interface.")
        print()
    
    def interactive_generate(self):
        """Interactive PIN generation for TUI."""
        pin = self.generate_pin()
        pin_hash = self.compute_hash(pin)
        self.display_generate_result(pin, pin_hash)
    
    def interactive_hash(self):
        """Interactive PIN hash computation for TUI."""
        print()
        print("Enter 4-digit PIN to compute hash:")
        pin = input("PIN: ").strip()
        
        is_valid, error = self.validate_pin_format(pin)
        if not is_valid:
            print(f"\n❌ Invalid PIN: {error}")
            return
        
        pin_hash = self.compute_hash(pin)
        self.display_hash_result(pin, pin_hash)
    
    def interactive_validate(self):
        """Interactive PIN validation for TUI."""
        print()
        print("Enter PIN to validate format:")
        pin = input("PIN: ").strip()
        
        is_valid, error = self.validate_pin_format(pin)
        
        print()
        if is_valid:
            print(f"✅ Valid PIN: {pin}")
            print("   Format: 4 digits ✓")
        else:
            print(f"❌ Invalid PIN: {pin}")
            print(f"   Error: {error}")
    
    def show_tui_menu(self):
        """
        Show interactive TUI menu for PIN management.
        
        Returns:
            True if should continue, False to exit
        """
        print()
        print("=" * 70)
        print("PIN Management - Telegram Trusted Organizers")
        print("=" * 70)
        print()
        print("1. Generate new PIN")
        print("2. Compute hash for existing PIN")
        print("3. Validate PIN format")
        print("4. Show PIN slot status")
        print("5. Show GitHub Secrets instructions")
        print("6. Back to main menu")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            self.interactive_generate()
            input("\nPress Enter to continue...")
            return True
        elif choice == '2':
            self.interactive_hash()
            input("\nPress Enter to continue...")
            return True
        elif choice == '3':
            self.interactive_validate()
            input("\nPress Enter to continue...")
            return True
        elif choice == '4':
            self.display_slots_status()
            input("\nPress Enter to continue...")
            return True
        elif choice == '5':
            print(self.get_github_secrets_instructions())
            input("\nPress Enter to continue...")
            return True
        elif choice == '6':
            return False
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("Press Enter to continue...")
            return True


def main():
    """Standalone entry point for testing."""
    from pathlib import Path
    
    base_path = Path(__file__).parent.parent.parent
    manager = PINManager(base_path)
    
    # Simple TUI loop
    import os
    running = True
    while running:
        os.system('cls' if os.name == 'nt' else 'clear')
        running = manager.show_tui_menu()
    
    print("\nGoodbye!")


if __name__ == '__main__':
    main()
