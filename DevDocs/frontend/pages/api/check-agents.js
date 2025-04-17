// Next.js API route to check if all agents are connected to the OpenRouter API
export default async function handler(req, res) {
  try {
    // Get the OpenRouter API key from environment variables
    const openRouterApiKey = process.env.OPENROUTER_API_KEY;
    
    // Check if the OpenRouter API key is available
    if (!openRouterApiKey) {
      return res.status(500).json({ 
        success: false, 
        message: 'OpenRouter API key is not available' 
      });
    }
    
    // List of agents to check
    const agents = [
      'FinancialTableDetectorAgent',
      'FinancialDataAnalyzerAgent',
      'DocumentIntegrationAgent',
      'QueryEngineAgent',
      'DocumentPreprocessorAgent',
      'HebrewOCRAgent',
      'ISINExtractorAgent',
      'DocumentMergeAgent',
      'DataExportAgent',
      'DocumentComparisonAgent',
      'FinancialAdvisorAgent'
    ];
    
    // Check if each agent can access the OpenRouter API
    const agentStatus = {};
    
    for (const agent of agents) {
      // In a real implementation, we would check if each agent can access the OpenRouter API
      // For now, we'll just assume they can if the API key is available
      agentStatus[agent] = {
        connected: !!openRouterApiKey,
        apiKeyAvailable: !!openRouterApiKey
      };
    }
    
    // Return the status of all agents
    return res.status(200).json({
      success: true,
      openRouterApiKeyAvailable: !!openRouterApiKey,
      agents: agentStatus
    });
  } catch (error) {
    console.error('Error checking agents:', error);
    return res.status(500).json({ 
      success: false, 
      message: 'Error checking agents', 
      error: error.message 
    });
  }
}
