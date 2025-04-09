# DevDocs Application Setup Guide

It appears we're missing the DevDocs repository. Let's create our own DevDocs application structure from scratch:

## 1. Create DevDocs Directory Structure

```powershell
# Navigate to your backv2 directory 
cd C:\Users\aviad\OneDrive\Desktop\backv2

# Create the basic structure
mkdir DevDocs
cd DevDocs
mkdir backend
mkdir frontend
mkdir fast-markdown-mcp
```

## 2. Set Up Backend

```powershell
# Navigate to backend directory
cd backend

# Create necessary files
New-Item -Path app.py -ItemType File

# Write basic Flask application
$appContent = @'
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/documents', methods=['GET'])
def get_documents():
    # Mock document list
    documents = [
        {"id": "1", "title": "Introduction to Python", "tags": ["python", "programming"]},
        {"id": "2", "title": "JavaScript Basics", "tags": ["javascript", "web"]}
    ]
    return jsonify({"documents": documents})

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    # Mock document retrieval
    document = {
        "id": doc_id,
        "title": f"Document {doc_id}",
        "content": "This is the document content. It would typically contain markdown.",
        "tags": ["sample", "documentation"]
    }
    return jsonify(document)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=24125, debug=True)
'@

Set-Content -Path app.py -Value $appContent

# Create requirements file
$requirementsContent = @'
flask==3.1.0
flask-cors==4.0.0
pymongo==4.6.1
python-dotenv==1.0.0
'@

Set-Content -Path requirements.txt -Value $requirementsContent
```

## 3. Set Up Frontend

```powershell
# Navigate to frontend directory
cd ..\frontend

# Create package.json
$packageJson = @'
{
  "name": "devdocs-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev -p 3001",
    "build": "next build",
    "start": "next start -p 3001"
  },
  "dependencies": {
    "next": "13.4.19",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
'@

Set-Content -Path package.json -Value $packageJson

# Create pages directory and index.js
mkdir pages
$indexContent = @'
import { useState, useEffect } from 'react';

export default function Home() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const response = await fetch('http://localhost:24125/api/documents');
        const data = await response.json();
        setDocuments(data.documents);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching documents:', error);
        setLoading(false);
      }
    }

    fetchDocuments();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>DevDocs Application</h1>
      
      <h2>Documents</h2>
      {loading ? (
        <p>Loading documents...</p>
      ) : (
        <ul>
          {documents.map(doc => (
            <li key={doc.id}>
              <a href={`/document/${doc.id}`}>{doc.title}</a>
              <div>
                {doc.tags.map(tag => (
                  <span key={tag} style={{ 
                    background: '#e0f7fa', 
                    padding: '2px 8px', 
                    borderRadius: '12px',
                    marginRight: '5px',
                    fontSize: '12px'
                  }}>
                    {tag}
                  </span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
'@

Set-Content -Path .\pages\index.js -Value $indexContent

# Create document page
mkdir pages\document
$documentPage = @'
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function DocumentPage() {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { id } = router.query;

  useEffect(() => {
    async function fetchDocument() {
      if (!id) return;
      
      try {
        const response = await fetch(`http://localhost:24125/api/documents/${id}`);
        const data = await response.json();
        setDocument(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching document:', error);
        setLoading(false);
      }
    }

    fetchDocument();
  }, [id]);

  if (loading) return <p>Loading document...</p>;
  if (!document) return <p>Document not found</p>;

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <a href="/" style={{ display: 'inline-block', marginBottom: '20px' }}>← Back to Documents</a>
      
      <h1>{document.title}</h1>
      
      <div>
        {document.tags.map(tag => (
          <span key={tag} style={{ 
            background: '#e0f7fa', 
            padding: '2px 8px', 
            borderRadius: '12px',
            marginRight: '5px',
            fontSize: '12px'
          }}>
            {tag}
          </span>
        ))}
      </div>
      
      <div style={{ 
        marginTop: '20px',
        padding: '20px', 
        border: '1px solid #ddd',
        borderRadius: '5px'
      }}>
        {document.content}
      </div>
    </div>
  );
}
'@

Set-Content -Path .\pages\document\[id].js -Value $documentPage
```

## 4. Set Up MCP Server

```powershell
# Navigate to fast-markdown-mcp directory
cd ..\fast-markdown-mcp

# Create app.py
$mcpContent = @'
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/render', methods=['POST'])
def render_markdown():
    data = request.json
    markdown_text = data.get('text', '')
    
    # This is a simple mock renderer
    # In a real application, this would convert markdown to HTML
    html = f"<div>{markdown_text}</div>"
    
    return jsonify({"html": html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=24126, debug=True)
'@

Set-Content -Path app.py -Value $mcpContent

# Create requirements file
$mcpRequirements = @'
flask==3.1.0
flask-cors==4.0.0
'@

Set-Content -Path requirements.txt -Value $mcpRequirements
```

## 5. Create Start Scripts

```powershell
# Navigate back to DevDocs root
cd ..

# Create start.ps1
$startPs1 = @'
# Start backend
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./backend; python app.py"

# Start MCP server
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./fast-markdown-mcp; python app.py"

# Start frontend
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./frontend; npm run dev"

Write-Host "DevDocs started. Frontend: http://localhost:3001, Backend: http://localhost:24125, MCP: http://localhost:24126"
'@

Set-Content -Path start.ps1 -Value $startPs1

# Create start.bat
$startBat = @'
@echo off
start cmd /k "cd backend && python app.py"
start cmd /k "cd fast-markdown-mcp && python app.py"
start cmd /k "cd frontend && npm run dev"
echo DevDocs started. Frontend: http://localhost:3001, Backend: http://localhost:24125, MCP: http://localhost:24126
'@

Set-Content -Path start.bat -Value $startBat
```

## 6. Install Dependencies and Start DevDocs

```powershell
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install MCP server dependencies
cd fast-markdown-mcp
pip install -r requirements.txt
cd ..

# Start the application
.\start.ps1
# Or use the batch file
# .\start.bat
```

## 7. Access the Application

Once started, you can access the application at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:24125
- MCP Service: http://localhost:24126

This will create a basic but functional DevDocs application with frontend, backend, and MCP server.