#!/usr/bin/env python3
"""Generate self-contained preview/index.html with all resources inlined"""

import json
from pathlib import Path

def main():
    base = Path(__file__).parent.parent
    static = base / 'static'
    
    # Load files
    config = json.load(open(base / 'config.preview.json'))
    events = json.load(open(static / 'events.json')).get('events', [])
    demo = json.load(open(static / 'events.demo.json')).get('events', [])
    content_en = json.load(open(static / 'content.json'))
    content_de = json.load(open(static / 'content.de.json'))
    
    leaflet_css = open(static / 'lib/leaflet/leaflet.css').read()
    leaflet_js = open(static / 'lib/leaflet/leaflet.js').read()
    app_css = open(static / 'css/style.css').read()
    i18n_js = open(static / 'js/i18n.js').read()
    app_js = open(static / 'js/app.js').read()
    
    all_events = events + demo
    
    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['app']['name']}</title>
    <meta name="robots" content="noindex">
    <style>{leaflet_css}</style>
    <style>{app_css}</style>
    <style>body::before{{content:'PREVIEW';position:fixed;top:10px;right:10px;background:rgba(255,105,180,.8);color:#000;padding:4px 12px;border-radius:4px;font-weight:bold;font-size:12px;z-index:10000;pointer-events:none}}</style>
</head>
<body>
    <div id="app">
        <noscript>
            <div style="max-width:1200px;margin:0 auto;padding:2rem;background:#1a1a1a;color:#fff">
                <h1 style="color:#FF69B4">{config['app']['name']}</h1>
                <p>Enable JavaScript to view {len(all_events)} events</p>
            </div>
        </noscript>
        <div id="main-content" style="display:none">
            <div id="filter-sentence">
                <span id="event-count-text">0 events</span>
                <span id="category-text" class="filter-part">in all categories</span>
                <span id="time-text" class="filter-part">till sunrise</span>
                <span id="distance-text" class="filter-part">within 5 km</span>
                <span id="location-text" class="filter-part">from your location</span>
            </div>
            <div id="location-status"></div>
            <div id="map"></div>
            <div id="event-detail" class="hidden">
                <div class="event-detail-content">
                    <button id="close-detail">&times;</button>
                    <h2 id="detail-title"></h2>
                    <p id="detail-description"></p>
                    <p><strong>Location:</strong> <span id="detail-location"></span></p>
                    <p><strong>Time:</strong> <span id="detail-time"></span></p>
                    <p><strong>Distance:</strong> <span id="detail-distance"></span></p>
                    <a id="detail-link" href="#" target="_blank">View Details</a>
                </div>
            </div>
        </div>
    </div>
    <script>window.EMBEDDED_CONFIG={json.dumps(config)};</script>
    <script>window.EMBEDDED_EVENTS={json.dumps(all_events)};</script>
    <script>window.EMBEDDED_CONTENT_EN={json.dumps(content_en)};</script>
    <script>window.EMBEDDED_CONTENT_DE={json.dumps(content_de)};</script>
    <script>{leaflet_js}</script>
    <script>{i18n_js}</script>
    <script>
(function(){{
    const f=window.fetch;
    window.fetch=function(url,opts){{
        if(url.includes('config.json'))return Promise.resolve({{ok:true,json:()=>Promise.resolve(window.EMBEDDED_CONFIG)}});
        if(url.includes('events.json'))return Promise.resolve({{ok:true,json:()=>Promise.resolve({{events:window.EMBEDDED_EVENTS}})}});
        if(url.includes('content.json')){{
            const c=url.includes('.de.')?window.EMBEDDED_CONTENT_DE:window.EMBEDDED_CONTENT_EN;
            return Promise.resolve({{ok:true,json:()=>Promise.resolve(c)}});
        }}
        return f.apply(this,arguments);
    }};
}})();
{app_js}
document.getElementById('main-content').style.display='block';
    </script>
</body>
</html>'''
    
    # Write output
    preview_dir = base / 'preview'
    preview_dir.mkdir(exist_ok=True)
    (preview_dir / 'index.html').write_text(html)
    print(f"✓ Generated preview/index.html ({len(html)/1024:.0f}KB, {len(all_events)} events)")

if __name__ == '__main__':
    main()
