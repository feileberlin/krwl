# Marker Design Audit

## Summary

Out of 29 required markers, **9 are compliant** with the unified gyro design and **20 need updating**.

## Design Philosophy

All markers should follow the unified gyro/teardrop shape as documented in `assets/markers/UNIFIED_DESIGN.md`:

```svg
<!-- STANDARD GYRO SHAPE (same for all) -->
<path d="M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z" 
      fill="none" stroke="#00ff00" stroke-width="2"/>
```

**Key principle:** The gyro outline stays the same; only the internal icon changes.

## Compliance Status

### ✅ Compliant Markers (9)
These markers already use the standard gyro shape:

1. `marker-music` ✓
2. `marker-workshops` ✓
3. `marker-community` ✓
4. `marker-arts` ✓
5. `marker-food` ✓
6. `marker-church` ✓
7. `marker-library` ✓
8. `marker-default` ✓
9. `marker-geolocation` ✓

### ❌ Non-Compliant Markers (20)
These markers use custom shapes and need updating:

1. `marker-on-stage` - Uses diamond shape
2. `marker-opera-house` - Uses building/house shape
3. `marker-pub-games` - Uses hexagon shape
4. `marker-festivals` - Uses star shape
5. `marker-school` - Uses building shape
6. `marker-shopping` - Uses bag shape
7. `marker-sports` - Uses octagon shape
8. `marker-sports-field` - Uses rectangle shape
9. `marker-swimming` - Uses wave shape
10. `marker-museum` - Uses building shape
11. `marker-traditional-oceanic` - Uses building shape
12. `marker-castle` - Uses building shape
13. `marker-monument` - Uses obelisk shape
14. `marker-tower` - Uses tower shape
15. `marker-ruins` - Uses ruins shape
16. `marker-palace` - Uses palace shape
17. `marker-park` - Uses tree/park shape
18. `marker-parliament` - Uses building shape
19. `marker-mayors-office` - Uses building shape
20. `marker-national-archive` - Uses building shape

## Recommendation

### Option 1: Update All Markers (Recommended)
Update all 20 non-compliant markers to use the standard gyro shape with appropriate internal icons. This ensures:
- ✓ Consistent visual language across the map
- ✓ Professional, cohesive appearance
- ✓ Easier to recognize all markers as map pins
- ✓ Better scalability and maintainability

**Effort**: Moderate - requires SVG editing for 20 markers

### Option 2: Accept Mixed Design
Keep current markers as-is but document the decision. This means:
- Some markers use gyro shape (9)
- Some markers use custom shapes (20)
- ⚠️ Visual inconsistency on the map
- ⚠️ Harder to maintain design consistency

**Effort**: Low - but sacrifices design consistency

## Next Steps

1. **Decision**: Choose between Option 1 (unify) or Option 2 (accept mixed)

2. **If Option 1 (Recommended)**:
   - Extract the internal icons from non-compliant markers
   - Apply the standard gyro outline to each
   - Keep the unique icon inside (microphone, star, etc.)
   - Test visual appearance on map
   - Rebuild and verify

3. **If Option 2**:
   - Document the decision in `assets/markers/DESIGN_PHILOSOPHY.md`
   - Accept that markers will have varied shapes
   - Close this design requirement

## Example Conversion

### Before (marker-festivals.svg)
```svg
<!-- Star-shaped marker -->
<path d="M16 2 L18 10 L26 10 L20 15 L22 22 L16 17 L16 46..." 
      fill="none" stroke="#00ff00" stroke-width="2"/>
```

### After (Unified Design)
```svg
<!-- Standard gyro with star icon inside -->
<path d="M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z" 
      fill="none" stroke="#00ff00" stroke-width="2"/>
<!-- Star icon -->
<path d="M16 10 L17 13 L20 13 L18 15 L19 18 L16 16 L13 18 L14 15 L12 13 L15 13 Z"
      fill="none" stroke="#00ff00" stroke-width="1.5"/>
```

## File Size Impact

Converting all markers to unified design should not significantly impact file size since:
- The gyro path is similar length to custom shapes
- We're still using 29 markers total
- Base64 encoding efficiency remains the same

Expected impact: ±5 KB (negligible)

## Generated

- Date: 2026-01-03
- Tool: `/tmp/check_marker_design.py`
- Status: Audit complete, awaiting decision
