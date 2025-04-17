import requests
import json

# OpenRouter API key
OPENROUTER_API_KEY = "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"

def test_openrouter_key():
    url = "https://openrouter.ai/api/v1/auth/key"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("API key is valid!")
        else:
            print("API key is invalid or expired.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_openrouter_key()
