import React from 'react';
import Link from 'next/link';
import { FiFileText, FiUpload, FiBarChart2, FiPieChart, FiDatabase, FiServer } from 'react-icons/fi';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Document Understanding Demo</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">Welcome to the Document Understanding Demo</h2>
        <p className="text-gray-600 mb-4">
          This demo showcases our Document Understanding Engine's capabilities for analyzing financial documents.
          You can explore the following demos:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <Link href="/document-demo" className="block p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-200 transition-colors">
            <div className="flex items-center mb-2">
              <FiUpload className="text-blue-500 mr-2 text-xl" />
              <h3 className="font-medium text-gray-900">Document Upload Demo</h3>
            </div>
            <p className="text-sm text-gray-600">
              Upload and analyze financial documents. Test our document understanding capabilities with your own files.
            </p>
          </Link>

          <Link href="/messos-demo" className="block p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-200 transition-colors">
            <div className="flex items-center mb-2">
              <FiFileText className="text-blue-500 mr-2 text-xl" />
              <h3 className="font-medium text-gray-900">Messos Financial Document Analysis</h3>
            </div>
            <p className="text-sm text-gray-600">
              View and analyze the Messos financial document. See how our system extracts and presents financial data.
            </p>
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">About Document Understanding</h2>
        <p className="text-gray-600 mb-4">
          Our Document Understanding Engine can analyze financial documents such as PDFs, Excel spreadsheets, and CSV files.
          It extracts financial data, identifies entities, recognizes financial statements, and provides insights into your financial documents.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="bg-blue-50 p-4 rounded-md">
            <h3 className="text-md font-medium text-gray-900 mb-2 flex items-center">
              <FiBarChart2 className="text-blue-500 mr-2" />
              Key Features
            </h3>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              <li>Automatic financial data extraction</li>
              <li>Entity recognition (companies, dates, amounts)</li>
              <li>Financial statement classification</li>
              <li>Financial metrics calculation</li>
              <li>Multi-document comparison</li>
              <li>Historical trend analysis</li>
            </ul>
          </div>

          <div className="bg-blue-50 p-4 rounded-md">
            <h3 className="text-md font-medium text-gray-900 mb-2 flex items-center">
              <FiFileText className="text-blue-500 mr-2" />
              Supported Document Types
            </h3>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
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

        <div className="mt-6 border-t border-gray-200 pt-6">
          <h3 className="text-md font-medium text-gray-900 mb-2">Technology Stack</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="flex items-center">
              <FiDatabase className="text-blue-500 mr-2" />
              <span className="text-sm text-gray-600">Supabase Database</span>
            </div>
            <div className="flex items-center">
              <FiServer className="text-blue-500 mr-2" />
              <span className="text-sm text-gray-600">Next.js Framework</span>
            </div>
            <div className="flex items-center">
              <FiPieChart className="text-blue-500 mr-2" />
              <span className="text-sm text-gray-600">Data Visualization</span>
            </div>
            <div className="flex items-center">
              <FiBarChart2 className="text-blue-500 mr-2" />
              <span className="text-sm text-gray-600">Financial Analysis</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
