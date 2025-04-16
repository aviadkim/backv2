"""
Test script to verify the implementation of the Financial Document Processor.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_extraction():
    """Test PDF extraction."""
    logger.info("Testing PDF extraction...")
    
    try:
        import pdfplumber
        import camelot
        from unstructured.partition.pdf import partition_pdf
        
        logger.info("PDF extraction libraries imported successfully")
        return True
    except ImportError as e:
        logger.error(f"Error importing PDF extraction libraries: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection."""
    logger.info("Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co")
        key = os.environ.get("SUPABASE_KEY")
        
        if not key:
            logger.error("SUPABASE_KEY environment variable not set")
            return False
        
        client = create_client(url, key)
        response = client.table("documents").select("*").limit(1).execute()
        
        logger.info("Supabase connection successful")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
        return False

def test_openrouter_connection():
    """Test OpenRouter connection."""
    logger.info("Testing OpenRouter connection...")
    
    try:
        import openai
        
        api_key = os.environ.get("OPENROUTER_API_KEY", "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")
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        
        logger.info(f"OpenRouter response: {response.choices[0].message.content}")
        logger.info("OpenRouter connection successful")
        return True
    except Exception as e:
        logger.error(f"Error connecting to OpenRouter: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app."""
    logger.info("Testing FastAPI app...")
    
    try:
        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates
        
        # Import the app
        from financial_document_processor.web.app import app
        
        logger.info("FastAPI app imported successfully")
        return True
    except Exception as e:
        logger.error(f"Error importing FastAPI app: {e}")
        return False

def test_document_processor():
    """Test document processor."""
    logger.info("Testing document processor...")
    
    try:
        from financial_document_processor.extractors.pdf_extractor import PDFExtractor
        from financial_document_processor.database.supabase_db import SupabaseDB
        from financial_document_processor.processor import DocumentProcessor
        
        # Create extractor
        extractor = PDFExtractor()
        
        # Create database connection
        db = SupabaseDB(
            url=os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co"),
            key=os.environ.get("SUPABASE_KEY")
        )
        
        # Create processor
        processor = DocumentProcessor(db, extractor)
        
        logger.info("Document processor created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating document processor: {e}")
        return False

def test_openrouter_agent():
    """Test OpenRouter agent."""
    logger.info("Testing OpenRouter agent...")
    
    try:
        from financial_document_processor.agents.openrouter_agent import OpenRouterAgent
        
        # Create agent
        agent = OpenRouterAgent(
            api_key=os.environ.get("OPENROUTER_API_KEY", "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"),
            model=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
        )
        
        logger.info("OpenRouter agent created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating OpenRouter agent: {e}")
        return False

def main():
    """Main function."""
    logger.info("Testing Financial Document Processor implementation...")
    
    # Run tests
    tests = [
        ("PDF Extraction", test_pdf_extraction),
        ("Supabase Connection", test_supabase_connection),
        ("OpenRouter Connection", test_openrouter_connection),
        ("FastAPI App", test_fastapi_app),
        ("Document Processor", test_document_processor),
        ("OpenRouter Agent", test_openrouter_agent)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
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
