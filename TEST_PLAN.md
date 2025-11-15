# LiteLLM Proxy - Comprehensive Test Plan

> **Purpose**: Complete validation of the LiteLLM Proxy with LangFuse Integration
>
> **Last Updated**: 2025-11-14
>
> This document provides a step-by-step test plan to validate all functionality of the proxy server.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Phase 1: Environment Setup Verification](#phase-1-environment-setup-verification)
- [Phase 2: Basic Functionality Tests](#phase-2-basic-functionality-tests)
- [Phase 3: Core API Tests](#phase-3-core-api-tests)
- [Phase 4: LangFuse Integration Tests](#phase-4-langfuse-integration-tests)
- [Phase 5: Monitoring & Metrics Tests](#phase-5-monitoring--metrics-tests)
- [Phase 6: Error Handling Tests](#phase-6-error-handling-tests)
- [Phase 7: IDE Integration Tests](#phase-7-ide-integration-tests)
- [Phase 8: Load & Performance Tests](#phase-8-load--performance-tests)
- [Final Checklist](#final-checklist)

---

## Prerequisites

### Required Components

- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] curl or similar HTTP client
- [ ] Access to LangFuse instance (cloud or self-hosted)
- [ ] At least one LLM provider API key (OpenAI, Anthropic, etc.)

### Before Starting

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/MueMike/llm-scope.git
   cd llm-scope
   ```

2. **Prepare environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your credentials**:
   - Add LangFuse keys (public, secret, host)
   - Add at least one LLM provider API key
   - Review and adjust other settings as needed

---

## Phase 1: Environment Setup Verification

### 1.1 Verify Configuration File

**Objective**: Ensure `.env` file is properly configured

**Steps**:
```bash
# Check that .env file exists
ls -la .env

# Verify required variables are set (without showing values)
grep -E "LANGFUSE_PUBLIC_KEY|LANGFUSE_SECRET_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY" .env
```

**Expected Result**: File exists and contains required API keys

**Status**: [ ] Pass / [ ] Fail

---

### 1.2 Verify Docker Setup

**Objective**: Ensure Docker environment is working

**Steps**:
```bash
# Check Docker version
docker --version
docker-compose --version

# Verify Docker is running
docker ps
```

**Expected Result**:
- Docker version 20.10+ or higher
- Docker Compose version 1.29+ or higher
- Command returns without errors

**Status**: [ ] Pass / [ ] Fail

---

### 1.3 Build Docker Image

**Objective**: Build the proxy Docker image

**Steps**:
```bash
cd docker
docker-compose build
```

**Expected Result**: Build completes successfully without errors

**Status**: [ ] Pass / [ ] Fail

**Notes**:
_____________________________________________________________________________

---

## Phase 2: Basic Functionality Tests

### 2.1 Start the Proxy Server

**Objective**: Start the proxy and verify it's running

**Steps**:
```bash
cd docker
docker-compose up -d
```

**Verification**:
```bash
# Check container status
docker-compose ps

# Check logs for startup messages
docker-compose logs litellm-proxy | head -20
```

**Expected Result**:
- Container status shows "Up"
- Logs show "Starting LiteLLM Proxy with LangFuse integration"
- Logs show "LangFuse enabled: True"
- No error messages in logs

**Status**: [ ] Pass / [ ] Fail

**Container ID**: _______________________

**Notes**:
_____________________________________________________________________________

---

### 2.2 Health Check Endpoint

**Objective**: Verify the health endpoint responds correctly

**Steps**:
```bash
curl http://localhost:8000/health
```

**Expected Result**:
```json
{
  "status": "healthy",
  "service": "litellm-proxy-langfuse"
}
```

**Status**: [ ] Pass / [ ] Fail

---

### 2.3 Readiness Check Endpoint

**Objective**: Verify the readiness endpoint responds correctly

**Steps**:
```bash
curl http://localhost:8000/ready
```

**Expected Result**:
```json
{
  "status": "ready",
  "service": "litellm-proxy-langfuse"
}
```

**Status**: [ ] Pass / [ ] Fail

---

### 2.4 List Models Endpoint

**Objective**: Verify the models endpoint returns available models

**Steps**:
```bash
# Test /v1/models path
curl http://localhost:8000/v1/models

# Test alternative /models path
curl http://localhost:8000/models
```

**Expected Result**:
- Response contains `"object": "list"`
- Response contains `"data"` array
- Data array contains model objects with `id`, `object`, `owned_by` fields
- Both paths return same data

**Status**: [ ] Pass / [ ] Fail

**Models Found**: _______________________

---

## Phase 3: Core API Tests

### 3.1 Basic Chat Completion (OpenAI)

**Objective**: Test basic chat completion with OpenAI model

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "X-Session-ID: test-session-001" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Say hello in one word"}
    ],
    "max_tokens": 10
  }'
```

**Expected Result**:
- HTTP 200 status
- Response contains `choices` array
- Response contains `usage` object with token counts
- Response headers include `X-Trace-ID` and `X-Duration-Ms`

**Status**: [ ] Pass / [ ] Fail

**Response Time**: _______ ms

**Trace ID**: _______________________

---

### 3.2 Chat Completion with Metadata

**Objective**: Test chat completion with custom metadata

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "X-Session-ID: test-session-002" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write a hello world in Python"}
    ],
    "max_tokens": 100,
    "metadata": {
      "task_type": "code_generation",
      "language": "python",
      "project": "test-project"
    }
  }'
```

**Expected Result**:
- HTTP 200 status
- Successful response with code output
- Headers include trace ID

**Status**: [ ] Pass / [ ] Fail

**Trace ID**: _______________________

---

### 3.3 Chat Completion with Anthropic (Claude)

**Objective**: Test chat completion with Anthropic model (if configured)

**Prerequisites**: Anthropic API key must be configured in `.env`

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "X-Session-ID: test-session-003" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "messages": [
      {"role": "user", "content": "Say hello in one word"}
    ],
    "max_tokens": 10
  }'
```

**Expected Result**:
- HTTP 200 status
- Successful response from Claude model

**Status**: [ ] Pass / [ ] Fail / [ ] Skipped (no API key)

**Trace ID**: _______________________

---

### 3.4 Alternative Endpoint Path

**Objective**: Test alternative `/chat/completions` path

**Steps**:
```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

**Expected Result**:
- HTTP 200 status
- Same behavior as `/v1/chat/completions`

**Status**: [ ] Pass / [ ] Fail

---

### 3.5 Streaming Response Test

**Objective**: Test streaming chat completion

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "X-Session-ID: stream-session" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Count from 1 to 5"}],
    "stream": true,
    "max_tokens": 50
  }'
```

**Expected Result**:
- Server-sent events (SSE) format response
- Multiple `data:` chunks received
- Final `data: [DONE]` message

**Status**: [ ] Pass / [ ] Fail

---

## Phase 4: LangFuse Integration Tests

### 4.1 Verify LangFuse Connection

**Objective**: Ensure proxy is connected to LangFuse

**Steps**:
```bash
# Check logs for LangFuse initialization
docker-compose logs litellm-proxy | grep -i langfuse
```

**Expected Result**:
- Log shows "LangFuse client initialized successfully"
- Log shows "LangFuse enabled: True"
- No connection errors

**Status**: [ ] Pass / [ ] Fail

---

### 4.2 Verify Trace Creation

**Objective**: Confirm traces are being created in LangFuse

**Steps**:
1. Make a test request:
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "X-User-ID: test-user-langfuse" \
     -H "X-Session-ID: langfuse-test-session" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Test for LangFuse"}],
       "max_tokens": 20,
       "metadata": {
         "test_name": "langfuse_integration_test",
         "phase": "4.2"
       }
     }'
   ```

2. Note the `X-Trace-ID` from response headers

3. Open LangFuse dashboard:
   - Navigate to your project
   - Go to "Traces" section
   - Search for the trace ID or session ID

**Expected Result**:
- Trace appears in LangFuse dashboard
- Trace shows user ID: `test-user-langfuse`
- Trace shows session ID: `langfuse-test-session`
- Metadata includes `test_name` and `phase`
- Tags include model name and provider

**Status**: [ ] Pass / [ ] Fail

**Screenshot**: [ ] Attached

**Trace URL**: _______________________

---

### 4.3 Verify Token Usage Tracking

**Objective**: Confirm token usage is tracked correctly

**Steps**:
1. Make a request with known token usage
2. Check the trace in LangFuse

**Expected Result in LangFuse**:
- Trace shows `prompt_tokens` count
- Trace shows `completion_tokens` count
- Trace shows `total_tokens` count
- Values are non-zero and reasonable

**Status**: [ ] Pass / [ ] Fail

**Prompt Tokens**: _______

**Completion Tokens**: _______

**Total Tokens**: _______

---

### 4.4 Verify Cost Tracking

**Objective**: Confirm cost calculation is working

**Steps**:
1. Check the trace from previous test
2. Look for cost information

**Expected Result**:
- Trace shows estimated cost in USD
- Cost is greater than 0
- Cost seems reasonable for token usage

**Status**: [ ] Pass / [ ] Fail

**Estimated Cost**: $_______ USD

---

### 4.5 Verify Session Tracking

**Objective**: Confirm multiple requests in same session are grouped

**Steps**:
1. Make multiple requests with same session ID:
   ```bash
   # Request 1
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "X-User-ID: session-test-user" \
     -H "X-Session-ID: session-grouping-test" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "First message"}], "max_tokens": 10}'

   # Request 2
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "X-User-ID: session-test-user" \
     -H "X-Session-ID: session-grouping-test" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Second message"}], "max_tokens": 10}'

   # Request 3
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "X-User-ID: session-test-user" \
     -H "X-Session-ID: session-grouping-test" \
     -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Third message"}], "max_tokens": 10}'
   ```

2. Check LangFuse dashboard
3. Filter by session ID: `session-grouping-test`

**Expected Result**:
- All 3 traces appear under same session
- Session view shows all traces together
- User ID is consistent across all traces

**Status**: [ ] Pass / [ ] Fail

**Number of Traces in Session**: _______

---

## Phase 5: Monitoring & Metrics Tests

### 5.1 Prometheus Metrics Endpoint

**Objective**: Verify Prometheus metrics are exposed

**Steps**:
```bash
curl http://localhost:9090/metrics
```

**Expected Result**:
- HTTP 200 status
- Response contains Prometheus-formatted metrics
- Metrics include `litellm_` prefixed entries

**Status**: [ ] Pass / [ ] Fail

---

### 5.2 Verify Request Metrics

**Objective**: Confirm request metrics are being recorded

**Steps**:
```bash
# Make a few test requests first
for i in {1..5}; do
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Test '$i'"}], "max_tokens": 5}' \
    > /dev/null 2>&1
done

# Check metrics
curl http://localhost:9090/metrics | grep litellm_requests_total
```

**Expected Result**:
- Metric `litellm_requests_total` exists
- Count is >= 5
- Metrics broken down by model, provider, status

**Status**: [ ] Pass / [ ] Fail

**Total Requests**: _______

---

### 5.3 Verify Duration Metrics

**Objective**: Confirm request duration tracking

**Steps**:
```bash
curl http://localhost:9090/metrics | grep litellm_request_duration
```

**Expected Result**:
- Metric `litellm_request_duration_seconds` exists
- Shows histogram buckets
- Shows count and sum

**Status**: [ ] Pass / [ ] Fail

---

### 5.4 Verify Token Metrics

**Objective**: Confirm token usage metrics

**Steps**:
```bash
curl http://localhost:9090/metrics | grep litellm_tokens_used
```

**Expected Result**:
- Metric `litellm_tokens_used_total` exists
- Broken down by model and token type (prompt/completion)

**Status**: [ ] Pass / [ ] Fail

---

### 5.5 Verify Cost Metrics

**Objective**: Confirm cost tracking metrics

**Steps**:
```bash
curl http://localhost:9090/metrics | grep litellm_cost_usd
```

**Expected Result**:
- Metric `litellm_cost_usd_total` exists
- Shows accumulated cost

**Status**: [ ] Pass / [ ] Fail

**Total Cost**: $_______ USD

---

## Phase 6: Error Handling Tests

### 6.1 Automated Curl Test Suite

**Objective**: Run comprehensive edge case tests

**Steps**:
```bash
cd /path/to/llm-scope
./tests/test_curl.sh
```

**Expected Result**:
- All tests pass (0 failures)
- Tests verify proper error handling for:
  - Missing API keys
  - Invalid JSON
  - Missing required fields
  - Null values
  - Malformed requests
  - Wrong HTTP methods

**Status**: [ ] Pass / [ ] Fail

**Passed Tests**: _______ / _______

**Failed Tests**: _______

**Notes**:
_____________________________________________________________________________

---

### 6.2 Invalid Model Name

**Objective**: Test handling of non-existent model

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nonexistent-model-123",
    "messages": [{"role": "user", "content": "Test"}]
  }'
```

**Expected Result**:
- HTTP 500 status (or appropriate error code)
- Error message in response
- No server crash
- Error logged in server logs

**Status**: [ ] Pass / [ ] Fail

---

### 6.3 Null Metadata Handling

**Objective**: Verify fix from PR #4 - null metadata handling

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Test"}],
    "metadata": null,
    "max_tokens": 10
  }'
```

**Expected Result**:
- Request succeeds (HTTP 200)
- No "NoneType is not iterable" error
- Response is valid

**Status**: [ ] Pass / [ ] Fail

**Critical**: This test validates the fix from PR #4

---

### 6.4 Missing Required Fields

**Objective**: Test validation error handling

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo"
  }'
```

**Expected Result**:
- HTTP 422 status (Unprocessable Entity)
- Validation error message
- Indicates missing "messages" field

**Status**: [ ] Pass / [ ] Fail

---

### 6.5 Rate Limiting (if enabled)

**Objective**: Test rate limiting behavior

**Prerequisites**: Set `ENABLE_RATE_LIMITING=true` in `.env`

**Steps**:
```bash
# Make rapid requests
for i in {1..100}; do
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Test"}], "max_tokens": 5}' &
done
wait
```

**Expected Result**:
- Some requests succeed
- Some requests return 429 (Too Many Requests) if limits exceeded
- Server remains stable

**Status**: [ ] Pass / [ ] Fail / [ ] Skipped (not enabled)

---

## Phase 7: IDE Integration Tests

### 7.1 VSCode Continue Extension (Optional)

**Objective**: Test IDE integration with Continue extension

**Prerequisites**: VSCode with Continue extension installed

**Steps**:
1. Configure Continue in VSCode settings:
   ```json
   {
     "continue.models": [{
       "title": "GPT-4 via Proxy",
       "provider": "openai",
       "model": "gpt-4",
       "apiBase": "http://localhost:8000/v1",
       "apiKey": "dummy-key"
     }],
     "continue.customHeaders": {
       "X-User-ID": "vscode-test-user",
       "X-Session-ID": "vscode-test-session"
     }
   }
   ```

2. Use Continue to ask a coding question
3. Check LangFuse for traces

**Expected Result**:
- Continue successfully communicates with proxy
- Responses are received in VSCode
- Traces appear in LangFuse with correct user/session IDs

**Status**: [ ] Pass / [ ] Fail / [ ] Skipped

---

### 7.2 Direct API Test with IDE Headers

**Objective**: Simulate IDE request pattern

**Steps**:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: ide-simulator" \
  -H "X-Session-ID: ide-session-001" \
  -H "User-Agent: VSCode/1.85.0" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "You are a coding assistant."},
      {"role": "user", "content": "Write a Python function to check if a number is prime"}
    ],
    "max_tokens": 200,
    "temperature": 0.7,
    "metadata": {
      "task_type": "code_generation",
      "language": "python",
      "source": "vscode"
    }
  }'
