"""
Document service for managing and processing documents.
"""
import logging
import os
import json
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import aiofiles
import asyncio

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for document management and processing."""
    
    def __init__(self):
        self.documents_dir = os.environ.get("DOCUMENTS_DIR", "data/documents")
        self.ensure_documents_dir()
    
    def ensure_documents_dir(self):
        """Ensure the documents directory exists."""
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def get_document_path(self, document_id: str) -> str:
        """Get the path to a document's metadata file."""
        return os.path.join(self.documents_dir, f"{document_id}.json")
    
    def get_document_content_path(self, document_id: str) -> str:
        """Get the path to a document's content file."""
        return os.path.join(self.documents_dir, f"{document_id}.txt")
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            metadata_path = self.get_document_path(document_id)
            content_path = self.get_document_content_path(document_id)
            
            if not os.path.exists(metadata_path) or not os.path.exists(content_path):
                logger.warning(f"Document not found: {document_id}")
                return None
            
            # Load metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Load content
            with open(content_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Combine metadata and content
            document = metadata.copy()
            document["content"] = content
            
            return document
        
        except Exception as e:
            logger.exception(f"Error getting document {document_id}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents (metadata only, not content)."""
        try:
            documents = []
            
            # List all JSON files in the documents directory
            for filename in os.listdir(self.documents_dir):
                if filename.endswith(".json"):
                    document_id = filename[:-5]  # Remove .json extension
                    
                    # Load metadata
                    with open(os.path.join(self.documents_dir, filename), "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    
                    documents.append(metadata)
            
            # Sort by upload date (newest first)
            documents.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
            
            return documents
        
        except Exception as e:
            logger.exception("Error getting all documents")
            return []
    
    async def save_document(self, filename: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Save a document."""
        try:
            document_id = str(uuid.uuid4())
            upload_date = datetime.now().isoformat()
            
            # Prepare metadata
            document_metadata = {
                "id": document_id,
                "filename": filename,
                "upload_date": upload_date,
                "metadata": metadata or {}
            }
            
            # Save metadata
            metadata_path = self.get_document_path(document_id)
            async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(document_metadata, indent=2))
            
            # Save content
            content_path = self.get_document_content_path(document_id)
            async with aiofiles.open(content_path, "w", encoding="utf-8") as f:
                await f.write(content)
            
            logger.info(f"Document saved: {document_id} - {filename}")
            
            # Return the document metadata
            return document_metadata
        
        except Exception as e:
            logger.exception(f"Error saving document {filename}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            metadata_path = self.get_document_path(document_id)
            content_path = self.get_document_content_path(document_id)
            
            # Check if files exist
            metadata_exists = os.path.exists(metadata_path)
            content_exists = os.path.exists(content_path)
            
            if not metadata_exists and not content_exists:
                logger.warning(f"Document not found for deletion: {document_id}")
                return False
            
            # Delete files if they exist
            if metadata_exists:
                os.remove(metadata_path)
            
            if content_exists:
                os.remove(content_path)
            
            logger.info(f"Document deleted: {document_id}")
            return True
        
        except Exception as e:
            logger.exception(f"Error deleting document {document_id}")
            return False
    
    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """Process a document to extract information."""
        try:
            document = self.get_document(document_id)
            
            if not document:
                return {
                    "error": "document_not_found",
                    "error_message": f"Document with ID {document_id} not found."
                }
            
            # In a real implementation, this would perform actual document processing
            # For now, we'll just return some mock analysis results
            
            analysis_results = {
                "document_id": document_id,
                "filename": document.get("filename", "Unknown"),
                "analysis_date": datetime.now().isoformat(),
                "content_length": len(document.get("content", "")),
                "extracted_data": {
                    "entities": ["Sample Entity 1", "Sample Entity 2"],
                    "key_phrases": ["Sample Phrase 1", "Sample Phrase 2"],
                    "sentiment": "neutral"
                }
            }
            
            # Update document metadata with analysis results
            document_metadata = document.copy()
            document_metadata.pop("content", None)  # Remove content from metadata
            document_metadata["metadata"] = document_metadata.get("metadata", {})
            document_metadata["metadata"]["analysis"] = analysis_results
            
            # Save updated metadata
            metadata_path = self.get_document_path(document_id)
            async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(document_metadata, indent=2))
            
            logger.info(f"Document processed: {document_id}")
            
            return analysis_results
        
        except Exception as e:
            logger.exception(f"Error processing document {document_id}")
            return {
                "error": "processing_error",
                "error_message": f"Error processing document: {str(e)}"
            }
