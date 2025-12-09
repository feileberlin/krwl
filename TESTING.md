# Testing Strategy

This document describes the comprehensive testing approach for KRWL HOF Community Events application, covering both development and production environments.

## Test Levels

### 1. Development Tests (Pre-commit)
Fast, local tests run by developers before committing code.

### 2. Integration Tests (CI/CD)
Automated tests run on every PR and push.

### 3. Production Tests (Monitoring)
Continuous validation of live production environment.

## Development Tests

### Unit Tests

**test_scraper.py** - Event scraper functionality
- ✅ Manual event creation
- ✅ Event deduplication
- ✅ Source type handling (RSS, API, HTML)
- ✅ Data validation
- ✅ Error handling
- Runtime: ~5 seconds
- Run: `python3 test_scraper.py --verbose`

**test_filters.py** - Event filtering logic
- ✅ Time filtering (sunrise, sunday, full moon, hours)
- ✅ Distance filtering (15 min foot, 10 min bike, 1 hr transport)
- ✅ Category filtering
- ✅ Location filtering
- Runtime: ~3 seconds
- Run: `python3 test_filters.py --verbose`

**test_event_schema.py** - Event schema and filter stringency validation
- ✅ JSON schema definition validation
- ✅ Event example file validation against schema
- ✅ Event data file validation against schema
- ✅ Example vs schema consistency (coverage of optional fields)
- ✅ Time filter stringency testing
- ✅ Distance filter stringency testing
- ✅ Category filter stringency testing
- ✅ Recovery suggestions for schema violations
- Runtime: ~2 seconds
- Run: `python3 test_event_schema.py --verbose`
- Show schema: `python3 test_event_schema.py --show-schema`

**verify_features.py** - Feature registry validation
- ✅ All declared features are implemented
- ✅ Feature registry matches codebase
- ✅ No undeclared features exist
- Runtime: ~2 seconds
- Run: `python3 verify_features.py --verbose`

**check_kiss.py** - KISS principle compliance
- ✅ Code complexity checks
- ✅ File size limits
- ✅ Dependency checks
- Runtime: ~2 seconds
- Run: `python3 check_kiss.py --verbose`

### Component Tests

**docs/build_docs.py --validate** - Documentation validation
- ✅ Required files exist
- ✅ Config has all sections
- ✅ Documentation matches code
- Runtime: ~1 second
- Run: `python3 docs/build_docs.py --validate`

**manage_libs.py verify** - Library integrity
- ✅ All required libraries present
- ✅ File checksums valid
- ✅ Version compatibility
- Runtime: ~1 second
- Run: `python3 manage_libs.py verify`

### Running All Development Tests

```bash
# Quick test suite (development)
./run-dev-tests.sh
```

## Integration Tests (CI/CD)

### Workflow: verify-features.yml
- Runs on: Push to main/preview, PRs
- Tests:
  - Feature verification
  - Scraper tests
  - Filter tests
- Artifacts: Test results, logs
- Fail fast: Yes

### Workflow: kiss-compliance.yml
- Runs on: Push to main/preview, PRs
- Tests:
  - KISS principle compliance
  - Code complexity
  - File size limits
- Artifacts: Compliance report
- Fail fast: No (informational)

### Workflow: lint.yml
- Runs on: Push to main/preview, PRs
- Tests:
  - JavaScript syntax (ESLint)
  - Python syntax (pylint/flake8)
  - HTML validation
  - CSS validation
- Fail fast: Yes

### Workflow: docs.yml
- Runs on: Push to main, PRs
- Tests:
  - Documentation validation
  - README generation
  - Link checking
- Fail fast: Yes

## Production Tests

### 1. Deployment Validation Tests

**test_production.py** - Post-deployment validation
- ✅ Site is accessible
- ✅ All static assets load (JS, CSS, images)
- ✅ Config files are valid JSON
- ✅ Events data is valid
- ✅ Map initializes correctly
- ✅ Filters work
- ✅ PWA manifest is valid
- Runtime: ~30 seconds
- Run: `python3 test_production.py --url https://krwl.in`

### 2. End-to-End Tests

**test_e2e.py** - User journey testing
- ✅ Page loads successfully
- ✅ Map renders
- ✅ Events appear on map
- ✅ Filters update event display
- ✅ Event details open/close
- ✅ Burger menu actions work
- ✅ Geolocation works
- ✅ Responsive design (mobile/desktop)
- Runtime: ~60 seconds
- Run: `python3 test_e2e.py --url https://krwl.in`

### 3. Performance Tests

