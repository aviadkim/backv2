# FinDoc UI Quick Fix Script
Write-Host "=== Setting up FinDoc UI ===" -ForegroundColor Cyan

# 1. Create directory structure
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
$componentsDir = "$frontendDir\components"
$pagesDir = "$frontendDir\pages"
$stylesDir = "$frontendDir\styles"

# Create directories if they don't exist
if (!(Test-Path $componentsDir)) { New-Item -ItemType Directory -Path $componentsDir -Force | Out-Null }
if (!(Test-Path $pagesDir)) { New-Item -ItemType Directory -Path $pagesDir -Force | Out-Null }
if (!(Test-Path $stylesDir)) { New-Item -ItemType Directory -Path $stylesDir -Force | Out-Null }
if (!(Test-Path $backendDir)) { New-Item -ItemType Directory -Path $backendDir -Force | Out-Null }

Write-Host "✓ Directory structure created" -ForegroundColor Green

# 2. Create necessary files
# Backend app.py
Set-Content -Path "$backendDir\app.py" @'
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# Disable .env file loading to avoid UTF-8 decoding errors
os.environ["FLASK_SKIP_DOTENV"] = "1"

app = Flask(__name__)
CORS(app)

# Sample data
documents = [
    {"id": 1, "title": "Q4 Financial Report 2024.pdf", "content": "Financial report content", "tags": ["financial", "report"]},
    {"id": 2, "title": "Investment Portfolio Summary.pdf", "content": "Portfolio content", "tags": ["investment", "portfolio"]},
    {"id": 3, "title": "Bank Statement March 2025.pdf", "content": "Bank statement content", "tags": ["banking", "statement"]}
]
document_id_counter = 4

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/documents", methods=["GET"])
def get_documents():
    return jsonify({"documents": documents})

@app.route("/api/documents", methods=["POST"])
def add_document():
    global document_id_counter
    data = request.json
    doc = {
        "id": document_id_counter,
        "title": data.get("title", "Untitled"),
        "content": data.get("content", ""),
        "tags": data.get("tags", [])
    }
    documents.append(doc)
    document_id_counter += 1
    return jsonify(doc), 201

if __name__ == "__main__":
    print("Starting FinDoc API on http://localhost:24125")
    app.run(host="0.0.0.0", port=24125)
'@
Write-Host "✓ Backend app.py created" -ForegroundColor Green

# FinDocLayout.js
Set-Content -Path "$componentsDir\FinDocLayout.js" @'
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
        .icon-home:before { content: '🏠'; }
        .icon-upload:before { content: '📤'; }
        .icon-file:before { content: '📄'; }
        .icon-chart-bar:before { content: '📊'; }
        .icon-cog:before { content: '⚙️'; }
        .icon-key:before { content: '🔑'; }
        .icon-bell:before { content: '🔔'; }
        .icon-search:before { content: '🔍'; }
      `}</style>
    </div>
  );
};

export default FinDocLayout;
'@
Write-Host "✓ FinDocLayout component created" -ForegroundColor Green

# index.js
Set-Content -Path "$pagesDir\index.js" @'
import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [isins, setIsins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        console.log('Fetching documents from API...');
        
        const response = await fetch('http://localhost:24125/api/documents', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          mode: 'cors',
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Documents loaded:', data);
        setDocuments(data.documents || []);
        
        // Mock ISIN data
        const mockISINs = [
          { isin: 'US0378331005', description: 'Apple Inc.', document: 'Investment Portfolio Summary', value: '$176.35' },
          { isin: 'US5949181045', description: 'Microsoft Corporation', document: 'Investment Portfolio Summary', value: '$412.27' },
          { isin: 'US88160R1014', description: 'Tesla Inc.', document: 'Q4 Financial Report 2024', value: '$175.34' }
        ];
        setIsins(mockISINs);
      } catch (error) {
        console.error('Error fetching documents:', error);
        setError('Failed to load documents. Please try again later.');
        
        // Load mock data as fallback
        const mockDocuments = [
          { id: 1, title: 'Q4 Financial Report 2024.pdf', tags: ['financial', 'report'], date: 'Mar 24, 2025', type: 'Financial', pages: 12 },
          { id: 2, title: 'Investment Portfolio Summary.pdf', tags: ['investment', 'portfolio'], date: 'Mar 22, 2025', type: 'Portfolio', pages: 8 },
          { id: 3, title: 'Bank Statement March 2025.pdf', tags: ['banking', 'statement'], date: 'Mar 20, 2025', type: 'Banking', pages: 4 }
        ];
        setDocuments(mockDocuments);
        
        const mockISINs = [
          { isin: 'US0378331005', description: 'Apple Inc.', document: 'Investment Portfolio Summary', value: '$176.35' },
          { isin: 'US5949181045', description: 'Microsoft Corporation', document: 'Investment Portfolio Summary', value: '$412.27' }
        ];
        setIsins(mockISINs);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <FinDocLayout>
      <Head>
        <title>Dashboard | FinDoc Analyzer</title>
      </Head>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button 
            className="retry-button"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="dashboard">
          <div className="stats-cards">
            <div className="stat-card">
              <h3>Total Documents</h3>
              <div className="stat-value">{documents.length}</div>
              <div className="stat-trend positive">+24% from last month</div>
            </div>
            
            <div className="stat-card">
              <h3>Total Pages</h3>
              <div className="stat-value">
                {documents.reduce((total, doc) => total + (doc.pages || 0), 0) || 24}
              </div>
              <div className="stat-trend positive">+12% from last month</div>
            </div>
            
            <div className="stat-card">
              <h3>ISIN Numbers</h3>
              <div className="stat-value">{isins.length}</div>
              <div className="stat-trend positive">+18% from last month</div>
            </div>
          </div>

          <div className="section recent-documents">
            <h2>Recent Documents</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Document Name</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Pages</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td>{doc.title}</td>
                      <td>{doc.date || 'Mar 24, 2025'}</td>
                      <td>{doc.type || doc.tags?.[0] || 'Document'}</td>
                      <td>{doc.pages || Math.floor(Math.random() * 20) + 1}</td>
                      <td>
                        <div className="actions">
                          <button className="action-btn view-btn" title="View">👁️</button>
                          <button className="action-btn edit-btn" title="Edit">✏️</button>
                          <button className="action-btn delete-btn" title="Delete">🗑️</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="section isin-analysis">
            <h2>ISIN Analysis</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>ISIN</th>
                    <th>Description</th>
                    <th>Document</th>
                    <th>Value</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {isins.map((isin, index) => (
                    <tr key={index}>
                      <td>{isin.isin}</td>
                      <td>{isin.description}</td>
                      <td>{isin.document}</td>
                      <td>{isin.value}</td>
                      <td>
                        <div className="actions">
                          <button className="action-btn view-btn" title="View Document">📄</button>
                          <button className="action-btn chart-btn" title="View Chart">📊</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .dashboard {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }

        .stats-cards {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .stat-card {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .stat-card h3 {
          margin: 0 0 10px 0;
          font-size: 0.9rem;
          color: #718096;
          font-weight: 500;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 600;
          margin-bottom: 5px;
        }

        .stat-trend {
          font-size: 0.85rem;
          display: flex;
          align-items: center;
        }

        .stat-trend.positive {
          color: #38a169;
        }

        .stat-trend.negative {
          color: #e53e3e;
        }

        .section {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .section h2 {
          margin-top: 0;
          margin-bottom: 20px;
          font-size: 1.25rem;
          color: #2d3748;
        }

        .table-container {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          text-align: left;
          padding: 12px 15px;
          background-color: #f8fafc;
          color: #4a5568;
          font-weight: 600;
          font-size: 0.9rem;
          border-bottom: 1px solid #e2e8f0;
        }

        td {
          padding: 12px 15px;
          border-bottom: 1px solid #e2e8f0;
          color: #4a5568;
          font-size: 0.9rem;
        }

        tr:last-child td {
          border-bottom: none;
        }

        .actions {
          display: flex;
          gap: 5px;
        }

        .action-btn {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1rem;
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 300px;
        }

        .loading-spinner {
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-radius: 50%;
          border-top: 4px solid #3498db;
          width: 30px;
          height: 30px;
          animation: spin 1s linear infinite;
          margin-bottom: 15px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-container {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          color: #c53030;
        }

        .retry-button {
          background-color: #3182ce;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 10px;
        }

        .retry-button:hover {
          background-color: #2c5282;
        }
      `}</style>
    </FinDocLayout>
  );
}
'@
Write-Host "✓ Main dashboard page created" -ForegroundColor Green

