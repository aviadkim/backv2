"""
Test runner script.

This script runs all the tests for the AI feedback learning and AI enhanced processor.
"""
import os
import sys
import unittest
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_tests(test_type="all", verbose=False):
    """
    Run the tests.

    Args:
        test_type: Type of tests to run (all, unit, integration)
        verbose: Whether to print verbose output

    Returns:
        True if all tests pass, False otherwise
    """
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add tests based on test type
    if test_type in ["all", "unit"]:
        logger.info("Running unit tests...")
        from test_ai_feedback_learning import TestAIFeedbackLearning
        from test_ai_enhanced_processor import TestAIEnhancedProcessor

        # Add AI feedback learning tests
        test_suite.addTest(unittest.makeSuite(TestAIFeedbackLearning))

        # Add AI enhanced processor tests
        test_suite.addTest(unittest.makeSuite(TestAIEnhancedProcessor))

    if test_type in ["all", "integration"]:
        logger.info("Running integration tests...")
        from test_ai_learning_integration import TestAILearningIntegration

        # Add AI learning integration tests
        test_suite.addTest(unittest.makeSuite(TestAILearningIntegration))

    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    test_result = test_runner.run(test_suite)

    # Return True if all tests pass, False otherwise
    return test_result.wasSuccessful()

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for AI feedback learning and AI enhanced processor.")
    parser.add_argument("--test-type", choices=["all", "unit", "integration"], default="all",
                        help="Type of tests to run (all, unit, integration)")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--api-key", help="OpenRouter API key")

    args = parser.parse_args()

    # Set OpenRouter API key if provided
    if args.api_key:
        os.environ["OPENROUTER_API_KEY"] = args.api_key
        logger.info("OpenRouter API key set from command line.")
    elif os.environ.get("OPENROUTER_API_KEY"):
        logger.info("Using OpenRouter API key from environment.")
    else:
        logger.warning("No OpenRouter API key provided. Tests requiring API access may fail.")

    # Run tests
    success = run_tests(args.test_type, args.verbose)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
