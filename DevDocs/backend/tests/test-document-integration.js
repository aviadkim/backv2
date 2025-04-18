/**
 * Test Document Integration
 * 
 * Tests the document integration functionality.
 */

const { DocumentIntegrationAgent } = require('../services/agents');
const logger = require('../utils/logger');

// Mock document data
const mockPortfolioDocuments = [
  {
    id: '1',
    filename: 'portfolio-statement-2023-q2.pdf',
    document_type: 'portfolio',
    processed_at: '2023-04-15T00:00:00Z',
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
      { isin: 'US0378331005', name: 'Apple Inc.', value: 95000, quantity: 500, price: 190 }
    ]
  },
  {
    id: '2',
    filename: 'portfolio-statement-2023-q1.pdf',
    document_type: 'portfolio',
    processed_at: '2023-01-15T00:00:00Z',
    portfolio_value: 1850000,
    asset_allocation: {
      'Equities': 0.35,
      'Fixed Income': 0.40,
      'Cash': 0.10,
      'Alternative Investments': 0.15
    },
    securities: [
      { isin: 'US5949181045', name: 'Microsoft Corp.', value: 150000, quantity: 500, price: 300 },
      { isin: 'US88160R1014', name: 'Tesla Inc.', value: 120000, quantity: 600, price: 200 },
      { isin: 'US0378331005', name: 'Apple Inc.', value: 85000, quantity: 500, price: 170 }
    ]
  }
];

const mockTradeDocuments = [
  {
    id: '3',
    filename: 'trade-confirmation-2023-03.pdf',
    document_type: 'trade',
    processed_at: '2023-03-15T00:00:00Z',
    trades: [
      {
        trade_date: '2023-03-15T00:00:00Z',
        type: 'buy',
        security_name: 'Microsoft Corp.',
        isin: 'US5949181045',
        quantity: 100,
        price: 300,
        value: 30000
      }
    ]
  },
  {
    id: '4',
    filename: 'trade-confirmation-2023-02.pdf',
    document_type: 'trade',
    processed_at: '2023-02-15T00:00:00Z',
    trades: [
      {
        trade_date: '2023-02-15T00:00:00Z',
        type: 'sell',
        security_name: 'Tesla Inc.',
        isin: 'US88160R1014',
        quantity: 100,
        price: 205,
        value: 20500
      }
    ]
  }
];

/**
 * Mock implementation of the DocumentIntegrationAgent
 */
class MockDocumentIntegrationAgent extends DocumentIntegrationAgent {
  constructor() {
    super({ apiKey: 'mock-api-key' });
  }
  
  async _generateInsights() {
    return {
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
    };
  }
  
  async _generateTradeInsights() {
    return {
      summary: "This is a mock trade insights result. The trading activity shows a mix of buy and sell trades.",
      key_observations: [
        "Buy trades focused on Microsoft Corp.",
        "Sell trades focused on Tesla Inc."
      ],
      recommendations: [
        "Consider diversifying buy trades across multiple securities",
        "Review the timing of sell trades to optimize returns"
      ]
    };
  }
  
  async _generateCombinedInsights() {
    return {
      summary: "This is a mock combined insights result. The portfolio and trading activity show a coherent strategy.",
      key_observations: [
        "Portfolio value increased while trading activity was moderate",
        "Buy trades aligned with the increasing allocation to equities",
        "Sell trades aligned with the decreasing allocation to fixed income"
      ],
      recommendations: [
        "Continue the current strategy of increasing equity allocation",
        "Consider taking profits on some equity positions",
        "Review the fixed income allocation for potential rebalancing"
      ]
    };
  }
}

/**
 * Test portfolio document integration
 */
