import React, { useState, useEffect } from 'react';
import withProtectedRoute from '../components/ProtectedRoute';
import DocumentUploader from '../components/DocumentUploader';
import DocumentAnalysisViewer from '../components/DocumentAnalysisViewer';
import DocumentComparisonViewer from '../components/DocumentComparisonViewer';
import { FiFileText, FiUpload, FiBarChart2, FiList } from 'react-icons/fi';
import axios from 'axios';

const TestDocumentUnderstandingPage = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Fetch available documents
    fetchDocuments();
  }, []);
  
  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/documents');
      setDocuments(response.data.documents);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Error fetching documents');
      setLoading(false);
    }
  };
  
  const fetchAnalysisResults = async (documentId) => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/documents/${documentId}/analysis`);
      setAnalysisResults(response.data.analysis_results);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching analysis results:', err);
      setError('Error fetching analysis results');
      setLoading(false);
    }
  };
  
  const handleDocumentProcessed = (data) => {
    // Refresh document list
    fetchDocuments();
    
    // Set the newly processed document as selected
    setSelectedDocument(data.document_id);
    
    // Fetch analysis results for the document
    fetchAnalysisResults(data.document_id);
    
    // Switch to analysis tab
    setActiveTab('analysis');
  };
  
  const handleDocumentSelect = (documentId) => {
    setSelectedDocument(documentId);
    fetchAnalysisResults(documentId);
    setActiveTab('analysis');
  };
  
  const renderUploadTab = () => {
    return (
      <div>
        <DocumentUploader onDocumentProcessed={handleDocumentProcessed} />
      </div>
    );
  };
  
  const renderDocumentsTab = () => {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Your Documents</h3>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-500">Loading documents...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <FiFileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by uploading a document.</p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setActiveTab('upload')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <FiUpload className="mr-2 -ml-1 h-5 w-5" />
                Upload Document
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-hidden bg-white shadow sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {documents.map((document) => (
                <li key={document.id}>
                  <button
                    onClick={() => handleDocumentSelect(document.id)}
                    className="block hover:bg-gray-50 w-full text-left"
                  >
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <p className="truncate text-sm font-medium text-blue-600">
                          {document.title || document.file_name}
                        </p>
                        <div className="ml-2 flex flex-shrink-0">
                          <p className="inline-flex rounded-full bg-green-100 px-2 text-xs font-semibold leading-5 text-green-800">
                            Processed
                          </p>
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex">
                          <p className="flex items-center text-sm text-gray-500">
                            <FiFileText className="mr-1.5 h-5 w-5 flex-shrink-0 text-gray-400" />
                            {document.file_name}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <p>
                            Processed on {new Date(document.processed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  const renderAnalysisTab = () => {
    return (
      <div>
        {!selectedDocument ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-center py-8">
              <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No document selected</h3>
              <p className="mt-1 text-sm text-gray-500">Select a document to view analysis results.</p>
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => setActiveTab('documents')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <FiList className="mr-2 -ml-1 h-5 w-5" />
                  View Documents
                </button>
              </div>
            </div>
          </div>
        ) : loading ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-sm text-gray-500">Loading analysis results...</p>
            </div>
          </div>
        ) : (
          <DocumentAnalysisViewer analysisResults={analysisResults} />
        )}
      </div>
    );
  };
  
  const renderComparisonTab = () => {
    return (
      <div>
        <DocumentComparisonViewer />
      </div>
    );
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Document Understanding</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">About Document Understanding</h2>
        <p className="text-gray-600 mb-4">
          Our Document Understanding Engine can analyze financial documents such as PDFs, Excel spreadsheets, and CSV files.
          It extracts financial data, identifies entities, recognizes financial statements, and provides insights into your financial documents.
        </p>
        
        <div className="bg-blue-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-blue-800 mb-1">Supported Document Types:</h3>
          <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
            <li>Financial Statements (Income Statement, Balance Sheet, Cash Flow)</li>
            <li>Annual Reports</li>
            <li>Quarterly Reports</li>
            <li>Bank Statements</li>
            <li>Investment Account Statements</li>
            <li>Credit Card Statements</li>
            <li>Financial Spreadsheets</li>
          </ul>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="sm:hidden">
          <label htmlFor="tabs" className="sr-only">Select a tab</label>
          <select
            id="tabs"
            name="tabs"
            className="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value)}
          >
            <option value="upload">Upload Document</option>
            <option value="documents">Your Documents</option>
            <option value="analysis">Document Analysis</option>
            <option value="comparison">Document Comparison</option>
          </select>
        </div>
        <div className="hidden sm:block">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('upload')}
                className={`${
                  activeTab === 'upload'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Upload Document
              </button>
              <button
                onClick={() => setActiveTab('documents')}
                className={`${
                  activeTab === 'documents'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Your Documents
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`${
                  activeTab === 'analysis'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Document Analysis
              </button>
              <button
                onClick={() => setActiveTab('comparison')}
                className={`${
                  activeTab === 'comparison'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Document Comparison
              </button>
            </nav>
          </div>
        </div>
      </div>
      
      {activeTab === 'upload' && renderUploadTab()}
      {activeTab === 'documents' && renderDocumentsTab()}
      {activeTab === 'analysis' && renderAnalysisTab()}
      {activeTab === 'comparison' && renderComparisonTab()}
    </div>
  );
};

export default withProtectedRoute(TestDocumentUnderstandingPage);
