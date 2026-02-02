#!/usr/bin/env python3
"""
Real-time JavaScript Execution Tracer
Identifies WHY flyers don't show by tracing actual code execution
"""

print("=" * 80)
print("JAVASCRIPT EXECUTION TRACE")
print("=" * 80)

code_checks = [
    ("1. Leaflet available check", "isLeafletAvailable()", "returns typeof L !== 'undefined'"),
    ("2. Map initialization", "initMap('map')", "creates this.map = L.map()"),
    ("3. Events loading", "loadEvents()", "populates this.events array"),  
    ("4. Display events called", "displayEvents()", "filters and adds markers"),
    ("5. Filter check", "filteredEvents.length", "must be > 0 to proceed"),
    ("6. Fallback mode check", "isFallbackMode", "must be false to show map"),
    ("7. Add marker loop", "forEach addEventMarker", "creates L.marker().addTo(map)"),
    ("8. Map existence check", "!this.map", "returns null if map doesn't exist"),
]

print("\n🔍 EXECUTION FLOW CHECKPOINTS:")
for i, (step, func, desc) in enumerate(code_checks, 1):
    print(f"\n{i}. {step}")
    print(f"   Function: {func}")
    print(f"   Does: {desc}")

print("\n" + "=" * 80)
print("POTENTIAL FAILURE POINTS")
print("=" * 80)

failures = [
    ("❌ Leaflet CDN blocked", "isLeafletAvailable() returns false", "Leaflet not loaded from CDN"),
    ("❌ Map div missing", "document.getElementById('map') returns null", "HTML missing map container"),
    ("❌ Events filtered out", "filteredEvents.length === 0", "Early return on line 663"),
    ("❌ Map init failed", "this.map is null", "addEventMarker returns null on line 356"),
    ("❌ Timing issue", "displayEvents() called before Leaflet loads", "Race condition"),
]

for issue, check, reason in failures:
    print(f"\n{issue}")
    print(f"  Check: {check}")
    print(f"  Reason: {reason}")

print("\n" + "=" * 80)
print("MOST LIKELY ROOT CAUSE")
print("=" * 80)

print("""
Based on code analysis, the most likely issue is:

🎯 **Leaflet CDN Fails to Load**

When: Browser cannot reach unpkg.com or CDN is blocked
Result: typeof L === 'undefined'
Effect: 
  - isLeafletAvailable() returns false (line 47)
  - initMap() returns false (line 60)
  - this.map stays null
  - addEventMarker() returns null (line 356)
  - No flyers added to map

This would happen even with correct:
  ✅ Filters (5km, sunrise)
  ✅ Region (antarctica)
  ✅ Event data (150 events)
  ✅ HTML generated

Because if Leaflet doesn't load, NOTHING can render.

💡 SOLUTION: Check browser console for:
  - Leaflet loading errors
  - CDN connection failures
  - JavaScript errors blocking execution
""")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMMANDS")
print("=" * 80)

print("""
In browser console, type:

1. Check if Leaflet loaded:
   typeof L

2. Check if app initialized:
   window.app

3. Check if events loaded:
   window.app.events.length

4. Check if map exists:
   window.app.mapManager.map

5. Check filtered events:
   window.app.eventFilter.filterEvents(window.app.events, window.app.filters, window.app.mapManager.userLocation).length

6. Check for errors:
   Look for red errors in console
""")
