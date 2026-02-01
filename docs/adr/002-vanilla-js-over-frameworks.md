# ADR-002: Vanilla JS Over Frameworks

**Status**: Accepted  
**Date**: 2026-02-01  
**Deciders**: @feileberlin, Development Team  
**Tags**: frontend, architecture, kiss-principle

## Context

When starting the KRWL HOF project, we needed to choose a frontend technology stack. The modern JavaScript ecosystem offers many frameworks:

- **React**: Component-based, large ecosystem, JSX syntax
- **Vue**: Progressive framework, gentle learning curve
- **Svelte**: Compile-time framework, minimal runtime
- **Angular**: Full-featured, TypeScript-first
- **Vanilla JS**: No framework, browser native APIs only

Our project requirements:
- Single-page app with interactive map (Leaflet.js)
- Event filtering and search
- Minimal bundle size for fast loading
- Easy maintenance by small team
- Progressive enhancement for accessibility

## Decision

We chose **Vanilla JavaScript (ES6+)** with no frontend framework.

**Implementation Approach:**
- Use modern JavaScript features (async/await, modules, classes)
- Leverage Web APIs directly (fetch, localStorage, DOM manipulation)
- Structure code with modular classes (`MapManager`, `FilterManager`, etc.)
- Use Leaflet.js as the only external dependency for maps
- Keep HTML templates simple and server-rendered when possible

**Files Following This Decision:**
- `assets/js/app.js` - Main application orchestrator
- `assets/js/map.js` - Map management
- `assets/js/filters.js` - Event filtering logic
- `assets/js/storage.js` - LocalStorage abstraction
- `assets/js/utils.js` - Utility functions

## Consequences

### Positive

- **Small Bundle Size**: No framework overhead (~40KB total JS vs 100KB+ for frameworks)
- **Fast Loading**: Less JavaScript to parse and execute
- **No Build Step Required**: Can edit and test directly in browser
- **Direct Control**: Full understanding of what code does, no "magic"
- **Long-Term Stability**: No framework version upgrades or breaking changes
- **Easy Debugging**: Standard browser DevTools, no special extensions needed
- **Low Barrier to Entry**: Any JavaScript developer can contribute without learning framework-specific patterns

### Negative

- **More Boilerplate**: Manual DOM manipulation, no declarative templates
- **No Virtual DOM**: Inefficient re-rendering if not careful
- **State Management**: Must implement manually or keep simple
- **Code Organization**: Requires discipline to maintain structure
- **Tooling**: No framework-specific linting, hot reloading out of the box

### Neutral

- **Performance**: Fast for our use case (moderate complexity, not thousands of components)
- **Team Familiarity**: All JavaScript developers know vanilla JS
- **Community Support**: Smaller community than React/Vue, but Web APIs are well-documented

## Alternatives Considered

### 1. React
**Rejected**: Overkill for our needs, large bundle size, JSX build step required, frequent breaking changes

### 2. Vue
**Rejected**: Still adds 30KB+ to bundle, template syntax to learn, not necessary for our simple component needs

### 3. Svelte
**Considered Seriously**: Compile-time approach appealing, but still adds build complexity and was newer/less proven at decision time

### 4. Alpine.js
**Rejected**: Lightweight option, but still adds dependency and abstraction layer we don't need

## KISS Principle Alignment

This decision strongly aligns with our **KISS (Keep It Simple, Stupid)** principle:

```
"Always prefer simple solutions. 
Avoid frameworks when vanilla solutions suffice."
```

Vanilla JS is the simplest possible approach that meets our needs. Adding a framework would be over-engineering.

## Validation

Our KISS checker validates this decision:
```bash
python3 src/modules/kiss_checker.py --verbose
```

Checks for:
- No React/Vue/Angular imports in JS files
- Direct DOM manipulation patterns
- Modular class structure without framework overhead

## Related Decisions

- **ADR-001**: Fallback List When Map Fails - Easier to implement without framework constraints
- **ADR-003**: Single Entry Point - Backend follows same KISS philosophy
- **features.json**: All frontend features implemented without frameworks
- **.github/copilot-instructions.md**: "No frameworks: Vanilla JS only"

## When to Revisit

Consider adding a framework if:
- Application grows to 50+ interactive components
- Complex state management becomes unmanageable
- Team grows and needs stricter code organization
- Performance degrades significantly (100ms+ render times)

**As of 2026-02-01**: None of these conditions are met. Vanilla JS remains appropriate.

## References

- [You Might Not Need a Framework](https://www.freecodecamp.org/news/you-might-not-need-a-framework/)
- [The Simplest Web App](https://javascriptweekly.com/link/126706/web)
- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)
- Project: `src/modules/kiss_checker.py` - Enforces this decision
