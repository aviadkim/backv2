import requests
import sys
import time

def test_endpoint(url, description):
    """Test an API endpoint and print results"""
    print(f"Testing {description} at {url}...")
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        duration = time.time() - start_time
        
        print(f"Status Code: {response.status_code} (in {duration:.2f}s)")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("✓ SUCCESS")
            return True
        else:
            print(f"Error: Unexpected status code {response.status_code}")
            print("✗ FAILED")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Connection failed - {e}")
        print("✗ FAILED")
        return False
    except Exception as e:
        print(f"Error: {type(e).__name__} - {e}")
        print("✗ FAILED")
        return False
    finally:
        print("-" * 60)

def main():
    """Main test function"""
    print("=" * 60)
    print("DevDocs API Test")
    print("=" * 60)
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:24125"
    
    # Define endpoints to test
    endpoints = [
        ("", "Root endpoint"),
        ("/test", "Test endpoint"),
        ("/api/health", "Health endpoint"),
        ("/api/documents", "Documents endpoint"),
        ("/api/tags", "Tags endpoint"),
        ("/api/documents/1", "Specific document endpoint")
    ]
    
    # Test each endpoint
    results = []
    for path, description in endpoints:
        url = f"{base_url}{path}"
        result = test_endpoint(url, description)
        results.append(result)
    
    # Print summary
    print("\nTest Summary:")
    success_count = results.count(True)
    print(f"✓ {success_count}/{len(results)} endpoints passed")
    
    # Return success if all tests passed
    return all(results)

if __name__ == "__main__":
    success = main()
    # Use a non-zero exit code if any tests failed
    sys.exit(0 if success else 1)
