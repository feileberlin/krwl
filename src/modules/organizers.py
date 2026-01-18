"""
Organizer Management Module

Complete organizer management with backend CRUD, TUI, and CLI:
- OrganizerManager: Backend operations (add, update, delete, search, verify, merge)
- OrganizerTUI: Interactive text-based interface
- OrganizerCLI: Command-line interface

Usage:
    # Backend
    from modules.organizers import OrganizerManager
    manager = OrganizerManager(base_path)
    organizer = manager.add_organizer(organizer_obj)
    
    # TUI
    from modules.organizers import OrganizerTUI
    tui = OrganizerTUI(base_path)
    tui.run()
    
    # CLI
    python3 src/event_manager.py organizers list
    python3 src/event_manager.py organizers add --name "Kulturverein Hof"
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from .entity_models import Organizer, generate_organizer_id

logger = logging.getLogger(__name__)


class OrganizerManager:
    """Backend CRUD for organizers.json library - NO UI CODE"""
    
    def __init__(self, base_path: Path):
        """
        Initialize organizer manager.
        
        Args:
            base_path: Repository root path
        """
        self.base_path = Path(base_path)
        self.organizers_file = self.base_path / 'assets' / 'json' / 'organizers.json'
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure organizers.json exists"""
        if not self.organizers_file.exists():
            self.organizers_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                '_comment': 'Organizer library for unified entity management system',
                '_description': 'Central organizer repository with ID-based references.',
                '_version': '1.0',
                'organizers': []
            }
            with open(self.organizers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_data(self) -> dict:
        """Load organizers.json"""
        with open(self.organizers_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: dict):
        """Save organizers.json"""
        with open(self.organizers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_organizer(self, organizer: Organizer) -> str:
        """
        Add new organizer to library.
        
        Args:
            organizer: Organizer object
            
        Returns:
            Organizer ID
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        # Check if ID already exists
        if any(org['id'] == organizer.id for org in organizers):
            raise ValueError(f"Organizer ID already exists: {organizer.id}")
        
        # Set timestamps
        if not organizer.created_at:
            organizer.created_at = datetime.now(timezone.utc).isoformat()
        organizer.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Add to library
        organizers.append(organizer.to_dict())
        data['organizers'] = organizers
        self._save_data(data)
        
        logger.info(f"Added organizer: {organizer.id} - {organizer.name}")
        return organizer.id
    
    def update_organizer(self, organizer_id: str, updates: Dict[str, Any]) -> Organizer:
        """
        Update existing organizer.
        
        Args:
            organizer_id: Organizer ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated Organizer object
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        # Find organizer
        for org in organizers:
            if org['id'] == organizer_id:
                # Apply updates
                for key, value in updates.items():
                    if key not in ['id', 'created_at']:  # Protect immutable fields
                        org[key] = value
                
                # Update timestamp
                org['updated_at'] = datetime.now(timezone.utc).isoformat()
                
                # Save
                data['organizers'] = organizers
                self._save_data(data)
                
                logger.info(f"Updated organizer: {organizer_id}")
                return Organizer.from_dict(org)
        
        raise ValueError(f"Organizer not found: {organizer_id}")
    
    def delete_organizer(self, organizer_id: str):
        """
        Delete organizer from library.
        
        Args:
            organizer_id: Organizer ID to delete
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        # Filter out organizer
        original_count = len(organizers)
        organizers = [org for org in organizers if org['id'] != organizer_id]
        
        if len(organizers) == original_count:
            raise ValueError(f"Organizer not found: {organizer_id}")
        
        data['organizers'] = organizers
        self._save_data(data)
        
        logger.info(f"Deleted organizer: {organizer_id}")
    
    def get_organizer(self, organizer_id: str) -> Optional[Organizer]:
        """
        Get organizer by ID.
        
        Args:
            organizer_id: Organizer ID
            
        Returns:
            Organizer object or None
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        for org in organizers:
            if org['id'] == organizer_id:
                return Organizer.from_dict(org)
        
        return None
    
    def list_organizers(self, verified_only: bool = False) -> List[Organizer]:
        """
        List all organizers.
        
        Args:
            verified_only: If True, only return verified organizers
            
        Returns:
            List of Organizer objects
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        if verified_only:
            organizers = [org for org in organizers if org.get('verified', False)]
        
        return [Organizer.from_dict(org) for org in organizers]
    
    def search_organizers(self, query: str) -> List[Organizer]:
        """
        Search organizers by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Organizer objects
        """
        query_lower = query.lower()
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        results = []
        for org in organizers:
            name = org.get('name', '').lower()
            description = org.get('description', '').lower()
            
            if query_lower in name or query_lower in description:
                results.append(Organizer.from_dict(org))
        
        return results
    
    def verify_organizer(self, organizer_id: str, verified_by: str = None):
        """
        Mark organizer as verified.
        
        Args:
            organizer_id: Organizer ID
            verified_by: User who verified (optional)
        """
        updates = {
            'verified': True,
            'verified_at': datetime.now(timezone.utc).isoformat(),
            'verified_by': verified_by
        }
        self.update_organizer(organizer_id, updates)
    
    def merge_organizers(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Merge two organizers (combine data, update event references).
        
        Args:
            source_id: Organizer to merge from (will be deleted)
            target_id: Organizer to merge into (will be kept)
            
        Returns:
            Dict with merge results
        """
        # Get both organizers
        source = self.get_organizer(source_id)
        target = self.get_organizer(target_id)
        
        if not source:
            raise ValueError(f"Source organizer not found: {source_id}")
        if not target:
            raise ValueError(f"Target organizer not found: {target_id}")
        
        # Merge social media
        merged_social = {**source.social_media, **target.social_media}
        
        # Update target with merged data
        updates = {
            'social_media': merged_social
        }
        
        # Merge metadata
        merged_metadata = {**source.metadata, **target.metadata}
        updates['metadata'] = merged_metadata
        
        self.update_organizer(target_id, updates)
        
        # Delete source
        self.delete_organizer(source_id)
        
        logger.info(f"Merged organizer {source_id} into {target_id}")
        
        return {
            'source_id': source_id,
            'target_id': target_id,
            'merged_social_media': merged_social
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get organizer library statistics.
        
        Returns:
            Dict with stats (total_organizers, verified_count, etc.)
        """
        data = self._load_data()
        organizers = data.get('organizers', [])
        
        verified_count = sum(1 for org in organizers if org.get('verified', False))
        with_website = sum(1 for org in organizers if org.get('website'))
        with_email = sum(1 for org in organizers if org.get('email'))
        with_phone = sum(1 for org in organizers if org.get('phone'))
        
        return {
            'total_organizers': len(organizers),
            'verified_count': verified_count,
            'with_website': with_website,
            'with_email': with_email,
            'with_phone': with_phone
        }


class OrganizerTUI:
    """Interactive TUI - uses OrganizerManager"""
    
    def __init__(self, base_path: Path):
        """Initialize organizer TUI"""
        self.manager = OrganizerManager(base_path)
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Main TUI loop"""
        while self.running:
            self.show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.list_organizers_interactive()
            elif choice == '2':
                self.add_organizer_interactive()
            elif choice == '3':
                self.edit_organizer_interactive()
            elif choice == '4':
                self.verify_organizer_interactive()
            elif choice == '5':
                self.search_organizers_interactive()
            elif choice == '6':
                self.merge_organizers_interactive()
            elif choice == '7':
                self.show_statistics()
            elif choice == '8':
                self.running = False
            else:
                print("\nInvalid choice. Try again.")
                input("Press Enter to continue...")
    
    def show_menu(self):
        """Display main menu"""
        self.clear_screen()
        print("=" * 70)
        print("  Organizer Management")
        print("=" * 70)
        print()
        print("1. List All Organizers")
        print("2. Add New Organizer")
        print("3. Edit Organizer")
        print("4. Verify Organizer")
        print("5. Search Organizers")
        print("6. Merge Organizers")
        print("7. Show Statistics")
        print("8. Back to Main Menu")
        print()
        print("─" * 70)
    
    def list_organizers_interactive(self):
        """List all organizers interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  All Organizers")
        print("=" * 70)
        print()
        
        organizers = self.manager.list_organizers()
        
        if not organizers:
            print("No organizers found.")
        else:
            for i, org in enumerate(organizers, 1):
                verified = "✅" if org.verified else "⚪"
                print(f"{i}. {verified} {org.name} ({org.id})")
                if org.website:
                    print(f"   Website: {org.website}")
                if org.email:
                    print(f"   Email: {org.email}")
                print()
        
        input("Press Enter to continue...")
    
    def add_organizer_interactive(self):
        """Add new organizer interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Add New Organizer")
        print("=" * 70)
        print()
        
        try:
            name = input("Organizer name: ").strip()
            if not name:
                print("❌ Name is required")
                input("Press Enter to continue...")
                return
            
            website = input("Website (optional): ").strip() or None
            email = input("Email (optional): ").strip() or None
            phone = input("Phone (optional): ").strip() or None
            
            # Generate ID
            organizer_id = generate_organizer_id(name)
            
            # Create organizer
            organizer = Organizer(
                id=organizer_id,
                name=name,
                website=website,
                email=email,
                phone=phone
            )
            
            # Add to library
            self.manager.add_organizer(organizer)
            
            print(f"\n✅ Organizer added: {organizer_id}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def edit_organizer_interactive(self):
        """Edit organizer interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Edit Organizer")
        print("=" * 70)
        print()
        
        organizer_id = input("Organizer ID: ").strip()
        if not organizer_id:
            return
        
        organizer = self.manager.get_organizer(organizer_id)
        if not organizer:
            print(f"❌ Organizer not found: {organizer_id}")
            input("Press Enter to continue...")
            return
        
        print(f"\nCurrent: {organizer.name}")
        print(f"Website: {organizer.website or 'N/A'}")
        print(f"Email: {organizer.email or 'N/A'}")
        print(f"Phone: {organizer.phone or 'N/A'}")
        print()
        
        print("Enter new values (leave blank to keep current):")
        name = input(f"Name [{organizer.name}]: ").strip()
        website = input(f"Website [{organizer.website or 'N/A'}]: ").strip()
        email = input(f"Email [{organizer.email or 'N/A'}]: ").strip()
        phone = input(f"Phone [{organizer.phone or 'N/A'}]: ").strip()
        
        updates = {}
        if name:
            updates['name'] = name
        if website:
            updates['website'] = website
        if email:
            updates['email'] = email
        if phone:
            updates['phone'] = phone
        
        if updates:
            try:
                self.manager.update_organizer(organizer_id, updates)
                print(f"\n✅ Organizer updated: {organizer_id}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def verify_organizer_interactive(self):
        """Verify organizer interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Verify Organizer")
        print("=" * 70)
        print()
        
        organizer_id = input("Organizer ID: ").strip()
        if not organizer_id:
            return
        
        try:
            verified_by = input("Verified by (optional): ").strip() or None
            self.manager.verify_organizer(organizer_id, verified_by)
            print(f"\n✅ Organizer verified: {organizer_id}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def search_organizers_interactive(self):
        """Search organizers interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Search Organizers")
        print("=" * 70)
        print()
        
        query = input("Search query: ").strip()
        if not query:
            return
        
        results = self.manager.search_organizers(query)
        
        print()
        if not results:
            print("No results found.")
        else:
            print(f"Found {len(results)} organizers:")
            print()
            for i, org in enumerate(results, 1):
                verified = "✅" if org.verified else "⚪"
                print(f"{i}. {verified} {org.name} ({org.id})")
                if org.website:
                    print(f"   Website: {org.website}")
                if org.email:
                    print(f"   Email: {org.email}")
                print()
        
        input("Press Enter to continue...")
    
    def merge_organizers_interactive(self):
        """Merge organizers interactively"""
        self.clear_screen()
        print("=" * 70)
        print("  Merge Organizers")
        print("=" * 70)
        print()
        print("⚠️  This will merge source into target and delete source")
        print()
        
        source_id = input("Source organizer ID (will be deleted): ").strip()
        target_id = input("Target organizer ID (will be kept): ").strip()
        
        if not source_id or not target_id:
            return
        
        confirm = input(f"\nMerge {source_id} → {target_id}? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        try:
            self.manager.merge_organizers(source_id, target_id)
            print(f"\n✅ Merged successfully")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("Press Enter to continue...")
    
    def show_statistics(self):
        """Show organizer statistics"""
        self.clear_screen()
        print("=" * 70)
        print("  Organizer Statistics")
        print("=" * 70)
        print()
        
        stats = self.manager.get_statistics()
        
        print(f"Total Organizers:   {stats['total_organizers']}")
        print(f"Verified:           {stats['verified_count']}")
        print(f"With Website:       {stats['with_website']}")
        print(f"With Email:         {stats['with_email']}")
        print(f"With Phone:         {stats['with_phone']}")
        print()
        
        input("Press Enter to continue...")


class OrganizerCLI:
    """CLI commands - uses OrganizerManager"""
    
    def __init__(self, base_path: Path):
        """Initialize CLI handler"""
        self.manager = OrganizerManager(base_path)
    
    def handle_command(self, args):
        """Route organizer subcommands"""
        subcommand = args.organizer_command
        
        if subcommand == 'list':
            return self.list_command(args)
        elif subcommand == 'add':
            return self.add_command(args)
        elif subcommand == 'edit':
            return self.edit_command(args)
        elif subcommand == 'verify':
            return self.verify_command(args)
        elif subcommand == 'search':
            return self.search_command(args)
        elif subcommand == 'merge':
            return self.merge_command(args)
        elif subcommand == 'stats':
            return self.stats_command(args)
        else:
            print(f"Unknown organizer command: {subcommand}")
            return 1
    
    def list_command(self, args):
        """List organizers"""
        verified_only = getattr(args, 'verified_only', False)
        output_format = getattr(args, 'format', 'text')
        
        organizers = self.manager.list_organizers(verified_only=verified_only)
        
        if output_format == 'json':
            data = [org.to_dict() for org in organizers]
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Total organizers: {len(organizers)}")
            print()
            for org in organizers:
                verified = "✅" if org.verified else "⚪"
                print(f"{verified} {org.name} ({org.id})")
                if org.website:
                    print(f"   Website: {org.website}")
                if org.email:
                    print(f"   Email: {org.email}")
                print()
        
        return 0
    
    def add_command(self, args):
        """Add organizer"""
        name = args.name
        website = getattr(args, 'website', None)
        email = getattr(args, 'email', None)
        phone = getattr(args, 'phone', None)
        
        organizer_id = generate_organizer_id(name)
        
        organizer = Organizer(
            id=organizer_id,
            name=name,
            website=website,
            email=email,
            phone=phone
        )
        
        try:
            self.manager.add_organizer(organizer)
            print(f"✅ Organizer added: {organizer_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def edit_command(self, args):
        """Edit organizer"""
        organizer_id = args.organizer_id
        
        updates = {}
        if hasattr(args, 'name') and args.name:
            updates['name'] = args.name
        if hasattr(args, 'website') and args.website:
            updates['website'] = args.website
        if hasattr(args, 'email') and args.email:
            updates['email'] = args.email
        if hasattr(args, 'phone') and args.phone:
            updates['phone'] = args.phone
        
        try:
            self.manager.update_organizer(organizer_id, updates)
            print(f"✅ Organizer updated: {organizer_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def verify_command(self, args):
        """Verify organizer"""
        organizer_id = args.organizer_id
        verified_by = getattr(args, 'verified_by', None)
        
        try:
            self.manager.verify_organizer(organizer_id, verified_by)
            print(f"✅ Organizer verified: {organizer_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def search_command(self, args):
        """Search organizers"""
        query = args.query
        
        results = self.manager.search_organizers(query)
        
        print(f"Found {len(results)} organizers:")
        print()
        for org in results:
            verified = "✅" if org.verified else "⚪"
            print(f"{verified} {org.name} ({org.id})")
            if org.website:
                print(f"   Website: {org.website}")
            if org.email:
                print(f"   Email: {org.email}")
            print()
        
        return 0
    
    def merge_command(self, args):
        """Merge organizers"""
        source_id = args.source_id
        target_id = args.target_id
        
        try:
            self.manager.merge_organizers(source_id, target_id)
            print(f"✅ Merged {source_id} → {target_id}")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def stats_command(self, args):
        """Show statistics"""
        stats = self.manager.get_statistics()
        
        print("Organizer Statistics:")
        print("=" * 50)
        print(f"Total Organizers:   {stats['total_organizers']}")
        print(f"Verified:           {stats['verified_count']}")
        print(f"With Website:       {stats['with_website']}")
        print(f"With Email:         {stats['with_email']}")
        print(f"With Phone:         {stats['with_phone']}")
        
        return 0


def setup_organizer_cli(subparsers):
    """
    Setup argparse subcommands for organizers.
    
    Commands:
        organizers list [--verified-only] [--format json]
        organizers add --name NAME [--website URL] [--email EMAIL] [--phone PHONE]
        organizers verify ORGANIZER_ID
        organizers search QUERY
        organizers merge SOURCE_ID TARGET_ID
        organizers stats
    """
    organizers_parser = subparsers.add_parser('organizers', help='Organizer management')
    organizers_subparsers = organizers_parser.add_subparsers(dest='organizer_command', help='Organizer subcommands')
    
    # list
    list_parser = organizers_subparsers.add_parser('list', help='List all organizers')
    list_parser.add_argument('--verified-only', action='store_true', help='Show only verified organizers')
    list_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # add
    add_parser = organizers_subparsers.add_parser('add', help='Add new organizer')
    add_parser.add_argument('--name', required=True, help='Organizer name')
    add_parser.add_argument('--website', help='Website URL (optional)')
    add_parser.add_argument('--email', help='Email address (optional)')
    add_parser.add_argument('--phone', help='Phone number (optional)')
    
    # edit
    edit_parser = organizers_subparsers.add_parser('edit', help='Edit organizer')
    edit_parser.add_argument('organizer_id', help='Organizer ID')
    edit_parser.add_argument('--name', help='New name')
    edit_parser.add_argument('--website', help='New website')
    edit_parser.add_argument('--email', help='New email')
    edit_parser.add_argument('--phone', help='New phone')
    
    # verify
    verify_parser = organizers_subparsers.add_parser('verify', help='Verify organizer')
    verify_parser.add_argument('organizer_id', help='Organizer ID')
    verify_parser.add_argument('--verified-by', help='User who verified')
    
    # search
    search_parser = organizers_subparsers.add_parser('search', help='Search organizers')
    search_parser.add_argument('query', help='Search query')
    
    # merge
    merge_parser = organizers_subparsers.add_parser('merge', help='Merge organizers')
    merge_parser.add_argument('source_id', help='Source organizer ID (will be deleted)')
    merge_parser.add_argument('target_id', help='Target organizer ID (will be kept)')
    
    # stats
    organizers_subparsers.add_parser('stats', help='Show statistics')
