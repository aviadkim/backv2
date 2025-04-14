"""
Script to run the API server.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description="Run API Server")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Set the API key
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    # Run the API server
    print(f"Starting API server on {args.host}:{args.port}...")
    
    # Build the command
    command = [
        sys.executable,
        "backend/api_server.py",
        f"--host={args.host}",
        f"--port={args.port}"
    ]
    
    if args.reload:
        command.append("--reload")
    
    # Run the command
    try:
        subprocess.run(command, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running API server: {e}")
        return 1
    except KeyboardInterrupt:
        print("API server stopped.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
