# Workflow Re-run Capabilities - Analysis & Solutions

## Current Requirement
**Request:** "maybe run buttons after each entry not just in the end?"

## GitHub Actions Limitations

### What GitHub Actions Provides
1. **Re-run all jobs** - Entire workflow from scratch
2. **Re-run failed jobs** - Only jobs that failed (if any)
3. **Workflow dispatch** - Manual trigger with inputs

### What GitHub Actions Does NOT Support
❌ **Re-run individual jobs** - This is a platform limitation
❌ **Run buttons after each job** - Not available in GitHub UI
❌ **Skip to specific job** - Cannot jump to middle of workflow

## Why Individual Job Re-run Isn't Possible

GitHub Actions workflows are designed as **immutable execution graphs**:
- Jobs inherit context from previous jobs via `needs` dependencies
- Artifacts and outputs flow between jobs
- Environment state is established at workflow start
- Re-running a single job would break the dependency chain

## Practical Alternatives (What We CAN Do)

### Option 1: Task-Specific Workflow Dispatch (RECOMMENDED)
**What:** Add granular manual trigger options for each major task

**Current Implementation:**
```yaml
workflow_dispatch:
  inputs:
    task:
      type: choice
      options:
        - 'scrape-only'
        - 'scrape-and-deploy'
        - 'force-deploy'
        - 'update-events'
        - 'review-pending'
        - 'scrape-weather'
        # etc...
```

**Enhancement:** Make task options more granular and clear

**Benefits:**
- ✅ Run specific workflows on demand
- ✅ Skip unnecessary steps
- ✅ Fast iteration for specific tasks
- ✅ Available in GitHub UI via "Run workflow" button

**Implementation:**
```yaml
workflow_dispatch:
  inputs:
    task:
      description: '🎯 Select specific task to run'
      type: choice
      options:
        # Data Collection
        - '📅 Scrape events only'
        - '🌤️ Scrape weather only'
        - '📥 Scrape all data'
        
        # Build & Deploy
        - '🔨 Rebuild HTML only'
        - '⚡ Fast event update'
        - '🚀 Full rebuild + deploy'
        - '🚀 Force deploy (skip scraping)'
        
        # Editorial
        - '✏️ Review pending events'
        - '📝 Publish specific event'
        - '🗄️ Archive old events'
        
        # Telegram
        - '📸 Process flyer'
        - '💬 Process contact form'
        - '🔐 Process PIN publish'
        
        # Diagnostics
        - '📊 Show config info'
        - '🧪 Run tests only'
        - '✅ Validate config only'
```

### Option 2: Separate Focused Workflows
**What:** Split large workflow into multiple smaller workflows

**Example Structure:**
```
.github/workflows/
  ├── deploy.yml              (Deployment only - fast re-run)
  ├── scraping.yml            (Data collection only)
  ├── editorial.yml           (Review & publish only)
  ├── telegram-integration.yml (Telegram handlers only)
  ├── ci-tests.yml            (CI/CD checks only)
  └── maintenance.yml         (Scheduled maintenance)
```

**Benefits:**
- ✅ Each workflow can be re-run independently
- ✅ Faster execution (smaller workflows)
- ✅ Clearer purpose per workflow
- ✅ Easier to find specific task in UI

**Trade-offs:**
- ⚠️ More files to maintain
- ⚠️ Harder to see full picture
- ⚠️ May need workflow_run triggers

### Option 3: Conditional Job Execution via Inputs
**What:** Add granular skip/run controls for each job category

**Implementation:**
```yaml
workflow_dispatch:
  inputs:
    run_scraping:
      description: '📥 Run scraping jobs?'
      type: boolean
      default: true
    
    run_build:
      description: '🔨 Run build jobs?'
      type: boolean
      default: true
    
    run_deployment:
      description: '🚀 Run deployment?'
      type: boolean
      default: true
    
    run_editorial:
      description: '✏️ Run editorial jobs?'
      type: boolean
      default: false
    
    run_telegram:
      description: '📱 Run Telegram jobs?'
      type: boolean
      default: false

jobs:
  scrape-events:
    if: ${{ github.event.inputs.run_scraping != 'false' }}
    # ...
  
  full-rebuild:
    if: ${{ github.event.inputs.run_build != 'false' }}
    # ...
  
  deploy:
    if: ${{ github.event.inputs.run_deployment != 'false' }}
    # ...
```

**Benefits:**
- ✅ Fine-grained control over what runs
- ✅ Single workflow file
- ✅ Easy to mix and match tasks

### Option 4: GitHub CLI for Custom Re-runs
**What:** Create helper scripts for common scenarios

**Example Script:**
```bash
#!/bin/bash
# quick-deploy.sh - Deploy without scraping

gh workflow run website-maintenance.yml \
  -f task='force-deploy' \
  -R feileberlin/krwl-hof
```

**Benefits:**
- ✅ Command-line control
- ✅ Can be automated/scripted
- ✅ Fast for power users

## Recommended Solution

### Combination Approach (Best of All Worlds)

**Phase 1: Enhance Current Workflow Dispatch (IMMEDIATE)**
1. Add more granular task options with clear descriptions
2. Group tasks by category in dropdown
3. Add quick-access options for common scenarios

**Phase 2: Add Conditional Controls (SHORT TERM)**
1. Add boolean inputs to skip major job categories
2. Keep single workflow file
3. Allow flexible job combinations

**Phase 3: Split Large Workflows (LONG TERM - if needed)**
1. Only if workflow becomes too complex
2. Create focused workflows for specific purposes
3. Keep main workflow as orchestrator

## Implementation for Current Workflow

Let me enhance the `workflow_dispatch` inputs to be more granular:

```yaml
workflow_dispatch:
  inputs:
    # ═══════════════════════════════════════════════════════════════
    # 🎯 QUICK ACTIONS - Common scenarios
    # ═══════════════════════════════════════════════════════════════
    task:
      description: '🎯 Quick Action - Select what to do'
      type: choice
      options:
        # Most Common
        - '🚀 Deploy now (full rebuild)'
        - '📥 Scrape + Deploy (everything)'
        - '⚡ Update events only (fast)'
        
        # Data Collection
        - '📅 Scrape events only'
        - '🌤️ Scrape weather only'
        
        # Editorial
        - '✏️ Review pending events'
        
        # Diagnostics
        - '📊 Show configuration'
        - '🧪 Run tests & validation'
    
    # ═══════════════════════════════════════════════════════════════
    # 🎛️ ADVANCED CONTROLS - Fine-tune execution
    # ═══════════════════════════════════════════════════════════════
    skip_scraping:
      description: '⏭️ Skip scraping jobs?'
      type: boolean
      default: false
    
    skip_build:
      description: '⏭️ Skip build/generation?'
      type: boolean
      default: false
    
    skip_deployment:
      description: '⏭️ Skip deployment?'
      type: boolean
      default: false
```

## Summary

**Direct Answer:** GitHub Actions doesn't support individual job re-run buttons.

**Best Alternative:** Enhanced workflow_dispatch with granular task options that simulate "run this specific thing" functionality.

**Next Step:** Implement enhanced workflow dispatch inputs for better control?

---

**Status:** Analysis complete, awaiting decision on implementation approach
