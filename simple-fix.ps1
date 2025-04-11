# Simple fix script for the FinDoc UI
Write-Host "=== FinDoc UI Simple Fix ===" -ForegroundColor Cyan

# Check if directories exist, create if needed
$componentsDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\components"
$pagesDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\pages"
$stylesDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\styles"
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"

if (!(Test-Path $componentsDir)) { New-Item -Path $componentsDir -ItemType Directory -Force }
if (!(Test-Path $pagesDir)) { New-Item -Path $pagesDir -ItemType Directory -Force }
if (!(Test-Path $stylesDir)) { New-Item -Path $stylesDir -ItemType Directory -Force }
if (!(Test-Path $backendDir)) { New-Item -Path $backendDir -ItemType Directory -Force }

# Create simple backend
$backendFile = "$backendDir\app.py"
Set-Content -Path $backendFile -Value @"
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data
documents = [
    {"id": 1, "title": "Q4 Financial Report 2024.pdf", "tags": ["financial", "report"]},
    {"id": 2, "title": "Investment Portfolio Summary.pdf", "tags": ["investment", "portfolio"]},
    {"id": 3, "title": "Bank Statement March 2025.pdf", "tags": ["banking", "statement"]}
]

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({"documents": documents})

if __name__ == '__main__':
    print("Starting FinDoc API on port 24125...")
    app.run(host='0.0.0.0', port=24125)
"@

# Create the FinDoc layout component
$layoutFile = "$componentsDir\FinDocLayout.js"
Set-Content -Path $layoutFile -Value @"
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function FinDocLayout({ children }) {
  const router = useRouter();
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'home' },
    { name: 'Upload Documents', path: '/upload', icon: 'upload' },
    { name: 'My Documents', path: '/documents', icon: 'file' },
    { name: 'Settings', path: '/settings', icon: 'cog' },
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
                  <span>{item.name}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="main-header">
          <div className="search-box">
            <input type="text" placeholder="Search documents..." />
          </div>
        </header>
        
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
          font-family: 'Segoe UI', sans-serif;
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
        
        .app-title {
          padding: 20px;
          font-size: 1.5rem;
          margin: 0;
        }
        
        .sidebar-nav ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .sidebar-nav li a {
          display: block;
          padding: 12px 20px;
          color: white;
          text-decoration: none;
        }
        
        .sidebar-nav li.active a {
          background-color: rgba(255,255,255,0.1);
          border-left: 3px solid #3498db;
        }
        
        .main-content {
          flex: 1;
          margin-left: 250px;
        }
        
        .main-header {
          padding: 20px;
          background-color: white;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .search-box input {
          width: 300px;
          padding: 10px;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
        }
        
        .page-content {
          padding: 20px;
        }
      \`}</style>
    </div>
  );
}
"@

# Create a simple index.js page
$indexFile = "$pagesDir\index.js"
Set-Content -Path $indexFile -Value @"
import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch documents or use fallback data
    async function fetchData() {
      try {
        const response = await fetch('http://localhost:24125/api/documents');
        const data = await response.json();
        setDocuments(data.documents || []);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Fallback data
        setDocuments([
          { id: 1, title: 'Q4 Financial Report 2024.pdf', tags: ['financial', 'report'] },
          { id: 2, title: 'Investment Portfolio Summary.pdf', tags: ['investment', 'portfolio'] },
          { id: 3, title: 'Bank Statement March 2025.pdf', tags: ['banking', 'statement'] }
        ]);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, []);

  return (
    <FinDocLayout>
      <Head>
        <title>FinDoc Dashboard</title>
      </Head>
      
      <div className="dashboard">
        <h1>FinDoc Dashboard</h1>
        
        {loading ? (
          <p>Loading...</p>
        ) : (
          <div className="document-table">
            <h2>Recent Documents</h2>
            <table>
              <thead>
                <tr>
                  <th>Document Name</th>
                  <th>Tags</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map(doc => (
                  <tr key={doc.id}>
                    <td>{doc.title}</td>
                    <td>{doc.tags?.join(', ')}</td>
                    <td>
                      <button>View</button>
                      <button>Edit</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      <style jsx>{\`
        .dashboard {
          max-width: 1200px;
          margin: 0 auto;
        }
        
        h1 {
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .document-table {
          background: white;
          border-radius: 5px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          padding: 20px;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
        }
        
        th, td {
          padding: 12px 15px;
          text-align: left;
          border-bottom: 1px solid #e2e8f0;
        }
        
        th {
          background-color: #f8fafc;
          font-weight: 600;
        }
        
        button {
          background-color: #3498db;
          color: white;
          border: none;
          padding: 5px 10px;
          border-radius: 4px;
          margin-right: 5px;
          cursor: pointer;
        }
        
        button:hover {
          background-color: #2980b9;
        }
      \`}</style>
    </FinDocLayout>
  );
}
"@

# Create the _app.js file
$appFile = "$pagesDir\_app.js"
Set-Content -Path $appFile -Value @"
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />
}

export default MyApp;
"@

# Create a simple global CSS file
$cssFile = "$stylesDir\globals.css"
Set-Content -Path $cssFile -Value @"
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
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
"@

# Create a simple package.json file
$packageFile = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\package.json"
Set-Content -Path $packageFile -Value @"
{
  "name": "findoc-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3003",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
"@

# Create a simple run script
$runScript = "C:\Users\aviad\OneDrive\Desktop\backv2\run-findoc.ps1"
Set-Content -Path $runScript -Value @"
# Script to run FinDoc app
Write-Host "Starting FinDoc app..." -ForegroundColor Cyan

# Kill any processes using ports 24125 or 3003
try {
    $connections = netstat -ano | Select-String -Pattern "TCP.*:24125.*LISTENING"
    foreach ($conn in $connections) {
        $pid = ($conn -split '\s+')[-1]
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }

    $connections = netstat -ano | Select-String -Pattern "TCP.*:3003.*LISTENING"
    foreach ($conn in $connections) {
        $pid = ($conn -split '\s+')[-1]
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
} catch {}

# Start backend in a new window
Start-Process powershell -ArgumentList "-NoExit -Command `"cd 'C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend'; python app.py`""

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
Write-Host "Starting frontend. Access at http://localhost:3003"
npm run dev
"@

Write-Host "Setup complete! Follow these steps:" -ForegroundColor Green
Write-Host "1. Install dependencies:" -ForegroundColor Cyan
Write-Host "   pip install flask flask_cors" -ForegroundColor White
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend" -ForegroundColor White
Write-Host "   npm install" -ForegroundColor White
Write-Host "2. Run the app:" -ForegroundColor Cyan
Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2" -ForegroundColor White
Write-Host "   .\run-findoc.ps1" -ForegroundColor White
