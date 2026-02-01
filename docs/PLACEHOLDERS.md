# Repository URL Placeholders

This document explains the placeholder system for repository URLs in the KRWL> Community Events project.

## Overview

To make repository URLs maintainable and avoid hardcoding them in multiple places, we use a placeholder system. Repository information is stored centrally in `config.json` and placeholders in source files are replaced during the build process.

## Why Use Placeholders?

**Before (Hardcoded):**
```html
<a href="https://github.com/feileberlin/krwl.in">Repository</a>
```

**After (With Placeholders):**
```html
<a href="{{REPO_URL}}">Repository</a>
```

**Benefits:**
- ✅ Single source of truth (`config.json`)
- ✅ Easy repository renaming (change once, applies everywhere)
- ✅ Consistent URLs across the entire application
- ✅ No need to search and replace URLs manually

## Available Placeholders

### {{REPO_URL}}
Full repository URL.

**Example:**
```
Placeholder: {{REPO_URL}}
Replaced with: https://github.com/feileberlin/krwl.in
```

**Usage:**
```html
<!-- HTML -->
<a href="{{REPO_URL}}">Visit Repository</a>

<!-- JavaScript -->
const repoUrl = '{{REPO_URL}}';
```

### {{REPO_OWNER}}
Repository owner name only.

**Example:**
```
Placeholder: {{REPO_OWNER}}
Replaced with: feileberlin
```

### {{REPO_NAME}}
Repository name only.

**Example:**
```
Placeholder: {{REPO_NAME}}
Replaced with: krwl.in
```

### {{REPO_OWNER_SLASH_NAME}}
Owner and name in `owner/name` format.

**Example:**
```
Placeholder: {{REPO_OWNER_SLASH_NAME}}
Replaced with: feileberlin/krwl.in
```

## Where to Use Placeholders

### HTML Templates
Files in `assets/html/` can use placeholders:

```html
<!-- assets/html/dashboard-aside.html -->
<a href="{{REPO_URL}}/actions/workflows/scrape-events.yml">
  Review Events
</a>

<a href="{{REPO_URL}}/blob/main/README.md">README</a>
```

### JavaScript Files
Files in `assets/js/` can use placeholders:

```javascript
// assets/js/app.js
const repoUrl = this.config?.app?.repository?.url || '{{REPO_URL}}';

// assets/js/forms.js
'• GitHub: {{REPO_URL}}/issues\n'
```

## Configuration

Repository information is stored in `config.json`:

```json
{
  "app": {
    "repository": {
      "owner": "feileberlin",
      "name": "krwl.in",
      "url": "https://github.com/feileberlin/krwl.in"
    }
  }
}
```

## How It Works

### Build Process

1. **Load Configuration**
   ```python
   config = load_config('config.json')
   repo_info = config['app']['repository']
   ```

2. **Load Templates**
   ```python
   html_template = load_component('dashboard-aside.html')
   js_code = load_script('app.js')
   ```

3. **Replace Placeholders**
   ```python
   html_template = replace_repository_placeholders(html_template, config)
   js_code = replace_repository_placeholders(js_code, config)
   ```

4. **Generate Output**
   ```python
   # public/index.html now contains actual URLs
   ```

### Implementation

The placeholder replacement is implemented in `src/modules/site_generator.py`:

```python
def replace_repository_placeholders(self, content: str, config: Dict) -> str:
    """
    Replace repository URL placeholders with actual values from config.json.
    
    Placeholders supported:
    - {{REPO_URL}} -> Full repository URL
    - {{REPO_OWNER}} -> Repository owner
    - {{REPO_NAME}} -> Repository name
    - {{REPO_OWNER_SLASH_NAME}} -> owner/name format
    """
    repo_info = config.get('app', {}).get('repository', {})
    repo_owner = repo_info.get('owner', 'feileberlin')
    repo_name = repo_info.get('name', 'krwl.in')
    repo_url = repo_info.get('url', f'https://github.com/{repo_owner}/{repo_name}')
    
    replacements = {
        '{{REPO_URL}}': repo_url,
        '{{REPO_OWNER}}': repo_owner,
        '{{REPO_NAME}}': repo_name,
        '{{REPO_OWNER_SLASH_NAME}}': f'{repo_owner}/{repo_name}'
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    return content
```

## Renaming the Repository

To rename the repository:

1. **Update config.json** (only place to change):
   ```json
   {
     "app": {
       "repository": {
         "owner": "new-owner",
         "name": "new-repo-name",
         "url": "https://github.com/new-owner/new-repo-name"
       }
     }
   }
   ```

2. **Rebuild the site**:
   ```bash
   python3 src/event_manager.py generate
   ```

3. **Done!** All URLs are updated automatically.

## Verification

After building, verify that no unreplaced placeholders remain:

```bash
# Check for unreplaced placeholders
grep "{{REPO" public/index.html
# Should return no results

# Verify actual URLs are present
grep "github.com" public/index.html | head -5
# Should show actual repository URLs
```

## Files Using Placeholders

### HTML Templates
- `assets/html/dashboard-aside.html` - Contact links, documentation links

### JavaScript Files
- `assets/js/app.js` - Fallback repository URL
- `assets/js/forms.js` - GitHub issue links
- `assets/js/scraper-setup-tool.js` - GitHub Actions workflow links

## Best Practices

### DO ✅
- Use placeholders for any repository-specific URLs
- Test the build after adding new placeholders
- Document new placeholders if you add custom ones

### DON'T ❌
- Don't hardcode repository URLs in source files
- Don't edit `public/index.html` directly (it's auto-generated)
- Don't add placeholders without updating the replacement logic

## Troubleshooting

### Placeholder not replaced?

**Check:**
1. Is the placeholder spelled correctly? (case-sensitive)
2. Is the file being processed by `replace_repository_placeholders()`?
3. Is `config.json` loaded correctly during build?

**Fix:**
- For HTML: Ensure component is loaded and processed in `generate_html_from_components()`
- For JavaScript: Ensure script is loaded via `load_script_resources()` with config parameter

### Wrong URL after replacement?

**Check:**
- Verify `config.json` has correct repository information
- Rebuild the site: `python3 src/event_manager.py generate`
- Clear any cached files

## Future Enhancements

Potential improvements:
- Add more placeholder types (e.g., `{{BASE_URL}}`, `{{APP_NAME}}`)
- Support conditional placeholders (e.g., `{{#if DEV}}...{{/if}}`)
- Add placeholder validation during build
- Generate placeholder documentation automatically

## Related Documentation

- [Copilot Instructions](.github/copilot-instructions.md) - Project guidelines
- [Site Generator](src/modules/site_generator.py) - Implementation details
- [Configuration](config.json) - Repository settings

---

**Last Updated:** 2026-02-01
**Introduced:** v2.1.0 (Repository rename refactoring)
