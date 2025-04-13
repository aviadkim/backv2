import formidable from 'formidable';
import getSupabaseClient from '../../../lib/supabaseClient';

// Disable the default body parser to handle form data
export const config = {
  api: {
    bodyParser: false,
  },
};

/**
 * Parse form data
 * @param {import('next').NextApiRequest} req - The request object
 * @returns {Promise<{fields: any, files: any}>} Parsed form data
 */
const parseForm = (req) => {
  return new Promise((resolve, reject) => {
    const form = new formidable.IncomingForm();
    form.parse(req, (err, fields, files) => {
      if (err) reject(err);
      resolve({ fields, files });
    });
  });
};

/**
 * API handler for document uploads
 * @param {import('next').NextApiRequest} req - The request object
 * @param {import('next').NextApiResponse} res - The response object
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  try {
    // Parse the form data
    const { fields, files } = await parseForm(req);
    const file = files.file;

    if (!file) {
      return res.status(400).json({ 
        success: false, 
        error: 'No file provided' 
      });
    }

    // Get the Supabase client
    const supabase = getSupabaseClient();
    
    if (!supabase) {
      return res.status(500).json({ 
        success: false, 
        error: 'Supabase client not available' 
      });
    }

    // Process options
    const title = fields.title || file.originalFilename;
    const tags = fields.tags ? JSON.parse(fields.tags) : [];
    const processingOptions = fields.processing_options ? JSON.parse(fields.processing_options) : {};

    // 1. Upload file to Supabase Storage
    const fileName = file.originalFilename;
    const fileExt = fileName.split('.').pop();
    const filePath = `documents/${Date.now()}_${fileName}`;

    // Read the file
    const fs = require('fs');
    const fileData = fs.readFileSync(file.filepath);

    const { data: uploadData, error: uploadError } = await supabase
      .storage
      .from('documents')
      .upload(filePath, fileData, {
        contentType: file.mimetype,
      });

    if (uploadError) {
      throw uploadError;
    }

    // 2. Create document record in database
    const { data: document, error: docError } = await supabase
      .from('documents')
      .insert({
        title,
        file_path: filePath,
        file_name: fileName,
        file_type: fileExt?.toUpperCase() || 'UNKNOWN',
        file_size: file.size,
        tags,
        metadata: {
          processingOptions
        }
      })
      .select()
      .single();

    if (docError) {
      throw docError;
    }

    return res.status(201).json({ 
      success: true, 
      document 
    });
  } catch (error) {
    console.error('Error uploading document:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message || 'Failed to upload document' 
    });
  }
}
