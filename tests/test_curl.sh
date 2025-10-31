#!/bin/bash

################################################################################
# Comprehensive cURL Tests for LiteLLM Proxy
################################################################################
# This script tests various curl scenarios for the LiteLLM proxy API
#
# Usage:
#   ./test_curl.sh              # Test localhost:8000
#   ./test_curl.sh <host:port>  # Test custom host/port
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
################################################################################

# Configuration
PROXY_URL="${1:-http://localhost:8000}"
TIMEOUT=10
FAILED_TESTS=0
PASSED_TESTS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_test() {
    echo -e "\n${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "  $1"
}

# Test 1: Health check endpoint
test_health_check() {
    print_test "Test 1: Health Check Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/health" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status".*"healthy"'; then
            print_success "Health check passed"
            print_info "Response: $body"
            return 0
        else
            print_error "Health check returned unexpected body"
            print_info "Response: $body"
            return 1
        fi
    else
        print_error "Health check failed (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 2: Readiness check endpoint
test_readiness_check() {
    print_test "Test 2: Readiness Check Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/ready" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"status".*"ready"'; then
            print_success "Readiness check passed"
            print_info "Response: $body"
            return 0
        else
            print_error "Readiness check returned unexpected body"
            print_info "Response: $body"
            return 1
        fi
    else
        print_error "Readiness check failed (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 3: List models endpoint (v1 path)
test_list_models_v1() {
    print_test "Test 3: List Models Endpoint (/v1/models)"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/v1/models" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"data"'; then
            model_count=$(echo "$body" | grep -o '"id"' | wc -l)
            print_success "Models endpoint passed ($model_count models found)"
            print_info "Sample: $(echo "$body" | head -c 150)..."
            return 0
        else
            print_error "Models endpoint response missing 'data' field"
            print_info "Response: $body"
            return 1
        fi
    else
        print_error "Models endpoint failed (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 4: List models endpoint (alternative path)
test_list_models_alt() {
    print_test "Test 4: List Models Endpoint (/models)"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/models" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"data"'; then
            print_success "Alternative models endpoint passed"
            return 0
        else
            print_error "Alternative models endpoint response missing 'data' field"
            print_info "Response: $body"
            return 1
        fi
    else
        print_error "Alternative models endpoint failed (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 5: Chat completion with valid request (no API key - expected to fail gracefully)
test_chat_completion_no_api_key() {
    print_test "Test 5: Chat Completion Without API Key (Expected Error)"
    
    payload='{
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Say hello"}
        ],
        "max_tokens": 10
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "X-User-ID: test-user" \
        -H "X-Session-ID: test-session" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # We expect this to fail with 500 due to missing API key
    # But it should return a proper JSON error, not "NoneType is not iterable"
    if [ "$http_code" = "500" ]; then
        if echo "$body" | grep -q "AuthenticationError\|api_key"; then
            print_success "Chat completion failed as expected with proper error message"
            print_info "Error: $(echo "$body" | head -c 100)..."
            return 0
        elif echo "$body" | grep -q "NoneType.*not iterable"; then
            print_error "Chat completion failed with NoneType error (BUG DETECTED)"
            print_info "Response: $body"
            return 1
        else
            print_error "Chat completion failed with unexpected error"
            print_info "Response: $body"
            return 1
        fi
    elif [ "$http_code" = "200" ]; then
        print_success "Chat completion succeeded unexpectedly (API key configured?)"
        return 0
    else
        print_error "Chat completion returned unexpected status code (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 6: Chat completion without Content-Type header
test_chat_completion_no_content_type() {
    print_test "Test 6: Chat Completion Without Content-Type Header"
    
    payload='{"model":"gpt-4","messages":[{"role":"user","content":"hello"}]}'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should return 422 (Unprocessable Entity) or similar, not "NoneType is not iterable"
    if [ "$http_code" = "422" ] || [ "$http_code" = "400" ]; then
        if echo "$body" | grep -q "NoneType.*not iterable"; then
            print_error "Request without Content-Type header caused NoneType error (BUG DETECTED)"
            print_info "Response: $body"
            return 1
        else
            print_success "Request without Content-Type header handled gracefully"
            print_info "Error: $(echo "$body" | head -c 100)..."
            return 0
        fi
    else
        print_error "Request without Content-Type header returned unexpected status (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 7: Chat completion with missing required field (messages)
test_chat_completion_missing_messages() {
    print_test "Test 7: Chat Completion With Missing Messages Field"
    
    payload='{
        "model": "gpt-4"
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should return 422 (validation error), not "NoneType is not iterable"
    if [ "$http_code" = "422" ]; then
        if echo "$body" | grep -q "NoneType.*not iterable"; then
            print_error "Missing messages field caused NoneType error (BUG DETECTED)"
            print_info "Response: $body"
            return 1
        else
            print_success "Missing messages field handled with proper validation error"
            print_info "Error: $(echo "$body" | head -c 100)..."
            return 0
        fi
    else
        print_error "Missing messages field returned unexpected status (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 8: Chat completion with empty messages array
test_chat_completion_empty_messages() {
    print_test "Test 8: Chat Completion With Empty Messages Array"
    
    payload='{
        "model": "gpt-4",
        "messages": []
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should fail gracefully, not with "NoneType is not iterable"
    if echo "$body" | grep -q "NoneType.*not iterable"; then
        print_error "Empty messages array caused NoneType error (BUG DETECTED)"
        print_info "Response: $body"
        return 1
    else
        print_success "Empty messages array handled gracefully"
        print_info "Response: $(echo "$body" | head -c 100)..."
        return 0
    fi
}

# Test 9: Chat completion with null messages
test_chat_completion_null_messages() {
    print_test "Test 9: Chat Completion With Null Messages"
    
    payload='{
        "model": "gpt-4",
        "messages": null
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should return validation error, not "NoneType is not iterable"
    if [ "$http_code" = "422" ]; then
        if echo "$body" | grep -q "NoneType.*not iterable"; then
            print_error "Null messages caused NoneType error (BUG DETECTED)"
            print_info "Response: $body"
            return 1
        else
            print_success "Null messages handled with proper validation error"
            print_info "Error: $(echo "$body" | head -c 100)..."
            return 0
        fi
    else
        print_error "Null messages returned unexpected status (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 10: Chat completion with malformed JSON
test_chat_completion_malformed_json() {
    print_test "Test 10: Chat Completion With Malformed JSON"
    
    payload='{"model":"gpt-4","messages":[{"role":"user","content":"hello"}'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should return JSON parse error, not "NoneType is not iterable"
    if echo "$body" | grep -q "NoneType.*not iterable"; then
        print_error "Malformed JSON caused NoneType error (BUG DETECTED)"
        print_info "Response: $body"
        return 1
    else
        print_success "Malformed JSON handled gracefully"
        print_info "Response: $(echo "$body" | head -c 100)..."
        return 0
    fi
}

# Test 11: Chat completion with optional null metadata
test_chat_completion_null_metadata() {
    print_test "Test 11: Chat Completion With Null Metadata"
    
    payload='{
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "hello"}],
        "metadata": null
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Null metadata should be acceptable, not cause "NoneType is not iterable"
    if echo "$body" | grep -q "NoneType.*not iterable"; then
        print_error "Null metadata caused NoneType error (BUG DETECTED)"
        print_info "Response: $body"
        return 1
    else
        print_success "Null metadata handled gracefully"
        print_info "Response: $(echo "$body" | head -c 100)..."
        return 0
    fi
}

# Test 12: Chat completion alternative endpoint
test_chat_completion_alt_endpoint() {
    print_test "Test 12: Chat Completion Alternative Endpoint (/chat/completions)"
    
    payload='{
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "hello"}]
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should work the same as /v1/chat/completions
    if echo "$body" | grep -q "NoneType.*not iterable"; then
        print_error "Alternative endpoint caused NoneType error (BUG DETECTED)"
        print_info "Response: $body"
        return 1
    else
        print_success "Alternative endpoint handled gracefully"
        print_info "Response: $(echo "$body" | head -c 100)..."
        return 0
    fi
}

# Test 13: GET request on POST-only endpoint
test_get_on_post_endpoint() {
    print_test "Test 13: GET Request On POST-Only Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X GET "${PROXY_URL}/v1/chat/completions" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should return 405 Method Not Allowed, not "NoneType is not iterable"
    if [ "$http_code" = "405" ]; then
        if echo "$body" | grep -q "NoneType.*not iterable"; then
            print_error "GET on POST endpoint caused NoneType error (BUG DETECTED)"
            print_info "Response: $body"
            return 1
        else
            print_success "GET on POST endpoint handled correctly"
            return 0
        fi
    else
        print_error "GET on POST endpoint returned unexpected status (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

# Test 14: OPTIONS request (CORS preflight)
test_options_request() {
    print_test "Test 14: OPTIONS Request (CORS Preflight)"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X OPTIONS "${PROXY_URL}/v1/chat/completions" \
        -H "Origin: http://example.com" \
        -H "Access-Control-Request-Method: POST" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    
    # Should return 200 for CORS preflight
    if [ "$http_code" = "200" ]; then
        print_success "OPTIONS request handled correctly"
        return 0
    else
        print_error "OPTIONS request returned unexpected status (HTTP $http_code)"
        return 1
    fi
}

# Test 15: Request with custom headers
test_custom_headers() {
    print_test "Test 15: Request With Custom Headers (X-User-ID, X-Session-ID)"
    
    payload='{
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "hello"}]
    }'
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
        -X POST "${PROXY_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "X-User-ID: test-user-123" \
        -H "X-Session-ID: session-abc-456" \
        -d "$payload" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Should handle custom headers gracefully
    if echo "$body" | grep -q "NoneType.*not iterable"; then
        print_error "Custom headers caused NoneType error (BUG DETECTED)"
        print_info "Response: $body"
        return 1
    else
        print_success "Custom headers handled gracefully"
        return 0
    fi
}

# Main execution
main() {
    print_header "LiteLLM Proxy Comprehensive cURL Tests"
    echo -e "Testing proxy at: ${YELLOW}${PROXY_URL}${NC}\n"
    
    # Check if proxy is reachable
    print_test "Checking if proxy is reachable"
    if curl -s --max-time 5 "${PROXY_URL}/health" > /dev/null 2>&1; then
        print_success "Proxy is reachable"
    else
        print_error "Cannot reach proxy at ${PROXY_URL}"
        print_info "Make sure the server is running:"
        print_info "  python -m uvicorn src.proxy.server:create_app --factory --host 0.0.0.0 --port 8000"
        exit 1
    fi
    
    # Run all tests
    test_health_check || true
    test_readiness_check || true
    test_list_models_v1 || true
    test_list_models_alt || true
    test_chat_completion_no_api_key || true
    test_chat_completion_no_content_type || true
    test_chat_completion_missing_messages || true
    test_chat_completion_empty_messages || true
    test_chat_completion_null_messages || true
    test_chat_completion_malformed_json || true
    test_chat_completion_null_metadata || true
    test_chat_completion_alt_endpoint || true
    test_get_on_post_endpoint || true
    test_options_request || true
    test_custom_headers || true
    
    # Print summary
    echo ""
    print_header "Test Summary"
    echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
    echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed! No NoneType errors detected.${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed. Review the output above for details.${NC}"
        exit 1
    fi
}

# Run main function
main
