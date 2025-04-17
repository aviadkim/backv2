import React, { useState } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import Link from 'next/link';
import { useRouter } from 'next/router';

function FinDocLayout({ children }) {
  const router = useRouter();
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'home' },
    { name: 'Upload Documents', path: '/upload', icon: 'upload' },
    { name: 'My Documents', path: '/documents', icon: 'file' },
    { name: 'Analysis', path: '/analysis', icon: 'chart-bar' },
    { name: 'Portfolio', path: '/portfolio', icon: 'chart-pie' },
    { name: 'Agents', path: '/agents', icon: 'robot' },
    { name: 'Document Understanding', path: '/document-understanding-demo', icon: 'file-search' },
    { name: 'SQL Agent', path: '/test-sql-agent', icon: 'database' },
    { name: 'Web Browser', path: '/test-web-browser', icon: 'globe' },
    { name: 'Google Cloud MCP', path: '/mcp-integration', icon: 'cloud' },
    { name: 'Testing', path: '/dev-test-center', icon: 'tool' },
    { name: 'API Setup', path: '/api-key-setup', icon: 'key-square' },
    { name: 'Settings', path: '/settings', icon: 'cog' },
    { name: 'API Keys', path: '/api-keys', icon: 'key' },
  ];

  return (
    <AccessibilityWrapper>
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
                <Link href={item.path}>
                  <span className={`icon icon-${item.icon}`}></span>
                  <span>{item.name}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">AB</div>
            <div className="user-details">
              <div className="user-name">Aviad B.</div>
              <div className="user-role">Administrator</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="search-box">
            <input type="text" placeholder="Search documents..." />
            <span className="icon icon-search"></span>
          </div>
          <div className="header-actions">
            <Link href="/upload" className="upload-btn">
              <span className="icon icon-upload"></span>
              <span>Upload Document</span>
            </Link>
            <button className="icon-btn" onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}>
              <span className="icon icon-bell"></span>
            </button>
            <button className="user-menu-btn" onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}>
              <div className="user-avatar-small">AB</div>
            </button>
          </div>
        </header>

        {/* Notifications dropdown */}
        {isNotificationsOpen && (
          <div className="notifications-dropdown">
            <h3>Notifications</h3>
            <ul>
              <li>New document uploaded: Q4 Financial Report</li>
              <li>Analysis complete for 3 documents</li>
              <li>System update scheduled for tomorrow</li>
            </ul>
          </div>
        )}

        {/* User menu dropdown */}
        {isUserMenuOpen && (
          <div className="user-menu-dropdown">
            <ul>
              <li><Link href="/profile">My Profile</Link></li>
              <li><Link href="/settings">Settings</Link></li>
              <li><a href="/logout">Logout</a></li>
            </ul>
          </div>
        )}

        {/* Page content */}
        <div className="page-content">
          {children}
        </div>
      </main>

      <style jsx global>{`
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        html, body {
          padding: 0;
          margin: 0;
          font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
          line-height: 1.6;
          font-size: 16px;
          color: #333;
          background: #f7f9fc;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        button {
          cursor: pointer;
        }

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
          font-size: 1.5rem;
          margin: 0;
          font-weight: 600;
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

        .sidebar-nav li a {
          display: flex;
          align-items: center;
          padding: 12px 20px;
          color: rgba(255,255,255,0.7);
          text-decoration: none;
          transition: all 0.3s;
        }

        .sidebar-nav li a:hover, .sidebar-nav li.active a {
          background-color: rgba(255,255,255,0.1);
          color: white;
          border-left: 3px solid #3498db;
        }

        .sidebar-nav .icon {
          margin-right: 10px;
          width: 20px;
          text-align: center;
        }

        .sidebar-footer {
          padding: 15px 20px;
          border-top: 1px solid rgba(255,255,255,0.1);
        }

        .user-info {
          display: flex;
          align-items: center;
        }

        .user-avatar, .user-avatar-small {
          background-color: #3498db;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 600;
        }

        .user-avatar {
          width: 40px;
          height: 40px;
          margin-right: 10px;
        }

        .user-avatar-small {
          width: 32px;
          height: 32px;
          font-size: 0.8rem;
        }

        .user-details {
          display: flex;
          flex-direction: column;
        }

        .user-name {
          font-weight: 600;
          font-size: 0.9rem;
        }

        .user-role {
          font-size: 0.7rem;
          opacity: 0.7;
        }

        .main-content {
          flex: 1;
          margin-left: 250px;
          width: calc(100% - 250px);
        }

        .main-header {
          height: 70px;
          background-color: white;
          border-bottom: 1px solid #e1e5eb;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 30px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }

        .search-box {
          position: relative;
          width: 300px;
        }

        .search-box input {
          width: 100%;
          padding: 10px 15px 10px 40px;
          border: 1px solid #e1e5eb;
          border-radius: 20px;
          font-size: 0.9rem;
        }

        .search-box .icon-search {
          position: absolute;
          left: 15px;
          top: 50%;
          transform: translateY(-50%);
          color: #a7a7a7;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .upload-btn {
          display: flex;
          align-items: center;
          background-color: #3498db;
          color: white;
          border: none;
          border-radius: 5px;
          padding: 8px 15px;
          font-size: 0.9rem;
          cursor: pointer;
          text-decoration: none;
        }

        .upload-btn .icon {
          margin-right: 8px;
        }

        .icon-btn {
          background: none;
          border: none;
          color: #718096;
          font-size: 1.25rem;
          cursor: pointer;
          position: relative;
        }

        .user-menu-btn {
          background: none;
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
        }

        .notifications-dropdown,
        .user-menu-dropdown {
          position: absolute;
          right: 30px;
          top: 70px;
          background-color: white;
          border: 1px solid #e1e5eb;
          border-radius: 5px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          z-index: 1000;
          min-width: 220px;
        }

        .notifications-dropdown h3 {
          padding: 15px;
          margin: 0;
          border-bottom: 1px solid #e1e5eb;
          font-size: 1rem;
        }

        .notifications-dropdown ul,
        .user-menu-dropdown ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .notifications-dropdown li,
        .user-menu-dropdown li {
          padding: 12px 15px;
          border-bottom: 1px solid #f0f0f0;
          font-size: 0.9rem;
        }

        .notifications-dropdown li:last-child,
        .user-menu-dropdown li:last-child {
          border-bottom: none;
        }

        .user-menu-dropdown a {
          color: #333;
          text-decoration: none;
        }

        .user-menu-dropdown a:hover {
          color: #3498db;
        }

        .page-content {
          padding: 30px;
        }

        /* Icon placeholders */
        .icon:before {
          font-family: 'Font Awesome 5 Free';
          font-weight: 900;
        }
        .icon-home:before { content: '\f015'; }
        .icon-upload:before { content: '\f093'; }
        .icon-file:before { content: '\f15b'; }
        .icon-chart-bar:before { content: '\f080'; }
        .icon-chart-pie:before { content: '\f200'; }
        .icon-robot:before { content: '\f544'; }
        .icon-cog:before { content: '\f013'; }
        .icon-key:before { content: '\f084'; }
        .icon-bell:before { content: '\f0f3'; }
        .icon-search:before { content: '\f002'; }
        .icon-file-search:before { content: '\f002'; }
        .icon-database:before { content: '\f1c0'; }
        .icon-globe:before { content: '\f0ac'; }
        .icon-cloud:before { content: '\f0c2'; }
        .icon-key-square:before { content: '\f084'; }
        .icon-tool:before { content: '\f7d9'; }
      `}</style>
    </div>
    </AccessibilityWrapper>
  );
}

export default FinDocLayout;
