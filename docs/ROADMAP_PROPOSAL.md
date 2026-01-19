# KRWL HOF Feature Roadmap - Implementation Proposal

> **Purpose**: Machine-readable roadmap with milestones, timelines, and ownership assignments for implementing features from the krawl.foundation wishlist.

## Document Overview

This roadmap breaks down the [WISHLIST_KRAWL_FOUNDATION.md](WISHLIST_KRAWL_FOUNDATION.md) into actionable phases with estimated timelines, resource requirements, and dependencies.

---

## Roadmap Summary

| Phase | Focus | Timeline | Features | Total Effort |
|-------|-------|----------|----------|--------------|
| Phase 1 | Quick Wins | 4-6 weeks | 4 features | 56-78 hours |
| Phase 2 | Enhanced UX | 8-12 weeks | 4 features | 96-142 hours |
| Phase 3 | Advanced Features | 16-24 weeks | 7 features | 304-404 hours |
| **Total** | **All Phases** | **6-10 months** | **15 features** | **456-624 hours** |

---

## Phase 1: Quick Wins & Foundation (Q1 2025)

**Goal**: Deliver high-value, low-risk features that improve user experience immediately.

**Timeline**: 4-6 weeks (starting 2025-02-01)

**Prerequisites**: 
- None (all features are standalone)

### Milestones

