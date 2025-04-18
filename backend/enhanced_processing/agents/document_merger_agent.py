"""
Document Merger Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..utils import ensure_dir, calculate_accuracy

logger = logging.getLogger(__name__)

class DocumentMergerAgent:
    """
    Document Merger Agent for merging and finalizing results.
    """
    
    def __init__(self, config):
        """
        Initialize the Document Merger Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_config = config["output"]
        self.expected = config.get("expected", {})
        
        logger.info("Initialized Document Merger Agent")
    
    def process(self, rag_results: Dict[str, Any], pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process RAG results to create final output.
        
        Args:
            rag_results: RAG validation results
            pdf_path: Path to the PDF file
            output_dir: Output directory
            
        Returns:
            Dictionary with final results
        """
        logger.info("Merging and finalizing results")
        
        # Create output directory
        final_dir = os.path.join(output_dir, "final")
        ensure_dir(final_dir)
        
        # Get validated data
        financial_data = rag_results["validated_data"]
        
        # Create document info
        document_info = self._create_document_info(pdf_path)
        
        # Create metrics
        metrics = self._create_metrics(financial_data)
        
        # Create final output
        final_output = {
            "portfolio": {
                "securities": financial_data["securities"],
                "asset_allocation": financial_data["asset_allocation"],
                "total_value": financial_data["total_value"],
                "currency": financial_data["currency"]
            },
            "metrics": metrics,
            "document_info": document_info
        }
        
        # Calculate accuracy
        accuracy = calculate_accuracy(final_output["portfolio"], self.expected)
        final_output["accuracy"] = accuracy
        
        # Save final output
        output_path = os.path.join(final_dir, f"{os.path.basename(pdf_path).split('.')[0]}_processed.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Final output saved to {output_path}")
        logger.info(f"Overall accuracy: {accuracy.get('overall_accuracy', 0) * 100:.2f}%")
        
        return {
            "final_output": final_output,
            "output_path": output_path
        }
    
    def _create_document_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Create document information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Document information dictionary
        """
        # Get file information
        file_name = os.path.basename(pdf_path)
        file_base = os.path.splitext(file_name)[0]
        
        # Get file modification time
        file_time = os.path.getmtime(pdf_path)
        file_date = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d")
        
        # Create document info
        return {
            "document_id": file_base,
            "document_name": file_name,
            "document_date": file_date,
            "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": None  # Will be filled by the main processor
        }
    
    def _create_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metrics from financial data.
        
        Args:
            financial_data: Financial data
            
        Returns:
            Metrics dictionary
        """
        # Get securities
        securities = financial_data.get("securities", [])
        
        # Get asset allocation
        asset_allocation = financial_data.get("asset_allocation", {})
        
        # Create basic metrics
        metrics = {
            "total_securities": len(securities),
            "total_asset_classes": len(asset_allocation)
        }
        
        # Add existing metrics
        if "metrics" in financial_data:
            metrics.update(financial_data["metrics"])
        
        return metrics
