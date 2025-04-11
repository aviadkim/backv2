import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Import the modules to test
from report_generator import ReportGenerator, PortfolioReportGenerator, FinancialStatementReportGenerator

class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator base class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.report_generator = ReportGenerator(template_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test report generator initialization."""
        self.assertEqual(self.report_generator.template_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_generate_report_invalid_input(self):
        """Test generate_report with invalid input."""
        # Test with empty report type
        with self.assertRaises(ValueError):
            self.report_generator.generate_report("", {"data": "test"})
        
        # Test with empty data
        with self.assertRaises(ValueError):
            self.report_generator.generate_report("portfolio", {})
    
    def test_generate_report_unsupported_type(self):
        """Test generate_report with unsupported report type."""
        with self.assertRaises(ValueError):
            self.report_generator.generate_report("unsupported_type", {"data": "test"})
    
    def test_format_as_html(self):
        """Test HTML formatting."""
        report = {
            "report_type": "portfolio",
            "generated_at": "2023-01-01T00:00:00",
            "data": {
                "title": "Test Portfolio Report"
            }
        }
        
        html = self.report_generator._format_as_html(report)
        
        # Check that HTML contains the title
        self.assertIn("<title>Test Portfolio Report</title>", html)
        self.assertIn("<h1>Test Portfolio Report</h1>", html)
    
    def test_format_as_markdown(self):
        """Test Markdown formatting."""
        report = {
            "report_type": "portfolio",
            "generated_at": "2023-01-01T00:00:00",
            "data": {
                "title": "Test Portfolio Report"
            }
        }
        
        markdown = self.report_generator._format_as_markdown(report)
        
        # Check that Markdown contains the title
        self.assertIn("# Test Portfolio Report", markdown)

class TestPortfolioReportGenerator(unittest.TestCase):
    """Test cases for the PortfolioReportGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.report_generator = PortfolioReportGenerator(template_dir=self.temp_dir)
        
        # Sample portfolio data
        self.sample_portfolio_data = {
            "summary": {
                "total_value": 44687.5,
                "total_cost": 40250,
                "total_gain_loss": 4437.5,
                "total_gain_loss_percent": 11.02,
                "securities_count": 3
            },
            "allocation": {
                "by_asset_class": {
                    "Equity": {
                        "value": 33812.5,
                        "percent": 75.66
                    },
                    "Bond": {
                        "value": 10875,
                        "percent": 24.34
                    }
                },
                "by_sector": {
                    "Technology": {
                        "value": 33812.5,
                        "percent": 75.66
                    },
                    "Fixed Income": {
                        "value": 10875,
                        "percent": 24.34
                    }
                }
            },
            "holdings": [
                {
                    "security": "Apple Inc.",
                    "isin": "US0378331005",
                    "ticker": "AAPL",
                    "asset_class": "Equity",
                    "sector": "Technology",
                    "value": 17525,
                    "weight": 39.22,
                    "gain_loss": 2525,
                    "gain_loss_percent": 16.83
                },
                {
                    "security": "Microsoft Corporation",
                    "isin": "US5949181045",
                    "ticker": "MSFT",
                    "asset_class": "Equity",
                    "sector": "Technology",
                    "value": 16287.5,
                    "weight": 36.44,
                    "gain_loss": 2287.5,
                    "gain_loss_percent": 16.34
                },
                {
                    "security": "Vanguard Total Bond Market ETF",
                    "isin": "US9219378356",
                    "ticker": "BND",
                    "asset_class": "Bond",
                    "sector": "Fixed Income",
                    "value": 10875,
                    "weight": 24.34,
                    "gain_loss": -375,
                    "gain_loss_percent": -3.33
                }
            ]
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_generate_portfolio_report(self):
        """Test generation of portfolio report."""
        result = self.report_generator._generate_portfolio_report(self.sample_portfolio_data)
        
        # Check that all sections are present
        self.assertIn("title", result)
        self.assertIn("summary", result)
        self.assertIn("allocation_charts", result)
        self.assertIn("holdings", result)
    
    def test_format_summary(self):
        """Test formatting of portfolio summary."""
        result = self.report_generator._format_summary(self.sample_portfolio_data["summary"])
        
        # Check formatted values
        self.assertEqual(result["total_value"], "$44,687.50")
        self.assertEqual(result["total_cost"], "$40,250.00")
        self.assertEqual(result["total_gain_loss"], "$4,437.50")
        self.assertEqual(result["total_gain_loss_percent"], "11.02%")
    
    def test_format_allocation(self):
        """Test formatting of portfolio allocation."""
        result = self.report_generator._format_allocation(self.sample_portfolio_data["allocation"])
        
        # Check asset class allocation
        self.assertIn("by_asset_class", result)
        self.assertEqual(len(result["by_asset_class"]), 2)
        
        # Check sector allocation
        self.assertIn("by_sector", result)
        self.assertEqual(len(result["by_sector"]), 2)
    
    def test_format_holdings(self):
        """Test formatting of portfolio holdings."""
        result = self.report_generator._format_holdings(self.sample_portfolio_data["holdings"])
        
        # Check number of holdings
        self.assertEqual(len(result), 3)
        
        # Check first holding
        self.assertEqual(result[0]["security"], "Apple Inc.")
        self.assertEqual(result[0]["value"]["formatted"], "$17,525.00")
        self.assertEqual(result[0]["weight"]["formatted"], "39.22%")
    
    def test_portfolio_to_html(self):
        """Test conversion of portfolio report to HTML."""
        report_data = self.report_generator._generate_portfolio_report(self.sample_portfolio_data)
        html = self.report_generator._portfolio_to_html(report_data)
        
        # Check that HTML contains key sections
        self.assertIn("<h2>Portfolio Summary</h2>", html)
        self.assertIn("<h2>Asset Allocation</h2>", html)
        self.assertIn("<h2>Portfolio Holdings</h2>", html)
    
    def test_portfolio_to_markdown(self):
        """Test conversion of portfolio report to Markdown."""
        report_data = self.report_generator._generate_portfolio_report(self.sample_portfolio_data)
        markdown = self.report_generator._portfolio_to_markdown(report_data)
        
        # Check that Markdown contains key sections
        self.assertIn("## Portfolio Summary", markdown)
        self.assertIn("## Asset Allocation", markdown)
        self.assertIn("## Portfolio Holdings", markdown)

class TestFinancialStatementReportGenerator(unittest.TestCase):
    """Test cases for the FinancialStatementReportGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.report_generator = FinancialStatementReportGenerator(template_dir=self.temp_dir)
        
        # Sample profit and loss data
        self.sample_pl_data = {
            "period": "2023-01-01 to 2023-12-31",
            "revenue_items": [
                {"name": "Product Sales", "amount": 800000, "notes": ""},
                {"name": "Service Revenue", "amount": 450000, "notes": ""}
            ],
            "expense_items": [
                {"name": "Cost of Goods Sold", "amount": 600000, "notes": ""},
                {"name": "Operating Expenses", "amount": 300000, "notes": ""},
                {"name": "Tax Expense", "amount": 50000, "notes": ""}
            ]
        }
        
        # Sample balance sheet data
        self.sample_bs_data = {
            "as_of_date": "2023-12-31",
            "assets": {
                "Current Assets": [
                    {"name": "Cash and Equivalents", "amount": 400000, "notes": ""},
                    {"name": "Accounts Receivable", "amount": 250000, "notes": ""},
                    {"name": "Inventory", "amount": 150000, "notes": ""}
                ],
                "Non-Current Assets": [
                    {"name": "Property, Plant and Equipment", "amount": 1200000, "notes": ""},
                    {"name": "Goodwill", "amount": 500000, "notes": ""}
                ]
            },
            "liabilities": {
                "Current Liabilities": [
                    {"name": "Accounts Payable", "amount": 200000, "notes": ""},
                    {"name": "Short-Term Debt", "amount": 100000, "notes": ""}
                ],
                "Non-Current Liabilities": [
                    {"name": "Long-Term Debt", "amount": 700000, "notes": ""}
                ]
            },
            "equity": {
                "Shareholders' Equity": [
                    {"name": "Share Capital", "amount": 1000000, "notes": ""},
                    {"name": "Retained Earnings", "amount": 500000, "notes": ""}
                ]
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_generate_profit_loss_report(self):
        """Test generation of profit and loss report."""
        result = self.report_generator._generate_profit_loss_report(self.sample_pl_data)
        
        # Check that all sections are present
        self.assertIn("title", result)
        self.assertIn("period", result)
        self.assertIn("summary", result)
        self.assertIn("details", result)
        
        # Check summary calculations
        self.assertEqual(result["summary"]["total_revenue"], "$1,250,000.00")
        self.assertEqual(result["summary"]["total_expenses"], "$950,000.00")
        self.assertEqual(result["summary"]["net_income"], "$300,000.00")
    
    def test_generate_balance_sheet_report(self):
        """Test generation of balance sheet report."""
        result = self.report_generator._generate_balance_sheet_report(self.sample_bs_data)
        
        # Check that all sections are present
        self.assertIn("title", result)
        self.assertIn("as_of_date", result)
        self.assertIn("summary", result)
        self.assertIn("details", result)
        
        # Check summary calculations
        self.assertEqual(result["summary"]["total_assets"], "$2,500,000.00")
        self.assertEqual(result["summary"]["total_liabilities"], "$1,000,000.00")
        self.assertEqual(result["summary"]["total_equity"], "$1,500,000.00")
    
    def test_profit_loss_to_html(self):
        """Test conversion of profit and loss report to HTML."""
        report_data = self.report_generator._generate_profit_loss_report(self.sample_pl_data)
        html = self.report_generator._profit_loss_to_html(report_data)
        
        # Check that HTML contains key sections
        self.assertIn("<h2>Profit and Loss Statement</h2>", html)
        self.assertIn("<h3>Revenue</h3>", html)
        self.assertIn("<h3>Expenses</h3>", html)
    
    def test_balance_sheet_to_html(self):
        """Test conversion of balance sheet report to HTML."""
        report_data = self.report_generator._generate_balance_sheet_report(self.sample_bs_data)
        html = self.report_generator._balance_sheet_to_html(report_data)
        
        # Check that HTML contains key sections
        self.assertIn("<h2>Balance Sheet</h2>", html)
        self.assertIn("<h3>Assets</h3>", html)
        self.assertIn("<h3>Liabilities</h3>", html)
        self.assertIn("<h3>Equity</h3>", html)

if __name__ == '__main__':
    unittest.main()
