# Custom Copilot Agents

This document explains the custom GitHub Copilot agents available in this repository and how to use them for structured development work.

## Overview

This repository uses a modular custom agent structure that allows different instruction sets to coexist side-by-side. Each agent provides context-specific guidance based on the task at hand.

## Available Agents

### Default Agent (`../.github/copilot-instructions.md`)

The default agent provides comprehensive project-specific context including:
- Project architecture and technology stack
- Coding conventions and style guidelines
- File structure and module purposes
- Build and test instructions
- Configuration and deployment guidelines

**When to use**: This is always active and provides general context for working with the codebase.

### Planning Agent (`../.github/agents/planning-agent.md`)

The planning agent specializes in creating structured, actionable plans for development work.

**Capabilities**:
- Break down features into phases and tasks
- Create numbered, hierarchical task lists
- Define measurable success criteria
- Organize work sequentially based on dependencies

**When to use**:
- Starting a new feature or major change
- Breaking down a complex bug fix
- Planning a refactoring effort
- Organizing a technical investigation
- Need a structured approach before coding

**Output location**: Plans are saved to `docs/plans/` with naming convention `YYYYMMDD-<description>.md`

### Implementation Agent (`../.github/agents/implementation-agent.md`)

The implementation agent specializes in executing plans and implementing code systematically.

**Capabilities**:
- Follow structured plans step-by-step
- Update plan checkboxes as tasks complete
- Write code following project conventions
- Create detailed implementation notes
- Ensure tests pass before marking tasks complete

**When to use**:
- Executing a plan created by the planning agent
- Need systematic progress tracking
- Want detailed documentation of implementation decisions
- Working on multi-phase implementations

**Output location**: 
- Code goes to `src/` following project structure
- Notes are saved to `docs/notes/` with naming convention `<plan-name>-notes.md`

## How to Invoke Custom Agents

### Method 1: Direct Reference (Recommended)

Reference the agent name in your Copilot conversation:

```
@planning-agent Create a plan for implementing user authentication
```

```
@implementation-agent Follow the plan in docs/plans/20260201-auth.md
```

### Method 2: Explicit Request

Ask Copilot to use the specific agent instructions:

```
I need help planning out feature X. Can you use the planning agent to structure this work?
```

```
I have a plan ready at docs/plans/my-plan.md. Can you help implement it using the implementation agent?
```

## Typical Workflow

### 1. Planning Phase

**Use**: Planning Agent

**Steps**:
1. Discuss the feature or change with Copilot
2. Ask planning agent to create a structured plan
3. Review and refine the plan
4. Plan is saved to `docs/plans/YYYYMMDD-description.md`

**Example conversation**:
```
User: I need to add OAuth authentication to the application
Copilot: Let me help you plan this. @planning-agent

[Planning agent creates structured plan with phases and tasks]
```

### 2. Implementation Phase

**Use**: Implementation Agent

**Steps**:
1. Reference the plan file created in planning phase
2. Implementation agent reads plan and begins execution
3. Agent writes code, runs tests, updates plan checkboxes
4. Agent creates implementation notes as phases complete
5. Notes are saved to `docs/notes/YYYYMMDD-description-notes.md`

**Example conversation**:
```
User: Let's implement the plan at docs/plans/20260201-oauth.md
Copilot: I'll follow the plan systematically. @implementation-agent

[Implementation agent executes tasks, updates plan, creates notes]
```

## File Organization

```
.github/
├── copilot-instructions.md          # Default agent (always active)
└── agents/
    ├── planning-agent.md             # Planning-focused agent
    ├── implementation-agent.md       # Implementation-focused agent
    └── docs_agent.md                 # Documentation-focused agent

docs/
├── plans/                            # Structured plans
│   ├── 20260201-feature-a.md
│   └── 20260215-bugfix-b.md
├── notes/                            # Implementation notes
│   ├── 20260201-feature-a-notes.md
│   └── 20260215-bugfix-b-notes.md
└── COPILOT_AGENTS.md                 # This file

src/                                  # Implementation code
```

## Example Usage Scenarios

### Scenario 1: New Feature Development

**Goal**: Add a new API endpoint

**Workflow**:
1. Ask planning agent to create plan
2. Review plan phases and tasks
3. Ask implementation agent to execute plan
4. Agent writes code, tests, and documentation
5. Agent updates plan and creates notes

### Scenario 2: Bug Fix

**Goal**: Fix authentication issue

**Workflow**:
1. Ask planning agent to structure investigation and fix
2. Plan includes: reproduce bug, identify root cause, implement fix, add tests
3. Ask implementation agent to follow plan
4. Agent investigates, fixes, tests, documents

### Scenario 3: Refactoring

**Goal**: Restructure module organization

**Workflow**:
1. Ask planning agent to create refactoring plan
2. Plan breaks down into: prepare, migrate code, update imports, update tests, cleanup
3. Ask implementation agent to execute carefully
4. Agent refactors incrementally with tests passing at each step

## Best Practices

### For Planning

1. **Be specific about requirements**: Provide clear context and constraints
2. **Review the plan**: Ensure phases and tasks make sense before implementing
3. **Adjust as needed**: Plans can be updated based on new information
4. **Keep plans focused**: One plan per logical unit of work

### For Implementation

1. **Follow the plan**: Don't deviate without updating plan first
2. **Test continuously**: Verify functionality as you go
3. **Document decisions**: Use notes to capture important implementation details
4. **Commit frequently**: Save progress after completing each task
5. **Review before completing phases**: Ensure quality before moving on

### For Documentation

1. **Keep notes current**: Update after completing each phase
2. **Be specific**: Note actual file changes, not just intentions
3. **Capture rationale**: Explain why you chose specific approaches
4. **Link to plan**: Always reference the original plan file

## Integration with Existing Project

These custom agents complement the default copilot-instructions.md file:

- **Default agent**: Always provides project context (architecture, conventions, etc.)
- **Planning agent**: Adds planning-specific guidance when needed
- **Implementation agent**: Adds implementation-specific guidance when executing plans

All agents work together to provide comprehensive, context-aware assistance for different phases of development work.

## Tips

1. **Use planning agent early**: Don't jump straight to coding for complex work
2. **Reference plan files explicitly**: Helps both you and Copilot stay aligned
3. **Update plans as you learn**: Plans are living documents
4. **Review notes files**: They provide valuable history and context
5. **Combine with default agent**: Project conventions still apply during implementation

## Troubleshooting

**Q: How do I know which agent to use?**
A: Use planning agent for structuring work, implementation agent for executing work, default agent handles everything else automatically.

**Q: Can I use multiple agents at once?**
A: The default agent is always active. Explicitly invoke planning or implementation agents as needed for their specific guidance.

**Q: What if I need to change the plan mid-implementation?**
A: Update the plan file first, then continue with implementation agent following the updated plan.

**Q: Do I need to use these agents?**
A: No, they're optional. The default agent provides general guidance. Use custom agents when you want structured planning and implementation workflows.

## Additional Resources

- [Planning Agent Details](../.github/agents/planning-agent.md)
- [Implementation Agent Details](../.github/agents/implementation-agent.md)
- [Default Agent Instructions](../.github/copilot-instructions.md)

---

**Note**: This custom agent structure is designed to enhance your development workflow while maintaining the flexibility to work however you prefer.
