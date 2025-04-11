import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';

export default function Analysis() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isins, setIsins] = useState([]);
  const [portfolioSummary, setPortfolioSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Fetch documents on component mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch('http://localhost:24125/api/documents');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        setDocuments(data.documents || []);
      } catch (error) {
        console.error('Error fetching documents:', error);
        setError('Failed to load documents. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    const fetchPortfolioSummary = async () => {
      try {
        const response = await fetch('http://localhost:24125/api/financial/portfolio');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        setPortfolioSummary(data);
      } catch (error) {
        console.error('Error fetching portfolio summary:', error);
      }
    };

    const fetchIsins = async () => {
      try {
        const response = await fetch('http://localhost:24125/api/financial/isins');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        setIsins(data.isins || []);
      } catch (error) {
        console.error('Error fetching ISINs:', error);
      }
    };

    fetchDocuments();
    fetchPortfolioSummary();
    fetchIsins();
  }, []);

  // Handle document selection
  const handleDocumentSelect = async (documentId) => {
    setSelectedDocument(documentId);
    setAnalyzing(true);
    
    try {
      const response = await fetch(`http://localhost:24125/api/financial/document/${documentId}/isins`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setIsins(data.isins || []);
    } catch (error) {
      console.error('Error fetching document ISINs:', error);
      setError('Failed to analyze document. Please try again later.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Handle document analysis
  const handleAnalyzeDocument = async (documentId) => {
    setAnalyzing(true);
    
    try {
      const response = await fetch('http://localhost:24125/api/financial/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ document_id: documentId }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      alert(`Analysis complete: ${data.analysis.summary}`);
      
      // Refresh ISINs after analysis
      const isinsResponse = await fetch(`http://localhost:24125/api/financial/document/${documentId}/isins`);
      if (isinsResponse.ok) {
        const isinsData = await isinsResponse.json();
        setIsins(isinsData.isins || []);
      }
    } catch (error) {
      console.error('Error analyzing document:', error);
      setError('Failed to analyze document. Please try again later.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <FinDocLayout>
      <Head>
        <title>Financial Analysis | FinDoc Analyzer</title>
      </Head>

      <div className="analysis-page">
        <h1 className="page-title">Financial Analysis</h1>
        
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading financial data...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <p className="error-message">{error}</p>
            <button 
              className="retry-button"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="analysis-content">
            <div className="document-selector">
              <h2>Select Document to Analyze</h2>
              <div className="document-list">
                {documents.map((doc) => (
                  <div 
                    key={doc.id} 
                    className={`document-item ${selectedDocument === doc.id ? 'selected' : ''}`}
                    onClick={() => handleDocumentSelect(doc.id)}
                  >
                    <div className="document-icon">📄</div>
                    <div className="document-info">
                      <div className="document-title">{doc.title}</div>
                      <div className="document-meta">
                        {doc.date} • {doc.pages} pages • {doc.tags.join(', ')}
                      </div>
                    </div>
                    <button 
                      className="analyze-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAnalyzeDocument(doc.id);
                      }}
                      disabled={analyzing}
                    >
                      {analyzing && selectedDocument === doc.id ? 'Analyzing...' : 'Analyze'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="analysis-results">
              <div className="section portfolio-summary">
                <h2>Portfolio Summary</h2>
                {portfolioSummary ? (
                  <div className="summary-content">
                    <div className="summary-card">
                      <h3>Total Value</h3>
                      <div className="summary-value">{portfolioSummary.total_value}</div>
                    </div>
                    
                    <div className="summary-card">
                      <h3>Asset Allocation</h3>
                      <div className="allocation-list">
                        {Object.entries(portfolioSummary.asset_allocation).map(([asset, percentage]) => (
                          <div key={asset} className="allocation-item">
                            <span className="allocation-name">{asset}</span>
                            <span className="allocation-value">{percentage}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="summary-card">
                      <h3>Currency Allocation</h3>
                      <div className="allocation-list">
                        {Object.entries(portfolioSummary.currency_allocation).map(([currency, percentage]) => (
                          <div key={currency} className="allocation-item">
                            <span className="allocation-name">{currency}</span>
                            <span className="allocation-value">{percentage}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="no-data">No portfolio data available</p>
                )}
              </div>
              
              <div className="section isin-analysis">
                <h2>ISIN Analysis {selectedDocument ? `(Document #${selectedDocument})` : '(All Documents)'}</h2>
                {isins.length > 0 ? (
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>ISIN</th>
                          <th>Description</th>
                          <th>Value</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {isins.map((isin, index) => (
                          <tr key={index}>
                            <td>{isin.isin}</td>
                            <td>{isin.description}</td>
                            <td>{isin.value}</td>
                            <td>
                              <div className="actions">
                                <button className="action-btn view-btn" title="View Details">📊</button>
                                <button className="action-btn chart-btn" title="View Chart">📈</button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="no-data">No ISIN data available{selectedDocument ? ' for this document' : ''}</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .analysis-page {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }
        
        .page-title {
          margin: 0 0 20px 0;
          font-size: 1.8rem;
          color: #2d3748;
        }
        
        .analysis-content {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 30px;
        }
        
        .document-selector {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .document-selector h2 {
          margin-top: 0;
          margin-bottom: 20px;
          font-size: 1.25rem;
          color: #2d3748;
        }
        
        .document-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .document-item {
          display: flex;
          align-items: center;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .document-item:hover {
          border-color: #cbd5e0;
          background-color: #f7fafc;
        }
        
        .document-item.selected {
          border-color: #4299e1;
          background-color: #ebf8ff;
        }
        
        .document-icon {
          font-size: 1.5rem;
          margin-right: 15px;
        }
        
        .document-info {
          flex: 1;
        }
        
        .document-title {
          font-weight: 500;
          margin-bottom: 5px;
        }
        
        .document-meta {
          font-size: 0.8rem;
          color: #718096;
        }
        
        .analyze-button {
          background-color: #4299e1;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 8px 12px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .analyze-button:hover {
          background-color: #3182ce;
        }
        
        .analyze-button:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
        }
        
        .analysis-results {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }
        
        .section {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .section h2 {
          margin-top: 0;
          margin-bottom: 20px;
          font-size: 1.25rem;
          color: #2d3748;
        }
        
        .summary-content {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 20px;
        }
        
        .summary-card {
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          background-color: #f7fafc;
        }
        
        .summary-card h3 {
          margin: 0 0 10px 0;
          font-size: 0.9rem;
          color: #718096;
          font-weight: 500;
        }
        
        .summary-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: #2d3748;
        }
        
        .allocation-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .allocation-item {
          display: flex;
          justify-content: space-between;
          font-size: 0.9rem;
        }
        
        .allocation-name {
          color: #4a5568;
        }
        
        .allocation-value {
          font-weight: 500;
          color: #2d3748;
        }
        
        .table-container {
          overflow-x: auto;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
        }
        
        th {
          text-align: left;
          padding: 12px 15px;
          background-color: #f8fafc;
          color: #4a5568;
          font-weight: 600;
          font-size: 0.9rem;
          border-bottom: 1px solid #e2e8f0;
        }
        
        td {
          padding: 12px 15px;
          border-bottom: 1px solid #e2e8f0;
          color: #4a5568;
          font-size: 0.9rem;
        }
        
        tr:last-child td {
          border-bottom: none;
        }
        
        .actions {
          display: flex;
          gap: 5px;
        }
        
        .action-btn {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1rem;
        }
        
        .no-data {
          color: #718096;
          font-style: italic;
          padding: 20px 0;
          text-align: center;
        }
        
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 300px;
        }
        
        .loading-spinner {
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-radius: 50%;
          border-top: 4px solid #3498db;
          width: 30px;
          height: 30px;
          animation: spin 1s linear infinite;
          margin-bottom: 15px;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error-container {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          color: #c53030;
        }
        
        .retry-button {
          background-color: #3182ce;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
        }
        
        .retry-button:hover {
          background-color: #2c5282;
        }
        
        @media (max-width: 768px) {
          .analysis-content {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </FinDocLayout>
  );
}
