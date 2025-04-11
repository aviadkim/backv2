import os
import json
import logging
import psycopg2
import numpy as np
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", 5432),
    "dbname": os.environ.get("DB_NAME", "ai"),
    "user": os.environ.get("DB_USER", "ai"),
    "password": os.environ.get("DB_PASSWORD", "ai")
}

# Financial tables schema
FINANCIAL_TABLES = [
    {
        "name": "portfolios",
        "columns": [
            {"name": "id", "type": "VARCHAR(50) PRIMARY KEY"},
            {"name": "name", "type": "VARCHAR(255) NOT NULL"},
            {"name": "user_id", "type": "VARCHAR(50) NOT NULL"},
            {"name": "organization_id", "type": "VARCHAR(50)"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
            {"name": "updated_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    {
        "name": "holdings",
        "columns": [
            {"name": "id", "type": "VARCHAR(50) PRIMARY KEY"},
            {"name": "portfolio_id", "type": "VARCHAR(50) NOT NULL REFERENCES portfolios(id)"},
            {"name": "isin", "type": "VARCHAR(12) NOT NULL"},
            {"name": "name", "type": "VARCHAR(255) NOT NULL"},
            {"name": "quantity", "type": "NUMERIC NOT NULL"},
            {"name": "price", "type": "NUMERIC NOT NULL"},
            {"name": "value", "type": "NUMERIC NOT NULL"},
            {"name": "currency", "type": "VARCHAR(3) NOT NULL"},
            {"name": "asset_class", "type": "VARCHAR(50)"},
            {"name": "sector", "type": "VARCHAR(50)"},
            {"name": "region", "type": "VARCHAR(50)"},
            {"name": "cost_basis", "type": "NUMERIC"},
            {"name": "purchase_date", "type": "DATE"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
            {"name": "updated_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    {
        "name": "performance_metrics",
        "columns": [
            {"name": "id", "type": "VARCHAR(50) PRIMARY KEY"},
            {"name": "portfolio_id", "type": "VARCHAR(50) NOT NULL REFERENCES portfolios(id)"},
            {"name": "date", "type": "DATE NOT NULL"},
            {"name": "value", "type": "NUMERIC NOT NULL"},
            {"name": "daily_return", "type": "NUMERIC"},
            {"name": "cumulative_return", "type": "NUMERIC"},
            {"name": "volatility", "type": "NUMERIC"},
            {"name": "sharpe_ratio", "type": "NUMERIC"},
            {"name": "max_drawdown", "type": "NUMERIC"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    {
        "name": "documents",
        "columns": [
            {"name": "id", "type": "VARCHAR(50) PRIMARY KEY"},
            {"name": "title", "type": "VARCHAR(255) NOT NULL"},
            {"name": "file_path", "type": "VARCHAR(255) NOT NULL"},
            {"name": "file_name", "type": "VARCHAR(255) NOT NULL"},
            {"name": "file_type", "type": "VARCHAR(50) NOT NULL"},
            {"name": "file_size", "type": "INTEGER NOT NULL"},
            {"name": "content", "type": "TEXT"},
            {"name": "metadata", "type": "JSONB"},
            {"name": "tags", "type": "VARCHAR(50)[]"},
            {"name": "organization_id", "type": "VARCHAR(50)"},
            {"name": "created_by", "type": "VARCHAR(50) NOT NULL"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
            {"name": "updated_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
        ]
    },
    {
        "name": "financial_data",
        "columns": [
            {"name": "id", "type": "VARCHAR(50) PRIMARY KEY"},
            {"name": "document_id", "type": "VARCHAR(50) REFERENCES documents(id)"},
            {"name": "isin", "type": "VARCHAR(12)"},
            {"name": "data_type", "type": "VARCHAR(50) NOT NULL"},
            {"name": "date", "type": "DATE"},
            {"name": "value", "type": "NUMERIC"},
            {"name": "currency", "type": "VARCHAR(3)"},
            {"name": "source", "type": "VARCHAR(255)"},
            {"name": "metadata", "type": "JSONB"},
            {"name": "created_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
        ]
    }
]

# Sample data for knowledge base
SAMPLE_QUERIES = [
    {
        "type": "sample_query",
        "content": """
Question: What is the total value of all portfolios?
Reasoning: To find the total value of all portfolios, I need to sum the value of all holdings. The holdings table contains the value of each holding, so I can use the SUM function to calculate the total.
```sql
SELECT SUM(value) AS total_portfolio_value
FROM holdings;
```
This query calculates the sum of the 'value' column from the holdings table, giving us the total value of all portfolios.
""",
        "metadata": {"category": "portfolio_analysis"}
    },
    {
        "type": "sample_query",
        "content": """
Question: What is the asset allocation of portfolio 'portfolio-1'?
Reasoning: To find the asset allocation, I need to group the holdings by asset class and calculate the sum and percentage of each group. I'll need to join the portfolios and holdings tables.
```sql
SELECT 
    h.asset_class,
    SUM(h.value) AS total_value,
    (SUM(h.value) / (SELECT SUM(value) FROM holdings WHERE portfolio_id = 'portfolio-1')) * 100 AS percentage
FROM 
    holdings h
JOIN 
    portfolios p ON h.portfolio_id = p.id
WHERE 
    p.id = 'portfolio-1'
GROUP BY 
    h.asset_class
ORDER BY 
    total_value DESC;
```
This query groups holdings by asset class, calculates the total value for each class, and computes the percentage of the portfolio that each asset class represents.
""",
        "metadata": {"category": "asset_allocation"}
    },
    {
        "type": "sample_query",
        "content": """
Question: What are the top 5 performing holdings in terms of return on investment?
Reasoning: To calculate return on investment, I need to compare the current value with the cost basis. I'll use (current_value - cost_basis) / cost_basis to calculate the ROI.
```sql
SELECT 
    name,
    isin,
    asset_class,
    price,
    cost_basis,
    ((price - cost_basis) / cost_basis) * 100 AS roi_percentage
FROM 
    holdings
WHERE 
    cost_basis IS NOT NULL AND cost_basis > 0
ORDER BY 
    roi_percentage DESC
LIMIT 5;
```
This query calculates the return on investment for each holding and returns the top 5 performers.
""",
        "metadata": {"category": "performance_analysis"}
    },
    {
        "type": "sample_query",
        "content": """
Question: How has the portfolio value changed over the last 30 days?
Reasoning: To track the portfolio value over time, I need to use the performance_metrics table which stores historical values.
```sql
SELECT 
    date,
    value,
    daily_return,
    cumulative_return
FROM 
    performance_metrics
WHERE 
    portfolio_id = 'portfolio-1'
    AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY 
    date;
```
This query retrieves the daily portfolio value, daily return, and cumulative return for the last 30 days.
""",
        "metadata": {"category": "performance_tracking"}
    },
    {
        "type": "sample_query",
        "content": """
Question: What documents contain information about Apple Inc.?
Reasoning: To find documents related to Apple Inc., I need to search the documents table and possibly join with the financial_data table to find documents that reference Apple's ISIN.
```sql
SELECT DISTINCT
    d.id,
    d.title,
    d.file_type,
    d.created_at
FROM 
    documents d
LEFT JOIN 
    financial_data fd ON d.id = fd.document_id
WHERE 
    d.title ILIKE '%Apple%'
    OR d.content ILIKE '%Apple%'
    OR fd.isin = 'US0378331005' -- Apple's ISIN
ORDER BY 
    d.created_at DESC;
```
This query searches for documents that mention "Apple" in their title or content, or are linked to Apple's ISIN in the financial_data table.
""",
        "metadata": {"category": "document_search"}
    }
]

RULES = [
    {
        "type": "rule",
        "content": "Always use ISO currency codes (USD, EUR, GBP, etc.) when displaying currency values.",
        "metadata": {"category": "formatting"}
    },
    {
        "type": "rule",
        "content": "Format percentage values with two decimal places and include the % symbol.",
        "metadata": {"category": "formatting"}
    },
    {
        "type": "rule",
        "content": "When calculating portfolio returns, use time-weighted return methodology to account for cash flows.",
        "metadata": {"category": "calculation"}
    },
    {
        "type": "rule",
        "content": "For risk metrics, calculate volatility as the standard deviation of daily returns annualized by multiplying by the square root of 252 (trading days).",
        "metadata": {"category": "calculation"}
    },
    {
        "type": "rule",
        "content": "The Sharpe ratio should be calculated as (portfolio return - risk-free rate) / portfolio volatility.",
        "metadata": {"category": "calculation"}
    }
]

TABLE_METADATA = [
    {
        "type": "table_metadata",
        "content": json.dumps(FINANCIAL_TABLES[0]),
        "metadata": {"table_name": "portfolios"}
    },
    {
        "type": "table_metadata",
        "content": json.dumps(FINANCIAL_TABLES[1]),
        "metadata": {"table_name": "holdings"}
    },
    {
        "type": "table_metadata",
        "content": json.dumps(FINANCIAL_TABLES[2]),
        "metadata": {"table_name": "performance_metrics"}
    },
    {
        "type": "table_metadata",
        "content": json.dumps(FINANCIAL_TABLES[3]),
        "metadata": {"table_name": "documents"}
    },
    {
        "type": "table_metadata",
        "content": json.dumps(FINANCIAL_TABLES[4]),
        "metadata": {"table_name": "financial_data"}
    }
]

def get_random_embedding():
    """Generate a random embedding vector for demo purposes."""
    return np.random.rand(1536).tolist()

def setup_database():
    """Set up the database schema and load initial data."""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Register pgvector extension
        register_vector(conn)
        
        # Create pgvector extension if it doesn't exist
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create financial tables
        for table in FINANCIAL_TABLES:
            columns = ", ".join([f"{col['name']} {col['type']}" for col in table["columns"]])
            cursor.execute(f"DROP TABLE IF EXISTS {table['name']} CASCADE;")
            cursor.execute(f"CREATE TABLE {table['name']} ({columns});")
            logger.info(f"Created table: {table['name']}")
        
        # Create knowledge base table
        cursor.execute("""
        DROP TABLE IF EXISTS knowledge_base;
        CREATE TABLE knowledge_base (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB,
            embedding vector(1536)
        );
        """)
        logger.info("Created knowledge_base table")
        
        # Create index on embedding
        cursor.execute("""
        CREATE INDEX ON knowledge_base USING hnsw (embedding vector_l2_ops);
        """)
        logger.info("Created index on knowledge_base.embedding")
        
        # Load knowledge base data
        knowledge_base_data = []
        
        # Add sample queries
        for query in SAMPLE_QUERIES:
            knowledge_base_data.append((
                query["type"],
                query["content"],
                json.dumps(query["metadata"]),
                get_random_embedding()
            ))
        
        # Add rules
        for rule in RULES:
            knowledge_base_data.append((
                rule["type"],
                rule["content"],
                json.dumps(rule["metadata"]),
                get_random_embedding()
            ))
        
        # Add table metadata
        for metadata in TABLE_METADATA:
            knowledge_base_data.append((
                metadata["type"],
                metadata["content"],
                json.dumps(metadata["metadata"]),
                get_random_embedding()
            ))
        
        # Insert knowledge base data
        execute_values(
            cursor,
            "INSERT INTO knowledge_base (type, content, metadata, embedding) VALUES %s",
            knowledge_base_data
        )
        logger.info(f"Inserted {len(knowledge_base_data)} rows into knowledge_base")
        
        # Load sample portfolio data
        sample_portfolio = {
            "id": "portfolio-1",
            "name": "Sample Investment Portfolio",
            "user_id": "user-1",
            "organization_id": "org-1"
        }
        
        cursor.execute(
            "INSERT INTO portfolios (id, name, user_id, organization_id) VALUES (%s, %s, %s, %s)",
            (sample_portfolio["id"], sample_portfolio["name"], sample_portfolio["user_id"], sample_portfolio["organization_id"])
        )
        
        # Sample holdings
        holdings = [
            {
                "id": "holding-1",
                "portfolio_id": "portfolio-1",
                "isin": "US0378331005",
                "name": "Apple Inc.",
                "quantity": 100,
                "price": 176.35,
                "value": 17635.00,
                "currency": "USD",
                "asset_class": "Equity",
                "sector": "Technology",
                "region": "North America",
                "cost_basis": 150.25,
                "purchase_date": "2022-01-15"
            },
            {
                "id": "holding-2",
                "portfolio_id": "portfolio-1",
                "isin": "US5949181045",
                "name": "Microsoft Corporation",
                "quantity": 50,
                "price": 412.27,
                "value": 20613.50,
                "currency": "USD",
                "asset_class": "Equity",
                "sector": "Technology",
                "region": "North America",
                "cost_basis": 320.15,
                "purchase_date": "2022-02-10"
            },
            {
                "id": "holding-3",
                "portfolio_id": "portfolio-1",
                "isin": "US88160R1014",
                "name": "Tesla Inc.",
                "quantity": 25,
                "price": 175.34,
                "value": 4383.50,
                "currency": "USD",
                "asset_class": "Equity",
                "sector": "Automotive",
                "region": "North America",
                "cost_basis": 200.50,
                "purchase_date": "2022-03-05"
            },
            {
                "id": "holding-4",
                "portfolio_id": "portfolio-1",
                "isin": "US0231351067",
                "name": "Amazon.com Inc.",
                "quantity": 10,
                "price": 1528.08,
                "value": 15280.80,
                "currency": "USD",
                "asset_class": "Equity",
                "sector": "Consumer Discretionary",
                "region": "North America",
                "cost_basis": 1200.75,
                "purchase_date": "2022-01-20"
            },
            {
                "id": "holding-5",
                "portfolio_id": "portfolio-1",
                "isin": "US02079K1079",
                "name": "Alphabet Inc.",
                "quantity": 8,
                "price": 1556.29,
                "value": 12450.32,
                "currency": "USD",
                "asset_class": "Equity",
                "sector": "Communication Services",
                "region": "North America",
                "cost_basis": 1300.00,
                "purchase_date": "2022-02-15"
            },
            {
                "id": "holding-6",
                "portfolio_id": "portfolio-1",
                "isin": "US4642872422",
                "name": "iShares MSCI EAFE ETF",
                "quantity": 100,
                "price": 75.25,
                "value": 7525.00,
                "currency": "USD",
                "asset_class": "ETF",
                "sector": "International",
                "region": "Europe",
                "cost_basis": 70.50,
                "purchase_date": "2022-03-10"
            },
            {
                "id": "holding-7",
                "portfolio_id": "portfolio-1",
                "isin": "US9128282D10",
                "name": "US Treasury Bond 2.5% 2024",
                "quantity": 10000,
                "price": 0.985,
                "value": 9850.00,
                "currency": "USD",
                "asset_class": "Fixed Income",
                "sector": "Government",
                "region": "North America",
                "cost_basis": 1.00,
                "purchase_date": "2022-01-05"
            },
            {
                "id": "holding-8",
                "portfolio_id": "portfolio-1",
                "isin": "US912810TW33",
                "name": "US Treasury Bond 3.0% 2049",
                "quantity": 5000,
                "price": 0.92,
                "value": 4600.00,
                "currency": "USD",
                "asset_class": "Fixed Income",
                "sector": "Government",
                "region": "North America",
                "cost_basis": 0.98,
                "purchase_date": "2022-02-15"
            }
        ]
        
        # Insert holdings
        for holding in holdings:
            cursor.execute("""
                INSERT INTO holdings (
                    id, portfolio_id, isin, name, quantity, price, value, currency, 
                    asset_class, sector, region, cost_basis, purchase_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                holding["id"], holding["portfolio_id"], holding["isin"], holding["name"],
                holding["quantity"], holding["price"], holding["value"], holding["currency"],
                holding["asset_class"], holding["sector"], holding["region"],
                holding["cost_basis"], holding["purchase_date"]
            ))
        
        logger.info(f"Inserted {len(holdings)} holdings")
        
        # Generate performance metrics for the last 30 days
        from datetime import datetime, timedelta
        
        performance_metrics = []
        start_value = 90000.00
        current_value = start_value
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            
            # Generate a random daily return between -1.5% and 2%
            daily_return = np.random.uniform(-0.015, 0.02)
            
            # Calculate new value
            current_value = current_value * (1 + daily_return)
            
            # Calculate cumulative return
            cumulative_return = (current_value / start_value) - 1
            
            # Calculate volatility (simplified)
            volatility = np.random.uniform(0.1, 0.15)
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = np.random.uniform(0.8, 1.5)
            
            # Calculate max drawdown (simplified)
            max_drawdown = np.random.uniform(0.05, 0.15)
            
            performance_metrics.append({
                "id": f"perf-{i+1}",
                "portfolio_id": "portfolio-1",
                "date": date,
                "value": current_value,
                "daily_return": daily_return,
                "cumulative_return": cumulative_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown
            })
        
        # Insert performance metrics
        for metric in performance_metrics:
            cursor.execute("""
                INSERT INTO performance_metrics (
                    id, portfolio_id, date, value, daily_return, cumulative_return,
                    volatility, sharpe_ratio, max_drawdown
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                metric["id"], metric["portfolio_id"], metric["date"], metric["value"],
                metric["daily_return"], metric["cumulative_return"], metric["volatility"],
                metric["sharpe_ratio"], metric["max_drawdown"]
            ))
        
        logger.info(f"Inserted {len(performance_metrics)} performance metrics")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    setup_database()
