import React, { useState } from 'react';
import DocumentUploader from '../components/DocumentUploader';
import DocumentAnalysisViewer from '../components/DocumentAnalysisViewer';

const DocumentDemo = () => {
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleDocumentProcessed = (data) => {
    // Set mock analysis results for demo purposes
    // In a real application, this would come from the backend
    setAnalysisResults({
      document_info: {
        file_name: data.document_info.file_name,
        title: data.document_info.title || "Financial Report"
      },
      company_info: {
        name: "Demo Company Inc.",
        ticker: "DEMO",
        industry: "Technology",
        sector: "Software",
        description: "This is a demonstration of the document understanding capabilities. In a real application, this information would be extracted from the uploaded document.",
        executives: [
          { name: "John Doe", title: "CEO" },
          { name: "Jane Smith", title: "CFO" }
        ]
      },
      financial_data: {
        financial_statements: [
          {
            type: "income_statement",
            page: 1,
            data: [
              {
                name: "Revenue",
                row_label: "Revenue",
                values: [
                  { period: "2023", value: 1000000 },
                  { period: "2022", value: 800000 }
                ]
              },
              {
                name: "Cost of Revenue",
                row_label: "Cost of Revenue",
                values: [
                  { period: "2023", value: 600000 },
                  { period: "2022", value: 500000 }
                ]
              },
              {
                name: "Gross Profit",
                row_label: "Gross Profit",
                values: [
                  { period: "2023", value: 400000 },
                  { period: "2022", value: 300000 }
                ]
              },
              {
                name: "Operating Expenses",
                row_label: "Operating Expenses",
                values: [
                  { period: "2023", value: 200000 },
                  { period: "2022", value: 150000 }
                ]
              },
              {
                name: "Net Income",
                row_label: "Net Income",
                values: [
                  { period: "2023", value: 200000 },
                  { period: "2022", value: 150000 }
                ]
              }
            ]
          },
          {
            type: "balance_sheet",
            page: 2,
            data: [
              {
                name: "Cash and Cash Equivalents",
                row_label: "Cash and Cash Equivalents",
                values: [
                  { period: "2023", value: 500000 },
                  { period: "2022", value: 400000 }
                ]
              },
              {
                name: "Total Assets",
                row_label: "Total Assets",
                values: [
                  { period: "2023", value: 2000000 },
                  { period: "2022", value: 1500000 }
                ]
              },
              {
                name: "Total Liabilities",
                row_label: "Total Liabilities",
                values: [
                  { period: "2023", value: 1000000 },
                  { period: "2022", value: 800000 }
                ]
              },
              {
                name: "Total Shareholders' Equity",
                row_label: "Total Shareholders' Equity",
                values: [
                  { period: "2023", value: 1000000 },
                  { period: "2022", value: 700000 }
                ]
              }
            ]
          }
        ],
        financial_metrics: [
          {
            name: "revenue",
            display_name: "Revenue",
            value: 1000000,
            period: "2023",
            source: "table"
          },
          {
            name: "net_income",
            display_name: "Net Income",
            value: 200000,
            period: "2023",
            source: "table"
          },
          {
            name: "total_assets",
            display_name: "Total Assets",
            value: 2000000,
            period: "2023",
            source: "table"
          },
          {
            name: "total_liabilities",
            display_name: "Total Liabilities",
            value: 1000000,
            period: "2023",
            source: "table"
          },
          {
            name: "shareholders_equity",
            display_name: "Shareholders' Equity",
            value: 1000000,
            period: "2023",
            source: "table"
          }
        ],
        time_periods: [
          { text: "2023", source: "table_header" },
          { text: "2022", source: "table_header" }
        ],
        entities: {
          currencies: [
            { text: "$1,000,000", value: 1000000, start: 100, end: 110 },
            { text: "$200,000", value: 200000, start: 200, end: 208 }
          ],
          percentages: [
            { text: "20%", value: 0.2, start: 300, end: 303 },
            { text: "15%", value: 0.15, start: 400, end: 403 }
          ],
          dates: [
            { text: "2023-12-31", value: "2023-12-31", start: 500, end: 510 },
            { text: "2022-12-31", value: "2022-12-31", start: 600, end: 610 }
          ],
          numbers: [
            { text: "1,000,000", value: 1000000, start: 700, end: 709 },
            { text: "200,000", value: 200000, start: 800, end: 807 }
          ],
          organizations: [
            { text: "Demo Company Inc.", start: 900, end: 917, label: "ORG" }
          ]
        }
      },
      financial_ratios: [
        {
          name: "gross_margin",
          display_name: "Gross Margin",
          value: 0.4,
          period: "2023",
          source: "calculated"
        },
        {
          name: "net_margin",
          display_name: "Net Margin",
          value: 0.2,
          period: "2023",
          source: "calculated"
        },
        {
          name: "return_on_equity",
          display_name: "Return on Equity",
          value: 0.2,
          period: "2023",
          source: "calculated"
        },
        {
          name: "debt_to_equity",
          display_name: "Debt to Equity",
          value: 1.0,
          period: "2023",
          source: "calculated"
        }
      ]
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Document Understanding Demo</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">About This Demo</h2>
        <p className="text-gray-600 mb-4">
          This demo showcases our Document Understanding Engine's capabilities for analyzing financial documents.
          Upload a financial document (PDF, Excel, or CSV) to see how the system extracts and analyzes financial data.
        </p>

        <div className="bg-yellow-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-yellow-800 mb-1">Demo Mode Notice:</h3>
          <p className="text-sm text-yellow-700">
            This is a demonstration with mock data. In a real application, the analysis would be performed on your actual uploaded document.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <DocumentUploader onDocumentProcessed={handleDocumentProcessed} />

        {analysisResults && (
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Document Analysis Results</h2>
            <DocumentAnalysisViewer analysisResults={analysisResults} />
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentDemo;
