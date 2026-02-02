#!/usr/bin/env python3
"""
Comprehensive Event Data Flow Diagnostic
Traces events from JSON → HTML → JavaScript → Leaflet
"""
import json
import re
import os

def check_events_json():
    """Check source events.json file"""
    print("=" * 80)
    print("STEP 1: SOURCE DATA (assets/json/events.json)")
    print("=" * 80)
    
    with open('assets/json/events.json', 'r') as f:
        data = json.load(f)
        events = data.get('events', [])
        
    print(f"✅ Total events in source: {len(events)}")
    
    # Validate structure
    valid = 0
    invalid = []
    for event in events:
        if all(k in event for k in ['id', 'title', 'location', 'start_time']):
            if 'lat' in event['location'] and 'lon' in event['location']:
                valid += 1
            else:
                invalid.append(f"{event['id']}: missing lat/lon")
        else:
            invalid.append(f"{event['id']}: missing required fields")
    
    print(f"✅ Valid events (have id, title, location.lat, location.lon, start_time): {valid}")
    if invalid:
        print(f"❌ Invalid events: {len(invalid)}")
        for inv in invalid[:5]:
            print(f"   - {inv}")
    
    return events

def check_html_embedding():
    """Check if events are properly embedded in HTML"""
    print("\n" + "=" * 80)
    print("STEP 2: HTML EMBEDDING (public/index.html)")
    print("=" * 80)
    
    if not os.path.exists('public/index.html'):
        print("❌ CRITICAL: public/index.html does NOT exist!")
        print("   Run: python3 src/event_manager.py generate")
        return None
    
    with open('public/index.html', 'r') as f:
        html = f.read()
    
    # Find __INLINE_EVENTS_DATA__
    if 'window.__INLINE_EVENTS_DATA__' not in html:
        print("❌ CRITICAL: window.__INLINE_EVENTS_DATA__ NOT found in HTML!")
        return None
    
    print("✅ window.__INLINE_EVENTS_DATA__ found in HTML")
    
    # Extract and parse
    match = re.search(r'window\.__INLINE_EVENTS_DATA__\s*=\s*(\{.+?\});', html, re.DOTALL)
    if not match:
        print("❌ Could not extract __INLINE_EVENTS_DATA__ value")
        return None
    
    try:
        data_str = match.group(1)
        data = json.loads(data_str)
        events = data.get('events', [])
        print(f"✅ Events embedded in HTML: {len(events)}")
        
        # Check first event structure
        if events:
            event = events[0]
            print(f"\n   Sample event structure:")
            print(f"   - ID: {event.get('id')}")
            print(f"   - Title: {event.get('title', '')[:50]}")
            print(f"   - Location: lat={event.get('location', {}).get('lat')}, lon={event.get('location', {}).get('lon')}")
            print(f"   - Start time: {event.get('start_time')}")
        
        return events
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None

def check_javascript_loading():
    """Check JavaScript event loading code"""
    print("\n" + "=" * 80)
    print("STEP 3: JAVASCRIPT LOADING CODE")
    print("=" * 80)
    
    with open('public/index.html', 'r') as f:
        html = f.read()
    
    # Check for key functions
    checks = {
        'loadEvents() exists': 'loadEvents()' in html or 'async loadEvents' in html,
        'displayEvents() exists': 'displayEvents()' in html,
        'EventFilter exists': 'class EventFilter' in html or 'EventFilter' in html,
        'MapManager exists': 'class MapManager' in html or 'MapManager' in html,
        'addEventMarker exists': 'addEventMarker' in html,
        'Leaflet map init': 'L.map(' in html or 'initMap' in html,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    if not all_passed:
        print("\n❌ Some JavaScript components missing!")
    
    return all_passed

def check_filter_logic():
    """Check if filter is too restrictive"""
    print("\n" + "=" * 80)
    print("STEP 4: FILTER LOGIC ANALYSIS")
    print("=" * 80)
    
    with open('assets/js/filters.js', 'r') as f:
        filter_js = f.read()
    
    # Look for filter logic
    if 'filterEvents' in filter_js:
        print("✅ filterEvents method found")
        
        # Check for potential issues
        issues = []
        if 'this.events.length === 0' in filter_js:
            issues.append("Empty events check - might bail early")
        if 'return []' in filter_js:
            issues.append("Code path that returns empty array")
        
        # Check time filtering
        if 'sunrise' in filter_js or 'sunset' in filter_js:
            print("⚠️  Time-based filtering (sunrise/sunset) is active")
            print("   This might filter out all events if times are wrong")
        
        # Check distance filtering  
        if 'distance' in filter_js and 'maxDistance' in filter_js:
            print("⚠️  Distance filtering is active")
            print("   Events outside radius will be hidden")
    else:
        print("❌ filterEvents method NOT found")

def check_leaflet_integration():
    """Check Leaflet integration"""
    print("\n" + "=" * 80)
    print("STEP 5: LEAFLET INTEGRATION")
    print("=" * 80)
    
    with open('assets/js/map.js', 'r') as f:
        map_js = f.read()
    
    # Check critical functions
    checks = {
        'addEventMarker defined': 'addEventMarker(' in map_js,
        'Creates Leaflet marker': 'L.marker(' in map_js,
        'Adds marker to map': '.addTo(this.map)' in map_js,
        'Stores markers': 'this.flyers.push' in map_js or 'this.markers.push' in map_js,
        'clearMarkers defined': 'clearMarkers()' in map_js,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
    
    # Check for error handling
    if 'if (!this.map' in map_js:
        print("⚠️  Code checks if map exists (might bail if Leaflet not loaded)")
    
    if 'if (!event.location)' in map_js:
        print("⚠️  Code checks event.location (events without location are skipped)")

def analyze_flow():
    """Run complete analysis"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "EVENT DATA FLOW DIAGNOSTIC" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    source_events = check_events_json()
    html_events = check_html_embedding()
    js_ok = check_javascript_loading()
    check_filter_logic()
    check_leaflet_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if source_events and html_events:
        if len(source_events) == len(html_events):
            print(f"✅ Data integrity: {len(source_events)} events in JSON → {len(html_events)} events in HTML")
        else:
            print(f"⚠️  Data mismatch: {len(source_events)} events in JSON but {len(html_events)} events in HTML")
    
    if not html_events:
        print("\n❌ CRITICAL ISSUE: Events not embedded in HTML")
        print("   FIX: Run 'python3 src/event_manager.py generate'")
    elif not js_ok:
        print("\n❌ CRITICAL ISSUE: JavaScript components missing")
        print("   FIX: Check build process")
    else:
        print("\n🔍 LIKELY ISSUES TO INVESTIGATE:")
        print("   1. Filter settings too restrictive (sunrise/distance)")
        print("   2. Leaflet not loading (CDN blocked)")
        print("   3. User location not set (geolocation permission)")
        print("   4. Events filtered by time (all in past/future)")
        print("\n   DEBUG IN BROWSER:")
        print("   - Open public/index.html in browser")
        print("   - Open DevTools Console (F12)")
        print("   - Type: window.__INLINE_EVENTS_DATA__.events.length")
        print("   - Type: window.app.events.length")
        print("   - Type: window.app.mapManager.flyers.length")

if __name__ == '__main__':
    analyze_flow()
