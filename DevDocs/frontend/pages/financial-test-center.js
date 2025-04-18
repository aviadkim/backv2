import React, { useState } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const FinancialTestCenter = () => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [apiKeyStatus, setApiKeyStatus] = useState(null);

  // Agent selection state
  const [selectedAgents, setSelectedAgents] = useState({
    documentPreprocessor: true,
    hebrewOCR: false,
    isinExtractor: true,
    financialTableDetector: true,
    financialDataAnalyzer: true,
    documentIntegration: false,
    queryEngine: false
  });

  // Document type selection
  const [documentType, setDocumentType] = useState('financial');

  // Fetch API key on component mount
  React.useEffect(() => {
    const fetchApiKey = async () => {
      try {
        const response = await axios.get('/api/config/api-key');
        if (response.data && response.data.key) {
          setApiKey(response.data.key);
          setApiKeyStatus('loaded');
        }
      } catch (error) {
        console.error('Error fetching API key:', error);
        setApiKeyStatus('error');
      }
    };

    fetchApiKey();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResults(null);
      setError(null);
    }
  };

  const handleProcessFile = async () => {
    if (!file) {
      setError('Please select a file to process');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResults(null);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);

      // Add selected agents to form data
      formData.append('agents', JSON.stringify(selectedAgents));

      // Process the file
      const response = await axios.post('/api/financial/process-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResults(response.data);
    } catch (error) {
      console.error('Error processing file:', error);
      setError(error.response?.data?.detail || error.message || 'Error processing file');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAgentToggle = (agentName) => {
    setSelectedAgents(prev => ({
      ...prev,
      [agentName]: !prev[agentName]
    }));
  };

  const handleDocumentTypeChange = (e) => {
    setDocumentType(e.target.value);
  };

  const handleTestApiKey = async () => {
    try {
      setApiKeyStatus('testing');
      const response = await axios.post('/api/config/test-api-key');
      setApiKeyStatus(response.data.success ? 'valid' : 'invalid');
    } catch (error) {
      console.error('Error testing API key:', error);
      setApiKeyStatus('error');
    }
  };

  return (
    <SimpleFinDocUI>
      <div className="test-center">
        <h1 className="page-title">Financial Document Testing Center</h1>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">API Key Status</h2>
          </div>
          <div className="card-content">
            <div className="api-key-status">
              <div className="status-label">OpenRouter API Key:</div>
              <div className={`status-value ${apiKeyStatus}`}>
                {apiKeyStatus === 'loaded' && apiKey}
                {apiKeyStatus === 'testing' && 'Testing...'}
                {apiKeyStatus === 'valid' && 'Valid'}
                {apiKeyStatus === 'invalid' && 'Invalid'}
                {apiKeyStatus === 'error' && 'Error loading key'}
                {!apiKeyStatus && 'Not loaded'}
              </div>
              <button
                className="btn primary"
                onClick={handleTestApiKey}
                disabled={apiKeyStatus === 'testing'}
              >
                Test API Key
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Process Financial Document</h2>
          </div>
          <div className="card-content">
            <div className="document-options">
              <div className="option-group">
                <label className="option-label">Document Type:</label>
                <select
                  className="document-type-select"
                  value={documentType}
                  onChange={handleDocumentTypeChange}
                >
                  <option value="financial">Financial Statement</option>
                  <option value="portfolio">Portfolio Report</option>
                  <option value="trade">Trade Confirmation</option>
                  <option value="account">Account Statement</option>
                </select>
              </div>
            </div>

            <div className="agent-selection">
              <h3 className="section-title">Processing Agents</h3>
              <div className="agent-grid">
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="documentPreprocessor"
                    checked={selectedAgents.documentPreprocessor}
                    onChange={() => handleAgentToggle('documentPreprocessor')}
                  />
                  <label htmlFor="documentPreprocessor">Document Preprocessor</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="hebrewOCR"
                    checked={selectedAgents.hebrewOCR}
                    onChange={() => handleAgentToggle('hebrewOCR')}
                  />
                  <label htmlFor="hebrewOCR">Hebrew OCR</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="isinExtractor"
                    checked={selectedAgents.isinExtractor}
                    onChange={() => handleAgentToggle('isinExtractor')}
                  />
                  <label htmlFor="isinExtractor">ISIN Extractor</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="financialTableDetector"
                    checked={selectedAgents.financialTableDetector}
                    onChange={() => handleAgentToggle('financialTableDetector')}
                  />
                  <label htmlFor="financialTableDetector">Financial Table Detector</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="financialDataAnalyzer"
                    checked={selectedAgents.financialDataAnalyzer}
                    onChange={() => handleAgentToggle('financialDataAnalyzer')}
                  />
                  <label htmlFor="financialDataAnalyzer">Financial Data Analyzer</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="documentIntegration"
                    checked={selectedAgents.documentIntegration}
                    onChange={() => handleAgentToggle('documentIntegration')}
                  />
                  <label htmlFor="documentIntegration">Document Integration</label>
                </div>
                <div className="agent-option">
                  <input
                    type="checkbox"
                    id="queryEngine"
                    checked={selectedAgents.queryEngine}
                    onChange={() => handleAgentToggle('queryEngine')}
                  />
                  <label htmlFor="queryEngine">Query Engine</label>
                </div>
              </div>
            </div>

            <div className="file-upload">
              <input
                type="file"
                id="file-upload"
                onChange={handleFileChange}
                accept=".pdf,.xlsx,.csv"
              />
              <label htmlFor="file-upload" className="file-upload-label">
                {file ? file.name : 'Choose a file'}
              </label>
              <button
                className="btn primary"
                onClick={handleProcessFile}
                disabled={!file || isProcessing}
              >
                {isProcessing ? 'Processing...' : 'Process Document'}
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {results && (
              <div className="results">
                <h3>Processing Results</h3>

                {results.tables && results.tables.length > 0 && (
                  <div className="result-section">
                    <h4>Detected Tables ({results.tables.length})</h4>
                    {results.tables.map((table, index) => (
                      <div key={index} className="table-result">
                        <h5>Table {index + 1}</h5>
                        <div className="table-info">
                          <div>Page: {table.page || 'N/A'}</div>
                          <div>Headers: {table.headers?.length || 0}</div>
                          <div>Rows: {table.rows?.length || 0}</div>
                        </div>

                        {table.headers && table.rows && (
                          <div className="table-preview">
                            <table>
                              <thead>
                                <tr>
                                  {table.headers.map((header, i) => (
                                    <th key={i}>{header}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {table.rows.slice(0, 5).map((row, rowIndex) => (
                                  <tr key={rowIndex}>
                                    {row.map((cell, cellIndex) => (
                                      <td key={cellIndex}>{cell}</td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {table.rows.length > 5 && (
                              <div className="table-more">
                                +{table.rows.length - 5} more rows
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {results.entities && results.entities.isin && results.entities.isin.length > 0 && (
                  <div className="result-section">
                    <h4>Detected ISINs ({results.entities.isin.length})</h4>
                    <ul className="isin-list">
                      {results.entities.isin.map((isin, index) => (
                        <li key={index} className="isin-item">
                          <span className="isin-code">{isin.code}</span>
                          {isin.name && <span className="isin-name">{isin.name}</span>}
                          {isin.value && <span className="isin-value">${isin.value.toLocaleString()}</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {results.financial_data && (
                  <div className="result-section">
                    <h4>Financial Data</h4>
                    <div className="financial-data">
                      {results.financial_data.portfolio_value && (
                        <div className="data-item">
                          <div className="data-label">Portfolio Value:</div>
                          <div className="data-value">${results.financial_data.portfolio_value.toLocaleString()}</div>
                        </div>
                      )}

                      {results.financial_data.asset_allocation && (
                        <div className="data-item">
                          <div className="data-label">Asset Allocation:</div>
                          <div className="data-value">
                            <ul className="allocation-list">
                              {Object.entries(results.financial_data.asset_allocation).map(([key, value]) => (
                                <li key={key}>
                                  {key}: {typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : value}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}

                      {results.financial_data.securities && results.financial_data.securities.length > 0 && (
                        <div className="data-item">
                          <div className="data-label">Securities:</div>
                          <div className="data-value">
                            <table className="securities-table">
                              <thead>
                                <tr>
                                  <th>Name</th>
                                  <th>ISIN</th>
                                  <th>Value</th>
                                  <th>Quantity</th>
                                </tr>
                              </thead>
                              <tbody>
                                {results.financial_data.securities.map((security, index) => (
                                  <tr key={index}>
                                    <td>{security.name}</td>
                                    <td>{security.isin}</td>
                                    <td>${security.value?.toLocaleString() || 'N/A'}</td>
                                    <td>{security.quantity?.toLocaleString() || 'N/A'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="result-section">
                  <h4>Raw Results</h4>
                  <pre className="json-output">{JSON.stringify(results, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .test-center {
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

        .api-key-status {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .status-label {
          font-weight: 500;
          min-width: 150px;
        }

        .status-value {
          padding: 5px 10px;
          border-radius: 4px;
          font-family: monospace;
        }

        .status-value.loaded {
          background-color: #e2f2ff;
          color: #0366d6;
        }

        .status-value.valid {
          background-color: #d4edda;
          color: #155724;
        }

        .status-value.invalid {
          background-color: #f8d7da;
          color: #721c24;
        }

        .status-value.error {
          background-color: #f8d7da;
          color: #721c24;
        }

        .status-value.testing {
          background-color: #fff3cd;
          color: #856404;
        }

        .file-upload {
          display: flex;
          align-items: center;
          gap: 15px;
          margin-bottom: 20px;
        }

        .file-upload input[type="file"] {
          display: none;
        }

        .file-upload-label {
          padding: 10px 15px;
          background-color: #f8f9fa;
          border: 1px solid #ced4da;
          border-radius: 4px;
          cursor: pointer;
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .document-options {
          margin-bottom: 20px;
        }

        .option-group {
          display: flex;
          align-items: center;
          margin-bottom: 10px;
        }

        .option-label {
          font-weight: 500;
          margin-right: 10px;
          min-width: 120px;
        }

        .document-type-select {
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          background-color: #fff;
          min-width: 200px;
        }

        .section-title {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
        }

        .agent-selection {
          margin-bottom: 20px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }

        .agent-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 10px;
        }

        .agent-option {
          display: flex;
          align-items: center;
          padding: 8px;
          border-radius: 4px;
          transition: background-color 0.2s ease;
        }

        .agent-option:hover {
          background-color: #e9ecef;
        }

        .agent-option input[type="checkbox"] {
          margin-right: 10px;
        }

        .agent-option label {
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
          margin-bottom: 20px;
        }

        .results {
          margin-top: 20px;
        }

        .results h3 {
          font-size: 18px;
          margin-bottom: 15px;
          color: #2c3e50;
        }

        .result-section {
          margin-bottom: 25px;
          padding-bottom: 25px;
          border-bottom: 1px solid #e9ecef;
        }

        .result-section h4 {
          font-size: 16px;
          margin-bottom: 15px;
          color: #2c3e50;
        }

        .table-result {
          margin-bottom: 20px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }

        .table-result h5 {
          font-size: 14px;
          margin-top: 0;
          margin-bottom: 10px;
          color: #2c3e50;
        }

        .table-info {
          display: flex;
          gap: 15px;
          margin-bottom: 10px;
          font-size: 14px;
          color: #6c757d;
        }

        .table-preview {
          overflow-x: auto;
          margin-top: 15px;
        }

        .table-preview table {
          width: 100%;
          border-collapse: collapse;
        }

        .table-preview th, .table-preview td {
          padding: 8px 12px;
          border: 1px solid #dee2e6;
          text-align: left;
        }

        .table-preview th {
          background-color: #f1f3f5;
          font-weight: 500;
        }

        .table-more {
          text-align: center;
          padding: 8px;
          color: #6c757d;
          font-size: 14px;
        }

        .isin-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .isin-item {
          display: flex;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #e9ecef;
        }

        .isin-item:last-child {
          border-bottom: none;
        }

        .isin-code {
          font-family: monospace;
          font-weight: 500;
          margin-right: 15px;
          min-width: 120px;
        }

        .isin-name {
          flex: 1;
          color: #495057;
        }

        .isin-value {
          font-weight: 500;
          color: #2c3e50;
        }

        .financial-data {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .data-item {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .data-label {
          font-weight: 500;
          color: #495057;
        }

        .allocation-list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .allocation-list li {
          padding: 5px 10px;
          background-color: #e9ecef;
          border-radius: 4px;
          font-size: 14px;
        }

        .securities-table {
          width: 100%;
          border-collapse: collapse;
        }

        .securities-table th, .securities-table td {
          padding: 8px 12px;
          border: 1px solid #dee2e6;
          text-align: left;
        }

        .securities-table th {
          background-color: #f1f3f5;
          font-weight: 500;
        }

        .json-output {
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 4px;
          overflow: auto;
          font-family: monospace;
          font-size: 14px;
          max-height: 400px;
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

export default FinancialTestCenter;
