# CSS Custom Properties Reference

Auto-generated CSS custom properties from design tokens in `config.json`.

## Usage

```css
/* In your CSS files */
.my-component {
  color: var(--color-primary);
  background: var(--color-bg-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-medium);
  transition: all var(--transition-normal);
}
```

## Color Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--color-primary` | #FF69B4 | Primary brand color (Barbie Pink) |
| `--color-primary-hover` | #ff4da6 | Primary color hover state |
| `--color-bg-primary` | #0d1117 | Primary background (darkest) |
| `--color-bg-secondary` | #161b22 | Secondary background |
| `--color-bg-tertiary` | #21262d | Tertiary background (lightest dark) |
| `--color-text-primary` | #c9d1d9 | Primary text color |
| `--color-text-secondary` | #8b949e | Secondary text color |
| `--color-text-tertiary` | #6e7681 | Tertiary text color (muted) |
| `--color-border-primary` | #30363d | Primary border color |
| `--color-border-secondary` | #21262d | Secondary border color |
| `--color-accent` | #58a6ff | Accent color for highlights |
| `--color-success` | #3fb950 | Success state color |
| `--color-warning` | #d29922 | Warning state color |
| `--color-error` | #f85149 | Error state color |

## Typography Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--font-family-base` | -apple-system, BlinkMacSystemFont, 'Segoe UI'... | Base font stack (system fonts) |
| `--font-family-mono` | 'Monaco', 'Courier New', monospace | Monospace font stack |
| `--font-size-base` | 16px | Base font size |
| `--font-size-small` | 14px | Small font size |
| `--font-size-large` | 18px | Large font size |
| `--line-height-base` | 1.6 | Base line height |
| `--line-height-tight` | 1.25 | Tight line height (headings) |

## Spacing Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--spacing-unit` | 8px | Base spacing unit |
| `--spacing-xs` | 4px | Extra small spacing (0.5 units) |
| `--spacing-sm` | 8px | Small spacing (1 unit) |
| `--spacing-md` | 16px | Medium spacing (2 units) |
| `--spacing-lg` | 24px | Large spacing (3 units) |
| `--spacing-xl` | 32px | Extra large spacing (4 units) |
| `--spacing-xxl` | 48px | Extra extra large spacing (6 units) |

## Z-Index Variables (4-Layer System)

| Variable | Default Value | Layer | Description |
|----------|---------------|-------|-------------|
| `--z-layer-1-map` | 0 | 1 | Map background |
| `--z-layer-2-leaflet-tooltip` | 650 | 2 | Leaflet tooltips |
| `--z-layer-2-leaflet-popup` | 700 | 2 | Leaflet popups |
| `--z-layer-2-event-popups` | 1000 | 2 | Event popups |
| `--z-layer-3-ui` | 1500 | 3 | Generic UI elements |
| `--z-layer-3-filter-bar` | 1500 | 3 | Filter bar |
| `--z-layer-3-dashboard` | 1600 | 3 | Dashboard menu |
| `--z-layer-3-time-drawer` | 1600 | 3 | Time drawer |
| `--z-layer-4-modals` | 2000 | 4 | Modal dialogs |
| `--z-layer-4-dashboard-expanded` | 2000 | 4 | Expanded dashboard |
| `--z-layer-4-alerts` | 2100 | 4 | Alert notifications |

## Shadow Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--shadow-small` | 0 2px 4px rgba(0, 0, 0, 0.3) | Small shadow |
| `--shadow-medium` | 0 4px 12px rgba(0, 0, 0, 0.4) | Medium shadow |
| `--shadow-large` | 0 8px 24px rgba(0, 0, 0, 0.5) | Large shadow |
| `--shadow-glow-primary` | 0 0 10px rgba(255, 105, 180, 0.3) | Primary color glow |

## Border Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--border-radius-small` | 4px | Small border radius |
| `--border-radius-medium` | 6px | Medium border radius |
| `--border-radius-large` | 8px | Large border radius |
| `--border-radius-xl` | 12px | Extra large border radius |
| `--border-width-thin` | 1px | Thin border |
| `--border-width-medium` | 2px | Medium border |
| `--border-width-thick` | 4px | Thick border |

## Transition Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `--transition-fast` | 0.1s ease-out | Fast transition |
| `--transition-normal` | 0.2s ease-out | Normal transition |
| `--transition-slow` | 0.3s ease-out | Slow transition |

## Overlay Utility Classes

Pre-built classes using design tokens:

```css
.overlay {
  position: fixed;
  background: var(--color-bg-secondary);
  border: var(--border-width-thin) solid var(--color-border-primary);
  border-radius: var(--border-radius-medium);
  box-shadow: var(--shadow-medium);
}

.overlay--layer-3 {
  z-index: var(--z-layer-3-ui);
}

.overlay--layer-4 {
  z-index: var(--z-layer-4-modals);
}

.overlay--top-left {
  top: var(--spacing-md);
  left: var(--spacing-md);
}

.overlay--top-center {
  top: var(--spacing-md);
  left: 50%;
  transform: translateX(-50%);
}

.overlay--top-right {
  top: var(--spacing-md);
  right: var(--spacing-md);
}
```

## Regenerating Variables

When you update design tokens in `config.json`:

```bash
# Regenerate CSS custom properties
python3 src/templates/components/generate_design_tokens.py

# Rebuild the site
python3 src/event_manager.py generate
```

## Browser Support

CSS custom properties are supported in:
- Chrome 49+
- Firefox 31+
- Safari 9.1+
- Edge 15+

For older browsers, consider using a fallback or polyfill.

## Related Files

- `config.json` - Design token definitions
- `src/templates/components/generate_design_tokens.py` - Token generator
- `src/templates/components/design-tokens.css` - Generated CSS output
- `assets/css/style.css` - Main stylesheet using tokens
