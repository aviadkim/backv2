#!/usr/bin/env python3
"""
Test script for OpenRouter API integration.
"""
import os
import sys
import argparse
import requests
from pathlib import Path

def main():
    """Test the OpenRouter API integration."""
    parser = argparse.ArgumentParser(description="Test OpenRouter API integration")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--prompt", default="Hello, I'm testing the OpenRouter API with Optimus Alpha. Please respond with a short greeting.", help="Prompt to send to the API")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Set up the API URL
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Set up the headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://backv2.com",
        "X-Title": "FinDoc Analyzer"
    }
    
    # Set up the data
    data = {
        "model": "openrouter/optimus-alpha",
        "messages": [
            {"role": "user", "content": args.prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    # Send the request
    print(f"Testing OpenRouter API key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Sending prompt: {args.prompt}")
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        print("\nResponse from Optimus Alpha:")
        print("-" * 40)
        print(result["choices"][0]["message"]["content"])
        print("-" * 40)
        
        print("\nAPI key is working correctly!")
        return 0
    except Exception as e:
        print(f"Error testing API key: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
