/**
 * Financial Advisor Agent
 * 
 * Specialized agent for providing financial advice based on portfolio analysis.
 * Analyzes portfolio composition, risk, diversification, and provides recommendations.
 */

const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const config = require('../config');
const supabase = require('../db/supabase');
const openRouter = require('../services/ai/openRouterService');

/**
 * Financial Advisor Agent class
 */
class FinancialAdvisorAgent {
  /**
   * Create a new FinancialAdvisorAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      model: 'anthropic/claude-3-opus-20240229',
      maxTokens: 4000,
      temperature: 0.7,
      ...options
    };
    
    logger.info('FinancialAdvisorAgent initialized');
  }
  
  /**
   * Analyze portfolio and provide recommendations
   * @param {string} documentId - Document ID
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  async analyzePortfolio(documentId, options = {}) {
    try {
      // Get document from database
      const client = supabase.getClient();
      const { data: document, error } = await client
        .from('documents')
        .select('*')
        .eq('id', documentId)
        .single();
      
      if (error) {
        logger.error('Error getting document:', error);
        throw new Error('Error getting document');
      }
      
      if (!document) {
        throw new Error('Document not found');
      }
      
      // Get document data
      const { data: documentData, error: dataError } = await client
        .from('document_data')
        .select('*')
        .eq('document_id', documentId)
        .eq('data_type', 'financial_data')
        .order('created_at', { ascending: false })
        .limit(1);
      
      if (dataError) {
        logger.error('Error getting document data:', dataError);
        throw new Error('Error getting document data');
      }
      
      if (!documentData || documentData.length === 0) {
        throw new Error('No financial data found for this document');
      }
      
      // Get financial data
      const financialData = documentData[0].content;
      
      // Analyze portfolio
      const result = await this.generateAnalysis(document, financialData, options);
      
      // Save analysis
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: 'advisor_analysis',
          content: result,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      return result;
    } catch (error) {
      logger.error('Error analyzing portfolio:', error);
      throw error;
    }
  }
  
  /**
   * Generate portfolio analysis
   * @param {Object} document - Document object
   * @param {Object} financialData - Financial data
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  async generateAnalysis(document, financialData, options = {}) {
    try {
      const analysisOptions = {
        ...this.options,
        ...options
      };
      
      // Initialize result
      const result = {
        document_id: document.id,
        document_name: document.name,
        portfolio_summary: {
          total_value: financialData.portfolio.total_value,
          currency: financialData.portfolio.currency,
          total_securities: financialData.metrics.total_securities,
          total_asset_classes: financialData.metrics.total_asset_classes
        },
        risk_analysis: {
          risk_level: 'medium', // Default value
          risk_factors: [],
          diversification_score: 0
        },
        recommendations: [],
        insights: [],
        analysis_date: new Date().toISOString()
      };
      
      // Perform basic analysis
      await this.performBasicAnalysis(result, financialData);
      
      // Generate AI analysis
      await this.generateAIAnalysis(result, document, financialData, analysisOptions);
      
      return result;
    } catch (error) {
      logger.error('Error generating portfolio analysis:', error);
      throw error;
    }
  }
  
  /**
   * Perform basic portfolio analysis
   * @param {Object} result - Result object to update
   * @param {Object} financialData - Financial data
   * @returns {Promise<void>}
   */
  async performBasicAnalysis(result, financialData) {
    try {
      // Calculate diversification score
      const diversificationScore = this.calculateDiversificationScore(financialData);
      result.risk_analysis.diversification_score = diversificationScore;
      
      // Determine risk level based on diversification score
      if (diversificationScore < 0.3) {
        result.risk_analysis.risk_level = 'high';
        result.risk_analysis.risk_factors.push('Low diversification across asset classes');
      } else if (diversificationScore < 0.6) {
        result.risk_analysis.risk_level = 'medium';
      } else {
        result.risk_analysis.risk_level = 'low';
      }
      
      // Check for concentration risk
      const concentrationRisk = this.checkConcentrationRisk(financialData);
      if (concentrationRisk.hasRisk) {
        result.risk_analysis.risk_factors.push(
          `High concentration in ${concentrationRisk.assetClass} (${(concentrationRisk.percentage * 100).toFixed(2)}%)`
        );
      }
      
      // Check for top holdings concentration
      const topHoldingsRisk = this.checkTopHoldingsConcentration(financialData);
      if (topHoldingsRisk.hasRisk) {
        result.risk_analysis.risk_factors.push(
          `Top 3 holdings represent ${(topHoldingsRisk.percentage * 100).toFixed(2)}% of the portfolio`
        );
      }
      
      // Add basic recommendations
      if (diversificationScore < 0.3) {
        result.recommendations.push({
          type: 'diversification',
          priority: 'high',
          description: 'Increase portfolio diversification across different asset classes'
        });
      }
      
      if (concentrationRisk.hasRisk) {
        result.recommendations.push({
          type: 'asset_allocation',
          priority: 'medium',
          description: `Consider reducing exposure to ${concentrationRisk.assetClass}`
        });
      }
      
      if (topHoldingsRisk.hasRisk) {
        result.recommendations.push({
          type: 'concentration',
          priority: 'medium',
          description: 'Reduce concentration in top holdings to minimize single-security risk'
        });
      }
    } catch (error) {
      logger.error('Error performing basic analysis:', error);
      throw error;
    }
  }
  
