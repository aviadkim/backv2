# FinDoc Financial Analyzer

## Overview

FinDoc Financial Analyzer is a web application for analyzing financial documents. It extracts and displays financial data such as ISIN codes (International Securities Identification Numbers) from uploaded documents and provides portfolio analysis.

## Features

- **Document Management**: Upload, view, and manage financial documents
- **ISIN Extraction**: Automatically extract ISIN codes from document content
- **Portfolio Analysis**: View portfolio summary including total value and asset allocation
- **Financial Dashboard**: Visual representation of financial data

## Technical Implementation

### Backend (Flask)

The backend is built with Flask and provides the following API endpoints:

- `/api/documents`: List, add, and retrieve documents
- `/api/financial/isins`: Get all extracted ISIN codes
- `/api/financial/document/{id}/isins`: Get ISINs for a specific document
- `/api/financial/portfolio`: Get portfolio summary
- `/api/financial/analyze`: Analyze a document for financial data

### Frontend (Next.js)

The frontend is built with Next.js and includes the following pages:

- **Dashboard**: Overview of documents and financial data
- **Analysis**: Detailed financial analysis of documents
- **Upload**: Form for uploading new documents

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Install backend dependencies:
   ```
   cd DevDocs/backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```
   cd DevDocs/frontend
   npm install
   ```

### Running the Application

Run the application using the provided script:

```
.\run-findoc-enhanced.ps1
```

This will:
1. Start the backend API on port 24125
2. Start the frontend on port 3002
3. Open the application in your default browser

## Usage

1. **View Documents**: The dashboard displays all uploaded documents
2. **Analyze Documents**: Go to the Analysis page to analyze documents for financial data
3. **Upload Documents**: Use the Upload page to add new documents

## Implementation Details

### ISIN Extraction

ISINs are extracted using a regular expression pattern that matches the ISIN format (2 letters followed by 10 characters that can be letters or numbers).

```python
def extract_isins(text):
    """Extract ISIN codes from text using regex"""
    # ISIN format: 2 letters followed by 10 characters (letters or numbers)
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
    return re.findall(isin_pattern, text)
```

### Portfolio Analysis

The portfolio summary includes:
- Total value of all securities
- Asset allocation by category
- Currency allocation

## Future Enhancements

- **OCR Integration**: Extract text from scanned documents
- **Advanced Financial Analysis**: Calculate risk metrics and performance indicators
- **Export Functionality**: Export analysis results to PDF or Excel
- **User Authentication**: Secure access to documents and analysis
- **Real-time Data**: Connect to financial data providers for real-time security prices
