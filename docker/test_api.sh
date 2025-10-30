#!/bin/bash

################################################################################
# LiteLLM Proxy Docker Container API Test Script
################################################################################
# This script tests if the LiteLLM proxy API is working correctly after
# starting the Docker container.
#
# Usage:
#   ./test_api.sh              # Test localhost:8000
#   ./test_api.sh <host:port>  # Test custom host/port
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
################################################################################

set -e

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

# Test functions
test_health_check() {
    print_test "Testing Health Check Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/health" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        print_success "Health check endpoint responded with 200 OK"
        print_info "Response: $body"
        return 0
    else
        print_error "Health check failed (HTTP $http_code)"
        print_info "Response: $body"
        return 1
    fi
}

test_list_models() {
    print_test "Testing List Models Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${PROXY_URL}/v1/models" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        # Check if response contains "data" field (OpenAI format)
        if echo "$body" | grep -q '"data"'; then
            model_count=$(echo "$body" | grep -o '"id"' | wc -l)
            print_success "Models endpoint responded with $model_count models"
            print_info "Sample: $(echo "$body" | head -c 200)..."
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

test_chat_completion() {
    print_test "Testing Chat Completion Endpoint (Basic)"
    
    # Simple test request
    payload='{
        "model": "gpt-5-mini",
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
    
    if [ "$http_code" = "200" ]; then
        # Check if response contains expected fields
        if echo "$body" | grep -q '"choices"' && echo "$body" | grep -q '"usage"'; then
            print_success "Chat completion endpoint working correctly"
            print_info "Sample: $(echo "$body" | head -c 150)..."
            return 0
        else
            print_error "Chat completion response missing required fields"
            print_info "Response: $body"
            return 1
        fi
    else
        print_error "Chat completion failed (HTTP $http_code)"
        print_info "Response: $body"
        
        # Provide helpful hints for common errors
        if [ "$http_code" = "401" ]; then
            print_info "Hint: Check if API keys are configured in .env file"
        elif [ "$http_code" = "500" ]; then
            print_info "Hint: Check docker logs with: docker compose logs litellm-proxy"
        fi
        return 1
    fi
}

test_metrics_endpoint() {
    print_test "Testing Prometheus Metrics Endpoint"
    
    metrics_url=$(echo "$PROXY_URL" | sed 's/:8000/:9090/')/metrics
    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$metrics_url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        # Check if response contains prometheus metrics
        if echo "$body" | grep -q "# HELP\|# TYPE"; then
            print_success "Metrics endpoint is accessible"
            metric_count=$(echo "$body" | grep -c "^litellm_" || echo "0")
            print_info "Found $metric_count LiteLLM metrics"
            return 0
        else
            print_error "Metrics endpoint response doesn't look like Prometheus format"
            return 1
        fi
    else
        print_error "Metrics endpoint failed (HTTP $http_code)"
        print_info "Note: Metrics may be disabled or on different port"
        return 1
    fi
}

test_container_status() {
    print_test "Testing Docker Container Status"
    
    # Check if docker/docker compose is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker command not found"
        return 1
    fi
    
    # Try to find the container
    container_name="litellm-proxy-langfuse"
    
    if docker ps --format "{{.Names}}" | grep -q "$container_name"; then
        container_status=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null)
        container_health=$(docker inspect -f '{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        
        print_success "Container '$container_name' is running"
        print_info "Status: $container_status"
        
        if [ "$container_health" != "none" ] && [ "$container_health" != "<no value>" ]; then
            print_info "Health: $container_health"
        fi
        return 0
    else
        print_error "Container '$container_name' not found or not running"
        print_info "Start with: cd docker && docker compose up -d"
        return 1
    fi
}

# Main execution
main() {
    print_header "LiteLLM Proxy Docker Container API Tests"
    echo -e "Testing proxy at: ${YELLOW}${PROXY_URL}${NC}\n"
    
    # Check if proxy is reachable
    print_test "Checking if proxy is reachable"
    if curl -s --max-time 5 "${PROXY_URL}/health" > /dev/null 2>&1; then
        print_success "Proxy is reachable"
    else
        print_error "Cannot reach proxy at ${PROXY_URL}"
        print_info "Make sure the Docker container is running:"
        print_info "  cd docker && docker compose up -d"
        exit 1
    fi
    
    # Run tests
    test_container_status || true  # Don't fail on this one
    test_health_check || true
    test_list_models || true
    test_chat_completion || true
    test_metrics_endpoint || true  # Don't fail if metrics are disabled
    
    # Print summary
    echo ""
    print_header "Test Summary"
    echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
    echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed! API is working correctly.${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. View logs: docker compose logs -f litellm-proxy"
        echo "  2. Check LangFuse dashboard for traces"
        echo "  3. Run full test suite: python examples/test_requests.py"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed. Check the output above for details.${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check logs: docker compose logs litellm-proxy"
        echo "  2. Verify .env file has required API keys"
        echo "  3. Ensure container is running: docker compose ps"
        exit 1
    fi
}

# Run main function
main
