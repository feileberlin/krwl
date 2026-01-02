#!/usr/bin/env python3
"""Unified HTML Generator - KISS: One simple script for all HTML generation"""
import json, base64, sys
from pathlib import Path

def generate(mode='preview'):
    base = Path(__file__).parent.parent
    static = base / 'static'
    
    # Load resources
    css = (static/'lib/leaflet/leaflet.css').read_text() + (static/'css/style.css').read_text()
    js = (static/'lib/leaflet/leaflet.js').read_text() + '\n' + (static/'js/i18n.js').read_text() + '\n' + (static/'js/app.js').read_text()
    icon = 'data:image/svg+xml;base64,' + base64.b64encode((static/'favicon.svg').read_text().encode()).decode()
    
    # Load data
    cfg = json.load(open(base/'config.prod.json' if mode=='production' else base/'config.preview.json'))
    events = json.load(open(static/'events.json')).get('events', [])
    if mode == 'preview':
        events += json.load(open(static/'events.demo.json')).get('events', [])
    i18n_en = json.load(open(static/'content.json'))
    i18n_de = json.load(open(static/'content.de.json'))
    
    # Generate HTML
    badge = '<style>body::before{content:"PREVIEW";position:fixed;top:10px;right:10px;background:rgba(255,105,180,.8);color:#000;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:12px;z-index:10000}</style>' if mode=='preview' else ''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['app']['name']}</title>
<link rel="icon" href="{icon}">
<style>{css}</style>{badge}
</head>
<body>
<div id="app">
<noscript><div style="max-width:1200px;margin:0 auto;padding:2rem;background:#1a1a1a;color:#fff"><h1 style="color:#FF69B4">{cfg['app']['name']}</h1><p>Enable JavaScript to view {len(events)} events</p></div></noscript>
<div id="main-content" style="display:none">
<div id="filter-sentence"><span id="event-count-text">0 events</span> <span id="category-text" class="filter-part">in all categories</span> <span id="time-text" class="filter-part">till sunrise</span> <span id="distance-text" class="filter-part">within 5 km</span> <span id="location-text" class="filter-part">from your location</span></div>
<div id="location-status"></div>
<div id="map"></div>
<div id="event-detail" class="hidden"><div class="event-detail-content"><button id="close-detail">&times;</button><h2 id="detail-title"></h2><p id="detail-description"></p><p><strong>Location:</strong> <span id="detail-location"></span></p><p><strong>Time:</strong> <span id="detail-time"></span></p><p><strong>Distance:</strong> <span id="detail-distance"></span></p><a id="detail-link" href="#" target="_blank">View Details</a></div></div>
</div></div>
<script>window.EMBEDDED_CONFIG={json.dumps(cfg)};window.EMBEDDED_EVENTS={json.dumps(events)};window.EMBEDDED_CONTENT_EN={json.dumps(i18n_en)};window.EMBEDDED_CONTENT_DE={json.dumps(i18n_de)};
(function(){{const f=window.fetch;window.fetch=function(url,opts){{if(url.includes('config.json'))return Promise.resolve({{ok:1,json:()=>Promise.resolve(window.EMBEDDED_CONFIG)}});if(url.includes('events.json'))return Promise.resolve({{ok:1,json:()=>Promise.resolve({{events:window.EMBEDDED_EVENTS}})}});if(url.includes('content.json'))return Promise.resolve({{ok:1,json:()=>Promise.resolve(url.includes('.de.')?window.EMBEDDED_CONTENT_DE:window.EMBEDDED_CONTENT_EN)}});return f.apply(this,arguments)}}}})();
{js}
document.getElementById('main-content').style.display='block';
</script>
</body>
</html>'''
    
    # Write output
    out = (static/'preview'/'index.html') if mode=='preview' else (static/'index.html')
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f"✓ Generated {out.relative_to(base)} ({len(html)//1024}KB, {len(events)} events)")

if __name__ == '__main__':
    generate(sys.argv[1] if len(sys.argv) > 1 else 'preview')
