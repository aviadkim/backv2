"""
OpenRouter API client for accessing Optimus Alpha and other models.
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional, Union

class OpenRouterClient:
    """Client for interacting with OpenRouter API to access Optimus Alpha and other models."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If not provided, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass it to the constructor.")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = "openrouter/optimus-alpha"
        
    def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter API.
        
        Args:
            messages: List of message objects with role and content
            model: Model to use (defaults to Optimus Alpha)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://backv2.com",  # Replace with your actual domain
            "X-Title": "FinDoc Analyzer"
        }
        
        data = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            error_msg = f"OpenRouter API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg += f": {error_data['error']['message']}"
            except:
                pass
            raise Exception(error_msg)
            
        return response.json()
    
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a simple text completion for a prompt.
        
        Args:
            prompt: The text prompt
            **kwargs: Additional parameters to pass to chat_completion
            
        Returns:
            Generated text as a string
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        
        return response["choices"][0]["message"]["content"]
    
    def get_structured_output(self, prompt: str, output_schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Get a structured output based on a schema.
        
        Args:
            prompt: The text prompt
            output_schema: JSON schema for the expected output
            **kwargs: Additional parameters to pass to chat_completion
            
        Returns:
            Structured data according to the schema
        """
        system_message = (
            "You are a helpful assistant that responds with structured data according to the provided schema. "
            "Your response should be valid JSON that matches the schema exactly."
        )
        
        schema_prompt = (
            f"{prompt}\n\n"
            f"Respond with valid JSON that matches this schema:\n{json.dumps(output_schema, indent=2)}"
        )
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": schema_prompt}
        ]
        
        response = self.chat_completion(messages, **kwargs)
        response_text = response["choices"][0]["message"]["content"]
        
        # Extract JSON from the response
        try:
            # Try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
                    
            # If all else fails, raise an error
            raise ValueError("Failed to parse structured output from model response")
