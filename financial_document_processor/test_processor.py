"""
Test script for the Financial Document Processor.
"""
import os
import sys
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

def test_extraction(pdf_path, output_dir=None):
    """Test PDF extraction."""
    print(f"Testing PDF extraction on {pdf_path}...")
    
    from financial_document_processor.extractors.pdf_extractor import PDFExtractor
    
    # Create extractor
    extractor = PDFExtractor()
    
    # Extract content
    result = extractor.extract(pdf_path, output_dir)
    
    # Print results
    print(f"Extraction completed with {len(result.get('tables', []))} tables")
    print(f"Text length: {sum(len(text) for text in result.get('text', {}).values())}")
    
    # Extract securities
    securities = extractor.extract_securities(pdf_path)
    print(f"Extracted {len(securities)} securities")
    
    # Extract portfolio value
    portfolio_value = extractor.extract_portfolio_value(pdf_path)
    print(f"Portfolio value: {portfolio_value}")
    
    return result

def test_database():
    """Test database connection."""
    print("Testing database connection...")
    
    from financial_document_processor.database.db import Database
    
    # Create database connection
    db = Database(os.environ.get("DATABASE_URL"))
    
    # Create tables
    db.create_tables()
    
    # Close connection
    db.close()
    
    print("Database connection successful")

def test_document_processing(pdf_path, output_dir=None):
    """Test document processing."""
    print(f"Testing document processing on {pdf_path}...")
    
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
        pdf_path,
        output_dir=output_dir,
        document_type="test_document"
    )
    
    # Print results
    print(f"Document processed: {result}")
    
    # Close database connection
    db.close()
    
    return result

def test_document_indexing(document_id, persist_dir=None):
    """Test document indexing."""
    print(f"Testing document indexing for document ID {document_id}...")
    
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
    document_index = DocumentIndex(db, ai_config, persist_dir)
    
    # Index document
    result = document_index.index_document(document_id)
    
    # Print results
    print(f"Document indexed: {result}")
    
    # Close database connection
    db.close()
    
    return result

def test_document_querying(query, document_id=None, persist_dir=None):
    """Test document querying."""
    print(f"Testing document querying with query: {query}")
    
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
    document_index = DocumentIndex(db, ai_config, persist_dir)
    
    # Create query agent
    query_agent = FinancialQueryAgent(db, ai_config, document_index)
    
    # Query document
    result = query_agent.query(query, document_id)
    
    # Print results
    print(f"Query: {query}")
    print(f"Response: {result['response']}")
    
    # Close database connection
    db.close()
    
    return result

def test_table_generation(request, document_id, format="markdown", persist_dir=None):
    """Test table generation."""
    print(f"Testing table generation with request: {request}")
    
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
    document_index = DocumentIndex(db, ai_config, persist_dir)
    
    # Create table agent
    table_agent = TableGenerationAgent(db, ai_config, document_index)
    
    # Generate table
    result = table_agent.generate_table(request, document_id, format)
    
    # Print results
    print(f"Request: {request}")
    print(f"Table: {result['table']}")
    
    # Close database connection
    db.close()
    
    return result

def test_document_analysis(request, document_id, persist_dir=None):
    """Test document analysis."""
    print(f"Testing document analysis with request: {request}")
    
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
    document_index = DocumentIndex(db, ai_config, persist_dir)
    
    # Create analysis agent
    analysis_agent = FinancialAnalysisAgent(db, ai_config, document_index)
    
    # Analyze document
    result = analysis_agent.analyze(request, document_id)
    
    # Print results
    print(f"Request: {request}")
    print(f"Analysis: {result['analysis']}")
    
    # Close database connection
    db.close()
    
    return result

def main():
    """Main entry point."""
    # Set up logging
    setup_logging()
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Test Financial Document Processor")
    parser.add_argument("--pdf-path", help="Path to the PDF file")
    parser.add_argument("--output-dir", help="Directory to save extracted data")
    parser.add_argument("--document-id", type=int, help="Document ID")
    parser.add_argument("--persist-dir", help="Directory to persist the index")
    parser.add_argument("--test-extraction", action="store_true", help="Test PDF extraction")
    parser.add_argument("--test-database", action="store_true", help="Test database connection")
    parser.add_argument("--test-processing", action="store_true", help="Test document processing")
    parser.add_argument("--test-indexing", action="store_true", help="Test document indexing")
    parser.add_argument("--test-querying", action="store_true", help="Test document querying")
    parser.add_argument("--query", help="Query text")
    parser.add_argument("--test-table", action="store_true", help="Test table generation")
    parser.add_argument("--table-request", help="Table generation request")
    parser.add_argument("--format", default="markdown", help="Output format (markdown, html, or csv)")
    parser.add_argument("--test-analysis", action="store_true", help="Test document analysis")
    parser.add_argument("--analysis-request", help="Analysis request")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run tests
    if args.test_extraction:
        if not args.pdf_path:
            print("Error: --pdf-path is required for --test-extraction")
            sys.exit(1)
        test_extraction(args.pdf_path, args.output_dir)
    
    if args.test_database:
        test_database()
    
    if args.test_processing:
        if not args.pdf_path:
            print("Error: --pdf-path is required for --test-processing")
            sys.exit(1)
        test_document_processing(args.pdf_path, args.output_dir)
    
    if args.test_indexing:
        if not args.document_id:
            print("Error: --document-id is required for --test-indexing")
            sys.exit(1)
        test_document_indexing(args.document_id, args.persist_dir)
    
    if args.test_querying:
        if not args.query:
            print("Error: --query is required for --test-querying")
            sys.exit(1)
        test_document_querying(args.query, args.document_id, args.persist_dir)
    
    if args.test_table:
        if not args.table_request or not args.document_id:
            print("Error: --table-request and --document-id are required for --test-table")
            sys.exit(1)
        test_table_generation(args.table_request, args.document_id, args.format, args.persist_dir)
    
    if args.test_analysis:
        if not args.analysis_request or not args.document_id:
            print("Error: --analysis-request and --document-id are required for --test-analysis")
            sys.exit(1)
        test_document_analysis(args.analysis_request, args.document_id, args.persist_dir)
    
    # If no tests specified, print help
    if not any([
        args.test_extraction,
        args.test_database,
        args.test_processing,
        args.test_indexing,
        args.test_querying,
        args.test_table,
        args.test_analysis
    ]):
        parser.print_help()

if __name__ == "__main__":
    main()
