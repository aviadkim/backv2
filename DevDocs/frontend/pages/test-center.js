import { useState } from 'react';
import Head from 'next/head';
import TestRunner from '../components/TestRunner';
import { FaClipboardCheck, FaCode, FaBug, FaRocket } from 'react-icons/fa';

export default function TestCenter() {
  const [activeTab, setActiveTab] = useState('tests');
  
  const tabs = [
    { id: 'tests', name: 'Tests', icon: <FaClipboardCheck /> },
    { id: 'code', name: 'Code Quality', icon: <FaCode /> },
    { id: 'bugs', name: 'Bug Reports', icon: <FaBug /> },
    { id: 'deploy', name: 'Deployment', icon: <FaRocket /> }
  ];
  
  return (
    <div>
      <Head>
        <title>Test Center | DevDocs</title>
        <meta name="description" content="Test Center for DevDocs" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Test Center</h1>
        
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`
                  flex items-center pb-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                `}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
        
        {/* Tab Content */}
        <div>
          {activeTab === 'tests' && (
            <TestRunner />
          )}
          
          {activeTab === 'code' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Code Quality</h2>
              <p className="text-gray-500 mb-4">
                This section will show code quality metrics and linting results.
              </p>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-center text-gray-500">
                  Code quality analysis will be available soon.
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'bugs' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Bug Reports</h2>
              <p className="text-gray-500 mb-4">
                This section will show bug reports and allow you to create new ones.
              </p>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-center text-gray-500">
                  Bug reporting will be available soon.
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'deploy' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Deployment</h2>
              <p className="text-gray-500 mb-4">
                This section will show deployment status and allow you to deploy the application.
              </p>
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-center text-gray-500">
                  Deployment features will be available soon.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
