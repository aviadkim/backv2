/**
 * Test script for FinancialAdvisorAgent
 * This file will not be committed to GitHub
 */

// Mock the Supabase client
const mockSupabaseClient = {
  from: (table) => ({
    select: () => ({
      eq: (field, value) => ({
        single: async () => {
          if (table === 'documents') {
            return { data: { id: 'mock-document-id', name: 'Sample Portfolio' }, error: null };
          }
          return { data: null, error: null };
        },
        order: () => ({
          limit: async () => {
            if (table === 'document_data' && field === 'document_id' && value === 'mock-document-id') {
              return { 
                data: [{ 
                  content: portfolioData 
                }], 
                error: null 
              };
            }
            return { data: [], error: null };
          }
        })
      })
    }),
    insert: async () => ({ data: { id: 'mock-data-id' }, error: null })
  })
};

// Sample portfolio data
const portfolioData = {
  portfolio: {
    total_value: 846420.25,
    currency: 'USD',
    securities: [
      {
        isin: 'US0378331005',
        name: 'Apple Inc.',
        quantity: 100,
        price: 175.5,
        value: 17550,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US5949181045',
        name: 'Microsoft Corp.',
        quantity: 50,
        price: 410.3,
        value: 20515,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US88160R1014',
        name: 'Tesla Inc.',
        quantity: 20,
        price: 219.5,
        value: 4390,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US0231351067',
        name: 'Amazon.com Inc.',
        quantity: 30,
        price: 178.75,
        value: 5362.5,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US30303M1027',
        name: 'Meta Platforms Inc.',
        quantity: 40,
        price: 485.2,
        value: 19408,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US02079K1079',
        name: 'Alphabet Inc.',
        quantity: 25,
        price: 175.85,
        value: 4396.25,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US67066G1040',
        name: 'NVIDIA Corp.',
        quantity: 15,
        price: 890.5,
        value: 13357.5,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US4781601046',
        name: 'Johnson & Johnson',
        quantity: 60,
        price: 157.8,
        value: 9468,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US9311421039',
        name: 'Walmart Inc.',
        quantity: 80,
        price: 59.75,
        value: 4780,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US1912161007',
        name: 'Coca-Cola Co.',
        quantity: 120,
        price: 60.15,
        value: 7218,
        currency: 'USD',
        assetClass: 'Equities'
      },
      {
        isin: 'US91282CJL79',
        name: 'US Treasury Bond 3.5% 2033',
        quantity: 100000,
        price: 98.75,
        value: 98750,
        currency: 'USD',
        assetClass: 'Fixed Income'
      },
      {
        isin: 'US91282CFX29',
        name: 'US Treasury Bond 4.25% 2028',
        quantity: 150000,
        price: 101.25,
        value: 151875,
        currency: 'USD',
        assetClass: 'Fixed Income'
      },
      {
        isin: 'XS2281342878',
        name: 'Credit Suisse 3.75% 2026',
        quantity: 200000,
        price: 97.5,
        value: 195000,
        currency: 'USD',
        assetClass: 'Fixed Income'
      },
      {
        isin: 'XS2315191069',
        name: 'UBS Group 4.25% 2028',
        quantity: 200000,
        price: 99.3,
        value: 198600,
        currency: 'USD',
        assetClass: 'Fixed Income'
      },
      {
        isin: 'US037833DX25',
        name: 'Apple Inc. 3.85% 2043',
        quantity: 100000,
        price: 95.75,
        value: 95750,
        currency: 'USD',
        assetClass: 'Fixed Income'
      }
    ],
    asset_allocation: {
      'Equities': {
        value: 106445.25,
        percentage: 0.12575933763399447
      },
      'Fixed Income': {
        value: 739975,
        percentage: 0.8742406623660055
      }
    }
  },
  metrics: {
    total_securities: 15,
    total_asset_classes: 2,
    average_security_value: 56428.01666666667
  }
};

// Mock the OpenRouter service
const mockOpenRouterService = {
  generateText: async ({ prompt, model, max_tokens, temperature }) => {
    console.log('Generating text with OpenRouter...');
    console.log('Prompt:', prompt.substring(0, 100) + '...');
    
    // Return a mock response
    return `
{
  "risk_analysis": {
    "risk_factors": [
      "High concentration in Fixed Income (87.4%)",
      "Equity holdings concentrated in US tech sector",
      "Credit risk from financial sector bonds (Credit Suisse, UBS)",
      "Interest rate risk due to large fixed income allocation"
    ],
    "diversification_score": 0.35,
    "interest_rate_sensitivity": "high",
    "credit_quality": "medium"
  },
  "recommendations": [
    {
      "type": "asset_allocation",
      "priority": "high",
      "description": "Reduce fixed income allocation to 60-70% and increase equity exposure"
    },
    {
      "type": "diversification",
      "priority": "high",
      "description": "Diversify equity holdings beyond US tech sector into other sectors and geographies"
    },
    {
      "type": "credit_risk",
      "priority": "medium",
      "description": "Review and potentially reduce exposure to Credit Suisse and UBS bonds"
    },
    {
      "type": "interest_rate",
      "priority": "medium",
      "description": "Consider shorter duration bonds to reduce interest rate sensitivity"
    }
  ],
  "insights": [
    {
      "title": "Conservative Allocation",
      "description": "The portfolio has a conservative allocation with 87.4% in fixed income, which may limit growth potential."
    },
    {
      "title": "Tech Concentration",
      "description": "The equity portion is heavily concentrated in US tech stocks, which increases sector-specific risk."
    },
    {
      "title": "Interest Rate Vulnerability",
      "description": "The large allocation to fixed income makes the portfolio vulnerable to rising interest rates."
    },
    {
      "title": "Credit Risk",
      "description": "Significant exposure to financial sector bonds (Credit Suisse, UBS) introduces credit risk."
    }
  ],
  "summary": "The portfolio is heavily weighted towards fixed income (87.4%), which provides stability but limits growth potential and introduces interest rate risk. The equity portion is concentrated in US tech stocks, lacking sector and geographic diversification. Significant exposure to financial sector bonds introduces credit risk. Recommended actions include reducing fixed income allocation, diversifying equity holdings, and reviewing credit risk exposure."
}`;
  }
};

// Mock the required modules
jest.mock('./DevDocs/backend/db/supabase', () => ({
  getClient: () => mockSupabaseClient
}));

jest.mock('./DevDocs/backend/services/ai/openRouterService', () => mockOpenRouterService);

jest.mock('./DevDocs/backend/utils/logger', () => ({
  info: console.log,
  error: console.error,
  warn: console.warn,
  debug: console.log
}));

// Import the FinancialAdvisorAgent
const FinancialAdvisorAgent = require('./DevDocs/backend/agents/FinancialAdvisorAgent');

async function testFinancialAdvisorAgent() {
  try {
    console.log('Testing FinancialAdvisorAgent...');
    
    // Create an instance of the FinancialAdvisorAgent
    const advisorAgent = new FinancialAdvisorAgent({
      model: 'anthropic/claude-3-opus-20240229',
      maxTokens: 4000,
      temperature: 0.7
    });
    
    // Analyze portfolio
    console.log('Analyzing portfolio...');
    const result = await advisorAgent.analyzePortfolio('mock-document-id');
    
    console.log('Analysis result:');
    console.log(JSON.stringify(result, null, 2));
    
    return result;
  } catch (error) {
    console.error('Error testing FinancialAdvisorAgent:', error);
    return null;
  }
}

// Run the test
testFinancialAdvisorAgent();
