"""
Test script for enhanced document processing

This script tests the enhanced document processing pipeline on the messos.pdf file
and compares the results with the original processing.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced document processor
from DevDocs.backend.enhanced_processing.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_processing(pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Test the enhanced document processing pipeline.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output files
        
    Returns:
        Processing results
    """
    logger.info(f"Testing enhanced processing on {pdf_path}")
    
    # Create output directory if not provided
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(pdf_path), 'enhanced_output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        logger.warning("No API key found in environment variables")
        logger.warning("AI validation will be limited")
    
    # Create processor
    processor = DocumentProcessor(api_key=api_key)
    
    # Process document
    start_time = time.time()
    result = processor.process(pdf_path, output_dir)
    processing_time = time.time() - start_time
    
    # Save results
    results_path = os.path.join(output_dir, 'test_results.json')
    
    test_results = {
        'pdf_path': pdf_path,
        'processing_time': processing_time,
        'securities_count': len(result['portfolio']['securities']),
        'asset_classes_count': len(result['portfolio']['asset_allocation']),
        'total_value': result['portfolio']['total_value'],
        'currency': result['portfolio']['currency']
    }
    
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Test results saved to {results_path}")
    logger.info(f"Processing time: {processing_time:.2f} seconds")
    logger.info(f"Securities count: {test_results['securities_count']}")
    logger.info(f"Asset classes count: {test_results['asset_classes_count']}")
    logger.info(f"Total value: {test_results['total_value']} {test_results['currency']}")
    
    return result

def evaluate_results(enhanced_result: Dict[str, Any], original_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate the results of the enhanced processing.
    
    Args:
        enhanced_result: Results from enhanced processing
        original_result: Results from original processing (if available)
        
    Returns:
        Evaluation metrics
    """
    logger.info("Evaluating results")
    
    # Initialize evaluation metrics
    evaluation = {
        'securities_count': len(enhanced_result['portfolio']['securities']),
        'asset_classes_count': len(enhanced_result['portfolio']['asset_allocation']),
        'total_value': enhanced_result['portfolio']['total_value'],
        'currency': enhanced_result['portfolio']['currency'],
        'has_all_isins': False,
        'has_correct_total': False,
        'has_all_asset_classes': False,
        'improvement_metrics': {}
    }
    
    # Check if all 41 ISINs are extracted
    if evaluation['securities_count'] >= 41:
        evaluation['has_all_isins'] = True
    
    # Check if total value is correct (19,510,599)
    if abs(evaluation['total_value'] - 19510599) / 19510599 < 0.01:  # Within 1%
        evaluation['has_correct_total'] = True
    
    # Check if all asset classes are extracted
    expected_classes = ['Liquidity', 'Bonds', 'Equities', 'Structured products', 'Other assets']
    asset_classes = enhanced_result['portfolio']['asset_allocation'].keys()
    
    missing_classes = [cls for cls in expected_classes if cls not in asset_classes]
    evaluation['missing_asset_classes'] = missing_classes
    evaluation['has_all_asset_classes'] = len(missing_classes) == 0
    
    # Compare with original results if available
    if original_result:
        original_securities_count = len(original_result.get('securities', []))
        original_asset_classes_count = len(original_result.get('asset_allocation', {}))
        original_total_value = original_result.get('total_value')
        
        evaluation['improvement_metrics'] = {
            'securities_count_improvement': evaluation['securities_count'] - original_securities_count,
            'asset_classes_count_improvement': evaluation['asset_classes_count'] - original_asset_classes_count,
            'total_value_improvement': abs(evaluation['total_value'] - 19510599) < abs(original_total_value - 19510599) if original_total_value else True
        }
    
    # Calculate overall accuracy
    accuracy_metrics = [
        evaluation['has_all_isins'],
        evaluation['has_correct_total'],
        evaluation['has_all_asset_classes']
    ]
    
    evaluation['overall_accuracy'] = sum(1 for metric in accuracy_metrics if metric) / len(accuracy_metrics)
    
    logger.info(f"Overall accuracy: {evaluation['overall_accuracy'] * 100:.2f}%")
    
    if evaluation['has_all_isins']:
        logger.info("✅ All 41 ISINs extracted successfully")
    else:
        logger.info(f"❌ Only {evaluation['securities_count']} ISINs extracted (expected 41)")
    
    if evaluation['has_correct_total']:
        logger.info("✅ Correct total value extracted")
    else:
        logger.info(f"❌ Incorrect total value: {evaluation['total_value']} (expected 19,510,599)")
    
    if evaluation['has_all_asset_classes']:
        logger.info("✅ All asset classes extracted successfully")
    else:
        logger.info(f"❌ Missing asset classes: {evaluation['missing_asset_classes']}")
    
    return evaluation

def load_original_results(results_path: str) -> Optional[Dict[str, Any]]:
    """
    Load original processing results if available.
    
    Args:
        results_path: Path to the original results file
        
    Returns:
        Original results or None if not available
    """
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning(f"Original results not found at {results_path}")
        return None

def main():
    """
    Main function to run the test.
    """
    # Get PDF path from command line or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Try to find messos.pdf in the current directory or subdirectories
        pdf_path = None
        for root, _, files in os.walk('.'):
            for file in files:
                if file.lower() == 'messos.pdf':
                    pdf_path = os.path.join(root, file)
                    break
            if pdf_path:
                break
        
        if not pdf_path:
            logger.error("messos.pdf not found")
            return
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(pdf_path), 'enhanced_output')
    
    # Test enhanced processing
    enhanced_result = test_enhanced_processing(pdf_path, output_dir)
    
    # Load original results if available
    original_results_path = os.path.join(os.path.dirname(pdf_path), 'original_output', 'test_results.json')
    original_result = load_original_results(original_results_path)
    
    # Evaluate results
    evaluation = evaluate_results(enhanced_result, original_result)
    
    # Save evaluation
    evaluation_path = os.path.join(output_dir, 'evaluation.json')
    with open(evaluation_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Evaluation saved to {evaluation_path}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("ENHANCED PROCESSING TEST RESULTS")
    print("=" * 50)
    print(f"PDF: {pdf_path}")
    print(f"Securities extracted: {evaluation['securities_count']} / 41")
    print(f"Total value: {evaluation['total_value']} {evaluation['currency']}")
    print(f"Asset classes: {evaluation['asset_classes_count']} / {len(['Liquidity', 'Bonds', 'Equities', 'Structured products', 'Other assets'])}")
    print(f"Overall accuracy: {evaluation['overall_accuracy'] * 100:.2f}%")
    
    if original_result:
        print("\nIMPROVEMENT METRICS")
        print(f"Securities count: {evaluation['improvement_metrics']['securities_count_improvement']:+d}")
        print(f"Asset classes count: {evaluation['improvement_metrics']['asset_classes_count_improvement']:+d}")
        print(f"Total value accuracy: {'Improved' if evaluation['improvement_metrics']['total_value_improvement'] else 'No improvement'}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
