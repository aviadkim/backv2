"""
API endpoints for OpenRouter integration.
"""
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from ..utils.openrouter_client import OpenRouterClient

router = APIRouter()

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

@router.post("/chat")
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

@router.post("/completion")
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

@router.get("/status")
async def api_status(client: OpenRouterClient = Depends(get_openrouter_client)):
    """
    Check the OpenRouter API status.
    
    Args:
        client: OpenRouter client
        
    Returns:
        API status
    """
    try:
        # Send a simple test request
        response = client.get_completion(
            prompt="Hello, this is a test.",
            max_tokens=5
        )
        
        return {
            "status": "ok",
            "message": "OpenRouter API is working correctly"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API is not working: {str(e)}")
