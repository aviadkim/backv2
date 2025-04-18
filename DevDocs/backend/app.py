from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import re
import json
from datetime import datetime
import random
import uuid
from werkzeug.utils import secure_filename

# Import MCP routes
from mcp_routes import mcp_bp

# Import agents and processors
from agents import FinancialAgent
from agents.chat_agent import ChatAgent
from document_processor import DocumentProcessor
from financial_document_processor import FinancialDocumentProcessor
from portfolio_analyzer import PortfolioAnalyzer
from report_generator import PortfolioReportGenerator, FinancialStatementReportGenerator
from ai_analysis import FinancialAnalysisAgent

# Disable .env file loading to avoid UTF-8 decoding errors
os.environ["FLASK_SKIP_DOTENV"] = "1"

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Fix CORS issues by allowing all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Register the MCP blueprint
app.register_blueprint(mcp_bp)

# Initialize agents and processors
financial_agent = FinancialAgent(memory_path="memory/financial_agent.json")
chat_agent = ChatAgent(memory_path="memory/chat_agent.json")
document_processor = DocumentProcessor(upload_dir="uploads")

# Initialize financial processing components
financial_document_processor = FinancialDocumentProcessor(upload_dir="uploads")
portfolio_analyzer = PortfolioAnalyzer()
portfolio_report_generator = PortfolioReportGenerator(template_dir="report_templates")
financial_statement_report_generator = FinancialStatementReportGenerator(template_dir="report_templates")
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set. AI analysis features will be disabled.")
financial_analysis_agent = FinancialAnalysisAgent(api_key=openai_api_key)

# Create required directories if they don't exist
os.makedirs("memory", exist_ok=True)
os.makedirs("report_templates", exist_ok=True)

# TODO: Replace with database connection in production environment
# documents = [
#     {"id": 1, "title": "Q4 Financial Report 2024.pdf", "content": "Financial report content with ISINs: US0378331005, US5949181045", "tags": ["financial", "report"], "date": "2025-03-24", "pages": 12},
#     {"id": 2, "title": "Investment Portfolio Summary.pdf", "content": "Portfolio content with ISINs: US0378331005, US5949181045, US88160R1014", "tags": ["investment", "portfolio"], "date": "2025-03-22", "pages": 8},
#     {"id": 3, "title": "Bank Statement March 2025.pdf", "content": "Bank statement content", "tags": ["banking", "statement"], "date": "2025-03-20", "pages": 4}
# ]
document_id_counter = 1

# TODO: Replace with database connection in production environment
# portfolio_data = [
#     {"isin": "US0378331005", "name": "Apple Inc.", "quantity": 10, "price": 176.35, "value": 1763.50, "currency": "USD", "asset_class": "Equity", "sector": "Technology", "region": "North America"},
#     {"isin": "US5949181045", "name": "Microsoft Corporation", "quantity": 5, "price": 412.27, "value": 2061.35, "currency": "USD", "asset_class": "Equity", "sector": "Technology", "region": "North America"},
#     {"isin": "US88160R1014", "name": "Tesla Inc.", "quantity": 8, "price": 175.34, "value": 1402.72, "currency": "USD", "asset_class": "Equity", "sector": "Consumer Discretionary", "region": "North America"},
#     {"isin": "US0231351067", "name": "Amazon.com Inc.", "quantity": 3, "price": 178.75, "value": 536.25, "currency": "USD", "asset_class": "Equity", "sector": "Consumer Discretionary", "region": "North America"},
#     {"isin": "US30303M1027", "name": "Meta Platforms Inc.", "quantity": 4, "price": 485.58, "value": 1942.32, "currency": "USD", "asset_class": "Equity", "sector": "Communication Services", "region": "North America"},
#     {"isin": "US912810SP08", "name": "US Treasury Bond 1.375% 15/08/2050", "quantity": 10000, "price": 0.8734, "value": 8734.00, "currency": "USD", "asset_class": "Bond", "sector": "Government", "region": "North America"},
#     {"isin": "IE00B4L5Y983", "name": "iShares Core MSCI World UCITS ETF", "quantity": 50, "price": 85.64, "value": 4282.00, "currency": "USD", "asset_class": "ETF", "sector": "Diversified", "region": "Global"}
# ]

# Sample financial data
financial_data = {
    "isins": [
        {"isin": "US0378331005", "description": "Apple Inc.", "value": "$176.35", "document_id": 2},
        {"isin": "US5949181045", "description": "Microsoft Corporation", "value": "$412.27", "document_id": 2},
        {"isin": "US88160R1014", "description": "Tesla Inc.", "value": "$175.34", "document_id": 1}
    ],
    "portfolio_summary": {
        "total_value": "$20,722.14",
        "asset_allocation": {
            "Equity": "37%",
            "Bond": "42%",
            "ETF": "21%"
        },
        "currency_allocation": {
            "USD": "100%"
        }
    }
}

