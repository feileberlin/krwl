# Feature Registry and Testing Guide

## Overview

This system provides a comprehensive feature registry and automated testing to ensure that all documented features remain present in the codebase after merges to the main branch.

## Components

### 1. Feature Registry (`features.json`)

The feature registry is a JSON file that documents all implemented features in the KRWL HOF application. Each feature includes:

- **id**: Unique identifier for the feature
- **name**: Human-readable feature name
- **description**: Brief description of what the feature does
- **category**: Feature category (backend, frontend, deployment)
- **implemented**: Boolean indicating if the feature is implemented
- **files**: List of files that implement this feature
- **config_keys**: Configuration keys used by this feature (optional)
- **code_patterns**: Regular expressions to verify feature presence in code (optional)
- **test_method**: Method used to verify the feature

#### Example Feature Entry

```json
{
  "id": "geolocation-filtering",
  "name": "Geolocation Filtering",
  "description": "Shows only events near the user's location",
  "category": "frontend",
  "implemented": true,
  "files": [
    "static/js/app.js"
  ],
  "config_keys": [
    "filtering.max_distance_km"
  ],
  "code_patterns": [
    {
      "file": "static/js/app.js",
      "pattern": "navigator.geolocation.getCurrentPosition",
      "description": "Geolocation API usage"
    }
  ],
  "test_method": "check_code_patterns"
}
```

### 2. Feature Verification Script (`verify_features.py`)

A Python script that verifies all features documented in `features.json` are present in the codebase.

#### Usage

```bash
# Basic verification
python3 scripts/verify_features.py

# Verbose output (shows detailed checks)
python3 scripts/verify_features.py --verbose

# JSON output (for CI/CD integration)
python3 scripts/verify_features.py --json
```

#### Verification Methods

The script supports three types of verification:

1. **File Existence** (`check_files_exist`)
   - Verifies that all files listed in the feature's `files` array exist
   - Used for all features by default

2. **Code Pattern Matching** (`check_code_patterns`)
   - Uses regular expressions to verify code patterns exist in specified files
   - Ensures feature implementation hasn't been removed during refactoring

3. **Config Key Verification** (`check_config_keys`)
   - Verifies configuration keys are present in config files
   - Checks both `config.dev.json` and `config.prod.json`

### 3. GitHub Actions Workflow (`.github/workflows/verify-features.yml`)

Automatically runs feature verification on:
- Push to `main` or `preview` branches
- Pull requests to `main` or `preview` branches
- Manual workflow dispatch

#### Workflow Features

- **Automatic Verification**: Runs on every push and PR
- **PR Comments**: Posts detailed failure information on PRs if verification fails
- **Artifacts**: Uploads verification results for later review
- **Job Summary**: Provides quick overview in GitHub Actions UI
- **Fail on Error**: Blocks merges if features are missing (optional based on branch protection)

## How It Works

### 1. Feature Documentation

When adding a new feature:

1. Implement the feature in code
2. Add an entry to `features.json` documenting:
   - What files implement it
   - What code patterns verify it
   - What config keys it uses
3. Run `python3 scripts/verify_features.py` locally to verify

### 2. Automatic Verification

When code is pushed or a PR is created:

1. GitHub Actions runs the verification workflow
2. The workflow executes `verify_features.py`
3. Results are:
   - Displayed in the workflow logs
   - Uploaded as artifacts
   - Posted as PR comments (if failures occur)
   - Shown in the job summary

### 3. Preventing Feature Loss

If a feature is accidentally removed:

1. The verification workflow fails
2. A detailed comment is posted on the PR showing:
   - Which features failed
   - What files are missing
   - What code patterns weren't found
3. The PR can be blocked until:
   - The feature is restored, OR
   - The feature registry is updated to reflect intentional removal

## Adding New Features

### Step 1: Implement the Feature

Implement your feature in the codebase as usual.

### Step 2: Document in Feature Registry

Add an entry to `features.json`:

