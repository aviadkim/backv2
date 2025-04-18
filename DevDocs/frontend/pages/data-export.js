import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const DataExportTool = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [exportFormat, setExportFormat] = useState('json');
  const [exportOptions, setExportOptions] = useState({
    includeText: true,
    includeTables: true,
    includeISINs: true,
    includeFinancialData: true
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportUrl, setExportUrl] = useState(null);
  const [error, setError] = useState(null);

  // Fetch documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/financial/documents');
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to load documents. Please try again later.');
    }
  };

  const handleOptionChange = (option) => {
    setExportOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  const handleExport = async () => {
    if (!selectedDoc) {
      setError('Please select a document to export');
      return;
    }

    setIsExporting(true);
    setError(null);
    setExportUrl(null);

    try {
      const response = await axios.post('/api/financial/export-document', {
        document_id: selectedDoc,
        format: exportFormat,
        options: exportOptions
      }, {
        responseType: 'blob'
      });

      // Create a blob URL for the downloaded file
      const blob = new Blob([response.data], {
        type: getContentType(exportFormat)
      });
      const url = window.URL.createObjectURL(blob);
      setExportUrl(url);

      // Trigger download
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-${selectedDoc}.${getFileExtension(exportFormat)}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting document:', error);
      setError(error.response?.data?.detail || error.message || 'Error exporting document');
    } finally {
      setIsExporting(false);
    }
  };

  const getContentType = (format) => {
    switch (format) {
      case 'json':
        return 'application/json';
      case 'csv':
        return 'text/csv';
      case 'excel':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'pdf':
        return 'application/pdf';
      default:
        return 'application/octet-stream';
    }
  };

  const getFileExtension = (format) => {
    switch (format) {
      case 'json':
        return 'json';
      case 'csv':
        return 'csv';
      case 'excel':
        return 'xlsx';
      case 'pdf':
        return 'pdf';
      default:
        return 'txt';
    }
  };

  return (
    <SimpleFinDocUI>
      <div className="export-tool">
        <h1 className="page-title">Data Export Tool</h1>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Export Financial Data</h2>
          </div>
          <div className="card-content">
            <div className="export-options">
              <div className="option-group">
                <label className="option-label">Select Document:</label>
                <select
                  className="document-select"
                  value={selectedDoc}
                  onChange={(e) => setSelectedDoc(e.target.value)}
                >
                  <option value="">Select a document</option>
                  {documents.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.filename} ({new Date(doc.processed_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <div className="option-group">
                <label className="option-label">Export Format:</label>
                <div className="format-options">
                  <label className="format-option">
                    <input
                      type="radio"
                      name="format"
                      value="json"
                      checked={exportFormat === 'json'}
                      onChange={() => setExportFormat('json')}
                    />
                    <span>JSON</span>
                  </label>
                  <label className="format-option">
                    <input
                      type="radio"
                      name="format"
                      value="csv"
                      checked={exportFormat === 'csv'}
                      onChange={() => setExportFormat('csv')}
                    />
                    <span>CSV</span>
                  </label>
                  <label className="format-option">
                    <input
                      type="radio"
                      name="format"
                      value="excel"
                      checked={exportFormat === 'excel'}
                      onChange={() => setExportFormat('excel')}
                    />
                    <span>Excel</span>
                  </label>
                  <label className="format-option">
                    <input
                      type="radio"
                      name="format"
                      value="pdf"
                      checked={exportFormat === 'pdf'}
                      onChange={() => setExportFormat('pdf')}
                    />
                    <span>PDF</span>
                  </label>
                </div>
              </div>

              <div className="option-group">
                <label className="option-label">Include Data:</label>
                <div className="include-options">
                  <label className="include-option">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeText}
                      onChange={() => handleOptionChange('includeText')}
                    />
                    <span>Extracted Text</span>
                  </label>
                  <label className="include-option">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeTables}
                      onChange={() => handleOptionChange('includeTables')}
                    />
                    <span>Tables</span>
                  </label>
                  <label className="include-option">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeISINs}
                      onChange={() => handleOptionChange('includeISINs')}
                    />
                    <span>ISINs</span>
                  </label>
                  <label className="include-option">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeFinancialData}
                      onChange={() => handleOptionChange('includeFinancialData')}
                    />
                    <span>Financial Data</span>
                  </label>
                </div>
              </div>

              <button
                className="btn primary"
                onClick={handleExport}
                disabled={!selectedDoc || isExporting}
              >
                {isExporting ? 'Exporting...' : 'Export Data'}
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {exportUrl && (
              <div className="success-message">
                Export completed successfully! <a href={exportUrl} download>Click here</a> if the download didn't start automatically.
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Export Format Information</h2>
          </div>
          <div className="card-content">
            <div className="format-info">
              <div className="format-item">
                <h3>JSON</h3>
                <p>Exports all data in JavaScript Object Notation format. Best for developers or for importing into other systems.</p>
                <ul>
                  <li>Complete data structure</li>
                  <li>Preserves all relationships</li>
                  <li>Machine-readable</li>
                </ul>
              </div>

              <div className="format-item">
                <h3>CSV</h3>
                <p>Exports data in Comma-Separated Values format. Best for importing into spreadsheet software or data analysis tools.</p>
                <ul>
                  <li>Simple tabular format</li>
                  <li>Compatible with Excel, Google Sheets, etc.</li>
                  <li>Easy to process with data analysis tools</li>
                </ul>
              </div>

              <div className="format-item">
                <h3>Excel</h3>
                <p>Exports data in Microsoft Excel format with multiple sheets for different data types. Best for detailed analysis and reporting.</p>
                <ul>
                  <li>Multiple sheets for different data types</li>
                  <li>Formatted for readability</li>
                  <li>Includes formulas for calculations</li>
                </ul>
              </div>

              <div className="format-item">
                <h3>PDF</h3>
                <p>Exports data in a formatted PDF report. Best for sharing with others or for printing.</p>
                <ul>
                  <li>Professional report format</li>
                  <li>Includes charts and visualizations</li>
                  <li>Suitable for printing or sharing</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .export-tool {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .page-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
          overflow: hidden;
        }
        
        .card-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .card-title {
          font-size: 18px;
          font-weight: bold;
          margin: 0;
          color: #2c3e50;
        }
        
        .card-content {
          padding: 20px;
        }
        
        .export-options {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .option-group {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .option-label {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .document-select {
          padding: 10px 15px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          width: 100%;
        }
        
        .format-options, .include-options {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
        }
        
        .format-option, .include-option {
          display: flex;
          align-items: center;
          gap: 5px;
          cursor: pointer;
        }
        
        .format-option input, .include-option input {
          cursor: pointer;
        }
        
        .btn {
          padding: 10px 15px;
          border: none;
          border-radius: 4px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
          align-self: flex-start;
        }
        
        .btn.primary {
          background-color: #3498db;
          color: white;
        }
        
        .btn.primary:hover {
          background-color: #2980b9;
        }
        
        .btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        .error-message {
          padding: 10px 15px;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .success-message {
          padding: 10px 15px;
          background-color: #d4edda;
          color: #155724;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .success-message a {
          color: #155724;
          text-decoration: underline;
          font-weight: 500;
        }
        
        .format-info {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 20px;
        }
        
        .format-item {
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #3498db;
        }
        
        .format-item h3 {
          font-size: 16px;
          font-weight: 600;
          margin-top: 0;
          margin-bottom: 10px;
          color: #2c3e50;
        }
        
        .format-item p {
          margin-bottom: 10px;
          color: #495057;
        }
        
        .format-item ul {
          padding-left: 20px;
          margin: 0;
        }
        
        .format-item li {
          margin-bottom: 5px;
          color: #495057;
        }
        
        @media (max-width: 768px) {
          .format-info {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

export default DataExportTool;
