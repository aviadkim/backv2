import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const DocumentComparisonTool = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc1, setSelectedDoc1] = useState('');
  const [selectedDoc2, setSelectedDoc2] = useState('');
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
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

  const handleCompare = async () => {
    if (!selectedDoc1 || !selectedDoc2) {
      setError('Please select two documents to compare');
      return;
    }

    if (selectedDoc1 === selectedDoc2) {
      setError('Please select two different documents to compare');
      return;
    }

    setIsComparing(true);
    setError(null);
    setComparisonResults(null);

    try {
      const response = await axios.post('/api/financial/compare-documents', {
        document1_id: selectedDoc1,
        document2_id: selectedDoc2
      });

      setComparisonResults(response.data);
    } catch (error) {
      console.error('Error comparing documents:', error);
      setError(error.response?.data?.detail || error.message || 'Error comparing documents');
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <SimpleFinDocUI>
      <div className="comparison-tool">
        <h1 className="page-title">Document Comparison Tool</h1>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Select Documents to Compare</h2>
          </div>
          <div className="card-content">
            <div className="document-selection">
              <div className="document-select-group">
                <label className="document-select-label">First Document:</label>
                <select
                  className="document-select"
                  value={selectedDoc1}
                  onChange={(e) => setSelectedDoc1(e.target.value)}
                >
                  <option value="">Select a document</option>
                  {documents.map((doc) => (
                    <option key={`doc1-${doc.id}`} value={doc.id}>
                      {doc.filename} ({new Date(doc.processed_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <div className="document-select-group">
                <label className="document-select-label">Second Document:</label>
                <select
                  className="document-select"
                  value={selectedDoc2}
                  onChange={(e) => setSelectedDoc2(e.target.value)}
                >
                  <option value="">Select a document</option>
                  {documents.map((doc) => (
                    <option key={`doc2-${doc.id}`} value={doc.id}>
                      {doc.filename} ({new Date(doc.processed_at).toLocaleDateString()})
                    </option>
                  ))}
                </select>
              </div>

              <button
                className="btn primary"
                onClick={handleCompare}
                disabled={!selectedDoc1 || !selectedDoc2 || isComparing}
              >
                {isComparing ? 'Comparing...' : 'Compare Documents'}
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>

        {comparisonResults && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Comparison Results</h2>
            </div>
            <div className="card-content">
              <div className="comparison-summary">
                <h3 className="section-title">Summary</h3>
                <div className="summary-text">
                  {comparisonResults.summary?.summary || 'No summary available'}
                </div>

                {comparisonResults.summary?.highlights && comparisonResults.summary.highlights.length > 0 && (
                  <div className="highlights">
                    <h4>Key Highlights</h4>
                    <ul className="highlights-list">
                      {comparisonResults.summary.highlights.map((highlight, index) => (
                        <li key={index} className="highlight-item">{highlight}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="comparison-details">
                <h3 className="section-title">Portfolio Value</h3>
                <div className="comparison-value-change">
                  <div className="value-item">
                    <div className="value-label">First Document:</div>
                    <div className="value-amount">${comparisonResults.portfolio_comparison.doc1_value?.toLocaleString() || 'N/A'}</div>
                  </div>
                  <div className="value-item">
                    <div className="value-label">Second Document:</div>
                    <div className="value-amount">${comparisonResults.portfolio_comparison.doc2_value?.toLocaleString() || 'N/A'}</div>
                  </div>
                  <div className="value-change">
                    <div className="value-label">Change:</div>
                    <div className={`value-amount ${comparisonResults.portfolio_comparison.direction === 'increase' ? 'positive' : 'negative'}`}>
                      {comparisonResults.portfolio_comparison.direction === 'increase' ? '+' : ''}
                      ${comparisonResults.portfolio_comparison.absolute_difference?.toLocaleString() || 'N/A'}
                      {' '}
                      ({comparisonResults.portfolio_comparison.direction === 'increase' ? '+' : ''}
                      {comparisonResults.portfolio_comparison.percentage_difference?.toFixed(2) || 'N/A'}%)
                    </div>
                  </div>
                </div>
              </div>

              {comparisonResults.allocation_comparison.has_changes && (
                <div className="comparison-section">
                  <h3 className="section-title">Asset Allocation Changes</h3>
                  
                  {comparisonResults.allocation_comparison.changes.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>Changed Allocations</h4>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>Asset Class</th>
                            <th>First Document</th>
                            <th>Second Document</th>
                            <th>Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonResults.allocation_comparison.changes.map((change, index) => (
                            <tr key={index}>
                              <td>{change.asset_class}</td>
                              <td>{(change.doc1_value * 100).toFixed(2)}%</td>
                              <td>{(change.doc2_value * 100).toFixed(2)}%</td>
                              <td className={change.direction === 'increase' ? 'positive' : 'negative'}>
                                {change.direction === 'increase' ? '+' : ''}
                                {change.percentage_difference.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  
                  {comparisonResults.allocation_comparison.additions.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>New Asset Classes</h4>
                      <ul className="addition-list">
                        {comparisonResults.allocation_comparison.additions.map((addition, index) => (
                          <li key={index} className="addition-item">
                            <span className="addition-name">{addition.asset_class}</span>
                            <span className="addition-value">{(addition.value * 100).toFixed(2)}%</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {comparisonResults.allocation_comparison.removals.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>Removed Asset Classes</h4>
                      <ul className="removal-list">
                        {comparisonResults.allocation_comparison.removals.map((removal, index) => (
                          <li key={index} className="removal-item">
                            <span className="removal-name">{removal.asset_class}</span>
                            <span className="removal-value">{(removal.value * 100).toFixed(2)}%</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {comparisonResults.securities_comparison.has_changes && (
                <div className="comparison-section">
                  <h3 className="section-title">Securities Changes</h3>
                  
                  <div className="securities-summary">
                    <div className="summary-item">
                      <div className="summary-label">First Document:</div>
                      <div className="summary-value">{comparisonResults.securities_comparison.total_securities.doc1} securities</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Second Document:</div>
                      <div className="summary-value">{comparisonResults.securities_comparison.total_securities.doc2} securities</div>
                    </div>
                    <div className="summary-item">
                      <div className="summary-label">Difference:</div>
                      <div className="summary-value">
                        {comparisonResults.securities_comparison.total_securities.difference > 0 ? '+' : ''}
                        {comparisonResults.securities_comparison.total_securities.difference} securities
                      </div>
                    </div>
                  </div>
                  
                  {comparisonResults.securities_comparison.changes.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>Changed Securities ({comparisonResults.securities_comparison.changes.length})</h4>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>Security</th>
                            <th>First Value</th>
                            <th>Second Value</th>
                            <th>Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonResults.securities_comparison.changes.slice(0, 10).map((security, index) => (
                            <tr key={index}>
                              <td>{security.name} ({security.isin})</td>
                              <td>${security.value.doc1?.toLocaleString() || 'N/A'}</td>
                              <td>${security.value.doc2?.toLocaleString() || 'N/A'}</td>
                              <td className={security.value.direction === 'increase' ? 'positive' : 'negative'}>
                                {security.value.direction === 'increase' ? '+' : ''}
                                ${Math.abs(security.value.absolute_change).toLocaleString()}
                                {' '}
                                ({security.value.direction === 'increase' ? '+' : ''}
                                {security.value.percentage_change.toFixed(2)}%)
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {comparisonResults.securities_comparison.changes.length > 10 && (
                        <div className="table-more">
                          +{comparisonResults.securities_comparison.changes.length - 10} more securities
                        </div>
                      )}
                    </div>
                  )}
                  
                  {comparisonResults.securities_comparison.additions.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>Added Securities ({comparisonResults.securities_comparison.additions.length})</h4>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>Security</th>
                            <th>ISIN</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonResults.securities_comparison.additions.slice(0, 5).map((security, index) => (
                            <tr key={index}>
                              <td>{security.name}</td>
                              <td>{security.isin}</td>
                              <td>${security.value?.toLocaleString() || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {comparisonResults.securities_comparison.additions.length > 5 && (
                        <div className="table-more">
                          +{comparisonResults.securities_comparison.additions.length - 5} more securities
                        </div>
                      )}
                    </div>
                  )}
                  
                  {comparisonResults.securities_comparison.removals.length > 0 && (
                    <div className="comparison-subsection">
                      <h4>Removed Securities ({comparisonResults.securities_comparison.removals.length})</h4>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>Security</th>
                            <th>ISIN</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonResults.securities_comparison.removals.slice(0, 5).map((security, index) => (
                            <tr key={index}>
                              <td>{security.name}</td>
                              <td>{security.isin}</td>
                              <td>${security.value?.toLocaleString() || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {comparisonResults.securities_comparison.removals.length > 5 && (
                        <div className="table-more">
                          +{comparisonResults.securities_comparison.removals.length - 5} more securities
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .comparison-tool {
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
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        
        .document-select-group {
          display: flex;
          align-items: center;
          gap: 15px;
        }
        
        .document-select-label {
          font-weight: 500;
          min-width: 150px;
        }
        
        .document-select {
          padding: 10px 15px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          flex: 1;
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
        
        .error-message {
          padding: 10px 15px;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .section-title {
          font-size: 18px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
          border-bottom: 1px solid #e9ecef;
          padding-bottom: 10px;
        }
        
        .comparison-summary {
          margin-bottom: 25px;
        }
        
        .summary-text {
          line-height: 1.6;
          color: #495057;
        }
        
        .highlights {
          margin-top: 15px;
        }
        
        .highlights h4 {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 10px;
          color: #2c3e50;
        }
        
        .highlights-list {
          list-style-type: disc;
          padding-left: 20px;
        }
        
        .highlight-item {
          margin-bottom: 5px;
          color: #495057;
        }
        
        .comparison-value-change {
          display: flex;
          flex-wrap: wrap;
          gap: 20px;
          margin-bottom: 25px;
        }
        
        .value-item {
          flex: 1;
          min-width: 200px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .value-label {
          font-weight: 500;
          margin-bottom: 5px;
          color: #6c757d;
        }
        
        .value-amount {
          font-size: 18px;
          font-weight: 600;
          color: #2c3e50;
        }
        
        .value-change {
          flex: 1;
          min-width: 200px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #6c757d;
        }
        
        .positive {
          color: #28a745;
        }
        
        .negative {
          color: #dc3545;
        }
        
        .comparison-section {
          margin-bottom: 25px;
          padding-bottom: 15px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .comparison-subsection {
          margin-bottom: 20px;
        }
        
        .comparison-subsection h4 {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 10px;
          color: #2c3e50;
        }
        
        .comparison-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 10px;
        }
        
        .comparison-table th, .comparison-table td {
          padding: 10px;
          border: 1px solid #dee2e6;
          text-align: left;
        }
        
        .comparison-table th {
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
        
        .addition-list, .removal-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .addition-item, .removal-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 10px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .addition-item:last-child, .removal-item:last-child {
          border-bottom: none;
        }
        
        .addition-name, .removal-name {
          font-weight: 500;
        }
        
        .addition-value {
          color: #28a745;
        }
        
        .removal-value {
          color: #dc3545;
        }
        
        .securities-summary {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          margin-bottom: 20px;
        }
        
        .summary-item {
          flex: 1;
          min-width: 150px;
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
          font-weight: 600;
          color: #2c3e50;
        }
        
        @media (max-width: 768px) {
          .document-select-group {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .document-select-label {
            margin-bottom: 5px;
          }
          
          .document-select {
            width: 100%;
          }
          
          .btn {
            width: 100%;
          }
          
          .comparison-value-change {
            flex-direction: column;
          }
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

export default DocumentComparisonTool;
