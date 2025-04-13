import formidable from 'formidable';
import fs from 'fs';

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
 * API handler for OCR operations
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

    // Check if Vision API is configured
    const visionApiEnabled = process.env.NEXT_PUBLIC_VISION_API_ENABLED === 'true';
    const googleCredentials = process.env.GOOGLE_APPLICATION_CREDENTIALS;
    
    if (!visionApiEnabled || !googleCredentials) {
      // Return a simulated response if Vision API is not configured
      return res.status(200).json({
        success: true,
        text: simulateOcrResponse(file.originalFilename || 'unknown.jpg'),
        confidence: 0.8
      });
    }
    
    // TODO: Implement actual Vision API call
    // This would require the Google Cloud Vision Node.js client library
    // and proper authentication with the service account
    
    // For now, return a simulated response
    return res.status(200).json({
      success: true,
      text: simulateOcrResponse(file.originalFilename || 'unknown.jpg'),
      confidence: 0.8
    });
  } catch (error) {
    console.error('Error processing OCR request:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message || 'Failed to process OCR request' 
    });
  }
}

/**
 * Simulate an OCR response for testing
 * @param {string} filename - The filename
 * @returns {string} The simulated OCR text
 */
function simulateOcrResponse(filename) {
  // Generate different responses based on the filename
  const lowerFilename = filename.toLowerCase();
  
  if (lowerFilename.includes('invoice')) {
    return `INVOICE
Invoice Number: INV-2023-1234
Date: 2023-10-15
Due Date: 2023-11-15

Bill To:
John Doe
123 Main St
Anytown, CA 12345

Description                   Quantity    Rate    Amount
Web Development Services      40 hours    $75     $3,000
UI/UX Design                  20 hours    $85     $1,700
Server Configuration          5 hours     $95     $475

Subtotal: $5,175
Tax (8%): $414
Total: $5,589

Payment Terms: Net 30
Thank you for your business!`;
  }
  
  if (lowerFilename.includes('receipt')) {
    return `RECEIPT
Store: Grocery Mart
Date: 2023-10-10
Time: 14:32:45

Items:
1. Apples (1kg)              $3.99
2. Milk (1 gallon)           $4.29
3. Bread (whole wheat)       $3.49
4. Eggs (dozen)              $5.99
5. Chicken Breast (2lbs)     $12.99

Subtotal: $30.75
Tax: $2.46
Total: $33.21

Payment Method: Credit Card
Card ending in: 1234

Thank you for shopping with us!`;
  }
  
  if (lowerFilename.includes('statement') || lowerFilename.includes('bank')) {
    return `BANK STATEMENT
Account Number: XXXX-XXXX-1234
Statement Period: 09/15/2023 - 10/15/2023
Opening Balance: $5,432.10

Transactions:
09/18/2023  Deposit            +$2,500.00
09/20/2023  Check #1234        -$150.00
09/25/2023  ATM Withdrawal     -$200.00
09/28/2023  Direct Deposit     +$1,750.00
10/01/2023  Monthly Fee        -$12.00
10/05/2023  Online Payment     -$500.00
10/10/2023  Grocery Store      -$87.65
10/12/2023  Gas Station        -$45.23

Closing Balance: $8,687.22

Available Balance: $8,687.22`;
  }
  
  // Default response for other files
  return `Sample Document
Date: October 15, 2023

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, 
nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies
nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt, nisl
nisl aliquam nisl, eget ultricies nisl nisl eget nisl.

Contact Information:
Name: John Doe
Email: john.doe@example.com
Phone: (123) 456-7890

Thank you for your attention to this matter.

Sincerely,
John Doe`;
}
