"""
Example of how to use the API in a Python script.
"""
import os
import sys
import argparse
import requests
import json

def main():
    """Example of how to use the API."""
    parser = argparse.ArgumentParser(description="API Usage Example")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--host", default="localhost", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Set up the API URL
    api_url = f"http://{args.host}:{args.port}"
    
    # Check the API health
    print("Checking API health...")
    try:
        response = requests.get(f"{api_url}/api/health")
        response.raise_for_status()
        print(f"API health: {response.json()}")
    except Exception as e:
        print(f"Error checking API health: {e}")
        print("Make sure the API server is running.")
        return 1
    
    # Check the OpenRouter API status
    print("\nChecking OpenRouter API status...")
    try:
        response = requests.get(f"{api_url}/api/openrouter/status")
        response.raise_for_status()
        print(f"OpenRouter API status: {response.json()}")
    except Exception as e:
        print(f"Error checking OpenRouter API status: {e}")
        return 1
    
    # Example of using the chat completion endpoint
    print("\nExample of using the chat completion endpoint:")
    try:
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about financial document analysis."}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(f"{api_url}/api/openrouter/chat", json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response from Optimus Alpha:")
        print("-" * 40)
        print(result["choices"][0]["message"]["content"])
        print("-" * 40)
    except Exception as e:
        print(f"Error using chat completion endpoint: {e}")
        return 1
    
    # Example of using the text completion endpoint
    print("\nExample of using the text completion endpoint:")
    try:
        data = {
            "prompt": "Explain how financial document analysis works in 3 sentences.",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(f"{api_url}/api/openrouter/completion", json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response from Optimus Alpha:")
        print("-" * 40)
        print(result["completion"])
        print("-" * 40)
    except Exception as e:
        print(f"Error using text completion endpoint: {e}")
        return 1
    
    print("\nAPI usage examples completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
