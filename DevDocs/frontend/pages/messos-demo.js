import React, { useState } from 'react';
import { FiFileText, FiDownload, FiExternalLink, FiBarChart2 } from 'react-icons/fi';
import DocumentAnalysisViewer from '../components/DocumentAnalysisViewer';

const MessosDemo = () => {
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleAnalyze = () => {
    setShowAnalysis(true);

    // Set mock analysis results
    setAnalysisResults({
      document_info: {
        file_name: "Messos 28.02.2025.pdf",
        title: "Financial Statement",
        date: "2025-02-28",
        pages: 12
      },
      company_info: {
        name: "Messos Group",
        ticker: "MSG",
        industry: "Technology",
        sector: "Software",
        description: "Messos Group is a leading technology company specializing in financial software solutions."
      },
      financial_data: {
        financial_statements: [
          {
            type: "income_statement",
            page: 3,
            data: [
              {
                name: "Revenue",
                row_label: "Revenue",
                values: [
                  { period: "2025", value: 1234567 },
                  { period: "2024", value: 1000000 }
                ]
              },
              {
                name: "Cost of Revenue",
                row_label: "Cost of Revenue",
                values: [
                  { period: "2025", value: 700000 },
                  { period: "2024", value: 600000 }
                ]
              },
              {
                name: "Gross Profit",
                row_label: "Gross Profit",
                values: [
                  { period: "2025", value: 534567 },
                  { period: "2024", value: 400000 }
                ]
              },
              {
                name: "Operating Expenses",
                row_label: "Operating Expenses",
                values: [
                  { period: "2025", value: 300000 },
                  { period: "2024", value: 250000 }
                ]
              },
              {
                name: "Net Income",
                row_label: "Net Income",
                values: [
                  { period: "2025", value: 234567 },
                  { period: "2024", value: 150000 }
                ]
              }
            ]
          },
          {
            type: "balance_sheet",
            page: 5,
            data: [
              {
                name: "Cash and Cash Equivalents",
                row_label: "Cash and Cash Equivalents",
                values: [
                  { period: "2025", value: 800000 },
                  { period: "2024", value: 600000 }
                ]
              },
              {
                name: "Total Assets",
                row_label: "Total Assets",
                values: [
                  { period: "2025", value: 3456789 },
                  { period: "2024", value: 3000000 }
                ]
              },
              {
                name: "Total Liabilities",
                row_label: "Total Liabilities",
                values: [
                  { period: "2025", value: 1456789 },
                  { period: "2024", value: 1200000 }
                ]
              },
              {
                name: "Total Shareholders' Equity",
                row_label: "Total Shareholders' Equity",
                values: [
                  { period: "2025", value: 2000000 },
                  { period: "2024", value: 1800000 }
                ]
              }
            ]
          }
        ],
        financial_metrics: [
          {
            name: "revenue",
            display_name: "Revenue",
            value: 1234567,
            period: "2025",
            source: "table"
          },
          {
            name: "net_income",
            display_name: "Net Income",
            value: 234567,
            period: "2025",
            source: "table"
          },
          {
            name: "total_assets",
            display_name: "Total Assets",
            value: 3456789,
            period: "2025",
            source: "table"
          },
          {
            name: "total_liabilities",
            display_name: "Total Liabilities",
            value: 1456789,
            period: "2025",
            source: "table"
          }
        ],
        time_periods: [
          { text: "2025", source: "table_header" },
          { text: "2024", source: "table_header" }
        ]
      },
      financial_ratios: [
        {
          name: "gross_margin",
          display_name: "Gross Margin",
          value: 0.425,
          period: "2025",
          source: "calculated"
        },
        {
          name: "net_margin",
          display_name: "Net Margin",
          value: 0.19,
          period: "2025",
          source: "calculated"
        },
        {
          name: "return_on_equity",
          display_name: "Return on Equity",
          value: 0.158,
          period: "2025",
          source: "calculated"
        },
        {
          name: "debt_to_equity",
          display_name: "Debt to Equity",
          value: 0.73,
          period: "2025",
          source: "calculated"
        }
      ]
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Messos Financial Document Analysis</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">About This Demo</h2>
        <p className="text-gray-600 mb-4">
          This demo showcases our Document Understanding Engine's capabilities for analyzing the Messos financial document.
        </p>

        <div className="bg-yellow-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-yellow-800 mb-1">Demo Mode Notice:</h3>
          <p className="text-sm text-yellow-700">
            This is a demonstration with mock analysis results. In a real application, the analysis would be performed on the actual document.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <FiFileText className="mr-2" />
              Messos Financial Document
            </h3>
          </div>
          <div className="p-4">
            <div className="aspect-w-16 aspect-h-9 mb-4">
              <div className="w-full h-[400px] border border-gray-200 rounded flex items-center justify-center bg-gray-50">
                <p className="text-gray-500">PDF Viewer would appear here</p>
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={handleAnalyze}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <FiBarChart2 className="mr-2" />
                Analyze Document
              </button>

              <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                <FiDownload className="mr-2" />
                Download PDF
              </button>

              <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                <FiExternalLink className="mr-2" />
                Open in New Tab
              </button>
            </div>
          </div>
        </div>

        {showAnalysis && analysisResults && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Analysis Results</h3>
            </div>
            <div className="p-4">
              <DocumentAnalysisViewer analysisResults={analysisResults} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessosDemo;
