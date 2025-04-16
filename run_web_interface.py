"""
Run Web Interface - Script to run the web interface with all agents integrated.

This script loads the environment variables, initializes all agents, and runs the web interface.
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
    parser = argparse.ArgumentParser(description="Run the web interface with all agents integrated.")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the web interface on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the web interface on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if OpenRouter API key is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
        logger.error("You can set it in the .env file or as an environment variable.")
        return 1
    
    logger.info("OpenRouter API key loaded successfully.")
    
    # Import the web interface
    try:
        from web_interface import app
        logger.info("Web interface loaded successfully.")
    except ImportError as e:
        logger.error(f"Error importing web interface: {str(e)}")
        return 1
    
    # Run the web interface
    logger.info(f"Starting web interface on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