# _app.js
Set-Content -Path "$pagesDir\_app.js" @'
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />
}

export default MyApp;
'@

# globals.css
Set-Content -Path "$stylesDir\globals.css" @'
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
'@
Write-Host "✓ Base styles created" -ForegroundColor Green

# package.json
Set-Content -Path "$frontendDir\package.json" @'
{
  "name": "findoc-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3003",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
'@
Write-Host "✓ package.json created" -ForegroundColor Green

# Create run-findoc.ps1
Set-Content -Path "$basePath\run-findoc.ps1" @'
# Script to run the FinDoc application
Write-Host "=== FinDoc Application Launcher ===" -ForegroundColor Cyan

# Kill any processes using the required ports
$ports = @(24125, 3003)
foreach ($port in $ports) {
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$port.*LISTENING"
    if ($connections) {
        foreach ($conn in $connections) {
            try {
                $pidMatch = $conn -match "\s+(\d+)$"
                if ($pidMatch) {
                    $pid = $Matches[1]
                    Write-Host "Stopping process with PID $pid using port $port..." -ForegroundColor Yellow
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Host "Process stopped" -ForegroundColor Green
                }
            } catch {
                Write-Host "Error stopping process on port $port: $_" -ForegroundColor Red
            }
        }
    }
}

# Start backend in a new window
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
if (Test-Path $backendDir) {
    Write-Host "Starting backend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py"
    
    # Wait for backend to start
    Write-Host "Waiting for backend to start (5 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Backend directory not found at $backendDir" -ForegroundColor Red
    exit
}

# Open browser to the frontend URL
Start-Process "http://localhost:3003"

# Start frontend
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
if (Test-Path $frontendDir) {
    Write-Host "`nStarting frontend..." -ForegroundColor Cyan
    Write-Host "Frontend will be available at: http://localhost:3003" -ForegroundColor Green
    Write-Host "`nPress Ctrl+C to stop the frontend when done`n" -ForegroundColor Yellow
    
    Set-Location -Path $frontendDir
    npm run dev
} else {
    Write-Host "Frontend directory not found at $frontendDir" -ForegroundColor Red
}
'@
Write-Host "✓ Created run script" -ForegroundColor Green

Write-Host "`nSetup complete! To run the FinDoc application:" -ForegroundColor Cyan
Write-Host "1. Install Python dependencies:" -ForegroundColor White
Write-Host "   pip install flask flask-cors" -ForegroundColor White
Write-Host "2. Install Node.js dependencies:" -ForegroundColor White
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend" -ForegroundColor White
Write-Host "   npm install" -ForegroundColor White
Write-Host "3. Run the application:" -ForegroundColor White
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2" -ForegroundColor White
Write-Host "   .\run-findoc.ps1" -ForegroundColor White
Write-Host "`nThe UI will be available at: http://localhost:3003" -ForegroundColor Green
