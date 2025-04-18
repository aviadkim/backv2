/**
 * Document Integration API
 * 
 * Handles integrating multiple financial documents.
 */

const express = require('express');
const router = express.Router();
const logger = require('../../../utils/logger');
const { DocumentIntegrationAgent } = require('../../../services/agents');

/**
 * @route POST /api/financial/integrate-documents
 * @desc Integrate multiple financial documents
 * @access Public
 */
router.post('/', async (req, res) => {
  try {
    const { document_ids, options } = req.body;
    
    if (!document_ids || !Array.isArray(document_ids) || document_ids.length === 0) {
      return res.status(400).json({ error: 'Document IDs array is required' });
    }
    
    logger.info(`Integrating ${document_ids.length} documents`);
    
    // In a real implementation, we would fetch the documents from the database
    // and use the DocumentIntegrationAgent to integrate them
    
    // For now, we'll return mock integration results
    const integrationResults = await generateMockIntegrationResults(document_ids, options);
    
    return res.status(200).json(integrationResults);
  } catch (error) {
    logger.error(`Error integrating documents: ${error.message}`, error);
    return res.status(500).json({ error: 'Error integrating documents', detail: error.message });
  }
});

/**
 * Generate mock integration results
 * @param {Array} document_ids - Array of document IDs
 * @param {Object} options - Integration options
 * @returns {Promise<Object>} - Integration results
 */
async function generateMockIntegrationResults(document_ids, options) {
  // Mock document data
  const mockDocuments = document_ids.map((id, index) => {
    const isPortfolio = index % 2 === 0; // Alternate between portfolio and trade documents
    
    if (isPortfolio) {
      return {
        id,
        filename: `portfolio-statement-${2023 - Math.floor(index / 2)}-q${(index % 4) + 1}.pdf`,
        document_type: 'portfolio',
        processed_at: new Date(Date.now() - index * 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days apart
        portfolio_value: 1950000 - (index * 50000), // Decreasing value over time
        asset_allocation: {
          'Equities': 0.40 - (index * 0.01),
          'Fixed Income': 0.35 + (index * 0.01),
          'Cash': 0.05,
          'Alternative Investments': 0.20
        },
        securities: [
          { isin: 'US5949181045', name: 'Microsoft Corp.', value: 180000 - (index * 5000), quantity: 600 - (index * 10), price: 300 - (index * 5) },
          { isin: 'US88160R1014', name: 'Tesla Inc.', value: 105000 - (index * 3000), quantity: 500 - (index * 5), price: 210 - (index * 3) },
          { isin: 'US0378331005', name: 'Apple Inc.', value: 95000 - (index * 2000), quantity: 500, price: 190 - (index * 4) },
          { isin: 'US0231351067', name: 'Amazon.com Inc.', value: 90000 - (index * 1000), quantity: 300, price: 300 - (index * 3) },
          { isin: 'US30303M1027', name: 'Meta Platforms Inc.', value: 75000 - (index * 1000), quantity: 250, price: 300 - (index * 4) }
        ]
      };
    } else {
      return {
        id,
        filename: `trade-confirmation-${2023 - Math.floor(index / 2)}-${(index % 12) + 1}.pdf`,
        document_type: 'trade',
        processed_at: new Date(Date.now() - index * 15 * 24 * 60 * 60 * 1000).toISOString(), // 15 days apart
        trades: [
          {
            trade_date: new Date(Date.now() - index * 15 * 24 * 60 * 60 * 1000).toISOString(),
            type: index % 3 === 0 ? 'buy' : 'sell',
            security_name: 'Microsoft Corp.',
            isin: 'US5949181045',
            quantity: 10,
            price: 300 - (index * 5),
            value: (300 - (index * 5)) * 10
          }
        ]
      };
    }
  });
  
  // Create a DocumentIntegrationAgent instance
  const integrationAgent = new DocumentIntegrationAgent();
  
  // Integrate the documents
  try {
    const integratedData = await integrationAgent.integrateDocuments(mockDocuments, options);
    return integratedData;
  } catch (error) {
    logger.error(`Error in integration agent: ${error.message}`, error);
    
    // Return a simplified mock result
    return {
      integrated_at: new Date().toISOString(),
      document_count: document_ids.length,
      document_types: ['portfolio', 'trade'],
      integration_strategy: 'portfolio_trade',
      portfolio: {
        current: {
          date: mockDocuments[0].processed_at,
          portfolio_value: mockDocuments[0].portfolio_value,
          asset_allocation: mockDocuments[0].asset_allocation
        },
        historical: mockDocuments
          .filter(doc => doc.document_type === 'portfolio' && doc !== mockDocuments[0])
          .map(doc => ({
            date: doc.processed_at,
            portfolio_value: doc.portfolio_value,
            asset_allocation: doc.asset_allocation
          }))
      },
      insights: {
        summary: "This is a mock integration result. The portfolio shows a general upward trend in value over time, with an increasing allocation to equities and a decreasing allocation to fixed income.",
        key_observations: [
          "Portfolio value increased by approximately 5% over the observed period",
          "Equity allocation increased from 35% to 40%",
          "Fixed income allocation decreased from 40% to 35%"
        ],
        recommendations: [
          "Consider rebalancing the portfolio to maintain target asset allocation",
          "Review the performance of individual securities to identify opportunities for optimization",
          "Consider increasing cash reserves for potential market volatility"
        ]
      }
    };
  }
}

module.exports = router;
