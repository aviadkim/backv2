/**
 * Test script for PDF processing with Google API
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const { createClient } = require('@supabase/supabase-js');

// Import the HebrewOCRAgent
const HebrewOCRAgent = require('./DevDocs/backend/agents/HebrewOCRAgent');

// Google API key for testing (will be deleted after testing)
const GOOGLE_API_KEY = 'AIzaSyBmRbgqfJYNt5fRlFBgr0Css_eUH3IKPoI';

// Mock the Supabase client
const mockSupabaseClient = {
  from: () => ({
    select: () => ({
      eq: () => ({
        single: async () => ({ data: { id: 'mock-document-id', name: 'messos.pdf' }, error: null })
      }),
      eq: () => ({
        order: () => ({
          limit: async () => ({ data: [], error: null })
        })
      })
    }),
    insert: async () => ({ data: { id: 'mock-data-id' }, error: null }),
    update: async () => ({ data: { id: 'mock-document-id' }, error: null })
  }),
  storage: {
    from: () => ({
      upload: async () => ({ data: { path: 'mock-path' }, error: null })
    })
  }
};

// Mock the config module
jest.mock('./DevDocs/backend/config', () => ({
  database: {
    url: 'https://mock-supabase-url.com',
    key: 'mock-supabase-key'
  },
  api: {
    openrouterApiKey: GOOGLE_API_KEY
  },
  upload: {
    uploadDir: './uploads',
    tempDir: './temp'
  }
}));

// Mock the Supabase module
jest.mock('./DevDocs/backend/db/supabase', () => ({
  getClient: () => mockSupabaseClient,
  executeQuery: async (queryFn) => {
    const result = await queryFn(mockSupabaseClient);
    return { data: result.data, error: null };
  }
}));

async function testPDFProcessing() {
  try {
    console.log('Testing PDF processing with HebrewOCRAgent and Google API...');
    
    // Create an instance of the HebrewOCRAgent
    const ocrAgent = new HebrewOCRAgent({
      apiKey: GOOGLE_API_KEY
    });
    
    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');
    
    // Read the PDF file
    const pdfBuffer = await readFile(pdfPath);
    
    // Process the PDF
    console.log('Processing PDF...');
    const result = await ocrAgent.processDocument({
      buffer: pdfBuffer,
      fileName: 'messos.pdf',
      language: 'heb+eng'
    });
    
    console.log('PDF processing result:');
    console.log(JSON.stringify(result, null, 2));
    
    return result;
  } catch (error) {
    console.error('Error processing PDF:', error);
    return null;
  }
}

// Run the test
testPDFProcessing();
