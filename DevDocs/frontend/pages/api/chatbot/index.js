/**
 * API handler for chatbot interactions
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
    const { text, sessionId } = req.body;
    
    if (!text) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required parameter: text' 
      });
    }
    
    // Check if Dialogflow is configured
    const dialogflowEnabled = process.env.NEXT_PUBLIC_CHATBOT_ENABLED === 'true';
    const dialogflowCredentials = process.env.DIALOGFLOW_CREDENTIALS;
    const dialogflowAgentId = process.env.NEXT_PUBLIC_DIALOGFLOW_AGENT_ID;
    
    if (!dialogflowEnabled || !dialogflowCredentials || !dialogflowAgentId) {
      // Return a simulated response if Dialogflow is not configured
      return res.status(200).json({
        success: true,
        fulfillmentText: simulateChatbotResponse(text),
        intent: 'simulated.intent',
        intentDetectionConfidence: 0.8
      });
    }
    
    // TODO: Implement actual Dialogflow API call
    // This would require the Dialogflow Node.js client library
    // and proper authentication with the service account
    
    // For now, return a simulated response
    return res.status(200).json({
      success: true,
      fulfillmentText: simulateChatbotResponse(text),
      intent: 'simulated.intent',
      intentDetectionConfidence: 0.8
    });
  } catch (error) {
    console.error('Error processing chatbot request:', error);
    return res.status(500).json({ 
      success: false, 
      error: error.message || 'Failed to process chatbot request' 
    });
  }
}

/**
 * Simulate a chatbot response for testing
 * @param {string} text - The user's message
 * @returns {string} The simulated response
 */
function simulateChatbotResponse(text) {
  // Simple keyword-based responses
  const lowerText = text.toLowerCase();
  
  if (lowerText.includes('hello') || lowerText.includes('hi')) {
    return 'Hello! How can I help you with your financial documents today?';
  }
  
  if (lowerText.includes('help')) {
    return 'I can help you with document analysis, financial reporting, and portfolio management. What would you like to know?';
  }
  
  if (lowerText.includes('document') || lowerText.includes('upload')) {
    return 'You can upload documents by going to the Documents page and clicking the Upload button. I support PDF, DOC, DOCX, XLS, XLSX, and CSV files.';
  }
  
  if (lowerText.includes('portfolio') || lowerText.includes('investment')) {
    return 'I can analyze your investment portfolio and provide insights on asset allocation, performance, and risk. Would you like to see a demo?';
  }
  
  if (lowerText.includes('report') || lowerText.includes('reporting')) {
    return 'I can generate financial reports based on your documents and portfolio data. You can customize the reports and export them as PDF or Excel files.';
  }
  
  if (lowerText.includes('ocr') || lowerText.includes('extract')) {
    return 'I use OCR technology to extract text and data from your documents. This helps automate data entry and analysis.';
  }
  
  if (lowerText.includes('api') || lowerText.includes('key')) {
    return 'You can configure API keys in the Settings page. I need API keys for Supabase, Google Cloud, OCR, and chatbot services.';
  }
  
  // Default response
  return 'I\'m here to help with your financial document analysis needs. You can ask me about document processing, portfolio analysis, or financial reporting.';
}
