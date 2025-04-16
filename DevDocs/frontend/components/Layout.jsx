import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../providers/AuthProvider';

const Layout = ({ children }) => {
  const router = useRouter();
  const { user, signOut } = useAuth();

  // Create a demo user if none exists
  const demoUser = user || {
    email: 'demo@example.com',
    fullName: 'Demo User',
    role: 'user'
  };

  const handleSignOut = async () => {
    if (signOut) {
      await signOut();
    }
    router.push('/');
  };

  const isActive = (path) => {
    return router.pathname === path ? 'bg-blue-700' : '';
  };

  return (
    <AccessibilityWrapper>
      
    <div className="min-h-screen flex flex-col">
      <header className="bg-blue-600 text-white">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold">
            DevDocs
          </Link>

          <div className="flex items-center space-x-4">
            <span className="hidden md:inline">{demoUser.email}</span>
            <button
              onClick={handleSignOut}
              className="px-4 py-2 bg-blue-700 hover:bg-blue-800 rounded"
            >
              Sign Out
            </button>
          </div>
        </div>

        <nav className="bg-blue-800">
          <div className="container mx-auto px-4">
            <ul className="flex overflow-x-auto">
              <li>
                <Link href="/dashboard" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/dashboard')}`}>
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/test-upload" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-upload')}`}>
                  Upload
                </Link>
              </li>
              <li>
                <Link href="/test-document-understanding" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-document-understanding')}`}>
                  Document Understanding
                </Link>
              </li>
              <li>
                <Link href="/test-visualization" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-visualization')}`}>
                  Visualization
                </Link>
              </li>
              <li>
                <Link href="/test-portfolio" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-portfolio')}`}>
                  Portfolio
                </Link>
              </li>
              <li>
                <Link href="/test-sql-agent" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-sql-agent')}`}>
                  SQL Agent
                </Link>
              </li>
              <li>
                <Link href="/test-web-browser" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/test-web-browser')}`}>
                  Web Browser
                </Link>
              </li>
              <li>
                <Link href="/mcp-demo" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/mcp-demo')}`}>
                  MCP Demo
                </Link>
              </li>
              <li>
                <Link href="/dev-test-center" className={`block px-4 py-2 hover:bg-blue-700 ${isActive('/dev-test-center')}`}>
                  Testing
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </header>

      <main className="flex-grow">
        {children}
      </main>

      <footer className="bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4">
          <p className="text-center">© {new Date().getFullYear()} DevDocs. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
