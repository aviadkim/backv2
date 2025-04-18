/**
 * Document Comparison API
 * 
 * Handles comparing financial documents.
 */

const express = require('express');
const router = express.Router();
const logger = require('../../../utils/logger');
const { DocumentComparisonAgent } = require('../../../services/agents');

/**
 * @route POST /api/financial/compare-documents
 * @desc Compare two financial documents
 * @access Public
 */
router.post('/', async (req, res) => {
  try {
    const { document1_id, document2_id, options } = req.body;
    
    if (!document1_id || !document2_id) {
      return res.status(400).json({ error: 'Both document IDs are required' });
    }
    
    logger.info(`Comparing documents: ${document1_id} and ${document2_id}`);
    
    // In a real implementation, we would fetch the documents from the database
    // and use the DocumentComparisonAgent to compare them
    
    // For now, we'll return mock comparison results
    const comparisonResults = generateMockComparisonResults(document1_id, document2_id, options);
    
    return res.status(200).json(comparisonResults);
  } catch (error) {
    logger.error(`Error comparing documents: ${error.message}`, error);
    return res.status(500).json({ error: 'Error comparing documents', detail: error.message });
  }
});

/**
 * Generate mock comparison results
 * @param {string} document1_id - First document ID
 * @param {string} document2_id - Second document ID
 * @param {Object} options - Comparison options
 * @returns {Object} - Comparison results
 */
