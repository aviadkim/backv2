import { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import axios from 'axios';

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
    // Parse form data
    const form = new formidable.IncomingForm();
    form.uploadDir = path.join(process.cwd(), 'tmp');
    form.keepExtensions = true;
    
    // Create upload directory if it doesn't exist
    if (!fs.existsSync(form.uploadDir)) {
      fs.mkdirSync(form.uploadDir, { recursive: true });
    }
    
    const [fields, files] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });
    
    const file = files.file;
    const lang = fields.lang || 'heb+eng';
    
    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // Create form data for the API request
    const formData = new FormData();
    formData.append('file', fs.createReadStream(file.filepath));
    formData.append('lang', lang);
    
    // Forward the request to the backend API
    const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    const response = await axios.post(`${apiUrl}/api/financial/process-document`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Clean up the temporary file
    fs.unlinkSync(file.filepath);
    
    // Return the response from the backend
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error processing document:', error);
    return res.status(500).json({ 
      error: 'Error processing document', 
      detail: error.response?.data?.detail || error.message 
    });
  }
}