async function testPortfolioIntegration() {
  console.log('Testing portfolio document integration...');
  
  try {
    // Create a mock integration agent
    const integrationAgent = new MockDocumentIntegrationAgent();
    
    // Integrate portfolio documents
    const result = await integrationAgent.integrateDocuments(mockPortfolioDocuments);
    
    // Check if the result has the expected properties
    if (result.document_count === mockPortfolioDocuments.length &&
        result.document_types.includes('portfolio') &&
        result.integration_strategy === 'portfolio' &&
        result.portfolio &&
        result.securities &&
        result.insights) {
      console.log('✅ Portfolio integration test passed');
      console.log('Document count:', result.document_count);
      console.log('Integration strategy:', result.integration_strategy);
      
      if (result.portfolio.current) {
        console.log('Current portfolio value:', result.portfolio.current.portfolio_value);
      }
      
      if (result.securities) {
        console.log('Securities count:', result.securities.length);
      }
      
      if (result.insights) {
        console.log('Insights summary:', result.insights.summary.substring(0, 50) + '...');
      }
      
      return true;
    } else {
      console.error('❌ Portfolio integration test failed');
      console.error('Missing expected properties in result');
      return false;
    }
  } catch (error) {
    console.error('❌ Portfolio integration test failed with error:', error.message);
    return false;
  }
}

/**
 * Test trade document integration
 */
async function testTradeIntegration() {
  console.log('\nTesting trade document integration...');
  
  try {
    // Create a mock integration agent
    const integrationAgent = new MockDocumentIntegrationAgent();
    
    // Integrate trade documents
    const result = await integrationAgent.integrateDocuments(mockTradeDocuments);
    
    // Check if the result has the expected properties
    if (result.document_count === mockTradeDocuments.length &&
        result.document_types.includes('trade') &&
        result.integration_strategy === 'trade' &&
        result.trades &&
        result.trade_summary &&
        result.insights) {
      console.log('✅ Trade integration test passed');
      console.log('Document count:', result.document_count);
      console.log('Integration strategy:', result.integration_strategy);
      
      if (result.trades.all) {
        console.log('Trades count:', result.trades.all.length);
      }
      
      if (result.trade_summary) {
        console.log('Buy count:', result.trade_summary.buy_count);
        console.log('Sell count:', result.trade_summary.sell_count);
      }
      
      if (result.insights) {
        console.log('Insights summary:', result.insights.summary.substring(0, 50) + '...');
      }
      
      return true;
    } else {
      console.error('❌ Trade integration test failed');
      console.error('Missing expected properties in result');
      return false;
    }
  } catch (error) {
    console.error('❌ Trade integration test failed with error:', error.message);
    return false;
  }
}

/**
 * Test mixed document integration
 */
async function testMixedIntegration() {
  console.log('\nTesting mixed document integration...');
  
  try {
    // Create a mock integration agent
    const integrationAgent = new MockDocumentIntegrationAgent();
    
    // Combine portfolio and trade documents
    const mixedDocuments = [...mockPortfolioDocuments, ...mockTradeDocuments];
    
    // Integrate mixed documents
    const result = await integrationAgent.integrateDocuments(mixedDocuments);
    
    // Check if the result has the expected properties
    if (result.document_count === mixedDocuments.length &&
        result.document_types.includes('portfolio') &&
        result.document_types.includes('trade') &&
        result.integration_strategy === 'portfolio_trade' &&
        result.portfolio &&
        result.trades &&
        result.insights) {
      console.log('✅ Mixed integration test passed');
      console.log('Document count:', result.document_count);
      console.log('Integration strategy:', result.integration_strategy);
      
      if (result.portfolio.current) {
        console.log('Current portfolio value:', result.portfolio.current.portfolio_value);
      }
      
      if (result.trades.all) {
        console.log('Trades count:', result.trades.all.length);
      }
      
      if (result.insights) {
        console.log('Insights summary:', result.insights.summary.substring(0, 50) + '...');
      }
      
      return true;
    } else {
      console.error('❌ Mixed integration test failed');
      console.error('Missing expected properties in result');
      return false;
    }
  } catch (error) {
    console.error('❌ Mixed integration test failed with error:', error.message);
    return false;
  }
}

/**
 * Run all tests
 */
async function runTests() {
  const portfolioSuccess = await testPortfolioIntegration();
  const tradeSuccess = await testTradeIntegration();
  const mixedSuccess = await testMixedIntegration();
  
  // Print test summary
  console.log('\n=== Test Summary ===');
  console.log(`Portfolio Integration: ${portfolioSuccess ? '✅ Passed' : '❌ Failed'}`);
  console.log(`Trade Integration: ${tradeSuccess ? '✅ Passed' : '❌ Failed'}`);
  console.log(`Mixed Integration: ${mixedSuccess ? '✅ Passed' : '❌ Failed'}`);
  
  return portfolioSuccess && tradeSuccess && mixedSuccess;
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
