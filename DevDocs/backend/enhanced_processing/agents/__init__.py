"""
Agents for the RAG Multimodal Financial Document Processor.
"""

from .ocr_agent import OCRAgent
from .table_detector_agent import TableDetectorAgent
from .isin_extractor_agent import ISINExtractorAgent
from .financial_analyzer_agent import FinancialAnalyzerAgent
from .rag_agent import RAGAgent
from .document_merger_agent import DocumentMergerAgent

__all__ = [
    "OCRAgent",
    "TableDetectorAgent",
    "ISINExtractorAgent",
    "FinancialAnalyzerAgent",
    "RAGAgent",
    "DocumentMergerAgent"
]
