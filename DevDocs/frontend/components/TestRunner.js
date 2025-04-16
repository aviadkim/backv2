import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';

import { useState, useEffect } from 'react';
import { FaCheckCircle, FaTimesCircle, FaExclamationTriangle, FaSpinner } from 'react-icons/fa';

const TestRunner = () => {
  const [tests, setTests] = useState([]);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [autoFix, setAutoFix] = useState(false);

  // Test categories
  const categories = [
    { id: 'all', name: 'All Tests' },
    { id: 'ui', name: 'UI Components' },
    { id: 'functionality', name: 'Functionality' },
    { id: 'integration', name: 'Integration' }
  ];

  // Mock tests
  const mockTests = [
    // UI Tests
    { id: 'layout-components', category: 'ui', name: 'Layout Components', description: 'Tests the layout components like header, footer, and sidebar' },
    { id: 'form-components', category: 'ui', name: 'Form Components', description: 'Tests form components like inputs, buttons, and validation' },
    { id: 'data-display', category: 'ui', name: 'Data Display Components', description: 'Tests components that display data like tables, charts, and cards' },

    // Functionality Tests
    { id: 'document-upload', category: 'functionality', name: 'Document Upload', description: 'Tests document upload functionality with mocked API responses' },
    { id: 'data-processing', category: 'functionality', name: 'Data Processing', description: 'Tests data processing functionality with sample data' },
    { id: 'report-generation', category: 'functionality', name: 'Report Generation', description: 'Tests report generation with sample data' },

    // Integration Tests
    { id: 'workflow', category: 'integration', name: 'User Workflow', description: 'Tests complete user workflows from upload to report generation' },
    { id: 'error-handling', category: 'integration', name: 'Error Handling', description: 'Tests error handling across the application' }
  ];

  // Load tests
  useEffect(() => {
    setTests(mockTests);
  }, []);

  // Filter tests by category
  const filteredTests = selectedCategory === 'all'
    ? tests
    : tests.filter(test => test.category === selectedCategory);

  // Run tests
  const runTests = async () => {
    setRunning(true);
    setResults({});

    // Mock test results
    const mockResults = {
      'layout-components': { success: true, message: 'All layout components render correctly' },
      'form-components': { success: true, message: 'All form components work correctly' },
      'data-display': { success: false, message: 'Chart component fails to render with empty data', fix: 'Update Chart component to handle empty data gracefully' },
      'document-upload': { success: true, message: 'Document upload works correctly with mocked API' },
      'data-processing': { success: true, message: 'Data processing works correctly with sample data' },
      'report-generation': { success: false, message: 'Data formatting does not handle currency correctly', fix: 'Update data formatting to handle currency correctly' },
      'workflow': { success: true, message: 'User workflow works correctly' },
      'error-handling': { success: false, message: 'Validation error handling does not display user-friendly messages', fix: 'Update validation error handling to display user-friendly messages' }
    };

    // Simulate running tests
    for (const test of filteredTests) {
      // Update UI to show test is running
      setResults(prev => ({
        ...prev,
        [test.id]: { running: true }
      }));

      // Simulate test execution time
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Update results
      setResults(prev => ({
        ...prev,
        [test.id]: mockResults[test.id] || { success: true, message: 'Test passed' }
      }));
    }

    setRunning(false);

    // Auto-fix if enabled
    if (autoFix) {
      await fixIssues();
    }
  };

  // Fix issues
  const fixIssues = async () => {
    const failedTests = Object.entries(results)
      .filter(([_, result]) => !result.success && result.fix)
      .map(([id, result]) => ({ id, ...result }));

    if (failedTests.length === 0) {
      return;
    }

    // Simulate fixing issues
    for (const test of failedTests) {
      // Update UI to show fix is in progress
      setResults(prev => ({
        ...prev,
        [test.id]: { ...prev[test.id], fixing: true }
      }));

      // Simulate fix execution time
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Update results
      setResults(prev => ({
        ...prev,
        [test.id]: { success: true, message: 'Issue fixed automatically', fixed: true }
      }));
    }
  };

  // Get test status
  const getTestStatus = (testId) => {
    const result = results[testId];

    if (!result) {
      return 'pending';
    }

    if (result.running) {
      return 'running';
    }

    if (result.fixing) {
      return 'fixing';
    }

    if (result.success) {
      return result.fixed ? 'fixed' : 'passed';
    }

    return 'failed';
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <FaCheckCircle className="text-green-500" />;
      case 'failed':
        return <FaTimesCircle className="text-red-500" />;
      case 'fixed':
        return <FaCheckCircle className="text-yellow-500" />;
      case 'running':
      case 'fixing':
        return <FaSpinner className="text-blue-500 animate-spin" />;
      default:
        return <FaExclamationTriangle className="text-gray-300" />;
    }
  };

  // Get summary
  const getSummary = () => {
    const total = filteredTests.length;
    const completed = Object.keys(results).filter(id =>
      filteredTests.some(test => test.id === id) &&
      !results[id].running &&
      !results[id].fixing
    ).length;

    const passed = Object.entries(results).filter(([id, result]) =>
      filteredTests.some(test => test.id === id) &&
      result.success
    ).length;

    const failed = Object.entries(results).filter(([id, result]) =>
      filteredTests.some(test => test.id === id) &&
      !result.success &&
      !result.running &&
      !result.fixing
    ).length;

    const fixed = Object.entries(results).filter(([id, result]) =>
      filteredTests.some(test => test.id === id) &&
      result.fixed
    ).length;

    return { total, completed, passed, failed, fixed };
  };

  const summary = getSummary();

  return (
    <AccessibilityWrapper>
      <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Test Runner</h2>

      {/* Controls */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            id="category"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            disabled={running}
          >
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-end">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              checked={autoFix}
              onChange={(e) => setAutoFix(e.target.checked)}
              disabled={running}
            />
            <span className="ml-2 text-sm text-gray-700">Auto-fix issues</span>
          </label>
        </div>

        <div className="flex items-end ml-auto">
          <button
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            onClick={runTests}
            disabled={running || filteredTests.length === 0}
          >
            {running ? (
              <>
                <FaSpinner className="animate-spin -ml-1 mr-2 h-4 w-4" />
                Running...
              </>
            ) : (
              'Run Tests'
            )}
          </button>
        </div>
      </div>

      {/* Summary */}
      {Object.keys(results).length > 0 && (
        <div className="bg-gray-50 p-4 rounded-md mb-6">
          <h3 className="text-lg font-medium mb-2">Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-500">Total</div>
              <div className="text-2xl font-bold">{summary.total}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Passed</div>
              <div className="text-2xl font-bold text-green-600">{summary.passed}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Failed</div>
              <div className="text-2xl font-bold text-red-600">{summary.failed}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Fixed</div>
              <div className="text-2xl font-bold text-yellow-600">{summary.fixed}</div>
            </div>
          </div>
        </div>
      )}

      {/* Test List */}
      <div className="border rounded-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Test
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredTests.length === 0 ? (
              <tr>
                <td colSpan="3" className="px-6 py-4 text-center text-sm text-gray-500">
                  No tests found for this category
                </td>
              </tr>
            ) : (
              filteredTests.map(test => {
                const status = getTestStatus(test.id);
                const result = results[test.id] || {};

                return (
                  <tr key={test.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {test.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {test.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <span className="mr-2">
                          {getStatusIcon(status)}
                        </span>
                        <span>
                          {status === 'passed' && 'Passed'}
                          {status === 'failed' && 'Failed'}
                          {status === 'fixed' && 'Fixed'}
                          {status === 'running' && 'Running...'}
                          {status === 'fixing' && 'Fixing...'}
                          {status === 'pending' && 'Pending'}
                        </span>
                      </div>
                      {status === 'failed' && result.message && (
                        <div className="mt-1 text-xs text-red-600">
                          {result.message}
                        </div>
                      )}
                      {status === 'failed' && result.fix && (
                        <div className="mt-1 text-xs text-yellow-600">
                          Fix: {result.fix}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default TestRunner;
