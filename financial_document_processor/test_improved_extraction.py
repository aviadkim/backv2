"""
Test script to verify the improved extraction implementation.
"""
import os
import sys
import logging
import argparse
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_preprocessor(pdf_path: str, output_dir: str):
    """Test enhanced preprocessor."""
    logger.info("Testing enhanced preprocessor...")
    
    try:
        from financial_document_processor.extractors.enhanced_preprocessor import EnhancedPreprocessor
        
        # Create preprocessor
        preprocessor = EnhancedPreprocessor(ocr_languages="eng")
        
        # Preprocess PDF
        result = preprocessor.preprocess(pdf_path, output_dir=output_dir)
        
        logger.info(f"Preprocessed PDF: {pdf_path}")
        logger.info(f"Metadata: {result['metadata']}")
        logger.info(f"Text extraction methods: {list(result['text'].keys())}")
        logger.info(f"Tables: {len(result['tables'])}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing enhanced preprocessor: {e}")
        return False

def test_multi_tool_extractor(pdf_path: str, output_dir: str):
    """Test multi-tool extractor."""
    logger.info("Testing multi-tool extractor...")
    
    try:
        from financial_document_processor.extractors.multi_tool_extractor import MultiToolExtractor
        
        # Create extractor
        extractor = MultiToolExtractor(ocr_languages="eng")
        
        # Extract data
        result = extractor.extract(pdf_path, output_dir=output_dir)
        
        logger.info(f"Extracted data from PDF: {pdf_path}")
        logger.info(f"Portfolio value: {result['portfolio_value'].get('value')}")
        logger.info(f"Securities: {len(result['securities'])}")
        logger.info(f"Asset allocation: {len(result['asset_allocation'])}")
        logger.info(f"Risk profile: {result['risk_profile'].get('value')}")
        logger.info(f"Currency: {result['currency'].get('value')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing multi-tool extractor: {e}")
        return False

def test_extraction_validator(pdf_path: str, output_dir: str):
    """Test extraction validator."""
    logger.info("Testing extraction validator...")
    
    try:
        from financial_document_processor.extractors.multi_tool_extractor import MultiToolExtractor
        from financial_document_processor.validation.validator import ExtractionValidator
        
        # Create extractor
        extractor = MultiToolExtractor(ocr_languages="eng")
        
        # Extract data
        extraction_result = extractor.extract(pdf_path, output_dir=output_dir)
        
        # Create validator
        validator = ExtractionValidator()
        
        # Validate extraction
        validation_result = validator.validate(extraction_result)
        
        logger.info(f"Validated extraction for PDF: {pdf_path}")
        logger.info(f"Overall valid: {validation_result['overall']['valid']}")
        logger.info(f"Portfolio value valid: {validation_result['portfolio_value']['valid']}")
        logger.info(f"Asset allocation valid: {validation_result['asset_allocation']['valid']}")
        logger.info(f"Securities valid: {validation_result['securities']['valid']}")
        logger.info(f"Issues: {validation_result['overall']['issues']}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing extraction validator: {e}")
        return False

def test_database_integration(pdf_path: str, output_dir: str):
    """Test database integration."""
    logger.info("Testing database integration...")
    
    try:
        from financial_document_processor.database.supabase_db import SupabaseDB
        from financial_document_processor.extractors.multi_tool_extractor import MultiToolExtractor
        from financial_document_processor.validation.validator import ExtractionValidator
        from financial_document_processor.processor import DocumentProcessor
        
        # Create database connection
        db = SupabaseDB(
            url=os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co"),
            key=os.environ.get("SUPABASE_KEY")
        )
        
        # Create extractor
        extractor = MultiToolExtractor(ocr_languages="eng")
        
        # Create validator
        validator = ExtractionValidator()
        
        # Create processor
        processor = DocumentProcessor(db, extractor, validator)
        
        # Process document
        result = processor.process_document(pdf_path, output_dir=output_dir)
        
        logger.info(f"Processed document: {pdf_path}")
        logger.info(f"Document ID: {result['document_id']}")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Portfolio value: {result.get('portfolio_value')}")
        logger.info(f"Securities count: {result.get('securities_count')}")
        logger.info(f"Asset allocations count: {result.get('asset_allocations_count')}")
        logger.info(f"Validation valid: {result.get('validation_valid')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing database integration: {e}")
        return False

def test_openrouter_integration(pdf_path: str, output_dir: str):
    """Test OpenRouter integration."""
    logger.info("Testing OpenRouter integration...")
    
    try:
        from financial_document_processor.agents.openrouter_agent import OpenRouterAgent
        from financial_document_processor.extractors.multi_tool_extractor import MultiToolExtractor
        
        # Create extractor
        extractor = MultiToolExtractor(ocr_languages="eng")
        
        # Extract data
        extraction_result = extractor.extract(pdf_path, output_dir=output_dir)
        
        # Get text
        text = ""
        for method, method_text in extraction_result["text"].items():
            text += f"\n\n--- {method.upper()} ---\n\n{method_text}"
        
        # Create OpenRouter agent
        agent = OpenRouterAgent(
            api_key=os.environ.get("OPENROUTER_API_KEY", "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"),
            model=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
        )
        
        # Query document
        question = "What is the total portfolio value?"
        answer = agent.query(text, question)
        
        logger.info(f"Queried document: {pdf_path}")
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {answer}")
        
        # Analyze document
        request = "Analyze the asset allocation and provide recommendations"
        analysis = agent.analyze(text, request)
        
        logger.info(f"Analyzed document: {pdf_path}")
        logger.info(f"Request: {request}")
        logger.info(f"Analysis: {analysis.get('analysis')}")
        logger.info(f"Key points: {analysis.get('key_points')}")
        logger.info(f"Recommendations: {analysis.get('recommendations')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing OpenRouter integration: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test improved extraction implementation")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", default="test_results", help="Directory to save test results")
    parser.add_argument("--test", choices=["all", "preprocessor", "extractor", "validator", "database", "openrouter"], default="all", help="Test to run")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run tests
    tests = []
    
    if args.test == "all" or args.test == "preprocessor":
        tests.append(("Enhanced Preprocessor", test_enhanced_preprocessor))
    
    if args.test == "all" or args.test == "extractor":
        tests.append(("Multi-Tool Extractor", test_multi_tool_extractor))
    
    if args.test == "all" or args.test == "validator":
        tests.append(("Extraction Validator", test_extraction_validator))
    
    if args.test == "all" or args.test == "database":
        tests.append(("Database Integration", test_database_integration))
    
    if args.test == "all" or args.test == "openrouter":
        tests.append(("OpenRouter Integration", test_openrouter_integration))
    
    results = []
    for name, test_func in tests:
        try:
            test_output_dir = os.path.join(args.output_dir, name.lower().replace(" ", "_"))
            os.makedirs(test_output_dir, exist_ok=True)
            
            result = test_func(args.pdf_path, test_output_dir)
            results.append((name, result))
        except Exception as e:
            logger.error(f"Error running test {name}: {e}")
            results.append((name, False))
    
    # Print results
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS")
    logger.info("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("=" * 50)
    logger.info(f"Overall: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
