# Marker Icons Recommendation: Free Icon Libraries

## Current Situation

The project currently has 77 custom-designed SVG markers in `assets/markers/` that follow a unified gyro/teardrop design system. However, there's a requirement to use pre-designed free SVG icons from established libraries instead.

## Recommended Free Icon Libraries

### 1. **Font Awesome (Free)** ⭐ RECOMMENDED
- **License**: SIL OFL 1.1 & MIT (Free for commercial use)
- **URL**: https://fontawesome.com/icons
- **Icons**: 2,000+ free icons
- **Formats**: SVG, Web Fonts
- **Quality**: Professional, consistent design
- **Categories**: Comprehensive coverage of event types
- **CDN**: Available
- **Download**: Can download individual SVGs

**Why Font Awesome?**
- ✅ Most comprehensive free icon set
- ✅ Professional quality
- ✅ Consistent design language
- ✅ Easy to customize colors/sizes
- ✅ Well-maintained and widely used
- ✅ Clear licensing (no attribution required for free version)

### 2. **Feather Icons**
- **License**: MIT (Free for commercial use)
- **URL**: https://feathericons.com/
- **Icons**: 287 icons
- **Quality**: Minimal, clean design
- **Note**: Limited set, may not cover all event types

### 3. **Material Icons (Google)**
- **License**: Apache 2.0 (Free for commercial use)
- **URL**: https://fonts.google.com/icons
- **Icons**: 2,000+ icons
- **Quality**: Professional, consistent
- **Note**: Material Design style (may not fit pink aesthetic)

### 4. **Ionicons**
- **License**: MIT (Free for commercial use)
- **URL**: https://ionic.io/ionicons
- **Icons**: 1,300+ icons
- **Quality**: Clean, modern design

### 5. **Heroicons**
- **License**: MIT (Free for commercial use)
- **URL**: https://heroicons.com/
- **Icons**: 292 icons (outline & solid)
- **Quality**: Minimalist, Tailwind CSS style

## Implementation Options

### Option A: Use Font Awesome Icons (Recommended)

**Approach:**
1. Download required SVG icons from Font Awesome free set
2. Wrap each icon in the standard gyro marker shape
3. Apply #00ff00 stroke color to match design
4. Keep same base64 embedding approach

**Example Mapping:**
```javascript
{
  'concert': 'fa-music',           // 🎵 Music note
  'festival': 'fa-star',           // ⭐ Star
  'workshop': 'fa-chalkboard',     // 📋 Chalkboard
  'market': 'fa-shopping-bag',     // 🛍️ Shopping bag
  'sports': 'fa-futbol',           // ⚽ Soccer ball
  'community': 'fa-users',         // 👥 Users
  'food': 'fa-utensils',           // 🍴 Utensils
  'library': 'fa-book',            // 📖 Book
  'park': 'fa-tree',               // 🌳 Tree
  'church': 'fa-church',           // ⛪ Church
  'museum': 'fa-landmark',         // 🏛️ Museum
  'theater': 'fa-masks-theater',   // 🎭 Theater masks
}
```

**Benefits:**
- ✅ Professional, recognizable icons
- ✅ Consistent design language
- ✅ No copyright concerns
- ✅ Easy to update/maintain
- ✅ Can keep gyro marker wrapper for consistency

**File Size:**
- Font Awesome SVGs are typically 1-3 KB each
- 29 markers × 2 KB = ~58 KB (similar to current)
- Plus gyro wrapper: +1 KB per marker
- **Total**: ~87 KB for markers (vs current ~60 KB)
- **HTML size impact**: +27 KB (acceptable)

### Option B: Use Marker Library (Leaflet.awesome-markers)

**Approach:**
1. Use existing Leaflet plugin for icon markers
2. Integrates Font Awesome icons automatically
3. Pre-designed marker shapes with icons inside

**Benefits:**
- ✅ Zero custom design work
- ✅ Battle-tested library
- ✅ Works with Leaflet out of the box

**Drawbacks:**
- ❌ Less customization
- ❌ May not match pink theme perfectly
- ❌ External dependency

### Option C: Mixed Approach

**Approach:**
1. Keep simple markers as custom SVGs (geolocation, default)
2. Use Font Awesome for complex icons (music, sports, etc.)
3. Wrap FA icons in standard gyro marker shape

