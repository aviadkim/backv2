import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from sql_reasoning_agent import SQLReasoningAgent

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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize SQL Reasoning Agent
sql_agent = SQLReasoningAgent(DB_CONFIG)

@app.route('/api/sql-agent/query', methods=['POST'])
def query():
    """
    Process a natural language question and return the answer.
    
    Request body:
    {
        "question": "What is the total value of all portfolios?"
    }
    
    Response:
    {
        "question": "What is the total value of all portfolios?",
        "sql_query": "SELECT SUM(value) AS total_portfolio_value FROM holdings;",
        "results": [{"total_portfolio_value": 92338.12}],
        "explanation": "The total value of all portfolios is $92,338.12...",
        "reasoning": "To find the total value of all portfolios, I need to sum the value of all holdings..."
    }
    """
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Process the question
        result = sql_agent.process_question(question)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql-agent/tables', methods=['GET'])
def get_tables():
    """
    Get the list of tables in the database.
    
    Response:
    {
        "tables": ["portfolios", "holdings", "performance_metrics", "documents", "financial_data"]
    }
    """
    try:
        # Connect to the database
        sql_agent._connect_to_db()
        
        # Get all tables
        sql_agent.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN ('knowledge_base', 'pg_stat_statements')
        """)
        tables = [record['table_name'] for record in sql_agent.cursor.fetchall()]
        
        return jsonify({"tables": tables})
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql-agent/schema', methods=['GET'])
def get_schema():
    """
    Get the database schema information.
    
    Response:
    {
        "schema": "Table: portfolios\nColumns: id VARCHAR(50), name VARCHAR(255), ...\n\nTable: holdings\n..."
    }
    """
    try:
        schema_info = sql_agent._get_table_schema()
        return jsonify({"schema": schema_info})
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql-agent/execute', methods=['POST'])
def execute_query():
    """
    Execute a SQL query directly.
    
    Request body:
    {
        "query": "SELECT * FROM portfolios LIMIT 10;"
    }
    
    Response:
    {
        "results": [{"id": "portfolio-1", "name": "Sample Investment Portfolio", ...}],
        "error": null
    }
    """
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Execute the query
        results, error = sql_agent._execute_sql_query(query)
        
        return jsonify({
            "results": results,
            "error": error
        })
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql-agent/knowledge', methods=['GET'])
def get_knowledge():
    """
    Get the knowledge base entries.
    
    Response:
    {
        "knowledge_base": {
            "table_metadata": [...],
            "sample_queries": [...],
            "rules": [...]
        }
    }
    """
    try:
        return jsonify({"knowledge_base": sql_agent.knowledge_base})
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql-agent/search', methods=['POST'])
def search_knowledge():
    """
    Search the knowledge base for relevant information.
    
    Request body:
    {
        "query": "asset allocation",
        "k": 5
    }
    
    Response:
    {
        "results": [...]
    }
    """
    try:
        data = request.json
        query = data.get('query')
        k = data.get('k', 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Search the knowledge base
        results = sql_agent._search_knowledge_base(query, k)
        
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return jsonify({"error": str(e)}), 500

@app.teardown_appcontext
def close_db_connection(error):
    """Close the database connection when the application context ends."""
    sql_agent.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
