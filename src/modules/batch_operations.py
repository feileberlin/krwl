"""
Batch Operations Module - Simple batch processing utilities

Focused, modular batch operations following KISS principles.
Each function does one thing well.
"""

import fnmatch
import logging

logger = logging.getLogger(__name__)


def expand_wildcards(patterns, events):
    """
    Expand wildcard patterns to match event IDs
    
    Args:
        patterns: List of patterns (can include wildcards)
        events: List of events with 'id' field
        
    Returns:
        List of expanded event IDs (no duplicates)
    """
    expanded_ids = []
    seen_ids = set()
    
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        
        if _is_wildcard(pattern):
            _add_wildcard_matches(pattern, events, expanded_ids, seen_ids)
        else:
            _add_exact_id(pattern, expanded_ids, seen_ids)
    
    return expanded_ids


def _is_wildcard(pattern):
    """Check if pattern contains wildcards"""
    return '*' in pattern or '?' in pattern or '[' in pattern


def _add_wildcard_matches(pattern, events, expanded_ids, seen_ids):
    """Add events matching wildcard pattern"""
    matches_found = False
    for event in events:
        event_id = event.get('id', '')
        if fnmatch.fnmatch(event_id, pattern):
            matches_found = True
            if event_id not in seen_ids:
                expanded_ids.append(event_id)
                seen_ids.add(event_id)
    
    if not matches_found:
        logger.warning(f"Pattern '{pattern}' matched no events")
        print(f"⚠ Warning: Pattern '{pattern}' matched no events")


def _add_exact_id(pattern, expanded_ids, seen_ids):
    """Add exact event ID"""
    if pattern not in seen_ids:
        expanded_ids.append(pattern)
        seen_ids.add(pattern)


def process_in_batches(items, batch_size=10, callback=None):
    """
    Process items in batches with progress reporting
    
    Args:
        items: List of items to process
        batch_size: Number of items per batch
        callback: Function(batch_items, batch_num, total_batches) -> dict
        
    Returns:
        Dict with 'total', 'batches', 'processed', 'failed' keys
    """
    if not items:
        return _empty_results()
    
    batches = _split_into_batches(items, batch_size)
    results = _init_results(len(items), len(batches))
    
    print(f"📦 Processing {len(items)} items in {len(batches)} batch(es)")
    
    for batch_num, batch_items in enumerate(batches, 1):
        batch_result = _process_batch(batch_items, batch_num, len(batches), callback)
        _update_results(results, batch_result)
    
    _print_summary(results)
    return results


def _empty_results():
    """Return empty results structure"""
    return {'total': 0, 'batches': 0, 'processed': 0, 'failed': 0}


def _split_into_batches(items, batch_size):
    """Split items into batches"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def _init_results(total, batches):
    """Initialize results structure"""
    return {
        'total': total,
        'batches': batches,
        'processed': 0,
        'failed': 0,
        'batch_results': []
    }


def _process_batch(batch_items, batch_num, total_batches, callback):
    """Process a single batch"""
    print(f"\n🔄 Batch {batch_num}/{total_batches} ({len(batch_items)} items)...")
    
    batch_result = {
        'batch_num': batch_num,
        'items': batch_items,
        'success': [],
        'failed': []
    }
    
    if callback:
        try:
            callback_result = callback(batch_items, batch_num, total_batches)
            batch_result.update(callback_result)
        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {e}")
            print(f"❌ Batch {batch_num} failed: {e}")
            batch_result['failed'] = batch_items
    
    return batch_result


def _update_results(results, batch_result):
    """Update overall results with batch result"""
    results['processed'] += len(batch_result.get('success', []))
    results['failed'] += len(batch_result.get('failed', []))
    results['batch_results'].append(batch_result)


def _print_summary(results):
    """Print processing summary"""
    print(f"\n✅ Batch processing complete:")
    print(f"   Total: {results['total']}")
    print(f"   Processed: {results['processed']}")
    print(f"   Failed: {results['failed']}")


def find_events_by_ids(event_ids, events):
    """
    Find events by their IDs
    
    Args:
        event_ids: List of event IDs
        events: List of events
        
    Returns:
        Tuple of (found_events, failed_ids)
    """
    found_events = []
    failed_ids = []
    
    for event_id in event_ids:
        event_data = _find_event(event_id, events)
        if event_data:
            found_events.append(event_data)
        else:
            failed_ids.append(event_id)
    
    # Sort by index in reverse for safe removal
    found_events.sort(key=lambda x: x[0], reverse=True)
    
    return found_events, failed_ids


def _find_event(event_id, events):
    """Find single event by ID"""
    for i, event in enumerate(events):
        if event.get('id') == event_id:
            return (i, event_id, event)
    
    logger.warning(f"Event '{event_id}' not found")
    return None


def determine_batch_size(total_count):
    """
    Determine optimal batch size
    
    Args:
        total_count: Total number of items
        
    Returns:
        Optimal batch size
    """
    if total_count <= 10:
        return total_count
    elif total_count <= 50:
        return 10
    else:
        return 20
