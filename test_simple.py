#!/usr/bin/env python
import requests
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing different endpoints...")
    
    # Test admin endpoint first
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/admin/", timeout=5)
        end_time = time.time()
        print(f"Admin endpoint: {response.status_code} in {end_time - start_time:.2f}s")
    except Exception as e:
        print(f"Admin endpoint error: {e}")
    
    # Test papers API with shorter timeout
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/papers/", timeout=3)
        end_time = time.time()
        print(f"Papers API: {response.status_code} in {end_time - start_time:.2f}s")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Papers API error: {e}")

if __name__ == "__main__":
    test_endpoints()
