import React from 'react';
import withProtectedRoute from '../components/ProtectedRoute';
import SQLReasoningAgent from '../components/SQLReasoningAgent';

const TestSQLAgentPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">SQL Reasoning Agent</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">About the SQL Reasoning Agent</h2>
        <p className="text-gray-600 mb-4">
          The SQL Reasoning Agent allows you to query your financial data using natural language.
          Simply ask questions about your portfolio, holdings, performance, or documents, and the agent
          will generate SQL queries and provide insights based on the results.
        </p>
        
        <div className="bg-blue-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-blue-800 mb-1">Example Questions:</h3>
          <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
            <li>What is the total value of my portfolio?</li>
            <li>Show me my asset allocation by sector</li>
            <li>What are my top 5 performing holdings?</li>
            <li>How has my portfolio performed over the last 30 days?</li>
            <li>Which documents contain information about Apple Inc.?</li>
          </ul>
        </div>
      </div>
      
      <SQLReasoningAgent />
    </div>
  );
};

export default withProtectedRoute(TestSQLAgentPage);
