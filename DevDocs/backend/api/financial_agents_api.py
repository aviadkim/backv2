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
from ..agents.document_integration_agent import DocumentIntegrationAgent
from ..agents.query_engine_agent import QueryEngineAgent
from ..agents.notification_agent import NotificationAgent
from ..agents.data_export_agent import DataExportAgent
from ..agents.document_comparison_agent import DocumentComparisonAgent
from ..agents.financial_advisor_agent import FinancialAdvisorAgent
from ..agents.document_merge_agent import DocumentMergeAgent
from ..agents.document_preprocessor_agent import DocumentPreprocessorAgent
from ..agents.hebrew_ocr_agent import HebrewOCRAgent
from ..agents.isin_extractor_agent import ISINExtractorAgent

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

class DocumentIntegrationRequest(BaseModel):
    """Document integration request model."""
    extracted_text: str
    tables_data: List[Dict[str, Any]]
    financial_data: Dict[str, Any]
    isin_entities: Optional[List[Dict[str, Any]]] = None
    output_format: Optional[str] = None

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    document_data: Dict[str, Any]

class NotificationRequest(BaseModel):
    """Notification request model."""
    document_data: Dict[str, Any]
    user_settings: Optional[Dict[str, Any]] = None

class DataExportRequest(BaseModel):
    """Data export request model."""
    data: Dict[str, Any]
    format_type: str
    filename: Optional[str] = None
    export_type: Optional[str] = "raw"

class DocumentComparisonRequest(BaseModel):
    """Document comparison request model."""
    current_doc: Dict[str, Any]
    previous_doc: Dict[str, Any]

class FinancialAdvisorRequest(BaseModel):
    """Financial advisor request model."""
    analysis_type: str
    document_data: Dict[str, Any]
    risk_profile: Optional[str] = "medium"
    investment_amount: Optional[float] = 0

class DocumentMergeRequest(BaseModel):
    """Document merge request model."""
    documents: List[Dict[str, Any]]

class DocumentCompareOverTimeRequest(BaseModel):
    """Document compare over time request model."""
    merged_documents: List[Dict[str, Any]]

class ComprehensiveReportRequest(BaseModel):
    """Comprehensive report request model."""
    merged_document: Dict[str, Any]

class DocumentPreprocessRequest(BaseModel):
    """Document preprocess request model."""
    image_base64: str
    options: Optional[Dict[str, Any]] = None

class HebrewOCRRequest(BaseModel):
    """Hebrew OCR request model."""
    image_base64: str
    with_positions: Optional[bool] = False
    language: Optional[str] = "heb+eng"

