# Model Context Protocol (MCP) Configuration

This directory contains the MCP server configuration for the KRWL HOF project.

## What is MCP?

Model Context Protocol (MCP) is a standardized protocol for providing contextual information to AI assistants like GitHub Copilot. It enables AI tools to access relevant project information, repository structure, and development context to provide more accurate and project-aware suggestions.

## Configuration Files

### `servers.json`

The main MCP configuration file that defines:

1. **GitHub Server**: Provides repository context including issues, PRs, and workflows
2. **Filesystem Server**: Enables filesystem access within the workspace
3. **Memory Server**: Maintains persistent context across development sessions

### Context Files

The following files are automatically provided as context to AI assistants:

- `.github/copilot-instructions.md` - Project-specific Copilot instructions
- `.github/agents/` - Custom Copilot agents for specialized tasks
  - `docs_agent.md` - Documentation expert agent
  - `planning-agent.md` - Planning agent for structured plans
  - `implementation-agent.md` - Implementation agent for executing plans
- `.github/COPILOT_SETUP.md` - Complete guide for setting up Copilot
- `.github/CODEOWNERS` - Code ownership and review assignments
- `.github/pull_request_template.md` - PR template with best practices checklist
- `features.json` - Feature registry documenting all implemented features
- `README.md` - Project overview and quick start
- `TESTING.md` - Testing guidelines and procedures
- `config.dev.json` / `config.prod.json` - Configuration schemas
- `static/.copilot-protected` - Auto-generated file warnings

## Setup

### Prerequisites

- Node.js and npm installed (for MCP servers)
- GitHub personal access token (for GitHub MCP server)

### Installation

The MCP servers are automatically installed when needed via `npx`. No manual installation required.

### Environment Variables

For the GitHub MCP server to work, set:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

MCP servers are automatically used by compatible AI tools when they detect the `servers.json` configuration. Supported tools include:

- GitHub Copilot (with MCP support)
- Claude Desktop
- Other MCP-compatible AI assistants

## Customization

To add more context files, edit `servers.json` and add paths to the `contextFiles` array:

```json
{
  "settings": {
    "contextFiles": [
      ".github/copilot-instructions.md",
      "your-custom-file.md"
    ]
  }
}
```

## Excluded Patterns

The following patterns are excluded from context to reduce noise:

- `__pycache__` directories
- `venv` directories
- `node_modules` directories
- `.git` directories
- `static/libs` (external libraries)

## Security

- Never commit GitHub tokens or secrets to the repository
- Use environment variables for sensitive credentials
- The `.gitignore` ensures tokens are not accidentally committed

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
