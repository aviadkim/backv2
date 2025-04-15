"""
Test script for the Financial Document Processor V2.

This script tests the Financial Document Processor V2 on a sample financial document.
"""
import os
import sys
import logging
import argparse
from financial_document_processor_v2 import FinancialDocumentProcessorV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_processor(pdf_path, output_dir):
    """Test the Financial Document Processor V2."""
    # Initialize the processor
    processor = FinancialDocumentProcessorV2()
    
    # Process the document
    logger.info(f"Processing document: {pdf_path}")
    result = processor.process(pdf_path, output_dir=output_dir)
    
    # Check for errors
    if "error" in result:
        logger.error(f"Error processing document: {result['error']}")
        return False
    
    # Verify portfolio value
    portfolio_value = processor.get_portfolio_value()
    if not portfolio_value:
        logger.warning("Portfolio value not found")
    else:
        logger.info(f"Portfolio value: ${portfolio_value:,.2f}")
    
    # Verify securities
    securities = processor.get_securities()
    if not securities:
        logger.warning("No securities found")
    else:
        logger.info(f"Found {len(securities)} securities")
        
        # Verify top securities
        top_securities = processor.get_top_securities(5)
        logger.info("Top 5 securities by valuation:")
        for i, security in enumerate(top_securities, 1):
            logger.info(f"{i}. {security.get('description', security.get('isin', 'Unknown'))}: ${security.get('valuation', 0):,.2f}")
    
    # Verify asset allocation
    asset_allocation = processor.get_asset_allocation()
    if not asset_allocation:
        logger.warning("No asset allocation found")
    else:
        logger.info(f"Found {len(asset_allocation)} asset allocation entries")
        
        # Verify top asset classes
        top_asset_classes = processor.get_top_asset_classes(5)
        logger.info("Top 5 asset classes by percentage:")
        for i, allocation in enumerate(top_asset_classes, 1):
            logger.info(f"{i}. {allocation.get('asset_class', 'Unknown')}: {allocation.get('percentage', 0):.2f}%")
    
    # Verify validation results
    validation = processor.get_validation_results()
    if not validation:
        logger.warning("No validation results found")
    else:
        logger.info("Validation results:")
        for section, result in validation.items():
            if section != "overall":
                continue
            logger.info(f"Overall: {'Valid' if result.get('valid', False) else 'Invalid'}")
            
            if "issues" in result and result["issues"]:
                logger.info(f"  Issues ({len(result['issues'])}):")
                for issue in result["issues"]:
                    logger.info(f"  - {issue}")
    
    # Verify structured products
    structured_products = processor.get_structured_products()
    if not structured_products:
        logger.warning("No structured products found")
    else:
        logger.info(f"Found {len(structured_products)} structured products")
    
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"Comprehensive report: {os.path.join(output_dir, 'comprehensive_report.html')}")
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the Financial Document Processor V2.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create output directory if not specified
    if not args.output_dir:
        file_name = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output_dir = f"{file_name}_test_results"
    
    # Test the processor
    success = test_processor(args.file_path, args.output_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
