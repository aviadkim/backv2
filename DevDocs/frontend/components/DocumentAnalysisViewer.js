import React, { useState } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiFileText, FiDollarSign, FiPieChart, FiBarChart2, FiCalendar, FiDownload } from 'react-icons/fi';

const DocumentAnalysisViewer = ({ analysisResults }) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!analysisResults) {
    return (
      <AccessibilityWrapper>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center py-8">
            <FiFileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No document analysis available</h3>
            <p className="mt-1 text-sm text-gray-500">Upload a document to view analysis results.</p>
          </div>
        </div>
      </AccessibilityWrapper>
    );
  }

  const { document_info, company_info, financial_data, financial_ratios } = analysisResults;

  const renderOverviewTab = () => {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Document Information</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">File Name</p>
                <p className="text-sm font-medium text-gray-900">{document_info.file_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Title</p>
                <p className="text-sm font-medium text-gray-900">{document_info.title || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Company Information</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Company Name</p>
                <p className="text-sm font-medium text-gray-900">{company_info.name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Ticker Symbol</p>
                <p className="text-sm font-medium text-gray-900">{company_info.ticker || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Industry</p>
                <p className="text-sm font-medium text-gray-900">{company_info.industry || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Sector</p>
                <p className="text-sm font-medium text-gray-900">{company_info.sector || 'N/A'}</p>
              </div>
            </div>

            {company_info.description && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Description</p>
                <p className="text-sm text-gray-700">{company_info.description}</p>
              </div>
            )}

            {company_info.executives && company_info.executives.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-gray-500 mb-2">Key Executives</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {company_info.executives.map((executive, index) => (
                    <div key={index} className="text-sm">
                      <span className="font-medium">{executive.name}</span> - {executive.title}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Analysis Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <FiFileText className="h-8 w-8 text-blue-500 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Financial Statements</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {financial_data.financial_statements.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center">
                <FiDollarSign className="h-8 w-8 text-green-500 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Financial Metrics</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {financial_data.financial_metrics.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center">
                <FiPieChart className="h-8 w-8 text-purple-500 mr-2" />
                <div>
                  <p className="text-sm text-gray-500">Financial Ratios</p>
                  <p className="text-xl font-semibold text-gray-900">
                    {financial_ratios.length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Key Financial Metrics</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Metric
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
                {financial_data.financial_metrics.slice(0, 5).map((metric, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {metric.display_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {typeof metric.value === 'number'
                        ? new Intl.NumberFormat('en-US', {
                            style: metric.name.includes('ratio') ? 'decimal' : 'currency',
                            currency: 'USD',
                            maximumFractionDigits: 2
                          }).format(metric.value)
                        : metric.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.period}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {financial_data.financial_metrics.length > 5 && (
            <div className="mt-2 text-right">
              <button
                type="button"
                onClick={() => setActiveTab('metrics')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all metrics
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderFinancialStatementsTab = () => {
    return (
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Statements</h3>

        {financial_data.financial_statements.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <FiFileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">No financial statements found in this document.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {financial_data.financial_statements.map((statement, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                  <h4 className="text-md font-medium text-gray-900 capitalize">
                    {statement.type.replace('_', ' ')}
                  </h4>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Line Item
                        </th>
                        {statement.data[0]?.values.map((value, i) => (
                          <th key={i} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {value.period}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {statement.data.map((lineItem, lineIndex) => (
                        <tr key={lineIndex}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {lineItem.name}
                          </td>
                          {lineItem.values.map((value, valueIndex) => (
                            <td key={valueIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {value.value !== null
                                ? new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    maximumFractionDigits: 0
                                  }).format(value.value)
                                : 'N/A'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderMetricsTab = () => {
    return (
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Metrics</h3>

        {financial_data.financial_metrics.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <FiBarChart2 className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">No financial metrics found in this document.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Metric
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {financial_data.financial_metrics.map((metric, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {metric.display_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {typeof metric.value === 'number'
                        ? new Intl.NumberFormat('en-US', {
                            style: metric.name.includes('ratio') ? 'decimal' : 'currency',
                            currency: 'USD',
                            maximumFractionDigits: 2
                          }).format(metric.value)
                        : metric.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.period}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.source === 'table' ? 'Table' : 'Text'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <h3 className="text-lg font-medium text-gray-900 mt-8 mb-4">Financial Ratios</h3>

        {financial_ratios.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <FiPieChart className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">No financial ratios found in this document.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ratio
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {financial_ratios.map((ratio, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {ratio.display_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {typeof ratio.value === 'number'
                        ? ratio.name.includes('percentage') || ratio.name.includes('yield')
                          ? `${(ratio.value * 100).toFixed(2)}%`
                          : ratio.value.toFixed(2)
                        : ratio.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {ratio.period}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {ratio.source === 'table' ? 'Table' : 'Text'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const renderEntitiesTab = () => {
    return (
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Extracted Entities</h3>

        <div className="space-y-6">
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-2">Time Periods</h4>
            {financial_data.time_periods.length === 0 ? (
              <p className="text-sm text-gray-500">No time periods found in this document.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {financial_data.time_periods.map((period, index) => (
                  <div key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    <FiCalendar className="mr-1 h-4 w-4" />
                    {period.text}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="text-md font-medium text-gray-900 mb-2">Organizations</h4>
            {financial_data.entities.organizations.length === 0 ? (
              <p className="text-sm text-gray-500">No organizations found in this document.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {financial_data.entities.organizations.map((org, index) => (
                  <div key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    {org.text}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h4 className="text-md font-medium text-gray-900 mb-2">Currencies</h4>
            {financial_data.entities.currencies.length === 0 ? (
              <p className="text-sm text-gray-500">No currencies found in this document.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Text
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {financial_data.entities.currencies.slice(0, 10).map((currency, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {currency.text}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {currency.value !== null
                            ? new Intl.NumberFormat('en-US', {
                                style: 'decimal',
                                maximumFractionDigits: 2
                              }).format(currency.value)
                            : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'overview'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-label="Overview tab"
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('statements')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'statements'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-label="Financial Statements tab"
            >
              Financial Statements
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'metrics'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-label="Metrics & Ratios tab"
            >
              Metrics & Ratios
            </button>
            <button
              onClick={() => setActiveTab('entities')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'entities'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-label="Entities tab"
            >
              Entities
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'statements' && renderFinancialStatementsTab()}
          {activeTab === 'metrics' && renderMetricsTab()}
          {activeTab === 'entities' && renderEntitiesTab()}
        </div>

        <div className="bg-gray-50 px-6 py-3 flex justify-end">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            aria-label="Export Analysis"
          >
            <FiDownload className="mr-2 -ml-1 h-5 w-5" />
            Export Analysis
          </button>
        </div>
      </div>
    </AccessibilityWrapper>
  );
};

export default DocumentAnalysisViewer;
