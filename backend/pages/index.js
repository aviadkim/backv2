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
