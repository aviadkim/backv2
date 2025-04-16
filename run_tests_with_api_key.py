"""
Run Tests With API Key - Script to run tests with the API key.

This script loads the environment variables, sets the OpenRouter API key,
and runs the tests.
"""
import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests with the API key.")
    parser.add_argument("--test-type", choices=["all", "unit", "integration"], default="all",
                        help="Type of tests to run (all, unit, integration)")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if OpenRouter API key is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
        logger.error("You can set it in the .env file or as an environment variable.")
        return 1
    
    logger.info("OpenRouter API key loaded successfully.")
    
    # Import the run_tests function
    try:
        from run_tests import run_tests
        logger.info("Test runner loaded successfully.")
    except ImportError as e:
        logger.error(f"Error importing test runner: {str(e)}")
        return 1
    
    # Run tests
    success = run_tests(args.test_type, args.verbose)
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
