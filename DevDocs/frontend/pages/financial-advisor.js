import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const FinancialAdvisorTool = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [queryInput, setQueryInput] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [advisorResponse, setAdvisorResponse] = useState(null);
  const [error, setError] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);

  // Sample questions
  const sampleQuestions = [
    "What is my portfolio's asset allocation?",
    "What are my top 5 holdings by value?",
    "How diversified is my portfolio?",
    "What is my exposure to technology stocks?",
    "What recommendations do you have to improve my portfolio?",
    "What is my portfolio's risk level?",
    "How can I reduce my portfolio's volatility?",
    "What tax optimization strategies would you recommend?",
    "Should I rebalance my portfolio?"
  ];

  // Fetch documents and API key status on component mount
  useEffect(() => {
    fetchDocuments();
    checkApiKey();
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

  const checkApiKey = async () => {
    try {
      const response = await axios.get('/api/config/api-key');
      setApiKeyStatus(response.data.isConfigured ? 'configured' : 'not-configured');
    } catch (error) {
      console.error('Error checking API key:', error);
      setApiKeyStatus('error');
    }
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedDoc) {
      setError('Please select a document to analyze');
      return;
    }

    if (!queryInput.trim()) {
      setError('Please enter a question');
      return;
    }

    setIsQuerying(true);
    setError(null);
    setAdvisorResponse(null);

    try {
      const response = await axios.post('/api/financial/advisor', {
        document_id: selectedDoc,
        query: queryInput
      });

      setAdvisorResponse(response.data);
    } catch (error) {
      console.error('Error querying advisor:', error);
      setError(error.response?.data?.detail || error.message || 'Error querying advisor');
    } finally {
      setIsQuerying(false);
    }
  };

  const handleSampleQuestionClick = (question) => {
    setQueryInput(question);
  };

  return (
    <SimpleFinDocUI>
      <div className="advisor-tool">
        <h1 className="page-title">Financial Advisor</h1>

        {apiKeyStatus === 'not-configured' && (
          <div className="warning-message">
            <strong>API Key Not Configured</strong>
            <p>The OpenRouter API key is not configured. The financial advisor may not work properly.</p>
            <p>Please configure the API key in the settings.</p>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Ask Your Financial Advisor</h2>
          </div>
          <div className="card-content">
            <div className="document-selection">
              <label className="document-label">Select a document to analyze:</label>
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

            <form onSubmit={handleQuerySubmit} className="query-form">
              <div className="query-input-container">
                <textarea
                  className="query-input"
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  placeholder="Ask a question about your portfolio..."
                  rows={3}
                ></textarea>
                <button
                  type="submit"
                  className="btn primary"
                  disabled={!selectedDoc || !queryInput.trim() || isQuerying}
                >
                  {isQuerying ? 'Analyzing...' : 'Ask Advisor'}
                </button>
              </div>
            </form>

            <div className="sample-questions">
              <h3 className="section-title">Sample Questions</h3>
              <div className="questions-grid">
                {sampleQuestions.map((question, index) => (
                  <div
                    key={index}
                    className="question-item"
                    onClick={() => handleSampleQuestionClick(question)}
                  >
                    {question}
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>

        {advisorResponse && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Advisor Response</h2>
            </div>
            <div className="card-content">
              <div className="response-container">
                <div className="query-summary">
                  <div className="query-label">Your Question:</div>
                  <div className="query-text">{advisorResponse.query}</div>
                </div>

                <div className="response-content">
                  <div className="response-text" dangerouslySetInnerHTML={{ __html: formatResponse(advisorResponse.response) }}></div>
                </div>

                {advisorResponse.data && (
                  <div className="supporting-data">
                    <h3 className="section-title">Supporting Data</h3>
                    
                    {advisorResponse.data.portfolio_value && (
                      <div className="data-item">
                        <div className="data-label">Portfolio Value:</div>
                        <div className="data-value">${advisorResponse.data.portfolio_value.toLocaleString()}</div>
                      </div>
                    )}
                    
                    {advisorResponse.data.asset_allocation && (
                      <div className="data-section">
                        <h4>Asset Allocation</h4>
                        <div className="allocation-chart">
                          {Object.entries(advisorResponse.data.asset_allocation).map(([assetClass, allocation], index) => (
                            <div key={index} className="allocation-bar-container">
                              <div className="allocation-label">{assetClass}</div>
                              <div className="allocation-bar">
                                <div
                                  className="allocation-fill"
                                  style={{
                                    width: `${allocation * 100}%`,
                                    backgroundColor: getColorForIndex(index)
                                  }}
                                ></div>
                                <div className="allocation-percentage">{(allocation * 100).toFixed(1)}%</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {advisorResponse.data.top_holdings && (
                      <div className="data-section">
                        <h4>Top Holdings</h4>
                        <table className="holdings-table">
                          <thead>
                            <tr>
                              <th>Security</th>
                              <th>ISIN</th>
                              <th>Value</th>
                              <th>% of Portfolio</th>
                            </tr>
                          </thead>
                          <tbody>
                            {advisorResponse.data.top_holdings.map((holding, index) => (
                              <tr key={index}>
                                <td>{holding.name}</td>
                                <td>{holding.isin}</td>
                                <td>${holding.value.toLocaleString()}</td>
                                <td>{((holding.value / advisorResponse.data.portfolio_value) * 100).toFixed(2)}%</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    
                    {advisorResponse.data.metrics && (
                      <div className="data-section">
                        <h4>Portfolio Metrics</h4>
                        <div className="metrics-grid">
                          {Object.entries(advisorResponse.data.metrics).map(([metric, value], index) => (
                            <div key={index} className="metric-item">
                              <div className="metric-label">{formatMetricName(metric)}</div>
                              <div className="metric-value">{formatMetricValue(metric, value)}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .advisor-tool {
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
        
        .document-selection {
          margin-bottom: 20px;
        }
        
        .document-label {
          display: block;
          font-weight: 500;
          margin-bottom: 8px;
          color: #2c3e50;
        }
        
        .document-select {
          width: 100%;
          padding: 10px 15px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 16px;
        }
        
        .query-form {
          margin-bottom: 20px;
        }
        
        .query-input-container {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .query-input {
          width: 100%;
          padding: 12px 15px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 16px;
          resize: vertical;
        }
        
        .btn {
          padding: 10px 15px;
          border: none;
          border-radius: 4px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
          align-self: flex-end;
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
        
        .sample-questions {
          margin-top: 25px;
        }
        
        .section-title {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
        }
        
        .questions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 10px;
        }
        
        .question-item {
          padding: 10px 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          border-left: 3px solid #3498db;
        }
        
        .question-item:hover {
          background-color: #e9ecef;
        }
        
        .error-message {
          padding: 10px 15px;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .warning-message {
          padding: 15px;
          background-color: #fff3cd;
          color: #856404;
          border-radius: 4px;
          margin-bottom: 20px;
        }
        
        .warning-message strong {
          display: block;
          margin-bottom: 5px;
        }
        
        .warning-message p {
          margin: 5px 0;
        }
        
        .response-container {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .query-summary {
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #3498db;
        }
        
        .query-label {
          font-weight: 500;
          margin-bottom: 5px;
          color: #6c757d;
        }
        
        .query-text {
          font-size: 18px;
          color: #2c3e50;
        }
        
        .response-content {
          padding: 20px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #28a745;
        }
        
        .response-text {
          line-height: 1.6;
          color: #2c3e50;
        }
        
        .response-text p {
          margin-bottom: 15px;
        }
        
        .response-text ul, .response-text ol {
          margin-bottom: 15px;
          padding-left: 20px;
        }
        
        .response-text li {
          margin-bottom: 5px;
        }
        
        .supporting-data {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e9ecef;
        }
        
        .data-item {
          display: flex;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .data-label {
          font-weight: 500;
          min-width: 150px;
          color: #6c757d;
        }
        
        .data-value {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        .data-section {
          margin-bottom: 25px;
        }
        
        .data-section h4 {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
          padding-bottom: 5px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .allocation-chart {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .allocation-bar-container {
          display: flex;
          align-items: center;
        }
        
        .allocation-label {
          min-width: 150px;
          font-weight: 500;
          color: #495057;
        }
        
        .allocation-bar {
          flex: 1;
          height: 25px;
          background-color: #e9ecef;
          border-radius: 4px;
          position: relative;
          overflow: hidden;
        }
        
        .allocation-fill {
          height: 100%;
          border-radius: 4px;
        }
        
        .allocation-percentage {
          position: absolute;
          right: 10px;
          top: 50%;
          transform: translateY(-50%);
          font-weight: 500;
          color: #495057;
        }
        
        .holdings-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .holdings-table th, .holdings-table td {
          padding: 10px;
          border: 1px solid #dee2e6;
          text-align: left;
        }
        
        .holdings-table th {
          background-color: #f1f3f5;
          font-weight: 500;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
        }
        
        .metric-item {
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 3px solid #6c757d;
        }
        
        .metric-label {
          font-weight: 500;
          margin-bottom: 5px;
          color: #6c757d;
        }
        
        .metric-value {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        @media (max-width: 768px) {
          .query-input-container {
            flex-direction: column;
          }
          
          .btn {
            align-self: stretch;
          }
          
          .questions-grid {
            grid-template-columns: 1fr;
          }
          
          .metrics-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

// Helper functions
function formatResponse(response) {
  // Convert markdown-like syntax to HTML
  let formatted = response
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Wrap in paragraph tags if not already
  if (!formatted.startsWith('<p>')) {
    formatted = '<p>' + formatted;
  }
  if (!formatted.endsWith('</p>')) {
    formatted = formatted + '</p>';
  }
  
  return formatted;
}

function getColorForIndex(index) {
  const colors = [
    '#3498db', // Blue
    '#2ecc71', // Green
    '#e74c3c', // Red
    '#f39c12', // Orange
    '#9b59b6', // Purple
    '#1abc9c', // Teal
    '#d35400', // Dark Orange
    '#34495e', // Navy
    '#7f8c8d', // Gray
    '#2c3e50'  // Dark Blue
  ];
  
  return colors[index % colors.length];
}

function formatMetricName(metric) {
  // Convert camelCase or snake_case to Title Case with spaces
  return metric
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

function formatMetricValue(metric, value) {
  // Format different types of metrics appropriately
  if (metric.includes('ratio') || metric.includes('percentage') || metric.includes('rate')) {
    return (value * 100).toFixed(2) + '%';
  } else if (metric.includes('score')) {
    return value.toFixed(2);
  } else if (typeof value === 'number') {
    return value.toLocaleString();
  } else {
    return value;
  }
}

export default FinancialAdvisorTool;
