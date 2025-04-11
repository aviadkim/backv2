import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialAnalysisAgent:
    """AI-powered agent for financial analysis and insights."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the financial analysis agent."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided for FinancialAnalysisAgent. AI analysis will not be available.")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def analyze_financial_document(self, document_text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a financial document and extract key insights.
        
        Args:
            document_text: The text content of the document
            document_type: Optional type of document (e.g., 'annual_report', 'balance_sheet')
            
        Returns:
            Dictionary with analysis results
        """
        if not self.api_key:
            return {"error": "API key not available for AI analysis"}
        
        try:
            # Prepare the prompt based on document type
            prompt = self._create_document_analysis_prompt(document_text, document_type)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse the response
            analysis = self._parse_document_analysis(response)
            
            return {
                "document_type": document_type or "Financial Document",
                "analysis": analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial document: {str(e)}", exc_info=True)
            return {"error": f"Document analysis failed: {str(e)}"}
    
    def generate_investment_recommendations(self, portfolio_data: Dict[str, Any], 
                                           risk_profile: str = "moderate") -> Dict[str, Any]:
        """
        Generate investment recommendations based on portfolio analysis.
        
        Args:
            portfolio_data: Portfolio data including holdings and analysis
            risk_profile: Risk profile of the investor ('conservative', 'moderate', 'aggressive')
            
        Returns:
            Dictionary with investment recommendations
        """
        if not self.api_key:
            return {"error": "API key not available for AI analysis"}
        
        try:
            # Prepare the prompt
            prompt = self._create_investment_recommendations_prompt(portfolio_data, risk_profile)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse the response
            recommendations = self._parse_investment_recommendations(response)
            
            return {
                "risk_profile": risk_profile,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {str(e)}", exc_info=True)
            return {"error": f"Recommendation generation failed: {str(e)}"}
    
    def explain_financial_metrics(self, metrics: Dict[str, Any], 
                                 audience_level: str = "professional") -> Dict[str, Any]:
        """
        Explain financial metrics in plain language.
        
        Args:
            metrics: Dictionary of financial metrics to explain
            audience_level: Target audience level ('beginner', 'intermediate', 'professional')
            
        Returns:
            Dictionary with explanations for each metric
        """
        if not self.api_key:
            return {"error": "API key not available for AI analysis"}
        
        try:
            # Prepare the prompt
            prompt = self._create_metrics_explanation_prompt(metrics, audience_level)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse the response
            explanations = self._parse_metrics_explanations(response)
            
            return {
                "audience_level": audience_level,
                "explanations": explanations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error explaining financial metrics: {str(e)}", exc_info=True)
            return {"error": f"Metrics explanation failed: {str(e)}"}
    
    def analyze_financial_trends(self, historical_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyze financial trends from historical data.
        
        Args:
            historical_data: Dictionary of historical financial data
            
        Returns:
            Dictionary with trend analysis
        """
        if not self.api_key:
            return {"error": "API key not available for AI analysis"}
        
        try:
            # Prepare the prompt
            prompt = self._create_trend_analysis_prompt(historical_data)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            # Parse the response
            trend_analysis = self._parse_trend_analysis(response)
            
            return {
                "trend_analysis": trend_analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial trends: {str(e)}", exc_info=True)
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get a response from the AI model."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a financial analysis expert. Provide clear, accurate, and detailed financial analysis and insights."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Lower temperature for more consistent, factual responses
            "max_tokens": 2000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            raise Exception(f"API request failed: {response.text}")
        
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    
    def _create_document_analysis_prompt(self, document_text: str, document_type: Optional[str] = None) -> str:
        """Create a prompt for document analysis."""
        # Truncate document text if it's too long
        max_length = 8000
        truncated_text = document_text[:max_length] if len(document_text) > max_length else document_text
        
        prompt = f"""Analyze the following financial document{' (' + document_type + ')' if document_type else ''}:

```
{truncated_text}
```

Please provide a comprehensive analysis including:
1. A summary of the key points and findings
2. Identification of important financial figures and metrics
3. Analysis of financial health and performance
4. Notable trends or patterns
5. Potential risks or concerns
6. Opportunities or strengths

Format your response as JSON with the following structure:
{{
  "summary": "Brief summary of the document",
  "key_figures": [
    {{"name": "Figure name", "value": "Value", "context": "Brief context"}}
  ],
  "financial_health": "Analysis of financial health",
  "performance_analysis": "Analysis of performance",
  "trends": [
    {{"trend": "Description of trend", "significance": "Why it matters"}}
  ],
  "risks": [
    {{"risk": "Description of risk", "severity": "high/medium/low", "mitigation": "Possible mitigation"}}
  ],
  "opportunities": [
    {{"opportunity": "Description of opportunity", "potential": "high/medium/low"}}
  ]
}}

Ensure your analysis is accurate, objective, and based solely on the information provided in the document.
"""
        return prompt
    
    def _create_investment_recommendations_prompt(self, portfolio_data: Dict[str, Any], risk_profile: str) -> str:
        """Create a prompt for investment recommendations."""
        portfolio_json = json.dumps(portfolio_data, indent=2)
        
        prompt = f"""Generate investment recommendations based on the following portfolio data and risk profile:

Risk Profile: {risk_profile}

Portfolio Data:
```json
{portfolio_json}
```

Please provide comprehensive investment recommendations including:
1. Overall assessment of the portfolio
2. Recommended asset allocation adjustments
3. Specific investment recommendations (buy, sell, hold)
4. Risk management suggestions
5. Tax optimization strategies (if applicable)

Format your response as JSON with the following structure:
{{
  "overall_assessment": "Assessment of the current portfolio",
  "asset_allocation_recommendations": [
    {{"asset_class": "Asset class name", "current_allocation": "Current %", "recommended_allocation": "Recommended %", "rationale": "Explanation"}}
  ],
  "investment_recommendations": [
    {{"action": "buy/sell/hold", "security_type": "Type", "description": "Description", "rationale": "Explanation"}}
  ],
  "risk_management": [
    {{"strategy": "Risk management strategy", "description": "Description"}}
  ],
  "tax_optimization": [
    {{"strategy": "Tax strategy", "description": "Description"}}
  ],
  "summary": "Brief summary of recommendations"
}}

Ensure your recommendations are appropriate for the specified risk profile and based on sound financial principles.
"""
        return prompt
    
    def _create_metrics_explanation_prompt(self, metrics: Dict[str, Any], audience_level: str) -> str:
        """Create a prompt for explaining financial metrics."""
        metrics_json = json.dumps(metrics, indent=2)
        
        prompt = f"""Explain the following financial metrics in plain language for a {audience_level} audience:

```json
{metrics_json}
```

Please provide clear explanations for each metric including:
1. What the metric means
2. How it's calculated
3. Why it's important
4. How to interpret the current values
5. Benchmark or typical values for context

Format your response as JSON with the following structure:
{{
  "metric_explanations": [
    {{
      "metric_name": "Name of the metric",
      "value": "Current value",
      "explanation": "Plain language explanation",
      "calculation": "How it's calculated",
      "importance": "Why it matters",
      "interpretation": "What the current value indicates",
      "benchmark": "Typical values or benchmarks"
    }}
  ],
  "overall_assessment": "Brief overall assessment based on these metrics"
}}

Adjust your language and level of detail to be appropriate for a {audience_level} audience.
"""
        return prompt
    
    def _create_trend_analysis_prompt(self, historical_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a prompt for trend analysis."""
        # Convert historical data to a more concise format for the prompt
        simplified_data = {}
        for key, data_points in historical_data.items():
            if len(data_points) > 10:
                # Take first, last, and evenly spaced points in between
                step = len(data_points) // 8
                selected_points = [data_points[0]] + [data_points[i] for i in range(step, len(data_points) - step, step)] + [data_points[-1]]
                simplified_data[key] = selected_points
            else:
                simplified_data[key] = data_points
        
        historical_json = json.dumps(simplified_data, indent=2)
        
        prompt = f"""Analyze the trends in the following historical financial data:

```json
{historical_json}
```

Please provide a comprehensive trend analysis including:
1. Identification of significant trends
2. Analysis of growth or decline patterns
3. Seasonality or cyclical patterns
4. Correlation between different metrics
5. Anomalies or outliers
6. Forecasts or projections based on historical patterns

Format your response as JSON with the following structure:
{{
  "identified_trends": [
    {{"metric": "Metric name", "trend": "Description of trend", "significance": "Why it matters"}}
  ],
  "growth_analysis": "Analysis of growth or decline patterns",
  "seasonality": "Analysis of any seasonal or cyclical patterns",
  "correlations": [
    {{"metrics": "Related metrics", "relationship": "Description of relationship", "strength": "strong/moderate/weak"}}
  ],
  "anomalies": [
    {{"metric": "Metric name", "anomaly": "Description of anomaly", "possible_explanation": "Explanation"}}
  ],
  "forecast": "Projection based on historical patterns",
  "summary": "Brief summary of the trend analysis"
}}

Ensure your analysis is data-driven and based on the patterns evident in the provided historical data.
"""
        return prompt
    
    def _parse_document_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the document analysis response."""
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create a structured response from the text
                return {
                    "summary": response,
                    "key_figures": [],
                    "financial_health": "",
                    "performance_analysis": "",
                    "trends": [],
                    "risks": [],
                    "opportunities": []
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from document analysis response")
            return {
                "summary": response,
                "key_figures": [],
                "financial_health": "",
                "performance_analysis": "",
                "trends": [],
                "risks": [],
                "opportunities": []
            }
    
    def _parse_investment_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse the investment recommendations response."""
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create a structured response from the text
                return {
                    "overall_assessment": response,
                    "asset_allocation_recommendations": [],
                    "investment_recommendations": [],
                    "risk_management": [],
                    "tax_optimization": [],
                    "summary": ""
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from investment recommendations response")
            return {
                "overall_assessment": response,
                "asset_allocation_recommendations": [],
                "investment_recommendations": [],
                "risk_management": [],
                "tax_optimization": [],
                "summary": ""
            }
    
    def _parse_metrics_explanations(self, response: str) -> Dict[str, Any]:
        """Parse the metrics explanations response."""
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create a structured response from the text
                return {
                    "metric_explanations": [],
                    "overall_assessment": response
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from metrics explanations response")
            return {
                "metric_explanations": [],
                "overall_assessment": response
            }
    
    def _parse_trend_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the trend analysis response."""
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create a structured response from the text
                return {
                    "identified_trends": [],
                    "growth_analysis": "",
                    "seasonality": "",
                    "correlations": [],
                    "anomalies": [],
                    "forecast": "",
                    "summary": response
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from trend analysis response")
            return {
                "identified_trends": [],
                "growth_analysis": "",
                "seasonality": "",
                "correlations": [],
                "anomalies": [],
                "forecast": "",
                "summary": response
            }
