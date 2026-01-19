#!/usr/bin/env python3
"""
PIN Management Helper for Telegram Bot

Generates and manages 4-digit PINs for trusted organizers who can
publish events directly via Telegram without editorial review.

Usage:
    python3 scripts/manage_pins.py generate         # Generate new PIN and hash
    python3 scripts/manage_pins.py validate PIN     # Validate a PIN format
    python3 scripts/manage_pins.py hash PIN         # Show hash for existing PIN
"""

import sys
import hashlib
import secrets
import argparse


def generate_pin():
    """Generate a random 4-digit PIN using cryptographically secure random."""
    return f"{secrets.randbelow(10000):04d}"


def compute_hash(pin: str) -> str:
    """Compute SHA256 hash of PIN."""
    return hashlib.sha256(pin.encode()).hexdigest()


def validate_pin(pin: str) -> bool:
    """Validate PIN format (4 digits)."""
    return pin.isdigit() and len(pin) == 4


def cmd_generate(args):
    """Generate a new PIN with hash."""
    pin = generate_pin()
    pin_hash = compute_hash(pin)
    
    print("=" * 70)
    print("Generated New PIN")
    print("=" * 70)
    print()
    print(f"📌 PIN: {pin}")
    print(f"🔐 Hash: {pin_hash}")
    print()
    print("=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print()
    print("1. Share PIN with trusted organizer (securely, e.g., encrypted message)")
    print("2. Add hash to GitHub Secrets:")
    print("   - Go to: Settings > Secrets and variables > Actions")
    print("   - Create secret: ORGANIZER_PIN_HASH_1 (or _2, _3)")
    print("   - Value: Copy the hash above")
    print()
    print("3. Trusted organizer can now publish via Telegram:")
    print("   Format:")
    print("   PIN:1234")
    print("   {")
    print('     "title": "Event Title",')
    print('     "start_time": "2026-01-25T18:00:00",')
    print("     ...")
    print("   }")
    print()
    print("⚠️  SECURITY NOTES:")
    print("   - Never commit PINs to repository")
    print("   - Never share PINs in public channels")
    print("   - Rotate PINs regularly")
    print("   - Revoke compromised PINs immediately")
    print()


def cmd_hash(args):
    """Show hash for existing PIN."""
    pin = args.pin.strip()
    
    if not validate_pin(pin):
        print("❌ Invalid PIN format. Must be 4 digits.")
        sys.exit(1)
    
    pin_hash = compute_hash(pin)
    
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


def cmd_validate(args):
    """Validate PIN format."""
    pin = args.pin.strip()
    
    if validate_pin(pin):
        print(f"✅ Valid PIN: {pin}")
        print("   Format: 4 digits ✓")
    else:
        print(f"❌ Invalid PIN: {pin}")
        if not pin.isdigit():
            print("   Error: Must contain only digits")
        if len(pin) != 4:
            print(f"   Error: Must be exactly 4 digits (got {len(pin)})")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Manage PINs for Telegram bot trusted organizers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate              # Generate new random PIN
  %(prog)s hash 1234              # Show hash for PIN 1234
  %(prog)s validate 5678          # Validate PIN format

Security:
  - PINs are 4 digits (0000-9999)
  - Hashes use SHA256
  - Never commit PINs to repository
  - Store hashes in GitHub Secrets only
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # generate command
    parser_generate = subparsers.add_parser(
        'generate',
        help='Generate a new random PIN with hash'
    )
    parser_generate.set_defaults(func=cmd_generate)
    
    # hash command
    parser_hash = subparsers.add_parser(
        'hash',
        help='Compute hash for existing PIN'
    )
    parser_hash.add_argument('pin', help='4-digit PIN')
    parser_hash.set_defaults(func=cmd_hash)
    
    # validate command
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate PIN format'
    )
    parser_validate.add_argument('pin', help='4-digit PIN to validate')
    parser_validate.set_defaults(func=cmd_validate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
