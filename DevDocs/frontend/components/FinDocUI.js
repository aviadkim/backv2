import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import axios from 'axios';

// Icons
import {
  FiHome,
  FiUpload,
  FiBarChart2,
  FiFileText,
  FiSettings,
  FiSearch,
  FiPlus,
  FiDatabase,
  FiDollarSign,
  FiCode,
  FiPieChart
} from 'react-icons/fi';

const FinDocUI = ({ children }) => {
  const router = useRouter();
  const [user, setUser] = useState({ name: 'Aviad B.', role: 'Administrator' });
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Fetch API key from GitHub secrets on component mount
  useEffect(() => {
    const fetchApiKey = async () => {
      try {
        const response = await axios.get('/api/config/api-key');
        if (response.data && response.data.key) {
          setApiKey(response.data.key);
          console.log('API key loaded successfully');
        }
      } catch (error) {
        console.error('Error fetching API key:', error);
        showNotification('Error loading API key. Some features may not work properly.', 'error');
      }
    };

    fetchApiKey();
  }, []);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleUploadClick = () => {
    router.push('/upload');
  };

  const handleAnalyticsClick = () => {
    router.push('/analytics');
  };

  const handleReportsClick = () => {
    router.push('/reports');
  };

  const handleTestingClick = () => {
    router.push('/test-center');
  };

  const handleDevTestingClick = () => {
    router.push('/dev-test-center');
  };

  const handleSettingsClick = () => {
    router.push('/settings');
  };

  const handleApiKeySetup = () => {
    router.push('/api-key-setup');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <FiHome size={18} />, onClick: () => router.push('/') },
    { name: 'Upload Documents', path: '/upload', icon: <FiUpload size={18} />, onClick: handleUploadClick },
    { name: 'Analytics', path: '/analytics', icon: <FiBarChart2 size={18} />, onClick: handleAnalyticsClick },
    { name: 'Reports', path: '/reports', icon: <FiFileText size={18} />, onClick: handleReportsClick },
    { name: 'Financial Testing', path: '/financial-test-center', icon: <FiDollarSign size={18} />, onClick: () => router.push('/financial-test-center') },
    { name: 'Testing', path: '/test-center', icon: <FiSearch size={18} />, onClick: handleTestingClick },
    { name: 'Dev Testing', path: '/dev-test-center', icon: <FiCode size={18} />, onClick: handleDevTestingClick },
    { name: 'Settings', path: '/settings', icon: <FiSettings size={18} />, onClick: handleSettingsClick },
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
                <a href="#" onClick={(e) => { e.preventDefault(); item.onClick(); }}>
                  <span className="icon">{item.icon}</span>
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
        {notification && (
          <div className={`notification ${notification.type}`}>
            {notification.message}
          </div>
        )}
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

        .notification {
          padding: 10px 15px;
          margin-bottom: 20px;
          border-radius: 4px;
          font-weight: 500;
        }

        .notification.info {
          background-color: #d1ecf1;
          color: #0c5460;
        }

        .notification.error {
          background-color: #f8d7da;
          color: #721c24;
        }

        .notification.success {
          background-color: #d4edda;
          color: #155724;
        }
      `}</style>
    </div>
  );
};

export default FinDocUI;
