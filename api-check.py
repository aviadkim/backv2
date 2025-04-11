import sys
import requests
from urllib.parse import urljoin

def check_api(base_url):
    """Check if the API is running and accessible"""
    endpoints = [
        "/",
        "/api/health",
        "/api/documents",
        "/api/tags"
    ]
    
    print(f"Checking API at {base_url}")
    print("=" * 50)
    
    success = True
    
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=3)
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {response.json()}")
                print("  ✓ Success")
            else:
                print(f"  ✗ Failed - Status code: {response.status_code}")
                success = False
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            success = False
        
        print("-" * 50)
    
    print("\nSummary:")
    if success:
        print("✓ All API endpoints are working correctly")
    else:
        print("✗ Some API endpoints failed")
    
if __name__ == "__main__":
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:24125"
    check_api(api_url)
