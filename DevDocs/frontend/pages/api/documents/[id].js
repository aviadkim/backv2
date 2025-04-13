import getSupabaseClient from '../../../lib/supabaseClient';

/**
 * API handler for document operations by ID
 * @param {import('next').NextApiRequest} req - The request object
 * @param {import('next').NextApiResponse} res - The response object
 */
export default async function handler(req, res) {
  // Get the document ID from the URL
  const { id } = req.query;
  
  // Get the Supabase client
  const supabase = getSupabaseClient();
  
  if (!supabase) {
    return res.status(500).json({ 
      success: false, 
      error: 'Supabase client not available' 
    });
  }

  // Handle different HTTP methods
  switch (req.method) {
    case 'GET':
      try {
        // Get document by ID
        const { data, error } = await supabase
          .from('documents')
          .select('*')
          .eq('id', id)
          .single();

        if (error) {
          throw error;
        }

        if (!data) {
          return res.status(404).json({ 
            success: false, 
            error: 'Document not found' 
          });
        }

        return res.status(200).json({ 
          success: true, 
          document: data 
        });
      } catch (error) {
        console.error(`Error fetching document with ID ${id}:`, error);
        return res.status(500).json({ 
          success: false, 
          error: error.message || 'Failed to fetch document' 
        });
      }

    case 'DELETE':
      try {
        // Get the document to find the file path
        const { data: document, error: getError } = await supabase
          .from('documents')
          .select('file_path')
          .eq('id', id)
          .single();

        if (getError) {
          throw getError;
        }

        // Delete the document record
        const { error: deleteError } = await supabase
          .from('documents')
          .delete()
          .eq('id', id);

        if (deleteError) {
          throw deleteError;
        }

        // Delete the file from storage if it exists
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

        return res.status(200).json({ 
          success: true, 
          message: 'Document deleted successfully' 
        });
      } catch (error) {
        console.error(`Error deleting document with ID ${id}:`, error);
        return res.status(500).json({ 
          success: false, 
          error: error.message || 'Failed to delete document' 
        });
      }

    default:
      return res.status(405).json({ 
        success: false, 
        error: 'Method not allowed' 
      });
  }
}
