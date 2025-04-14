"""
Tests for the financial agents.
"""
import os
import sys
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.financial_table_detector_agent import FinancialTableDetectorAgent
from agents.financial_data_analyzer_agent import FinancialDataAnalyzerAgent

class TestFinancialTableDetectorAgent(unittest.TestCase):
    """Tests for the FinancialTableDetectorAgent."""

    def setUp(self):
        """Set up the test."""
        self.agent = FinancialTableDetectorAgent()

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "Financial Table Detector")
        self.assertEqual(self.agent.lang, "heb+eng")

    def test_detect_table_type(self):
        """Test table type detection."""
        # Create a sample text block with portfolio keywords
        text_items = [
            {'text': 'ISIN', 'x': 10, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'כמות', 'x': 70, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'שער', 'x': 130, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'שווי', 'x': 190, 'y': 10, 'w': 50, 'h': 20}
        ]

        table_type = self.agent._detect_table_type(text_items)
        self.assertEqual(table_type, "portfolio")

        # Create a sample text block with balance sheet keywords
        text_items = [
            {'text': 'נכסים', 'x': 10, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'התחייבויות', 'x': 70, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'הון', 'x': 130, 'y': 10, 'w': 50, 'h': 20}
        ]

        table_type = self.agent._detect_table_type(text_items)
        self.assertEqual(table_type, "balance_sheet")

        # Create a sample text block with income statement keywords
        text_items = [
            {'text': 'הכנסות', 'x': 10, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'הוצאות', 'x': 70, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'רווח נקי', 'x': 130, 'y': 10, 'w': 50, 'h': 20}
        ]

        table_type = self.agent._detect_table_type(text_items)
        self.assertEqual(table_type, "income_statement")

        # Create a sample text block with no financial keywords
        text_items = [
            {'text': 'שם', 'x': 10, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'כתובת', 'x': 70, 'y': 10, 'w': 50, 'h': 20},
            {'text': 'טלפון', 'x': 130, 'y': 10, 'w': 50, 'h': 20}
        ]

        table_type = self.agent._detect_table_type(text_items)
        self.assertEqual(table_type, "unknown")

    def test_merge_table_regions(self):
        """Test merging table regions."""
        # Create two overlapping regions
        region1 = {
            'x1': 10, 'y1': 10, 'x2': 100, 'y2': 100,
            'rows': 5, 'cols': 3
        }

        region2 = {
            'x1': 50, 'y1': 50, 'x2': 150, 'y2': 150,
            'rows': 6, 'cols': 4,
            'table_type': 'portfolio'
        }

        merged_regions = self.agent._merge_table_regions([region1], [region2])

        # Should be merged into one region
        self.assertEqual(len(merged_regions), 1)

        # Check merged region properties
        merged = merged_regions[0]
        self.assertEqual(merged['x1'], 10)
        self.assertEqual(merged['y1'], 10)
        self.assertEqual(merged['x2'], 150)
        self.assertEqual(merged['y2'], 150)
        self.assertEqual(merged['rows'], 6)  # Max of both
        self.assertEqual(merged['cols'], 4)  # Max of both
        self.assertEqual(merged['table_type'], 'portfolio')  # From region2

        # Create two non-overlapping regions
        region3 = {
            'x1': 10, 'y1': 10, 'x2': 100, 'y2': 100,
            'rows': 5, 'cols': 3
        }

        region4 = {
            'x1': 200, 'y1': 200, 'x2': 300, 'y2': 300,
            'rows': 6, 'cols': 4,
            'table_type': 'balance_sheet'
        }

        merged_regions = self.agent._merge_table_regions([region3], [region4])

        # Should remain as two separate regions
        self.assertEqual(len(merged_regions), 2)

