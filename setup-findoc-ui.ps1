# Script to set up the FinDoc UI components

# Create directories
Write-Host "Creating components and styles directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\components" -Force
New-Item -ItemType Directory -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\styles" -Force

# Create the FinDocLayout component
Write-Host "Creating FinDocLayout component..." -ForegroundColor Cyan
$finDocLayoutContent = @'
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const FinDocLayout = ({ children }) => {
  const router = useRouter();
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  // Define navigation items
  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'home' },
    { name: 'Upload Documents', path: '/upload', icon: 'upload' },
    { name: 'My Documents', path: '/documents', icon: 'file' },
    { name: 'Analysis', path: '/analysis', icon: 'chart-bar' },
    { name: 'Settings', path: '/settings', icon: 'cog' },
    { name: 'API Keys', path: '/api-keys', icon: 'key' },
    { name: 'Integrations', path: '/integrations', icon: 'plug' },
  ];

  // Toggle functions
  const toggleNotifications = () => setIsNotificationsOpen(!isNotificationsOpen);
  const toggleUserMenu = () => setIsUserMenuOpen(!isUserMenuOpen);

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
            <button className="icon-btn" onClick={toggleNotifications}>
              <span className="icon icon-bell"></span>
              <span className="sr-only">Toggle notifications</span>
            </button>
            <button className="user-menu-btn" onClick={toggleUserMenu}>
              <div className="user-avatar-small">AB</div>
              <span className="sr-only">Toggle user menu</span>
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

        .user-avatar {
          width: 40px;
          height: 40px;
          background-color: #3498db;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 10px;
          font-weight: 600;
        }

        .user-avatar-small {
          width: 32px;
          height: 32px;
          background-color: #3498db;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 600;
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

        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
          border-width: 0;
        }

        /* Add icon placeholders */
        .icon:before {
          font-family: 'Font Awesome 5 Free';
          font-weight: 900;
        }
        .icon-home:before { content: '🏠'; }
        .icon-upload:before { content: '📤'; }
        .icon-file:before { content: '📄'; }
        .icon-chart-bar:before { content: '📊'; }
        .icon-cog:before { content: '⚙️'; }
        .icon-key:before { content: '🔑'; }
        .icon-plug:before { content: '🔌'; }
        .icon-bell:before { content: '🔔'; }
        .icon-search:before { content: '🔍'; }
      `}</style>
    </div>
  );
};

export default FinDocLayout;
'@

Set-Content -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\components\FinDocLayout.js" -Value $finDocLayoutContent

# Create global CSS file
Write-Host "Creating global CSS styles..." -ForegroundColor Cyan
$globalCssContent = @'
/* Reset and base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
  padding: 0;
  margin: 0;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
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

/* Utility classes */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Button styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.5;
  border-radius: 0.375rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-outline {
  background-color: transparent;
  border-color: #e2e8f0;
}

.btn-outline:hover {
  background-color: #f8fafc;
}

/* Card styles */
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.card-body {
  padding: 1rem;
}

.card-footer {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
}

/* Form styles */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: #4a5568;
  background-color: white;
  background-clip: padding-box;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  transition: border-color 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #3498db;
  outline: 0;
}

/* Table styles */
.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, 
.table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  font-weight: 600;
  text-align: left;
}

/* Alert styles */
.alert {
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border-radius: 0.25rem;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
}

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
}
'@

Set-Content -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\styles\globals.css" -Value $globalCssContent

# Create _app.js if it doesn't exist
$appJsPath = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\pages\_app.js"
if (-not (Test-Path $appJsPath)) {
    Write-Host "Creating _app.js file..." -ForegroundColor Cyan
    $appJsContent = @'
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />
}

export default MyApp;
'@
    Set-Content -Path $appJsPath -Value $appJsContent
}

# Create upload page
Write-Host "Creating upload page..." -ForegroundColor Cyan
$uploadPageContent = @'
import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import FinDocLayout from '../components/FinDocLayout';

export default function UploadDocument() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files);
    }
  };

  const handleFileChange = (files) => {
    if (files.length > 0) {
      const selectedFile = files[0];
      setFile(selectedFile);
      
      // Auto-fill title from filename (remove extension)
      const fileName = selectedFile.name.replace(/\.[^/.]+$/, "");
      setTitle(fileName);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a file to upload");
      return;
    }
    
    if (!title.trim()) {
      setError("Please enter a document title");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Convert tags string to array
      const tagsArray = tags.split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
      
      // Create document metadata
      const document = {
        title: title,
        content: `Content of ${title}`,
        tags: tagsArray
      };
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:24125';
      
      // Try to upload to the API
      const response = await fetch(`${API_URL}/api/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(document)
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('Document created:', result);
      
      // Redirect to dashboard
      setTimeout(() => {
        router.push('/');
      }, 1000);
      
    } catch (error) {
      console.error('Error uploading document:', error);
      setError("Failed to upload document. Please try again.");
      
      // For demo, redirect anyway
      if (process.env.NODE_ENV !== 'production') {
        setTimeout(() => {
          router.push('/');
        }, 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <FinDocLayout>
      <Head>
        <title>Upload Document | FinDoc Analyzer</title>
      </Head>

      <div className="upload-page">
        <h1 className="page-title">Upload Document</h1>
        
        <div className="upload-card">
          <form onSubmit={handleSubmit}>
            {/* File upload area */}
            <div 
              className={`upload-area ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="file-info">
                  <div className="file-icon">📄</div>
                  <div className="file-details">
                    <div className="file-name">{file.name}</div>
                    <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                  <button 
                    type="button" 
                    className="remove-file-btn"
                    onClick={() => setFile(null)}
                  >
                    &times;
                  </button>
                </div>
              ) : (
                <>
                  <div className="upload-icon">📁</div>
                  <div className="upload-text">
                    <p className="primary-text">Drag & drop your file here</p>
                    <p className="secondary-text">or</p>
                    <label className="browse-btn">
                      Browse files
                      <input 
                        type="file" 
                        className="visually-hidden"
                        onChange={(e) => handleFileChange(e.target.files)}
                        accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.csv"
                      />
                    </label>
                  </div>
                  <p className="upload-hint">Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX, CSV</p>
                </>
              )}
            </div>
            
            {/* Document info fields */}
            <div className="form-group">
              <label className="form-label" htmlFor="title">Document Title</label>
              <input 
                type="text" 
                id="title" 
                className="form-control"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="tags">Tags (comma separated)</label>
              <input 
                type="text" 
                id="tags" 
                className="form-control"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="financial, report, quarterly"
              />
            </div>
            
            {/* Error message */}
            {error && (
              <div className="alert alert-danger">
                {error}
              </div>
            )}
            
            {/* Submit button */}
            <div className="form-actions">
              <button 
                type="button" 
                className="btn btn-outline"
                onClick={() => router.push('/')}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Uploading...' : 'Upload Document'}
              </button>
            </div>
          </form>
        </div>
        
        <div className="upload-help">
          <h3>Document Analysis Features</h3>
          <ul className="feature-list">
            <li>Automatic ISIN extraction</li>
            <li>Financial data recognition</li>
            <li>Document categorization</li>
            <li>Text searchable PDFs</li>
            <li>Metadata extraction</li>
          </ul>
        </div>
      </div>

      <style jsx>{`
        .upload-page {
          max-width: 900px;
          margin: 0 auto;
        }

        .page-title {
          margin-bottom: 1.5rem;
          font-size: 1.75rem;
          color: #2d3748;
        }

        .upload-card {
          background-color: white;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
          margin-bottom: 2rem;
        }

        .upload-area {
          border: 2px dashed #cbd5e0;
          border-radius: 8px;
          padding: 2rem;
          text-align: center;
          margin-bottom: 1.5rem;
          transition: all 0.3s;
        }

        .upload-area.drag-active {
          border-color: #3498db;
          background-color: rgba(52, 152, 219, 0.05);
        }

        .upload-area.has-file {
          border-style: solid;
          border-color: #3498db;
          background-color: rgba(52, 152, 219, 0.05);
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          color: #a0aec0;
        }

        .primary-text {
          font-size: 1.25rem;
          font-weight: 500;
          margin-bottom: 0.5rem;
          color: #4a5568;
        }

        .secondary-text {
          margin-bottom: 0.5rem;
          color: #718096;
        }

        .browse-btn {
          display: inline-block;
          background-color: #3498db;
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.3s;
        }

        .browse-btn:hover {
          background-color: #2980b9;
        }

        .upload-hint {
          margin-top: 1rem;
          font-size: 0.875rem;
          color: #a0aec0;
        }

        .file-info {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.5rem 1rem;
          background-color: white;
          border-radius: 4px;
        }

        .file-icon {
          font-size: 2rem;
          margin-right: 1rem;
          color: #3498db;
        }

        .file-details {
          flex: 1;
          text-align: left;
        }

        .file-name {
          font-weight: 500;
          color: #4a5568;
          margin-bottom: 0.25rem;
        }

        .file-size {
          font-size: 0.875rem;
          color: #718096;
        }

        .remove-file-btn {
          background: none;
          border: none;
          color: #e53e3e;
          font-size: 1.5rem;
          cursor: pointer;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .upload-help {
          background-color: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .upload-help h3 {
          margin-top: 0;
          margin-bottom: 1rem;
          color: #2d3748;
          font-size: 1.25rem;
        }

        .feature-list {
          list-style-type: none;
          padding: 0;
        }

        .feature-list li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
          color: #4a5568;
        }

        .feature-list li:before {
          content: "✓";
          color: #38a169;
          position: absolute;
          left: 0;
        }
      `}</style>
    </FinDocLayout>
  );
}
'@

Set-Content -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\pages\upload.js" -Value $uploadPageContent

# Create a next.config.js file
Write-Host "Creating Next.js configuration..." -ForegroundColor Cyan
$nextConfigContent = @'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Enable CORS for API requests
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:24125',
  },
};

module.exports = nextConfig;
'@

Set-Content -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\next.config.js" -Value $nextConfigContent

Write-Host "✅ FinDoc UI implementation completed!" -ForegroundColor Green
Write-Host "Now run: cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend; npm install; npm run dev" -ForegroundColor Cyan
