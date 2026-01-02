# CDN Fallback System

## Overview

The KRWL HOF static site generator uses a **CDN-first approach with local fallback** for Leaflet.js resources. This ensures the site can be generated even without internet connectivity.

## How It Works

### CDN Priority

When generating the static site, the system attempts to fetch Leaflet resources from CDN:

```
1. Try CDN: https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css
2. If successful: Use CDN version (latest, optimized)
3. If failed: Fall back to local files
```

### Local Fallback

If CDN is unavailable (no internet, blocked domain, timeout), the system automatically falls back to local files:

```
static/lib/leaflet/
  ├── leaflet.css    (fallback CSS)
  └── leaflet.js     (fallback JS)
```

## Architecture

### CDN Inliner Module

**File**: `src/modules/cdn_inliner.py`

**Key Methods**:

1. **`get_leaflet_css()`** - Fetches CSS from CDN or local fallback
2. **`get_leaflet_js()`** - Fetches JS from CDN or local fallback
3. **`fetch_from_cdn(url)`** - Attempts CDN fetch with timeout
4. **`read_local_file(path)`** - Reads from local filesystem

### Example Flow

```python
def get_leaflet_css(self):
    """Get Leaflet CSS from CDN or local fallback"""
    try:
        print("Fetching Leaflet CSS from CDN...")
        return self.fetch_from_cdn(self.LEAFLET_CSS_URL)
    except Exception as e:
        print(f"  ⚠ CDN fetch failed: {e}")
        print("  Using local Leaflet CSS...")
        local_path = self.static_path / 'lib' / 'leaflet' / 'leaflet.css'
        return self.read_local_file(local_path)
```

## Testing

### Automated Tests

Run the CDN fallback test suite:

```bash
python3 test_cdn_fallback.py
```

**Tests include**:
- Local files exist and are not empty
- Network error fallback works
- Timeout fallback works
- Successful CDN fetch works
- Full generation with fallback succeeds

### Manual Testing

#### Test CDN Fallback (No Internet)

1. Disconnect from internet or block CDN domain
2. Run generation:
   ```bash
   python3 src/main.py generate
   ```
3. Observe output:
   ```
   Fetching Leaflet CSS from CDN...
     ⚠ CDN fetch failed: [Errno -5] No address associated with hostname
     Using local Leaflet CSS...
   ```
4. Verify HTML generated successfully

#### Test CDN Success (With Internet)

1. Connect to internet
2. Run generation:
   ```bash
   python3 src/main.py generate
   ```
3. Observe successful CDN fetch (no fallback messages)

## Benefits

### 1. Reliability
- **Works offline**: Developers can generate site without internet
- **CI/CD resilience**: Builds succeed even if CDN is down
- **Emergency fallback**: Production deploys always succeed

### 2. Performance
- **CDN-first**: Uses latest optimized versions when available
- **Local cache**: Faster builds in restricted environments

### 3. Flexibility
- **Development**: Local files ensure consistent dev environment
- **Production**: CDN provides latest security patches and performance

## Maintenance

### Updating Local Fallback Files

When Leaflet versions change:

1. **Download new version**:
   ```bash
   ./scripts/download-libs.sh
   ```

2. **Verify integrity**:
   ```bash
   python3 manage_libs.py verify
   ```

3. **Update CDN URLs** in `src/modules/cdn_inliner.py`:
   ```python
   LEAFLET_CSS_URL = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
   LEAFLET_JS_URL = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"
   ```

4. **Test both paths**:
   ```bash
   # Test with internet (CDN)
   python3 src/main.py generate
   
   # Test without internet (fallback)
   python3 test_cdn_fallback.py
   ```

## Troubleshooting

### Problem: Generation fails even with local files

**Solution**: Verify local files exist and are not empty:
```bash
ls -lh static/lib/leaflet/
```

Expected output:
```
-rw-rw-r-- 1 user user  723 Jan  1 14:36 leaflet.css
-rw-rw-r-- 1 user user 2.6K Jan  1 14:36 leaflet.js
```

### Problem: Local files are outdated

**Solution**: Re-download libraries:
```bash
./scripts/download-libs.sh
python3 manage_libs.py verify
```

### Problem: CDN always fails (network restrictions)

**Solution**: This is expected behavior. The fallback will automatically use local files. No action needed.

## Security Considerations

### CDN Integrity

When using CDN:
- **jsDelivr**: Trusted CDN with integrity checks
- **HTTPS only**: Enforced by URL scheme
- **Version pinning**: Specific version (1.9.4) prevents surprises

### Local Files

When using fallback:
- **Downloaded via script**: Controlled download process
- **Version locked**: Files match version in CDN URL
- **Integrity verification**: Optional via `manage_libs.py verify`

## Performance Comparison

| Scenario | CDN | Local Fallback |
|----------|-----|----------------|
| **Build Time** | +2-5s (fetch) | Instant |
| **File Size** | Optimized | Same |
| **Freshness** | Latest | Snapshot |
| **Reliability** | Network-dependent | Always works |

## Best Practices

1. **Keep local files updated**: Run `./scripts/download-libs.sh` regularly
2. **Test both paths**: Verify CDN and fallback in CI/CD
3. **Monitor CDN health**: jsDelivr status page
4. **Version pin CDN**: Don't use `@latest` in production

## Related Files

- `src/modules/cdn_inliner.py` - Implementation
- `test_cdn_fallback.py` - Automated tests
- `download-libs.sh` - Download script for local files
- `manage_libs.py` - Library management utilities
- `static/lib/leaflet/` - Local fallback directory

## Further Reading

- [jsDelivr CDN Documentation](https://www.jsdelivr.com/documentation)
- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [CDN Best Practices](https://web.dev/content-delivery-networks/)
