"""
Run All Agents - Script to run all agents with the best processing combination.

This script loads the environment variables, initializes all agents, and runs them
with the best processing combination.
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
    parser = argparse.ArgumentParser(description="Run all agents with the best processing combination.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--correct", action="store_true", help="Record a correction")
    parser.add_argument("--field", help="Field to correct")
    parser.add_argument("--original", help="Original value")
    parser.add_argument("--corrected", help="Corrected value")
    parser.add_argument("--suggestions", action="store_true", help="Generate improvement suggestions")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if OpenRouter API key is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
        logger.error("You can set it in the .env file or as an environment variable.")
        return 1
    
    logger.info("OpenRouter API key loaded successfully.")
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create output directory if not specified
    if not args.output_dir:
        file_name = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output_dir = f"{file_name}_ai_enhanced_results"
    
    # Import the AI enhanced processor
    try:
        from ai_enhanced_processor import AIEnhancedProcessor
        logger.info("AI enhanced processor loaded successfully.")
    except ImportError as e:
        logger.error(f"Error importing AI enhanced processor: {str(e)}")
        return 1
    
    # Initialize the AI enhanced processor
    processor = AIEnhancedProcessor()
    
    # Run the appropriate action based on the arguments
    if args.correct and args.field and args.original and args.corrected:
        # Process document
        processor.process_document(args.file_path, output_dir=args.output_dir)
        
        # Record correction
        success = processor.record_user_correction(
            args.field, args.original, args.corrected
        )
        
        if success:
            logger.info(f"Correction recorded for field: {args.field}")
        else:
            logger.error("Failed to record correction")
    
    elif args.suggestions:
        # Process document
        processor.process_document(args.file_path, output_dir=args.output_dir)
        
        # Generate improvement suggestions
        suggestions = processor.generate_improvement_suggestions()
        
        logger.info("Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            logger.info(f"{i}. {suggestion}")
    
    else:
        # Process document
        result = processor.process_document(args.file_path, output_dir=args.output_dir)
        
        # Print summary
        print("\nAI Enhanced Financial Document Processing Summary:")
        print("=================================================")
        
        portfolio_value = processor.get_portfolio_value()
        if portfolio_value:
            print(f"Portfolio Value: ${portfolio_value:,.2f}")
        else:
            print("Portfolio Value: Not found")
        
        securities = processor.get_securities()
        print(f"Securities: {len(securities)}")
        
        asset_allocation = processor.get_asset_allocation()
        print(f"Asset Allocation Entries: {len(asset_allocation)}")
        
        structured_products = processor.get_structured_products()
        print(f"Structured Products: {len(structured_products)}")
        
        # Print top securities
        top_securities = processor.get_top_securities(5)
        if top_securities:
            print("\nTop 5 Securities by Valuation:")
            for i, security in enumerate(top_securities, 1):
                print(f"{i}. {security.get('description', security.get('isin', 'Unknown'))}: ${security.get('valuation', 0):,.2f}")
        
        # Print AI analysis if available
        if "ai_analysis" in result:
            print("\nAI Analysis:")
            print(result["ai_analysis"])
        
        # Print AI corrections if available
        if "ai_corrections" in result and result["ai_corrections"]:
            print("\nAI Corrections:")
            for field, correction in result["ai_corrections"].items():
                print(f"{field}: {correction}")
        
        print(f"\nResults saved to: {args.output_dir}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
