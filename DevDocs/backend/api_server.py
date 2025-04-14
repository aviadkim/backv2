"""
Simple FastAPI server for testing the OpenRouter integration.
"""
import os
import uvicorn
import argparse
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from utils.openrouter_client import OpenRouterClient

app = FastAPI(
    title="OpenRouter API Test",
    description="Simple API for testing the OpenRouter integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    print(f"Warning: Static directory not found: {static_dir}")

class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[Dict[str, Any]]
    model: Optional[str] = "openrouter/optimus-alpha"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class CompletionRequest(BaseModel):
    """Completion request model."""
    prompt: str
    model: Optional[str] = "openrouter/optimus-alpha"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

def get_openrouter_client():
    """Get the OpenRouter client."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        return OpenRouterClient(api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize OpenRouter client: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    # Check if the static directory exists
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"

    if index_file.exists():
        # Redirect to the static index.html file
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")
    else:
        # Return a simple JSON response
        return {
            "message": "OpenRouter API Test",
            "version": "1.0.0",
            "status": "running"
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.environ.get("OPENROUTER_API_KEY"))
    }

@app.post("/api/chat")
async def chat_completion(request: ChatRequest, client: OpenRouterClient = Depends(get_openrouter_client)):
    """
    Chat completion endpoint.

    Args:
        request: Chat request
        client: OpenRouter client

    Returns:
        Chat completion response
    """
    try:
        response = client.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API request failed: {str(e)}")

@app.post("/api/completion")
async def text_completion(request: CompletionRequest, client: OpenRouterClient = Depends(get_openrouter_client)):
    """
    Text completion endpoint.

    Args:
        request: Completion request
        client: OpenRouter client

    Returns:
        Text completion response
    """
    try:
        response = client.get_completion(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return {"completion": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API request failed: {str(e)}")

def main():
    """Run the FastAPI server."""
    parser = argparse.ArgumentParser(description="OpenRouter API Test Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()

    # Set the API key
    if args.api_key:
        os.environ["OPENROUTER_API_KEY"] = args.api_key

    # Check if the API key is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Warning: OpenRouter API key is not set. Set it with --api-key or the OPENROUTER_API_KEY environment variable.")

    # Run the server
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
