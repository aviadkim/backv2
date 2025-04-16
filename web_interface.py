"""
Web Interface - Simple web interface for the AI Enhanced Financial Document Processor.

This module provides a simple web interface for the AI Enhanced Financial Document Processor
using Flask.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, render_template, send_from_directory
import tempfile
from werkzeug.utils import secure_filename

# Import the AI enhanced processor
from ai_enhanced_processor import AIEnhancedProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize the processor with the OpenRouter API key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
processor = AIEnhancedProcessor(api_key=OPENROUTER_API_KEY)
if OPENROUTER_API_KEY:
    logger.info("OpenRouter API key loaded successfully.")
else:
    logger.warning("No OpenRouter API key provided. AI capabilities will be limited.")

# Create upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create results folder
RESULTS_FOLDER = 'results'
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Set allowed extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render index page."""
    return render_template('index.html')

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
    if not allowed_file(file.filename):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Create output directory
        output_dir = os.path.join(RESULTS_FOLDER, os.path.splitext(filename)[0])
        os.makedirs(output_dir, exist_ok=True)

        # Process the document
        result = processor.process_document(file_path, output_dir=output_dir)

        # Prepare response
        response = {
            "success": True,
            "filename": filename,
            "output_dir": output_dir,
            "portfolio_value": processor.get_portfolio_value(),
            "securities_count": len(processor.get_securities()),
            "asset_allocation_count": len(processor.get_asset_allocation()),
            "structured_products_count": len(processor.get_structured_products()),
            "top_securities": processor.get_top_securities(5)
        }

        # Add AI analysis if available
        if "ai_analysis" in result:
            response["ai_analysis"] = result["ai_analysis"]

        # Add AI corrections if available
        if "ai_corrections" in result and result["ai_corrections"]:
            response["ai_corrections"] = result["ai_corrections"]

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/correct', methods=['POST'])
def record_correction():
    """
    Record a correction made by the user.

    Expects a JSON request with 'filename', 'field', 'original_value', and 'corrected_value' fields.

    Returns:
        JSON response indicating success or failure
    """
    # Check if request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Get request data
    data = request.get_json()

    # Check if required fields are provided
    if 'filename' not in data or 'field' not in data or 'original_value' not in data or 'corrected_value' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Get file path
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(data['filename']))

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Process document
        output_dir = os.path.join(RESULTS_FOLDER, os.path.splitext(data['filename'])[0])
        processor.process_document(file_path, output_dir=output_dir)

        # Record correction
        success = processor.record_user_correction(
            data['field'], data['original_value'], data['corrected_value']
        )

        if success:
            return jsonify({"success": True, "message": f"Correction recorded for field: {data['field']}"})
        else:
            return jsonify({"error": "Failed to record correction"}), 500

    except Exception as e:
        logger.error(f"Error recording correction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/suggestions', methods=['POST'])
def generate_suggestions():
    """
    Generate improvement suggestions.

    Expects a JSON request with a 'filename' field.

    Returns:
        JSON response containing improvement suggestions
    """
    # Check if request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Get request data
    data = request.get_json()

    # Check if filename is provided
    if 'filename' not in data:
        return jsonify({"error": "Missing filename"}), 400

    try:
        # Get file path
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(data['filename']))

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Process document
        output_dir = os.path.join(RESULTS_FOLDER, os.path.splitext(data['filename'])[0])
        processor.process_document(file_path, output_dir=output_dir)

        # Generate improvement suggestions
        suggestions = processor.generate_improvement_suggestions()

        return jsonify({"success": True, "suggestions": suggestions})

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results/<path:filename>')
def download_file(filename):
    """
    Download a result file.

    Args:
        filename: Path to the file relative to the results folder

    Returns:
        File download response
    """
    directory = os.path.dirname(os.path.join(RESULTS_FOLDER, filename))
    file = os.path.basename(filename)
    return send_from_directory(directory, file)

