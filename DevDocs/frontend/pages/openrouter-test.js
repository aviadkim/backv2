import React from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';
import OpenRouterKeyManager from '../components/OpenRouterKeyManager';
import OpenRouterTest from '../components/OpenRouterTest';

export default function OpenRouterTestPage() {
  return (
    <FinDocLayout>
      <Head>
        <title>OpenRouter Test | FinDoc Analyzer</title>
      </Head>
      
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">OpenRouter API Test</h1>
        
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <h2 className="text-lg font-medium text-blue-800 mb-2">About OpenRouter</h2>
          <p className="text-sm text-blue-700">
            OpenRouter provides access to 300+ AI models including Optimus Alpha. 
            This page allows you to configure the API key and test the connection.
          </p>
        </div>
        
        <div className="space-y-6">
          <OpenRouterKeyManager />
          <OpenRouterTest />
        </div>
      </div>
    </FinDocLayout>
  );
}
