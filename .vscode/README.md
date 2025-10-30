# VSCode Configuration for LiteLLM Proxy

This directory contains VSCode workspace configuration files for developing and testing the LiteLLM proxy with LangFuse tracing.

## Files Overview

### `settings.json`
**Purpose**: Workspace settings for Python development and AI assistant integration

**Key Features**:
- Python interpreter configuration (uses `venv/bin/python`)
- Linting and formatting setup (flake8, mypy, black, isort)
- Testing configuration (pytest)
- **Continue extension** models configured to use proxy at `http://localhost:8000/v1`
- **GitHub Copilot** proxy configuration
- Custom headers for LangFuse tracking (`X-User-ID`, `X-Session-ID`)

**AI Models Available**:
- GPT-4 via Proxy
- GPT-4 Turbo via Proxy
- GPT-3.5 via Proxy
- Claude 3 Opus via Proxy
- Claude 3 Sonnet via Proxy
- Claude 3 Haiku via Proxy

### `launch.json`
**Purpose**: Debug configurations for running and debugging the proxy

**Available Debug Configurations**:
1. **Debug Local Proxy** - Run proxy locally with debugger attached (auto-reload enabled)
2. **Debug Local Proxy (Without Reload)** - For stable debugging sessions
3. **Debug Tests** - Debug all pytest tests
4. **Debug Specific Test File** - Debug currently open test file
5. **Debug Test Suite with Coverage** - Run tests with coverage report
6. **Debug Test Requests Script** - Debug the example request script
7. **Attach to Running Proxy** - Attach debugger to already-running proxy
8. **Debug Current Python File** - Quick debug of any Python file

**How to Use**:
1. Set breakpoints in code (click left of line numbers)
2. Open Run & Debug panel (`Ctrl+Shift+D` or `Cmd+Shift+D`)
3. Select configuration from dropdown
4. Press `F5` to start debugging

### `tasks.json`
**Purpose**: Automated tasks for common development operations

**Task Categories**:

**Environment Setup**:
- Create Virtual Environment
- Install Dependencies
- Create .env from Example

**Local Development**:
- Start Proxy (Local) - with auto-reload
- Start Proxy (Local, No Reload)

**Docker Operations**:
- Docker: Start Proxy - `docker compose up -d`
- Docker: Stop Proxy - `docker compose down`
- Docker: Restart Proxy
- Docker: Rebuild and Start
- Docker: View Logs (live tail)
- Docker: Check Status

**Testing**:
- Test: Run All Tests
- Test: Run with Coverage
- Test: Run Current File
- Test: Run Example Requests

**Health Checks**:
- Health: Check Proxy - `curl http://localhost:8000/health`
- Health: List Models
- Health: Check Metrics

**Linting/Formatting**:
- Lint: Run Flake8
- Lint: Run MyPy
- Format: Run Black
- Format: Sort Imports
- Lint: Run All Checks

**Debug/Diagnostics**:
- Debug: Show Environment Variables
- Debug: Test LangFuse Connection
- Debug: Show Recent Errors

**How to Use**:
- Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
- Type "Tasks: Run Task"
- Select the task you want to run

### `extensions.json`
**Purpose**: Recommended VSCode extensions for this project

**Core Extensions**:
- Python language support and linting
- Docker integration
- YAML support
- REST Client for API testing

**AI Coding Assistants**:
- Continue extension (recommended)
- GitHub Copilot

**Additional Tools**:
- GitLens, Markdown tools, Prettier

**How to Install**:
VSCode will prompt you to install recommended extensions when you open the workspace.

### `api-tests.http`
**Purpose**: REST Client test file for interactive API testing

**Features**:
- Pre-configured requests for all common endpoints
- Examples for different models (GPT-4, Claude, etc.)
- Real-world use cases:
  - Code generation
  - Code review
  - Unit test generation
  - Bug fixes
  - Documentation
- Streaming requests
- Error testing scenarios
- LangFuse tracing verification instructions

**How to Use**:
1. Install "REST Client" extension (`humao.rest-client`)
2. Open `api-tests.http`
3. Click "Send Request" above any request
4. View response in split pane

