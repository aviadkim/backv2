import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const DocumentIntegration = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [isIntegrating, setIsIntegrating] = useState(false);
  const [integrationResults, setIntegrationResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);

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

  const handleDocumentSelect = (docId) => {
    setSelectedDocs(prev => {
      if (prev.includes(docId)) {
        return prev.filter(id => id !== docId);
      } else {
        return [...prev, docId];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedDocs.length === documents.length) {
      setSelectedDocs([]);
    } else {
      setSelectedDocs(documents.map(doc => doc.id));
    }
  };

  const handleIntegrate = async () => {
    if (selectedDocs.length < 2) {
      setError('Please select at least two documents to integrate');
      return;
    }

    setIsIntegrating(true);
    setError(null);
    setIntegrationResults(null);

    try {
      const response = await axios.post('/api/financial/integrate-documents', {
        document_ids: selectedDocs,
        options: {
          includeInsights: true
        }
      });

      setIntegrationResults(response.data);
    } catch (error) {
      console.error('Error integrating documents:', error);
      setError(error.response?.data?.detail || error.message || 'Error integrating documents');
    } finally {
      setIsIntegrating(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <SimpleFinDocUI>
      <div className="integration-tool">
        <h1 className="page-title">Document Integration</h1>

        {apiKeyStatus === 'not-configured' && (
          <div className="warning-message">
            <strong>API Key Not Configured</strong>
            <p>The OpenRouter API key is not configured. AI-enhanced insights may not be available.</p>
            <p>Please configure the API key in the settings.</p>
          </div>
        )}

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Select Documents to Integrate</h2>
          </div>
          <div className="card-content">
            <div className="document-selection">
              <div className="selection-header">
                <div className="select-all">
                  <input
                    type="checkbox"
                    id="select-all"
                    checked={selectedDocs.length === documents.length && documents.length > 0}
                    onChange={handleSelectAll}
                  />
                  <label htmlFor="select-all">Select All</label>
                </div>
                <div className="selection-count">
                  {selectedDocs.length} of {documents.length} selected
                </div>
              </div>

              <div className="documents-list">
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <div
                      key={doc.id}
                      className={`document-item ${selectedDocs.includes(doc.id) ? 'selected' : ''}`}
                      onClick={() => handleDocumentSelect(doc.id)}
                    >
                      <div className="document-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedDocs.includes(doc.id)}
                          onChange={() => {}} // Handled by the onClick on the parent div
                        />
                      </div>
                      <div className="document-icon">
                        {doc.document_type === 'portfolio' ? '📊' : '📄'}
                      </div>
                      <div className="document-details">
                        <div className="document-name">{doc.filename}</div>
                        <div className="document-info">
                          <span className="document-type">{doc.document_type}</span>
                          <span className="document-date">{formatDate(doc.processed_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-documents">
                    <p>No documents found</p>
                    <p>Please upload and process some documents first</p>
                  </div>
                )}
              </div>

              <div className="action-buttons">
                <button
                  className="btn primary"
                  onClick={handleIntegrate}
                  disabled={selectedDocs.length < 2 || isIntegrating}
                >
                  {isIntegrating ? 'Integrating...' : 'Integrate Documents'}
                </button>
              </div>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>

        {integrationResults && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Integration Results</h2>
            </div>
            <div className="card-content">
              <div className="integration-summary">
                <div className="summary-item">
                  <div className="summary-label">Documents Integrated:</div>
                  <div className="summary-value">{integrationResults.document_count}</div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Document Types:</div>
                  <div className="summary-value">{integrationResults.document_types.join(', ')}</div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Integration Strategy:</div>
                  <div className="summary-value">{formatStrategy(integrationResults.integration_strategy)}</div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Integrated At:</div>
                  <div className="summary-value">{formatDate(integrationResults.integrated_at)}</div>
                </div>
              </div>

              {integrationResults.portfolio && (
                <div className="portfolio-section">
                  <h3 className="section-title">Portfolio Overview</h3>
                  
                  <div className="portfolio-current">
                    <h4>Current Portfolio (as of {formatDate(integrationResults.portfolio.current.date)})</h4>
                    <div className="portfolio-value">
                      <div className="value-label">Portfolio Value:</div>
                      <div className="value-amount">${integrationResults.portfolio.current.portfolio_value.toLocaleString()}</div>
                    </div>
                    
                    {integrationResults.portfolio.current.asset_allocation && (
                      <div className="asset-allocation">
                        <h5>Asset Allocation</h5>
                        <div className="allocation-chart">
                          {Object.entries(integrationResults.portfolio.current.asset_allocation).map(([assetClass, allocation], index) => (
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
                  </div>
                  
                  {integrationResults.portfolio.historical && integrationResults.portfolio.historical.length > 0 && (
                    <div className="portfolio-historical">
                      <h4>Historical Portfolio Values</h4>
                      <div className="historical-chart">
                        {integrationResults.portfolio.historical.map((item, index) => (
                          <div key={index} className="historical-item">
                            <div className="historical-date">{formatDate(item.date)}</div>
                            <div className="historical-value">${item.portfolio_value.toLocaleString()}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {integrationResults.securities && integrationResults.securities.length > 0 && (
                <div className="securities-section">
                  <h3 className="section-title">Securities</h3>
                  <div className="securities-list">
                    <table className="securities-table">
                      <thead>
                        <tr>
                          <th>Security</th>
                          <th>ISIN</th>
                          <th>Current Value</th>
                          <th>Current Quantity</th>
                          <th>Current Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {integrationResults.securities.slice(0, 5).map((security, index) => (
                          <tr key={index}>
                            <td>{security.name}</td>
                            <td>{security.isin}</td>
                            <td>${security.current?.value?.toLocaleString() || 'N/A'}</td>
                            <td>{security.current?.quantity?.toLocaleString() || 'N/A'}</td>
                            <td>${security.current?.price?.toLocaleString() || 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {integrationResults.securities.length > 5 && (
                      <div className="table-more">
                        +{integrationResults.securities.length - 5} more securities
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {integrationResults.trades && (
                <div className="trades-section">
                  <h3 className="section-title">Trades</h3>
                  <div className="trades-summary">
                    <div className="summary-item">
                      <div className="summary-label">Buy Trades:</div>
                      <div className="summary-value">{integrationResults.trade_summary?.buy_count || 0}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Sell Trades:</div>
                      <div className="summary-value">{integrationResults.trade_summary?.sell_count || 0}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Total Buy Value:</div>
                      <div className="summary-value">${integrationResults.trade_summary?.total_buy_value?.toLocaleString() || 0}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Total Sell Value:</div>
                      <div className="summary-value">${integrationResults.trade_summary?.total_sell_value?.toLocaleString() || 0}</div>
                    </div>
                  </div>
                  
                  {integrationResults.trades.all && integrationResults.trades.all.length > 0 && (
                    <div className="recent-trades">
                      <h4>Recent Trades</h4>
                      <table className="trades-table">
                        <thead>
                          <tr>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Security</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {integrationResults.trades.all.slice(0, 5).map((trade, index) => (
                            <tr key={index}>
                              <td>{formatDate(trade.trade_date || trade.document_date)}</td>
                              <td className={trade.type === 'buy' ? 'buy' : 'sell'}>{trade.type}</td>
                              <td>{trade.security_name}</td>
                              <td>{trade.quantity?.toLocaleString() || 'N/A'}</td>
                              <td>${trade.price?.toLocaleString() || 'N/A'}</td>
                              <td>${trade.value?.toLocaleString() || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {integrationResults.trades.all.length > 5 && (
                        <div className="table-more">
                          +{integrationResults.trades.all.length - 5} more trades
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {integrationResults.performance && (
                <div className="performance-section">
                  <h3 className="section-title">Performance</h3>
                  <div className="performance-summary">
                    <div className="summary-item">
                      <div className="summary-label">Start Date:</div>
                      <div className="summary-value">{formatDate(integrationResults.performance.start_date)}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">End Date:</div>
                      <div className="summary-value">{formatDate(integrationResults.performance.end_date)}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Time Period:</div>
                      <div className="summary-value">{Math.round(integrationResults.performance.time_period_days)} days</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Start Value:</div>
                      <div className="summary-value">${integrationResults.performance.start_value.toLocaleString()}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">End Value:</div>
                      <div className="summary-value">${integrationResults.performance.end_value.toLocaleString()}</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Absolute Change:</div>
                      <div className={`summary-value ${integrationResults.performance.absolute_change >= 0 ? 'positive' : 'negative'}`}>
                        {integrationResults.performance.absolute_change >= 0 ? '+' : ''}
                        ${integrationResults.performance.absolute_change.toLocaleString()}
                      </div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Percentage Change:</div>
                      <div className={`summary-value ${integrationResults.performance.percentage_change >= 0 ? 'positive' : 'negative'}`}>
                        {integrationResults.performance.percentage_change >= 0 ? '+' : ''}
                        {integrationResults.performance.percentage_change.toFixed(2)}%
                      </div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Annualized Return:</div>
                      <div className={`summary-value ${integrationResults.performance.annualized_return >= 0 ? 'positive' : 'negative'}`}>
                        {integrationResults.performance.annualized_return >= 0 ? '+' : ''}
                        {integrationResults.performance.annualized_return.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {integrationResults.insights && (
                <div className="insights-section">
                  <h3 className="section-title">AI-Enhanced Insights</h3>
                  
                  <div className="insights-summary">
                    <h4>Summary</h4>
                    <p>{integrationResults.insights.summary}</p>
                  </div>
                  
                  {integrationResults.insights.key_observations && (
                    <div className="key-observations">
                      <h4>Key Observations</h4>
                      <ul className="observations-list">
                        {integrationResults.insights.key_observations.map((observation, index) => (
                          <li key={index} className="observation-item">{observation}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {integrationResults.insights.recommendations && (
                    <div className="recommendations">
                      <h4>Recommendations</h4>
                      <ul className="recommendations-list">
                        {integrationResults.insights.recommendations.map((recommendation, index) => (
                          <li key={index} className="recommendation-item">{recommendation}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .integration-tool {
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
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        
        .selection-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-bottom: 10px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .select-all {
          display: flex;
          align-items: center;
          gap: 5px;
        }
        
        .selection-count {
          font-size: 14px;
          color: #6c757d;
        }
        
        .documents-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          max-height: 400px;
          overflow-y: auto;
          padding: 10px 0;
        }
        
        .document-item {
          display: flex;
          align-items: center;
          padding: 10px;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .document-item:hover {
          background-color: #f8f9fa;
        }
        
        .document-item.selected {
          background-color: #e3f2fd;
        }
        
        .document-checkbox {
          margin-right: 10px;
        }
        
        .document-icon {
          margin-right: 10px;
          font-size: 20px;
        }
        
        .document-details {
          flex: 1;
        }
        
        .document-name {
          font-weight: 500;
          color: #2c3e50;
          margin-bottom: 5px;
        }
        
        .document-info {
          display: flex;
          gap: 15px;
          font-size: 14px;
          color: #6c757d;
        }
        
        .document-type {
          text-transform: capitalize;
        }
        
        .no-documents {
          text-align: center;
          padding: 20px;
          color: #6c757d;
        }
        
        .action-buttons {
          display: flex;
          justify-content: flex-end;
          margin-top: 15px;
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
          margin-top: 15px;
        }
        
        .integration-summary {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 15px;
          margin-bottom: 25px;
          padding-bottom: 15px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .summary-item {
          padding: 10px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .summary-label {
          font-weight: 500;
          margin-bottom: 5px;
          color: #6c757d;
        }
        
        .summary-value {
          font-size: 16px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        .section-title {
          font-size: 18px;
          font-weight: 500;
          margin: 25px 0 15px;
          padding-bottom: 10px;
          border-bottom: 1px solid #e9ecef;
          color: #2c3e50;
        }
        
        .portfolio-section, .securities-section, .trades-section, .performance-section, .insights-section {
          margin-bottom: 25px;
        }
        
        .portfolio-section h4, .securities-section h4, .trades-section h4, .performance-section h4, .insights-section h4 {
          font-size: 16px;
          font-weight: 500;
          margin: 15px 0 10px;
          color: #2c3e50;
        }
        
        .portfolio-value {
          display: flex;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .value-label {
          font-weight: 500;
          margin-right: 10px;
          color: #6c757d;
        }
        
        .value-amount {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        .asset-allocation {
          margin-bottom: 20px;
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
        
        .historical-chart {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
        }
        
        .historical-item {
          padding: 10px;
          background-color: #f8f9fa;
          border-radius: 4px;
          min-width: 150px;
        }
        
        .historical-date {
          font-weight: 500;
          margin-bottom: 5px;
          color: #6c757d;
        }
        
        .historical-value {
          font-weight: 600;
          color: #2c3e50;
        }
        
        .securities-table, .trades-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 10px;
        }
        
        .securities-table th, .securities-table td,
        .trades-table th, .trades-table td {
          padding: 10px;
          border: 1px solid #dee2e6;
          text-align: left;
        }
        
        .securities-table th, .trades-table th {
          background-color: #f1f3f5;
          font-weight: 500;
        }
        
        .table-more {
          text-align: center;
          padding: 8px;
          color: #6c757d;
          font-size: 14px;
          background-color: #f8f9fa;
          border-radius: 0 0 4px 4px;
        }
        
        .trades-summary {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }
        
        .buy {
          color: #28a745;
        }
        
        .sell {
          color: #dc3545;
        }
        
        .positive {
          color: #28a745;
        }
        
        .negative {
          color: #dc3545;
        }
        
        .insights-summary p {
          line-height: 1.6;
          color: #495057;
        }
        
        .observations-list, .recommendations-list {
          padding-left: 20px;
          margin-bottom: 20px;
        }
        
        .observation-item, .recommendation-item {
          margin-bottom: 8px;
          line-height: 1.5;
          color: #495057;
        }
        
        @media (max-width: 768px) {
          .integration-summary {
            grid-template-columns: 1fr;
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
          
          .historical-chart {
            flex-direction: column;
          }
          
          .historical-item {
            width: 100%;
          }
          
          .trades-summary {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

// Helper functions
function formatStrategy(strategy) {
  if (!strategy) return 'Unknown';
  
  return strategy
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
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

export default DocumentIntegration;
