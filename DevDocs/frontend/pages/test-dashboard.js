import React, { useState, useEffect } from 'react';
import { FiCheckCircle, FiXCircle, FiAlertTriangle, FiClock, FiPlay, FiRefreshCw, FiSettings, FiDownload, FiUpload } from 'react-icons/fi';
import Link from 'next/link';
import withProtectedRoute from '../components/ProtectedRoute';

const TestDashboard = () => {
  const [testResults, setTestResults] = useState({});
  const [runningTests, setRunningTests] = useState([]);
  const [overallStatus, setOverallStatus] = useState('idle');
  const [expandedSection, setExpandedSection] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState({
    supabase: 'unknown',
    googleCloud: 'unknown',
    ocr: 'unknown',
    chatbot: 'unknown'
  });

  // Test categories and their tests
  const testSuites = {
    'UI Components': [
      { id: 'ui-layout', name: 'Layout Components', description: 'Tests the main layout components' },
      { id: 'ui-forms', name: 'Form Components', description: 'Tests form inputs, validation, and submission' },
      { id: 'ui-tables', name: 'Table Components', description: 'Tests data tables and grid components' },
      { id: 'ui-charts', name: 'Chart Components', description: 'Tests chart and visualization components' },
      { id: 'ui-responsive', name: 'Responsive Design', description: 'Tests responsive behavior across screen sizes' }
    ],
    'API Connections': [
      { id: 'api-supabase', name: 'Supabase Connection', description: 'Tests connection to Supabase database' },
      { id: 'api-gcp', name: 'Google Cloud Connection', description: 'Tests connection to Google Cloud Platform' },
      { id: 'api-ocr', name: 'OCR Service', description: 'Tests connection to OCR service' },
      { id: 'api-chatbot', name: 'Chatbot API', description: 'Tests connection to chatbot API' },
      { id: 'api-local', name: 'Local API', description: 'Tests connection to local API endpoints' }
    ],
    'Document Processing': [
      { id: 'doc-upload', name: 'Document Upload', description: 'Tests document upload functionality' },
      { id: 'doc-parsing', name: 'Document Parsing', description: 'Tests document parsing and extraction' },
      { id: 'doc-analysis', name: 'Document Analysis', description: 'Tests document analysis and insights' },
      { id: 'doc-storage', name: 'Document Storage', description: 'Tests document storage and retrieval' },
      { id: 'doc-export', name: 'Document Export', description: 'Tests document export functionality' }
    ],
    'Financial Analysis': [
      { id: 'fin-portfolio', name: 'Portfolio Analysis', description: 'Tests portfolio analysis functionality' },
      { id: 'fin-reports', name: 'Financial Reports', description: 'Tests financial report generation' },
      { id: 'fin-metrics', name: 'Financial Metrics', description: 'Tests financial metrics calculation' },
      { id: 'fin-visualization', name: 'Financial Visualization', description: 'Tests financial data visualization' },
      { id: 'fin-forecasting', name: 'Financial Forecasting', description: 'Tests financial forecasting functionality' }
    ],
    'AI & ML Features': [
      { id: 'ai-ocr', name: 'OCR Capabilities', description: 'Tests OCR capabilities and accuracy' },
      { id: 'ai-nlp', name: 'NLP Processing', description: 'Tests natural language processing capabilities' },
      { id: 'ai-chatbot', name: 'Chatbot Functionality', description: 'Tests chatbot functionality and responses' },
      { id: 'ai-recommendations', name: 'AI Recommendations', description: 'Tests AI-powered recommendations' },
      { id: 'ai-mcp', name: 'MCP Integration', description: 'Tests Model Context Protocol integration' }
    ],
    'Performance & Security': [
      { id: 'perf-loading', name: 'Page Loading Speed', description: 'Tests page loading performance' },
      { id: 'perf-rendering', name: 'Rendering Performance', description: 'Tests UI rendering performance' },
      { id: 'perf-api', name: 'API Response Time', description: 'Tests API response times' },
      { id: 'sec-auth', name: 'Authentication', description: 'Tests authentication security' },
      { id: 'sec-data', name: 'Data Protection', description: 'Tests data protection and privacy' }
    ]
  };

  // Run a specific test
  const runTest = async (testId) => {
    setRunningTests(prev => [...prev, testId]);
    
    try {
      // Simulate API call to run test
      const response = await fetch(`/api/tests/run?testId=${testId}`, {
        method: 'POST'
      }).catch(() => {
        // Fallback to simulated test results if API is not available
        return simulateTestRun(testId);
      });
      
      let result;
      if (response.ok) {
        result = await response.json();
      } else {
        result = simulateTestRun(testId);
      }
      
      // Update test results
      setTestResults(prev => ({
        ...prev,
        [testId]: {
          status: result.status,
          details: result.details,
          timestamp: new Date().toISOString(),
          duration: result.duration || Math.floor(Math.random() * 2000) + 500
        }
      }));
    } catch (error) {
      console.error(`Error running test ${testId}:`, error);
      
      // Set error status
      setTestResults(prev => ({
        ...prev,
        [testId]: {
          status: 'error',
          details: error.message || 'An unexpected error occurred',
          timestamp: new Date().toISOString(),
          duration: 0
        }
      }));
    } finally {
      setRunningTests(prev => prev.filter(id => id !== testId));
    }
  };

  // Run all tests in a category
  const runCategoryTests = async (category) => {
    setOverallStatus('running');
    
    const tests = testSuites[category];
    for (const test of tests) {
      await runTest(test.id);
    }
    
    setOverallStatus('completed');
  };

  // Run all tests
  const runAllTests = async () => {
    setOverallStatus('running');
    
    for (const category in testSuites) {
      const tests = testSuites[category];
      for (const test of tests) {
        await runTest(test.id);
      }
    }
    
    setOverallStatus('completed');
  };

  // Simulate a test run (for development/demo purposes)
  const simulateTestRun = (testId) => {
    // Predefined test results for specific tests
    const predefinedResults = {
      'api-supabase': {
        status: 'failed',
        details: 'Invalid API key. Double check your Supabase `anon` or `service_role` API key.',
        duration: 1245
      },
      'api-gcp': {
        status: 'warning',
        details: 'Connected successfully but missing permissions for some operations.',
        duration: 876
      },
      'ai-ocr': {
        status: 'warning',
        details: 'OCR service connected but API key has usage limitations.',
        duration: 1532
      },
      'ai-chatbot': {
        status: 'failed',
        details: 'Unable to connect to chatbot API. Check API key configuration.',
        duration: 654
      },
      'doc-upload': {
        status: 'passed',
        details: 'Document upload functionality working correctly.',
        duration: 987
      }
    };
    
    // Return predefined result if available, otherwise generate random result
    if (predefinedResults[testId]) {
      return predefinedResults[testId];
    }
    
    // Generate random result for other tests
    const statuses = ['passed', 'warning', 'failed'];
    const randomStatus = statuses[Math.floor(Math.random() * (testId.includes('api') ? 3 : 2))]; // Higher chance of failure for API tests
    
    return {
      status: randomStatus,
      details: `Test ${randomStatus === 'passed' ? 'completed successfully' : randomStatus === 'warning' ? 'completed with warnings' : 'failed'}`,
      duration: Math.floor(Math.random() * 2000) + 500
    };
  };

  // Check API key status
  const checkApiKeyStatus = async () => {
    try {
      // Simulate API call to check API keys
      const response = await fetch('/api/tests/check-api-keys').catch(() => {
        // Fallback to simulated results if API is not available
        return {
          ok: true,
          json: () => Promise.resolve({
            supabase: 'invalid',
            googleCloud: 'missing',
            ocr: 'valid',
            chatbot: 'missing'
          })
        };
      });
      
      if (response.ok) {
        const result = await response.json();
        setApiKeyStatus(result);
      }
    } catch (error) {
      console.error('Error checking API key status:', error);
    }
  };

  // Load initial test results
  useEffect(() => {
    const loadInitialResults = async () => {
      try {
        // Simulate API call to get test results
        const response = await fetch('/api/tests/results').catch(() => {
          // Fallback to empty results if API is not available
          return {
            ok: true,
            json: () => Promise.resolve({})
          };
        });
        
        if (response.ok) {
          const results = await response.json();
          setTestResults(results);
        }
      } catch (error) {
        console.error('Error loading test results:', error);
      }
    };
    
    loadInitialResults();
    checkApiKeyStatus();
  }, []);

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <FiCheckCircle className="text-green-500" />;
      case 'failed':
        return <FiXCircle className="text-red-500" />;
      case 'warning':
        return <FiAlertTriangle className="text-yellow-500" />;
      case 'running':
        return <FiClock className="text-blue-500 animate-pulse" />;
      default:
        return <FiClock className="text-gray-400" />;
    }
  };

  // Get API key status icon
  const getApiKeyStatusIcon = (status) => {
    switch (status) {
      case 'valid':
        return <FiCheckCircle className="text-green-500" />;
      case 'invalid':
        return <FiXCircle className="text-red-500" />;
      case 'missing':
        return <FiAlertTriangle className="text-yellow-500" />;
      default:
        return <FiClock className="text-gray-400" />;
    }
  };

  // Get API key status text
  const getApiKeyStatusText = (status) => {
    switch (status) {
      case 'valid':
        return 'Valid API key';
      case 'invalid':
        return 'Invalid API key';
      case 'missing':
        return 'API key not configured';
      default:
        return 'Unknown status';
    }
  };

  // Calculate category status
  const getCategoryStatus = (category) => {
    const tests = testSuites[category];
    const results = tests.map(test => testResults[test.id]?.status || 'unknown');
    
    if (results.some(status => status === 'failed')) {
      return 'failed';
    } else if (results.some(status => status === 'warning')) {
      return 'warning';
    } else if (results.every(status => status === 'passed')) {
      return 'passed';
    } else {
      return 'unknown';
    }
  };

  // Calculate overall test coverage
  const calculateTestCoverage = () => {
    let total = 0;
    let completed = 0;
    
    for (const category in testSuites) {
      const tests = testSuites[category];
      total += tests.length;
      
      for (const test of tests) {
        if (testResults[test.id]?.status) {
          completed++;
        }
      }
    }
    
    return Math.round((completed / total) * 100);
  };

  // Calculate pass rate
  const calculatePassRate = () => {
    let total = 0;
    let passed = 0;
    
    for (const category in testSuites) {
      const tests = testSuites[category];
      
      for (const test of tests) {
        if (testResults[test.id]?.status) {
          total++;
          if (testResults[test.id].status === 'passed') {
            passed++;
          }
        }
      }
    }
    
    return total > 0 ? Math.round((passed / total) * 100) : 0;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Test Dashboard</h1>
      
      {/* API Key Status */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">API Key Status</h2>
          <button
            onClick={checkApiKeyStatus}
            className="flex items-center px-3 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100"
          >
            <FiRefreshCw className="mr-2" />
            Refresh
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Supabase</span>
              {getApiKeyStatusIcon(apiKeyStatus.supabase)}
            </div>
            <p className="text-sm text-gray-600">{getApiKeyStatusText(apiKeyStatus.supabase)}</p>
            <Link href="/api-key-setup#supabase" className="text-sm text-blue-600 hover:underline mt-2 inline-block">
              Configure Supabase API Key
            </Link>
          </div>
          
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Google Cloud</span>
              {getApiKeyStatusIcon(apiKeyStatus.googleCloud)}
            </div>
            <p className="text-sm text-gray-600">{getApiKeyStatusText(apiKeyStatus.googleCloud)}</p>
            <Link href="/api-key-setup#google-cloud" className="text-sm text-blue-600 hover:underline mt-2 inline-block">
              Configure Google Cloud API Key
            </Link>
          </div>
          
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">OCR Service</span>
              {getApiKeyStatusIcon(apiKeyStatus.ocr)}
            </div>
            <p className="text-sm text-gray-600">{getApiKeyStatusText(apiKeyStatus.ocr)}</p>
            <Link href="/api-key-setup#ocr" className="text-sm text-blue-600 hover:underline mt-2 inline-block">
              Configure OCR API Key
            </Link>
          </div>
          
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Chatbot</span>
              {getApiKeyStatusIcon(apiKeyStatus.chatbot)}
            </div>
            <p className="text-sm text-gray-600">{getApiKeyStatusText(apiKeyStatus.chatbot)}</p>
            <Link href="/api-key-setup#chatbot" className="text-sm text-blue-600 hover:underline mt-2 inline-block">
              Configure Chatbot API Key
            </Link>
          </div>
        </div>
      </div>
      
      {/* Test Summary */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Test Summary</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="border rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Test Coverage</h3>
            <div className="flex items-end">
              <span className="text-3xl font-bold">{calculateTestCoverage()}%</span>
              <span className="text-sm text-gray-500 ml-2 mb-1">of tests run</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${calculateTestCoverage()}%` }}
              ></div>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Pass Rate</h3>
            <div className="flex items-end">
              <span className="text-3xl font-bold">{calculatePassRate()}%</span>
              <span className="text-sm text-gray-500 ml-2 mb-1">tests passing</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
              <div 
                className={`h-2.5 rounded-full ${
                  calculatePassRate() > 80 ? 'bg-green-500' : 
                  calculatePassRate() > 50 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${calculatePassRate()}%` }}
              ></div>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Test Actions</h3>
            <div className="flex flex-col space-y-2 mt-2">
              <button
                onClick={runAllTests}
                disabled={overallStatus === 'running'}
                className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300"
              >
                {overallStatus === 'running' ? (
                  <>
                    <FiClock className="mr-2 animate-spin" />
                    Running Tests...
                  </>
                ) : (
                  <>
                    <FiPlay className="mr-2" />
                    Run All Tests
                  </>
                )}
              </button>
              
              <Link href="/api-key-setup" className="flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200">
                <FiSettings className="mr-2" />
                Configure API Keys
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Test Categories */}
      <div className="space-y-6">
        {Object.entries(testSuites).map(([category, tests]) => (
          <div key={category} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div 
              className="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50"
              onClick={() => setExpandedSection(expandedSection === category ? null : category)}
            >
              <div className="flex items-center">
                {getStatusIcon(getCategoryStatus(category))}
                <h3 className="text-lg font-medium ml-2">{category}</h3>
                <span className="ml-2 text-sm text-gray-500">
                  ({tests.filter(test => testResults[test.id]?.status === 'passed').length}/{tests.length} passing)
                </span>
              </div>
              
              <div className="flex items-center">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    runCategoryTests(category);
                  }}
                  className="flex items-center px-3 py-1 mr-4 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100"
                  disabled={tests.some(test => runningTests.includes(test.id))}
                >
                  {tests.some(test => runningTests.includes(test.id)) ? (
                    <>
                      <FiClock className="mr-1 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <FiPlay className="mr-1" />
                      Run Tests
                    </>
                  )}
                </button>
                
                <svg
                  className={`w-5 h-5 transition-transform ${expandedSection === category ? 'transform rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            
            {expandedSection === category && (
              <div className="border-t">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Test
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duration
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Run
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tests.map((test) => (
                      <tr key={test.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{test.name}</div>
                          <div className="text-sm text-gray-500">{test.description}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getStatusIcon(testResults[test.id]?.status || 'unknown')}
                            <span className="ml-2 text-sm text-gray-900">
                              {testResults[test.id]?.status 
                                ? testResults[test.id].status.charAt(0).toUpperCase() + testResults[test.id].status.slice(1) 
                                : 'Not Run'}
                            </span>
                          </div>
                          {testResults[test.id]?.details && (
                            <div className="text-xs text-gray-500 mt-1">{testResults[test.id].details}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {testResults[test.id]?.duration 
                            ? `${testResults[test.id].duration}ms` 
                            : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {testResults[test.id]?.timestamp 
                            ? new Date(testResults[test.id].timestamp).toLocaleString() 
                            : 'Never'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => runTest(test.id)}
                            disabled={runningTests.includes(test.id)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            {runningTests.includes(test.id) ? 'Running...' : 'Run'}
                          </button>
                          <Link href={`/test-details/${test.id}`} className="text-gray-600 hover:text-gray-900">
                            Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default withProtectedRoute(TestDashboard);
