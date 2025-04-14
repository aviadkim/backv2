"""
Script to test the OpenRouter API key.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the utils
sys.path.append(str(Path(__file__).parent.parent))

from utils.openrouter_client import OpenRouterClient

def main():
    """Test the OpenRouter API key."""
    parser = argparse.ArgumentParser(description="Test OpenRouter API key")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
        
    print(f"Testing OpenRouter API key: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Create client
        client = OpenRouterClient(api_key)
        
        # Test with a simple prompt
        prompt = "Hello, I'm testing the OpenRouter API with Optimus Alpha. Please respond with a short greeting."
        
        print("Sending test request to OpenRouter API...")
        response = client.get_completion(prompt, temperature=0.7, max_tokens=50)
        
        print("\nResponse from Optimus Alpha:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        print("\nAPI key is working correctly!")
        return 0
        
    except Exception as e:
        print(f"Error testing API key: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
