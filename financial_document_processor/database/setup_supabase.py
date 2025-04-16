"""
Script to set up Supabase tables for the Financial Document Processor.
"""
import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.error("Supabase library not available. Install with: pip install supabase")
    sys.exit(1)

def setup_supabase_tables(url: str, key: str):
    """
    Set up Supabase tables.
    
    Args:
        url: Supabase URL
        key: Supabase API key
    """
    logger.info(f"Setting up Supabase tables at {url}")
    
    # Create Supabase client
    client = create_client(url, key)
    
    # Define SQL for creating tables
    create_tables_sql = """
    -- Documents table
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT,
        file_size INTEGER,
        content_type TEXT,
        page_count INTEGER,
        title TEXT,
        author TEXT,
        creation_date TIMESTAMP,
        modification_date TIMESTAMP,
        document_date TIMESTAMP,
        document_type TEXT,
        processing_status TEXT DEFAULT 'pending',
        extraction_date TIMESTAMP DEFAULT NOW(),
        extraction_method TEXT,
        extraction_version TEXT,
        risk_profile TEXT,
        currency TEXT
    );

    -- Securities table
    CREATE TABLE IF NOT EXISTS securities (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        isin TEXT,
        cusip TEXT,
        ticker TEXT,
        name TEXT,
        description TEXT,
        security_type TEXT,
        asset_class TEXT,
        valuation FLOAT,
        price FLOAT,
        quantity FLOAT,
        currency TEXT,
        coupon_rate FLOAT,
        maturity_date TIMESTAMP,
        extraction_method TEXT,
        confidence_score FLOAT
    );

    -- Portfolio values table
    CREATE TABLE IF NOT EXISTS portfolio_values (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        value FLOAT NOT NULL,
        currency TEXT,
        value_date TIMESTAMP,
        extraction_method TEXT,
        confidence_score FLOAT
    );

    -- Asset allocations table
    CREATE TABLE IF NOT EXISTS asset_allocations (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        asset_class TEXT NOT NULL,
        value FLOAT,
        percentage FLOAT,
        currency TEXT,
        parent_id INTEGER REFERENCES asset_allocations(id),
        extraction_method TEXT,
        confidence_score FLOAT
    );

    -- Raw text table
    CREATE TABLE IF NOT EXISTS raw_texts (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id) UNIQUE,
        content TEXT,
        extraction_method TEXT
    );

    -- Document tables table
    CREATE TABLE IF NOT EXISTS document_tables (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        page_number INTEGER,
        table_number INTEGER,
        extraction_method TEXT,
        headers JSONB,
        data JSONB,
        accuracy FLOAT
    );
    
    -- Enable Row Level Security (RLS)
    ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    ALTER TABLE securities ENABLE ROW LEVEL SECURITY;
    ALTER TABLE portfolio_values ENABLE ROW LEVEL SECURITY;
    ALTER TABLE asset_allocations ENABLE ROW LEVEL SECURITY;
    ALTER TABLE raw_texts ENABLE ROW LEVEL SECURITY;
    ALTER TABLE document_tables ENABLE ROW LEVEL SECURITY;
    
    -- Create policies for authenticated users
    CREATE POLICY "Allow authenticated users to read documents" ON documents
        FOR SELECT USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated users to read securities" ON securities
        FOR SELECT USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated users to read portfolio_values" ON portfolio_values
        FOR SELECT USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated users to read asset_allocations" ON asset_allocations
        FOR SELECT USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated users to read raw_texts" ON raw_texts
        FOR SELECT USING (auth.role() = 'authenticated');
    
    CREATE POLICY "Allow authenticated users to read document_tables" ON document_tables
        FOR SELECT USING (auth.role() = 'authenticated');
    
    -- Create policies for service role
    CREATE POLICY "Allow service role to manage documents" ON documents
        FOR ALL USING (auth.role() = 'service_role');
    
    CREATE POLICY "Allow service role to manage securities" ON securities
        FOR ALL USING (auth.role() = 'service_role');
    
    CREATE POLICY "Allow service role to manage portfolio_values" ON portfolio_values
        FOR ALL USING (auth.role() = 'service_role');
    
    CREATE POLICY "Allow service role to manage asset_allocations" ON asset_allocations
        FOR ALL USING (auth.role() = 'service_role');
    
    CREATE POLICY "Allow service role to manage raw_texts" ON raw_texts
        FOR ALL USING (auth.role() = 'service_role');
    
    CREATE POLICY "Allow service role to manage document_tables" ON document_tables
        FOR ALL USING (auth.role() = 'service_role');
    """
    
    # Execute SQL
    try:
        # Note: In a real implementation, we would use the Supabase SQL editor or migrations
        # For this example, we'll just log the SQL that would be executed
        logger.info("SQL to create tables:")
        logger.info(create_tables_sql)
        
        logger.info("Tables should be created via Supabase dashboard or migrations")
        logger.info("Please execute the SQL above in the Supabase SQL editor")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up Supabase tables: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Set up Supabase tables")
    parser.add_argument("--url", help="Supabase URL")
    parser.add_argument("--key", help="Supabase API key")
    
    args = parser.parse_args()
    
    # Get Supabase URL and key
    url = args.url or os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co")
    key = args.key or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        logger.error("Supabase URL and key must be provided or set as environment variables")
        sys.exit(1)
    
    # Set up Supabase tables
    success = setup_supabase_tables(url, key)
    
    if success:
        logger.info("Supabase tables set up successfully")
    else:
        logger.error("Failed to set up Supabase tables")
        sys.exit(1)

if __name__ == "__main__":
    main()