class TestFinancialDataAnalyzerAgent(unittest.TestCase):
    """Tests for the FinancialDataAnalyzerAgent."""

    def setUp(self):
        """Set up the test."""
        self.agent = FinancialDataAnalyzerAgent()

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "Financial Data Analyzer")

    def test_is_numeric_column(self):
        """Test numeric column detection."""
        # Create a numeric column
        numeric_series = pd.Series(['100', '200.5', '300,000', '400'])
        self.assertTrue(self.agent._is_numeric_column(numeric_series))

        # Create a non-numeric column
        non_numeric_series = pd.Series(['abc', 'def', 'ghi', 'jkl'])
        self.assertFalse(self.agent._is_numeric_column(non_numeric_series))

        # Create a mixed column (less than 70% numeric)
        mixed_series = pd.Series(['100', 'abc', '200', 'def'])
        self.assertFalse(self.agent._is_numeric_column(mixed_series))

        # Create a mixed column (more than 70% numeric)
        mixed_series = pd.Series(['100', '200', '300', 'abc'])
        self.assertTrue(self.agent._is_numeric_column(mixed_series))

    def test_convert_to_numeric(self):
        """Test converting to numeric values."""
        # Create a series with various formats
        series = pd.Series(['100', '200.5', '300,000', '₪400', '$500', '600€', '700%', 'abc'])

        # Convert to numeric
        numeric_series = self.agent._convert_to_numeric(series)

        # Check the results
        self.assertEqual(numeric_series[0], 100.0)
        self.assertEqual(numeric_series[1], 200.5)
        self.assertEqual(numeric_series[2], 300000.0)
        self.assertEqual(numeric_series[3], 400.0)
        self.assertEqual(numeric_series[4], 500.0)
        self.assertEqual(numeric_series[5], 600.0)
        self.assertEqual(numeric_series[6], 700.0)
        self.assertEqual(numeric_series[7], 'abc')  # Non-numeric remains unchanged

    def test_detect_table_type(self):
        """Test table type detection."""
        # Create a portfolio table
        portfolio_df = pd.DataFrame({
            'נייר ערך': ['מניה א', 'מניה ב', 'מניה ג'],
            'ISIN': ['IL0001', 'IL0002', 'IL0003'],
            'כמות': [100, 200, 300],
            'שער': [10.5, 20.5, 30.5],
            'שווי': [1050, 4100, 9150]
        })

        table_type = self.agent._detect_table_type(portfolio_df)
        self.assertEqual(table_type, "portfolio")

        # Create a balance sheet table
        balance_sheet_df = pd.DataFrame({
            'סעיף': ['נכסים', 'התחייבויות', 'הון עצמי'],
            '2021': [1000000, 600000, 400000],
            '2022': [1200000, 700000, 500000]
        })

        table_type = self.agent._detect_table_type(balance_sheet_df)
        self.assertEqual(table_type, "balance_sheet")

        # Create an income statement table
        income_df = pd.DataFrame({
            'סעיף': ['הכנסות', 'הוצאות', 'רווח נקי'],
            '2021': [500000, 300000, 200000],
            '2022': [600000, 350000, 250000]
        })

        table_type = self.agent._detect_table_type(income_df)
        self.assertEqual(table_type, "income_statement")

        # Create a general table
        general_df = pd.DataFrame({
            'שם': ['אבי', 'בני', 'גדי'],
            'גיל': [30, 40, 50],
            'עיר': ['תל אביב', 'ירושלים', 'חיפה']
        })

        table_type = self.agent._detect_table_type(general_df)
        self.assertEqual(table_type, "unknown")

    def test_analyze_portfolio_table(self):
        """Test portfolio table analysis."""
        # Create a portfolio table
        portfolio_df = pd.DataFrame({
            'נייר ערך': ['מניה א', 'מניה ב', 'מניה ג'],
            'ISIN': ['IL0001', 'IL0002', 'IL0003'],
            'כמות': [100, 200, 300],
            'שער': [10.5, 20.5, 30.5],
            'שווי': [1050, 4100, 9150],
            'סוג': ['מניות', 'מניות', 'אג"ח']
        })

        result = self.agent._analyze_portfolio_table(portfolio_df)

        # Check the result
        self.assertEqual(result['table_type'], 'portfolio')
        self.assertGreaterEqual(len(result['securities']), 1)

        # Check that securities exist
        securities = result['securities']
        self.assertTrue(len(securities) > 0)

        # Check the summary
        self.assertIn('summary', result)

        # Check that there's some data in the summary
        self.assertTrue(len(result['summary']) > 0)

    def test_analyze_balance_sheet(self):
        """Test balance sheet analysis."""
        # Create a balance sheet table
        balance_sheet_df = pd.DataFrame({
            'סעיף': ['נכסים שוטפים', 'נכסים קבועים', 'סה"כ נכסים',
                    'התחייבויות שוטפות', 'התחייבויות ארוכות', 'סה"כ התחייבויות',
                    'הון מניות', 'עודפים', 'סה"כ הון'],
            '2022': [500000, 700000, 1200000,
                    300000, 400000, 700000,
                    300000, 200000, 500000]
        })

        result = self.agent._analyze_balance_sheet(balance_sheet_df)

        # Check the result
        self.assertEqual(result['table_type'], 'balance_sheet')

        # Check that the result contains the expected keys
        self.assertIn('assets', result)
        self.assertIn('liabilities', result)
        self.assertIn('equity', result)
        self.assertIn('summary', result)

        # Check summary
        self.assertIn('total_assets', result['summary'])
        self.assertIn('total_liabilities', result['summary'])
        self.assertIn('total_equity', result['summary'])

    def test_analyze_income_statement(self):
        """Test income statement analysis."""
        # Create an income statement table
        income_df = pd.DataFrame({
            'סעיף': ['הכנסות ממכירות', 'הכנסות משירותים', 'סה"כ הכנסות',
                    'עלות המכר', 'הוצאות תפעול', 'סה"כ הוצאות',
                    'רווח גולמי', 'רווח תפעולי', 'רווח נקי'],
            '2022': [800000, 200000, 1000000,
                    400000, 300000, 700000,
                    600000, 300000, 300000]
        })

        result = self.agent._analyze_income_statement(income_df)

        # Check the result
        self.assertEqual(result['table_type'], 'income_statement')

        # Check that the result contains the expected keys
        self.assertIn('revenues', result)
        self.assertIn('expenses', result)
        self.assertIn('profits', result)
        self.assertIn('summary', result)

        # Check summary
        self.assertIn('total_revenue', result['summary'])
        self.assertIn('total_expenses', result['summary'])
        self.assertIn('net_profit', result['summary'])

    def test_general_table_analysis(self):
        """Test general table analysis."""
        # Create a general table
        general_df = pd.DataFrame({
            'שם': ['אבי', 'בני', 'גדי'],
            'גיל': [30, 40, 50],
            'משכורת': [15000, 20000, 25000],
            'בונוס': [1000, 2000, 3000]
        })

        result = self.agent._general_table_analysis(general_df)

        # Check the result
        self.assertEqual(result['table_type'], 'general')

        # Check dimensions
        self.assertEqual(result['summary']['dimensions']['rows'], 3)
        self.assertEqual(result['summary']['dimensions']['columns'], 4)

        # Check numeric columns
        self.assertEqual(result['summary']['numeric_columns'], 3)  # גיל, משכורת, בונוס

        # Check likely_financial flag
        self.assertTrue(result['summary']['likely_financial'])

        # Check data statistics
        self.assertAlmostEqual(result['data']['גיל']['mean'], 40.0)
        self.assertAlmostEqual(result['data']['גיל']['median'], 40.0)
        self.assertEqual(result['data']['גיל']['min'], 30)
        self.assertEqual(result['data']['גיל']['max'], 50)

        self.assertAlmostEqual(result['data']['משכורת']['mean'], 20000.0)
        self.assertAlmostEqual(result['data']['משכורת']['median'], 20000.0)
        self.assertEqual(result['data']['משכורת']['min'], 15000)
        self.assertEqual(result['data']['משכורת']['max'], 25000)

if __name__ == '__main__':
    unittest.main()
