import os
import json
import logging
import re
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
import anthropic
from pgvector.psycopg2 import register_vector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLReasoningAgent:
    """
    SQL Reasoning Agent for financial data analysis.
    Uses Claude 3.7 Sonnet to generate and execute SQL queries based on natural language questions.
    """
    
    def __init__(self, db_config: Dict[str, str], model: str = "claude-3-7-sonnet-20240620"):
        """
        Initialize the SQL Reasoning Agent.
        
        Args:
            db_config: Database configuration (host, port, dbname, user, password)
            model: The model to use for reasoning
        """
        self.db_config = db_config
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.conn = None
        self.cursor = None
        self.knowledge_base = {}
        
        # Connect to the database
        self._connect_to_db()
        
        # Load knowledge base
        self._load_knowledge_base()
    
    def _connect_to_db(self):
        """Connect to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5432),
                dbname=self.db_config.get("dbname", "ai"),
                user=self.db_config.get("user", "ai"),
                password=self.db_config.get("password", "ai")
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            # Register pgvector extension
            register_vector(self.conn)
            
            logger.info("Connected to the database successfully")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise
    
    def _load_knowledge_base(self):
        """Load the knowledge base from the database."""
        try:
            # Load table metadata
            self.cursor.execute("""
                SELECT * FROM knowledge_base WHERE type = 'table_metadata'
            """)
            table_metadata = self.cursor.fetchall()
            
            # Load sample queries
            self.cursor.execute("""
                SELECT * FROM knowledge_base WHERE type = 'sample_query'
            """)
            sample_queries = self.cursor.fetchall()
            
            # Load rules
            self.cursor.execute("""
                SELECT * FROM knowledge_base WHERE type = 'rule'
            """)
            rules = self.cursor.fetchall()
            
            # Organize knowledge base
            self.knowledge_base = {
                "table_metadata": table_metadata,
                "sample_queries": sample_queries,
                "rules": rules
            }
            
            logger.info(f"Loaded knowledge base: {len(table_metadata)} tables, {len(sample_queries)} sample queries, {len(rules)} rules")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = {
                "table_metadata": [],
                "sample_queries": [],
                "rules": []
            }
    
    def _search_knowledge_base(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of relevant knowledge base entries
        """
        try:
            # Get embedding for the query
            embedding = self._get_embedding(query)
            
            # Search for relevant entries
            self.cursor.execute("""
                SELECT id, type, content, metadata,
                       embedding <=> %s AS distance
                FROM knowledge_base
                ORDER BY distance
                LIMIT %s
            """, (embedding, k))
            
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using Claude.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        # In a real implementation, this would use an embedding model
        # For this demo, we'll return a random vector
        return np.random.rand(1536).tolist()
    
    def _get_table_schema(self) -> str:
        """
        Get the database schema information.
        
        Returns:
            String representation of the database schema
        """
        try:
            # Get all tables
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name NOT IN ('knowledge_base', 'pg_stat_statements')
            """)
            tables = [record['table_name'] for record in self.cursor.fetchall()]
            
            schema_info = []
            
            # Get columns for each table
            for table in tables:
                self.cursor.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = self.cursor.fetchall()
                
                column_info = [f"{col['column_name']} {col['data_type']}" for col in columns]
                schema_info.append(f"Table: {table}\nColumns: {', '.join(column_info)}\n")
                
                # Get sample data
                self.cursor.execute(f"""
                    SELECT *
                    FROM {table}
                    LIMIT 3
                """)
                sample_data = self.cursor.fetchall()
                
                if sample_data:
                    schema_info.append("Sample data:")
                    for row in sample_data:
                        schema_info.append(str(dict(row)))
                
                schema_info.append("\n")
            
            return "\n".join(schema_info)
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return "Error retrieving schema information."
    
    def _extract_sql_query(self, text: str) -> str:
        """
        Extract SQL query from text.
        
        Args:
            text: Text containing SQL query
            
        Returns:
            Extracted SQL query
        """
        # Look for SQL query between ```sql and ``` markers
        sql_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(sql_pattern, text, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # If not found, look for any code block
        code_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_pattern, text, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # If still not found, return the original text
        return text
    
    def _execute_sql_query(self, query: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple of (results, error_message)
        """
        try:
            # Execute the query
            self.cursor.execute(query)
            
            # Fetch results
            results = self.cursor.fetchall()
            
            # Convert to list of dicts
            results_list = [dict(row) for row in results]
            
            return results_list, None
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return [], str(e)
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question and return the answer.
        
        Args:
            question: Natural language question about financial data
            
        Returns:
            Dictionary containing the answer, SQL query, and results
        """
        try:
            # Search knowledge base for relevant information
            relevant_info = self._search_knowledge_base(question)
            
            # Get database schema
            schema_info = self._get_table_schema()
            
            # Prepare few-shot examples from knowledge base
            few_shot_examples = []
            for info in relevant_info:
                if info['type'] == 'sample_query':
                    few_shot_examples.append(info['content'])
            
            # Prepare rules from knowledge base
            rules = []
            for info in relevant_info:
                if info['type'] == 'rule':
                    rules.append(info['content'])
            
            # Construct the prompt
            prompt = f"""You are a financial data analyst who helps users query a database of financial information.

