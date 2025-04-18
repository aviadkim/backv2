"""
Main processor for the RAG Multimodal Financial Document Processor.
"""

import os
import time
import logging
from typing import Dict, Any, Optional

from .config import get_config
from .utils import ensure_dir
from .agents.ocr_agent import OCRAgent
from .agents.table_detector_agent import TableDetectorAgent
from .agents.isin_extractor_agent import ISINExtractorAgent
from .agents.financial_analyzer_agent import FinancialAnalyzerAgent
from .agents.rag_agent import RAGAgent
from .agents.document_merger_agent import DocumentMergerAgent

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Main document processor that combines all components.
    """
    
    def __init__(self, config=None):
        """
        Initialize the DocumentProcessor.
        
        Args:
            config: Custom configuration
        """
        self.config = get_config(config)
        
        # Initialize agents
        self.ocr_agent = OCRAgent(self.config)
        self.table_detector_agent = TableDetectorAgent(self.config)
        self.isin_extractor_agent = ISINExtractorAgent(self.config)
        self.financial_analyzer_agent = FinancialAnalyzerAgent(self.config)
        self.rag_agent = RAGAgent(self.config)
        self.document_merger_agent = DocumentMergerAgent(self.config)
        
        logger.info("Initialized DocumentProcessor")
    
    def process(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files
            
        Returns:
            Processed financial data
        """
        start_time = time.time()
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(pdf_path), "output")
        
        ensure_dir(output_dir)
        
        logger.info(f"Processing document: {pdf_path}")
        logger.info(f"Output directory: {output_dir}")
        
        # Step 1: OCR Processing
        print("Progress: 10%")
        ocr_results = self.ocr_agent.process(pdf_path, os.path.join(output_dir, "ocr"))
        
        # Step 2: Table Detection
        print("Progress: 30%")
        table_results = self.table_detector_agent.process(pdf_path, ocr_results, os.path.join(output_dir, "tables"))
        
        # Step 3: ISIN Extraction
        print("Progress: 50%")
        isin_results = self.isin_extractor_agent.process(ocr_results, table_results, os.path.join(output_dir, "isins"))
        
        # Step 4: Financial Analysis
        print("Progress: 70%")
        financial_results = self.financial_analyzer_agent.process(ocr_results, table_results, isin_results, os.path.join(output_dir, "analysis"))
        
        # Step 5: RAG Validation
        print("Progress: 80%")
        rag_results = self.rag_agent.process(ocr_results, financial_results, pdf_path, os.path.join(output_dir, "rag"))
        
        # Step 6: Document Merging
        print("Progress: 90%")
        final_results = self.document_merger_agent.process(rag_results, pdf_path, output_dir)
        
        # Update processing time
        processing_time = time.time() - start_time
        final_results["final_output"]["document_info"]["processing_time"] = processing_time
        
        # Save updated final output
        with open(final_results["output_path"], "w") as f:
            import json
            json.dump(final_results["final_output"], f, indent=2, ensure_ascii=False)
        
        print("Progress: 100%")
        
        logger.info(f"Processing complete in {processing_time:.2f} seconds")
        
        return final_results["final_output"]
