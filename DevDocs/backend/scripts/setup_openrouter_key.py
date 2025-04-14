"""
Script to set up the OpenRouter API key for the financial document processing system.
"""
import os
import sys
import argparse
from pathlib import Path

def main():
    """Set up the OpenRouter API key."""
    parser = argparse.ArgumentParser(description="Set up OpenRouter API key")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")
    args = parser.parse_args()
    
    # Get API key from arguments or prompt
    api_key = args.api_key
    if not api_key:
        api_key = input("Enter your OpenRouter API key (starts with 'sk-or-'): ")
        
    # Validate API key
    if not api_key.startswith("sk-or-"):
        print("Error: Invalid OpenRouter API key. It should start with 'sk-or-'.")
        return 1
        
    # Create or update .env file
    env_file = Path(args.env_file)
    
    # Read existing .env file if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    
    # Update API key
    env_vars["OPENROUTER_API_KEY"] = api_key
    
    # Write updated .env file
    with open(env_file, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"OpenRouter API key saved to {env_file}")
    print("You can now use the API key in your applications by setting the OPENROUTER_API_KEY environment variable.")
    print("For example:")
    print(f"  export OPENROUTER_API_KEY={api_key}")
    
    # Set environment variable for current session
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
