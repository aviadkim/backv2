import React, { useState } from 'react';
import { useRouter } from 'next/router';

const SimpleDashboard = () => {
  const router = useRouter();
  const [portfolioValue, setPortfolioValue] = useState('19,510,599');

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      
      {/* Welcome Card */}
      <div className="welcome-card">
        <h2 className="welcome-title">Welcome, Aviad</h2>
        <p className="welcome-text">
          This is your financial document dashboard. Upload documents, analyze your portfolio, and get insights from your financial data.
        </p>
        <div className="welcome-actions">
          <button
            type="button"
            onClick={() => router.push('/dev-test-center')}
            className="test-button"
          >
            <span>🔍</span>
            <span>Open Testing Dashboard</span>
          </button>
          <button
            type="button"
            onClick={() => router.push('/api-key-setup')}
            className="api-button"
          >
            <span>➕</span>
            <span>Configure API Keys</span>
          </button>
        </div>
      </div>
      
      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Recent Documents</h2>
            <div className="card-icon">📄</div>
          </div>
          <div className="card-content">
            <p>You have 3 recently processed documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/documents'); }} className="card-link">View All Documents</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Portfolio Summary</h2>
            <div className="card-icon">💼</div>
          </div>
          <div className="card-content">
            <p>Total portfolio value: ${portfolioValue}</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/portfolio'); }} className="card-link">View Portfolio</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Document Analysis</h2>
            <div className="card-icon">🔍</div>
          </div>
          <div className="card-content">
            <p>Run analysis on your financial documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/analysis'); }} className="card-link">Start Analysis</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Data Export</h2>
            <div className="card-icon">📊</div>
          </div>
          <div className="card-content">
            <p>Export your financial data in various formats.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/export'); }} className="card-link">Export Data</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">ISIN Extraction</h2>
            <div className="card-icon">🔢</div>
          </div>
          <div className="card-content">
            <p>Extract ISIN codes from your documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/isins'); }} className="card-link">View ISINs</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Financial Advisor</h2>
            <div className="card-icon">💡</div>
          </div>
          <div className="card-content">
            <p>Get financial advice based on your documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); router.push('/advisor'); }} className="card-link">Get Advice</a>
          </div>
        </div>
      </div>

      <style jsx>{`
        .page-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .welcome-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          padding: 20px;
          margin-bottom: 20px;
        }
        
        .welcome-title {
          font-size: 20px;
          font-weight: bold;
          margin: 0 0 10px 0;
          color: #2c3e50;
        }
        
        .welcome-text {
          color: #7f8c8d;
          margin-bottom: 15px;
        }
        
        .welcome-actions {
          display: flex;
          gap: 10px;
        }
        
        .welcome-actions button {
          display: flex;
          align-items: center;
          padding: 8px 16px;
          background-color: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 4px;
          color: #495057;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .welcome-actions button:hover {
          background-color: #e9ecef;
        }
        
        .welcome-actions button span {
          margin-right: 8px;
        }
        
        .dashboard-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }
        
        .dashboard-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          padding: 20px;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .dashboard-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .card-title {
          font-size: 18px;
          font-weight: bold;
          margin: 0;
          color: #2c3e50;
        }
        
        .card-icon {
          font-size: 24px;
        }
        
        .card-content {
          margin-bottom: 15px;
        }
        
        .card-footer {
          display: flex;
          justify-content: flex-end;
        }
        
        .card-link {
          color: #3498db;
          text-decoration: none;
          font-weight: bold;
          transition: color 0.3s ease;
        }
        
        .card-link:hover {
          color: #2980b9;
        }
      `}</style>
    </div>
  );
};

export default SimpleDashboard;
