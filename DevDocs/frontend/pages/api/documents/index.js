import getSupabaseClient from '../../../lib/supabaseClient';

/**
 * API handler for document operations
 * @param {import('next').NextApiRequest} req - The request object
 * @param {import('next').NextApiResponse} res - The response object
 */
export default async function handler(req, res) {
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
        // Get all documents
        const { data, error } = await supabase
          .from('documents')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) {
          throw error;
        }

        return res.status(200).json({ 
          success: true, 
          documents: data 
        });
      } catch (error) {
        console.error('Error fetching documents:', error);
        return res.status(500).json({ 
          success: false, 
          error: error.message || 'Failed to fetch documents' 
        });
      }

    case 'POST':
      try {
        // Create a new document
        const { title, content, metadata, tags } = req.body;
        
        const { data, error } = await supabase
          .from('documents')
          .insert([{ 
            title, 
            content, 
            metadata, 
            tags,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }])
          .select();

        if (error) {
          throw error;
        }

        return res.status(201).json({ 
          success: true, 
          document: data[0] 
        });
      } catch (error) {
        console.error('Error creating document:', error);
        return res.status(500).json({ 
          success: false, 
          error: error.message || 'Failed to create document' 
        });
      }

    default:
      return res.status(405).json({ 
        success: false, 
        error: 'Method not allowed' 
      });
  }
}
