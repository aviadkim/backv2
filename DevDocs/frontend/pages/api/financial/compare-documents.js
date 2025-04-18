// API endpoint for comparing two financial documents

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { document1_id, document2_id } = req.body;

    if (!document1_id || !document2_id) {
      return res.status(400).json({ error: 'Both document IDs are required' });
    }

    // In a real implementation, we would fetch the documents from the database
    // and use the DocumentComparisonAgent to compare them
    // For now, we'll return mock comparison results

    // Mock comparison results
    const mockResults = {
      document1: {
        id: document1_id,
        date: '2023-01-15T00:00:00Z',
        portfolio_value: 1850000
      },
      document2: {
        id: document2_id,
        date: '2023-04-15T00:00:00Z',
        portfolio_value: 1950000
      },
      basic_comparison: {
        document_types_match: true,
        time_difference: {
          milliseconds: 7776000000,
          days: 90
        },
        chronological_order: 'doc1_older'
      },
      portfolio_comparison: {
        has_both_values: true,
        doc1_value: 1850000,
        doc2_value: 1950000,
        absolute_difference: 100000,
        percentage_difference: 5.41,
        direction: 'increase'
      },
      allocation_comparison: {
        changes: [
          {
            asset_class: 'Equities',
            doc1_value: 0.35,
            doc2_value: 0.40,
            absolute_difference: 0.05,
            percentage_difference: 14.29,
            direction: 'increase'
          },
          {
            asset_class: 'Fixed Income',
            doc1_value: 0.40,
            doc2_value: 0.35,
            absolute_difference: -0.05,
            percentage_difference: -12.5,
            direction: 'decrease'
          },
          {
            asset_class: 'Cash',
            doc1_value: 0.10,
            doc2_value: 0.05,
            absolute_difference: -0.05,
            percentage_difference: -50,
            direction: 'decrease'
          }
        ],
        additions: [
          {
            asset_class: 'Alternative Investments',
            value: 0.05
          }
        ],
        removals: [],
        has_changes: true
      },
      securities_comparison: {
        changes: [
          {
            isin: 'US0378331005',
            name: 'Apple Inc.',
            value: {
              doc1: 85000,
              doc2: 95000,
              absolute_change: 10000,
              percentage_change: 11.76,
              direction: 'increase'
            },
            quantity: {
              doc1: 500,
              doc2: 500,
              absolute_change: 0,
              percentage_change: 0,
              direction: 'no_change'
            },
            price: {
              doc1: 170,
              doc2: 190,
              absolute_change: 20,
              percentage_change: 11.76,
              direction: 'increase'
            }
          },
          {
            isin: 'US88160R1014',
            name: 'Tesla Inc.',
            value: {
              doc1: 120000,
              doc2: 105000,
              absolute_change: -15000,
              percentage_change: -12.5,
              direction: 'decrease'
            },
            quantity: {
              doc1: 600,
              doc2: 500,
              absolute_change: -100,
              percentage_change: -16.67,
              direction: 'decrease'
            },
            price: {
              doc1: 200,
              doc2: 210,
              absolute_change: 10,
              percentage_change: 5,
              direction: 'increase'
            }
          },
          {
            isin: 'US5949181045',
            name: 'Microsoft Corp.',
            value: {
              doc1: 150000,
              doc2: 180000,
              absolute_change: 30000,
              percentage_change: 20,
              direction: 'increase'
            },
            quantity: {
              doc1: 500,
              doc2: 600,
              absolute_change: 100,
              percentage_change: 20,
              direction: 'increase'
            },
            price: {
              doc1: 300,
              doc2: 300,
              absolute_change: 0,
              percentage_change: 0,
              direction: 'no_change'
            }
          }
        ],
        additions: [
          {
            isin: 'US0231351067',
            name: 'Amazon.com Inc.',
            value: 90000,
            quantity: 300,
            price: 300
          },
          {
            isin: 'US30303M1027',
            name: 'Meta Platforms Inc.',
            value: 75000,
            quantity: 250,
            price: 300
          }
        ],
        removals: [
          {
            isin: 'US67066G1040',
            name: 'NVIDIA Corp.',
            value: 80000,
            quantity: 200,
            price: 400
          }
        ],
        total_securities: {
          doc1: 15,
          doc2: 16,
          difference: 1
        },
        has_changes: true
      },
      performance_comparison: {
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
      },
      summary: {
        summary: "The portfolio has shown positive growth over the 90-day period between January 15, 2023, and April 15, 2023, with the total value increasing by 5.41% ($100,000) from $1,850,000 to $1,950,000. This growth is primarily driven by increased allocation to equities (from 35% to 40%) and the addition of alternative investments (5%), while reducing exposure to fixed income (from 40% to 35%) and cash (from 10% to 5%).\n\nSignificant changes in individual securities include increased positions in Microsoft Corp. (20% increase in value) and Apple Inc. (11.76% increase in value), while reducing exposure to Tesla Inc. (12.5% decrease in value). The portfolio also added new positions in Amazon.com Inc. and Meta Platforms Inc., while completely divesting from NVIDIA Corp. Overall, the number of securities increased from 15 to 16.\n\nPerformance metrics have improved across the board, with year-to-date returns increasing from 5% to 8% and one-year returns improving from 12% to 15%, indicating stronger overall performance in the more recent period.",
        highlights: [
          "Portfolio value increased by 5.41% ($100,000) over a 90-day period",
          "Shifted allocation from fixed income and cash toward equities and alternative investments",
          "Added new positions in Amazon and Meta while divesting from NVIDIA",
          "Increased holdings in Microsoft by 20% in value",
          "Performance metrics improved with YTD returns up from 5% to 8%"
        ]
      }
    };

    return res.status(200).json(mockResults);
  } catch (error) {
    console.error('Error comparing documents:', error);
    return res.status(500).json({ 
      error: 'Error comparing documents', 
      detail: error.message 
    });
  }
}
