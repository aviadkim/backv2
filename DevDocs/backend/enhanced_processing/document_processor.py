"""
Document Processor Module

This module combines all components to process financial documents with high accuracy.
It orchestrates the entire processing pipeline from OCR to output generation.
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .table_extractor import TableExtractor
from .grid_analyzer import GridAnalyzer
from .ocr_processor import OCRProcessor
from .ai_validator import AIValidator
from .output_generator import OutputGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Main document processor that combines all components.
    Orchestrates the entire processing pipeline from OCR to output generation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DocumentProcessor.
        
        Args:
            api_key: API key for AI services
        """
        self.api_key = api_key
        self.output_dir = None
        
        logger.info("Initialized DocumentProcessor")
    
    def process(self, pdf_path: str, output_dir: Optional[str] = None, 
               languages: List[str] = ['eng', 'heb']) -> Dict[str, Any]:
        """
        Process a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files
            languages: List of languages for OCR
            
        Returns:
            Processed financial data
        """
        start_time = time.time()
        
        # Set output directory
        self.output_dir = output_dir or os.path.join(os.path.dirname(pdf_path), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Processing document: {pdf_path}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Step 1: OCR Processing
        ocr_result = self._perform_ocr(pdf_path, languages)
        
        # Step 2: Table Extraction
        table_result = self._extract_tables(ocr_result['ocr_path'])
        
        # Step 3: Grid Analysis
        grid_result = self._analyze_grid(ocr_result['ocr_path'])
        
        # Step 4: Combine Results
        combined_result = self._combine_results(table_result, grid_result)
        
        # Step 5: AI Validation
        validated_result = self._validate_with_ai(combined_result, ocr_result['text'])
        
        # Step 6: Generate Output
        document_info = {
            "document_id": os.path.basename(pdf_path).split('.')[0],
            "document_name": os.path.basename(pdf_path),
            "document_date": datetime.now().strftime('%Y-%m-%d'),
            "processing_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "processing_time": time.time() - start_time
        }
        
        final_result = self._generate_output(validated_result, document_info)
        
        # Save final result
        output_path = os.path.join(self.output_dir, f"{os.path.basename(pdf_path).split('.')[0]}_processed.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete in {time.time() - start_time:.2f} seconds")
        logger.info(f"Final result saved to {output_path}")
        
        return final_result
    
    def _perform_ocr(self, pdf_path: str, languages: List[str]) -> Dict[str, Any]:
        """
        Perform OCR on the document.
        
        Args:
            pdf_path: Path to the PDF file
            languages: List of languages for OCR
            
        Returns:
            Dictionary with OCR results
        """
        logger.info("Step 1: OCR Processing")
        
        ocr_processor = OCRProcessor(pdf_path)
        ocr_path = ocr_processor.process(languages=languages)
        
        # Extract text
        text = ocr_processor.extract_text()
        
        # Save text to file
        text_path = os.path.join(self.output_dir, f"{os.path.basename(pdf_path).split('.')[0]}_ocr.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"OCR processing complete, text saved to {text_path}")
        
        return {
            'ocr_path': ocr_path,
            'text': text,
            'text_path': text_path
        }
    
    def _extract_tables(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract tables from the document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with table extraction results
        """
        logger.info("Step 2: Table Extraction")
        
        table_extractor = TableExtractor(pdf_path)
        tables = table_extractor.extract_tables()
        
        # Extract financial data
        financial_data = table_extractor.extract_financial_data()
        
        # Save tables to file
        tables_path = os.path.join(self.output_dir, f"{os.path.basename(pdf_path).split('.')[0]}_tables.json")
        with open(tables_path, 'w', encoding='utf-8') as f:
            # Convert tables to serializable format
            serializable_tables = []
            for table in tables:
                serializable_tables.append(table.to_dict(orient='records'))
            
            json.dump(serializable_tables, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Table extraction complete, extracted {len(tables)} tables")
        logger.info(f"Extracted {len(financial_data.get('securities', []))} securities from tables")
        
        return {
            'tables': tables,
            'financial_data': financial_data,
            'tables_path': tables_path
        }
    
    def _analyze_grid(self, pdf_path: str) -> Dict[str, Any]:
        """
        Perform grid-based analysis on the document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with grid analysis results
        """
        logger.info("Step 3: Grid Analysis")
        
        grid_analyzer = GridAnalyzer(pdf_path)
        financial_data = grid_analyzer.analyze()
        
        # Save grid data to file
        grid_path = os.path.join(self.output_dir, f"{os.path.basename(pdf_path).split('.')[0]}_grid.json")
        with open(grid_path, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Grid analysis complete, extracted {len(financial_data.get('securities', []))} securities")
        
        return {
            'financial_data': financial_data,
            'grid_path': grid_path
        }
    
    def _combine_results(self, table_result: Dict[str, Any], 
                        grid_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine results from table extraction and grid analysis.
        
        Args:
            table_result: Table extraction results
            grid_result: Grid analysis results
            
        Returns:
            Combined financial data
        """
        logger.info("Step 4: Combining Results")
        
        # Get financial data from both sources
        table_data = table_result['financial_data']
        grid_data = grid_result['financial_data']
        
        # Initialize combined data
        combined_data = {
            'securities': [],
            'asset_allocation': {},
            'total_value': None,
            'currency': None
        }
        
        # Combine securities
        table_securities = table_data.get('securities', [])
        grid_securities = grid_data.get('securities', [])
        
        # Create a map of ISINs to securities
        isin_to_security = {}
        
        # Add table securities
        for security in table_securities:
            if 'isin' in security:
                isin = security['isin']
                isin_to_security[isin] = security
        
        # Add or merge grid securities
        for security in grid_securities:
            if 'isin' in security:
                isin = security['isin']
                
                if isin in isin_to_security:
                    # Merge with existing security
                    existing = isin_to_security[isin]
                    
                    # Keep non-null values
                    for field, value in security.items():
                        if field not in existing or existing[field] is None:
                            existing[field] = value
                else:
                    # Add new security
                    isin_to_security[isin] = security
        
        # Convert back to list
        combined_data['securities'] = list(isin_to_security.values())
        
        # Combine asset allocation
        table_allocation = table_data.get('asset_allocation', {})
        grid_allocation = grid_data.get('asset_allocation', {})
        
        # Merge allocations
        for asset_class, allocation in table_allocation.items():
            combined_data['asset_allocation'][asset_class] = allocation
        
        for asset_class, allocation in grid_allocation.items():
            if asset_class not in combined_data['asset_allocation']:
                combined_data['asset_allocation'][asset_class] = allocation
            else:
                # Merge with existing allocation
                existing = combined_data['asset_allocation'][asset_class]
                
                # Keep non-null values
                for field, value in allocation.items():
                    if field not in existing or existing[field] is None:
                        existing[field] = value
        
        # Combine total value and currency
        combined_data['total_value'] = table_data.get('total_value') or grid_data.get('total_value')
        combined_data['currency'] = table_data.get('currency') or grid_data.get('currency')
        
        # Save combined data to file
        combined_path = os.path.join(self.output_dir, f"{os.path.basename(self.output_dir)}_combined.json")
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Combined results: {len(combined_data['securities'])} securities, "
                   f"{len(combined_data['asset_allocation'])} asset classes")
        
        return combined_data
    
    def _validate_with_ai(self, financial_data: Dict[str, Any], 
                         extracted_text: str) -> Dict[str, Any]:
        """
        Validate financial data with AI.
        
        Args:
            financial_data: Combined financial data
            extracted_text: Extracted text from OCR
            
        Returns:
            Validated financial data
        """
        logger.info("Step 5: AI Validation")
        
        ai_validator = AIValidator(api_key=self.api_key)
        validated_data = ai_validator.validate_financial_data(financial_data, extracted_text)
        
        # Save validated data to file
        validated_path = os.path.join(self.output_dir, f"{os.path.basename(self.output_dir)}_validated.json")
        with open(validated_path, 'w', encoding='utf-8') as f:
            json.dump(validated_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"AI validation complete, validated {len(validated_data.get('securities', []))} securities")
        
        return validated_data
    
    def _generate_output(self, financial_data: Dict[str, Any], 
                        document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final output.
        
        Args:
            financial_data: Validated financial data
            document_info: Document information
            
        Returns:
            Final output
        """
        logger.info("Step 6: Output Generation")
        
        output_generator = OutputGenerator()
        output = output_generator.generate_output(financial_data, document_info)
        
        logger.info("Output generation complete")
        
        return output


# Example usage
if __name__ == "__main__":
    # This will only run when the script is executed directly
    import sys
    import os
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
        
        # Create processor
        processor = DocumentProcessor(api_key=api_key)
        
        # Process document
        result = processor.process(pdf_path, output_dir)
        
        print(f"Processing complete, extracted {len(result['portfolio']['securities'])} securities")
        print(f"Total value: {result['portfolio']['total_value']} {result['portfolio']['currency']}")
    else:
        print("Please provide a PDF file path")
