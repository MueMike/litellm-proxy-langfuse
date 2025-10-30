# LiteLLM Proxy with LangFuse Integration

A production-ready LiteLLM proxy server with integrated LangFuse tracing for monitoring and analyzing agentic coding sessions from IDEs like VSCode, Cursor, GitHub Copilot, and more.

## 🚀 Features

- **Multi-Provider Support**: OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Google Vertex AI, and more
- **LangFuse Integration**: Automatic trace generation, session tracking, and cost monitoring
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API endpoints
- **Real-time Streaming**: Full support for streaming responses
- **Advanced Monitoring**: Prometheus metrics, request/response logging, error tracking
- **IDE Integration**: Ready-to-use configurations for VSCode, Cursor, and other IDEs
- **Docker Support**: Production-ready containerized deployment
- **Cost Tracking**: Automatic token usage and cost calculation per request
- **Session Analytics**: Track and analyze coding sessions across multiple requests

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [IDE Integration](#ide-integration)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## 🏗️ Architecture

```
┌─────────────────┐
│   IDE Client    │  (VSCode, Cursor, etc.)
│  (Copilot/Roo)  │
└────────┬────────┘
         │ OpenAI-compatible API
         ▼
┌─────────────────────────────────────────┐
│       LiteLLM Proxy Server              │
│  ┌──────────────────────────────────┐   │
│  │  FastAPI + Middleware            │   │
│  │  - CORS, Tracing, Metrics        │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  LangFuse Integration            │   │
│  │  - Traces, Spans, Generations    │   │
│  │  - Cost & Token Tracking         │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  LiteLLM Core                    │   │
│  │  - Model Routing & Fallbacks     │   │
│  │  - Request Transformation        │   │
│  └──────────────────────────────────┘   │
└────────┬────────────────────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │ OpenAI │ │Anthropic│ │ Azure  │ │Bedrock │
    └────────┘ └────────┘ └────────┘ └────────┘
         │
         ▼
    ┌─────────────┐
    │  LangFuse   │ (Existing Instance)
    │  Dashboard  │
    └─────────────┘
```

## ⚡ Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/MueMike/litellm-proxy-langfuse.git
cd litellm-proxy-langfuse
```

2. Create `.env` file from template:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```bash
# Required: LangFuse credentials
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com

# At least one LLM provider API key
OPENAI_API_KEY=sk-xxxxxxxx
# or
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

4. Start the proxy:
```bash
cd docker
docker-compose up -d
```

5. Test the proxy:
```bash
curl http://localhost:8000/health
```

The proxy will be available at:
- API: http://localhost:8000
- Metrics: http://localhost:9090

### Local Development

1. Install Python 3.11+:
```bash
python --version  # Should be 3.11 or higher
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file and configure:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the server:
```bash
python -m uvicorn src.proxy.server:create_app --factory --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# LangFuse (Required for tracing)
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true

# Proxy Settings
PROXY_HOST=0.0.0.0
PROXY_PORT=8000
LOG_LEVEL=INFO

# LLM Providers (At least one required)
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
AZURE_API_KEY=xxx
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# Optional: Security
LITELLM_MASTER_KEY=sk-proxy-xxx  # Enable authentication
REQUIRE_AUTH=true

# Optional: Monitoring
ENABLE_PROMETHEUS=true
ENABLE_COST_TRACKING=true
```

### Model Configuration

Edit `config/config.yaml` to:
- Add or remove models
- Configure fallback models
- Set rate limits
- Customize routing

Example:
```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: ${OPENAI_API_KEY}
      
  - model_name: claude-3-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: ${ANTHROPIC_API_KEY}
```

## 🖥️ IDE Integration

### VSCode with Continue Extension

1. Install the [Continue extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue)

2. Add to `.vscode/settings.json`:
```json
{
  "continue.models": [
    {
      "title": "GPT-4 via Proxy",
      "provider": "openai",
      "model": "gpt-4",
      "apiBase": "http://localhost:8000/v1",
      "apiKey": "dummy-key"
    }
  ],
  "continue.customHeaders": {
    "X-User-ID": "your-username",
    "X-Session-ID": "coding-session"
  }
}
```

See `examples/vscode_settings.json` for complete configuration.

### Cursor IDE

1. Open Cursor Settings
2. Go to Models > Custom Models
3. Add configuration from `examples/cursor_config.json`

### GitHub Copilot

Configure proxy URL in GitHub Copilot settings:
```json
{
  "github.copilot.advanced": {
    "debug.overrideProxyUrl": "http://localhost:8000"
  }
}
```

## 📚 API Reference

### Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "litellm-proxy-langfuse"
}
```

#### List Models
```bash
GET /v1/models
```

#### Chat Completions
```bash
POST /v1/chat/completions
```

Request:
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "metadata": {
    "task_type": "code_generation",
    "language": "python"
  }
}
```

Custom Headers:
```
X-User-ID: your-username
X-Session-ID: session-123
```

Response includes trace information:
```
X-Trace-ID: <uuid>
X-Duration-Ms: <milliseconds>
```

### Testing

Run example requests:
```bash
python examples/test_requests.py
```

Run unit tests:
```bash
pytest tests/
```

## 🐳 Deployment

### Docker Deployment

1. Build image:
```bash
docker build -f docker/Dockerfile -t litellm-proxy-langfuse .
```

2. Run with docker-compose:
```bash
cd docker
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f litellm-proxy
```

4. Stop:
```bash
docker-compose down
```

### Production Considerations

- **Security**: Set `REQUIRE_AUTH=true` and configure `LITELLM_MASTER_KEY`
- **Scaling**: Run multiple instances behind a load balancer
- **Monitoring**: Use Prometheus metrics at `http://localhost:9090`
- **Logging**: Configure log aggregation (ELK, Datadog, etc.)
- **Secrets**: Use secret management (AWS Secrets Manager, Vault, etc.)

