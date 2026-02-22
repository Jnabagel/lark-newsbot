"""Test script for API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_news():
    """Test NewsBot endpoint."""
    print("\n2. Testing NewsBot...")
    response = requests.post(f"{BASE_URL}/news/run")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result.get('success')}")
    print(f"   Headlines Count: {result.get('headlines_count')}")
    print(f"   Execution Time: {result.get('execution_time_seconds', 0):.2f}s")
    if result.get('summary'):
        print(f"   Summary Preview: {result['summary'][:100]}...")
    return response.status_code == 200

def test_compliance(question: str = "What are the key compliance requirements?"):
    """Test ComplianceSME endpoint."""
    print(f"\n3. Testing ComplianceSME with question: '{question}'...")
    response = requests.post(
        f"{BASE_URL}/compliance/query",
        json={"question": question}
    )
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Answer: {result.get('answer', 'N/A')[:200]}...")
    print(f"   Sources: {result.get('sources', [])}")
    print(f"   Confidence: {result.get('confidence')}")
    print(f"   Execution Time: {result.get('execution_time_seconds', 0):.2f}s")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent Platform - Endpoint Testing")
    print("=" * 60)
    
    try:
        # Test health
        health_ok = test_health()
        
        if health_ok:
            # Test NewsBot
            test_news()
            
            # Test ComplianceSME
            test_compliance()
            
            print("\n" + "=" * 60)
            print("Testing Complete!")
            print("=" * 60)
        else:
            print("\n❌ Server is not running. Please start the server first.")
            print("   Run: python run.py")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Is it running?")
        print("   Start the server with: python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
