"""
Main entry point for the FastAPI application.
"""
import os
import uvicorn
import argparse

def main():
    """Run the FastAPI application."""
    parser = argparse.ArgumentParser(description="Financial Document Processing API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()

    # Set the API key if provided
    if args.api_key:
        os.environ["OPENROUTER_API_KEY"] = args.api_key

    uvicorn.run(
        "api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
