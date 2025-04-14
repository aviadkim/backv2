"""
API endpoints for financial agents.
"""
import os
import io
import base64
import tempfile
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cv2
import numpy as np
import pandas as pd

from ..agents.agent_manager import AgentManager
from ..agents.financial_table_detector_agent import FinancialTableDetectorAgent
from ..agents.financial_data_analyzer_agent import FinancialDataAnalyzerAgent

# Create router
router = APIRouter(
    prefix="/api/financial",
    tags=["financial"],
    responses={404: {"description": "Not found"}},
)

# Models
class TableDetectionRequest(BaseModel):
    """Table detection request model."""
    image_base64: str
    lang: Optional[str] = "heb+eng"

class DataAnalysisRequest(BaseModel):
    """Data analysis request model."""
    table_data: Dict[str, Any]
    table_type: Optional[str] = "unknown"

# Helper functions
def get_agent_manager():
    """Get the agent manager."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    manager = AgentManager(api_key=api_key)
    
    # Create agents if they don't exist
    if "table_detector" not in manager.agents:
        manager.create_agent(
            "table_detector",
            FinancialTableDetectorAgent
        )
    
    if "data_analyzer" not in manager.agents:
        manager.create_agent(
            "data_analyzer",
            FinancialDataAnalyzerAgent
        )
    
    return manager

def decode_image(image_base64: str):
    """Decode base64 image."""
    try:
        # Remove data URL prefix if present
        if image_base64.startswith('data:image'):
            image_base64 = image_base64.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(image_base64)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

# Endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.environ.get("OPENROUTER_API_KEY"))
    }

@router.post("/detect-tables")
async def detect_tables(
    request: TableDetectionRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Detect tables in an image.
    
    Args:
        request: Table detection request
        manager: Agent manager
        
    Returns:
        Detected tables
    """
    try:
        # Decode image
        image = decode_image(request.image_base64)
        
        # Detect tables
        result = manager.run_agent(
            "table_detector",
            image=image,
            lang=request.lang
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting tables: {str(e)}")

@router.post("/analyze-data")
async def analyze_data(
    request: DataAnalysisRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Analyze financial data.
    
    Args:
        request: Data analysis request
        manager: Agent manager
        
    Returns:
        Analyzed data
    """
    try:
        # Analyze data
        result = manager.run_agent(
            "data_analyzer",
            table_data=request.table_data,
            table_type=request.table_type
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

@router.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    lang: str = Form("heb+eng"),
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Upload a file, detect tables, and analyze the data.
    
    Args:
        file: Uploaded file
        lang: OCR language
        manager: Agent manager
        
    Returns:
        Analysis results
    """
    try:
        # Read file content
        content = await file.read()
        
        # Check file type
        if file.content_type.startswith('image/'):
            # Process image
            nparr = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            
            # Detect tables
            detection_result = manager.run_agent(
                "table_detector",
                image=image,
                lang=lang
            )
            
            # Analyze each table
            analysis_results = []
            for table in detection_result['tables']:
                analysis = manager.run_agent(
                    "data_analyzer",
                    table_data=table['data'],
                    table_type=table['region'].get('table_type', 'unknown')
                )
                
                analysis_results.append({
                    'region': table['region'],
                    'analysis': analysis
                })
            
            return {
                'detection': detection_result,
                'analysis': analysis_results
            }
        
        elif file.content_type == 'text/csv' or file.filename.endswith('.csv'):
            # Process CSV
            df = pd.read_csv(io.BytesIO(content))
            
            # Analyze data
            analysis = manager.run_agent(
                "data_analyzer",
                table_data=df
            )
            
            return {
                'analysis': analysis
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    lang: str = Form("heb+eng"),
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Process a financial document.
    
    Args:
        file: Uploaded file
        lang: OCR language
        manager: Agent manager
        
    Returns:
        Processing results
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            # Write content to the temporary file
            content = await file.read()
            temp.write(content)
            temp_path = temp.name
        
        try:
            # Process the document based on file type
            if file.content_type.startswith('image/') or file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                # Process image
                image = cv2.imread(temp_path)
                
                if image is None:
                    raise HTTPException(status_code=400, detail="Invalid image file")
                
                # Detect tables
                detection_result = manager.run_agent(
                    "table_detector",
                    image_path=temp_path,
                    lang=lang
                )
                
                # Analyze each table
                analysis_results = []
                for table in detection_result['tables']:
                    analysis = manager.run_agent(
                        "data_analyzer",
                        table_data=table['data'],
                        table_type=table['region'].get('table_type', 'unknown')
                    )
                    
                    analysis_results.append({
                        'region': table['region'],
                        'analysis': analysis
                    })
                
                return {
                    'file_name': file.filename,
                    'detection': detection_result,
                    'analysis': analysis_results
                }
            
            elif file.content_type == 'text/csv' or file.filename.lower().endswith('.csv'):
                # Process CSV
                df = pd.read_csv(temp_path)
                
                # Analyze data
                analysis = manager.run_agent(
                    "data_analyzer",
                    table_data=df
                )
                
                return {
                    'file_name': file.filename,
                    'analysis': analysis
                }
            
            elif file.content_type == 'application/pdf' or file.filename.lower().endswith('.pdf'):
                # For PDF, we would need additional processing
                # This is a placeholder for future implementation
                return {
                    'file_name': file.filename,
                    'status': 'PDF processing not implemented yet'
                }
            
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