#### Milestone 1.1: iCal Export (Week 1-2)
- **Effort**: 8-12 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/ical_exporter.py` module
  - [ ] CLI command: `python3 src/event_manager.py export-ical`
  - [ ] "Add to Calendar" button in event popups
  - [ ] Tests: RFC 5545 validation, timezone handling
  - [ ] Documentation: Usage guide, configuration options
- **Dependencies**: `icalendar` Python library
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**: 
  - Users can export single events or entire calendar to .ics format
  - Successfully imports into Google Calendar, Apple Calendar, Outlook

#### Milestone 1.2: Automated CI/CD Tests (Week 2-3)
- **Effort**: 20-30 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `tests/test_scrapers_comprehensive.py` - All scraper tests
  - [ ] `tests/test_filters_comprehensive.py` - All filter tests
  - [ ] `tests/test_ui_components.py` - Playwright UI tests
  - [ ] `.github/workflows/ci-tests.yml` - CI workflow
  - [ ] Code coverage report (target: 80%+)
- **Dependencies**: `pytest-cov`, `playwright`
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**:
  - All tests pass on CI
  - Coverage > 80% for critical modules
  - Tests complete in < 5 minutes

#### Milestone 1.3: Map Marker Clustering (Week 3-4)
- **Effort**: 8-12 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] Integrate Leaflet.markercluster plugin
  - [ ] Cluster styling and configuration
  - [ ] Performance testing with 200+ markers
  - [ ] Mobile usability testing
- **Dependencies**: `Leaflet.markercluster` library
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**:
  - Clusters form automatically with 5+ nearby events
  - No performance degradation with 500 events
  - Mobile tap targets meet accessibility standards

#### Milestone 1.4: PWA Offline Support (Week 4-6)
- **Effort**: 16-24 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `assets/js/service-worker.js` implementation
  - [ ] Cache strategy for assets and events
  - [ ] Offline indicator UI
  - [ ] Cache management and versioning
  - [ ] Browser compatibility tests
- **Dependencies**: Service Worker API (native)
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - App functions offline after initial load
  - Cache updates when online
  - Storage usage < 50MB

### Phase 1 Success Metrics
- [ ] All 4 features deployed to production
- [ ] User feedback collected (survey or GitHub discussions)
- [ ] No critical bugs reported
- [ ] Performance baseline established

---

## Phase 2: Enhanced User Experience (Q2 2025)

**Goal**: Improve discoverability, moderation workflow, and data quality.

**Timeline**: 8-12 weeks (starting 2025-04-01)

**Prerequisites**: 
- Phase 1 automated tests in place
- Performance baseline established

### Milestones

#### Milestone 2.1: Venue Registry (Week 7-10)
- **Effort**: 24-32 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `assets/json/venues.json` database (50+ venues)
  - [ ] `src/modules/venue_matcher.py` fuzzy matching
  - [ ] CLI commands: `add-venue`, `list-venues`
  - [ ] Venue filter in map UI
  - [ ] Geocoding integration (Nominatim)
- **Dependencies**: `fuzzywuzzy` library, geocoding API
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - 90%+ venue match rate for scraped events
  - Users can filter events by venue
  - Automatic geocoding for new venues

#### Milestone 2.2: Moderation Dashboard (Week 10-14)
- **Effort**: 40-50 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `assets/html/dashboard.html` web UI
  - [ ] `src/modules/dashboard_api.py` REST API
  - [ ] Authentication system (simple username/password)
  - [ ] Inline event editing
  - [ ] Activity log and audit trail
  - [ ] Mobile-responsive design
- **Dependencies**: Flask or FastAPI for REST API
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - Non-technical editors can approve/reject events
  - Mobile-friendly moderation workflow
  - Audit log tracks all actions

#### Milestone 2.3: OCR Improvements (Week 14-16)
- **Effort**: 24-32 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] Image pre-processing pipeline
  - [ ] Integration with PaddleOCR or EasyOCR
  - [ ] Named Entity Recognition for dates/locations
  - [ ] Confidence scoring for extractions
  - [ ] Test suite with 50 real flyers
- **Dependencies**: `paddleocr` or `easyocr`, `spacy`
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - 20%+ improvement in OCR accuracy
  - Handles rotated/skewed images
  - Processing time < 5 seconds per image

#### Milestone 2.4: RSVP Metadata (Week 16-18)
- **Effort**: 20-28 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `assets/json/rsvps.json` storage
  - [ ] `src/modules/rsvp_tracker.py` logic
  - [ ] RSVP button in event popups
  - [ ] Popular events indicator on map
  - [ ] Privacy-compliant implementation (no PII)
- **Dependencies**: None (client-side storage)
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - Users can RSVP to events
  - RSVP counts displayed on map
  - Rate limiting prevents spam

### Phase 2 Success Metrics
- [ ] Moderation time reduced by 50%
- [ ] Venue match rate > 90%
- [ ] OCR accuracy > 85%
- [ ] User engagement tracked via RSVPs

---

## Phase 3: Advanced Features (Q3-Q4 2025)

**Goal**: Add sophisticated features for power users and integrations.

**Timeline**: 16-24 weeks (starting 2025-07-01)

**Prerequisites**: 
- Phase 2 venue registry and moderation dashboard operational
- Stable user base for feedback

### Milestones

#### Milestone 3.1: Advanced Deduplication (Week 19-23)
- **Effort**: 32-40 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/deduplicator.py` fuzzy matching
  - [ ] Multi-field similarity scoring
  - [ ] Manual review queue for ambiguous cases
  - [ ] Performance optimization for 1000+ events
  - [ ] Configuration tuning guide
- **Dependencies**: `fuzzywuzzy`, `python-Levenshtein`
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - 95%+ duplicate detection rate
  - < 5% false positive rate
  - Processing time < 1 second per event

#### Milestone 3.2: Bulk Import/Export (Week 23-25)
- **Effort**: 12-16 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/importer.py` - CSV/JSON/iCal import
  - [ ] `src/modules/exporter.py` - Multi-format export
  - [ ] CLI commands: `import`, `export`
  - [ ] Schema validation and error reporting
  - [ ] Performance testing with 1000+ events
- **Dependencies**: `csv`, `json`, `icalendar` libraries
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**:
  - Import/export in CSV, JSON, iCal formats
  - Handles 1000+ events efficiently
  - Clear validation error messages

#### Milestone 3.3: Moderation & Audit Logging (Week 25-27)
- **Effort**: 20-28 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `assets/json/audit_log.json` storage
  - [ ] `src/modules/audit_logger.py` utilities
  - [ ] Integration with editorial workflow
  - [ ] Log search and filtering
  - [ ] Automatic log rotation
- **Dependencies**: None
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**:
  - All moderation actions logged
  - Logs include user, timestamp, changes
  - 90-day retention with rotation

#### Milestone 3.4: Webhook Notifications (Week 27-30)
- **Effort**: 24-32 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/webhook_dispatcher.py`
  - [ ] Retry logic and delivery tracking
  - [ ] Discord/Slack/Matrix integrations
  - [ ] Signature verification
  - [ ] Configuration via `config.json`