# Helper functions for financial analysis
def extract_isins(text):
    """Extract ISIN codes from text using regex"""
    # ISIN format: 2 letters followed by 10 characters (letters or numbers)
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
    return re.findall(isin_pattern, text)

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/documents", methods=["GET"])
def get_documents():
    return jsonify({"documents": documents})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/documents", methods=["POST"])
def add_document():
    global document_id_counter

    # Handle JSON document metadata
    if request.content_type and 'application/json' in request.content_type:
        data = request.json
        doc = {
            "id": document_id_counter,
            "title": data.get("title", "Untitled"),
            "content": data.get("content", ""),
            "tags": data.get("tags", []),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "pages": random.randint(1, 20),
            "file_path": None
        }
        documents.append(doc)
        document_id_counter += 1
        return jsonify(doc), 201

    return jsonify({"error": "Invalid content type"}), 400

@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    global document_id_counter

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Get document type from form or use file extension
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1].lower()
        doc_type = request.form.get('type', file_ext[1:].upper())  # Default to file extension

        # Get document title or use filename
        title = request.form.get('title', '')
        if not title:
            title = os.path.splitext(original_filename)[0]  # Use filename without extension

        # Get tags if provided
        tags = []
        if 'tags' in request.form:
            try:
                tags = json.loads(request.form['tags'])
            except:
                tags = [request.form['tags']]

        # If no tags provided, use file type as a tag
        if not tags:
            tags = [file_ext[1:].lower()]

        # Get processing options if provided
        processing_options = {}
        if 'processing_options' in request.form:
            try:
                processing_options = json.loads(request.form['processing_options'])
            except:
                pass

        try:
            # Generate a secure filename
            secure_name = secure_filename(original_filename)
            # Add unique identifier to prevent filename collisions
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{unique_id}_{secure_name}"

            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the document
            processing_result = document_processor.process_document(file_path, doc_type, processing_options)

            # Extract metadata from processing result
            pages = processing_result.get('pages', 0)
            if pages == 0 and 'tables' in processing_result:
                # For spreadsheets, count sheets as pages
                pages = len(processing_result.get('sheets', [])) or len(processing_result.get('tables', []))

            # Extract ISINs if available
            isins = processing_result.get('isins', [])

            # Create document record
            doc = {
                "id": document_id_counter,
                "title": title,
                "content": processing_result.get('text', f"Content of {original_filename}"),
                "tags": tags,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "pages": pages or random.randint(1, 20),  # Use processed pages or random if not available
                "file_path": file_path,
                "original_filename": original_filename,
                "file_size": os.path.getsize(file_path),
                "file_type": doc_type,
                "processing_result": processing_result
            }

            documents.append(doc)
            document_id_counter += 1

            # Add extracted ISINs to our financial data
            if isins:
                for isin in isins:
                    if not any(i["isin"] == isin for i in financial_data["isins"]):
                        financial_data["isins"].append({
                            "isin": isin,
                            "description": f"Security {isin}",
                            "value": f"${random.randint(50, 500)}.{random.randint(0, 99):02d}",
                            "document_id": doc["id"]
                        })

            return jsonify({
                "status": "success",
                "message": "File uploaded successfully",
                "document": doc
            }), 201

        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route("/api/documents/<int:document_id>", methods=["GET"])
def get_document(document_id):
    """Get a specific document by ID"""
    doc = next((d for d in documents if d["id"] == document_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"document": doc})

@app.route("/api/financial/isins", methods=["GET"])
def get_isins():
    """Get all ISINs extracted from documents"""
    return jsonify({"isins": financial_data["isins"]})

