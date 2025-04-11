import React, { useState } from 'react';
import FinancialDataVisualization from '../components/FinancialDataVisualization';
import withProtectedRoute from '../components/ProtectedRoute';

const TestVisualizationPage = () => {
  const [visualizationType, setVisualizationType] = useState('portfolio');
  
  // Sample portfolio data
  const portfolioData = {
    holdings: [
      { name: 'Apple Inc.', isin: 'US0378331005', value: 17635.00 },
      { name: 'Microsoft Corporation', isin: 'US5949181045', value: 20613.50 },
      { name: 'Tesla Inc.', isin: 'US88160R1014', value: 4383.50 },
      { name: 'Amazon.com Inc.', isin: 'US0231351067', value: 15280.75 },
      { name: 'Alphabet Inc.', isin: 'US02079K1079', value: 12450.30 }
    ],
    summary: {
      totalValue: '$70,363.05',
      totalSecurities: 5,
      topHolding: 'Microsoft Corporation',
      lastUpdated: '2023-05-15'
    }
  };
  
  // Sample time series data
  const timeSeriesData = {
    timeSeries: {
      dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      values: [65000, 67500, 69200, 68400, 70300, 72100, 71500, 73200, 75600, 74800, 76300, 78500]
    },
    summary: {
      startValue: '$65,000.00',
      endValue: '$78,500.00',
      change: '+$13,500.00',
      percentChange: '+20.77%',
      annualizedReturn: '20.77%'
    }
  };
  
  // Sample comparison data
  const comparisonData = {
    comparison: {
      categories: ['Stocks', 'Bonds', 'Cash', 'Real Estate', 'Commodities'],
      series: [
        {
          name: 'Current Allocation',
          data: [60, 25, 5, 7, 3]
        },
        {
          name: 'Target Allocation',
          data: [55, 30, 5, 8, 2]
        }
      ]
    },
    summary: {
      totalValue: '$70,363.05',
      largestDeviation: 'Bonds (-5%)',
      rebalanceRecommended: 'Yes'
    }
  };
  
  // Get the appropriate data based on visualization type
  const getVisualizationData = () => {
    switch (visualizationType) {
      case 'portfolio':
        return portfolioData;
      case 'timeSeries':
        return timeSeriesData;
      case 'comparison':
        return comparisonData;
      default:
        return portfolioData;
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Financial Data Visualization Test</h1>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Visualization Type</label>
        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setVisualizationType('portfolio')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'portfolio'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Portfolio Allocation
          </button>
          <button
            type="button"
            onClick={() => setVisualizationType('timeSeries')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'timeSeries'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Time Series
          </button>
          <button
            type="button"
            onClick={() => setVisualizationType('comparison')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'comparison'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Comparison
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <FinancialDataVisualization
          data={getVisualizationData()}
          type={visualizationType}
        />
      </div>
    </div>
  );
};

export default withProtectedRoute(TestVisualizationPage);