- **Dependencies**: `requests` library
- **Risk Level**: 🟡 Medium
- **Acceptance Criteria**:
  - Events post to Discord/Slack
  - Failed deliveries retry 3 times
  - Webhook logs track all deliveries

#### Milestone 3.5: Tag-Based Digests (Week 30-32)
- **Effort**: 16-24 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/digest_generator.py`
  - [ ] HTML email templates
  - [ ] RSS feeds per tag
  - [ ] Subscription management
  - [ ] Scheduled digest generation
- **Dependencies**: Email service (SendGrid, Mailgun)
- **Risk Level**: 🟢 Low
- **Acceptance Criteria**:
  - Users subscribe to tag-based digests
  - Digests sent weekly/daily
  - Unsubscribe works

#### Milestone 3.6: AI-Powered Extraction (Week 32-38) [OPTIONAL]
- **Effort**: 80-100 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/ai_extractor.py` LLM integration
  - [ ] Local model support (Ollama)
  - [ ] Confidence scoring
  - [ ] Manual review queue
  - [ ] Privacy-preserving implementation
- **Dependencies**: OpenAI API or local LLM (Ollama)
- **Risk Level**: 🔴 High
- **Acceptance Criteria**:
  - Extracts events from unstructured text
  - Works offline with local models
  - Accuracy > 80% for structured fields

#### Milestone 3.7: ActivityPub Federation (Week 38-44) [OPTIONAL]
- **Effort**: 60-80 hours
- **Owner**: TBD
- **Deliverables**:
  - [ ] `src/modules/activitypub.py` server
  - [ ] `src/modules/webfinger.py` discovery
  - [ ] Actor management
  - [ ] HTTP signatures
  - [ ] Federation with Mastodon/Pleroma
- **Dependencies**: `activitypub.py` library
- **Risk Level**: 🔴 High
- **Acceptance Criteria**:
  - Events federate to Mastodon
  - Users can follow krwl-hof actor
  - Updates propagate to followers

### Phase 3 Success Metrics
- [ ] Duplicate events reduced by 80%
- [ ] Webhook integrations active (Discord/Slack)
- [ ] Email digests reaching 100+ subscribers
- [ ] Federation with 5+ Fediverse instances (if implemented)

---

## Resource Requirements

### Development Team

| Role | Allocation | Responsibilities |
|------|------------|------------------|
| Backend Developer | 60% time | Python modules, scrapers, API |
| Frontend Developer | 30% time | UI components, PWA, map features |
| DevOps Engineer | 10% time | CI/CD, deployment, monitoring |
| QA/Testing | 20% time | Test writing, manual QA, bug triage |

### Infrastructure

| Component | Provider | Cost Estimate |
|-----------|----------|---------------|
| GitHub Actions | GitHub | Free (< 2000 min/month) |
| Email Service | SendGrid/Mailgun | $10-20/month |
| Geocoding API | Nominatim | Free (self-hosted) |
| Domain/Hosting | GitHub Pages | Free |
| **Total** | | **~$10-20/month** |

### Dependencies to Add

**Python Libraries**:
```
icalendar==5.0.11        # Phase 1.1: iCal export
pytest-cov==4.1.0        # Phase 1.2: Test coverage
playwright==1.40.0       # Phase 1.2: UI tests
fuzzywuzzy==0.18.0       # Phase 2.1: Venue matching
python-Levenshtein==0.21.1  # Phase 3.1: Deduplication
paddleocr==2.7.0         # Phase 2.3: OCR improvements (optional)
```

