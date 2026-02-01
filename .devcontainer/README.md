# Development Container Configuration Guide

This directory contains the devcontainer configuration that creates a consistent, containerized development environment for the KRWL> project.

## What is a Dev Container?

A development container (devcontainer) is a Docker-based environment that:
- Runs your development environment in an isolated container
- Ensures every developer has identical tools, dependencies, and settings
- Works locally with VS Code or in the cloud with GitHub Codespaces
- Eliminates "works on my machine" problems

## devcontainer.json

**Purpose**: Defines the containerized development environment specification.

### Container Base Configuration

**What it does**: Specifies which Docker image to use as the foundation.

**How to configure**:
```json
"name": "KRWL> Development Container",
"image": "mcr.microsoft.com/devcontainers/python:3.11"
```
- `name`: Friendly name shown in VS Code status bar
- `image`: Base Docker image (Python 3.11 from Microsoft's official devcontainers)

**To use a different Python version**:
```json
"image": "mcr.microsoft.com/devcontainers/python:3.12"
```

**Why this configuration**: Python 3.11 provides the best balance of performance and compatibility for this project.

### Installing Additional Tools (Features)

**What it does**: Automatically installs common development tools in the container.

**How to configure**:
```json
"features": {
  "ghcr.io/devcontainers/features/git:1": {},
  "ghcr.io/devcontainers/features/github-cli:1": {}
}
```
- Each feature is a pre-packaged tool installer
- `{}` means use default configuration
- Features are cached for faster container rebuilds

**To add Node.js**:
```json
"features": {
  "ghcr.io/devcontainers/features/git:1": {},
  "ghcr.io/devcontainers/features/github-cli:1": {},
  "ghcr.io/devcontainers/features/node:1": {
    "version": "18"
  }
}
```

**Browse available features**: https://containers.dev/features

### VS Code Extensions in Container

**What it does**: Auto-installs VS Code extensions inside the container so they're available to all developers.

**How to configure**:
```json
"extensions": [
  "github.copilot",
  "ms-python.python"
]
```
- Extensions install automatically when container is created
- No manual installation needed by developers

**To add a new extension**:
1. Find extension ID from VS Code marketplace (e.g., "publisher.extension-name")
2. Add to the array
3. Rebuild container: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"

**Why these extensions**: Matches the project's tech stack (Python, JavaScript, Markdown) and team workflow (Git, Copilot).

### Container-Specific VS Code Settings

**What it does**: Applies VS Code settings only when working inside the container.

**How to configure**:
```json
"settings": {
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```
- These settings override workspace and user settings when in container
- Use absolute paths (container filesystem)

**Why different from workspace settings**: Container has different file paths than host machine.

### Automatic Setup Commands

**What it does**: Runs commands automatically after container is created, setting up the development environment.

**How to configure**:
```json
"postCreateCommand": "pip install -r requirements.txt && ./scripts/download-libs.sh"
```
- Runs once after container is first created
- Use `&&` to chain multiple commands
- Failures will show in terminal

**To add database setup**:
```json
"postCreateCommand": "pip install -r requirements.txt && ./scripts/download-libs.sh && python setup_db.py"
```

**Other lifecycle hooks**:
- `onCreateCommand`: Runs once when container is first created (not on rebuilds)
- `updateContentCommand`: Runs when container configuration changes
- `postStartCommand`: Runs every time container starts

**Why this configuration**: Automates the "setup" section of the README so new developers can start immediately.

### Port Forwarding

**What it does**: Makes ports from inside the container accessible on your host machine.

**How to configure**:
```json
"forwardPorts": [8000],
"portsAttributes": {
  "8000": {
    "label": "Local Dev Server",
    "onAutoForward": "notify"
  }
}
```
- `forwardPorts`: Array of ports to forward
- `label`: Friendly name in VS Code Ports panel
- `onAutoForward`: What to do when port is detected ("notify", "openBrowser", "openPreview", "silent", or "ignore")

**To add multiple ports**:
```json
"forwardPorts": [8000, 5000, 3000],
"portsAttributes": {
  "8000": {
    "label": "Web Server",
    "onAutoForward": "openBrowser"
  },
  "5000": {
    "label": "API Server",
    "onAutoForward": "notify"
  }
}
```

**Why this configuration**: Automatically exposes the local development server (port 8000) so you can test the site in your host browser.

### Security: Container User

**What it does**: Runs VS Code and your processes as a non-root user inside the container.

**How to configure**:
```json
"remoteUser": "vscode"
```
- `vscode` is a pre-configured non-root user with sudo access
- Improves security (principle of least privilege)

**To run as root** (not recommended):
```json
"remoteUser": "root"
```

**Why this configuration**: Running as non-root is a security best practice and prevents accidental system-wide changes.

### Synchronizing Workspace Files

**What it does**: Mounts directories from your host machine into the container so they stay in sync.

**How to configure**:
```json
"mounts": [
  "source=${localWorkspaceFolder}/.vscode,target=/workspaces/${localWorkspaceFolderBasename}/.vscode,type=bind,consistency=cached"
]
```
- `source`: Path on host machine (supports variables)
- `target`: Path in container
- `type=bind`: Sync changes bidirectionally
- `consistency=cached`: Optimize for read performance

**Variables available**:
- `${localWorkspaceFolder}`: Workspace root on host
- `${localWorkspaceFolderBasename}`: Workspace directory name
- `${containerWorkspaceFolder}`: Workspace root in container

**To mount SSH keys for Git**:
```json
"mounts": [
  "source=${localWorkspaceFolder}/.vscode,target=/workspaces/${localWorkspaceFolderBasename}/.vscode,type=bind,consistency=cached",
  "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,readonly"
]
```

## Using Dev Containers

### First Time Setup (Local VS Code)

1. **Install prerequisites**:
   - Install Docker Desktop
   - Install VS Code extension: "Dev Containers" (ms-vscode-remote.remote-containers)

2. **Open in container**:
   - Open the project folder in VS Code
   - Click "Reopen in Container" notification, OR
   - Press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

3. **Wait for container build**:
   - First time takes 5-10 minutes (downloads image, installs dependencies)
   - Subsequent opens take ~30 seconds (container is cached)

4. **Start developing**:
   - Terminal opens inside container
   - All commands run in containerized environment
   - Files sync automatically between host and container

### Using GitHub Codespaces (Cloud)

1. **Create codespace**:
   - Go to repository on GitHub
   - Click "Code" → "Codespaces" → "Create codespace on main"

2. **Wait for environment**:
   - GitHub provisions a cloud VM
   - Container builds automatically
   - VS Code opens in browser

3. **Start developing**:
   - Identical environment to local dev container
   - No local setup required
   - Accessible from any device

### Rebuilding the Container

**When to rebuild**:
- After changing `devcontainer.json`
- After adding new features or extensions
- When dependencies are out of sync

**How to rebuild**:
- `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
- Or `Ctrl+Shift+P` → "Dev Containers: Rebuild Without Cache" (clean rebuild)

## Customizing for Your Needs

### Adding Project-Specific Tools

**Example: Add PostgreSQL**:
```json
"features": {
  "ghcr.io/devcontainers/features/git:1": {},
  "ghcr.io/devcontainers/features/github-cli:1": {},
  "ghcr.io/devcontainers-contrib/features/postgres-asdf:1": {}
}
```

### Running Commands on Container Start

**Example: Start a background service**:
```json
"postStartCommand": "python manage.py runserver 0.0.0.0:8000 &"
```

### Environment Variables

**Add to pass configuration to container**:
```json
"containerEnv": {
  "DEBUG": "true",
  "DATABASE_URL": "sqlite:///db.sqlite3"
}
```

## Troubleshooting

### Container won't build

**Error: "Docker is not running"**
- Start Docker Desktop
- Wait for it to fully start (whale icon in system tray)

**Error: "Failed to build image"**
- Check Docker has enough disk space
- Try: `Ctrl+Shift+P` → "Dev Containers: Rebuild Without Cache"

### Extensions not working

**Problem**: Extension installed but not available
- Extensions must be in `extensions` array to work in container
- Rebuild container after adding extensions

### Port forwarding not working

**Problem**: Can't access `localhost:8000`
- Check Ports panel: `Ctrl+Shift+P` → "Ports: Focus on Ports View"
- Verify process is listening on `0.0.0.0`, not `127.0.0.1`
- Try manually forwarding: Right-click port → "Forward Port"

### Slow performance

**Problem**: File operations are slow
- On Windows/Mac, this is normal (Docker VM overhead)
- Consider using WSL2 on Windows for better performance
- Use `consistency=cached` in mounts (already configured)

### Changes not persisting

**Problem**: Installed packages disappear after restart
- Install in `postCreateCommand`, not manually in terminal
- Or use a volume mount for persistent data

## Benefits of Using Dev Containers

✅ **Onboarding**: New developers productive in minutes, not hours
✅ **Consistency**: Same environment for everyone (dev/prod parity)
✅ **Isolation**: Project dependencies don't conflict with other projects
✅ **Portability**: Work from any machine with Docker and VS Code
✅ **Collaboration**: Share exact environment configuration via Git
✅ **Cloud-ready**: Seamlessly switch between local and GitHub Codespaces
