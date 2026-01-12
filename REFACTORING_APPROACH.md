# Complete Refactoring Approach - With Extensive Testing

## Strategy: Incremental Refactoring with Testing

Given the complexity of app.js (3344 lines with tight coupling), I'll use an incremental approach:

### Phase 1: Verify Modules Work Independently ✅
- [x] Created 5 KISS-compliant modules (storage, filters, map, speech-bubbles, utils)
- [x] Each module < 500 lines
- [x] Clear separation of concerns

### Phase 2: Create Integration Layer (Current)
- [ ] Create new app.js that uses modules
- [ ] Ensure all methods delegate properly
- [ ] Maintain backward compatibility

### Phase 3: Testing Before Integration
- [ ] Test modules can load without errors
- [ ] Test modules interact correctly
- [ ] Verify no circular dependencies
- [ ] Check browser compatibility

### Phase 4: Build Integration
- [ ] Update site_generator.py to inline all modules
- [ ] Build test version of index.html
- [ ] Verify build succeeds

### Phase 5: Functional Testing
- [ ] Test map loads and displays
- [ ] Test markers appear correctly
- [ ] Test filters work (time, distance, category)
- [ ] Test bookmarks persist
- [ ] Test speech bubbles show
- [ ] Test dashboard opens/closes
- [ ] Test keyboard shortcuts
- [ ] Test event detail popups
- [ ] Test weather display
- [ ] Test pending event notifications

### Phase 6: KISS Compliance Check
- [ ] Run kiss_checker on all files
- [ ] Verify all files < 500 lines
- [ ] Document any remaining issues

### Phase 7: Final PR
- [ ] Update features.json
- [ ] Update documentation
- [ ] Create comprehensive PR description
- [ ] Include before/after metrics

## Testing Plan

### Unit Tests (Module Level)
```bash
# Test each module independently
node -e "const EventStorage = require('./assets/js/storage.js'); console.log('Storage OK')"
node -e "const EventFilter = require('./assets/js/filters.js'); console.log('Filters OK')"
# etc for each module
```

### Integration Tests (Build Level)
```bash
# Build production HTML with refactored code
python3 src/event_manager.py build production

# Check for JavaScript errors
grep -i "error\|undefined\|null" public/index.html || echo "No obvious errors"

# Verify file size
ls -lh public/index.html
```

### Manual Browser Tests
1. Start local server: `cd public && python3 -m http.server 8000`
2. Open http://localhost:8000
3. Test each feature systematically
4. Check browser console for errors

### Screenshot Verification
```bash
# Use existing screenshot generation
python3 scripts/generate_screenshots.py
# Verify screenshots look correct
```

## Risk Mitigation

### High Risk Areas
1. **setupEventListeners()** - 800 lines of tightly coupled UI logic
2. **Custom Dropdown Class** - Inline class definition
3. **Focus Trap Logic** - Complex keyboard handling
4. **Event Delegation** - Many event handlers

### Mitigation Strategy
- Keep backup of original app.js
- Test each feature individually
- Use git branches for safety
- Document any breaking changes

## Success Criteria

### Must Have ✅
- [ ] All modules load without errors
- [ ] Map displays correctly
- [ ] Markers show on map
- [ ] Filters work
- [ ] No console errors
- [ ] KISS checker passes

### Should Have ✅
- [ ] Bookmarks persist
- [ ] Speech bubbles appear
- [ ] Dashboard works
- [ ] Keyboard shortcuts work

### Nice to Have
- [ ] Performance improvements
- [ ] Better error handling
- [ ] Cleaner code structure

## Rollback Plan

If integration fails:
1. Restore original app.js from backup
2. Keep modules as separate files (for future use)
3. Document lessons learned
4. Plan gradual migration strategy
