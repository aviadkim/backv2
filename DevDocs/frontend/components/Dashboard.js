import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

// Icons
import { 
  FiSearch, 
  FiPlus, 
  FiFileText, 
  FiBriefcase, 
  FiSearch as FiMagnify, 
  FiBarChart2, 
  FiHash, 
  FiZap 
} from 'react-icons/fi';

const Dashboard = () => {
  const router = useRouter();
  const [documents, setDocuments] = useState([]);
  const [portfolioValue, setPortfolioValue] = useState('19,510,599');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch documents and portfolio data on component mount
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch documents
        const docsResponse = await axios.get('/api/documents/recent');
        if (docsResponse.data) {
          setDocuments(docsResponse.data);
        }

        // Fetch portfolio value
        const portfolioResponse = await axios.get('/api/financial/portfolio');
        if (portfolioResponse.data && portfolioResponse.data.totalValue) {
          setPortfolioValue(portfolioResponse.data.totalValue.toLocaleString());
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    // Comment out actual API calls for now to avoid errors
    // fetchData();
  }, []);

  const handleTestingDashboard = () => {
    router.push('/dev-test-center');
  };

  const handleApiKeySetup = () => {
    router.push('/api-key-setup');
  };

  const handleViewDocuments = () => {
    router.push('/documents');
  };

  const handleViewPortfolio = () => {
    router.push('/portfolio');
  };

  const handleStartAnalysis = () => {
    router.push('/analysis');
  };

  const handleExportData = () => {
    router.push('/export');
  };

  const handleViewIsins = () => {
    router.push('/isins');
  };

  const handleGetAdvice = () => {
    router.push('/advisor');
  };

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
            onClick={handleTestingDashboard}
            className="test-button"
          >
            <FiSearch size={16} />
            <span>Open Testing Dashboard</span>
          </button>
          <button
            type="button"
            onClick={handleApiKeySetup}
            className="api-button"
          >
            <FiPlus size={16} />
            <span>Configure API Keys</span>
          </button>
        </div>
      </div>
      
      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Recent Documents</h2>
            <div className="card-icon"><FiFileText size={24} /></div>
          </div>
          <div className="card-content">
            <p>You have {documents.length || 3} recently processed documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleViewDocuments(); }} className="card-link">View All Documents</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Portfolio Summary</h2>
            <div className="card-icon"><FiBriefcase size={24} /></div>
          </div>
          <div className="card-content">
            <p>Total portfolio value: ${portfolioValue}</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleViewPortfolio(); }} className="card-link">View Portfolio</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Document Analysis</h2>
            <div className="card-icon"><FiMagnify size={24} /></div>
          </div>
          <div className="card-content">
            <p>Run analysis on your financial documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleStartAnalysis(); }} className="card-link">Start Analysis</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Data Export</h2>
            <div className="card-icon"><FiBarChart2 size={24} /></div>
          </div>
          <div className="card-content">
            <p>Export your financial data in various formats.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleExportData(); }} className="card-link">Export Data</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">ISIN Extraction</h2>
            <div className="card-icon"><FiHash size={24} /></div>
          </div>
          <div className="card-content">
            <p>Extract ISIN codes from your documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleViewIsins(); }} className="card-link">View ISINs</a>
          </div>
        </div>
        
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Financial Advisor</h2>
            <div className="card-icon"><FiZap size={24} /></div>
          </div>
          <div className="card-content">
            <p>Get financial advice based on your documents.</p>
          </div>
          <div className="card-footer">
            <a href="#" onClick={(e) => { e.preventDefault(); handleGetAdvice(); }} className="card-link">Get Advice</a>
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
        
        .welcome-actions button svg {
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
          color: #3498db;
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

export default Dashboard;
