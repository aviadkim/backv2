import React, { useState, useEffect } from 'react';
import withProtectedRoute from '../components/ProtectedRoute';
import PortfolioAnalysisDashboard from '../components/PortfolioAnalysisDashboard';
import ReportGenerator from '../components/ReportGenerator';
import ExportData from '../components/ExportData';
import { FiRefreshCw } from 'react-icons/fi';

const TestPortfolioPage = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Load sample portfolio data
    const loadSamplePortfolio = () => {
      setLoading(true);
      
      // Sample portfolio data
      const samplePortfolio = {
        id: 'portfolio-1',
        name: 'Sample Investment Portfolio',
        holdings: [
          {
            id: 'holding-1',
            portfolioId: 'portfolio-1',
            isin: 'US0378331005',
            name: 'Apple Inc.',
            quantity: 100,
            price: 176.35,
            value: 17635.00,
            currency: 'USD',
            assetClass: 'Equity',
            sector: 'Technology',
            region: 'North America',
            costBasis: 150.25,
            purchaseDate: '2022-01-15'
          },
          {
            id: 'holding-2',
            portfolioId: 'portfolio-1',
            isin: 'US5949181045',
            name: 'Microsoft Corporation',
            quantity: 50,
            price: 412.27,
            value: 20613.50,
            currency: 'USD',
            assetClass: 'Equity',
            sector: 'Technology',
            region: 'North America',
            costBasis: 320.15,
            purchaseDate: '2022-02-10'
          },
          {
            id: 'holding-3',
            portfolioId: 'portfolio-1',
            isin: 'US88160R1014',
            name: 'Tesla Inc.',
            quantity: 25,
            price: 175.34,
            value: 4383.50,
            currency: 'USD',
            assetClass: 'Equity',
            sector: 'Automotive',
            region: 'North America',
            costBasis: 200.50,
            purchaseDate: '2022-03-05'
          },
          {
            id: 'holding-4',
            portfolioId: 'portfolio-1',
            isin: 'US0231351067',
            name: 'Amazon.com Inc.',
            quantity: 10,
            price: 1528.08,
            value: 15280.80,
            currency: 'USD',
            assetClass: 'Equity',
            sector: 'Consumer Discretionary',
            region: 'North America',
            costBasis: 1200.75,
            purchaseDate: '2022-01-20'
          },
          {
            id: 'holding-5',
            portfolioId: 'portfolio-1',
            isin: 'US02079K1079',
            name: 'Alphabet Inc.',
            quantity: 8,
            price: 1556.29,
            value: 12450.32,
            currency: 'USD',
            assetClass: 'Equity',
            sector: 'Communication Services',
            region: 'North America',
            costBasis: 1300.00,
            purchaseDate: '2022-02-15'
          },
          {
            id: 'holding-6',
            portfolioId: 'portfolio-1',
            isin: 'US4642872422',
            name: 'iShares MSCI EAFE ETF',
            quantity: 100,
            price: 75.25,
            value: 7525.00,
            currency: 'USD',
            assetClass: 'ETF',
            sector: 'International',
            region: 'Europe',
            costBasis: 70.50,
            purchaseDate: '2022-03-10'
          },
          {
            id: 'holding-7',
            portfolioId: 'portfolio-1',
            isin: 'US9128282D10',
            name: 'US Treasury Bond 2.5% 2024',
            quantity: 10000,
            price: 0.985,
            value: 9850.00,
            currency: 'USD',
            assetClass: 'Fixed Income',
            sector: 'Government',
            region: 'North America',
            costBasis: 1.00,
            purchaseDate: '2022-01-05'
          },
          {
            id: 'holding-8',
            portfolioId: 'portfolio-1',
            isin: 'US912810TW33',
            name: 'US Treasury Bond 3.0% 2049',
            quantity: 5000,
            price: 0.92,
            value: 4600.00,
            currency: 'USD',
            assetClass: 'Fixed Income',
            sector: 'Government',
            region: 'North America',
            costBasis: 0.98,
            purchaseDate: '2022-02-20'
          }
        ],
        performanceData: {
          startValue: 85000.00,
          currentValue: 92338.12,
          startDate: '2022-01-01',
          currentDate: '2023-05-15'
        },
        riskData: {
          volatility: 12.5,
          sharpeRatio: 1.2,
          maxDrawdown: 15.3,
          beta: 0.85,
          alpha: 2.1
        },
        createdAt: '2022-01-01T00:00:00Z',
        updatedAt: '2023-05-15T00:00:00Z'
      };
      
      setPortfolio(samplePortfolio);
      setLoading(false);
    };
    
    loadSamplePortfolio();
  }, []);
  
  const handleRefresh = () => {
    setLoading(true);
    
    // Simulate refresh delay
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Portfolio Analysis Test</h1>
        <button
          type="button"
          onClick={handleRefresh}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <FiRefreshCw className="mr-2 -ml-1 h-5 w-5" />
          Refresh
        </button>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="space-y-8">
          <PortfolioAnalysisDashboard portfolio={portfolio} />
          
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <ReportGenerator portfolio={portfolio} />
            <ExportData portfolio={portfolio} />
          </div>
        </div>
      )}
    </div>
  );
};

export default withProtectedRoute(TestPortfolioPage);
