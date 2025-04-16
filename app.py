"""
FinDoc Analyzer v1.0 - Main Application

This is the main application file for the FinDoc Analyzer v1.0 solution.
"""
import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.processors.multi_document_processor import MultiDocumentProcessor
from backend.processors.holdings_extractor import HoldingsExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend/build')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
OUTPUT_FOLDER = 'results'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API Routes
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload and process a financial document.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the document
        try:
            # Get API key from environment variable
            api_key = os.environ.get('OPENROUTER_API_KEY')
            
            # Create document processor
            processor = MultiDocumentProcessor(output_dir=OUTPUT_FOLDER, api_key=api_key)
            
            # Add and process the document
            document_id = processor.add_document(file_path)
            result = processor.get_document_data(document_id)
            
            # Extract comprehensive holdings information
            holdings_extractor = HoldingsExtractor(output_dir=OUTPUT_FOLDER)
            text = json.dumps(result)  # Convert result to text for extraction
            top_holdings = holdings_extractor.extract_comprehensive_holdings(text, document_id)
            
            # Prepare response
            response = {
                'client_info': result.get('client_info', {}),
                'document_date': result.get('document_date', ''),
                'portfolio_value': result.get('portfolio_value', 0),
                'top_holdings': top_holdings,
                'asset_allocation': result.get('asset_allocation', {})
            }
            
            return jsonify(response)
        
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/api/corrections', methods=['POST'])
def save_correction():
    """
    Save corrections to extracted data.
    """
    data = request.json
    document_id = data.get('document_id')
    original = data.get('original')
    corrected = data.get('corrected')
    
    # Save corrections to a file
    corrections_dir = os.path.join(OUTPUT_FOLDER, 'corrections')
    os.makedirs(corrections_dir, exist_ok=True)
    
    correction_path = os.path.join(corrections_dir, f"{document_id}_correction.json")
    with open(correction_path, 'w', encoding='utf-8') as f:
        json.dump({
            'document_id': document_id,
            'original': original,
            'corrected': corrected,
        }, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/api/results/<path:filename>')
def get_result(filename):
    """
    Get a result file.
    """
    return send_from_directory(OUTPUT_FOLDER, filename)

# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=False)
