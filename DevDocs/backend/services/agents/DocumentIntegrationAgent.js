/**
 * Document Integration Agent
 * 
 * Integrates data from multiple financial documents to create a comprehensive view.
 */

const axios = require('axios');
const logger = require('../../utils/logger');

class DocumentIntegrationAgent {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.OPENROUTER_API_KEY;
    this.model = options.model || 'anthropic/claude-3-opus:beta';
    this.apiUrl = options.apiUrl || 'https://openrouter.ai/api/v1/chat/completions';
    this.logger = logger;
  }

  /**
   * Integrate data from multiple documents
   * @param {Array} documents - Array of document data objects
   * @param {Object} options - Integration options
   * @returns {Promise<Object>} - Integrated data
   */
  async integrateDocuments(documents, options = {}) {
    this.logger.info(`Integrating ${documents.length} documents`);
    
    try {
      if (!documents || documents.length === 0) {
        throw new Error('No documents provided for integration');
      }
      
      // Sort documents by date (newest first)
      const sortedDocuments = [...documents].sort((a, b) => {
        return new Date(b.processed_at) - new Date(a.processed_at);
      });
      
      // Extract document types
      const documentTypes = new Set(sortedDocuments.map(doc => doc.document_type));
      
      // Determine integration strategy based on document types
      let integrationStrategy = 'default';
      
      if (documentTypes.size === 1) {
        // All documents are of the same type
        integrationStrategy = sortedDocuments[0].document_type;
      } else if (documentTypes.has('portfolio') && documentTypes.has('trade')) {
        // Portfolio and trade documents
        integrationStrategy = 'portfolio_trade';
      }
      
      // Perform integration based on strategy
      let integratedData;
      
      switch (integrationStrategy) {
        case 'portfolio':
          integratedData = await this._integratePortfolioDocuments(sortedDocuments, options);
          break;
        case 'trade':
          integratedData = await this._integrateTradeDocuments(sortedDocuments, options);
          break;
        case 'portfolio_trade':
          integratedData = await this._integratePortfolioTradeDocuments(sortedDocuments, options);
          break;
        default:
          integratedData = await this._integrateGenericDocuments(sortedDocuments, options);
      }
      
      return {
        integrated_at: new Date().toISOString(),
        document_count: documents.length,
        document_types: Array.from(documentTypes),
        integration_strategy: integrationStrategy,
        ...integratedData
      };
    } catch (error) {
      this.logger.error(`Error integrating documents: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Integrate portfolio documents
   * @param {Array} documents - Array of portfolio documents
   * @param {Object} options - Integration options
   * @returns {Promise<Object>} - Integrated portfolio data
   * @private
   */
  async _integratePortfolioDocuments(documents, options) {
    this.logger.info(`Integrating ${documents.length} portfolio documents`);
    
    // Get the most recent document for current portfolio state
    const currentDocument = documents[0];
    
    // Extract historical data from older documents
    const historicalData = documents.slice(1).map(doc => ({
      date: doc.processed_at,
      portfolio_value: doc.portfolio_value,
      asset_allocation: doc.asset_allocation
    }));
    
    // Create integrated portfolio data
    const integratedData = {
      portfolio: {
        current: {
          date: currentDocument.processed_at,
          portfolio_value: currentDocument.portfolio_value,
          asset_allocation: currentDocument.asset_allocation
        },
        historical: historicalData
      },
      securities: this._integrateSecurities(documents),
      performance: this._calculatePerformance(documents)
    };
    
    // Add AI-enhanced insights if API key is available
    if (this.apiKey && options.includeInsights !== false) {
      integratedData.insights = await this._generateInsights(documents);
    }
    
    return integratedData;
  }

  /**
   * Integrate trade documents
   * @param {Array} documents - Array of trade documents
   * @param {Object} options - Integration options
   * @returns {Promise<Object>} - Integrated trade data
   * @private
   */
  async _integrateTradeDocuments(documents, options) {
    this.logger.info(`Integrating ${documents.length} trade documents`);
    
    // Extract trades from documents
    const trades = documents.flatMap(doc => {
      if (!doc.trades) return [];
      
      return doc.trades.map(trade => ({
        ...trade,
        document_id: doc.id,
        document_date: doc.processed_at
      }));
    });
    
    // Sort trades by date (newest first)
    const sortedTrades = trades.sort((a, b) => {
      return new Date(b.trade_date || b.document_date) - new Date(a.trade_date || a.document_date);
    });
    
    // Group trades by security
    const tradesBySecurity = {};
    
    sortedTrades.forEach(trade => {
      const securityId = trade.isin || trade.security_id;
      
      if (!securityId) return;
      
      if (!tradesBySecurity[securityId]) {
        tradesBySecurity[securityId] = [];
      }
      
      tradesBySecurity[securityId].push(trade);
    });
    
    // Create integrated trade data
    const integratedData = {
      trades: {
        all: sortedTrades,
        by_security: tradesBySecurity
      },
      trade_summary: this._createTradeSummary(sortedTrades)
    };
    
    // Add AI-enhanced insights if API key is available
    if (this.apiKey && options.includeInsights !== false) {
      integratedData.insights = await this._generateTradeInsights(sortedTrades);
    }
    
    return integratedData;
  }

  /**
   * Integrate portfolio and trade documents
   * @param {Array} documents - Array of portfolio and trade documents
   * @param {Object} options - Integration options
   * @returns {Promise<Object>} - Integrated data
   * @private
   */
  async _integratePortfolioTradeDocuments(documents, options) {
    this.logger.info(`Integrating portfolio and trade documents`);
    
    // Separate documents by type
    const portfolioDocuments = documents.filter(doc => doc.document_type === 'portfolio');
    const tradeDocuments = documents.filter(doc => doc.document_type === 'trade');
    
    // Integrate portfolio documents
    const portfolioData = await this._integratePortfolioDocuments(portfolioDocuments, { includeInsights: false });
    
    // Integrate trade documents
    const tradeData = await this._integrateTradeDocuments(tradeDocuments, { includeInsights: false });
    
    // Combine the data
    const integratedData = {
      portfolio: portfolioData.portfolio,
      securities: portfolioData.securities,
      performance: portfolioData.performance,
      trades: tradeData.trades,
      trade_summary: tradeData.trade_summary
    };
    
    // Add AI-enhanced insights if API key is available
    if (this.apiKey && options.includeInsights !== false) {
      integratedData.insights = await this._generateCombinedInsights(portfolioDocuments, tradeDocuments);
    }
    
    return integratedData;
  }

  /**
   * Integrate generic documents
   * @param {Array} documents - Array of documents
   * @param {Object} options - Integration options
   * @returns {Promise<Object>} - Integrated data
   * @private
   */
  async _integrateGenericDocuments(documents, options) {
    this.logger.info(`Integrating generic documents`);
    
    // Create a simple integration of document metadata
    const integratedData = {
      documents: documents.map(doc => ({
        id: doc.id,
        filename: doc.filename,
        document_type: doc.document_type,
        processed_at: doc.processed_at
      }))
    };
    
    // Add AI-enhanced insights if API key is available
    if (this.apiKey && options.includeInsights !== false) {
      integratedData.insights = await this._generateGenericInsights(documents);
    }
    
    return integratedData;
  }

  /**
   * Integrate securities data from multiple documents
   * @param {Array} documents - Array of documents
   * @returns {Object} - Integrated securities data
   * @private
   */
  _integrateSecurities(documents) {
    // Get the most recent document for current securities
    const currentDocument = documents[0];
    const currentSecurities = currentDocument.securities || [];
    
    // Create a map of securities by ISIN
    const securitiesMap = {};
    
    currentSecurities.forEach(security => {
      if (!security.isin) return;
      
      securitiesMap[security.isin] = {
        ...security,
        current: {
          value: security.value,
          quantity: security.quantity,
          price: security.price
        },
        historical: []
      };
    });
    
    // Add historical data from older documents
    documents.slice(1).forEach(doc => {
      const docSecurities = doc.securities || [];
      
      docSecurities.forEach(security => {
        if (!security.isin) return;
        
        if (securitiesMap[security.isin]) {
          // Add historical data for existing security
          securitiesMap[security.isin].historical.push({
            date: doc.processed_at,
            value: security.value,
            quantity: security.quantity,
            price: security.price
          });
        } else {
          // Add security that's not in the current document
          securitiesMap[security.isin] = {
            ...security,
            current: null,
            historical: [{
              date: doc.processed_at,
              value: security.value,
              quantity: security.quantity,
              price: security.price
            }]
          };
        }
      });
    });
    
    // Convert map to array
    return Object.values(securitiesMap);
  }

  /**
   * Calculate performance metrics from multiple documents
   * @param {Array} documents - Array of documents
   * @returns {Object} - Performance metrics
   * @private
   */
  _calculatePerformance(documents) {
    if (documents.length < 2) {
      return documents[0]?.performance || {};
    }
    
    // Get the most recent and oldest documents
    const newestDoc = documents[0];
    const oldestDoc = documents[documents.length - 1];
    
    // Calculate time difference in days
    const timeDiffMs = new Date(newestDoc.processed_at) - new Date(oldestDoc.processed_at);
    const timeDiffDays = timeDiffMs / (1000 * 60 * 60 * 24);
    
    // Calculate portfolio value change
    const startValue = oldestDoc.portfolio_value;
    const endValue = newestDoc.portfolio_value;
    const absoluteChange = endValue - startValue;
    const percentageChange = (absoluteChange / startValue) * 100;
    
    // Calculate annualized return
    const annualizedReturn = (Math.pow((endValue / startValue), (365 / timeDiffDays)) - 1) * 100;
    
    return {
      start_date: oldestDoc.processed_at,
      end_date: newestDoc.processed_at,
      time_period_days: timeDiffDays,
      start_value: startValue,
      end_value: endValue,
      absolute_change: absoluteChange,
      percentage_change: percentageChange,
      annualized_return: annualizedReturn
    };
  }

  /**
   * Create a summary of trades
   * @param {Array} trades - Array of trades
   * @returns {Object} - Trade summary
   * @private
   */
  _createTradeSummary(trades) {
    if (!trades || trades.length === 0) {
      return {
        buy_count: 0,
        sell_count: 0,
        total_buy_value: 0,
        total_sell_value: 0
      };
    }
    
    // Count buys and sells
    let buyCount = 0;
    let sellCount = 0;
    let totalBuyValue = 0;
    let totalSellValue = 0;
    
    trades.forEach(trade => {
      if (trade.type === 'buy') {
        buyCount++;
        totalBuyValue += trade.value || 0;
      } else if (trade.type === 'sell') {
        sellCount++;
        totalSellValue += trade.value || 0;
      }
    });
    
    return {
      buy_count: buyCount,
      sell_count: sellCount,
      total_buy_value: totalBuyValue,
      total_sell_value: totalSellValue,
      net_value: totalSellValue - totalBuyValue
    };
  }

  /**
   * Generate insights from portfolio documents using AI
   * @param {Array} documents - Array of portfolio documents
   * @returns {Promise<Object>} - Insights
   * @private
   */
  async _generateInsights(documents) {
    if (!this.apiKey) {
      return {
        summary: 'API key not configured. Unable to generate AI insights.',
        recommendations: []
      };
    }
    
    try {
      // Prepare document data for the prompt
      const documentContext = this._preparePortfolioContext(documents);
      
      // Create a prompt for the AI
      const prompt = this._createPortfolioInsightsPrompt(documentContext);
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial portfolio analysis assistant. You analyze financial portfolio data and provide insights and recommendations.' },
            { role: 'user', content: prompt }
          ],
          response_format: { type: 'json_object' }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Parse the response
      const aiResponse = response.data.choices[0].message.content;
      
      try {
        // Parse the JSON response
        return JSON.parse(aiResponse);
      } catch (error) {
        this.logger.error(`Error parsing AI response: ${error.message}`);
        return {
          summary: 'Error generating insights: Invalid response format',
          recommendations: []
        };
      }
    } catch (error) {
      this.logger.error(`Error generating insights: ${error.message}`);
      return {
        summary: 'Error generating insights: ' + error.message,
        recommendations: []
      };
    }
  }

  /**
   * Generate insights from trade documents using AI
   * @param {Array} trades - Array of trades
   * @returns {Promise<Object>} - Insights
   * @private
   */
  async _generateTradeInsights(trades) {
    if (!this.apiKey) {
      return {
        summary: 'API key not configured. Unable to generate AI insights.',
        recommendations: []
      };
    }
    
    try {
      // Prepare trade data for the prompt
      const tradeContext = this._prepareTradeContext(trades);
      
      // Create a prompt for the AI
      const prompt = this._createTradeInsightsPrompt(tradeContext);
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial trade analysis assistant. You analyze financial trade data and provide insights and recommendations.' },
            { role: 'user', content: prompt }
          ],
          response_format: { type: 'json_object' }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Parse the response
      const aiResponse = response.data.choices[0].message.content;
      
      try {
        // Parse the JSON response
        return JSON.parse(aiResponse);
      } catch (error) {
        this.logger.error(`Error parsing AI response: ${error.message}`);
        return {
          summary: 'Error generating insights: Invalid response format',
          recommendations: []
        };
      }
    } catch (error) {
      this.logger.error(`Error generating trade insights: ${error.message}`);
      return {
        summary: 'Error generating insights: ' + error.message,
        recommendations: []
      };
    }
  }

  /**
   * Generate insights from portfolio and trade documents using AI
   * @param {Array} portfolioDocuments - Array of portfolio documents
   * @param {Array} tradeDocuments - Array of trade documents
   * @returns {Promise<Object>} - Insights
   * @private
   */
  async _generateCombinedInsights(portfolioDocuments, tradeDocuments) {
    if (!this.apiKey) {
      return {
        summary: 'API key not configured. Unable to generate AI insights.',
        recommendations: []
      };
    }
    
    try {
      // Prepare document data for the prompt
      const portfolioContext = this._preparePortfolioContext(portfolioDocuments);
      const tradeContext = this._prepareTradeContext(
        tradeDocuments.flatMap(doc => doc.trades || [])
      );
      
      // Create a prompt for the AI
      const prompt = this._createCombinedInsightsPrompt(portfolioContext, tradeContext);
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial analysis assistant. You analyze financial portfolio and trade data to provide insights and recommendations.' },
            { role: 'user', content: prompt }
          ],
          response_format: { type: 'json_object' }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Parse the response
      const aiResponse = response.data.choices[0].message.content;
      
      try {
        // Parse the JSON response
        return JSON.parse(aiResponse);
      } catch (error) {
        this.logger.error(`Error parsing AI response: ${error.message}`);
        return {
          summary: 'Error generating insights: Invalid response format',
          recommendations: []
        };
      }
    } catch (error) {
      this.logger.error(`Error generating combined insights: ${error.message}`);
      return {
        summary: 'Error generating insights: ' + error.message,
        recommendations: []
      };
    }
  }

  /**
   * Generate insights from generic documents using AI
   * @param {Array} documents - Array of documents
   * @returns {Promise<Object>} - Insights
   * @private
   */
  async _generateGenericInsights(documents) {
    if (!this.apiKey) {
      return {
        summary: 'API key not configured. Unable to generate AI insights.',
        recommendations: []
      };
    }
    
    try {
      // Prepare document data for the prompt
      const documentContext = documents.map(doc => ({
        id: doc.id,
        filename: doc.filename,
        document_type: doc.document_type,
        processed_at: doc.processed_at
      }));
      
      // Create a prompt for the AI
      const prompt = `
I need you to analyze the following financial documents and provide insights.

DOCUMENT LIST:
${JSON.stringify(documentContext, null, 2)}

Please provide:
1. A summary of the documents
2. Any recommendations based on the document types and dates

Return your response as a JSON object with the following structure:
{
  "summary": "Your summary of the documents",
  "recommendations": [
    "First recommendation",
    "Second recommendation",
    ...
  ]
}
`;
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial document analysis assistant. You analyze financial documents and provide insights and recommendations.' },
            { role: 'user', content: prompt }
          ],
          response_format: { type: 'json_object' }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Parse the response
      const aiResponse = response.data.choices[0].message.content;
      
      try {
        // Parse the JSON response
        return JSON.parse(aiResponse);
      } catch (error) {
        this.logger.error(`Error parsing AI response: ${error.message}`);
        return {
          summary: 'Error generating insights: Invalid response format',
          recommendations: []
        };
      }
    } catch (error) {
      this.logger.error(`Error generating generic insights: ${error.message}`);
      return {
        summary: 'Error generating insights: ' + error.message,
        recommendations: []
      };
    }
  }

  /**
   * Prepare portfolio context for AI prompt
   * @param {Array} documents - Array of portfolio documents
   * @returns {string} - Portfolio context
   * @private
   */
  _preparePortfolioContext(documents) {
    let context = '';
    
    // Add information about each document
    documents.forEach((doc, index) => {
      context += `DOCUMENT ${index + 1}:\n`;
      context += `Date: ${doc.processed_at}\n`;
      context += `Portfolio Value: $${doc.portfolio_value?.toLocaleString() || 'N/A'}\n`;
      
      if (doc.asset_allocation) {
        context += 'Asset Allocation:\n';
        
        Object.entries(doc.asset_allocation).forEach(([assetClass, allocation]) => {
          context += `- ${assetClass}: ${(allocation * 100).toFixed(2)}%\n`;
        });
      }
      
      if (doc.securities && doc.securities.length > 0) {
        context += `Securities (${doc.securities.length}):\n`;
        
        // Sort securities by value (descending)
        const sortedSecurities = [...doc.securities].sort((a, b) => (b.value || 0) - (a.value || 0));
        
        // Show top 5 securities
        sortedSecurities.slice(0, 5).forEach(security => {
          context += `- ${security.name} (${security.isin}): `;
          
          if (security.value) {
            context += `$${security.value.toLocaleString()}`;
          }
          
          if (security.quantity) {
            context += `, ${security.quantity.toLocaleString()} shares`;
          }
          
          context += '\n';
        });
        
        if (sortedSecurities.length > 5) {
          context += `- ... and ${sortedSecurities.length - 5} more securities\n`;
        }
      }
      
      context += '\n';
    });
    
    return context;
  }

  /**
   * Prepare trade context for AI prompt
   * @param {Array} trades - Array of trades
   * @returns {string} - Trade context
   * @private
   */
  _prepareTradeContext(trades) {
    let context = '';
    
    // Count buys and sells
    const buyTrades = trades.filter(trade => trade.type === 'buy');
    const sellTrades = trades.filter(trade => trade.type === 'sell');
    
    context += `TRADES SUMMARY:\n`;
    context += `Total Trades: ${trades.length}\n`;
    context += `Buy Trades: ${buyTrades.length}\n`;
    context += `Sell Trades: ${sellTrades.length}\n\n`;
    
    // Add information about each trade
    context += `RECENT TRADES (up to 10):\n`;
    
    // Sort trades by date (newest first)
    const sortedTrades = [...trades].sort((a, b) => {
      return new Date(b.trade_date || b.document_date) - new Date(a.trade_date || a.document_date);
    });
    
    // Show up to 10 recent trades
    sortedTrades.slice(0, 10).forEach((trade, index) => {
      context += `TRADE ${index + 1}:\n`;
      context += `Date: ${trade.trade_date || trade.document_date}\n`;
      context += `Type: ${trade.type || 'N/A'}\n`;
      context += `Security: ${trade.security_name || 'N/A'} (${trade.isin || 'N/A'})\n`;
      
      if (trade.quantity) {
        context += `Quantity: ${trade.quantity.toLocaleString()}\n`;
      }
      
      if (trade.price) {
        context += `Price: $${trade.price.toLocaleString()}\n`;
      }
      
      if (trade.value) {
        context += `Value: $${trade.value.toLocaleString()}\n`;
      }
      
      context += '\n';
    });
    
    if (sortedTrades.length > 10) {
      context += `... and ${sortedTrades.length - 10} more trades\n\n`;
    }
    
    return context;
  }

  /**
   * Create a prompt for portfolio insights
   * @param {string} documentContext - Portfolio context
   * @returns {string} - Prompt
   * @private
   */
  _createPortfolioInsightsPrompt(documentContext) {
    return `
I need you to analyze the following portfolio documents and provide insights.

${documentContext}

Based on this information, please provide:
1. A summary of the portfolio's performance and changes over time
2. Key observations about asset allocation and securities
3. Recommendations for portfolio optimization

Return your response as a JSON object with the following structure:
{
  "summary": "Your summary of the portfolio's performance and changes",
  "key_observations": [
    "First observation",
    "Second observation",
    ...
  ],
  "recommendations": [
    "First recommendation",
    "Second recommendation",
    ...
  ]
}
`;
  }

  /**
   * Create a prompt for trade insights
   * @param {string} tradeContext - Trade context
   * @returns {string} - Prompt
   * @private
   */
  _createTradeInsightsPrompt(tradeContext) {
    return `
I need you to analyze the following trade data and provide insights.

${tradeContext}

Based on this information, please provide:
1. A summary of the trading activity
2. Key observations about trading patterns
3. Recommendations for future trading decisions

Return your response as a JSON object with the following structure:
{
  "summary": "Your summary of the trading activity",
  "key_observations": [
    "First observation",
    "Second observation",
    ...
  ],
  "recommendations": [
    "First recommendation",
    "Second recommendation",
    ...
  ]
}
`;
  }

  /**
   * Create a prompt for combined portfolio and trade insights
   * @param {string} portfolioContext - Portfolio context
   * @param {string} tradeContext - Trade context
   * @returns {string} - Prompt
   * @private
   */
  _createCombinedInsightsPrompt(portfolioContext, tradeContext) {
    return `
I need you to analyze the following portfolio and trade data and provide insights.

PORTFOLIO DATA:
${portfolioContext}

TRADE DATA:
${tradeContext}

Based on this information, please provide:
1. A summary of the portfolio's performance and trading activity
2. Key observations about the relationship between portfolio changes and trades
3. Recommendations for portfolio management and future trading decisions

Return your response as a JSON object with the following structure:
{
  "summary": "Your summary of the portfolio and trading activity",
  "key_observations": [
    "First observation",
    "Second observation",
    ...
  ],
  "recommendations": [
    "First recommendation",
    "Second recommendation",
    ...
  ]
}
`;
  }
}

module.exports = DocumentIntegrationAgent;
