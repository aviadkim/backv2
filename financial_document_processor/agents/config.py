"""
Configuration for AI agents.
"""
import os
from typing import Dict, Any, Optional, List
import logging

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Install with: pip install openai")

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Install with: pip install google-generativeai")

class AIConfig:
    """Configuration for AI models."""
    
    def __init__(self, api_key: Optional[str] = None, model_provider: str = "openai", 
                 model_name: Optional[str] = None):
        """
        Initialize AI configuration.
        
        Args:
            api_key: API key for the model provider
            model_provider: Model provider (openai or google)
            model_name: Model name
        """
        self.model_provider = model_provider.lower()
        
        # Set API key
        if api_key:
            self.api_key = api_key
        else:
            if self.model_provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            elif self.model_provider == "google":
                self.api_key = os.environ.get("GOOGLE_API_KEY")
            else:
                self.api_key = None
        
        # Set model name
        if model_name:
            self.model_name = model_name
        else:
            if self.model_provider == "openai":
                self.model_name = "gpt-4o"
            elif self.model_provider == "google":
                self.model_name = "gemini-1.5-pro"
            else:
                self.model_name = None
        
        # Initialize the selected provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected model provider."""
        if self.model_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not available. Install with: pip install openai")
            
            if not self.api_key:
                raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
            
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=self.api_key)
        
        elif self.model_provider == "google":
            if not GOOGLE_AI_AVAILABLE:
                raise ImportError("Google Generative AI library not available. Install with: pip install google-generativeai")
            
            if not self.api_key:
                raise ValueError("Google API key not provided and GOOGLE_API_KEY environment variable not set")
            
            # Initialize Google Generative AI
            genai.configure(api_key=self.api_key)
            self.client = genai
        
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration for LangChain.
        
        Returns:
            Dictionary with LLM configuration
        """
        if self.model_provider == "openai":
            from langchain_openai import ChatOpenAI
            
            return {
                "llm": ChatOpenAI(
                    model_name=self.model_name,
                    temperature=0.1,
                    api_key=self.api_key
                )
            }
        
        elif self.model_provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            return {
                "llm": ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=0.1,
                    google_api_key=self.api_key
                )
            }
        
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """
        Get embedding configuration for LlamaIndex.
        
        Returns:
            Dictionary with embedding configuration
        """
        if self.model_provider == "openai":
            from llama_index.embeddings.openai import OpenAIEmbedding
            
            return {
                "embed_model": OpenAIEmbedding(
                    model="text-embedding-3-small",
                    api_key=self.api_key
                )
            }
        
        elif self.model_provider == "google":
            from llama_index.embeddings.google import GoogleGenerativeAIEmbedding
            
            return {
                "embed_model": GoogleGenerativeAIEmbedding(
                    model_name="models/embedding-001",
                    api_key=self.api_key
                )
            }
        
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def get_completion_config(self) -> Dict[str, Any]:
        """
        Get completion configuration for LlamaIndex.
        
        Returns:
            Dictionary with completion configuration
        """
        if self.model_provider == "openai":
            from llama_index.llms.openai import OpenAI
            
            return {
                "llm": OpenAI(
                    model=self.model_name,
                    temperature=0.1,
                    api_key=self.api_key
                )
            }
        
        elif self.model_provider == "google":
            from llama_index.llms.google_genai import GoogleGenerativeAI
            
            return {
                "llm": GoogleGenerativeAI(
                    model_name=self.model_name,
                    temperature=0.1,
                    api_key=self.api_key
                )
            }
        
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def generate_completion(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a completion using the configured model.
        
        Args:
            prompt: Prompt text
            max_tokens: Maximum number of tokens to generate
        
        Returns:
            Generated text
        """
        if self.model_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.1
            )
            return response.choices[0].message.content
        
        elif self.model_provider == "google":
            model = self.client.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def generate_structured_output(self, prompt: str, output_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured output using the configured model.
        
        Args:
            prompt: Prompt text
            output_schema: JSON schema for the output
        
        Returns:
            Generated structured output
        """
        import json
        
        # Create a prompt that asks for JSON output
        structured_prompt = f"""
        {prompt}
        
        Please provide your response as a valid JSON object with the following schema:
        {json.dumps(output_schema, indent=2)}
        
        Your response should be valid JSON that can be parsed with json.loads().
        """
        
        # Generate completion
        completion = self.generate_completion(structured_prompt)
        
        # Extract JSON from the completion
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', completion, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no JSON code block, try to parse the whole response
                json_str = completion
            
            # Parse JSON
            return json.loads(json_str)
        
        except json.JSONDecodeError:
            # If JSON parsing fails, try to fix common issues
            try:
                # Remove any non-JSON text before and after the JSON object
                json_start = completion.find('{')
                json_end = completion.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = completion[json_start:json_end]
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON object found in the response")
            
            except (json.JSONDecodeError, ValueError):
                # If all parsing attempts fail, return a simple error object
                return {
                    "error": "Failed to parse JSON from model response",
                    "raw_response": completion
                }
