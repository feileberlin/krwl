# Component-Based Templating System

## Overview

This directory contains the modular component-based templating system for KRWL HOF Community Events. The system enables instant rebranding through centralized design tokens while maintaining semantic HTML, accessibility, and SEO best practices.

## Architecture

### 4-Layer Z-Index System

The application uses a strict 4-layer z-index architecture:

1. **Layer 1 (z-index: 0)** - Fullscreen map background
2. **Layer 2 (z-index: 700-1000)** - Event popups and Leaflet UI elements
3. **Layer 3 (z-index: 1500-1700)** - UI overlays (dashboard, filter bar, time drawer)
4. **Layer 4 (z-index: 2000+)** - Modals and alerts

## Directory Structure

**KISS Principle Applied: Flat is better than nested!**

```
assets/html/
├── README.md                          # This file
├── variables-reference.md             # CSS variable documentation
├── design-tokens.css                  # Generated CSS (auto-created)
├── html-head.html                     # <head> with meta, title, styles
├── html-body-open.html                # <body> opening + noscript
├── html-body-close.html               # Scripts + </body></html>
├── map-main.html                      # <main> map container (Layer 1)
├── dashboard-aside.html               # <aside> dashboard menu (Layer 3)
├── filter-nav.html                    # <nav> filter bar (Layer 3)
└── noscript-content.html              # No-JS fallback content
```

**Why flat?** 
- Easier to find files
- Simpler imports
- Less mental overhead
- Follows UNIX philosophy: do one thing well

## Component Reference

### HTML Components

All components are in the root components directory for simplicity (KISS principle: flat is better than nested).

#### html-head.html
Contains the HTML `<head>` section with:
- Meta tags (charset, viewport)
- Page title
- Favicon link
- Inlined CSS (design tokens, Leaflet, app styles)

**Template Variables:**
- `{app_name}` - Application name from config
- `{favicon}` - Base64-encoded favicon data URL
- `{design_tokens_css}` - Generated design token CSS
- `{leaflet_css}` - Leaflet.js stylesheet
- `{app_css}` - Main application styles
- `{time_drawer_css}` - Time drawer component styles

#### html-body-open.html
Contains the opening `<body>` tag and noscript fallback:
- Opening body tag
- Noscript content for users without JavaScript

**Template Variables:**
- `{noscript_html}` - Generated noscript fallback HTML

#### html-body-close.html
Contains closing scripts and tags:
- Embedded data (events, configs, translations)
- JavaScript libraries (Leaflet, Lucide, i18n)
- Application logic
- Closing body and html tags

**Template Variables:**
- `{embedded_data}` - Embedded JSON data
- `{config_loader}` - Legacy placeholder (not currently used)
- `{fetch_interceptor}` - Legacy placeholder (not currently used)
- `{leaflet_js}` - Leaflet.js library
- `{lucide_js}` - Lucide icons library
- `{i18n_js}` - Internationalization module
- `{time_drawer_js}` - Time drawer component
- `{app_js}` - Main application logic

#### map-main.html
**Semantic Tag:** `<main>`  
**Layer:** 1 (z-index: 0)  
**Purpose:** Fullscreen interactive map container

Contains the main Leaflet map that displays event markers. Uses proper ARIA attributes for accessibility:
- `role="application"` - Indicates interactive map application
- `aria-label="Interactive event map"` - Describes the map's purpose

#### dashboard-aside.html
**Semantic Tag:** `<aside>`  
**Layer:** 3 (z-index: 1600)  
**Purpose:** Complementary information panel

Contains the application menu with:
- About section
- Debug information
- Maintainer contact
- Documentation links
- Credits and acknowledgments

**CSS Classes:**
- `.overlay` - Base overlay styling
- `.overlay--layer-3` - Layer 3 z-index
- `.overlay--top-left` - Top-left positioning

**Template Variables:**
- `{logo_svg}` - SVG logo content

**ARIA Attributes:**
- `role="complementary"` - Complementary content
- `aria-label="Application menu and information"` - Screen reader label
- `aria-hidden="true"` - Initially hidden

#### filter-nav.html
**Semantic Tag:** `<nav>`  
**Layer:** 3 (z-index: 1500)  
**Purpose:** Event filter navigation

Contains filter controls for:
- Event count display (live region)
- Time range filter
- Distance filter
- Location filter

**CSS Classes:**
- `.overlay` - Base overlay styling
- `.overlay--layer-3` - Layer 3 z-index
- `.overlay--top-center` - Top-center positioning

**ARIA Attributes:**
- `role="navigation"` - Navigation landmark
- `aria-label="Event filter controls"` - Screen reader label
- `role="status"` - Live status region for event count
- `aria-live="polite"` - Polite live region updates
- `aria-atomic="true"` - Read entire region on update

#### noscript-content.html
**Purpose:** Fallback content for users without JavaScript

This is a placeholder component. Actual content is generated dynamically by `SiteGenerator.build_noscript_html()` method, which creates a rich HTML-only experience with:
- Complete event listings
- Formatted dates and times
- Event descriptions
- Links to event details
- Responsive styling

