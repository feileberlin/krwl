"""
Batch Selection Module - Interactive checkbox-based event selection

This module provides a focused, modular implementation of batch selection
functionality for the editorial workflow, following KISS principles.
"""

import logging

logger = logging.getLogger(__name__)


class BatchSelector:
    """Handle interactive batch selection with checkboxes"""
    
    def __init__(self, pending_events):
        """
        Initialize batch selector
        
        Args:
            pending_events: List of pending event dictionaries
        """
        self.pending_events = pending_events
        self.selected = set()
    
    def run(self):
        """
        Run interactive batch selection mode
        
        Returns:
            Dict with keys: 'action' ('approve'/'reject'/None), 'indices' (set)
        """
        self._print_header()
        
        while True:
            self._display_list()
            self._display_commands()
            
            choice = input("\nCommand: ").strip().lower()
            result = self._handle_command(choice)
            
            if result:
                return result
        
        return {'action': None, 'indices': set()}
    
    def _print_header(self):
        """Print batch selection header"""
        print("\n" + "=" * 80)
        print("📦 BATCH SELECTION MODE")
        print("=" * 80)
        print("Select events for batch operations using checkboxes")
        print("-" * 80)
    
    def _display_list(self):
        """Display event list with checkboxes"""
        print("\n" + "─" * 80)
        print("📋 All Pending Events:")
        print("─" * 80)
        
        for idx, event in enumerate(self.pending_events):
            checkbox = "☑" if idx in self.selected else "☐"
            title = event.get('title', 'N/A')[:50]
            event_id = event.get('id', 'N/A')
            source = event.get('source', 'N/A')
            print(f"{idx + 1:3}. {checkbox} {title}")
            print(f"      ID: {event_id} | Source: {source}")
        
        print("\n" + "─" * 80)
        print(f"Selected: {len(self.selected)} event(s)")
        print("─" * 80)
    
    def _display_commands(self):
        """Display available commands"""
        print("Commands:")
        print("  [number]      Toggle selection (e.g., '1' or '1,3,5')")
        print("  all           Select all")
        print("  none          Clear selection")
        print("  range N-M     Select range (e.g., 'range 1-5')")
        print("  pattern WORD  Select by pattern (e.g., 'pattern concert')")
        print("  approve       Batch approve")
        print("  reject        Batch reject")
        print("  show          Show details")
        print("  back          Exit")
        print("─" * 80)
    
    def _handle_command(self, choice):
        """
        Handle user command
        
        Returns:
            Dict with action and indices, or None to continue
        """
        if choice == 'back':
            return {'action': None, 'indices': set()}
        
        if choice == 'all':
            self.selected = set(range(len(self.pending_events)))
            print(f"✓ Selected all {len(self.selected)} events")
            return None
        
        if choice == 'none':
            self.selected.clear()
            print("✓ Cleared selection")
            return None
        
        if choice.startswith('range '):
            self._select_range(choice)
            return None
        
        if choice.startswith('pattern '):
            self._select_pattern(choice)
            return None
        
        if choice == 'show':
            self._show_selected()
            return None
        
        if choice == 'approve':
            if self._confirm_action('approve'):
                return {'action': 'approve', 'indices': self.selected}
            return None
        
        if choice == 'reject':
            if self._confirm_action('reject'):
                return {'action': 'reject', 'indices': self.selected}
            return None
        
        # Try to parse as numbers
        self._toggle_numbers(choice)
        return None
    
    def _select_range(self, choice):
        """Select range of events"""
        try:
            range_str = choice.split(' ', 1)[1]
            start, end = map(int, range_str.split('-'))
            self.selected.update(range(start - 1, end))
            print(f"✓ Selected events {start} to {end}")
        except Exception as e:
            print(f"❌ Invalid range: {e}")
    
    def _select_pattern(self, choice):
        """Select events matching pattern"""
        pattern = choice.split(' ', 1)[1].lower()
        matched = 0
        for idx, event in enumerate(self.pending_events):
            title = event.get('title', '').lower()
            if pattern in title:
                self.selected.add(idx)
                matched += 1
        print(f"✓ Selected {matched} events matching '{pattern}'")
    
    def _toggle_numbers(self, choice):
        """Toggle selection of specific numbers"""
        try:
            numbers = [int(n.strip()) - 1 for n in choice.split(',')]
            
            for num in numbers:
                if 0 <= num < len(self.pending_events):
                    if num in self.selected:
                        self.selected.remove(num)
                        print(f"☐ Deselected event {num + 1}")
                    else:
                        self.selected.add(num)
                        print(f"☑ Selected event {num + 1}")
                else:
                    print(f"❌ Invalid event number: {num + 1}")
        except ValueError:
            print("❌ Invalid command")
    
    def _show_selected(self):
        """Show details of selected events"""
        if not self.selected:
            print("❌ No events selected")
            return
        
        print("\n" + "=" * 80)
        print("📋 Selected Events:")
        print("=" * 80)
        for idx in sorted(self.selected):
            event = self.pending_events[idx]
            print(f"\n{idx + 1}. {event.get('title', 'N/A')}")
            print(f"   ID: {event.get('id', 'N/A')}")
            print(f"   Source: {event.get('source', 'N/A')}")
            print(f"   Time: {event.get('start_time', 'N/A')}")
        input("\nPress Enter to continue...")
    
    def _confirm_action(self, action):
        """Confirm batch action"""
        if not self.selected:
            print("❌ No events selected")
            return False
        
        confirm = input(f"\n⚠️  {action.capitalize()} {len(self.selected)} event(s)? (yes/no): ")
        return confirm.lower() == 'yes'
