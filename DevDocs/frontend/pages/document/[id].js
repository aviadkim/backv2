import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    // Wait until we have an ID from the route
    if (!id) return;
    
    async function fetchDocument() {
      try {
        const response = await fetch(`http://localhost:24125/api/documents/${id}`);
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        setDocument(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching document:', error);
        setError(error.message);
        setLoading(false);
      }
    }

    fetchDocument();
  }, [id]);

  const handleTagClick = (tag) => {
    router.push(`/?tag=${encodeURIComponent(tag)}`);
  };

  const handleEditClick = () => {
    router.push(`/edit/${id}`);
  };

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    setDeleting(true);
    try {
      const response = await fetch(`http://localhost:24125/api/documents/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete document');
      }
      
      router.push('/');
    } catch (error) {
      console.error('Error deleting document:', error);
      setError(error.message);
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
  };

  if (loading && id) {
    return <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>Loading document...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>Error</h1>
        <p style={{ color: 'red' }}>{error}</p>
        <button 
          onClick={() => router.push('/')} 
          style={{ padding: '8px 16px', cursor: 'pointer' }}
        >
          Back to Documents
        </button>
      </div>
    );
  }

  if (!document) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>Document Not Found</h1>
        <button 
          onClick={() => router.push('/')} 
          style={{ padding: '8px 16px', cursor: 'pointer' }}
        >
          Back to Documents
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <button 
          onClick={() => router.push('/')} 
          style={{ 
            padding: '8px 16px',
            background: '#e1f5fe',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ← Back to Documents
        </button>
        
        <div>
          <button
            onClick={handleEditClick}
            style={{
              padding: '8px 16px',
              background: '#ff9800',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            Edit Document
          </button>
          
          <button
            onClick={handleDeleteClick}
            style={{
              padding: '8px 16px',
              background: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Delete Document
          </button>
        </div>
      </div>
      
      <h1>{document.title}</h1>
      
      <div style={{ marginBottom: '20px' }}>
        {document.tags.map(tag => (
          <span 
            key={tag} 
            onClick={(e) => {
              e.stopPropagation();
              handleTagClick(tag);
            }}
            style={{ 
              background: '#e0f7fa', 
              padding: '2px 8px', 
              borderRadius: '12px',
              marginRight: '5px',
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div style={{ 
        padding: '20px',
        background: '#f5f5f5',
        borderRadius: '4px',
        marginTop: '20px',
        whiteSpace: 'pre-line'
      }}>
        {document.content}
      </div>
      
      {/* Delete confirmation dialog */}
      {showDeleteConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '400px',
            textAlign: 'center'
          }}>
            <h3 style={{ marginTop: 0 }}>Delete Document</h3>
            <p>Are you sure you want to delete "{document.title}"?</p>
            <p style={{ fontSize: '14px', color: '#f44336' }}>This action cannot be undone.</p>
            
            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
              <button
                onClick={handleDeleteCancel}
                disabled={deleting}
                style={{
                  padding: '8px 16px',
                  background: '#e0e0e0',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: deleting ? 'not-allowed' : 'pointer'
                }}
              >
                Cancel
              </button>
              
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting}
                style={{
                  padding: '8px 16px',
                  background: '#f44336',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: deleting ? 'not-allowed' : 'pointer',
                  opacity: deleting ? 0.7 : 1
                }}
              >
                {deleting ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