```json
{
  "id": "my-new-feature",
  "name": "My New Feature",
  "description": "Brief description of what it does",
  "category": "frontend",
  "implemented": true,
  "files": [
    "path/to/implementation.js"
  ],
  "code_patterns": [
    {
      "file": "path/to/implementation.js",
      "pattern": "uniqueFunctionName|uniqueCodePattern",
      "description": "What this pattern verifies"
    }
  ],
  "config_keys": [
    "config.key.for.feature"
  ],
  "test_method": "check_code_patterns"
}
```

### Step 3: Verify Locally

```bash
python3 scripts/verify_features.py --verbose
```

Ensure your new feature passes verification before committing.

### Step 4: Commit and Push

```bash
git add features.json path/to/implementation.js
git commit -m "Add my new feature"
git push
```

The verification workflow will automatically run and verify your feature.

## Removing Features

If you intentionally remove a feature:

### Step 1: Remove the Feature Code

Delete or modify the feature implementation.

### Step 2: Update Feature Registry

Either:

- **Remove the feature entry** from `features.json`, OR
- **Mark as not implemented**: Set `"implemented": false`

### Step 3: Document the Change

In your commit message, explain why the feature was removed.

### Step 4: Verify

Run `python3 scripts/verify_features.py` to ensure no other features were accidentally affected.

## Preview Deployment with Custom Domains

The preview deployment workflow now supports both GitHub Pages default URLs and custom domains:

### How It Works

1. **Custom Domain Detection**: The workflow checks if a `CNAME` file exists
2. **Dynamic Base URL**: 
   - With CNAME: `https://yourdomain.com/preview/`
   - Without CNAME: `https://owner.github.io/repo-name/preview/`
3. **Relative Paths**: Uses `<base href="/preview/">` which works with both setups

### Preview URLs

- **GitHub Pages (no custom domain)**: 
  - `https://feileberlin.github.io/krwl-hof/preview/`
  
- **Custom Domain (with CNAME)**:
  - `https://krwl.in/preview/`

Both work automatically without code changes!

## Troubleshooting

### Feature Verification Fails Locally

**Problem**: `verify_features.py` reports failures

**Solution**:
1. Run with `--verbose` to see detailed output
2. Check if files exist at specified paths
3. Verify code patterns match actual implementation
4. Update `features.json` if feature was intentionally modified

### Workflow Fails in CI

**Problem**: GitHub Actions workflow fails but local verification passes

**Solution**:
1. Check workflow logs in Actions tab
2. Download verification artifacts for detailed results
3. Ensure all files are committed and pushed
4. Verify file paths are relative to repository root

### False Positives in Pattern Matching

**Problem**: Code pattern not found even though feature exists

**Solution**:
1. Check the regular expression in `code_patterns`
2. Make pattern more flexible or specific as needed
3. Test pattern locally: `grep -E "pattern" file.js`
4. Update pattern in `features.json`

### Preview Path Not Working with Custom Domain

**Problem**: Preview site doesn't load properly at custom domain

**Solution**:
1. Verify CNAME file exists in repository root
2. Check GitHub Pages settings show custom domain
3. Ensure DNS is configured correctly
4. Wait a few minutes for DNS propagation
5. Check that `<base href="/preview/">` is injected in index.html

## Best Practices

### 1. Granular Features

Document features at an appropriate level of granularity:
- Too granular: Every function becomes a "feature"
- Too broad: Entire modules as single features
- **Good balance**: User-facing features and major capabilities

### 2. Reliable Code Patterns

Choose code patterns that:
- Are unlikely to change during refactoring
- Are unique to the feature
- Use function names, class names, or distinctive strings

### 3. Keep Registry Updated

- Update `features.json` whenever features change
- Review registry during code reviews
- Run verification before merging PRs

### 4. Document Intent

Use descriptive feature names and descriptions that explain:
- What the feature does for users
- Why it exists
- What problem it solves

