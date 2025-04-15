"""
Financial Document Processor V2 - Comprehensive financial document processing.

This module integrates all components of the financial document processing pipeline,
including document structure analysis, table extraction, pattern-based extraction,
entity relationship modeling, hierarchical data parsing, validation, and reporting.
"""
import os
import logging
import argparse
import json
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

# Import all components
from document_structure_analyzer import DocumentStructureAnalyzer
from enhanced_table_extractor import EnhancedTableExtractor
from pattern_based_extractor import PatternBasedExtractor
from entity_relationship_modeler import EntityRelationshipModeler
from hierarchical_data_parser import HierarchicalDataParser
from multi_stage_validator import MultiStageValidator
from structured_products_handler import StructuredProductsHandler
from isin_security_extractor import ISINSecurityExtractor
from asset_allocation_deduplicator import AssetAllocationDeduplicator
from comprehensive_report_generator import ComprehensiveReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDocumentProcessorV2:
    """
    Comprehensive financial document processor that integrates all components.
    """

    def __init__(self):
        """Initialize the financial document processor."""
        self.document_structure_analyzer = DocumentStructureAnalyzer()
        self.table_extractor = EnhancedTableExtractor()
        self.pattern_extractor = PatternBasedExtractor()
        self.entity_modeler = EntityRelationshipModeler()
        self.hierarchical_parser = HierarchicalDataParser()
        self.validator = MultiStageValidator()
        self.structured_products_handler = StructuredProductsHandler()
        self.isin_extractor = ISINSecurityExtractor()
        self.asset_allocation_deduplicator = AssetAllocationDeduplicator()
        self.report_generator = ComprehensiveReportGenerator()

        self.extraction_results = {}
        self.processing_results = {}

    def process(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)

        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing financial document: {pdf_path}")

        # Reset data
        self.extraction_results = {}
        self.processing_results = {}

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            # Extract text from PDF
            text = self._extract_text(pdf_path)

            # Save extracted text
            if output_dir:
                text_path = os.path.join(output_dir, "extracted_text.txt")
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(text)

            # Step 1: Analyze document structure
            logger.info("Step 1: Analyzing document structure")
            document_map = self.document_structure_analyzer.analyze(pdf_path, output_dir=output_dir)
            self.processing_results["document_structure"] = document_map

            # Step 2: Extract tables
            logger.info("Step 2: Extracting tables")
            tables_result = self.table_extractor.extract(pdf_path, output_dir=output_dir)
            self.processing_results["tables"] = tables_result

            # Step 3: Extract patterns
            logger.info("Step 3: Extracting patterns")
            patterns_result = self.pattern_extractor.extract(text, output_dir=output_dir)
            self.processing_results["patterns"] = patterns_result

            # Step 4: Parse hierarchical data
            logger.info("Step 4: Parsing hierarchical data")
            hierarchical_result = self.hierarchical_parser.parse(tables_result["tables"], text, output_dir=output_dir)
            self.processing_results["hierarchical"] = hierarchical_result

            # Step 5: Handle structured products
            logger.info("Step 5: Handling structured products")
            structured_products_result = self.structured_products_handler.process(tables_result["tables"], text, output_dir=output_dir)
            self.processing_results["structured_products"] = structured_products_result

            # Step 6: Extract ISIN and security information
            logger.info("Step 6: Extracting ISIN and security information")
            securities_result = self.isin_extractor.extract(tables_result["tables"], text, output_dir=output_dir)
            self.processing_results["securities"] = securities_result

            # Step 7: Deduplicate asset allocation
            logger.info("Step 7: Deduplicating asset allocation")
            if "asset_allocation" in hierarchical_result and hierarchical_result["asset_allocation"]:
                asset_allocation_result = self.asset_allocation_deduplicator.deduplicate(hierarchical_result["asset_allocation"], output_dir=output_dir)
                self.processing_results["asset_allocation"] = asset_allocation_result
            else:
                logger.warning("No asset allocation data found for deduplication")
                self.processing_results["asset_allocation"] = {"original_allocations": [], "deduplicated_allocations": [], "normalized_allocations": []}

            # Step 8: Model entity relationships
            logger.info("Step 8: Modeling entity relationships")
            entity_result = self.entity_modeler.model(self._create_entity_input(), output_dir=output_dir)
            self.processing_results["entity_relationships"] = entity_result

            # Step 9: Consolidate extraction results
            logger.info("Step 9: Consolidating extraction results")
            self._consolidate_results()

            # Step 10: Validate extraction results
            logger.info("Step 10: Validating extraction results")
            validation_result = self.validator.validate(self.extraction_results, output_dir=output_dir)
            self.extraction_results["validation"] = validation_result

            # Step 11: Generate reports
            if output_dir:
                logger.info("Step 11: Generating reports")
                report_result = self.report_generator.generate(self.extraction_results, output_dir)
                self.processing_results["reports"] = report_result

            # Save extraction results
            if output_dir:
                result_path = os.path.join(output_dir, "result.json")
                with open(result_path, "w", encoding="utf-8") as f:
                    json.dump(self.extraction_results, f, indent=2)

            logger.info("Financial document processing completed.")
            return {
                "extraction_results": self.extraction_results,
                "processing_results": self.processing_results
            }

        except Exception as e:
            logger.error(f"Error processing financial document: {str(e)}")
            return {"error": str(e)}

    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"

                return text
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""

    def _create_entity_input(self) -> Dict[str, Any]:
        """Create input for entity relationship modeling."""
        entity_input = {}

        # Add portfolio value
        if "hierarchical" in self.processing_results and "portfolio" in self.processing_results["hierarchical"]:
            entity_input["portfolio_value"] = self.processing_results["hierarchical"]["portfolio"]

        # Add securities
        if "securities" in self.processing_results and "securities" in self.processing_results["securities"]:
            entity_input["securities"] = self.processing_results["securities"]["securities"]

        # Add asset allocation
        if "asset_allocation" in self.processing_results and "normalized_allocations" in self.processing_results["asset_allocation"]:
            entity_input["asset_allocation"] = self.processing_results["asset_allocation"]["normalized_allocations"]

        # Add structured products
        if "structured_products" in self.processing_results and "structured_products" in self.processing_results["structured_products"]:
            entity_input["structured_products"] = self.processing_results["structured_products"]["structured_products"]

        return entity_input

    def _consolidate_results(self):
        """Consolidate extraction results from all components."""
        # Portfolio value
        if "hierarchical" in self.processing_results and "portfolio" in self.processing_results["hierarchical"]:
            self.extraction_results["portfolio_value"] = self.processing_results["hierarchical"]["portfolio"]

        # Securities
        if "securities" in self.processing_results and "securities" in self.processing_results["securities"]:
            self.extraction_results["securities"] = self.processing_results["securities"]["securities"]

        # Asset allocation
        if "asset_allocation" in self.processing_results and "normalized_allocations" in self.processing_results["asset_allocation"]:
            self.extraction_results["asset_allocation"] = self.processing_results["asset_allocation"]["normalized_allocations"]

        # Structured products
        if "structured_products" in self.processing_results and "structured_products" in self.processing_results["structured_products"]:
            self.extraction_results["structured_products"] = self.processing_results["structured_products"]["structured_products"]

        # Entity relationships
        if "entity_relationships" in self.processing_results:
            self.extraction_results["entity_relationships"] = self.processing_results["entity_relationships"]

        # Add metadata
        self.extraction_results["metadata"] = {
            "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "2.0"
        }

    def get_extraction_results(self) -> Dict[str, Any]:
        """
        Get extraction results.

        Returns:
            Dict containing extraction results
        """
        return self.extraction_results

    def get_processing_results(self) -> Dict[str, Any]:
        """
        Get processing results.

        Returns:
            Dict containing processing results
        """
        return self.processing_results

    def get_portfolio_value(self) -> Optional[float]:
        """
        Get the portfolio value.

        Returns:
            Portfolio value or None if not found
        """
        if "portfolio_value" in self.extraction_results:
            if isinstance(self.extraction_results["portfolio_value"], dict):
                return self.extraction_results["portfolio_value"].get("value")
            elif isinstance(self.extraction_results["portfolio_value"], (int, float)):
                return float(self.extraction_results["portfolio_value"])
        return None

    def get_securities(self) -> List[Dict[str, Any]]:
        """
        Get securities.

        Returns:
            List of securities
        """
        return self.extraction_results.get("securities", [])

    def get_asset_allocation(self) -> List[Dict[str, Any]]:
        """
        Get asset allocation.

        Returns:
            List of asset allocation entries
        """
        return self.extraction_results.get("asset_allocation", [])

    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get structured products.

        Returns:
            List of structured products
        """
        return self.extraction_results.get("structured_products", [])

    def get_validation_results(self) -> Dict[str, Any]:
        """
        Get validation results.

        Returns:
            Dict containing validation results
        """
        return self.extraction_results.get("validation", {})

    def get_top_securities(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N securities by valuation.

        Args:
            n: Number of securities to retrieve (default: 5)

        Returns:
            List of top N securities by valuation
        """
        securities = self.get_securities()

        # Filter securities with valuation
        securities_with_valuation = [s for s in securities if s.get("valuation")]

        # Sort by valuation (descending)
        sorted_securities = sorted(securities_with_valuation, key=lambda s: s["valuation"], reverse=True)

        return sorted_securities[:n]

    def get_top_asset_classes(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N asset classes by percentage.

        Args:
            n: Number of asset classes to retrieve (default: 5)

        Returns:
            List of top N asset classes by percentage
        """
        asset_allocation = self.get_asset_allocation()

        # Filter allocations with percentage
        allocations_with_percentage = [a for a in asset_allocation if a.get("percentage")]

        # Sort by percentage (descending)
        sorted_allocations = sorted(allocations_with_percentage, key=lambda a: a["percentage"], reverse=True)

        return sorted_allocations[:n]

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")

    args = parser.parse_args()

    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1

    # Create output directory if not specified
    if not args.output_dir:
        file_name = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output_dir = f"{file_name}_results"

    # Process the document
    processor = FinancialDocumentProcessorV2()
    result = processor.process(args.file_path, output_dir=args.output_dir)

    # Check for errors
    if "error" in result:
        logger.error(f"Error processing document: {result['error']}")
        return 1

    # Print summary
    print("\nFinancial Document Processing Summary:")
    print("====================================")

    portfolio_value = processor.get_portfolio_value()
    if portfolio_value:
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
    else:
        print("Portfolio Value: Not found")

    securities = processor.get_securities()
    print(f"Securities: {len(securities)}")

    asset_allocation = processor.get_asset_allocation()
    print(f"Asset Allocation Entries: {len(asset_allocation)}")

    structured_products = processor.get_structured_products()
    print(f"Structured Products: {len(structured_products)}")

    # Print validation summary
    validation = processor.get_validation_results()
    if validation:
        print("\nValidation Summary:")
        for section, result in validation.items():
            if section != "overall":
                continue
            print(f"Overall: {'Valid' if result.get('valid', False) else 'Invalid'}")

            if "issues" in result and result["issues"]:
                print(f"  Issues ({len(result['issues'])}):")
                for issue in result["issues"]:
                    print(f"  - {issue}")

    # Print top securities
    top_securities = processor.get_top_securities(5)
    if top_securities:
        print("\nTop 5 Securities by Valuation:")
        for i, security in enumerate(top_securities, 1):
            print(f"{i}. {security.get('description', security.get('isin', 'Unknown'))}: ${security.get('valuation', 0):,.2f}")

    # Print top asset classes
    top_asset_classes = processor.get_top_asset_classes(5)
    if top_asset_classes:
        print("\nTop 5 Asset Classes by Percentage:")
        for i, allocation in enumerate(top_asset_classes, 1):
            print(f"{i}. {allocation.get('asset_class', 'Unknown')}: {allocation.get('percentage', 0):.2f}%")

    print(f"\nResults saved to: {args.output_dir}")
    print(f"Comprehensive report: {os.path.join(args.output_dir, 'comprehensive_report.html')}")

    return 0

if __name__ == "__main__":
    main()
