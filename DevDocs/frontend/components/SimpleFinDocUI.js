import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

const SimpleFinDocUI = ({ children }) => {
  const router = useRouter();
  const [user, setUser] = useState({ name: 'Aviad B.', role: 'Administrator' });

  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Upload Documents', path: '/upload' },
    { name: 'Document Comparison', path: '/document-comparison' },
    { name: 'Document Integration', path: '/document-integration' },
    { name: 'OCR Tool', path: '/ocr-tool' },
    { name: 'Data Export', path: '/data-export' },
    { name: 'Financial Advisor', path: '/financial-advisor' },
    { name: 'Query Engine', path: '/query-engine' },
    { name: 'Analytics', path: '/analytics' },
    { name: 'Reports', path: '/reports' },
    { name: 'Financial Testing', path: '/financial-test-center' },
    { name: 'Testing', path: '/test-center' },
    { name: 'Dev Testing', path: '/dev-test-center' },
    { name: 'Settings', path: '/settings' },
  ];

  return (
    <div className="findoc-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="app-title">FinDoc Analyzer</h1>
        </div>
        <nav className="sidebar-nav">
          <ul>
            {navItems.map((item) => (
              <li key={item.name} className={router.pathname === item.path ? 'active' : ''}>
                <a href={item.path} onClick={(e) => { e.preventDefault(); router.push(item.path); }}>
                  <span className="icon">
                    {item.name === 'Dashboard' && '📊'}
                    {item.name === 'Upload Documents' && '📤'}
                    {item.name === 'Document Comparison' && '🔄'}
                    {item.name === 'Document Integration' && '📋'}
                    {item.name === 'OCR Tool' && '📖'}
                    {item.name === 'Data Export' && '📂'}
                    {item.name === 'Financial Advisor' && '🧠'}
                    {item.name === 'Query Engine' && '🔍'}
                    {item.name === 'Analytics' && '📈'}
                    {item.name === 'Reports' && '📄'}
                    {item.name === 'Financial Testing' && '💰'}
                    {item.name === 'Testing' && '🧪'}
                    {item.name === 'Dev Testing' && '⚙️'}
                    {item.name === 'Settings' && '⚙️'}
                  </span>
                  <span>{item.name}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user.name.split(' ').map(n => n[0]).join('')}</div>
            <div className="user-details">
              <div className="user-name">{user.name}</div>
              <div className="user-role">{user.role}</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>

      <style jsx>{`
        .findoc-layout {
          display: flex;
          min-height: 100vh;
          background-color: #f7f9fc;
          color: #333;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .sidebar {
          width: 250px;
          background-color: #2c3e50;
          color: white;
          display: flex;
          flex-direction: column;
          position: fixed;
          height: 100vh;
        }

        .sidebar-header {
          padding: 20px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .app-title {
          margin: 0;
          font-size: 24px;
          font-weight: bold;
        }

        .sidebar-nav {
          flex: 1;
          padding: 20px 0;
        }

        .sidebar-nav ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .sidebar-nav li {
          margin-bottom: 5px;
        }

        .sidebar-nav a {
          display: flex;
          align-items: center;
          padding: 10px 20px;
          color: #ecf0f1;
          text-decoration: none;
          transition: background-color 0.3s ease;
        }

        .sidebar-nav a:hover {
          background-color: #34495e;
        }

        .sidebar-nav li.active a {
          background-color: #3498db;
          font-weight: bold;
        }

        .icon {
          margin-right: 10px;
          display: flex;
          align-items: center;
        }

        .sidebar-footer {
          padding: 20px;
          border-top: 1px solid rgba(255,255,255,0.1);
        }

        .user-info {
          display: flex;
          align-items: center;
        }

        .user-avatar {
          width: 40px;
          height: 40px;
          background-color: #3498db;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          margin-right: 10px;
        }

        .user-name {
          font-weight: bold;
        }

        .user-role {
          font-size: 12px;
          color: #bdc3c7;
        }

        .main-content {
          flex: 1;
          margin-left: 250px;
          padding: 20px;
        }
      `}</style>
    </div>
  );
};

export default SimpleFinDocUI;
