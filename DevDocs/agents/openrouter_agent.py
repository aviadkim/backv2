"""
OpenRouter AI agent implementation.
"""
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
import os

from .base import Agent, AgentResponse, AgentFactory

logger = logging.getLogger(__name__)

@AgentFactory.register("openrouter")
class OpenRouterAgent(Agent):
    """Agent that uses OpenRouter API to process queries."""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, description, config)
        self.api_key = config.get("api_key", os.environ.get("OPENROUTER_API_KEY", ""))
        self.model = config.get("model", "openai/gpt-3.5-turbo")
        self.system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.7)
        
        if not self.api_key:
            logger.warning("OpenRouter API key not provided. Agent will not function properly.")
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a query using the OpenRouter API."""
        if not self.api_key:
            return AgentResponse(
                content="Error: OpenRouter API key not configured. Please provide an API key.",
                metadata={"error": "api_key_missing"}
            )
        
        # Add user query to history
        self.add_to_history("user", query, context)
        
        # Prepare messages for the API
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history (limited to last 10 messages to avoid token limits)
        for msg in self.conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://document-understanding-demo.com",  # Replace with your actual domain
                        "X-Title": "Document Understanding Demo"  # Replace with your app name
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {error_text}")
                        return AgentResponse(
                            content=f"Error: Failed to get response from AI model. Status code: {response.status}",
                            metadata={"error": "api_error", "status_code": response.status}
                        )
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return AgentResponse(
                            content="Error: No response received from the AI model.",
                            metadata={"error": "empty_response"}
                        )
                    
                    content = data["choices"][0]["message"]["content"]
                    
                    # Add assistant response to history
                    self.add_to_history("assistant", content)
                    
                    return AgentResponse(
                        content=content,
                        metadata={
                            "model": data.get("model", self.model),
                            "usage": data.get("usage", {}),
                            "id": data.get("id")
                        }
                    )
        
        except Exception as e:
            logger.exception("Error processing query with OpenRouter")
            return AgentResponse(
                content=f"Error: {str(e)}",
                metadata={"error": "exception", "message": str(e)}
            )
