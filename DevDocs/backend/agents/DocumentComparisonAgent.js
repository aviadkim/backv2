/**
 * Document Comparison Agent
 * 
 * Specialized agent for comparing financial documents and identifying differences.
 * Compares portfolios, securities, asset allocations, and other financial data.
 */

const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const config = require('../config');
const supabase = require('../db/supabase');
const openRouter = require('../services/ai/openRouterService');
const FinancialDataAnalyzerAgent = require('./FinancialDataAnalyzerAgent');

/**
 * Document Comparison Agent class
 */
class DocumentComparisonAgent {
  /**
   * Create a new DocumentComparisonAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      enhanceWithAI: true,
      confidenceThreshold: 0.7,
      maxRetries: 3,
      ...options
    };
    
    // Initialize financial data analyzer agent
    this.financialDataAnalyzerAgent = new FinancialDataAnalyzerAgent();
    
    logger.info('DocumentComparisonAgent initialized');
  }
  
  /**
   * Compare two documents
   * @param {string} documentId1 - First document ID
   * @param {string} documentId2 - Second document ID
   * @param {Object} options - Comparison options
   * @returns {Promise<Object>} Comparison results
   */
  async compareDocuments(documentId1, documentId2, options = {}) {
    try {
      // Get documents from database
      const client = supabase.getClient();
      const { data: documents, error } = await client
        .from('documents')
        .select('*')
        .in('id', [documentId1, documentId2]);
      
      if (error) {
        logger.error('Error getting documents:', error);
        throw new Error('Error getting documents');
      }
      
      if (!documents || documents.length !== 2) {
        throw new Error('One or both documents not found');
      }
      
      // Get document data
      const { data: documentData, error: dataError } = await client
        .from('document_data')
        .select('*')
        .in('document_id', [documentId1, documentId2])
        .in('data_type', ['financial_data', 'ocr', 'tables'])
        .order('created_at', { ascending: false });
      
      if (dataError) {
        logger.error('Error getting document data:', dataError);
        throw new Error('Error getting document data');
      }
      
      // Get financial data for both documents
      const financialData1 = documentData.find(data => 
        data.document_id === documentId1 && data.data_type === 'financial_data'
      );
      
      const financialData2 = documentData.find(data => 
        data.document_id === documentId2 && data.data_type === 'financial_data'
      );
      
      // If financial data is missing for either document, process it first
      if (!financialData1) {
        await this.financialDataAnalyzerAgent.processDocument(documentId1);
      }
      
      if (!financialData2) {
        await this.financialDataAnalyzerAgent.processDocument(documentId2);
      }
      
      // Get updated financial data if needed
      let updatedFinancialData1 = financialData1;
      let updatedFinancialData2 = financialData2;
      
      if (!financialData1 || !financialData2) {
        const { data: updatedData, error: updatedError } = await client
          .from('document_data')
          .select('*')
          .in('document_id', [documentId1, documentId2])
          .eq('data_type', 'financial_data')
          .order('created_at', { ascending: false });
        
        if (updatedError) {
          logger.error('Error getting updated document data:', updatedError);
          throw new Error('Error getting updated document data');
        }
        
        updatedFinancialData1 = updatedData.find(data => data.document_id === documentId1);
        updatedFinancialData2 = updatedData.find(data => data.document_id === documentId2);
      }
      
      // Compare documents
      const result = await this.compareFinancialData(
        documents[0],
        documents[1],
        updatedFinancialData1,
        updatedFinancialData2,
        options
      );
      
      // Save comparison results
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId1,
          data_type: 'comparison',
          content: {
            ...result,
            compared_with: documentId2,
            timestamp: new Date().toISOString()
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      return result;
    } catch (error) {
      logger.error('Error comparing documents:', error);
      throw error;
    }
  }
  
  /**
   * Compare financial data from two documents
   * @param {Object} document1 - First document
   * @param {Object} document2 - Second document
   * @param {Object} financialData1 - Financial data for first document
   * @param {Object} financialData2 - Financial data for second document
   * @param {Object} options - Comparison options
   * @returns {Promise<Object>} Comparison results
   */
  async compareFinancialData(document1, document2, financialData1, financialData2, options = {}) {
    try {
      const processingOptions = {
        ...this.options,
        ...options
      };
      
      // Initialize result
      const result = {
        document1: {
          id: document1.id,
          name: document1.name,
          created_at: document1.created_at
        },
        document2: {
          id: document2.id,
          name: document2.name,
          created_at: document2.created_at
        },
        portfolio_comparison: {
          total_value_difference: 0,
          total_value_percentage_change: 0,
          securities_added: [],
          securities_removed: [],
          securities_changed: []
        },
        asset_allocation_comparison: {
          added: [],
          removed: [],
          changed: []
        },
        summary: {
          total_changes: 0,
          significant_changes: []
        },
        comparison_date: new Date().toISOString()
      };
      
      // Compare portfolio total values
      if (financialData1 && financialData2 && 
          financialData1.content && financialData2.content &&
          financialData1.content.portfolio && financialData2.content.portfolio) {
        
        const portfolio1 = financialData1.content.portfolio;
        const portfolio2 = financialData2.content.portfolio;
        
        // Calculate total value difference
        result.portfolio_comparison.total_value_difference = 
          portfolio2.total_value - portfolio1.total_value;
        
        // Calculate percentage change
        if (portfolio1.total_value > 0) {
          result.portfolio_comparison.total_value_percentage_change = 
            (result.portfolio_comparison.total_value_difference / portfolio1.total_value) * 100;
        }
        
        // Compare securities
        await this.compareSecurities(result, portfolio1, portfolio2);
        
        // Compare asset allocation
        await this.compareAssetAllocation(result, portfolio1, portfolio2);
        
        // Calculate total changes
        result.summary.total_changes = 
          result.portfolio_comparison.securities_added.length +
          result.portfolio_comparison.securities_removed.length +
          result.portfolio_comparison.securities_changed.length +
          result.asset_allocation_comparison.added.length +
          result.asset_allocation_comparison.removed.length +
          result.asset_allocation_comparison.changed.length;
        
        // Identify significant changes
        await this.identifySignificantChanges(result);
      }
      
      // Enhance with AI if enabled
      if (processingOptions.enhanceWithAI) {
        await this.enhanceWithAI(result, document1, document2, financialData1, financialData2);
      }
      
      return result;
    } catch (error) {
      logger.error('Error comparing financial data:', error);
      throw error;
    }
  }
  
  /**
   * Compare securities between two portfolios
   * @param {Object} result - Result object to update
   * @param {Object} portfolio1 - First portfolio
   * @param {Object} portfolio2 - Second portfolio
   * @returns {Promise<void>}
   */
  async compareSecurities(result, portfolio1, portfolio2) {
    try {
      // Create maps for easier comparison
      const securitiesMap1 = new Map();
      const securitiesMap2 = new Map();
      
      // Map securities by ISIN
      portfolio1.securities.forEach(security => {
        if (security.isin) {
          securitiesMap1.set(security.isin, security);
        }
      });
      
      portfolio2.securities.forEach(security => {
        if (security.isin) {
          securitiesMap2.set(security.isin, security);
        }
      });
      
      // Find added securities
      for (const [isin, security] of securitiesMap2) {
        if (!securitiesMap1.has(isin)) {
          result.portfolio_comparison.securities_added.push({
            name: security.name,
            isin: security.isin,
            quantity: security.quantity,
            value: security.value,
            percentage: security.value / portfolio2.total_value
          });
        }
      }
      
      // Find removed securities
      for (const [isin, security] of securitiesMap1) {
        if (!securitiesMap2.has(isin)) {
          result.portfolio_comparison.securities_removed.push({
            name: security.name,
            isin: security.isin,
            quantity: security.quantity,
            value: security.value,
            percentage: security.value / portfolio1.total_value
          });
        }
      }
      
      // Find changed securities
      for (const [isin, security1] of securitiesMap1) {
        if (securitiesMap2.has(isin)) {
          const security2 = securitiesMap2.get(isin);
          
          // Calculate changes
          const quantityDifference = security2.quantity - security1.quantity;
          const valueDifference = security2.value - security1.value;
          
          // Calculate percentage changes
          let quantityPercentageChange = 0;
          let valuePercentageChange = 0;
          
          if (security1.quantity > 0) {
            quantityPercentageChange = (quantityDifference / security1.quantity) * 100;
          }
          
          if (security1.value > 0) {
            valuePercentageChange = (valueDifference / security1.value) * 100;
          }
          
          // Add to changed securities if there's a significant change
          if (Math.abs(quantityPercentageChange) > 1 || Math.abs(valuePercentageChange) > 1) {
            result.portfolio_comparison.securities_changed.push({
              name: security1.name,
              isin: security1.isin,
              quantity1: security1.quantity,
              quantity2: security2.quantity,
              quantity_difference: quantityDifference,
              quantity_percentage_change: quantityPercentageChange,
              value1: security1.value,
              value2: security2.value,
              value_difference: valueDifference,
              value_percentage_change: valuePercentageChange
            });
          }
        }
      }
    } catch (error) {
      logger.error('Error comparing securities:', error);
      throw error;
    }
  }
  
  /**
   * Compare asset allocation between two portfolios
   * @param {Object} result - Result object to update
   * @param {Object} portfolio1 - First portfolio
   * @param {Object} portfolio2 - Second portfolio
   * @returns {Promise<void>}
   */
  async compareAssetAllocation(result, portfolio1, portfolio2) {
    try {
      // Get asset allocation
      const assetAllocation1 = portfolio1.asset_allocation || {};
      const assetAllocation2 = portfolio2.asset_allocation || {};
      
      // Find added asset classes
      for (const assetClass in assetAllocation2) {
        if (!assetAllocation1[assetClass]) {
          result.asset_allocation_comparison.added.push({
            asset_class: assetClass,
            percentage: assetAllocation2[assetClass].percentage,
            value: assetAllocation2[assetClass].value
          });
        }
      }
      
      // Find removed asset classes
      for (const assetClass in assetAllocation1) {
        if (!assetAllocation2[assetClass]) {
          result.asset_allocation_comparison.removed.push({
            asset_class: assetClass,
            percentage: assetAllocation1[assetClass].percentage,
            value: assetAllocation1[assetClass].value
          });
        }
      }
      
      // Find changed asset classes
      for (const assetClass in assetAllocation1) {
        if (assetAllocation2[assetClass]) {
          // Calculate changes
          const percentageDifference = 
            assetAllocation2[assetClass].percentage - assetAllocation1[assetClass].percentage;
          
          const valueDifference = 
            assetAllocation2[assetClass].value - assetAllocation1[assetClass].value;
          
          // Calculate percentage change in value
          let valuePercentageChange = 0;
          
          if (assetAllocation1[assetClass].value > 0) {
            valuePercentageChange = (valueDifference / assetAllocation1[assetClass].value) * 100;
          }
          
          // Add to changed asset classes if there's a significant change
          if (Math.abs(percentageDifference) > 0.01 || Math.abs(valuePercentageChange) > 1) {
            result.asset_allocation_comparison.changed.push({
              asset_class: assetClass,
              percentage1: assetAllocation1[assetClass].percentage,
              percentage2: assetAllocation2[assetClass].percentage,
              percentage_difference: percentageDifference,
              value1: assetAllocation1[assetClass].value,
              value2: assetAllocation2[assetClass].value,
              value_difference: valueDifference,
              value_percentage_change: valuePercentageChange
            });
          }
        }
      }
    } catch (error) {
      logger.error('Error comparing asset allocation:', error);
      throw error;
    }
  }
  
  /**
   * Identify significant changes
   * @param {Object} result - Result object to update
   * @returns {Promise<void>}
   */
  async identifySignificantChanges(result) {
    try {
      // Add total value change if significant
      if (Math.abs(result.portfolio_comparison.total_value_percentage_change) > 5) {
        result.summary.significant_changes.push({
          type: 'total_value',
          description: `Total portfolio value ${result.portfolio_comparison.total_value_difference > 0 ? 'increased' : 'decreased'} by ${Math.abs(result.portfolio_comparison.total_value_percentage_change).toFixed(2)}%`,
          percentage_change: result.portfolio_comparison.total_value_percentage_change
        });
      }
      
      // Add significant security changes
      for (const security of result.portfolio_comparison.securities_changed) {
        if (Math.abs(security.value_percentage_change) > 10) {
          result.summary.significant_changes.push({
            type: 'security',
            security_name: security.name,
            security_isin: security.isin,
            description: `${security.name} ${security.value_difference > 0 ? 'increased' : 'decreased'} by ${Math.abs(security.value_percentage_change).toFixed(2)}%`,
            percentage_change: security.value_percentage_change
          });
        }
      }
      
      // Add significant asset allocation changes
      for (const assetClass of result.asset_allocation_comparison.changed) {
        if (Math.abs(assetClass.percentage_difference) > 0.05) {
          result.summary.significant_changes.push({
            type: 'asset_allocation',
            asset_class: assetClass.asset_class,
            description: `${assetClass.asset_class} allocation ${assetClass.percentage_difference > 0 ? 'increased' : 'decreased'} by ${Math.abs(assetClass.percentage_difference * 100).toFixed(2)} percentage points`,
            percentage_change: assetClass.percentage_difference * 100
          });
        }
      }
      
      // Add added securities if significant
      for (const security of result.portfolio_comparison.securities_added) {
        if (security.percentage > 0.05) {
          result.summary.significant_changes.push({
            type: 'security_added',
            security_name: security.name,
            security_isin: security.isin,
            description: `Added ${security.name} (${(security.percentage * 100).toFixed(2)}% of portfolio)`,
            percentage: security.percentage * 100
          });
        }
      }
      
      // Add removed securities if significant
      for (const security of result.portfolio_comparison.securities_removed) {
        if (security.percentage > 0.05) {
          result.summary.significant_changes.push({
            type: 'security_removed',
            security_name: security.name,
            security_isin: security.isin,
            description: `Removed ${security.name} (was ${(security.percentage * 100).toFixed(2)}% of portfolio)`,
            percentage: security.percentage * 100
          });
        }
      }
      
      // Sort significant changes by absolute percentage change
      result.summary.significant_changes.sort((a, b) => {
        const aPercentage = Math.abs(a.percentage_change || a.percentage || 0);
        const bPercentage = Math.abs(b.percentage_change || b.percentage || 0);
        return bPercentage - aPercentage;
      });
    } catch (error) {
      logger.error('Error identifying significant changes:', error);
      throw error;
    }
  }
  
  /**
   * Enhance comparison results with AI
   * @param {Object} result - Result object to update
   * @param {Object} document1 - First document
   * @param {Object} document2 - Second document
   * @param {Object} financialData1 - Financial data for first document
   * @param {Object} financialData2 - Financial data for second document
   * @returns {Promise<void>}
   */
  async enhanceWithAI(result, document1, document2, financialData1, financialData2) {
    try {
      // Create prompt for AI
      const prompt = `
You are a financial document analysis expert. I have compared two financial documents and need your help to enhance the comparison results and provide insights.

Document 1: ${document1.name} (${new Date(document1.created_at).toLocaleDateString()})
Document 2: ${document2.name} (${new Date(document2.created_at).toLocaleDateString()})

Here are the comparison results:
${JSON.stringify(result, null, 2)}

Please analyze these results and provide:
1. A summary of the key changes between the two documents
2. Potential reasons for the significant changes
3. Any patterns or trends you observe
4. Recommendations based on the changes
5. Any additional insights that might be valuable

Please return your analysis in a structured format that I can easily integrate into my comparison results.
`;
      
      // Call OpenRouter API
      const aiResponse = await openRouter.generateText({
        prompt,
        model: 'anthropic/claude-3-opus-20240229',
        max_tokens: 4000
      });
      
      // Add AI analysis to result
      result.ai_analysis = {
        analysis: aiResponse,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('Error enhancing comparison with AI:', error);
      // Continue without AI enhancement
    }
  }
  
  /**
   * Get comparison history for a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Array>} Comparison history
   */
  async getComparisonHistory(documentId) {
    try {
      // Get document data
      const client = supabase.getClient();
      const { data, error } = await client
        .from('document_data')
        .select('*')
        .eq('document_id', documentId)
        .eq('data_type', 'comparison')
        .order('created_at', { ascending: false });
      
      if (error) {
        logger.error('Error getting comparison history:', error);
        throw new Error('Error getting comparison history');
      }
      
      return data.map(item => ({
        id: item.id,
        documentId: item.document_id,
        comparedWith: item.content.compared_with,
        timestamp: item.content.comparison_date,
        summary: item.content.summary
      }));
    } catch (error) {
      logger.error('Error in getComparisonHistory:', error);
      throw error;
    }
  }
}

module.exports = DocumentComparisonAgent;
