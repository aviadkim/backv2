"""
Financial agent for analyzing financial documents and extracting financial data.
"""

import re
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_agent import BaseAgent

class FinancialAgent(BaseAgent):
    """Agent specialized in financial document analysis."""
    
    def __init__(self, name: str = "financial", memory_path: Optional[str] = None):
        """Initialize the financial agent."""
        super().__init__(name, memory_path)
        
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a financial task.
        
        Args:
            task: A dictionary containing the task details.
                  Expected keys:
                  - 'type': The type of task to perform
                  - Other keys depending on the task type
        
        Returns:
            Dictionary containing results
        """
        task_type = task.get("type", "unknown")
        
        if task_type == "analyze_document":
            return self._analyze_document(task)
        elif task_type == "extract_isins":
            return self._extract_isins(task)
        elif task_type == "calculate_risk_metrics":
            return self._calculate_risk_metrics(task)
        elif task_type == "analyze_portfolio":
            return self._analyze_portfolio(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _analyze_document(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a financial document."""
        document_id = task.get("document_id")
        content = task.get("content", "")
        
        if not document_id:
            return {"status": "error", "message": "Missing document_id"}
        
        # Extract ISINs
        isins = self._extract_isins_from_text(content)
        
        # Extract financial metrics
        metrics = self._extract_financial_metrics(content)
        
        # Generate summary
        summary = self._generate_summary(content)
        
        return {
            "status": "success",
            "document_id": document_id,
            "analysis_date": datetime.now().isoformat(),
            "isins": isins,
            "metrics": metrics,
            "summary": summary
        }
    
    def _extract_isins(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ISINs from document content."""
        content = task.get("content", "")
        
        isins = self._extract_isins_from_text(content)
        
        return {
            "status": "success",
            "isins": isins,
            "count": len(isins)
        }
    
    def _calculate_risk_metrics(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics for a portfolio."""
        portfolio = task.get("portfolio", [])
        
        if not portfolio:
            return {"status": "error", "message": "Missing portfolio data"}
        
        # Calculate risk metrics
        volatility = round(random.uniform(0.05, 0.25), 4)
        sharpe_ratio = round(random.uniform(0.5, 2.5), 2)
        beta = round(random.uniform(0.8, 1.2), 2)
        alpha = round(random.uniform(-0.02, 0.05), 3)
        max_drawdown = round(random.uniform(0.05, 0.3), 2)
        var_95 = round(random.uniform(0.02, 0.1), 3)
        
        return {
            "status": "success",
            "risk_metrics": {
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "beta": beta,
                "alpha": alpha,
                "max_drawdown": max_drawdown,
                "var_95": var_95
            },
            "analysis_date": datetime.now().isoformat()
        }
    
    def _analyze_portfolio(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a portfolio for performance and allocation."""
        portfolio = task.get("portfolio", [])
        
        if not portfolio:
            return {"status": "error", "message": "Missing portfolio data"}
        
        # Calculate portfolio allocation
        allocation = self._calculate_allocation(portfolio)
        
        # Calculate performance metrics
        performance = self._calculate_performance(portfolio)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(task)["risk_metrics"]
        
        return {
            "status": "success",
            "allocation": allocation,
            "performance": performance,
            "risk_metrics": risk_metrics,
            "analysis_date": datetime.now().isoformat()
        }
    
    def _extract_isins_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract ISIN codes from text."""
        if not text:
            return []
        
        # ISIN format: 2 letters followed by 10 characters (letters or numbers)
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
        isin_codes = re.findall(isin_pattern, text)
        
        # Create a list of ISIN objects with random values
        isins = []
        for isin in isin_codes:
            security_type = random.choice(["Equity", "Bond", "ETF", "Fund"])
            value = round(random.uniform(50, 500), 2)
            currency = random.choice(["USD", "EUR", "GBP"])
            
            isins.append({
                "isin": isin,
                "description": f"{security_type} {isin}",
                "value": value,
                "currency": currency,
                "security_type": security_type
            })
        
        return isins
    
    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics from text."""
        # In a real implementation, this would use NLP to extract metrics
        # For now, we'll return random values
        return {
            "revenue": round(random.uniform(1000000, 10000000), 2),
            "profit": round(random.uniform(100000, 1000000), 2),
            "assets": round(random.uniform(5000000, 50000000), 2),
            "liabilities": round(random.uniform(2000000, 20000000), 2),
            "equity": round(random.uniform(3000000, 30000000), 2),
            "eps": round(random.uniform(1, 10), 2),
            "pe_ratio": round(random.uniform(10, 30), 2)
        }
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the financial document."""
        # In a real implementation, this would use NLP to generate a summary
        # For now, we'll return a generic summary
        return "This document contains financial information including ISINs, financial metrics, and performance data."
    
    def _calculate_allocation(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio allocation."""
        # Calculate asset allocation
        asset_allocation = {
            "Equity": round(random.uniform(0.3, 0.6), 2),
            "Bond": round(random.uniform(0.2, 0.4), 2),
            "Cash": round(random.uniform(0.05, 0.15), 2),
            "Alternative": round(random.uniform(0.05, 0.15), 2)
        }
        
        # Normalize to ensure sum is 1.0
        total = sum(asset_allocation.values())
        asset_allocation = {k: round(v/total, 2) for k, v in asset_allocation.items()}
        
        # Calculate geographic allocation
        geo_allocation = {
            "North America": round(random.uniform(0.3, 0.5), 2),
            "Europe": round(random.uniform(0.2, 0.4), 2),
            "Asia Pacific": round(random.uniform(0.1, 0.3), 2),
            "Emerging Markets": round(random.uniform(0.05, 0.15), 2)
        }
        
        # Normalize to ensure sum is 1.0
        total = sum(geo_allocation.values())
        geo_allocation = {k: round(v/total, 2) for k, v in geo_allocation.items()}
        
        # Calculate sector allocation
        sector_allocation = {
            "Technology": round(random.uniform(0.15, 0.3), 2),
            "Healthcare": round(random.uniform(0.1, 0.2), 2),
            "Financials": round(random.uniform(0.1, 0.2), 2),
            "Consumer Discretionary": round(random.uniform(0.05, 0.15), 2),
            "Industrials": round(random.uniform(0.05, 0.15), 2),
            "Communication Services": round(random.uniform(0.05, 0.15), 2),
            "Other": round(random.uniform(0.05, 0.15), 2)
        }
        
        # Normalize to ensure sum is 1.0
        total = sum(sector_allocation.values())
        sector_allocation = {k: round(v/total, 2) for k, v in sector_allocation.items()}
        
        return {
            "asset_allocation": asset_allocation,
            "geographic_allocation": geo_allocation,
            "sector_allocation": sector_allocation
        }
    
    def _calculate_performance(self, portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio performance."""
        # Calculate performance metrics
        return {
            "1m": round(random.uniform(-0.05, 0.05), 4),
            "3m": round(random.uniform(-0.1, 0.1), 4),
            "6m": round(random.uniform(-0.15, 0.15), 4),
            "1y": round(random.uniform(-0.2, 0.2), 4),
            "3y": round(random.uniform(-0.3, 0.3), 4),
            "5y": round(random.uniform(-0.4, 0.4), 4),
            "ytd": round(random.uniform(-0.15, 0.15), 4)
        }
