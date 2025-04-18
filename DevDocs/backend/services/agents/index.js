/**
 * Agents Index
 *
 * Exports all agent classes
 */

// Import agents
const QueryEngineAgent = require('./QueryEngineAgent');
const DocumentIntegrationAgent = require('./DocumentIntegrationAgent');
const HebrewOCRAgent = require('./HebrewOCRAgent');

// Mock DocumentComparisonAgent for testing
class DocumentComparisonAgent {
  constructor(options = {}) {
    this.options = options;
  }

  async compareDocuments(document1, document2, options = {}) {
    return {
      document1: {
        id: document1.id,
        date: document1.processed_at,
        portfolio_value: document1.portfolio_value
      },
      document2: {
        id: document2.id,
        date: document2.processed_at,
        portfolio_value: document2.portfolio_value
      },
      summary: {
        summary: "Mock comparison summary",
        highlights: ["Mock highlight 1", "Mock highlight 2"]
      }
    };
  }
}

module.exports = {
  DocumentComparisonAgent,
  QueryEngineAgent,
  DocumentIntegrationAgent,
  HebrewOCRAgent
};