def main():
    """Main function."""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))

    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Create index.html template
    with open('templates/index.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>AI Enhanced Financial Document Processor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
        }
        h2 {
            color: #3498db;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .btn {
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .correction-form {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .hidden {
            display: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        .loading {
            text-align: center;
            margin-top: 20px;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Enhanced Financial Document Processor</h1>

        <div class="form-group">
            <h2>Upload Financial Document</h2>
            <form id="upload-form" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Select PDF file:</label>
                    <input type="file" id="file" name="file" accept=".pdf" required>
                </div>
                <button type="submit" class="btn">Process Document</button>
            </form>
        </div>

        <div id="loading" class="loading hidden">
            <p>Processing document... This may take a few minutes.</p>
        </div>

        <div id="error" class="error hidden"></div>

        <div id="result" class="result hidden">
            <h2>Processing Results</h2>
            <div id="result-content"></div>

            <h3>Top Securities</h3>
            <table id="securities-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>ISIN</th>
                        <th>Description</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>

            <h3>AI Analysis</h3>
            <div id="ai-analysis"></div>

            <h3>AI Corrections</h3>
            <div id="ai-corrections"></div>

            <button id="suggestions-btn" class="btn">Generate Improvement Suggestions</button>

            <div id="suggestions" class="hidden">
                <h3>Improvement Suggestions</h3>
                <ul id="suggestions-list"></ul>
            </div>
        </div>

        <div id="correction-form" class="correction-form hidden">
            <h2>Record Correction</h2>
            <form id="correction-submit-form">
                <div class="form-group">
                    <label for="field">Field:</label>
                    <input type="text" id="field" name="field" required>
                </div>
                <div class="form-group">
                    <label for="original-value">Original Value:</label>
                    <input type="text" id="original-value" name="original-value" required>
                </div>
                <div class="form-group">
                    <label for="corrected-value">Corrected Value:</label>
                    <input type="text" id="corrected-value" name="corrected-value" required>
                </div>
                <button type="submit" class="btn">Submit Correction</button>
            </form>
            <div id="correction-result" class="hidden"></div>
        </div>
    </div>

    <script>
        // Global variable to store the current filename
        let currentFilename = '';

        // Handle form submission
        document.getElementById('upload-form').addEventListener('submit', function(e) {
            e.preventDefault();

            // Show loading indicator
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('result').classList.add('hidden');
            document.getElementById('error').classList.add('hidden');
            document.getElementById('correction-form').classList.add('hidden');

            // Get form data
            const formData = new FormData();
            const fileInput = document.getElementById('file');
            formData.append('file', fileInput.files[0]);

            // Store filename
            currentFilename = fileInput.files[0].name;

            // Send request
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                document.getElementById('loading').classList.add('hidden');

                if (data.error) {
                    // Show error
                    const errorElement = document.getElementById('error');
                    errorElement.textContent = data.error;
                    errorElement.classList.remove('hidden');
                } else {
                    // Show result
                    document.getElementById('result').classList.remove('hidden');
                    document.getElementById('correction-form').classList.remove('hidden');

                    // Populate result content
                    const resultContent = document.getElementById('result-content');
                    resultContent.innerHTML = `
                        <p><strong>Portfolio Value:</strong> $${data.portfolio_value ? data.portfolio_value.toLocaleString() : 'Not found'}</p>
                        <p><strong>Securities Count:</strong> ${data.securities_count}</p>
                        <p><strong>Asset Allocation Count:</strong> ${data.asset_allocation_count}</p>
                        <p><strong>Structured Products Count:</strong> ${data.structured_products_count}</p>
                    `;

                    // Populate securities table
                    const securitiesTable = document.getElementById('securities-table').getElementsByTagName('tbody')[0];
                    securitiesTable.innerHTML = '';

                    if (data.top_securities && data.top_securities.length > 0) {
                        data.top_securities.forEach((security, index) => {
                            const row = securitiesTable.insertRow();
                            row.insertCell(0).textContent = index + 1;
                            row.insertCell(1).textContent = security.isin || '';
                            row.insertCell(2).textContent = security.description || '';
                            row.insertCell(3).textContent = security.valuation ? `$${security.valuation.toLocaleString()}` : '';
                        });
                    } else {
                        const row = securitiesTable.insertRow();
                        const cell = row.insertCell(0);
                        cell.colSpan = 4;
                        cell.textContent = 'No securities found';
                    }

                    // Populate AI analysis
                    const aiAnalysis = document.getElementById('ai-analysis');
                    if (data.ai_analysis) {
                        aiAnalysis.innerHTML = `<pre>${data.ai_analysis}</pre>`;
                    } else {
                        aiAnalysis.innerHTML = '<p>No AI analysis available</p>';
                    }

                    // Populate AI corrections
                    const aiCorrections = document.getElementById('ai-corrections');
                    if (data.ai_corrections && Object.keys(data.ai_corrections).length > 0) {
                        let correctionsHtml = '<ul>';
                        for (const [field, correction] of Object.entries(data.ai_corrections)) {
                            correctionsHtml += `<li><strong>${field}:</strong> ${correction}</li>`;
                        }
                        correctionsHtml += '</ul>';
                        aiCorrections.innerHTML = correctionsHtml;
                    } else {
                        aiCorrections.innerHTML = '<p>No AI corrections available</p>';
                    }
                }
            })
            .catch(error => {
                // Hide loading indicator
                document.getElementById('loading').classList.add('hidden');

                // Show error
                const errorElement = document.getElementById('error');
                errorElement.textContent = 'Error processing document: ' + error.message;
                errorElement.classList.remove('hidden');
            });
        });

        // Handle correction form submission
        document.getElementById('correction-submit-form').addEventListener('submit', function(e) {
            e.preventDefault();

            // Get form data
            const field = document.getElementById('field').value;
            const originalValue = document.getElementById('original-value').value;
            const correctedValue = document.getElementById('corrected-value').value;

            // Send request
            fetch('/correct', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: currentFilename,
                    field: field,
                    original_value: originalValue,
                    corrected_value: correctedValue
                })
            })
            .then(response => response.json())
            .then(data => {
                // Show correction result
                const correctionResult = document.getElementById('correction-result');
                correctionResult.classList.remove('hidden');

                if (data.error) {
                    correctionResult.innerHTML = `<p class="error">${data.error}</p>`;
                } else {
                    correctionResult.innerHTML = `<p>${data.message}</p>`;

                    // Clear form
                    document.getElementById('field').value = '';
                    document.getElementById('original-value').value = '';
                    document.getElementById('corrected-value').value = '';
                }
            })
            .catch(error => {
                // Show error
                const correctionResult = document.getElementById('correction-result');
                correctionResult.classList.remove('hidden');
                correctionResult.innerHTML = `<p class="error">Error recording correction: ${error.message}</p>`;
            });
        });

        // Handle suggestions button click
        document.getElementById('suggestions-btn').addEventListener('click', function() {
            // Send request
            fetch('/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: currentFilename
                })
            })
            .then(response => response.json())
            .then(data => {
                // Show suggestions
                const suggestions = document.getElementById('suggestions');
                suggestions.classList.remove('hidden');

                const suggestionsList = document.getElementById('suggestions-list');
                suggestionsList.innerHTML = '';

                if (data.error) {
                    suggestionsList.innerHTML = `<li class="error">${data.error}</li>`;
                } else if (data.suggestions && data.suggestions.length > 0) {
                    data.suggestions.forEach(suggestion => {
                        const li = document.createElement('li');
                        li.textContent = suggestion;
                        suggestionsList.appendChild(li);
                    });
                } else {
                    suggestionsList.innerHTML = '<li>No suggestions available</li>';
                }
            })
            .catch(error => {
                // Show error
                const suggestions = document.getElementById('suggestions');
                suggestions.classList.remove('hidden');

                const suggestionsList = document.getElementById('suggestions-list');
                suggestionsList.innerHTML = `<li class="error">Error generating suggestions: ${error.message}</li>`;
            });
        });
    </script>
</body>
</html>
        """)

    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()