```

**Expected Result**:
- HTTP 200 status
- Valid code response
- Trace in LangFuse shows IDE-specific metadata

**Status**: [ ] Pass / [ ] Fail

---

## Phase 8: Load & Performance Tests

### 8.1 Sequential Load Test

**Objective**: Test handling of sequential requests

**Steps**:
```bash
# Run 50 sequential requests
for i in {1..50}; do
  echo "Request $i"
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "X-User-ID: load-test-user" \
    -H "X-Session-ID: sequential-load-test" \
    -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Test '$i'"}], "max_tokens": 5}'
  echo ""
done
```

**Expected Result**:
- All requests succeed
- Response times are consistent
- Server remains stable
- Memory usage is stable

**Status**: [ ] Pass / [ ] Fail

**Average Response Time**: _______ ms

**Notes**:
_____________________________________________________________________________

---

### 8.2 Concurrent Load Test

**Objective**: Test handling of concurrent requests

**Steps**:
```bash
# Run 20 concurrent requests
for i in {1..20}; do
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "X-User-ID: load-test-user" \
    -H "X-Session-ID: concurrent-load-test" \
    -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Test '$i'"}], "max_tokens": 5}' &
done
wait
```

**Expected Result**:
- All requests complete successfully
- Server handles concurrency well
- No crashes or errors

**Status**: [ ] Pass / [ ] Fail

---

### 8.3 Memory Leak Test

**Objective**: Verify no memory leaks over extended operation

**Steps**:
```bash
# Check initial memory usage
docker stats litellm-proxy --no-stream

