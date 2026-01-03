# CSS Modules

> Modular CSS architecture for maintainability and reusability

## 🎯 Overview

The CSS has been split into focused modules following the component-based architecture. Each module handles a specific aspect of the UI, making it easier to maintain, update, and understand.

## 📦 Modules

### base.css
Global reset and base styles for the entire application.
- CSS reset (margin, padding, box-sizing)
- Body styles (font, background, colors)
- App container
- Noscript warning

### map.css
Map container and Leaflet integration styles.
- Map container positioning
- Leaflet tile filtering (monochromatic Barbie theme)
- Map overlay positioning

### filters.css
Interactive filter bar and controls.
- Filter bar layout and positioning
- Filter logo button
- Filter dropdowns and controls
- Distance slider
- Time range selector

### dashboard.css
Dashboard menu modal and overlay.
- Dashboard modal container
- Content sections
- Open/close animations
- Environment indicators (DEV/PRODUCTION)

### mobile.css
Mobile-responsive styles and optimizations.
- Mobile breakpoints (@media queries)
- Touch-friendly interactions
- Responsive layouts
- Small screen adaptations

### leaflet-custom.css
Leaflet library customization.
- Custom popup styles
- Edge-positioned event details
- SVG arrows for popups
- Marker glow effects

### scrollbar.css
Custom scrollbar styling.
- Barbie Pink themed scrollbars
- Webkit scrollbar customization
- Firefox scrollbar properties

## 🚀 Usage

Modules are automatically loaded by the site generator in the correct order:

```python
# In src-modules/site_generator.py
css_modules = [
    'base.css',
    'map.css', 
    'filters.css',
    'dashboard.css',
    'mobile.css',
    'leaflet-custom.css',
    'scrollbar.css'
]
```

## 🔧 Editing

To modify styles:

1. Edit the specific module file in `assets/css-modules/`
2. Regenerate the site: `python3 src/event_manager.py generate`
3. The modules are combined and inlined during generation

## 💡 Design Tokens

All modules use CSS custom properties from `design-tokens.css`:
- `var(--color-primary)` - Barbie Pink
- `var(--color-bg-primary)` - Dark background
- `var(--color-text-primary)` - Light text
- And more...

See `layouts/components/variables-reference.md` for complete token reference.

## 📝 Adding New Modules

1. Create new `.css` file in `assets/css-modules/`
2. Add module header comment: `/* Module Name */`
3. Write focused, scoped styles
4. Update `src-modules/site_generator.py` to include new module
5. Test with `python3 src/event_manager.py generate`

## ✅ Benefits

- **Maintainability**: Easy to find and update specific styles
- **Modularity**: Independent modules, minimal coupling
- **Readability**: Small, focused files
- **Reusability**: Modules can be included/excluded as needed
- **KISS Principle**: Simple, flat structure

---

**Total**: 7 CSS modules, ~767 lines split into focused components