### 5. Regular Audits

Periodically review:
- Are all features still relevant?
- Are new features documented?
- Do patterns still match implementation?

## Integration with Development Workflow

### Local Development

```bash
# Before committing
python3 scripts/verify_features.py

# See detailed output
python3 scripts/verify_features.py --verbose
```

### Pull Request Workflow

1. Create feature branch
2. Implement feature
3. Add to `features.json`
4. Verify locally
5. Push and create PR
6. Automated verification runs
7. Review results in PR comments
8. Fix any issues
9. Merge when verification passes

### Production Deploy

1. Changes merged to `preview` branch
2. Verification runs automatically
3. Deploy to `/preview/` for testing
4. Promote to `main` via PR
5. Verification runs again on `main`
6. Deploy to production

## Example Workflow

Here's a complete example of adding a new feature:

### 1. Implement the Feature

```javascript
// static/js/app.js
class EventsApp {
    setupNotifications() {
        if ('Notification' in window) {
            this.notificationsEnabled = true;
            // ... implementation
        }
    }
}
```

### 2. Update Feature Registry

```json
{
  "id": "push-notifications",
  "name": "Push Notifications",
  "description": "Browser notifications for upcoming events",
  "category": "frontend",
  "implemented": true,
  "files": [
    "static/js/app.js"
  ],
  "code_patterns": [
    {
      "file": "static/js/app.js",
      "pattern": "setupNotifications|Notification.*in.*window",
      "description": "Notification API usage"
    }
  ],
  "config_keys": [
    "notifications.enabled"
  ],
  "test_method": "check_code_patterns"
}
```

### 3. Verify

```bash
$ python3 scripts/verify_features.py
============================================================
KRWL HOF Feature Verification
============================================================
✓ Push Notifications (push-notifications)
...
✓ All features verified successfully!
```

### 4. Commit and Push

```bash
git add static/js/app.js features.json
git commit -m "Add push notifications feature"
git push origin feature/push-notifications
```

### 5. Create PR

The verification workflow runs automatically and posts results on the PR.

## Advanced Usage

### Custom Verification Logic

To add custom verification logic, extend the `FeatureVerifier` class in `verify_features.py`:

```python
def check_custom_method(self, feature):
    """Custom verification method"""
    # Your custom logic here
    return success, details
```

Then use `"test_method": "check_custom_method"` in `features.json`.

### Selective Verification

To verify only specific features:

```bash
# Verify only frontend features
python3 -c "
import json
from verify_features import FeatureVerifier

verifier = FeatureVerifier(verbose=True)
data = verifier.load_features()
frontend_features = [f for f in data['features'] if f['category'] == 'frontend']

for feature in frontend_features:
    result = verifier.verify_feature(feature)
    print(f\"{result['name']}: {result['status']}\")
"
```

### Integration with Other Tools

The JSON output can be used by other tools:

```bash
# Generate HTML report
python3 scripts/verify_features.py --json | python3 generate_report.py > report.html

# Send to monitoring system
python3 scripts/verify_features.py --json | curl -X POST -d @- https://monitoring.example.com/api
```

## Maintenance

### Regular Tasks

- **Weekly**: Review feature registry for accuracy
- **Per Release**: Audit features against release notes
- **Quarterly**: Update verification patterns for robustness

### When to Update

Update `features.json` when:
- Adding new features
- Removing features
- Refactoring code (patterns may change)
- Updating configuration structure
- Moving files to new locations

## Support

For issues or questions:
1. Check this documentation
2. Review `verify_features.py` code comments
3. Check workflow logs in GitHub Actions
4. Open an issue in the repository

## Future Enhancements

Potential improvements to the system:

- [ ] Visual dashboard for feature status
- [ ] Integration testing beyond file/pattern checking
- [ ] Automated feature discovery from code
- [ ] Historical tracking of feature changes
- [ ] Performance impact monitoring per feature
- [ ] Dependency mapping between features