## 📊 Monitoring

### LangFuse Dashboard

1. Access your LangFuse instance (e.g., https://cloud.langfuse.com)
2. Navigate to your project
3. View traces with:
   - Request/response details
   - Token usage and costs
   - Latency metrics
   - Session analytics
   - Custom metadata (task types, languages, etc.)

### Prometheus Metrics

Available at `http://localhost:9090/metrics`:

- `litellm_requests_total` - Total requests by model/provider/status
- `litellm_request_duration_seconds` - Request duration histogram
- `litellm_tokens_used_total` - Token usage by model/type
- `litellm_cost_usd_total` - Total cost in USD
- `litellm_active_requests` - Current active requests
- `litellm_errors_total` - Error count by type

Example queries:
```promql
# Average request duration
rate(litellm_request_duration_seconds_sum[5m]) / rate(litellm_request_duration_seconds_count[5m])

# Requests per minute
rate(litellm_requests_total[1m]) * 60

# Total cost per hour
rate(litellm_cost_usd_total[1h]) * 3600
```

## 🔍 Troubleshooting

### Common Issues

**1. LangFuse not receiving traces**
- Verify `LANGFUSE_ENABLED=true`
- Check API keys in `.env`
- Confirm LangFuse host URL is correct
- Check logs for LangFuse connection errors

**2. LLM API calls failing**
- Verify provider API keys are set
- Check model names match configuration
- Review logs for specific error messages
- Test provider API directly

**3. Docker container won't start**
- Check `.env` file exists
- Verify all required environment variables are set
- Review logs: `docker-compose logs litellm-proxy`
- Ensure ports 8000 and 9090 are available

**4. High latency**
- Check network connectivity to LLM providers
- Monitor Prometheus metrics
- Consider increasing `REQUEST_TIMEOUT`
- Review LangFuse overhead in traces

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
DEBUG_MODE=true
```

### Logs

View logs:
```bash
# Docker
docker-compose logs -f litellm-proxy

# Local
# Logs are output to stdout
```

## 💡 Examples

### C++ Unit Test Generation

Example workflow tracked in LangFuse:

```python
import requests

headers = {
    "X-User-ID": "developer-cpp",
    "X-Session-ID": "cpp-unittest-session",
}

data = {
    "model": "gpt-4",
    "messages": [
        {
            "role": "system",
            "content": "You are an expert C++ developer."
        },
        {
            "role": "user",
            "content": "Generate unit tests for this function: int add(int a, int b) { return a + b; }"
        }
    ],
    "metadata": {
        "task_type": "unit_test_generation",
        "language": "cpp",
        "framework": "googletest"
    }
}

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    headers=headers,
    json=data
)

print(response.json())
```

This will appear in LangFuse with:
- User ID: `developer-cpp`
- Session ID: `cpp-unittest-session`
- Tags: `unit_test_generation`, `cpp`, `googletest`
- Full cost and token metrics

See `examples/test_requests.py` for more examples.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LangFuse Documentation](https://langfuse.com/docs)
- [GitHub Repository](https://github.com/MueMike/litellm-proxy-langfuse)

## 📞 Support

- Issues: [GitHub Issues](https://github.com/MueMike/litellm-proxy-langfuse/issues)
- Discussions: [GitHub Discussions](https://github.com/MueMike/litellm-proxy-langfuse/discussions)