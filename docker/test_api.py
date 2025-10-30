#!/usr/bin/env python3
"""
LiteLLM Proxy Docker Container API Test Script

This script tests if the LiteLLM proxy API is working correctly after
starting the Docker container.

Usage:
    python test_api.py              # Test localhost:8000
    python test_api.py <host:port>  # Test custom host/port

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import json
import sys
import time
from typing import Tuple

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found.")
    print("Install it with: pip install requests")
    sys.exit(1)

# Configuration
PROXY_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
TIMEOUT = 10
FAILED_TESTS = 0
PASSED_TESTS = 0

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"{Colors.BLUE}{'=' * 64}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 64}{Colors.NC}")

def print_test(text: str) -> None:
    """Print test name."""
    print(f"\n{Colors.YELLOW}▶ {text}{Colors.NC}")

def print_success(text: str) -> None:
    """Print success message."""
    global PASSED_TESTS
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")
    PASSED_TESTS += 1

def print_error(text: str) -> None:
    """Print error message."""
    global FAILED_TESTS
    print(f"{Colors.RED}✗ {text}{Colors.NC}")
    FAILED_TESTS += 1

def print_info(text: str) -> None:
    """Print info message."""
    print(f"  {text}")

def test_health_check() -> bool:
    """Test health check endpoint."""
    print_test("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{PROXY_URL}/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            print_success("Health check endpoint responded with 200 OK")
            print_info(f"Response: {response.text}")
            return True
        else:
            print_error(f"Health check failed (HTTP {response.status_code})")
            print_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {e}")
        return False

def test_list_models() -> bool:
    """Test list models endpoint."""
    print_test("Testing List Models Endpoint")
    
    try:
        response = requests.get(f"{PROXY_URL}/v1/models", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if response contains "data" field (OpenAI format)
            if "data" in data:
                model_count = len(data["data"])
                print_success(f"Models endpoint responded with {model_count} models")
                print_info(f"Sample: {json.dumps(data)[:200]}...")
                return True
            else:
                print_error("Models endpoint response missing 'data' field")
                print_info(f"Response: {response.text}")
                return False
        else:
            print_error(f"Models endpoint failed (HTTP {response.status_code})")
            print_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Models endpoint failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {e}")
        return False

def test_chat_completion() -> bool:
    """Test chat completion endpoint."""
    print_test("Testing Chat Completion Endpoint (Basic)")
    
    payload = {
        "model": "gpt-5-mini",
        "messages": [
            {"role": "user", "content": "Say hello"}
        ],
        "max_tokens": 10
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user",
        "X-Session-ID": "test-session"
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if response contains expected fields
            if "choices" in data and "usage" in data:
                print_success("Chat completion endpoint working correctly")
                print_info(f"Sample: {json.dumps(data)[:150]}...")
                return True
            else:
                print_error("Chat completion response missing required fields")
                print_info(f"Response: {response.text}")
                return False
        else:
            print_error(f"Chat completion failed (HTTP {response.status_code})")
            print_info(f"Response: {response.text}")
            
            # Provide helpful hints for common errors
            if response.status_code == 401:
                print_info("Hint: Check if API keys are configured in .env file")
            elif response.status_code == 500:
                print_info("Hint: Check docker logs with: docker compose logs litellm-proxy")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Chat completion failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {e}")
        return False

def test_metrics_endpoint() -> bool:
    """Test Prometheus metrics endpoint."""
    print_test("Testing Prometheus Metrics Endpoint")
    
    # Replace port 8000 with 9090 for metrics
    metrics_url = PROXY_URL.replace(":8000", ":9090") + "/metrics"
    
    try:
        response = requests.get(metrics_url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            # Check if response contains prometheus metrics
            if "# HELP" in response.text or "# TYPE" in response.text:
                print_success("Metrics endpoint is accessible")
                metric_count = response.text.count("litellm_")
                print_info(f"Found {metric_count} LiteLLM metrics")
                return True
            else:
                print_error("Metrics endpoint response doesn't look like Prometheus format")
                return False
        else:
            print_error(f"Metrics endpoint failed (HTTP {response.status_code})")
            print_info("Note: Metrics may be disabled or on different port")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Metrics endpoint not accessible: {e}")
        print_info("Note: Metrics may be disabled or on different port")
        return False

def test_container_status() -> bool:
    """Test Docker container status."""
    print_test("Testing Docker Container Status")
    
    try:
        import subprocess
        
        # Try to find the container
        container_name = "litellm-proxy-langfuse"
        
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if container_name in result.stdout:
            print_success(f"Container '{container_name}' is running")
            
            # Get container status
            status_result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if status_result.returncode == 0:
                print_info(f"Status: {status_result.stdout.strip()}")
            
            return True
        else:
            print_error(f"Container '{container_name}' not found or not running")
            print_info("Start with: cd docker && docker compose up -d")
            return False
            
    except FileNotFoundError:
        print_error("Docker command not found")
        return False
    except subprocess.TimeoutExpired:
        print_error("Docker command timed out")
        return False
    except Exception as e:
        print_error(f"Could not check container status: {e}")
        return False

def main() -> int:
    """Main execution function."""
    print_header("LiteLLM Proxy Docker Container API Tests")
    print(f"Testing proxy at: {Colors.YELLOW}{PROXY_URL}{Colors.NC}\n")
    
    # Check if proxy is reachable
    print_test("Checking if proxy is reachable")
    try:
        response = requests.get(f"{PROXY_URL}/health", timeout=5)
        print_success("Proxy is reachable")
    except requests.exceptions.RequestException:
        print_error(f"Cannot reach proxy at {PROXY_URL}")
        print_info("Make sure the Docker container is running:")
        print_info("  cd docker && docker compose up -d")
        return 1
    
    # Run tests (some are optional)
    test_container_status()  # Optional - don't fail if Docker not available
    test_health_check()
    test_list_models()
    test_chat_completion()
    test_metrics_endpoint()  # Optional - don't fail if metrics are disabled
    
    # Print summary
    print()
    print_header("Test Summary")
    print(f"Passed: {Colors.GREEN}{PASSED_TESTS}{Colors.NC}")
    print(f"Failed: {Colors.RED}{FAILED_TESTS}{Colors.NC}")
    print()
    
    if FAILED_TESTS == 0:
        print(f"{Colors.GREEN}✓ All tests passed! API is working correctly.{Colors.NC}")
        print()
        print("Next steps:")
        print("  1. View logs: docker compose logs -f litellm-proxy")
        print("  2. Check LangFuse dashboard for traces")
        print("  3. Run full test suite: python examples/test_requests.py")
        return 0
    else:
        print(f"{Colors.RED}✗ Some tests failed. Check the output above for details.{Colors.NC}")
        print()
        print("Troubleshooting:")
        print("  1. Check logs: docker compose logs litellm-proxy")
        print("  2. Verify .env file has required API keys")
        print("  3. Ensure container is running: docker compose ps")
        return 1

if __name__ == "__main__":
    sys.exit(main())
