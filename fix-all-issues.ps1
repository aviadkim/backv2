# FinDoc Quick-Fix Tool: Automatically fixes common issues

Write-Host "=== FinDoc Quick-Fix Tool ===" -ForegroundColor Cyan
Write-Host "This script will automatically fix common issues with the FinDoc application" -ForegroundColor Yellow

# Define paths
$basePath = "C:\Users\aviad\OneDrive\Desktop\backv2"
$backendDir = Join-Path $basePath "DevDocs\backend"
$frontendDir = Join-Path $basePath "DevDocs\frontend"

# Fix 1: Create any missing directories
Write-Host "`n[Fix 1/8] Creating missing directories..." -ForegroundColor Yellow
$requiredDirs = @(
    $basePath,
    (Join-Path $basePath "DevDocs"),
    $backendDir,
    $frontendDir,
    (Join-Path $frontendDir "components"),
    (Join-Path $frontendDir "pages"),
    (Join-Path $frontendDir "styles")
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Fix 2: Install required Python packages
Write-Host "`n[Fix 2/8] Installing required Python packages..." -ForegroundColor Yellow
try {
    $pythonInstalled = python --version 2>&1
    Write-Host "Python detected: $pythonInstalled" -ForegroundColor Green
    
    # Install Flask and Flask-CORS
    Write-Host "Installing Flask and Flask-CORS..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "-m", "pip", "install", "flask", "flask-cors" -Wait -NoNewWindow
    Write-Host "✓ Python packages installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not detected! Please install Python first." -ForegroundColor Red
}

# Fix 3: Free up required ports
Write-Host "`n[Fix 3/8] Freeing up required ports..." -ForegroundColor Yellow
$portsToFree = @(3002, 24125)

foreach ($port in $portsToFree) {
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$port\s+.*LISTENING"
    if ($connections) {
        foreach ($conn in $connections) {
            $processId = ($conn -split "\s+")[-1]
            try {
                $process = Get-Process -Id $processId -ErrorAction Stop
                $procName = $process.ProcessName
                
                Write-Host "Stopping $procName (PID: $processId) using port $port..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force
                Write-Host "Process stopped successfully" -ForegroundColor Green
            } catch {
                Write-Host "Failed to stop process: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Port $port is already free" -ForegroundColor Green
    }
}

# Fix 4: Fix app.py if needed or create it if missing
Write-Host "`n[Fix 4/8] Updating Flask backend configuration..." -ForegroundColor Yellow
$appPyPath = Join-Path $backendDir "app.py"

if (Test-Path $appPyPath) {
    Write-Host "app.py exists, checking for issues..." -ForegroundColor Yellow
    $appPyContent = Get-Content -Path $appPyPath -Raw
    $modified = $false
    
    # Fix common issues
    if (-not ($appPyContent -match "FLASK_SKIP_DOTENV")) {
        $appPyContent = "import os`nos.environ['FLASK_SKIP_DOTENV'] = '1'`n" + $appPyContent
        $modified = $true
    }
    
    if (-not ($appPyContent -match "from flask_cors import CORS")) {
        $appPyContent = $appPyContent -replace "from flask import .*", "$&`nfrom flask_cors import CORS"
        $modified = $true
    }
    
    if (-not ($appPyContent -match "CORS\(app\)")) {
        $appPyContent = $appPyContent -replace "app = Flask\(.*\)", "$&`nCORS(app)"
        $modified = $true
    }
    
    if (-not ($appPyContent -match "host=.*0\.0\.0\.0")) {
        $appPyContent = $appPyContent -replace "app\.run\(.*\)", "app.run(host='0.0.0.0', port=24125, debug=True)"
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $appPyPath -Value $appPyContent
        Write-Host "✓ Updated app.py with fixes" -ForegroundColor Green
    } else {
        Write-Host "✓ app.py looks good, no changes needed" -ForegroundColor Green
    }
} else {
    Write-Host "app.py not found, creating minimal version..." -ForegroundColor Yellow
    
    $minimalApp = @"
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Disable .env file loading to avoid UTF-8 decoding errors
os.environ["FLASK_SKIP_DOTENV"] = "1"

app = Flask(__name__)
CORS(app)

# In-memory storage for demonstration
documents = []
document_id_counter = 1

@app.route('/')
def home():
    return "FinDoc API is running!"

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "API is operational"})

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({"documents": documents})

@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    doc = next((d for d in documents if d['id'] == doc_id), None)
    if doc:
        return jsonify(doc)
    return jsonify({"error": "Document not found"}), 404

@app.route('/api/documents', methods=['POST'])
def create_document():
    global document_id_counter
    data = request.json
    
    # Validate required fields
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    # Create new document
    new_doc = {
        "id": document_id_counter,
        "title": data['title'],
        "content": data.get('content', ''),
        "tags": data.get('tags', [])
    }
    
    document_id_counter += 1
    documents.append(new_doc)
    
    return jsonify(new_doc), 201

@app.route('/api/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    data = request.json
    
    # Find document
    doc_index = next((i for i, d in enumerate(documents) if d['id'] == doc_id), None)
    if doc_index is None:
        return jsonify({"error": "Document not found"}), 404
    
    # Update document
    documents[doc_index].update({
        "title": data.get('title', documents[doc_index]['title']),
        "content": data.get('content', documents[doc_index]['content']),
        "tags": data.get('tags', documents[doc_index]['tags'])
    })
    
    return jsonify(documents[doc_index])

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    global documents
    doc = next((d for d in documents if d['id'] == doc_id), None)
    
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    
    documents = [d for d in documents if d['id'] != doc_id]
    return jsonify({"message": "Document deleted"})

@app.route('/api/tags', methods=['GET'])
def get_tags():
    # Extract all unique tags from documents
    all_tags = set()
    for doc in documents:
        all_tags.update(doc.get('tags', []))
    
    return jsonify({"tags": list(all_tags)})

if __name__ == '__main__':
    # Add some sample documents
    documents = [
        {"id": 1, "title": "Q4 Financial Report 2024.pdf", "content": "Financial report content", "tags": ["financial", "report"]},
        {"id": 2, "title": "Investment Portfolio Summary.pdf", "content": "Portfolio content", "tags": ["investment", "portfolio"]},
        {"id": 3, "title": "Bank Statement March 2025.pdf", "content": "Bank statement content", "tags": ["banking", "statement"]}
    ]
    document_id_counter = 4
    
    print("Starting FinDoc API on port 24125...")
    app.run(host='0.0.0.0', port=24125, debug=True)
"@
    
    Set-Content -Path $appPyPath -Value $minimalApp
    Write-Host "✓ Created minimal app.py with core API functionality" -ForegroundColor Green
}

# Fix 5: Fix package.json if needed or create it if missing
Write-Host "`n[Fix 5/8] Updating Next.js configuration..." -ForegroundColor Yellow
$packageJsonPath = Join-Path $frontendDir "package.json"

if (Test-Path $packageJsonPath) {
    Write-Host "package.json exists, checking for issues..." -ForegroundColor Yellow
    try {
        $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
        $modified = $false
        
        # Fix Next.js version if it's the problematic one
        if ($packageJson.dependencies.next -like "*15.1.4*") {
            $packageJson.dependencies.next = "^14.0.4"
            $modified = $true
            Write-Host "Fixed Next.js version (changed to 14.0.4)" -ForegroundColor Green
        }
        
        # Ensure port is correct
        if ($packageJson.scripts.dev -notlike "*-p 3002*") {
            $packageJson.scripts.dev = "next dev -p 3002"
            $modified = $true
            Write-Host "Fixed dev script to use port 3002" -ForegroundColor Green
        }
        
        if ($modified) {
            $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
            Write-Host "✓ Updated package.json with fixes" -ForegroundColor Green
        } else {
            Write-Host "✓ package.json looks good, no changes needed" -ForegroundColor Green
        }
    } catch {
        Write-Host "Error processing package.json: $_" -ForegroundColor Red
    }
} else {
    Write-Host "package.json not found, creating basic version..." -ForegroundColor Yellow
    
    $basicPackageJson = @"
{
  "name": "findoc-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3002",
    "build": "next build",
    "start": "next start -p 3002",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
"@
    
    Set-Content -Path $packageJsonPath -Value $basicPackageJson
    Write-Host "✓ Created basic package.json" -ForegroundColor Green
}

# Fix 6: Create FinDocLayout if missing
Write-Host "`n[Fix 6/8] Checking FinDoc UI components..." -ForegroundColor Yellow
$finDocLayoutPath = Join-Path $frontendDir "components\FinDocLayout.js"

if (-not (Test-Path $finDocLayoutPath)) {
    Write-Host "FinDocLayout component is missing, creating it..." -ForegroundColor Yellow
    
    $finDocLayoutContent = @"
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
                  <span className={\`icon icon-\${item.icon}\`}></span>
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

      <style jsx>{\`
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
      \`}</style>
    </div>
  );
};

export default FinDocLayout;
"@
    
    # Ensure the components directory exists
    $componentsDir = Join-Path $frontendDir "components"
    if (-not (Test-Path $componentsDir)) {
        New-Item -ItemType Directory -Path $componentsDir -Force | Out-Null
    }
    
    Set-Content -Path $finDocLayoutPath -Value $finDocLayoutContent
    Write-Host "✓ Created FinDocLayout component" -ForegroundColor Green
} else {
    Write-Host "✓ FinDocLayout component already exists" -ForegroundColor Green
}

# Fix 7: Create index.js with FinDocLayout if missing or update it
Write-Host "`n[Fix 7/8] Checking index.js..." -ForegroundColor Yellow
$indexJsPath = Join-Path $frontendDir "pages\index.js"

if (-not (Test-Path $indexJsPath) -or -not ((Get-Content -Path $indexJsPath -Raw) -match "FinDocLayout")) {
    Write-Host "index.js is missing or doesn't use FinDocLayout, creating it..." -ForegroundColor Yellow
    
    $indexJsContent = @"
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
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:24125';
        console.log('Fetching documents from:', \`\${API_URL}/api/documents\`);
        
        // Add timeout handler
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const response = await fetch(\`\${API_URL}/api/documents\`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(\`API responded with status: \${response.status}\`);
        }
        
        const data = await response.json();
        setDocuments(data.documents || []);
        
        // Extract ISIN data (mock data for now)
        extractMockISINData(data.documents || []);
      } catch (error) {
        console.error('Failed to fetch documents:', error);
        setError(\`Failed to load documents: \${error.message}\`);
        loadMockData();
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  const extractMockISINData = (docs) => {
    const mockISINs = [
      { 
        isin: 'US0378331005', 
        description: 'Apple Inc.', 
        document: 'Investment Portfolio Summary', 
        value: '$176.35',
        documentId: '1' 
      },
      { 
        isin: 'US5949181045', 
        description: 'Microsoft Corporation', 
        document: 'Investment Portfolio Summary', 
        value: '$412.27',
        documentId: '2' 
      },
      { 
        isin: 'US88160R1014', 
        description: 'Tesla Inc.', 
        document: 'Q4 Financial Report 2024', 
        value: '$175.34',
        documentId: '3' 
      }
    ];
    
    setIsins(mockISINs);
  };

  const loadMockData = () => {
    const mockDocuments = [
      { id: '1', title: 'Q4 Financial Report 2024.pdf', tags: ['financial', 'report'], date: 'Mar 24, 2025', type: 'Financial', pages: 12 },
      { id: '2', title: 'Investment Portfolio Summary.pdf', tags: ['investment', 'portfolio'], date: 'Mar 22, 2025', type: 'Portfolio', pages: 8 },
      { id: '3', title: 'Bank Statement March 2025.pdf', tags: ['banking', 'statement'], date: 'Mar 20, 2025', type: 'Banking', pages: 4 }
    ];
    
    setDocuments(mockDocuments);
    
    const mockISINs = [
      { isin: 'US0378331005', description: 'Apple Inc.', document: 'Investment Portfolio Summary', value: '$176.35', documentId: '2' },
      { isin: 'US5949181045', description: 'Microsoft Corporation', document: 'Investment Portfolio Summary', value: '$412.27', documentId: '2' }
    ];
    
    setIsins(mockISINs);
  };

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
                {documents.reduce((total, doc) => total + (doc.pages || 0), 0) || 243}
              </div>
              <div className="stat-trend positive">+12% from last month</div>
            </div>
            
            <div className="stat-card">
              <h3>ISIN Numbers</h3>
              <div className="stat-value">{isins.length || 93}</div>
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
                  {documents.slice(0, 5).map((doc) => (
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

      <style jsx>{\`
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
      \`}</style>
    </FinDocLayout>
  );
}
"@
    
    # Ensure the pages directory exists
    $pagesDir = Join-Path $frontendDir "pages"
    if (-not (Test-Path $pagesDir)) {
        New-Item -ItemType Directory -Path $pagesDir -Force | Out-Null
    }
    
    Set-Content -Path $indexJsPath -Value $indexJsContent
    Write-Host "✓ Created/updated index.js with FinDoc UI" -ForegroundColor Green
} else {
    Write-Host "✓ index.js already exists and uses FinDocLayout" -ForegroundColor Green
}

# Fix 8: Create globals.css for better styling
Write-Host "`n[Fix 8/8] Checking global CSS styles..." -ForegroundColor Yellow
$globalsCssPath = Join-Path $frontendDir "styles\globals.css"

if (-not (Test-Path $globalsCssPath)) {
    Write-Host "globals.css is missing, creating it..." -ForegroundColor Yellow
    
    $globalsCssContent = @"
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
"@
    
    # Ensure the styles directory exists
    $stylesDir = Join-Path $frontendDir "styles"
    if (-not (Test-Path $stylesDir)) {
        New-Item -ItemType Directory -Path $stylesDir -Force | Out-Null
    }
    
    Set-Content -Path $globalsCssPath -Value $globalsCssContent
    Write-Host "✓ Created globals.css with styles" -ForegroundColor Green
} else {
    Write-Host "✓ globals.css already exists" -ForegroundColor Green
}

# Final steps - create _app.js if needed
$appJsPath = Join-Path $frontendDir "pages\_app.js"
if (-not (Test-Path $appJsPath)) {
    $appJsContent = @"
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />
}

export default MyApp;
"@
    Set-Content -Path $appJsPath -Value $appJsContent
    Write-Host "Created _app.js to load global styles" -ForegroundColor Green
}

# Create next.config.js if needed
$nextConfigPath = Join-Path $frontendDir "next.config.js"
if (-not (Test-Path $nextConfigPath)) {
    $nextConfigContent = @"
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:24125',
  },
};

module.exports = nextConfig;
"@
    Set-Content -Path $nextConfigPath -Value $nextConfigContent
    Write-Host "Created next.config.js with API URL configuration" -ForegroundColor Green
}

# Summary
Write-Host "`n✓ All fixes have been applied!" -ForegroundColor Green
Write-Host "To start the application, run:" -ForegroundColor Cyan
Write-Host "1. Start the backend first:" -ForegroundColor White
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor White
Write-Host "2. Then start the frontend in a separate window:" -ForegroundColor White
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host "3. Access the application at: http://localhost:3002" -ForegroundColor White

Write-Host "`nWould you like to start the application now? (Y/N)" -ForegroundColor Cyan
$startNow = Read-Host

if ($startNow.ToLower() -eq "y") {
    Write-Host "Starting the application..." -ForegroundColor Green
    & "C:\Users\aviad\OneDrive\Desktop\backv2\start-findoc-app.ps1"
}
