import supabaseService from '../services/supabase_service';
import { Document, DocumentUploadOptions } from '../frontend/models/types';

/**
 * Repository for document operations
 */
class DocumentRepository {
  /**
   * Get all documents for the current user's organization
   * @returns Array of documents
   */
  async getAllDocuments(): Promise<Document[]> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return [];
    }

    try {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching documents from Supabase:', error);
        return [];
      }

      return data as Document[];
    } catch (error) {
      console.error('Exception fetching documents from Supabase:', error);
      return [];
    }
  }

  /**
   * Get a document by ID
   * @param id Document ID
   * @returns Document or null if not found
   */
  async getDocumentById(id: string): Promise<Document | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        console.error('Error fetching document from Supabase:', error);
        return null;
      }

      return data as Document;
    } catch (error) {
      console.error('Exception fetching document from Supabase:', error);
      return null;
    }
  }

  /**
   * Upload a document to Supabase Storage and create a record in the documents table
   * @param file File to upload
   * @param options Upload options
   * @returns Created document
   */
  async uploadDocument(file: File, options?: DocumentUploadOptions): Promise<Document | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      // 1. Upload file to Supabase Storage
      const fileExt = file.name.split('.').pop();
      const fileName = `${Math.random().toString(36).substring(2, 15)}.${fileExt}`;
      const filePath = `${options?.organizationId || 'public'}/${fileName}`;

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('documents')
        .upload(filePath, file);

      if (uploadError) {
        console.error('Error uploading file to Supabase Storage:', uploadError);
        return null;
      }

      // 2. Get public URL for the file
      const { data: urlData } = supabase.storage
        .from('documents')
        .getPublicUrl(filePath);

      // 3. Create document record in the database
      const { data: documentData, error: documentError } = await supabase
        .from('documents')
        .insert({
          organization_id: options?.organizationId || null,
          title: options?.title || file.name,
          description: options?.description || '',
          file_path: filePath,
          file_name: file.name,
          file_type: file.type,
          file_size: file.size,
          tags: options?.tags || [],
          created_by: options?.userId || null,
        })
        .select()
        .single();

      if (documentError) {
        console.error('Error creating document record in Supabase:', documentError);
        return null;
      }

      return documentData as Document;
    } catch (error) {
      console.error('Exception uploading document to Supabase:', error);
      return null;
    }
  }

  /**
   * Update a document
   * @param id Document ID
   * @param data Updated document data
   * @returns Updated document
   */
  async updateDocument(id: string, data: Partial<Document>): Promise<Document | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      const { data: updatedData, error } = await supabase
        .from('documents')
        .update(data)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('Error updating document in Supabase:', error);
        return null;
      }

      return updatedData as Document;
    } catch (error) {
      console.error('Exception updating document in Supabase:', error);
      return null;
    }
  }

  /**
   * Delete a document
   * @param id Document ID
   * @returns True if successful, false otherwise
   */
  async deleteDocument(id: string): Promise<boolean> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return false;
    }

    try {
      // 1. Get the document to find the file path
      const { data: document, error: getError } = await supabase
        .from('documents')
        .select('file_path')
        .eq('id', id)
        .single();

      if (getError) {
        console.error('Error getting document for deletion:', getError);
        return false;
      }

      // 2. Delete the file from storage
      if (document && document.file_path) {
        const { error: storageError } = await supabase.storage
          .from('documents')
          .remove([document.file_path]);

        if (storageError) {
          console.error('Error deleting file from Supabase Storage:', storageError);
          // Continue with deleting the record even if file deletion fails
        }
      }

      // 3. Delete the document record
      const { error: deleteError } = await supabase
        .from('documents')
        .delete()
        .eq('id', id);

      if (deleteError) {
        console.error('Error deleting document from Supabase:', deleteError);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Exception deleting document from Supabase:', error);
      return false;
    }
  }
}

// Export a singleton instance
const documentRepository = new DocumentRepository();
export default documentRepository;
