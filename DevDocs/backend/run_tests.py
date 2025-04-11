#!/usr/bin/env python
import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests.test_financial_document_processor import TestFinancialDocumentProcessor
from tests.test_portfolio_analyzer import TestPortfolioAnalyzer
from tests.test_report_generator import TestReportGenerator, TestPortfolioReportGenerator, TestFinancialStatementReportGenerator

def run_tests():
    """Run all tests and return the result."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFinancialDocumentProcessor))
    test_suite.addTest(unittest.makeSuite(TestPortfolioAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestReportGenerator))
    test_suite.addTest(unittest.makeSuite(TestPortfolioReportGenerator))
    test_suite.addTest(unittest.makeSuite(TestFinancialStatementReportGenerator))
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result

if __name__ == '__main__':
    result = run_tests()
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
