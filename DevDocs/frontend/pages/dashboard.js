import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { FiUpload, FiFileText, FiPieChart, FiTrendingUp, FiSearch, FiPlus } from 'react-icons/fi';
import withProtectedRoute from '../components/ProtectedRoute';
import { useDocument } from '../providers/DocumentProvider';
import { useAuth } from '../providers/AuthProvider';
import DocumentUpload from '../components/DocumentUpload';
import FinancialDataVisualization from '../components/FinancialDataVisualization';

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
        setRecentDocuments(documents.slice(0, 5)); // Get the 5 most recent documents
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setIsUploadModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <FiUpload className="mr-2 -ml-1 h-5 w-5" />
                Upload Document
              </button>
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <FiSearch className="mr-2 -ml-1 h-5 w-5" />
                Search
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome message */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-2">Welcome, {user?.fullName || 'User'}</h2>
          <p className="text-gray-600">
            This is your financial document dashboard. Upload documents, analyze your portfolio, and get insights from your financial data.
          </p>
        </div>
        
        {/* Dashboard grid */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Recent documents */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-900">Recent Documents</h2>
              <button
                type="button"
                onClick={() => router.push('/documents')}
                className="text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                View all
              </button>
            </div>
            
            {recentDocuments.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {recentDocuments.map((doc) => (
                  <li key={doc.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <FiFileText className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{doc.title}</p>
                        <p className="text-sm text-gray-500 truncate">{doc.fileType} • {(doc.fileSize / 1024).toFixed(2)} KB</p>
                      </div>
                      <div className="flex-shrink-0 text-sm text-gray-500">
                        {new Date(doc.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="py-12 text-center">
                <FiFileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by uploading a document.</p>
                <div className="mt-6">
                  <button
                    type="button"
                    onClick={() => setIsUploadModalOpen(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <FiPlus className="mr-2 -ml-1 h-5 w-5" />
                    Upload Document
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Portfolio visualization */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-900">Portfolio Overview</h2>
              <button
                type="button"
                onClick={() => router.push('/portfolio')}
                className="text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                View details
              </button>
            </div>
            
            {portfolioData ? (
              <FinancialDataVisualization data={portfolioData} type="portfolio" />
            ) : (
              <div className="py-12 text-center">
                <FiPieChart className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No portfolio data</h3>
                <p className="mt-1 text-sm text-gray-500">Upload financial documents to build your portfolio.</p>
              </div>
            )}
          </div>
        </div>
      </main>
      
      {/* Upload modal */}
      {isUploadModalOpen && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Upload Document</h3>
                    <div className="mt-2">
                      <DocumentUpload onUploadComplete={handleUploadComplete} />
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default withProtectedRoute(Dashboard);
