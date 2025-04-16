"""
Document indexing for AI agents using LlamaIndex.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json

from financial_document_processor.database.db import Database
from financial_document_processor.agents.config import AIConfig

# Try to import LlamaIndex
try:
    from llama_index import (
        VectorStoreIndex, 
        ServiceContext, 
        Document as LlamaDocument,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.schema import TextNode
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False
    logging.warning("LlamaIndex library not available. Install with: pip install llama-index")

class DocumentIndex:
    """Document indexing for AI agents using LlamaIndex."""
    
    def __init__(self, database: Database, ai_config: AIConfig, persist_dir: Optional[str] = None):
        """
        Initialize the document index.
        
        Args:
            database: Database connection
            ai_config: AI configuration
            persist_dir: Directory to persist the index (optional)
        """
        if not LLAMA_INDEX_AVAILABLE:
            raise ImportError("LlamaIndex library not available. Install with: pip install llama-index")
        
        self.database = database
        self.ai_config = ai_config
        self.persist_dir = persist_dir
        
        # Create service context
        self.service_context = ServiceContext.from_defaults(
            llm=ai_config.get_completion_config()["llm"],
            embed_model=ai_config.get_embedding_config()["embed_model"]
        )
        
        # Initialize or load index
        self.index = self._initialize_index()
    
    def _initialize_index(self) -> VectorStoreIndex:
        """
        Initialize or load the index.
        
        Returns:
            VectorStoreIndex
        """
        if self.persist_dir and os.path.exists(self.persist_dir):
            try:
                # Try to load existing index
                storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                return load_index_from_storage(storage_context)
            except Exception as e:
                logging.warning(f"Failed to load index from {self.persist_dir}: {e}")
                # If loading fails, create a new index
                return VectorStoreIndex([], service_context=self.service_context)
        else:
            # Create a new index
            return VectorStoreIndex([], service_context=self.service_context)
    
    def index_document(self, document_id: int) -> Dict[str, Any]:
        """
        Index a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            Dictionary with indexing results
        """
        # Get document from database
        document = self.database.get_document(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Get raw text
        raw_text = self.database.get_raw_text(document_id)
        if not raw_text or not raw_text.content:
            raise ValueError(f"No raw text found for document: {document_id}")
        
        # Get securities
        securities = self.database.get_securities(document_id)
        
        # Get portfolio value
        portfolio_value = self.database.get_portfolio_value(document_id)
        
        # Get asset allocations
        asset_allocations = self.database.get_asset_allocations(document_id)
        
        # Get tables
        tables = self.database.get_tables(document_id)
        
        # Create document nodes
        nodes = []
        
        # Add raw text node
        text_node = TextNode(
            text=raw_text.content,
            metadata={
                "document_id": document_id,
                "filename": document.filename,
                "document_type": document.document_type,
                "content_type": "raw_text"
            }
        )
        nodes.append(text_node)
        
        # Add securities node
        if securities:
            securities_text = "Securities in the document:\n\n"
            for security in securities:
                securities_text += f"ISIN: {security.isin or 'N/A'}\n"
                securities_text += f"Name: {security.name or security.description or 'N/A'}\n"
                securities_text += f"Type: {security.security_type or 'N/A'}\n"
                securities_text += f"Asset Class: {security.asset_class or 'N/A'}\n"
                securities_text += f"Valuation: {security.valuation or 'N/A'} {security.currency or 'USD'}\n"
                securities_text += f"Price: {security.price or 'N/A'}\n"
                securities_text += f"Quantity: {security.quantity or 'N/A'}\n\n"
            
            securities_node = TextNode(
                text=securities_text,
                metadata={
                    "document_id": document_id,
                    "filename": document.filename,
                    "document_type": document.document_type,
                    "content_type": "securities",
                    "securities_count": len(securities)
                }
            )
            nodes.append(securities_node)
        
        # Add portfolio value node
        if portfolio_value:
            portfolio_text = f"Portfolio Value: {portfolio_value.value} {portfolio_value.currency or 'USD'}\n"
            portfolio_text += f"Date: {portfolio_value.value_date.isoformat() if portfolio_value.value_date else 'N/A'}\n"
            
            portfolio_node = TextNode(
                text=portfolio_text,
                metadata={
                    "document_id": document_id,
                    "filename": document.filename,
                    "document_type": document.document_type,
                    "content_type": "portfolio_value"
                }
            )
            nodes.append(portfolio_node)
        
        # Add asset allocations node
        if asset_allocations:
            allocations_text = "Asset Allocations:\n\n"
            for allocation in asset_allocations:
                allocations_text += f"Asset Class: {allocation.asset_class}\n"
                allocations_text += f"Value: {allocation.value or 'N/A'} {allocation.currency or 'USD'}\n"
                allocations_text += f"Percentage: {allocation.percentage or 'N/A'}%\n\n"
            
            allocations_node = TextNode(
                text=allocations_text,
                metadata={
                    "document_id": document_id,
                    "filename": document.filename,
                    "document_type": document.document_type,
                    "content_type": "asset_allocations",
                    "allocations_count": len(asset_allocations)
                }
            )
            nodes.append(allocations_node)
        
        # Add tables node
        if tables:
            tables_text = "Tables in the document:\n\n"
            for i, table in enumerate(tables):
                tables_text += f"Table {i+1} (Page {table.page_number or 'N/A'}):\n"
                
                # Add headers
                if table.headers:
                    tables_text += "Headers: " + " | ".join([str(h) for h in table.headers]) + "\n"
                
                # Add sample rows (up to 5)
                if table.data:
                    tables_text += "Sample rows:\n"
                    for j, row in enumerate(table.data[:5]):
                        tables_text += " | ".join([str(cell) for cell in row]) + "\n"
                    
                    if len(table.data) > 5:
                        tables_text += f"... and {len(table.data) - 5} more rows\n"
                
                tables_text += "\n"
            
            tables_node = TextNode(
                text=tables_text,
                metadata={
                    "document_id": document_id,
                    "filename": document.filename,
                    "document_type": document.document_type,
                    "content_type": "tables",
                    "tables_count": len(tables)
                }
            )
            nodes.append(tables_node)
        
        # Add document summary node
        summary_text = f"Document Summary for {document.filename}:\n\n"
        summary_text += f"Document Type: {document.document_type or 'N/A'}\n"
        summary_text += f"Page Count: {document.page_count or 'N/A'}\n"
        summary_text += f"Securities Count: {len(securities)}\n"
        summary_text += f"Portfolio Value: {portfolio_value.value if portfolio_value else 'N/A'} {portfolio_value.currency if portfolio_value else 'USD'}\n"
        summary_text += f"Asset Allocations Count: {len(asset_allocations)}\n"
        summary_text += f"Tables Count: {len(tables)}\n"
        
        summary_node = TextNode(
            text=summary_text,
            metadata={
                "document_id": document_id,
                "filename": document.filename,
                "document_type": document.document_type,
                "content_type": "summary"
            }
        )
        nodes.append(summary_node)
        
        # Add nodes to index
        self.index.insert_nodes(nodes)
        
        # Persist index if directory is provided
        if self.persist_dir:
            os.makedirs(self.persist_dir, exist_ok=True)
            self.index.storage_context.persist(persist_dir=self.persist_dir)
        
        return {
            "document_id": document_id,
            "nodes_count": len(nodes),
            "indexed_content_types": [node.metadata["content_type"] for node in nodes]
        }
    
    def query(self, query_text: str, document_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Query the index.
        
        Args:
            query_text: Query text
            document_id: Document ID to filter results (optional)
        
        Returns:
            Dictionary with query results
        """
        # Create query engine
        query_engine = self.index.as_query_engine(
            service_context=self.service_context
        )
        
        # Add document filter if specified
        if document_id is not None:
            query_engine = self.index.as_query_engine(
                service_context=self.service_context,
                filters=lambda node: node.metadata.get("document_id") == document_id
            )
        
        # Execute query
        response = query_engine.query(query_text)
        
        # Extract source nodes
        source_nodes = response.source_nodes if hasattr(response, "source_nodes") else []
        sources = []
        
        for node in source_nodes:
            source = {
                "document_id": node.metadata.get("document_id"),
                "filename": node.metadata.get("filename"),
                "content_type": node.metadata.get("content_type"),
                "score": node.score if hasattr(node, "score") else None
            }
            sources.append(source)
        
        return {
            "query": query_text,
            "response": str(response),
            "sources": sources
        }
