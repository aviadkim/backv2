"""
SQL agent implementation for database queries.
"""
import logging
from typing import Dict, List, Any, Optional
import os
import aiohttp
import json
import re

from .base import Agent, AgentResponse, AgentFactory
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

@AgentFactory.register("sql")
class SQLAgent(Agent):
    """Agent that generates and executes SQL queries based on natural language questions."""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, description, config)
        self.api_key = config.get("api_key", os.environ.get("OPENROUTER_API_KEY", ""))
        self.model = config.get("model", "openai/gpt-4")  # Using GPT-4 for better SQL generation
        self.database_service = DatabaseService()
        self.execute_queries = config.get("execute_queries", True)
        self.max_rows = config.get("max_rows", 50)
        
        if not self.api_key:
            logger.warning("API key not provided. SQL agent will not function properly.")
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a natural language query and convert it to SQL."""
        if not self.api_key:
            return AgentResponse(
                content="Error: API key not configured. Please provide an API key.",
                metadata={"error": "api_key_missing"}
            )
        
        # Add user query to history
        self.add_to_history("user", query, context)
        
        # Get database schema
        db_schema = await self._get_database_schema()
        
        # Create system prompt with database schema
        system_prompt = self._create_system_prompt(db_schema)
        
        # Prepare messages for the API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limited to last 5 messages)
        for msg in self.conversation_history[-5:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            # First, generate the SQL query
            sql_query = await self._generate_sql_query(messages)
            
            if "error" in sql_query:
                return AgentResponse(
                    content=f"Error: {sql_query['error_message']}",
                    metadata={"error": sql_query["error"]}
                )
            
            # Execute the query if configured to do so
            if self.execute_queries:
                query_result = await self._execute_sql_query(sql_query["query"])
                
                if "error" in query_result:
                    return AgentResponse(
                        content=f"Error executing SQL query: {query_result['error_message']}\n\nGenerated SQL: ```sql\n{sql_query['query']}\n```",
                        metadata={
                            "error": query_result["error"],
                            "sql_query": sql_query["query"]
                        }
                    )
                
                # Generate a response that explains the query and results
                final_response = await self._generate_query_explanation(
                    original_query=query,
                    sql_query=sql_query["query"],
                    query_result=query_result["result"]
                )
                
                # Add assistant response to history
                self.add_to_history("assistant", final_response["content"])
                
                return AgentResponse(
                    content=final_response["content"],
                    metadata={
                        "sql_query": sql_query["query"],
                        "query_result": query_result["result"],
                        "row_count": len(query_result["result"]) if isinstance(query_result["result"], list) else 0
                    }
                )
            else:
                # Just return the generated SQL without executing
                response_content = f"Based on your question, here's the SQL query I would run:\n\n```sql\n{sql_query['query']}\n```\n\nThe query has not been executed as per configuration."
                
                # Add assistant response to history
                self.add_to_history("assistant", response_content)
                
                return AgentResponse(
                    content=response_content,
                    metadata={
                        "sql_query": sql_query["query"],
                        "executed": False
                    }
                )
        
        except Exception as e:
            logger.exception("Error processing SQL query")
            return AgentResponse(
                content=f"Error processing your database query: {str(e)}",
                metadata={"error": "exception", "message": str(e)}
            )
    
    async def _get_database_schema(self) -> Dict[str, Any]:
        """Get the database schema."""
        try:
            schema = await self.database_service.get_schema()
            return schema
        except Exception as e:
            logger.exception("Error getting database schema")
            return {
                "error": "Failed to retrieve database schema",
                "tables": []
            }
    
    def _create_system_prompt(self, db_schema: Dict[str, Any]) -> str:
        """Create a system prompt with database schema."""
        tables_info = ""
        
        for table in db_schema.get("tables", []):
            table_name = table.get("name", "unknown_table")
            columns = table.get("columns", [])
            
            columns_info = "\n".join([
                f"  - {col.get('name', 'unknown')} ({col.get('type', 'unknown')}): {col.get('description', 'No description')}"
                for col in columns
            ])
            
            tables_info += f"Table: {table_name}\nDescription: {table.get('description', 'No description')}\nColumns:\n{columns_info}\n\n"
        
        return f"""You are a SQL expert that helps users query a database by converting natural language questions into SQL queries.

Database Schema:
{tables_info}

Your task is to:
1. Analyze the user's question carefully
2. Generate a valid SQL query that answers their question
3. Format your response as follows:
   ```sql
   YOUR_SQL_QUERY_HERE
   ```

