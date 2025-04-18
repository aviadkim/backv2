// API endpoint for fetching financial documents

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // In a real implementation, we would fetch documents from the database
    // For now, we'll return mock data
    
    // Generate mock documents
    const mockDocuments = [
      {
        id: '1',
        filename: 'portfolio-statement-2023-q1.pdf',
        processed_at: '2023-01-15T00:00:00Z',
        document_type: 'portfolio',
        status: 'valid',
        portfolio_value: 1850000
      },
      {
        id: '2',
        filename: 'portfolio-statement-2023-q2.pdf',
        processed_at: '2023-04-15T00:00:00Z',
        document_type: 'portfolio',
        status: 'valid',
        portfolio_value: 1950000
      },
      {
        id: '3',
        filename: 'trade-confirmation-msft.pdf',
        processed_at: '2023-05-10T00:00:00Z',
        document_type: 'trade',
        status: 'valid'
      },
      {
        id: '4',
        filename: 'account-statement-may-2023.pdf',
        processed_at: '2023-06-01T00:00:00Z',
        document_type: 'account',
        status: 'valid'
      },
      {
        id: '5',
        filename: 'tax-document-2022.pdf',
        processed_at: '2023-03-15T00:00:00Z',
        document_type: 'tax',
        status: 'valid'
      }
    ];
    
    return res.status(200).json({ documents: mockDocuments });
  } catch (error) {
    console.error('Error fetching documents:', error);
    return res.status(500).json({ 
      error: 'Error fetching documents', 
      detail: error.message 
    });
  }
}