**test_performance.py** - Performance benchmarks
- ✅ Page load time < 3s
- ✅ Time to interactive < 5s
- ✅ First contentful paint < 1.5s
- ✅ Map initialization < 2s
- ✅ Filter response time < 100ms
- Runtime: ~30 seconds
- Run: `python3 test_performance.py --url https://krwl.in`

### 4. Accessibility Tests

**test_accessibility.py** - WCAG compliance
- ✅ WCAG 2.1 Level AA compliance
- ✅ Keyboard navigation
- ✅ Screen reader compatibility
- ✅ Color contrast ratios
- ✅ ARIA labels present
- ✅ Focus indicators visible
- Runtime: ~45 seconds
- Run: `python3 test_accessibility.py --url https://krwl.in`

### 5. Security Tests

**test_security.py** - Security validation
- ✅ HTTPS enabled
- ✅ Security headers present
- ✅ No mixed content
- ✅ CSP headers configured
- ✅ XSS protection
- ✅ No exposed secrets
- Runtime: ~20 seconds
- Run: `python3 test_security.py --url https://krwl.in`

### 6. PWA Tests

**test_pwa.py** - Progressive Web App validation
- ✅ Manifest is valid
- ✅ Service worker registers
- ✅ App is installable
- ✅ Icons are accessible
- ✅ Offline mode works
- ✅ Cache strategy effective
- Runtime: ~30 seconds
- Run: `python3 test_pwa.py --url https://krwl.in`

## Continuous Monitoring

### Production Smoke Tests (Every 5 minutes)
```bash
# Lightweight health check
curl -f https://krwl.in/ > /dev/null || alert
```

### Daily Comprehensive Tests
```bash
# Full production test suite
./run-production-tests.sh --url https://krwl.in
```

### Weekly Load Tests
```bash
# Stress testing
python3 test_load.py --url https://krwl.in --users 100
```

## Test Matrix

| Test Type | Frequency | Environment | Duration | Fail Fast |
|-----------|-----------|-------------|----------|-----------|
| Unit Tests | Pre-commit | Local | 5-10s | Yes |
| Component Tests | Pre-commit | Local | 2-5s | Yes |
| Integration Tests | On PR/Push | CI | 30-60s | Yes |
| Deployment Tests | Post-deploy | Staging/Prod | 30s | Yes |
| E2E Tests | Post-deploy | Production | 60s | Yes |
| Performance Tests | Daily | Production | 30s | No |
| Accessibility Tests | Weekly | Production | 45s | No |
| Security Tests | Weekly | Production | 20s | Yes |
| PWA Tests | Post-deploy | Production | 30s | Yes |
| Load Tests | Weekly | Staging | 5-10m | No |

## Test Data

### Development
- Uses `config.dev.json`
- Demo events with current timestamps
- Mock data for scrapers

### Production
- Uses `config.prod.json`
- Real events from live sources
- No mock data

## Running Tests

### Local Development
```bash
# Run all development tests
./run-dev-tests.sh

# Run specific test
python3 test_scraper.py --verbose
python3 test_filters.py --verbose
python3 verify_features.py --verbose
```

### CI/CD Pipeline
Tests run automatically on:
- Pull requests
- Push to main branch
- Push to preview branch
- Manual workflow dispatch

### Production Validation
```bash
# After deployment
./run-production-tests.sh --url https://krwl.in

# Or individual tests
python3 test_production.py --url https://krwl.in
python3 test_e2e.py --url https://krwl.in
python3 test_performance.py --url https://krwl.in
```

## Test Environments

### Local (Development)
- URL: http://localhost:8000
- Config: config.dev.json
- Events: Demo data
- Purpose: Development and debugging

### Preview (Staging)
- URL: https://krwl.in/preview/
- Config: config.dev.json
- Events: Demo + real data
- Purpose: Testing before production

### Production
- URL: https://krwl.in
- Config: config.prod.json
- Events: Real data only
- Purpose: Live application

## Adding New Tests

### Development Test
1. Create test file: `test_<feature>.py`
2. Follow existing test pattern
3. Add to `run-dev-tests.sh`
4. Document in this file

### Production Test
1. Create test file: `test_<feature>.py`
2. Support `--url` parameter
3. Add to `run-production-tests.sh`
4. Add to CI/CD workflow

## Test Coverage Goals

- Unit Tests: > 80% code coverage
- Integration Tests: All critical paths
- E2E Tests: All user journeys
- Production Tests: All deployments

## Alerts and Notifications

### Critical Failures (Immediate)
- Production site down
- Security vulnerabilities
- Data corruption

### Warnings (Daily digest)
- Performance degradation
- Accessibility issues
- KISS violations

### Info (Weekly report)
- Test coverage metrics
- Performance trends
- Feature usage statistics
