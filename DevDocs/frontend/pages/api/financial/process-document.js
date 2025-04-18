import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

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
    const documentType = fields.document_type || 'financial';

    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Process the document (mock implementation)
    const result = await mockProcessDocument(file.filepath, documentType);

    // Clean up the temporary file
    fs.unlinkSync(file.filepath);

    // Return the mock response
    return res.status(200).json(result);
  } catch (error) {
    console.error('Error processing document:', error);
    return res.status(500).json({
      error: 'Error processing document',
      detail: error.message
    });
  }
}

// Mock implementation of document processing
async function mockProcessDocument(filePath, documentType) {
  // Create a unique ID for the document
  const documentId = uuidv4();

  // Return mock data
  return {
    document_id: documentId,
    document_type: documentType,
    extracted_text: "This is a financial document with portfolio value of $19,510,599. It contains various securities including stocks, bonds, and structured products.",
    tables: [
      {
        page: 1,
        extraction_method: 'mock',
        table_number: 1,
        headers: ['Security', 'ISIN', 'Quantity', 'Price', 'Value'],
        rows: [
          ['Apple Inc.', 'US0378331005', '100', '$175.50', '$17,550.00'],
          ['Tesla Inc.', 'US88160R1014', '20', '$219.50', '$4,390.00'],
          ['Microsoft Corp.', 'US5949181045', '50', '$410.30', '$20,515.00'],
          ['Structured Product 1', 'CH1259344831', '250', '$999.20', '$249,800.00'],
          ['Structured Product 2', 'CH0123456789', '7600', '$1,000.00', '$7,600,457.00']
        ]
      },
      {
        page: 2,
        extraction_method: 'mock',
        table_number: 2,
        headers: ['Asset Class', 'Allocation', 'Value'],
        rows: [
          ['Equities', '25%', '$4,877,649.75'],
          ['Fixed Income', '15%', '$2,926,589.85'],
          ['Structured Products', '40%', '$7,850,257.00'],
          ['Cash', '10%', '$1,951,059.90'],
          ['Alternative Investments', '10%', '$1,951,059.90']
        ]
      }
    ],
    financial_data: {
      portfolio_value: 19510599,
      asset_allocation: {
        'Equities': 0.25,
        'Fixed Income': 0.15,
        'Structured Products': 0.40,
        'Cash': 0.10,
        'Alternative Investments': 0.10
      },
      securities: [
        {
          name: 'Apple Inc.',
          isin: 'US0378331005',
          quantity: 100,
          price: 175.50,
          value: 17550.00
        },
        {
          name: 'Tesla Inc.',
          isin: 'US88160R1014',
          quantity: 20,
          price: 219.50,
          value: 4390.00
        },
        {
          name: 'Microsoft Corp.',
          isin: 'US5949181045',
          quantity: 50,
          price: 410.30,
          value: 20515.00
        },
        {
          name: 'Structured Product 1',
          isin: 'CH1259344831',
          quantity: 250,
          price: 999.20,
          value: 249800.00
        },
        {
          name: 'Structured Product 2',
          isin: 'CH0123456789',
          quantity: 7600,
          price: 1000.00,
          value: 7600457.00
        }
      ]
    },
    entities: {
      isin: [
        {
          code: 'US0378331005',
          name: 'Apple Inc.',
          value: 17550.00
        },
        {
          code: 'US88160R1014',
          name: 'Tesla Inc.',
          value: 4390.00
        },
        {
          code: 'US5949181045',
          name: 'Microsoft Corp.',
          value: 20515.00
        },
        {
          code: 'CH1259344831',
          name: 'Structured Product 1',
          value: 249800.00
        },
        {
          code: 'CH0123456789',
          name: 'Structured Product 2',
          value: 7600457.00
        }
      ]
    }
  };
}