**JavaScript Libraries**:
```
leaflet.markercluster@1.5.3  # Phase 1.3: Map clustering
```

---

## Risk Management

### High-Risk Items

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| Phase 3 features exceed timeline | High | Medium | Mark AI/Federation as optional, defer to later release |
| Test suite slows down CI | Medium | Medium | Optimize tests, use parallel execution |
| Service worker bugs break PWA | Medium | High | Extensive testing, gradual rollout, kill switch |
| OCR accuracy not improved | Medium | Low | Make advanced OCR optional, fallback to Tesseract |
| Moderation dashboard security issues | Low | High | Security audit, penetration testing before launch |

### Contingency Plans

- **If Phase 1 delayed**: Prioritize iCal export and tests, defer PWA to Phase 2
- **If Phase 2 delayed**: Skip RSVP feature, focus on venue registry and moderation
- **If Phase 3 over budget**: Defer AI extraction and ActivityPub to separate project

---

## Communication Plan

### Stakeholder Updates

- **Weekly**: Progress updates in GitHub Discussions
- **Bi-weekly**: Demo of completed features (video or live)
- **Monthly**: Retrospective and planning session
- **Per-Phase**: Release notes and changelog

### Community Involvement

- **Feature Voting**: Use GitHub Discussions polls to prioritize within phases
- **Beta Testing**: Invite community members to test features before release
- **Documentation**: Maintain user-facing docs at docs.krwl.in (if available)
- **Feedback Loop**: GitHub Issues for bug reports and feature requests

---

## Success Criteria

### Phase 1 Success (End of Q1 2025)
- [ ] 4 features deployed and stable
- [ ] User satisfaction score > 4/5 (survey)
- [ ] Zero critical bugs
- [ ] Test coverage > 80%

### Phase 2 Success (End of Q2 2025)
- [ ] Moderation time reduced by 50%
- [ ] Venue match rate > 90%
- [ ] OCR accuracy improved by 20%
- [ ] 50+ active RSVP users

### Phase 3 Success (End of Q4 2025)
- [ ] All planned features implemented (except optional)
- [ ] Duplicate events < 5% of total
- [ ] Webhook integrations active
- [ ] 100+ email digest subscribers

---

## Maintenance Plan

After initial implementation:

- **Ongoing Support**: 4-8 hours/week for bug fixes and minor features
- **Security Updates**: Monthly dependency updates, quarterly security audits
- **Performance Monitoring**: Track page load times, scraper success rates
- **Community Moderation**: 2-4 hours/week for event approval

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approve Roadmap**: Maintainers approve this proposal
2. **Create GitHub Project**: Set up project board with milestones
3. **Assign Phase 1 Owners**: Identify contributors for first 4 features
4. **Setup Communication**: Create GitHub Discussions category for roadmap updates

### Week 1-2 Actions

1. **Kickoff Meeting**: Phase 1 team alignment
2. **Branch Strategy**: Decide on feature branches vs. monorepo
3. **CI Setup**: Prepare infrastructure for automated tests
4. **Documentation**: Update README with roadmap link

### Monthly Actions

1. **Retrospective**: What worked, what didn't
2. **Reprioritize**: Adjust roadmap based on feedback
3. **Release**: Deploy completed features
4. **Celebrate**: Recognize contributors

---

## Document Metadata

- **Created**: 2025-01-20
- **Last Updated**: 2025-01-20
- **Status**: Draft for review
- **Next Review**: 2025-02-01
- **Owner**: TBD (assign maintainer)

## Changelog

- **2025-01-20**: Initial roadmap proposal created

---

## References

- [Wishlist Document](WISHLIST_KRAWL_FOUNDATION.md) - Detailed feature specifications
- [Feature Registry](../features.json) - Implemented features tracker
- [Configuration Guide](../config.json) - Configuration reference
- [Copilot Instructions](../.github/copilot-instructions.md) - Development guidelines
