/**
 * Document Comparison Agent
 * 
 * Compares two financial documents to identify differences and changes:
 * - Portfolio value changes
 * - Asset allocation changes
 * - Security additions/removals
 * - Security value changes
 * - Performance changes
 */

const axios = require('axios');
const logger = require('../../utils/logger');

class DocumentComparisonAgent {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.OPENROUTER_API_KEY;
    this.model = options.model || 'anthropic/claude-3-opus:beta';
    this.apiUrl = options.apiUrl || 'https://openrouter.ai/api/v1/chat/completions';
    this.logger = logger;
  }

  /**
   * Compare two documents
   * @param {Object} document1 - First document data
   * @param {Object} document2 - Second document data
   * @param {Object} options - Comparison options
   * @returns {Promise<Object>} - Comparison results
   */
  async compareDocuments(document1, document2, options = {}) {
    this.logger.info('Comparing documents');
    
    try {
      // Extract relevant data from documents
      const doc1Data = this._extractDocumentData(document1);
      const doc2Data = this._extractDocumentData(document2);
      
      // Compare basic document information
      const basicComparison = this._compareBasicInfo(doc1Data, doc2Data);
      
      // Compare portfolio values
      const portfolioComparison = this._comparePortfolioValues(doc1Data, doc2Data);
      
      // Compare asset allocations
      const allocationComparison = this._compareAssetAllocations(doc1Data, doc2Data);
      
      // Compare securities
      const securitiesComparison = this._compareSecurities(doc1Data, doc2Data);
      
      // Compare performance metrics
      const performanceComparison = this._comparePerformance(doc1Data, doc2Data);
      
      // Generate summary using AI
      const summary = await this._generateComparisonSummary(
        doc1Data, 
        doc2Data, 
        {
          basicComparison,
          portfolioComparison,
          allocationComparison,
          securitiesComparison,
          performanceComparison
        }
      );
      
      // Return comparison results
      return {
        document1: {
          id: document1.id,
          date: document1.processed_at,
          portfolio_value: doc1Data.portfolio_value
        },
        document2: {
          id: document2.id,
          date: document2.processed_at,
          portfolio_value: doc2Data.portfolio_value
        },
        basic_comparison: basicComparison,
        portfolio_comparison: portfolioComparison,
        allocation_comparison: allocationComparison,
        securities_comparison: securitiesComparison,
        performance_comparison: performanceComparison,
        summary
      };
    } catch (error) {
      this.logger.error(`Error comparing documents: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Extract relevant data from a document
   * @param {Object} document - Document data
   * @returns {Object} - Extracted data
   * @private
   */
  _extractDocumentData(document) {
    return {
      id: document.id,
      document_type: document.document_type,
      processed_at: document.processed_at,
      portfolio_value: document.portfolio?.portfolio_value,
      asset_allocation: document.portfolio?.asset_allocation || {},
      securities: document.securities || [],
      performance: document.portfolio?.performance || {}
    };
  }

  /**
   * Compare basic document information
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @returns {Object} - Basic comparison results
   * @private
   */
  _compareBasicInfo(doc1, doc2) {
    const timeDiff = new Date(doc2.processed_at) - new Date(doc1.processed_at);
    const daysDiff = Math.abs(Math.round(timeDiff / (1000 * 60 * 60 * 24)));
    
    return {
      document_types_match: doc1.document_type === doc2.document_type,
      time_difference: {
        milliseconds: timeDiff,
        days: daysDiff
      },
      chronological_order: timeDiff > 0 ? 'doc1_older' : 'doc2_older'
    };
  }

  /**
   * Compare portfolio values
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @returns {Object} - Portfolio comparison results
   * @private
   */
  _comparePortfolioValues(doc1, doc2) {
    if (!doc1.portfolio_value || !doc2.portfolio_value) {
      return {
        has_both_values: false,
        message: 'One or both documents are missing portfolio values'
      };
    }
    
    const absoluteDiff = doc2.portfolio_value - doc1.portfolio_value;
    const percentageDiff = (absoluteDiff / doc1.portfolio_value) * 100;
    
    return {
      has_both_values: true,
      doc1_value: doc1.portfolio_value,
      doc2_value: doc2.portfolio_value,
      absolute_difference: absoluteDiff,
      percentage_difference: percentageDiff,
      direction: absoluteDiff > 0 ? 'increase' : (absoluteDiff < 0 ? 'decrease' : 'no_change')
    };
  }

  /**
   * Compare asset allocations
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @returns {Object} - Asset allocation comparison results
   * @private
   */
  _compareAssetAllocations(doc1, doc2) {
    const allAssetClasses = new Set([
      ...Object.keys(doc1.asset_allocation),
      ...Object.keys(doc2.asset_allocation)
    ]);
    
    const changes = [];
    const additions = [];
    const removals = [];
    
    for (const assetClass of allAssetClasses) {
      const doc1Value = doc1.asset_allocation[assetClass] || 0;
      const doc2Value = doc2.asset_allocation[assetClass] || 0;
      
      if (doc1Value === 0 && doc2Value > 0) {
        additions.push({
          asset_class: assetClass,
          value: doc2Value
        });
      } else if (doc1Value > 0 && doc2Value === 0) {
        removals.push({
          asset_class: assetClass,
          value: doc1Value
        });
      } else if (doc1Value !== doc2Value) {
        const absoluteDiff = doc2Value - doc1Value;
        const percentageDiff = doc1Value ? (absoluteDiff / doc1Value) * 100 : 100;
        
        changes.push({
          asset_class: assetClass,
          doc1_value: doc1Value,
          doc2_value: doc2Value,
          absolute_difference: absoluteDiff,
          percentage_difference: percentageDiff,
          direction: absoluteDiff > 0 ? 'increase' : 'decrease'
        });
      }
    }
    
    return {
      changes,
      additions,
      removals,
      has_changes: changes.length > 0 || additions.length > 0 || removals.length > 0
    };
  }

  /**
   * Compare securities
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @returns {Object} - Securities comparison results
   * @private
   */
  _compareSecurities(doc1, doc2) {
    // Create maps of securities by ISIN
    const doc1Securities = new Map();
    const doc2Securities = new Map();
    
    doc1.securities.forEach(security => {
      doc1Securities.set(security.isin, security);
    });
    
    doc2.securities.forEach(security => {
      doc2Securities.set(security.isin, security);
    });
    
    // Find common, added, and removed securities
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
    const changes = [];
    
    for (const isin of commonIsins) {
      const security1 = doc1Securities.get(isin);
      const security2 = doc2Securities.get(isin);
      
      const valueChange = security2.value - security1.value;
      const valuePercentageChange = security1.value ? (valueChange / security1.value) * 100 : 0;
      
      const quantityChange = (security2.quantity || 0) - (security1.quantity || 0);
      const quantityPercentageChange = security1.quantity ? (quantityChange / security1.quantity) * 100 : 0;
      
      const priceChange = (security2.price || 0) - (security1.price || 0);
      const pricePercentageChange = security1.price ? (priceChange / security1.price) * 100 : 0;
      
      // Only add to changes if there's a significant change
      if (Math.abs(valuePercentageChange) > 0.1 || 
          Math.abs(quantityPercentageChange) > 0.1 || 
          Math.abs(pricePercentageChange) > 0.1) {
        
        changes.push({
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
    const additions = Array.from(addedIsins).map(isin => {
      const security = doc2Securities.get(isin);
      return {
        isin,
        name: security.name,
        value: security.value,
        quantity: security.quantity,
        price: security.price
      };
    });
    
    const removals = Array.from(removedIsins).map(isin => {
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
    changes.sort((a, b) => Math.abs(b.value.absolute_change) - Math.abs(a.value.absolute_change));
    
    // Sort additions and removals by value
    additions.sort((a, b) => b.value - a.value);
    removals.sort((a, b) => b.value - a.value);
    
    return {
      changes,
      additions,
      removals,
      total_securities: {
        doc1: doc1.securities.length,
        doc2: doc2.securities.length,
        difference: doc2.securities.length - doc1.securities.length
      },
      has_changes: changes.length > 0 || additions.length > 0 || removals.length > 0
    };
  }

  /**
   * Compare performance metrics
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @returns {Object} - Performance comparison results
   * @private
   */
  _comparePerformance(doc1, doc2) {
    const allPeriods = new Set([
      ...Object.keys(doc1.performance),
      ...Object.keys(doc2.performance)
    ]);
    
    const changes = [];
    
    for (const period of allPeriods) {
      const doc1Value = doc1.performance[period];
      const doc2Value = doc2.performance[period];
      
      // Skip if both are null or undefined
      if (doc1Value == null && doc2Value == null) {
        continue;
      }
      
      // Calculate changes if both values exist
      if (doc1Value != null && doc2Value != null) {
        const absoluteDiff = doc2Value - doc1Value;
        const percentageDiff = Math.abs(doc1Value) > 0.0001 ? (absoluteDiff / Math.abs(doc1Value)) * 100 : 0;
        
        changes.push({
          period,
          doc1_value: doc1Value,
          doc2_value: doc2Value,
          absolute_difference: absoluteDiff,
          percentage_difference: percentageDiff,
          direction: absoluteDiff > 0 ? 'improved' : (absoluteDiff < 0 ? 'worsened' : 'no_change')
        });
      } else {
        // One value exists and the other doesn't
        changes.push({
          period,
          doc1_value: doc1Value,
          doc2_value: doc2Value,
          status: doc1Value == null ? 'added_in_doc2' : 'removed_in_doc2'
        });
      }
    }
    
    return {
      changes,
      has_changes: changes.length > 0
    };
  }

  /**
   * Generate a summary of the comparison using AI
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @param {Object} comparisons - Comparison results
   * @returns {Promise<Object>} - Summary
   * @private
   */
  async _generateComparisonSummary(doc1, doc2, comparisons) {
    if (!this.apiKey) {
      return {
        summary: 'API key not configured. Unable to generate AI summary.',
        highlights: []
      };
    }
    
    try {
      // Create a prompt for the AI
      const prompt = this._createSummaryPrompt(doc1, doc2, comparisons);
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial document comparison AI assistant. You analyze differences between financial documents and provide clear, concise summaries.' },
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
          summary: 'Error generating summary: Invalid response format',
          highlights: []
        };
      }
    } catch (error) {
      this.logger.error(`Error generating comparison summary: ${error.message}`);
      return {
        summary: 'Error generating summary: ' + error.message,
        highlights: []
      };
    }
  }

  /**
   * Create a prompt for the AI to generate a summary
   * @param {Object} doc1 - First document data
   * @param {Object} doc2 - Second document data
   * @param {Object} comparisons - Comparison results
   * @returns {string} - Prompt
   * @private
   */
  _createSummaryPrompt(doc1, doc2, comparisons) {
    const { basicComparison, portfolioComparison, allocationComparison, securitiesComparison, performanceComparison } = comparisons;
    
    return `
I need you to analyze the differences between two financial documents and provide a summary.

Document 1 Date: ${doc1.processed_at}
Document 2 Date: ${doc2.processed_at}
Time Difference: ${basicComparison.time_difference.days} days

Portfolio Value:
- Document 1: ${portfolioComparison.doc1_value?.toLocaleString() || 'N/A'}
- Document 2: ${portfolioComparison.doc2_value?.toLocaleString() || 'N/A'}
- Change: ${portfolioComparison.absolute_difference?.toLocaleString() || 'N/A'} (${portfolioComparison.percentage_difference?.toFixed(2) || 'N/A'}%)

Asset Allocation Changes:
${allocationComparison.changes.map(change => 
  `- ${change.asset_class}: ${(change.doc1_value * 100).toFixed(2)}% → ${(change.doc2_value * 100).toFixed(2)}% (${change.direction === 'increase' ? '+' : ''}${(change.percentage_difference).toFixed(2)}%)`
).join('\n')}

${allocationComparison.additions.length > 0 ? `New Asset Classes:\n${allocationComparison.additions.map(addition => 
  `- ${addition.asset_class}: ${(addition.value * 100).toFixed(2)}%`
).join('\n')}` : ''}

${allocationComparison.removals.length > 0 ? `Removed Asset Classes:\n${allocationComparison.removals.map(removal => 
  `- ${removal.asset_class}: ${(removal.value * 100).toFixed(2)}%`
).join('\n')}` : ''}

Securities:
- Total in Document 1: ${securitiesComparison.total_securities.doc1}
- Total in Document 2: ${securitiesComparison.total_securities.doc2}
- Difference: ${securitiesComparison.total_securities.difference}

${securitiesComparison.additions.length > 0 ? `Added Securities (${securitiesComparison.additions.length}):\n${securitiesComparison.additions.slice(0, 5).map(security => 
  `- ${security.name} (${security.isin}): ${security.value?.toLocaleString() || 'N/A'}`
).join('\n')}${securitiesComparison.additions.length > 5 ? `\n- ... and ${securitiesComparison.additions.length - 5} more` : ''}` : ''}

${securitiesComparison.removals.length > 0 ? `Removed Securities (${securitiesComparison.removals.length}):\n${securitiesComparison.removals.slice(0, 5).map(security => 
  `- ${security.name} (${security.isin}): ${security.value?.toLocaleString() || 'N/A'}`
).join('\n')}${securitiesComparison.removals.length > 5 ? `\n- ... and ${securitiesComparison.removals.length - 5} more` : ''}` : ''}

${securitiesComparison.changes.length > 0 ? `Changed Securities (${securitiesComparison.changes.length}):\n${securitiesComparison.changes.slice(0, 5).map(security => 
  `- ${security.name} (${security.isin}): ${security.value.doc1?.toLocaleString() || 'N/A'} → ${security.value.doc2?.toLocaleString() || 'N/A'} (${security.value.direction === 'increase' ? '+' : ''}${security.value.percentage_change.toFixed(2)}%)`
).join('\n')}${securitiesComparison.changes.length > 5 ? `\n- ... and ${securitiesComparison.changes.length - 5} more` : ''}` : ''}

${performanceComparison.changes.length > 0 ? `Performance Changes:\n${performanceComparison.changes.map(change => 
  `- ${change.period}: ${(change.doc1_value * 100)?.toFixed(2) || 'N/A'}% → ${(change.doc2_value * 100)?.toFixed(2) || 'N/A'}% (${change.direction === 'improved' ? '+' : ''}${change.percentage_difference?.toFixed(2) || 'N/A'}%)`
).join('\n')}` : ''}

Based on this information, please provide:
1. A concise summary of the key changes between these documents (2-3 paragraphs)
2. A list of 3-5 key highlights or notable changes that deserve attention

Return your response as a JSON object with the following structure:
{
  "summary": "Your summary text here...",
  "highlights": [
    "First key highlight",
    "Second key highlight",
    ...
  ]
}
`;
  }
}

module.exports = DocumentComparisonAgent;
