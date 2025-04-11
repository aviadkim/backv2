"""
Document analysis agent implementation.
"""
import logging
from typing import Dict, List, Any, Optional
import os
import aiohttp
import json

from .base import Agent, AgentResponse, AgentFactory
from ..services.document_service import DocumentService

logger = logging.getLogger(__name__)

@AgentFactory.register("document")
class DocumentAgent(Agent):
    """Agent that analyzes documents and answers questions about them."""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, description, config)
        self.api_key = config.get("api_key", os.environ.get("OPENROUTER_API_KEY", ""))
        self.model = config.get("model", "openai/gpt-4")  # Using GPT-4 for better document analysis
        self.document_service = DocumentService()
        self.document_id = config.get("document_id")
        
        if not self.api_key:
            logger.warning("API key not provided. Document agent will not function properly.")
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a document-related query."""
        if not self.api_key:
            return AgentResponse(
                content="Error: API key not configured. Please provide an API key.",
                metadata={"error": "api_key_missing"}
            )
        
        # Add user query to history
        self.add_to_history("user", query, context)
        
        # Get document context
        document_context = await self._get_document_context(context)
        if "error" in document_context:
            return AgentResponse(
                content=f"Error: {document_context['error_message']}",
                metadata={"error": document_context["error"]}
            )
        
        # Create system prompt with document context
        system_prompt = self._create_system_prompt(document_context)
        
        # Prepare messages for the API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limited to last 5 messages to leave room for document content)
        for msg in self.conversation_history[-5:]:
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
                        "HTTP-Referer": "https://document-understanding-demo.com",
                        "X-Title": "Document Understanding Demo"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 1500,
                        "temperature": 0.3  # Lower temperature for more factual responses
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {error_text}")
                        return AgentResponse(
                            content=f"Error: Failed to analyze document. Status code: {response.status}",
                            metadata={"error": "api_error", "status_code": response.status}
                        )
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return AgentResponse(
                            content="Error: No response received from the document analysis.",
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
                            "document_id": self.document_id or context.get("document_id"),
                            "document_name": document_context.get("document_name", "Unknown document")
                        }
                    )
        
        except Exception as e:
            logger.exception("Error processing document query")
            return AgentResponse(
                content=f"Error analyzing document: {str(e)}",
                metadata={"error": "exception", "message": str(e)}
            )
    
    async def _get_document_context(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get the document context for the query."""
        context = context or {}
        
        # Use document_id from context if provided, otherwise use the one from config
        document_id = context.get("document_id", self.document_id)
        
        if not document_id:
            return {
                "error": "document_missing",
                "error_message": "No document specified. Please select a document to analyze."
            }
        
        try:
            # Get document data
            document = self.document_service.get_document(document_id)
            
            if not document:
                return {
                    "error": "document_not_found",
                    "error_message": f"Document with ID {document_id} not found."
                }
            
            # Extract text content
            text_content = document.get("content", "")
            if not text_content:
                return {
                    "error": "document_empty",
                    "error_message": "The document has no text content to analyze."
                }
            
            return {
                "document_id": document_id,
                "document_name": document.get("filename", "Unknown document"),
                "document_type": document.get("metadata", {}).get("mime_type", "Unknown type"),
                "text_content": text_content,
                "metadata": document.get("metadata", {})
            }
        
        except Exception as e:
            logger.exception(f"Error getting document context for ID {document_id}")
            return {
                "error": "document_retrieval_error",
                "error_message": f"Error retrieving document: {str(e)}"
            }
    
    def _create_system_prompt(self, document_context: Dict[str, Any]) -> str:
        """Create a system prompt with document context."""
        document_name = document_context.get("document_name", "the document")
        text_content = document_context.get("text_content", "")
        
        # Truncate text content if it's too long (to avoid exceeding token limits)
        max_chars = 10000  # Adjust based on your needs and model token limits
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "...[content truncated]"
        
        return f"""You are a document analysis assistant specialized in understanding and extracting information from documents.
        
You are currently analyzing a document named "{document_name}".

Here is the content of the document:
---
{text_content}
---

Your task is to answer questions about this document accurately and helpfully. 
If the answer cannot be found in the document, clearly state that the information is not present in the document.
If asked about financial metrics or data, provide precise information from the document.
When appropriate, organize information in tables for clarity.
"""
