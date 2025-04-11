import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .report_base import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioReportGenerator(ReportGenerator):
    """Specialized report generator for portfolio reports."""
    
    def _generate_portfolio_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive portfolio report."""
        # Extract relevant data
        summary = data.get("summary", {})
        allocation = data.get("allocation", {})
        performance = data.get("performance", {})
        risk = data.get("risk", {})
        holdings = data.get("holdings", [])
        
        # Format the report
        report = {
            "title": "Portfolio Analysis Report",
            "generated_at": datetime.now().isoformat(),
            "summary": self._format_summary(summary),
            "allocation_charts": self._format_allocation(allocation),
            "performance_analysis": self._format_performance(performance),
            "risk_analysis": self._format_risk_metrics(risk),
            "holdings": self._format_holdings(holdings)
        }
        
        return report
    
    def _format_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio summary data."""
        formatted_summary = {
            "total_value": self._format_currency(summary.get("total_value", 0)),
            "total_cost": self._format_currency(summary.get("total_cost", 0)),
            "total_gain_loss": self._format_currency(summary.get("total_gain_loss", 0)),
            "total_gain_loss_percent": self._format_percentage(summary.get("total_gain_loss_percent", 0)),
            "securities_count": summary.get("securities_count", 0)
        }
        
        return formatted_summary
    
    def _format_allocation(self, allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio allocation data."""
        formatted_allocation = {}
        
        # Format asset class allocation
        if "by_asset_class" in allocation:
            formatted_allocation["by_asset_class"] = self._format_allocation_category(allocation["by_asset_class"])
        
        # Format sector allocation
        if "by_sector" in allocation:
            formatted_allocation["by_sector"] = self._format_allocation_category(allocation["by_sector"])
        
        # Format region allocation
        if "by_region" in allocation:
            formatted_allocation["by_region"] = self._format_allocation_category(allocation["by_region"])
        
        # Format currency allocation
        if "by_currency" in allocation:
            formatted_allocation["by_currency"] = self._format_allocation_category(allocation["by_currency"])
        
        return formatted_allocation
    
    def _format_allocation_category(self, category_data: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Format a single allocation category for chart display."""
        chart_data = []
        
        for key, data in category_data.items():
            chart_data.append({
                "name": key,
                "value": data.get("value", 0),
                "percent": data.get("percent", 0),
                "formatted_value": self._format_currency(data.get("value", 0)),
                "formatted_percent": self._format_percentage(data.get("percent", 0))
            })
        
        # Sort by value descending
        chart_data.sort(key=lambda x: x["value"], reverse=True)
        
        return chart_data
    
    def _format_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio performance data."""
        formatted_performance = {
            "returns": {},
            "annualized_returns": {}
        }
        
        # Format period returns
        if "returns" in performance:
            for period, value in performance["returns"].items():
                formatted_performance["returns"][period] = {
                    "value": value,
                    "formatted": self._format_percentage(value * 100)
                }
        
        # Format annualized returns
        if "annualized_returns" in performance:
            for period, value in performance["annualized_returns"].items():
                formatted_performance["annualized_returns"][period] = {
                    "value": value,
                    "formatted": self._format_percentage(value * 100)
                }
        
        return formatted_performance
    
    def _format_risk_metrics(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio risk metrics."""
        formatted_risk = {}
        
        # Format volatility
        if "volatility" in risk:
            formatted_risk["volatility"] = {
                "value": risk["volatility"],
                "formatted": self._format_percentage(risk["volatility"] * 100)
            }
        
        # Format Sharpe ratio
        if "sharpe_ratio" in risk:
            formatted_risk["sharpe_ratio"] = {
                "value": risk["sharpe_ratio"],
                "formatted": f"{risk['sharpe_ratio']:.2f}"
            }
        
        # Format Sortino ratio
        if "sortino_ratio" in risk:
            formatted_risk["sortino_ratio"] = {
                "value": risk["sortino_ratio"],
                "formatted": f"{risk['sortino_ratio']:.2f}"
            }
        
        # Format maximum drawdown
        if "max_drawdown" in risk:
            formatted_risk["max_drawdown"] = {
                "value": risk["max_drawdown"],
                "formatted": self._format_percentage(risk["max_drawdown"] * 100)
            }
        
        # Format beta
        if "beta" in risk:
            formatted_risk["beta"] = {
                "value": risk["beta"],
                "formatted": f"{risk['beta']:.2f}"
            }
        
        # Format alpha
        if "alpha" in risk:
            formatted_risk["alpha"] = {
                "value": risk["alpha"],
                "formatted": self._format_percentage(risk["alpha"] * 100)
            }
        
        # Format Value at Risk (VaR)
        if "var_95" in risk:
            formatted_risk["var_95"] = {
                "value": risk["var_95"],
                "formatted": self._format_currency(risk["var_95"])
            }
        
        if "var_99" in risk:
            formatted_risk["var_99"] = {
                "value": risk["var_99"],
                "formatted": self._format_currency(risk["var_99"])
            }
        
        # Format concentration risk
        if "concentration_risk" in risk:
            formatted_risk["concentration_risk"] = {
                "value": risk["concentration_risk"],
                "formatted": f"{risk['concentration_risk']:.2f}"
            }
        
        # Format diversification score
        if "diversification_score" in risk:
            formatted_risk["diversification_score"] = {
                "value": risk["diversification_score"],
                "formatted": f"{risk['diversification_score']:.1f}"
            }
        
        return formatted_risk
    
    def _format_holdings(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format portfolio holdings data."""
        formatted_holdings = []
        
        for holding in holdings:
            formatted_holding = {
                "security": holding.get("security", "Unknown"),
                "isin": holding.get("isin", ""),
                "ticker": holding.get("ticker", ""),
                "asset_class": holding.get("asset_class", "Unknown"),
                "sector": holding.get("sector", "Unknown"),
                "region": holding.get("region", "Unknown"),
                "currency": holding.get("currency", "Unknown"),
                "quantity": holding.get("quantity", 0),
                "price": {
                    "value": holding.get("price", 0),
                    "formatted": self._format_currency(holding.get("price", 0))
                },
                "value": {
                    "value": holding.get("value", 0),
                    "formatted": self._format_currency(holding.get("value", 0))
                },
                "weight": {
                    "value": holding.get("weight", 0),
                    "formatted": self._format_percentage(holding.get("weight", 0))
                },
                "gain_loss": {
                    "value": holding.get("gain_loss", 0),
                    "formatted": self._format_currency(holding.get("gain_loss", 0))
                },
                "gain_loss_percent": {
                    "value": holding.get("gain_loss_percent", 0),
                    "formatted": self._format_percentage(holding.get("gain_loss_percent", 0))
                }
            }
            
            formatted_holdings.append(formatted_holding)
        
        # Sort by value descending
        formatted_holdings.sort(key=lambda x: x["value"]["value"], reverse=True)
        
        return formatted_holdings
    
    def _portfolio_to_html(self, data: Dict[str, Any]) -> str:
        """Convert portfolio report data to HTML."""
        html = "<div class='portfolio-report'>"
        
        # Summary section
        html += "<section class='summary-section'>"
        html += "<h2>Portfolio Summary</h2>"
        html += "<div class='summary-grid'>"
        html += f"<div class='summary-item'><span class='label'>Total Value:</span> <span class='value'>{data.get('summary', {}).get('total_value', '$0.00')}</span></div>"
        html += f"<div class='summary-item'><span class='label'>Total Cost:</span> <span class='value'>{data.get('summary', {}).get('total_cost', '$0.00')}</span></div>"
        html += f"<div class='summary-item'><span class='label'>Total Gain/Loss:</span> <span class='value'>{data.get('summary', {}).get('total_gain_loss', '$0.00')}</span></div>"
        html += f"<div class='summary-item'><span class='label'>Total Gain/Loss %:</span> <span class='value'>{data.get('summary', {}).get('total_gain_loss_percent', '0.00%')}</span></div>"
        html += f"<div class='summary-item'><span class='label'>Securities Count:</span> <span class='value'>{data.get('summary', {}).get('securities_count', 0)}</span></div>"
        html += "</div>"
        html += "</section>"
        
        # Allocation section
        html += "<section class='allocation-section'>"
        html += "<h2>Asset Allocation</h2>"
        
        # Asset class allocation
        if "allocation_charts" in data and "by_asset_class" in data["allocation_charts"]:
            html += "<div class='allocation-chart'>"
            html += "<h3>By Asset Class</h3>"
            html += "<table class='allocation-table'>"
            html += "<thead><tr><th>Asset Class</th><th>Value</th><th>Percentage</th></tr></thead>"
            html += "<tbody>"
            
            for item in data["allocation_charts"]["by_asset_class"]:
                html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('formatted_value', '$0.00')}</td><td>{item.get('formatted_percent', '0.00%')}</td></tr>"
            
            html += "</tbody>"
            html += "</table>"
            html += "</div>"
        
        # Sector allocation
        if "allocation_charts" in data and "by_sector" in data["allocation_charts"]:
            html += "<div class='allocation-chart'>"
            html += "<h3>By Sector</h3>"
            html += "<table class='allocation-table'>"
            html += "<thead><tr><th>Sector</th><th>Value</th><th>Percentage</th></tr></thead>"
            html += "<tbody>"
            
            for item in data["allocation_charts"]["by_sector"]:
                html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('formatted_value', '$0.00')}</td><td>{item.get('formatted_percent', '0.00%')}</td></tr>"
            
            html += "</tbody>"
            html += "</table>"
            html += "</div>"
        
        html += "</section>"
        
        # Holdings section
        html += "<section class='holdings-section'>"
        html += "<h2>Portfolio Holdings</h2>"
        html += "<table class='holdings-table'>"
        html += "<thead><tr><th>Security</th><th>ISIN</th><th>Asset Class</th><th>Quantity</th><th>Price</th><th>Value</th><th>Weight</th><th>Gain/Loss</th><th>Gain/Loss %</th></tr></thead>"
        html += "<tbody>"
        
        for holding in data.get("holdings", []):
            html += "<tr>"
            html += f"<td>{holding.get('security', 'Unknown')}</td>"
            html += f"<td>{holding.get('isin', '')}</td>"
            html += f"<td>{holding.get('asset_class', 'Unknown')}</td>"
            html += f"<td>{holding.get('quantity', 0)}</td>"
            html += f"<td>{holding.get('price', {}).get('formatted', '$0.00')}</td>"
            html += f"<td>{holding.get('value', {}).get('formatted', '$0.00')}</td>"
            html += f"<td>{holding.get('weight', {}).get('formatted', '0.00%')}</td>"
            html += f"<td>{holding.get('gain_loss', {}).get('formatted', '$0.00')}</td>"
            html += f"<td>{holding.get('gain_loss_percent', {}).get('formatted', '0.00%')}</td>"
            html += "</tr>"
        
        html += "</tbody>"
        html += "</table>"
        html += "</section>"
        
        html += "</div>"
        return html
    
    def _portfolio_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert portfolio report data to Markdown."""
        markdown = "## Portfolio Summary\n\n"
        
        # Summary section
        summary = data.get("summary", {})
        markdown += f"- **Total Value:** {summary.get('total_value', '$0.00')}\n"
        markdown += f"- **Total Cost:** {summary.get('total_cost', '$0.00')}\n"
        markdown += f"- **Total Gain/Loss:** {summary.get('total_gain_loss', '$0.00')}\n"
        markdown += f"- **Total Gain/Loss %:** {summary.get('total_gain_loss_percent', '0.00%')}\n"
        markdown += f"- **Securities Count:** {summary.get('securities_count', 0)}\n\n"
        
        # Allocation section
        markdown += "## Asset Allocation\n\n"
        
        # Asset class allocation
        if "allocation_charts" in data and "by_asset_class" in data["allocation_charts"]:
            markdown += "### By Asset Class\n\n"
            markdown += "| Asset Class | Value | Percentage |\n"
            markdown += "|------------|-------|------------|\n"
            
            for item in data["allocation_charts"]["by_asset_class"]:
                markdown += f"| {item.get('name', 'Unknown')} | {item.get('formatted_value', '$0.00')} | {item.get('formatted_percent', '0.00%')} |\n"
            
            markdown += "\n"
        
        # Sector allocation
        if "allocation_charts" in data and "by_sector" in data["allocation_charts"]:
            markdown += "### By Sector\n\n"
            markdown += "| Sector | Value | Percentage |\n"
            markdown += "|--------|-------|------------|\n"
            
            for item in data["allocation_charts"]["by_sector"]:
                markdown += f"| {item.get('name', 'Unknown')} | {item.get('formatted_value', '$0.00')} | {item.get('formatted_percent', '0.00%')} |\n"
            
            markdown += "\n"
        
        # Holdings section
        markdown += "## Portfolio Holdings\n\n"
        markdown += "| Security | ISIN | Asset Class | Quantity | Price | Value | Weight | Gain/Loss | Gain/Loss % |\n"
        markdown += "|----------|------|------------|----------|-------|-------|--------|-----------|-------------|\n"
        
        for holding in data.get("holdings", [])[:10]:  # Limit to top 10 for readability
            markdown += f"| {holding.get('security', 'Unknown')} | {holding.get('isin', '')} | {holding.get('asset_class', 'Unknown')} | "
            markdown += f"{holding.get('quantity', 0)} | {holding.get('price', {}).get('formatted', '$0.00')} | "
            markdown += f"{holding.get('value', {}).get('formatted', '$0.00')} | {holding.get('weight', {}).get('formatted', '0.00%')} | "
            markdown += f"{holding.get('gain_loss', {}).get('formatted', '$0.00')} | {holding.get('gain_loss_percent', {}).get('formatted', '0.00%')} |\n"
        
        if len(data.get("holdings", [])) > 10:
            markdown += "\n*Note: Only showing top 10 holdings. Full report contains all holdings.*\n"
        
        return markdown
    
    # Helper methods for formatting values
    def _format_currency(self, value: float) -> str:
        """Format a value as currency."""
        if value >= 0:
            return f"${value:,.2f}"
        else:
            return f"-${abs(value):,.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format a value as percentage."""
        return f"{value:.2f}%"
