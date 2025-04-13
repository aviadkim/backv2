import React from 'react';
import { useAuth } from '../providers/AuthProvider';
import Layout from '../components/Layout';
import MCPDemo from '../components/MCPDemo';

const MCPDemoPage = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">MCP Integration Demo</h1>
        
        <div className="mb-6">
          <p className="text-gray-700">
            This page demonstrates the integration with Google Cloud's Model Context Protocol (MCP).
            You can use the search box below to query information from the web and your document repository.
          </p>
        </div>
        
        <MCPDemo />
      </div>
    </Layout>
  );
};

export default MCPDemoPage;
