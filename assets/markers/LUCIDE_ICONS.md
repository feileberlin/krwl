# Lucide Icons Integration

## Overview

All marker icons in this directory are based on **Lucide Icons** - a beautiful, consistent open-source icon library.

- **Library**: Lucide (https://lucide.dev/)
- **License**: ISC License (Free for commercial use)
- **Version**: Latest from GitHub main branch
- **Repository**: https://github.com/lucide-icons/lucide
- **Icons Used**: 29 markers

## Design

Each marker follows the **unified gyro design system**:
- Standard teardrop/location pin shape (green stroke: `#00ff00`)
- Lucide icon embedded inside at center point (16, 15)
- Drop shadow for depth
- Consistent size: 32x48 pixels

## Icon Mapping

| Marker File | Lucide Icon | Category |
|-------------|-------------|----------|
| `marker-on-stage.svg` | drama | Theater/Performance |
| `marker-music.svg` | music | Concerts/Music |
| `marker-opera-house.svg` | landmark | Opera/Theater |
| `marker-pub-games.svg` | beer | Pubs/Social Games |
| `marker-festivals.svg` | star | Festivals |
| `marker-workshops.svg` | presentation | Workshops/Training |
| `marker-school.svg` | graduation-cap | Education |
| `marker-shopping.svg` | shopping-bag | Markets/Shopping |
| `marker-sports.svg` | trophy | Sports |
| `marker-sports-field.svg` | ticket | Sports Fields |
| `marker-swimming.svg` | waves | Swimming |
| `marker-community.svg` | users | Community |
| `marker-arts.svg` | palette | Arts |
| `marker-museum.svg` | landmark | Museums |
| `marker-food.svg` | utensils | Food/Dining |
| `marker-church.svg` | church | Religious |
| `marker-traditional-oceanic.svg` | flame | Cultural/Traditional |
| `marker-castle.svg` | castle | Castles |
| `marker-monument.svg` | pilcrow | Monuments |
| `marker-tower.svg` | triangle | Towers |
| `marker-ruins.svg` | blocks | Ruins |
| `marker-palace.svg` | crown | Palaces |
| `marker-park.svg` | tree-pine | Parks/Nature |
| `marker-parliament.svg` | landmark | Government |
| `marker-mayors-office.svg` | building | City Hall |
| `marker-library.svg` | book-open | Libraries |
| `marker-national-archive.svg` | archive | Archives |
| `marker-default.svg` | map-pin | Default/Fallback |
| `marker-geolocation.svg` | locate | User Location |

## License

### Lucide Icons License (ISC)
```
Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.
```

**What this means:**
- ✅ Free to use commercially
- ✅ Can modify icons
- ✅ Can distribute
- ✅ No attribution required (but appreciated)

## Regenerating Icons

If you need to regenerate the markers (e.g., to update to newer Lucide versions):

1. Use the script at `/tmp/download_lucide_icons.py`
2. Modify the `ICON_MAPPING` dictionary to change icon assignments
3. Run: `python3 /tmp/download_lucide_icons.py`
4. Copy generated markers from `/tmp/lucide-markers/` to `assets/markers/`

## Benefits

### Why Lucide?

1. **Consistent Design** - All icons share the same design language
2. **High Quality** - Professional, well-crafted icons
3. **Open Source** - ISC licensed, free forever
4. **Actively Maintained** - Regular updates and new icons
5. **Well-Documented** - Clear naming and categories
6. **Lightweight** - Clean SVG code, small file sizes
7. **Customizable** - Easy to modify colors/sizes

### Design Consistency

All 29 markers now:
- ✅ Use the same gyro outline shape
- ✅ Have consistent icon sizing and positioning
- ✅ Follow the same color scheme (#00ff00)
- ✅ Include drop shadows
- ✅ Are optimized for map display

This replaces the previous mixed design where some markers used custom shapes (star, diamond, hexagon) while others used the gyro shape.

## Generated

- **Date**: 2026-01-03
- **Method**: Automated download from Lucide GitHub repository
- **Script**: `/tmp/download_lucide_icons.py`
- **Status**: Complete - all 29 required markers generated
