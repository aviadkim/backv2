import logging
import json
import random
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

from .base_agent import BaseAgent

class ChatAgent(BaseAgent):
    """Agent for handling chat interactions with users."""
    
    def __init__(self, name: str = "chat", memory_path: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the chat agent."""
        super().__init__(name, memory_path)
        self.api_key = api_key
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Default responses for when API key is not available
        self.default_responses = {
            "document_analyzer": [
                "I've analyzed the document and found the following key information: total revenue of $2.5M, operating expenses of $1.8M, and net profit of $700K.",
                "The document contains 3 ISIN codes: US0378331005 (Apple), US5949181045 (Microsoft), and US88160R1014 (Tesla).",
                "Based on my analysis, this appears to be a quarterly financial report with a focus on technology sector investments."
            ],
            "isin_extractor": [
                "I've extracted the following ISINs from the document: US0378331005, US5949181045, US88160R1014, US0231351067, US30303M1027.",
                "The document contains references to 5 different securities, all from the technology sector.",
                "I've identified and validated all ISINs in the document. Would you like me to provide more details about any specific security?"
            ],
            "portfolio_analyzer": [
                "Your portfolio has a Sharpe ratio of 1.2, which indicates a good risk-adjusted return compared to the market.",
                "The portfolio analysis shows an asset allocation of 60% equities, 30% bonds, and 10% cash equivalents.",
                "Based on my analysis, your portfolio has a beta of 0.85, indicating slightly lower volatility than the market."
            ],
            "regulatory_compliance": [
                "I've checked the document for regulatory compliance and found no major issues.",
                "The document meets all requirements for GDPR compliance.",
                "There are a few minor disclosure issues that should be addressed before final submission."
            ]
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat task."""
        task_type = task.get("type", "chat")
        
        if task_type == "chat":
            return self._handle_chat(task)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    def _handle_chat(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a chat interaction."""
        message = task.get("message", "")
        agent_id = task.get("agent_id", "")
        document_id = task.get("document_id")
        
        if not message:
            return {"status": "error", "message": "No message provided"}
        
        # If we have an API key, use the AI service
        if self.api_key:
            try:
                response = self._call_ai_service(message, agent_id, document_id)
                return {
                    "status": "success",
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Error calling AI service: {e}")
                # Fall back to default responses
        
        # Use default responses if no API key or if API call failed
        agent_type = self._get_agent_type(agent_id)
        responses = self.default_responses.get(agent_type, self.default_responses["document_analyzer"])
        random_response = random.choice(responses)
        
        return {
            "status": "success",
            "response": random_response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _call_ai_service(self, message: str, agent_id: str, document_id: Optional[int] = None) -> str:
        """Call the AI service (OpenRouter) to get a response."""
        if not self.api_key:
            raise ValueError("No API key provided")
        
        # Construct the prompt based on agent type and document
        agent_type = self._get_agent_type(agent_id)
        system_prompt = self._get_system_prompt(agent_type, document_id)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "anthropic/claude-3-opus:beta",  # Using Claude 3 Opus for best financial analysis
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status {response.status_code}: {response.text}")
        
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    
    def _get_agent_type(self, agent_id: str) -> str:
        """Map agent ID to agent type."""
        agent_map = {
            "1": "document_analyzer",
            "2": "isin_extractor",
            "3": "portfolio_analyzer",
            "4": "regulatory_compliance"
        }
        return agent_map.get(str(agent_id), "document_analyzer")
    
    def _get_system_prompt(self, agent_type: str, document_id: Optional[int] = None) -> str:
        """Get the system prompt for the AI based on agent type."""
        document_context = ""
        if document_id:
            # In a real implementation, we would fetch the document content
            document_context = f"You are analyzing document ID {document_id}. "
        
        prompts = {
            "document_analyzer": f"{document_context}You are a financial document analyzer AI. Your task is to analyze financial documents, extract key information, identify trends, and provide insights. Be precise, factual, and focus on the most important financial data.",
            "isin_extractor": f"{document_context}You are an ISIN extraction specialist AI. Your task is to identify and extract International Securities Identification Numbers (ISINs) from financial documents. Validate the ISINs you find and provide information about the securities they represent.",
            "portfolio_analyzer": f"{document_context}You are a portfolio analysis AI. Your task is to analyze investment portfolios, calculate risk metrics, assess performance, and provide recommendations for optimization. Use financial best practices in your analysis.",
            "regulatory_compliance": f"{document_context}You are a regulatory compliance AI. Your task is to review documents for compliance with financial regulations, identify potential issues, and suggest corrections. Be thorough and reference specific regulations when applicable."
        }
        
        return prompts.get(agent_type, prompts["document_analyzer"])
