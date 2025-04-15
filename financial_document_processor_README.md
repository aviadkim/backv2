# Comprehensive Financial Document Processor

This module provides a comprehensive solution for extracting and analyzing financial data from PDF documents, with a focus on portfolio statements, asset allocations, and securities information.

## Features

- **Document Structure Analysis**: Analyzes the structure of financial documents to identify sections, headers, and hierarchical relationships.
- **Enhanced Table Extraction**: Extracts tables using multiple methods (Camelot, pdfplumber, Tabula) and classifies them based on content.
- **Pattern-Based Financial Line Extraction**: Extracts financial data using pattern matching, focusing on common financial line formats.
- **Entity Relationship Modeling**: Models relationships between financial entities (securities, asset classes, etc.).
- **Hierarchical Data Parsing**: Parses hierarchical financial data, identifying totals, subtotals, and their components.
- **Multi-Stage Validation**: Validates extraction results using multiple validation stages and cross-validation.
- **Structured Products Special Handling**: Provides specialized handling for structured products sections.
- **ISIN and Security Information Extraction**: Extracts and validates ISIN codes and security information.
- **Asset Allocation Deduplication**: Deduplicates asset allocation entries and reconciles percentages.
- **Comprehensive Report Generation**: Generates detailed reports with visualizations.

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. For PDF processing, you'll need additional system dependencies:
   - Poppler (for pdfplumber and pdf2image)
   - Tesseract OCR (for text extraction from images)
   - GraphicsMagick (for image processing)

## Usage

### Command Line

```bash
python financial_document_processor_v2.py path/to/financial_document.pdf --output-dir results
```

### Python API

```python
from financial_document_processor_v2 import FinancialDocumentProcessorV2

# Initialize the processor
processor = FinancialDocumentProcessorV2()

# Process a document
result = processor.process("path/to/financial_document.pdf", output_dir="results")

# Access extraction results
portfolio_value = processor.get_portfolio_value()
securities = processor.get_securities()
asset_allocation = processor.get_asset_allocation()
top_securities = processor.get_top_securities(5)
top_asset_classes = processor.get_top_asset_classes(5)
```

## Components

1. **Document Structure Analyzer**: Analyzes the structure of financial documents.
2. **Enhanced Table Extractor**: Extracts tables using multiple methods.
3. **Pattern-Based Extractor**: Extracts financial data using pattern matching.
4. **Entity Relationship Modeler**: Models relationships between financial entities.
5. **Hierarchical Data Parser**: Parses hierarchical financial data.
6. **Multi-Stage Validator**: Validates extraction results.
7. **Structured Products Handler**: Specialized handling for structured products.
8. **ISIN Security Extractor**: Extracts and validates ISIN codes and security information.
9. **Asset Allocation Deduplicator**: Deduplicates asset allocation entries.
10. **Comprehensive Report Generator**: Generates detailed reports.

## Output

The processor generates various output files in the specified output directory:

- `result.json`: Consolidated extraction results
- `document_map.json`: Document structure analysis
- `extracted_tables.json`: Extracted tables
- `classified_tables.json`: Tables classified by type
- `pattern_extracted_data.json`: Data extracted using pattern matching
- `hierarchical_data.json`: Hierarchical financial data
- `entity_relationship_model.json`: Entity relationship model
- `validation_results.json`: Validation results
- `structured_products.json`: Structured products data
- `securities.json`: Securities data
- `isin_validation.json`: ISIN validation results
- `deduplicated_allocations.json`: Deduplicated asset allocations
- `normalized_allocations.json`: Normalized asset allocations
- `comprehensive_report.html`: Comprehensive HTML report
- Various charts and CSV files

## Validation

The processor performs extensive validation of extraction results:

- Portfolio value validation
- Securities validation (ISIN, valuation, etc.)
- Asset allocation validation (percentages, values, etc.)
- Overall consistency validation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
