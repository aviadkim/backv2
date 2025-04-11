import requests
import sys

def test_endpoint(url, name):
    """Test an endpoint and print the response"""
    print(f"Testing {name} endpoint at {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    base_url = "http://localhost:24125"
    
    print("Testing DevDocs API endpoints...")
    
    # Test root endpoint
    test_endpoint(f"{base_url}/", "Root")
    
    # Test health endpoint
    test_endpoint(f"{base_url}/api/health", "Health")
    
    # Test documents endpoint
    test_endpoint(f"{base_url}/api/documents", "Documents")
    
    # Test tags endpoint
    test_endpoint(f"{base_url}/api/tags", "Tags")
    
    print("Testing complete.")

if __name__ == "__main__":
    main()
