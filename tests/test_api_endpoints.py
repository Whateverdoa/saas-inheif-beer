#!/usr/bin/env python3
"""Quick API endpoint tester for business setup module."""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_legal_endpoints():
    """Test legal document endpoints (public)."""
    print_header("Testing Legal Document Endpoints")
    
    endpoints = [
        ("/legal/terms", "Terms of Service"),
        ("/legal/privacy", "Privacy Policy"),
        ("/legal/dpa", "Data Processing Agreement"),
        ("/legal/cookies", "Cookie Policy"),
        ("/legal/documents", "List Documents"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if endpoint == "/legal/documents":
                response = requests.get(url)
            else:
                response = requests.get(url, params={"format": "markdown"})
            
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
                if endpoint == "/legal/documents":
                    data = response.json()
                    print(f"   Found {len(data.get('documents', []))} documents")
                else:
                    content = response.text
                    print(f"   Content length: {len(content)} chars")
                results.append(True)
            else:
                print(f"❌ {name}: {response.status_code}")
                print(f"   Error: {response.text[:100]}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Server not running")
            print(f"   Start server with: uvicorn app.main:app --reload --port 8000")
            results.append(False)
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    return all(results)


def test_health_endpoint():
    """Test health check endpoint."""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code == 200:
            print(f"✅ Health check: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
        print("   Start server with: uvicorn app.main:app --reload --port 8000")
        return False


def main():
    """Run API endpoint tests."""
    print_header("API Endpoint Test Suite")
    print(f"Testing against: {BASE_URL}")
    print("Make sure the server is running!")
    
    results = []
    
    # Test health endpoint first
    results.append(("Health Check", test_health_endpoint()))
    
    # Test legal endpoints
    results.append(("Legal Endpoints", test_legal_endpoints()))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("✅ All API tests passed!")
        print("\nNext steps:")
        print("1. Test protected endpoints with Clerk authentication")
        print("2. Test invoice generation endpoints")
        print("3. Test compliance checklist endpoints")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

