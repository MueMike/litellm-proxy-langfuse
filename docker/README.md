# Docker Configuration

This directory contains Docker configuration and testing scripts for the LiteLLM proxy.

## Files

- **docker-compose.yml** - Docker Compose configuration for running the proxy
- **Dockerfile** - Container image definition
- **test_api.sh** - Shell script for testing the API (Linux/Mac)
- **test_api.py** - Python script for testing the API (cross-platform)

## Quick Start

### 1. Start the Container

```bash
# From repository root
cd docker
docker compose up -d
```

The proxy will be available at:
- API: http://localhost:8000
- Metrics: http://localhost:9090

### 2. Test the API

**Option A: Using Shell Script (Linux/Mac)**
```bash
./test_api.sh
```

**Option B: Using Python Script (Windows/Linux/Mac)**
```bash
python test_api.py
```

**Option C: Using Custom URL**
```bash
./test_api.sh http://myserver:8000
# or
python test_api.py http://myserver:8000
```

## Test Scripts

### test_api.sh / test_api.py

These scripts validate that the Docker container is running correctly by testing:

1. **Container Status** - Verifies container is running
2. **Health Check** - Tests `/health` endpoint
3. **List Models** - Tests `/v1/models` endpoint
4. **Chat Completion** - Tests `/v1/chat/completions` with basic request
5. **Metrics** - Tests Prometheus metrics endpoint (optional)

**Exit Codes:**
- `0` - All tests passed
- `1` - One or more tests failed

**Example Output:**
```
════════════════════════════════════════════════════════════════
LiteLLM Proxy Docker Container API Tests
════════════════════════════════════════════════════════════════
Testing proxy at: http://localhost:8000

▶ Checking if proxy is reachable
✓ Proxy is reachable

▶ Testing Docker Container Status
✓ Container 'litellm-proxy-langfuse' is running
  Status: running

▶ Testing Health Check Endpoint
✓ Health check endpoint responded with 200 OK
  Response: {"status":"healthy","service":"litellm-proxy-langfuse"}

▶ Testing List Models Endpoint
✓ Models endpoint responded with 5 models

▶ Testing Chat Completion Endpoint (Basic)
✓ Chat completion endpoint working correctly

▶ Testing Prometheus Metrics Endpoint
✓ Metrics endpoint is accessible
  Found 12 LiteLLM metrics

════════════════════════════════════════════════════════════════
Test Summary
════════════════════════════════════════════════════════════════
Passed: 6
Failed: 0

✓ All tests passed! API is working correctly.

Next steps:
  1. View logs: docker compose logs -f litellm-proxy
  2. Check LangFuse dashboard for traces
  3. Run full test suite: python examples/test_requests.py
```

## Common Issues

### Test fails: "Cannot reach proxy"

**Problem**: Container not running or not responding

**Solutions**:
1. Check container status: `docker compose ps`
2. View logs: `docker compose logs litellm-proxy`
3. Restart container: `docker compose restart`

### Test fails: "Chat completion failed (HTTP 401)"

**Problem**: Missing or invalid API keys

**Solutions**:
1. Check `.env` file in repository root
2. Ensure at least one provider API key is set (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
3. Restart container after updating .env: `docker compose restart`

### Test fails: "Chat completion failed (HTTP 500)"

**Problem**: Internal server error, likely configuration issue

**Solutions**:
1. Check logs: `docker compose logs litellm-proxy | tail -50`
2. Verify model configuration in `config/config.yaml`
3. Ensure API keys match the models configured

### Metrics endpoint not accessible

**Problem**: Port 9090 not accessible

**Note**: This is optional and won't cause overall test failure. Metrics may be disabled or on a different port.

## Container Management

### View Logs
```bash
# Live tail
docker compose logs -f litellm-proxy

# Last 100 lines
docker compose logs --tail=100 litellm-proxy

# Search for errors
docker compose logs litellm-proxy | grep -i error
```

### Stop Container
```bash
docker compose down
```

### Restart Container
```bash
docker compose restart litellm-proxy
```

### Rebuild Container
```bash
docker compose up -d --build
```

### Check Container Status
```bash
docker compose ps
```

## Environment Configuration

Edit `.env` file in repository root (not in docker/ directory):

```bash
# Required: LangFuse credentials
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com

# Required: At least one LLM provider
OPENAI_API_KEY=sk-xxxxxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

Then restart the container:
```bash
docker compose restart
```

## Advanced Testing

For comprehensive testing including LangFuse tracing verification:

```bash
cd ..  # Go to repository root
python examples/test_requests.py
```

## CI/CD Integration

Use these test scripts in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Start Docker Container
  run: |
    cd docker
    docker compose up -d
    
- name: Wait for container to be ready
  run: sleep 10
  
- name: Test API
  run: |
    cd docker
    python test_api.py
```

## See Also

- [USAGE.md](../USAGE.md) - Complete usage guide
- [README.md](../README.md) - Project overview
- [examples/test_requests.py](../examples/test_requests.py) - Comprehensive test suite
