"""
OpenRouter AI agent for financial document querying.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import OpenAI (used for OpenRouter)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")

class OpenRouterAgent:
    """OpenRouter AI agent for financial document querying."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-3-opus"):
        """
        Initialize the OpenRouter agent.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "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")
        self.model = model
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        logger.info(f"Initialized OpenRouter agent with model: {model}")
    
    def query(self, text: str, question: str) -> str:
        """
        Query the document with a question.
        
        Args:
            text: Document text
            question: Question to ask
        
        Returns:
            Answer to the question
        """
        logger.info(f"Querying document with question: {question}")
        
        # Create prompt
        prompt = f"""
        You are a financial document analysis assistant. Your task is to answer questions about financial documents accurately.
        
        Document:
        {text[:15000]}  # Limit text to avoid token limits
        
        Question: {question}
        
        Provide a detailed and accurate answer based only on the information in the document.
        If the answer cannot be found in the document, say so clearly.
        """
        
        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                headers={
                    "HTTP-Referer": "https://github.com/aviadkim/backv2"  # Optional: Helps OpenRouter with analytics
                }
            )
            
            # Extract answer
            answer = response.choices[0].message.content
            logger.info(f"Question answered: {question}")
            return answer
        
        except Exception as e:
            logger.error(f"Error querying OpenRouter: {e}")
            return f"Error answering question: {e}"
    
    def analyze(self, text: str, request: str) -> Dict[str, Any]:
        """
        Analyze the document with a specific request.
        
        Args:
            text: Document text
            request: Analysis request
        
        Returns:
            Analysis result
        """
        logger.info(f"Analyzing document with request: {request}")
        
        # Create prompt
        prompt = f"""
        You are a financial document analysis assistant. Your task is to analyze financial documents and provide insights.
        
        Document:
        {text[:15000]}  # Limit text to avoid token limits
        
        Analysis Request: {request}
        
        Provide a detailed analysis based only on the information in the document.
        Format your response as a JSON object with the following structure:
        {{
            "analysis": "Main analysis text",
            "key_points": ["Point 1", "Point 2", ...],
            "recommendations": ["Recommendation 1", "Recommendation 2", ...]
        }}
        """
        
        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                headers={
                    "HTTP-Referer": "https://github.com/aviadkim/backv2"  # Optional: Helps OpenRouter with analytics
                }
            )
            
            # Extract analysis
            analysis_text = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', analysis_text, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If no JSON code block, try to parse the whole response
                    json_str = analysis_text
                
                # Find JSON object in the text
                json_object_match = re.search(r'\{\s*".*"\s*:.*\}', json_str, re.DOTALL)
                if json_object_match:
                    json_str = json_object_match.group(0)
                
                # Parse JSON
                analysis = json.loads(json_str)
                logger.info(f"Document analyzed: {request}")
                return analysis
            
            except Exception as json_error:
                logger.error(f"Error parsing JSON from response: {json_error}")
                return {
                    "analysis": analysis_text,
                    "key_points": [],
                    "recommendations": []
                }
        
        except Exception as e:
            logger.error(f"Error analyzing with OpenRouter: {e}")
            return {
                "analysis": f"Error analyzing document: {e}",
                "key_points": [],
                "recommendations": []
            }
    
    def generate_table(self, text: str, request: str, format: str = "markdown") -> str:
        """
        Generate a table from the document.
        
        Args:
            text: Document text
            request: Table generation request
            format: Output format (markdown, html, or csv)
        
        Returns:
            Generated table
        """
        logger.info(f"Generating {format} table with request: {request}")
        
        # Create prompt
        prompt = f"""
        You are a financial document analysis assistant. Your task is to generate tables from financial documents.
        
        Document:
        {text[:15000]}  # Limit text to avoid token limits
        
        Table Request: {request}
        
        Generate a {format} table based on the information in the document.
        
        Format: {format}
        
        If the requested information cannot be found in the document, create a table indicating that the information is not available.
        """
        
        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                headers={
                    "HTTP-Referer": "https://github.com/aviadkim/backv2"  # Optional: Helps OpenRouter with analytics
                }
            )
            
            # Extract table
            table = response.choices[0].message.content
            logger.info(f"Table generated: {request}")
            return table
        
        except Exception as e:
            logger.error(f"Error generating table with OpenRouter: {e}")
            return f"Error generating table: {e}"
    
    def extract_insights(self, text: str) -> Dict[str, Any]:
        """
        Extract key insights from the document.
        
        Args:
            text: Document text
        
        Returns:
            Dictionary of insights
        """
        logger.info("Extracting insights from document")
        
        # Create prompt
        prompt = """
        You are a financial document analysis assistant. Your task is to extract key insights from financial documents.
        
        Document:
        {text}
        
        Extract the following key insights from the document:
        1. Portfolio summary
        2. Asset allocation
        3. Top holdings
        4. Risk assessment
        5. Key metrics
        
        Format your response as a JSON object with the following structure:
        {
            "portfolio_summary": "Summary text",
            "asset_allocation": [
                {"asset_class": "Class name", "percentage": 0.0}
            ],
            "top_holdings": [
                {"name": "Security name", "value": 0.0, "percentage": 0.0}
            ],
            "risk_assessment": "Risk assessment text",
            "key_metrics": {
                "metric1": "value1",
                "metric2": "value2"
            }
        }
        """.format(text=text[:15000])  # Limit text to avoid token limits
        
        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                headers={
                    "HTTP-Referer": "https://github.com/aviadkim/backv2"  # Optional: Helps OpenRouter with analytics
                }
            )
            
            # Extract insights
            insights_text = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', insights_text, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # If no JSON code block, try to parse the whole response
                    json_str = insights_text
                
                # Find JSON object in the text
                json_object_match = re.search(r'\{\s*".*"\s*:.*\}', json_str, re.DOTALL)
                if json_object_match:
                    json_str = json_object_match.group(0)
                
                # Parse JSON
                insights = json.loads(json_str)
                logger.info("Insights extracted from document")
                return insights
            
            except Exception as json_error:
                logger.error(f"Error parsing JSON from response: {json_error}")
                return {
                    "portfolio_summary": insights_text,
                    "asset_allocation": [],
                    "top_holdings": [],
                    "risk_assessment": "",
                    "key_metrics": {}
                }
        
        except Exception as e:
            logger.error(f"Error extracting insights with OpenRouter: {e}")
            return {
                "portfolio_summary": f"Error extracting insights: {e}",
                "asset_allocation": [],
                "top_holdings": [],
                "risk_assessment": "",
                "key_metrics": {}
            }