class ISINExtractRequest(BaseModel):
    """ISIN extract request model."""
    text: str
    validate: Optional[bool] = True
    include_metadata: Optional[bool] = True

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

    if "document_integration" not in manager.agents:
        manager.create_agent(
            "document_integration",
            DocumentIntegrationAgent
        )

    if "query_engine" not in manager.agents:
        manager.create_agent(
            "query_engine",
            QueryEngineAgent
        )

    if "notification" not in manager.agents:
        manager.create_agent(
            "notification",
            NotificationAgent
        )

    if "data_export" not in manager.agents:
        manager.create_agent(
            "data_export",
            DataExportAgent
        )

    if "document_comparison" not in manager.agents:
        manager.create_agent(
            "document_comparison",
            DocumentComparisonAgent
        )

    if "financial_advisor" not in manager.agents:
        manager.create_agent(
            "financial_advisor",
            FinancialAdvisorAgent
        )

    if "document_merge" not in manager.agents:
        manager.create_agent(
            "document_merge",
            DocumentMergeAgent
        )

    if "document_preprocessor" not in manager.agents:
        manager.create_agent(
            "document_preprocessor",
            DocumentPreprocessorAgent
        )

    if "hebrew_ocr" not in manager.agents:
        manager.create_agent(
            "hebrew_ocr",
            HebrewOCRAgent
        )

    if "isin_extractor" not in manager.agents:
        manager.create_agent(
            "isin_extractor",
            ISINExtractorAgent
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

                # Extract text from the image
                extracted_text = detection_result.get('text', '')

                # Integrate document data
                integrated_data = manager.run_agent(
                    "document_integration",
                    extracted_text=extracted_text,
                    tables_data=detection_result['tables'],
                    financial_data={
                        'portfolio': {
                            'securities': [],
                            'summary': {}
                        }
                    }
                )

                return {
                    'file_name': file.filename,
                    'detection': detection_result,
                    'analysis': analysis_results,
                    'integrated_data': integrated_data.get('integrated_data', {})
                }

            elif file.content_type == 'text/csv' or file.filename.lower().endswith('.csv'):
                # Process CSV
                df = pd.read_csv(temp_path)

                # Analyze data
                analysis = manager.run_agent(
                    "data_analyzer",
                    table_data=df
                )

                # Read CSV content as text
                with open(temp_path, 'r', encoding='utf-8') as f:
                    csv_text = f.read()

                # Integrate document data
                integrated_data = manager.run_agent(
                    "document_integration",
                    extracted_text=csv_text,
                    tables_data=[{
                        'data': df,
                        'type': analysis.get('table_type', 'unknown')
                    }],
                    financial_data={
                        analysis.get('table_type', 'portfolio'): analysis
                    }
                )

                return {
                    'file_name': file.filename,
                    'analysis': analysis,
                    'integrated_data': integrated_data.get('integrated_data', {})
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

@router.post("/integrate-document")
async def integrate_document(
    request: DocumentIntegrationRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Integrate document data.

    Args:
        request: Document integration request
        manager: Agent manager

    Returns:
        Integrated document data
    """
    try:
        # Integrate document data
        result = manager.run_agent(
            "document_integration",
            extracted_text=request.extracted_text,
            tables_data=request.tables_data,
            financial_data=request.financial_data,
            isin_entities=request.isin_entities,
            output_format=request.output_format
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error integrating document data: {str(e)}")

@router.post("/query")
async def query_document(
    request: QueryRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Query document data.

    Args:
        request: Query request
        manager: Agent manager

    Returns:
        Query results
    """
    try:
        # Process query
        result = manager.run_agent(
            "query_engine",
            query=request.query,
            document_data=request.document_data
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/notifications")
async def generate_notifications(
    request: NotificationRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Generate notifications based on document data.

    Args:
        request: Notification request
        manager: Agent manager

    Returns:
        Generated notifications
    """
    try:
        # Generate notifications
        result = manager.run_agent(
            "notification",
            document_data=request.document_data,
            user_settings=request.user_settings
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating notifications: {str(e)}")

@router.post("/export")
async def export_data(
    request: DataExportRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Export data to various formats.

    Args:
        request: Data export request
        manager: Agent manager

    Returns:
        Export results
    """
    try:
        # Export data
        result = manager.run_agent(
            "data_export",
            data=request.data,
            format_type=request.format_type,
            filename=request.filename,
            export_type=request.export_type
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.post("/compare-documents")
async def compare_documents(
    request: DocumentComparisonRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Compare documents and identify changes.

    Args:
        request: Document comparison request
        manager: Agent manager

    Returns:
        Comparison results
    """
    try:
        # Compare documents
        result = manager.run_agent(
            "document_comparison",
            current_doc=request.current_doc,
            previous_doc=request.previous_doc
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing documents: {str(e)}")

@router.post("/financial-advice")
async def get_financial_advice(
    request: FinancialAdvisorRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Get financial advice based on document data.

    Args:
        request: Financial advisor request
        manager: Agent manager

    Returns:
        Financial advice and recommendations
    """
    try:
        # Get financial advice
        result = manager.run_agent(
            "financial_advisor",
            analysis_type=request.analysis_type,
            document_data=request.document_data,
            risk_profile=request.risk_profile,
            investment_amount=request.investment_amount
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting financial advice: {str(e)}")

@router.post("/merge-documents")
async def merge_documents(
    request: DocumentMergeRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Merge multiple documents into a single document.

    Args:
        request: Document merge request
        manager: Agent manager

    Returns:
        Merged document
    """
    try:
        # Merge documents
        result = manager.run_agent(
            "document_merge",
            documents=request.documents
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging documents: {str(e)}")

@router.post("/compare-over-time")
async def compare_over_time(
    request: DocumentCompareOverTimeRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Compare merged documents over time.

    Args:
        request: Document compare over time request
        manager: Agent manager

    Returns:
        Comparison results
    """
    try:
        # Compare documents over time
        result = manager.run_agent(
            "document_merge",
            method="compare_merged_document_over_time",
            merged_documents=request.merged_documents
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing documents over time: {str(e)}")

@router.post("/comprehensive-report")
async def generate_comprehensive_report(
    request: ComprehensiveReportRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Generate a comprehensive financial report.

    Args:
        request: Comprehensive report request
        manager: Agent manager

    Returns:
        Comprehensive report
    """
    try:
        # Generate comprehensive report
        result = manager.run_agent(
            "document_merge",
            method="generate_comprehensive_report",
            merged_document=request.merged_document
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive report: {str(e)}")

@router.post("/preprocess-document")
async def preprocess_document(
    request: DocumentPreprocessRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Preprocess a document image for better OCR results.

    Args:
        request: Document preprocess request
        manager: Agent manager

    Returns:
        Preprocessed image
    """
    try:
        # Decode base64 image
        image = decode_image(request.image_base64)

        # Preprocess the image
        result = manager.run_agent(
            "document_preprocessor",
            image=image,
            options=request.options
        )

        # Encode the preprocessed image to base64
        if 'preprocessed_image' in result and result['status'] == 'success':
            _, buffer = cv2.imencode('.png', result['preprocessed_image'])
            preprocessed_base64 = base64.b64encode(buffer).decode('utf-8')
            result['preprocessed_image_base64'] = preprocessed_base64
            # Remove the numpy array from the response
            del result['preprocessed_image']

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preprocessing document: {str(e)}")

@router.post("/hebrew-ocr")
async def hebrew_ocr(
    request: HebrewOCRRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Extract text from an image with Hebrew OCR.

    Args:
        request: Hebrew OCR request
        manager: Agent manager

    Returns:
        Extracted text
    """
    try:
        # Decode base64 image
        image = decode_image(request.image_base64)

        # Extract text
        result = manager.run_agent(
            "hebrew_ocr",
            image=image,
            with_positions=request.with_positions,
            language=request.language
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

@router.post("/extract-isins")
async def extract_isins(
    request: ISINExtractRequest,
    manager: AgentManager = Depends(get_agent_manager)
):
    """
    Extract ISIN numbers from text.

    Args:
        request: ISIN extract request
        manager: Agent manager

    Returns:
        Extracted ISIN numbers
    """
    try:
        # Extract ISINs
        result = manager.run_agent(
            "isin_extractor",
            text=request.text,
            validate=request.validate,
            include_metadata=request.include_metadata
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting ISINs: {str(e)}")
