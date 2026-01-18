#!/usr/bin/env python3
"""
One-Time Entity System Migration Script

Runs complete migration in 4 steps:
1. Add entity references to all events
2. Validate references
3. Extract entities to libraries
4. Generate override report

This script can be deleted after first successful use.

Usage:
    python3 scripts/migrate_once.py --dry-run  # Preview
    python3 scripts/migrate_once.py            # Execute
    rm scripts/migrate_once.py                 # Delete after success
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.entity_operations import EntityOperations


def print_header(title):
    """Print section header"""
    print()
    print("─" * 70)
    print(f"  {title}")
    print("─" * 70)


def print_step_header(step_num, title):
    """Print step header"""
    print()
    print("=" * 70)
    print(f"  STEP {step_num}: {title}")
    print("=" * 70)
    print()


def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(
        description='One-time entity system migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview migration
    python3 scripts/migrate_once.py --dry-run
    
    # Execute migration
    python3 scripts/migrate_once.py
    
    # Force overwrite existing libraries
    python3 scripts/migrate_once.py --force
    
    # Delete script after success
    rm scripts/migrate_once.py
        """
    )
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without applying')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing entity libraries')
    args = parser.parse_args()
    
    # Print banner
    print()
    print("=" * 70)
    print("  KRWL HOF - One-Time Entity System Migration")
    print("=" * 70)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()
    
    # Initialize operations
    base_path = Path(__file__).parent.parent
    operations = EntityOperations(base_path)
    
    # Track success/failure
    all_steps_passed = True
    
    # STEP 1: Add entity references
    print_step_header(1, "Add Entity References to Events")
    
    try:
        stats = operations.add_references(dry_run=args.dry_run, force=args.force)
        
        print(f"✅ Events analyzed:        {stats['events_analyzed']}")
        print(f"✅ Events with locations:  {stats['events_with_locations']}")
        print(f"✅ Events with organizers: {stats['events_with_organizers']}")
        print(f"✅ Events modified:        {stats['events_modified']}")
        print(f"✅ Location IDs added:     {stats['location_ids_added']}")
        print(f"✅ Organizer IDs added:    {stats['organizer_ids_added']}")
        
        if stats['events_modified'] == 0:
            print()
            print("💡 No events modified - references may already exist")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_steps_passed = False
    
    # STEP 2: Validate references
    print_step_header(2, "Validate Entity References")
    
    try:
        results = operations.validate_references()
        
        print(f"✅ Valid events:     {results['valid_events']}")
        print(f"⚠️  Warnings:        {len(results['warnings'])}")
        print(f"❌ Errors:          {len(results['errors'])}")
        
        if results['errors']:
            print()
            print("❌ Errors Found:")
            for error in results['errors'][:5]:
                print(f"   Event: {error['event_id']}")
                print(f"   Error: {error['error']}")
            if len(results['errors']) > 5:
                print(f"   ... and {len(results['errors']) - 5} more")
            all_steps_passed = False
        
        if results['warnings']:
            print()
            print("⚠️  Warnings:")
            for warning in results['warnings'][:5]:
                print(f"   Event: {warning['event_id']}")
                print(f"   Warning: {warning['warning']}")
            if len(results['warnings']) > 5:
                print(f"   ... and {len(results['warnings']) - 5} more")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_steps_passed = False
    
    # STEP 3: Extract entities to libraries (skip in dry-run)
    if not args.dry_run:
        print_step_header(3, "Extract Entities to Libraries")
        
        try:
            stats = operations.migrate_to_system(force=args.force)
            
            print(f"✅ Events processed:        {stats['events_processed']}")
            print(f"✅ Locations extracted:     {stats['locations_extracted']}")
            print(f"✅ Organizers extracted:    {stats['organizers_extracted']}")
            print(f"✅ Duplicates merged:       {stats['duplicates_merged']}")
            print()
            print("📄 Created:")
            print("   - assets/json/locations.json")
            print("   - assets/json/organizers.json")
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("💡 Tip: Use --force to overwrite existing libraries")
            all_steps_passed = False
    else:
        print_step_header(3, "Extract Entities to Libraries")
        print("⏭️  Skipped in dry-run mode")
    
    # STEP 4: Generate override report
    print_step_header(4, "Generate Override Report")
    
    try:
        results = operations.track_overrides(output_format='text')
        
        total = results['total_events']
        loc = results['location_patterns']
        
        print("📊 Entity Override Report")
        print("=" * 70)
        print()
        print("📍 Location Override Analysis:")
        print("━" * 70)
        print(f"Total Events:          {total}")
        print(f"Reference Only:        {loc['reference_only']}  ({loc['reference_only']*100//total if total else 0}%)  ✅ Clean references")
        print(f"Partial Override:      {loc['partial_override']}  ({loc['partial_override']*100//total if total else 0}%)  ⚠️  Event-specific changes")
        print(f"Full Override:         {loc['full_override']}  ({loc['full_override']*100//total if total else 0}%)  📦 Fully embedded")
        print(f"Needs Migration:       {loc['needs_migration']}  ({loc['needs_migration']*100//total if total else 0}%)  ❌ Legacy events")
        print("━" * 70)
        print()
        
        if results['partial_overrides']:
            print("🔍 Partial Overrides Detected:")
            print("━" * 70)
            for i, override in enumerate(results['partial_overrides'][:5], 1):
                if override['entity_type'] == 'location':
                    print(f"{i}. {override['event_id']}")
                    print(f"   Title: {override['title']}")
                    print(f"   Base Location: {override['base_id']}")
                    print(f"   Overridden Fields: {', '.join(override['overridden_fields'])}")
            if len(results['partial_overrides']) > 5:
                print(f"   ... and {len(results['partial_overrides']) - 5} more")
            print("━" * 70)
        
        print()
        print("📄 Full report saved to: assets/json/entity_override_report.json")
    except Exception as e:
        print(f"❌ Error: {e}")
        all_steps_passed = False
    
    # Summary
    print()
    print("=" * 70)
    print("  Migration Summary")
    print("=" * 70)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN COMPLETED")
        print()
        print("💡 Next Steps:")
        print("   1. Review the changes above")
        print("   2. Run without --dry-run to apply changes:")
        print("      python3 scripts/migrate_once.py")
        print()
        return 0
    
    if all_steps_passed:
        print("✅ MIGRATION SUCCESSFUL!")
        print()
        print("📄 Files Created/Updated:")
        print("   - assets/json/locations.json (location library)")
        print("   - assets/json/organizers.json (organizer library)")
        print("   - assets/json/entity_override_report.json (analysis)")
        print("   - assets/json/events.json (with references)")
        print("   - assets/json/pending_events.json (with references)")
        print()
        print("💡 Next Steps:")
        print("   1. Review the generated libraries")
        print("   2. Test the entity resolution:")
        print("      python3 src/event_manager.py entities validate")
        print("   3. Start using entity commands:")
        print("      python3 src/event_manager.py locations list")
        print("      python3 src/event_manager.py organizers list")
        print("   4. (Optional) Delete this migration script:")
        print("      rm scripts/migrate_once.py")
        print()
        return 0
    else:
        print("❌ MIGRATION FAILED")
        print()
        print("💡 Troubleshooting:")
        print("   1. Review errors above")
        print("   2. Check event data format")
        print("   3. Try with --force to overwrite existing libraries")
        print("   4. Restore from backups if needed:")
        print("      cp assets/json/*.json.backup assets/json/")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
