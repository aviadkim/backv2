import getSupabaseClient from '../lib/supabaseClient';

class DocumentRepository {
  /**
   * Get all documents for the current user's organization
   */
  async getAllDocuments() {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.getAllDocumentsFromApi();
    }

    try {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching documents from Supabase:', error);
        return this.getAllDocumentsFromApi();
      }

      return data;
    } catch (error) {
      console.error('Exception fetching documents from Supabase:', error);
      return this.getAllDocumentsFromApi();
    }
  }

  /**
   * Get a document by ID
   */
  async getDocumentById(id) {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.getDocumentByIdFromApi(id);
    }

    try {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        console.error('Error fetching document from Supabase:', error);
        return this.getDocumentByIdFromApi(id);
      }

      return data;
    } catch (error) {
      console.error('Exception fetching document from Supabase:', error);
      return this.getDocumentByIdFromApi(id);
    }
  }

  /**
   * Upload a document
   */
  async uploadDocument(file, options) {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.uploadDocumentToApi(file, options);
    }

    try {
      // 1. Upload file to Supabase Storage
      const fileName = file.name;
      const fileExt = fileName.split('.').pop();
      const filePath = `documents/${Date.now()}_${fileName}`;

      const { data: fileData, error: fileError } = await supabase
        .storage
        .from('documents')
        .upload(filePath, file);

      if (fileError) {
        console.error('Error uploading file to Supabase Storage:', fileError);
        return this.uploadDocumentToApi(file, options);
      }

      // 2. Create document record in database
      const { data: document, error: docError } = await supabase
        .from('documents')
        .insert({
          title: options?.title || fileName.replace(`.${fileExt}`, ''),
          description: options?.description || '',
          file_path: filePath,
          file_name: fileName,
          file_type: fileExt?.toUpperCase() || 'UNKNOWN',
          file_size: file.size,
          tags: options?.tags || [],
          metadata: {
            processingOptions: options?.processingOptions || {}
          }
        })
        .select()
        .single();

      if (docError) {
        console.error('Error creating document record in Supabase:', docError);
        return this.uploadDocumentToApi(file, options);
      }

      return document;
    } catch (error) {
      console.error('Exception uploading document to Supabase:', error);
      return this.uploadDocumentToApi(file, options);
    }
  }

  /**
   * Delete a document
   */
  async deleteDocument(id) {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.deleteDocumentFromApi(id);
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
        return this.deleteDocumentFromApi(id);
      }

      // 2. Delete the document record
      const { error: deleteError } = await supabase
        .from('documents')
        .delete()
        .eq('id', id);

      if (deleteError) {
        console.error('Error deleting document record:', deleteError);
        return this.deleteDocumentFromApi(id);
      }

      // 3. Delete the file from storage
      if (document && document.file_path) {
        const { error: storageError } = await supabase
          .storage
          .from('documents')
          .remove([document.file_path]);

        if (storageError) {
          console.error('Error deleting file from storage:', storageError);
          // Continue anyway since the database record is deleted
        }
      }

      return true;
    } catch (error) {
      console.error('Exception deleting document from Supabase:', error);
      return this.deleteDocumentFromApi(id);
    }
  }

  // Fallback methods that use the API

  async getAllDocumentsFromApi() {
    try {
      const response = await fetch('/api/documents');
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      return data.documents || [];
    } catch (error) {
      console.error('Error fetching documents from API:', error);
      return [];
    }
  }

  async getDocumentByIdFromApi(id) {
    try {
      const response = await fetch(`/api/documents/${id}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      return data.document || null;
    } catch (error) {
      console.error('Error fetching document from API:', error);
      return null;
    }
  }

  async uploadDocumentToApi(file, options) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (options?.title) {
        formData.append('title', options.title);
      }
      
      if (options?.tags && options.tags.length > 0) {
        formData.append('tags', JSON.stringify(options.tags));
      }
      
      if (options?.processingOptions) {
        formData.append('processing_options', JSON.stringify(options.processingOptions));
      }
      
      const response = await fetch('/api/documents', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.document;
    } catch (error) {
      console.error('Error uploading document to API:', error);
      throw error;
    }
  }

  async deleteDocumentFromApi(id) {
    try {
      const response = await fetch(`/api/documents/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting document from API:', error);
      return false;
    }
  }
}

export default new DocumentRepository();
