import React from 'react';
import withProtectedRoute from '../components/ProtectedRoute';
import WebBrowser from '../components/WebBrowser';
import BrowsingProvider from '../providers/BrowsingProvider';

const TestWebBrowserPage = () => {
  return (
    <BrowsingProvider>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Web Browser</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-2">About the Web Browser</h2>
          <p className="text-gray-600 mb-4">
            The Web Browser allows you to browse financial websites, search for information, and extract financial data.
            You can bookmark pages, view your browsing history, and analyze financial data from web pages.
          </p>
          
          <div className="bg-blue-50 p-4 rounded-md">
            <h3 className="text-sm font-medium text-blue-800 mb-1">Suggested Financial Websites:</h3>
            <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
              <li>Yahoo Finance (finance.yahoo.com)</li>
              <li>MarketWatch (marketwatch.com)</li>
              <li>Investing.com (investing.com)</li>
              <li>Bloomberg (bloomberg.com)</li>
              <li>CNBC (cnbc.com)</li>
            </ul>
          </div>
        </div>
        
        <WebBrowser />
      </div>
    </BrowsingProvider>
  );
};

export default withProtectedRoute(TestWebBrowserPage);
