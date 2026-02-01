# KRWL> Feature Wishlist - Inspired by krawl.foundation

> **Purpose**: This document outlines a prioritized wishlist of features to port from the krawl.foundation project into krwl.in. Each feature includes effort estimates, implementation notes, test criteria, risks, and acceptance criteria to enable incremental development and review.

## Table of Contents

1. [Overview](#overview)
2. [Phased Roadmap](#phased-roadmap)
3. [Feature Wishlist](#feature-wishlist)
4. [Implementation Guidelines](#implementation-guidelines)
5. [Next Steps](#next-steps)

---

## Overview

The krawl.foundation project provides a comprehensive event aggregation and federation platform with advanced features. This wishlist identifies high-value features that align with krwl.in's goals while maintaining the project's KISS (Keep It Simple, Stupid) principles.

### Design Principles

- **KISS First**: Prioritize simple, maintainable solutions
- **Incremental Adoption**: Features can be implemented independently
- **Optional by Default**: New features should be toggleable via `config.json`
- **Mobile-First**: All features must work on mobile devices
- **Accessibility**: WCAG 2.1 Level AA compliance required

---

## Phased Roadmap

### Phase 1: Quick Wins (High Value, Low Risk)
**Timeline**: 2-4 weeks | **Effort**: 40-60 hours

Focus on features that provide immediate value with minimal complexity:

1. **iCal Export** - Allow users to subscribe to events in their calendar apps
2. **PWA Offline Support** - Service worker for offline event viewing
3. **Map Clustering** - Group nearby markers for better UX
4. **Automated Tests** - CI/CD test suite for scrapers and filters

### Phase 2: Enhanced User Experience (Medium Risk)
**Timeline**: 4-8 weeks | **Effort**: 80-120 hours

Features that improve discoverability and moderation:

5. **Venue Registry** - Centralized venue database with coordinates
6. **Moderation Dashboard** - Web UI for event approval/rejection
7. **OCR Improvements** - Better Facebook flyer text extraction
8. **RSVP Metadata** - Track event attendance interest

### Phase 3: Advanced Features (High Risk, High Reward)
**Timeline**: 8-16 weeks | **Effort**: 160-240 hours

Complex features requiring significant infrastructure:

9. **ActivityPub Federation** - Share events with Fediverse platforms
10. **Advanced Deduplication** - Fuzzy matching for duplicate events
11. **Improved Scrapers** - AI-powered content extraction
12. **Webhook Notifications** - Real-time event updates

---

## Feature Wishlist

### 1. iCal Export (RFC 5545)

**Priority**: 🔥 High | **Effort**: 🔨 Low (8-12 hours) | **Risk**: 🟢 Low

**Description**: Generate RFC 5545-compliant iCalendar (.ics) files for individual events or filtered event lists, allowing users to subscribe to events in their calendar applications (Google Calendar, Apple Calendar, Outlook, etc.).

**Benefits**:
- Users can sync events to personal calendars
- Increases event visibility and attendance
- Standard format widely supported by all calendar apps
- Enables calendar subscription feeds

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/ical_exporter.py` (NEW) - iCal generation logic
  - `src/event_manager.py` - Add `export-ical` CLI command
  - `assets/js/app.js` - Add "Export to Calendar" button in event popups
  - `config.json` - Add `ical.enabled` and `ical.base_url` settings
- **Key Dependencies**: `icalendar` Python library
- **Configuration Example**:
  ```json
  {
    "ical": {
      "enabled": true,
      "base_url": "https://krwl.in",
      "feeds": {
        "all_events": "/calendar/all.ics",
        "per_category": "/calendar/{category}.ics"
      }
    }
  }
  ```

**Test Criteria**:
- [ ] Generate valid .ics file for single event
- [ ] Generate .ics feed for all events
- [ ] Test import in Google Calendar, Apple Calendar, Outlook
- [ ] Verify timezone handling (Europe/Berlin)
- [ ] Test recurrence rules for recurring events
- [ ] Validate RFC 5545 compliance with online validators

**Risks & Mitigations**:
- **Risk**: Timezone handling complexity
  - **Mitigation**: Use `pytz` library, test extensively with Europe/Berlin timezone
- **Risk**: Calendar app incompatibilities
  - **Mitigation**: Test with top 3 calendar apps, follow RFC strictly

**Acceptance Criteria**:
- [ ] Users can click "Add to Calendar" button on event details
- [ ] Generated .ics files validate against RFC 5545
- [ ] Successfully imports into Google Calendar, Apple Calendar, and Outlook
- [ ] Subscription feeds update when events change
- [ ] Feature can be disabled via `config.json`

---

### 2. PWA Offline Support

**Priority**: 🔥 High | **Effort**: 🔨 Medium (16-24 hours) | **Risk**: 🟡 Medium

**Description**: Implement a service worker to cache events, map tiles, and assets for offline viewing. Users can browse previously loaded events without internet connection.

**Benefits**:
- Better mobile experience in low-connectivity areas
- Faster load times with aggressive caching
- True Progressive Web App capabilities
- Improved perceived performance

**Implementation Notes**:
- **Files to Modify**:
  - `assets/js/service-worker.js` (NEW) - Service worker implementation
  - `assets/js/app.js` - Register service worker
  - `public/index.html` - Add service worker registration
  - `assets/json/manifest.json` - Update with offline capabilities
  - `config.json` - Add `pwa.offline_enabled` setting
- **Key Dependencies**: Service Worker API (built into browsers)
- **Caching Strategy**:
  - **Cache First**: Static assets (CSS, JS, SVG icons)
  - **Network First**: Event data (with offline fallback)
  - **Cache Only**: Leaflet map tiles (pre-cache visible area)

**Test Criteria**:
- [ ] Service worker registers successfully
- [ ] Assets cached on first visit
- [ ] App loads offline with cached events
- [ ] Map tiles display offline (previously viewed area)
- [ ] Cache updates when events change
- [ ] Test on Chrome, Firefox, Safari mobile

**Risks & Mitigations**:
- **Risk**: Cache invalidation complexity
  - **Mitigation**: Use versioned cache keys, implement cache cleanup
- **Risk**: Storage quota exceeded
  - **Mitigation**: Limit cached events to 100 most recent, implement LRU eviction
- **Risk**: Service worker debugging difficulty
  - **Mitigation**: Add detailed logging, use Chrome DevTools

**Acceptance Criteria**:
- [ ] App functions offline after initial load
- [ ] Offline indicator shown in UI when network unavailable
- [ ] Cache updates automatically when online
- [ ] Storage usage stays under 50MB
- [ ] Feature can be disabled via `config.json`

---

### 3. Map Marker Clustering

**Priority**: 🔥 High | **Effort**: 🔨 Low (8-12 hours) | **Risk**: 🟢 Low

**Description**: Group nearby event markers into clusters to reduce visual clutter on the map. Clusters show the number of events and expand when clicked.

**Benefits**:
- Cleaner map UI with many events
- Better performance with 100+ markers
- Improved mobile usability (easier tap targets)
- Standard UX pattern for map applications

**Implementation Notes**:
- **Files to Modify**:
  - `assets/js/app.js` - Integrate Leaflet.markercluster plugin
  - `assets/css/style.css` - Style cluster icons
  - `public/index.html` - Add Leaflet.markercluster CDN or bundle
  - `config.json` - Add `map.clustering.enabled` and `map.clustering.max_zoom` settings
- **Key Dependencies**: `Leaflet.markercluster` plugin
- **Configuration Example**:
  ```json
  {
    "map": {
      "clustering": {
        "enabled": true,
        "max_zoom": 15,
        "radius": 80,
        "max_cluster_radius": 80
      }
    }
  }
  ```

**Test Criteria**:
- [ ] Clusters appear with 5+ events in same area
- [ ] Clicking cluster zooms to show individual markers
- [ ] Cluster count updates with filters
- [ ] Performance test with 200+ markers
- [ ] Mobile tap targets are adequate (44x44px minimum)
- [ ] Cluster icons visually distinct from event markers

**Risks & Mitigations**:
- **Risk**: Performance degradation with many markers
  - **Mitigation**: Use Leaflet.markercluster's built-in optimizations
- **Risk**: Confusing UX for users unfamiliar with clustering
  - **Mitigation**: Add tooltip explaining cluster interaction

**Acceptance Criteria**:
- [ ] Clusters form automatically with 5+ nearby events
- [ ] Cluster icons show event count
- [ ] Clicking cluster zooms in or spiderifies markers
- [ ] No performance issues with 500 events
- [ ] Feature can be disabled via `config.json`

---

### 4. Automated CI/CD Test Suite

**Priority**: 🔥 High | **Effort**: 🔨 Medium (20-30 hours) | **Risk**: 🟢 Low

**Description**: Comprehensive automated test suite for scrapers, filters, schema validation, and UI components. Runs on every PR to catch regressions.

**Benefits**:
- Prevent broken deployments
- Faster development with confidence
- Catch regressions before merge
- Document expected behavior

**Implementation Notes**:
- **Files to Modify**:
  - `tests/test_scrapers_comprehensive.py` (NEW) - Test all scraper sources
  - `tests/test_filters_comprehensive.py` (NEW) - Test all filter combinations
  - `tests/test_ui_components.py` (NEW) - Test frontend components
  - `.github/workflows/ci-tests.yml` (NEW) - CI workflow for tests
  - `requirements-dev.txt` - Add `pytest-cov`, `playwright` for UI tests
- **Test Categories**:
  - **Unit Tests**: Scraper logic, filter functions, utils
  - **Integration Tests**: End-to-end scraping workflows
  - **UI Tests**: Playwright tests for map, filters, popups
  - **Schema Tests**: Validate event JSON against schema

**Test Criteria**:
- [ ] All existing scrapers have unit tests
- [ ] All filters have unit tests
- [ ] UI components have Playwright tests
- [ ] Code coverage > 80%
- [ ] Tests run in < 5 minutes
- [ ] Tests run on PR and main branch pushes

**Risks & Mitigations**:
- **Risk**: Slow test execution
  - **Mitigation**: Use pytest-xdist for parallel execution
- **Risk**: Flaky UI tests
  - **Mitigation**: Use explicit waits, retry failed tests once

**Acceptance Criteria**:
- [ ] CI runs automatically on all PRs
- [ ] Test failures block merge
- [ ] Coverage report posted to PR
- [ ] Tests complete in < 5 minutes
- [ ] All critical paths covered

---

### 5. Venue Registry

**Priority**: 🟡 Medium | **Effort**: 🔨 Medium (24-32 hours) | **Risk**: 🟡 Medium

**Description**: Centralized database of venues with names, addresses, coordinates, and metadata. Automatically match scraped events to venues, improving data consistency.

**Benefits**:
- Consistent venue names and locations
- Automatic coordinate lookup for new events
- Venue-specific filtering and search
- Historical venue data tracking

**Implementation Notes**:
- **Files to Modify**:
  - `assets/json/venues.json` (NEW) - Venue database
  - `src/modules/venue_matcher.py` (NEW) - Fuzzy venue matching
  - `src/modules/scraper.py` - Integrate venue matching
  - `assets/js/app.js` - Venue filter UI
  - `config.json` - Add `venues.enabled` and `venues.auto_geocode` settings
- **Venue Schema**:
  ```json
  {
    "id": "venue_kulturhaus_hof",
    "name": "Kulturhaus Hof",
    "aliases": ["Kultur Hof", "KH Hof"],
    "address": "Kulmbacher Str. 5, 95030 Hof",
    "coordinates": {"lat": 50.3167, "lon": 11.9167},
    "type": "theater",
    "capacity": 200,
    "accessibility": true
  }
  ```

**Test Criteria**:
- [ ] Fuzzy matching identifies venues from scraped data
- [ ] New venues can be added via CLI
- [ ] Venue filtering works in UI
- [ ] Geocoding fallback for unknown venues
- [ ] Test with 50+ venue database

**Risks & Mitigations**:
- **Risk**: Venue matching false positives
  - **Mitigation**: Use confidence threshold, manual review for ambiguous matches
- **Risk**: Geocoding API costs
  - **Mitigation**: Cache coordinates, use free tier (Nominatim)

**Acceptance Criteria**:
- [ ] 90%+ venue match rate for scraped events
- [ ] Users can filter events by venue
- [ ] Venue details shown in event popups
- [ ] Feature can be disabled via `config.json`

---

### 6. Web-Based Moderation Dashboard

**Priority**: 🟡 Medium | **Effort**: 🔨 High (40-50 hours) | **Risk**: 🟡 Medium

**Description**: Web UI for reviewing, editing, and approving/rejecting pending events. Replaces CLI-based editorial workflow with accessible interface.

**Benefits**:
- Non-technical editors can moderate events
- Faster editorial workflow
- Better collaboration with multiple editors
- Mobile-friendly moderation

**Implementation Notes**:
- **Files to Modify**:
  - `assets/html/dashboard.html` (NEW) - Moderation UI
  - `src/modules/dashboard_api.py` (NEW) - REST API for moderation
  - `assets/js/dashboard.js` (NEW) - Frontend logic
  - `config.json` - Add `dashboard.enabled`, `dashboard.auth` settings
- **Features**:
  - View pending events in card layout
  - Edit event details inline
  - Approve/reject with one click
  - Bulk operations (approve all from source)
  - Activity log and audit trail

**Test Criteria**:
- [ ] Login/authentication works
- [ ] Pending events displayed correctly
- [ ] Approve/reject actions update events.json
- [ ] Inline editing saves changes
- [ ] Mobile-responsive layout
- [ ] Test with 50+ pending events

**Risks & Mitigations**:
- **Risk**: Security vulnerabilities (XSS, CSRF)
  - **Mitigation**: Input sanitization, CSRF tokens, rate limiting
- **Risk**: Concurrent editing conflicts
  - **Mitigation**: Optimistic locking, conflict detection

**Acceptance Criteria**:
- [ ] Editors can log in with username/password
- [ ] Approve/reject workflow functional
- [ ] Inline editing works on mobile
- [ ] Audit log tracks all actions
- [ ] Feature can be disabled via `config.json`

---

### 7. OCR Improvements (Facebook Flyers)

**Priority**: 🟡 Medium | **Effort**: 🔨 Medium (24-32 hours) | **Risk**: 🟡 Medium

**Description**: Enhance Facebook flyer OCR with better text extraction, date/time parsing, and event metadata extraction. Use AI/ML models for improved accuracy.

**Benefits**:
- Higher success rate for flyer parsing
- Fewer manual corrections needed
- Extract more metadata (prices, genres, organizers)
- Better multilingual support (German/English)

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/smart_scraper/image_analyzer/ocr.py` - Improve OCR pipeline
  - `src/modules/smart_scraper/image_analyzer/analyzer.py` - Add ML models
  - `config.json` - Add `ocr.model` and `ocr.confidence_threshold` settings
- **Improvements**:
  - Pre-process images (contrast, rotation correction)
  - Use PaddleOCR or EasyOCR for better accuracy
  - Named Entity Recognition for dates, times, locations
  - Structured data extraction with regex patterns

**Test Criteria**:
- [ ] OCR accuracy > 85% on test flyer set
- [ ] Date/time extraction accuracy > 90%
- [ ] Test with 50 real Facebook flyers
- [ ] Multilingual support (German/English)
- [ ] Performance < 5 seconds per image

**Risks & Mitigations**:
- **Risk**: ML model dependencies increase complexity
  - **Mitigation**: Make advanced OCR optional, fallback to Tesseract
- **Risk**: Increased processing time
  - **Mitigation**: Parallel processing, configurable timeout

**Acceptance Criteria**:
- [ ] 20%+ improvement in OCR accuracy
- [ ] Automatic date/time extraction works
- [ ] Handles rotated/skewed images
- [ ] Feature gracefully degrades if ML unavailable

---

### 8. RSVP Metadata & Attendance Tracking

**Priority**: 🟡 Medium | **Effort**: 🔨 Medium (20-28 hours) | **Risk**: 🟡 Medium

**Description**: Track user interest in events via lightweight RSVP system. Store attendance counts, display popularity indicators on map.

**Benefits**:
- Users discover popular events
- Event organizers see interest levels
- Community engagement metrics
- Trending events feature

**Implementation Notes**:
- **Files to Modify**:
  - `assets/json/rsvps.json` (NEW) - RSVP database
  - `src/modules/rsvp_tracker.py` (NEW) - RSVP logic
  - `assets/js/app.js` - RSVP button in event popups
  - `config.json` - Add `rsvp.enabled` and `rsvp.storage` settings
- **Privacy Considerations**:
  - No authentication required
  - Client-side storage (localStorage) for user RSVPs
  - Server-side anonymized counts only
  - GDPR-compliant (no personal data stored)

**Test Criteria**:
- [ ] Users can RSVP to events
- [ ] RSVP count displays on event marker
- [ ] Popular events highlighted on map
- [ ] RSVP data persists across sessions
- [ ] Test with 100+ RSVPs per event

**Risks & Mitigations**:
- **Risk**: Fake RSVPs/spam
  - **Mitigation**: Rate limiting, browser fingerprinting, CAPTCHA for high counts
- **Risk**: Privacy concerns
  - **Mitigation**: No PII stored, full transparency in privacy policy

**Acceptance Criteria**:
- [ ] RSVP button appears on event details
- [ ] Count updates in real-time
- [ ] Popular events badge shown on map
- [ ] Feature can be disabled via `config.json`

---

### 9. ActivityPub Federation

**Priority**: 🔴 Low | **Effort**: 🔨 Very High (60-80 hours) | **Risk**: 🔴 High

**Description**: Implement ActivityPub protocol to share events with Fediverse platforms (Mastodon, Pleroma, etc.). Events appear as posts/events on federated timelines.

**Benefits**:
- Reach broader audience via Fediverse
- Decentralized event distribution
- Cross-platform event discovery
- Future-proof against platform lock-in

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/activitypub.py` (NEW) - ActivityPub server
  - `src/modules/webfinger.py` (NEW) - WebFinger discovery
  - `assets/json/actors.json` (NEW) - ActivityPub actors
  - `config.json` - Add `activitypub.enabled` and `activitypub.domain` settings
- **Required Features**:
  - Actor discovery (WebFinger)
  - Inbox/Outbox endpoints
  - HTTP signatures for authentication
  - Create/Update/Delete activities
  - Follow/Unfollow support

**Test Criteria**:
- [ ] Events federate to Mastodon test instance
- [ ] WebFinger discovery works
- [ ] HTTP signatures validate correctly
- [ ] Test with real Mastodon/Pleroma instances
- [ ] Handle follower management

**Risks & Mitigations**:
- **Risk**: Protocol complexity
  - **Mitigation**: Use existing library (ActivityPub.py), incremental implementation
- **Risk**: Moderation challenges
  - **Mitigation**: Start with publish-only, add federation filtering

**Acceptance Criteria**:
- [ ] Events appear on Mastodon timeline
- [ ] Users can follow krwl.in actor
- [ ] Updates propagate to followers
- [ ] Feature can be disabled via `config.json`

---

### 10. Advanced Event Deduplication

**Priority**: 🟡 Medium | **Effort**: 🔨 High (32-40 hours) | **Risk**: 🟡 Medium

**Description**: Fuzzy matching algorithm to detect duplicate events from multiple sources. Automatically merge or flag duplicates for manual review.

**Benefits**:
- Cleaner event list without duplicates
- Aggregate data from multiple sources
- Better data quality
- Reduced manual curation effort

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/deduplicator.py` (NEW) - Fuzzy matching logic
  - `src/modules/scraper.py` - Integrate deduplication
  - `config.json` - Add `deduplication.enabled`, `deduplication.threshold` settings
- **Matching Criteria**:
  - Title similarity (Levenshtein distance)
  - Date/time overlap (within 2 hours)
  - Location proximity (within 500m)
  - Venue name matching
  - Weighted score threshold (> 85% confidence)

**Test Criteria**:
- [ ] Detect exact duplicates (100% match)
- [ ] Detect fuzzy duplicates (>85% similarity)
- [ ] No false positives on test dataset
- [ ] Performance < 1 second for 100 event comparisons
- [ ] Manual review UI for ambiguous matches

**Risks & Mitigations**:
- **Risk**: False positive merges
  - **Mitigation**: Conservative threshold, manual review queue
- **Risk**: Performance with large event sets
  - **Mitigation**: Use blocking/indexing strategies, cache comparisons

**Acceptance Criteria**:
- [ ] 95%+ duplicate detection rate
- [ ] < 5% false positive rate
- [ ] Manual review queue for ambiguous cases
- [ ] Feature can be disabled via `config.json`

---

### 11. AI-Powered Content Extraction

**Priority**: 🔴 Low | **Effort**: 🔨 Very High (80-100 hours) | **Risk**: 🔴 High

**Description**: Use large language models (LLMs) to extract structured event data from unstructured text (social media posts, HTML pages, emails). Automatically populate event fields.

**Benefits**:
- Support more event sources without custom scrapers
- Extract complex event details (multi-day, recurrence)
- Multilingual extraction
- Reduce scraper maintenance burden

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/ai_extractor.py` (NEW) - LLM integration
  - `src/modules/scraper.py` - Add AI extraction fallback
  - `config.json` - Add `ai.enabled`, `ai.model`, `ai.api_key` settings
- **Model Options**:
  - OpenAI GPT-4 (paid API)
  - Local LLM (LLaMA, Mistral via Ollama)
  - Hybrid approach (rules + LLM for ambiguous cases)

**Test Criteria**:
- [ ] Extract events from plain text posts
- [ ] Parse complex date expressions ("next Friday at 8pm")
- [ ] Handle multilingual content (German/English)
- [ ] Test with 100 diverse text samples
- [ ] Accuracy > 80% for structured fields

**Risks & Mitigations**:
- **Risk**: API costs (OpenAI)
  - **Mitigation**: Use local models, implement caching, rate limiting
- **Risk**: Hallucination/inaccurate extraction
  - **Mitigation**: Confidence scores, manual review queue
- **Risk**: Privacy concerns sending data to third-party APIs
  - **Mitigation**: Prefer local models, add opt-in consent

**Acceptance Criteria**:
- [ ] Successfully extracts events from unstructured text
- [ ] Works offline with local models
- [ ] Confidence scores indicate extraction quality
- [ ] Feature can be disabled via `config.json`

---

### 12. Webhook Notifications

**Priority**: 🔴 Low | **Effort**: 🔨 Medium (24-32 hours) | **Risk**: 🟡 Medium

**Description**: Send real-time notifications via webhooks when events are published, updated, or deleted. Integrates with Discord, Slack, Matrix, and custom endpoints.

**Benefits**:
- Real-time event updates for community
- Integration with chat platforms
- Automated social media posting
- Event monitoring and alerting

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/webhook_dispatcher.py` (NEW) - Webhook delivery
  - `src/event_manager.py` - Trigger webhooks on publish/update
  - `config.json` - Add `webhooks.endpoints` array
- **Webhook Payload Example**:
  ```json
  {
    "event": "event.published",
    "timestamp": "2025-01-20T12:00:00Z",
    "data": {
      "id": "event_123",
      "title": "Punk Concert",
      "url": "https://krwl.in/#event_123"
    }
  }
  ```

**Test Criteria**:
- [ ] Webhooks fire on event publish/update/delete
- [ ] Retry logic for failed deliveries
- [ ] Test with Discord, Slack, Matrix
- [ ] Signature verification for security
- [ ] Performance < 500ms per webhook

**Risks & Mitigations**:
- **Risk**: Webhook delivery failures
  - **Mitigation**: Retry queue, exponential backoff
- **Risk**: Webhook spam/abuse
  - **Mitigation**: Rate limiting, signature verification

**Acceptance Criteria**:
- [ ] Events post to Discord channel
- [ ] Failed deliveries retry 3 times
- [ ] Webhook logs track all deliveries
- [ ] Feature can be disabled via `config.json`

---

### 13. Bulk Import/Export

**Priority**: 🟡 Medium | **Effort**: 🔨 Low (12-16 hours) | **Risk**: 🟢 Low

**Description**: Import events from CSV/JSON files and export event database in multiple formats (CSV, JSON, iCal). Useful for backups, migrations, and bulk operations.

**Benefits**:
- Easy event database backup/restore
- Migrate events between instances
- Bulk event creation for organizers
- Data portability

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/importer.py` (NEW) - Import logic
  - `src/modules/exporter.py` (NEW) - Export logic
  - `src/event_manager.py` - Add `import` and `export` CLI commands
  - `config.json` - Add `import.allowed_formats` settings
- **Supported Formats**:
  - **Import**: CSV, JSON, iCal
  - **Export**: CSV, JSON, iCal, RSS

**Test Criteria**:
- [ ] Import CSV with 100 events
- [ ] Export all events to JSON
- [ ] Export filtered events (by category/date)
- [ ] Validate imported event schema
- [ ] Test round-trip import/export

**Risks & Mitigations**:
- **Risk**: Schema validation failures
  - **Mitigation**: Strict validation, clear error messages
- **Risk**: Large file performance
  - **Mitigation**: Streaming import/export, batch processing

**Acceptance Criteria**:
- [ ] Import events via CLI: `python3 src/event_manager.py import events.csv`
- [ ] Export events via CLI: `python3 src/event_manager.py export --format json`
- [ ] Validation errors shown with line numbers
- [ ] Feature handles 1000+ events efficiently

---

### 14. Tag-Based Event Digests

**Priority**: 🔴 Low | **Effort**: 🔨 Medium (16-24 hours) | **Risk**: 🟢 Low

**Description**: Generate email/RSS digests of events grouped by tags (music, theater, sports, etc.). Users subscribe to tags they're interested in.

**Benefits**:
- Personalized event discovery
- Email newsletters for engagement
- RSS feeds for aggregators
- Community topic clustering

**Implementation Notes**:
- **Files to Modify**:
  - `src/modules/digest_generator.py` (NEW) - Digest generation
  - `assets/json/subscriptions.json` (NEW) - User subscriptions
  - `config.json` - Add `digests.enabled`, `digests.schedule` settings
- **Digest Formats**:
  - HTML email (responsive template)
  - Plain text email
  - RSS feed per tag
  - JSON API endpoint

**Test Criteria**:
- [ ] Generate digest with 20 events
- [ ] Group events by category/tag
- [ ] HTML email renders correctly
- [ ] RSS feed validates
- [ ] Test scheduled digest generation

**Risks & Mitigations**:
- **Risk**: Email deliverability
  - **Mitigation**: Use established email service (SendGrid, Mailgun)
- **Risk**: Subscription management complexity
  - **Mitigation**: Simple opt-in/opt-out, no authentication required

**Acceptance Criteria**:
- [ ] Users can subscribe to tag-based digests
- [ ] Digests sent weekly/daily (configurable)
- [ ] Unsubscribe link works
- [ ] Feature can be disabled via `config.json`

---

### 15. Moderation & Audit Logging

**Priority**: 🟡 Medium | **Effort**: 🔨 Medium (20-28 hours) | **Risk**: 🟢 Low

**Description**: Comprehensive audit trail of all event moderation actions (publish, reject, edit). Track who did what, when, and why.

**Benefits**:
- Accountability for editorial decisions
- Debug event data issues
- Compliance with moderation policies
- Rollback support

**Implementation Notes**:
- **Files to Modify**:
  - `assets/json/audit_log.json` (NEW) - Audit log storage
  - `src/modules/audit_logger.py` (NEW) - Logging utilities
  - `src/modules/editor.py` - Integrate audit logging
  - `config.json` - Add `audit.enabled`, `audit.retention_days` settings
- **Log Entry Schema**:
  ```json
  {
    "timestamp": "2025-01-20T12:00:00Z",
    "action": "event.published",
    "user": "editor@example.com",
    "event_id": "event_123",
    "changes": {"status": "pending → published"},
    "reason": "Verified event details"
  }
  ```

**Test Criteria**:
- [ ] All moderation actions logged
- [ ] Logs include user, timestamp, changes
- [ ] Logs searchable by event ID, user, date
- [ ] Logs retained per configuration (default 90 days)
- [ ] Test log rotation and cleanup

**Risks & Mitigations**:
- **Risk**: Log storage growth
  - **Mitigation**: Automatic log rotation, configurable retention
- **Risk**: Performance impact
  - **Mitigation**: Async logging, batched writes

**Acceptance Criteria**:
- [ ] Every publish/reject/edit action logged
- [ ] Audit log viewable via CLI
- [ ] Logs include diff of changes
- [ ] Feature can be disabled via `config.json`

---

## Implementation Guidelines

### General Rules

1. **Feature Toggles**: All new features MUST be configurable via `config.json` with an `enabled` flag
2. **KISS Principle**: Prioritize simple solutions, avoid over-engineering
3. **Testing**: Every feature requires automated tests
4. **Documentation**: Update `features.json` registry for each feature
5. **Accessibility**: Maintain WCAG 2.1 Level AA compliance
6. **Mobile-First**: Test all features on mobile devices

### Configuration Template

```json
{
  "feature_name": {
    "enabled": false,
    "_comment": "Feature description and usage instructions",
    "setting1": "value",
    "setting2": 123
  }
}
```

### File Naming Conventions

- **Backend Modules**: `src/modules/feature_name.py`
- **Test Files**: `tests/test_feature_name.py`
- **Documentation**: `docs/FEATURE_NAME.md`
- **Data Files**: `assets/json/feature_name.json`

### Testing Requirements

Each feature must include:
- [ ] Unit tests for core logic
- [ ] Integration tests for workflows
- [ ] Configuration validation tests
- [ ] Documentation tests (examples work)
- [ ] Performance benchmarks (if applicable)

### Security Checklist

- [ ] Input validation and sanitization
- [ ] XSS prevention (escape user content)
- [ ] CSRF tokens for state-changing operations
- [ ] Rate limiting for API endpoints
- [ ] Authentication/authorization where needed
- [ ] Secrets not committed to repository
- [ ] HTTPS enforced in production

---

## Next Steps

### For Maintainers

1. **Review This Document**: Prioritize features based on community needs
2. **Create GitHub Issues**: One issue per feature using `wishlist-feature-proposal.md` template
3. **Assign Owners**: Identify contributors for each feature
4. **Milestone Planning**: Group features into releases (v1.1, v1.2, etc.)
5. **Incremental Merging**: Accept small PRs implementing individual features

### For Contributors

1. **Pick a Feature**: Choose from Phase 1 (quick wins) to start
2. **Create Issue**: Use `.github/ISSUE_TEMPLATE/wishlist-feature-proposal.md`
3. **Submit PR**: Reference issue, include tests and documentation
4. **Iterate**: Address review feedback, update `features.json`

### Recommended Order of Implementation

Based on dependencies and value:

1. **Start**: iCal Export (standalone, high value)
2. **Then**: Automated Tests (enables faster development)
3. **Then**: Map Clustering (improves UX immediately)
4. **Then**: PWA Offline Support (builds on existing PWA)
5. **Later**: Venue Registry (requires deduplication data)
6. **Later**: Moderation Dashboard (requires auth infrastructure)

---

## References

- **krawl.foundation**: Original project inspiration (link to be added if public)
- **KRWL> Documentation**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Feature Registry**: [features.json](../features.json)
- **Configuration Guide**: [config.json](../config.json)

---

## Document Status

- **Created**: 2025-01-20
- **Last Updated**: 2025-01-20
- **Status**: Draft for review
- **Next Review**: 2025-02-01

## Changelog

- **2025-01-20**: Initial wishlist document created with 15 features
