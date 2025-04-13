import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { FiUpload, FiFileText, FiPieChart, FiTrendingUp, FiSearch, FiPlus } from 'react-icons/fi';
import withProtectedRoute from '../components/ProtectedRoute';
import { useDocument } from '../providers/DocumentProvider';
import { useAuth } from '../providers/AuthProvider';
import DocumentUpload from '../components/DocumentUpload';
import FinancialDataVisualization from '../components/FinancialDataVisualization';
import FinDocLayout from '../components/FinDocLayout';

const Dashboard = () => {
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [portfolioData, setPortfolioData] = useState(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const router = useRouter();
  const { getAllDocuments } = useDocument();
  const { user } = useAuth();

  useEffect(() => {
    // Load recent documents
    const loadRecentDocuments = async () => {
      try {
        const documents = await getAllDocuments();
        setRecentDocuments(documents?.slice(0, 5) || []); // Get the 5 most recent documents
      } catch (error) {
        console.error('Error loading recent documents:', error);
      }
    };

    // Load portfolio data
    const loadPortfolioData = async () => {
      try {
        // In a real implementation, this would fetch from an API
        // For now, we'll use sample data
        setPortfolioData({
          holdings: [
            { name: 'Apple Inc.', isin: 'US0378331005', value: 17635.00 },
            { name: 'Microsoft Corporation', isin: 'US5949181045', value: 20613.50 },
            { name: 'Tesla Inc.', isin: 'US88160R1014', value: 4383.50 },
            { name: 'Amazon.com Inc.', isin: 'US0231351067', value: 15280.75 },
            { name: 'Alphabet Inc.', isin: 'US02079K1079', value: 12450.30 }
          ],
          summary: {
            totalValue: '$70,363.05',
            totalSecurities: 5,
            topHolding: 'Microsoft Corporation',
            lastUpdated: '2023-05-15'
          }
        });
      } catch (error) {
        console.error('Error loading portfolio data:', error);
      }
    };

    loadRecentDocuments();
    loadPortfolioData();
  }, [getAllDocuments]);

  const handleUploadComplete = (document) => {
    setRecentDocuments(prev => [document, ...prev].slice(0, 5));
    setIsUploadModalOpen(false);
  };

  return (
    <FinDocLayout>
      <div className="dashboard-container">
        {/* Welcome message */}
        <div className="welcome-card">
          <h2 className="welcome-title">Welcome, {user?.fullName || 'Aviad'}</h2>
          <p className="welcome-text">
            This is your financial document dashboard. Upload documents, analyze your portfolio, and get insights from your financial data.
          </p>
          <div className="welcome-actions">
            <button
              type="button"
              onClick={() => router.push('/dev-test-center')}
              className="test-button"
            >
              <FiSearch size={16} />
              Open Testing Dashboard
            </button>
            <button
              type="button"
              onClick={() => router.push('/api-key-setup')}
              className="api-button"
            >
              <FiPlus size={16} />
              Configure API Keys
            </button>
          </div>
        </div>

        {/* Dashboard grid */}
        <div className="dashboard-grid">
          {/* Recent documents */}
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">Recent Documents</h2>
              <button
                type="button"
                onClick={() => router.push('/documents')}
                className="view-all-button"
              >
                View all
              </button>
            </div>

            {recentDocuments && recentDocuments.length > 0 ? (
              <ul className="document-list">
                {recentDocuments.map((doc) => (
                  <li key={doc.id} className="document-item">
                    <div className="document-icon">
                      <FiFileText size={24} color="#3498db" />
                    </div>
                    <div className="document-info">
                      <p className="document-title">{doc.title}</p>
                      <p className="document-meta">{doc.fileType} • {(doc.fileSize / 1024).toFixed(2)} KB</p>
                    </div>
                    <div className="document-date">
                      {new Date(doc.createdAt).toLocaleDateString()}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty-state">
                <FiFileText size={48} color="#a0aec0" />
                <h3 className="empty-title">No documents</h3>
                <p className="empty-text">Get started by uploading a document.</p>
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(true)}
                  className="upload-button"
                >
                  <FiPlus size={16} />
                  Upload Document
                </button>
              </div>
            )}
          </div>

          {/* Portfolio visualization */}
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">Portfolio Overview</h2>
              <button
                type="button"
                onClick={() => router.push('/portfolio')}
                className="view-all-button"
              >
                View details
              </button>
            </div>

            {portfolioData ? (
              <FinancialDataVisualization data={portfolioData} type="portfolio" />
            ) : (
              <div className="empty-state">
                <FiPieChart size={48} color="#a0aec0" />
                <h3 className="empty-title">No portfolio data</h3>
                <p className="empty-text">Upload financial documents to build your portfolio.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload modal */}
      {isUploadModalOpen && (
        <div className="modal-overlay">
          <div className="modal-container">
            <div className="modal-header">
              <h3 className="modal-title">Upload Document</h3>
              <button
                type="button"
                onClick={() => setIsUploadModalOpen(false)}
                className="modal-close"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <DocumentUpload onUploadComplete={handleUploadComplete} />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                onClick={() => setIsUploadModalOpen(false)}
                className="cancel-button"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .dashboard-container {
          padding: 30px;
        }
        .welcome-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 25px;
          margin-bottom: 30px;
        }
        .welcome-title {
          font-size: 20px;
          font-weight: 600;
          margin-bottom: 10px;
          color: #2c3e50;
        }
        .welcome-text {
          color: #718096;
          line-height: 1.6;
          margin-bottom: 15px;
        }
        .welcome-actions {
          display: flex;
          gap: 10px;
          margin-top: 15px;
        }
        .test-button, .api-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s;
        }
        .test-button {
          background-color: #3498db;
          color: white;
          border: none;
        }
        .test-button:hover {
          background-color: #2980b9;
        }
        .api-button {
          background-color: #f1f5f9;
          color: #475569;
          border: 1px solid #cbd5e1;
        }
        .api-button:hover {
          background-color: #e2e8f0;
        }
        .dashboard-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
        }
        @media (max-width: 1024px) {
          .dashboard-grid {
            grid-template-columns: 1fr;
          }
        }
        .dashboard-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 25px;
        }
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        .card-title {
          font-size: 18px;
          font-weight: 500;
          color: #2c3e50;
        }
        .view-all-button {
          color: #3498db;
          font-size: 14px;
          font-weight: 500;
          background: none;
          border: none;
          cursor: pointer;
        }
        .view-all-button:hover {
          text-decoration: underline;
        }
        .document-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .document-item {
          display: flex;
          align-items: center;
          padding: 15px 0;
          border-bottom: 1px solid #edf2f7;
        }
        .document-item:last-child {
          border-bottom: none;
        }
        .document-icon {
          margin-right: 15px;
        }
        .document-info {
          flex: 1;
        }
        .document-title {
          font-weight: 500;
          margin: 0 0 5px 0;
          color: #2c3e50;
        }
        .document-meta {
          font-size: 13px;
          color: #a0aec0;
          margin: 0;
        }
        .document-date {
          font-size: 13px;
          color: #a0aec0;
        }
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 0;
          text-align: center;
        }
        .empty-title {
          margin: 15px 0 5px 0;
          font-size: 16px;
          font-weight: 500;
          color: #2c3e50;
        }
        .empty-text {
          margin: 0 0 20px 0;
          font-size: 14px;
          color: #a0aec0;
        }
        .upload-button {
          display: flex;
          align-items: center;
          gap: 8px;
          background-color: #3498db;
          color: white;
          border: none;
          border-radius: 5px;
          padding: 10px 15px;
          font-size: 14px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        .upload-button:hover {
          background-color: #2980b9;
        }
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        .modal-container {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
        }
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 25px;
          border-bottom: 1px solid #edf2f7;
        }
        .modal-title {
          font-size: 18px;
          font-weight: 500;
          color: #2c3e50;
          margin: 0;
        }
        .modal-close {
          background: none;
          border: none;
          font-size: 24px;
          color: #a0aec0;
          cursor: pointer;
        }
        .modal-body {
          padding: 25px;
        }
        .modal-footer {
          padding: 15px 25px;
          border-top: 1px solid #edf2f7;
          display: flex;
          justify-content: flex-end;
        }
        .cancel-button {
          background-color: #edf2f7;
          color: #64748b;
          border: none;
          border-radius: 5px;
          padding: 8px 15px;
          font-size: 14px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        .cancel-button:hover {
          background-color: #e2e8f0;
        }
      `}</style>
    </FinDocLayout>
  );
};

export default withProtectedRoute(Dashboard);
