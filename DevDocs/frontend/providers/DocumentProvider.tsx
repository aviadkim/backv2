import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Document, DocumentUploadOptions } from '../models/types';
import documentController from '../controllers/documentController';
import getSupabaseClient from '../lib/supabaseClient';

interface DocumentContextType {
  documents: Document[];
  currentDocument: Document | null;
  loading: boolean;
  error: string | null;
  getAllDocuments: () => Promise<Document[]>;
  getDocumentById: (id: string) => Promise<Document | null>;
  uploadDocument: (file: File, options?: DocumentUploadOptions) => Promise<Document>;
  updateDocument: (id: string, data: Partial<Document>) => Promise<Document>;
  deleteDocument: (id: string) => Promise<boolean>;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocument = () => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
};

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getAllDocuments = async (): Promise<Document[]> => {
    setLoading(true);
    setError(null);

    try {
      // Try using the controller first
      try {
        const result = await documentController.getAllDocuments();
        setDocuments(result);
        return result;
      } catch (controllerError) {
        console.warn('Controller error, falling back to direct Supabase access:', controllerError);

        // Fallback to direct Supabase access
        const supabase = getSupabaseClient();
        if (!supabase) {
          throw new Error('Supabase client not available');
        }

        const { data, error } = await supabase
          .from('documents')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) {
          throw error;
        }

        // Convert from snake_case to camelCase
        const formattedDocuments = data.map((doc: any) => ({
          id: doc.id,
          title: doc.title,
          filePath: doc.file_path,
          fileName: doc.file_name,
          fileType: doc.file_type,
          fileSize: doc.file_size,
          content: doc.content,
          metadata: doc.metadata,
          tags: doc.tags || [],
          organizationId: doc.organization_id,
          createdBy: doc.created_by,
          createdAt: doc.created_at,
          updatedAt: doc.updated_at
        }));

        setDocuments(formattedDocuments);
        return formattedDocuments;
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return [];
    } finally {
      setLoading(false);
    }
  };

  const getDocumentById = async (id: string): Promise<Document | null> => {
    setLoading(true);
    setError(null);

    try {
      // Try using the controller first
      try {
        const result = await documentController.getDocumentById(id);
        setCurrentDocument(result);
        return result;
      } catch (controllerError) {
        console.warn('Controller error, falling back to direct Supabase access:', controllerError);

        // Fallback to direct Supabase access
        const supabase = getSupabaseClient();
        if (!supabase) {
          throw new Error('Supabase client not available');
        }

        const { data, error } = await supabase
          .from('documents')
          .select('*')
          .eq('id', id)
          .single();

        if (error) {
          throw error;
        }

        if (!data) {
          return null;
        }

        // Convert from snake_case to camelCase
        const document: Document = {
          id: data.id,
          title: data.title,
          filePath: data.file_path,
          fileName: data.file_name,
          fileType: data.file_type,
          fileSize: data.file_size,
          content: data.content,
          metadata: data.metadata,
          tags: data.tags || [],
          organizationId: data.organization_id,
          createdBy: data.created_by,
          createdAt: data.created_at,
          updatedAt: data.updated_at
        };

        setCurrentDocument(document);
        return document;
      }
    } catch (err) {
      console.error(`Error fetching document with ID ${id}:`, err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file: File, options?: DocumentUploadOptions): Promise<Document> => {
    setLoading(true);
    setError(null);

    try {
      // Try using the controller first
      try {
        const result = await documentController.uploadDocument(file, options);
        setDocuments(prev => [...prev, result]);
        setCurrentDocument(result);
        return result;
      } catch (controllerError) {
        console.warn('Controller error, falling back to direct API access:', controllerError);

        // Fallback to direct API access
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        if (options?.title) {
          formData.append('title', options.title);
        }

        if (options?.tags) {
          formData.append('tags', JSON.stringify(options.tags));
        }

        // Upload to API
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
          throw new Error(result.error || 'Upload failed');
        }

        const newDocument = result.document;

        // Add to documents list
        setDocuments(prev => [newDocument, ...prev]);
        setCurrentDocument(newDocument);

        return newDocument;
      }
    } catch (err) {
      console.error('Error uploading document:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update document
  const updateDocument = async (id: string, data: Partial<Document>): Promise<Document> => {
    setLoading(true);
    setError(null);

    try {
      // Try using the controller if it has this method
      if (documentController.updateDocument) {
        try {
          const result = await documentController.updateDocument(id, data);
          setDocuments(prev => prev.map(doc => doc.id === id ? result : doc));
          if (currentDocument?.id === id) {
            setCurrentDocument(result);
          }
          return result;
        } catch (controllerError) {
          console.warn('Controller error, falling back to direct Supabase access:', controllerError);
        }
      }

      // Fallback to direct Supabase access
      const supabase = getSupabaseClient();
      if (!supabase) {
        throw new Error('Supabase client not available');
      }

      // Convert from camelCase to snake_case
      const dbData: any = {};
      if (data.title !== undefined) dbData.title = data.title;
      if (data.filePath !== undefined) dbData.file_path = data.filePath;
      if (data.fileName !== undefined) dbData.file_name = data.fileName;
      if (data.fileType !== undefined) dbData.file_type = data.fileType;
      if (data.fileSize !== undefined) dbData.file_size = data.fileSize;
      if (data.content !== undefined) dbData.content = data.content;
      if (data.metadata !== undefined) dbData.metadata = data.metadata;
      if (data.tags !== undefined) dbData.tags = data.tags;

      const { data: updatedData, error } = await supabase
        .from('documents')
        .update(dbData)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        throw error;
      }

      // Convert from snake_case to camelCase
      const updatedDocument: Document = {
        id: updatedData.id,
        title: updatedData.title,
        filePath: updatedData.file_path,
        fileName: updatedData.file_name,
        fileType: updatedData.file_type,
        fileSize: updatedData.file_size,
        content: updatedData.content,
        metadata: updatedData.metadata,
        tags: updatedData.tags || [],
        organizationId: updatedData.organization_id,
        createdBy: updatedData.created_by,
        createdAt: updatedData.created_at,
        updatedAt: updatedData.updated_at
      };

      // Update documents list
      setDocuments(prev => prev.map(doc => doc.id === id ? updatedDocument : doc));

      // Update current document if it's the one being edited
      if (currentDocument && currentDocument.id === id) {
        setCurrentDocument(updatedDocument);
      }

      return updatedDocument;
    } catch (err) {
      console.error('Error updating document:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // Try using the controller first
      try {
        const success = await documentController.deleteDocument(id);
        if (success) {
          setDocuments(prev => prev.filter(doc => doc.id !== id));
          if (currentDocument?.id === id) {
            setCurrentDocument(null);
          }
          return true;
        }
        return false;
      } catch (controllerError) {
        console.warn('Controller error, falling back to direct Supabase access:', controllerError);

        // Fallback to direct Supabase access
        const supabase = getSupabaseClient();
        if (!supabase) {
          throw new Error('Supabase client not available');
        }

        const { error } = await supabase
          .from('documents')
          .delete()
          .eq('id', id);

        if (error) {
          throw error;
        }

        // Update documents list
        setDocuments(prev => prev.filter(doc => doc.id !== id));

        // Clear current document if it's the one being deleted
        if (currentDocument && currentDocument.id === id) {
          setCurrentDocument(null);
        }

        return true;
      }
    } catch (err) {
      console.error(`Error deleting document with ID ${id}:`, err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    getAllDocuments();
  }, []);

  const value = {
    documents,
    currentDocument,
    loading,
    error,
    getAllDocuments,
    getDocumentById,
    uploadDocument,
    updateDocument,
    deleteDocument
  };

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>;
};
