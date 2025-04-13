import { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { getServiceSupabaseClient } from '../../../lib/supabaseClient';
import { processDocument } from '../../../services/documentProcessing';

// Disable the default body parser to handle file uploads
export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Parse the multipart form data
    const form = new formidable.IncomingForm();
    form.keepExtensions = true;
    form.uploadDir = path.join(process.cwd(), 'tmp');

    // Ensure upload directory exists
    if (!fs.existsSync(form.uploadDir)) {
      fs.mkdirSync(form.uploadDir, { recursive: true });
    }

    // Parse the form
    const [fields, files] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    // Get the uploaded file
    const file = files.file;
    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Get file details
    const filePath = file.filepath;
    const fileName = file.originalFilename;
    const fileType = file.mimetype;
    const fileSize = file.size;

    // Process the document using our custom document processing service
    // This uses our own code, not external APIs, to avoid costs
    const fileBuffer = fs.readFileSync(filePath);
    const processingResult = await processDocument(fileBuffer, fileType);

    // Clean up the temporary file
    fs.unlinkSync(filePath);

    // Extract tags if provided
    let tags = [];
    if (fields.tags) {
      try {
        tags = JSON.parse(fields.tags);
      } catch (e) {
        console.warn('Failed to parse tags:', e);
      }
    }

    // Create document record
    const document = {
      id: `doc-${Date.now()}`,
      title: fields.title || fileName.split('.')[0],
      fileName,
      fileType,
      fileSize,
      tags,
      createdAt: new Date().toISOString(),
      processingResult
    };

    // In a real implementation, you would save the document to Supabase here
    // const supabase = getServiceSupabaseClient();
    // if (supabase) {
    //   const { data, error } = await supabase
    //     .from('documents')
    //     .insert(document);
    //
    //   if (error) {
    //     console.error('Error saving document to Supabase:', error);
    //   }
    // }

    // Return the processing result
    return res.status(200).json({
      success: true,
      document
    });
  } catch (error) {
    console.error('Error processing document:', error);
    return res.status(500).json({
      error: 'Error processing document',
      message: error.message
    });
  }
}