  /**
   * Calculate diversification score
   * @param {Object} financialData - Financial data
   * @returns {number} Diversification score (0-1)
   */
  calculateDiversificationScore(financialData) {
    try {
      // Get asset allocation
      const assetAllocation = financialData.portfolio.asset_allocation || {};
      
      // Count number of asset classes
      const assetClassCount = Object.keys(assetAllocation).length;
      
      if (assetClassCount === 0) {
        return 0;
      }
      
      // Calculate Herfindahl-Hirschman Index (HHI)
      // HHI is the sum of squared percentages (0-1 scale)
      const hhi = Object.values(assetAllocation).reduce((sum, allocation) => {
        return sum + Math.pow(allocation.percentage, 2);
      }, 0);
      
      // Convert HHI to diversification score (1 - HHI)
      // Higher HHI means more concentration, so we subtract from 1 to get diversification
      const diversificationScore = 1 - hhi;
      
      return diversificationScore;
    } catch (error) {
      logger.error('Error calculating diversification score:', error);
      return 0.5; // Default to medium diversification
    }
  }
  
  /**
   * Check for concentration risk in asset classes
   * @param {Object} financialData - Financial data
   * @returns {Object} Concentration risk assessment
   */
  checkConcentrationRisk(financialData) {
    try {
      // Get asset allocation
      const assetAllocation = financialData.portfolio.asset_allocation || {};
      
      // Find asset class with highest allocation
      let highestAllocation = 0;
      let highestAssetClass = '';
      
      for (const [assetClass, allocation] of Object.entries(assetAllocation)) {
        if (allocation.percentage > highestAllocation) {
          highestAllocation = allocation.percentage;
          highestAssetClass = assetClass;
        }
      }
      
      // Check if highest allocation exceeds threshold (e.g., 50%)
      const hasRisk = highestAllocation > 0.5;
      
      return {
        hasRisk,
        assetClass: highestAssetClass,
        percentage: highestAllocation
      };
    } catch (error) {
      logger.error('Error checking concentration risk:', error);
      return { hasRisk: false };
    }
  }
  
  /**
   * Check for concentration risk in top holdings
   * @param {Object} financialData - Financial data
   * @returns {Object} Top holdings concentration assessment
   */
  checkTopHoldingsConcentration(financialData) {
    try {
      // Get securities
      const securities = financialData.portfolio.securities || [];
      
      if (securities.length === 0) {
        return { hasRisk: false };
      }
      
      // Sort securities by value
      const sortedSecurities = [...securities].sort((a, b) => b.value - a.value);
      
      // Get top 3 holdings (or fewer if less than 3 securities)
      const topCount = Math.min(3, sortedSecurities.length);
      const topHoldings = sortedSecurities.slice(0, topCount);
      
      // Calculate percentage of portfolio in top holdings
      const topHoldingsValue = topHoldings.reduce((sum, security) => sum + security.value, 0);
      const topHoldingsPercentage = topHoldingsValue / financialData.portfolio.total_value;
      
      // Check if top holdings exceed threshold (e.g., 40%)
      const hasRisk = topHoldingsPercentage > 0.4;
      
      return {
        hasRisk,
        holdings: topHoldings.map(security => security.name),
        percentage: topHoldingsPercentage
      };
    } catch (error) {
      logger.error('Error checking top holdings concentration:', error);
      return { hasRisk: false };
    }
  }
  
