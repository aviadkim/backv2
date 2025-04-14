import { createContext, useContext, useState } from 'react';

const DocumentContext = createContext();

export function DocumentProvider({ children }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);

      // Simulate API call to fetch documents
      await new Promise(resolve => setTimeout(resolve, 1000));

      // For testing purposes, create mock documents
      const mockDocuments = [
        {
          id: '1',
          name: 'Invoice_001.pdf',
          type: 'invoice',
          uploadDate: '2023-01-15',
          status: 'processed',
          size: 1024 * 1024 * 2.5, // 2.5 MB
          preview: '/mock/invoice_preview.jpg'
        },
        {
          id: '2',
          name: 'Bank_Statement_Q1.pdf',
          type: 'bank_statement',
          uploadDate: '2023-02-10',
          status: 'processed',
          size: 1024 * 1024 * 3.2, // 3.2 MB
          preview: '/mock/statement_preview.jpg'
        },
        {
          id: '3',
          name: 'Receipt_XYZ_Corp.pdf',
          type: 'receipt',
          uploadDate: '2023-03-05',
          status: 'processing',
          size: 1024 * 512, // 512 KB
          preview: '/mock/receipt_preview.jpg'
        }
      ];

      setDocuments(mockDocuments);
      return { success: true, data: mockDocuments };
    } catch (error) {
      console.error('Error fetching documents:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file) => {
    try {
      setLoading(true);

      // Simulate API call to upload document
      await new Promise(resolve => setTimeout(resolve, 2000));

      // For testing purposes, create a mock document
      const mockDocument = {
        id: Date.now().toString(),
        name: file.name,
        type: file.type.includes('pdf') ? 'pdf' : 'other',
        uploadDate: new Date().toISOString().split('T')[0],
        status: 'processing',
        size: file.size,
        preview: '/mock/new_document_preview.jpg'
      };

      setDocuments(prev => [...prev, mockDocument]);
      return { success: true, data: mockDocument };
    } catch (error) {
      console.error('Error uploading document:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId) => {
    try {
      setLoading(true);

      // Simulate API call to delete document
      await new Promise(resolve => setTimeout(resolve, 1000));

      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      return { success: true };
    } catch (error) {
      console.error('Error deleting document:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const processDocument = async (documentId) => {
    try {
      setLoading(true);

      // Simulate API call to process document
      await new Promise(resolve => setTimeout(resolve, 3000));

      setDocuments(prev =>
        prev.map(doc =>
          doc.id === documentId
            ? { ...doc, status: 'processed' }
            : doc
        )
      );

      return { success: true };
    } catch (error) {
      console.error('Error processing document:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    documents,
    loading,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    processDocument
  };

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>;
}

export function useDocuments() {
  return useContext(DocumentContext);
}

// Alias for backward compatibility
export function useDocument() {
  return useContext(DocumentContext);
}