## Design Token System

### Overview

Design tokens are centralized design values stored in `config.json` that enable instant rebranding. They are automatically converted to CSS custom properties by the token generator script.

### Design Token Categories

#### Colors
- `primary` - Primary brand color (ecoBarbie: #D689B8)
- `primary_hover` - Primary color hover state
- `bg_primary`, `bg_secondary`, `bg_tertiary` - Background colors
- `text_primary`, `text_secondary`, `text_tertiary` - Text colors
- `border_primary`, `border_secondary` - Border colors
- `accent` - Accent color for highlights
- `success`, `warning`, `error` - Semantic colors

#### Typography
- `font_family_base` - Base font stack
- `font_family_mono` - Monospace font stack
- `font_size_base`, `font_size_small`, `font_size_large` - Font sizes
- `line_height_base`, `line_height_tight` - Line heights

#### Spacing
- `unit` - Base spacing unit (8px)
- `xs`, `sm`, `md`, `lg`, `xl`, `xxl` - Spacing scale

#### Z-Index
- `layer_1_map` - Map layer (0)
- `layer_2_event_popups`, `layer_2_leaflet_popup`, `layer_2_leaflet_tooltip` - Popup layer (700-1000)
- `layer_3_ui`, `layer_3_filter_bar`, `layer_3_dashboard`, `layer_3_time_drawer` - UI layer (1500-1700)
- `layer_4_modals`, `layer_4_dashboard_expanded`, `layer_4_alerts` - Modal layer (2000+)

#### Shadows
- `small`, `medium`, `large` - Shadow sizes
- `glow_primary` - Primary color glow effect

#### Borders
- `radius_small`, `radius_medium`, `radius_large`, `radius_xl` - Border radii
- `width_thin`, `width_medium`, `width_thick` - Border widths

#### Transitions
- `fast`, `normal`, `slow` - Transition speeds

#### Branding
- `app_name` - Application name
- `tagline` - Application tagline
- `footer_text` - Footer attribution text

### CSS Variable Naming Convention

Design tokens are converted to CSS custom properties following this pattern:

```
config.json key → CSS variable name
───────────────────────────────────
colors.primary → --color-primary
typography.font_family_base → --font-family-base
spacing.md → --spacing-md
z_index.layer_3_ui → --z-layer-3-ui
shadows.medium → --shadow-medium
borders.radius_large → --border-radius-large
transitions.normal → --transition-normal
```

### Usage in CSS

```css
/* Colors */
color: var(--color-primary);
background: var(--color-bg-primary);

/* Typography */
font-family: var(--font-family-base);
font-size: var(--font-size-base);
line-height: var(--line-height-base);

/* Spacing */
padding: var(--spacing-md);
margin: var(--spacing-lg);

/* Z-Index */
z-index: var(--z-layer-3-ui);

/* Shadows */
box-shadow: var(--shadow-medium);

/* Borders */
border-radius: var(--border-radius-medium);
border-width: var(--border-width-thin);

/* Transitions */
transition: all var(--transition-normal);
```

## Instant Rebranding Workflow

Change your entire site's design in 4 steps:

### Step 1: Edit Design Tokens

Open `config.json` and modify the `design` section at the top:

```json
{
  "design": {
    "colors": {
      "primary": "#D689B8",  // Change to your brand color (default: ecoBarbie)
      "bg_primary": "#0d1117",
      ...
    },
    "typography": {
      "font_family_base": "Your Font, sans-serif",
      ...
    },
    ...
  }
}
```

### Step 2: Generate CSS Custom Properties

Run the token generator:

```bash
python3 src/tools/generate_design_tokens.py
```

This reads the design section and outputs `design-tokens.css`.

### Step 3: Rebuild Site

Generate the static site with updated tokens:

```bash
python3 src/event_manager.py generate
```

### Step 4: Test and Deploy

Test locally:

```bash
cd public
python3 -m http.server 8000
# Open http://localhost:8000
```

Deploy:

```bash
git add config.json layouts/ static/
git commit -m "🎨 Rebrand with new design tokens"
git push
```

## Semantic HTML Guidelines

### Use Proper Landmarks

- `<main>` - Main content (map)
- `<aside>` - Complementary content (dashboard)
- `<nav>` - Navigation (filter bar)
- `<header>` - Page header (if needed)
- `<footer>` - Page footer (if needed)

### ARIA Best Practices

1. **Always provide labels**
   ```html
   <nav aria-label="Event filter controls">
   ```

2. **Use live regions for dynamic content**
   ```html
   <div role="status" aria-live="polite" aria-atomic="true">
     <span id="filter-bar-event-count">0 events</span>
   </div>
   ```

3. **Mark dialogs properly**
   ```html
   <aside role="complementary" aria-label="Application menu">
   ```

4. **Indicate expanded/collapsed state**
   ```html
   <button aria-expanded="false" aria-haspopup="dialog">
   ```

### SEO Optimization

- Use semantic HTML5 tags
- Provide descriptive meta tags
- Include proper page title
- Use heading hierarchy (h1, h2, h3)
- Add alt text for images
- Provide noscript fallback with full content

## Testing and Linting

### Component Tests

Run component tests:

```bash
python3 tests/test_components.py --verbose
```

Tests validate:
- Component loading
- Design token loading
- CSS generation
- HTML assembly
- Backward compatibility
- Semantic structure
- Z-index layering

### Linting

Extend the linter for components:

```python
from src.modules.linter import Linter

linter = Linter(verbose=True)

# Lint individual component
result = linter.lint_component(component_html, "component-name")

# Lint all components
result = linter.lint_all_components(components_dir)

# Lint design tokens
result = linter.lint_design_tokens(design_config)

# Lint semantic structure
result = linter.lint_semantic_structure(html)
```

## Troubleshooting

### Design tokens not applying

1. Check if CSS was generated:
   ```bash
   ls -la assets/html/design-tokens.css
   ```

2. Regenerate tokens:
   ```bash
   python3 src/tools/generate_design_tokens.py
   ```

3. Rebuild site:
   ```bash
   python3 src/event_manager.py generate
   ```

### Components not loading

1. Verify all component files exist:
   ```bash
   find assets/html -name "*.html"
   ```

2. Check site generator logs for errors

3. Validate HTML structure

### Z-index conflicts

The 4-layer system is strictly enforced:
- Layer 1: 0 (map)
- Layer 2: 700-1000 (popups)
- Layer 3: 1500-1700 (UI)
- Layer 4: 2000+ (modals)

Always use `--z-layer-*` variables instead of hardcoded values.

## Best Practices

### KISS Principles Applied

This component system follows strict KISS (Keep It Simple, Stupid) principles:

1. **Flat Structure**
   - ✅ All components in one directory
   - ❌ No nested subdirectories
   - Why: Easier to find, simpler imports

2. **No Templating Engine**
   - ✅ Use Python's built-in `.format()`
   - ❌ No Jinja2, Mako, or complex templating
   - Why: Zero dependencies, transparent behavior

3. **Single Responsibility**
   - Each component does ONE thing
   - Each file is small (<200 lines)
   - Easy to understand at a glance

4. **Explicit Over Implicit**
   - Template variables clearly named: `{app_name}`
   - No magic: what you see is what you get
   - No hidden side effects

5. **Standard Library Only**
   - No external dependencies for components
   - Uses Python's `str.format()` and `Path`
   - Runs anywhere Python runs

### 1. Always Use Design Tokens

❌ **Don't:**
```css
.button {
  background: #D689B8;  /* Hardcoded color - bad! */
  padding: 16px;
}
```

✅ **Do:**
```css
.button {
  background: var(--color-primary);
  padding: var(--spacing-md);
}
```

### 2. Use Semantic HTML

❌ **Don't:**
```html
<div class="navigation">
  <div class="nav-item">Filter</div>
</div>
```

✅ **Do:**
```html
<nav aria-label="Event filters">
  <button class="filter-button">Filter</button>
</nav>
```

### 3. Follow Z-Index Layers

❌ **Don't:**
```css
.popup {
  z-index: 9999;
}
```

✅ **Do:**
```css
.popup {
  z-index: var(--z-layer-4-modals);
}
```

### 4. Provide Accessibility

Always include:
- ARIA labels for interactive elements
- Proper roles for landmarks
- Live regions for dynamic content
- Keyboard navigation support
- Focus indicators

### 5. Test Responsively

Test on:
- Mobile devices (320px+)
- Tablets (768px+)
- Desktop (1024px+)

### 6. Version Control Design Changes

Track design evolution:
```bash
git log --oneline config.json
```

## Integration with Existing System

This component system is fully integrated with the existing KRWL HOF infrastructure:

- **Site Generator**: `src/modules/site_generator.py` loads and assembles components
- **Linter**: `src/modules/linter.py` validates component HTML, CSS, and accessibility
- **Testing**: `tests/test_components.py` validates component functionality
- **Documentation**: All docs are markdown (.md) - no HTML generation needed (KISS principle)

## Future Enhancements

Potential improvements:
- [ ] Component variants (light/dark themes)
- [ ] Dynamic component loading
- [ ] Component preview tool
- [ ] Design token validation schemas
- [ ] Visual regression testing
- [ ] Component documentation generator

## Resources

- [Web Content Accessibility Guidelines (WCAG 2.1)](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs - HTML Semantics](https://developer.mozilla.org/en-US/docs/Glossary/Semantics)
- [CSS Custom Properties Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [ARIA Best Practices](https://www.w3.org/WAI/ARIA/apg/)

## Contributing

When adding new components:

1. Place in appropriate directory (`_base/`, `layout/`, `shared/`)
2. Use semantic HTML5 tags
3. Include ARIA attributes
4. Document template variables
5. Update this README
6. Add tests to `tests/test_components.py`
7. Update `features.json` registry

## License

Part of KRWL HOF Community Events project.
See main repository LICENSE for details.
