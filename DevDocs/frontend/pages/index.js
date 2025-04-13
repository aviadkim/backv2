import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Layout from '../components/Layout';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the dashboard page
    router.push('/dashboard');
  }, [router]);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">DevDocs Financial Document Analysis</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-2">Welcome to DevDocs</h2>
          <p className="text-gray-600 mb-4">
            This application helps financial professionals analyze documents, manage portfolios, and generate reports.
            You are being redirected to the dashboard...
          </p>

          <div className="mt-4 flex space-x-4">
            <Link href="/dashboard" className="inline-block px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
              Go to Dashboard
            </Link>
            <Link href="/mcp-demo" className="inline-block px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
              MCP Demo
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
