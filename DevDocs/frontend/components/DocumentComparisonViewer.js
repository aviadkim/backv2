import React, { useState, useEffect } from 'react';
import { FiFileText, FiBarChart2, FiArrowRight, FiDownload, FiPlus, FiX } from 'react-icons/fi';
import axios from 'axios';

const DocumentComparisonViewer = ({ documentIds = [] }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState(documentIds);
  const [availableDocuments, setAvailableDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('metrics');
  
  useEffect(() => {
    // Fetch available documents
    const fetchDocuments = async () => {
      try {
        const response = await axios.get('/api/documents');
        setAvailableDocuments(response.data.documents);
      } catch (err) {
        console.error('Error fetching documents:', err);
        setError('Error fetching available documents');
      }
    };
    
    fetchDocuments();
  }, []);
  
  useEffect(() => {
    // Update selected documents when documentIds prop changes
    setSelectedDocuments(documentIds);
  }, [documentIds]);
  
  useEffect(() => {
    // Fetch comparison data when selected documents change
    if (selectedDocuments.length >= 2) {
      fetchComparison();
    }
  }, [selectedDocuments]);
  
  const fetchComparison = async () => {
    if (selectedDocuments.length < 2) {
      setError('At least two documents are required for comparison');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/documents/compare', {
        document_ids: selectedDocuments
      });
      
      setComparison(response.data.comparison);
    } catch (err) {
      console.error('Error comparing documents:', err);
      setError(err.response?.data?.detail || 'Error comparing documents');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddDocument = (documentId) => {
    if (!selectedDocuments.includes(documentId)) {
      setSelectedDocuments([...selectedDocuments, documentId]);
    }
  };
  
  const handleRemoveDocument = (documentId) => {
    setSelectedDocuments(selectedDocuments.filter(id => id !== documentId));
  };
  
  const renderDocumentSelector = () => {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Selected Documents</h3>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {selectedDocuments.map(docId => {
            const document = availableDocuments.find(doc => doc.id === docId);
            return (
              <div key={docId} className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-blue-100 text-blue-800">
                <FiFileText className="mr-1 h-4 w-4" />
                {document ? document.title || document.file_name : docId}
                <button
                  type="button"
                  onClick={() => handleRemoveDocument(docId)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  <FiX className="h-4 w-4" />
                </button>
              </div>
            );
          })}
          
          {selectedDocuments.length < 5 && (
            <div className="relative inline-block">
              <button
                type="button"
                className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <FiPlus className="mr-1 h-4 w-4" />
                Add Document
              </button>
              
              <div className="absolute z-10 mt-1 w-56 bg-white rounded-md shadow-lg border border-gray-200">
                <div className="py-1">
                  <div className="px-3 py-2 text-xs font-medium text-gray-500">
                    Available Documents
                  </div>
                  
                  <div className="max-h-60 overflow-y-auto">
                    {availableDocuments
                      .filter(doc => !selectedDocuments.includes(doc.id))
                      .map(doc => (
                        <button
                          key={doc.id}
                          type="button"
                          onClick={() => handleAddDocument(doc.id)}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          {doc.title || doc.file_name}
                        </button>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {selectedDocuments.length < 2 && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Please select at least two documents to compare.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {selectedDocuments.length >= 2 && (
          <button
            type="button"
            onClick={fetchComparison}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Compare Documents
          </button>
        )}
      </div>
    );
  };
  
  const renderMetricsTab = () => {
    if (!comparison || !comparison.financial_metrics) {
      return (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No financial metrics available for comparison.</p>
        </div>
      );
    }
    
    const metrics = Object.entries(comparison.financial_metrics);
    
    if (metrics.length === 0) {
      return (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No common financial metrics found across selected documents.</p>
        </div>
      );
    }
    
    return (
      <div className="space-y-8">
        {metrics.map(([metricName, metricValues]) => (
          <div key={metricName} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <h4 className="text-md font-medium text-gray-900 capitalize">
                {metricName.replace(/_/g, ' ')}
              </h4>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Period
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {metricValues.map((metric, index) => {
                    const document = comparison.documents.find(doc => doc.id === metric.document_id);
                    return (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {document ? document.title || document.file_name : metric.document_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {typeof metric.value === 'number' 
                            ? new Intl.NumberFormat('en-US', { 
                                style: metricName.includes('ratio') ? 'decimal' : 'currency', 
                                currency: 'USD',
                                maximumFractionDigits: 2
                              }).format(metric.value)
                            : metric.value}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {metric.period}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  const renderRatiosTab = () => {
    if (!comparison || !comparison.financial_ratios) {
      return (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No financial ratios available for comparison.</p>
        </div>
      );
    }
    
    const ratios = Object.entries(comparison.financial_ratios);
    
    if (ratios.length === 0) {
      return (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No common financial ratios found across selected documents.</p>
        </div>
      );
    }
    
    return (
      <div className="space-y-8">
        {ratios.map(([ratioName, ratioValues]) => (
          <div key={ratioName} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <h4 className="text-md font-medium text-gray-900 capitalize">
                {ratioName.replace(/_/g, ' ')}
              </h4>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Value
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Period
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {ratioValues.map((ratio, index) => {
                    const document = comparison.documents.find(doc => doc.id === ratio.document_id);
                    return (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {document ? document.title || document.file_name : ratio.document_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {typeof ratio.value === 'number'
                            ? ratioName.includes('percentage') || ratioName.includes('yield')
                              ? `${(ratio.value * 100).toFixed(2)}%`
                              : ratio.value.toFixed(2)
                            : ratio.value}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {ratio.period}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  const renderPeriodsTab = () => {
    if (!comparison || !comparison.time_periods) {
      return (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No time periods available for comparison.</p>
        </div>
      );
    }
    
    return (
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Time Periods Across Documents</h3>
        
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Documents
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {comparison.time_periods.map((period, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {period}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="flex flex-wrap gap-2">
                        {comparison.documents.map(doc => (
                          <div key={doc.id} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {doc.title || doc.file_name}
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        {renderDocumentSelector()}
        
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-500">Comparing documents...</p>
          </div>
        )}
        
        {error && (
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
        )}
        
        {comparison && (
          <>
            <div className="border-b border-gray-200 mt-6">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('metrics')}
                  className={`py-4 px-6 text-sm font-medium flex items-center ${
                    activeTab === 'metrics'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Financial Metrics
                </button>
                <button
                  onClick={() => setActiveTab('ratios')}
                  className={`py-4 px-6 text-sm font-medium flex items-center ${
                    activeTab === 'ratios'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Financial Ratios
                </button>
                <button
                  onClick={() => setActiveTab('periods')}
                  className={`py-4 px-6 text-sm font-medium flex items-center ${
                    activeTab === 'periods'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Time Periods
                </button>
              </nav>
            </div>
            
            <div className="mt-6">
              {activeTab === 'metrics' && renderMetricsTab()}
              {activeTab === 'ratios' && renderRatiosTab()}
              {activeTab === 'periods' && renderPeriodsTab()}
            </div>
          </>
        )}
      </div>
      
      {comparison && (
        <div className="bg-gray-50 px-6 py-3 flex justify-end">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <FiDownload className="mr-2 -ml-1 h-5 w-5" />
            Export Comparison
          </button>
        </div>
      )}
    </div>
  );
};

export default DocumentComparisonViewer;
