import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Base class for generating financial reports."""
    
    def __init__(self, template_dir: str = "report_templates"):
        """Initialize the report generator."""
        self.template_dir = template_dir
        
        # Create template directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
    
    def generate_report(self, report_type: str, data: Dict[str, Any], 
                        output_format: str = "json") -> Dict[str, Any]:
        """
        Generate a report based on the specified type and data.
        
        Args:
            report_type: Type of report to generate (e.g., 'portfolio', 'profit_loss')
            data: Data to include in the report
            output_format: Format of the report output ('json', 'html', 'pdf', 'markdown')
            
        Returns:
            Dictionary containing the report data and metadata
        """
        # Validate input
        if not report_type:
            raise ValueError("Report type must be specified")
        
        if not data:
            raise ValueError("Report data must be provided")
        
        # Initialize report structure
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "data": {},
            "metadata": {
                "format": output_format
            }
        }
        
        try:
            # Generate report based on type
            if report_type == "portfolio":
                report["data"] = self._generate_portfolio_report(data)
            elif report_type == "profit_loss":
                report["data"] = self._generate_profit_loss_report(data)
            elif report_type == "balance_sheet":
                report["data"] = self._generate_balance_sheet_report(data)
            elif report_type == "cash_flow":
                report["data"] = self._generate_cash_flow_report(data)
            elif report_type == "financial_metrics":
                report["data"] = self._generate_financial_metrics_report(data)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Format the report
            if output_format == "html":
                report["html"] = self._format_as_html(report)
            elif output_format == "markdown":
                report["markdown"] = self._format_as_markdown(report)
            elif output_format == "pdf":
                report["pdf_path"] = self._format_as_pdf(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to generate {report_type} report: {str(e)}",
                "report_type": report_type,
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_portfolio_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a portfolio report."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        return {
            "title": "Portfolio Analysis Report",
            "summary": self._format_summary(data.get("summary", {})),
            "allocation": self._format_allocation(data.get("allocation", {})),
            "performance": self._format_performance(data.get("performance", {})),
            "risk": self._format_risk_metrics(data.get("risk", {})),
            "holdings": self._format_holdings(data.get("holdings", []))
        }
    
    def _generate_profit_loss_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a profit and loss report."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        return {
            "title": "Profit and Loss Report",
            "period": data.get("period", ""),
            "summary": self._format_pl_summary(data),
            "details": self._format_pl_details(data)
        }
    
    def _generate_balance_sheet_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a balance sheet report."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        return {
            "title": "Balance Sheet Report",
            "as_of_date": data.get("as_of_date", datetime.now().isoformat()),
            "assets": self._format_assets(data.get("assets", {})),
            "liabilities": self._format_liabilities(data.get("liabilities", {})),
            "equity": self._format_equity(data.get("equity", {}))
        }
    
    def _generate_cash_flow_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cash flow report."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        return {
            "title": "Cash Flow Report",
            "period": data.get("period", ""),
            "operating": self._format_operating_cash_flow(data.get("operating", {})),
            "investing": self._format_investing_cash_flow(data.get("investing", {})),
            "financing": self._format_financing_cash_flow(data.get("financing", {}))
        }
    
    def _generate_financial_metrics_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a financial metrics report."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        return {
            "title": "Financial Metrics Report",
            "as_of_date": data.get("as_of_date", datetime.now().isoformat()),
            "profitability": self._format_profitability_metrics(data.get("profitability", {})),
            "liquidity": self._format_liquidity_metrics(data.get("liquidity", {})),
            "solvency": self._format_solvency_metrics(data.get("solvency", {})),
            "valuation": self._format_valuation_metrics(data.get("valuation", {}))
        }
    
    # Helper methods for formatting report sections
    def _format_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio summary data."""
        return summary
    
    def _format_allocation(self, allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio allocation data."""
        return allocation
    
    def _format_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio performance data."""
        return performance
    
    def _format_risk_metrics(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """Format portfolio risk metrics."""
        return risk
    
    def _format_holdings(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format portfolio holdings data."""
        return holdings
    
    def _format_pl_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format profit and loss summary."""
        return {
            "revenue": data.get("revenue", 0),
            "expenses": data.get("expenses", 0),
            "net_income": data.get("net_income", 0)
        }
    
    def _format_pl_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format profit and loss details."""
        return {
            "revenue_items": data.get("revenue_items", []),
            "expense_items": data.get("expense_items", [])
        }
    
    def _format_assets(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Format balance sheet assets."""
        return assets
    
    def _format_liabilities(self, liabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Format balance sheet liabilities."""
        return liabilities
    
    def _format_equity(self, equity: Dict[str, Any]) -> Dict[str, Any]:
        """Format balance sheet equity."""
        return equity
    
    def _format_operating_cash_flow(self, operating: Dict[str, Any]) -> Dict[str, Any]:
        """Format operating cash flow."""
        return operating
    
    def _format_investing_cash_flow(self, investing: Dict[str, Any]) -> Dict[str, Any]:
        """Format investing cash flow."""
        return investing
    
    def _format_financing_cash_flow(self, financing: Dict[str, Any]) -> Dict[str, Any]:
        """Format financing cash flow."""
        return financing
    
    def _format_profitability_metrics(self, profitability: Dict[str, Any]) -> Dict[str, Any]:
        """Format profitability metrics."""
        return profitability
    
    def _format_liquidity_metrics(self, liquidity: Dict[str, Any]) -> Dict[str, Any]:
        """Format liquidity metrics."""
        return liquidity
    
    def _format_solvency_metrics(self, solvency: Dict[str, Any]) -> Dict[str, Any]:
        """Format solvency metrics."""
        return solvency
    
    def _format_valuation_metrics(self, valuation: Dict[str, Any]) -> Dict[str, Any]:
        """Format valuation metrics."""
        return valuation
    
    # Output format methods
    def _format_as_html(self, report: Dict[str, Any]) -> str:
        """Format report as HTML."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        html = f"<html><head><title>{report.get('data', {}).get('title', 'Financial Report')}</title></head><body>"
        html += f"<h1>{report.get('data', {}).get('title', 'Financial Report')}</h1>"
        html += f"<p>Generated at: {report.get('generated_at', '')}</p>"
        html += "<hr>"
        
        # Add report content based on type
        if report.get("report_type") == "portfolio":
            html += self._portfolio_to_html(report.get("data", {}))
        elif report.get("report_type") == "profit_loss":
            html += self._profit_loss_to_html(report.get("data", {}))
        elif report.get("report_type") == "balance_sheet":
            html += self._balance_sheet_to_html(report.get("data", {}))
        elif report.get("report_type") == "cash_flow":
            html += self._cash_flow_to_html(report.get("data", {}))
        elif report.get("report_type") == "financial_metrics":
            html += self._financial_metrics_to_html(report.get("data", {}))
        
        html += "</body></html>"
        return html
    
    def _format_as_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as Markdown."""
        # This is a placeholder implementation
        # Subclasses should override this method with specific implementation
        markdown = f"# {report.get('data', {}).get('title', 'Financial Report')}\n\n"
        markdown += f"Generated at: {report.get('generated_at', '')}\n\n"
        markdown += "---\n\n"
        
        # Add report content based on type
        if report.get("report_type") == "portfolio":
            markdown += self._portfolio_to_markdown(report.get("data", {}))
        elif report.get("report_type") == "profit_loss":
            markdown += self._profit_loss_to_markdown(report.get("data", {}))
        elif report.get("report_type") == "balance_sheet":
            markdown += self._balance_sheet_to_markdown(report.get("data", {}))
        elif report.get("report_type") == "cash_flow":
            markdown += self._cash_flow_to_markdown(report.get("data", {}))
        elif report.get("report_type") == "financial_metrics":
            markdown += self._financial_metrics_to_markdown(report.get("data", {}))
        
        return markdown
    
    def _format_as_pdf(self, report: Dict[str, Any]) -> str:
        """Format report as PDF and return the file path."""
        # This is a placeholder implementation
        # In a real implementation, this would use a PDF generation library
        # For now, we'll just create a placeholder file path
        
        report_type = report.get("report_type", "report")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.pdf"
        file_path = os.path.join(self.template_dir, filename)
        
        # In a real implementation, we would generate the PDF here
        # For now, just log that we would generate it
        logger.info(f"Would generate PDF at {file_path}")
        
        return file_path
    
    # HTML formatting methods
    def _portfolio_to_html(self, data: Dict[str, Any]) -> str:
        """Convert portfolio report data to HTML."""
        # Placeholder implementation
        return "<p>Portfolio report content would go here</p>"
    
    def _profit_loss_to_html(self, data: Dict[str, Any]) -> str:
        """Convert profit and loss report data to HTML."""
        # Placeholder implementation
        return "<p>Profit and loss report content would go here</p>"
    
    def _balance_sheet_to_html(self, data: Dict[str, Any]) -> str:
        """Convert balance sheet report data to HTML."""
        # Placeholder implementation
        return "<p>Balance sheet report content would go here</p>"
    
    def _cash_flow_to_html(self, data: Dict[str, Any]) -> str:
        """Convert cash flow report data to HTML."""
        # Placeholder implementation
        return "<p>Cash flow report content would go here</p>"
    
    def _financial_metrics_to_html(self, data: Dict[str, Any]) -> str:
        """Convert financial metrics report data to HTML."""
        # Placeholder implementation
        return "<p>Financial metrics report content would go here</p>"
    
    # Markdown formatting methods
    def _portfolio_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert portfolio report data to Markdown."""
        # Placeholder implementation
        return "Portfolio report content would go here\n"
    
    def _profit_loss_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert profit and loss report data to Markdown."""
        # Placeholder implementation
        return "Profit and loss report content would go here\n"
    
    def _balance_sheet_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert balance sheet report data to Markdown."""
        # Placeholder implementation
        return "Balance sheet report content would go here\n"
    
    def _cash_flow_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert cash flow report data to Markdown."""
        # Placeholder implementation
        return "Cash flow report content would go here\n"
    
    def _financial_metrics_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert financial metrics report data to Markdown."""
        # Placeholder implementation
        return "Financial metrics report content would go here\n"