## Quick Start

### 1. First Time Setup

```bash
# Open workspace in VSCode
code /path/to/litellm-proxy-langfuse

# VSCode will prompt to install recommended extensions - click "Install"

# Run setup tasks (Ctrl+Shift+P > Tasks: Run Task)
# - Setup: Create Virtual Environment
# - Setup: Install Dependencies
# - Setup: Create .env from Example

# Edit .env with your API keys
```

### 2. Start Development

**Option A: Docker (Recommended for Testing)**
```bash
# Run task: "Docker: Start Proxy"
# or from terminal:
cd docker && docker compose up -d
```

**Option B: Local Development**
```bash
# Run task: "Start Proxy (Local)"
# or press F5 with "Debug Local Proxy" selected
```

### 3. Test the Proxy

**Using REST Client**:
- Open `.vscode/api-tests.http`
- Click "Send Request" on any request

**Using Python Script**:
```bash
# Run task: "Test: Run Example Requests"
# or from terminal:
python examples/test_requests.py
```

**Using curl**:
```bash
curl http://localhost:8000/health
```

### 4. Configure AI Assistant

**For Continue Extension**:
- Already configured in `settings.json`
- Just start using Continue (`Ctrl+L` or `Cmd+L`)
- All requests will route through proxy → LangFuse

**For GitHub Copilot**:
- Already configured in `settings.json`
- Copilot will attempt to use proxy (limited support)

### 5. Verify LangFuse Tracing

1. Make some requests through the proxy
2. Go to https://cloud.langfuse.com (or your LangFuse host)
3. Navigate to your project
4. View "Traces" - you should see:
   - Request details with metadata
   - Token usage and costs
   - Latency metrics
   - Session tracking

## Debugging Tips

### Debug the Proxy Locally
1. Set breakpoints in `src/proxy/` files
2. Press `F5` (or select "Debug Local Proxy")
3. Make requests - execution will pause at breakpoints
4. Inspect variables, step through code

### Debug Tests
1. Set breakpoints in test files
2. Select "Debug Tests" configuration
3. Press `F5`

### View Docker Logs
Run task: "Docker: View Logs" to see live output

### Enable Debug Logging
Add to `.env`:
```bash
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

## Common Tasks Quick Reference

| Task | Keyboard Shortcut | Command Palette |
|------|------------------|-----------------|
| Run Task | N/A | `Ctrl+Shift+P` → "Tasks: Run Task" |
| Start Debugging | `F5` | Run & Debug panel |
| Open Command Palette | `Ctrl+Shift+P` (Windows/Linux)<br>`Cmd+Shift+P` (Mac) | N/A |
| Open Terminal | `` Ctrl+` `` | View → Terminal |
| Toggle Sidebar | `Ctrl+B` | View → Appearance → Sidebar |

## Environment Variables for Tracking

Set these in requests or in Continue's customHeaders:

```json
{
  "X-User-ID": "your-username",
  "X-Session-ID": "coding-session-id"
}
```

These appear in LangFuse traces for better tracking and analytics.

## Troubleshooting

### "Module not found" errors
- Ensure virtual environment is activated
- Run task: "Setup: Install Dependencies"
- Check Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"

### Proxy not responding
- Check if it's running: `curl http://localhost:8000/health`
- View logs: Run task "Docker: View Logs"
- Verify `.env` file has required variables

### Continue/Copilot not using proxy
- Check `settings.json` has correct `apiBase` URL
- Restart VSCode
- Check extension output: View → Output → Continue/Copilot

### Debugging not working
- Ensure `.env` file exists
- Check Python interpreter is correct
- Try "Debug Local Proxy (Without Reload)"

## Additional Resources

- [USAGE.md](../USAGE.md) - Complete usage guide
- [README.md](../README.md) - Project overview
- [examples/](../examples/) - More code examples

## Notes

- All configurations assume proxy runs on `localhost:8000`
- Proxy must be running for API tests and Continue extension to work
- JSONC format (JSON with Comments) is used for VSCode configs
- Tasks use both `docker-compose` and `docker compose` syntax