Important guidelines:
- Always use proper SQL syntax for the PostgreSQL dialect
- Use appropriate JOINs when querying across multiple tables
- Limit results to {self.max_rows} rows unless specified otherwise
- If you cannot generate a SQL query for the question, explain why
- Do not make assumptions about tables or columns that aren't in the schema
- Use appropriate aggregation functions (SUM, AVG, COUNT, etc.) when needed
- Format dates appropriately using PostgreSQL date functions
"""
    
    async def _generate_sql_query(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a SQL query using the AI model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://document-understanding-demo.com",
                        "X-Title": "Document Understanding Demo"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.2  # Lower temperature for more precise SQL generation
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {error_text}")
                        return {
                            "error": "api_error",
                            "error_message": f"Failed to generate SQL query. Status code: {response.status}"
                        }
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return {
                            "error": "empty_response",
                            "error_message": "No response received from the AI model."
                        }
                    
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract SQL query from the response
                    sql_match = re.search(r"```sql\s*(.*?)\s*```", content, re.DOTALL)
                    if not sql_match:
                        return {
                            "error": "no_sql_found",
                            "error_message": "Could not extract a valid SQL query from the AI response.",
                            "raw_response": content
                        }
                    
                    sql_query = sql_match.group(1).strip()
                    return {"query": sql_query}
        
        except Exception as e:
            logger.exception("Error generating SQL query")
            return {
                "error": "exception",
                "error_message": f"Error generating SQL query: {str(e)}"
            }
    
    async def _execute_sql_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute the SQL query."""
        try:
            result = await self.database_service.execute_query(sql_query, max_rows=self.max_rows)
            return {"result": result}
        except Exception as e:
            logger.exception(f"Error executing SQL query: {sql_query}")
            return {
                "error": "query_execution_error",
                "error_message": str(e)
            }
    
    async def _generate_query_explanation(self, original_query: str, sql_query: str, query_result: Any) -> Dict[str, str]:
        """Generate an explanation of the query and its results."""
        try:
            # Convert query result to a string representation
            if isinstance(query_result, list):
                if len(query_result) > 0:
                    # Format as a table for readability
                    if len(query_result) > 10:
                        result_str = f"The query returned {len(query_result)} rows. Here are the first 10 rows:\n\n"
                        result_sample = query_result[:10]
                    else:
                        result_str = f"The query returned {len(query_result)} rows:\n\n"
                        result_sample = query_result
                    
                    # Create a formatted table
                    if isinstance(result_sample[0], dict):
                        headers = list(result_sample[0].keys())
                        result_str += "| " + " | ".join(headers) + " |\n"
                        result_str += "| " + " | ".join(["---" for _ in headers]) + " |\n"
                        
                        for row in result_sample:
                            result_str += "| " + " | ".join([str(row.get(h, "")) for h in headers]) + " |\n"
                    else:
                        result_str += str(result_sample)
                else:
                    result_str = "The query returned no results."
            else:
                result_str = str(query_result)
            
            # Create a prompt for the explanation
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful SQL assistant. Your task is to explain SQL queries and their results in a clear, concise manner."
                },
                {
                    "role": "user",
                    "content": f"""I ran the following SQL query to answer the question: "{original_query}"

```sql
{sql_query}
```

The query returned the following results:

{result_str}

Please explain:
1. What the SQL query is doing (in simple terms)
2. How the results answer the original question
3. Any insights or observations from the data
"""
                }
            ]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://document-understanding-demo.com",
                        "X-Title": "Document Understanding Demo"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.5
                    }
                ) as response:
                    if response.status != 200:
                        # If explanation fails, return a basic response
                        return {
                            "content": f"I ran the following SQL query to answer your question:\n\n```sql\n{sql_query}\n```\n\nResults:\n\n{result_str}"
                        }
                    
                    data = await response.json()
                    
                    if not data.get("choices") or len(data["choices"]) == 0:
                        return {
                            "content": f"I ran the following SQL query to answer your question:\n\n```sql\n{sql_query}\n```\n\nResults:\n\n{result_str}"
                        }
                    
                    explanation = data["choices"][0]["message"]["content"]
                    return {"content": explanation}
        
        except Exception as e:
            logger.exception("Error generating query explanation")
            # Fall back to a basic response
            return {
                "content": f"I ran the following SQL query to answer your question:\n\n```sql\n{sql_query}\n```\n\nResults:\n\n{result_str}\n\n(Note: An error occurred while generating a detailed explanation: {str(e)})"
            }
