import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime
import uuid

from .pdf_processor import PDFProcessor
from .excel_processor import ExcelProcessor
from .financial_entity_recognizer import FinancialEntityRecognizer
from .financial_data_extractor import FinancialDataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentUnderstandingEngine:
    """
    Document Understanding Engine for processing and analyzing financial documents.
    """
    
    def __init__(self, storage_dir: str = "processed_documents"):
        """
        Initialize the Document Understanding Engine.
        
        Args:
            storage_dir: Directory to store processed documents
        """
        self.pdf_processor = PDFProcessor()
        self.excel_processor = ExcelProcessor()
        self.entity_recognizer = FinancialEntityRecognizer()
        self.financial_data_extractor = FinancialDataExtractor()
        
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a financial document and extract its content and structure.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing processed document data
        """
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Process based on file type
            if file_ext in ['.pdf']:
                document = self.pdf_processor.process_pdf(file_path)
            elif file_ext in ['.xlsx', '.xlsm', '.xls', '.csv']:
                document = self.excel_processor.process_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            document["id"] = document_id
            
            # Save processed document
            self._save_processed_document(document_id, document)
            
            return document
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def analyze_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a processed document and extract financial data.
        
        Args:
            document: Processed document dictionary
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing document: {document.get('file_name', 'unknown')}")
        
        try:
            # Extract financial data
            financial_data = self.financial_data_extractor.extract_financial_data(document)
            
            # Extract financial ratios
            financial_ratios = self.financial_data_extractor.extract_financial_ratios(document)
            
            # Extract company information
            company_info = self.financial_data_extractor.extract_company_information(document)
            
            # Combine results
            analysis_results = {
                "document_id": document.get("id", str(uuid.uuid4())),
                "document_info": {
                    "file_name": document.get("file_name", ""),
                    "file_path": document.get("file_path", ""),
                    "title": document.get("structure", {}).get("title", "")
                },
                "company_info": company_info,
                "financial_data": financial_data,
                "financial_ratios": financial_ratios,
                "analyzed_at": datetime.now().isoformat()
            }
            
            # Save analysis results
            self._save_analysis_results(analysis_results["document_id"], analysis_results)
            
            return analysis_results
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    def process_and_analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process and analyze a financial document in one step.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing analysis results
        """
        # Process document
        document = self.process_document(file_path)
        
        # Analyze document
        analysis_results = self.analyze_document(document)
        
        return analysis_results
    
    def _save_processed_document(self, document_id: str, document: Dict[str, Any]):
        """
        Save a processed document to storage.
        
        Args:
            document_id: Document ID
            document: Processed document dictionary
        """
        file_path = os.path.join(self.storage_dir, f"{document_id}_document.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
    
    def _save_analysis_results(self, document_id: str, analysis_results: Dict[str, Any]):
        """
        Save analysis results to storage.
        
        Args:
            document_id: Document ID
            analysis_results: Analysis results dictionary
        """
        file_path = os.path.join(self.storage_dir, f"{document_id}_analysis.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    def get_processed_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a processed document from storage.
        
        Args:
            document_id: Document ID
            
        Returns:
            Processed document dictionary or None if not found
        """
        file_path = os.path.join(self.storage_dir, f"{document_id}_document.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_analysis_results(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis results from storage.
        
        Args:
            document_id: Document ID
            
        Returns:
            Analysis results dictionary or None if not found
        """
        file_path = os.path.join(self.storage_dir, f"{document_id}_analysis.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_processed_documents(self) -> List[Dict[str, Any]]:
        """
        List all processed documents.
        
        Returns:
            List of document metadata
        """
        documents = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('_document.json'):
                document_id = filename.split('_')[0]
                
                file_path = os.path.join(self.storage_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    document = json.load(f)
                
                documents.append({
                    "id": document_id,
                    "file_name": document.get("file_name", ""),
                    "file_path": document.get("file_path", ""),
                    "title": document.get("structure", {}).get("title", ""),
                    "processed_at": document.get("processed_at", "")
                })
        
        return documents
    
    def compare_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple documents.
        
        Args:
            document_ids: List of document IDs to compare
            
        Returns:
            Dictionary containing comparison results
        """
        if len(document_ids) < 2:
            raise ValueError("At least two documents are required for comparison")
        
        # Load analysis results for all documents
        analysis_results = []
        for document_id in document_ids:
            result = self.get_analysis_results(document_id)
            if result:
                analysis_results.append(result)
            else:
                logger.warning(f"Analysis results not found for document ID: {document_id}")
        
        if len(analysis_results) < 2:
            raise ValueError("At least two valid analysis results are required for comparison")
        
        # Compare financial data
        comparison = self._compare_financial_data(analysis_results)
        
        return comparison
    
    def _compare_financial_data(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare financial data from multiple documents.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            "documents": [],
            "financial_metrics": {},
            "financial_ratios": {},
            "time_periods": set()
        }
        
        # Add document info
        for result in analysis_results:
            comparison["documents"].append({
                "id": result["document_id"],
                "title": result["document_info"]["title"],
                "file_name": result["document_info"]["file_name"]
            })
            
            # Collect time periods
            for period in result["financial_data"]["time_periods"]:
                comparison["time_periods"].add(period["text"])
        
        # Convert time periods to list
        comparison["time_periods"] = list(comparison["time_periods"])
        
        # Compare financial metrics
        metrics_by_name = {}
        
        for result in analysis_results:
            for metric in result["financial_data"]["financial_metrics"]:
                name = metric["name"]
                if name not in metrics_by_name:
                    metrics_by_name[name] = []
                
                metrics_by_name[name].append({
                    "document_id": result["document_id"],
                    "value": metric["value"],
                    "period": metric["period"],
                    "display_name": metric["display_name"]
                })
        
        comparison["financial_metrics"] = metrics_by_name
        
        # Compare financial ratios
        ratios_by_name = {}
        
        for result in analysis_results:
            for ratio in result["financial_ratios"]:
                name = ratio["name"]
                if name not in ratios_by_name:
                    ratios_by_name[name] = []
                
                ratios_by_name[name].append({
                    "document_id": result["document_id"],
                    "value": ratio["value"],
                    "period": ratio["period"],
                    "display_name": ratio["display_name"]
                })
        
        comparison["financial_ratios"] = ratios_by_name
        
        return comparison
    
    def generate_report(self, document_id: str, report_type: str = "summary") -> Dict[str, Any]:
        """
        Generate a report from analysis results.
        
        Args:
            document_id: Document ID
            report_type: Type of report to generate
            
        Returns:
            Dictionary containing report data
        """
        # Get analysis results
        analysis_results = self.get_analysis_results(document_id)
        
        if not analysis_results:
            raise ValueError(f"Analysis results not found for document ID: {document_id}")
        
        # Generate report based on type
        if report_type == "summary":
            report = self._generate_summary_report(analysis_results)
        elif report_type == "financial_statement":
            report = self._generate_financial_statement_report(analysis_results)
        elif report_type == "metrics":
            report = self._generate_metrics_report(analysis_results)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        return report
    
    def _generate_summary_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary report.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Dictionary containing report data
        """
        report = {
            "title": f"Summary Report: {analysis_results['document_info']['title']}",
            "document_id": analysis_results["document_id"],
            "document_info": analysis_results["document_info"],
            "company_info": analysis_results["company_info"],
            "key_metrics": [],
            "financial_statements": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Add key metrics
        for metric in analysis_results["financial_data"]["financial_metrics"]:
            if metric["name"] in ["revenue", "net_income", "ebitda", "eps"]:
                report["key_metrics"].append(metric)
        
        # Add financial statements
        for statement in analysis_results["financial_data"]["financial_statements"]:
            report["financial_statements"].append({
                "type": statement["type"],
                "line_items": statement["data"][:5]  # Include only top 5 line items
            })
        
        return report
    
    def _generate_financial_statement_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a financial statement report.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Dictionary containing report data
        """
        report = {
            "title": f"Financial Statement Report: {analysis_results['document_info']['title']}",
            "document_id": analysis_results["document_id"],
            "document_info": analysis_results["document_info"],
            "company_info": analysis_results["company_info"],
            "financial_statements": analysis_results["financial_data"]["financial_statements"],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_metrics_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a metrics report.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Dictionary containing report data
        """
        report = {
            "title": f"Financial Metrics Report: {analysis_results['document_info']['title']}",
            "document_id": analysis_results["document_id"],
            "document_info": analysis_results["document_info"],
            "company_info": analysis_results["company_info"],
            "financial_metrics": analysis_results["financial_data"]["financial_metrics"],
            "financial_ratios": analysis_results["financial_ratios"],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
