import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialAnalysisAgent:
    """AI agent for financial document analysis and insights."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the financial analysis agent."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            logger.warning("No API key provided. The agent will not be able to make API calls.")
    
    def analyze_financial_document(self, document_text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a financial document and extract insights.
        
        Args:
            document_text: The text content of the document to analyze
            document_type: Optional type of document (e.g., 'annual_report', 'balance_sheet', 'portfolio_statement')
            
        Returns:
            Dictionary containing structured analysis results
        """
        if not self.api_key:
            return {"error": "No API key provided. Cannot analyze document."}
        
        try:
            # Prepare prompt for the AI model
            prompt = self._prepare_analysis_prompt(document_text, document_type)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse and structure the response
            structured_analysis = self._parse_analysis_response(response)
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing financial document: {str(e)}", exc_info=True)
            return {"error": f"Document analysis failed: {str(e)}"}
    
    def generate_investment_recommendations(self, portfolio_data: List[Dict[str, Any]], 
                                           risk_profile: str = "moderate") -> Dict[str, Any]:
        """
        Generate investment recommendations based on portfolio data.
        
        Args:
            portfolio_data: List of portfolio holdings with details
            risk_profile: Risk profile of the investor ('conservative', 'moderate', 'aggressive')
            
        Returns:
            Dictionary containing investment recommendations
        """
        if not self.api_key:
            return {"error": "No API key provided. Cannot generate recommendations."}
        
        try:
            # Prepare prompt for the AI model
            prompt = self._prepare_recommendation_prompt(portfolio_data, risk_profile)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse and structure the response
            structured_recommendations = self._parse_recommendation_response(response)
            
            return structured_recommendations
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {str(e)}", exc_info=True)
            return {"error": f"Recommendation generation failed: {str(e)}"}
    
    def explain_financial_metrics(self, metrics: Dict[str, Any], 
                                 audience_level: str = "professional") -> Dict[str, Any]:
        """
        Generate explanations for financial metrics.
        
        Args:
            metrics: Dictionary of financial metrics to explain
            audience_level: Target audience level ('beginner', 'intermediate', 'professional')
            
        Returns:
            Dictionary containing explanations for each metric
        """
        if not self.api_key:
            return {"error": "No API key provided. Cannot explain metrics."}
        
        try:
            # Prepare prompt for the AI model
            prompt = self._prepare_explanation_prompt(metrics, audience_level)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse and structure the response
            structured_explanations = self._parse_explanation_response(response)
            
            return structured_explanations
            
        except Exception as e:
            logger.error(f"Error explaining financial metrics: {str(e)}", exc_info=True)
            return {"error": f"Explanation generation failed: {str(e)}"}
    
    def analyze_financial_trends(self, historical_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyze financial trends from historical data.
        
        Args:
            historical_data: Dictionary of historical financial data
            
        Returns:
            Dictionary containing trend analysis results
        """
        if not self.api_key:
            return {"error": "No API key provided. Cannot analyze trends."}
        
        try:
            # Prepare prompt for the AI model
            prompt = self._prepare_trend_analysis_prompt(historical_data)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse and structure the response
            structured_analysis = self._parse_trend_analysis_response(response)
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing financial trends: {str(e)}", exc_info=True)
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def _prepare_analysis_prompt(self, document_text: str, document_type: Optional[str] = None) -> str:
        """Prepare a prompt for financial document analysis."""
        # Truncate document text if it's too long
        max_length = 8000  # Adjust based on model token limits
        truncated_text = document_text[:max_length] if len(document_text) > max_length else document_text
        
        # Create a prompt based on document type
        if document_type == "annual_report":
            prompt = f"""
            You are a financial analyst AI assistant. Analyze the following annual report excerpt and extract key financial information.
            Focus on:
            1. Key financial metrics (revenue, profit, EPS, etc.)
            2. Year-over-year changes
            3. Balance sheet highlights
            4. Cash flow information
            5. Notable management comments
            6. Risk factors
            
            Format your response as JSON with the following structure:
            {{
                "financial_metrics": [
                    {{"name": "Revenue", "value": "X", "change": "Y%", "context": "..."}},
                    ...
                ],
                "balance_sheet": [
                    {{"item": "...", "value": "...", "context": "..."}},
                    ...
                ],
                "cash_flow": [
                    {{"item": "...", "value": "...", "context": "..."}},
                    ...
                ],
                "management_insights": [
                    {{"topic": "...", "insight": "..."}},
                    ...
                ],
                "risk_factors": [
                    {{"factor": "...", "description": "..."}},
                    ...
                ],
                "summary": "..."
            }}
            
            Annual report excerpt:
            {truncated_text}
            """
        elif document_type == "portfolio_statement":
            prompt = f"""
            You are a financial analyst AI assistant. Analyze the following portfolio statement and extract key information.
            Focus on:
            1. Securities held (names, identifiers, quantities)
            2. Asset allocation
            3. Values and performance metrics
            4. Fees and expenses
            5. Notable changes or transactions
            
            Format your response as JSON with the following structure:
            {{
                "securities": [
                    {{"name": "...", "identifier": "...", "quantity": "...", "value": "...", "performance": "..."}},
                    ...
                ],
                "asset_allocation": [
                    {{"class": "...", "percentage": "...", "value": "..."}},
                    ...
                ],
                "performance_metrics": [
                    {{"metric": "...", "value": "...", "context": "..."}},
                    ...
                ],
                "fees": [
                    {{"type": "...", "amount": "...", "context": "..."}},
                    ...
                ],
                "notable_changes": [
                    {{"change": "...", "context": "..."}},
                    ...
                ],
                "summary": "..."
            }}
            
            Portfolio statement:
            {truncated_text}
            """
        else:
            # Generic financial document analysis
            prompt = f"""
            You are a financial analyst AI assistant. Analyze the following financial document and extract key information.
            Focus on:
            1. Type of document (identify what kind of financial document this is)
            2. Key financial figures and metrics
            3. Dates and time periods
            4. Entities mentioned (companies, funds, etc.)
            5. Financial terms and their context
            6. Overall financial insights
            
            Format your response as JSON with the following structure:
            {{
                "document_type": "...",
                "financial_figures": [
                    {{"name": "...", "value": "...", "context": "..."}},
                    ...
                ],
                "time_periods": [
                    {{"description": "...", "start": "...", "end": "..."}},
                    ...
                ],
                "entities": [
                    {{"name": "...", "type": "...", "context": "..."}},
                    ...
                ],
                "financial_terms": [
                    {{"term": "...", "context": "..."}},
                    ...
                ],
                "insights": [
                    {{"topic": "...", "insight": "..."}},
                    ...
                ],
                "summary": "..."
            }}
            
            Financial document:
            {truncated_text}
            """
        
        return prompt
    
    def _prepare_recommendation_prompt(self, portfolio_data: List[Dict[str, Any]], 
                                      risk_profile: str = "moderate") -> str:
        """Prepare a prompt for investment recommendations."""
        # Convert portfolio data to a string representation
        portfolio_str = json.dumps(portfolio_data, indent=2)
        
        prompt = f"""
        You are a financial advisor AI assistant. Based on the following portfolio data and risk profile,
        generate investment recommendations.
        
        Risk profile: {risk_profile}
        
        Portfolio data:
        {portfolio_str}
        
        Provide recommendations in the following areas:
        1. Asset allocation adjustments
        2. Diversification suggestions
        3. Specific securities to consider adding
        4. Securities to consider reducing or eliminating
        5. Risk management strategies
        
        Format your response as JSON with the following structure:
        {{
            "asset_allocation_recommendations": [
                {{"recommendation": "...", "rationale": "...", "current_allocation": "...", "target_allocation": "..."}},
                ...
            ],
            "diversification_recommendations": [
                {{"recommendation": "...", "rationale": "..."}},
                ...
            ],
            "securities_to_add": [
                {{"type": "...", "name": "...", "rationale": "..."}},
                ...
            ],
            "securities_to_reduce": [
                {{"name": "...", "rationale": "..."}},
                ...
            ],
            "risk_management_recommendations": [
                {{"recommendation": "...", "rationale": "..."}},
                ...
            ],
            "summary": "..."
        }}
        """
        
        return prompt
    
    def _prepare_explanation_prompt(self, metrics: Dict[str, Any], audience_level: str = "professional") -> str:
        """Prepare a prompt for explaining financial metrics."""
        # Convert metrics to a string representation
        metrics_str = json.dumps(metrics, indent=2)
        
        prompt = f"""
        You are a financial educator AI assistant. Explain the following financial metrics in terms appropriate for a {audience_level} audience.
        
        Financial metrics:
        {metrics_str}
        
        For each metric, provide:
        1. A clear explanation of what the metric means
        2. How to interpret the value (is higher better? what's a good benchmark?)
        3. How it's calculated
        4. Why it's important
        5. Any limitations or caveats
        
        Format your response as JSON with the following structure:
        {{
            "explanations": [
                {{
                    "metric": "...",
                    "value": "...",
                    "explanation": "...",
                    "interpretation": "...",
                    "calculation": "...",
                    "importance": "...",
                    "limitations": "..."
                }},
                ...
            ],
            "summary": "..."
        }}
        """
        
        return prompt
    
    def _prepare_trend_analysis_prompt(self, historical_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Prepare a prompt for trend analysis."""
        # Convert historical data to a string representation
        historical_str = json.dumps(historical_data, indent=2)
        
        prompt = f"""
        You are a financial analyst AI assistant. Analyze the following historical financial data and identify key trends.
        
        Historical data:
        {historical_str}
        
        Identify trends in the following areas:
        1. Performance trends
        2. Growth patterns
        3. Cyclical patterns
        4. Correlations between different metrics
        5. Anomalies or outliers
        6. Long-term vs. short-term patterns
        
        Format your response as JSON with the following structure:
        {{
            "performance_trends": [
                {{"trend": "...", "description": "...", "significance": "..."}},
                ...
            ],
            "growth_patterns": [
                {{"pattern": "...", "description": "...", "significance": "..."}},
                ...
            ],
            "cyclical_patterns": [
                {{"pattern": "...", "period": "...", "description": "..."}},
                ...
            ],
            "correlations": [
                {{"metrics": ["...", "..."], "correlation": "...", "description": "..."}},
                ...
            ],
            "anomalies": [
                {{"anomaly": "...", "period": "...", "description": "..."}},
                ...
            ],
            "long_term_vs_short_term": [
                {{"metric": "...", "short_term": "...", "long_term": "...", "analysis": "..."}},
                ...
            ],
            "summary": "..."
        }}
        """
        
        return prompt
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get a response from the AI model."""
        try:
            # Make API call to OpenAI
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a financial analysis AI assistant that provides structured, accurate financial insights."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,  # Lower temperature for more deterministic responses
                "max_tokens": 2000,  # Adjust based on expected response length
                "response_format": {"type": "json_object"}  # Request JSON response
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return "{}"
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return "{}"
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the AI analysis response."""
        try:
            # Parse JSON response
            parsed_response = json.loads(response)
            
            # Add metadata
            parsed_response["analyzed_at"] = datetime.now().isoformat()
            parsed_response["model_used"] = self.model
            
            return parsed_response
            
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON", exc_info=True)
            return {
                "error": "Failed to parse AI response",
                "raw_response": response[:1000]  # Include truncated raw response for debugging
            }
    
    def _parse_recommendation_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the AI recommendation response."""
        try:
            # Parse JSON response
            parsed_response = json.loads(response)
            
            # Add metadata
            parsed_response["generated_at"] = datetime.now().isoformat()
            parsed_response["model_used"] = self.model
            
            return parsed_response
            
        except json.JSONDecodeError:
            logger.error("Failed to parse AI recommendation response as JSON", exc_info=True)
            return {
                "error": "Failed to parse AI recommendation response",
                "raw_response": response[:1000]  # Include truncated raw response for debugging
            }
    
    def _parse_explanation_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the AI explanation response."""
        try:
            # Parse JSON response
            parsed_response = json.loads(response)
            
            # Add metadata
            parsed_response["generated_at"] = datetime.now().isoformat()
            parsed_response["model_used"] = self.model
            
            return parsed_response
            
        except json.JSONDecodeError:
            logger.error("Failed to parse AI explanation response as JSON", exc_info=True)
            return {
                "error": "Failed to parse AI explanation response",
                "raw_response": response[:1000]  # Include truncated raw response for debugging
            }
    
    def _parse_trend_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse and structure the AI trend analysis response."""
        try:
            # Parse JSON response
            parsed_response = json.loads(response)
            
            # Add metadata
            parsed_response["analyzed_at"] = datetime.now().isoformat()
            parsed_response["model_used"] = self.model
            
            return parsed_response
            
        except json.JSONDecodeError:
            logger.error("Failed to parse AI trend analysis response as JSON", exc_info=True)
            return {
                "error": "Failed to parse AI trend analysis response",
                "raw_response": response[:1000]  # Include truncated raw response for debugging
            }
