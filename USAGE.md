# LiteLLM Proxy with LangFuse - Usage Guide

Complete guide for using the LiteLLM proxy with LangFuse tracing in VSCode for development and testing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [VSCode Setup](#vscode-setup)
- [Testing the Proxy](#testing-the-proxy)
- [LangFuse Tracing](#langfuse-tracing)
- [Development Workflow](#development-workflow)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** installed (for containerized deployment)
- **Python 3.11+** (for local development)
- **VSCode** with recommended extensions:
  - Python (ms-python.python)
  - Docker (ms-azuretools.vscode-docker)
  - REST Client (humao.rest-client) - optional but helpful
  - Continue or GitHub Copilot - for AI-assisted coding
- **LangFuse Account**: Sign up at [https://cloud.langfuse.com](https://cloud.langfuse.com) or use self-hosted instance
- **LLM Provider API Keys**: At least one (OpenAI, Anthropic, Azure, AWS, etc.)

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/MueMike/litellm-proxy-langfuse.git
cd litellm-proxy-langfuse

# Create environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and add your credentials:

```bash
# LangFuse - Required for tracing
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true

# At least one LLM provider
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Start the Docker Container

```bash
cd docker
docker-compose up -d
```

Verify the container is running:

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f litellm-proxy

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "litellm-proxy-langfuse"
}
```

### 4. Test the API

Run the API test script to verify everything is working:

```bash
# Option 1: Shell script (Linux/Mac)
./test_api.sh

# Option 2: Python script (Windows/Linux/Mac)
python test_api.py
```

The test script will verify:
- Container is running
- Health check endpoint
- Models endpoint
- Chat completion endpoint
- Metrics endpoint (optional)

Expected output:
```
✓ All tests passed! API is working correctly.
```

### 5. Verify LangFuse Tracing

Make a test request:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "X-Session-ID: test-session" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

Then check your LangFuse dashboard - you should see a new trace with:
- User ID: `test-user`
- Session ID: `test-session`
- Model usage and costs

## VSCode Setup

### Initial Configuration

1. **Open the project in VSCode**:
   ```bash
   code /path/to/litellm-proxy-langfuse
   ```

2. **Install recommended Python extensions**:
   - Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
   - Type "Python: Select Interpreter"
   - Choose Python 3.11 or higher

3. **Create VSCode workspace configuration**:

The repository includes pre-configured VSCode settings in `.vscode/` directory:

- **`.vscode/settings.json`** - Editor settings and Python configuration
- **`.vscode/launch.json`** - Debug configurations
- **`.vscode/tasks.json`** - Build and test tasks

### Using Pre-configured Settings

Copy the example VSCode configuration:

```bash
# The .vscode directory is included in the repository
# If it doesn't exist, create it:
mkdir -p .vscode

# Copy example configurations (if needed)
cp examples/vscode_settings.json .vscode/settings.json
```

### IDE Integration with Proxy

The proxy acts as an OpenAI-compatible endpoint. Configure your AI coding assistant:

#### Option 1: Continue Extension

1. Install [Continue extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue)

2. Update `.vscode/settings.json`:

```json
{
  "continue.telemetryEnabled": false,
  "continue.models": [
    {
      "title": "GPT-4 via Proxy",
      "provider": "openai",
      "model": "gpt-4",
      "apiBase": "http://localhost:8000/v1",
      "apiKey": "dummy-key"
    },
    {
      "title": "Claude 3 Opus via Proxy",
      "provider": "anthropic",
      "model": "claude-3-opus-20240229",
      "apiBase": "http://localhost:8000/v1",
      "apiKey": "dummy-key"
    }
  ],
  "continue.customHeaders": {
    "X-User-ID": "your-username",
    "X-Session-ID": "vscode-session"
  }
}
```

3. Start using Continue with `Ctrl+L` or `Cmd+L`

#### Option 2: GitHub Copilot

Configure Copilot to use the proxy (add to `.vscode/settings.json`):

```json
{
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",
    "debug.testOverrideProxyUrl": "http://localhost:8000",
    "debug.overrideProxyUrl": "http://localhost:8000"
  }
}
```

**Note**: GitHub Copilot proxy configuration may have limited support. Continue extension is recommended for full proxy support.

## Testing the Proxy

### Quick API Test (Recommended)

After starting the Docker container, run the API test script to verify everything is working:

```bash
cd docker

# Option 1: Shell script (Linux/Mac)
./test_api.sh

# Option 2: Python script (cross-platform)
python test_api.py
```

This will test:
- ✓ Container status
- ✓ Health endpoint
- ✓ Models endpoint
- ✓ Chat completion (basic test)
- ✓ Metrics endpoint

Exit code 0 means all tests passed.

### Comprehensive Test Suite

For more thorough testing including LangFuse tracing validation:

```bash
# From repository root
python examples/test_requests.py
```

This comprehensive suite will:
- ✓ Check health endpoint
- ✓ List available models
- ✓ Test chat completions with various models
- ✓ Test C++ unit test generation with metadata
- ✓ Verify trace headers and LangFuse integration

### Manual Testing with curl

#### Test Health:
```bash
curl http://localhost:8000/health
```

#### List Models:
```bash
curl http://localhost:8000/v1/models
```

#### Chat Completion:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: developer-1" \
  -H "X-Session-ID: coding-session-001" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "You are a helpful coding assistant."},
      {"role": "user", "content": "Write a Python function to calculate fibonacci numbers."}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "metadata": {
      "task_type": "code_generation",
      "language": "python"
    }
  }'
```

#### Test with Streaming:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: developer-1" \
  -H "X-Session-ID: stream-session" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Count from 1 to 5"}],
    "stream": true
  }'
```

### Using VSCode REST Client

Install the REST Client extension and create `test.http`:

```http
### Health Check
GET http://localhost:8000/health

### List Models
GET http://localhost:8000/v1/models

### Chat Completion
POST http://localhost:8000/v1/chat/completions
Content-Type: application/json
X-User-ID: vscode-user
X-Session-ID: rest-client-session

{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Explain async/await in Python"}
  ],
  "max_tokens": 500,
  "metadata": {
    "task_type": "explanation",
    "language": "python"
  }
}
```

Click "Send Request" above each request to execute.

## LangFuse Tracing

### Accessing the Dashboard

1. **Open LangFuse**:
   - Cloud: [https://cloud.langfuse.com](https://cloud.langfuse.com)
   - Self-hosted: Your configured `LANGFUSE_HOST`

2. **Navigate to your project**

3. **View Traces**:
   - Go to "Traces" in the sidebar
   - You'll see all requests made through the proxy

### Understanding Traces

Each trace includes:

- **Trace ID**: Unique identifier (also in response header `X-Trace-ID`)
- **Timestamp**: When the request was made
- **User ID**: From `X-User-ID` header
- **Session ID**: From `X-Session-ID` header
- **Model**: Which LLM was used
- **Input/Output**: Full request and response
- **Tokens**: Prompt tokens, completion tokens, total
- **Cost**: Calculated based on model pricing
- **Latency**: Request duration
- **Metadata**: Custom tags from request (task_type, language, etc.)

### Filtering and Analysis

Use LangFuse features to:

- **Filter by Session**: Track entire coding sessions
- **Filter by User**: See activity per developer
- **Filter by Metadata**: Find specific task types (e.g., "code_generation")
- **Cost Analysis**: View spending by model, user, or time period
- **Performance**: Analyze latency patterns

### Custom Metadata for Better Tracking

Add meaningful metadata to requests:

```python
{
  "model": "gpt-4",
  "messages": [...],
  "metadata": {
    "task_type": "code_review",      # Type of task
    "language": "typescript",         # Programming language
    "feature": "api-endpoint",        # Feature being worked on
    "file": "src/api/users.ts",      # File path
    "project": "backend-service",     # Project name
    "environment": "development"      # Environment
  }
}
```

This metadata appears as tags in LangFuse, making traces easier to find and analyze.

## Development Workflow

### Local Development (Without Docker)

For active development, run the proxy locally:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:
   ```bash
   python -m uvicorn src.proxy.server:create_app --factory --host 0.0.0.0 --port 8000 --reload
   ```

   The `--reload` flag enables auto-restart on code changes.

4. **Test your changes**:
   ```bash
   curl http://localhost:8000/health
   ```

### Using VSCode Tasks

Run predefined tasks from Command Palette (`Ctrl+Shift+P` > "Tasks: Run Task"):

- **Start Proxy (Local)**: Run proxy in development mode
- **Start Proxy (Docker)**: Start Docker container
- **Stop Proxy (Docker)**: Stop Docker container
- **Run Tests**: Execute test suite
- **View Logs (Docker)**: Tail Docker logs
- **Restart Proxy (Docker)**: Restart container

### Development with Docker

For development with Docker but live code updates:

```bash
# Start with volume mount for live code updates
docker-compose -f docker/docker-compose.dev.yml up
```

## Debugging

### Debugging in VSCode

The `.vscode/launch.json` includes debug configurations:

#### 1. Debug Local Proxy

1. Set breakpoints in code (click left margin in editor)
2. Press `F5` or go to Run & Debug (`Ctrl+Shift+D`)
3. Select "Debug Local Proxy"
4. Click Start Debugging (or press `F5`)

The debugger will:
- Start the proxy with debugger attached
- Stop at breakpoints
- Allow variable inspection and step-through

#### 2. Debug Tests

1. Set breakpoints in test files
2. Select "Debug Tests" configuration
3. Press `F5`

#### 3. Attach to Running Proxy

If proxy is already running:
1. Select "Attach to Proxy" configuration
2. Press `F5`

### Debug Mode

Enable detailed logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

Restart the proxy to see detailed logs:
- Request/response bodies
- LangFuse API calls
- Model selection logic
- Error stack traces

### Common Debugging Scenarios

#### Trace Not Appearing in LangFuse

1. **Check LangFuse credentials**:
   ```bash
   # View container logs
   docker-compose logs litellm-proxy | grep -i langfuse
   ```

2. **Verify LANGFUSE_ENABLED**:
   ```bash
   docker-compose exec litellm-proxy env | grep LANGFUSE
   ```

3. **Test LangFuse connection**:
   ```python
   from langfuse import Langfuse
   client = Langfuse(
       public_key="your-pk",
       secret_key="your-sk",
       host="https://cloud.langfuse.com"
   )
   client.auth_check()  # Should return True
   ```

#### High Latency

1. **Check Prometheus metrics**:
   ```bash
   curl http://localhost:9090/metrics | grep litellm_request_duration
   ```

2. **Enable timing logs**:
   Set `LOG_LEVEL=DEBUG` and check logs for slow operations

3. **Test provider directly**:
   Rule out proxy overhead by testing LLM provider API directly

## Common Tasks

### Updating Model Configuration

Edit `config/config.yaml` to add/remove models:

```yaml
model_list:
  # Add new model
  - model_name: gpt-4-turbo-preview
    litellm_params:
      model: gpt-4-turbo-preview
      api_key: ${OPENAI_API_KEY}
```

Restart the proxy:
```bash
docker-compose restart litellm-proxy
```

### Viewing Metrics

Access Prometheus metrics:

```bash
# All metrics
curl http://localhost:9090/metrics

# Request duration
curl http://localhost:9090/metrics | grep litellm_request_duration

# Total requests
curl http://localhost:9090/metrics | grep litellm_requests_total

# Token usage
curl http://localhost:9090/metrics | grep litellm_tokens_used

# Costs
curl http://localhost:9090/metrics | grep litellm_cost_usd
```

### Checking Logs

```bash
# Docker logs (live tail)
docker-compose logs -f litellm-proxy

# Docker logs (last 100 lines)
docker-compose logs --tail=100 litellm-proxy

# Search logs for errors
docker-compose logs litellm-proxy | grep -i error

# Filter by timestamp
docker-compose logs --since=10m litellm-proxy
```

### Stopping and Restarting

```bash
# Stop container
docker-compose down

# Start container
docker-compose up -d

# Restart container (reload config)
docker-compose restart litellm-proxy

# Rebuild and restart (after code changes)
docker-compose up -d --build
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_proxy.py

# Run with coverage
pytest --cov=src tests/

# Verbose output
pytest -v tests/
```

## Troubleshooting

### Issue: Container Won't Start

**Symptoms**: `docker-compose up` fails or container exits immediately

**Solutions**:

1. Check logs:
   ```bash
   docker-compose logs litellm-proxy
   ```

2. Verify `.env` file exists:
   ```bash
   ls -la .env
   ```

3. Check required environment variables:
   ```bash
   # Must have LangFuse credentials
   grep LANGFUSE .env
   # Must have at least one provider
   grep -E "OPENAI|ANTHROPIC|AZURE" .env
   ```

4. Check port availability:
   ```bash
   # Ports 8000 and 9090 must be free
   lsof -i :8000
   lsof -i :9090
   ```

### Issue: Requests Failing with 401/403

**Symptoms**: API calls return authentication errors

**Solutions**:

1. **If `REQUIRE_AUTH=true`**, include master key:
   ```bash
   curl -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
        http://localhost:8000/v1/models
   ```

2. **Check provider API keys**:
   ```bash
   docker-compose exec litellm-proxy env | grep -E "OPENAI|ANTHROPIC"
   ```

3. **Test provider API directly**:
   ```bash
   curl https://api.openai.com/v1/models \
        -H "Authorization: Bearer ${OPENAI_API_KEY}"
   ```

### Issue: LangFuse Not Receiving Traces

**Symptoms**: Requests work but no traces in LangFuse dashboard

**Solutions**:

1. **Verify LangFuse is enabled**:
   ```bash
   grep LANGFUSE_ENABLED .env  # Should be 'true'
   ```

2. **Check LangFuse credentials**:
   - Public key starts with `pk-lf-`
   - Secret key starts with `sk-lf-`
   - Host URL is correct (no trailing slash)

3. **Test LangFuse connection**:
   ```bash
   docker-compose logs litellm-proxy | grep -i langfuse
   ```

4. **Check network access**:
   ```bash
   # If using cloud.langfuse.com
   curl https://cloud.langfuse.com
   ```

5. **Look for error messages**:
   ```bash
   docker-compose logs litellm-proxy | grep -i "error\|failed"
   ```

### Issue: Slow Response Times

**Symptoms**: Requests take longer than expected

**Solutions**:

1. **Check metrics**:
   ```bash
   curl http://localhost:9090/metrics | grep duration
   ```

2. **Test without proxy**:
   Call LLM provider directly to isolate proxy overhead

3. **Review LangFuse overhead**:
   - LangFuse tracing adds minimal overhead (~10-50ms)
   - Most latency is from LLM provider

4. **Check network**:
   ```bash
   # Test connectivity to provider
   time curl -I https://api.openai.com
   ```

5. **Increase timeouts** (if timing out):
   ```bash
   # In .env
   REQUEST_TIMEOUT=900  # 15 minutes
   ```

### Issue: Model Not Found

**Symptoms**: Error "Model XYZ not found"

**Solutions**:

1. **List available models**:
   ```bash
   curl http://localhost:8000/v1/models
   ```

2. **Check model configuration**:
   ```bash
   cat config/config.yaml | grep model_name
   ```

3. **Verify provider API key** for that model's provider

4. **Add model to config**:
   Edit `config/config.yaml` and add model, then restart

### Issue: VSCode Extension Not Using Proxy

**Symptoms**: Continue or Copilot not routing through proxy

**Solutions**:

1. **Verify settings.json**:
   - Check `apiBase` is `http://localhost:8000/v1`
   - No trailing slash on apiBase

2. **Restart VSCode**:
   - Close and reopen VSCode
   - Reload window: `Ctrl+Shift+P` > "Reload Window"

3. **Check proxy is running**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Check extension logs**:
   - Continue: View > Output > Continue
   - Copilot: View > Output > GitHub Copilot

### Getting Help

If you continue to have issues:

1. **Enable debug logging**:
   ```bash
   LOG_LEVEL=DEBUG
   DEBUG_MODE=true
   ```

2. **Collect diagnostics**:
   ```bash
   # Container status
   docker-compose ps
   
   # Recent logs
   docker-compose logs --tail=100 litellm-proxy
   
   # Environment check
   docker-compose exec litellm-proxy env | grep -E "LANGFUSE|OPENAI|ANTHROPIC"
   
   # Test request
   curl -v http://localhost:8000/health
   ```

3. **Report issue**: [GitHub Issues](https://github.com/MueMike/litellm-proxy-langfuse/issues)
   - Include log output
   - Describe expected vs actual behavior
   - List environment (OS, Docker version, Python version)

## Next Steps

- **Explore Examples**: Check `examples/` directory for more use cases
- **Customize Configuration**: Review `config/config.yaml` for advanced settings
- **Set Up Monitoring**: Configure Prometheus and Grafana for production monitoring
- **Read Documentation**: See [README.md](README.md) for architecture details
- **Deploy to Production**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

## Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LangFuse Documentation](https://langfuse.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Reference](https://docs.anthropic.com/claude/reference)
- [GitHub Repository](https://github.com/MueMike/litellm-proxy-langfuse)
