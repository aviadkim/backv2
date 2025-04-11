import os
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# Import the module to test
from financial_document_processor import FinancialDocumentProcessor

class TestFinancialDocumentProcessor(unittest.TestCase):
    """Test cases for the FinancialDocumentProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for uploads
        self.temp_dir = tempfile.mkdtemp()
        self.processor = FinancialDocumentProcessor(upload_dir=self.temp_dir)
        
        # Sample test data
        self.sample_text = """
        ANNUAL REPORT 2023
        
        INCOME STATEMENT
        Revenue: $1,250,000
        Cost of Goods Sold: $750,000
        Gross Profit: $500,000
        Operating Expenses: $300,000
        Operating Income: $200,000
        Net Income: $150,000
        
        BALANCE SHEET
        Total Assets: $2,500,000
        Current Assets: $800,000
        Cash and Equivalents: $400,000
        Accounts Receivable: $250,000
        Inventory: $150,000
        Non-Current Assets: $1,700,000
        Property, Plant and Equipment: $1,200,000
        Goodwill: $500,000
        
        Total Liabilities: $1,000,000
        Current Liabilities: $300,000
        Accounts Payable: $200,000
        Short-Term Debt: $100,000
        Non-Current Liabilities: $700,000
        Long-Term Debt: $700,000
        
        Shareholders' Equity: $1,500,000
        
        PORTFOLIO HOLDINGS
        Apple Inc. (AAPL) - 100 shares at $175.25, value $17,525
        Microsoft Corporation (MSFT) - 50 shares at $325.75, value $16,287.50
        """
        
        # Create a sample file
        self.sample_file_path = os.path.join(self.temp_dir, "sample_financial_doc.txt")
        with open(self.sample_file_path, "w") as f:
            f.write(self.sample_text)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove sample file
        if os.path.exists(self.sample_file_path):
            os.remove(self.sample_file_path)
        
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertEqual(self.processor.upload_dir, self.temp_dir)
        self.assertGreater(len(self.processor.financial_keywords), 50)
    
    def test_extract_enhanced_financial_data(self):
        """Test extraction of enhanced financial data."""
        result = self.processor._extract_enhanced_financial_data(self.sample_text)
        
        # Check that currencies were extracted
        self.assertIn("$", result["currencies"])
        
        # Check that amounts were extracted
        self.assertGreater(len(result["amounts"]), 5)
        self.assertIn("$1,250,000", result["amounts"])
        
        # Check that financial terms were extracted
        self.assertGreater(len(result["financial_terms"]), 0)
        
        # Check that profit/loss items were extracted
        self.assertGreater(len(result["profit_loss_items"]), 0)
        
        # Check that balance sheet items were extracted
        self.assertGreater(len(result["balance_sheet_items"]), 0)
    
    def test_extract_financial_statements(self):
        """Test extraction of financial statements."""
        result = self.processor._extract_financial_statements(self.sample_text)
        
        # Check income statement extraction
        self.assertIn("income_statement", result)
        self.assertGreater(len(result["income_statement"].get("line_items", [])), 0)
        
        # Check balance sheet extraction
        self.assertIn("balance_sheet", result)
        self.assertGreater(len(result["balance_sheet"].get("line_items", [])), 0)
    
    def test_extract_portfolio_data(self):
        """Test extraction of portfolio data."""
        result = self.processor._extract_portfolio_data(self.sample_text, [])
        
        # Check that portfolio items were extracted
        self.assertGreater(len(result), 0)
        
        # Check specific portfolio item
        apple_item = next((item for item in result if "Apple" in item.get("security", "")), None)
        self.assertIsNotNone(apple_item)
        self.assertIn("AAPL", apple_item.get("security", ""))
    
    @patch('document_processor.DocumentProcessor.process_document')
    def test_process_document(self, mock_base_process):
        """Test the process_document method."""
        # Mock the base class method
        mock_base_process.return_value = {
            "text": self.sample_text,
            "file_type": "txt",
            "file_size": len(self.sample_text),
            "tables": []
        }
        
        # Call the method
        result = self.processor.process_document(self.sample_file_path, "txt")
        
        # Check that the base method was called
        mock_base_process.assert_called_once()
        
        # Check that financial data was extracted
        self.assertIn("financial_data", result)
        self.assertIn("financial_statements", result)
        self.assertIn("portfolio_data", result)

if __name__ == '__main__':
    unittest.main()
