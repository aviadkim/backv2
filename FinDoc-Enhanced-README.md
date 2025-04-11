# FinDoc Financial Analyzer - Enhanced Version

## Overview

FinDoc Financial Analyzer is a web application for analyzing financial documents. This enhanced version includes improved document upload functionality, financial analysis features, data visualization, agent integration, and a more intuitive user interface.

## New Features

### 1. Enhanced Document Upload

- **Multi-file Upload**: Upload multiple documents at once
- **Drag and Drop**: Intuitive drag and drop interface
- **File Type Selection**: Categorize documents as Financial, Report, Contract, or Other
- **Progress Tracking**: Real-time upload progress indicator
- **File Validation**: Automatic validation of file types and sizes

### 2. Financial Analysis

- **ISIN Extraction**: Automatically extract ISIN codes from document content
- **Portfolio Analysis**: View portfolio summary including total value and asset allocation
- **Document Classification**: Categorize documents by type for better organization

### 3. Data Visualization

- **Interactive Charts**: Visualize portfolio allocation and performance
- **Multiple Chart Types**: Pie charts, bar charts, and line charts
- **Responsive Design**: Charts adapt to different screen sizes
- **Tabbed Interface**: Organized view of different analysis aspects

### 4. Agent Integration

- **Agent Framework**: Integrated agent system for automated document processing
- **Financial Agent**: Specialized agent for financial document analysis
- **Risk Metrics**: Advanced risk analysis for portfolios
- **Performance Analysis**: Track portfolio performance over time

### 5. Improved UI/UX

- **Responsive Design**: Works on desktop and mobile devices
- **Visual Feedback**: Success/error messages and progress indicators
- **Intuitive Navigation**: Clear navigation between different sections

## Technical Implementation

### Backend (Flask)

The backend has been enhanced with the following features:

- **Agent System**: Integrated agent framework for document processing
- **Financial Analysis API**: Endpoints for portfolio analysis and risk metrics
- **File Upload Handling**: Secure file upload with validation
- **Document Storage**: Store uploaded files with unique identifiers
- **ISIN Extraction**: Extract ISIN codes from document content
- **Portfolio Analysis**: Calculate portfolio metrics based on extracted data

### Frontend (Next.js)

The frontend has been enhanced with the following features:

- **Chart.js Integration**: Interactive data visualization
- **Portfolio Analysis Page**: Comprehensive view of portfolio data
- **Tabbed Interface**: Organized view of different analysis aspects
- **Multi-file Upload**: Support for uploading multiple files at once
- **File Type Selection**: UI for selecting document types
- **Progress Tracking**: Real-time upload progress indicator
- **Responsive Design**: Works on desktop and mobile devices

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

1. **Upload Documents**:
   - Go to the Upload page
   - Select document type (Financial, Report, Contract, Other)
   - Drag and drop files or click to browse
   - Add document title and tags
   - Click "Upload Document"

2. **View Documents**:
   - The dashboard displays all uploaded documents
   - Click on a document to view details

3. **Analyze Documents**:
   - Go to the Analysis page
   - Select a document to analyze
   - View extracted ISIN codes and financial data

4. **Portfolio Analysis**:
   - Go to the Portfolio page
   - View portfolio allocation and performance
   - Analyze risk metrics
   - Explore holdings details

## Implementation Details

### Agent Framework

The agent framework provides a modular approach to document processing:

```python
class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str = "base", memory_path: Optional[str] = None):
        """Initialize the base agent."""
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

        # Setup memory persistence if path provided
        self.memory_path = memory_path
        self.memory = self._load_memory() if memory_path else {}
```

### Data Visualization

The data visualization components use Chart.js for interactive charts:

```javascript
const PieChart = ({ data, title, height = 300 }) => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    if (data) {
      // Extract labels and values from data
      const labels = Object.keys(data);
      const values = Object.values(data).map(val => {
        // If value is a string with a percentage, convert to number
        if (typeof val === 'string' && val.includes('%')) {
          return parseFloat(val.replace('%', ''));
        }
        return val;
      });

      setChartData({
        labels,
        datasets: [
          {
            data: values,
            backgroundColor,
            borderColor,
            borderWidth: 1,
          },
        ],
      });
    }
  }, [data]);
```

### Multi-file Upload

The enhanced upload functionality allows users to upload multiple files at once:

```javascript
const handleFileChange = (fileList) => {
  const newFiles = Array.from(fileList);

  // Filter for allowed file types
  const allowedExtensions = ['.pdf', '.docx', '.xlsx', '.csv'];
  const filteredFiles = newFiles.filter(file => {
    const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    return allowedExtensions.includes(extension);
  });

  if (filteredFiles.length > 0) {
    setFiles(filteredFiles);
    // Auto-fill title from first filename
    const fileName = filteredFiles[0].name.replace(/\.[^/.]+$/, "");
    setTitle(fileName);
  }
};
```

### ISIN Extraction

ISINs are extracted using a regular expression pattern:

```python
def extract_isins(text):
    """Extract ISIN codes from text using regex"""
    # ISIN format: 2 letters followed by 10 characters (letters or numbers)
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
    return re.findall(isin_pattern, text)
```

## Future Enhancements

- **OCR Integration**: Extract text from scanned documents
- **Advanced Financial Analysis**: Calculate risk metrics and performance indicators
- **Export Functionality**: Export analysis results to PDF or Excel
- **User Authentication**: Secure access to documents and analysis
- **Real-time Data**: Connect to financial data providers for real-time security prices
