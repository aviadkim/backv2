import React from 'react';

const PortfolioSummary = ({ data }) => {
  if (!data) {
    return null;
  }

  const { client_info, document_date, portfolio_value, asset_allocation } = data;

  return (
    <div className="portfolio-summary">
      <h2>Portfolio Summary</h2>
      
      <div className="summary-grid">
        <div className="summary-card">
          <h3>Client Information</h3>
          <p><strong>Name:</strong> {client_info?.name || 'N/A'}</p>
          <p><strong>Number:</strong> {client_info?.number || 'N/A'}</p>
        </div>
        
        <div className="summary-card">
          <h3>Document Details</h3>
          <p><strong>Date:</strong> {document_date || 'N/A'}</p>
          <p><strong>Portfolio Value:</strong> {formatCurrency(portfolio_value)}</p>
        </div>
        
        <div className="summary-card asset-allocation">
          <h3>Asset Allocation</h3>
          {renderAssetAllocation(asset_allocation)}
        </div>
      </div>
      
      <style jsx>{`
        .portfolio-summary {
          margin-top: 30px;
        }
        
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }
        
        .summary-card {
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .summary-card h3 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #333;
          font-size: 18px;
        }
        
        .asset-allocation {
          grid-column: span 2;
        }
        
        .allocation-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 10px;
        }
        
        .allocation-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #eee;
        }
        
        .allocation-item:last-child {
          border-bottom: none;
        }
        
        .allocation-bar {
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          margin-top: 5px;
          overflow: hidden;
        }
        
        .allocation-fill {
          height: 100%;
          background: #4285f4;
        }
        
        @media (max-width: 768px) {
          .asset-allocation {
            grid-column: span 1;
          }
        }
      `}</style>
    </div>
  );
};

// Helper functions
const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return `$${Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
};

const renderAssetAllocation = (allocation) => {
  if (!allocation || Object.keys(allocation).length === 0) {
    return <p>No asset allocation data available.</p>;
  }

  return (
    <div className="allocation-grid">
      {Object.entries(allocation).map(([assetClass, data]) => {
        const percentage = typeof data === 'object' ? data.percentage : data;
        const value = typeof data === 'object' ? data.value : null;
        
        return (
          <div key={assetClass} className="allocation-item">
            <div>
              <div>{assetClass}</div>
              <div className="allocation-bar">
                <div 
                  className="allocation-fill" 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div>{percentage}%</div>
              {value && <div>{formatCurrency(value)}</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default PortfolioSummary;
