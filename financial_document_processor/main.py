"""
Main entry point for the Financial Document Processor.
"""
import os
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """Set up logging."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def process_document(args):
    """Process a document."""
    from financial_document_processor.database.db import Database
    from financial_document_processor.extractors.pdf_extractor import PDFExtractor
    from financial_document_processor.processor import DocumentProcessor
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create extractor
    extractor = PDFExtractor()
    
    # Create processor
    processor = DocumentProcessor(db, extractor)
    
    # Process document
    result = processor.process_document(
        args.pdf_path,
        output_dir=args.output_dir,
        document_type=args.document_type
    )
    
    print(f"Document processed: {result}")
    
    # Close database connection
    db.close()

def index_document(args):
    """Index a document."""
    from financial_document_processor.database.db import Database
    from financial_document_processor.agents.config import AIConfig
    from financial_document_processor.agents.document_index import DocumentIndex
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create AI config
    ai_config = AIConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        model_provider=os.environ.get("MODEL_PROVIDER", "openai"),
        model_name=os.environ.get("MODEL_NAME")
    )
    
    # Create document index
    document_index = DocumentIndex(db, ai_config, args.persist_dir)
    
    # Index document
    result = document_index.index_document(args.document_id)
    
    print(f"Document indexed: {result}")
    
    # Close database connection
    db.close()

def query_document(args):
    """Query a document."""
    from financial_document_processor.database.db import Database
    from financial_document_processor.agents.config import AIConfig
    from financial_document_processor.agents.document_index import DocumentIndex
    from financial_document_processor.agents.financial_agents import FinancialQueryAgent
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create AI config
    ai_config = AIConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        model_provider=os.environ.get("MODEL_PROVIDER", "openai"),
        model_name=os.environ.get("MODEL_NAME")
    )
    
    # Create document index
    document_index = DocumentIndex(db, ai_config, args.persist_dir)
    
    # Create query agent
    query_agent = FinancialQueryAgent(db, ai_config, document_index)
    
    # Query document
    result = query_agent.query(args.query, args.document_id)
    
    print(f"Query: {args.query}")
    print(f"Response: {result['response']}")
    
    # Close database connection
    db.close()

def generate_table(args):
    """Generate a table."""
    from financial_document_processor.database.db import Database
    from financial_document_processor.agents.config import AIConfig
    from financial_document_processor.agents.document_index import DocumentIndex
    from financial_document_processor.agents.financial_agents import TableGenerationAgent
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create AI config
    ai_config = AIConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        model_provider=os.environ.get("MODEL_PROVIDER", "openai"),
        model_name=os.environ.get("MODEL_NAME")
    )
    
    # Create document index
    document_index = DocumentIndex(db, ai_config, args.persist_dir)
    
    # Create table agent
    table_agent = TableGenerationAgent(db, ai_config, document_index)
    
    # Generate table
    result = table_agent.generate_table(args.request, args.document_id, args.format)
    
    print(f"Request: {args.request}")
    print(f"Table: {result['table']}")
    
    # Close database connection
    db.close()

def analyze_document(args):
    """Analyze a document."""
    from financial_document_processor.database.db import Database
    from financial_document_processor.agents.config import AIConfig
    from financial_document_processor.agents.document_index import DocumentIndex
    from financial_document_processor.agents.financial_agents import FinancialAnalysisAgent
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create AI config
    ai_config = AIConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        model_provider=os.environ.get("MODEL_PROVIDER", "openai"),
        model_name=os.environ.get("MODEL_NAME")
    )
    
    # Create document index
    document_index = DocumentIndex(db, ai_config, args.persist_dir)
    
    # Create analysis agent
    analysis_agent = FinancialAnalysisAgent(db, ai_config, document_index)
    
    # Analyze document
    result = analysis_agent.analyze(args.request, args.document_id)
    
    print(f"Request: {args.request}")
    print(f"Analysis: {result['analysis']}")
    
    # Close database connection
    db.close()

def run_api(args):
    """Run the API server."""
    import uvicorn
    
    # Run API server
    uvicorn.run(
        "financial_document_processor.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

def main():
    """Main entry point."""
    # Set up logging
    setup_logging()
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Financial Document Processor")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Process document command
    process_parser = subparsers.add_parser("process", help="Process a document")
    process_parser.add_argument("pdf_path", help="Path to the PDF file")
    process_parser.add_argument("--output-dir", help="Directory to save extracted data")
    process_parser.add_argument("--document-type", help="Type of document")
    process_parser.set_defaults(func=process_document)
    
    # Index document command
    index_parser = subparsers.add_parser("index", help="Index a document")
    index_parser.add_argument("document_id", type=int, help="Document ID")
    index_parser.add_argument("--persist-dir", help="Directory to persist the index")
    index_parser.set_defaults(func=index_document)
    
    # Query document command
    query_parser = subparsers.add_parser("query", help="Query a document")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument("--document-id", type=int, help="Document ID")
    query_parser.add_argument("--persist-dir", help="Directory to persist the index")
    query_parser.set_defaults(func=query_document)
    
    # Generate table command
    table_parser = subparsers.add_parser("table", help="Generate a table")
    table_parser.add_argument("request", help="Table generation request")
    table_parser.add_argument("document_id", type=int, help="Document ID")
    table_parser.add_argument("--format", default="markdown", help="Output format (markdown, html, or csv)")
    table_parser.add_argument("--persist-dir", help="Directory to persist the index")
    table_parser.set_defaults(func=generate_table)
    
    # Analyze document command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a document")
    analyze_parser.add_argument("request", help="Analysis request")
    analyze_parser.add_argument("document_id", type=int, help="Document ID")
    analyze_parser.add_argument("--persist-dir", help="Directory to persist the index")
    analyze_parser.set_defaults(func=analyze_document)
    
    # Run API command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    api_parser.set_defaults(func=run_api)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
