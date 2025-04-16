# Financial Document Processor

A comprehensive solution for processing financial documents, extracting data, and enabling AI-powered querying and analysis.

## Features

- **Document Extraction**: Extract text, tables, and structured data from financial PDFs using multiple extraction methods
- **Database Storage**: Store extracted data in a structured PostgreSQL database
- **AI-Powered Querying**: Ask natural language questions about your financial documents
- **Table Generation**: Generate custom tables based on your financial data
- **Financial Analysis**: Get insights and recommendations based on your portfolio

## Architecture

The Financial Document Processor uses a stack of open-source tools:

1. **PDF Data Extraction**:
   - Unstructured: For general text and layout extraction
   - Camelot: For table extraction
   - pdfplumber: For additional text and table extraction

2. **Database**:
   - PostgreSQL: For structured storage of financial data

3. **AI and NLP**:
   - LlamaIndex: For document indexing and retrieval
   - LangChain: For building AI agents
   - OpenAI/Google AI: For natural language processing

4. **API and Web**:
   - FastAPI: For the REST API
   - Uvicorn: For the ASGI server

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Poppler (for PDF processing)
- Tesseract OCR (for text recognition)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/financial-document-processor.git
   cd financial-document-processor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Create the database:
   ```bash
   # Create a PostgreSQL database
   # Update the DATABASE_URL in .env
   ```

## Usage

### Command Line Interface

The Financial Document Processor provides a command-line interface for various operations:

#### Process a Document

```bash
python -m financial_document_processor.main process path/to/document.pdf --output-dir results --document-type portfolio_report
```

#### Index a Document

```bash
python -m financial_document_processor.main index 1 --persist-dir index
```

#### Query a Document

```bash
python -m financial_document_processor.main query "What is the total portfolio value?" --document-id 1
```

#### Generate a Table

```bash
python -m financial_document_processor.main table "Create a table of top 10 holdings by value" 1 --format markdown
```

#### Analyze a Document

```bash
python -m financial_document_processor.main analyze "Analyze the asset allocation and provide recommendations" 1
```

### API Server

Start the API server:

```bash
python -m financial_document_processor.main api --host 0.0.0.0 --port 8000
```

The API documentation will be available at http://localhost:8000/docs

## API Endpoints

- `POST /api/documents`: Create a new document
- `GET /api/documents`: Get all documents
- `GET /api/documents/{document_id}`: Get a document by ID
- `GET /api/documents/{document_id}/securities`: Get securities for a document
- `GET /api/documents/{document_id}/portfolio-value`: Get portfolio value for a document
- `GET /api/documents/{document_id}/asset-allocations`: Get asset allocations for a document
- `POST /api/process`: Process a document
- `POST /api/process/{document_id}`: Process an existing document
- `POST /api/query`: Query a document
- `POST /api/generate-table`: Generate a table
- `POST /api/analyze`: Analyze a document

## Docker Deployment

Build and run the Docker container:

```bash
docker build -t financial-document-processor .
docker run -p 8080:8080 --env-file .env financial-document-processor
```

## Google Cloud Deployment

Deploy to Google Cloud Run:

```bash
gcloud builds submit --tag gcr.io/your-project-id/financial-document-processor
gcloud run deploy financial-document-processor --image gcr.io/your-project-id/financial-document-processor --platform managed
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
