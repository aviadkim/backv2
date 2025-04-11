import { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { getServiceSupabaseClient } from '../../../lib/supabaseClient';

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
    
    // Simulate document processing
    const processingResult = await simulateDocumentProcessing(filePath, fileType);
    
    // Clean up the temporary file
    fs.unlinkSync(filePath);
    
    // Return the processing result
    return res.status(200).json({
      success: true,
      document: {
        id: `test-${Date.now()}`,
        title: fields.title || fileName,
        fileName,
        fileType,
        fileSize,
        createdAt: new Date().toISOString(),
        processingResult
      }
    });
  } catch (error) {
    console.error('Error processing document:', error);
    return res.status(500).json({ error: 'Error processing document' });
  }
}

async function simulateDocumentProcessing(filePath, fileType) {
  // In a real implementation, this would call the backend document processor
  // For this test, we'll simulate processing results
  
  // Determine file extension
  const ext = path.extname(filePath).toLowerCase();
  
  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Generate simulated results based on file type
  if (ext === '.pdf' || fileType.includes('pdf')) {
    return {
      type: 'pdf',
      pages: 5,
      text: 'Sample extracted text from PDF...',
      isins: ['US0378331005', 'US5949181045', 'US88160R1014'],
      tables: [
        {
          page: 1,
          rows: 3,
          columns: 3,
          headers: ['Security', 'ISIN', 'Value'],
          data: [
            { Security: 'Apple Inc.', ISIN: 'US0378331005', Value: '$17,635.00' },
            { Security: 'Microsoft Corporation', ISIN: 'US5949181045', Value: '$20,613.50' },
            { Security: 'Tesla Inc.', ISIN: 'US88160R1014', Value: '$4,383.50' }
          ]
        }
      ]
    };
  } else if (['.xlsx', '.xls'].includes(ext) || fileType.includes('excel') || fileType.includes('spreadsheet')) {
    return {
      type: 'excel',
      sheets: [
        {
          name: 'Sheet1',
          rows: 10,
          columns: 5,
          data: [
            { Security: 'Apple Inc.', ISIN: 'US0378331005', Shares: 100, Price: 176.35, Value: 17635.00 },
            { Security: 'Microsoft Corporation', ISIN: 'US5949181045', Shares: 50, Price: 412.27, Value: 20613.50 },
            { Security: 'Tesla Inc.', ISIN: 'US88160R1014', Shares: 25, Price: 175.34, Value: 4383.50 }
          ]
        }
      ],
      isins: ['US0378331005', 'US5949181045', 'US88160R1014']
    };
  } else if (ext === '.csv' || fileType.includes('csv')) {
    return {
      type: 'csv',
      rows: 3,
      columns: 5,
      tables: [
        {
          headers: ['Security', 'ISIN', 'Shares', 'Price', 'Value'],
          data: [
            { Security: 'Apple Inc.', ISIN: 'US0378331005', Shares: 100, Price: 176.35, Value: 17635.00 },
            { Security: 'Microsoft Corporation', ISIN: 'US5949181045', Shares: 50, Price: 412.27, Value: 20613.50 },
            { Security: 'Tesla Inc.', ISIN: 'US88160R1014', Shares: 25, Price: 175.34, Value: 4383.50 }
          ]
        }
      ],
      isins: ['US0378331005', 'US5949181045', 'US88160R1014']
    };
  } else if (['.doc', '.docx'].includes(ext) || fileType.includes('word')) {
    return {
      type: 'word',
      text: 'Sample extracted text from Word document...',
      isins: ['US0378331005', 'US5949181045', 'US0231351067']
    };
  } else {
    return {
      type: 'text',
      text: 'Sample extracted text from plain text file...',
      isins: []
    };
  }
}
