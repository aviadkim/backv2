import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

# Import the module to test
from portfolio_analyzer import PortfolioAnalyzer

class TestPortfolioAnalyzer(unittest.TestCase):
    """Test cases for the PortfolioAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.analyzer = PortfolioAnalyzer()
        
        # Sample portfolio data
        self.sample_portfolio = [
            {
                "security": "Apple Inc.",
                "isin": "US0378331005",
                "ticker": "AAPL",
                "asset_class": "Equity",
                "sector": "Technology",
                "region": "North America",
                "currency": "USD",
                "quantity": 100,
                "price": 175.25,
                "value": 17525,
                "cost": 15000,
                "weight": 15.2,
                "gain_loss": 2525,
                "gain_loss_percent": 16.83
            },
            {
                "security": "Microsoft Corporation",
                "isin": "US5949181045",
                "ticker": "MSFT",
                "asset_class": "Equity",
                "sector": "Technology",
                "region": "North America",
                "currency": "USD",
                "quantity": 50,
                "price": 325.75,
                "value": 16287.5,
                "cost": 14000,
                "weight": 14.1,
                "gain_loss": 2287.5,
                "gain_loss_percent": 16.34
            },
            {
                "security": "Vanguard Total Bond Market ETF",
                "isin": "US9219378356",
                "ticker": "BND",
                "asset_class": "Bond",
                "sector": "Fixed Income",
                "region": "North America",
                "currency": "USD",
                "quantity": 150,
                "price": 72.5,
                "value": 10875,
                "cost": 11250,
                "weight": 9.4,
                "gain_loss": -375,
                "gain_loss_percent": -3.33
            }
        ]
        
        # Sample historical data
        today = datetime.now()
        self.sample_historical_data = {
            "US0378331005": [
                {"date": (today - timedelta(days=365)).isoformat(), "price": 150.0},
                {"date": (today - timedelta(days=180)).isoformat(), "price": 160.0},
                {"date": (today - timedelta(days=90)).isoformat(), "price": 165.0},
                {"date": (today - timedelta(days=30)).isoformat(), "price": 170.0},
                {"date": today.isoformat(), "price": 175.25}
            ],
            "US5949181045": [
                {"date": (today - timedelta(days=365)).isoformat(), "price": 280.0},
                {"date": (today - timedelta(days=180)).isoformat(), "price": 290.0},
                {"date": (today - timedelta(days=90)).isoformat(), "price": 300.0},
                {"date": (today - timedelta(days=30)).isoformat(), "price": 310.0},
                {"date": today.isoformat(), "price": 325.75}
            ],
            "US9219378356": [
                {"date": (today - timedelta(days=365)).isoformat(), "price": 75.0},
                {"date": (today - timedelta(days=180)).isoformat(), "price": 74.0},
                {"date": (today - timedelta(days=90)).isoformat(), "price": 73.5},
                {"date": (today - timedelta(days=30)).isoformat(), "price": 73.0},
                {"date": today.isoformat(), "price": 72.5}
            ]
        }
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer.risk_free_rate)
        self.assertIsNotNone(self.analyzer.market_return)
    
    def test_calculate_summary(self):
        """Test calculation of portfolio summary."""
        result = self.analyzer._calculate_summary(self.sample_portfolio)
        
        # Check total value
        self.assertAlmostEqual(result["total_value"], 44687.5, places=1)
        
        # Check total cost
        self.assertAlmostEqual(result["total_cost"], 40250, places=1)
        
        # Check total gain/loss
        self.assertAlmostEqual(result["total_gain_loss"], 4437.5, places=1)
        
        # Check securities count
        self.assertEqual(result["securities_count"], 3)
    
    def test_calculate_allocation(self):
        """Test calculation of portfolio allocation."""
        result = self.analyzer._calculate_allocation(self.sample_portfolio)
        
        # Check asset class allocation
        self.assertIn("by_asset_class", result)
        self.assertIn("Equity", result["by_asset_class"])
        self.assertIn("Bond", result["by_asset_class"])
        
        # Check sector allocation
        self.assertIn("by_sector", result)
        self.assertIn("Technology", result["by_sector"])
        self.assertIn("Fixed Income", result["by_sector"])
        
        # Check region allocation
        self.assertIn("by_region", result)
        self.assertIn("North America", result["by_region"])
    
    def test_analyze_portfolio_without_historical_data(self):
        """Test portfolio analysis without historical data."""
        result = self.analyzer.analyze_portfolio(self.sample_portfolio)
        
        # Check that all sections are present
        self.assertIn("summary", result)
        self.assertIn("allocation", result)
        self.assertIn("risk", result)
        self.assertIn("analyzed_at", result)
        
        # Check that performance is empty (no historical data)
        self.assertIn("performance", result)
        self.assertEqual(result["performance"], {})
    
    def test_analyze_portfolio_with_historical_data(self):
        """Test portfolio analysis with historical data."""
        result = self.analyzer.analyze_portfolio(self.sample_portfolio, self.sample_historical_data)
        
        # Check that all sections are present
        self.assertIn("summary", result)
        self.assertIn("allocation", result)
        self.assertIn("performance", result)
        self.assertIn("risk", result)
        self.assertIn("analyzed_at", result)
        
        # Check that performance has data
        self.assertIn("returns", result["performance"])
    
    def test_generate_portfolio_recommendations(self):
        """Test generation of portfolio recommendations."""
        result = self.analyzer.generate_portfolio_recommendations(self.sample_portfolio, "moderate")
        
        # Check that all sections are present
        self.assertIn("summary", result)
        self.assertIn("allocation_recommendations", result)
        self.assertIn("security_recommendations", result)
        self.assertIn("risk_recommendations", result)
        
        # Check that there are recommendations
        self.assertGreater(len(result["allocation_recommendations"]) + 
                          len(result["security_recommendations"]) + 
                          len(result["risk_recommendations"]), 0)
    
    def test_extract_numeric_value(self):
        """Test extraction of numeric values from various formats."""
        # Test integer
        self.assertEqual(self.analyzer._extract_numeric_value(100), 100.0)
        
        # Test float
        self.assertEqual(self.analyzer._extract_numeric_value(123.45), 123.45)
        
        # Test string with currency symbol
        self.assertEqual(self.analyzer._extract_numeric_value("$123.45"), 123.45)
        
        # Test string with commas
        self.assertEqual(self.analyzer._extract_numeric_value("1,234.56"), 1234.56)
        
        # Test string with percentage
        self.assertEqual(self.analyzer._extract_numeric_value("12.34%"), 0.1234)
        
        # Test string with K suffix
        self.assertEqual(self.analyzer._extract_numeric_value("123.4K"), 123400.0)
        
        # Test string with M suffix
        self.assertEqual(self.analyzer._extract_numeric_value("1.23M"), 1230000.0)
        
        # Test string with B suffix
        self.assertEqual(self.analyzer._extract_numeric_value("1.23B"), 1230000000.0)

if __name__ == '__main__':
    unittest.main()
