import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the MCP demo page
    router.push('/mcp-demo');
  }, [router]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">DevDocs MCP Demo</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-2">Welcome to the DevDocs MCP Demo</h2>
        <p className="text-gray-600 mb-4">
          This demo showcases the integration with Google Cloud's Model Context Protocol (MCP).
          You are being redirected to the MCP demo page...
        </p>

        <div className="mt-4">
          <Link href="/mcp-demo" className="inline-block px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Go to MCP Demo
          </Link>
        </div>
      </div>
    </div>
  );
}
