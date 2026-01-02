# Development Environment Setup

This guide covers setting up your development environment for KRWL HOF, including GitHub Copilot integration, VS Code configuration, devcontainer, and Model Context Protocol (MCP) servers.

## Quick Start

### Option 1: VS Code (Recommended)

1. **Install VS Code** - [Download here](https://code.visualstudio.com/)

2. **Clone and open the project**
   ```bash
   git clone https://github.com/feileberlin/krwl-hof.git
   cd krwl-hof
   code .
   ```

3. **Install recommended extensions**
   - VS Code will prompt you to install recommended extensions
   - Click "Install All" or install individually from the Extensions panel

4. **Setup Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Download frontend libraries**
   ```bash
   ./scripts/download-libs.sh
   ```

### Option 2: Devcontainer (Docker-based)

1. **Prerequisites**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Install [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in container**
   - Clone the repository
   - Open the folder in VS Code
   - Press `F1` and select "Remote-Containers: Reopen in Container"
   - Wait for the container to build (first time only)

3. **Start developing**
   - All dependencies are automatically installed
   - Extensions are pre-configured
   - Port 8000 is forwarded for the dev server

## Configuration Files

### VS Code Configuration

The project includes several VS Code configuration files:

- **`.vscode/settings.json`** - Workspace settings including linting, formatting, and file protection
- **`.vscode/extensions.json`** - Recommended extensions for the project
- **`.vscode/tasks.json`** - Predefined tasks for common operations
- **`.vscode/launch.json`** - Debug configurations
- **`.vscode/krwl-hof.code-workspace`** - VS Code workspace file

### Devcontainer

- **`.devcontainer/devcontainer.json`** - Docker-based development container configuration

### MCP Servers

- **`.github/mcp/servers.json`** - Model Context Protocol server configuration
- **`.github/mcp/README.md`** - MCP setup documentation

### GitHub Copilot

- **`.github/copilot-instructions.md`** - Project-specific Copilot instructions

## GitHub Copilot Integration

GitHub Copilot is configured to understand the project structure and conventions through:

1. **Custom Instructions** (`.github/copilot-instructions.md`)
   - Project architecture overview
   - Coding guidelines and KISS principles
   - Auto-generated file warnings
   - Testing requirements

2. **MCP Server Integration**
   - Repository context (issues, PRs, workflows)
   - Filesystem access for project files
   - Persistent memory across sessions

### Using GitHub Copilot

With the configuration in place, Copilot will:
- Understand project-specific conventions
- Warn about editing auto-generated files
- Follow KISS principles in suggestions
- Know how to run tests and builds
- Provide context-aware completions

## Model Context Protocol (MCP)

MCP provides contextual information to AI assistants. The project includes three MCP servers:

### 1. GitHub Server
Provides repository information including issues, PRs, and workflows.

**Setup:**
```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

### 2. Filesystem Server
Enables AI assistants to access project files.

**No setup required** - automatically configured.

### 3. Memory Server
Maintains persistent context across development sessions.

**No setup required** - automatically configured.

### Context Files

The following files are automatically provided as context:
- `.github/copilot-instructions.md` - Project guidelines
- `features.json` - Feature registry
- `README.md` - Project overview
- `TESTING.md` - Testing guide
- Configuration files

## Available Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

### Setup Tasks
- **Install Python Dependencies** - `pip install -r requirements.txt`
- **Download Frontend Libraries** - Download Leaflet.js and dependencies

### Testing Tasks
- **All Tests** - Run complete test suite
- **Feature Verification** - Verify features.json registry
- **Scraper Tests** - Test event scrapers
- **KISS Compliance** - Check KISS principle compliance
- **Event Schema Validation** - Validate event data schema

### Build Tasks
- **Generate Static Site** - Generate HTML/CSS/JS from templates
- **Generate Documentation** - Regenerate README.md

### Development Tasks
- **Start Local Development Server** - Launch server on port 8000
- **Launch Event Manager TUI** - Start interactive TUI

## Debug Configurations

Available debug configurations (press `F5`):

- **Python: Current File** - Debug the currently open Python file
- **Python: TUI Main** - Debug the event manager TUI
- **Python: Generate Static Site** - Debug static site generation
- **Python: Test Scraper** - Debug scraper tests
- **Python: Verify Features** - Debug feature verification
- **Debug: Current Test File** - Debug the current test file

## Auto-Generated File Protection

The following file is protected from accidental edits:
- `static/index.html` (auto-generated, everything inlined)

The following files are SOURCE files (edit directly):
- `static/js/app.js` (application logic)
- `static/css/style.css` (application styles)

**To modify the generated index.html:**
1. Edit source files: `static/js/app.js` or `static/css/style.css`
2. Run: `python3 src/main.py generate`
3. Commit both source and generated files

**Architecture:**
- New simplified approach using `src/modules/cdn_inliner.py` (~300 lines)
- Replaces old `src/modules/generator.py` (2185 lines - deleted!)
- Single index.html with all resources inlined (~66KB)
- Events auto-updated via `update_events_in_html()` on approve/publish

## Testing the Setup

Run the development environment test:

```bash
python3 tests/test_dev_environment.py
```

This validates:
- All configuration files exist
- JSON files are properly formatted
- Feature registry includes new features
- Documentation is in place

## Recommended Extensions

The project recommends these VS Code extensions:

### Essential
- **GitHub Copilot** - AI pair programmer
- **GitHub Copilot Chat** - Chat interface for Copilot
- **Python** - Python language support
- **Pylance** - Python language server

### Development Tools
- **Black Formatter** - Python code formatting
- **ESLint** - JavaScript linting
- **YAML** - YAML language support

### Git Tools
- **Git Graph** - Visualize Git history
- **GitLens** - Enhanced Git capabilities

### Documentation
- **Markdown All in One** - Markdown editing support

## Troubleshooting

### Extensions Not Installing

1. Check internet connectivity
2. Manually install from Extensions marketplace (`Ctrl+Shift+X`)
3. Restart VS Code

### Devcontainer Issues

1. Ensure Docker Desktop is running
2. Check Docker has sufficient resources (4GB+ RAM recommended)
3. Rebuild container: `F1` → "Remote-Containers: Rebuild Container"

### Python Virtual Environment Issues

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### MCP Servers Not Working

1. Verify Node.js is installed: `node --version`
2. For GitHub server, set `GITHUB_TOKEN` environment variable
3. Ensure you're using an MCP-compatible AI tool

## Next Steps

1. **Read the Copilot instructions**: `.github/copilot-instructions.md`
2. **Run the tests**: `python3 verify_features.py --verbose`
3. **Start the dev server**: Run "Server: Start Local Development Server" task
4. **Open the app**: http://localhost:8000
5. **Try the TUI**: `python3 src/main.py`

## Additional Resources

- [GitHub Copilot Instructions](.github/copilot-instructions.md)
- [MCP Configuration](.github/mcp/README.md)
- [Development Environment Documentation](.github/DEV_ENVIRONMENT.md)
- [Testing Guide](../TESTING.md)
- [Feature Registry](.github/FEATURE_REGISTRY.md)

## Contributing

When adding new development environment features:

1. Update configuration files as needed
2. Add entry to `features.json`
3. Document in `.github/DEV_ENVIRONMENT.md`
4. Update this guide if setup steps change
5. Run `python3 tests/test_dev_environment.py` to verify