  /**
   * Generate AI analysis
   * @param {Object} result - Result object to update
   * @param {Object} document - Document object
   * @param {Object} financialData - Financial data
   * @param {Object} options - Analysis options
   * @returns {Promise<void>}
   */
  async generateAIAnalysis(result, document, financialData, options) {
    try {
      // Create prompt for AI
      const prompt = `
You are a financial advisor analyzing a portfolio. I have extracted financial data from a document and performed some basic analysis. I need your help to provide deeper insights and recommendations.

Document Name: ${document.name}

Portfolio Summary:
- Total Value: ${financialData.portfolio.total_value} ${financialData.portfolio.currency}
- Total Securities: ${financialData.metrics.total_securities}
- Total Asset Classes: ${financialData.metrics.total_asset_classes}

Asset Allocation:
${Object.entries(financialData.portfolio.asset_allocation || {})
  .map(([assetClass, allocation]) => `- ${assetClass}: ${(allocation.percentage * 100).toFixed(2)}% (${allocation.value} ${financialData.portfolio.currency})`)
  .join('\n')}

Top Securities:
${financialData.portfolio.securities
  ? financialData.portfolio.securities
      .sort((a, b) => b.value - a.value)
      .slice(0, 5)
      .map(security => `- ${security.name} (${security.isin}): ${security.value} ${financialData.portfolio.currency} (${((security.value / financialData.portfolio.total_value) * 100).toFixed(2)}%)`)
      .join('\n')
  : 'No securities data available'}

Basic Analysis:
- Risk Level: ${result.risk_analysis.risk_level}
- Diversification Score: ${result.risk_analysis.diversification_score.toFixed(2)}
- Risk Factors: ${result.risk_analysis.risk_factors.join(', ') || 'None identified'}

Please provide:
1. A deeper analysis of the portfolio's risk profile and diversification
2. Specific recommendations for improving the portfolio
3. Insights about the portfolio's strengths and weaknesses
4. Any other observations or advice that would be valuable

Format your response as a structured JSON object with the following fields:
- risk_analysis: Additional risk factors and detailed risk assessment
- recommendations: Array of specific recommendations with type, priority, and description
- insights: Array of insights about the portfolio
- summary: Brief summary of the overall analysis

Please ensure your recommendations are specific, actionable, and based on the portfolio data provided.
`;
      
      // Call OpenRouter API
      const aiResponse = await openRouter.generateText({
        prompt,
        model: options.model,
        max_tokens: options.maxTokens,
        temperature: options.temperature
      });
      
      // Parse AI response
      try {
        // Extract JSON from AI response
        const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/) || 
                         aiResponse.match(/```\n([\s\S]*?)\n```/) ||
                         aiResponse.match(/\{[\s\S]*?\}/);
        
        if (jsonMatch) {
          const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
          const analysisData = JSON.parse(jsonStr);
          
          // Update result with AI analysis
          if (analysisData.risk_analysis) {
            // Add risk factors from AI
            if (analysisData.risk_analysis.risk_factors) {
              result.risk_analysis.risk_factors = [
                ...result.risk_analysis.risk_factors,
                ...analysisData.risk_analysis.risk_factors
              ];
            }
            
            // Add other risk analysis fields
            for (const [key, value] of Object.entries(analysisData.risk_analysis)) {
              if (key !== 'risk_factors') {
                result.risk_analysis[key] = value;
              }
            }
          }
          
          // Add recommendations from AI
          if (analysisData.recommendations) {
            result.recommendations = [
              ...result.recommendations,
              ...analysisData.recommendations
            ];
          }
          
          // Add insights from AI
          if (analysisData.insights) {
            result.insights = analysisData.insights;
          }
          
          // Add summary from AI
          if (analysisData.summary) {
            result.summary = analysisData.summary;
          }
        } else {
          // If JSON parsing fails, use the entire response as a summary
          result.ai_analysis = aiResponse;
        }
      } catch (parseError) {
        logger.warn('Error parsing AI response:', parseError);
        
        // Use the entire response as a summary
        result.ai_analysis = aiResponse;
      }
    } catch (error) {
      logger.error('Error generating AI analysis:', error);
      // Continue without AI analysis
    }
  }
  
  /**
   * Get advisor analysis for a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} Advisor analysis
   */
  async getAdvisorAnalysis(documentId) {
    try {
      // Get document data
      const client = supabase.getClient();
      const { data, error } = await client
        .from('document_data')
        .select('*')
        .eq('document_id', documentId)
        .eq('data_type', 'advisor_analysis')
        .order('created_at', { ascending: false })
        .limit(1);
      
      if (error) {
        logger.error('Error getting advisor analysis:', error);
        throw new Error('Error getting advisor analysis');
      }
      
      if (!data || data.length === 0) {
        throw new Error('No advisor analysis found for this document');
      }
      
      return data[0].content;
    } catch (error) {
      logger.error('Error in getAdvisorAnalysis:', error);
      throw error;
    }
  }
}

module.exports = FinancialAdvisorAgent;
