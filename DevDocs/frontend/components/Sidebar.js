import React from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  FaHome,
  FaFileUpload,
  FaChartBar,
  FaFileAlt,
  FaCog,
  FaClipboardCheck,
  FaUserCircle,
  FaBars,
  FaTimes,
  FaRobot,
  FaFileInvoiceDollar
} from 'react-icons/fa';

const Sidebar = () => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: FaHome },
    { name: 'Upload Documents', href: '/upload', icon: FaFileUpload },
    { name: 'Analytics', href: '/analytics', icon: FaChartBar },
    { name: 'Reports', href: '/reports', icon: FaFileAlt },
    { name: 'RAG Processor', href: '/rag-processor', icon: FaRobot },
    { name: 'Financial Analysis', href: '/financial-analysis', icon: FaFileInvoiceDollar },
    { name: 'Testing', href: '/test-center', icon: FaClipboardCheck },
    { name: 'Dev Testing', href: '/dev-test-center', icon: FaClipboardCheck },
    { name: 'MCP Demo', href: '/mcp-demo', icon: FaFileAlt },
    { name: 'MCP Test', href: '/mcp-test', icon: FaFileAlt },
    { name: 'Settings', href: '/settings', icon: FaCog },
  ];

  // Secondary navigation links
  const secondaryNavigation = [
    { name: 'Help', href: '/help' },
    { name: 'Documentation', href: '/docs' },
    { name: 'API Keys', href: '/api-key-setup' },
    { name: 'OpenRouter Test', href: '/openrouter-test' },
  ];

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <AccessibilityWrapper>
      <>
      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          type="button"
          className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
          onClick={toggleSidebar}
        >
          <span className="sr-only">Open sidebar</span>
          {isOpen ? <FaTimes className="h-6 w-6" /> : <FaBars className="h-6 w-6" />}
        </button>
      </div>

      {/* Sidebar for mobile */}
      <div className={`md:hidden fixed inset-0 flex z-40 ${isOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={toggleSidebar}></div>

        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-gray-800">
          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div className="flex-shrink-0 flex items-center px-4">
              <h1 className="text-white text-xl font-bold">DevDocs</h1>
            </div>
            <nav className="mt-5 px-2 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-base font-medium rounded-md ${
                    router.pathname === item.href
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <item.icon
                    className={`mr-4 flex-shrink-0 h-6 w-6 ${
                      router.pathname === item.href
                        ? 'text-white'
                        : 'text-gray-400 group-hover:text-gray-300'
                    }`}
                  />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-700 p-4">
            <Link href="/profile" className="flex-shrink-0 group block">
              <div className="flex items-center">
                <div>
                  <FaUserCircle className="h-9 w-9 text-gray-400" />
                </div>
                <div className="ml-3">
                  <p className="text-base font-medium text-white">User Profile</p>
                  <p className="text-sm font-medium text-gray-400 group-hover:text-gray-300">
                    View profile
                  </p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-gray-800">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-white text-xl font-bold">DevDocs</h1>
            </div>
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    router.pathname === item.href
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <item.icon
                    className={`mr-3 flex-shrink-0 h-6 w-6 ${
                      router.pathname === item.href
                        ? 'text-white'
                        : 'text-gray-400 group-hover:text-gray-300'
                    }`}
                  />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-700 p-4">
            <Link href="/profile" className="flex-shrink-0 w-full group block">
              <div className="flex items-center">
                <div>
                  <FaUserCircle className="h-9 w-9 text-gray-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-white">User Profile</p>
                  <p className="text-xs font-medium text-gray-400 group-hover:text-gray-300">
                    View profile
                  </p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </>
    </AccessibilityWrapper>
  );
};

export default Sidebar;
