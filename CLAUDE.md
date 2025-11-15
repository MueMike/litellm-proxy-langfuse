# CLAUDE.md - AI Assistant Guide for LiteLLM Proxy with LangFuse

> Last Updated: 2025-11-14
>
> This document provides a comprehensive guide for AI assistants (like Claude) working with the LiteLLM Proxy with LangFuse Integration codebase. It explains the project structure, development workflows, coding conventions, and key patterns to follow.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Codebase Structure](#codebase-structure)
- [Key Components](#key-components)
- [Development Workflows](#development-workflows)
- [Code Conventions](#code-conventions)
- [Testing Strategy](#testing-strategy)
- [Common Tasks](#common-tasks)
- [Important Patterns](#important-patterns)
- [Git Workflow](#git-workflow)
- [Troubleshooting Guide](#troubleshooting-guide)

---

## Project Overview

### Purpose

This project is a **production-ready LiteLLM proxy server** with integrated **LangFuse tracing** designed to:
- Act as an OpenAI-compatible API gateway for multiple LLM providers
- Automatically capture and trace all LLM interactions for monitoring
- Enable cost tracking, token usage analytics, and session management
- Integrate seamlessly with IDEs (VSCode, Cursor, GitHub Copilot)

### Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Core Library**: LiteLLM (multi-provider LLM routing)
- **Tracing**: LangFuse (observability and analytics)
- **Monitoring**: Prometheus metrics
- **Testing**: pytest with async support
- **Deployment**: Docker + Docker Compose
- **Python Version**: 3.11+

### Key Features

1. **Multi-Provider Support**: OpenAI, Anthropic, Azure, AWS Bedrock, Google Vertex AI
2. **OpenAI-Compatible API**: Drop-in replacement for OpenAI SDK
3. **LangFuse Integration**: Automatic trace generation with cost tracking
4. **Streaming Support**: Full streaming response support
5. **Prometheus Metrics**: Request latency, token usage, cost tracking
6. **Session Analytics**: Track coding sessions across multiple requests

---

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   IDE Client    │  (VSCode, Cursor, etc.)
└────────┬────────┘
         │ OpenAI-compatible API
         ▼
┌─────────────────────────────────────────┐
│       LiteLLM Proxy Server              │
│  ┌──────────────────────────────────┐   │
│  │  FastAPI Application             │   │
│  │  - CORS Middleware               │   │
│  │  - Tracing Middleware            │   │
│  │  - Metrics Middleware            │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  LangFuse Client                 │   │
│  │  - Trace Creation                │   │
│  │  - Generation Tracking           │   │
│  │  - Cost Calculation              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  LiteLLM Core                    │   │
│  │  - Model Routing                 │   │
│  │  - Request Transformation        │   │
│  └──────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │ OpenAI │ │Anthropic│ │ Azure  │ │Bedrock │
    └────────┘ └────────┘ └────────┘ └────────┘
```

### Request Flow

1. **Client Request** → API endpoint (`/v1/chat/completions`)
2. **Middleware Chain**:
   - TracingMiddleware: Generate trace ID, extract user/session info
   - MetricsMiddleware: Start request timing
3. **Route Handler** (`src/proxy/routes.py`):
   - Parse request (Pydantic validation)
   - Create LangFuse trace
   - Call LiteLLM with model/provider routing
   - Calculate costs and metrics
   - Create LangFuse generation span
4. **Response**: Return to client with trace headers

---

## Codebase Structure

```
llm-scope/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── Makefile                   # Common development tasks
├── pyproject.toml            # Project metadata
├── .env.example              # Environment variables template
│
├── src/                      # Main source code
│   ├── __init__.py
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py      # Pydantic settings (loads .env)
│   │
│   ├── proxy/               # Core proxy implementation
│   │   ├── __init__.py
│   │   ├── server.py        # FastAPI app creation & lifespan
│   │   ├── routes.py        # API route handlers
│   │   └── middleware.py    # Tracing & metrics middleware
│   │
│   ├── integrations/        # External service integrations
│   │   ├── __init__.py
│   │   ├── langfuse_client.py    # LangFuse tracing client
│   │   └── llm_providers.py      # Provider detection/config
│   │
│   ├── monitoring/          # Observability components
│   │   ├── __init__.py
│   │   ├── metrics.py       # Prometheus metrics collector
│   │   └── logger.py        # Logging configuration
│   │
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py       # Cost calculation, metadata extraction
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_proxy.py        # Proxy endpoint tests
│   ├── test_langfuse.py     # LangFuse integration tests
│   ├── test_integration.py  # End-to-end tests
│   └── test_curl.sh         # Comprehensive curl tests (15+ tests)
│
├── config/                  # Configuration files
│   ├── config.yaml          # Model configuration
│   └── model_config.yaml    # Advanced model settings
│
├── docker/                  # Docker deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── test_api.py          # Docker API test script
│   └── README.md
│
├── examples/                # Usage examples
│   ├── test_requests.py     # Example API requests
│   ├── vscode_settings.json # VSCode IDE configuration
│   └── cursor_config.json   # Cursor IDE configuration
│
└── .vscode/                 # VSCode workspace settings
    ├── settings.json
    ├── launch.json          # Debug configurations
    └── tasks.json           # Build/test tasks
```

### Key File Descriptions

| File | Purpose | When to Modify |
|------|---------|----------------|
| `main.py` | Entry point, runs uvicorn server | Rarely - only for startup logic |
| `src/proxy/server.py` | FastAPI app creation, middleware setup | Adding new middleware, app-level config |
| `src/proxy/routes.py` | API endpoints (health, models, completions) | Adding new endpoints, changing API logic |
| `src/proxy/middleware.py` | Request/response middleware | Modifying tracing/metrics behavior |
| `src/config/settings.py` | Environment configuration with Pydantic | Adding new env variables |
| `src/integrations/langfuse_client.py` | LangFuse tracing logic | Changing trace structure, adding spans |
| `src/utils/helpers.py` | Cost calculation, metadata extraction | Updating cost models, adding utilities |
| `tests/test_curl.sh` | Comprehensive curl tests for edge cases | Adding regression tests |

---

## Key Components

### 1. Configuration System (`src/config/settings.py`)

**Pattern**: Pydantic Settings with `.env` file loading

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    langfuse_public_key: Optional[str] = Field(None, alias="LANGFUSE_PUBLIC_KEY")
    # ... more settings
```

**Key Method**: `is_langfuse_configured()` - Checks if LangFuse is properly set up

**When to Modify**: Adding new environment variables or feature flags

### 2. FastAPI Application (`src/proxy/server.py`)

**Pattern**: Factory function with async lifespan manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize metrics, LangFuse client
    yield
    # Shutdown: Flush LangFuse, cleanup

def create_app() -> FastAPI:
    # Create app, add middleware, include routes
    return app
```

**Important**:
- Middleware order matters (metrics → tracing → routes)
- LangFuse client stored in `app.state.langfuse_client`
- Dependency injection via middleware for request-level access

### 3. API Routes (`src/proxy/routes.py`)

**Key Endpoints**:
- `GET /health` - Health check (always returns 200)
- `GET /ready` - Readiness check
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions (main endpoint)
- `POST /chat/completions` - Alternative path (same handler)

**Request Flow in Chat Completions**:
1. Pydantic validation of `ChatCompletionRequest`
2. Extract user_id, session_id from headers
3. Create LangFuse trace (if enabled)
4. Call `litellm.acompletion()` with request params
5. Calculate cost and record metrics
6. Create LangFuse generation span
7. Return response

**Important Headers**:
- `X-User-ID` - User identifier for LangFuse
- `X-Session-ID` - Session identifier for grouping requests
- `X-Trace-ID` (response) - Trace ID for debugging

### 4. LangFuse Integration (`src/integrations/langfuse_client.py`)

**Key Methods**:
- `create_trace()` - Creates top-level trace with user/session metadata
- `create_generation()` - Records LLM generation with tokens/cost
- `create_span()` - Generic span for sub-operations
- `score_trace()` - Add quality scores to traces
- `flush()` - Flush pending events (call on shutdown)

**Usage Pattern**:
```python
# In routes.py
trace = langfuse_client.create_trace(
    name="chat_completion",
    user_id=user_id,
    session_id=session_id,
    metadata={...},
    tags=[provider, model]
)

# After LLM call
langfuse_client.create_generation(
    trace_id=trace.id,
    model=model,
    input_data=messages,
    output_data=response,
    usage={...},
)
```

### 5. Middleware (`src/proxy/middleware.py`)

**TracingMiddleware**:
- Generates unique trace ID per request
- Extracts `X-User-ID` and `X-Session-ID` headers
- Adds trace headers to response
- Skips health/metrics endpoints

**MetricsMiddleware**:
- Records request duration
- Adds `X-Duration-Ms` header
- Feeds data to Prometheus metrics collector

### 6. Utilities (`src/utils/helpers.py`)

**Key Functions**:
- `generate_trace_id()` - UUID generation
- `calculate_cost()` - Token-based cost estimation (model-specific rates)
- `extract_metadata()` - Extracts metadata from request, handles None values
- `format_messages_for_logging()` - Truncates messages for logs

**Important**: `extract_metadata()` includes the fix for `metadata=None` handling (PR #4)

---

## Development Workflows

### Local Development Setup

1. **Clone and Setup**:
   ```bash
   git clone <repo-url>
   cd llm-scope
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with API keys
   ```

3. **Run Server**:
   ```bash
   # Development mode (auto-reload)
   python -m uvicorn src.proxy.server:create_app --factory --reload --host 0.0.0.0 --port 8000

   # Or use Makefile
   make run
   ```

### Docker Development

```bash
cd docker
docker-compose up -d
docker-compose logs -f litellm-proxy

# Test
python test_api.py
# Or
./test_api.sh
```

### Running Tests

```bash
# All tests with coverage
make test

# Specific test file
pytest tests/test_proxy.py -v

# Curl regression tests (important!)
./tests/test_curl.sh

# Integration tests
python examples/test_requests.py
```

### Code Quality

```bash
# Format code
make format  # Runs black and isort

# Lint
make lint    # Runs flake8 and mypy

# Before committing
make format && make lint && make test
```

---

## Code Conventions

### Python Style

- **PEP 8** compliance (enforced by black and flake8)
- **Type hints** for function parameters and return values
- **Docstrings** for all public functions/classes (Google style)
- **Max line length**: 100 characters

### Example Function Style

```python
def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    provider: Optional[str] = None,
) -> float:
    """
    Calculate cost for API call based on token usage.

    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        provider: Optional provider name

    Returns:
        Estimated cost in USD
    """
    # Implementation
    pass
```

### Async/Await Patterns

- **All route handlers** must be async (`async def`)
- **LiteLLM calls** use `await litellm.acompletion()`
- **Database/IO operations** should be async where possible

### Error Handling

```python
try:
    # Operation
    response = await litellm.acompletion(...)
except Exception as e:
    # Log error with context
    logger.error(f"Chat completion failed: {e}", exc_info=True)

    # Record metrics
    metrics_collector.record_error(model, provider, type(e).__name__)

    # Return HTTP error
    raise HTTPException(status_code=500, detail=str(e))
```

### Configuration Access

**Always use dependency injection pattern**:

```python
from src.config import get_settings

def some_function():
    settings = get_settings()  # Cached singleton
    if settings.is_langfuse_configured():
        # Use LangFuse
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed info for debugging")
logger.info("Important events")
logger.warning("Warning conditions")
logger.error("Error conditions", exc_info=True)  # Include traceback
```

---

## Testing Strategy

### Test Types

1. **Unit Tests** (`tests/test_*.py`):
   - Test individual functions/classes
   - Mock external dependencies (LangFuse, LiteLLM)
   - Fast execution

2. **Integration Tests** (`tests/test_integration.py`):
   - Test full request/response flow
   - May use real API keys (configurable)
   - Test LangFuse integration end-to-end

3. **Curl Tests** (`tests/test_curl.sh`):
   - 15+ comprehensive edge case tests
   - Tests for NoneType errors (regression from PR #4)
   - Validates error handling

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient
from src.proxy.server import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Important Test Cases

**Always test these scenarios when modifying routes**:
1. Valid request with all fields
2. Request with `metadata=None` (regression test for PR #4)
3. Request with missing required fields
4. Request with invalid JSON
5. Request with custom headers (X-User-ID, X-Session-ID)

### Running Curl Tests

```bash
# Local server
./tests/test_curl.sh

# Custom host
./tests/test_curl.sh http://production-server:8000

# Expected: 0 failures
```

---

## Common Tasks

### Adding a New Environment Variable

1. **Add to `.env.example`**:
   ```bash
   NEW_FEATURE_ENABLED=true
   ```

2. **Add to `src/config/settings.py`**:
   ```python
   new_feature_enabled: bool = Field(True, alias="NEW_FEATURE_ENABLED")
   ```

3. **Update documentation**: README.md, USAGE.md

### Adding a New API Endpoint

1. **Define route in `src/proxy/routes.py`**:
   ```python
   @router.get("/v1/new-endpoint")
   async def new_endpoint(request: Request):
       # Implementation
       return {"status": "ok"}
   ```

2. **Add tests** in `tests/test_proxy.py`
3. **Update API documentation** in README.md
4. **Add curl test** in `tests/test_curl.sh` if needed

### Modifying LangFuse Tracing

**Location**: `src/integrations/langfuse_client.py`

**Common Modifications**:
- Adding new metadata fields
- Creating additional spans
- Changing trace structure

**Example - Adding a new metadata field**:
```python
# In routes.py
metadata.update({
    "endpoint": "/chat/completions",
    "provider": provider,
    "new_field": some_value,  # Add here
})
```

### Updating Cost Calculation

**Location**: `src/utils/helpers.py` → `calculate_cost()`

**Pattern**:
```python
if "new-model" in model.lower():
    cost_per_1k_prompt = 0.01
    cost_per_1k_completion = 0.03
```

### Adding a New LLM Provider

1. **Add API key to `.env.example`**
2. **Add to `src/config/settings.py`**
3. **Update provider detection** in `src/integrations/llm_providers.py`
4. **Add model to `config/config.yaml`**
5. **Update README.md** with setup instructions

---

## Important Patterns

### 1. Dependency Injection

**Pattern**: Store global instances in `app.state`, inject via middleware

```python
# In server.py lifespan
langfuse_client = LangFuseClient(settings)
app.state.langfuse_client = langfuse_client

# In middleware
request.state.langfuse_client = app.state.langfuse_client

# In route handler
langfuse_client = getattr(request.state, "langfuse_client", None)
```

### 2. Graceful Degradation

**Pattern**: Continue operation if LangFuse fails

```python
if langfuse_client and langfuse_client.enabled:
    try:
        trace = langfuse_client.create_trace(...)
    except Exception as e:
        logger.error(f"LangFuse trace failed: {e}")
        # Continue without tracing
```

### 3. Metrics Collection

**Pattern**: Always record metrics, even on failure

```python
try:
    response = await litellm.acompletion(...)
    metrics_collector.record_request(status="success", ...)
except Exception as e:
    metrics_collector.record_request(status="error", ...)
    metrics_collector.record_error(...)
    raise
finally:
    metrics_collector.dec_active_requests(...)
```

### 4. Metadata Handling (IMPORTANT)

**Always check for None before iteration**:

```python
# CORRECT (from PR #4 fix)
if "metadata" in request_data and request_data["metadata"] is not None:
    metadata.update(request_data["metadata"])

# WRONG - causes NoneType iteration error
if "metadata" in request_data:
    metadata.update(request_data["metadata"])  # Fails if None!
```

### 5. Async Context Managers

**Pattern**: Use for startup/shutdown lifecycle

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = SomeClient()
    app.state.client = client

    yield

    # Shutdown
    client.cleanup()
```

---

## Git Workflow

### Branch Naming

- **Feature branches**: `feature/description`
- **Bug fixes**: `fix/issue-description`
- **Claude branches**: `claude/claude-md-{session-id}` (auto-generated)

### Commit Messages

```bash
# Good commit messages
git commit -m "Add null metadata handling in extract_metadata"
git commit -m "Fix NoneType error when metadata is None"
git commit -m "Add comprehensive curl tests for edge cases"

# Bad commit messages
git commit -m "fix bug"
git commit -m "updates"
```

### Pull Request Process

1. Create feature branch
2. Make changes and add tests
3. Run full test suite: `make test`
4. Run curl tests: `./tests/test_curl.sh`
5. Format code: `make format`
6. Commit changes
7. Push to remote
8. Create PR with:
   - Clear description
   - Test results
   - Related issue reference

### Pre-Commit Checklist

- [ ] All tests pass (`make test`)
- [ ] Curl tests pass (`./tests/test_curl.sh`)
- [ ] Code formatted (`make format`)
- [ ] No linting errors (`make lint`)
- [ ] Documentation updated (if needed)
- [ ] `.env.example` updated (if new env vars added)

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "NoneType object is not iterable"

**Cause**: Attempting to iterate over `metadata` when it's `None`

**Solution**: Check for `None` before using `.update()` or iteration
```python
if metadata is not None:
    result.update(metadata)
```

**Related**: PR #4 fixed this in `extract_metadata()`

#### 2. LangFuse Traces Not Appearing

**Check**:
1. Is `LANGFUSE_ENABLED=true` in `.env`?
2. Are API keys correct?
3. Is LangFuse host URL correct?
4. Check logs: `docker-compose logs litellm-proxy | grep -i langfuse`

**Debug**:
```python
# In routes.py, add logging
logger.info(f"LangFuse client enabled: {langfuse_client.enabled}")
logger.info(f"Trace created: {trace}")
```

#### 3. Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Run from project root with proper Python path
```bash
# From project root
python -m uvicorn src.proxy.server:create_app --factory
```

#### 4. Port Already in Use

**Symptom**: `OSError: [Errno 98] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

#### 5. Docker Container Won't Start

**Check**:
1. `.env` file exists in project root
2. Required env vars are set (LangFuse keys, at least one LLM provider key)
3. Ports 8000 and 9090 are available

**Debug**:
```bash
docker-compose logs litellm-proxy
docker-compose ps
```

### Debug Mode

Enable detailed logging:
```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

Restart server to see:
- Full request/response bodies
- LangFuse API calls
- Model routing decisions
- Detailed error traces

---

## Best Practices for AI Assistants

### When Making Changes

1. **Read First**: Always read existing code before modifying
2. **Test Coverage**: Add tests for new functionality
3. **Backward Compatibility**: Don't break existing APIs
4. **Error Handling**: Always handle edge cases (None, empty lists, etc.)
5. **Documentation**: Update relevant .md files

### When Writing Code

1. **Follow existing patterns** (see patterns section above)
2. **Use type hints** for better IDE support
3. **Log important events** at appropriate levels
4. **Add docstrings** for public functions
5. **Handle async properly** - use `await` for all async calls

### When Debugging

1. **Check logs first**: `docker-compose logs` or console output
2. **Verify environment**: Ensure `.env` is correct
3. **Test incrementally**: Test each change before moving on
4. **Use debug endpoints**: `/health`, `/ready`, `/v1/models`
5. **Run curl tests**: `./tests/test_curl.sh` catches many issues

### Code Review Checklist

Before considering code complete:
- [ ] Follows existing code style and patterns
- [ ] Has appropriate error handling
- [ ] Has tests (unit + integration where appropriate)
- [ ] Has docstrings for public APIs
- [ ] Logs important events
- [ ] Handles None/empty values correctly
- [ ] No hardcoded values (use config/env)
- [ ] Updated documentation if needed

---

## Quick Reference

### Essential Commands

```bash
# Development
make run              # Start local server
make test             # Run all tests
make format           # Format code
make lint             # Check code quality

# Docker
cd docker && docker-compose up -d     # Start containers
cd docker && docker-compose logs -f   # View logs
cd docker && docker-compose down      # Stop containers

# Testing
./tests/test_curl.sh                  # Curl regression tests
python examples/test_requests.py      # Example requests
pytest tests/test_proxy.py -v         # Unit tests
```

### Important URLs (Local)

- API: http://localhost:8000
- Health: http://localhost:8000/health
- Models: http://localhost:8000/v1/models
- Metrics: http://localhost:9090/metrics
- LangFuse: https://cloud.langfuse.com (external)

### Key Files to Know

- **Entry Point**: `main.py`
- **App Creation**: `src/proxy/server.py`
- **Routes**: `src/proxy/routes.py`
- **Config**: `src/config/settings.py`
- **LangFuse**: `src/integrations/langfuse_client.py`
- **Tests**: `tests/test_*.py`, `tests/test_curl.sh`

### Environment Variables

See `.env.example` for full list. Most important:
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (at least one)
- `LOG_LEVEL`, `DEBUG_MODE`
- `PROXY_HOST`, `PROXY_PORT`

---

## Additional Resources

- **README.md**: User-facing documentation, setup instructions
- **USAGE.md**: Detailed usage guide, IDE integration
- **DEPLOYMENT.md**: Production deployment guide
- **CONTRIBUTING.md**: Contribution guidelines
- **LiteLLM Docs**: https://docs.litellm.ai/
- **LangFuse Docs**: https://langfuse.com/docs

---

## Change Log

### Recent Changes

- **PR #4 (2024-11-14)**: Fixed NoneType error when metadata is None
  - Modified `extract_metadata()` in `src/utils/helpers.py`
  - Added comprehensive curl tests in `tests/test_curl.sh`
  - Updated README with curl test instructions

### Known Issues

- None currently

---

**For Questions or Issues**: Open a GitHub issue or check the troubleshooting section above.

**Last Reviewed**: 2025-11-14