@app.route("/api/financial/document/<int:document_id>/isins", methods=["GET"])
def get_document_isins(document_id):
    """Get ISINs for a specific document"""
    doc = next((d for d in documents if d["id"] == document_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    # Extract ISINs from document content
    extracted_isins = extract_isins(doc["content"])

    # Match with our known financial data
    isins = [isin for isin in financial_data["isins"]
             if isin["isin"] in extracted_isins or isin["document_id"] == document_id]

    return jsonify({"document_id": document_id, "isins": isins})

@app.route("/api/financial/portfolio", methods=["GET"])
def get_portfolio_summary():
    """Get portfolio summary"""
    return jsonify(financial_data["portfolio_summary"])

@app.route("/api/financial/analyze", methods=["POST"])
def analyze_document():
    """Analyze a document for financial data"""
    data = request.json
    document_id = data.get("document_id")

    if not document_id:
        return jsonify({"error": "Document ID is required"}), 400

    doc = next((d for d in documents if d["id"] == document_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    # Extract ISINs from document content
    extracted_isins = extract_isins(doc["content"])

    # Generate analysis results
    analysis_result = {
        "document_id": document_id,
        "analysis_date": datetime.now().isoformat(),
        "isins_found": len(extracted_isins),
        "isins": extracted_isins,
        "summary": f"Found {len(extracted_isins)} ISIN codes in the document."
    }

    return jsonify({"status": "success", "analysis": analysis_result})

@app.route("/api/documents/download/<int:document_id>", methods=["GET"])
def download_document(document_id):
    """Download a document file"""
    doc = next((d for d in documents if d["id"] == document_id), None)
    if not doc or not doc.get("file_path"):
        return jsonify({"error": "Document not found or no file available"}), 404

    # Get the directory and filename from the file path
    directory = os.path.dirname(doc["file_path"])
    filename = os.path.basename(doc["file_path"])

    # Send the file
    return send_from_directory(
        directory,
        filename,
        as_attachment=True,
        download_name=doc.get("original_filename", filename)
    )

# Agent API endpoints
@app.route("/api/agents/financial/analyze", methods=["POST"])
def agent_financial_analyze():
    """Analyze a document using the financial agent"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    document_id = data.get("document_id")
    if not document_id:
        return jsonify({"error": "No document_id provided"}), 400

    # Get the document
    doc = next((d for d in documents if d["id"] == document_id), None)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    # Create task for the agent
    task = {
        "type": "analyze_document",
        "document_id": document_id,
        "content": doc.get("content", "")
    }

    # Process the task
    result = financial_agent.process(task)

    return jsonify(result)

@app.route("/api/agents/financial/extract-isins", methods=["POST"])
def agent_extract_isins():
    """Extract ISINs from text using the financial agent"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    content = data.get("content")
    if not content:
        return jsonify({"error": "No content provided"}), 400

    # Create task for the agent
    task = {
        "type": "extract_isins",
        "content": content
    }

    # Process the task
    result = financial_agent.process(task)

    return jsonify(result)

@app.route("/api/agents/financial/risk-metrics", methods=["POST"])
def agent_risk_metrics():
    """Calculate risk metrics for a portfolio using the financial agent"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    portfolio = data.get("portfolio", portfolio_data)

    # Create task for the agent
    task = {
        "type": "calculate_risk_metrics",
        "portfolio": portfolio
    }

    # Process the task
    result = financial_agent.process(task)

    return jsonify(result)

@app.route("/api/agents/financial/analyze-portfolio", methods=["POST"])
def agent_analyze_portfolio():
    """Analyze a portfolio using the financial agent"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    portfolio = data.get("portfolio", portfolio_data)

    # Create task for the agent
    task = {
        "type": "analyze_portfolio",
        "portfolio": portfolio
    }

    # Process the task
    result = financial_agent.process(task)

    return jsonify(result)

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Get the portfolio data"""
    return jsonify({"portfolio": portfolio_data})

@app.route("/api/portfolio/summary", methods=["GET"])
def get_portfolio_analysis():
    """Get the portfolio analysis"""
    # Use the financial agent to analyze the portfolio
    task = {
        "type": "analyze_portfolio",
        "portfolio": portfolio_data
    }

    result = financial_agent.process(task)

    return jsonify(result)

@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Get all available agents"""
    agents = [
        {
            "id": 1,
            "name": "Document Analyzer",
            "description": "Analyzes documents for financial data and extracts key information",
            "status": "active",
            "capabilities": ["Document Analysis", "Information Extraction", "Summary Generation", "Key Data Identification"]
        },
        {
            "id": 2,
            "name": "ISIN Extractor",
            "description": "Identifies and extracts ISIN numbers from documents",
            "status": "active",
            "capabilities": ["ISIN Extraction", "Security Identification", "Validation", "Cross-referencing"]
        },
        {
            "id": 3,
            "name": "Portfolio Analyzer",
            "description": "Analyzes investment portfolios for performance and risk assessment",
            "status": "active",
            "capabilities": ["Risk Analysis", "Performance Metrics", "Asset Allocation", "Optimization"]
        },
        {
            "id": 4,
            "name": "Regulatory Compliance",
            "description": "Checks documents for regulatory compliance issues",
            "status": "active",
            "capabilities": ["Compliance Checking", "Regulation Tracking", "Issue Identification", "Recommendation Generation"]
        }
    ]

    return jsonify({"agents": agents})

@app.route("/api/agents/chat", methods=["POST"])
def agent_chat():
    """Chat with an agent"""
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Required fields
    agent_id = data.get("agent_id")
    message = data.get("message")

    if not agent_id:
        return jsonify({"error": "Agent ID is required"}), 400

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Optional fields
    document_id = data.get("document_id")

    # Process the chat request
    task = {
        "type": "chat",
        "agent_id": agent_id,
        "message": message,
        "document_id": document_id
    }

    result = chat_agent.process(task)

    return jsonify(result)

@app.route("/api/agents/config", methods=["POST"])
def configure_agent():
    """Configure an agent with API key"""
    # TODO: Add authentication to prevent unauthorized access
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    # Update the chat agent with the new API key
    chat_agent.api_key = api_key

    return jsonify({"status": "success", "message": "Agent configured successfully"})

# New financial processing endpoints
@app.route("/api/financial/process-document", methods=["POST"])
def process_financial_document():
    """Process a document with the financial document processor"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Generate a secure filename
            secure_name = secure_filename(file.filename)
            # Add unique identifier to prevent filename collisions
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{unique_id}_{secure_name}"

            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Get document type from form or use file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            doc_type = request.form.get('type', file_ext[1:].upper())  # Default to file extension

            # Get processing options if provided
            processing_options = {}
            if 'processing_options' in request.form:
                try:
                    processing_options = json.loads(request.form['processing_options'])
                except:
                    pass

            # Process the document with the financial document processor
            processing_result = financial_document_processor.process_document(file_path, doc_type, processing_options)

            return jsonify({
                "status": "success",
                "message": "File processed successfully",
                "result": processing_result
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route("/api/financial/analyze-portfolio", methods=["POST"])
def analyze_portfolio():
    """Analyze a portfolio with the portfolio analyzer"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    portfolio_data = data.get("portfolio")
    if not portfolio_data:
        return jsonify({"error": "No portfolio data provided"}), 400

    historical_data = data.get("historical_data")

    try:
        # Analyze the portfolio
        analysis_result = portfolio_analyzer.analyze_portfolio(portfolio_data, historical_data)

        return jsonify({
            "status": "success",
            "result": analysis_result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/api/financial/generate-report", methods=["POST"])
def generate_financial_report():
    """Generate a financial report"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    report_type = data.get("report_type")
    if not report_type:
        return jsonify({"error": "No report type provided"}), 400

    report_data = data.get("data")
    if not report_data:
        return jsonify({"error": "No report data provided"}), 400

    output_format = data.get("output_format", "json")

    try:
        # Generate the report based on type
        if report_type == "portfolio":
            report = portfolio_report_generator.generate_report(report_type, report_data, output_format)
        elif report_type in ["profit_loss", "balance_sheet", "cash_flow"]:
            report = financial_statement_report_generator.generate_report(report_type, report_data, output_format)
        else:
            return jsonify({"error": f"Unsupported report type: {report_type}"}), 400

        return jsonify({
            "status": "success",
            "report": report
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/api/financial/ai-analysis", methods=["POST"])
def ai_financial_analysis():
    """Analyze financial data with AI"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    analysis_type = data.get("analysis_type")
    if not analysis_type:
        return jsonify({"error": "No analysis type provided"}), 400

    try:
        result = {}

        if analysis_type == "document":
            document_text = data.get("document_text")
            document_type = data.get("document_type")
            if not document_text:
                return jsonify({"error": "No document text provided"}), 400
            result = financial_analysis_agent.analyze_financial_document(document_text, document_type)

        elif analysis_type == "portfolio":
            portfolio_data = data.get("portfolio_data")
            risk_profile = data.get("risk_profile", "moderate")
            if not portfolio_data:
                return jsonify({"error": "No portfolio data provided"}), 400
            result = financial_analysis_agent.generate_investment_recommendations(portfolio_data, risk_profile)

        elif analysis_type == "metrics":
            metrics = data.get("metrics")
            audience_level = data.get("audience_level", "professional")
            if not metrics:
                return jsonify({"error": "No metrics provided"}), 400
            result = financial_analysis_agent.explain_financial_metrics(metrics, audience_level)

        elif analysis_type == "trends":
            historical_data = data.get("historical_data")
            if not historical_data:
                return jsonify({"error": "No historical data provided"}), 400
            result = financial_analysis_agent.analyze_financial_trends(historical_data)

        else:
            return jsonify({"error": f"Unsupported analysis type: {analysis_type}"}), 400

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting FinDoc API on http://localhost:24125")
    # Use explicit parameters to prevent .env loading issues
    app.run(host="0.0.0.0", port=24125, load_dotenv=False)
