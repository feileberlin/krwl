# Module Structure

The `src/modules/` directory is organized into logical categories for better code organization and maintainability.

## Directory Structure

```
src/modules/
├── core/           # Core event management functionality
├── ui/             # User interface modules (TUI)
├── cli/            # Command-line interface modules
├── build/          # Site generation and build tools
├── utils/          # Utility and helper functions
├── quality/        # Testing and quality assurance
└── utils.py        # Common utilities (backward compatibility)
```

## Categories

### 1. `core/` - Core Event Management
Event data handling, scraping, and editorial workflows.

**Modules:**
- `editor.py` - Event editorial workflow and review
- `scraper.py` - Event scraping from various sources
- `models.py` - Data validation models (Pydantic)
- `exceptions.py` - Custom exception classes

**Usage:**
```python
from modules.core.editor import EventEditor
from modules.core.scraper import EventScraper
from modules.core.models import validate_event_data
from modules.core.exceptions import SourceUnavailableError
```

---

### 2. `ui/` - User Interfaces
Interactive TUI (Text User Interface) components.

**Modules:**
- `batch_selector.py` - Interactive checkbox-based event selection
- `config_editor.py` - Configuration editor TUI
- `scraper_config_tui.py` - Scraper setup and configuration TUI

**Usage:**
```python
from modules.ui.batch_selector import BatchSelector
from modules.ui.config_editor import ConfigEditor
```

**When to use:**
- Building interactive command-line tools
- User-facing configuration interfaces
- Visual selection/editing workflows

---

### 3. `cli/` - Command-Line Tools
CLI commands and runners for various operations.

**Modules:**
- `scraper_cli.py` - Scraper management CLI commands
- `workflow_launcher.py` - GitHub Actions workflow launcher
- `test_runner.py` - Test execution runner
- `utility_runner.py` - Utility command runner
- `docs_runner.py` - Documentation command runner

**Usage:**
```python
from modules.cli.test_runner import TestRunner
from modules.cli.workflow_launcher import WorkflowLauncher
```

**When to use:**
- Implementing new CLI commands
- Adding workflow automation
- Running test suites programmatically

---

### 4. `build/` - Site Generation
HTML generation, linting, and build processes.

**Modules:**
- `site_generator.py` - HTML site generation engine
- `linter.py` - Code and content linting
- `lucide_markers.py` - Icon and marker management

**Usage:**
```python
from modules.build.site_generator import SiteGenerator
from modules.build.linter import Linter
```

**When to use:**
- Generating static site output
- Linting HTML/CSS/JS
- Managing visual assets

---

### 5. `utils/` - Utilities
Helper functions and shared utilities.

**Modules:**
- `batch_operations.py` - Batch processing and wildcard expansion
- `scheduler.py` - Schedule configuration helpers
- `logging_config.py` - Logging setup and configuration

**Root level:**
- `utils.py` - Common utilities (kept at root for backward compatibility)

**Usage:**
```python
from modules.utils.batch_operations import expand_wildcards, process_in_batches
from modules.utils.scheduler import ScheduleConfig
from modules.utils.logging_config import configure_for_cli
from modules.utils import load_config  # Root level
```

**When to use:**
- Need general helper functions
- Batch processing operations
- Schedule/timing utilities
- Logging configuration

---

### 6. `quality/` - Testing & Quality Assurance
Testing, verification, and code quality tools.

**Modules:**
- `feature_verifier.py` - Feature registry validation
- `filter_tester.py` - Event filter testing
- `kiss_checker.py` - KISS compliance checker
- `docs_generator.py` - Documentation generation

**Usage:**
```python
from modules.quality.feature_verifier import FeatureVerifier
from modules.quality.kiss_checker import KISSChecker
```

**When to use:**
- Running quality checks
- Validating features
- Generating documentation
- Ensuring code compliance

---

## Migration Guide

### Old Import Style
```python
from modules.editor import EventEditor
from modules.scraper import EventScraper
from modules.batch_selector import BatchSelector
```

### New Import Style
```python
from modules.core.editor import EventEditor
from modules.core.scraper import EventScraper
from modules.ui.batch_selector import BatchSelector
```

### Relative Imports (within modules)
```python
# Old
from .editor import EventEditor

# New (from same category)
from .editor import EventEditor  # If in core/

# New (from different category)
from ..core.editor import EventEditor  # If in ui/ or cli/
```

---

## Benefits

### 1. **Organization**
- Clear separation of concerns
- Easy to find related code
- Logical grouping by purpose

### 2. **Maintainability**
- Smaller directories
- Easier to navigate
- Clear responsibility per directory

### 3. **Scalability**
- Add new modules to appropriate category
- Categories can grow independently
- No "flat directory" clutter

### 4. **Discoverability**
- New developers know where to look
- Category names are self-documenting
- Related modules are co-located

### 5. **Testing**
- Test files can mirror structure
- Category-level test suites
- Isolated testing of components

---

## Adding New Modules

### Step 1: Choose Category
Determine which category fits your module's purpose:
- **Core**: Event data handling
- **UI**: Interactive interfaces
- **CLI**: Command-line tools
- **Build**: Site generation
- **Utils**: Helper functions
- **Quality**: Testing/verification

### Step 2: Create Module
Place your module in the appropriate subdirectory:
```bash
# Example: New export tool (CLI category)
touch src/modules/cli/export_tool.py
```

### Step 3: Update __init__.py (optional)
For commonly used exports, add to category's `__init__.py`:
```python
# src/modules/cli/__init__.py
from .export_tool import ExportTool
```

### Step 4: Import and Use
```python
from modules.cli.export_tool import ExportTool
```

---

## Best Practices

### 1. **Keep Categories Focused**
- Don't mix responsibilities
- If a module doesn't fit, create a new category
- Avoid "miscellaneous" categories

### 2. **Limit Category Size**
- Maximum ~10 modules per category
- If growing too large, consider sub-categories
- Split if modules serve different sub-purposes

### 3. **Document Category Purpose**
- Update category `__init__.py` docstrings
- Explain when to use the category
- Give examples

### 4. **Maintain Consistency**
- Follow naming conventions
- Use similar patterns within category
- Keep module sizes similar

### 5. **Avoid Circular Dependencies**
- Core modules shouldn't import from UI/CLI
- Utils should be dependency-free
- Build can import from core/utils only

---

## Category Dependencies

Allowed import directions (to avoid circular dependencies):

```
quality  →  core, utils, build, ui, cli
cli      →  core, utils, build, ui
ui       →  core, utils
build    →  core, utils
core     →  utils
utils    →  (no internal dependencies)
```

**Rule**: Higher-level categories can import from lower-level ones, not vice versa.

---

## Statistics

**Module Count by Category:**
- Core: 4 modules (event management)
- UI: 3 modules (interactive interfaces)
- CLI: 5 modules (command-line tools)
- Build: 3 modules (site generation)
- Utils: 3 modules + 1 root (utilities)
- Quality: 4 modules (testing/verification)

**Total**: 23 organized modules across 6 categories

---

## Future Structure

As the project grows, consider these sub-categories:

### core/
- `core/scraping/` - Scraper implementations
- `core/editorial/` - Editorial workflow
- `core/validation/` - Data validation

### ui/
- `ui/tui/` - Text user interfaces
- `ui/dialogs/` - Reusable dialog components

### utils/
- `utils/io/` - File I/O helpers
- `utils/time/` - Time/date utilities
- `utils/text/` - String processing

---

## Questions?

- Check this README for category descriptions
- Review existing modules for patterns
- Ask maintainers if unsure where to place code

**Remember**: Good organization makes code easier to maintain! 🎯
