import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiPieChart, FiTrendingUp, FiBarChart2, FiActivity, FiRefreshCw } from 'react-icons/fi';
import FinancialDataVisualization from './FinancialDataVisualization';
import portfolioController from '../controllers/portfolioController';

const PortfolioAnalysisDashboard = ({ portfolio }) => {
  const [activeTab, setActiveTab] = useState('allocation');
  const [timeframe, setTimeframe] = useState('1Y');
  const [benchmark, setBenchmark] = useState('S&P 500');
  const [portfolioSummary, setPortfolioSummary] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!portfolio) return;

    const analyzePortfolio = async () => {
      setLoading(true);
      try {
        // Analyze portfolio
        const summary = await portfolioController.analyzePortfolio(portfolio);
        setPortfolioSummary(summary);

        // Get historical performance data
        const historical = await portfolioController.getHistoricalPerformance(portfolio, timeframe);
        setHistoricalData(historical);

        // Get comparison data
        const comparison = await portfolioController.compareToIndex(portfolio, benchmark);
        setComparisonData(comparison);
      } catch (error) {
        console.error('Error analyzing portfolio:', error);
      } finally {
        setLoading(false);
      }
    };

    analyzePortfolio();
  }, [portfolio, timeframe, benchmark]);

  const handleTimeframeChange = (newTimeframe) => {
    setTimeframe(newTimeframe);
  };

  const handleBenchmarkChange = (newBenchmark) => {
    setBenchmark(newBenchmark);
  };

  const renderAllocationView = () => {
    if (!portfolioSummary) return null;

    const allocationData = {
      holdings: portfolioSummary.assetAllocation.assetClass.map(item => ({
        name: item.name,
        value: item.value
      })),
      summary: {
        totalValue: portfolioSummary.totalValue.toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        lastUpdated: new Date(portfolioSummary.lastUpdated).toLocaleDateString()
      }
    };

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Asset Class Allocation</h3>
            <FinancialDataVisualization data={allocationData} type="portfolio" />
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Sector Allocation</h3>
            <FinancialDataVisualization
              data={{
                holdings: portfolioSummary.assetAllocation.sector.map(item => ({
                  name: item.name,
                  value: item.value
                })),
                summary: allocationData.summary
              }}
              type="portfolio"
            />
          </div>

          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Geographic Allocation</h3>
            <FinancialDataVisualization
              data={{
                holdings: portfolioSummary.assetAllocation.region.map(item => ({
                  name: item.name,
                  value: item.value
                })),
                summary: allocationData.summary
              }}
              type="portfolio"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Allocation Summary</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-blue-500 uppercase">Total Value</h4>
              <p className="mt-1 text-lg font-semibold text-blue-700">
                {portfolioSummary.totalValue.toLocaleString('en-US', {
                  style: 'currency',
                  currency: 'USD'
                })}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Asset Classes</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.assetAllocation.assetClass.length}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Sectors</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.assetAllocation.sector.length}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Regions</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.assetAllocation.region.length}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderPerformanceView = () => {
    if (!portfolioSummary || !historicalData) return null;

    const performanceData = {
      timeSeries: {
        dates: historicalData.dates,
        values: historicalData.values
      },
      summary: {
        startValue: historicalData.values[0].toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        endValue: historicalData.values[historicalData.values.length - 1].toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD'
        }),
        change: portfolioSummary.performanceMetrics.absoluteReturn.toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD',
          signDisplay: 'always'
        }),
        percentChange: `${portfolioSummary.performanceMetrics.percentageReturn.toFixed(2)}%`,
        annualizedReturn: `${portfolioSummary.performanceMetrics.annualizedReturn.toFixed(2)}%`
      }
    };

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Performance Over Time</h3>
            <div className="flex space-x-2">
              {['1M', '3M', '1Y', '5Y'].map((tf) => (
                <button
                  key={tf}
                  type="button"
                  onClick={() => handleTimeframeChange(tf)}
                  className={`px-3 py-1 text-sm rounded-md ${
                    timeframe === tf
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <FinancialDataVisualization data={performanceData} type="timeSeries" />
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-blue-500 uppercase">Total Return</h4>
              <p className="mt-1 text-lg font-semibold text-blue-700">
                {portfolioSummary.performanceMetrics.percentageReturn.toFixed(2)}%
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Annualized Return</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.performanceMetrics.annualizedReturn.toFixed(2)}%
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Absolute Return</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.performanceMetrics.absoluteReturn.toLocaleString('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  signDisplay: 'always'
                })}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Start Date</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {new Date(portfolioSummary.performanceMetrics.startDate).toLocaleDateString()}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">End Date</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {new Date(portfolioSummary.performanceMetrics.currentDate).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderComparisonView = () => {
    if (!comparisonData) return null;

    const benchmarkOptions = ['S&P 500', 'NASDAQ', 'Dow Jones', 'Russell 2000', 'FTSE 100'];

    const comparisonChartData = {
      comparison: {
        categories: comparisonData.dates,
        series: [
          {
            name: 'Portfolio',
            data: comparisonData.portfolio
          },
          {
            name: comparisonData.benchmarkName,
            data: comparisonData.benchmark
          }
        ]
      },
      summary: {
        startDate: comparisonData.dates[0],
        endDate: comparisonData.dates[comparisonData.dates.length - 1],
        portfolioReturn: `${(comparisonData.portfolio[comparisonData.portfolio.length - 1] - comparisonData.portfolio[0]).toFixed(2)}%`,
        benchmarkReturn: `${(comparisonData.benchmark[comparisonData.benchmark.length - 1] - comparisonData.benchmark[0]).toFixed(2)}%`
      }
    };

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Benchmark Comparison</h3>
            <div className="flex items-center space-x-2">
              <label htmlFor="benchmark-select" className="text-sm text-gray-700">
                Benchmark:
              </label>
              <select
                id="benchmark-select"
                value={benchmark}
                onChange={(e) => handleBenchmarkChange(e.target.value)}
                className="block w-40 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                {benchmarkOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <FinancialDataVisualization data={comparisonChartData} type="comparison" />
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Comparison Summary</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-blue-500 uppercase">Portfolio Return</h4>
              <p className="mt-1 text-lg font-semibold text-blue-700">
                {comparisonChartData.summary.portfolioReturn}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">{benchmark} Return</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {comparisonChartData.summary.benchmarkReturn}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Difference</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {(parseFloat(comparisonChartData.summary.portfolioReturn) - parseFloat(comparisonChartData.summary.benchmarkReturn)).toFixed(2)}%
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Time Period</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {timeframe}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderRiskView = () => {
    if (!portfolioSummary) return null;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Metrics</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-blue-500 uppercase">Volatility</h4>
              <p className="mt-1 text-lg font-semibold text-blue-700">
                {portfolioSummary.riskMetrics.volatility.toFixed(2)}%
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Sharpe Ratio</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.riskMetrics.sharpeRatio.toFixed(2)}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Max Drawdown</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.riskMetrics.maxDrawdown.toFixed(2)}%
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Beta</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.riskMetrics.beta.toFixed(2)}
              </p>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="text-xs font-medium text-gray-500 uppercase">Alpha</h4>
              <p className="mt-1 text-lg font-semibold text-gray-700">
                {portfolioSummary.riskMetrics.alpha.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Assessment</h3>
          <div className="space-y-4">
            <div className="flex items-center">
              <div className="w-32 text-sm font-medium text-gray-700">Volatility</div>
              <div className="flex-1">
                <div className="h-2 bg-gray-200 rounded-full">
                  <div
                    className="h-2 bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(portfolioSummary.riskMetrics.volatility * 5, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm text-gray-500">
                {portfolioSummary.riskMetrics.volatility < 10 ? 'Low' :
                 portfolioSummary.riskMetrics.volatility < 20 ? 'Medium' : 'High'}
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-32 text-sm font-medium text-gray-700">Sharpe Ratio</div>
              <div className="flex-1">
                <div className="h-2 bg-gray-200 rounded-full">
                  <div
                    className="h-2 bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(portfolioSummary.riskMetrics.sharpeRatio * 33, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm text-gray-500">
                {portfolioSummary.riskMetrics.sharpeRatio < 1 ? 'Poor' :
                 portfolioSummary.riskMetrics.sharpeRatio < 2 ? 'Good' : 'Excellent'}
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-32 text-sm font-medium text-gray-700">Max Drawdown</div>
              <div className="flex-1">
                <div className="h-2 bg-gray-200 rounded-full">
                  <div
                    className="h-2 bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(portfolioSummary.riskMetrics.maxDrawdown * 2, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm text-gray-500">
                {portfolioSummary.riskMetrics.maxDrawdown < 15 ? 'Low' :
                 portfolioSummary.riskMetrics.maxDrawdown < 30 ? 'Medium' : 'High'}
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-32 text-sm font-medium text-gray-700">Beta</div>
              <div className="flex-1">
                <div className="h-2 bg-gray-200 rounded-full">
                  <div
                    className="h-2 bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(portfolioSummary.riskMetrics.beta * 50, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm text-gray-500">
                {portfolioSummary.riskMetrics.beta < 0.8 ? 'Defensive' :
                 portfolioSummary.riskMetrics.beta < 1.2 ? 'Neutral' : 'Aggressive'}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderActiveView = () => {
    switch (activeTab) {
      case 'allocation':
        return renderAllocationView();
      case 'performance':
        return renderPerformanceView();
      case 'comparison':
        return renderComparisonView();
      case 'risk':
        return renderRiskView();
      default:
        return renderAllocationView();
    }
  };

  if (!portfolio) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-500">No portfolio selected</p>
      </div>
    );
  }

  return (
    <AccessibilityWrapper>
      <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('allocation')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'allocation'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiPieChart className="mr-2 h-5 w-5" />
              Asset Allocation
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'performance'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiTrendingUp className="mr-2 h-5 w-5" />
              Performance
            </button>
            <button
              onClick={() => setActiveTab('comparison')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'comparison'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiBarChart2 className="mr-2 h-5 w-5" />
              Benchmark Comparison
            </button>
            <button
              onClick={() => setActiveTab('risk')}
              className={`py-4 px-6 text-sm font-medium flex items-center ${
                activeTab === 'risk'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <FiActivity className="mr-2 h-5 w-5" />
              Risk Analysis
            </button>
          </nav>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        renderActiveView()
      )}
    </div>
    </AccessibilityWrapper>
  );
};

export default PortfolioAnalysisDashboard;