DATABASE SCHEMA:
{schema_info}

RELEVANT RULES:
{' '.join(rules)}

SAMPLE QUERIES:
{' '.join(few_shot_examples)}

USER QUESTION:
{question}

Please follow these steps:
1. Analyze the user's question carefully
2. Think about which tables and columns are needed to answer the question
3. Write a SQL query that will answer the question
4. Explain your reasoning
5. Format your SQL query between ```sql and ``` markers

Your response should include:
- Your reasoning about how to approach the question
- The SQL query to execute
- An explanation of how the query answers the user's question
"""
            
            # Generate SQL query using Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0,
                system="You are a financial data analyst who helps users query a database of financial information. You write clear, efficient SQL queries to answer questions about financial data.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract SQL query from response
            sql_query = self._extract_sql_query(response.content[0].text)
            
            # Execute the query
            results, error = self._execute_sql_query(sql_query)
            
            # Generate explanation of results
            if error:
                explanation_prompt = f"""The SQL query you generated resulted in an error:

SQL Query:
```sql
{sql_query}
```

Error:
{error}

Please fix the SQL query and explain what went wrong.
"""
                explanation_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0,
                    system="You are a financial data analyst who helps users query a database of financial information. You write clear, efficient SQL queries to answer questions about financial data.",
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": response.content[0].text},
                        {"role": "user", "content": explanation_prompt}
                    ]
                )
                
                # Extract fixed SQL query
                fixed_sql_query = self._extract_sql_query(explanation_response.content[0].text)
                
                # Try executing the fixed query
                results, error = self._execute_sql_query(fixed_sql_query)
                
                if error:
                    return {
                        "question": question,
                        "sql_query": sql_query,
                        "fixed_sql_query": fixed_sql_query,
                        "error": error,
                        "results": [],
                        "explanation": explanation_response.content[0].text
                    }
                else:
                    sql_query = fixed_sql_query
            
            # Generate explanation of results
            if results:
                results_str = json.dumps(results[:10], indent=2)
                explanation_prompt = f"""The SQL query you generated returned the following results:

SQL Query:
```sql
{sql_query}
```

Results (first 10 rows):
{results_str}

Please explain these results in relation to the user's question: "{question}"
Provide insights and analysis based on the data.
"""
                explanation_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0,
                    system="You are a financial data analyst who helps users query a database of financial information. You provide clear, insightful analysis of financial data.",
                    messages=[
                        {"role": "user", "content": explanation_prompt}
                    ]
                )
                
                explanation = explanation_response.content[0].text
            else:
                explanation = "No results found for the query."
            
            return {
                "question": question,
                "sql_query": sql_query,
                "results": results,
                "explanation": explanation,
                "reasoning": response.content[0].text
            }
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "error": str(e),
                "results": [],
                "explanation": f"An error occurred while processing your question: {str(e)}"
            }
    
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
