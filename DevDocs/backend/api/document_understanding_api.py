import os
import logging
import json
import tempfile
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form, Body
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import uuid

# Import the Document Understanding Engine
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from document_understanding.document_understanding_engine import DocumentUnderstandingEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Understanding API",
    description="API for processing and analyzing financial documents",
    version="1.0.0"
)

# Initialize Document Understanding Engine
document_engine = DocumentUnderstandingEngine(storage_dir="processed_documents")

# Define Pydantic models for request/response validation
class DocumentInfo(BaseModel):
    id: str
    file_name: str
    title: str
    processed_at: Optional[str] = None

class CompareDocumentsRequest(BaseModel):
    document_ids: List[str]

class GenerateReportRequest(BaseModel):
    document_id: str
    report_type: str = "summary"

@app.post("/documents/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a financial document.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Write uploaded file content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the document
        document = document_engine.process_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return {
            "status": "success",
            "message": "Document processed successfully",
            "document_id": document["id"],
            "document_info": {
                "file_name": document.get("file_name", ""),
                "title": document.get("structure", {}).get("title", "")
            }
        }
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/analyze", response_model=Dict[str, Any])
async def analyze_document(document_id: str):
    """
    Analyze a processed document.
    """
    try:
        # Get the processed document
        document = document_engine.get_processed_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
        
        # Analyze the document
        analysis_results = document_engine.analyze_document(document)
        
        return {
            "status": "success",
            "message": "Document analyzed successfully",
            "document_id": document_id,
            "analysis_summary": {
                "company_name": analysis_results["company_info"]["name"],
                "financial_statements": len(analysis_results["financial_data"]["financial_statements"]),
                "financial_metrics": len(analysis_results["financial_data"]["financial_metrics"]),
                "financial_ratios": len(analysis_results["financial_ratios"])
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/process-and-analyze", response_model=Dict[str, Any])
async def process_and_analyze_document(file: UploadFile = File(...)):
    """
    Process and analyze a financial document in one step.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Write uploaded file content to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process and analyze the document
        analysis_results = document_engine.process_and_analyze_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return {
            "status": "success",
            "message": "Document processed and analyzed successfully",
            "document_id": analysis_results["document_id"],
            "document_info": analysis_results["document_info"],
            "analysis_summary": {
                "company_name": analysis_results["company_info"]["name"],
                "financial_statements": len(analysis_results["financial_data"]["financial_statements"]),
                "financial_metrics": len(analysis_results["financial_data"]["financial_metrics"]),
                "financial_ratios": len(analysis_results["financial_ratios"])
            }
        }
    except Exception as e:
        logger.error(f"Error processing and analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=Dict[str, Any])
async def list_documents():
    """
    List all processed documents.
    """
    try:
        documents = document_engine.list_processed_documents()
        
        return {
            "status": "success",
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(document_id: str):
    """
    Get a processed document.
    """
    try:
        document = document_engine.get_processed_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
        
        return {
            "status": "success",
            "document_id": document_id,
            "document": document
        }
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/analysis", response_model=Dict[str, Any])
async def get_analysis_results(document_id: str):
    """
    Get analysis results for a document.
    """
    try:
        analysis_results = document_engine.get_analysis_results(document_id)
        
        if not analysis_results:
            raise HTTPException(status_code=404, detail=f"Analysis results not found: {document_id}")
        
        return {
            "status": "success",
            "document_id": document_id,
            "analysis_results": analysis_results
        }
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/compare", response_model=Dict[str, Any])
async def compare_documents(request: CompareDocumentsRequest):
    """
    Compare multiple documents.
    """
    try:
        comparison = document_engine.compare_documents(request.document_ids)
        
        return {
            "status": "success",
            "document_ids": request.document_ids,
            "comparison": comparison
        }
    except Exception as e:
        logger.error(f"Error comparing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/report", response_model=Dict[str, Any])
async def generate_report(document_id: str, request: GenerateReportRequest):
    """
    Generate a report from analysis results.
    """
    try:
        report = document_engine.generate_report(document_id, request.report_type)
        
        return {
            "status": "success",
            "document_id": document_id,
            "report_type": request.report_type,
            "report": report
        }
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/extract-data", response_model=Dict[str, Any])
async def extract_data_from_text(text: str = Body(..., embed=True)):
    """
    Extract financial entities from text.
    """
    try:
        entities = document_engine.entity_recognizer.extract_entities(text)
        
        return {
            "status": "success",
            "entities": entities
        }
    except Exception as e:
        logger.error(f"Error extracting data from text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("document_understanding_api:app", host="0.0.0.0", port=8000, reload=True)
