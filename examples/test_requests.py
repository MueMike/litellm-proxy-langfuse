"""Example test requests for LiteLLM Proxy with LangFuse integration."""

import json
import time

import requests

# Configuration
PROXY_URL = "http://localhost:8000"
API_KEY = "dummy-key-if-auth-disabled"  # Change if authentication is enabled


def test_health_check():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{PROXY_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_list_models():
    """Test list models endpoint."""
    print("\n=== Testing List Models ===")
    response = requests.get(f"{PROXY_URL}/v1/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_chat_completion(model="gpt-5-mini", user_id="test-user", session_id=None):
    """Test chat completion endpoint."""
    print(f"\n=== Testing Chat Completion with {model} ===")
    
    if session_id is None:
        session_id = f"test-session-{int(time.time())}"
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": user_id,
        "X-Session-ID": session_id,
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful coding assistant.",
            },
            {
                "role": "user",
                "content": "Write a simple Python function to calculate factorial.",
            },
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "metadata": {
            "task_type": "code_generation",
            "language": "python",
            "feature": "factorial_function",
        },
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Model: {result.get('model')}")
            print(f"Usage: {json.dumps(result.get('usage', {}), indent=2)}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if result.get("choices"):
                print(f"\nGenerated Code:\n{result['choices'][0]['message']['content']}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_cpp_unit_test_generation():
    """Test C++ unit test generation use case."""
    print("\n=== Testing C++ Unit Test Generation ===")
    
    session_id = f"cpp-unittest-{int(time.time())}"
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "developer-cpp",
        "X-Session-ID": session_id,
    }
    
    data = {
        "model": "gpt-5",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert C++ developer specializing in unit tests with Google Test.",
            },
            {
                "role": "user",
                "content": """Generate comprehensive unit tests for this C++ function:

```cpp
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

Use Google Test framework and cover edge cases.""",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 1000,
        "metadata": {
            "task_type": "unit_test_generation",
            "language": "cpp",
            "framework": "googletest",
            "function": "fibonacci",
        },
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Trace ID: {response.headers.get('X-Trace-ID')}")
            print(f"Duration: {response.headers.get('X-Duration-Ms')}ms")
            print(f"Usage: {json.dumps(result.get('usage', {}), indent=2)}")
            
            if result.get("choices"):
                print(f"\nGenerated Unit Tests:\n{result['choices'][0]['message']['content']}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False


def test_streaming_completion():
    """Test streaming chat completion."""
    print("\n=== Testing Streaming Completion ===")
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user",
        "X-Session-ID": f"stream-session-{int(time.time())}",
    }
    
    data = {
        "model": "gpt-5-mini",
        "messages": [
            {
                "role": "user",
                "content": "Count from 1 to 5 slowly.",
            },
        ],
        "stream": True,
        "max_tokens": 100,
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=60,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    print(line.decode("utf-8"))
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False


def run_all_tests():
    """Run all test cases."""
    print("=" * 80)
    print("LiteLLM Proxy with LangFuse - Test Suite")
    print("=" * 80)
    
    tests = [
        ("Health Check", test_health_check),
        ("List Models", test_list_models),
        ("Chat Completion (GPT-5 Mini)", lambda: test_chat_completion("gpt-5-mini")),
        ("C++ Unit Test Generation (GPT-5)", test_cpp_unit_test_generation),
        # Uncomment to test other latest models (requires API keys)
        # ("Chat Completion (GPT-5)", lambda: test_chat_completion("gpt-5")),
        # ("Chat Completion (GPT-4.1)", lambda: test_chat_completion("gpt-4.1")),
        # ("Chat Completion (Claude Sonnet 4.5)", lambda: test_chat_completion("claude-sonnet-4-5")),
        # ("Chat Completion (Claude Opus 4.1)", lambda: test_chat_completion("claude-opus-4-1")),
        # ("Streaming Completion", test_streaming_completion),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nTest '{test_name}' failed with exception: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    run_all_tests()