function generateMockComparisonResults(document1_id, document2_id, options) {
  // Mock document data
  const document1 = {
    id: document1_id,
    date: '2023-01-15T00:00:00Z',
    portfolio_value: 1850000,
    asset_allocation: {
      'Equities': 0.35,
      'Fixed Income': 0.40,
      'Cash': 0.10,
      'Alternative Investments': 0.15
    },
    securities: [
      { isin: 'US0378331005', name: 'Apple Inc.', value: 85000, quantity: 500, price: 170 },
      { isin: 'US88160R1014', name: 'Tesla Inc.', value: 120000, quantity: 600, price: 200 },
      { isin: 'US5949181045', name: 'Microsoft Corp.', value: 150000, quantity: 500, price: 300 },
      { isin: 'US67066G1040', name: 'NVIDIA Corp.', value: 80000, quantity: 200, price: 400 }
    ]
  };
  
  const document2 = {
    id: document2_id,
    date: '2023-04-15T00:00:00Z',
    portfolio_value: 1950000,
    asset_allocation: {
      'Equities': 0.40,
      'Fixed Income': 0.35,
      'Cash': 0.05,
      'Alternative Investments': 0.20
    },
    securities: [
      { isin: 'US0378331005', name: 'Apple Inc.', value: 95000, quantity: 500, price: 190 },
      { isin: 'US88160R1014', name: 'Tesla Inc.', value: 105000, quantity: 500, price: 210 },
      { isin: 'US5949181045', name: 'Microsoft Corp.', value: 180000, quantity: 600, price: 300 },
      { isin: 'US0231351067', name: 'Amazon.com Inc.', value: 90000, quantity: 300, price: 300 },
      { isin: 'US30303M1027', name: 'Meta Platforms Inc.', value: 75000, quantity: 250, price: 300 }
    ]
  };
  
  // Calculate basic comparison
  const timeDiff = new Date(document2.date) - new Date(document1.date);
  const daysDiff = Math.abs(Math.round(timeDiff / (1000 * 60 * 60 * 24)));
  
  const basicComparison = {
    document_types_match: true,
    time_difference: {
      milliseconds: timeDiff,
      days: daysDiff
    },
    chronological_order: timeDiff > 0 ? 'doc1_older' : 'doc2_older'
  };
  
  // Calculate portfolio comparison
  const portfolioComparison = {
    has_both_values: true,
    doc1_value: document1.portfolio_value,
    doc2_value: document2.portfolio_value,
    absolute_difference: document2.portfolio_value - document1.portfolio_value,
    percentage_difference: ((document2.portfolio_value - document1.portfolio_value) / document1.portfolio_value) * 100,
    direction: document2.portfolio_value > document1.portfolio_value ? 'increase' : 'decrease'
  };
  
  // Calculate asset allocation comparison
  const allAssetClasses = new Set([
    ...Object.keys(document1.asset_allocation),
    ...Object.keys(document2.asset_allocation)
  ]);
  
  const allocationChanges = [];
  const allocationAdditions = [];
  const allocationRemovals = [];
  
  for (const assetClass of allAssetClasses) {
    const doc1Value = document1.asset_allocation[assetClass] || 0;
    const doc2Value = document2.asset_allocation[assetClass] || 0;
    
    if (doc1Value === 0 && doc2Value > 0) {
      allocationAdditions.push({
        asset_class: assetClass,
        value: doc2Value
      });
    } else if (doc1Value > 0 && doc2Value === 0) {
      allocationRemovals.push({
        asset_class: assetClass,
        value: doc1Value
      });
    } else if (doc1Value !== doc2Value) {
      const absoluteDiff = doc2Value - doc1Value;
      const percentageDiff = (absoluteDiff / doc1Value) * 100;
      
      allocationChanges.push({
        asset_class: assetClass,
        doc1_value: doc1Value,
        doc2_value: doc2Value,
        absolute_difference: absoluteDiff,
        percentage_difference: percentageDiff,
        direction: absoluteDiff > 0 ? 'increase' : 'decrease'
      });
    }
  }
  
  const allocationComparison = {
    changes: allocationChanges,
    additions: allocationAdditions,
    removals: allocationRemovals,
    has_changes: allocationChanges.length > 0 || allocationAdditions.length > 0 || allocationRemovals.length > 0
  };
  
  // Calculate securities comparison
  const doc1Securities = new Map();
  const doc2Securities = new Map();
  
  document1.securities.forEach(security => {
    doc1Securities.set(security.isin, security);
  });
  
  document2.securities.forEach(security => {
    doc2Securities.set(security.isin, security);
  });
  
  const commonIsins = new Set();
  const addedIsins = new Set();
  const removedIsins = new Set();
  
  // Check for added securities
  for (const isin of doc2Securities.keys()) {
    if (doc1Securities.has(isin)) {
      commonIsins.add(isin);
    } else {
      addedIsins.add(isin);
    }
  }
  
  // Check for removed securities
  for (const isin of doc1Securities.keys()) {
    if (!doc2Securities.has(isin)) {
      removedIsins.add(isin);
    }
  }
  
  // Compare common securities
  const securitiesChanges = [];
  
  for (const isin of commonIsins) {
    const security1 = doc1Securities.get(isin);
    const security2 = doc2Securities.get(isin);
    
    const valueChange = security2.value - security1.value;
    const valuePercentageChange = (valueChange / security1.value) * 100;
    
    const quantityChange = (security2.quantity || 0) - (security1.quantity || 0);
    const quantityPercentageChange = security1.quantity ? (quantityChange / security1.quantity) * 100 : 0;
    
    const priceChange = (security2.price || 0) - (security1.price || 0);
    const pricePercentageChange = security1.price ? (priceChange / security1.price) * 100 : 0;
    
    // Only add to changes if there's a significant change
    if (Math.abs(valuePercentageChange) > 0.1 || 
        Math.abs(quantityPercentageChange) > 0.1 || 
        Math.abs(pricePercentageChange) > 0.1) {
      
      securitiesChanges.push({
        isin,
        name: security2.name || security1.name,
        value: {
          doc1: security1.value,
          doc2: security2.value,
          absolute_change: valueChange,
          percentage_change: valuePercentageChange,
          direction: valueChange > 0 ? 'increase' : (valueChange < 0 ? 'decrease' : 'no_change')
        },
        quantity: {
          doc1: security1.quantity,
          doc2: security2.quantity,
          absolute_change: quantityChange,
          percentage_change: quantityPercentageChange,
          direction: quantityChange > 0 ? 'increase' : (quantityChange < 0 ? 'decrease' : 'no_change')
        },
        price: {
          doc1: security1.price,
          doc2: security2.price,
          absolute_change: priceChange,
          percentage_change: pricePercentageChange,
          direction: priceChange > 0 ? 'increase' : (priceChange < 0 ? 'decrease' : 'no_change')
        }
      });
    }
  }
  
  // Create lists of added and removed securities
  const securitiesAdditions = Array.from(addedIsins).map(isin => {
    const security = doc2Securities.get(isin);
    return {
      isin,
      name: security.name,
      value: security.value,
      quantity: security.quantity,
      price: security.price
    };
  });
  
  const securitiesRemovals = Array.from(removedIsins).map(isin => {
    const security = doc1Securities.get(isin);
    return {
      isin,
      name: security.name,
      value: security.value,
      quantity: security.quantity,
      price: security.price
    };
  });
  
  // Sort changes by absolute value change (largest first)
  securitiesChanges.sort((a, b) => Math.abs(b.value.absolute_change) - Math.abs(a.value.absolute_change));
  
  // Sort additions and removals by value
  securitiesAdditions.sort((a, b) => b.value - a.value);
  securitiesRemovals.sort((a, b) => b.value - a.value);
  
  const securitiesComparison = {
    changes: securitiesChanges,
    additions: securitiesAdditions,
    removals: securitiesRemovals,
    total_securities: {
      doc1: document1.securities.length,
      doc2: document2.securities.length,
      difference: document2.securities.length - document1.securities.length
    },
    has_changes: securitiesChanges.length > 0 || securitiesAdditions.length > 0 || securitiesRemovals.length > 0
  };
  
  // Mock performance comparison
  const performanceComparison = {
    changes: [
      {
        period: 'ytd',
        doc1_value: 0.05,
        doc2_value: 0.08,
        absolute_difference: 0.03,
        percentage_difference: 60,
        direction: 'improved'
      },
      {
        period: 'one_year',
        doc1_value: 0.12,
        doc2_value: 0.15,
        absolute_difference: 0.03,
        percentage_difference: 25,
        direction: 'improved'
      }
    ],
    has_changes: true
  };
  
  // Generate summary
  const summary = {
    summary: "The portfolio has shown positive growth over the 90-day period between January 15, 2023, and April 15, 2023, with the total value increasing by 5.41% ($100,000) from $1,850,000 to $1,950,000. This growth is primarily driven by increased allocation to equities (from 35% to 40%) and the addition of alternative investments (5%), while reducing exposure to fixed income (from 40% to 35%) and cash (from 10% to 5%).\n\nSignificant changes in individual securities include increased positions in Microsoft Corp. (20% increase in value) and Apple Inc. (11.76% increase in value), while reducing exposure to Tesla Inc. (12.5% decrease in value). The portfolio also added new positions in Amazon.com Inc. and Meta Platforms Inc., while completely divesting from NVIDIA Corp. Overall, the number of securities increased from 15 to 16.\n\nPerformance metrics have improved across the board, with year-to-date returns increasing from 5% to 8% and one-year returns improving from 12% to 15%, indicating stronger overall performance in the more recent period.",
    highlights: [
      "Portfolio value increased by 5.41% ($100,000) over a 90-day period",
      "Shifted allocation from fixed income and cash toward equities and alternative investments",
      "Added new positions in Amazon and Meta while divesting from NVIDIA",
      "Increased holdings in Microsoft by 20% in value",
      "Performance metrics improved with YTD returns up from 5% to 8%"
    ]
  };
  
  // Return comparison results
  return {
    document1: {
      id: document1_id,
      date: document1.date,
      portfolio_value: document1.portfolio_value
    },
    document2: {
      id: document2_id,
      date: document2.date,
      portfolio_value: document2.portfolio_value
    },
    basic_comparison: basicComparison,
    portfolio_comparison: portfolioComparison,
    allocation_comparison: allocationComparison,
    securities_comparison: securitiesComparison,
    performance_comparison: performanceComparison,
    summary
  };
}

module.exports = router;
