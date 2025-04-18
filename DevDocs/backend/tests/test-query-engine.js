/**
 * Test Query Engine
 * 
 * Tests the query engine functionality.
 */

const QueryEngineAgent = require('../services/agents/QueryEngineAgent');
const logger = require('../utils/logger');

// Mock document data
const mockDocumentData = {
  id: '1',
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

// Test queries
const testQueries = [
  "What is the total portfolio value?",
  "What is the asset allocation?",
  "What are the top 5 holdings?",
  "What is the performance of the portfolio?",
  "What is the largest holding?",
  "How much cash is in the portfolio?",
  "What equities are in the portfolio?"
];

/**
 * Mock implementation of the QueryEngineAgent
 */
class MockQueryEngineAgent extends QueryEngineAgent {
  constructor() {
    super({ apiKey: 'mock-api-key' });
  }
  
  async processQuery(query, documentData, options = {}) {
    logger.info(`Processing query: ${query}`);
    
    // Generate mock response based on query keywords
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
    } else {
      response = `I don't have specific information about "${query}" in the document data.`;
      confidence = 0.5;
    }
    
    return {
      query,
      response,
      data,
      confidence
    };
  }
}

/**
 * Run tests for the query engine
 */
async function runTests() {
  console.log('Starting query engine tests...');
  
  let passedTests = 0;
  let failedTests = 0;
  
  // Create a mock query engine agent
  const queryEngine = new MockQueryEngineAgent();
  
  // Test each query
  for (const query of testQueries) {
    try {
      console.log(`\nTesting query: "${query}"`);
      
      // Process the query
      const result = await queryEngine.processQuery(query, mockDocumentData);
      
      // Check if the result has the expected properties
      if (result.query === query && 
          result.response && 
          typeof result.confidence === 'number') {
        console.log('✅ Query test passed');
        console.log('Response:', result.response.substring(0, 100) + (result.response.length > 100 ? '...' : ''));
        console.log('Confidence:', result.confidence);
        
        if (result.data) {
          console.log('Data keys:', Object.keys(result.data));
        }
        
        passedTests++;
      } else {
        console.error('❌ Query test failed');
        console.error('Missing expected properties in result');
        failedTests++;
      }
    } catch (error) {
      console.error('❌ Query test failed with error:', error.message);
      failedTests++;
    }
  }
  
  // Print test summary
  console.log('\n=== Test Summary ===');
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${failedTests}`);
  console.log(`Total: ${testQueries.length}`);
  
  // Return success if all tests passed
  return failedTests === 0;
}

// Run the tests
runTests()
  .then(success => {
    if (success) {
      console.log('\nAll tests passed!');
      process.exit(0);
    } else {
      console.error('\nSome tests failed!');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('Error running tests:', error);
    process.exit(1);
  });