## Recommended Action Plan

### Phase 1: Evaluation ✅
- [x] Identify requirement for pre-designed free icons
- [x] Research available free icon libraries
- [x] Recommend Font Awesome as primary source

### Phase 2: Icon Selection 📋
- [ ] Map each category to appropriate Font Awesome icon
- [ ] Download SVG versions of selected icons
- [ ] Verify all 29 required categories have suitable icons

### Phase 3: Integration 🔧
- [ ] Create script to wrap FA icons in gyro marker shape
- [ ] Apply consistent #00ff00 stroke color
- [ ] Generate base64 data URLs
- [ ] Test visual appearance on map

### Phase 4: Update & Test ✅
- [ ] Replace custom markers with FA-based markers
- [ ] Rebuild site with new markers
- [ ] Verify file size is acceptable
- [ ] Test on multiple devices/browsers

## Icon Mapping for 29 Required Markers

| Category | Font Awesome Icon | Icon Name | Unicode |
|----------|-------------------|-----------|---------|
| on-stage | 🎭 | fa-masks-theater | f630 |
| music | 🎵 | fa-music | f001 |
| opera-house | 🏛️ | fa-landmark | f66f |
| pub-games | 🍺 | fa-beer-mug-empty | f0fc |
| festivals | ⭐ | fa-star | f005 |
| workshops | 📋 | fa-chalkboard-user | f51c |
| school | 🎓 | fa-graduation-cap | f19d |
| shopping | 🛍️ | fa-bag-shopping | f290 |
| sports | ⚽ | fa-futbol | f1e3 |
| sports-field | 🏟️ | fa-baseball | f433 |
| swimming | 🏊 | fa-person-swimming | f5c4 |
| community | 👥 | fa-users | f0c0 |
| arts | 🎨 | fa-palette | f53f |
| museum | 🏛️ | fa-landmark-dome | f752 |
| food | 🍴 | fa-utensils | f2e7 |
| church | ⛪ | fa-church | f51d |
| traditional-oceanic | 🗿 | fa-monument | f5a6 |
| castle | 🏰 | fa-chess-rook | f447 |
| monument | 🗿 | fa-monument | f5a6 |
| tower | 🗼 | fa-tower-observation | e586 |
| ruins | 🏛️ | fa-monument | f5a6 |
| palace | 👑 | fa-crown | f521 |
| park | 🌳 | fa-tree | f1bb |
| parliament | 🏛️ | fa-building-columns | f19c |
| mayors-office | 🏢 | fa-building | f1ad |
| library | 📚 | fa-book | f02d |
| national-archive | 📁 | fa-folder-open | f07c |
| default | 📍 | fa-location-dot | f3c5 |
| geolocation | 📍 | fa-location-crosshairs | f601 |

## Legal Considerations

### Font Awesome Free License
- **License**: SIL Open Font License 1.1 + MIT License
- **Commercial Use**: ✅ Allowed
- **Attribution**: ❌ Not required (but appreciated)
- **Modification**: ✅ Allowed
- **Distribution**: ✅ Allowed

**What this means:**
- Can use in this project without any legal concerns
- No need to display attribution on the site
- Can modify icons (colors, sizes, combine with shapes)
- Can distribute embedded in HTML

### Recommended Attribution (Optional)
Add to footer or about page:
```html
Icons from Font Awesome Free (https://fontawesome.com)
```

## Next Steps

**Decision Point:** Should we proceed with Font Awesome integration?

**If YES:**
1. I can create a script to download required FA icons
2. Wrap them in the gyro marker shape
3. Generate new marker map with FA icons
4. Test and verify appearance

**If NO:**
1. Specify alternative icon library or approach
2. Continue with current custom markers
3. Focus on unifying existing marker designs

## Questions to Answer

1. **Design preference**: Keep gyro wrapper or use FA icons standalone?
2. **Color scheme**: Keep #00ff00 or match pink theme (#FF69B4)?
3. **Icon style**: Solid, regular, or light (FA offers different weights)?
4. **Attribution**: Display credit to Font Awesome or skip it?

## File Generated
- **Date**: 2026-01-03
- **Purpose**: Evaluate free icon libraries for marker replacement
- **Status**: Awaiting decision on Font Awesome integration