# Run extended test
for i in {1..200}; do
  curl -s -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Test"}], "max_tokens": 5}' > /dev/null
  if [ $((i % 20)) -eq 0 ]; then
    echo "Completed $i requests"
  fi
done

# Check final memory usage
docker stats litellm-proxy --no-stream
```

**Expected Result**:
- Memory usage increases slightly during test
- Memory stabilizes and doesn't grow unbounded
- Container remains healthy

**Status**: [ ] Pass / [ ] Fail

**Initial Memory**: _______ MB

**Final Memory**: _______ MB

**Memory Growth**: _______ MB

---

## Final Checklist

### Functional Completeness

- [ ] All health/readiness endpoints working
- [ ] Model listing endpoint working
- [ ] Chat completions endpoint working
- [ ] Alternative endpoint paths working
- [ ] Custom headers (X-User-ID, X-Session-ID) working
- [ ] Metadata passing working
- [ ] Null metadata handling working (PR #4 fix verified)

### LangFuse Integration

- [ ] LangFuse connection established
- [ ] Traces being created
- [ ] User ID tracking working
- [ ] Session ID tracking working
- [ ] Token usage tracking working
- [ ] Cost calculation working
- [ ] Metadata appearing in traces
- [ ] Tags appearing in traces

### Monitoring & Metrics

- [ ] Prometheus metrics endpoint working
- [ ] Request count metrics working
- [ ] Duration metrics working
- [ ] Token usage metrics working
- [ ] Cost metrics working
- [ ] Error metrics working

### Error Handling

- [ ] Invalid requests handled gracefully
- [ ] Missing API keys handled properly
- [ ] Validation errors return proper status codes
- [ ] Malformed JSON handled correctly
- [ ] No "NoneType is not iterable" errors
- [ ] Server logs errors appropriately

### Performance

- [ ] Response times acceptable (< 5s for simple requests + LLM time)
- [ ] Handles sequential load well
- [ ] Handles concurrent load well
- [ ] No memory leaks detected
- [ ] Server remains stable under load

### Documentation

- [ ] README.md is accurate
- [ ] USAGE.md is helpful
- [ ] CLAUDE.md is comprehensive
- [ ] .env.example is complete
- [ ] Configuration examples work

---

## Test Summary

**Test Date**: _______________

**Tester**: _______________

**Environment**:
- OS: _______________
- Docker Version: _______________
- Python Version: _______________

**Overall Status**: [ ] PASS / [ ] FAIL

**Total Tests Run**: _______

**Tests Passed**: _______

**Tests Failed**: _______

**Critical Issues Found**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

**Minor Issues Found**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

**Recommendations**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

## Sign-off

**Tested By**: _______________________

**Date**: _______________________

**Signature**: _______________________

**Approved for**: [ ] Development [ ] Staging [ ] Production

---

## Appendix: Quick Commands Reference

```bash
# Start proxy
cd docker && docker-compose up -d

# Stop proxy
cd docker && docker-compose down

# View logs
cd docker && docker-compose logs -f litellm-proxy

# Run curl tests
./tests/test_curl.sh

# Check metrics
curl http://localhost:9090/metrics

# Health check
curl http://localhost:8000/health

# Simple test request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10}'
```
