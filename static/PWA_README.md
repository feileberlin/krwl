# PWA (Progressive Web App) Assets

This directory contains all the PWA icon placeholders and manifest for the KRWL HOF Community Events application.

## Files

### Manifest
- **manifest.json** - PWA manifest file that defines app behavior when installed

### Icons
- **favicon.svg** (32x32) - Browser tab favicon
- **icon-192.svg** (192x192) - Standard PWA icon
- **icon-512.svg** (512x512) - Large PWA icon for high-res displays
- **icon-192-maskable.svg** (192x192) - Maskable icon for Android adaptive icons
- **icon-512-maskable.svg** (512x512) - Large maskable icon for Android adaptive icons
- **logo.svg** (120x120) - Logo for imprint link

## Icon Types

### Standard Icons (`any` purpose)
Used on most devices and browsers. These have rounded corners built into the design.

### Maskable Icons (`maskable` purpose)
Android adaptive icons that work with any shape mask (circle, rounded square, squircle, etc.). 
These have:
- No rounded corners (system applies the mask)
- Safe area padding (icon content stays within 80% safe zone)
- Full bleed background color

## Customization

All icons use the brand colors from config.json:
- **Primary Color**: #4CAF50 (Green)
- **Background**: #1a1a1a (Dark)

To customize for your fork:
1. Edit `config.json` to set your colors:
   ```json
   "ui": {
     "theme_color": "#4CAF50",
     "background_color": "#1a1a1a"
   }
   ```

2. Replace the SVG icon files with your own design (keep the same dimensions)

3. Update `manifest.json` with your app name and description

## Testing PWA Installation

1. Open the app in Chrome/Edge on desktop or mobile
2. Look for the "Install" button in the address bar
3. Or use Chrome DevTools > Application > Manifest to check setup

## Icon Size Requirements

- **Favicon**: 32x32 or any size (SVG scales automatically)
- **Apple Touch Icon**: 180x180 minimum
- **PWA Icon**: 192x192 minimum, 512x512 recommended
- **Maskable Icon**: 192x192 minimum with 10% safe area padding

## Browser Support

- ✅ Chrome/Edge (full PWA support)
- ✅ Safari (limited PWA support, uses apple-touch-icon)
- ✅ Firefox (basic manifest support)
- ✅ Samsung Internet (full PWA support)
