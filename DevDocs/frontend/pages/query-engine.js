import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const QueryEngine = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState('');
  const [query, setQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResults, setQueryResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);
  const [recentQueries, setRecentQueries] = useState([]);

  // Sample queries
  const sampleQueries = [
    "What is the total portfolio value?",
    "What is the asset allocation?",
    "What are the top 5 holdings?",
    "What is the performance of the portfolio?",
    "What is the largest holding?",
    "How much cash is in the portfolio?",
    "What equities are in the portfolio?"
  ];

  // Fetch documents and API key status on component mount
  useEffect(() => {
    fetchDocuments();
    checkApiKey();
    
    // Load recent queries from localStorage
    const savedQueries = localStorage.getItem('recentQueries');
    if (savedQueries) {
      setRecentQueries(JSON.parse(savedQueries));
    }
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
      setError('Please select a document to query');
      return;
    }

    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setIsQuerying(true);
    setError(null);
    setQueryResults(null);

    try {
      const response = await axios.post('/api/financial/query-document', {
        document_id: selectedDoc,
        query: query
      });

      setQueryResults(response.data);
      
      // Save query to recent queries
      const updatedQueries = [query, ...recentQueries.filter(q => q !== query)].slice(0, 5);
      setRecentQueries(updatedQueries);
      localStorage.setItem('recentQueries', JSON.stringify(updatedQueries));
    } catch (error) {
      console.error('Error querying document:', error);
      setError(error.response?.data?.detail || error.message || 'Error querying document');
    } finally {
      setIsQuerying(false);
    }
  };

  const handleSampleQueryClick = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  const handleRecentQueryClick = (recentQuery) => {
    setQuery(recentQuery);
  };

  return (
    <SimpleFinDocUI>
      <div className="query-engine">
        <h1 className="page-title">Financial Query Engine</h1>

        {apiKeyStatus === 'not-configured' && (
          <div className="warning-message">
            <strong>API Key Not Configured</strong>
            <p>The OpenRouter API key is not configured. The query engine may not work properly.</p>
            <p>Please configure the API key in the settings.</p>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Query Financial Documents</h2>
          </div>
          <div className="card-content">
            <div className="document-selection">
              <label className="document-label">Select a document to query:</label>
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
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question about the document..."
                  rows={3}
                ></textarea>
                <button
                  type="submit"
                  className="btn primary"
                  disabled={!selectedDoc || !query.trim() || isQuerying}
                >
                  {isQuerying ? 'Querying...' : 'Submit Query'}
                </button>
              </div>
            </form>

            <div className="query-suggestions">
              {recentQueries.length > 0 && (
                <div className="recent-queries">
                  <h3 className="section-title">Recent Queries</h3>
                  <div className="queries-list">
                    {recentQueries.map((recentQuery, index) => (
                      <div
                        key={`recent-${index}`}
                        className="query-item"
                        onClick={() => handleRecentQueryClick(recentQuery)}
                      >
                        {recentQuery}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="sample-queries">
                <h3 className="section-title">Sample Queries</h3>
                <div className="queries-list">
                  {sampleQueries.map((sampleQuery, index) => (
                    <div
                      key={`sample-${index}`}
                      className="query-item"
                      onClick={() => handleSampleQueryClick(sampleQuery)}
                    >
                      {sampleQuery}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>

        {queryResults && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Query Results</h2>
            </div>
            <div className="card-content">
              <div className="results-container">
                <div className="query-summary">
                  <div className="query-label">Your Query:</div>
                  <div className="query-text">{queryResults.query}</div>
                  {queryResults.confidence && (
                    <div className="confidence-indicator">
                      <div className="confidence-label">Confidence:</div>
                      <div className="confidence-bar-container">
                        <div 
                          className="confidence-bar" 
                          style={{ 
                            width: `${queryResults.confidence * 100}%`,
                            backgroundColor: getConfidenceColor(queryResults.confidence)
                          }}
                        ></div>
                        <div className="confidence-value">{(queryResults.confidence * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="response-content">
                  <div className="response-text" dangerouslySetInnerHTML={{ __html: formatResponse(queryResults.response) }}></div>
                </div>

                {queryResults.data && (
                  <div className="supporting-data">
                    <h3 className="section-title">Supporting Data</h3>
                    
                    {queryResults.data.portfolio_value && (
                      <div className="data-item">
                        <div className="data-label">Portfolio Value:</div>
                        <div className="data-value">${queryResults.data.portfolio_value.toLocaleString()}</div>
                      </div>
                    )}
                    
                    {queryResults.data.asset_allocation && (
                      <div className="data-section">
                        <h4>Asset Allocation</h4>
                        <div className="allocation-chart">
                          {Object.entries(queryResults.data.asset_allocation).map(([assetClass, allocation], index) => (
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
                    
                    {queryResults.data.top_holdings && (
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
                            {queryResults.data.top_holdings.map((holding, index) => (
                              <tr key={index}>
                                <td>{holding.name}</td>
                                <td>{holding.isin}</td>
                                <td>${holding.value.toLocaleString()}</td>
                                <td>{((holding.value / (queryResults.data.portfolio_value || 1950000)) * 100).toFixed(2)}%</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    
                    {queryResults.data.largest_holding && (
                      <div className="data-section">
                        <h4>Largest Holding</h4>
                        <div className="holding-details">
                          <div className="holding-name">{queryResults.data.largest_holding.name}</div>
                          <div className="holding-isin">{queryResults.data.largest_holding.isin}</div>
                          <div className="holding-value">${queryResults.data.largest_holding.value.toLocaleString()}</div>
                          <div className="holding-percentage">
                            {((queryResults.data.largest_holding.value / (queryResults.data.portfolio_value || 1950000)) * 100).toFixed(2)}% of portfolio
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {queryResults.data.performance && (
                      <div className="data-section">
                        <h4>Performance</h4>
                        <table className="performance-table">
                          <thead>
                            <tr>
                              <th>Period</th>
                              <th>Return</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(queryResults.data.performance).map(([period, value], index) => (
                              <tr key={index}>
                                <td>{formatPeriod(period)}</td>
                                <td className={value >= 0 ? 'positive' : 'negative'}>
                                  {(value * 100).toFixed(2)}%
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
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
        .query-engine {
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
        
        .query-suggestions {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .recent-queries, .sample-queries {
          margin-top: 10px;
        }
        
        .section-title {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 10px;
          color: #2c3e50;
        }
        
        .queries-list {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }
        
        .query-item {
          padding: 8px 12px;
          background-color: #f8f9fa;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          font-size: 14px;
        }
        
        .query-item:hover {
          background-color: #e9ecef;
        }
        
        .error-message {
          padding: 10px 15px;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .results-container {
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
          margin-bottom: 10px;
        }
        
        .confidence-indicator {
          display: flex;
          align-items: center;
          margin-top: 10px;
        }
        
        .confidence-label {
          font-weight: 500;
          margin-right: 10px;
          color: #6c757d;
          min-width: 80px;
        }
        
        .confidence-bar-container {
          flex: 1;
          height: 10px;
          background-color: #e9ecef;
          border-radius: 5px;
          position: relative;
          overflow: hidden;
        }
        
        .confidence-bar {
          height: 100%;
          border-radius: 5px;
        }
        
        .confidence-value {
          margin-left: 10px;
          font-weight: 500;
          color: #6c757d;
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
          color: #fff;
          text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
        }
        
        .holdings-table, .performance-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .holdings-table th, .holdings-table td,
        .performance-table th, .performance-table td {
          padding: 10px;
          border: 1px solid #dee2e6;
          text-align: left;
        }
        
        .holdings-table th, .performance-table th {
          background-color: #f1f3f5;
          font-weight: 500;
        }
        
        .holding-details {
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .holding-name {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 5px;
        }
        
        .holding-isin {
          font-size: 14px;
          color: #6c757d;
          margin-bottom: 10px;
        }
        
        .holding-value {
          font-size: 16px;
          font-weight: 500;
          color: #2c3e50;
          margin-bottom: 5px;
        }
        
        .holding-percentage {
          font-size: 14px;
          color: #6c757d;
        }
        
        .positive {
          color: #28a745;
        }
        
        .negative {
          color: #dc3545;
        }
        
        @media (max-width: 768px) {
          .query-input-container {
            flex-direction: column;
          }
          
          .btn {
            align-self: stretch;
          }
          
          .confidence-indicator {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .confidence-label {
            margin-bottom: 5px;
          }
          
          .allocation-bar-container {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .allocation-label {
            margin-bottom: 5px;
          }
          
          .allocation-bar {
            width: 100%;
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

function getConfidenceColor(confidence) {
  if (confidence >= 0.9) {
    return '#2ecc71'; // Green
  } else if (confidence >= 0.7) {
    return '#f39c12'; // Orange
  } else {
    return '#e74c3c'; // Red
  }
}

function formatPeriod(period) {
  switch (period) {
    case 'ytd':
      return 'Year-to-Date';
    case 'one_year':
      return 'One Year';
    case 'three_year':
      return 'Three Years';
    case 'five_year':
      return 'Five Years';
    default:
      return period.charAt(0).toUpperCase() + period.slice(1).replace(/_/g, ' ');
  }
}

export default QueryEngine;
