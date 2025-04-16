"""
Test OpenRouter API keys with financial document analysis.
"""
import os
import json
import sys
import argparse
import requests
from pathlib import Path
import time

# List of API keys to test
API_KEYS = [
    {"key": "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", "model": "deepseek-ai/deepseek-v3", "name": "DeepSeek v3"},
    {"key": "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", "model": "deepseek-ai/deepseek-v1", "name": "DeepSeek v1"},
    {"key": "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", "model": "anthropic/claude-3-opus", "name": "Optimus1"},
    {"key": "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", "model": "google/gemini-1.5-pro", "name": "Gemini Finance"},
    {"key": "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", "model": "meta-llama/llama-3-70b-instruct", "name": "Llama Scout 4"},
    {"key": "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", "model": "google/gemini-1.5-flash", "name": "Gemini 2 Flash"},
    {"key": "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", "model": "anthropic/claude-3-haiku", "name": "Quaser"},
    {"key": "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", "model": "anthropic/claude-3-haiku", "name": "Quaser2"}
]

def test_api_key(api_key, model, name, extracted_data_path="test_output/messos_extraction.json"):
    """Test an OpenRouter API key."""
    print(f"\n=== Testing API Key: {name} ({model}) ===")
    
    # Load extracted data
    with open(extracted_data_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)
    
    # Create a simple prompt
    prompt = f"""
    You are a financial document analysis expert. Please analyze this financial document data:
    
    Client: {extracted_data.get('client_info', {})}
    Document date: {extracted_data.get('document_date')}
    Portfolio value: {extracted_data.get('portfolio_value')}
    
    What is the total portfolio value? Who is the client?
    """
    
    # Call OpenRouter API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/aviadkim/backv2",
        "X-Title": "Financial Document Analysis",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a financial document analysis expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    try:
        print(f"Calling OpenRouter API with {name}...")
        start_time = time.time()
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            response_json = response.json()
            answer = response_json["choices"][0]["message"]["content"]
            print(f"Success! Response time: {end_time - start_time:.2f} seconds")
            print(f"Answer: {answer[:100]}...")
            return {
                "name": name,
                "model": model,
                "key": api_key,
                "status": "success",
                "response_time": end_time - start_time,
                "answer": answer
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {
                "name": name,
                "model": model,
                "key": api_key,
                "status": "error",
                "error_code": response.status_code,
                "error_message": response.text
            }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            "name": name,
            "model": model,
            "key": api_key,
            "status": "exception",
            "error_message": str(e)
        }

def main():
    """Main function."""
    # Create output directory
    os.makedirs("api_test_results", exist_ok=True)
    
    # Test each API key
    results = []
    for api_key_info in API_KEYS:
        result = test_api_key(
            api_key_info["key"],
            api_key_info["model"],
            api_key_info["name"]
        )
        results.append(result)
        
        # Save individual result
        with open(f"api_test_results/{api_key_info['name'].replace(' ', '_').lower()}_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        
        # Wait a bit between requests
        time.sleep(2)
    
    # Save all results
    with open("api_test_results/all_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== API Key Test Summary ===")
    for result in results:
        status = result["status"]
        name = result["name"]
        if status == "success":
            print(f"✅ {name}: Success (Response time: {result['response_time']:.2f}s)")
        else:
            print(f"❌ {name}: Failed ({status})")
    
    # Identify best performing keys
    successful_results = [r for r in results if r["status"] == "success"]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x["response_time"])
        print(f"\nFastest API key: {fastest['name']} ({fastest['response_time']:.2f}s)")
        
        print("\nRecommended API keys to keep:")
        for result in successful_results:
            print(f"- {result['name']} ({result['model']}): {result['key']}")
    else:
        print("\nNo successful API keys found.")

if __name__ == "__main__":
    main()
