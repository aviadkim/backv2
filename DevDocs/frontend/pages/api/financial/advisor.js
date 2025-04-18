// API endpoint for financial advisor

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { document_id, query } = req.body;

    if (!document_id) {
      return res.status(400).json({ error: 'Document ID is required' });
    }

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // In a real implementation, we would fetch the document from the database
    // and use the OpenRouter API to generate a response
    // For now, we'll return mock data

    // Mock response based on the query
    const mockResponse = generateMockResponse(query);
    
    return res.status(200).json(mockResponse);
  } catch (error) {
    console.error('Error querying advisor:', error);
    return res.status(500).json({ 
      error: 'Error querying advisor', 
      detail: error.message 
    });
  }
}

/**
 * Generate a mock response based on the query
 * @param {string} query - The user's query
 * @returns {Object} - Mock response
 */
function generateMockResponse(query) {
  // Mock portfolio data
  const portfolioData = {
    portfolio_value: 1950000,
    asset_allocation: {
      'Equities': 0.40,
      'Fixed Income': 0.35,
      'Cash': 0.05,
      'Alternative Investments': 0.20
    },
    top_holdings: [
      {
        name: 'Microsoft Corp.',
        isin: 'US5949181045',
        value: 180000
      },
      {
        name: 'Tesla Inc.',
        isin: 'US88160R1014',
        value: 105000
      },
      {
        name: 'Apple Inc.',
        isin: 'US0378331005',
        value: 95000
      },
      {
        name: 'Amazon.com Inc.',
        isin: 'US0231351067',
        value: 90000
      },
      {
        name: 'Meta Platforms Inc.',
        isin: 'US30303M1027',
        value: 75000
      }
    ],
    metrics: {
      diversification_score: 0.72,
      risk_level: 'moderate',
      sharpe_ratio: 0.85,
      volatility: 0.12,
      expected_return: 0.08
    }
  };

  // Generate response based on query keywords
  let response = '';
  let data = null;

  const lowerQuery = query.toLowerCase();

  if (lowerQuery.includes('asset allocation') || lowerQuery.includes('allocation')) {
    response = `Your portfolio has the following asset allocation:\n\n` +
      `- Equities: 40%\n` +
      `- Fixed Income: 35%\n` +
      `- Cash: 5%\n` +
      `- Alternative Investments: 20%\n\n` +
      `This allocation is relatively balanced with a slight tilt towards equities, which is appropriate for moderate growth objectives. The 5% cash position provides some liquidity for opportunities or emergencies, while the 20% allocation to alternative investments adds diversification beyond traditional asset classes.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation
    };
  } else if (lowerQuery.includes('top') && (lowerQuery.includes('holdings') || lowerQuery.includes('positions'))) {
    response = `Your top 5 holdings by value are:\n\n` +
      `1. Microsoft Corp. (US5949181045): $180,000 (9.2% of portfolio)\n` +
      `2. Tesla Inc. (US88160R1014): $105,000 (5.4% of portfolio)\n` +
      `3. Apple Inc. (US0378331005): $95,000 (4.9% of portfolio)\n` +
      `4. Amazon.com Inc. (US0231351067): $90,000 (4.6% of portfolio)\n` +
      `5. Meta Platforms Inc. (US30303M1027): $75,000 (3.8% of portfolio)\n\n` +
      `These top 5 holdings represent approximately 28% of your total portfolio value. This concentration is moderate and within reasonable limits, though you may want to monitor these positions to ensure they don't grow to dominate your portfolio risk profile.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      top_holdings: portfolioData.top_holdings
    };
  } else if (lowerQuery.includes('diversif')) {
    response = `Your portfolio has a diversification score of 72 out of 100, which indicates a moderately well-diversified portfolio.\n\n` +
      `Your assets are spread across multiple asset classes:\n` +
      `- Equities: 40%\n` +
      `- Fixed Income: 35%\n` +
      `- Cash: 5%\n` +
      `- Alternative Investments: 20%\n\n` +
      `Within your equity allocation, you have exposure to different sectors including technology, consumer discretionary, and communication services. However, there appears to be a concentration in technology stocks, which represent about 20% of your total portfolio.\n\n` +
      `To improve diversification, you might consider:\n` +
      `1. Adding exposure to international markets, particularly emerging markets\n` +
      `2. Increasing allocation to sectors like healthcare, utilities, and consumer staples\n` +
      `3. Considering real estate investments (REITs) as part of your alternative investments`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      metrics: {
        diversification_score: portfolioData.metrics.diversification_score
      }
    };
  } else if (lowerQuery.includes('technology') || lowerQuery.includes('tech')) {
    response = `Your exposure to technology stocks is approximately 20% of your total portfolio value ($390,000).\n\n` +
      `This includes positions in:\n` +
      `- Microsoft Corp.: $180,000 (9.2% of portfolio)\n` +
      `- Apple Inc.: $95,000 (4.9% of portfolio)\n` +
      `- Amazon.com Inc.: $90,000 (4.6% of portfolio) - though Amazon is often classified as Consumer Discretionary, it has significant technology operations\n` +
      `- Other smaller technology positions: $25,000 (1.3% of portfolio)\n\n` +
      `This level of technology exposure is moderately high but not excessive for a growth-oriented portfolio. The technology sector has historically delivered strong returns but can experience higher volatility. Your exposure is primarily to large, established companies with strong balance sheets, which helps mitigate some of the sector risk.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      top_holdings: portfolioData.top_holdings.filter(h => 
        h.name.includes('Microsoft') || 
        h.name.includes('Apple') || 
        h.name.includes('Amazon')
      )
    };
  } else if (lowerQuery.includes('recommend') || lowerQuery.includes('improve')) {
    response = `Based on your current portfolio, here are my recommendations to improve your investment strategy:\n\n` +
      `1. **Increase International Exposure**: Your portfolio is heavily weighted towards US equities. Consider adding international developed markets (10-15%) and emerging markets (5-10%) to improve diversification.\n\n` +
      `2. **Rebalance Sector Allocations**: Technology represents about 20% of your portfolio. Consider trimming some tech positions and reallocating to underrepresented sectors like healthcare and consumer staples.\n\n` +
      `3. **Review Fixed Income Duration**: With interest rates potentially changing, review the duration of your fixed income holdings. Consider a barbell strategy with both short-term and long-term bonds.\n\n` +
      `4. **Increase Alternative Investments**: Your 20% allocation to alternatives is good, but consider diversifying within this category to include REITs, commodities, and perhaps private equity if appropriate for your risk tolerance.\n\n` +
      `5. **Tax-Loss Harvesting**: Several positions show unrealized losses that could be harvested for tax benefits while maintaining similar market exposure.\n\n` +
      `6. **Emergency Fund Review**: Ensure your 5% cash position is sufficient for your emergency needs (typically 3-6 months of expenses) before deploying more capital to investments.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      metrics: portfolioData.metrics
    };
  } else if (lowerQuery.includes('risk')) {
    response = `Your portfolio has a moderate risk level with the following risk metrics:\n\n` +
      `- Volatility: 12% (annualized standard deviation)\n` +
      `- Sharpe Ratio: 0.85 (risk-adjusted return)\n` +
      `- Maximum Drawdown: 18% (historical)\n` +
      `- Beta: 0.92 (relative to S&P 500)\n\n` +
      `This risk profile is appropriate for an investor with a moderate risk tolerance and a medium to long-term investment horizon (7-10+ years). Your 40% allocation to equities contributes most to the portfolio risk, while your fixed income holdings (35%) and cash (5%) provide stability.\n\n` +
      `Your alternative investments (20%) add diversification but also contribute to the overall risk. The portfolio's expected return of 8% annually is reasonable given this risk profile.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      metrics: {
        risk_level: portfolioData.metrics.risk_level,
        volatility: portfolioData.metrics.volatility,
        sharpe_ratio: portfolioData.metrics.sharpe_ratio,
        expected_return: portfolioData.metrics.expected_return
      }
    };
  } else if (lowerQuery.includes('volatility')) {
    response = `To reduce your portfolio's volatility (currently at 12% annualized), consider these strategies:\n\n` +
      `1. **Increase Fixed Income Allocation**: Consider increasing your fixed income allocation from 35% to 40-45%, focusing on high-quality bonds with moderate duration.\n\n` +
      `2. **Add Defensive Equities**: Within your equity allocation, shift some exposure to defensive sectors like utilities, consumer staples, and healthcare, which typically have lower volatility.\n\n` +
      `3. **Implement Options Strategies**: Consider covered call writing on some of your larger equity positions to generate income and provide some downside protection.\n\n` +
      `4. **Add Low-Correlation Assets**: Increase exposure to assets with low correlation to equities, such as certain types of real estate, infrastructure investments, or market-neutral alternative strategies.\n\n` +
      `5. **Dollar-Cost Averaging**: For new investments, use a systematic dollar-cost averaging approach to reduce the impact of market timing and volatility.\n\n` +
      `Implementing these changes could potentially reduce your portfolio volatility to around 9-10% while maintaining a reasonable expected return of 6-7%.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      metrics: {
        volatility: portfolioData.metrics.volatility,
        expected_return: portfolioData.metrics.expected_return
      }
    };
  } else if (lowerQuery.includes('tax')) {
    response = `Based on your portfolio, here are tax optimization strategies to consider:\n\n` +
      `1. **Tax-Loss Harvesting**: Several positions show unrealized losses that could be harvested to offset capital gains. Specifically, your positions in Tesla and Meta could be candidates if they have unrealized losses.\n\n` +
      `2. **Asset Location**: Consider moving your fixed income investments (currently 35% of your portfolio) to tax-advantaged accounts since they generate income taxed at ordinary rates. Keep growth-oriented equities in taxable accounts to benefit from lower long-term capital gains rates.\n\n` +
      `3. **Municipal Bonds**: For the fixed income portion in taxable accounts, consider tax-exempt municipal bonds if you're in a high tax bracket.\n\n` +
      `4. **Tax-Managed Funds**: Replace high-turnover actively managed funds with tax-managed funds or ETFs that are designed to minimize distributions.\n\n` +
      `5. **Charitable Giving**: Consider donating appreciated securities instead of cash to charities to avoid capital gains tax.\n\n` +
      `6. **Qualified Dividends**: Focus on investments that generate qualified dividends (taxed at lower rates) rather than non-qualified dividends in taxable accounts.\n\n` +
      `7. **Roth Conversion Ladder**: If applicable, consider strategically converting traditional IRA assets to Roth in years when you're in a lower tax bracket.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation
    };
  } else if (lowerQuery.includes('rebalance')) {
    response = `Based on your portfolio's current allocation and target allocation, rebalancing is recommended.\n\n` +
      `**Current Allocation**:\n` +
      `- Equities: 40% (target: 35%)\n` +
      `- Fixed Income: 35% (target: 40%)\n` +
      `- Cash: 5% (target: 5%)\n` +
      `- Alternative Investments: 20% (target: 20%)\n\n` +
      `**Recommended Rebalancing Actions**:\n` +
      `1. Reduce Equities by 5% (approximately $97,500)\n` +
      `2. Increase Fixed Income by 5% (approximately $97,500)\n\n` +
      `Within your equity allocation, consider trimming your technology exposure, particularly your Microsoft position which has grown to 9.2% of your portfolio.\n\n` +
      `The best approach would be to make these adjustments in tax-advantaged accounts if possible to avoid triggering capital gains taxes. If rebalancing in taxable accounts, consider using new contributions to build up underweight positions rather than selling overweight positions.\n\n` +
      `I recommend rebalancing when allocations drift more than 5% from targets, or at least annually if no significant drift occurs.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      top_holdings: portfolioData.top_holdings
    };
  } else {
    // Default response for other queries
    response = `Based on your portfolio analysis, here's what I can tell you:\n\n` +
      `Your portfolio value is $1,950,000 with a moderate risk profile. Your asset allocation is 40% equities, 35% fixed income, 5% cash, and 20% alternative investments.\n\n` +
      `Your top holding is Microsoft Corp. at $180,000 (9.2% of your portfolio), followed by Tesla, Apple, Amazon, and Meta.\n\n` +
      `Your portfolio has a diversification score of 72/100, which is reasonably good. The expected annual return is approximately 8% with a volatility of 12%.\n\n` +
      `For more specific insights, try asking about your asset allocation, top holdings, diversification, risk level, or recommendations for improvement.`;
    
    data = {
      portfolio_value: portfolioData.portfolio_value,
      asset_allocation: portfolioData.asset_allocation,
      top_holdings: portfolioData.top_holdings.slice(0, 3),
      metrics: portfolioData.metrics
    };
  }

  return {
    query: query,
    response: response,
    data: data
  };
}
