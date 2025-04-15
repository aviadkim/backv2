"""
Google Cloud Deployment - Demonstrates how to deploy the financial document processor to Google Cloud.

This module shows how to deploy the financial document processor to Google Cloud Run.
"""
import os
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
import tempfile

# Import the financial document processor
from financial_document_processor_v2 import FinancialDocumentProcessorV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize the processor
processor = FinancialDocumentProcessorV2()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/process', methods=['POST'])
def process_document():
    """
    Process a financial document.
    
    Expects a multipart/form-data request with a 'file' field containing the PDF document.
    
    Returns:
        JSON response containing processing results
    """
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({"error": "Empty file provided"}), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)
            
            # Process the document
            result = processor.process(temp_file_path, output_dir=temp_dir)
            
            # Return the extraction results
            if "extraction_results" in result:
                return jsonify(result["extraction_results"])
            else:
                return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_document():
    """
    Query a processed document.
    
    Expects a JSON request with 'file' field containing the PDF document and 'query' field containing the query.
    
    Returns:
        JSON response containing query results
    """
    # Check if request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Get request data
    data = request.get_json()
    
    # Check if query is provided
    if 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({"error": "Empty file provided"}), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    query = data['query']
    
    try:
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)
            
            # Process the document
            result = processor.process(temp_file_path, output_dir=temp_dir)
            
            # Handle different query types
            if "portfolio value" in query.lower():
                portfolio_value = processor.get_portfolio_value()
                return jsonify({"portfolio_value": portfolio_value})
            
            elif "top securities" in query.lower():
                # Extract number from query (e.g., "top 5 securities" -> 5)
                import re
                num_match = re.search(r"top\s+(\d+)", query.lower())
                n = int(num_match.group(1)) if num_match else 5
                
                top_securities = processor.get_top_securities(n)
                return jsonify({"top_securities": top_securities})
            
            elif "asset allocation" in query.lower():
                asset_allocation = processor.get_asset_allocation()
                return jsonify({"asset_allocation": asset_allocation})
            
            elif "structured products" in query.lower():
                structured_products = processor.get_structured_products()
                return jsonify({"structured_products": structured_products})
            
            elif "isin" in query.lower():
                # Extract ISIN from query
                import re
                isin_match = re.search(r"([A-Z]{2}[A-Z0-9]{9}[0-9])", query)
                if isin_match:
                    isin = isin_match.group(1)
                    
                    # Find security with this ISIN
                    securities = processor.get_securities()
                    for security in securities:
                        if security.get("isin") == isin:
                            return jsonify({"security": security})
                    
                    return jsonify({"error": f"No security found with ISIN {isin}"}), 404
                else:
                    return jsonify({"error": "Please provide a valid ISIN"}), 400
            
            else:
                return jsonify({"error": "Unsupported query type"}), 400
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/validate', methods=['POST'])
def validate_document():
    """
    Validate a financial document.
    
    Expects a multipart/form-data request with a 'file' field containing the PDF document.
    
    Returns:
        JSON response containing validation results
    """
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({"error": "Empty file provided"}), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)
            
            # Process the document
            result = processor.process(temp_file_path, output_dir=temp_dir)
            
            # Return the validation results
            if "extraction_results" in result and "validation" in result["extraction_results"]:
                return jsonify(result["extraction_results"]["validation"])
            else:
                return jsonify({"error": "Validation results not found"}), 500
    
    except Exception as e:
        logger.error(f"Error validating document: {str(e)}")
        return jsonify({"error": str(e)}), 500

def main():
    """Main function."""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
