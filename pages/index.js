import React from 'react';

export default function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Document Understanding Demo</h1>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '10px' }}>Welcome to the Document Understanding Demo</h2>
        <p style={{ marginBottom: '15px' }}>
          This demo showcases our Document Understanding Engine's capabilities for analyzing financial documents.
          You can explore the following demos:
        </p>
        
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li style={{ marginBottom: '10px' }}>
            <a href="/document-demo" style={{ color: 'blue', textDecoration: 'underline' }}>
              Document Upload Demo
            </a>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Upload and analyze financial documents
            </p>
          </li>
          <li style={{ marginBottom: '10px' }}>
            <a href="/messos-demo" style={{ color: 'blue', textDecoration: 'underline' }}>
              Messos Financial Document Analysis
            </a>
            <p style={{ fontSize: '14px', color: '#666' }}>
              View and analyze the Messos financial document
            </p>
          </li>
        </ul>
      </div>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2 style={{ marginBottom: '10px' }}>About Document Understanding</h2>
        <p style={{ marginBottom: '15px' }}>
          Our Document Understanding Engine can analyze financial documents such as PDFs, Excel spreadsheets, and CSV files.
          It extracts financial data, identifies entities, recognizes financial statements, and provides insights into your financial documents.
        </p>
        
        <div style={{ backgroundColor: '#E6F7FF', padding: '15px', borderRadius: '6px' }}>
          <h3 style={{ marginBottom: '5px', fontSize: '14px' }}>Supported Document Types:</h3>
          <ul style={{ paddingLeft: '20px', fontSize: '14px' }}>
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
    </div>
  );
}
