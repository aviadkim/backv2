# RAG Multimodal Financial Document Processor

A comprehensive solution for processing financial documents with high accuracy using RAG (Retrieval-Augmented Generation) and multimodal analysis.

## Features

- **OCR Processing**: Extract text from documents with support for multiple languages, including Hebrew.
- **Table Detection**: Detect and extract tables using multiple methods (Camelot, pdfplumber, computer vision).
- **ISIN Extraction**: Extract ISINs and related information from text and tables.
- **Financial Analysis**: Analyze financial data to extract securities, asset allocation, and metrics.
- **RAG Validation**: Validate and enhance financial data using AI (OpenAI or Google).
- **Visualization**: Visualize results with charts and annotations.
- **Comprehensive Testing**: Run comprehensive tests with detailed reports.

## Requirements

### Python Dependencies

```bash
pip install -r rag_multimodal_processor/requirements.txt
```

### System Dependencies

- **Poppler**: Required for PDF processing.
- **Tesseract OCR**: Required for OCR processing.
- **GraphicsMagick**: Required for image processing.

## Usage

### Command Line

```bash
python process_document.py messos.pdf --output-dir output
```

### Node.js

```javascript
const RagMultimodalProcessor = require('./node_wrapper');

const processor = new RagMultimodalProcessor({
  apiKey: process.env.OPENAI_API_KEY,
  languages: ['eng', 'heb'],
  verbose: true
});

processor.process('messos.pdf', 'output')
  .then(result => {
    console.log(`Processing complete, extracted ${result.metrics.total_securities} securities`);
    console.log(`Total value: ${result.portfolio.total_value} ${result.portfolio.currency}`);
  })
  .catch(error => {
    console.error(`Error processing document: ${error.message}`);
  });
```

### Comprehensive Testing

```bash
node run_comprehensive_test.js messos.pdf test_output
```

## Architecture

The processor is composed of several specialized agents:

1. **OCR Agent**: Extracts text from documents.
2. **Table Detector Agent**: Detects and extracts tables.
3. **ISIN Extractor Agent**: Extracts ISINs and related information.
4. **Financial Analyzer Agent**: Analyzes financial data.
5. **RAG Agent**: Validates and enhances financial data using AI.
6. **Document Merger Agent**: Merges and finalizes results.

## Output Format

The processor generates a JSON file with the following structure:

```json
{
  "portfolio": {
    "securities": [
      {
        "isin": "XS2754416860",
        "name": "Security 1",
        "quantity": 1000,
        "price": 100.0,
        "value": 100000.0,
        "currency": "USD",
        "asset_class": "Bonds"
      },
      ...
    ],
    "asset_allocation": {
      "Bonds": {
        "value": 44100000.0,
        "weight": 0.6
      },
      "Equities": {
        "value": 42000000.0,
        "weight": 0.4
      }
    },
    "total_value": 86100000.0,
    "currency": "USD"
  },
  "metrics": {
    "total_securities": 41,
    "total_asset_classes": 2
  },
  "document_info": {
    "document_id": "messos",
    "document_name": "messos.pdf",
    "document_date": "2025-04-18",
    "processing_date": "2025-04-18 15:49:42",
    "processing_time": 1.1748485565185547
  }
}
```

## Visualization

The processor can generate visualizations of the results:

- **Securities Chart**: Bar chart of top securities by value.
- **Asset Allocation Chart**: Pie chart of asset allocation.
- **Accuracy Chart**: Bar chart of accuracy metrics.
- **Annotated Pages**: PDF pages with annotations for ISINs.

## Testing

The comprehensive test script runs a complete test of the processor and generates a detailed HTML report with:

- **Test Configuration**: PDF path, output directory, API key.
- **Test Steps**: Status and duration of each step.
- **Validation Results**: Comparison of extracted data with expected values.
- **Performance Metrics**: Processing time for each step.
- **Visualizations**: Charts and annotated pages.

## License

MIT
