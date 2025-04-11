"""
Database service for SQL operations.
"""
import logging
import os
from typing import Dict, List, Any, Optional
import asyncio
import json
import asyncpg

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.connection_string = os.environ.get(
            "DATABASE_URL", 
            "postgresql://postgres:postgres@localhost:5432/devdocs"
        )
        self.pool = None
    
    async def get_connection_pool(self):
        """Get or create the connection pool."""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(self.connection_string)
            except Exception as e:
                logger.exception("Error creating database connection pool")
                raise
        
        return self.pool
    
    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get the database schema."""
        try:
            pool = await self.get_connection_pool()
            
            async with pool.acquire() as conn:
                # Get all tables
                tables_query = """
                SELECT 
                    t.table_name,
                    obj_description(pgc.oid) as table_description
                FROM 
                    information_schema.tables t
                JOIN 
                    pg_class pgc ON pgc.relname = t.table_name
                WHERE 
                    t.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                ORDER BY 
                    t.table_name;
                """
                
                tables = await conn.fetch(tables_query)
                
                schema = {
                    "tables": []
                }
                
                # For each table, get its columns
                for table in tables:
                    table_name = table["table_name"]
                    
                    columns_query = """
                    SELECT 
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        pg_catalog.col_description(pgc.oid, c.ordinal_position) as column_description
                    FROM 
                        information_schema.columns c
                    JOIN 
                        pg_class pgc ON pgc.relname = c.table_name
                    WHERE 
                        c.table_schema = 'public'
                        AND c.table_name = $1
                    ORDER BY 
                        c.ordinal_position;
                    """
                    
                    columns = await conn.fetch(columns_query, table_name)
                    
                    # Format columns
                    formatted_columns = []
                    for column in columns:
                        formatted_columns.append({
                            "name": column["column_name"],
                            "type": column["data_type"],
                            "nullable": column["is_nullable"] == "YES",
                            "default": column["column_default"],
                            "description": column["column_description"] or f"Column {column['column_name']}"
                        })
                    
                    # Add table to schema
                    schema["tables"].append({
                        "name": table_name,
                        "description": table["table_description"] or f"Table {table_name}",
                        "columns": formatted_columns
                    })
                
                return schema
        
        except Exception as e:
            logger.exception("Error getting database schema")
            return {
                "error": str(e),
                "tables": []
            }
    
    async def execute_query(self, query: str, params: List[Any] = None, max_rows: int = 50) -> List[Dict[str, Any]]:
        """Execute a SQL query."""
        try:
            pool = await self.get_connection_pool()
            
            async with pool.acquire() as conn:
                # Check if the query is a SELECT query
                is_select = query.strip().lower().startswith("select")
                
                if is_select:
                    # For SELECT queries, return the results
                    rows = await conn.fetch(query, *(params or []))
                    
                    # Convert to list of dicts and limit rows
                    result = [dict(row) for row in rows[:max_rows]]
                    
                    if len(rows) > max_rows:
                        logger.info(f"Query returned {len(rows)} rows, but only returning {max_rows}")
                    
                    return result
                else:
                    # For non-SELECT queries, execute and return affected rows
                    result = await conn.execute(query, *(params or []))
                    
                    # Parse the result to get the number of affected rows
                    affected_rows = 0
                    if result:
                        # Result format is typically "CMD N" where N is the number of affected rows
                        parts = result.split()
                        if len(parts) > 1 and parts[-1].isdigit():
                            affected_rows = int(parts[-1])
                    
                    return [{"affected_rows": affected_rows}]
        
        except Exception as e:
            logger.exception(f"Error executing query: {query}")
            raise
