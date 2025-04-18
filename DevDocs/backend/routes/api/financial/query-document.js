/**
 * Query Document API
 * 
 * Handles querying financial documents using natural language.
 */

const express = require('express');
const router = express.Router();
const logger = require('../../../utils/logger');
const { QueryEngineAgent } = require('../../../services/agents');

/**
 * @route POST /api/financial/query-document
 * @desc Query a financial document using natural language
 * @access Public
 */
router.post('/', async (req, res) => {
  try {
    const { document_id, query, options } = req.body;
    
    if (!document_id) {
      return res.status(400).json({ error: 'Document ID is required' });
    }
    
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }
    
    logger.info(`Querying document ${document_id}: ${query}`);
    
    // In a real implementation, we would fetch the document from the database
    // and use the QueryEngineAgent to process the query
    
    // For now, we'll return mock query results
    const queryResults = await generateMockQueryResults(document_id, query, options);
    
    return res.status(200).json(queryResults);
  } catch (error) {
    logger.error(`Error querying document: ${error.message}`, error);
    return res.status(500).json({ error: 'Error querying document', detail: error.message });
  }
});

/**
 * Generate mock query results
 * @param {string} document_id - Document ID
 * @param {string} query - Natural language query
 * @param {Object} options - Query options
 * @returns {Promise<Object>} - Query results
 */
async function generateMockQueryResults(document_id, query, options) {
  // Mock document data
  const documentData = {
    id: document_id,
    filename: 'portfolio-statement-2023-q2.pdf',
    processed_at: '2023-04-15T00:00:00Z',
    document_type: 'portfolio',
    portfolio_value: 1950000,
    asset_allocation: {
      'Equities': 0.40,
      'Fixed Income': 0.35,
      'Cash': 0.05,
      'Alternative Investments': 0.20
    },
    securities: [
      { isin: 'US5949181045', name: 'Microsoft Corp.', value: 180000, quantity: 600, price: 300 },
      { isin: 'US88160R1014', name: 'Tesla Inc.', value: 105000, quantity: 500, price: 210 },
      { isin: 'US0378331005', name: 'Apple Inc.', value: 95000, quantity: 500, price: 190 },
      { isin: 'US0231351067', name: 'Amazon.com Inc.', value: 90000, quantity: 300, price: 300 },
      { isin: 'US30303M1027', name: 'Meta Platforms Inc.', value: 75000, quantity: 250, price: 300 }
    ],
    performance: {
      'ytd': 0.08,
      'one_year': 0.15,
      'three_year': 0.35,
      'five_year': 0.60
    }
  };
  
  // Generate response based on query keywords
  let response = '';
  let data = null;
  let confidence = 0.95;

  const lowerQuery = query.toLowerCase();

  if (lowerQuery.includes('portfolio value') || lowerQuery.includes('total value')) {
    response = `The total portfolio value is $${documentData.portfolio_value.toLocaleString()}.`;
    data = {
      portfolio_value: documentData.portfolio_value
    };
  } else if (lowerQuery.includes('asset allocation') || lowerQuery.includes('allocation')) {
    response = `The portfolio has the following asset allocation:\n\n` +
      `- Equities: 40%\n` +
      `- Fixed Income: 35%\n` +
      `- Cash: 5%\n` +
      `- Alternative Investments: 20%\n\n` +
      `The portfolio has a moderate allocation with a slight tilt towards equities, which is appropriate for growth objectives while maintaining some stability with fixed income.`;
    
    data = {
      asset_allocation: documentData.asset_allocation
    };
  } else if (lowerQuery.includes('top') && (lowerQuery.includes('holdings') || lowerQuery.includes('positions'))) {
    // Extract number from query (e.g., "top 3 holdings")
    const numMatch = lowerQuery.match(/top\s+(\d+)/);
    const numHoldings = numMatch ? parseInt(numMatch[1]) : 5;
    const topHoldings = documentData.securities.slice(0, numHoldings);
    
    response = `The top ${numHoldings} holdings in the portfolio are:\n\n`;
    
    topHoldings.forEach((holding, index) => {
      const percentage = (holding.value / documentData.portfolio_value * 100).toFixed(2);
      response += `${index + 1}. ${holding.name} (${holding.isin}): $${holding.value.toLocaleString()} (${percentage}% of portfolio)\n`;
    });
    
    data = {
      top_holdings: topHoldings
    };
  } else if (lowerQuery.includes('performance')) {
    response = `The portfolio has the following performance metrics:\n\n` +
      `- Year-to-date: 8.00%\n` +
      `- One-year: 15.00%\n` +
      `- Three-year: 35.00%\n` +
      `- Five-year: 60.00%\n\n` +
      `The portfolio has shown strong performance across all time periods, with particularly strong returns over the longer time horizons.`;
    
    data = {
      performance: documentData.performance
    };
  } else if (lowerQuery.includes('largest') || lowerQuery.includes('biggest')) {
    const largestHolding = documentData.securities[0];
    const percentage = (largestHolding.value / documentData.portfolio_value * 100).toFixed(2);
    
    response = `The largest holding in the portfolio is ${largestHolding.name} (${largestHolding.isin}) with a value of $${largestHolding.value.toLocaleString()}, representing ${percentage}% of the total portfolio value.`;
    
    data = {
      largest_holding: largestHolding
    };
  } else if (lowerQuery.includes('cash')) {
    const cashAllocation = documentData.asset_allocation['Cash'];
    const cashValue = documentData.portfolio_value * cashAllocation;
    
    response = `The portfolio has a cash allocation of ${(cashAllocation * 100).toFixed(2)}%, which amounts to $${cashValue.toLocaleString()}.`;
    
    data = {
      cash_allocation: cashAllocation,
      cash_value: cashValue
    };
  } else if (lowerQuery.includes('equities') || lowerQuery.includes('stocks')) {
    const equitiesAllocation = documentData.asset_allocation['Equities'];
    const equitiesValue = documentData.portfolio_value * equitiesAllocation;
    
    response = `The portfolio has an equities allocation of ${(equitiesAllocation * 100).toFixed(2)}%, which amounts to $${equitiesValue.toLocaleString()}. This includes positions in technology companies like Microsoft, Apple, Amazon, and Meta, as well as Tesla in the automotive sector.`;
    
    data = {
      equities_allocation: equitiesAllocation,
      equities_value: equitiesValue,
      equity_holdings: documentData.securities
    };
  } else {
    response = `I don't have specific information about "${query}" in the document data. The document contains information about portfolio value ($${documentData.portfolio_value.toLocaleString()}), asset allocation, top holdings, and performance metrics. Please try asking about one of these topics.`;
    confidence = 0.5;
  }
  
  return {
    query,
    response,
    data,
    confidence
  };
}

module.exports = router;
