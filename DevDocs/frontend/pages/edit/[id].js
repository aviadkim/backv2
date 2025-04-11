import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function EditDocument() {
  const router = useRouter();
  const { id } = router.query;
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Wait until we have an ID from the route
    if (!id) return;

    async function fetchDocument() {
      try {
        const response = await fetch(`http://localhost:24125/api/documents/${id}`);
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        const document = await response.json();
        
        // Populate form fields with document data
        setTitle(document.title);
        setContent(document.content);
        setTagsInput(document.tags.join(', '));
        setLoading(false);
      } catch (error) {
        console.error('Error fetching document:', error);
        setError(error.message);
        setLoading(false);
      }
    }

    fetchDocument();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    // Parse tags from comma-separated input
    const tags = tagsInput.split(',')
      .map(tag => tag.trim())
      .filter(tag => tag !== '');

    try {
      const response = await fetch(`http://localhost:24125/api/documents/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          content,
          tags
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update document');
      }

      router.push(`/document/${id}`);
    } catch (err) {
      console.error('Error updating document:', err);
      setError(err.message);
      setIsSubmitting(false);
    }
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
          onClick={() => router.push(`/document/${id}`)} 
          style={{ padding: '8px 16px', cursor: 'pointer' }}
        >
          Back to Document
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <button
        onClick={() => router.push(`/document/${id}`)}
        style={{
          marginBottom: '20px',
          padding: '8px 16px',
          background: '#e1f5fe',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        ← Back to Document
      </button>
      
      <h1>Edit Document</h1>
      
      {error && (
        <div style={{ 
          padding: '10px', 
          background: '#ffebee', 
          color: '#c62828', 
          borderRadius: '4px',
          marginBottom: '20px' 
        }}>
          Error: {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Title:
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Content:
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows={10}
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontFamily: 'Arial, sans-serif'
            }}
          />
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Tags (comma-separated):
          </label>
          <input
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="e.g. javascript, programming, web"
            style={{
              width: '100%',
              padding: '8px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            padding: '10px 20px',
            background: '#ff9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            opacity: isSubmitting ? 0.7 : 1
          }}
        >
          {isSubmitting ? 'Updating...' : 'Update Document'}
        </button>
      </form>
    </div>
  );
}
